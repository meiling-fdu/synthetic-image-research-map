"""Evidence decisions resolve identities without bypassing corpus membership."""
import csv
import json

import pytest
from unittest.mock import patch

from scripts import audit_key_paper_coverage as audit
from scripts.key_paper_reconciliation import apply_decisions


def decision(key, **updates):
    return dict(checklist_row=1, checklist=key, classification='SAME_PAPER_METADATA_CONFLICT',
                resolved=updates, evidence_urls=['https://example.org/proceedings'],
                reason='Official version linkage verified.')


def test_explicit_correction_preserves_original_and_requires_public_membership():
    key = dict(title='Original title', year='2025', doi='10.1/bad')
    d = decision(key, doi='10.1/good')
    paper = dict(title='Published title', doi='10.1/good')
    rows, summary, errors = audit.compute_audit([key], [], [], [paper], [], [], [d])
    assert not errors
    assert rows[0]['title'] == key['title']
    assert rows[0]['matched_public_title'] == paper['title']
    assert summary['bibliography_covered'] == 1
    assert key['doi'] == '10.1/bad'
    assert audit.compute_audit([key], [], [], [], [], [], [d])[1]['bibliography_covered'] == 0


def test_stale_duplicate_or_unsupported_decisions_fail_closed():
    key = dict(title='Original', year='2025')
    d = decision(key, doi='10.1/x')
    for keys, decisions in [([dict(key, year='2026')], [d]), ([key], [d, d]),
                            ([key], [dict(d, evidence_urls=[])]),
                            ([key], [dict(d, classification='force_covered')]),
                            ([key], [dict(d, resolved={'tasks': 'detection'})])]:
        with pytest.raises(ValueError):
            apply_decisions(keys, decisions)


def test_distinct_rejection_is_specific_and_ambiguous_remains_review_only():
    key = dict(title='Detecting Generated Images by Real Images Only', year='2023')
    old = dict(title='Detecting Generated Images by Real Images', year='2022')
    d = dict(decision(key, arxiv_id='2311.00962'), classification='DISTINCT_PAPERS', rejected_titles=[old['title']])
    rows, _, _ = audit.compute_audit([key], [], [], [old], [], [], [d])
    assert rows[0]['coverage_status'] == 'missing_from_candidate_pool'
    d['classification'] = 'AMBIGUOUS'
    rows, _, _ = audit.compute_audit([key], [], [], [], [], [], [d])
    assert rows[0]['manual_review'] == 'yes'
    assert rows[0]['identity_review'] == d['reason']


def test_resolved_identity_recognizes_existing_exclusion():
    key = dict(title='Old title', year='2025')
    d = decision(key, doi='10.1/excluded')
    exclusion = dict(title='Published title', doi='10.1/excluded', is_active='true')
    rows, _, _ = audit.compute_audit([key], [], [], [], [], [exclusion], [d])
    assert rows[0]['coverage_status'] == 'excluded'


def test_all_targeted_additions_remain_unreviewed_and_have_no_inferred_geography():
    decisions = audit.load_json_records(audit.ROOT / audit.RECONCILIATION_PATH)
    additions = [d for d in decisions if d['action'] == 'added_needs_review']
    assert len(decisions) == 46
    assert len(additions) == 10
    papers = audit.load_csv(audit.ROOT / 'data/curated/papers.csv')
    mappings = audit.load_csv(audit.ROOT / 'data/curated/author_institution_mappings.csv')
    for d in additions:
        assert d['classification'] == 'MISSING_ADD'
        matches = [p for p in papers if p['paper_id'] == d['matched_record']['paper_id']]
        assert len(matches) == 1
        assert matches[0]['curation_status'] == 'needs_review'
        assert matches[0]['review_status'] == 'pending'
        assert not any(m['paper_id'] == matches[0]['paper_id'] for m in mappings)
        assert set(d['deduplication']) >= {'doi', 'arxiv', 'openalex', 'normalized_exact_title', 'method_acronym', 'bounded_fuzzy_candidates'}


def test_author_mapping_report_retains_key_designation_for_resolved_titles():
    from scripts import report_missing_author_mappings as mapping_report
    key = dict(title='Original title', year='2025')
    canonical_path = audit.ROOT / audit.KEY_PATH
    with patch.object(mapping_report, 'read_csv_rows', side_effect=lambda path, **kw: [key] if path == canonical_path else []), \
         patch.object(mapping_report, 'read_json_records', return_value=[]), \
         patch.object(audit, 'load_json_records', return_value=[decision(key, doi='10.1/published')]), \
         patch.object(mapping_report, 'build_report_rows', return_value=[]) as build, \
         patch.object(mapping_report, 'write_csv_report'), \
         patch.object(mapping_report, 'write_markdown_report'):
        assert mapping_report.main(['--key-papers', str(canonical_path)]) == 0
    assert build.call_args.args[4][0]['doi'] == '10.1/published'
