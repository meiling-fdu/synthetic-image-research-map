#!/usr/bin/env python3
"""Specific primary checks for already-discovered survey references, no discovery."""
import json
from collect_systematic_literature import PROCESSED
from build_systematic_literature_pass2 import make_job

CHECKS = {
    'Attributing image generative models using latent fingerprints': 'https://proceedings.mlr.press/v202/nie23a.html',
    'Artificial fingerprinting for generative models: Rooting deepfake attribution in training data': 'https://openaccess.thecvf.com/content/ICCV2021/html/Yu_Artificial_Fingerprinting_for_Generative_Models_Rooting_Deepfake_Attribution_in_Training_ICCV_2021_paper.html',
    'Forensic analysis of synthetically generated western blot images': 'https://arxiv.org/abs/2112.08739',
    'Responsible disclosure of generative models using scalable fingerprinting': 'https://arxiv.org/abs/2012.08726',
}


def prepare():
    path = PROCESSED / 'primary_jobs.json'
    jobs = {r['url']: r for r in json.loads(path.read_text())}
    for title, url in CHECKS.items():
        if url not in jobs:
            job = make_job('EVIDENCE', 'primary_paper', title, url, {}, 'specific previously discovered reference verification', candidate_ids=[], url_provenance='Exact-title primary-source lookup during reconciliation; not a discovery pass')
            job['discovery_pass'] = 7
            jobs[url] = job
    path.write_text(json.dumps(list(jobs.values()), indent=2) + '\n')


if __name__ == '__main__':
    prepare()
