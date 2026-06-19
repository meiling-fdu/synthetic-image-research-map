#!/usr/bin/env python3
"""Filter local candidate map data into a commit-safe public preview.

The public preview remains uncurated candidate metadata. This script only reads
an existing map export, calls no APIs, and never writes to data/manual/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


DEFAULT_INPUT = Path("web/data/openalex_candidate_map_data.json")
DEFAULT_OUTPUT = Path("web/data/public_preview_map_data.json")
DEFAULT_MAX_RECORDS = 200
DEFAULT_MIN_CONFIDENCE = "medium"

CONFIDENCE_RANK = {
    "unresolved": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}
PUBLIC_FIELDS = (
    "id",
    "title",
    "in_scope",
    "year",
    "publication_year",
    "publication_date",
    "task",
    "subtask",
    "venue",
    "venue_name",
    "venue_type",
    "publisher",
    "publication_type",
    "doi",
    "arxiv_id",
    "arxiv_url",
    "primary_url",
    "landing_page_url",
    "openalex_url",
    "is_arxiv_preprint",
    "url",
    "authors",
    "institution",
    "country",
    "city",
    "latitude",
    "longitude",
    "source_database",
    "resolution_method",
    "resolution_confidence",
    "needs_review",
    "notes",
)
PUBLIC_METADATA = {
    "dataset_type": "uncurated_public_preview",
    "generated_from": "OpenAlex candidate metadata",
    "warning": (
        "Automatically generated candidate metadata; not a manually curated "
        "bibliography."
    ),
}


class PreviewExportError(RuntimeError):
    """An expected input or output error that should not show a traceback."""


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a filtered, field-limited public preview from local "
            "OpenAlex candidate map data."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Map-ready candidate JSON (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Public preview JSON (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--max-records",
        type=positive_int,
        default=DEFAULT_MAX_RECORDS,
        help=f"Maximum records to publish (default: {DEFAULT_MAX_RECORDS}).",
    )
    parser.add_argument(
        "--min-confidence",
        choices=tuple(CONFIDENCE_RANK),
        default=DEFAULT_MIN_CONFIDENCE,
        help=(
            "Minimum institution resolution confidence "
            f"(default: {DEFAULT_MIN_CONFIDENCE})."
        ),
    )
    parser.add_argument(
        "--include-needs-review",
        action="store_true",
        help="Include records marked needs_review=true (excluded by default).",
    )
    parser.add_argument(
        "--include-out-of-scope",
        action="store_true",
        help="Include map records not marked in_scope=true for debugging.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print filtering results without writing the public JSON file.",
    )
    return parser.parse_args(argv)


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().casefold() in {"1", "true", "yes", "y"}


def normalize_confidence(value: Any) -> str:
    confidence = str(value or "").strip().casefold()
    return confidence if confidence in CONFIDENCE_RANK else "unresolved"


def read_candidate_records(path: Path) -> List[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise PreviewExportError(f"Could not read {path}: {error}") from error

    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise PreviewExportError(f"{path} must contain a JSON object with a records list")
    if not all(isinstance(record, dict) for record in payload["records"]):
        raise PreviewExportError(f"{path} contains a non-object map record")
    return payload["records"]


def build_preview(
    records: Sequence[Dict[str, Any]],
    max_records: int,
    min_confidence: str,
    include_needs_review: bool,
    include_out_of_scope: bool = False,
) -> Tuple[Dict[str, Any], Dict[str, int]]:
    minimum_rank = CONFIDENCE_RANK[min_confidence]
    selected = []
    below_confidence = 0
    excluded_needs_review = 0
    excluded_out_of_scope = 0

    for record in records:
        in_scope = parse_bool(record.get("in_scope"))
        if not in_scope and not include_out_of_scope:
            excluded_out_of_scope += 1
            continue

        confidence = normalize_confidence(record.get("resolution_confidence"))
        if CONFIDENCE_RANK[confidence] < minimum_rank:
            below_confidence += 1
            continue

        needs_review = parse_bool(record.get("needs_review"))
        if needs_review and not include_needs_review:
            excluded_needs_review += 1
            continue

        # Whitelisting prevents source-only or future internal fields from being
        # published accidentally when the local candidate schema expands.
        public_record = {
            field: record.get(field) for field in PUBLIC_FIELDS if field in record
        }
        public_record["resolution_confidence"] = confidence
        public_record["needs_review"] = needs_review
        public_record["in_scope"] = in_scope
        selected.append(public_record)

    eligible_records = len(selected)
    selected = selected[:max_records]
    summary = {
        "candidate_records_read": len(records),
        "records_excluded_out_of_scope": excluded_out_of_scope,
        "records_excluded_below_confidence": below_confidence,
        "records_excluded_needs_review": excluded_needs_review,
        "records_eligible_before_limit": eligible_records,
        "records_exported": len(selected),
    }
    return {"metadata": dict(PUBLIC_METADATA), "records": selected}, summary


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary_path.replace(path)
    except OSError as error:
        raise PreviewExportError(f"Could not write {path}: {error}") from error


def print_summary(summary: Dict[str, int], output: Path, dry_run: bool) -> None:
    print("Public preview export summary:")
    print(f"  Candidate records read: {summary['candidate_records_read']}")
    print(
        "  Records excluded as out of scope: "
        f"{summary['records_excluded_out_of_scope']}"
    )
    print(
        "  Records excluded below confidence threshold: "
        f"{summary['records_excluded_below_confidence']}"
    )
    print(
        "  Records excluded because they need review: "
        f"{summary['records_excluded_needs_review']}"
    )
    print(
        "  Records eligible before maximum: "
        f"{summary['records_eligible_before_limit']}"
    )
    print(f"  Records exported: {summary['records_exported']}")
    print(f"  Downstream rows processed: {summary['records_exported']}")
    print(f"  Output: {output}{' (not written; dry run)' if dry_run else ''}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        records = read_candidate_records(args.input)
        payload, summary = build_preview(
            records,
            args.max_records,
            args.min_confidence,
            args.include_needs_review,
            args.include_out_of_scope,
        )
        if not args.dry_run:
            write_json(args.output, payload)
        print_summary(summary, args.output, args.dry_run)
    except PreviewExportError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
