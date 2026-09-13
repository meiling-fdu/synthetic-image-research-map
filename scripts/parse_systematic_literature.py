#!/usr/bin/env python3
"""Extract traceable discovery observations from cached audit sources."""
import html
import json
import re
from html.parser import HTMLParser
from urllib.parse import urljoin
try:
    from .collect_systematic_literature import ROOT, PROCESSED, read_response
except ImportError:
    from collect_systematic_literature import ROOT, PROCESSED, read_response

# Broad discovery gate, never an inclusion decision.
DISCOVERY = re.compile(r'forensic|forger|deepfake|attribut|provenance|fingerprint|watermark|'
                       r'(?:detect|localiz|identif|authentic|fake).{0,90}(?:generat|synthe|image|diffusion|gan)|'
                       r'(?:generat|synthe|image|diffusion|gan).{0,90}(?:detect|localiz|identif|authentic|fake)', re.I)


def text(value):
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', value)).split())


def links(value):
    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.href, self.label, self.result = None, [], []
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                self.href, self.label = dict(attrs).get('href'), []
        def handle_data(self, data):
            if self.href is not None:
                self.label.append(data)
        def handle_endtag(self, tag):
            if tag == 'a' and self.href is not None:
                self.result.append((self.href, ' '.join(''.join(self.label).split())))
                self.href = None
    parser = Links()
    parser.feed(value)
    return parser.result


def indexes(source, body):
    result = []
    if source['kind'] == 'ijcai_index':
        for block in re.split(r'<div id="paper\d+" class="paper_wrapper">', body)[1:]:
            title = re.search(r'<div class="title">(.*?)</div>', block, re.S)
            authors = re.search(r'<div class="authors">(.*?)</div>', block, re.S)
            target = next((u for u, label in links(block) if label == 'Details'), '')
            if title and target:
                result.append({'title': text(title[1]), 'authors': text(authors[1]) if authors else '', 'primary_url': urljoin(source['url'], target)})
    elif source['kind'] == 'pmlr_index':
        for block in body.split('<div class="paper">')[1:]:
            title = re.search(r'<p class="title">(.*?)</p>', block, re.S)
            target = next((url for url, label in links(block) if label == 'abs'), '')
            if title and target:
                result.append({'title': text(title[1]), 'primary_url': target})
    else:
        for url, title in links(body):
            if not title:
                continue
            if source['kind'] == 'cvf_index' and '/html/' in url and '_paper.html' in url:
                result.append({'title': title, 'primary_url': urljoin(source['url'], url)})
            elif source['kind'] == 'neurips_index' and '-Abstract' in url:
                result.append({'title': title, 'primary_url': urljoin(source['url'], url)})
            elif source['kind'] == 'ecva_index' and 'eccv_2024' in url and '/html/' in url:
                result.append({'title': title, 'primary_url': urljoin(source['url'], url)})
    return list({r['primary_url']: r for r in result}.values())


def bibliography(source, body):
    result = []
    for number, block in enumerate(re.findall(r'<li\b[^>]*class="ltx_bibitem[^\"]*"[^>]*>(.*?)</li>', body, re.S), 1):
        pieces = re.split(r'<span class="ltx_bibblock">', block)[1:]
        if len(pieces) < 2:
            continue
        author_year = text(pieces[0])
        raw_title = text(pieces[1]).rstrip('.')
        title = raw_title
        # Some arXiv bibliographies place title and proceedings in one bibblock.
        # Retain the untouched reference below; strip only explicit venue delimiters.
        title = re.split(r'\. In (?:Proc\.|Proceedings|Computer Vision|European Conference|\d{4} IEEE|ICASSP)|, in: ', title, flags=re.I)[0].rstrip('.')
        all_text = text(block)
        year = re.search(r'\b(19\d{2}|20\d{2})\b', text(block.split('<span class="ltx_bibblock">')[0]) + ' ' + author_year)
        doi = re.search(r'https?://(?:dx\.)?doi.org/([^\s"<>]+)', block)
        arxiv = re.search(r'(?:arxiv[.:/ ]+(?:abs/|pdf/)?)(\d{4}\.\d{4,5})', all_text + ' ' + block, re.I)
        result.append({'title': title, 'raw_title': raw_title, 'authors': author_year, 'year': year[1] if year else '',
                       'doi': html.unescape(doi[1]).rstrip('.') if doi else '',
                       'arxiv_id': arxiv[1] if arxiv else '', 'reference_number': number,
                       'bibliography_text': all_text, 'reference_links': links(block)})
    return result


