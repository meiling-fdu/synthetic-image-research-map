#!/usr/bin/env python3
"""Build a deterministic marker-risk review report from generated outputs."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPOSITORY_ROOT / "data" / "manual" / "high_risk_marker_review.csv"
PUBLIC_MAP_PATH = REPOSITORY_ROOT / "web" / "data" / "public_preview_map_data.json"
CANDIDATE_MAP_PATH = (
    REPOSITORY_ROOT / "web" / "data" / "openalex_candidate_map_data.json"
)
BLOCKER_PATH = REPOSITORY_ROOT / "data" / "manual" / "paper_marker_blocker_report.csv"
KEY_COVERAGE_PATH = (
    REPOSITORY_ROOT / "data" / "manual" / "key_paper_coverage_report.csv"
)

COLUMNS = (
    "priority",
    "review_type",
    "title",
    "year",
    "doi",
    "openalex_url",
    "institution",
    "institution_authors",
    "city",
    "region",
    "country",
    "country_code",
    "lat",
    "lon",
    "source_database",
    "metadata_source",
    "publication_type",
    "task",
    "subtask",
    "needs_review",
    "resolution_confidence",
    "resolution_method",
    "resolution_notes",
    "current_public_preview_status",
    "recommended_action",
    "review_note",
)


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def truthy(value: Any) -> bool:
    return clean(value).casefold() in {"1", "true", "yes", "y"}


def list_text(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(clean(item) for item in value if clean(item))
    return clean(value)


def read_json_records(path: Path) -> list[Dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("records") or payload.get("papers") or []
    return [dict(row) for row in payload if isinstance(row, dict)]


def read_csv(path: Path) -> list[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def base_row(source: Mapping[str, Any]) -> Dict[str, str]:
    return {
        "title": clean(source.get("title")),
        "year": clean(source.get("year") or source.get("publication_year")),
        "doi": clean(source.get("doi")),
        "openalex_url": clean(source.get("openalex_url")),
        "institution": clean(source.get("institution")),
        "institution_authors": list_text(source.get("institution_authors")),
        "city": clean(source.get("city")),
        "region": clean(source.get("region")),
        "country": clean(source.get("country")),
        "country_code": clean(source.get("country_code")),
        "lat": clean(source.get("lat") or source.get("latitude")),
        "lon": clean(source.get("lon") or source.get("longitude")),
        "source_database": clean(source.get("source_database")),
        "metadata_source": clean(source.get("metadata_source")),
        "publication_type": clean(source.get("publication_type")),
        "task": clean(source.get("task")),
        "subtask": clean(source.get("subtask")),
        "needs_review": clean(source.get("needs_review")),
        "resolution_confidence": clean(source.get("resolution_confidence")),
        "resolution_method": clean(source.get("resolution_method")),
        "resolution_notes": clean(
            source.get("resolution_notes") or source.get("notes")
        ),
        "review_note": "",
    }


def low_confidence(row: Mapping[str, Any]) -> bool:
    value = clean(row.get("resolution_confidence")).casefold()
    return value in {"", "low", "uncertain", "ambiguous", "needs_review"}


def public_rows() -> Iterable[Dict[str, str]]:
    for marker in read_json_records(PUBLIC_MAP_PATH):
        suspicious = truthy(marker.get("needs_review")) or low_confidence(marker)
        if not suspicious:
            continue
        yield {
            **base_row(marker),
            "priority": "P0",
            "review_type": "suspicious_public_marker",
            "current_public_preview_status": "public_marker",
            "recommended_action": "confirm_marker",
        }


def candidate_rows() -> Iterable[Dict[str, str]]:
    for marker in read_json_records(CANDIDATE_MAP_PATH):
        if not (
            truthy(marker.get("needs_review"))
            or truthy(marker.get("manual_review"))
            or low_confidence(marker)
        ):
            continue
        has_coordinates = bool(
            clean(marker.get("latitude")) and clean(marker.get("longitude"))
        )
        yield {
            **base_row(marker),
            "priority": "P1" if has_coordinates else "P2",
            "review_type": (
                "blocked_candidate_marker"
                if has_coordinates
                else "candidate_missing_coordinates"
            ),
            "current_public_preview_status": "candidate_only",
            "recommended_action": (
                "confirm_marker" if has_coordinates else "send_to_location_review"
            ),
        }


def blocker_rows() -> Iterable[Dict[str, str]]:
    for source in read_csv(BLOCKER_PATH):
        blocker = clean(source.get("blocker_type"))
        if blocker == "already_mapped":
            continue
        action = {
            "missing_affiliation_rows": "replace_author_institution_mapping",
            "has_affiliation_missing_coordinates": "send_to_location_review",
            "needs_review_or_low_confidence": "confirm_marker",
        }.get(blocker, "no_action_after_review")
        yield {
            **base_row(source),
            "priority": "P1" if blocker == "needs_review_or_low_confidence" else "P2",
            "review_type": f"marker_blocker:{blocker or 'unknown'}",
            "current_public_preview_status": (
                "paper_list_only" if not truthy(source.get("has_map_location")) else "mapped"
            ),
            "recommended_action": action,
        }


def key_rows() -> Iterable[Dict[str, str]]:
    for source in read_csv(KEY_COVERAGE_PATH):
        stage = clean(source.get("missing_stage"))
        if stage == "covered_as_map_marker":
            continue
        yield {
            **base_row(source),
            "priority": "P1" if stage == "covered_in_public_preview_paper_list" else "P2",
            "review_type": f"key_paper:{stage or 'unknown'}",
            "current_public_preview_status": clean(
                source.get("coverage_status") or stage
            ),
            "recommended_action": (
                "replace_author_institution_mapping"
                if stage == "covered_in_public_preview_paper_list"
                else "no_action_after_review"
            ),
            "resolution_notes": clean(source.get("notes")),
        }


def identity(row: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        clean(row.get(field)).casefold()
        for field in (
            "priority",
            "review_type",
            "doi",
            "openalex_url",
            "title",
            "year",
            "institution",
        )
    )


def build_rows() -> list[Dict[str, str]]:
    rows: Dict[tuple[str, ...], Dict[str, str]] = {}
    for row in (*public_rows(), *candidate_rows(), *blocker_rows(), *key_rows()):
        rows.setdefault(identity(row), {column: clean(row.get(column)) for column in COLUMNS})
    return sorted(
        rows.values(),
        key=lambda row: (
            row["priority"],
            row["review_type"].casefold(),
            row["title"].casefold(),
            row["institution"].casefold(),
            row["openalex_url"].casefold(),
        ),
    )


def main() -> int:
    try:
        rows = build_rows()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = OUTPUT_PATH.with_suffix(".csv.tmp")
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(OUTPUT_PATH)
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError) as error:
        print(f"ERROR: could not build high-risk marker report: {error}", file=sys.stderr)
        return 1
    priorities = {priority: sum(row["priority"] == priority for row in rows) for priority in ("P0", "P1", "P2")}
    print(
        f"Wrote {len(rows)} high-risk marker review rows to "
        f"{OUTPUT_PATH.relative_to(REPOSITORY_ROOT)} "
        f"(P0={priorities['P0']}, P1={priorities['P1']}, P2={priorities['P2']})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
