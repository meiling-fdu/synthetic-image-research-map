#!/usr/bin/env python3
"""Prepare bounded second-pass jobs entirely from saved seeds; no network."""
import json
from urllib.parse import urlencode
try:
    from .collect_systematic_literature import PROCESSED, read_response
except ImportError:
    from collect_systematic_literature import PROCESSED, read_response

CUTOFF = '2026-09-12'


def make_job(channel, kind, seed, url, query, bound, **extra):
    return dict(channel=channel, kind=kind, seed=seed, url=url, query=query,
                retrieval_bound=bound, discovery_pass=2,
                enumeration_level='BOUNDED_SEARCH', **extra)


def build():
    jobs = []
    for source in json.loads((PROCESSED / 'pass1_sources.json').read_text()):
        if source['kind'] != 'seed_metadata' or source['status'] != 200:
            continue
        paper = json.loads(read_response(source))
        ids = paper.get('referenced_works', [])
        for offset in range(0, len(ids), 40):
            query = {'filter': 'openalex_id:' + '|'.join(v.rsplit('/', 1)[-1] for v in ids[offset:offset + 40]),
                     'per-page': 50}
            jobs.append(make_job('B', 'reference_works', source['seed'],
                                 'https://api.openalex.org/works?' + urlencode(query), query, 40,
                                 direction='REFERENCES', reference_offset=offset,
                                 expected_seed_references=len(ids)))
        query = {'filter': 'cites:' + paper['id'].rsplit('/', 1)[-1] + ',to_publication_date:' + CUTOFF,
                 'sort': 'publication_date:desc', 'per-page': 50}
        jobs.append(make_job('B', 'citing_works', source['seed'],
                             'https://api.openalex.org/works?' + urlencode(query), query, 50,
                             direction='CITED_BY'))
    for venue, year in [('ICLR', 2024), ('ICLR', 2025), ('ICLR', 2026), ('NeurIPS', 2025), ('ICML', 2026)]:
        query = {'content.venueid': f'{venue}.cc/{year}/Conference', 'limit': 1000, 'offset': 0}
        jobs.append(make_job('A', 'openreview_index', f'{venue} {year}',
                             'https://api2.openreview.net/notes?' + urlencode(query), query, 1000,
                             year=year, expected_venue_id=query['content.venueid']))
    jobs.append(make_job('A', 'cvf_index', 'CVPR 2026 NTIRE Workshops',
                         'https://openaccess.thecvf.com/CVPR2026_workshops/NTIRE', {},
                         'complete returned workshop index'))
    output = PROCESSED / 'pass2_jobs.json'
    output.write_text(json.dumps(jobs, indent=2) + '\n')
    print(f'Prepared {len(jobs)} jobs in {output.relative_to(PROCESSED.parent.parent.parent)}')


if __name__ == '__main__':
    build()
