#!/usr/bin/env python3
"""Idempotent migrations for obsolete curated institution-location fields."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .curated_schema import (
        CURATED_DATA_DIR, INSTITUTION_LOCATION_AUDIT_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS, INSTITUTION_LOCATION_REVIEW_COLUMNS,
    )
except ImportError:
    from curated_schema import (
        CURATED_DATA_DIR, INSTITUTION_LOCATION_AUDIT_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS, INSTITUTION_LOCATION_REVIEW_COLUMNS,
    )


LEGACY_LOCATION_FIELDS = frozenset({
    "coordinate_source", "coordinate_source_url", "review_note"
})
LEGACY_REVIEW_STATUS = {
    "needs_coordinates": "pending_review",
    "alias_candidate": "pending_review",
}


def _read(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return tuple(reader.fieldnames or ()), [dict(row) for row in reader]


def _write(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".migration.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def migrate_obsolete_location_schema(
    curated_dir: Path = CURATED_DATA_DIR,
) -> dict[str, int]:
    """Drop obsolete provenance columns and collapse transitional statuses."""
    specifications = (
        ("institution_locations.csv", INSTITUTION_LOCATION_COLUMNS),
        ("institution_location_review.csv", INSTITUTION_LOCATION_REVIEW_COLUMNS),
        ("institution_location_audit_log.csv", INSTITUTION_LOCATION_AUDIT_COLUMNS),
    )
    proposed: list[tuple[Path, Sequence[str], list[dict[str, str]]]] = []
    result = {"files_migrated": 0, "records_migrated": 0, "statuses_migrated": 0}
    for filename, columns in specifications:
        path = curated_dir / filename
        if not path.exists():
            continue
        header, rows = _read(path)
        unknown = set(header) - set(columns) - LEGACY_LOCATION_FIELDS
        missing = set(columns) - set(header)
        if unknown or missing:
            raise ValueError(
                f"{path} cannot be migrated safely; unknown={sorted(unknown)}, missing={sorted(missing)}"
            )
        changed = header != tuple(columns)
        for row in rows:
            replacement = LEGACY_REVIEW_STATUS.get(row.get("review_status", ""))
            if replacement:
                row["review_status"] = replacement
                result["statuses_migrated"] += 1
                changed = True
        if changed:
            proposed.append((path, columns, rows))
            result["files_migrated"] += 1
            result["records_migrated"] += len(rows)
    snapshots = {path: path.read_bytes() for path, _columns, _rows in proposed}
    try:
        for path, columns, rows in proposed:
            _write(path, columns, rows)
    except Exception:
        for path, content in snapshots.items():
            path.write_bytes(content)
        raise
    return result


if __name__ == "__main__":
    print(migrate_obsolete_location_schema())
