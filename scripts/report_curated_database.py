#!/usr/bin/env python3
"""Print a lightweight summary of the curated CSV database layer."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from typing import Dict, List

try:
    from .curated_schema import CURATED_DATA_DIR, EXPECTED_COLUMNS
except ImportError:  # Support direct execution from the repository root.
    from curated_schema import CURATED_DATA_DIR, EXPECTED_COLUMNS


TRUE_VALUES = {"true", "1", "yes", "y"}
COMPLETED_LOCATION_STATUSES = {"confirmed", "known", "resolved", "reviewed"}


class ReportInputError(RuntimeError):
    """A missing or malformed curated input that prevents reporting."""


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def read_rows(filename: str) -> List[Dict[str, str]]:
    path = CURATED_DATA_DIR / filename
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS[filename]:
                raise ReportInputError(
                    f"{path} does not have the expected header; run the validator"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise ReportInputError(f"could not read {path}: {error}") from error
    except (UnicodeError, csv.Error) as error:
        raise ReportInputError(f"invalid CSV in {path}: {error}") from error


def print_breakdown(label: str, counts: Counter[str]) -> None:
    print(f"{label}:")
    if not counts:
        print("  (none)")
        return
    for value, count in sorted(counts.items()):
        print(f"  {value or '(blank)'}: {count}")


def main() -> int:
    try:
        papers = read_rows("papers.csv")
        mappings = read_rows("author_institution_mappings.csv")
        exclusions = read_rows("paper_exclusions.csv")
        locations = read_rows("institution_location_review.csv")
    except ReportInputError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    active_exclusions = sum(
        clean(row.get("is_active")).casefold() in TRUE_VALUES for row in exclusions
    )
    pending_institutions = {
        clean(row.get("institution"))
        for row in locations
        if clean(row.get("institution"))
        and (
            clean(row.get("coordinate_status")).casefold() != "known"
            or clean(row.get("location_status")).casefold()
            not in COMPLETED_LOCATION_STATUSES
        )
    }

    print("Curated database report")
    print(f"Curated papers: {len(papers)}")
    print(f"Curated mappings: {len(mappings)}")
    print(f"Active exclusions: {active_exclusions}")
    print(f"Institutions pending location review: {len(pending_institutions)}")
    print_breakdown(
        "Papers by task", Counter(clean(row.get("task")) for row in papers)
    )
    print_breakdown(
        "Papers by curation_status",
        Counter(clean(row.get("curation_status")) for row in papers),
    )
    print_breakdown(
        "Exclusions by reason",
        Counter(clean(row.get("reason")) for row in exclusions),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
