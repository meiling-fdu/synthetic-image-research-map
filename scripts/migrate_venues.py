#!/usr/bin/env python3
"""Audit or apply the idempotent curated-paper venue migration."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

try:
    from .curated_schema import PAPERS_COLUMNS
    from .paper_exclusions import all_identity_keys
    from .venues import (
        alias_key,
        canonicalize_record,
        clean_text,
        display_venue,
        read_venue_aliases,
        _known_lookup_keys,
    )
except ImportError:
    from curated_schema import PAPERS_COLUMNS
    from paper_exclusions import all_identity_keys
    from venues import (
        alias_key,
        canonicalize_record,
        clean_text,
        display_venue,
        read_venue_aliases,
        _known_lookup_keys,
    )


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "curated" / "papers.csv"
DEFAULT_REPORT = ROOT / "docs" / "venue_migration_report.json"
MALFORMED_TOKEN_PATTERNS = (
    "Inter national",
    "Work shop",
    "Multi media",
    "Infor mation",
)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or ()), [dict(row) for row in reader]


def paper_identity(row: Mapping[str, Any], index: int) -> tuple[Any, ...]:
    keys = all_identity_keys(row)
    return tuple(keys[0]) if keys else ("row", index)


def _alias_lookup(aliases: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in aliases:
        if clean_text(row.get("review_status")) != "confirmed":
            continue
        key = alias_key(row.get("alias"))
        if key:
            lookup[key].append(row)
    return lookup


def _applied_alias_or_rule(raw: str, resolved: Mapping[str, Any], alias_lookup: Mapping[str, list[dict[str, str]]]) -> str:
    venue_id = clean_text(resolved.get("venue_id"))
    for key in _known_lookup_keys(raw):
        for row in alias_lookup.get(key, []):
            if clean_text(row.get("venue_id")) == venue_id:
                alias = clean_text(row.get("alias"))
                return f"alias:{alias}" if alias else "alias"
    if clean_text(resolved.get("ambiguity_status")) == "unmapped":
        return "generated-unmapped-canonical"
    if clean_text(resolved.get("ambiguity_status")) == "ambiguous":
        return "ambiguous-generated-canonical"
    return "existing-canonical-fields"


def _canonical_key(row: Mapping[str, Any], *, include_acronym: bool = False) -> tuple[str, str]:
    name = alias_key(row.get("venue_name"))
    track = clean_text(row.get("venue_track") or "main")
    if include_acronym:
        return (name, alias_key(row.get("venue_acronym")), track)
    return (name, track)


def _inventory_scan(rows: list[dict[str, str]], migrated: list[dict[str, Any]], aliases: list[dict[str, str]]) -> dict[str, Any]:
    inventories = {
        "curated_before": rows,
        "curated_after": migrated,
    }
    scans: dict[str, Any] = {}
    for label, source_rows in inventories.items():
        by_name_track: dict[tuple[str, str], dict[str, Any]] = defaultdict(lambda: {
            "canonical_name": "",
            "track": "",
            "venue_ids": set(),
            "labels": set(),
        })
        by_name_acronym_track: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(lambda: {
            "canonical_name": "",
            "acronyms": set(),
            "track": "",
            "venue_ids": set(),
            "labels": set(),
        })
        malformed = []
        missing_acronyms = []
        for row in source_rows:
            venue_id = clean_text(row.get("venue_id"))
            name = clean_text(row.get("venue_name"))
            acronym = clean_text(row.get("venue_acronym"))
            track = clean_text(row.get("venue_track") or "main")
            if not (venue_id or name):
                continue
            label_text = display_venue(row)
            name_key, track_key = _canonical_key(row)
            bucket = by_name_track[(name_key, track_key)]
            bucket["canonical_name"] = name
            bucket["track"] = track
            bucket["venue_ids"].add(venue_id)
            bucket["labels"].add(label_text)
            acronym_bucket = by_name_acronym_track[(name_key, alias_key(acronym), track_key)]
            acronym_bucket["canonical_name"] = name
            acronym_bucket["acronyms"].add(acronym)
            acronym_bucket["track"] = track
            acronym_bucket["venue_ids"].add(venue_id)
            acronym_bucket["labels"].add(label_text)
            checked_values = [
                ("venue_name", name),
                ("raw_venue", clean_text(row.get("raw_venue"))),
                ("venue", clean_text(row.get("venue"))),
            ]
            for field, value in checked_values:
                for pattern in MALFORMED_TOKEN_PATTERNS:
                    if pattern.casefold() in value.casefold():
                        malformed.append({
                            "field": field,
                            "value": value,
                            "pattern": pattern,
                            "venue_id": venue_id,
                            "paper_id": clean_text(row.get("paper_id")),
                        })
            if name and not acronym and re.search(
                r"\b(?:IEEE|ACM|International|Conference|Workshop|Computer Vision|Multimedia|Neural Networks)\b",
                name,
                flags=re.I,
            ):
                missing_acronyms.append({
                    "venue_id": venue_id,
                    "venue_name": name,
                    "track": track,
                    "paper_id": clean_text(row.get("paper_id")),
                })
        scans[label] = {
            "same_name_different_ids": [
                {
                    **{key: value for key, value in bucket.items() if key not in {"venue_ids", "labels"}},
                    "venue_ids": sorted(bucket["venue_ids"]),
                    "labels": sorted(bucket["labels"]),
                }
                for bucket in by_name_track.values()
                if len(bucket["venue_ids"] - {""}) > 1
            ],
            "same_name_acronym_variant_ids": [
                {
                    "canonical_name": bucket["canonical_name"],
                    "track": bucket["track"],
                    "venue_ids": sorted(bucket["venue_ids"]),
                    "labels": sorted(bucket["labels"]),
                }
                for bucket in by_name_track.values()
                if len(bucket["labels"]) > 1 and len(bucket["venue_ids"] - {""}) > 1
            ],
            "malformed_embedded_whitespace": malformed,
            "missing_established_acronym_candidates": missing_acronyms,
        }
    alias_malformed = []
    for row in aliases:
        for field in ("alias", "venue_name"):
            value = clean_text(row.get(field))
            for pattern in MALFORMED_TOKEN_PATTERNS:
                if pattern.casefold() in value.casefold():
                    alias_malformed.append({
                        "field": field,
                        "value": value,
                        "pattern": pattern,
                        "venue_id": clean_text(row.get("venue_id")),
                    })
    scans["alias_registry"] = {
        "malformed_embedded_whitespace": alias_malformed,
    }
    return scans


def migrate_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    aliases = read_venue_aliases()
    alias_lookup = _alias_lookup(aliases)
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
        previous_venue_id = str(row.get("venue_id", "")).strip()
        key = (raw, previous_venue_id, resolved.get("venue_id", ""))
        audit.setdefault(key, {
            "raw_venue": raw,
            "previous_venue_id": previous_venue_id,
            "proposed_canonical_venue": display_venue(resolved),
            "proposed_canonical_venue_id": resolved.get("venue_id", ""),
            "venue_name": resolved.get("venue_name", ""),
            "venue_acronym": resolved.get("venue_acronym", ""),
            "venue_type": resolved.get("venue_type", ""),
            "venue_track": resolved.get("venue_track", "main"),
            "affected_paper_count": 0,
            "applied_alias_or_rule": _applied_alias_or_rule(raw, resolved, alias_lookup),
            "ambiguity_status": resolved.get("ambiguity_status", "resolved"),
        })
        audit[key]["affected_paper_count"] += 1
        migrated.append({column: resolved.get(column, "") for column in PAPERS_COLUMNS})
    groups = []
    raw_by_canonical: dict[str, set[str]] = defaultdict(set)
    for (raw, previous_venue_id, venue_id), item in audit.items():
        if venue_id:
            raw_by_canonical[venue_id].add(raw)
    for venue_id, raw_values in raw_by_canonical.items():
        if len(raw_values) > 1:
            example = next(item for (raw, previous, candidate), item in audit.items() if candidate == venue_id)
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
        "audit": sorted(audit.values(), key=lambda item: (
            item["raw_venue"].casefold(),
            item["previous_venue_id"],
            item["proposed_canonical_venue_id"],
        )),
        "largest_duplicate_groups_merged": groups,
        "inventory_scan": _inventory_scan(rows, migrated, aliases),
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
