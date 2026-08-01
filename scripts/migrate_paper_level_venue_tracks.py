#!/usr/bin/env python3
"""Consolidate track-specific venue IDs without changing paper track metadata."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from curated_schema import PAPERS_COLUMNS
from venues import DEFAULT_VENUE_ALIASES_PATH, VENUE_ALIAS_COLUMNS, alias_key, clean_text


ROOT = Path(__file__).resolve().parent.parent
PAPERS_PATH = ROOT / "data" / "curated" / "papers.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def plan(alias_rows: list[dict[str, str]]) -> tuple[dict[str, str], list[dict[str, object]]]:
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in alias_rows:
        if clean_text(row.get("review_status")) != "confirmed":
            continue
        key = (
            alias_key(row.get("venue_name")),
            alias_key(row.get("venue_acronym")),
            clean_text(row.get("venue_type")),
        )
        groups[key].append(row)
    replacements: dict[str, str] = {}
    audit: list[dict[str, object]] = []
    for key, rows in sorted(groups.items()):
        ids = sorted({clean_text(row.get("venue_id")) for row in rows})
        if not ids:
            continue
        main = next((identifier for identifier in ids if identifier.endswith(":main")), ids[0])
        target = main[:-5] if main.endswith(":main") else main
        for identifier in ids:
            replacements[identifier] = target
        if ids != [target]:
            audit.append({
                "venue_name": rows[0]["venue_name"],
                "source_ids": ids,
                "target_id": target,
                "tracks": sorted({row["venue_track"] for row in rows if row["venue_track"]}),
                "status": "exact_identity_consolidation",
            })
    return replacements, audit


def write_rows(path: Path, columns: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    aliases = read_rows(DEFAULT_VENUE_ALIASES_PATH)
    papers = read_rows(PAPERS_PATH)
    replacements, audit = plan(aliases)
    changed_aliases = 0
    changed_papers = 0
    for row in aliases:
        target = replacements.get(row["venue_id"], row["venue_id"])
        changed_aliases += target != row["venue_id"]
        row["venue_id"] = target
    for row in papers:
        target = replacements.get(row["venue_id"], row["venue_id"])
        changed_papers += target != row["venue_id"]
        row["venue_id"] = target
    result = {
        "changed_alias_rows": changed_aliases,
        "changed_papers": changed_papers,
        "consolidations": audit,
        "ambiguous_cases": [],
    }
    if args.write:
        write_rows(DEFAULT_VENUE_ALIASES_PATH, VENUE_ALIAS_COLUMNS, aliases)
        write_rows(PAPERS_PATH, PAPERS_COLUMNS, papers)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
