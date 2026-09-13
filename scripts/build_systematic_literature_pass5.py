#!/usr/bin/env python3
"""Independent bounded Crossref fallback and dataset-author lineage sources."""
import json
from urllib.parse import urlencode
from collect_systematic_literature import PROCESSED, read_response
from build_systematic_literature_pass2 import make_job


def build():
    jobs = []
    for source in json.loads((PROCESSED / 'pass3_sources.json').read_text()):
        if source['kind'] != 'source_lookup' or source['status'] != 200:
            continue
        matches = json.loads(read_response(source)).get('results', [])
        if not matches or not matches[0].get('issn') or source['seed'] in {'ACM Multimedia', 'International Conference on Image Processing', 'AAAI Conference on Artificial Intelligence'}:
            continue
        record = matches[0]
        for year in (2024, 2025, 2026):
            query = {'filter': f'issn:{record["issn"][0]},from-pub-date:{year}-01-01,until-pub-date:' + (f'{year}-12-31' if year < 2026 else '2026-09-12'), 'query.title': 'generated image detection attribution manipulation', 'rows': 20}
            jobs.append(make_job('A', 'crossref_search', record['display_name'] + f' {year}', 'https://api.crossref.org/works?' + urlencode(query), query, 20, venue=record['display_name'], year=year))
    for year in (2024, 2025, 2026):
        query = {'filter': f'type:proceedings-article,from-pub-date:{year}-01-01,until-pub-date:' + (f'{year}-12-31' if year < 2026 else '2026-09-12'), 'query.container-title': f'ACM International Conference on Multimedia', 'query.title': 'generated image detection attribution', 'rows': 40}
        jobs.append(make_job('A', 'crossref_search', f'ACM MM {year} bounded container query', 'https://api.crossref.org/works?' + urlencode(query), query, 40, venue='ACM MM', year=year, venue_filter_verified=False))
    for family, url in [
        ('GenImage', 'https://github.com/GenImage-Dataset/GenImage'),
        ('GenImage++', 'https://huggingface.co/datasets/Lunahera/genimagepp'),
    ]:
        jobs.append(make_job('C', 'lineage_primary', family, url, {}, 'author dataset overview and linked original/associated works'))
    for job in jobs:
        job['discovery_pass'] = 5
    (PROCESSED / 'pass5_jobs.json').write_text(json.dumps(jobs, indent=2) + '\n')
    print(f'Prepared {len(jobs)} independent fallback/lineage jobs')


if __name__ == '__main__':
    build()
