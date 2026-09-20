"""Policy-layer invariants; these tests do not apply any scope recommendation."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('tier2_policy_report', ROOT / 'scripts/report_systematic_tier2_policy.py')
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


def test_exact_selected_population_and_preserved_evidence():
    rows, registry = policy.load_inputs()
    policy.validate(rows, registry)
    assert len(rows) == 215
    assert {r['primary_policy_cluster'] for r in rows} == {p['cluster_id'] for p in registry['policies']}


def test_duplicate_or_omitted_candidate_is_rejected():
    rows, registry = policy.load_inputs()
    broken = copy.deepcopy(rows)
    broken[-1] = broken[0]
    with pytest.raises(AssertionError):
        policy.validate(broken, registry)


def test_tier1_or_tier3_substitution_is_rejected():
    rows, registry = policy.load_inputs()
    original = policy.read_csv(ROOT / registry['source'])
    # Read IDs/statuses only; do not review evidence outside the selected population.
    foreign_ids = [r['candidate_id'] for r in original if r['final_status'] != policy.SOURCE_STATUS]
    broken = copy.deepcopy(rows)
    broken[0]['candidate_id'] = foreign_ids[0]
    with pytest.raises(AssertionError):
        policy.validate(broken, registry)


def test_recommendation_must_match_canonical_policy():
    rows, registry = policy.load_inputs()
    broken = copy.deepcopy(rows)
    broken[0]['recommended_policy'] = 'MISSING_ADD'
    with pytest.raises(AssertionError):
        policy.validate(broken, registry)


def test_outcomes_are_disjoint_and_evidence_flags_do_not_double_count():
    rows, registry = policy.load_inputs()
    summary = policy.stats(rows, registry)
    assert sum(summary['total'][k] for k in policy.OUTCOMES) == 215
    for cluster in summary['clusters'].values():
        assert sum(cluster[k] for k in policy.OUTCOMES) == cluster['paper_count']
    assert sum(summary['causes'].values()) == 215
    assert summary['total']['additional_evidence_flags'] > summary['total']['PAPER_SPECIFIC_REVIEW']
    broken = copy.deepcopy(rows)
    row = next(r for r in broken if r['requires_user_decision'] == 'true')
    row['provisional_outcome'] = 'LIKELY_INCLUDE'
    with pytest.raises(AssertionError):
        policy.validate(broken, registry)


def test_report_and_summary_regenerate_from_canonical_registries():
    report, summary = policy.render(*policy.load_inputs())
    assert report == policy.REPORT.read_text()
    assert summary == (policy.PROCESSED / 'summary.json').read_text()
    parsed = json.loads(summary)
    for outcome in policy.OUTCOMES:
        assert f'| {outcome} | {parsed["total"][outcome]} |' in report
    for cluster, counts in parsed['clusters'].items():
        assert f'({counts["paper_count"]} papers)' in report
        assert f'id="policy-{cluster}"' in report


def test_generation_is_deterministic_and_does_not_write_manual_files(tmp_path):
    before = {p: p.read_bytes() for p in (policy.CANDIDATES, policy.POLICIES)}
    command = [sys.executable, str(ROOT / 'scripts/report_systematic_tier2_policy.py'), '--output-dir', str(tmp_path)]
    subprocess.run(command, check=True, capture_output=True)
    first = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    subprocess.run(command, check=True, capture_output=True)
    assert first == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert first[policy.REPORT.name] == policy.REPORT.read_bytes()
    assert before == {p: p.read_bytes() for p in before}


def test_pre_task_repository_files_are_byte_identical():
    assert policy.integrity()['changed_paths'] == []
