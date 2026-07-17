#!/usr/bin/env python3
"""Dry-run or apply the canonical four-value institution-type migration."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

try:
    from .curated_institutions import load_institutions, save_institutions
    from .curated_schema import INSTITUTION_ALIAS_COLUMNS, AUTHOR_INSTITUTION_MAPPING_COLUMNS
    from .institution_types import build_migration_rows
except ImportError:
    from curated_institutions import load_institutions, save_institutions
    from curated_schema import INSTITUTION_ALIAS_COLUMNS, AUTHOR_INSTITUTION_MAPPING_COLUMNS
    from institution_types import build_migration_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INSTITUTIONS = ROOT / "data/curated/institutions.csv"
DEFAULT_ALIASES = ROOT / "data/curated/institution_aliases.csv"
DEFAULT_MAPPINGS = ROOT / "data/curated/author_institution_mappings.csv"
DEFAULT_REPORT = ROOT / "data/processed/institution_type_migration_report.csv"
REPORT_COLUMNS = (
    "institution_id", "canonical_name", "aliases_considered", "previous_type",
    "proposed_type", "applied_rule", "evidence", "affected_unique_paper_count",
)


def read_rows(path: Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != columns:
            raise ValueError(f"{path} has an unexpected CSV header")
        return list(reader)


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def migrate(
    institutions_path: Path, aliases_path: Path, mappings_path: Path,
    report_path: Path, apply: bool = False,
) -> dict[str, object]:
    institutions = load_institutions(institutions_path)
    aliases = read_rows(aliases_path, tuple(INSTITUTION_ALIAS_COLUMNS))
    mappings = read_rows(mappings_path, tuple(AUTHOR_INSTITUTION_MAPPING_COLUMNS))
    report = build_migration_rows(institutions, aliases, mappings)
    write_report(report_path, report)
    changes = [row for row in report if row["previous_type"] != row["proposed_type"]]
    if apply and changes:
        proposed = {row["institution_id"]: row["proposed_type"] for row in report}
        for row in institutions:
            row["institution_type"] = proposed[row["institution_id"]]
        save_institutions(institutions, institutions_path)
    return {
        "mode": "apply" if apply else "dry-run",
        "institutions": len(report),
        "changes": len(changes),
        "migrated_from": dict(sorted(Counter(row["previous_type"] for row in changes).items())),
        "final_types": dict(sorted(Counter(row["proposed_type"] for row in report).items())),
        "report": str(report_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--institutions", type=Path, default=DEFAULT_INSTITUTIONS)
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES)
    parser.add_argument("--mappings", type=Path, default=DEFAULT_MAPPINGS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    summary = migrate(args.institutions, args.aliases, args.mappings, args.report, args.apply)
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
