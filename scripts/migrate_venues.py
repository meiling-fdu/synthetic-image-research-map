#!/usr/bin/env python3
"""Audit or apply the idempotent curated-paper venue migration."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

try:
    from .curated_schema import PAPERS_COLUMNS
    from .paper_exclusions import all_identity_keys
    from .venues import canonicalize_record, display_venue, read_venue_aliases
except ImportError:
    from curated_schema import PAPERS_COLUMNS
    from paper_exclusions import all_identity_keys
    from venues import canonicalize_record, display_venue, read_venue_aliases


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "curated" / "papers.csv"
DEFAULT_REPORT = ROOT / "docs" / "venue_migration_report.json"


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or ()), [dict(row) for row in reader]


def paper_identity(row: Mapping[str, Any], index: int) -> tuple[Any, ...]:
    keys = all_identity_keys(row)
    return tuple(keys[0]) if keys else ("row", index)


def migrate_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    aliases = read_venue_aliases()
    migrated: list[dict[str, Any]] = []
    raw_identities: dict[str, set[tuple[Any, ...]]] = defaultdict(set)
    canonical_identities: dict[str, set[tuple[Any, ...]]] = defaultdict(set)
    changes = 0
    ambiguous = 0
    workshop_record_ids: set[tuple[Any, ...]] = set()
    workshop_venue_ids: set[str] = set()
    normalized_workshop_record_ids: set[tuple[Any, ...]] = set()
    normalized_workshop_venue_ids: set[str] = set()
    audit: dict[tuple[str, str], dict[str, Any]] = {}
    venue_fields = ("venue_id", "venue_name", "venue_acronym", "venue_type", "venue_track", "raw_venue")
    for index, row in enumerate(rows):
        resolved = canonicalize_record(row, aliases)
        identity = paper_identity(row, index)
        if str(row.get("venue_type", "")).strip().casefold() == "workshop":
            workshop_record_ids.add(identity)
            workshop_venue_ids.add(str(row.get("venue_id", "")).strip())
        if str(resolved.get("venue_track", "")).strip().casefold() == "workshops":
            normalized_workshop_record_ids.add(identity)
            normalized_workshop_venue_ids.add(str(resolved.get("venue_id", "")).strip())
        raw = str(row.get("raw_venue") or row.get("venue") or "").strip()
        raw_identities[raw].add(identity)
        canonical_identities[resolved.get("venue_id", "")].add(identity)
        changed = any(str(row.get(field, "")) != str(resolved.get(field, "")) for field in (*venue_fields, "venue"))
        changes += int(changed)
        ambiguous += int(resolved.get("ambiguity_status") == "ambiguous")
        key = (raw, resolved.get("venue_id", ""))
        audit.setdefault(key, {
            "raw_venue": raw,
            "proposed_canonical_venue": display_venue(resolved),
            "venue_id": resolved.get("venue_id", ""),
            "venue_name": resolved.get("venue_name", ""),
            "venue_acronym": resolved.get("venue_acronym", ""),
            "venue_type": resolved.get("venue_type", ""),
            "venue_track": resolved.get("venue_track", "main"),
            "affected_paper_count": 0,
            "ambiguity_status": resolved.get("ambiguity_status", "resolved"),
        })
        audit[key]["affected_paper_count"] += 1
        migrated.append({column: resolved.get(column, "") for column in PAPERS_COLUMNS})
    groups = []
    raw_by_canonical: dict[str, set[str]] = defaultdict(set)
    for (raw, venue_id), item in audit.items():
        if venue_id:
            raw_by_canonical[venue_id].add(raw)
    for venue_id, raw_values in raw_by_canonical.items():
        if len(raw_values) > 1:
            example = next(item for (raw, candidate), item in audit.items() if candidate == venue_id)
            groups.append({
                "venue_id": venue_id,
                "canonical_venue": example["proposed_canonical_venue"],
                "raw_variant_count": len(raw_values),
                "paper_count": len(canonical_identities[venue_id]),
                "raw_variants": sorted(raw_values),
            })
    groups.sort(key=lambda group: (-group["paper_count"], -group["raw_variant_count"], group["venue_id"]))
    report = {
        "mode": "audit",
        "source": "data/curated/papers.csv",
        "paper_count": len({paper_identity(row, index) for index, row in enumerate(rows)}),
        "raw_venue_variant_count": sum(bool(key) for key in raw_identities),
        "canonical_venue_count": sum(bool(key) for key in canonical_identities),
        "records_changed": changes,
        "ambiguous_records": ambiguous,
        "workshop_records_migrated": len(workshop_record_ids),
        "workshop_venues_migrated": len(workshop_venue_ids - {""}),
        "workshop_track_records": len(normalized_workshop_record_ids),
        "workshop_track_venues": len(normalized_workshop_venue_ids - {""}),
        "audit": sorted(audit.values(), key=lambda item: (item["raw_venue"].casefold(), item["venue_id"])),
        "largest_duplicate_groups_merged": groups,
    }
    return migrated, report


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPERS_COLUMNS, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--apply", action="store_true", help="Atomically update the curated paper CSV after writing the report.")
    args = parser.parse_args()
    _header, rows = read_rows(args.input)
    migrated, report = migrate_rows(rows)
    report["mode"] = "apply" if args.apply else "dry-run"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.apply:
        write_rows(args.input, migrated)
    print(json.dumps({key: report[key] for key in (
        "mode", "paper_count", "raw_venue_variant_count", "canonical_venue_count",
        "records_changed", "ambiguous_records", "workshop_records_migrated",
        "workshop_venues_migrated",
        "workshop_track_records", "workshop_track_venues",
    )}, indent=2))
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
