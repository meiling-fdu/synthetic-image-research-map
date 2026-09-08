"""Coverage is bibliography membership; reports must be reproducible together."""
import csv
import json
from pathlib import Path
from unittest.mock import patch

from scripts import audit_key_paper_coverage as audit
from scripts import refresh_public_preview as refresh
from scripts.admin_workflows import ALLOWED_WORKFLOWS, KNOWN_WORKFLOW_OUTPUTS
from scripts.paper_exclusions import PAPER_EXCLUSION_COLUMNS


def compute(keys, papers=(), markers=(), candidates=(), exclusions=()):
    return audit.compute_audit(keys, list(candidates), [], list(papers), list(markers), exclusions)


def test_markerless_is_covered_and_diagnostics_are_separate():
    paper = dict(title='An exact paper', doi='10.1/x', missing_affiliation=True)
    rows, totals, errors = compute([paper], [paper])
    assert not errors
    assert totals['bibliography_covered'] == 1
    assert rows[0]['coverage_status'] == 'covered_in_public_preview_paper_list'
    assert rows[0]['missing_affiliation'] == 'yes'
    assert rows[0]['map_record_count'] == '0'


def test_multiple_markers_count_one_paper():
    paper = dict(title='One paper', doi='10.1/x')
    rows, totals, errors = compute([paper], [paper], [paper, paper, paper])
    assert not errors
    assert totals['bibliography_covered'] == totals['unique_mapped_papers'] == 1
    assert rows[0]['map_record_count'] == '3'


def test_candidate_missing_excluded_and_fuzzy_are_distinct():
    keys = [dict(title=t, year='2024') for t in ('Candidate', 'Entirely absent work', 'Excluded', 'A study of synthetic generated image detection')]
    exclusion = dict(title='Excluded', year='2024', is_active='true', exclusion_reason='out_of_scope')
    rows, totals, _ = compute(keys, [dict(title='A study of synthetic generated images detection')], candidates=[keys[0]], exclusions=[exclusion])
    assert [r['coverage_status'] for r in rows] == ['candidate_only', 'missing_from_candidate_pool', 'excluded', 'possible_title_match_failure']
    assert totals['bibliography_covered'] == 0
    assert sum(totals[s] for s in audit.ALLOWED_STATUSES) == totals['key_papers']
    assert rows[-1]['manual_review'] == 'yes'


def test_identifier_priority_variants_and_conflicts():
    papers = [dict(title='Published title', doi='10.1/x', arxiv_id='2401.12345'), dict(title='Original title', doi='10.1/y')]
    rows, _, _ = compute([dict(title='Original title', doi='https://doi.org/10.1/X')], papers)
    assert rows[0]['matched_public_title'] == 'Published title'
    assert rows[0]['match_method'] == 'doi'
    rows, _, _ = compute([dict(title='Changed title', arxiv_id='https://arxiv.org/abs/2401.12345v2')], papers)
    assert rows[0]['match_method'] == 'arxiv'
    rows, _, _ = compute([dict(title='Published title', doi='10.1/conflict')], papers)
    assert rows[0]['in_public_preview'] == 'no'
    rows, _, _ = compute([dict(title='Same title')], [dict(title='Same title', doi='10.1/a'), dict(title='Same title', doi='10.1/b')])
    assert rows[0]['coverage_status'] == 'possible_title_match_failure'
    assert 'ambiguous' in rows[0]['identity_review']


def test_openalex_and_normalized_exact_title():
    rows, _, _ = compute([dict(title='Variant', openalex_url='https://openalex.org/W123')], [dict(title='Canonical', openalex_id='W123')])
    assert rows[0]['match_method'] == 'openalex'
    rows, _, _ = compute([dict(title='Real-world: image detection!')], [dict(title='Real world image detection')])
    assert rows[0]['match_method'] == 'title'


def test_marker_orphan_and_public_exclusion_are_errors():
    paper = dict(title='An excluded paper', year='2024')
    assert compute([], markers=[paper])[2]
    assert compute([], [paper], exclusions=[dict(paper, is_active='true')])[2]