def openalex(record):
    abstract = record.get('abstract_inverted_index') or {}
    words = {i: word for word, indexes in abstract.items() for i in indexes}
    return {'title': record.get('display_name', ''),
            'authors': '; '.join(a['author']['display_name'] for a in record.get('authorships', [])),
            'year': record.get('publication_year', ''), 'doi': record.get('doi') or '',
            'openalex_url': record.get('id', ''),
            'venue': ((record.get('primary_location') or {}).get('source') or {}).get('display_name', ''),
            'primary_url': (record.get('primary_location') or {}).get('landing_page_url') or '',
            'abstract': ' '.join(words[i] for i in sorted(words)),
            'publication_date': record.get('publication_date', '')}


def pdf_bibliography():
    value = (PROCESSED / 'attribution_survey_text.txt').read_text().split('\nReferences\n', 1)[1]
    starts = list(re.finditer(r'(?m)^([A-Z][^\n]+(?:\n(?:et al|[A-Z][a-z]+ [A-Z]{1,3})[^\n]*)?)\s+\((19\d{2}|20\d{2})[a-z]?\)', value))
    rows = []
    for n, match in enumerate(starts):
        tail = value[match.end():starts[n + 1].start() if n + 1 < len(starts) else len(value)]
        tail = re.sub(r'(?m)^\d{1,2}\s*$', '', tail)
        tail = re.sub(r'(?<!ai)(?<!gan)-\n(?=[a-z])', '', tail, flags=re.I)
        tail = ' '.join(tail.split())
        title = re.split(r'\s+In:|\.\s+(?:arXiv|IEEE|Pattern|Wiley|ACM|Advances|Electronic|Electronics|Trans|Journal|Computer|International|Tech\.)', tail)[0].rstrip('.')
        arxiv = re.search(r'arXiv:(\d{4})\.?([0-9]{4,5})', tail)
        rows.append({'title': title, 'authors': ' '.join(match[1].split()), 'year': match[2],
                     'arxiv_id': arxiv[1] + '.' + arxiv[2] if arxiv else '',
                     'reference_number': n + 1, 'bibliography_text': match[0] + ' ' + tail})
    return rows


def crossref(record):
    parts = (record.get('published') or {}).get('date-parts', [[]])[0]
    return {'title': text(' '.join(record.get('title', []))), 'doi': record.get('DOI', ''),
            'authors': '; '.join(' '.join([a.get('given', ''), a.get('family', '')]).strip() for a in record.get('author', [])),
            'year': parts[0] if parts else '', 'venue': '; '.join(record.get('container-title', [])),
            'primary_url': record.get('URL', ''), 'abstract': text(record.get('abstract', ''))}


