#!/usr/bin/env python3
"""Collect final validation evidence without changing curated/manual records."""
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from prepare_systematic_tier1 import ROOT, OUT


def main():
    suite = ET.parse(OUT / 'full_suite.xml').getroot().find('testsuite')
    results = {k: int(suite.get(k)) for k in ('tests', 'errors', 'failures', 'skipped')}
    results['passed'] = results['tests'] - results['errors'] - results['failures'] - results['skipped']
    assert results['passed'] >= 1458 and not any(results[k] for k in ('errors', 'failures', 'skipped'))
    focused = ET.parse(OUT / 'focused_validation.xml').getroot().find('testsuite')
    focused_results = {k: int(focused.get(k)) for k in ('tests', 'errors', 'failures', 'skipped')}
    assert not any(focused_results[k] for k in ('errors', 'failures', 'skipped'))
    validators = {}
    for name, file in [('curated', 'curated_validation.txt'), ('exclusion', 'exclusion_validation.txt'), ('public', 'public_validation.txt')]:
        content = (OUT / file).read_text()
        errors = list(map(int, re.findall(r'^Errors: (\d+)', content, re.M)))
        warnings = list(map(int, re.findall(r'^Warnings: (\d+)', content, re.M)))
        assert errors and not any(errors), name
        validators[name] = {'errors': sum(errors), 'warnings': sum(warnings)}
    reproduction = json.loads((OUT / 'reproducibility.json').read_text())
    assert reproduction['byte_identical']
    final_refresh_errors = list(map(int, re.findall(r'^Errors: (\d+)', (OUT / 'reproduction_log.txt').read_text(), re.M)))
    assert final_refresh_errors and not any(final_refresh_errors)
    identities = json.loads((OUT / 'final_identity_audit.json').read_text())
    assert not identities['duplicate_identifier_or_normalized_title_groups']
    locations = json.loads((OUT / 'final_location_audit.json').read_text())
    assert len(locations['markerless_new_papers']) == 6
    assert len(locations['authors_without_verified_institutional_mappings']) == 13
    assert 'Historical audit reproduced byte-for-byte' in (OUT / 'historical_reproduction.txt').read_text()
    preservation = json.loads((OUT / 'existing_public_diff.json').read_text())
    assert not preservation['pre_existing_public_changes']
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    value = {'full_suite': results, 'focused_tests': focused_results, 'validators': validators, 'artifact_reproducibility': True,
             'final_identity_audit': identities,
             'final_location_audit': locations,
             'historical_audit_reproduces': True, 'public_preservation': preservation,
             'git_diff_check_exit': diff.returncode, 'test_environment': 'System Python 3.9 with pytest; bundled Node; localhost bindings permitted',
             'corpus_and_strict_diff': json.loads((OUT / 'validation_data.json').read_text()),
             'source_integrity': json.loads((OUT / 'source_integrity.json').read_text()),
             'committed': False, 'pushed': False}
    (OUT / 'final_validation.json').write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'full_suite': results, 'validators': validators, 'artifact_reproducibility': True}, indent=2))


if __name__ == '__main__':
    main()
