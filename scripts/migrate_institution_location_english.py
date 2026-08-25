#!/usr/bin/env python3
"""Persist reviewed English forms for canonical institution locations."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .country_normalization import canonical_english_location_fields
    from .curated_schema import CURATED_DATA_DIR, INSTITUTION_LOCATION_COLUMNS
except ImportError:
    from country_normalization import canonical_english_location_fields
    from curated_schema import CURATED_DATA_DIR, INSTITUTION_LOCATION_COLUMNS


DEFAULT_PATH = CURATED_DATA_DIR / "institution_locations.csv"
DEFAULT_AUDIT_PATH = (
    CURATED_DATA_DIR.parent / "processed" / "institution_location_english_audit.csv"
)
AUDIT_COLUMNS = (
    "location_id", "institution_id", "institution", "field",
    "previous_value", "english_value", "status", "evidence_basis",
)


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != tuple(INSTITUTION_LOCATION_COLUMNS):
            raise ValueError(f"{path} has an unexpected header")
        return [dict(row) for row in reader]


def _write(
    path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]
) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def migrate_rows(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    migrated = [dict(row) for row in rows]
    audit: list[dict[str, str]] = []
    for row in migrated:
        normalized = canonical_english_location_fields({
            field: row.get(field, "")
            for field in ("city", "region", "country", "country_code")
        })
        for field in ("city", "region", "country"):
            previous = str(row.get(field, "")).strip()
            current = normalized.get(field, previous)
            if previous == current:
                continue
            audit.append({
                "location_id": str(row.get("location_id", "")).strip(),
                "institution_id": str(row.get("institution_id", "")).strip(),
                "institution": str(row.get("institution", "")).strip(),
                "field": field,
                "previous_value": previous,
                "english_value": current,
                "status": "normalized",
                "evidence_basis": (
                    "canonical country-code registry"
                    if field == "country"
                    else "reviewed English geographic alias table"
                ),
            })
            row[field] = current
        if normalized.get("country_code"):
            row["country_code"] = normalized["country_code"]
    return migrated, audit


def migrate(
    path: Path = DEFAULT_PATH,
    *,
    audit_path: Path = DEFAULT_AUDIT_PATH,
    apply: bool = True,
) -> int:
    migrated, audit = migrate_rows(_read(path))
    if apply:
        _write(path, INSTITUTION_LOCATION_COLUMNS, migrated)
        _write(audit_path, AUDIT_COLUMNS, audit)
    return len(audit)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    count = migrate(args.path, audit_path=args.audit_output, apply=not args.dry_run)
    print(f"Normalized {count} persisted location field values in {args.path}")


if __name__ == "__main__":
    main()
