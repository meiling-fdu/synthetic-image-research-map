#!/usr/bin/env python3
"""Audit curated paper venue references against the canonical registry."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from venues import (
    DEFAULT_VENUE_ALIASES_PATH,
    VenueRegistryError,
    alias_key,
    canonical_venue_by_id,
    clean_text,
    read_venue_aliases,
    resolve_venue,
)


ROOT = Path(__file__).resolve().parent.parent
PAPERS_PATH = ROOT / "data" / "curated" / "papers.csv"
REPORT_PATH = ROOT / "docs" / "venue_registry_audit.csv"
REPORT_COLUMNS = (
    "category",
    "paper_id",
    "title",
    "venue_id",
    "venue_name",
    "venue_type",
    "venue_track",
    "resolved_venue_id",
    "note",
)


def audit() -> list[dict[str, str]]:
    aliases = read_venue_aliases(DEFAULT_VENUE_ALIASES_PATH)
    with PAPERS_PATH.open(encoding="utf-8-sig", newline="") as handle:
        papers = list(csv.DictReader(handle))
    report: list[dict[str, str]] = []
    for paper in papers:
        venue_id = clean_text(paper.get("venue_id"))
        name = clean_text(paper.get("venue_name") or paper.get("venue"))
        category = "no_action_required"
        resolved_id = ""
        note = ""
        if venue_id:
            try:
                canonical = canonical_venue_by_id(venue_id, aliases)
            except VenueRegistryError:
                resolved = resolve_venue(
                    paper.get("raw_venue") or name,
                    publication_type=paper.get("publication_type"),
                    venue_type=paper.get("venue_type"),
                    aliases=aliases,
                )
                resolved_id = resolved.venue_id
                category = (
                    "resolved_to_existing"
                    if resolved.ambiguity_status == "resolved"
                    else "ambiguous_match"
                    if resolved.ambiguity_status == "ambiguous"
                    else "dangling_venue_id"
                )
                note = "paper venue_id is absent from the canonical registry"
            else:
                resolved_id = canonical["venue_id"]
                if name and alias_key(name) != alias_key(canonical["venue_name"]):
                    category = "dangling_venue_id"
                    note = "visible venue name disagrees with canonical venue_id"
                if (
                    canonical["venue_type"] != "conference"
                    and clean_text(paper.get("venue_track"))
                ):
                    category = "invalid_type_track_combination"
                    note = "trackless venue type carries a conference track"
        elif name:
            resolved = resolve_venue(
                paper.get("raw_venue") or name,
                publication_type=paper.get("publication_type"),
                venue_type=paper.get("venue_type"),
                aliases=aliases,
            )
            resolved_id = resolved.venue_id
            category = (
                "resolved_to_existing"
                if resolved.ambiguity_status == "resolved"
                else "ambiguous_match"
                if resolved.ambiguity_status == "ambiguous"
                else "dangling_venue_id"
            )
            note = "venue name has no stored canonical venue_id"
        report.append({
            "category": category,
            "paper_id": clean_text(paper.get("paper_id")),
            "title": clean_text(paper.get("title")),
            "venue_id": venue_id,
            "venue_name": name,
            "venue_type": clean_text(paper.get("venue_type")),
            "venue_track": clean_text(paper.get("venue_track")),
            "resolved_venue_id": resolved_id,
            "note": note,
        })
    return report


def main() -> int:
    report = audit()
    with REPORT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(report)
    counts = Counter(row["category"] for row in report)
    print(" | ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
