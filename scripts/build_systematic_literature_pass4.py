#!/usr/bin/env python3
"""Bounded database fallback for venue/year gaps and primary survey download."""
import json
from urllib.parse import urlencode
from build_systematic_literature_pass2 import make_job
from collect_systematic_literature import PROCESSED, read_response

# IDs verified against the cached pass-three source lookup, not guessed IDs.
SOURCES = {'ICASSP': 'S4363607879', 'ICIP': 'S4306419523', 'WIFS': 'S4306420309',
           'AAAI': 'S4210191458', 'IJCAI': 'S4306419999', 'ICLR': 'S4306419637',
           'ICML': 'S4306419644', 'TIFS': 'S61310614', 'TMM': 'S137030581',
           'TIP': 'S4210173141', 'SPL': 'S120629676', 'TPAMI': 'S199944782',
           'IJCV': 'S25538012', 'Pattern Recognition': 'S414566',
           'Information Fusion': 'S7560371', 'Signal Processing Image Communication': 'S38090728',
           'IEEE Access': 'S2485537415', 'CVIU': 'S185008460', 'PR Letters': 'S151820558'}


def build():
    jobs = []
    for venue, source_id in SOURCES.items():
        for year in (2024, 2025, 2026):
            for term in ('synthetic image detection', 'image forgery attribution'):
                query = {'filter': f'primary_location.source.id:{source_id},from_publication_date:{year}-01-01,to_publication_date:' + (f'{year}-12-31' if year < 2026 else '2026-09-12'), 'search': term, 'per-page': 30}
                jobs.append(make_job('A', 'discovery_search', f'{venue} {year}', 'https://api.openalex.org/works?' + urlencode(query), query, 30, venue=venue, year=year, verified_source_id=source_id))
    # ACM proceedings IDs are year-specific; a generic source lookup returned 2022.
    # Use bounded title/abstract search and retain returned venues for review.
    for year in (2024, 2025, 2026):
        for venue in ('ACM Multimedia', 'NeurIPS', 'ECCV'):
            query = {'search': venue + ' AI generated image detection attribution', 'filter': f'from_publication_date:{year}-01-01,to_publication_date:' + (f'{year}-12-31' if year < 2026 else '2026-09-12'), 'per-page': 30}
            jobs.append(make_job('A', 'discovery_search', f'{venue} {year} keyword fallback', 'https://api.openalex.org/works?' + urlencode(query), query, 30, venue=venue, year=year, venue_filter_verified=False))
    for source in json.loads((PROCESSED / 'pass3_sources.json').read_text()):
        if source['kind'] == 'zenodo_metadata' and source['status'] == 200:
            record = json.loads(read_response(source))
            jobs.append(make_job('D', 'survey_pdf', source['seed'], record['files'][0]['links']['self'], {}, 'complete PDF bibliography; title gate', expected_checksum=record['files'][0]['checksum']))
    for job in jobs:
        job['discovery_pass'] = 4
    (PROCESSED / 'pass4_jobs.json').write_text(json.dumps(jobs, indent=2) + '\n')
    print(f'Prepared {len(jobs)} bounded pass-four jobs')


if __name__ == '__main__':
    build()
