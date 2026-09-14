#!/usr/bin/env python3
"""Record version chronology from the already cached primary metadata."""
import json
import re
import unicodedata
from prepare_systematic_tier1 import ROOT, OUT
from verify_systematic_literature_sources import Metadata
from reconcile_systematic_tier1 import regular_name


def author_key(value):
    return re.sub('[^a-z]', '', unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower())


def main():
    papers = json.loads((OUT / 'proposals.json').read_text())['papers']
    sources = json.loads((OUT / 'sources.json').read_text())
    result = []
    for p in papers:
        versions = []
        for source in sources:
            if source['candidate_id'] != p['candidate_id'] or source['status'] != 200 or source['kind'] not in {'primary_html', 'version_primary'}:
                continue
            if 'arxiv.org/abs/' not in source['url']:
                continue
            parser = Metadata()
            parser.feed((ROOT / source['raw_path']).read_text())
            values = parser.values
            earlier_authors = [regular_name(a) for a in values.get('citation_author', [])]
            versions.append({'earlier_title': (values.get('citation_title') or [''])[0], 'earlier_authors': earlier_authors,
                'later_title': p['title'], 'later_authors': p['authors'], 'author_overlap_normalized': sorted({author_key(a) for a in earlier_authors} & {author_key(a) for a in p['authors']}),
                'arxiv_version_history': source['url'], 'earlier_date': values.get('citation_date', values.get('citation_publication_date', [])),
                'venue_chronology': 'arXiv → ' + p['venue'] + ' ' + p['year'] if p['publication_type'] != 'preprint' else 'arXiv only; no verified final publication',
                'method_identity': p['identity_note'] or 'Same title, authors and method in the cached primary metadata and reviewed manuscript.', 'final_corpus_decision': 'One canonical work: ' + p['paper_id']})
        if p['title'].startswith('Detective SAM:'):
            earlier = ['Gert Lek', 'Chaoyi Zhu', 'Pin-Yu Chen', 'Robert Birke', 'Lydia Y. Chen']
            versions.append({'earlier_title': 'Detective SAM: Adapting SAM to Localize Diffusion-based Forgeries via Embedding Artifacts', 'later_title': p['title'], 'earlier_authors': earlier, 'later_authors': p['authors'],
                'author_overlap_normalized': sorted(author_key(a) for a in earlier), 'arxiv_version_history': 'No verified arXiv or DOI shared identifier; OpenReview workshop GPpFTmGLgT, final ICLR proceedings 262dd62fd1bbb30d6a6b4d578f5e65ff.',
                'venue_chronology': 'ICML DIG-BUG workshop, July 19 2025 → ICLR 2026',
                'method_identity': 'Continuous Detective SAM method: perturbation/blur forensic embeddings, learned prompts and lightweight SAM adaptation. Final version adds Nicolas van Schaik, SAM2/adaptive extensions and AutoEditForge. Author publication history explicitly calls it the full paper extending Detective SAM.',
                'evidence': ['https://iris.unito.it/handle/2318/2088015', 'https://gertlek.com/', p['primary_pdf_url']],
                'final_corpus_decision': 'One expanded canonical ICLR work: ' + p['paper_id']})
        result.append({'candidate_id': p['candidate_id'], 'versions': versions, 'decision': 'One canonical paper; no second distinct scientific work established.'})
    (OUT / 'version_relationships.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
