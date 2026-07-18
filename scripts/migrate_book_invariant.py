#!/usr/bin/env python3
"""Audit and optionally clear incompatible metadata from curated book rows."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .curated_papers import (
        DEFAULT_CURATED_PAPERS_PATH,
        read_curated_papers,
        write_curated_papers,
    )
    from .publication_types import book_incompatibilities, normalize_book_record
except ImportError:
    from curated_papers import (
        DEFAULT_CURATED_PAPERS_PATH,
        read_curated_papers,
        write_curated_papers,
    )
    from publication_types import book_incompatibilities, normalize_book_record


DEFAULT_REPORT_PATH = Path("data/processed/book_invariant_audit.csv")
REPORT_COLUMNS = (
    "paper_id",
    "title",
    "current_venue",
    "current_paper_type_category",
    "current_track",
    "incompatible_values",
    "action_taken",
    "evidence_rationale",
)


def audit_rows(rows: Sequence[Mapping[str, Any]], *, apply: bool = False):
    migrated = []
    report = []
    for source in rows:
        incompatible = book_incompatibilities(source)
        normalized = normalize_book_record(source) if apply else dict(source)
        migrated.append(normalized)
        if str(source.get("publication_type") or "").strip().casefold() != "book":
            continue
        report.append({
            "paper_id": source.get("paper_id", ""),
            "title": source.get("title", ""),
            "current_venue": source.get("venue_name") or source.get("venue", ""),
            "current_paper_type_category": source.get("entry_type", ""),
            "current_track": source.get("venue_track", ""),
            "incompatible_values": json.dumps(incompatible, ensure_ascii=False, sort_keys=True),
            "action_taken": (
                "cleared incompatible metadata" if apply and incompatible
                else "no change required" if not incompatible
                else "would clear incompatible metadata"
            ),
            "evidence_rationale": (
                "The curated publication_type is book; the listed values are in the "
                "authoritative book-incompatible venue/category taxonomy. Publication "
                "type, identity, authors, and mappings were preserved."
            ),
        })
    return migrated, report


def write_report(rows, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--papers", type=Path, default=DEFAULT_CURATED_PAPERS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = read_curated_papers(args.papers)
    migrated, report = audit_rows(source, apply=args.apply)
    write_report(report, args.report)
    if args.apply:
        write_curated_papers(migrated, args.papers)
    print(f"Audited {len(report)} curated book records; apply={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
