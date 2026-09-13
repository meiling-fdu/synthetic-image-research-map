#!/usr/bin/env python3
"""Prepare primary-source checks and extract metadata, without inclusion decisions."""
import argparse
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit
from collect_systematic_literature import PROCESSED, read_response
from build_systematic_literature_pass2 import make_job
from parse_systematic_literature import text

RELEVANT = re.compile(r'forensic|forger|deepfake|fake|watermark|attribut|provenance|fingerprint|synthetic image|generated image|image manipulation|image authent', re.I)
IRRELEVANT = re.compile(r'community forensic|forensic (mental|psychiatr)|forensic assertive|bacterial community|language model watermark|text watermark|3d gaussian|radiance field|feature attribution|data attribution|neuron attribution|weight attribution|fingerprint sensor|partial fingerprint', re.I)


def prepare():
    previous = PROCESSED / 'primary_jobs.json'
    jobs = {r['url']: r for r in json.loads(previous.read_text())} if previous.exists() else {}
    for group in json.loads((PROCESSED / 'candidate_queue.json').read_text()):
        if group['provisional_status'] != 'REVIEW_REQUIRED' or not RELEVANT.search(group['title']) or IRRELEVANT.search(group['title']):
            continue
        if re.search(r'large language model', group['title'], re.I) and not re.search(r'deepfake|forger|ai.generated image|fake image|synthetic image', group['title'], re.I):
            continue
        for row in group['observations']:
            url = row.get('primary_url', '')
            if not url and row.get('arxiv_id'):
                url = 'https://arxiv.org/abs/' + row['arxiv_id']
            if not url and row.get('doi'):
                url = 'https://doi.org/' + row['doi'].removeprefix('https://doi.org/')
            if not url.startswith('https://') or 'openalex.org' in url:
                continue
            # Paper links are evidence checks, not independent discovery channels.
            job = jobs.setdefault(url, make_job('EVIDENCE', 'primary_paper', group['title'], url, {}, 'one primary landing page', candidate_ids=[]))
            job['discovery_pass'] = 5
            if group['candidate_id'] not in job['candidate_ids']:
                job['candidate_ids'].append(group['candidate_id'])
    (PROCESSED / 'primary_jobs.json').write_text(json.dumps(list(jobs.values()), indent=2) + '\n')
    print(f'Prepared {len(jobs)} primary-page checks')


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('content'):
            self.values.setdefault(a.get('name') or a.get('property') or '', []).append(a['content'])


def extract():
    result = []
    sources = json.loads((PROCESSED / 'primary_sources.json').read_text())
    for manifest in sorted(PROCESSED.glob('pass*_sources.json')):
        sources += [r for r in json.loads(manifest.read_text()) if r['kind'] == 'lineage_paper']
    for source in sources:
        if source['status'] != 200:
            continue
        body = read_response(source).decode(errors='replace')
        parser = Metadata()
        parser.feed(body)
        meta = parser.values
        title = (meta.get('citation_title') or meta.get('DC.Title') or meta.get('dc.Title') or meta.get('og:title') or [''])[0]
        if not title:
            page_title = re.search(r'<div id="papertitle">(.*?)</div>', body, re.S)
            title = text(page_title[1]) if page_title else ''
        abstract = re.search(r'<(?:div|blockquote)[^>]*(?:id="abstract"|class="abstract[^"]*")[^>]*>(.*?)</(?:div|blockquote)>', body, re.S)
        if not abstract:
            abstract = re.search(r'<h[234][^>]*>\s*Abstract\s*</h[234]>\s*<p[^>]*>(.*?)</p>', body, re.S | re.I)
        summary = text(abstract[1]) if abstract else text((meta.get('description') or meta.get('og:description') or [''])[0])
        if re.search(r"world.s premier source for conference proceedings|browse.*conference proceedings|enable javascript|access denied|just a moment", summary, re.I):
            summary = ''  # Publisher navigation/challenge text is not paper evidence.
        if 'ijcai.org/proceedings/' in source['url']:
            section = re.search(r'<hr>\s*<div class="row">\s*<div class="col-md-12">(.*?)</div>', body, re.S)
            if section:
                summary = text(section[1])
        doi = (meta.get('citation_doi') or meta.get('DC.Identifier') or [''])[0]
        arxiv = re.search(r'(?:arxiv.org/(?:abs|pdf|html)/|arxiv\.)(\d{4}\.\d{4,5})', source['url'] + ' ' + source.get('final_url', '') + ' ' + doi, re.I)
        result.append({'candidate_ids': source.get('candidate_ids', []), 'requested_title': source.get('paper_title') or source['seed'],
                       'lineage_family': source['seed'] if source['kind'] == 'lineage_paper' else '',
                       'title': text(title), 'authors': '; '.join(meta.get('citation_author', [])),
                       'doi': doi if doi.startswith('10.') else '', 'arxiv_id': arxiv[1] if arxiv else '',
                       'year': (meta.get('citation_publication_date') or meta.get('citation_date') or [''])[0][:4],
                       'venue': (meta.get('citation_conference_title') or meta.get('citation_journal_title') or [''])[0],
                       'abstract': summary, 'primary_url': source['url'], 'final_url': source.get('final_url', ''),
                       'raw_path': source['raw_path'], 'metadata_present': bool(title), 'status': 200})
    (PROCESSED / 'primary_evidence.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'Extracted {len(result)} successful responses; {sum(bool(r["title"] and r["abstract"]) for r in result)} with title and summary')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'extract'])
    args = parser.parse_args()
    prepare() if args.action == 'prepare' else extract()
