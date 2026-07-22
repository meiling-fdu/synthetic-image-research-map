#!/usr/bin/env python3
"""Audit institution-type classifications across curated and public surfaces."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .curated_institutions import load_institutions, save_institutions
    from .curated_schema import INSTITUTION_ALIAS_COLUMNS
    from .institution_types import (
        INSTITUTION_TYPE_SET,
        clean,
        confirmed_aliases_by_institution,
        type_decision,
    )
except ImportError:
    from curated_institutions import load_institutions, save_institutions
    from curated_schema import INSTITUTION_ALIAS_COLUMNS
    from institution_types import (
        INSTITUTION_TYPE_SET,
        clean,
        confirmed_aliases_by_institution,
        type_decision,
    )


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INSTITUTIONS = ROOT / "data/curated/institutions.csv"
DEFAULT_ALIASES = ROOT / "data/curated/institution_aliases.csv"
DEFAULT_PAPER_PUBLIC = ROOT / "web/data/public_preview_papers.json"
DEFAULT_MAP_PUBLIC = ROOT / "web/data/public_preview_map_data.json"
DEFAULT_REPORT = ROOT / "data/processed/institution_type_audit.csv"
APPLY_TIMESTAMP = "2026-07-22T00:00:00Z"
REPORT_COLUMNS = (
    "institution_id",
    "canonical_name",
    "current_type",
    "proposed_type",
    "evidence",
    "confidence",
    "provenance",
    "usage_paper_count",
    "usage_map_record_count",
    "review_required",
    "applied_rule",
    "curated_presence",
)


def read_csv_rows(path: Path, columns: tuple[str, ...] | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if columns is not None and tuple(reader.fieldnames or ()) != columns:
            raise ValueError(f"{path} has an unexpected CSV header")
        return list(reader)


def read_public_payload(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise ValueError(f"{path} is not a public preview payload")
    return payload


def public_institution_name(value: dict[str, Any]) -> str:
    return clean(
        value.get("canonical_name")
        or value.get("canonical_institution_name")
        or value.get("name")
        or value.get("institution")
        or value.get("institution_name")
    )


def iter_public_institution_values(record: dict[str, Any]):
    if isinstance(record, dict):
        yield record
        for field in ("affiliations", "author_institution_affiliations"):
            for affiliation in record.get(field) or []:
                if isinstance(affiliation, dict):
                    yield affiliation
        current = record.get("current_institution")
        if isinstance(current, dict):
            yield current


def collect_public_other_records(
    paper_payload: dict[str, Any],
    map_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    public: dict[str, dict[str, Any]] = {}
    paper_usage: dict[str, set[str]] = defaultdict(set)
    map_usage: Counter[str] = Counter()

    def ensure(value: dict[str, Any], source: str) -> str:
        institution_id = clean(
            value.get("institution_id") or value.get("canonical_institution_id")
        )
        name = public_institution_name(value)
        if not institution_id or not name:
            return ""
        row = public.setdefault(institution_id, {
            "institution_id": institution_id,
            "canonical_name": name,
            "current_type": "other",
            "sources": set(),
        })
        row["sources"].add(source)
        if len(name) > len(row["canonical_name"]):
            row["canonical_name"] = name
        return institution_id

    for record in paper_payload["records"]:
        paper_identity = clean(record.get("paper_id")) or clean(record.get("title"))
        for value in iter_public_institution_values(record):
            if clean(value.get("institution_type") or value.get("type")) != "other":
                continue
            institution_id = ensure(value, "public_preview_papers")
            if institution_id and paper_identity:
                paper_usage[institution_id].add(paper_identity)

    for record in map_payload["records"]:
        for value in iter_public_institution_values(record):
            if clean(value.get("institution_type") or value.get("type")) != "other":
                continue
            institution_id = ensure(value, "public_preview_map_data")
            if institution_id:
                map_usage[institution_id] += 1

    for institution_id, row in public.items():
        row["usage_paper_count"] = len(paper_usage[institution_id])
        row["usage_map_record_count"] = map_usage[institution_id]
        row["provenance"] = ";".join(sorted(row["sources"]))
    return public


def audit_rows(
    institutions: list[dict[str, str]],
    aliases: list[dict[str, str]],
    public_other: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    by_id = {clean(row.get("institution_id")): row for row in institutions}
    active_by_id = {
        institution_id: row
        for institution_id, row in by_id.items()
        if clean(row.get("institution_status")) == "active"
    }
    aliases_by_id = confirmed_aliases_by_institution(aliases)
    parent_types = {
        institution_id: clean(active_by_id.get(clean(row.get("parent_institution_id")), {}).get("institution_type"))
        for institution_id, row in active_by_id.items()
    }

    candidates: dict[str, dict[str, Any]] = {}
    for institution_id, row in active_by_id.items():
        if (
            clean(row.get("institution_type")) != "other"
            and clean(row.get("created_by")) != "institution-type-audit"
        ):
            continue
        candidates[institution_id] = {
            "institution_id": institution_id,
            "canonical_name": clean(row.get("canonical_name")),
            "current_type": clean(row.get("institution_type")),
            "curated_presence": "curated",
            "usage_paper_count": 0,
            "usage_map_record_count": 0,
            "provenance": "curated",
            "reviewed_type": True,
            "parent_type": parent_types.get(institution_id, ""),
        }
    for institution_id, row in public_other.items():
        if institution_id in candidates:
            candidates[institution_id]["usage_paper_count"] = row.get("usage_paper_count", 0)
            candidates[institution_id]["usage_map_record_count"] = row.get("usage_map_record_count", 0)
            candidates[institution_id]["provenance"] += ";" + row.get("provenance", "")
            continue
        if institution_id in active_by_id and clean(active_by_id[institution_id].get("institution_type")) != "other":
            candidates[institution_id] = {
                "institution_id": institution_id,
                "canonical_name": clean(active_by_id[institution_id].get("canonical_name")) or clean(row.get("canonical_name")),
                "current_type": "other",
                "curated_presence": "curated_public_mismatch",
                "usage_paper_count": row.get("usage_paper_count", 0),
                "usage_map_record_count": row.get("usage_map_record_count", 0),
                "provenance": row.get("provenance", "public_preview"),
                "reviewed_type": False,
                "trusted_type": clean(active_by_id[institution_id].get("institution_type")),
                "parent_type": "",
            }
            continue
        candidates[institution_id] = {
            "institution_id": institution_id,
            "canonical_name": clean(row.get("canonical_name")),
            "current_type": "other",
            "curated_presence": "public_only",
            "usage_paper_count": row.get("usage_paper_count", 0),
            "usage_map_record_count": row.get("usage_map_record_count", 0),
            "provenance": row.get("provenance", "public_preview"),
            "reviewed_type": False,
            "parent_type": "",
        }

    report = []
    for institution_id, candidate in sorted(
        candidates.items(),
        key=lambda item: (clean(item[1].get("canonical_name")).casefold(), item[0]),
    ):
        decision = type_decision(
            candidate["canonical_name"],
            aliases_by_id.get(institution_id, ()),
            candidate["current_type"],
            reviewed_type=bool(candidate.get("reviewed_type")),
            trusted_type=candidate.get("trusted_type", ""),
            parent_type=candidate.get("parent_type", ""),
        )
        report.append({
            "institution_id": institution_id,
            "canonical_name": candidate["canonical_name"],
            "current_type": candidate["current_type"],
            "proposed_type": decision.proposed_type,
            "evidence": decision.evidence,
            "confidence": decision.confidence,
            "provenance": candidate["provenance"] + f";policy={decision.provenance}",
            "usage_paper_count": str(candidate["usage_paper_count"]),
            "usage_map_record_count": str(candidate["usage_map_record_count"]),
            "review_required": "yes" if decision.review_required else "no",
            "applied_rule": decision.rule,
            "curated_presence": candidate["curated_presence"],
        })
    return report


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def apply_high_confidence(
    institutions: list[dict[str, str]],
    rows: list[dict[str, str]],
    institutions_path: Path,
) -> int:
    by_id = {clean(row.get("institution_id")): row for row in institutions}
    changes = 0
    for row in rows:
        if row["confidence"] != "high" or row["review_required"] != "no":
            continue
        if row["proposed_type"] not in INSTITUTION_TYPE_SET:
            continue
        if row["current_type"] == row["proposed_type"]:
            continue
        institution_id = row["institution_id"]
        if institution_id in by_id:
            target = by_id[institution_id]
            if clean(target.get("institution_type")) == row["proposed_type"]:
                continue
            target["institution_type"] = row["proposed_type"]
            target["updated_at"] = APPLY_TIMESTAMP
            changes += 1
            continue
        institutions.append({
            "institution_id": institution_id,
            "canonical_name": row["canonical_name"],
            "institution_type": row["proposed_type"],
            "institution_status": "active",
            "parent_institution_id": "",
            "public_display": "self",
            "created_at": APPLY_TIMESTAMP,
            "updated_at": APPLY_TIMESTAMP,
            "created_by": "institution-type-audit",
        })
        by_id[institution_id] = institutions[-1]
        changes += 1
    if changes:
        save_institutions(institutions, institutions_path)
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--institutions", type=Path, default=DEFAULT_INSTITUTIONS)
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES)
    parser.add_argument("--public-papers", type=Path, default=DEFAULT_PAPER_PUBLIC)
    parser.add_argument("--public-maps", type=Path, default=DEFAULT_MAP_PUBLIC)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply-high-confidence", action="store_true")
    args = parser.parse_args(argv)

    institutions = load_institutions(args.institutions)
    aliases = read_csv_rows(args.aliases, tuple(INSTITUTION_ALIAS_COLUMNS))
    public_other = collect_public_other_records(
        read_public_payload(args.public_papers),
        read_public_payload(args.public_maps),
    )
    rows = audit_rows(institutions, aliases, public_other)
    write_report(args.output, rows)
    changes = 0
    if args.apply_high_confidence:
        changes = apply_high_confidence(institutions, rows, args.institutions)
        if changes:
            institutions = load_institutions(args.institutions)
            rows = audit_rows(institutions, aliases, public_other)
            write_report(args.output, rows)

    pending = [
        row for row in rows
        if row["confidence"] == "high"
        and row["review_required"] == "no"
        and row["current_type"] != row["proposed_type"]
        and row["curated_presence"] != "curated_public_mismatch"
    ]
    unresolved = [row for row in rows if row["review_required"] == "yes"]
    proposed_counts = Counter(row["proposed_type"] for row in rows)
    print(f"Institution type audit rows: {len(rows)}")
    print(f"High-confidence changes applied: {changes}")
    print(f"Pending high-confidence changes: {len(pending)}")
    print(f"Review-required rows: {len(unresolved)}")
    print(f"Proposed types among audited rows: {dict(sorted(proposed_counts.items()))}")
    print(f"Report: {args.output}")
    return 1 if args.check and pending else 0


if __name__ == "__main__":
    raise SystemExit(main())
