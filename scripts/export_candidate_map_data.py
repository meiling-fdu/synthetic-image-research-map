#!/usr/bin/env python3
"""Export uncurated OpenAlex candidate CSVs for exploratory map viewing.

The generated JSON is candidate data only, not curated final literature data. This
script performs no geocoding, calls no APIs, and never writes to data/manual/.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DEFAULT_PAPERS_CSV = Path("data/processed/openalex_candidate_papers.csv")
DEFAULT_AFFILIATIONS_CSV = Path(
    "data/processed/openalex_candidate_affiliations.csv"
)
DEFAULT_OUTPUT = Path("web/data/openalex_candidate_map_data.json")

PAPER_REQUIRED_COLUMNS = {
    "openalex_id",
    "title",
    "year",
    "venue",
    "url",
    "preliminary_task",
    "preliminary_subtask",
    "source_database",
    "manual_review",
    "notes",
}
AFFILIATION_REQUIRED_COLUMNS = {
    "openalex_id",
    "author_name",
    "institution_name",
    "city",
    "country",
    "latitude",
    "longitude",
    "manual_review",
    "notes",
}


class ExportError(RuntimeError):
    """An expected input or output error that should not show a traceback."""


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export processed OpenAlex candidate CSVs as local map JSON. "
            "Only rows with valid coordinates are included."
        )
    )
    parser.add_argument(
        "--papers-csv",
        type=Path,
        default=DEFAULT_PAPERS_CSV,
        help=f"Candidate papers CSV (default: {DEFAULT_PAPERS_CSV}).",
    )
    parser.add_argument(
        "--affiliations-csv",
        type=Path,
        default=DEFAULT_AFFILIATIONS_CSV,
        help=f"Candidate affiliations CSV (default: {DEFAULT_AFFILIATIONS_CSV}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Generated map JSON path (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--max-records",
        type=positive_int,
        help="Maximum number of grouped map records to export.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read, join, and summarize CSVs without writing JSON.",
    )
    return parser.parse_args(argv)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def unique_strings(values: Iterable[Any]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        cleaned = clean_text(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def split_notes(value: Any) -> List[str]:
    note = clean_text(value)
    return [note] if note else []


def parse_bool(value: Any) -> bool:
    return clean_text(value).casefold() in {"1", "true", "yes", "y"}


def parse_year(value: Any) -> Optional[int]:
    cleaned = clean_text(value)
    if not cleaned:
        return None
    try:
        year = int(cleaned)
    except ValueError:
        return None
    return year if 0 < year < 10000 else None


def parse_coordinate(value: Any, minimum: float, maximum: float) -> Optional[float]:
    cleaned = clean_text(value)
    if not cleaned:
        return None
    try:
        coordinate = float(cleaned)
    except ValueError:
        return None
    if not math.isfinite(coordinate) or not minimum <= coordinate <= maximum:
        return None
    return coordinate


def read_csv(path: Path, required_columns: set) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = set(reader.fieldnames or [])
            missing = sorted(required_columns - fieldnames)
            if missing:
                raise ExportError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise ExportError(f"Could not read {path}: {error}") from error


def record_id(openalex_id: str, institution_key: Tuple[Any, ...]) -> str:
    identity = "|".join([openalex_id, *(str(value) for value in institution_key)])
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return f"openalex-candidate-{digest}"


def group_map_records(
    paper_rows: Sequence[Dict[str, str]],
    affiliation_rows: Sequence[Dict[str, str]],
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    papers_by_id = {}
    for paper in paper_rows:
        openalex_id = clean_text(paper.get("openalex_id"))
        if openalex_id and openalex_id not in papers_by_id:
            papers_by_id[openalex_id] = paper

    grouped: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    missing_coordinates = 0
    invalid_coordinates = 0
    unmatched_papers = 0

    for affiliation in affiliation_rows:
        latitude_text = clean_text(affiliation.get("latitude"))
        longitude_text = clean_text(affiliation.get("longitude"))
        if not latitude_text or not longitude_text:
            missing_coordinates += 1
            continue

        latitude = parse_coordinate(latitude_text, -90.0, 90.0)
        longitude = parse_coordinate(longitude_text, -180.0, 180.0)
        if latitude is None or longitude is None:
            invalid_coordinates += 1
            continue

        openalex_id = clean_text(affiliation.get("openalex_id"))
        paper = papers_by_id.get(openalex_id)
        if paper is None:
            unmatched_papers += 1
            continue

        institution_key = (
            clean_text(affiliation.get("institution_name")),
            clean_text(affiliation.get("city")),
            clean_text(affiliation.get("country")),
            latitude,
            longitude,
        )
        group_key = (openalex_id, *institution_key)
        group = grouped.get(group_key)
        if group is None:
            group = {
                "id": record_id(openalex_id, institution_key),
                "title": clean_text(paper.get("title")),
                "year": parse_year(paper.get("year")),
                "task": clean_text(paper.get("preliminary_task")) or "uncertain",
                "subtask": clean_text(paper.get("preliminary_subtask")),
                "venue": clean_text(paper.get("venue")),
                "url": clean_text(paper.get("url")),
                "authors": [],
                "institution": institution_key[0],
                "country": institution_key[2],
                "city": institution_key[1],
                "latitude": latitude,
                "longitude": longitude,
                "source_database": clean_text(paper.get("source_database"))
                or "OpenAlex",
                "manual_review": parse_bool(paper.get("manual_review"))
                or parse_bool(affiliation.get("manual_review")),
                "notes": [],
            }
            grouped[group_key] = group

        author_name = clean_text(affiliation.get("author_name"))
        if author_name and author_name not in group["authors"]:
            group["authors"].append(author_name)
        group["manual_review"] = group["manual_review"] or parse_bool(
            affiliation.get("manual_review")
        )
        group["notes"].extend(split_notes(affiliation.get("notes")))
        group["notes"].extend(split_notes(paper.get("notes")))

    records = []
    for group in grouped.values():
        group["authors"] = unique_strings(group["authors"])
        group["notes"] = " | ".join(unique_strings(group["notes"]))
        records.append(group)

    counters = {
        "affiliation_rows_skipped_missing_coordinates": missing_coordinates,
        "affiliation_rows_skipped_invalid_coordinates": invalid_coordinates,
        "affiliation_rows_skipped_unmatched_paper": unmatched_papers,
    }
    return records, counters


def build_export(
    paper_rows: Sequence[Dict[str, str]],
    affiliation_rows: Sequence[Dict[str, str]],
    max_records: Optional[int],
) -> Dict[str, Any]:
    records, counters = group_map_records(paper_rows, affiliation_rows)
    available_records = len(records)
    if max_records is not None:
        records = records[:max_records]

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    summary = {
        "candidate_papers_read": len(paper_rows),
        "affiliation_rows_read": len(affiliation_rows),
        "map_records_available_before_limit": available_records,
        "map_records_exported": len(records),
        **counters,
    }
    return {
        "dataset_type": "openalex_candidate_map_data",
        "notice": (
            "Automatically generated OpenAlex candidate data for exploratory local "
            "visualization only. These records are not curated final data."
        ),
        "generated_at": generated_at.replace("+00:00", "Z"),
        "records": records,
        "summary": summary,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary_path.replace(path)
    except OSError as error:
        raise ExportError(f"Could not write {path}: {error}") from error


def print_summary(summary: Dict[str, int]) -> None:
    print("Export summary:")
    print(f"  Candidate papers read: {summary['candidate_papers_read']}")
    print(f"  Affiliation rows read: {summary['affiliation_rows_read']}")
    print(f"  Map records exported: {summary['map_records_exported']}")
    print(
        "  Rows skipped because coordinates were missing: "
        f"{summary['affiliation_rows_skipped_missing_coordinates']}"
    )
    if summary["affiliation_rows_skipped_invalid_coordinates"]:
        print(
            "  Rows skipped because coordinates were invalid: "
            f"{summary['affiliation_rows_skipped_invalid_coordinates']}"
        )
    if summary["affiliation_rows_skipped_unmatched_paper"]:
        print(
            "  Rows skipped because no matching paper was found: "
            f"{summary['affiliation_rows_skipped_unmatched_paper']}"
        )


def run(args: argparse.Namespace) -> int:
    try:
        paper_rows = read_csv(args.papers_csv, PAPER_REQUIRED_COLUMNS)
        affiliation_rows = read_csv(
            args.affiliations_csv, AFFILIATION_REQUIRED_COLUMNS
        )
        payload = build_export(paper_rows, affiliation_rows, args.max_records)
    except ExportError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("DRY RUN: no files were written.")
        print(f"Would write: {args.output}")
    else:
        try:
            write_json(args.output, payload)
        except ExportError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print(f"Wrote exploratory candidate map data: {args.output}")

    print_summary(payload["summary"])
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
