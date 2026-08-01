#!/usr/bin/env python3
"""Migrate curated paper contribution categories to the multi-value schema."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

try:
    from .curated_schema import PAPERS_COLUMNS
    from .paper_categories import serialize_paper_categories
except ImportError:
    from curated_schema import PAPERS_COLUMNS
    from paper_categories import serialize_paper_categories


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = ROOT / "data" / "curated" / "papers.csv"


def migrate(path: Path, *, check: bool = False) -> int:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if "paper_categories" in fields:
        source_field = "paper_categories"
    elif "entry_type" in fields:
        source_field = "entry_type"
        fields[fields.index("entry_type")] = "paper_categories"
    else:
        raise ValueError("papers.csv has neither entry_type nor paper_categories")
    changed = 0
    for number, row in enumerate(rows, 2):
        try:
            normalized = serialize_paper_categories(row.get(source_field))
        except ValueError as error:
            raise ValueError(f"{path}:{number}: {error}") from error
        if source_field != "paper_categories" or row.get(source_field, "") != normalized:
            changed += 1
        row["paper_categories"] = normalized
        row.pop("entry_type", None)
    if tuple(fields) != PAPERS_COLUMNS:
        raise ValueError("migrated header does not match the canonical papers schema")
    if changed and not check:
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = migrate(args.path, check=args.check)
    print(f"{changed} row(s) would change" if args.check else f"{changed} row(s) changed")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
