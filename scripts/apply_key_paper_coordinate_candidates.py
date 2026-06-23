#!/usr/bin/env python3
"""Safely apply confirmed key-paper coordinate candidates to enrichment rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


CANDIDATES = Path("data/manual/key_paper_coordinate_candidates.csv")
ENRICHMENT = Path("data/manual/key_paper_affiliation_enrichment.csv")

SEDID_TITLE = "Exposing the Fake: Effective Diffusion-Generated Images Detection"

CANDIDATE_COLUMNS = {
    "title",
    "normalized_title",
    "author",
    "author_position",
    "institution",
    "candidate_latitude",
    "candidate_longitude",
    "candidate_source",
    "candidate_source_detail",
    "apply_status",
}
ENRICHMENT_COLUMNS = [
    "title",
    "year",
    "normalized_title",
    "openalex_url",
    "doi",
    "author",
    "author_position",
    "raw_affiliation",
    "institution",
    "city",
    "region",
    "country",
    "country_code",
    "latitude",
    "longitude",
    "institution_source",
    "confidence",
    "needs_manual_review",
    "notes",
]


class ApplyError(RuntimeError):
    """An expected input, validation, matching, or output error."""


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: Any) -> str:
    title = clean_text(value).casefold()
    title = title.replace("‐", "-").replace("–", "-").replace("—", "-")
    title = title.replace("real-world", "real world")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", title).split())


def normalize_institution_name(value: Any) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", clean_text(value).casefold()).split())


def row_key(row: Dict[str, Any]) -> Tuple[str, str, str, str]:
    return (
        clean_text(row.get("normalized_title")) or normalize_title(row.get("title")),
        clean_text(row.get("author")).casefold(),
        clean_text(row.get("author_position")),
        normalize_institution_name(row.get("institution")),
    )


def parse_coordinate(value: Any, minimum: float, maximum: float) -> Optional[float]:
    text = clean_text(value)
    if not text:
        return None
    try:
        coordinate = float(text)
    except ValueError:
        return None
    if math.isfinite(coordinate) and minimum <= coordinate <= maximum:
        return coordinate
    return None


def parse_candidate_coordinates(row: Dict[str, str]) -> Tuple[float, float]:
    latitude = parse_coordinate(row.get("candidate_latitude"), -90.0, 90.0)
    longitude = parse_coordinate(row.get("candidate_longitude"), -180.0, 180.0)
    if latitude is None or longitude is None:
        raise ApplyError(
            f"Invalid candidate coordinates for {row.get('title')} / "
            f"{row.get('author')} / {row.get('institution')}"
        )
    return latitude, longitude


def coordinates_equivalent(
    existing_latitude: Any,
    existing_longitude: Any,
    candidate_latitude: float,
    candidate_longitude: float,
) -> bool:
    existing_lat = parse_coordinate(existing_latitude, -90.0, 90.0)
    existing_lon = parse_coordinate(existing_longitude, -180.0, 180.0)
    if existing_lat is None or existing_lon is None:
        return False
    return (
        abs(existing_lat - candidate_latitude) < 1e-7
        and abs(existing_lon - candidate_longitude) < 1e-7
    )


def read_csv(
    path: Path,
    required_columns: Iterable[str],
    optional: bool = False,
) -> Tuple[List[Dict[str, str]], List[str]]:
    if not path.exists():
        if optional:
            return [], []
        raise ApplyError(f"Required local input does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            missing = sorted(set(required_columns) - set(fieldnames))
            if missing:
                raise ApplyError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader], fieldnames
    except OSError as error:
        raise ApplyError(f"Could not read {path}: {error}") from error


def file_hash(path: Path) -> str:
    if not path.exists():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_note(existing: Any, note: str) -> str:
    parts = [clean_text(part) for part in clean_text(existing).split("|") if clean_text(part)]
    if note not in parts:
        parts.append(note)
    return " | ".join(parts)


def confirmed_candidate_rows(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    return [
        row
        for row in rows
        if clean_text(row.get("apply_status")).casefold() == "confirmed"
        and clean_text(row.get("candidate_latitude"))
        and clean_text(row.get("candidate_longitude"))
        and clean_text(row.get("candidate_source"))
    ]


def apply_candidates(write: bool) -> Dict[str, Any]:
    before_hash = file_hash(ENRICHMENT)
    candidate_rows, _candidate_fields = read_csv(CANDIDATES, CANDIDATE_COLUMNS)
    enrichment_rows, enrichment_fields = read_csv(ENRICHMENT, ENRICHMENT_COLUMNS)
    if enrichment_fields != ENRICHMENT_COLUMNS:
        # Preserve schema order from the established enrichment table exactly.
        missing_order = [column for column in ENRICHMENT_COLUMNS if column not in enrichment_fields]
        if missing_order:
            raise ApplyError(
                f"{ENRICHMENT} is missing expected output columns: {missing_order}"
            )

    enrichment_by_key: Dict[Tuple[str, str, str, str], List[Dict[str, str]]] = {}
    for row in enrichment_rows:
        enrichment_by_key.setdefault(row_key(row), []).append(row)

    skipped_by_status = sum(
        clean_text(row.get("apply_status")).casefold() != "confirmed"
        for row in candidate_rows
    )
    skipped_empty_coordinates = sum(
        clean_text(row.get("apply_status")).casefold() == "confirmed"
        and (
            not clean_text(row.get("candidate_latitude"))
            or not clean_text(row.get("candidate_longitude"))
        )
        for row in candidate_rows
    )
    skipped_empty_source = sum(
        clean_text(row.get("apply_status")).casefold() == "confirmed"
        and clean_text(row.get("candidate_latitude"))
        and clean_text(row.get("candidate_longitude"))
        and not clean_text(row.get("candidate_source"))
        for row in candidate_rows
    )
    eligible = confirmed_candidate_rows(candidate_rows)

    updated = 0
    rejected_conflicts = 0
    sedid_applicable = False
    for candidate in eligible:
        latitude, longitude = parse_candidate_coordinates(candidate)
        key = row_key(candidate)
        matches = enrichment_by_key.get(key, [])
        if len(matches) != 1:
            rejected_conflicts += 1
            raise ApplyError(
                f"Expected exactly one enrichment match for {key}, found {len(matches)}"
            )
        enrichment = matches[0]
        existing_latitude = clean_text(enrichment.get("latitude"))
        existing_longitude = clean_text(enrichment.get("longitude"))
        if existing_latitude or existing_longitude:
            if not coordinates_equivalent(
                existing_latitude,
                existing_longitude,
                latitude,
                longitude,
            ):
                rejected_conflicts += 1
                raise ApplyError(
                    "Enrichment row already has different coordinates for "
                    f"{candidate.get('title')} / {candidate.get('author')}"
                )
        if normalize_title(candidate.get("title")) == normalize_title(SEDID_TITLE):
            sedid_applicable = True
        if not existing_latitude and not existing_longitude:
            note = (
                "Coordinates applied from key_paper_coordinate_candidates.csv; "
                f"source={clean_text(candidate.get('candidate_source'))}; "
                f"detail={clean_text(candidate.get('candidate_source_detail'))}."
            )
            enrichment["latitude"] = f"{latitude:.8g}"
            enrichment["longitude"] = f"{longitude:.8g}"
            enrichment["notes"] = append_note(enrichment.get("notes"), note)
            updated += 1

    if write and updated:
        write_csv(ENRICHMENT, enrichment_rows, enrichment_fields)
    after_hash = file_hash(ENRICHMENT)
    return {
        "total_candidate_rows": len(candidate_rows),
        "confirmed_rows_with_coordinates": len(eligible),
        "rows_eligible_for_update": len(eligible),
        "rows_skipped_by_status": skipped_by_status,
        "rows_skipped_empty_coordinates": skipped_empty_coordinates,
        "rows_skipped_empty_source": skipped_empty_source,
        "rows_updated": updated if write else 0,
        "rows_would_update": updated,
        "rows_rejected_match_conflict": rejected_conflicts,
        "sedid_has_confirmed_applicable_coordinates": sedid_applicable,
        "enrichment_changed": before_hash != after_hash,
        "before_hash": before_hash,
        "after_hash": after_hash,
    }


def write_csv(
    path: Path,
    rows: Sequence[Dict[str, str]],
    fieldnames: Sequence[str],
) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise ApplyError(f"Could not write {path}: {error}") from error


def print_summary(summary: Dict[str, Any], write: bool) -> None:
    if not write:
        print("DRY RUN: no files were written.")
    print("Key-paper coordinate apply summary:")
    print(f"  Total candidate rows: {summary['total_candidate_rows']}")
    print(
        "  Confirmed rows with coordinates: "
        f"{summary['confirmed_rows_with_coordinates']}"
    )
    print(f"  Rows eligible for update: {summary['rows_eligible_for_update']}")
    print(f"  Rows skipped by status: {summary['rows_skipped_by_status']}")
    print(
        "  Rows skipped because coordinates are empty: "
        f"{summary['rows_skipped_empty_coordinates']}"
    )
    print(
        "  Rows skipped because candidate source is empty: "
        f"{summary['rows_skipped_empty_source']}"
    )
    if write:
        print(f"  Rows updated: {summary['rows_updated']}")
    else:
        print(f"  Rows that would update: {summary['rows_would_update']}")
    print(
        "  Rows rejected due to match conflict: "
        f"{summary['rows_rejected_match_conflict']}"
    )
    print(
        "  SeDID has confirmed/applicable coordinates: "
        f"{summary['sedid_has_confirmed_applicable_coordinates']}"
    )
    print(f"  Enrichment CSV changed: {summary['enrichment_changed']}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Apply only confirmed key-paper coordinate candidates to the "
            "manual affiliation enrichment CSV."
        )
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually write confirmed coordinates (default: dry-run validation only).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        summary = apply_candidates(args.write)
    except ApplyError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print_summary(summary, args.write)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