def setup_inputs(root):
    paper = dict(title='Test paper', year='2024')
    for path in audit.INPUT_PATHS:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == '.json':
            target.write_text(json.dumps({'records': [paper] if path == audit.PREVIEW_PAPERS_JSON else []}))
        else:
            with target.open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=PAPER_EXCLUSION_COLUMNS if path == audit.EXCLUSIONS_PATH else list(paper))
                writer.writeheader()
                if path == audit.KEY_PATH:
                    writer.writerow(paper)
    artifacts, _, errors = audit.expected_artifacts(root)
    assert not errors
    for path, content in artifacts.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(content)


def test_stale_csv_markdown_counts_vocabulary_and_inputs(tmp_path):
    setup_inputs(tmp_path)
    assert not audit.validate_artifacts(tmp_path)
    for path in (audit.OUT_PATH, audit.MARKDOWN_PATH):
        original = (tmp_path / path).read_text()
        for changed in (original.replace('covered_in_public_preview_paper_list', 'not_covered_by_pipeline'), original + '\n', original.replace('Test paper', 'Different paper')):
            (tmp_path / path).write_text(changed)
            assert audit.validate_artifacts(tmp_path)
        (tmp_path / path).write_text(original)
    # Even a source change that leaves the totals unchanged invalidates the report.
    with (tmp_path / audit.KEY_PATH).open('a') as handle:
        handle.write('\n')
    assert audit.validate_artifacts(tmp_path)


def test_missing_input_fails_closed(tmp_path):
    setup_inputs(tmp_path)
    (tmp_path / audit.KEY_PATH).unlink()
    assert audit.validate_artifacts(tmp_path)


def test_workflow_reports_precede_validation_and_are_transaction_outputs():
    args = refresh.parse_args(['--skip-search', '--user-agent', 'test'])
    workflows = [[Path(s.command[1]).name for s in refresh.build_steps(args)], [Path(c[1]).name for c in ALLOWED_WORKFLOWS['full_refresh']]]
    workflows.append([Path(c[1]).name for c in ALLOWED_WORKFLOWS["export_preview"]])
    for names in workflows:
        for report in ('export_public_preview.py', 'report_public_preview.py', 'report_missing_author_mappings.py', 'audit_key_paper_coverage.py'):
            assert names.index(report) < names.index('validate_public_preview.py')
    assert audit.OUT_PATH in KNOWN_WORKFLOW_OUTPUTS
    assert audit.MARKDOWN_PATH in KNOWN_WORKFLOW_OUTPUTS


def test_refresh_failure_restores_all_reports(tmp_path):
    paths = (refresh.PREVIEW_JSON, refresh.PAPER_PREVIEW_JSON, refresh.QUALITY_REPORT, refresh.MAPPING_REPORT, refresh.MAPPING_REPORT_CSV, refresh.KEY_REPORT, refresh.KEY_REPORT_CSV)
    for path in paths:
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text('before')
    def fail(*args, **kwargs):
        for path in paths:
            (tmp_path / path).write_text('after')
        raise OSError('could not start validation')
    with patch.object(refresh, 'REPOSITORY_ROOT', tmp_path), patch.object(refresh.subprocess, 'run', fail):
        assert refresh.execute_steps([refresh.RefreshStep(1, 'fail', ['fake'])]) == 1
    assert all((tmp_path / path).read_text() == 'before' for path in paths)


def test_quality_report_uses_bibliography_identity_for_marker_variants():
    from scripts.report_public_preview import build_report
    paper = dict(title='One paper', doi='10.1/x', openalex_url='https://openalex.org/W1')
    markers = [paper, dict(title='One paper', doi='10.1/x')]
    report = build_report(Path('preview.json'), {}, markers, [paper])
    assert '| Unique mapped papers | 1 |' in report
    assert '| Map records | 2 |' in report
