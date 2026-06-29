#!/usr/bin/env python3
"""Report the local institution location-review queue."""

from __future__ import annotations

import sys

try:
    from .curated_locations import (
        CuratedLocationError,
        load_confirmed_locations,
        load_location_review_queue,
        location_review_report,
    )
except ImportError:
    from curated_locations import (
        CuratedLocationError,
        load_confirmed_locations,
        load_location_review_queue,
        location_review_report,
    )


def main() -> int:
    try:
        report = location_review_report(
            load_location_review_queue(), load_confirmed_locations()
        )
    except CuratedLocationError as error:
        print(f"Location review report failed: {error}", file=sys.stderr)
        return 1

    print("Institution location review")
    print(f"Total queue rows: {report['total_queue_rows']}")
    print(f"Known: {report['known']}")
    print(f"Missing: {report['missing']}")
    print(f"Ambiguous: {report['ambiguous']}")
    print(
        "Needs coordinate review: "
        f"{report['needs_coordinate_review']}"
    )
    print(
        "Confirmed locations: "
        f"{report['confirmed_locations_count']}"
    )
    print(
        "Institutions with multiple location candidates: "
        f"{report['multiple_location_candidate_count']}"
    )
    for institution in report["institutions_with_multiple_location_candidates"]:
        print(f"  {institution}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
