#!/usr/bin/env python3
"""Add deterministic affiliation order values without changing row sequence."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

try:
    from .curated_mappings import ACTIVE_MAPPING_STATUSES, save_mappings
    from .curated_schema import AUTHOR_INSTITUTION_MAPPING_COLUMNS, CURATED_DATA_DIR
except ImportError:
    from curated_mappings import ACTIVE_MAPPING_STATUSES, save_mappings
    from curated_schema import AUTHOR_INSTITUTION_MAPPING_COLUMNS, CURATED_DATA_DIR


DEFAULT_PATH = CURATED_DATA_DIR / "author_institution_mappings.csv"


def migrate(path: Path = DEFAULT_PATH) -> int:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    active_counts: dict[str, int] = defaultdict(int)
    historical_counts: dict[str, int] = defaultdict(int)
    changed = 0
    for row in rows:
        paper_key = (
            row.get("paper_id", "").strip()
            or row.get("doi", "").strip().casefold()
            or row.get("openalex_url", "").strip().casefold()
            or "|".join((row.get("title", "").strip().casefold(), row.get("year", "").strip()))
        )
        current = row.get("mapping_status", "").strip() in ACTIVE_MAPPING_STATUSES
        counts = active_counts if current else historical_counts
        counts[paper_key] += 1
        expected = str(counts[paper_key])
        if current and row.get("affiliation_order", "").strip() != expected:
            row["affiliation_order"] = expected
            changed += 1
        elif not row.get("affiliation_order", "").strip():
            row["affiliation_order"] = expected
            changed += 1

    save_mappings(rows, path)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args()
    print(f"Migrated {migrate(args.path)} mapping rows in {args.path}")


if __name__ == "__main__":
    main()
