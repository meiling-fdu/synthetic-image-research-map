#!/usr/bin/env python3
"""Audit or apply deterministic publication-type normalization."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

try:
    from .curated_schema import PAPERS_COLUMNS
    from .publication_types import resolve_publication_type
except ImportError:
    from curated_schema import PAPERS_COLUMNS
    from publication_types import resolve_publication_type


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "curated" / "papers.csv"
DEFAULT_REPORT = ROOT / "data" / "processed" / "publication_type_migration_audit.csv"
DEFAULT_PUBLIC_INPUT = ROOT / "web" / "data" / "public_preview_papers.json"
DEFAULT_PUBLIC_REPORT = ROOT / "data" / "processed" / "public_preprint_book_audit.csv"

AUDIT_COLUMNS = (
    "canonical_paper_identity",
    "title",
    "previous_publication_type",
    "canonical_venue_id",
    "canonical_venue_name",
    "canonical_venue_type",
    "arxiv_id",
    "arxiv_url",
    "doi",
    "repository_identifiers",
    "proposed_publication_type",
    "applied_rule",
    "ambiguity_status",
)


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != PAPERS_COLUMNS:
            raise ValueError(f"{path} does not have the exact curated paper header")
        return [dict(row) for row in reader]


def migrate_csv(path: Path, *, write: bool = False) -> dict[str, Any]:
    """Normalize publication_type in any CSV that has that column.

    This compatibility helper is intentionally narrower than the curated-paper
    audit path: it preserves the original columns and only rewrites the
    publication_type cell when the shared resolver returns a deterministic
    normalized value.
    """
    original_text = path.read_text(encoding="utf-8-sig")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or ())
        rows = [dict(row) for row in reader]
    if "publication_type" not in fieldnames:
        raise ValueError("CSV must include publication_type")
    changes: Counter[str] = Counter()
    migrated: list[dict[str, str]] = []
    for row in rows:
        previous = row.get("publication_type", "")
        proposed, _rule = resolve_publication_type(
            previous,
            venue=row.get("venue") or row.get("venue_name") or row.get("publication_venue"),
            venue_type=row.get("venue_type"),
            arxiv_id=row.get("arxiv_id"),
            arxiv_url=row.get("arxiv_url"),
            doi=row.get("doi"),
        )
        next_row = dict(row)
        if proposed and proposed != previous:
            next_row["publication_type"] = proposed
            changes[f"{previous} -> {proposed}"] += 1
        migrated.append(next_row)
    if write and changes:
        publication_index = fieldnames.index("publication_type")
        lines = original_text.splitlines(keepends=True)
        replacements = [
            row["publication_type"]
            for row in migrated
        ]
        for index, replacement in enumerate(replacements, start=1):
            lines[index] = replace_csv_field(lines[index], publication_index, replacement)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text("".join(lines), encoding="utf-8")
        temporary.replace(path)
    return {"changes": dict(changes), "rows": len(rows)}


def replace_csv_field(line: str, field_index: int, replacement: str) -> str:
    terminator = ""
    if line.endswith("\r\n"):
        line, terminator = line[:-2], "\r\n"
    elif line.endswith("\n"):
        line, terminator = line[:-1], "\n"
    fields: list[tuple[int, int, bool]] = []
    start = 0
    quoted = False
    in_quotes = False
    index = 0
    while index < len(line):
        char = line[index]
        if index == start and char == '"':
            quoted = True
            in_quotes = True
            index += 1
            continue
        if char == '"' and in_quotes:
            if index + 1 < len(line) and line[index + 1] == '"':
                index += 2
                continue
            in_quotes = False
        elif char == "," and not in_quotes:
            fields.append((start, index, quoted))
            start = index + 1
            quoted = False
        index += 1
    fields.append((start, len(line), quoted))
    if field_index >= len(fields):
        return line + terminator
    start, end, quoted = fields[field_index]
    value = replacement.replace('"', '""') if quoted else replacement
    if quoted:
        value = f'"{value}"'
    return line[:start] + value + line[end:] + terminator


def audit_row(row: Mapping[str, Any]) -> dict[str, str]:
    proposed, rule = resolve_publication_type(
        row.get("publication_type"),
        venue=row.get("venue_name") or row.get("venue"),
        venue_type=row.get("venue_type"),
        arxiv_id=row.get("arxiv_id"),
        arxiv_url=row.get("arxiv_url"),
        doi=row.get("doi"),
    )
    ambiguity_status = "resolved" if proposed else "requires_review"
    previous = clean(row.get("publication_type"))
    canonical_identity = (
        clean(row.get("paper_id"))
        or clean(row.get("doi"))
        or clean(row.get("openalex_url"))
        or f"title-year:{clean(row.get('title'))}|{clean(row.get('year'))}"
    )
    repository_identifiers = "; ".join(dict.fromkeys(filter(None, (
        clean(row.get("arxiv_id")),
        clean(row.get("arxiv_url")),
        clean(row.get("doi")) if any(
            token in clean(row.get("doi")).casefold()
            for token in ("arxiv", "zenodo", "figshare")
        ) else "",
    ))))
    if clean(row.get("venue_id")) and clean(row.get("venue_type")) in {"conference", "journal", "book"}:
        ambiguity_status = "resolved"
    elif not proposed:
        ambiguity_status = "requires_review"
    return {
        "canonical_paper_identity": canonical_identity,
        "title": clean(row.get("title")),
        "previous_publication_type": previous,
        "canonical_venue_id": clean(row.get("venue_id")),
        "canonical_venue_name": clean(row.get("venue_name") or row.get("venue")),
        "canonical_venue_type": clean(row.get("venue_type")),
        "arxiv_id": clean(row.get("arxiv_id")),
        "arxiv_url": clean(row.get("arxiv_url")),
        "doi": clean(row.get("doi")),
        "repository_identifiers": repository_identifiers,
        "proposed_publication_type": proposed,
        "applied_rule": rule,
        "ambiguity_status": ambiguity_status,
    }


def migrate(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    migrated: list[dict[str, str]] = []
    audit: list[dict[str, str]] = []
    for row in rows:
        item = audit_row(row)
        next_row = dict(row)
        if item["ambiguity_status"] == "resolved" and item["proposed_publication_type"]:
            next_row["publication_type"] = item["proposed_publication_type"]
        migrated.append(next_row)
        audit.append(item)
    return migrated, audit


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPERS_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def write_audit(path: Path, audit: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(audit)


def audit_public_preprint_book(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise ValueError(f"{path} must contain a records list")
    return [
        audit_row(row)
        for row in records
        if isinstance(row, dict)
        and clean(row.get("publication_type")) in {"preprint", "book"}
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--public-input", type=Path, default=DEFAULT_PUBLIC_INPUT)
    parser.add_argument("--public-report", type=Path, default=DEFAULT_PUBLIC_REPORT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows = read_rows(args.input)
    migrated, audit = migrate(rows)
    write_audit(args.report, audit)
    public_audit = audit_public_preprint_book(args.public_input)
    write_audit(args.public_report, public_audit)
    changes = [
        item for item in audit
        if item["previous_publication_type"] != item["proposed_publication_type"]
        and item["ambiguity_status"] == "resolved"
    ]
    unresolved = [item for item in audit if item["ambiguity_status"] != "resolved"]
    if args.apply:
        write_rows(args.input, migrated)
    changed_by_type = Counter(
        (item["previous_publication_type"], item["proposed_publication_type"])
        for item in changes
    )
    print(f"mode: {'apply' if args.apply else 'dry-run'}")
    print(f"papers: {len(rows)}")
    print(f"changes: {len(changes)}")
    print(f"changed_by_type: {dict(sorted(changed_by_type.items()))}")
    print(f"unresolved_conflicts: {len(unresolved)}")
    print(f"report: {args.report}")
    print(f"public_preprint_book_records_audited: {len(public_audit)}")
    print(f"public_report: {args.public_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
