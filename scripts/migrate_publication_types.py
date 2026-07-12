#!/usr/bin/env python3
"""Migrate publication_type CSV fields without rewriting unrelated fields."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from .publication_types import normalize_publication_type
except ImportError:
    from publication_types import normalize_publication_type


ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOTS = (ROOT / "data/curated", ROOT / "data/manual", ROOT / "data/processed")
CANONICAL_TYPES = {"conference", "journal", "preprint", "book"}
MIGRATABLE_LEGACY_TYPES = {
    "article", "article-journal", "journal-article", "journal article",
    "conference-paper", "conference paper", "proceedings",
    "proceedings-article", "proceedings article", "inproceedings",
    "review", "editorial", "letter", "survey", "book-chapter",
    "book chapter", "chapter", "posted-content", "posted content",
}


def csv_record_spans(text: str) -> List[Tuple[int, int]]:
    spans: List[Tuple[int, int]] = []
    start = 0
    quoted = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == '"':
            if quoted and index + 1 < len(text) and text[index + 1] == '"':
                index += 2
                continue
            quoted = not quoted
        if char == "\n" and not quoted:
            spans.append((start, index + 1))
            start = index + 1
        index += 1
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def csv_field_spans(record: str) -> List[Tuple[int, int]]:
    spans: List[Tuple[int, int]] = []
    start = 0
    quoted = False
    index = 0
    while index < len(record):
        char = record[index]
        if char == '"':
            if quoted and index + 1 < len(record) and record[index + 1] == '"':
                index += 2
                continue
            quoted = not quoted
        elif char == "," and not quoted:
            spans.append((start, index))
            start = index + 1
        elif char in "\r\n" and not quoted:
            break
        index += 1
    spans.append((start, index))
    return spans


def replacement_field(raw_field: str, value: str) -> str:
    if raw_field.startswith('"') and raw_field.endswith('"'):
        return '"' + value.replace('"', '""') + '"'
    return value


def normalize_row(row: Dict[str, str]) -> str:
    return normalize_publication_type(
        row.get("publication_type"),
        venue=(
            row.get("venue")
            or row.get("venue_name")
            or row.get("publication_venue")
            or row.get("formal_venue")
        ),
        venue_type=row.get("venue_type"),
        arxiv_id=row.get("arxiv_id"),
        arxiv_url=row.get("arxiv_url"),
        doi=row.get("doi"),
    )


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def migrate_csv(path: Path, *, write: bool) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        text = handle.read()
    record_spans = csv_record_spans(text)
    parsed = list(csv.reader(text.splitlines(keepends=True)))
    if not parsed or "publication_type" not in parsed[0]:
        return {"path": display_path(path), "changes": {}, "unresolved": []}
    if len(parsed) != len(record_spans):
        raise ValueError(f"Could not preserve CSV record boundaries in {path}")
    fieldnames = parsed[0]
    type_index = fieldnames.index("publication_type")
    changes: Counter[str] = Counter()
    unresolved: List[Dict[str, str]] = []
    replacements: List[Tuple[int, int, str]] = []
    for row_number, ((record_start, record_end), values) in enumerate(
        zip(record_spans[1:], parsed[1:]), start=2
    ):
        padded = values + [""] * (len(fieldnames) - len(values))
        row = dict(zip(fieldnames, padded))
        old = row.get("publication_type", "").strip()
        if not old:
            continue
        old_key = old.casefold().replace("_", "-")
        if old_key in CANONICAL_TYPES:
            if old_key != "journal" or normalize_row(row) != "conference":
                continue
        if old_key not in CANONICAL_TYPES and old_key not in MIGRATABLE_LEGACY_TYPES:
            unresolved.append({"row": str(row_number), "title": row.get("title", ""), "value": old})
            continue
        new = normalize_row(row)
        if not new:
            unresolved.append({"row": str(row_number), "title": row.get("title", ""), "value": old})
            continue
        if new == old:
            continue
        field_spans = csv_field_spans(text[record_start:record_end])
        start, end = field_spans[type_index]
        raw_field = text[record_start + start : record_start + end]
        replacements.append(
            (record_start + start, record_start + end, replacement_field(raw_field, new))
        )
        changes[f"{old} -> {new}"] += 1
    if write and replacements:
        for start, end, replacement in reversed(replacements):
            text = text[:start] + replacement + text[end:]
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    return {
        "path": display_path(path),
        "changes": dict(sorted(changes.items())),
        "unresolved": unresolved,
    }


def source_csvs() -> Iterable[Path]:
    for root in SOURCE_ROOTS:
        yield from sorted(root.rglob("*.csv"))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Apply field-only CSV updates")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)
    paths = [path.resolve() for path in args.paths] if args.paths else list(source_csvs())
    results = [migrate_csv(path, write=args.write) for path in paths]
    print(json.dumps({"write": args.write, "files": results}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
