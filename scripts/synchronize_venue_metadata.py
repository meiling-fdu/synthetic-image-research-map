#!/usr/bin/env python3
"""Audit and synchronize paper metadata for confirmed, existing venue IDs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

try:
    from .curated_papers import DEFAULT_CURATED_PAPERS_PATH
    from .curated_schema import PAPERS_COLUMNS
    from .venues import (
        DEFAULT_VENUE_ALIASES_PATH,
        VenueRegistryError,
        canonical_venue_registry,
        clean_text,
        materialize_existing_venue_id,
        read_venue_aliases,
    )
except ImportError:
    from curated_papers import DEFAULT_CURATED_PAPERS_PATH
    from curated_schema import PAPERS_COLUMNS
    from venues import (
        DEFAULT_VENUE_ALIASES_PATH,
        VenueRegistryError,
        canonical_venue_registry,
        clean_text,
        materialize_existing_venue_id,
        read_venue_aliases,
    )


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT_PATH = ROOT / "data" / "processed" / "venue_metadata_sync_audit.json"
SYNC_FIELDS = (
    "venue",
    "venue_name",
    "venue_acronym",
    "venue_type",
    "venue_track",
)


def read_papers(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != PAPERS_COLUMNS:
            raise ValueError(f"{path} does not have the exact papers header")
        return [dict(row) for row in reader]


def audit_and_synchronize(
    papers: list[dict[str, str]],
    alias_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Return synchronized copies and a stable grouped audit report."""
    registry = canonical_venue_registry(alias_rows)
    synchronized: list[dict[str, str]] = []
    groups: dict[str, dict[str, Any]] = {}
    dangling: list[dict[str, str]] = []
    legacy_ids_removed = 0
    canonical_ids_replaced = 0
    changed_records = 0

    for paper in papers:
        row = dict(paper)
        venue_id = clean_text(row.get("venue_id"))
        if not venue_id:
            synchronized.append(row)
            continue
        try:
            materialized = materialize_existing_venue_id(
                row, alias_rows, registry=registry
            )
        except VenueRegistryError:
            dangling.append({
                "paper_id": clean_text(row.get("paper_id")),
                "title": clean_text(row.get("title")),
                "venue_id": venue_id,
            })
            synchronized.append(row)
            continue
        materialized_id = clean_text(materialized.get("venue_id"))
        if not materialized_id:
            legacy_ids_removed += 1
            changed_records += 1
            for field in SYNC_FIELDS:
                row[field] = clean_text(materialized.get(field))
            row["venue_id"] = ""
            synchronized.append(row)
            continue
        if materialized_id != venue_id:
            canonical_ids_replaced += 1
            row["venue_id"] = materialized_id
        venue_id = materialized_id
        differences = [
            field for field in SYNC_FIELDS
            if clean_text(row.get(field)) != clean_text(materialized.get(field))
        ]
        group = groups.setdefault(venue_id, {
            "venue_id": venue_id,
            "canonical": {
                field: clean_text(materialized.get(field))
                for field in ("venue_name", "venue_acronym", "venue_type")
            },
            "paper_count": 0,
            "inconsistent_paper_count": 0,
            "fields_that_differ": set(),
            "affected_papers": [],
        })
        group["paper_count"] += 1
        if differences:
            changed_records += 1
            group["inconsistent_paper_count"] += 1
            group["fields_that_differ"].update(differences)
            group["affected_papers"].append({
                "paper_id": clean_text(row.get("paper_id")),
                "title": clean_text(row.get("title")),
                "fields": differences,
            })
            for field in SYNC_FIELDS:
                row[field] = clean_text(materialized.get(field))
        synchronized.append(row)

    group_rows = []
    for venue_id in sorted(groups):
        group = groups[venue_id]
        group["fields_that_differ"] = sorted(group["fields_that_differ"])
        group["affected_papers"] = sorted(
            group["affected_papers"], key=lambda item: (item["paper_id"], item["title"])
        )
        group_rows.append(group)
    report = {
        "canonical_registry_conflicts": [],
        "confirmed_venue_count": len(registry),
        "paper_count": len(papers),
        "papers_with_confirmed_venue_id": sum(row["paper_count"] for row in group_rows),
        "inconsistent_records": changed_records,
        "repaired_records": changed_records,
        "legacy_placeholder_ids_removed": legacy_ids_removed,
        "canonical_ids_replaced": canonical_ids_replaced,
        "dangling_records_not_modified": len(dangling),
        "dangling_records": sorted(
            dangling, key=lambda item: (item["venue_id"], item["paper_id"], item["title"])
        ),
        "venues": group_rows,
    }
    return synchronized, report


def write_papers(path: Path, papers: list[dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPERS_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(papers)
    temporary.replace(path)


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papers", type=Path, default=DEFAULT_CURATED_PAPERS_PATH)
    parser.add_argument("--venues", type=Path, default=DEFAULT_VENUE_ALIASES_PATH)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        aliases = read_venue_aliases(args.venues)
        papers = read_papers(args.papers)
        synchronized, report = audit_and_synchronize(papers, aliases)
    except (OSError, ValueError, VenueRegistryError) as error:
        print(f"ERROR: {error}")
        return 1
    if report["dangling_records_not_modified"]:
        for row in report["dangling_records"]:
            print(
                "ERROR: dangling venue_id "
                f"{row['venue_id']!r} for {row['title']!r}"
            )
        return 1
    if args.write:
        write_papers(args.papers, synchronized)
    if args.report:
        write_report(args.report, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
