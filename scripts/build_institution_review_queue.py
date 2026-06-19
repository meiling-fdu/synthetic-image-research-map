#!/usr/bin/env python3
"""Build an uncurated institution review queue from candidate geocoding data.

This script only identifies records for human review. It never modifies the manual
institution correction table and does not promote candidate metadata to curated data.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Deque, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from geocode_candidate_affiliations import normalize_institution_name
except ModuleNotFoundError:
    from scripts.geocode_candidate_affiliations import normalize_institution_name


DEFAULT_ORIGINAL = Path(
    "data/processed/openalex_candidate_affiliations_in_scope.csv"
)
DEFAULT_GEOCODED = Path(
    "data/processed/openalex_candidate_affiliations_geocoded.csv"
)
DEFAULT_OUTPUT = Path("data/processed/institution_review_queue.csv")
MANUAL_DATA_DIR = Path("data/manual")

QUEUE_COLUMNS = (
    "institution_name",
    "city",
    "country",
    "example_raw_affiliation_text",
    "example_author_name",
    "example_openalex_id",
    "reason",
    "suggested_match_key",
    "current_latitude",
    "current_longitude",
    "manual_action",
    "notes",
)

REQUIRED_COLUMNS = {
    "openalex_id",
    "author_name",
    "institution_name",
    "city",
    "country",
    "latitude",
    "longitude",
    "raw_affiliation_text",
    "notes",
}

SUSPICIOUS_GENERIC_NAMES = (
    "Microsoft",
    "Meta",
    "Google",
    "Adobe",
    "OpenAI",
    "National Institute",
    "Cambridge School",
    "Institute of Art",
)

REASON_ORDER = (
    "missing_coordinates",
    "invalid_coordinates",
    "geocoding_failed",
    "institution_name_changed",
    "suspicious_generic_name",
)

FAILURE_NOTE_PHRASES = (
    "geocoding failed",
    "nominatim found no result",
    "geocoding not attempted",
    "geocoding was not completed",
    "could not reach nominatim",
    "rate limit",
)


class QueueError(RuntimeError):
    """An expected file or schema error shown without a traceback."""


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deduplicated review queue from original and geocoded "
            "OpenAlex candidate affiliation CSVs."
        )
    )
    parser.add_argument(
        "--original",
        type=Path,
        default=DEFAULT_ORIGINAL,
        help=f"Original candidate affiliations (default: {DEFAULT_ORIGINAL}).",
    )
    parser.add_argument(
        "--geocoded",
        type=Path,
        default=DEFAULT_GEOCODED,
        help=f"Geocoded candidate affiliations (default: {DEFAULT_GEOCODED}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Generated review queue (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and summarize the queue without writing a CSV.",
    )
    parser.add_argument(
        "--include-out-of-scope",
        action="store_true",
        help=(
            "Include rows marked in_scope=false when broader input files are "
            "provided for debugging."
        ),
    )
    parser.add_argument(
        "--max-examples",
        type=positive_int,
        help="Maximum deduplicated review entries to write or preview.",
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


def parse_bool(value: Any) -> bool:
    return clean_text(value).casefold() in {"1", "true", "yes", "y"}


def select_scope_rows(
    rows: Sequence[Dict[str, str]], include_out_of_scope: bool
) -> List[Dict[str, str]]:
    if include_out_of_scope or not any("in_scope" in row for row in rows):
        return list(rows)
    return [row for row in rows if parse_bool(row.get("in_scope"))]


def read_csv(path: Path) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
            if missing:
                raise QueueError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise QueueError(f"Could not read {path}: {error}") from error


def path_is_in_manual_data(path: Path) -> bool:
    try:
        path.resolve().relative_to(MANUAL_DATA_DIR.resolve())
        return True
    except ValueError:
        return False


def coordinate_status(latitude: Any, longitude: Any) -> str:
    latitude_text = clean_text(latitude)
    longitude_text = clean_text(longitude)
    if not latitude_text or not longitude_text:
        return "missing"
    try:
        latitude_value = float(latitude_text)
        longitude_value = float(longitude_text)
    except ValueError:
        return "invalid"
    if (
        not math.isfinite(latitude_value)
        or not math.isfinite(longitude_value)
        or not -90.0 <= latitude_value <= 90.0
        or not -180.0 <= longitude_value <= 180.0
    ):
        return "invalid"
    return "valid"


def notes_indicate_failure(notes: Any) -> bool:
    normalized = clean_text(notes).casefold()
    return any(phrase in normalized for phrase in FAILURE_NOTE_PHRASES)


def is_suspicious_generic_name(name: Any) -> bool:
    normalized_name = normalize_institution_name(name)
    if not normalized_name:
        return False
    padded_name = f" {normalized_name} "
    for generic_name in SUSPICIOUS_GENERIC_NAMES:
        normalized_generic = normalize_institution_name(generic_name)
        if f" {normalized_generic} " in padded_name:
            return True
    return False


def authorship_identity(row: Dict[str, str]) -> Tuple[str, ...]:
    return tuple(
        clean_text(row.get(column)).casefold()
        for column in (
            "openalex_id",
            "author_name",
            "author_position",
            "ror_id",
            "raw_affiliation_text",
        )
    )


def pair_original_rows(
    original_rows: Sequence[Dict[str, str]],
    geocoded_rows: Sequence[Dict[str, str]],
) -> List[Optional[Dict[str, str]]]:
    """Pair occurrence-aware authorship identities without assuming unique authors."""
    originals_by_identity: Dict[Tuple[str, ...], Deque[Dict[str, str]]] = defaultdict(deque)
    for row in original_rows:
        originals_by_identity[authorship_identity(row)].append(row)

    paired = []
    for index, row in enumerate(geocoded_rows):
        candidates = originals_by_identity.get(authorship_identity(row))
        if candidates:
            paired.append(candidates.popleft())
        elif index < len(original_rows):
            paired.append(original_rows[index])
        else:
            paired.append(None)
    return paired


def row_reasons(
    original: Optional[Dict[str, str]],
    geocoded: Dict[str, str],
) -> List[str]:
    reasons = []
    coordinate_state = coordinate_status(
        geocoded.get("latitude"), geocoded.get("longitude")
    )
    if coordinate_state == "missing":
        reasons.append("missing_coordinates")
    elif coordinate_state == "invalid":
        reasons.append("invalid_coordinates")

    notes = clean_text(geocoded.get("notes"))
    if notes_indicate_failure(notes):
        reasons.append("geocoding_failed")

    original_name = clean_text(original.get("institution_name")) if original else ""
    current_name = clean_text(geocoded.get("institution_name"))
    manual_correction_applied = "manual institution correction applied" in notes.casefold()
    if (
        original is not None
        and normalize_institution_name(original_name)
        != normalize_institution_name(current_name)
        and not manual_correction_applied
    ):
        reasons.append("institution_name_changed")

    if is_suspicious_generic_name(current_name or original_name):
        reasons.append("suspicious_generic_name")
    return reasons


def queue_key(row: Dict[str, str], original: Optional[Dict[str, str]]) -> Tuple[str, str, str]:
    institution = clean_text(row.get("institution_name")) or (
        clean_text(original.get("institution_name")) if original else ""
    )
    city = clean_text(row.get("city")) or (
        clean_text(original.get("city")) if original else ""
    )
    country = clean_text(row.get("country")) or (
        clean_text(original.get("country")) if original else ""
    )
    return (
        normalize_institution_name(institution),
        normalize_institution_name(city),
        normalize_institution_name(country),
    )


def choose_manual_action(reasons: Sequence[str]) -> str:
    reason_set = set(reasons)
    if "institution_name_changed" in reason_set:
        return "inspect_possible_mismatch"
    if reason_set & {"missing_coordinates", "geocoding_failed"}:
        return "add_manual_correction"
    return "verify_coordinates"


def build_queue(
    original_rows: Sequence[Dict[str, str]],
    geocoded_rows: Sequence[Dict[str, str]],
) -> List[Dict[str, str]]:
    paired_originals = pair_original_rows(original_rows, geocoded_rows)
    grouped: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    for original, geocoded in zip(paired_originals, geocoded_rows):
        reasons = row_reasons(original, geocoded)
        if not reasons:
            continue

        key = queue_key(geocoded, original)
        institution = clean_text(geocoded.get("institution_name")) or (
            clean_text(original.get("institution_name")) if original else ""
        )
        city = clean_text(geocoded.get("city")) or (
            clean_text(original.get("city")) if original else ""
        )
        country = clean_text(geocoded.get("country")) or (
            clean_text(original.get("country")) if original else ""
        )

        group = grouped.get(key)
        if group is None:
            group = {
                "institution_name": institution,
                "city": city,
                "country": country,
                "example_raw_affiliation_text": clean_text(
                    geocoded.get("raw_affiliation_text")
                ),
                "example_author_name": clean_text(geocoded.get("author_name")),
                "example_openalex_id": clean_text(geocoded.get("openalex_id")),
                "current_latitude": clean_text(geocoded.get("latitude")),
                "current_longitude": clean_text(geocoded.get("longitude")),
                "reasons": set(),
                "source_notes": [],
                "row_count": 0,
            }
            grouped[key] = group

        group["reasons"].update(reasons)
        group["source_notes"].append(geocoded.get("notes"))
        group["row_count"] += 1
        for target, source in (
            ("example_raw_affiliation_text", "raw_affiliation_text"),
            ("example_author_name", "author_name"),
            ("example_openalex_id", "openalex_id"),
            ("current_latitude", "latitude"),
            ("current_longitude", "longitude"),
        ):
            if not group[target]:
                group[target] = clean_text(geocoded.get(source))

    queue = []
    for group in grouped.values():
        ordered_reasons = [
            reason for reason in REASON_ORDER if reason in group["reasons"]
        ]
        source_notes = unique_strings(group["source_notes"])
        notes = (
            "Automatically generated from candidate metadata; not curated final data. "
            f"Grouped candidate affiliation rows: {group['row_count']}."
        )
        if source_notes:
            notes += f" Example source note: {source_notes[0]}"
        queue.append(
            {
                "institution_name": group["institution_name"],
                "city": group["city"],
                "country": group["country"],
                "example_raw_affiliation_text": group[
                    "example_raw_affiliation_text"
                ],
                "example_author_name": group["example_author_name"],
                "example_openalex_id": group["example_openalex_id"],
                "reason": ";".join(ordered_reasons),
                "suggested_match_key": normalize_institution_name(
                    group["institution_name"]
                ),
                "current_latitude": group["current_latitude"],
                "current_longitude": group["current_longitude"],
                "manual_action": choose_manual_action(ordered_reasons),
                "notes": notes,
            }
        )
    return queue


def write_queue(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=QUEUE_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        raise QueueError(f"Could not write review queue {path}: {error}") from error


def print_summary(
    original_count: int,
    geocoded_count: int,
    downstream_count: int,
    queue: Sequence[Dict[str, str]],
    available_count: int,
) -> None:
    reason_counts = Counter(
        reason
        for row in queue
        for reason in clean_text(row.get("reason")).split(";")
        if reason
    )
    print("Institution review queue summary:")
    print(f"  Original affiliation rows read: {original_count}")
    print(f"  Geocoded affiliation rows read: {geocoded_count}")
    print(f"  Downstream rows processed: {downstream_count}")
    print(f"  Deduplicated review entries available: {available_count}")
    print(f"  Review entries selected: {len(queue)}")
    for reason in REASON_ORDER:
        if reason_counts[reason]:
            print(f"  {reason}: {reason_counts[reason]}")


def run(args: argparse.Namespace) -> int:
    if path_is_in_manual_data(args.output):
        print("Error: review queue output must not be inside data/manual/.", file=sys.stderr)
        return 1
    try:
        original_rows = read_csv(args.original)
        geocoded_rows = read_csv(args.geocoded)
    except QueueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    original_count = len(original_rows)
    geocoded_count = len(geocoded_rows)
    original_rows = select_scope_rows(original_rows, args.include_out_of_scope)
    geocoded_rows = select_scope_rows(geocoded_rows, args.include_out_of_scope)
    queue = build_queue(original_rows, geocoded_rows)

    available_count = len(queue)
    if args.max_examples is not None:
        queue = queue[: args.max_examples]

    if args.dry_run:
        print("DRY RUN: no files were written.")
        print(f"Would write: {args.output}")
        for row in queue[:5]:
            label = row["institution_name"] or "(missing institution name)"
            print(f"  Example: {label} [{row['reason']}]")
    else:
        try:
            write_queue(args.output, queue)
        except QueueError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print(f"Wrote institution review queue: {args.output}")

    print_summary(
        original_count,
        geocoded_count,
        len(geocoded_rows),
        queue,
        available_count,
    )
    print("Queue entries are candidate review aids, not curated institution metadata.")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
