#!/usr/bin/env python3
"""Conservatively split acronym suffixes from canonical institution names."""

from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .curated_schema import (
        CURATED_DATA_DIR, INSTITUTION_ALIAS_COLUMNS, INSTITUTION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
    )
except ImportError:
    from curated_schema import (
        CURATED_DATA_DIR, INSTITUTION_ALIAS_COLUMNS, INSTITUTION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
    )


LEGACY_COLUMNS = tuple(column for column in INSTITUTION_COLUMNS if column != "abbreviation")
ACRONYM_SUFFIX = re.compile(
    r"^(?P<name>.+\S)\s+\((?P<abbreviation>[A-Z0-9][A-Z0-9&+./* -]{1,22})\)$"
)


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def split_clear_acronym_suffix(value: Any) -> tuple[str, str] | None:
    """Recognize only compact, uppercase acronym-style terminal suffixes."""
    canonical = clean(value)
    match = ACRONYM_SUFFIX.fullmatch(canonical)
    if not match:
        return None
    name = clean(match.group("name"))
    abbreviation = clean(match.group("abbreviation"))
    letters = [character for character in abbreviation if character.isalpha()]
    if len(name) < 4 or len(letters) < 2 or any(letter != letter.upper() for letter in letters):
        return None
    return name, abbreviation


def migrate_rows(rows: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, str]], int]:
    migrated: list[dict[str, str]] = []
    changed = 0
    for source in rows:
        row = {column: clean(source.get(column)) for column in INSTITUTION_COLUMNS}
        if not row["abbreviation"]:
            split = split_clear_acronym_suffix(row["canonical_name"])
            if split:
                row["canonical_name"], row["abbreviation"] = split
                changed += 1
        migrated.append(row)
    return migrated, changed


def migrate_file(path: Path, *, check: bool = False) -> int:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = tuple(reader.fieldnames or ())
        if header not in {LEGACY_COLUMNS, INSTITUTION_COLUMNS}:
            raise ValueError(f"{path} has an unexpected CSV header")
        rows, changed = migrate_rows(list(reader))
    header_change = header != INSTITUTION_COLUMNS
    if check or (not changed and not header_change):
        return changed
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INSTITUTION_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return changed


def _write_durable(
    path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]], *,
    lineterminator: str = "\n",
) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator=lineterminator)
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def synchronize_canonical_references(
    path: Path, columns: Sequence[str], names_by_id: Mapping[str, str], *, check: bool = False
) -> int:
    uses_crlf = b"\r\n" in path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != tuple(columns):
            raise ValueError(f"{path} has an unexpected CSV header")
        rows = list(reader)
    changed = 0
    for row in rows:
        canonical = names_by_id.get(clean(row.get("institution_id")))
        if canonical and clean(row.get("canonical_institution_name")) != canonical:
            row["canonical_institution_name"] = canonical
            changed += 1
    if changed and not check:
        _write_durable(
            path, columns, rows,
            lineterminator="\r\n" if uses_crlf else "\n",
        )
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=CURATED_DATA_DIR / "institutions.csv")
    parser.add_argument("--aliases-path", type=Path, default=CURATED_DATA_DIR / "institution_aliases.csv")
    parser.add_argument("--reviews-path", type=Path, default=CURATED_DATA_DIR / "institution_location_review.csv")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    changed = migrate_file(arguments.path, check=arguments.check)
    with arguments.path.open(encoding="utf-8-sig", newline="") as handle:
        names_by_id = {
            clean(row.get("institution_id")): clean(row.get("canonical_name"))
            for row in csv.DictReader(handle)
        }
    aliases_changed = synchronize_canonical_references(
        arguments.aliases_path, INSTITUTION_ALIAS_COLUMNS, names_by_id,
        check=arguments.check,
    )
    reviews_changed = synchronize_canonical_references(
        arguments.reviews_path, INSTITUTION_LOCATION_REVIEW_COLUMNS, names_by_id,
        check=arguments.check,
    )
    qualifier = "would be " if arguments.check else ""
    print(
        f"{changed} institution abbreviation suffixes {qualifier}migrated; "
        f"{aliases_changed + reviews_changed} canonical references {qualifier}synchronized"
    )


if __name__ == "__main__":
    main()
