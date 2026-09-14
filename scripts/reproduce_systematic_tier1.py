#!/usr/bin/env python3
"""Repeat the standard offline refresh and compare final artifacts byte-for-byte."""
import hashlib
import json
import subprocess
import sys
from prepare_systematic_tier1 import ROOT, OUT

PATHS = [
    'data/manual/systematic_tier1_reconciliation_2026_09.csv',
    'docs/systematic_tier1_reconciliation_2026_09.md',
    'data/processed/systematic_tier1_2026_09/validation_data.json',
    'data/processed/systematic_tier1_2026_09/version_relationships.json',
    'web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json',
    'data/manual/key_paper_coverage_report.csv', 'docs/key_paper_coverage_report.md',
    'data/manual/missing_author_mappings_report.csv', 'docs/missing_author_mappings_report.md',
    'docs/public_preview_report.md',
]


def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in PATHS}


def main():
    before = hashes()
    commands = [
        ['refresh_public_preview.py', '--skip-search', '--user-agent', 'SyntheticImageResearchMap-Tier1Curation/1.0'],
        ['report_systematic_tier1_versions.py'], ['report_systematic_tier1.py'],
    ]
    for command in commands:
        subprocess.run([sys.executable, str(ROOT / 'scripts' / command[0]), *command[1:]], cwd=ROOT, check=True)
    after = hashes()
    result = {'byte_identical': before == after, 'changed': [p for p in before if before[p] != after[p]], 'sha256': after}
    (OUT / 'reproducibility.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    assert before == after, result['changed']
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
