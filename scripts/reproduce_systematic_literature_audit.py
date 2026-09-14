#!/usr/bin/env python3
"""Repeat the offline pipeline and compare canonical audit artifacts byte-for-byte."""
import hashlib
import json
import subprocess
import sys
import shutil
import tempfile
from collect_systematic_literature import ROOT, PROCESSED
from report_systematic_literature import CANONICAL, REPORT


def reproduce():
    followup = ROOT / 'data/processed/systematic_tier1_2026_09'
    if (followup / 'insertion.json').exists():
        # Re-run the historical audit against its original corpus, in isolation.
        # Never let a later curation pass rewrite the completed audit decisions.
        with tempfile.TemporaryDirectory(prefix='historical-literature-audit-') as temp:
            frozen = __import__('pathlib').Path(temp)
            shutil.copytree(followup / 'baseline', frozen, dirs_exist_ok=True)
            shutil.copytree(ROOT / 'scripts', frozen / 'scripts')
            shutil.copytree(PROCESSED, frozen / 'data/processed/systematic_literature_2026_09', dirs_exist_ok=True)
            (frozen / 'data/raw').mkdir(exist_ok=True)
            for raw in (ROOT / 'data/raw').iterdir():
                destination = frozen / 'data/raw' / raw.name
                if not destination.exists():
                    destination.symlink_to(raw)
            subprocess.run([sys.executable, str(frozen / 'scripts/reproduce_systematic_literature_audit.py')], cwd=frozen, check=True)
            for original in (CANONICAL, REPORT):
                assert original.read_bytes() == (frozen / original.relative_to(ROOT)).read_bytes()
        print('Historical audit reproduced byte-for-byte from its frozen corpus.')
        return
    paths = [CANONICAL, REPORT] + [PROCESSED / name for name in
             ('audit_statistics.json', 'source_coverage.json', 'lineage_review.json')]
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    commands = [('verify_systematic_literature_sources.py', 'extract'),
                ('parse_systematic_literature.py',), ('reconcile_systematic_literature.py',),
                ('screen_systematic_literature.py',), ('report_systematic_literature.py',)]
    for command in commands:
        subprocess.run([sys.executable, str(ROOT / 'scripts' / command[0]), *command[1:]], cwd=ROOT, check=True)
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert before == after
    assert CANONICAL.read_bytes() == (PROCESSED / 'candidate_registry_draft.csv').read_bytes()
    result = {'byte_identical': True, 'sha256': after,
              'canonical_matches_regenerated_draft': True,
              'statistics_include': ['candidate counts', 'channel overlap', 'pass yields', 'survey outcomes', 'coverage counts']}
    (PROCESSED / 'reproducibility.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    reproduce()
