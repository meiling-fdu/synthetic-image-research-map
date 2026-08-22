#!/usr/bin/env python3
"""Focused local benchmark for institution identity saves and derived admin views."""

from __future__ import annotations

import argparse
import shutil
import statistics
import tempfile
import time
from pathlib import Path

try:
    from .curated_institutions import load_institutions, update_institution_identity
    from .curated_locations import location_review_payload
    from .curated_mappings import load_mappings
    from .serve_admin import institution_registry_payload
except ImportError:
    from curated_institutions import load_institutions, update_institution_identity
    from curated_locations import location_review_payload
    from curated_mappings import load_mappings
    from serve_admin import institution_registry_payload


ROOT = Path(__file__).resolve().parents[1]


def milliseconds(operation) -> float:
    started = time.perf_counter()
    operation()
    return (time.perf_counter() - started) * 1000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=7)
    arguments = parser.parse_args()
    curated = ROOT / "data/curated"
    institutions_path = curated / "institutions.csv"
    institutions = load_institutions(institutions_path)
    representative = next(
        row for row in institutions if row.get("institution_status") == "active"
    )
    identity_times = []
    with tempfile.TemporaryDirectory() as directory:
        for index in range(arguments.samples):
            copy = Path(directory) / f"institutions-{index}.csv"
            shutil.copy2(institutions_path, copy)
            identity_times.append(milliseconds(lambda: update_institution_identity(
                representative["institution_id"], representative,
                institutions_path=copy,
            )))
    mappings = load_mappings(curated / "author_institution_mappings.csv")
    review_time = milliseconds(lambda: location_review_payload(
        review_path=curated / "institution_location_review.csv",
        locations_path=curated / "institution_locations.csv",
        aliases_path=curated / "institution_aliases.csv",
        mappings=mappings,
        institutions_path=institutions_path,
    ))
    registry_arguments = {
        "institutions_path": institutions_path,
        "aliases_path": curated / "institution_aliases.csv",
        "mappings_path": curated / "author_institution_mappings.csv",
        "locations_path": curated / "institution_locations.csv",
        "public_map_path": ROOT / "web/data/public_preview_map_data.json",
    }
    registry_cold = milliseconds(lambda: institution_registry_payload(**registry_arguments))
    registry_cached = milliseconds(lambda: institution_registry_payload(**registry_arguments))
    print({
        "identity_write_ms_median": round(statistics.median(identity_times), 2),
        "review_payload_ms": round(review_time, 2),
        "registry_cold_ms": round(registry_cold, 2),
        "registry_cached_ms": round(registry_cached, 3),
        "samples": arguments.samples,
    })


if __name__ == "__main__":
    main()