def parse_all():
    observations, enumerations, raw_records = [], [], []
    evidence = json.loads((PROCESSED / 'primary_evidence.json').read_text()) if (PROCESSED / 'primary_evidence.json').exists() else []
    for manifest in sorted(PROCESSED.glob('*_sources.json')):
        for source in json.loads(manifest.read_text()):
            if source['status'] not in (200, 'CLI_SUCCESS'):
                continue
            kind = source['kind']
            body = (ROOT / source['raw_path']).read_text() if kind == 'hf_search' else read_response(source).decode(errors='replace')
            if kind.endswith('_index'):
                rows = indexes(source, body)
            elif kind == 'survey_html':
                rows = bibliography(source, body)
            elif kind == 'survey_pdf':
                rows = pdf_bibliography()
            elif kind == 'crossref_search':
                rows = [crossref(r) for r in json.loads(body).get('message', {}).get('items', [])]
            elif kind == 'hf_search':
                rows = [{'title': text(r['title']), 'authors': '; '.join(a['name'] for a in r.get('authors', [])),
                         'arxiv_id': r['id'], 'year': str(r.get('published_at', ''))[:4],
                         'publication_date': str(r.get('published_at', ''))[:10], 'venue': 'arXiv',
                         'abstract': r.get('summary', ''), 'primary_url': 'https://arxiv.org/abs/' + r['id']}
                        for r in json.loads(body) if str(r.get('published_at', ''))[:10] <= '2026-09-12']
            elif kind == 'lineage_paper':
                rows = [r for r in evidence if r.get('lineage_family') == source['seed'] and r['primary_url'] == source['url'] and r['title']]
            elif kind in {'citing_works', 'reference_works', 'discovery_search', 'lineage_search'}:
                data = json.loads(body)
                rows = [openalex(row) for row in data.get('results', [])]
            else:
                continue
            source_pass = source.get('discovery_pass') or int(re.search(r'pass(\d+)', manifest.name)[1])
            enumerations.append({'source': source['url'], 'seed': source['seed'], 'channel': source['channel'],
                                 'discovery_pass': source_pass,
                                 'kind': kind, 'enumerated': len(rows),
                                 'screened': sum(bool(DISCOVERY.search(r['title'])) or kind.startswith('survey_') or kind == 'lineage_paper' for r in rows)})
            for rank, row in enumerate(rows, 1):
                year = re.search(r'20\d\d', source['seed']) if kind.endswith('_index') else None
                selected = bool(DISCOVERY.search(row['title'])) or kind.startswith('survey_') or kind == 'lineage_paper'
                reference_rank = row.get('reference_number', rank)
                if kind == 'reference_works':
                    expected_ids = str(source.get('query', {}).get('filter', '')).removeprefix('openalex_id:').split('|')
                    record_id = row.get('openalex_url', '').rsplit('/', 1)[-1]
                    if record_id in expected_ids:
                        reference_rank = source.get('reference_offset', 0) + expected_ids.index(record_id) + 1
                entry = {**row, 'raw_title': row.get('raw_title', row['title']), 'raw_authors': row.get('authors', ''),
                                     'year': row.get('year') or (year[0] if year else ''),
                                     'venue': row.get('venue') or (source['seed'] if kind.endswith('_index') else ''),
                                     'channel': source['channel'], 'seed': source['seed'],
                                     'source_kind': kind,
                                     'retrieval_mode': 'BOUNDED_SEARCH',
                                     'selected_for_review': selected,
                                     'source_record_id': row.get('openalex_url') or row.get('primary_url') or str(row.get('reference_number', rank)),
                                     'venue_year_source': source['seed'] if source['channel'] == 'A' else '',
                                     'survey_source': source['seed'] if source['channel'] == 'D' else '',
                                     'lineage_family': source['seed'] if source['channel'] == 'C' else '',
                                     'direction': source.get('direction', 'REFERENCES' if kind.startswith('survey_') else ''),
                                     'rank': reference_rank, 'response_rank': rank,
                                     'rank_basis': 'seed bibliography order' if kind in {'reference_works', 'survey_html', 'survey_pdf'} else 'returned source order',
                                     'discovery_pass': source_pass,
                                     'retrieval_bound': source.get('retrieval_bound') or 'returned source; see source manifest',
                                     'discovery_source': source['url'], 'raw_path': source['raw_path']}
                raw_records.append(entry)
                if selected:
                    observations.append(entry)
    with (PROCESSED / 'raw_discovery.jsonl').open('w') as handle:
        for row in raw_records:
            handle.write(json.dumps(row, sort_keys=True) + '\n')
    (PROCESSED / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n')
    (PROCESSED / 'enumerations.json').write_text(json.dumps(enumerations, indent=2) + '\n')
    print(json.dumps({'raw_records': len(raw_records), 'observations': len(observations), 'sources_enumerated': len(enumerations)}, indent=2))


if __name__ == '__main__':
    parse_all()
