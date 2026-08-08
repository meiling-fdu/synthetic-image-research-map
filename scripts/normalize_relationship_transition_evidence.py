#!/usr/bin/env python3
"""Idempotently materialize exact relationship-transition evidence columns."""

from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        INSTITUTION_AUDIT_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
    )
except ImportError:
    from curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        INSTITUTION_AUDIT_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
    )

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = ROOT / "data/curated/author_institution_mappings.csv"
AUDITS = ROOT / "data/curated/institution_audit_log.csv"
LOCATIONS = ROOT / "data/curated/institution_locations.csv"
TRANSITION_ACTIONS = {
    "confirmed_mapping_changed",
    "mapping_replaced",
    "mapping_change_confirmed",
    "mapping_removed",
}


def clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_if_changed(
    path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]
) -> bool:
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            {column: clean(row.get(column)) for column in columns} for row in rows
        )
    try:
        if path.exists() and path.read_bytes() == temporary.read_bytes():
            temporary.unlink()
            return False
        os.replace(temporary, path)
        return True
    finally:
        temporary.unlink(missing_ok=True)


def confirmation_fields(row: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for part in clean(row.get("confirmation_text")).split(";"):
        key, separator, value = part.partition("=")
        if separator and clean(key):
            result[clean(key).casefold()] = clean(value)
    return result


def assign_multilocation_ids(
    mappings: list[dict[str, str]], locations: Sequence[Mapping[str, str]]
) -> int:
    by_institution: dict[str, list[Mapping[str, str]]] = {}
    for location in locations:
        by_institution.setdefault(clean(location.get("institution_id")), []).append(
            location
        )
    changed = 0
    for mapping in mappings:
        candidates = by_institution.get(clean(mapping.get("institution_id")), [])
        if len(candidates) < 2:
            continue
        selected_id = clean(mapping.get("location_id"))
        if selected_id:
            selected = next(
                (row for row in candidates if clean(row.get("location_id")) == selected_id),
                None,
            )
            if selected is not None:
                row_changed = False
                for mapping_field, location_field in (
                    ("institution_city", "city"),
                    ("institution_country", "country"),
                ):
                    if not clean(mapping.get(mapping_field)):
                        mapping[mapping_field] = clean(selected.get(location_field))
                        row_changed = True
                changed += int(row_changed)
            continue
        city = clean(mapping.get("institution_city")).casefold()
        country = clean(mapping.get("institution_country")).casefold()
        evidence = clean(mapping.get("raw_affiliation")).casefold()
        matches = [
            location for location in candidates
            if (
                city and clean(location.get("city")).casefold() == city
                and (
                    not country
                    or clean(location.get("country")).casefold() == country
                )
            )
            or (
                clean(location.get("city"))
                and clean(location.get("city")).casefold() in evidence
            )
        ]
        unique_ids = {clean(row.get("location_id")) for row in matches}
        if len(unique_ids) == 1:
            selected_id = unique_ids.pop()
            selected = next(
                row for row in candidates
                if clean(row.get("location_id")) == selected_id
            )
            mapping["location_id"] = selected_id
            mapping["institution_city"] = clean(selected.get("city"))
            mapping["institution_country"] = clean(selected.get("country"))
            changed += 1
    return changed


def normalize_audits(
    audits: list[dict[str, str]], mappings: Sequence[Mapping[str, str]]
) -> int:
    mapping_by_id = {
        clean(row.get("mapping_id")): row
        for row in mappings if clean(row.get("mapping_id"))
    }
    changed = 0
    for audit in audits:
        action = clean(audit.get("action"))
        if action not in TRANSITION_ACTIONS:
            continue
        before = {column: clean(audit.get(column)) for column in INSTITUTION_AUDIT_COLUMNS}
        fields = confirmation_fields(audit)
        mapping_id = clean(audit.get("mapping_id")) or fields.get("mapping_id", "")
        mapping = mapping_by_id.get(mapping_id, {})
        authors = clean(mapping.get("institution_authors")) or clean(
            audit.get("affected_authors")
        )
        audit.update({
            "paper_id": clean(audit.get("paper_id"))
            or fields.get("paper_id", "") or clean(mapping.get("paper_id")),
            "previous_mapping_id": clean(audit.get("previous_mapping_id"))
            or mapping_id,
            "mapping_id": mapping_id,
            "previous_location_id": clean(audit.get("previous_location_id")),
            "location_id": "" if action == "mapping_removed" else (
                clean(audit.get("location_id"))
                or clean(mapping.get("location_id"))
            ),
            "previous_authors": clean(audit.get("previous_authors")) or authors,
            "new_authors": "" if action == "mapping_removed" else (
                clean(audit.get("new_authors")) or authors
            ),
            "evidence_source": clean(audit.get("evidence_source"))
            or fields.get("evidence_source", "") or fields.get("source", "")
            or fields.get("change_source", ""),
            "evidence_url": clean(audit.get("evidence_url"))
            or fields.get("evidence_url", ""),
        })
        after = {column: clean(audit.get(column)) for column in INSTITUTION_AUDIT_COLUMNS}
        changed += int(before != after)
    return changed


def main() -> int:
    mappings = read_rows(MAPPINGS)
    locations = read_rows(LOCATIONS)
    audits = read_rows(AUDITS)
    mapping_locations = assign_multilocation_ids(mappings, locations)
    audit_rows = normalize_audits(audits, mappings)
    mappings_written = write_if_changed(
        MAPPINGS, AUTHOR_INSTITUTION_MAPPING_COLUMNS, mappings
    )
    audits_written = write_if_changed(AUDITS, INSTITUTION_AUDIT_COLUMNS, audits)
    print(
        "Relationship evidence normalization: "
        f"mapping_locations={mapping_locations}, audit_rows={audit_rows}, "
        f"files_written={int(mappings_written) + int(audits_written)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
