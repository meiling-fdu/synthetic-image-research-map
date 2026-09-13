#!/usr/bin/env python3
"""Prepare source lookups, bounded lineage searches and primary survey sources."""
import json
from urllib.parse import urlencode
from build_systematic_literature_pass2 import make_job
from collect_systematic_literature import PROCESSED

VENUES = [
    'ACM Multimedia', 'ICASSP', 'International Conference on Image Processing',
    'International Workshop on Information Forensics and Security',
    'AAAI Conference on Artificial Intelligence', 'International Joint Conference on Artificial Intelligence',
    'International Conference on Learning Representations', 'International Conference on Machine Learning',
    'IEEE Transactions on Information Forensics and Security', 'IEEE Transactions on Multimedia',
    'IEEE Transactions on Image Processing', 'IEEE Signal Processing Letters',
    'IEEE Transactions on Pattern Analysis and Machine Intelligence', 'International Journal of Computer Vision',
    'Pattern Recognition', 'Information Fusion', 'Signal Processing Image Communication',
    'IEEE Access', 'Computer Vision and Image Understanding', 'Pattern Recognition Letters',
]
FAMILIES = ['GenImage', 'Chameleon AI image', 'Synthbuster', 'WildFake', 'Community Forensics',
            'GIM generative image manipulation', 'Semi-Truths', 'UniAIDet', 'SAFE Image Authenticity',
            'OpenFake', 'ForenSynths', 'Artifact synthetic image', 'ImageAttributionBench',
            'FakeBench', 'ForensicHub', 'NTIRE AI generated image detection']


def build():
    jobs = []
    for venue in VENUES:
        query = {'search': venue, 'per-page': 5}
        jobs.append(make_job('A', 'source_lookup', venue, 'https://api.openalex.org/sources?' + urlencode(query), query, 5))
    for family in FAMILIES:
        query = {'search': family, 'filter': 'to_publication_date:2026-09-12', 'per-page': 15}
        jobs.append(make_job('C', 'lineage_search', family, 'https://api.openalex.org/works?' + urlencode(query), query, 15))
    for kind, seed, url in [
        ('neurips_index', 'NeurIPS 2025 official current proceedings', 'https://papers.neurips.cc/paper_files/paper/2025'),
        ('ijcai_index', 'IJCAI 2024', 'https://www.ijcai.org/proceedings/2024/'),
        ('ijcai_index', 'IJCAI 2025', 'https://www.ijcai.org/proceedings/2025/'),
        ('ijcai_index', 'IJCAI 2026', 'https://www.ijcai.org/proceedings/2026/'),
        ('zenodo_metadata', 'Source Attribution of AI-Generated Images: a Principled Survey', 'https://zenodo.org/api/records/20814592'),
    ]:
        jobs.append(make_job('D' if kind == 'zenodo_metadata' else 'A', kind, seed, url, {}, 'complete returned source'))
    for job in jobs:
        job['discovery_pass'] = 3
    (PROCESSED / 'pass3_jobs.json').write_text(json.dumps(jobs, indent=2) + '\n')
    print(f'Prepared {len(jobs)} pass-three jobs')


if __name__ == '__main__':
    build()
