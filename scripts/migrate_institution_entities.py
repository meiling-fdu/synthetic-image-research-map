#!/usr/bin/env python3
"""One-time migration from name-linked institution CSVs to stable IDs."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from curated_institutions import alias_id_for, normalize_institution, stable_institution_id
from curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_AUDIT_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"


def read_csv(name: str) -> list[dict[str, str]]:
    with (CURATED / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, columns, rows) -> None:
    path = CURATED / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def infer_type(name: str) -> str:
    normalized = normalize_institution(name)
    if any(word in normalized.split() for word in ("amazon", "adobe", "alibaba", "apple", "google", "huawei", "intel", "meta", "microsoft", "nvidia", "sony", "tencent")):
        return "company"
    if "department" in normalized:
        return "department"
    if "laboratory" in normalized or normalized.endswith(" lab"):
        return "laboratory"
    if "institute" in normalized or "academy" in normalized or "centre" in normalized or "center" in normalized:
        return "institute"
    if "university" in normalized or "college" in normalized:
        return "university"
    return "research_unit"


def main() -> int:
    if (CURATED / "institutions.csv").exists() or (CURATED / "institution_audit_log.csv").exists():
        print("Institution entities already exist; migration did not overwrite curated state.")
        return 0
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    mappings = read_csv("author_institution_mappings.csv")
    locations = read_csv("institution_locations.csv")
    reviews = read_csv("institution_location_review.csv")
    aliases = read_csv("institution_aliases.csv")
    hierarchy = read_csv("institution_hierarchy.csv")

    # Repair the documented corruption conservatively from the preserved evidence.
    aliases = [
        row for row in aliases
        if not (
            normalize_institution(row.get("alias_name"))
            == normalize_institution("Centre for Research and Technology Hellas (CERTH)")
            and normalize_institution(row.get("canonical_institution_name"))
            == normalize_institution("Amazon")
        )
    ]
    for row in reviews:
        if (
            row.get("title") == "AI-Generated Image Detection: Challenges and Recent Advances"
            and "Centre for Research and Technology Hellas" in row.get("raw_affiliation", "")
        ):
            row["canonical_institution_name"] = "Centre for Research and Technology Hellas (CERTH)"
            row["matched_institution"] = ""
            row["review_status"] = "needs_coordinates"
            row["location_status"] = "missing"
            row["coordinate_status"] = "missing"
            row["review_note"] = "Restored from raw affiliation evidence after an unrelated Amazon location edit corrupted the canonical link."
            row["updated_at"] = now

    canonical_names: dict[str, str] = {}
    for row in locations:
        name = row.get("institution", "").strip()
        if name:
            canonical_names.setdefault(normalize_institution(name), name)
    for row in mappings:
        name = row.get("institution", "").strip()
        if name:
            canonical_names.setdefault(normalize_institution(name), name)
    for row in aliases:
        name = row.get("canonical_institution_name", "").strip()
        if name:
            canonical_names.setdefault(normalize_institution(name), name)
    for row in reviews:
        name = (row.get("canonical_institution_name") or row.get("institution") or "").strip()
        if name:
            canonical_names.setdefault(normalize_institution(name), name)

    # Required reviewed alias; it resolves to the existing CERTH entity.
    iti_alias = "Information Technologies Institute"
    certh = "Centre for Research and Technology Hellas (CERTH)"
    if not any(normalize_institution(row.get("alias_name")) == normalize_institution(iti_alias) for row in aliases):
        aliases.append({
            "alias_name": iti_alias,
            "canonical_institution_name": certh,
            "alias_language": "",
            "alias_source": "documented-parent-unit-review",
            "review_status": "confirmed",
            "notes": "Affiliation evidence uses Information Technologies Institute as the CERTH unit; public canonical mapping remains CERTH.",
        })

    parents = {row["child_institution_id"]: row["parent_institution_id"] for row in hierarchy if row.get("review_status") == "confirmed"}
    institutions = []
    for name in sorted(canonical_names.values(), key=str.casefold):
        institution_id = stable_institution_id(name)
        institutions.append({
            "institution_id": institution_id,
            "canonical_name": name,
            "institution_type": infer_type(name),
            "institution_status": "active",
            "parent_institution_id": parents.get(institution_id, ""),
            "public_display": "self",
            "created_at": now,
            "updated_at": now,
            "created_by": "institution-model-migration",
        })

    id_by_name = {normalize_institution(row["canonical_name"]): row["institution_id"] for row in institutions}
    for row in mappings:
        row["institution_id"] = id_by_name.get(normalize_institution(row.get("institution")), stable_institution_id(row.get("institution")))
    for row in locations:
        row["institution_id"] = id_by_name.get(normalize_institution(row.get("institution")), stable_institution_id(row.get("institution")))
    for row in reviews:
        canonical = row.get("canonical_institution_name") or row.get("institution")
        row["institution_id"] = id_by_name.get(normalize_institution(canonical), stable_institution_id(canonical))
    for row in aliases:
        canonical = row.get("canonical_institution_name", "")
        row["alias_id"] = alias_id_for(row.get("alias_name"))
        row["institution_id"] = id_by_name.get(normalize_institution(canonical), stable_institution_id(canonical))

    write_csv("institutions.csv", INSTITUTION_COLUMNS, institutions)
    write_csv("institution_audit_log.csv", INSTITUTION_AUDIT_COLUMNS, [])
    write_csv("author_institution_mappings.csv", AUTHOR_INSTITUTION_MAPPING_COLUMNS, mappings)
    write_csv("institution_locations.csv", INSTITUTION_LOCATION_COLUMNS, locations)
    write_csv("institution_location_review.csv", INSTITUTION_LOCATION_REVIEW_COLUMNS, reviews)
    write_csv("institution_aliases.csv", INSTITUTION_ALIAS_COLUMNS, aliases)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
