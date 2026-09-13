#!/usr/bin/env python3
"""Repeat the offline pipeline and compare canonical audit artifacts byte-for-byte."""
import hashlib
import json
import subprocess
import sys
from collect_systematic_literature import ROOT, PROCESSED
from report_systematic_literature import CANONICAL, REPORT


def reproduce():
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
