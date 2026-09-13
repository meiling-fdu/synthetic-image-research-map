#!/usr/bin/env python3
"""Record completed audit validation without touching frozen corpus files."""
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collect_systematic_literature import ROOT, PROCESSED
from report_systematic_literature import CANONICAL, REPORT, accounting, read_csv, render, generate


def verify():
    baseline = json.loads((PROCESSED / 'baseline_sha256.json').read_text())
    changed = [path for path, sha in baseline.items()
               if not (ROOT / path).exists() or hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != sha]
    validators = {}
    for name in ('public', 'curated', 'exclusion'):
        output = (PROCESSED / (name + '_validation.txt')).read_text()
        validators[name] = {'errors': sum(map(int, re.findall(r'^Errors: (\d+)', output, re.M))),
                            'warnings': sum(map(int, re.findall(r'^Warnings: (\d+)', output, re.M)))}
        assert re.search(r'^Errors:', output, re.M)
    suite = ET.parse(PROCESSED / 'full_suite.xml').getroot().find('testsuite')
    results = {k: int(suite.get(k)) for k in ('tests', 'errors', 'failures', 'skipped')}
    results['passed'] = results['tests'] - results['errors'] - results['failures'] - results['skipped']
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    data = read_csv(CANONICAL)
    report_reproduces = REPORT.read_text() == render(data, accounting(data), CANONICAL)
    draft_reproduces = CANONICAL.read_bytes() == (PROCESSED / 'candidate_registry_draft.csv').read_bytes()
    value = {'frozen_files_checked': len(baseline), 'changed_frozen_files': changed,
             'authoritative_corpus_changed': bool(changed), 'validators': validators,
             'full_suite': results, 'report_reproduces': report_reproduces,
             'canonical_reproduces_from_cached_screening': draft_reproduces,
             'git_diff_check_exit': diff.returncode,
             'public_sha256': {name: hashlib.sha256((ROOT / 'web/data' / name).read_bytes()).hexdigest()
                               for name in ('public_preview_papers.json', 'public_preview_map_data.json')},
             'test_command': 'env PATH=<bundled-node-bin>:/opt/homebrew/bin:/usr/bin:/bin /usr/bin/python3 -m pytest -q --junitxml=data/processed/systematic_literature_2026_09/full_suite.xml',
             'test_environment': 'System Python 3.9 with installed pytest; bundled Node on PATH; localhost test-server binding permitted.'}
    value['initial_full_suite'] = {'passed': 1449, 'failed': 1,
        'cause': 'Report generator was edited after pytest collection; the loaded generator differed from the regenerated report. Initial log/XML retained; final rerun uses frozen generator and artifacts.'}
    value['offline_artifacts_byte_identical'] = json.loads((PROCESSED / 'reproducibility.json').read_text())['byte_identical']
    assert not changed and not diff.returncode and report_reproduces and draft_reproduces
    assert not results['errors'] and not results['failures'] and results['passed'] >= 1440
    assert all(v['errors'] == 0 for v in validators.values())
    (PROCESSED / 'validation.json').write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    generate()
    assert REPORT.read_text() == render(data, accounting(data), CANONICAL)
    print(json.dumps(value, indent=2))


if __name__ == '__main__':
    verify()
