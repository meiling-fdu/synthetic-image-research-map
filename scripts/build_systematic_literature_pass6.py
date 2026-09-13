#!/usr/bin/env python3
"""Official alternate proceedings and bounded primary dataset lineage checks."""
import json
from collect_systematic_literature import ROOT, PROCESSED
from build_systematic_literature_pass2 import make_job

LINEAGES = {
    'GenImage': 'GenImage:', 'GenImage++': 'Breaking Latent Prior Bias',
    'Community Forensics': 'Community Forensics:', 'FakeBench': 'FakeBench:',
    'ForensicHub': 'ForensicHub:', 'GIM': 'GIM:', 'OpenFake': 'OpenFake:',
    'UniAIDet': 'UniAIDet:', 'WildFake': 'WildFake:', 'Semi-Truths': 'Semi-Truths:',
    'Artifact': 'Artifact:', 'Synthbuster': 'Synthbuster:',
    'ImageAttributionBench': 'ImageAttributionBench:', 'SAFE': 'The SAFE Image',
    'ForenSynths': 'CNN-Generated Images Are Surprisingly', 'Chameleon': 'A Sanity Check for AI-generated Image Detection',
}


def build():
    jobs = []
    for year in (2024, 2025, 2026):
        jobs.append(make_job('A', 'neurips_index', f'ICLR {year} official proceedings', f'https://proceedings.iclr.cc/paper_files/paper/{year}', {}, 'complete official returned book index'))
    jobs.append(make_job('A', 'neurips_index', 'NeurIPS 2025 Main Conference', 'https://proceedings.neurips.cc/paper_files/paper/2025/vol38-main-conference', {}, 'complete official book; main/position/dataset tracks', url_provenance='Main Conference link in cached Creative AI book'))
    papers = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    for family, prefix in LINEAGES.items():
        for paper in papers:
            if paper['title'].casefold().startswith(prefix.casefold()):
                url = 'https://arxiv.org/abs/' + paper['arxiv_id'] if paper.get('arxiv_id') else paper.get('paper_url') or paper.get('primary_url')
                if url:
                    jobs.append(make_job('C', 'lineage_paper', family, url, {}, 'foundational dataset/benchmark primary paper; no arbitrary dataset users', paper_title=paper['title']))
    for job in jobs:
        job['discovery_pass'] = 6
    (PROCESSED / 'pass6_jobs.json').write_text(json.dumps(jobs, indent=2) + '\n')
    print(f'Prepared {len(jobs)} official index/lineage jobs')


if __name__ == '__main__':
    build()
