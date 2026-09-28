#!/usr/bin/env python3
"""Plan, apply, and verify the bounded September 2026 legacy-scope migration.

The migration is deliberately split into a read-only Phase A and a separately
invoked Phase B.  The 44-paper queue is never rediscovered from taxonomy, and
public/title matching is never used as an exclusion identity.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import re
import subprocess
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from .curated_schema import PAPER_EXCLUSION_COLUMNS
    from .paper_exclusions import (
        all_identity_keys,
        normalize_arxiv_id,
        normalize_doi,
        normalize_openalex_url,
        normalize_title,
        parse_boolean,
        read_exclusion_rows,
        write_exclusion_rows,
    )
except ImportError:
    from curated_schema import PAPER_EXCLUSION_COLUMNS
    from paper_exclusions import (
        all_identity_keys,
        normalize_arxiv_id,
        normalize_doi,
        normalize_openalex_url,
        normalize_title,
        parse_boolean,
        read_exclusion_rows,
        write_exclusion_rows,
    )


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = (
    ROOT / "data/processed/legacy_scope_cleanup_2026_09/high_confidence_scope_drift.csv"
)
AUDIT_PATH = ROOT / "data/manual/legacy_scope_cleanup_audit_2026_09.csv"
EXCLUSIONS_PATH = ROOT / "data/curated/paper_exclusions.csv"
PUBLIC_PAPERS_PATH = ROOT / "web/data/public_preview_papers.json"
PUBLIC_MAP_PATH = ROOT / "web/data/public_preview_map_data.json"
BASELINE_EXPECTATIONS_PATH = ROOT / "tests/baseline_expectations.py"
OUT = ROOT / "data/processed/legacy_scope_exclusion_migration_2026_09"
PLAN_PATH = OUT / "migration_plan.csv"
PLAN_RECEIPT_PATH = OUT / "migration_plan_receipt.json"
PREDECESSOR_PATH = OUT / "predecessor_666_snapshot.json"
RESTORATION_RECEIPT_PATH = OUT / "restoration_receipt.csv"
VALIDATION_EVIDENCE_PATH = OUT / "validation_evidence.json"
VALIDATION_SUMMARY_PATH = OUT / "validation_summary.json"
REPRODUCIBILITY_PATH = OUT / "reproducibility.json"
CHANGED_MANIFEST_PATH = OUT / "changed_files_manifest.json"
TEST_SUCCESSOR_MIGRATION_PATH = OUT / "test_successor_migration.json"
HISTORICAL_VERIFICATION_PATH = OUT / "historical_verification.json"
TAXONOMY_SUMMARY_PATH = OUT / "taxonomy_current_counts.json"
LEDGER_PATH = ROOT / "data/manual/legacy_scope_exclusion_migration_2026_09.csv"
REPORT_PATH = ROOT / "docs/legacy_scope_exclusion_migration_2026_09.md"

AUDIT_SOURCE = "legacy_scope_cleanup_audit_2026_09"
MIGRATION_TIMESTAMP = "2026-09-27T11:20:56Z"
MIGRATION_NAMESPACE = uuid.UUID("4d465d34-5433-4e2d-8c63-b56b599efed6")

PREDECESSOR_COUNTS = {
    "public_papers": 666,
    "published_only": 555,
    "mapped_papers": 645,
    "map_markers": 1508,
}

CATEGORY_COUNTS = {
    "watermark_provenance": 1,
    "pure_deepfake": 41,
    "classical_manipulation": 2,
}

CATEGORY_LABELS = {
    "watermark_provenance": "watermark/provenance",
    "pure_deepfake": "deepfake/face/video",
    "classical_manipulation": "classical manipulation",
}

PLAN_FIELDS = (
    "audit_candidate",
    "resolved_paper_id",
    "resolved_authoritative_identity",
    "title",
    "doi",
    "arxiv_id",
    "openalex_id",
    "category",
    "identity_resolution_basis",
    "identity_resolution_status",
    "authoritative_targets_found",
    "strong_identifiers_agree",
    "normalized_title_corroborates",
    "pre_migration_exclusion_state",
    "existing_exclusion_id",
    "existing_is_active",
    "existing_restored_at",
    "existing_restore_note",
    "existing_reason",
    "existing_source",
    "exclusion_match_identifiers",
    "proposed_migration_action",
    "proposed_exclusion_id",
    "publication_type",
    "pre_migration_marker_count",
    "blocking_issue",
)

RECEIPT_FIELDS = (
    "paper_id",
    "resolved_authoritative_identity",
    "exclusion_id",
    "prior_exclusion_existence",
    "prior_active_state",
    "prior_restored_at",
    "prior_restore_note",
    "prior_reason",
    "prior_review_note",
    "prior_exclusion_row_sha256",
    "migration_action",
    "audit_source",
    "resulting_active_state",
    "future_restoration_action",
)

LEDGER_FIELDS = (
    "audit_candidate",
    "title",
    "resolved_paper_id",
    "resolved_authoritative_identity",
    "doi",
    "arxiv_id",
    "openalex_id",
    "category",
    "audit_evidence_reference",
    "decisive_audit_evidence",
    "identity_basis",
    "pre_migration_exclusion_state",
    "migration_action",
    "final_exclusion_id",
    "final_is_active",
    "public_suppression_status",
    "map_suppression_status",
    "restoration_receipt_status",
    "remaining_issue",
)

ALLOWED_PLAN_ACTIONS = {
    "NEW_ACTIVE_EXCLUSION",
    "REACTIVATE_EXISTING_EXCLUSION",
    "NOOP_ALREADY_ACTIVE",
    "BLOCK_IDENTITY",
    "BLOCK_EXCLUSION_CONFLICT",
}

ALLOWED_FINAL_ACTIONS = {
    "NEW_ACTIVE_EXCLUSION",
    "REACTIVATED_EXCLUSION",
    "ALREADY_ACTIVE",
    "MIGRATION_IDENTITY_BLOCKED",
    "MIGRATION_CONFLICT_BLOCKED",
}

PROTECTED_AUTHORITATIVE_PATHS = (
    "data/curated/papers.csv",
    "data/curated/paper_taxonomy.csv",
    "data/curated/author_institution_mappings.csv",
    "data/curated/institutions.csv",
    "data/curated/institution_aliases.csv",
    "data/curated/institution_hierarchy.csv",
    "data/curated/institution_locations.csv",
    "data/curated/institution_location_review.csv",
    "data/curated/institution_search_relationships.csv",
    "data/curated/venue_aliases.csv",
)

REPRODUCTION_PATH_GROUPS = {
    "locked_phase_a": (
        "data/processed/legacy_scope_exclusion_migration_2026_09/migration_plan.csv",
        "data/processed/legacy_scope_exclusion_migration_2026_09/migration_plan_receipt.json",
        "data/processed/legacy_scope_exclusion_migration_2026_09/predecessor_666_snapshot.json",
    ),
    "migration_outputs": (
        "data/processed/legacy_scope_exclusion_migration_2026_09/historical_verification.json",
        "data/processed/legacy_scope_exclusion_migration_2026_09/taxonomy_current_counts.json",
        "data/processed/legacy_scope_exclusion_migration_2026_09/restoration_receipt.csv",
        "data/processed/legacy_scope_exclusion_migration_2026_09/test_successor_migration.json",
        "data/manual/legacy_scope_exclusion_migration_2026_09.csv",
        "docs/legacy_scope_exclusion_migration_2026_09.md",
        "data/processed/legacy_scope_exclusion_migration_2026_09/validation_summary.json",
    ),
    "public_outputs": (
        "web/data/public_preview_papers.json",
        "web/data/public_preview_map_data.json",
    ),
    "successor_reports": (
        "data/processed/institution_type_audit.csv",
        "data/manual/key_paper_coverage_report.csv",
        "data/manual/missing_author_mappings_report.csv",
        "docs/key_paper_coverage_report.md",
        "docs/missing_author_mappings_report.md",
        "docs/public_preview_report.md",
    ),
}

MANIFEST_IMPLEMENTATION_PATHS = {
    "scripts/audit_key_paper_coverage.py",
    "scripts/export_public_preview.py",
    "scripts/migrate_paper_taxonomy.py",
    "scripts/paper_taxonomy_registry.py",
    "scripts/verify_key_paper_reconciliation.py",
}

MANIFEST_SUCCESSOR_OUTPUT_PATHS = {
    "data/manual/key_paper_coverage_report.csv",
    "data/manual/missing_author_mappings_report.csv",
    "data/processed/institution_type_audit.csv",
    "docs/key_paper_coverage_report.md",
    "docs/missing_author_mappings_report.md",
    "docs/public_preview_report.md",
    "web/data/public_preview_map_data.json",
    "web/data/public_preview_papers.json",
}

MANIFEST_AUDIT_ARTIFACT_PATHS = {
    "data/manual/legacy_scope_cleanup_audit_2026_09.csv",
    "data/manual/legacy_scope_exclusion_migration_2026_09.csv",
    "docs/legacy_scope_cleanup_audit_2026_09.md",
    "docs/legacy_scope_exclusion_migration_2026_09.md",
    "scripts/legacy_scope_exclusion_migration.py",
}

MANIFEST_HISTORICAL_SUPPORT_PATHS = {
    "docs/systematic_tier2_normal_priority_evidence_review_2026_09.md",
    "scripts/build_legacy_audit.py",
    "scripts/frozen_predecessor_666.py",
    "scripts/legacy_scope_cleanup_audit.py",
    "scripts/report_systematic_tier2_application.py",
    "scripts/report_systematic_tier2_normal_priority_evidence.py",
    "scripts/report_systematic_tier2_policy.py",
}

TEST_SUCCESSOR_CHANGES = (
    {
        "classification": "CURRENT_SUCCESSOR_EXPECTATION",
        "file": "tests/baseline_expectations.py",
        "new_source_of_truth": "current generated public paper and map outputs",
        "old_assumption": "the current public corpus was the 666-paper NORMAL evidence successor",
        "reason": "repository-wide current-count invariants must describe the 623-paper successor",
    },
    {
        "classification": "HISTORICAL_SNAPSHOT_REDIRECT",
        "file": "tests/test_author_affiliation_evidence_repairs.py",
        "new_source_of_truth": "hash-verified frozen 666-paper predecessor public records",
        "old_assumption": "historically reviewed author records were always present in the current public export",
        "reason": "active exclusions change visibility without invalidating the completed author-evidence review",
    },
    {
        "classification": "HISTORICAL_SNAPSHOT_REDIRECT",
        "file": "tests/test_formal_publication_authors.py",
        "new_source_of_truth": "hash-verified frozen 666-paper predecessor public and map records",
        "old_assumption": "formal-publication audit fixtures were always present in current public outputs",
        "reason": "the audit must continue to verify retained author and location curation after public suppression",
    },
    {
        "classification": "EXCLUSION_AWARE_INVARIANT",
        "file": "tests/test_frontend_paper_details.py",
        "new_source_of_truth": "verified retained author/affiliation fixture independent of current public membership",
        "old_assumption": "an excluded deepfake survey had to remain public to test author disclosure rendering",
        "reason": "the renderer contract is independent of whether its historical fixture is publicly visible",
    },
    {
        "classification": "CURRENT_SUCCESSOR_EXPECTATION",
        "file": "tests/test_frontend_published_only_filter.py",
        "new_source_of_truth": "current generated publication-type totals",
        "old_assumption": "the current export contained 666 papers and 555 published works",
        "reason": "filter counts must match the current 623-paper successor",
    },
    {
        "classification": "CURRENT_SUCCESSOR_EXPECTATION",
        "file": "tests/test_frontend_venue_filters.py",
        "new_source_of_truth": "the exact venue-track sets and labels represented in the current public export",
        "old_assumption": "every historically corrected venue track remained current-public",
        "reason": "current track membership and label uniqueness must remain exact while active exclusions govern historical membership",
    },
    {
        "classification": "HISTORICAL_SNAPSHOT_REDIRECT",
        "file": "tests/test_manual_location_audit_20260827.py",
        "new_source_of_truth": "frozen 666-paper predecessor map and exclusion state",
        "old_assumption": "historically audited markers and exclusion state were identical to current public state",
        "reason": "the historical location audit must verify its reviewed corpus layer after reversible suppression",
    },
    {
        "classification": "CURRENT_SUCCESSOR_EXPECTATION",
        "file": "tests/test_paper_metadata_consistency_audit.py",
        "new_source_of_truth": "current generated paper, publication, relationship, and marker totals",
        "old_assumption": "metadata consistency ran against 666 current-public papers",
        "reason": "the invariant is unchanged but its current population is 623 papers",
    },
    {
        "classification": "EXCLUSION_AWARE_INVARIANT",
        "file": "tests/test_paper_taxonomy_migration.py",
        "new_source_of_truth": "current public identities plus active strong-identity exclusions",
        "old_assumption": "every historical taxonomy row had to match a current public paper",
        "reason": "historical taxonomy is retained; an unmatched row still fails unless an active exclusion accounts for it",
    },
    {
        "classification": "EXCLUSION_AWARE_INVARIANT",
        "file": "tests/test_primary_paper_curation.py",
        "new_source_of_truth": "current public output, active exclusions, and frozen predecessor identity records",
        "old_assumption": "every reconciled checklist identity remained discoverable in the current public output",
        "reason": "three newly suppressed key papers must count as excluded rather than missing",
    },
)


def clean(value: Any) -> str:
    return " ".join(str(value if value is not None else "").split())


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def row_sha256(row: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(payload.encode("utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def csv_text(rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=fields,
        lineterminator="\n",
        extrasaction="ignore",
    )
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise AssertionError(f"{path} must contain a records array")
    return payload


def openalex_id(value: Any) -> str:
    match = re.search(r"(?:openalex\.org/)?(W\d+)$", clean(value), re.I)
    return match.group(1).upper() if match else ""


def public_identity(row: Mapping[str, Any]) -> str:
    if clean(row.get("paper_id")):
        return clean(row["paper_id"])
    if normalize_doi(row.get("doi")):
        return f"doi:{normalize_doi(row.get('doi'))}"
    if normalize_arxiv_id(row.get("arxiv_id") or row.get("arxiv_url")):
        return f"arxiv:{normalize_arxiv_id(row.get('arxiv_id') or row.get('arxiv_url'))}"
    if openalex_id(row.get("openalex_url")):
        return f"openalex:{openalex_id(row.get('openalex_url'))}"
    raise AssertionError(f"record lacks a strong identity: {row.get('title')}")


def candidate_identifiers(candidate: Mapping[str, Any]) -> list[tuple[str, str]]:
    values = [
        # Locked migration-plan rows name the authoritative internal identity
        # ``resolved_paper_id``.  Treat it exactly like the queue's
        # ``paper_id`` when verifying suppression and curated retention.
        ("paper_id", clean(candidate.get("paper_id") or candidate.get("resolved_paper_id"))),
        ("doi", normalize_doi(candidate.get("doi"))),
        ("arxiv_id", normalize_arxiv_id(candidate.get("arxiv_id"))),
        ("openalex_id", openalex_id(candidate.get("openalex_id"))),
    ]
    return [(kind, value) for kind, value in values if value]


def record_identifier(row: Mapping[str, Any], kind: str) -> str:
    if kind == "paper_id":
        return clean(row.get("paper_id"))
    if kind == "doi":
        return normalize_doi(row.get("doi"))
    if kind == "arxiv_id":
        return normalize_arxiv_id(row.get("arxiv_id") or row.get("arxiv_url"))
    if kind == "openalex_id":
        return openalex_id(row.get("openalex_url") or row.get("openalex_id"))
    raise AssertionError(kind)


def candidate_target_resolution(
    candidate: Mapping[str, str], public_rows: Sequence[Mapping[str, Any]]
) -> tuple[str, list[int], bool, bool, dict[str, list[int]]]:
    per_identifier: dict[str, list[int]] = {}
    for kind, wanted in candidate_identifiers(candidate):
        per_identifier[kind] = [
            index
            for index, row in enumerate(public_rows)
            if record_identifier(row, kind) == wanted
        ]
    union = sorted({index for indexes in per_identifier.values() for index in indexes})
    nonempty = list(per_identifier.values())
    agree = bool(nonempty) and all(indexes == union and len(indexes) == 1 for indexes in nonempty)
    title_ok = (
        len(union) == 1
        and normalize_title(candidate.get("title"))
        == normalize_title(public_rows[union[0]].get("title"))
    )
    basis = next(
        (kind for kind, _ in candidate_identifiers(candidate) if per_identifier.get(kind)),
        "",
    )
    return basis, union, agree, title_ok, per_identifier


def exclusion_identifier_matches(
    target: Mapping[str, Any], exclusion: Mapping[str, Any]
) -> list[str]:
    matches: list[str] = []
    for kind in ("paper_id", "doi", "openalex_id"):
        target_value = record_identifier(target, kind)
        exclusion_value = record_identifier(exclusion, kind)
        if target_value and exclusion_value and target_value == exclusion_value:
            matches.append(kind)
    return matches


def exclusion_matches_for_target(
    target: Mapping[str, Any], rows: Sequence[Mapping[str, Any]]
) -> list[tuple[int, Mapping[str, Any], list[str]]]:
    return [
        (index, row, matches)
        for index, row in enumerate(rows)
        if (matches := exclusion_identifier_matches(target, row))
    ]


def exclusion_title_year_conflicts(
    target: Mapping[str, Any], rows: Sequence[Mapping[str, Any]]
) -> list[tuple[int, Mapping[str, Any]]]:
    """Return exact title/year collisions that disagree on all strong IDs.

    Title is never used to migrate or suppress a paper.  This check only
    prevents a new active row that the repository validator would treat as a
    duplicate while its strong identifiers point at a different record.
    """
    target_title = normalize_title(target.get("title"))
    target_year = clean(target.get("year") or target.get("publication_year"))
    if not target_title or not target_year:
        return []
    return [
        (index, row)
        for index, row in enumerate(rows)
        if normalize_title(row.get("title")) == target_title
        and clean(row.get("year")) == target_year
        and not exclusion_identifier_matches(target, row)
    ]


def duplicate_active_groups(
    rows: Sequence[Mapping[str, Any]],
) -> list[tuple[str, list[int]]]:
    positions: dict[str, list[int]] = {}
    for row_number, row in enumerate(rows, start=2):
        if not parse_boolean(row.get("is_active")):
            continue
        for key in all_identity_keys(row):
            positions.setdefault(key, []).append(row_number)
    return [
        (key, row_numbers)
        for key, row_numbers in positions.items()
        if len(set(row_numbers)) > 1
    ]


def target_map_indexes(
    candidate: Mapping[str, str], map_rows: Sequence[Mapping[str, Any]]
) -> list[int]:
    identifiers = candidate_identifiers(candidate)
    return [
        index
        for index, row in enumerate(map_rows)
        if any(record_identifier(row, kind) == wanted for kind, wanted in identifiers)
    ]


def corpus_counts(papers: Sequence[Mapping[str, Any]], maps: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "public_papers": len(papers),
        "published_only": sum(clean(row.get("publication_type")) != "preprint" for row in papers),
        "mapped_papers": sum(bool(row.get("has_map_location")) for row in papers),
        "map_markers": len(maps),
    }


def deterministic_exclusion_id(identity: str) -> str:
    return f"exclusion-{uuid.uuid5(MIGRATION_NAMESPACE, AUDIT_SOURCE + '|' + identity).hex}"


def tracked_hashes() -> dict[str, str]:
    process = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    result: dict[str, str] = {}
    for name in process.stdout.decode("utf-8").split("\0"):
        if not name:
            continue
        path = ROOT / name
        if path.is_file():
            result[name] = file_sha256(path)
    return result


def historical_artifact_hashes() -> dict[str, str]:
    roots = (
        ROOT / "data/processed/systematic_literature_2026_09",
        ROOT / "data/processed/systematic_tier1_2026_09",
        ROOT / "data/processed/systematic_tier2_policy_2026_09",
        ROOT / "data/processed/systematic_tier2_application_2026_09",
        ROOT / "data/processed/systematic_tier2_include_2026_09",
        ROOT / "data/processed/systematic_tier2_high_priority_evidence_review_2026_09",
        ROOT / "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09",
        ROOT / "data/processed/legacy_scope_cleanup_2026_09",
        ROOT / "data/processed/legacy_scope_cleanup_audit_2026_09",
    )
    explicit = (
        AUDIT_PATH,
        ROOT / "docs/legacy_scope_cleanup_audit_2026_09.md",
    )
    paths = [path for root in roots if root.exists() for path in root.rglob("*") if path.is_file()]
    paths.extend(path for path in explicit if path.exists())
    return {
        path.relative_to(ROOT).as_posix(): file_sha256(path)
        for path in sorted(set(paths))
    }


def protected_set_rows(audit_rows: Sequence[Mapping[str, str]], status: str) -> list[dict[str, str]]:
    return [dict(row) for row in audit_rows if row.get("final_audit_status") == status]


def protected_set_snapshot(
    audit_rows: Sequence[Mapping[str, str]],
    status: str,
    public_rows: Sequence[Mapping[str, Any]],
    map_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    result = []
    for row in protected_set_rows(audit_rows, status):
        candidate = {
            "paper_id": row.get("paper_id", ""),
            "doi": row.get("doi", ""),
            "arxiv_id": row.get("arxiv_id", ""),
            "openalex_id": row.get("openalex_id", ""),
            "title": row.get("title", ""),
        }
        basis, indexes, agree, title_ok, _ = candidate_target_resolution(candidate, public_rows)
        if len(indexes) != 1 or not agree or not title_ok:
            raise AssertionError(f"protected set identity is not locked: {row['candidate_identity']}")
        map_indexes = target_map_indexes(candidate, map_rows)
        target = public_rows[indexes[0]]
        result.append(
            {
                "candidate_identity": row["candidate_identity"],
                "resolved_authoritative_identity": public_identity(target),
                "identity_basis": basis,
                "public_record_sha256": row_sha256(target),
                "map_record_sha256": [row_sha256(map_rows[index]) for index in map_indexes],
                "map_marker_count": len(map_indexes),
            }
        )
    return result


def build_phase_a() -> tuple[list[dict[str, str]], dict[str, Any], dict[str, Any]]:
    queue = read_csv(QUEUE_PATH)
    audit_rows = read_csv(AUDIT_PATH)
    exclusion_rows = read_exclusion_rows(EXCLUSIONS_PATH)
    paper_payload = load_payload(PUBLIC_PAPERS_PATH)
    map_payload = load_payload(PUBLIC_MAP_PATH)
    public_rows = paper_payload["records"]
    map_rows = map_payload["records"]

    if len(queue) != 44 or len({row["candidate_identity"] for row in queue}) != 44:
        raise AssertionError("migration queue must contain exactly 44 unique candidates")
    if Counter(row["legacy_category"] for row in queue) != CATEGORY_COUNTS:
        raise AssertionError("migration queue category split is not 1/41/2")
    if corpus_counts(public_rows, map_rows) != PREDECESSOR_COUNTS:
        raise AssertionError("Phase A requires the unchanged 666-paper predecessor")

    keep = protected_set_rows(audit_rows, "LEGACY_KEEP_IN_SCOPE")
    needs = protected_set_rows(audit_rows, "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW")
    if len(keep) != 16 or len(needs) != 16:
        raise AssertionError("protected audit sets must contain 16 rows each")
    queue_ids = {row["candidate_identity"] for row in queue}
    keep_ids = {row["candidate_identity"] for row in keep}
    needs_ids = {row["candidate_identity"] for row in needs}
    if queue_ids & keep_ids or queue_ids & needs_ids or keep_ids & needs_ids:
        raise AssertionError("migration, KEEP, and NEEDS_REVIEW sets must be disjoint")

    plan: list[dict[str, str]] = []
    target_papers: list[dict[str, Any]] = []
    target_maps: list[dict[str, Any]] = []
    target_paper_indexes: set[int] = set()
    target_map_indexes_seen: set[int] = set()
    for candidate in queue:
        basis, indexes, agree, title_ok, per_identifier = candidate_target_resolution(
            candidate, public_rows
        )
        if len(indexes) == 0:
            identity_status = "IDENTITY_BLOCKED_ZERO_MATCH"
        elif len(indexes) > 1:
            identity_status = "IDENTITY_BLOCKED_MULTIPLE_MATCH"
        elif not agree or not title_ok:
            identity_status = "IDENTITY_BLOCKED_CONFLICT"
        else:
            identity_status = "IDENTITY_LOCKED"
        target = public_rows[indexes[0]] if len(indexes) == 1 else {}
        exclusion_matches = exclusion_matches_for_target(target, exclusion_rows) if target else []
        title_year_conflicts = (
            exclusion_title_year_conflicts(target, exclusion_rows) if target else []
        )
        match_identifiers = sorted(
            {identifier for _, _, identifiers in exclusion_matches for identifier in identifiers}
        )
        if identity_status != "IDENTITY_LOCKED":
            exclusion_state = "NO_EXISTING_EXCLUSION"
            action = "BLOCK_IDENTITY"
            existing: Mapping[str, Any] = {}
        elif len(exclusion_matches) > 1 or title_year_conflicts:
            exclusion_state = "CONFLICTING_EXCLUSION_IDENTITY"
            action = "BLOCK_EXCLUSION_CONFLICT"
            existing = (
                exclusion_matches[0][1]
                if exclusion_matches
                else title_year_conflicts[0][1]
            )
        elif exclusion_matches:
            existing = exclusion_matches[0][1]
            if parse_boolean(existing.get("is_active")):
                exclusion_state = "EXISTING_ACTIVE_EXCLUSION"
                action = "NOOP_ALREADY_ACTIVE"
            else:
                exclusion_state = "EXISTING_INACTIVE_EXCLUSION"
                action = "REACTIVATE_EXISTING_EXCLUSION"
        else:
            exclusion_state = "NO_EXISTING_EXCLUSION"
            action = "NEW_ACTIVE_EXCLUSION"
            existing = {}
        if action not in ALLOWED_PLAN_ACTIONS:
            raise AssertionError(action)

        resolved_identity = public_identity(target) if target else clean(candidate.get("resolved_authoritative_identity"))
        map_indexes = target_map_indexes(candidate, map_rows) if target else []
        blocking = ""
        if identity_status != "IDENTITY_LOCKED":
            blocking = identity_status
        elif exclusion_state == "CONFLICTING_EXCLUSION_IDENTITY":
            if title_year_conflicts:
                blocking = (
                    "exact normalized title/year collides with exclusion "
                    f"{clean(existing.get('exclusion_id'))}, but strong identifiers disagree"
                )
                match_identifiers = ["normalized_title_year_conflict"]
            else:
                blocking = "multiple exclusion rows match the same authoritative identity"
        proposed_id = (
            clean(existing.get("exclusion_id"))
            if existing
            else deterministic_exclusion_id(resolved_identity)
        )
        plan.append(
            {
                "audit_candidate": candidate["candidate_identity"],
                "resolved_paper_id": clean(target.get("paper_id")),
                "resolved_authoritative_identity": resolved_identity,
                "title": clean(candidate.get("title")),
                "doi": normalize_doi(target.get("doi") or candidate.get("doi")),
                "arxiv_id": normalize_arxiv_id(target.get("arxiv_id") or candidate.get("arxiv_id")),
                "openalex_id": openalex_id(target.get("openalex_url") or candidate.get("openalex_id")),
                "category": candidate["legacy_category"],
                "identity_resolution_basis": basis,
                "identity_resolution_status": identity_status,
                "authoritative_targets_found": str(len(indexes)),
                "strong_identifiers_agree": str(agree).lower(),
                "normalized_title_corroborates": str(title_ok).lower(),
                "pre_migration_exclusion_state": exclusion_state,
                "existing_exclusion_id": clean(existing.get("exclusion_id")),
                "existing_is_active": clean(existing.get("is_active")),
                "existing_restored_at": clean(existing.get("restored_at")),
                "existing_restore_note": clean(existing.get("restore_note")),
                "existing_reason": clean(existing.get("reason")),
                "existing_source": clean(existing.get("created_by") or existing.get("source_database")),
                "exclusion_match_identifiers": ";".join(match_identifiers),
                "proposed_migration_action": action,
                "proposed_exclusion_id": proposed_id,
                "publication_type": clean(target.get("publication_type")),
                "pre_migration_marker_count": str(len(map_indexes)),
                "blocking_issue": blocking,
            }
        )
        if target:
            target_paper_indexes.add(indexes[0])
            target_papers.append(
                {
                    "audit_candidate": candidate["candidate_identity"],
                    "index": indexes[0],
                    "record": target,
                }
            )
        for index in map_indexes:
            target_map_indexes_seen.add(index)
            target_maps.append(
                {
                    "audit_candidate": candidate["candidate_identity"],
                    "index": index,
                    "record": map_rows[index],
                }
            )

    plan_text = csv_text(plan, PLAN_FIELDS)
    receipt = {
        "schema_version": 1,
        "audit_source": AUDIT_SOURCE,
        "locked_at": MIGRATION_TIMESTAMP,
        "candidate_queue": QUEUE_PATH.relative_to(ROOT).as_posix(),
        "candidate_queue_sha256": file_sha256(QUEUE_PATH),
        "migration_plan_sha256": sha256_bytes(plan_text.encode("utf-8")),
        "rows": len(plan),
        "category_counts": dict(sorted(Counter(row["category"] for row in plan).items())),
        "identity_status_counts": dict(sorted(Counter(row["identity_resolution_status"] for row in plan).items())),
        "identity_basis_counts": dict(sorted(Counter(row["identity_resolution_basis"] for row in plan).items())),
        "pre_migration_exclusion_state_counts": dict(sorted(Counter(row["pre_migration_exclusion_state"] for row in plan).items())),
        "proposed_action_counts": dict(sorted(Counter(row["proposed_migration_action"] for row in plan).items())),
        "fuzzy_title_matches": 0,
        "protected_sets": {"LEGACY_KEEP_IN_SCOPE": 16, "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW": 16},
    }

    unrelated_papers = [
        row_sha256(row) for index, row in enumerate(public_rows) if index not in target_paper_indexes
    ]
    unrelated_maps = [
        row_sha256(row) for index, row in enumerate(map_rows) if index not in target_map_indexes_seen
    ]
    snapshot = {
        "schema_version": 1,
        "snapshot": "666-paper NORMAL-priority successor before legacy-scope exclusion migration",
        "captured_at": MIGRATION_TIMESTAMP,
        "counts": PREDECESSOR_COUNTS,
        "source_hashes": {
            "paper_exclusions.csv": file_sha256(EXCLUSIONS_PATH),
            "public_preview_papers.json": file_sha256(PUBLIC_PAPERS_PATH),
            "public_preview_map_data.json": file_sha256(PUBLIC_MAP_PATH),
            "baseline_expectations.py": file_sha256(BASELINE_EXPECTATIONS_PATH),
        },
        "paper_metadata": paper_payload.get("metadata", {}),
        "map_metadata": map_payload.get("metadata", {}),
        "target_public_papers": target_papers,
        "target_map_records": target_maps,
        "unrelated_public_record_sha256": unrelated_papers,
        "unrelated_map_record_sha256": unrelated_maps,
        "paper_exclusions_csv_base64": base64.b64encode(EXCLUSIONS_PATH.read_bytes()).decode("ascii"),
        "baseline_expectations_base64": base64.b64encode(BASELINE_EXPECTATIONS_PATH.read_bytes()).decode("ascii"),
        "protected_sets": {
            "LEGACY_KEEP_IN_SCOPE": protected_set_snapshot(audit_rows, "LEGACY_KEEP_IN_SCOPE", public_rows, map_rows),
            "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW": protected_set_snapshot(audit_rows, "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW", public_rows, map_rows),
        },
        "protected_authoritative_sha256": {
            name: file_sha256(ROOT / name) for name in PROTECTED_AUTHORITATIVE_PATHS
        },
        "historical_artifact_sha256": historical_artifact_hashes(),
        "tracked_pre_migration_sha256": tracked_hashes(),
    }
    return plan, receipt, snapshot


def write_phase_a(destination: Path = OUT) -> dict[str, Any]:
    plan, receipt, snapshot = build_phase_a()
    destination.mkdir(parents=True, exist_ok=True)
    write_text_atomic(destination / PLAN_PATH.name, csv_text(plan, PLAN_FIELDS))
    write_text_atomic(
        destination / PLAN_RECEIPT_PATH.name,
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    write_text_atomic(
        destination / PREDECESSOR_PATH.name,
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
    )
    return receipt


def load_locked_plan() -> tuple[list[dict[str, str]], dict[str, Any], dict[str, Any]]:
    plan = read_csv(PLAN_PATH)
    receipt = json.loads(PLAN_RECEIPT_PATH.read_text(encoding="utf-8"))
    snapshot = json.loads(PREDECESSOR_PATH.read_text(encoding="utf-8"))
    if tuple(plan[0]) != PLAN_FIELDS:
        raise AssertionError("migration plan header is not canonical")
    if len(plan) != 44:
        raise AssertionError("locked plan does not contain 44 rows")
    if file_sha256(PLAN_PATH) != receipt["migration_plan_sha256"]:
        raise AssertionError("migration plan hash does not match its lock receipt")
    if receipt["candidate_queue_sha256"] != file_sha256(QUEUE_PATH):
        raise AssertionError("authoritative migration queue changed after plan lock")
    return plan, receipt, snapshot


def migration_review_note(plan_row: Mapping[str, str]) -> str:
    return (
        "Narrowed-scope legacy cleanup; "
        f"audit={AUDIT_SOURCE}; category={CATEGORY_LABELS[plan_row['category']]}; "
        "status=LEGACY_SCOPE_DRIFT_HIGH_CONFIDENCE; "
        f"candidate={plan_row['audit_candidate']}."
    )


def target_by_candidate(snapshot: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        item["audit_candidate"]: item["record"]
        for item in snapshot["target_public_papers"]
    }


def apply_phase_b() -> dict[str, int]:
    plan, _, snapshot = load_locked_plan()
    if any(row["identity_resolution_status"] != "IDENTITY_LOCKED" for row in plan):
        raise AssertionError("Phase B refused: not every candidate is identity-locked")
    if any(
        bool(row["blocking_issue"])
        != row["proposed_migration_action"].startswith("BLOCK_")
        for row in plan
    ):
        raise AssertionError("Phase B refused: plan blockers and actions disagree")
    if file_sha256(EXCLUSIONS_PATH) != snapshot["source_hashes"]["paper_exclusions.csv"]:
        raise AssertionError("exclusion registry changed after Phase A lock")
    if file_sha256(PUBLIC_PAPERS_PATH) != snapshot["source_hashes"]["public_preview_papers.json"]:
        raise AssertionError("public papers changed after Phase A lock")
    if file_sha256(PUBLIC_MAP_PATH) != snapshot["source_hashes"]["public_preview_map_data.json"]:
        raise AssertionError("public map changed after Phase A lock")

    rows = read_exclusion_rows(EXCLUSIONS_PATH)
    targets = target_by_candidate(snapshot)
    receipts: list[dict[str, str]] = []
    by_id = {clean(row.get("exclusion_id")): row for row in rows}
    for item in plan:
        action = item["proposed_migration_action"]
        if action == "NEW_ACTIVE_EXCLUSION":
            target = targets[item["audit_candidate"]]
            exclusion_id = item["proposed_exclusion_id"]
            if exclusion_id in by_id:
                raise AssertionError(f"deterministic exclusion ID already exists: {exclusion_id}")
            new_row = {
                "exclusion_id": exclusion_id,
                "paper_id": clean(target.get("paper_id")),
                "title": clean(target.get("title")),
                "year": clean(target.get("year") or target.get("publication_year")),
                "doi": clean(target.get("doi")),
                "openalex_url": clean(target.get("openalex_url")),
                "reason": "out_of_scope",
                "review_note": migration_review_note(item),
                "excluded_from_public_preview": "true",
                "excluded_from_map": "true",
                "is_active": "true",
                "created_at": MIGRATION_TIMESTAMP,
                "created_by": "codex_legacy_scope_cleanup",
                "restored_at": "",
                "restore_note": "",
                "source_database": clean(target.get("source_database")),
                "metadata_source": clean(target.get("metadata_source")),
            }
            rows.append(new_row)
            by_id[exclusion_id] = new_row
            receipts.append(
                {
                    "paper_id": item["resolved_paper_id"],
                    "resolved_authoritative_identity": item["resolved_authoritative_identity"],
                    "exclusion_id": exclusion_id,
                    "prior_exclusion_existence": "false",
                    "prior_active_state": "",
                    "prior_restored_at": "",
                    "prior_restore_note": "",
                    "prior_reason": "",
                    "prior_review_note": "",
                    "prior_exclusion_row_sha256": "",
                    "migration_action": "NEW_ACTIVE_EXCLUSION",
                    "audit_source": AUDIT_SOURCE,
                    "resulting_active_state": "true",
                    "future_restoration_action": "SET_INACTIVE_RETAIN_ROW",
                }
            )
        elif action == "REACTIVATE_EXISTING_EXCLUSION":
            exclusion_id = item["existing_exclusion_id"]
            existing = by_id.get(exclusion_id)
            if existing is None or parse_boolean(existing.get("is_active")):
                raise AssertionError(f"inactive exclusion no longer available: {exclusion_id}")
            prior = dict(existing)
            note = migration_review_note(item)
            prior_note = clean(existing.get("review_note"))
            existing["review_note"] = f"{prior_note} | {note}" if prior_note else note
            existing["excluded_from_public_preview"] = "true"
            existing["excluded_from_map"] = "true"
            existing["is_active"] = "true"
            # restored_at / restore_note deliberately remain as historical fields.
            receipts.append(
                {
                    "paper_id": item["resolved_paper_id"],
                    "resolved_authoritative_identity": item["resolved_authoritative_identity"],
                    "exclusion_id": exclusion_id,
                    "prior_exclusion_existence": "true",
                    "prior_active_state": clean(prior.get("is_active")),
                    "prior_restored_at": clean(prior.get("restored_at")),
                    "prior_restore_note": clean(prior.get("restore_note")),
                    "prior_reason": clean(prior.get("reason")),
                    "prior_review_note": clean(prior.get("review_note")),
                    "prior_exclusion_row_sha256": row_sha256(prior),
                    "migration_action": "REACTIVATED_EXCLUSION",
                    "audit_source": AUDIT_SOURCE,
                    "resulting_active_state": "true",
                    "future_restoration_action": "RESTORE_PRIOR_ROW_FROM_RECEIPT",
                }
            )
        elif action == "NOOP_ALREADY_ACTIVE":
            continue
        elif action in {"BLOCK_IDENTITY", "BLOCK_EXCLUSION_CONFLICT"}:
            continue
        else:
            raise AssertionError(f"blocked plan action cannot be applied: {action}")

    duplicates = duplicate_active_groups(rows)
    if duplicates:
        raise AssertionError(f"Phase B would create duplicate active exclusions: {duplicates}")
    if len({row["exclusion_id"] for row in rows}) != len(rows):
        raise AssertionError("Phase B would create duplicate exclusion IDs")

    write_text_atomic(RESTORATION_RECEIPT_PATH, csv_text(receipts, RECEIPT_FIELDS))
    write_exclusion_rows(rows, EXCLUSIONS_PATH)
    return dict(sorted(Counter(row["migration_action"] for row in receipts).items()))


def strong_public_matches(candidate: Mapping[str, str], rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    identifiers = candidate_identifiers(candidate)
    matches = []
    for row in rows:
        if any(record_identifier(row, kind) == wanted for kind, wanted in identifiers):
            matches.append(row)
    return matches


def validate_protected_snapshot(
    snapshot_rows: Sequence[Mapping[str, Any]],
    papers: Sequence[Mapping[str, Any]],
    maps: Sequence[Mapping[str, Any]],
) -> list[str]:
    errors = []
    by_identity = {public_identity(row): row for row in papers}
    for item in snapshot_rows:
        identity = item["resolved_authoritative_identity"]
        paper = by_identity.get(identity)
        if paper is None:
            errors.append(f"{identity}: missing public paper")
            continue
        if row_sha256(paper) != item["public_record_sha256"]:
            errors.append(f"{identity}: public paper changed")
        marker_hashes = [
            row_sha256(row)
            for row in maps
            if any(
                record_identifier(row, kind) == record_identifier(paper, kind)
                for kind in ("paper_id", "doi", "arxiv_id", "openalex_id")
                if record_identifier(paper, kind)
            )
        ]
        if marker_hashes != item["map_record_sha256"]:
            errors.append(f"{identity}: map records changed")
    return errors


def preservation_audit(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    protected = {
        name: file_sha256(ROOT / name) for name in PROTECTED_AUTHORITATIVE_PATHS
    }
    protected_changed = sorted(
        name
        for name, digest in snapshot["protected_authoritative_sha256"].items()
        if protected.get(name) != digest
    )
    historical_changed = sorted(
        name
        for name, digest in snapshot["historical_artifact_sha256"].items()
        if not (ROOT / name).is_file() or file_sha256(ROOT / name) != digest
    )
    return {
        "protected_authoritative_paths": len(protected),
        "protected_authoritative_changed": protected_changed,
        "historical_artifacts_checked": len(snapshot["historical_artifact_sha256"]),
        "historical_artifacts_changed": historical_changed,
    }


def build_ledger_and_validation() -> tuple[list[dict[str, str]], str, dict[str, Any]]:
    plan, plan_receipt, snapshot = load_locked_plan()
    queue_by_id = {row["candidate_identity"]: row for row in read_csv(QUEUE_PATH)}
    exclusions = read_exclusion_rows(EXCLUSIONS_PATH)
    papers = load_payload(PUBLIC_PAPERS_PATH)["records"]
    maps = load_payload(PUBLIC_MAP_PATH)["records"]
    receipts = read_csv(RESTORATION_RECEIPT_PATH)
    receipt_by_exclusion = {row["exclusion_id"]: row for row in receipts}
    exclusion_by_id = {row["exclusion_id"]: row for row in exclusions}
    ledger: list[dict[str, str]] = []
    for item in plan:
        candidate = queue_by_id[item["audit_candidate"]]
        action = item["proposed_migration_action"]
        final_action = {
            "NEW_ACTIVE_EXCLUSION": "NEW_ACTIVE_EXCLUSION",
            "REACTIVATE_EXISTING_EXCLUSION": "REACTIVATED_EXCLUSION",
            "NOOP_ALREADY_ACTIVE": "ALREADY_ACTIVE",
            "BLOCK_IDENTITY": "MIGRATION_IDENTITY_BLOCKED",
            "BLOCK_EXCLUSION_CONFLICT": "MIGRATION_CONFLICT_BLOCKED",
        }[action]
        exclusion_id = item["proposed_exclusion_id"] if action not in {"BLOCK_IDENTITY", "BLOCK_EXCLUSION_CONFLICT"} else ""
        exclusion = exclusion_by_id.get(exclusion_id, {})
        paper_matches = strong_public_matches(item, papers)
        map_matches = strong_public_matches(item, maps)
        changed = action in {"NEW_ACTIVE_EXCLUSION", "REACTIVATE_EXISTING_EXCLUSION"}
        receipt_status = (
            "RECORDED" if changed and exclusion_id in receipt_by_exclusion
            else "NOT_REQUIRED" if not changed and not item["blocking_issue"]
            else "NOT_REQUIRED_BLOCKED"
        )
        remaining = item["blocking_issue"]
        if not remaining and (paper_matches or map_matches):
            remaining = "public suppression verification failed"
        if not remaining and not parse_boolean(exclusion.get("is_active")):
            remaining = "final exclusion is not active"
        ledger.append(
            {
                "audit_candidate": item["audit_candidate"],
                "title": item["title"],
                "resolved_paper_id": item["resolved_paper_id"],
                "resolved_authoritative_identity": item["resolved_authoritative_identity"],
                "doi": item["doi"],
                "arxiv_id": item["arxiv_id"],
                "openalex_id": item["openalex_id"],
                "category": item["category"],
                "audit_evidence_reference": f"{AUDIT_SOURCE}:{item['audit_candidate']} | {candidate['primary_source']}",
                "decisive_audit_evidence": candidate["decisive_primary_evidence"],
                "identity_basis": item["identity_resolution_basis"],
                "pre_migration_exclusion_state": item["pre_migration_exclusion_state"],
                "migration_action": final_action,
                "final_exclusion_id": exclusion_id,
                "final_is_active": str(parse_boolean(exclusion.get("is_active"))).lower() if exclusion else "false",
                "public_suppression_status": (
                    "NOT_SUPPRESSED_BLOCKED"
                    if item["blocking_issue"]
                    else "VERIFIED_ABSENT" if not paper_matches else "FAILED_PRESENT"
                ),
                "map_suppression_status": (
                    "NOT_SUPPRESSED_BLOCKED"
                    if item["blocking_issue"]
                    else "VERIFIED_ABSENT" if not map_matches else "FAILED_PRESENT"
                ),
                "restoration_receipt_status": receipt_status,
                "remaining_issue": remaining,
            }
        )

    current_counts = corpus_counts(papers, maps)
    preservation = preservation_audit(snapshot)
    protected_errors = {
        status: validate_protected_snapshot(snapshot["protected_sets"][status], papers, maps)
        for status in ("LEGACY_KEEP_IN_SCOPE", "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW")
    }
    target_hashes = {
        item["record"] and row_sha256(item["record"])
        for item in snapshot["target_public_papers"]
    }
    unrelated_papers = [
        row_sha256(row) for row in papers if row_sha256(row) not in target_hashes
    ]
    # Targets are absent, so every current record must be one of the predecessor's unrelated records.
    unrelated_papers_unchanged = unrelated_papers == snapshot["unrelated_public_record_sha256"]
    target_map_hashes = {
        row_sha256(item["record"]) for item in snapshot["target_map_records"]
    }
    unrelated_maps_unchanged = [
        row_sha256(row) for row in maps if row_sha256(row) not in target_map_hashes
    ] == snapshot["unrelated_map_record_sha256"]

    validation_evidence = (
        json.loads(VALIDATION_EVIDENCE_PATH.read_text(encoding="utf-8"))
        if VALIDATION_EVIDENCE_PATH.exists()
        else {"status": "pending"}
    )
    validation = {
        "schema_version": 1,
        "audit_source": AUDIT_SOURCE,
        "plan": {
            "sha256": plan_receipt["migration_plan_sha256"],
            "rows": 44,
            "identity_status_counts": dict(sorted(Counter(row["identity_resolution_status"] for row in plan).items())),
            "identity_basis_counts": dict(sorted(Counter(row["identity_resolution_basis"] for row in plan).items())),
            "pre_migration_exclusion_state_counts": dict(sorted(Counter(row["pre_migration_exclusion_state"] for row in plan).items())),
        },
        "migration": {
            "action_counts": dict(sorted(Counter(row["migration_action"] for row in ledger).items())),
            "category_counts": dict(sorted(Counter(row["category"] for row in ledger if not row["remaining_issue"]).items())),
            "restoration_receipt_rows": len(receipts),
            "remaining_issues": [row["audit_candidate"] for row in ledger if row["remaining_issue"]],
        },
        "corpus": {
            "predecessor": snapshot["counts"],
            "successor": current_counts,
            "removed": {
                key: snapshot["counts"][key] - current_counts[key]
                for key in snapshot["counts"]
            },
        },
        "protected_sets": {
            "keep_errors": protected_errors["LEGACY_KEEP_IN_SCOPE"],
            "needs_review_errors": protected_errors["LEGACY_SCOPE_DRIFT_NEEDS_REVIEW"],
        },
        "preservation": {
            **preservation,
            "unrelated_public_records_unchanged": unrelated_papers_unchanged,
            "unrelated_map_records_unchanged": unrelated_maps_unchanged,
        },
        "external_validation_evidence": validation_evidence,
    }
    report = render_report(ledger, validation)
    return ledger, report, validation


def md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_report(rows: Sequence[Mapping[str, str]], validation: Mapping[str, Any]) -> str:
    actions = Counter(row["migration_action"] for row in rows)
    categories = Counter(row["category"] for row in rows if not row["remaining_issue"])
    corpus = validation["corpus"]
    lines = [
        "# Reversible legacy-scope exclusion migration (September 2026)",
        "",
        "This successor migration uses only the locked 44-paper high-confidence queue from the completed legacy-scope audit. It retains every source record and applies the repository's identity-based active-exclusion layer at the public export boundary.",
        "",
        "## Result",
        "",
        f"- Identity-locked candidates: {sum(row['identity_resolution_status'] == 'IDENTITY_LOCKED' for row in read_csv(PLAN_PATH))} / 44",
        f"- New active exclusions: {actions['NEW_ACTIVE_EXCLUSION']}",
        f"- Reactivated exclusions: {actions['REACTIVATED_EXCLUSION']}",
        f"- Already active exclusions: {actions['ALREADY_ACTIVE']}",
        f"- Blocked migrations: {actions['MIGRATION_IDENTITY_BLOCKED'] + actions['MIGRATION_CONFLICT_BLOCKED']}",
        f"- Public papers: {corpus['predecessor']['public_papers']} → {corpus['successor']['public_papers']}",
        f"- Published-only papers: {corpus['predecessor']['published_only']} → {corpus['successor']['published_only']}",
        f"- Mapped papers: {corpus['predecessor']['mapped_papers']} → {corpus['successor']['mapped_papers']}",
        f"- Map markers: {corpus['predecessor']['map_markers']} → {corpus['successor']['map_markers']}",
        "",
        "## Category totals",
        "",
        "| Category | Migrated |",
        "|---|---:|",
    ]
    for category in ("watermark_provenance", "pure_deepfake", "classical_manipulation"):
        lines.append(f"| {CATEGORY_LABELS[category]} | {categories[category]} |")
    lines += [
        "",
        "## Migration ledger",
        "",
        "| Title | Resolved identity | Category | Identity basis | Prior state | Action | Exclusion ID | Public | Map | Receipt | Remaining issue |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                md_cell(value)
                for value in (
                    row["title"],
                    row["resolved_paper_id"] or row["resolved_authoritative_identity"],
                    CATEGORY_LABELS[row["category"]],
                    row["identity_basis"],
                    row["pre_migration_exclusion_state"],
                    row["migration_action"],
                    row["final_exclusion_id"],
                    row["public_suppression_status"],
                    row["map_suppression_status"],
                    row["restoration_receipt_status"],
                    row["remaining_issue"],
                )
            )
            + " |"
        )
    lines += [
        "",
        "## Reversibility and history",
        "",
        "New exclusion rows should be restored by setting them inactive while retaining the row. The reactivated historical row must be restored from its receipt so its prior inactive state, restoration timestamp, restoration note, reason, and review note are recovered. The receipt is evidence for a future explicitly authorized restoration; it is not a parallel suppression mechanism.",
        "",
        "The 666-paper predecessor is preserved by a hash-locked delta snapshot containing the exact 44 paper records, 117 map records, prior metadata, prior exclusion registry bytes, and hashes of every unrelated public record. Earlier systematic, Tier 1, Tier 2, HIGH, NORMAL, and legacy-audit artifacts remain byte-preserved.",
        "Current verification compares the 4,061-entry frozen inventory through a stored-hash relationship, hashes 1,014 retained historical artifacts, and reconstructs and hashes three predecessor source files. It does not claim all inventory entries were byte-verified. Per-layer inventory counts, actual byte-comparison counts, methods, and checked artifact hashes are recorded in [historical verification](../data/processed/legacy_scope_exclusion_migration_2026_09/historical_verification.json). Frozen historical receipts describe their original runs.",
        "",
    ]
    return "\n".join(lines)


def test_successor_migration_payload() -> dict[str, Any]:
    """Describe why each existing test changed for the 623-paper successor."""
    return {
        "schema_version": 1,
        "audit_source": AUDIT_SOURCE,
        "successor": "623-paper reversible legacy-scope exclusion successor",
        "predecessor": "666-paper immediate pre-migration snapshot",
        "changes": [dict(row) for row in TEST_SUCCESSOR_CHANGES],
        "authoritative_data_changed_to_satisfy_tests": False,
    }


def test_successor_migration_text() -> str:
    return json.dumps(
        test_successor_migration_payload(), ensure_ascii=False, indent=2
    ) + "\n"


def reproduction_paths() -> tuple[str, ...]:
    return tuple(
        path
        for group in REPRODUCTION_PATH_GROUPS.values()
        for path in group
    )


def reproduction_texts(
    ledger: Sequence[Mapping[str, str]],
    report: str,
    validation: Mapping[str, Any],
) -> dict[str, str]:
    """Render the migration-owned outputs and hash-lock external refresh outputs.

    Public JSON and standard successor reports are produced by the repository's
    normal refresh pipeline, not by this migration script.  They are included
    verbatim so two ``--reproduce`` runs cover the complete required output set
    without introducing a second exporter.
    """
    rendered = {
        LEDGER_PATH.relative_to(ROOT).as_posix(): csv_text(ledger, LEDGER_FIELDS),
        REPORT_PATH.relative_to(ROOT).as_posix(): report,
        TEST_SUCCESSOR_MIGRATION_PATH.relative_to(ROOT).as_posix(): (
            test_successor_migration_text()
        ),
        VALIDATION_SUMMARY_PATH.relative_to(ROOT).as_posix(): (
            json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ),
        RESTORATION_RECEIPT_PATH.relative_to(ROOT).as_posix(): csv_text(
            read_csv(RESTORATION_RECEIPT_PATH), RECEIPT_FIELDS
        ),
    }
    texts: dict[str, str] = {}
    for name in reproduction_paths():
        texts[name] = (
            rendered[name]
            if name in rendered
            else (ROOT / name).read_text(encoding="utf-8")
        )
    return texts


def build_reproducibility(
    ledger: Sequence[Mapping[str, str]],
    report: str,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    first = reproduction_texts(ledger, report, validation)
    second = reproduction_texts(ledger, report, validation)
    first_sha256 = {
        name: sha256_bytes(text.encode("utf-8")) for name, text in first.items()
    }
    second_sha256 = {
        name: sha256_bytes(text.encode("utf-8")) for name, text in second.items()
    }
    current_sha256 = {name: file_sha256(ROOT / name) for name in reproduction_paths()}
    validation_evidence = validation.get("external_validation_evidence", {})
    if not isinstance(validation_evidence, Mapping):
        validation_evidence = {"status": "invalid"}
    external_regeneration = validation_evidence.get(
        "deterministic_regeneration",
        {"status": validation_evidence.get("status", "pending")},
    )
    return {
        "schema_version": 1,
        "audit_source": AUDIT_SOURCE,
        "rounds": 2,
        "byte_identical": first_sha256 == second_sha256,
        "matches_current": second_sha256 == current_sha256,
        "changed_after_first": sorted(
            name for name in first if current_sha256[name] != first_sha256[name]
        ),
        "changed_after_second": sorted(
            name for name in second if first_sha256[name] != second_sha256[name]
        ),
        "paths_checked": len(second_sha256),
        "path_groups": {
            name: list(paths) for name, paths in REPRODUCTION_PATH_GROUPS.items()
        },
        "sha256": second_sha256,
        "external_standard_refresh_evidence": external_regeneration,
        "scope_note": (
            "Migration-owned artifacts are rendered twice. Public JSON and standard "
            "successor reports are hash-locked here after regeneration by the standard "
            "refresh pipeline; its two-round evidence is recorded separately above."
        ),
        "self_referential_artifacts_excluded_from_sha256": [
            CHANGED_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            REPRODUCIBILITY_PATH.relative_to(ROOT).as_posix(),
        ],
    }


def git_status_entries() -> list[dict[str, str]]:
    process = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    tokens = process.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    entries: list[dict[str, str]] = []
    index = 0
    while index < len(tokens) and tokens[index]:
        token = tokens[index]
        if len(token) < 4 or token[2] != " ":
            raise AssertionError(f"unexpected git status record: {token!r}")
        status = token[:2]
        path = token[3:]
        entry = {"path": path, "status": status}
        if "R" in status or "C" in status:
            index += 1
            if index >= len(tokens) or not tokens[index]:
                raise AssertionError(f"rename/copy status lacks source path: {token!r}")
            entry["source_path"] = tokens[index]
        # Inventorying our own path/status is safe; only a content hash would
        # introduce a recursive dependency on the manifest's own bytes.
        entries.append(entry)
        index += 1
    return sorted(entries, key=lambda item: (item["path"], item["status"]))


def build_changed_files_manifest() -> dict[str, Any]:
    entries = git_status_entries()
    paths = {entry["path"] for entry in entries}
    migration_prefix = OUT.relative_to(ROOT).as_posix() + "/"
    audit_artifact_prefixes = (
        "data/processed/legacy_scope_cleanup_2026_09/",
        "data/processed/legacy_scope_cleanup_audit_2026_09/",
        migration_prefix,
    )
    groups = {
        "A_authoritative_exclusion_changes": sorted(
            paths & {"data/curated/paper_exclusions.csv"}
        ),
        "B_exporter_and_invariant_implementation": sorted(
            paths & MANIFEST_IMPLEMENTATION_PATHS
        ),
        "C_generated_623_paper_successor_outputs": sorted(
            paths & MANIFEST_SUCCESSOR_OUTPUT_PATHS
        ),
        "D_migration_restoration_and_audit_artifacts": sorted(
            path
            for path in paths
            if path in MANIFEST_AUDIT_ARTIFACT_PATHS
            or path.startswith(audit_artifact_prefixes)
        ),
        "E_successor_aware_tests": sorted(
            path for path in paths if path.startswith("tests/")
        ),
        "F_historical_snapshot_support": sorted(
            paths & MANIFEST_HISTORICAL_SUPPORT_PATHS
        ),
    }
    grouped_paths = [path for group in groups.values() for path in group]
    duplicate_group_entries = sorted(
        path for path in set(grouped_paths) if grouped_paths.count(path) > 1
    )
    classified = set(grouped_paths)
    unclassified = sorted(paths - classified)
    frontend_source = sorted(
        path for path in paths if path.startswith("web/") and not path.startswith("web/data/")
    )
    tier3 = sorted(path for path in paths if "tier3" in path.lower())
    authoritative = sorted(path for path in paths if path.startswith("data/curated/"))
    return {
        "schema_version": 1,
        "audit_source": AUDIT_SOURCE,
        "task_scope": "44-paper reversible legacy-scope exclusion migration",
        "command": "git status --porcelain=v1 -z --untracked-files=all",
        "counts": {
            "reported_entries": len(entries),
            "reported_entries_excluding_manifest": len(entries) - int(
                CHANGED_MANIFEST_PATH.relative_to(ROOT).as_posix() in paths
            ),
            "tracked_changes": sum(entry["status"] != "??" for entry in entries),
            "untracked": sum(entry["status"] == "??" for entry in entries),
        },
        "entries": entries,
        "groups": {**groups, "unclassified": unclassified},
        "group_integrity": {
            "all_entries_classified": not unclassified,
            "duplicate_group_entries": duplicate_group_entries,
            "classified_entry_count": len(classified),
        },
        "semantic_boundaries": {
            "authoritative_files_changed": authoritative,
            "allowed_authoritative_file": "data/curated/paper_exclusions.csv",
            "protected_authoritative_files_changed": sorted(
                path for path in authoritative if path != "data/curated/paper_exclusions.csv"
            ),
            "frontend_source_files_changed": frontend_source,
            "tier3_files_changed": tier3,
            "public_generated_outputs_changed": sorted(
                paths
                & {
                    "web/data/public_preview_papers.json",
                    "web/data/public_preview_map_data.json",
                }
            ),
        },
        "bookkeeping_artifacts": [
            CHANGED_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            REPRODUCIBILITY_PATH.relative_to(ROOT).as_posix(),
        ],
        "manifest_content_hash_excluded_to_avoid_self_reference": True,
        "no_commit_or_push": True,
    }


def write_post_migration_artifacts() -> dict[str, Any]:
    try:
        from .frozen_predecessor_666 import historical_verification_receipts
        from .paper_taxonomy_registry import apply_paper_taxonomy_registry, read_paper_taxonomy_registry
    except ImportError:
        from frozen_predecessor_666 import historical_verification_receipts
        from paper_taxonomy_registry import apply_paper_taxonomy_registry, read_paper_taxonomy_registry

    write_text_atomic(
        HISTORICAL_VERIFICATION_PATH,
        json.dumps(historical_verification_receipts(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    taxonomy = read_paper_taxonomy_registry(ROOT / "data/curated/paper_taxonomy.csv")
    taxonomy_summary = apply_paper_taxonomy_registry(
        load_payload(PUBLIC_PAPERS_PATH)["records"],
        load_payload(PUBLIC_MAP_PATH)["records"],
        taxonomy, read_exclusion_rows(EXCLUSIONS_PATH),
    )
    write_text_atomic(
        TAXONOMY_SUMMARY_PATH,
        json.dumps(taxonomy_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    ledger, report, validation = build_ledger_and_validation()
    write_text_atomic(LEDGER_PATH, csv_text(ledger, LEDGER_FIELDS))
    write_text_atomic(REPORT_PATH, report)
    write_text_atomic(TEST_SUCCESSOR_MIGRATION_PATH, test_successor_migration_text())
    write_text_atomic(
        VALIDATION_SUMMARY_PATH,
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    reproducibility = build_reproducibility(ledger, report, validation)
    write_text_atomic(
        REPRODUCIBILITY_PATH,
        json.dumps(reproducibility, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    manifest = build_changed_files_manifest()
    write_text_atomic(
        CHANGED_MANIFEST_PATH,
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    return validation


def reconstruct_predecessor(destination: Path) -> dict[str, str]:
    _, _, snapshot = load_locked_plan()
    destination.mkdir(parents=True, exist_ok=True)
    current_papers = load_payload(PUBLIC_PAPERS_PATH)
    current_maps = load_payload(PUBLIC_MAP_PATH)
    current_papers["metadata"] = snapshot["paper_metadata"]
    current_maps["metadata"] = snapshot["map_metadata"]
    paper_records = list(current_papers["records"])
    map_records = list(current_maps["records"])
    current_paper_hashes = {row_sha256(row) for row in paper_records}
    current_map_hashes = {row_sha256(row) for row in map_records}
    for item in sorted(snapshot["target_public_papers"], key=lambda value: value["index"]):
        if row_sha256(item["record"]) not in current_paper_hashes:
            paper_records.insert(item["index"], item["record"])
    for item in sorted(snapshot["target_map_records"], key=lambda value: value["index"]):
        if row_sha256(item["record"]) not in current_map_hashes:
            map_records.insert(item["index"], item["record"])
    current_papers["records"] = paper_records
    current_maps["records"] = map_records
    outputs = {
        "public_preview_papers.json": json.dumps(current_papers, ensure_ascii=False, indent=2) + "\n",
        "public_preview_map_data.json": json.dumps(current_maps, ensure_ascii=False, indent=2) + "\n",
        "paper_exclusions.csv": base64.b64decode(snapshot["paper_exclusions_csv_base64"]).decode("utf-8"),
        "baseline_expectations.py": base64.b64decode(snapshot["baseline_expectations_base64"]).decode("utf-8"),
    }
    hashes = {}
    for name, text in outputs.items():
        path = destination / name
        path.write_text(text, encoding="utf-8")
        hashes[name] = file_sha256(path)
    expected = snapshot["source_hashes"]
    if hashes != expected:
        raise AssertionError(f"predecessor reconstruction mismatch: {hashes} != {expected}")
    return hashes


def check_current() -> dict[str, Any]:
    plan, _, snapshot = load_locked_plan()
    ledger, report, validation = build_ledger_and_validation()
    errors = []
    if LEDGER_PATH.read_text(encoding="utf-8-sig") != csv_text(ledger, LEDGER_FIELDS):
        errors.append("canonical migration ledger is stale")
    if REPORT_PATH.read_text(encoding="utf-8") != report:
        errors.append("migration report is stale")
    expected_validation = json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if VALIDATION_SUMMARY_PATH.read_text(encoding="utf-8") != expected_validation:
        errors.append("validation summary is stale")
    expected_reproducibility = (
        json.dumps(
            build_reproducibility(ledger, report, validation),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    if not REPRODUCIBILITY_PATH.is_file():
        errors.append("reproducibility receipt is missing")
    elif REPRODUCIBILITY_PATH.read_text(encoding="utf-8") != expected_reproducibility:
        errors.append("reproducibility receipt is stale")
    manifest = build_changed_files_manifest()
    expected_manifest = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    if not CHANGED_MANIFEST_PATH.is_file():
        errors.append("changed-files manifest is missing")
    elif CHANGED_MANIFEST_PATH.read_text(encoding="utf-8") != expected_manifest:
        errors.append("changed-files manifest is stale")
    if not manifest["group_integrity"]["all_entries_classified"]:
        errors.append(
            "changed-files manifest has unclassified paths: "
            + ", ".join(manifest["groups"]["unclassified"])
        )
    if manifest["group_integrity"]["duplicate_group_entries"]:
        errors.append(
            "changed-files manifest groups overlap: "
            + ", ".join(manifest["group_integrity"]["duplicate_group_entries"])
        )
    unexpected_issues = [
        row["audit_candidate"]
        for row in ledger
        if row["remaining_issue"]
        and row["migration_action"]
        not in {"MIGRATION_IDENTITY_BLOCKED", "MIGRATION_CONFLICT_BLOCKED"}
    ]
    if unexpected_issues:
        errors.append(f"safe migration rows contain unresolved issues: {unexpected_issues}")
    if validation["protected_sets"]["keep_errors"]:
        errors.append("KEEP protected set changed")
    if validation["protected_sets"]["needs_review_errors"]:
        errors.append("NEEDS_REVIEW protected set changed")
    if validation["preservation"]["protected_authoritative_changed"]:
        errors.append("protected authoritative files changed")
    if validation["preservation"]["historical_artifacts_changed"]:
        errors.append("historical artifacts changed")
    if not validation["preservation"]["unrelated_public_records_unchanged"]:
        errors.append("unrelated public papers changed")
    if not validation["preservation"]["unrelated_map_records_unchanged"]:
        errors.append("unrelated map records changed")
    if Counter(row["identity_resolution_status"] for row in plan) != {"IDENTITY_LOCKED": 44}:
        errors.append("not all Phase A identities remain locked")
    if errors:
        raise AssertionError("; ".join(errors))
    return validation


def reproduce(destination: Path) -> dict[str, str]:
    ledger, report, validation = build_ledger_and_validation()
    destination.mkdir(parents=True, exist_ok=True)
    texts = reproduction_texts(ledger, report, validation)
    output_names = [Path(name).name for name in texts]
    if len(set(output_names)) != len(output_names):
        raise AssertionError("reproduction output basenames must be unique")
    hashes = {}
    for source_name, text in texts.items():
        path = destination / Path(source_name).name
        path.write_text(text, encoding="utf-8")
        hashes[source_name] = file_sha256(path)
    return hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--phase-a", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--render", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--reconstruct-predecessor", type=Path)
    group.add_argument("--reproduce", type=Path)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    if args.phase_a:
        result = write_phase_a(args.output_dir)
    elif args.apply:
        result = apply_phase_b()
    elif args.render:
        result = write_post_migration_artifacts()
    elif args.check:
        result = check_current()
    elif args.reconstruct_predecessor:
        result = reconstruct_predecessor(args.reconstruct_predecessor)
    else:
        result = reproduce(args.reproduce)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
