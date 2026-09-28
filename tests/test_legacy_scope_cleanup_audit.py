"""Integrity tests for the non-destructive 76-paper legacy-scope audit."""

from __future__ import annotations

import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path

from scripts.legacy_scope_cleanup_audit import (
    ARTIFACT_HASH_PATH,
    CATEGORY_LABELS,
    CSV_PATH,
    FIELDS,
    HIGH_CONFIDENCE_PATH,
    IDENTITY_SUMMARY_PATH,
    NEEDS_REVIEW_PATH,
    REPORT_PATH,
    STATUS_VALUES,
    VALIDATION_PATH,
    category_summary,
    compare_baseline_files,
    generated_texts,
    high_confidence_rows,
    needs_review_rows,
    read_csv,
    reproduce,
    validate_rows,
    verify_baseline,
)
from scripts.build_legacy_audit import build_rows


def audit_rows() -> list[dict[str, str]]:
    rows = read_csv(CSV_PATH)
    assert tuple(rows[0]) == FIELDS
    return rows


def test_exact_bounded_queue_and_valid_statuses():
    rows = audit_rows()
    totals = validate_rows(rows)
    assert totals["reviewed"] == 76
    assert totals["unique_papers"] == 76
    assert len({row["candidate_identity"] for row in rows}) == 76
    assert sum(not row["paper_id"] for row in rows) == 46
    assert totals["identity_resolution"] == {
        "IDENTITY_RESOLVABLE_BY_STRONG_ID": 46,
        "INTERNAL_ID_RESOLVED": 30,
    }
    assert Counter(row["legacy_category"] for row in rows) == {
        "watermark_provenance": 3,
        "pure_deepfake": 71,
        "classical_manipulation": 2,
    }
    assert all(row["final_audit_status"] in STATUS_VALUES for row in rows)
    assert Counter(row["final_audit_status"] for row in rows) == {
        "LEGACY_KEEP_IN_SCOPE": 16,
        "LEGACY_SCOPE_DRIFT_HIGH_CONFIDENCE": 44,
        "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW": 16,
    }
    assert category_summary(rows) == {
        "watermark_provenance": {
            "reviewed": 3,
            "keep": 2,
            "high_confidence_drift": 1,
            "needs_review": 0,
        },
        "pure_deepfake": {
            "reviewed": 71,
            "keep": 14,
            "high_confidence_drift": 41,
            "needs_review": 16,
        },
        "classical_manipulation": {
            "reviewed": 2,
            "keep": 0,
            "high_confidence_drift": 2,
            "needs_review": 0,
        },
    }


def test_evidence_and_ambiguity_requirements_are_explicit():
    rows = audit_rows()
    for row in rows:
        assert row["primary_source"]
        assert row["decisive_datasets_tasks"]
        assert row["rationale"]
        if row["final_audit_status"] == "LEGACY_SCOPE_DRIFT_HIGH_CONFIDENCE":
            assert row["recommended_next_action"] == "MOVE_TO_EXCLUDED_ARCHIVE"
            assert not row["exact_evidence_needed"]
        elif row["final_audit_status"] == "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW":
            assert row["recommended_next_action"] == "FURTHER_PRIMARY_REVIEW"
            assert row["exact_evidence_needed"].endswith("?")
        else:
            assert row["recommended_next_action"] == "NO_ACTION"
            assert not row["exact_evidence_needed"]


def test_report_and_derived_queue_totals_come_from_csv():
    rows = audit_rows()
    summary = category_summary(rows)
    report = REPORT_PATH.read_text(encoding="utf-8")
    for category, values in summary.items():
        expected = (
            f"| {CATEGORY_LABELS[category]} | {values['reviewed']} | "
            f"{values['keep']} | {values['high_confidence_drift']} | "
            f"{values['needs_review']} |"
        )
        assert expected in report
    assert len(read_csv(HIGH_CONFIDENCE_PATH)) == len(high_confidence_rows(rows))
    assert len(read_csv(NEEDS_REVIEW_PATH)) == len(needs_review_rows(rows))
    assert read_csv(HIGH_CONFIDENCE_PATH) == high_confidence_rows(rows)
    assert read_csv(NEEDS_REVIEW_PATH) == needs_review_rows(rows)


