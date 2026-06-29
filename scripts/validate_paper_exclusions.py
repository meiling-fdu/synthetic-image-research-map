#!/usr/bin/env python3
"""Validate durable paper exclusions and preview matching."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, List, Mapping, Sequence

try:
    from .curated_schema import (
        ALLOWED_EXCLUSION_REASONS,
        PAPER_EXCLUSION_COLUMNS,
    )
    from .paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        all_identity_keys,
        clean,
        matching_exclusion_rows,
        parse_boolean,
        read_exclusion_rows,
        read_json_records,
    )
except ImportError:
    from curated_schema import (
        ALLOWED_EXCLUSION_REASONS,
        PAPER_EXCLUSION_COLUMNS,
    )
    from paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        all_identity_keys,
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
BOOLEAN_FIELDS = (
    "excluded_from_public_preview",
    "excluded_from_map",
    "is_active",
)
BOOLEAN_LIKE = {"1", "0", "true", "false", "yes", "no", "y", "n"}


def duplicate_active_groups(
    rows: Sequence[Mapping[str, str]],
) -> List[tuple[str, List[int]]]:
    positions: DefaultDict[str, List[int]] = defaultdict(list)
    for row_number, row in enumerate(rows, start=2):
        if not parse_boolean(row.get("is_active")):
            continue
        for key in all_identity_keys(row):
            positions[key].append(row_number)
    return [
        (key, row_numbers)
        for key, row_numbers in positions.items()
        if len(set(row_numbers)) > 1
    ]


def main() -> int:
    errors: List[str] = []
    warnings: List[str] = []
    try:
        rows = read_exclusion_rows(DEFAULT_EXCLUSIONS_PATH)
        preview_records = [
            record
            for path in PREVIEW_PATHS
            for record in read_json_records(path)
        ]
    except PaperExclusionError as error:
        print(f"ERROR: {error}")
        return 1

    for row_number, row in enumerate(rows, start=2):
        reason = clean(row.get("reason"))
        if not reason:
            errors.append(f"row {row_number}: exclusion reason is required")
        elif reason not in ALLOWED_EXCLUSION_REASONS:
            errors.append(
                f"row {row_number}: unsupported exclusion reason {reason!r}"
            )
        for field in BOOLEAN_FIELDS:
            value = clean(row.get(field))
            if not value:
                errors.append(f"row {row_number}: {field} is required")
            elif value.casefold() not in BOOLEAN_LIKE:
                errors.append(
                    f"row {row_number}: {field} is not boolean-like: {value!r}"
                )
        if not all_identity_keys(row):
            errors.append(
                f"row {row_number}: DOI, OpenAlex URL, or title + year is required"
            )

    duplicates = duplicate_active_groups(rows)
    for key, row_numbers in duplicates:
        errors.append(
            f"duplicate active exclusion {key!r} on rows "
            + ", ".join(map(str, sorted(set(row_numbers))))
        )

    matched = 0
    unmatched = 0
    for row_number, row in enumerate(rows, start=2):
        if matching_exclusion_rows(row, preview_records):
            matched += 1
        else:
            unmatched += 1
            warnings.append(
                f"row {row_number}: exclusion is not currently present in public preview"
            )

    print("Paper exclusion validation")
    print(f"Header columns: {len(PAPER_EXCLUSION_COLUMNS)}")
    print(f"Rows: {len(rows)}")
    print(f"Active exclusions: {sum(parse_boolean(row.get('is_active')) for row in rows)}")
    print(f"Matched against current preview: {matched}")
    print(f"Not currently present: {unmatched}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
