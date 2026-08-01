#!/usr/bin/env python3
"""Durably migrate paper curation_status values to the two-state model."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

try:
    from .curated_papers import DEFAULT_CURATED_PAPERS_PATH, write_curated_papers
    from .curated_schema import PAPERS_COLUMNS, normalize_curation_status
except ImportError:
    from curated_papers import DEFAULT_CURATED_PAPERS_PATH, write_curated_papers
    from curated_schema import PAPERS_COLUMNS, normalize_curation_status


def migrate(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != PAPERS_COLUMNS:
            raise ValueError(f"{path} does not have the exact curated paper header")
        rows = [dict(row) for row in reader]
    changed = 0
    for row_number, row in enumerate(rows, start=2):
        try:
            normalized = normalize_curation_status(row.get("curation_status"))
        except ValueError as error:
            raise ValueError(f"{path}:{row_number}: {error}") from error
        if row.get("curation_status") != normalized:
            row["curation_status"] = normalized
            changed += 1
    if changed:
        write_curated_papers(rows, path)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papers", type=Path, default=DEFAULT_CURATED_PAPERS_PATH)
    args = parser.parse_args()
    try:
        changed = migrate(args.papers)
    except (OSError, csv.Error, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Migrated {changed} paper curation_status value(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
