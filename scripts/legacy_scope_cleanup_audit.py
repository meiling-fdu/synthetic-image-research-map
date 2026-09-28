#!/usr/bin/env python3
"""Validate and render the non-destructive September 2026 legacy-scope audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

try:
    from .frozen_predecessor_666 import (
        SNAPSHOT_PATH as PREDECESSOR_SNAPSHOT_PATH,
        predecessor_public_records,
        verify_predecessor,
    )
except ImportError:
    from frozen_predecessor_666 import (
        SNAPSHOT_PATH as PREDECESSOR_SNAPSHOT_PATH,
        predecessor_public_records,
        verify_predecessor,
    )


ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_PATH = (
    ROOT
    / "data/processed/systematic_tier2_application_2026_09/legacy_scope_diagnostic.csv"
)
CSV_PATH = ROOT / "data/manual/legacy_scope_cleanup_audit_2026_09.csv"
REPORT_PATH = ROOT / "docs/legacy_scope_cleanup_audit_2026_09.md"
BASELINE_PATH = (
    ROOT / "data/processed/legacy_scope_cleanup_audit_2026_09/baseline_sha256.json"
)
OUT = ROOT / "data/processed/legacy_scope_cleanup_2026_09"
HIGH_CONFIDENCE_PATH = OUT / "high_confidence_scope_drift.csv"
NEEDS_REVIEW_PATH = OUT / "needs_review.csv"
VALIDATION_PATH = OUT / "validation_summary.json"
ARTIFACT_HASH_PATH = OUT / "artifact_sha256.json"
IDENTITY_SUMMARY_PATH = OUT / "identity_resolution_summary.json"
PUBLIC_PAPERS_PATH = ROOT / "web/data/public_preview_papers.json"
PUBLIC_MAP_PATH = ROOT / "web/data/public_preview_map_data.json"

FIELDS = (
    "source_diagnostic_row_id",
    "candidate_identity",
    "paper_id",
    "title",
    "year",
    "doi",
    "arxiv_id",
    "openalex_id",
    "resolved_authoritative_identity",
    "normalized_title_identity",
    "identity_match_method",
    "strong_identifiers_agree",
    "source_record_sha256",
    "identity_resolution_status",
    "current_taxonomy",
    "legacy_category",
    "primary_source",
    "decisive_datasets_tasks",
    "face_only_flag",
    "video_temporal_flag",
    "media_scope_status",
    "mechanism",
    "broader_synthetic_image_evidence",
    "final_audit_status",
    "confidence",
    "recommended_next_action",
    "exact_evidence_needed",
    "rationale",
    "corpus_action",
)

STATUS_VALUES = {
    "LEGACY_KEEP_IN_SCOPE",
    "LEGACY_SCOPE_DRIFT_HIGH_CONFIDENCE",
    "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW",
}
CATEGORY_BY_DIAGNOSTIC = {
    "LEGACY_SCOPE_REVIEW_WATERMARK": "watermark_provenance",
    "LEGACY_SCOPE_REVIEW_DEEPFAKE": "pure_deepfake",
    "LEGACY_SCOPE_REVIEW_CLASSICAL": "classical_manipulation",
}
CATEGORY_LABELS = {
    "watermark_provenance": "Watermark / provenance",
    "pure_deepfake": "Deepfake / face / video",
    "classical_manipulation": "Classical manipulation",
}
CATEGORY_ORDER = tuple(CATEGORY_LABELS)
HIGH_CONFIDENCE_FIELDS = (
    "candidate_identity",
    "paper_id",
    "title",
    "year",
    "doi",
    "arxiv_id",
    "openalex_id",
    "resolved_authoritative_identity",
    "identity_match_method",
    "identity_resolution_status",
    "legacy_category",
    "primary_source",
    "decisive_primary_evidence",
    "scope_conflict",
    "recommended_future_action",
)
NEEDS_REVIEW_FIELDS = (
    "candidate_identity",
    "paper_id",
    "title",
    "year",
    "doi",
    "arxiv_id",
    "openalex_id",
    "resolved_authoritative_identity",
    "identity_match_method",
    "identity_resolution_status",
    "legacy_category",
    "primary_source",
    "evidence_available",
    "exact_unresolved_question",
    "recommended_future_action",
)

IDENTITY_STATUS_VALUES = {
    "INTERNAL_ID_RESOLVED",
    "IDENTITY_RESOLVABLE_BY_STRONG_ID",
    "IDENTITY_RESOLUTION_REQUIRED",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def load_json_records(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise AssertionError(f"{path} does not contain a record list")
    return records


def legacy_public_records() -> list[dict[str, object]]:
    """Return the exact public-paper state audited by this historical layer."""
    if PREDECESSOR_SNAPSHOT_PATH.is_file():
        return predecessor_public_records()
    return load_json_records(PUBLIC_PAPERS_PATH)


def normalize_doi(value: object) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        str(value or "").strip(),
        flags=re.IGNORECASE,
    ).casefold()


def normalize_title(value: object) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").casefold()))


def openalex_id(value: object) -> str:
    match = re.search(r"(?:openalex\.org/)?(W\d+)$", str(value or "").strip(), re.I)
    return match.group(1).upper() if match else ""


def arxiv_id(value: object) -> str:
    match = re.search(
        r"(?:arxiv\.org/(?:abs|pdf)/|arxiv:)(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?$",
        str(value or "").strip(),
        re.I,
    )
    return match.group(1) if match else ""


def expected_public_identity(row: Mapping[str, object]) -> str:
    if row.get("paper_id"):
        return str(row["paper_id"])
    if normalize_doi(row.get("doi")):
        return f"doi:{normalize_doi(row.get('doi'))}"
    if str(row.get("arxiv_id") or "").strip():
        return f"arxiv:{str(row['arxiv_id']).strip()}"
    if openalex_id(row.get("openalex_url")):
        return f"openalex:{openalex_id(row.get('openalex_url'))}"
    return f"normalized-title:{normalize_title(row.get('title'))}"


def expected_identity_match_method(
    diagnostic: Mapping[str, str], public: Mapping[str, object]
) -> str:
    if diagnostic.get("paper_id", "").strip():
        return "paper_id"
    if normalize_doi(diagnostic.get("doi") or public.get("doi")):
        return "doi"
    if arxiv_id(diagnostic.get("primary_url")):
        return "arxiv_id"
    if openalex_id(diagnostic.get("primary_url")):
        return "openalex_id"
    if str(public.get("arxiv_id") or "").strip():
        return "arxiv_id"
    if openalex_id(public.get("openalex_url")):
        return "openalex_id"
    return "normalized_title_year"


def expected_identity_status(
    diagnostic: Mapping[str, str], public: Mapping[str, object]
) -> str:
    if diagnostic.get("paper_id", "").strip():
        return "INTERNAL_ID_RESOLVED"
    if (
        normalize_doi(diagnostic.get("doi") or public.get("doi"))
        or str(public.get("arxiv_id") or "").strip()
        or openalex_id(public.get("openalex_url"))
    ):
        return "IDENTITY_RESOLVABLE_BY_STRONG_ID"
    return "IDENTITY_RESOLUTION_REQUIRED"


def public_match(
    diagnostic: Mapping[str, str], public_rows: Sequence[Mapping[str, object]]
) -> Mapping[str, object]:
    matches: list[Mapping[str, object]] = []
    wanted_id = diagnostic.get("paper_id", "").strip()
    wanted_doi = normalize_doi(diagnostic.get("doi"))
    wanted_arxiv = arxiv_id(diagnostic.get("primary_url"))
    wanted_openalex = openalex_id(diagnostic.get("primary_url"))
    wanted_title = normalize_title(diagnostic.get("canonical_title"))
    for row in public_rows:
        if wanted_id and str(row.get("paper_id") or "") == wanted_id:
            matches.append(row)
        elif wanted_doi and normalize_doi(row.get("doi")) == wanted_doi:
            matches.append(row)
        elif wanted_arxiv and str(row.get("arxiv_id") or "").strip() == wanted_arxiv:
            matches.append(row)
        elif wanted_openalex and openalex_id(row.get("openalex_url")) == wanted_openalex:
            matches.append(row)
        elif not (wanted_id or wanted_doi or wanted_arxiv or wanted_openalex) and (
            normalize_title(row.get("title")) == wanted_title
            and str(row.get("year") or row.get("publication_year") or "")
            == diagnostic.get("year", "")
        ):
            matches.append(row)
    unique = {id(row): row for row in matches}
    if len(unique) != 1:
        raise AssertionError(
            f"expected one frozen-predecessor public match for {diagnostic.get('paper_identity')}; "
            f"found {len(unique)}"
        )
    return next(iter(unique.values()))


def taxonomy_text(row: Mapping[str, object]) -> str:
    def joined(field: str) -> str:
        value = row.get(field)
        if isinstance(value, list):
            return ";".join(str(item) for item in value)
        return str(value or "")

    return (
        f"Forensic Task={joined('tasks')} | Image Scope={joined('image_scopes')} | "
        f"Research Type={joined('research_types')}"
    )


def csv_text(
    rows: Sequence[Mapping[str, str]], fields: Sequence[str]
) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=fields,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def canonical_csv_text(rows: Sequence[Mapping[str, str]]) -> str:
    return csv_text(rows, FIELDS)


def category_summary(rows: Iterable[Mapping[str, str]]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    materialized = list(rows)
    for category in CATEGORY_ORDER:
        selected = [row for row in materialized if row["legacy_category"] == category]
        counts = Counter(row["final_audit_status"] for row in selected)
        result[category] = {
            "reviewed": len(selected),
            "keep": counts["LEGACY_KEEP_IN_SCOPE"],
            "high_confidence_drift": counts[
                "LEGACY_SCOPE_DRIFT_HIGH_CONFIDENCE"
            ],
            "needs_review": counts["LEGACY_SCOPE_DRIFT_NEEDS_REVIEW"],
        }
    return result


def validate_rows(rows: Sequence[Mapping[str, str]]) -> dict[str, object]:
    diagnostic = read_csv(DIAGNOSTIC_PATH)
    public_rows = legacy_public_records()
    assert len(diagnostic) == 76
    assert len(rows) == len(diagnostic)
    assert len({row["candidate_identity"] for row in rows}) == len(rows)
    assert len({row["resolved_authoritative_identity"] for row in rows}) == len(rows)
    paper_ids = [row["paper_id"] for row in rows if row["paper_id"]]
    assert len(set(paper_ids)) == len(paper_ids)
    assert all(row["corpus_action"] == "NONE_AUDIT_ONLY" for row in rows)
    assert all(row["final_audit_status"] in STATUS_VALUES for row in rows)
    assert all(row["confidence"] in {"high", "medium", "low"} for row in rows)

    by_identity = {row["candidate_identity"]: row for row in rows}
    assert len(by_identity) == len(rows)
    assert set(by_identity) == {row["paper_identity"] for row in diagnostic}
    for candidate in diagnostic:
        row = by_identity[candidate["paper_identity"]]
        public = public_match(candidate, public_rows)
        assert row["title"] == candidate["canonical_title"]
        assert row["legacy_category"] == CATEGORY_BY_DIAGNOSTIC[
            candidate["legacy_scope_category"]
        ]
        assert row["source_diagnostic_row_id"] == candidate["legacy_review_id"]
        assert row["paper_id"] == candidate["paper_id"]
        assert row["year"] == candidate["year"]
        assert row["doi"] == normalize_doi(candidate["doi"] or public.get("doi"))
        assert row["arxiv_id"] == str(public.get("arxiv_id") or "").strip()
        assert row["openalex_id"] == openalex_id(public.get("openalex_url"))
        assert row["resolved_authoritative_identity"] == expected_public_identity(public)
        assert row["normalized_title_identity"] == (
            f"title-year:{normalize_title(candidate['canonical_title'])}|{candidate['year']}"
        )
        assert row["identity_match_method"] == expected_identity_match_method(
            candidate, public
        )
        assert row["strong_identifiers_agree"] in {"true", "false"}
        if row["identity_resolution_status"] != "IDENTITY_RESOLUTION_REQUIRED":
            assert row["strong_identifiers_agree"] == "true"
        assert row["source_record_sha256"] == candidate["source_record_sha256"]
        assert row["identity_resolution_status"] == expected_identity_status(
            candidate, public
        )
        assert row["current_taxonomy"] == taxonomy_text(public)
        for field in (
            "primary_source",
            "decisive_datasets_tasks",
            "face_only_flag",
            "video_temporal_flag",
            "media_scope_status",
            "mechanism",
            "broader_synthetic_image_evidence",
            "recommended_next_action",
            "rationale",
        ):
            assert row[field].strip(), (candidate["paper_identity"], field)
        assert row["face_only_flag"] in {"yes", "no", "unclear", "not_applicable"}
        assert row["video_temporal_flag"] in {
            "yes",
            "no",
            "unclear",
            "mixed_independent_still",
            "not_applicable",
        }
        if row["final_audit_status"] == "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW":
            assert row["exact_evidence_needed"].strip()
            assert row["recommended_next_action"] == "FURTHER_PRIMARY_REVIEW"
        else:
            assert not row["exact_evidence_needed"].strip()
        if row["final_audit_status"] == "LEGACY_KEEP_IN_SCOPE":
            assert row["recommended_next_action"] == "NO_ACTION"
        if row["final_audit_status"] == "LEGACY_SCOPE_DRIFT_HIGH_CONFIDENCE":
            assert row["recommended_next_action"] in {
                "REMOVE_FROM_PUBLIC_CORPUS",
                "KEEP_AS_LEGACY_EXCEPTION",
                "MOVE_TO_EXCLUDED_ARCHIVE",
            }

    summary = category_summary(rows)
    assert summary["watermark_provenance"]["reviewed"] == 3
    assert summary["pure_deepfake"]["reviewed"] == 71
    assert summary["classical_manipulation"]["reviewed"] == 2
    identity_counts = dict(
        sorted(Counter(row["identity_resolution_status"] for row in rows).items())
    )
    assert set(identity_counts).issubset(IDENTITY_STATUS_VALUES)
    assert sum(identity_counts.values()) == 76
    return {
        "reviewed": len(rows),
        "unique_papers": len({row["candidate_identity"] for row in rows}),
        "status_counts": dict(sorted(Counter(row["final_audit_status"] for row in rows).items())),
        "categories": summary,
        "identity_resolution": identity_counts,
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_baseline_files(
    expected_hashes: Mapping[str, str], root: Path = ROOT
) -> tuple[list[str], list[str]]:
    changed = []
    missing = []
    for relative, expected in expected_hashes.items():
        path = root / relative
        if not path.is_file():
            missing.append(relative)
        elif file_sha256(path) != expected:
            changed.append(relative)
    return changed, missing


def verify_baseline() -> dict[str, object]:
    if PREDECESSOR_SNAPSHOT_PATH.is_file():
        return verify_predecessor()
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    changed, missing = compare_baseline_files(
        baseline["tracked_baseline_sha256"]
    )
    papers = load_json_records(PUBLIC_PAPERS_PATH)
    markers = load_json_records(PUBLIC_MAP_PATH)
    actual_counts = {
        "public_papers": len(papers),
        "published_only": sum(
            row.get("publication_type") != "preprint" for row in papers
        ),
        "mapped_papers": sum(bool(row.get("has_map_location")) for row in papers),
        "map_markers": len(markers),
    }
    assert not changed, f"baseline files changed: {changed}"
    assert not missing, f"baseline files missing: {missing}"
    assert actual_counts == baseline["corpus_counts"]
    return {
        "manifest_entry_count": len(baseline["tracked_baseline_sha256"]),
        "byte_verified_count": len(baseline["tracked_baseline_sha256"]),
        "byte_verified_match_count": len(baseline["tracked_baseline_sha256"]),
        "byte_verified_mismatch_count": 0,
        "verification_scope": "fully_byte_verified",
        "verification_method": "Read and hash every baseline manifest entry.",
        "changed": changed,
        "missing": missing,
        "corpus_counts": actual_counts,
    }


def verify_workspace_scope() -> dict[str, object]:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    allowed = tuple(baseline["allowed_new_artifact_prefixes"])
    if PREDECESSOR_SNAPSHOT_PATH.is_file():
        verify_predecessor()
        return {
            "changed_paths": [],
            "unauthorized_paths": [],
            "allowed_prefixes": list(allowed),
        }
    process = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    changed_paths = []
    entries = process.stdout.decode("utf-8", errors="strict").split("\0")
    for entry in entries:
        if not entry:
            continue
        path = entry[3:]
        changed_paths.append(path)
    unauthorized = [
        path
        for path in changed_paths
        if not any(path == prefix or path.startswith(prefix) for prefix in allowed)
    ]
    assert not unauthorized, f"unauthorized workspace changes: {unauthorized}"
    return {
        "changed_paths": changed_paths,
        "unauthorized_paths": unauthorized,
        "allowed_prefixes": list(allowed),
    }


def md_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_report(rows: Sequence[Mapping[str, str]]) -> str:
    totals = validate_rows(rows)
    summary = totals["categories"]
    assert isinstance(summary, dict)
    lines = [
        "# Legacy-scope cleanup audit (September 2026)",
        "",
        "This is a non-destructive evidence audit of the 76 papers in the then-current 666-paper NORMAL-priority successor, now preserved as the immediate pre-migration predecessor. The audit itself modified no paper, taxonomy row, exclusion, affiliation, institution, location, public export, frontend file, Tier 1/Tier 2 history, or Tier 3 artifact.",
        "",
        "The diagnostic was used only to define the bounded queue. Each decision below is based on the paper's primary task, datasets, and experimental protocol. A deepfake or traditional-manipulation taxonomy label alone was never treated as a scope finding.",
        "",
        "## Summary",
        "",
        "| Category | Reviewed | Keep | High-confidence drift | Needs review |",
        "|---|---:|---:|---:|---:|",
    ]
    for category in CATEGORY_ORDER:
        values = summary[category]
        lines.append(
            f"| {CATEGORY_LABELS[category]} | {values['reviewed']} | "
            f"{values['keep']} | {values['high_confidence_drift']} | "
            f"{values['needs_review']} |"
        )
    status_counts = totals["status_counts"]
    assert isinstance(status_counts, dict)
    lines += [
        "",
        f"Unique papers reviewed: **{totals['unique_papers']}**. The diagnostic assigns one category per paper, so the category total and unique-paper total are both 76.",
        "",
        "Status totals: "
        + ", ".join(f"`{status}` = {count}" for status, count in status_counts.items())
        + ".",
        "",
        "## Identity readiness",
        "",
        "| Identity state | Count |",
        "|---|---:|",
    ]
    for status in sorted(IDENTITY_STATUS_VALUES):
        lines.append(
            f"| `{status}` | {totals['identity_resolution'].get(status, 0)} |"
        )
    lines += [
        "",
        "The 46 diagnostic rows without an internal `paper_id` are retained as identity-ready migrations, not repaired corpus records. Forty-five match the frozen 666-paper predecessor through an exact DOI. AdaptPrompt matches through the diagnostic OpenAlex ID `W7117078863`, corroborated by arXiv `2512.17730`. No candidate in this audit requires a weak fuzzy-title-only match.",
        "",
        "## High-confidence legacy scope drift",
        "",
        "These are historical inclusions under an older, broader scope. The finding is scope drift, not a claim that their bibliographic metadata is wrong.",
        "",
        "| Paper | Candidate identity | Internal paper ID | Strong identifiers | Category | Decisive primary evidence | Narrowed-scope conflict | Future action |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        if row["final_audit_status"] != "LEGACY_SCOPE_DRIFT_HIGH_CONFIDENCE":
            continue
        lines.append(
            "| "
            + " | ".join(
                md_cell(value)
                for value in (
                    f"[{row['title']}]({row['primary_source']})",
                    f"`{row['candidate_identity']}`",
                    f"`{row['paper_id'] or 'not assigned'}`",
                    "; ".join(
                        value
                        for value in (
                            f"DOI {row['doi']}" if row["doi"] else "",
                            f"arXiv {row['arxiv_id']}" if row["arxiv_id"] else "",
                            f"OpenAlex {row['openalex_id']}" if row["openalex_id"] else "",
                        )
                        if value
                    ),
                    CATEGORY_LABELS[row["legacy_category"]],
                    row["decisive_datasets_tasks"],
                    row["rationale"],
                    f"`{row['recommended_next_action']}`",
                )
            )
            + " |"
        )

    lines += [
        "",
        "## Previously flagged papers retained in scope",
        "",
        "| Paper | Category | Decisive broader synthetic-image evidence |",
        "|---|---|---|",
    ]
    for row in rows:
        if row["final_audit_status"] != "LEGACY_KEEP_IN_SCOPE":
            continue
        lines.append(
            "| "
            + " | ".join(
                md_cell(value)
                for value in (
                    f"[{row['title']}]({row['primary_source']})",
                    CATEGORY_LABELS[row["legacy_category"]],
                    row["broader_synthetic_image_evidence"],
                )
            )
            + " |"
        )

    lines += [
        "",
        "## Remaining review-needed cases",
        "",
        "| Paper | Category | Evidence available now | Exact evidence still needed |",
        "|---|---|---|---|",
    ]
    for row in rows:
        if row["final_audit_status"] != "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW":
            continue
        lines.append(
            "| "
            + " | ".join(
                md_cell(value)
                for value in (
                    f"[{row['title']}]({row['primary_source']})",
                    CATEGORY_LABELS[row["legacy_category"]],
                    row["decisive_datasets_tasks"],
                    row["exact_evidence_needed"],
                )
            )
            + " |"
        )

    lines += [
        "",
        "## Recommended reversible cleanup mechanism",
        "",
        "For a later, separately authorized cleanup, prefer `MOVE_TO_EXCLUDED_ARCHIVE` for high-confidence drift. Keep the scientific identity and historical record, then suppress the work only at the public-export boundary. The then-current exclusion registry stores paper ID, DOI, OpenAlex ID, title/year, reason, review note, `is_active`, `restored_at`, and `restore_note`; the exporter removes matching paper and map records together. The audit ledger supplies the structured primary-evidence link and rationale.",
        "",
        "The future migration must: (1) resolve each candidate to authoritative identity, (2) verify all available strong identifiers agree, (3) create or activate the exclusion, (4) regenerate public paper and map outputs together, and (5) preserve historical corpus snapshots. Never exclusion-match on a fuzzy title alone. Retain a full metadata snapshot, reference this audit in the exclusion review note, and preserve the old 666-paper baselines. `KEEP_AS_LEGACY_EXCEPTION` maximizes public continuity but leaves the narrowed public scope inconsistent. Direct deletion has the highest provenance and reproducibility risk and is not recommended.",
        "",
        "No cleanup action was applied by this audit.",
        "",
        "## Reproducibility and integrity",
        "",
        "The canonical CSV is normalized with a fixed header/order and LF line endings. The report is rendered from that CSV, and tests reproduce both artifacts twice in isolated temporary directories and compare bytes. A pre-audit SHA-256 manifest covers every tracked baseline file, including authoritative data, public exports, frontend files, historical Tier 1/Tier 2 layers, and Tier 3 artifacts.",
        "",
        "Baseline corpus: 666 public papers; 555 published-only papers; 645 mapped papers; 1,508 map markers.",
        "",
        "## Historical successor layers",
        "",
        "| Frozen layer | Integrity result |",
        "|---|---|",
        "| 620-paper systematic audit | PASS — byte preserved |",
        "| Tier 1 reconciliation | PASS — byte preserved |",
        "| 636-paper Tier 2 policy analysis/application | PASS — byte preserved |",
        "| 648-paper inclusion successor | PASS — byte preserved |",
        "| 657-paper HIGH evidence successor | PASS — byte preserved |",
        "| 666-paper NORMAL evidence successor | PASS — byte preserved |",
        "",
        "## Complete evidence ledger",
        "",
        "| Candidate identity | Paper ID | Title | Taxonomy in audited predecessor | Category | Media scope | Mechanism | Primary evidence | Status | Confidence | Next action |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                md_cell(value)
                for value in (
                    f"`{row['candidate_identity']}`",
                    f"`{row['paper_id'] or 'not assigned'}`",
                    f"[{row['title']}]({row['primary_source']})",
                    row["current_taxonomy"],
                    CATEGORY_LABELS[row["legacy_category"]],
                    row["media_scope_status"],
                    row["mechanism"],
                    row["decisive_datasets_tasks"],
                    f"`{row['final_audit_status']}`",
                    row["confidence"],
                    f"`{row['recommended_next_action']}`",
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def high_confidence_rows(
    rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "candidate_identity": row["candidate_identity"],
            "paper_id": row["paper_id"],
            "title": row["title"],
            "year": row["year"],
            "doi": row["doi"],
            "arxiv_id": row["arxiv_id"],
            "openalex_id": row["openalex_id"],
            "resolved_authoritative_identity": row[
                "resolved_authoritative_identity"
            ],
            "identity_match_method": row["identity_match_method"],
            "identity_resolution_status": row["identity_resolution_status"],
            "legacy_category": row["legacy_category"],
            "primary_source": row["primary_source"],
            "decisive_primary_evidence": row["decisive_datasets_tasks"],
            "scope_conflict": row["rationale"],
            "recommended_future_action": row["recommended_next_action"],
        }
        for row in rows
        if row["final_audit_status"] == "LEGACY_SCOPE_DRIFT_HIGH_CONFIDENCE"
    ]


def needs_review_rows(
    rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "candidate_identity": row["candidate_identity"],
            "paper_id": row["paper_id"],
            "title": row["title"],
            "year": row["year"],
            "doi": row["doi"],
            "arxiv_id": row["arxiv_id"],
            "openalex_id": row["openalex_id"],
            "resolved_authoritative_identity": row[
                "resolved_authoritative_identity"
            ],
            "identity_match_method": row["identity_match_method"],
            "identity_resolution_status": row["identity_resolution_status"],
            "legacy_category": row["legacy_category"],
            "primary_source": row["primary_source"],
            "evidence_available": row["decisive_datasets_tasks"],
            "exact_unresolved_question": row["exact_evidence_needed"],
            "recommended_future_action": row["recommended_next_action"],
        }
        for row in rows
        if row["final_audit_status"] == "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW"
    ]


def validation_text(
    rows: Sequence[Mapping[str, str]], integrity: Mapping[str, object]
) -> str:
    if PREDECESSOR_SNAPSHOT_PATH.is_file():
        # Replay the original receipt only after verifying its frozen bytes.
        # It describes the historical run, not the current verification scope;
        # verify_baseline() returns the precise current-run receipt separately.
        verify_predecessor()
        validate_rows(rows)
        verify_workspace_scope()
        return VALIDATION_PATH.read_text(encoding="utf-8")
    totals = validate_rows(rows)
    workspace_scope = verify_workspace_scope()
    payload = {
        "audit": "legacy_scope_cleanup_audit_2026_09",
        "audit_only": True,
        "authoritative_corpus_changed": False,
        "exclusions_changed": False,
        "frontend_changed": False,
        "public_data_changed": False,
        "tier3_changed": False,
        "corpus_counts": integrity["corpus_counts"],
        "protected_baseline_files_verified": integrity["byte_verified_count"],
        "protected_baseline_files_changed": len(integrity["changed"]),
        "protected_baseline_files_missing": len(integrity["missing"]),
        "unauthorized_workspace_changes": len(
            workspace_scope["unauthorized_paths"]
        ),
        "reviewed": totals["reviewed"],
        "unique_papers": totals["unique_papers"],
        "status_counts": totals["status_counts"],
        "categories": totals["categories"],
        "identity_resolution": totals["identity_resolution"],
        "historical_successor_layers_byte_preserved": {
            "620_paper_systematic_audit": True,
            "tier_1": True,
            "636_paper_tier_2_policy": True,
            "648_paper_inclusion": True,
            "657_paper_high_evidence": True,
            "666_paper_normal_evidence": True,
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def identity_summary_text(rows: Sequence[Mapping[str, str]]) -> str:
    totals = validate_rows(rows)
    basis_counts = Counter(row["identity_match_method"] for row in rows)
    conflicts = [
        row["candidate_identity"]
        for row in rows
        if row["strong_identifiers_agree"] != "true"
    ]
    adaptprompt = next(
        row for row in rows if row["candidate_identity"].startswith("title-sha256:")
    )
    payload = {
        "audit": "legacy_scope_cleanup_audit_2026_09",
        "diagnostic_rows_without_internal_paper_id": sum(
            not row["paper_id"] for row in rows
        ),
        "identity_resolution_counts": totals["identity_resolution"],
        "resolution_basis_counts": {
            "paper_id": basis_counts["paper_id"],
            "doi": basis_counts["doi"],
            "arxiv_id": basis_counts["arxiv_id"],
            "openalex_id": basis_counts["openalex_id"],
            "normalized_title_year": basis_counts["normalized_title_year"],
        },
        "originally_idless_resolution": {
            "rows": sum(not row["paper_id"] for row in rows),
            "doi": sum(
                not row["paper_id"] and row["identity_match_method"] == "doi"
                for row in rows
            ),
            "arxiv_id": sum(
                not row["paper_id"] and row["identity_match_method"] == "arxiv_id"
                for row in rows
            ),
            "openalex_id": sum(
                not row["paper_id"] and row["identity_match_method"] == "openalex_id"
                for row in rows
            ),
        },
        "conflicting_strong_identifiers": conflicts,
        "adaptprompt_resolution": {
            "source_diagnostic_identity": adaptprompt["candidate_identity"],
            "resolution_basis": adaptprompt["identity_match_method"],
            "openalex_id": adaptprompt["openalex_id"],
            "corroborating_arxiv_id": adaptprompt["arxiv_id"],
            "resolved_authoritative_identity": adaptprompt[
                "resolved_authoritative_identity"
            ],
        },
        "migration_policy": [
            "resolve candidate to authoritative identity",
            "then create or activate a reversible exclusion",
        ],
        "weak_fuzzy_title_only_matching_permitted": False,
        "weak_fuzzy_title_matching_required": False,
        "rows": [
            {
                "source_diagnostic_row_id": row["source_diagnostic_row_id"],
                "candidate_identity": row["candidate_identity"],
                "paper_id": row["paper_id"],
                "title": row["title"],
                "year": row["year"],
                "doi": row["doi"],
                "arxiv_id": row["arxiv_id"],
                "openalex_id": row["openalex_id"],
                "resolved_authoritative_identity": row[
                    "resolved_authoritative_identity"
                ],
                "normalized_title_identity": row["normalized_title_identity"],
                "identity_match_method": row["identity_match_method"],
                "strong_identifiers_agree": row["strong_identifiers_agree"],
                "source_record_sha256": row["source_record_sha256"],
                "identity_resolution_status": row["identity_resolution_status"],
            }
            for row in rows
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def generated_texts(
    rows: Sequence[Mapping[str, str]], integrity: Mapping[str, object]
) -> dict[str, str]:
    high_text = csv_text(high_confidence_rows(rows), HIGH_CONFIDENCE_FIELDS)
    needs_text = csv_text(needs_review_rows(rows), NEEDS_REVIEW_FIELDS)
    validation = validation_text(rows, integrity)
    identity_summary = identity_summary_text(rows)
    base = {
        CSV_PATH.name: canonical_csv_text(rows),
        REPORT_PATH.name: render_report(rows),
        HIGH_CONFIDENCE_PATH.name: high_text,
        NEEDS_REVIEW_PATH.name: needs_text,
        VALIDATION_PATH.name: validation,
        IDENTITY_SUMMARY_PATH.name: identity_summary,
        BASELINE_PATH.name: BASELINE_PATH.read_text(encoding="utf-8"),
    }
    artifact_hashes = {
        name: hashlib.sha256(text.encode("utf-8")).hexdigest()
        for name, text in base.items()
    }
    base[ARTIFACT_HASH_PATH.name] = (
        json.dumps(artifact_hashes, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    return base


def reproduce(
    destination: Path,
    rows: Sequence[Mapping[str, str]],
    integrity: Mapping[str, object],
) -> dict[str, str]:
    destination.mkdir(parents=True, exist_ok=True)
    result = {}
    for name, text in generated_texts(rows, integrity).items():
        path = destination / name
        path.write_text(text, encoding="utf-8")
        result[name] = file_sha256(path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-derived", action="store_true")
    parser.add_argument("--reproduce", type=Path)
    args = parser.parse_args()

    rows = read_csv(CSV_PATH)
    if tuple(rows[0]) != FIELDS:
        raise AssertionError("legacy audit CSV does not have the exact canonical header")
    totals = validate_rows(rows)
    integrity = verify_baseline()
    expected_csv = canonical_csv_text(rows)
    if CSV_PATH.read_text(encoding="utf-8-sig") != expected_csv:
        raise AssertionError("legacy audit CSV is not in canonical deterministic form")
    texts = generated_texts(rows, integrity)
    if args.write_derived:
        OUT.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(texts[REPORT_PATH.name], encoding="utf-8")
        HIGH_CONFIDENCE_PATH.write_text(
            texts[HIGH_CONFIDENCE_PATH.name], encoding="utf-8"
        )
        NEEDS_REVIEW_PATH.write_text(texts[NEEDS_REVIEW_PATH.name], encoding="utf-8")
        VALIDATION_PATH.write_text(texts[VALIDATION_PATH.name], encoding="utf-8")
        IDENTITY_SUMMARY_PATH.write_text(
            texts[IDENTITY_SUMMARY_PATH.name], encoding="utf-8"
        )
        ARTIFACT_HASH_PATH.write_text(
            texts[ARTIFACT_HASH_PATH.name], encoding="utf-8"
        )
    else:
        current_paths = (
            REPORT_PATH,
            HIGH_CONFIDENCE_PATH,
            NEEDS_REVIEW_PATH,
            VALIDATION_PATH,
            IDENTITY_SUMMARY_PATH,
            ARTIFACT_HASH_PATH,
        )
        for path in current_paths:
            if path.read_text(encoding="utf-8") != texts[path.name]:
                raise AssertionError(f"legacy audit artifact is stale: {path}")
    reproduced = (
        reproduce(args.reproduce, rows, integrity) if args.reproduce else None
    )
    print(
        json.dumps(
            {"audit": totals, "integrity": integrity, "reproduced": reproduced},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
