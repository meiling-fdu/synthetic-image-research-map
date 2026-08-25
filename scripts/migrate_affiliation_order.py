#!/usr/bin/env python3
"""Add deterministic affiliation order values without changing row sequence."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .curated_mappings import (
        ACTIVE_MAPPING_STATUSES,
        paper_identity_keys,
        save_mappings,
    )
    from .curated_schema import AUTHOR_INSTITUTION_MAPPING_COLUMNS, CURATED_DATA_DIR
except ImportError:
    from curated_mappings import (
        ACTIVE_MAPPING_STATUSES,
        paper_identity_keys,
        save_mappings,
    )
    from curated_schema import AUTHOR_INSTITUTION_MAPPING_COLUMNS, CURATED_DATA_DIR


DEFAULT_PATH = CURATED_DATA_DIR / "author_institution_mappings.csv"


def _active_components(
    rows: Sequence[Mapping[str, Any]],
) -> list[list[int]]:
    """Group active rows by any shared durable paper identity, transitively."""
    parent = list(range(len(rows)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    owner_by_key: dict[str, int] = {}
    active_indices: list[int] = []
    for index, row in enumerate(rows):
        if str(row.get("mapping_status", "")).strip() not in ACTIVE_MAPPING_STATUSES:
            continue
        active_indices.append(index)
        for key in paper_identity_keys(row):
            owner = owner_by_key.setdefault(key, index)
            union(index, owner)

    grouped: dict[int, list[int]] = defaultdict(list)
    for index in active_indices:
        grouped[find(index)].append(index)
    return list(grouped.values())


def affiliation_order_issues(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Describe every active paper component that violates persisted 1..N order."""
    issues: list[dict[str, Any]] = []
    for indices in _active_components(rows):
        raw = [str(rows[index].get("affiliation_order", "")).strip() for index in indices]
        parsed = [int(value) if value.isdigit() else None for value in raw]
        expected = list(range(1, len(indices) + 1))
        reasons: list[str] = []
        if any(not value for value in raw):
            reasons.append("missing")
        if any(value and not value.isdigit() for value in raw):
            reasons.append("non_integer")
        if any(value is not None and value < 1 for value in parsed):
            reasons.append("non_positive")
        positive = [value for value in parsed if value is not None and value > 0]
        if len(set(positive)) != len(positive):
            reasons.append("duplicate")
        if sorted(positive) != expected:
            reasons.append("gapped_or_non_contiguous")
        if reasons:
            representative = rows[indices[0]]
            issues.append({
                "paper_id": str(representative.get("paper_id", "")).strip(),
                "title": str(representative.get("title", "")).strip(),
                "mapping_ids": [
                    str(rows[index].get("mapping_id", "")).strip()
                    for index in indices
                ],
                "orders": raw,
                "reasons": reasons,
                "row_indices": indices,
            })
    return issues


def migrate(path: Path = DEFAULT_PATH) -> int:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    changed = 0
    for issue in affiliation_order_issues(rows):
        # Stable CSV record order is the deterministic fallback when persisted
        # values are ambiguous, duplicated, missing, or otherwise unusable.
        for order, index in enumerate(issue["row_indices"], start=1):
            expected = str(order)
            if rows[index].get("affiliation_order", "").strip() != expected:
                rows[index]["affiliation_order"] = expected
                changed += 1

    save_mappings(rows, path)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args()
    print(f"Migrated {migrate(args.path)} mapping rows in {args.path}")


if __name__ == "__main__":
    main()