def test_identity_resolution_is_strong_deterministic_and_conflict_free():
    rows = audit_rows()
    assert Counter(row["identity_match_method"] for row in rows) == {
        "paper_id": 30,
        "doi": 45,
        "openalex_id": 1,
    }
    assert all(row["strong_identifiers_agree"] == "true" for row in rows)
    assert all(row["identity_match_method"] != "normalized_title_year" for row in rows)
    idless = [row for row in rows if not row["paper_id"]]
    assert len(idless) == 46
    assert all(
        row["identity_resolution_status"] == "IDENTITY_RESOLVABLE_BY_STRONG_ID"
        for row in idless
    )
    receipt = json.loads(IDENTITY_SUMMARY_PATH.read_text(encoding="utf-8"))
    assert receipt["originally_idless_resolution"] == {
        "rows": 46,
        "doi": 45,
        "arxiv_id": 0,
        "openalex_id": 1,
    }
    assert receipt["conflicting_strong_identifiers"] == []
    assert receipt["weak_fuzzy_title_matching_required"] is False
    assert receipt["adaptprompt_resolution"] == {
        "source_diagnostic_identity": "title-sha256:a829f1665d646a9ae989",
        "resolution_basis": "openalex_id",
        "openalex_id": "W7117078863",
        "corroborating_arxiv_id": "2512.17730",
        "resolved_authoritative_identity": "arxiv:2512.17730",
    }


def test_guard_manifest_detects_a_protected_file_mutation():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        protected = root / "protected.txt"
        protected.write_text("baseline\n", encoding="utf-8")
        expected = {
            "protected.txt": hashlib.sha256(protected.read_bytes()).hexdigest(),
            "missing.txt": "0" * 64,
        }
        protected.write_text("mutated\n", encoding="utf-8")
        changed, missing = compare_baseline_files(expected, root)
        assert changed == ["protected.txt"]
        assert missing == ["missing.txt"]


def test_predecessor_receipt_distinguishes_inventory_from_verified_bytes():
    integrity = verify_baseline()
    assert integrity["manifest_entry_count"] == 4061
    assert "baseline_files_verified" not in integrity
    assert 0 < integrity["byte_verified_count"] < integrity["manifest_entry_count"]
    assert integrity["byte_verified_match_count"] == integrity["byte_verified_count"]
    assert integrity["byte_verified_mismatch_count"] == 0
    assert integrity["reconstructed_byte_verified_count"] == 3
    assert integrity["verification_scope"] == "stored_hash_relationship_with_partial_byte_verification"
    assert integrity["changed"] == []
    assert integrity["missing"] == []
    assert integrity["corpus_counts"] == {
        "public_papers": 666,
        "published_only": 555,
        "mapped_papers": 645,
        "map_markers": 1508,
    }


def test_all_audit_artifacts_reproduce_byte_for_byte_twice():
    rows = audit_rows()
    assert build_rows() == rows
    integrity = verify_baseline()
    expected = generated_texts(rows, integrity)
    current = {
        CSV_PATH.name: CSV_PATH.read_text(encoding="utf-8"),
        REPORT_PATH.name: REPORT_PATH.read_text(encoding="utf-8"),
        HIGH_CONFIDENCE_PATH.name: HIGH_CONFIDENCE_PATH.read_text(encoding="utf-8"),
        NEEDS_REVIEW_PATH.name: NEEDS_REVIEW_PATH.read_text(encoding="utf-8"),
        VALIDATION_PATH.name: VALIDATION_PATH.read_text(encoding="utf-8"),
        IDENTITY_SUMMARY_PATH.name: IDENTITY_SUMMARY_PATH.read_text(encoding="utf-8"),
        ARTIFACT_HASH_PATH.name: ARTIFACT_HASH_PATH.read_text(encoding="utf-8"),
    }
    for name in current:
        assert current[name] == expected[name]
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        first_hashes = reproduce(Path(first), rows, integrity)
        second_hashes = reproduce(Path(second), rows, integrity)
        assert first_hashes == second_hashes
