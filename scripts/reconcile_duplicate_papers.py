#!/usr/bin/env python3
"""Conservatively consolidate an explicitly reviewed duplicate paper identity."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .curated_papers import read_curated_papers, write_curated_papers
    from .paper_exclusions import clean, normalize_doi, normalized_title_year_key
except ImportError:  # pragma: no cover - direct script execution
    from curated_papers import read_curated_papers, write_curated_papers
    from paper_exclusions import clean, normalize_doi, normalized_title_year_key


ROOT = Path(__file__).resolve().parent.parent
CURATED = ROOT / "data" / "curated"
REFERENCE_FILES = (
    "author_institution_mappings.csv",
    "institution_location_review.csv",
    "institution_audit_log.csv",
    "institution_review_queue.csv",
    "paper_exclusions.csv",
    "review_decisions.csv",
)


class DuplicateReconciliationError(RuntimeError):
    """The reviewed pair cannot be consolidated without discarding evidence."""


def _parts(value: Any) -> list[str]:
    text = clean(value)
    separator = (
        ";" if ";" in text else "|" if "|" in text else "," if "," in text else ""
    )
    return [clean(part) for part in text.split(separator)] if separator else ([text] if text else [])


def _union_text(left: Any, right: Any, separator: str = "; ") -> str:
    values: list[str] = []
    seen: set[str] = set()
    for value in (*_parts(left), *_parts(right)):
        key = value.casefold()
        if value and key not in seen:
            seen.add(key)
            values.append(value)
    return separator.join(values)


def merge_paper_rows(
    canonical: Mapping[str, Any], duplicate: Mapping[str, Any]
) -> dict[str, Any]:
    """Merge non-conflicting metadata while retaining the chosen stable ID."""
    if normalize_doi(canonical.get("doi")) != normalize_doi(duplicate.get("doi")):
        raise DuplicateReconciliationError("reviewed rows do not share the same DOI")
    if normalized_title_year_key(canonical) != normalized_title_year_key(duplicate):
        raise DuplicateReconciliationError(
            "reviewed rows do not share the same normalized title + year"
        )
    merged = dict(canonical)
    for field, value in duplicate.items():
        if not clean(merged.get(field)) and clean(value):
            merged[field] = value
    canonical_authors = _parts(canonical.get("authors"))
    duplicate_authors = _parts(duplicate.get("authors"))
    merged["authors"] = "; ".join(
        duplicate_authors
        if set(map(str.casefold, canonical_authors)) < set(map(str.casefold, duplicate_authors))
        else _parts(_union_text(canonical.get("authors"), duplicate.get("authors")))
    )
    merged["paper_categories"] = _union_text(
        canonical.get("paper_categories"), duplicate.get("paper_categories")
    )
    merged["paper_id"] = clean(canonical.get("paper_id"))
    merged["created_at"] = clean(canonical.get("created_at"))
    merged["updated_at"] = datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    return merged


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or ()), [dict(row) for row in reader]


def _write_csv(path: Path, fields: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def reassign_references(
    retired_id: str,
    canonical: Mapping[str, Any],
    *,
    curated_dir: Path = CURATED,
) -> int:
    """Repoint exact stored IDs and refresh identity metadata on changed rows."""
    changed = 0
    canonical_id = clean(canonical.get("paper_id"))
    for filename in REFERENCE_FILES:
        path = curated_dir / filename
        if not path.exists():
            continue
        fields, rows = _read_csv(path)
        file_changed = False
        for row in rows:
            row_changed = False
            for field, value in tuple(row.items()):
                if clean(value) == retired_id:
                    row[field] = canonical_id
                    row_changed = True
                elif retired_id and retired_id in (value or ""):
                    row[field] = (value or "").replace(retired_id, canonical_id)
                    row_changed = True
            if row_changed:
                for field in ("title", "year", "doi", "openalex_url"):
                    if field in row:
                        row[field] = clean(canonical.get(field))
                changed += 1
                file_changed = True
        if file_changed:
            _write_csv(path, fields, rows)
    return changed


def consolidate(
    canonical_id: str,
    retired_id: str,
    *,
    papers_path: Path = CURATED / "papers.csv",
    curated_dir: Path = CURATED,
) -> dict[str, Any]:
    rows = read_curated_papers(papers_path)
    by_id = {clean(row.get("paper_id")): row for row in rows}
    canonical = by_id.get(canonical_id)
    duplicate = by_id.get(retired_id)
    if canonical is None and duplicate is None:
        return {"changed": False, "references_reassigned": 0}
    if canonical is None:
        raise DuplicateReconciliationError("canonical paper ID does not exist")
    if duplicate is None:
        return {"changed": False, "references_reassigned": 0}
    merged = merge_paper_rows(canonical, duplicate)
    output = [
        merged if clean(row.get("paper_id")) == canonical_id else row
        for row in rows
        if clean(row.get("paper_id")) != retired_id
    ]
    references = reassign_references(retired_id, merged, curated_dir=curated_dir)
    write_curated_papers(output, papers_path)
    return {
        "changed": True,
        "canonical_id": canonical_id,
        "retired_id": retired_id,
        "references_reassigned": references,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--retired-id", required=True)
    args = parser.parse_args(argv)
    result = consolidate(args.canonical_id, args.retired_id)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
