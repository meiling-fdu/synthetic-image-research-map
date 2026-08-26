#!/usr/bin/env python3
"""Report the local institution location-review queue."""

from __future__ import annotations

import sys

try:
    from .curated_locations import (
        CuratedLocationError,
        location_review_payload,
    )
    from .curated_mappings import load_mappings
    from .paper_exclusions import read_exclusion_rows
except ImportError:
    from curated_locations import (
        CuratedLocationError,
        location_review_payload,
    )
    from curated_mappings import load_mappings
    from paper_exclusions import read_exclusion_rows


def main() -> int:
    try:
        report = location_review_payload(
            mappings=load_mappings(), exclusions=read_exclusion_rows()
        )["summary"]
    except CuratedLocationError as error:
        print(f"Location review report failed: {error}", file=sys.stderr)
        return 1

    print("Institution location review")
    print(f"Total queue rows: {report['total_queue_rows']}")
    print(f"Confirmed: {report['confirmed']}")
    print(f"Pending review: {report['pending_review']}")
    print(f"Aliases: {report['alias_of_confirmed']}")
    print(f"Ignored: {report['ignore']}")
    print(f"Excluded: {report['excluded']}")
    print(f"Ambiguous: {report['ambiguous']}")
    print(f"Needs coordinates: {report['needs_coordinates']}")
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
