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


DEFAULT_PAPERS_CSV = Path(
    "data/processed/openalex_candidate_papers_in_scope.csv"
)
DEFAULT_AFFILIATIONS_CSV = Path(
    "data/processed/openalex_candidate_affiliations_geocoded.csv"
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
    parser.add_argument(
        "--include-out-of-scope",
        action="store_true",
        help=(
            "Include papers marked in_scope=false for debugging. By default, "
            "paper IDs and affiliation rows are restricted to in-scope papers."
        ),
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


def paper_is_in_scope(row: Dict[str, str]) -> bool:
    # Older explicitly scoped CSVs may predate the column; current extraction always adds it.
    return parse_bool(row.get("in_scope")) if "in_scope" in row else True


def select_scope_rows(
    paper_rows: Sequence[Dict[str, str]],
    affiliation_rows: Sequence[Dict[str, str]],
    include_out_of_scope: bool,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], Dict[str, int]]:
    in_scope_papers = [paper for paper in paper_rows if paper_is_in_scope(paper)]
    selected_papers = list(paper_rows) if include_out_of_scope else in_scope_papers
    selected_ids = {
        clean_text(paper.get("openalex_id"))
        for paper in selected_papers
        if clean_text(paper.get("openalex_id"))
    }
    in_scope_ids = {
        clean_text(paper.get("openalex_id"))
        for paper in in_scope_papers
        if clean_text(paper.get("openalex_id"))
    }
    in_scope_affiliation_count = sum(
        clean_text(row.get("openalex_id")) in in_scope_ids
        for row in affiliation_rows
    )
    selected_affiliations = [
        row
        for row in affiliation_rows
        if clean_text(row.get("openalex_id")) in selected_ids
    ]
    counts = {
        "total_candidate_papers": len(paper_rows),
        "in_scope_papers": len(in_scope_papers),
        "out_of_scope_papers": len(paper_rows) - len(in_scope_papers),
        "total_affiliation_rows": len(affiliation_rows),
        "in_scope_affiliation_rows": in_scope_affiliation_count,
        "downstream_rows_processed": len(selected_affiliations),
    }
    return selected_papers, selected_affiliations, counts


def parse_year(value: Any) -> Optional[int]:
    cleaned = clean_text(value)
    if not cleaned:
        return None
    try:
        year = int(cleaned)
    except ValueError:
        return None
    return year if 0 < year < 10000 else None


def parse_positive_int(value: Any) -> Optional[int]:
    cleaned = clean_text(value)
    if not cleaned:
        return None
    try:
        parsed = int(cleaned)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def parse_ordered_authors(value: Any) -> List[str]:
    """Parse the JSON-encoded paper-level author list from the candidate CSV."""
    raw_value = str(value or "").strip()
    if not raw_value:
        return []
    try:
        authors = json.loads(raw_value)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(authors, list):
        return []
    return [name for name in (clean_text(author) for author in authors) if name]


def fallback_authors_by_paper(
    affiliation_rows: Sequence[Dict[str, str]],
) -> Dict[str, List[str]]:
    """Reconstruct one ordered list per paper for pre-authors_ordered CSVs."""
    authors: Dict[str, Dict[str, Tuple[int, int, str]]] = {}
    for row_index, affiliation in enumerate(affiliation_rows):
        openalex_id = clean_text(affiliation.get("openalex_id"))
        author_name = clean_text(affiliation.get("author_name"))
        if not openalex_id or not author_name:
            continue
        author_order = parse_positive_int(affiliation.get("author_order"))
        author_id = clean_text(affiliation.get("author_openalex_id"))
        identity = author_id or f"{author_order or ''}:{author_name.casefold()}"
        paper_authors = authors.setdefault(openalex_id, {})
        if identity not in paper_authors:
            paper_authors[identity] = (
                author_order if author_order is not None else 10**9,
                row_index,
                author_name,
            )
    return {
        openalex_id: [item[2] for item in sorted(paper_authors.values())]
        for openalex_id, paper_authors in authors.items()
    }


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


def preferred_value(row: Dict[str, str], resolved_column: str, original_column: str) -> str:
    return clean_text(row.get(resolved_column)) or clean_text(row.get(original_column))


def preferred_coordinates(
    row: Dict[str, str],
) -> Tuple[Optional[float], Optional[float], str, str]:
    """Choose a complete valid coordinate pair without mixing resolution sources."""
    pairs = (
        (
            clean_text(row.get("resolved_latitude")),
            clean_text(row.get("resolved_longitude")),
            "resolved",
        ),
        (
            clean_text(row.get("latitude")),
            clean_text(row.get("longitude")),
            "original",
        ),
    )
    has_complete_pair = False
    for latitude_text, longitude_text, source in pairs:
        if not latitude_text or not longitude_text:
            continue
        has_complete_pair = True
        latitude = parse_coordinate(latitude_text, -90.0, 90.0)
        longitude = parse_coordinate(longitude_text, -180.0, 180.0)
        if latitude is not None and longitude is not None:
            return latitude, longitude, source, ""
    failure = "invalid" if has_complete_pair else "missing"
    return None, None, "", failure


def has_resolution_metadata(row: Dict[str, str]) -> bool:
    return any(
        column in row
        for column in (
            "resolution_method",
            "resolution_confidence",
            "needs_review",
            "resolution_notes",
        )
    )


def group_map_records(
    paper_rows: Sequence[Dict[str, str]],
    affiliation_rows: Sequence[Dict[str, str]],
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    papers_by_id = {}
    for paper in paper_rows:
        openalex_id = clean_text(paper.get("openalex_id"))
        if openalex_id and openalex_id not in papers_by_id:
            papers_by_id[openalex_id] = paper

    legacy_authors = fallback_authors_by_paper(affiliation_rows)
    authors_by_paper = {
        openalex_id: (
            parse_ordered_authors(paper.get("authors_ordered"))
            or legacy_authors.get(openalex_id, [])
        )
        for openalex_id, paper in papers_by_id.items()
    }

    grouped: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    missing_coordinates = 0
    invalid_coordinates = 0
    unmatched_papers = 0
    skipped_record_keys = set()

    for affiliation in affiliation_rows:
        institution = preferred_value(
            affiliation, "resolved_institution_name", "institution_name"
        )
        city = preferred_value(affiliation, "resolved_city", "city")
        country = preferred_value(
            affiliation, "resolved_country", "country"
        ) or clean_text(affiliation.get("country_code"))
        institution_openalex_id = clean_text(
            affiliation.get("institution_openalex_id")
        )
        latitude, longitude, coordinate_source, coordinate_failure = (
            preferred_coordinates(affiliation)
        )
        if latitude is None or longitude is None:
            if coordinate_failure == "missing":
                missing_coordinates += 1
            else:
                invalid_coordinates += 1
            skipped_record_keys.add(
                (
                    clean_text(affiliation.get("openalex_id")),
                    institution,
                    city,
                    country,
                )
            )
            continue

        openalex_id = clean_text(affiliation.get("openalex_id"))
        paper = papers_by_id.get(openalex_id)
        if paper is None:
            unmatched_papers += 1
            continue

        institution_key = (
            institution_openalex_id,
            institution,
            city,
            country,
            latitude,
            longitude,
        )
        group_key = (openalex_id, *institution_key)
        group = grouped.get(group_key)
        if group is None:
            publication_year = parse_year(
                clean_text(paper.get("publication_year")) or paper.get("year")
            )
            venue_name = clean_text(paper.get("venue_name")) or clean_text(
                paper.get("venue")
            )
            primary_url = clean_text(paper.get("primary_url")) or clean_text(
                paper.get("url")
            )
            group = {
                "id": record_id(openalex_id, institution_key),
                "title": clean_text(paper.get("title")),
                "in_scope": paper_is_in_scope(paper),
                # Keep legacy aliases so existing sample/front-end behavior remains valid.
                "year": publication_year,
                "publication_year": publication_year,
                "publication_date": clean_text(paper.get("publication_date")),
                "task": clean_text(paper.get("preliminary_task")) or "uncertain",
                "subtask": clean_text(paper.get("preliminary_subtask")),
                "venue": venue_name,
                "venue_name": venue_name,
                "venue_type": clean_text(paper.get("venue_type")),
                "publisher": clean_text(paper.get("publisher")),
                "publication_type": clean_text(paper.get("publication_type")),
                "doi": clean_text(paper.get("doi")),
                "arxiv_id": clean_text(paper.get("arxiv_id")),
                "arxiv_url": clean_text(paper.get("arxiv_url")),
                "primary_url": primary_url,
                "landing_page_url": clean_text(paper.get("landing_page_url")),
                "openalex_url": clean_text(paper.get("openalex_url")) or openalex_id,
                "is_arxiv_preprint": parse_bool(paper.get("is_arxiv_preprint")),
                "url": primary_url,
                "authors": list(authors_by_paper.get(openalex_id, [])),
                "institution_openalex_id": institution_key[0],
                "institution": institution_key[1],
                "country": institution_key[3],
                "city": institution_key[2],
                "latitude": latitude,
                "longitude": longitude,
                "source_database": clean_text(paper.get("source_database"))
                or "OpenAlex",
                "manual_review": parse_bool(paper.get("manual_review"))
                or parse_bool(affiliation.get("manual_review")),
                "notes": [],
                "_coordinate_sources": set(),
                "_has_resolution_metadata": False,
                "_resolution_notes": [],
            }
            grouped[group_key] = group

        group["_coordinate_sources"].add(coordinate_source)
        if has_resolution_metadata(affiliation):
            group["_has_resolution_metadata"] = True
            if not group.get("resolution_method"):
                group["resolution_method"] = clean_text(
                    affiliation.get("resolution_method")
                )
            if not group.get("resolution_confidence"):
                group["resolution_confidence"] = clean_text(
                    affiliation.get("resolution_confidence")
                )
            group["needs_review"] = group.get("needs_review", False) or parse_bool(
                affiliation.get("needs_review")
            )
            group["_resolution_notes"].extend(
                split_notes(affiliation.get("resolution_notes"))
            )

        group["manual_review"] = group["manual_review"] or parse_bool(
            affiliation.get("manual_review")
        )
        group["notes"].extend(split_notes(affiliation.get("notes")))
        group["notes"].extend(split_notes(paper.get("notes")))

    records = []
    for group in grouped.values():
        group["notes"] = " | ".join(unique_strings(group["notes"]))
        if group["_has_resolution_metadata"]:
            group["resolution_notes"] = " | ".join(
                unique_strings(group["_resolution_notes"])
            )
        records.append(group)

    counters = {
        "affiliation_rows_skipped_missing_coordinates": missing_coordinates,
        "affiliation_rows_skipped_invalid_coordinates": invalid_coordinates,
        "affiliation_rows_skipped_unmatched_paper": unmatched_papers,
        "map_records_skipped_missing_coordinates": len(skipped_record_keys),
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

    resolved_coordinate_records = sum(
        "resolved" in record["_coordinate_sources"] for record in records
    )
    original_coordinate_records = sum(
        "resolved" not in record["_coordinate_sources"]
        and "original" in record["_coordinate_sources"]
        for record in records
    )
    records_needing_review = sum(
        record.get("needs_review") is True for record in records
    )
    for record in records:
        record.pop("_coordinate_sources", None)
        record.pop("_has_resolution_metadata", None)
        record.pop("_resolution_notes", None)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    summary = {
        "candidate_papers_read": len(paper_rows),
        "affiliation_rows_read": len(affiliation_rows),
        "map_records_available_before_limit": available_records,
        "map_records_exported": len(records),
        "map_records_using_resolved_coordinates": resolved_coordinate_records,
        "map_records_using_original_coordinates": original_coordinate_records,
        "map_records_marked_needs_review": records_needing_review,
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
    print(f"  Total candidate papers: {summary['total_candidate_papers']}")
    print(f"  In-scope papers: {summary['in_scope_papers']}")
    print(f"  Out-of-scope papers: {summary['out_of_scope_papers']}")
    print(f"  Total affiliation rows: {summary['total_affiliation_rows']}")
    print(f"  In-scope affiliation rows: {summary['in_scope_affiliation_rows']}")
    print(f"  Downstream rows processed: {summary['downstream_rows_processed']}")
    print(f"  Candidate papers read: {summary['candidate_papers_read']}")
    print(f"  Affiliation rows read: {summary['affiliation_rows_read']}")
    print(f"  Map records exported: {summary['map_records_exported']}")
    print(
        "  Map records using resolved coordinates: "
        f"{summary['map_records_using_resolved_coordinates']}"
    )
    print(
        "  Map records using original coordinates: "
        f"{summary['map_records_using_original_coordinates']}"
    )
    print(
        "  Map records skipped because coordinates were missing or invalid: "
        f"{summary['map_records_skipped_missing_coordinates']}"
    )
    print(
        "  Exported records marked needs_review=true: "
        f"{summary['map_records_marked_needs_review']}"
    )
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
        all_paper_rows = read_csv(args.papers_csv, PAPER_REQUIRED_COLUMNS)
        all_affiliation_rows = read_csv(
            args.affiliations_csv, AFFILIATION_REQUIRED_COLUMNS
        )
        paper_rows, affiliation_rows, scope_counts = select_scope_rows(
            all_paper_rows,
            all_affiliation_rows,
            args.include_out_of_scope,
        )
        payload = build_export(paper_rows, affiliation_rows, args.max_records)
        payload["summary"].update(scope_counts)
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
