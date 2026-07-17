#!/usr/bin/env python3
"""List records lost between a Git baseline and current public JSON outputs."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Sequence

try:
    from .export_public_preview import identity_key
except ImportError:
    from export_public_preview import identity_key


DEFAULT_PAPERS = Path("web/data/public_preview_papers.json")
DEFAULT_MAP = Path("web/data/public_preview_map_data.json")
DEFAULT_PAPER_REPORT = Path("docs/public_export_missing_papers.csv")
DEFAULT_MAP_REPORT = Path("docs/public_export_missing_map_records.csv")


def read_payload(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)["records"]


def read_git_payload(ref: str, path: Path) -> List[Dict[str, Any]]:
    raw = subprocess.check_output(["git", "show", f"{ref}:{path.as_posix()}"])
    return json.loads(raw)["records"]


def identity_label(record: Dict[str, Any]) -> str:
    kind, value = identity_key(record)
    if isinstance(value, (list, tuple)):
        value = " | ".join(str(part) for part in value)
    return f"{kind}:{value}"


def write_rows(path: Path, rows: Sequence[Dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", default="HEAD")
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--map", dest="map_path", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--paper-report", type=Path, default=DEFAULT_PAPER_REPORT)
    parser.add_argument("--map-report", type=Path, default=DEFAULT_MAP_REPORT)
    args = parser.parse_args()

    baseline_papers = read_git_payload(args.baseline_ref, args.papers)
    current_papers = read_payload(args.papers)
    current_paper_keys = {identity_key(record) for record in current_papers}
    missing_papers = [
        record for record in baseline_papers
        if identity_key(record) not in current_paper_keys
    ]
    paper_rows = [{
        "canonical_paper_identity": identity_label(record),
        "title": record.get("title", ""),
        "year": record.get("year", ""),
        "doi": record.get("doi", ""),
        "openalex_url": record.get("openalex_url", ""),
        "in_scope": record.get("in_scope", ""),
        "review_status": record.get("review_status", ""),
        "needs_review": record.get("needs_review", ""),
        "publication_type": record.get("publication_type", ""),
        "venue_type": record.get("venue_type", ""),
        "venue_id": record.get("venue_id", ""),
        "venue_label": record.get("venue_label", ""),
        "ambiguity_status": record.get("ambiguity_status", ""),
        "map_record_count": record.get("map_record_count", ""),
        "trace_result": "valid baseline-only record absent from current partial source snapshot",
    } for record in missing_papers]
    paper_fields = list(paper_rows[0]) if paper_rows else ["canonical_paper_identity"]
    write_rows(args.paper_report, paper_rows, paper_fields)

    baseline_maps = read_git_payload(args.baseline_ref, args.map_path)
    current_maps = read_payload(args.map_path)
    current_map_ids = {record.get("id") for record in current_maps}
    missing_maps = [
        record for record in baseline_maps
        if record.get("id") not in current_map_ids
    ]
    map_rows = [{
        "map_record_id": record.get("id", ""),
        "canonical_paper_identity": identity_label(record),
        "title": record.get("title", ""),
        "year": record.get("year", ""),
        "institution": record.get("institution", ""),
        "institution_id": record.get("institution_id", ""),
        "institution_source": record.get("institution_source", ""),
        "latitude": record.get("latitude", ""),
        "longitude": record.get("longitude", ""),
        "in_scope": record.get("in_scope", ""),
        "publication_type": record.get("publication_type", ""),
        "venue_type": record.get("venue_type", ""),
        "venue_id": record.get("venue_id", ""),
        "venue_label": record.get("venue_label", ""),
        "trace_result": "valid baseline-only marker absent from current partial source snapshot",
    } for record in missing_maps]
    map_fields = list(map_rows[0]) if map_rows else ["map_record_id"]
    write_rows(args.map_report, map_rows, map_fields)
    print(f"Missing papers: {len(missing_papers)} -> {args.paper_report}")
    print(f"Missing map records: {len(missing_maps)} -> {args.map_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
