#!/usr/bin/env python3
"""Freeze the pre-curation state and prepare only the 16 authorized source checks."""
import csv
import gzip
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/systematic_tier1_2026_09'
RAW = ROOT / 'data/raw/systematic_tier1_2026_09'


def prepare():
    OUT.mkdir(exist_ok=True)
    RAW.mkdir(exist_ok=True)
    snapshot = OUT / 'baseline'
    if not (OUT / 'baseline_sha256.json').exists():
        hashes = {}
        for folder in ('data/curated', 'data/manual', 'web', 'docs'):
            for path in sorted((ROOT / folder).rglob('*')):
                if path.is_file():
                    rel = path.relative_to(ROOT)
                    hashes[str(rel)] = hashlib.sha256(path.read_bytes()).hexdigest()
                    target = snapshot / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, target)
        (OUT / 'baseline_sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    rows = [r for r in csv.DictReader((ROOT / 'data/manual/systematic_literature_completeness_candidates_2026_09.csv').open()) if r['final_status'] == 'CANDIDATE_ADD_HIGH_CONFIDENCE']
    assert len(rows) == 16
    (OUT / 'candidates.json').write_text(json.dumps(rows, indent=2) + '\n')
    evidence = json.loads((ROOT / 'data/processed/systematic_literature_2026_09/primary_evidence.json').read_text())
    jobs = []
    for row in rows:
        urls = row['primary_evidence_url'].split(' | ')
        for url in urls:
            jobs.append({'candidate_id': row['candidate_id'], 'kind': 'primary_html', 'url': url})
            for e in evidence:
                if e['primary_url'] != url:
                    continue
                body = gzip.decompress((ROOT / e['raw_path']).read_bytes()).decode(errors='replace')
                pdfs = re.findall(r'<meta[^>]*name="citation_pdf_url"[^>]*content="([^"]+)"', body)
                pdfs += re.findall(r'href="([^"]+\.pdf)"[^>]*>\s*(?:pdf|Paper)', body, re.I)
                if row['arxiv_id']:
                    pdfs.append('https://arxiv.org/pdf/' + row['arxiv_id'])
                for pdf in pdfs:
                    jobs.append({'candidate_id': row['candidate_id'], 'kind': 'primary_pdf', 'url': urljoin(url, pdf)})
    jobs = list({(j['candidate_id'], j['url']): j for j in jobs}.values())
    (OUT / 'jobs.json').write_text(json.dumps(jobs, indent=2) + '\n')
    print(f'Preserved baseline and prepared {len(jobs)} named-paper source requests.')


if __name__ == '__main__':
    prepare()
