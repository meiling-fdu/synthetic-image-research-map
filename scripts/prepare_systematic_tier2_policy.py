#!/usr/bin/env python3
"""Freeze existing files and extract only the 215 unresolved policy candidates."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/systematic_tier2_policy_2026_09'
SOURCE = ROOT / 'data/manual/systematic_literature_completeness_candidates_2026_09.csv'
STATUS = 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW'


def selected():
    with SOURCE.open(newline='', encoding='utf-8-sig') as handle:
        rows = [r for r in csv.DictReader(handle) if r['final_status'] == STATUS]
    assert len(rows) == 215 and len({r['candidate_id'] for r in rows}) == 215
    return sorted(rows, key=lambda r: r['candidate_id'])


def main():
    rows = selected()
    OUT.mkdir(parents=True, exist_ok=True)
    baseline = OUT / 'baseline_sha256.json'
    if not baseline.exists():
        paths = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
        hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sorted(set(paths))
                  if (ROOT / p).is_file() and 'systematic_tier2' not in p}
        baseline.write_text(json.dumps(hashes, indent=2, sort_keys=True) + '\n')
    inventory = OUT / 'inventory.json'
    value = json.dumps(rows, indent=2, ensure_ascii=False) + '\n'
    if inventory.exists():
        assert inventory.read_text() == value
    else:
        inventory.write_text(value)
    print(f'{len(rows)} Tier 2 candidates; original decisions are read-only.')


if __name__ == '__main__':
    main()
