"""Integrity tests for the bounded 44-paper reversible exclusion migration."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from unittest.mock import patch
from collections import Counter
from pathlib import Path

from scripts.legacy_scope_exclusion_migration import (
    AUDIT_PATH,
    AUDIT_SOURCE,
    CATEGORY_COUNTS,
    EXCLUSIONS_PATH,
    LEDGER_FIELDS,
    LEDGER_PATH,
    PLAN_FIELDS,
    PLAN_PATH,
    PLAN_RECEIPT_PATH,
    PREDECESSOR_PATH,
    PUBLIC_MAP_PATH,
    PUBLIC_PAPERS_PATH,
    QUEUE_PATH,
    RECEIPT_FIELDS,
    REPORT_PATH,
    RESTORATION_RECEIPT_PATH,
    TEST_SUCCESSOR_MIGRATION_PATH,
    VALIDATION_SUMMARY_PATH,
    build_changed_files_manifest,
    build_ledger_and_validation,
    candidate_identifiers,
    check_current,
    csv_text,
    duplicate_active_groups,
    file_sha256,
    load_locked_plan,
    load_payload,
    parse_boolean,
    preservation_audit,
    public_identity,
    read_csv,
    read_exclusion_rows,
    reconstruct_predecessor,
    row_sha256,
    strong_public_matches,
    test_successor_migration_payload,
    test_successor_migration_text,
    validate_protected_snapshot,
)


ROOT = Path(__file__).resolve().parents[1]


def test_predecessor_receipt_counts_actual_historical_file_reads():
    from scripts.frozen_predecessor_666 import load_snapshot, verify_predecessor

    snapshot = load_snapshot()
    expected = {ROOT / name for name in snapshot["historical_artifact_sha256"]}
    opened = []
    read_bytes = Path.read_bytes

    def observed(path):
        opened.append(path)
        return read_bytes(path)

    with patch.object(Path, "read_bytes", observed):
        receipt = verify_predecessor()
    assert expected == set(opened)
    assert len(opened) == len(expected)
    assert receipt["byte_verified_count"] == len(opened) + 3
    assert receipt["manifest_entry_count"] == 4061


def test_historical_receipts_reproduce_with_explicit_partial_scope():
    from scripts.frozen_predecessor_666 import historical_verification_receipts
    from scripts.legacy_scope_exclusion_migration import HISTORICAL_VERIFICATION_PATH

    receipt = historical_verification_receipts()
    assert json.loads(HISTORICAL_VERIFICATION_PATH.read_text()) == receipt
    assert len(receipt["layers"]) == 9
    for layer in receipt["layers"].values():
        assert layer["result"] == "PASS"
        assert layer["byte_verified_count"] == layer["byte_verified_match_count"]
        assert layer["byte_verified_mismatch_count"] == 0
        assert layer["verification_scope"] in {
            "fully_byte_verified", "stored_hash_relationship_with_partial_byte_verification"
        }
        if layer["verification_scope"] == "fully_byte_verified":
            assert layer["manifest_entry_count"] == layer["byte_verified_count"]


def test_phase_a_queue_is_exact_bounded_and_disjoint():
    queue = read_csv(QUEUE_PATH)
    audit = read_csv(AUDIT_PATH)
    assert len(queue) == 44
    assert len({row["candidate_identity"] for row in queue}) == 44
    assert Counter(row["legacy_category"] for row in queue) == CATEGORY_COUNTS
    migration = {row["candidate_identity"] for row in queue}
    keep = {
        row["candidate_identity"]
        for row in audit
        if row["final_audit_status"] == "LEGACY_KEEP_IN_SCOPE"
    }
    needs = {
        row["candidate_identity"]
        for row in audit
        if row["final_audit_status"] == "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW"
    }
    assert len(keep) == len(needs) == 16
    assert not migration.intersection(keep)
    assert not migration.intersection(needs)
    assert not keep.intersection(needs)


def test_phase_a_identity_resolution_is_strong_and_one_to_one():
    plan, receipt, _ = load_locked_plan()
    assert tuple(plan[0]) == PLAN_FIELDS
    assert Counter(row["identity_resolution_status"] for row in plan) == {
        "IDENTITY_LOCKED": 44
    }
    assert Counter(row["identity_resolution_basis"] for row in plan) == {
        "paper_id": 13,
        "doi": 31,
    }
    assert Counter(row["authoritative_targets_found"] for row in plan) == {"1": 44}
    assert all(row["strong_identifiers_agree"] == "true" for row in plan)
    assert all(row["normalized_title_corroborates"] == "true" for row in plan)
    assert all(row["identity_resolution_basis"] != "normalized_title" for row in plan)
    assert receipt["fuzzy_title_matches"] == 0


def test_phase_a_plan_is_hash_locked_and_canonical():
    plan, receipt, _ = load_locked_plan()
    assert file_sha256(PLAN_PATH) == receipt["migration_plan_sha256"]
    assert file_sha256(QUEUE_PATH) == receipt["candidate_queue_sha256"]
    assert PLAN_PATH.read_text(encoding="utf-8-sig") == csv_text(plan, PLAN_FIELDS)
    assert receipt["rows"] == 44


def test_phase_a_exclusion_states_and_reactivation_history_are_explicit():
    plan, _, _ = load_locked_plan()
    assert Counter(row["pre_migration_exclusion_state"] for row in plan) == {
        "NO_EXISTING_EXCLUSION": 42,
        "EXISTING_INACTIVE_EXCLUSION": 1,
        "CONFLICTING_EXCLUSION_IDENTITY": 1,
    }
    assert Counter(row["proposed_migration_action"] for row in plan) == {
        "NEW_ACTIVE_EXCLUSION": 42,
        "REACTIVATE_EXISTING_EXCLUSION": 1,
        "BLOCK_EXCLUSION_CONFLICT": 1,
    }
    restored = next(
        row for row in plan
        if row["pre_migration_exclusion_state"] == "EXISTING_INACTIVE_EXCLUSION"
    )
    assert restored["existing_exclusion_id"] == "exclusion-b4c81bf833c64b808efdec040224d1f4"
    assert restored["existing_is_active"] == "false"
    assert restored["existing_restored_at"] == "2026-07-17T23:00:57Z"
    assert restored["existing_restore_note"] == "ML"
    assert restored["existing_reason"] == "deepfake_only_not_core"


def test_phase_a_predecessor_snapshot_freezes_protected_sets():
    _, _, snapshot = load_locked_plan()
    assert snapshot["counts"] == {
        "public_papers": 666,
        "published_only": 555,
        "mapped_papers": 645,
        "map_markers": 1508,
    }
    assert len(snapshot["target_public_papers"]) == 44
    assert len(snapshot["target_map_records"]) == 117
    assert len(snapshot["protected_sets"]["LEGACY_KEEP_IN_SCOPE"]) == 16
    assert len(snapshot["protected_sets"]["LEGACY_SCOPE_DRIFT_NEEDS_REVIEW"]) == 16


def test_phase_b_receipt_and_exclusion_state_are_consistent():
    plan, _, _ = load_locked_plan()
    receipts = read_csv(RESTORATION_RECEIPT_PATH)
    exclusions = read_exclusion_rows(EXCLUSIONS_PATH)
    assert tuple(receipts[0]) == RECEIPT_FIELDS
    assert len(receipts) == 43
    assert Counter(row["migration_action"] for row in receipts) == {
        "NEW_ACTIVE_EXCLUSION": 42,
        "REACTIVATED_EXCLUSION": 1,
    }
    assert len({row["exclusion_id"] for row in receipts}) == 43
    assert not duplicate_active_groups(exclusions)
    by_id = {row["exclusion_id"]: row for row in exclusions}
    assert all(parse_boolean(by_id[row["exclusion_id"]]["is_active"]) for row in receipts)
    restored = next(row for row in receipts if row["migration_action"] == "REACTIVATED_EXCLUSION")
    final = by_id[restored["exclusion_id"]]
    assert restored["prior_active_state"] == "false"
    assert restored["prior_restored_at"] == final["restored_at"] == "2026-07-17T23:00:57Z"
    assert restored["prior_restore_note"] == final["restore_note"] == "ML"
    assert "legacy_scope_cleanup_audit_2026_09" in final["review_note"]


def test_migrated_papers_are_suppressed_but_source_identities_are_retained():
    plan, _, snapshot = load_locked_plan()
    papers = load_payload(PUBLIC_PAPERS_PATH)["records"]
    maps = load_payload(PUBLIC_MAP_PATH)["records"]
    curated = read_csv(ROOT / "data/curated/papers.csv")
    taxonomy = read_csv(ROOT / "data/curated/paper_taxonomy.csv")
    for row in plan:
        if row["proposed_migration_action"].startswith("BLOCK_"):
            assert len(strong_public_matches(row, papers)) == 1
            assert strong_public_matches(row, maps)
        else:
            assert not strong_public_matches(row, papers)
            assert not strong_public_matches(row, maps)
        # The historical taxonomy registry retains every migrated scientific
        # identity. Rows with an internal curated ID must also remain in the
        # curated paper table itself.
        assert strong_public_matches(row, taxonomy), row["title"]
        if row["resolved_paper_id"]:
            assert strong_public_matches(row, curated), row["title"]
    assert len(snapshot["target_public_papers"]) == 44


def test_keep_and_needs_review_sets_remain_byte_equivalent_in_public_outputs():
    _, _, snapshot = load_locked_plan()
    papers = load_payload(PUBLIC_PAPERS_PATH)["records"]
    maps = load_payload(PUBLIC_MAP_PATH)["records"]
    assert validate_protected_snapshot(
        snapshot["protected_sets"]["LEGACY_KEEP_IN_SCOPE"], papers, maps
    ) == []
    assert validate_protected_snapshot(
        snapshot["protected_sets"]["LEGACY_SCOPE_DRIFT_NEEDS_REVIEW"], papers, maps
    ) == []


def test_curated_and_historical_files_are_preserved():
    _, _, snapshot = load_locked_plan()
    result = preservation_audit(snapshot)
    assert result["protected_authoritative_changed"] == []
    assert result["historical_artifacts_changed"] == []


def test_predecessor_666_state_reconstructs_byte_for_byte():
    _, _, snapshot = load_locked_plan()
    with tempfile.TemporaryDirectory() as directory:
        hashes = reconstruct_predecessor(Path(directory))
    assert hashes == snapshot["source_hashes"]


def test_ledger_report_and_validation_are_generated_from_locked_sources():
    ledger, report, validation = build_ledger_and_validation()
    assert tuple(ledger[0]) == LEDGER_FIELDS
    assert len(ledger) == 44
    assert LEDGER_PATH.read_text(encoding="utf-8-sig") == csv_text(ledger, LEDGER_FIELDS)
    assert REPORT_PATH.read_text(encoding="utf-8") == report
    assert json.loads(VALIDATION_SUMMARY_PATH.read_text(encoding="utf-8")) == validation
    assert Counter(row["migration_action"] for row in ledger) == {
        "NEW_ACTIVE_EXCLUSION": 42,
        "REACTIVATED_EXCLUSION": 1,
        "MIGRATION_CONFLICT_BLOCKED": 1,
    }
    blocked = [row for row in ledger if row["remaining_issue"]]
    assert len(blocked) == 1
    assert blocked[0]["migration_action"] == "MIGRATION_CONFLICT_BLOCKED"
    assert check_current() == validation


def test_changed_files_manifest_classifies_every_path_once():
    manifest = build_changed_files_manifest()
    assert manifest["groups"]["unclassified"] == []
    assert manifest["group_integrity"] == {
        "all_entries_classified": True,
        "duplicate_group_entries": [],
        "classified_entry_count": manifest["counts"][
            "reported_entries"
        ],
    }
    assert "data/processed/legacy_scope_exclusion_migration_2026_09/changed_files_manifest.json" in manifest["groups"]["D_migration_restoration_and_audit_artifacts"]


def test_successor_test_migration_receipt_is_generated_and_hash_locked():
    expected_text = test_successor_migration_text()
    assert TEST_SUCCESSOR_MIGRATION_PATH.read_text(encoding="utf-8") == expected_text
    assert json.loads(expected_text) == test_successor_migration_payload()

    receipt = test_successor_migration_payload()
    assert len(receipt["changes"]) == 10
    assert len({row["file"] for row in receipt["changes"]}) == 10
    assert receipt["authoritative_data_changed_to_satisfy_tests"] is False

    reproducibility = json.loads(
        (ROOT / "data/processed/legacy_scope_exclusion_migration_2026_09/reproducibility.json").read_text(
            encoding="utf-8"
        )
    )
    relative = TEST_SUCCESSOR_MIGRATION_PATH.relative_to(ROOT).as_posix()
    assert relative in reproducibility["path_groups"]["migration_outputs"]
    assert reproducibility["sha256"][relative] == file_sha256(
        TEST_SUCCESSOR_MIGRATION_PATH
    )
