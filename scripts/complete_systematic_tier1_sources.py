#!/usr/bin/env python3
"""Add narrowly scoped version/identifier checks for the fixed 16-paper list."""
import json
from urllib.parse import urlencode
from prepare_systematic_tier1 import OUT

if __name__ == '__main__':
    jobs = json.loads((OUT / 'jobs.json').read_text())
    rows = json.loads((OUT / 'candidates.json').read_text())
    extras = {'d2f5890b11ab48bf': ['https://arxiv.org/abs/2409.08849'],
              '07a67ddede76cbd3': ['https://arxiv.org/abs/2311.04584'],
              '90848f868ebeb1f7': ['https://arxiv.org/abs/2008.10588', 'https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123710103.pdf'],
              '745a864cbd6a6efc': ['https://doi.org/10.1109/ICCIT68739.2025.11491327'],
              '08beb6425ead6689': ['https://doi.org/10.1109/ACCESS.2022.3179116']}
    for row in rows:
        for url in extras.get(row['candidate_id'].split(':')[1], []):
            jobs.append(dict(candidate_id=row['candidate_id'], kind='version_primary', url=url))
        jobs.append(dict(candidate_id=row['candidate_id'], kind='openalex_identity', url='https://api.openalex.org/works?' + urlencode({'search': row['canonical_title'], 'per-page': 3})))
        jobs.append(dict(candidate_id=row['candidate_id'], kind='crossref_identity', url='https://api.crossref.org/works?' + urlencode({'query.bibliographic': row['canonical_title'], 'rows': 3})))
    jobs = list({(j['candidate_id'], j['url']): j for j in jobs}.values())
    (OUT / 'jobs.json').write_text(json.dumps(jobs, indent=2) + '\n')
