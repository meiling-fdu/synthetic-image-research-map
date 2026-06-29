#!/usr/bin/env python3
"""Summarize durable paper exclusions and current preview presence."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

try:
    from .paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        clean,
        matching_exclusion_rows,
        parse_boolean,
        read_exclusion_rows,
        read_json_records,
    )
except ImportError:
    from paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        clean,
        matching_exclusion_rows,
        parse_boolean,
        read_exclusion_rows,
        read_json_records,
    )


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
PREVIEW_PATHS = (
    REPOSITORY_ROOT / "web" / "data" / "public_preview_papers.json",
    REPOSITORY_ROOT / "web" / "data" / "public_preview_map_data.json",
)


def main() -> int:
    try:
        rows = read_exclusion_rows(DEFAULT_EXCLUSIONS_PATH)
        preview_records = [
            record
            for path in PREVIEW_PATHS
            for record in read_json_records(path)
        ]
    except PaperExclusionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    active = [row for row in rows if parse_boolean(row.get("is_active"))]
    inactive = [row for row in rows if not parse_boolean(row.get("is_active"))]
    matched = [
        row for row in rows if matching_exclusion_rows(row, preview_records)
    ]
    unmatched = [
        row for row in rows if not matching_exclusion_rows(row, preview_records)
    ]

    print("Excluded papers report")
    print(f"Total exclusions: {len(rows)}")
    print(f"Active exclusions: {len(active)}")
    print(f"Inactive/restored exclusions: {len(inactive)}")
    print(f"Matched against current preview: {len(matched)}")
    print(f"Not currently present: {len(unmatched)}")
    print("Exclusions by reason:")
    reasons = Counter(clean(row.get("reason")) or "(blank)" for row in rows)
    if reasons:
        for reason, count in sorted(reasons.items()):
            print(f"  {reason}: {count}")
    else:
        print("  (none)")
    if unmatched:
        print("Not currently present:")
        for row in unmatched:
            print(
                "  "
                + (clean(row.get("title")) or "<untitled>")
                + (f" ({clean(row.get('year'))})" if clean(row.get("year")) else "")
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
