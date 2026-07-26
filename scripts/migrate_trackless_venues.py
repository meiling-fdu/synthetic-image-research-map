#!/usr/bin/env python3
"""Migrate canonical non-conference venues away from conference track IDs."""

from __future__ import annotations

import csv
from pathlib import Path

from venues import VENUE_ALIAS_COLUMNS


ROOT = Path(__file__).resolve().parent.parent
ALIASES_PATH = ROOT / "data" / "curated" / "venue_aliases.csv"
PAPERS_PATH = ROOT / "data" / "curated" / "papers.csv"
TRACKLESS_TYPES = {"journal", "preprint", "book"}


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> None:
    with ALIASES_PATH.open(encoding="utf-8-sig", newline="") as handle:
        aliases = list(csv.DictReader(handle))
    id_redirects: dict[str, str] = {}
    for row in aliases:
        if row["venue_type"] not in TRACKLESS_TYPES:
            continue
        old_id = row["venue_id"]
        new_id = old_id.removesuffix(":main")
        id_redirects[old_id] = new_id
        row["venue_id"] = new_id
        row["venue_track"] = ""

    additions = [
        {
            "alias": "Computer Vision and Image Understanding",
            "venue_id": "venue:computer-vision-and-image-understanding",
            "venue_name": "Computer Vision and Image Understanding",
            "venue_acronym": "CVIU",
            "venue_type": "journal",
            "venue_track": "",
            "review_status": "confirmed",
            "notes": "Canonical journal identity; journals do not have conference tracks.",
        },
        {
            "alias": "Sensors",
            "venue_id": "venue:sensors",
            "venue_name": "Sensors",
            "venue_acronym": "",
            "venue_type": "journal",
            "venue_track": "",
            "review_status": "confirmed",
            "notes": "Canonical journal identity; journals do not have conference tracks.",
        },
        {
            "alias": "ACM SIGGRAPH Posters",
            "venue_id": "venue:siggraph:posters",
            "venue_name": "ACM SIGGRAPH",
            "venue_acronym": "SIGGRAPH",
            "venue_type": "conference",
            "venue_track": "posters",
            "review_status": "confirmed",
            "notes": "Reviewed SIGGRAPH Posters track.",
        },
        {
            "alias": "Special Interest Group on Computer Graphics and Interactive Techniques Posters",
            "venue_id": "venue:siggraph:posters",
            "venue_name": "ACM SIGGRAPH",
            "venue_acronym": "SIGGRAPH",
            "venue_type": "conference",
            "venue_track": "posters",
            "review_status": "confirmed",
            "notes": "Historical full-name alias for the reviewed SIGGRAPH Posters track.",
        },
    ]
    existing = {(row["alias"], row["venue_id"]) for row in aliases}
    aliases.extend(
        row for row in additions if (row["alias"], row["venue_id"]) not in existing
    )
    canonical_by_id = {}
    for alias in aliases:
        canonical_by_id.setdefault(
            alias["venue_id"],
            {
                "venue": alias["venue_name"],
                "venue_name": alias["venue_name"],
                "venue_acronym": alias["venue_acronym"],
                "venue_type": alias["venue_type"],
                "venue_track": alias["venue_track"],
            },
        )
    write_rows(ALIASES_PATH, list(VENUE_ALIAS_COLUMNS), aliases)

    with PAPERS_PATH.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or ())
        papers = list(reader)
    for row in papers:
        if row["venue_type"] in TRACKLESS_TYPES:
            row["venue_id"] = id_redirects.get(
                row["venue_id"], row["venue_id"].removesuffix(":main")
            )
            row["venue_track"] = ""
        if row["venue_id"] in canonical_by_id:
            row.update(canonical_by_id[row["venue_id"]])
    write_rows(PAPERS_PATH, fieldnames, papers)


if __name__ == "__main__":
    main()
