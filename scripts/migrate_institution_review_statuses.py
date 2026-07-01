#!/usr/bin/env python3
"""One-time conservative migration of legacy institution review diagnostics."""

from __future__ import annotations

import csv
from pathlib import Path

try:
    from .curated_locations import normalize_institution_name
    from .curated_schema import (
        CURATED_DATA_DIR,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
    )
except ImportError:
    from curated_locations import normalize_institution_name
    from curated_schema import CURATED_DATA_DIR, INSTITUTION_LOCATION_REVIEW_COLUMNS


def migrate(
    review_path: Path = CURATED_DATA_DIR / "institution_location_review.csv",
    locations_path: Path = CURATED_DATA_DIR / "institution_locations.csv",
) -> None:
    with locations_path.open(encoding="utf-8-sig", newline="") as handle:
        confirmed = {
            normalize_institution_name(
                row.get("normalized_institution") or row.get("institution")
            )
            for row in csv.DictReader(handle)
            if row.get("lat") and row.get("lon")
        }
    with review_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if row.get("review_status"):
            continue
        location_status = (row.get("location_status") or "").strip()
        coordinate_status = (row.get("coordinate_status") or "").strip()
        if (row.get("ignored") or "").strip().lower() in {"1", "true", "yes"}:
            status = "ignore"
        elif (row.get("excluded") or "").strip().lower() in {"1", "true", "yes"}:
            status = "excluded"
        elif location_status == "ambiguous" or coordinate_status == "ambiguous":
            status = "ambiguous"
        elif (
            location_status == "known"
            and coordinate_status == "known"
            and normalize_institution_name(row.get("institution")) in confirmed
        ):
            status = "confirmed"
            row["canonical_institution_name"] = row.get("institution", "")
        elif coordinate_status in {"missing", "needs_coordinate_review"}:
            status = "needs_coordinates"
        else:
            status = "pending_review"
        row["review_status"] = status
    temporary = review_path.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=INSTITUTION_LOCATION_REVIEW_COLUMNS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(review_path)


if __name__ == "__main__":
    migrate()
