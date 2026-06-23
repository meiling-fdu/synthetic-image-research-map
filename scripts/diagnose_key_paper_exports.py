#!/usr/bin/env python3
"""Diagnose why covered OpenAlex key papers are absent from map exports.

This script is local-only. It reads the current coverage report and pipeline
artifacts, writes a manual-review diagnostics table, and changes no export or
scope behavior.
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


COVERAGE_REPORT = Path("data/manual/key_paper_coverage_report.csv")
OPENALEX_PAPERS = Path("data/processed/openalex_candidate_papers.csv")
IN_SCOPE_PAPERS = Path("data/processed/openalex_candidate_papers_in_scope.csv")
AFFILIATIONS = Path("data/processed/openalex_candidate_affiliations.csv")
GEOCODED_AFFILIATIONS = Path(
    "data/processed/openalex_candidate_affiliations_geocoded.csv"
)
KEY_PAPER_AFFILIATION_ENRICHMENT = Path(
    "data/manual/key_paper_affiliation_enrichment.csv"
)
CANDIDATE_MAP = Path("web/data/openalex_candidate_map_data.json")
PUBLIC_PREVIEW = Path("web/data/public_preview_map_data.json")
OUTPUT = Path("data/manual/key_paper_export_diagnostics.csv")

TARGET_STATUS = "in_openalex_candidate_pool_but_not_exported"
SEDID_TITLE = "Exposing the Fake: Effective Diffusion-Generated Images Detection"

OUTPUT_COLUMNS = [
    "title",
    "year",
    "normalized_title",
    "key_paper_status",
    "openalex_candidate_status",
    "in_openalex_candidate_papers",
    "in_openalex_candidate_papers_in_scope",
    "in_candidate_map_export",
    "in_public_preview",
    "openalex_url",
    "doi",
    "candidate_record_id",
    "stable_id_status",
    "affiliation_record_status",
    "coordinate_status",
    "export_status",
    "skip_reason",
    "recommended_next_action",
    "notes",
]

ALLOWED_SKIP_REASONS = {
    "missing_affiliation_records",
    "missing_valid_coordinates",
    "title_match_only_no_stable_id",
    "not_in_in_scope_candidate_file",
    "blocked_by_current_export_rule",
    "unknown_export_skip_reason",
}
ALLOWED_ACTIONS = {
    "add_or_verify_affiliation_records",
    "add_or_verify_coordinates",
    "check_export_rule",
    "confirm_stable_identifier",
    "manual_review",
}
KEY_PAPER_AFFILIATION_ENRICHMENT_COLUMNS = {
    "title",
    "year",
    "normalized_title",
    "openalex_url",
    "doi",
    "raw_affiliation",
    "institution",
    "latitude",
    "longitude",
}


class DiagnosisError(RuntimeError):
    """An expected local input or validation error."""


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: Any) -> str:
    title = clean_text(value).casefold()
    title = title.replace("‐", "-").replace("–", "-").replace("—", "-")
    title = title.replace("real-world", "real world")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", title).split())


def read_csv(
    path: Path,
    required_columns: Iterable[str],
    optional: bool = False,
) -> List[Dict[str, str]]:
    if not path.exists():
        if optional:
            return []
        raise DiagnosisError(f"Required local input does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(set(required_columns) - set(reader.fieldnames or []))
            if missing:
                raise DiagnosisError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise DiagnosisError(f"Could not read {path}: {error}") from error


def read_json_records(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise DiagnosisError(f"Could not read {path}: {error}") from error
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        return [
            row for row in payload.get("records", []) if isinstance(row, dict)
        ]
    return []


def title_index(rows: Sequence[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = normalize_title(row.get("title"))
        if key:
            index[key].append(row)
    return index


def normalize_identifier_url(value: Any) -> str:
    return clean_text(value).casefold().rstrip("/")


def normalize_doi(value: Any) -> str:
    doi = clean_text(value)
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    return doi.casefold()


def parse_year(value: Any) -> str:
    text = clean_text(value)
    return text if re.fullmatch(r"\d{1,4}", text) else ""


def paper_identity_keys(row: Dict[str, Any]) -> List[Tuple[str, Any]]:
    keys: List[Tuple[str, Any]] = []
    openalex = normalize_identifier_url(row.get("openalex_url") or row.get("openalex_id"))
    if openalex:
        keys.append(("openalex", openalex))
    doi = normalize_doi(row.get("doi"))
    if doi:
        keys.append(("doi", doi))
    title = normalize_title(row.get("title"))
    year = parse_year(row.get("publication_year") or row.get("year"))
    if title and year:
        keys.append(("title_year", (title, year)))
    return keys


def key_affiliation_index(
    rows: Sequence[Dict[str, str]],
) -> Dict[Tuple[str, Any], List[Dict[str, str]]]:
    index: Dict[Tuple[str, Any], List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        for key in paper_identity_keys(row):
            index[key].append(row)
    return index


def matching_key_affiliations(
    candidate: Dict[str, Any],
    index: Dict[Tuple[str, Any], List[Dict[str, str]]],
) -> List[Dict[str, str]]:
    seen = set()
    matches: List[Dict[str, str]] = []
    for key in paper_identity_keys(candidate):
        for row in index.get(key, []):
            identity = tuple(row.get(column, "") for column in sorted(row))
            if identity in seen:
                continue
            seen.add(identity)
            matches.append(row)
    return matches


def enrichment_has_affiliation(row: Dict[str, str]) -> bool:
    return bool(clean_text(row.get("institution")) and clean_text(row.get("raw_affiliation")))


def valid_coordinate_pair(row: Dict[str, Any]) -> bool:
    pairs = (
        (row.get("resolved_latitude"), row.get("resolved_longitude")),
        (row.get("latitude"), row.get("longitude")),
    )
    for raw_latitude, raw_longitude in pairs:
        try:
            latitude = float(raw_latitude)
            longitude = float(raw_longitude)
        except (TypeError, ValueError):
            continue
        if (
            math.isfinite(latitude)
            and math.isfinite(longitude)
            and -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):
            return True
    return False


def stable_identifier_status(candidate: Dict[str, Any]) -> str:
    fields = (
        "openalex_id",
        "openalex_url",
        "doi",
        "arxiv_id",
        "paper_url",
        "url",
        "primary_url",
        "landing_page_url",
    )
    return (
        "stable_identifier_available"
        if any(clean_text(candidate.get(field)) for field in fields)
        else "title_match_only_no_stable_id"
    )


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def diagnose() -> List[Dict[str, str]]:
    report = read_csv(
        COVERAGE_REPORT,
        {"title", "year", "missing_stage"},
    )
    targets = [row for row in report if row["missing_stage"] == TARGET_STATUS]
    if len(targets) != 22:
        raise DiagnosisError(
            f"Expected 22 {TARGET_STATUS} rows, found {len(targets)}"
        )

    openalex_rows = read_csv(
        OPENALEX_PAPERS,
        {"openalex_id", "title", "doi", "openalex_url"},
    )
    in_scope_rows = read_csv(
        IN_SCOPE_PAPERS,
        {"openalex_id", "title"},
    )
    affiliation_rows = read_csv(
        AFFILIATIONS,
        {"openalex_id", "institution_name", "raw_affiliation_text"},
    )
    geocoded_rows = read_csv(
        GEOCODED_AFFILIATIONS,
        {"openalex_id", "institution_name", "latitude", "longitude"},
    )
    key_affiliation_rows = read_csv(
        KEY_PAPER_AFFILIATION_ENRICHMENT,
        KEY_PAPER_AFFILIATION_ENRICHMENT_COLUMNS,
        optional=True,
    )
    candidate_records = read_json_records(CANDIDATE_MAP)
    preview_records = read_json_records(PUBLIC_PREVIEW)

    openalex_by_title = title_index(openalex_rows)
    in_scope_by_title = title_index(in_scope_rows)
    candidate_by_title = title_index(candidate_records)
    preview_by_title = title_index(preview_records)
    affiliations_by_work: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    geocoded_by_work: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in affiliation_rows:
        affiliations_by_work[clean_text(row.get("openalex_id"))].append(row)
    for row in geocoded_rows:
        geocoded_by_work[clean_text(row.get("openalex_id"))].append(row)
    key_affiliations_by_identity = key_affiliation_index(key_affiliation_rows)

    diagnostics: List[Dict[str, str]] = []
    for target in targets:
        normalized = normalize_title(target.get("title"))
        openalex_matches = openalex_by_title.get(normalized, [])
        if not openalex_matches:
            raise DiagnosisError(
                f"Coverage target has no exact OpenAlex title match: {target['title']}"
            )
        candidate = openalex_matches[0]
        openalex_id = clean_text(candidate.get("openalex_id"))
        in_scope = bool(in_scope_by_title.get(normalized))
        map_matches = candidate_by_title.get(normalized, [])
        preview_matches = preview_by_title.get(normalized, [])
        affiliations = affiliations_by_work.get(openalex_id, [])
        geocoded = geocoded_by_work.get(openalex_id, [])
        key_affiliations = matching_key_affiliations(
            candidate,
            key_affiliations_by_identity,
        )
        enriched_institution_rows = [
            row for row in key_affiliations if enrichment_has_affiliation(row)
        ]
        enriched_valid_coordinates = [
            row for row in key_affiliations if valid_coordinate_pair(row)
        ]
        openalex_institution_rows = [
            row
            for row in affiliations
            if clean_text(row.get("institution_name"))
            or clean_text(row.get("raw_affiliation_text"))
        ]
        institution_rows = openalex_institution_rows + enriched_institution_rows
        valid_coordinates = [
            row for row in geocoded if valid_coordinate_pair(row)
        ] + enriched_valid_coordinates
        stable_status = stable_identifier_status(candidate)

        if not institution_rows:
            skip_reason = "missing_affiliation_records"
            action = "add_or_verify_affiliation_records"
            export_status = "cannot_build_institution_map_record"
        elif not valid_coordinates:
            skip_reason = "missing_valid_coordinates"
            action = "add_or_verify_coordinates"
            export_status = "cannot_build_coordinate_bearing_map_record"
        elif stable_status == "title_match_only_no_stable_id":
            skip_reason = "title_match_only_no_stable_id"
            action = "confirm_stable_identifier"
            export_status = "title_match_requires_identifier_confirmation"
        elif not map_matches:
            skip_reason = "blocked_by_current_export_rule"
            action = "check_export_rule"
            export_status = (
                "eligible_key_paper_attempt_not_in_candidate_map"
                if not in_scope
                else "eligible_local_records_not_in_candidate_map"
            )
        else:
            skip_reason = "unknown_export_skip_reason"
            action = "manual_review"
            export_status = "requires_manual_pipeline_trace"

        affiliation_status = (
            "institution_records_available_from_key_paper_enrichment"
            if enriched_institution_rows and not openalex_institution_rows
            else "institution_records_available"
            if institution_rows
            else "author_rows_without_institution_or_raw_affiliation"
            if affiliations
            else "no_affiliation_rows"
        )
        coordinate_status = (
            "valid_coordinates_available"
            if valid_coordinates
            else "not_applicable_without_institution_records"
            if not institution_rows
            else "no_valid_coordinates"
        )
        candidate_ids = sorted(
            {
                clean_text(row.get("id"))
                for row in map_matches
                if clean_text(row.get("id"))
            }
        )
        notes = (
            f"OpenAlex matches={len(openalex_matches)}; "
            f"affiliation rows={len(affiliations)}; "
            f"openalex institution-bearing rows={len(openalex_institution_rows)}; "
            f"key-paper enrichment rows={len(key_affiliations)}; "
            f"key-paper enrichment institution-bearing rows={len(enriched_institution_rows)}; "
            f"geocoded rows={len(geocoded)}; "
            f"valid-coordinate rows={len(valid_coordinates)}. "
            "Diagnostic only; key-paper checklist membership remains in scope."
        )
        diagnostics.append(
            {
                "title": clean_text(target.get("title")),
                "year": clean_text(target.get("year")),
                "normalized_title": normalized,
                "key_paper_status": TARGET_STATUS,
                "openalex_candidate_status": "exact_normalized_title_match",
                "in_openalex_candidate_papers": "yes",
                "in_openalex_candidate_papers_in_scope": yes_no(in_scope),
                "in_candidate_map_export": yes_no(bool(map_matches)),
                "in_public_preview": yes_no(bool(preview_matches)),
                "openalex_url": clean_text(
                    candidate.get("openalex_url") or candidate.get("openalex_id")
                ),
                "doi": clean_text(candidate.get("doi")),
                "candidate_record_id": "; ".join(candidate_ids),
                "stable_id_status": stable_status,
                "affiliation_record_status": affiliation_status,
                "coordinate_status": coordinate_status,
                "export_status": export_status,
                "skip_reason": skip_reason,
                "recommended_next_action": action,
                "notes": notes,
            }
        )

    validate(diagnostics, targets)
    return diagnostics


def validate(
    diagnostics: Sequence[Dict[str, str]],
    targets: Sequence[Dict[str, str]],
) -> None:
    diagnostic_titles = [row["normalized_title"] for row in diagnostics]
    target_titles = {normalize_title(row.get("title")) for row in targets}
    if len(diagnostics) != 22:
        raise DiagnosisError(f"Expected 22 diagnostic rows, found {len(diagnostics)}")
    if len(set(diagnostic_titles)) != len(diagnostic_titles):
        raise DiagnosisError("Diagnostics contain duplicate normalized titles")
    if set(diagnostic_titles) != target_titles:
        missing = sorted(target_titles - set(diagnostic_titles))
        extra = sorted(set(diagnostic_titles) - target_titles)
        raise DiagnosisError(f"Diagnostics target mismatch: missing={missing}, extra={extra}")
    if normalize_title(SEDID_TITLE) not in diagnostic_titles:
        raise DiagnosisError("SeDID is missing from diagnostics")
    for row in diagnostics:
        if row["skip_reason"] not in ALLOWED_SKIP_REASONS:
            raise DiagnosisError(f"Invalid skip_reason: {row['skip_reason']}")
        if row["recommended_next_action"] not in ALLOWED_ACTIONS:
            raise DiagnosisError(
                f"Invalid recommended_next_action: {row['recommended_next_action']}"
            )


def write_csv(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=OUTPUT_COLUMNS,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise DiagnosisError(f"Could not write {path}: {error}") from error


def main() -> int:
    try:
        rows = diagnose()
        write_csv(OUTPUT, rows)
    except DiagnosisError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Wrote: {OUTPUT}")
    print(f"Diagnostic rows: {len(rows)}")
    print("By skip_reason:")
    for key, count in Counter(row["skip_reason"] for row in rows).most_common():
        print(f"  {key}: {count}")
    print("By recommended_next_action:")
    for key, count in Counter(
        row["recommended_next_action"] for row in rows
    ).most_common():
        print(f"  {key}: {count}")
    print(f"SeDID included: {any(normalize_title(row['title']) == normalize_title(SEDID_TITLE) for row in rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
