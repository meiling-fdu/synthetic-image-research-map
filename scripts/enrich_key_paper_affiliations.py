#!/usr/bin/env python3
"""Prepare local-only manual affiliation enrichment placeholders for key papers."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DIAGNOSTICS = Path("data/manual/key_paper_export_diagnostics.csv")
CANDIDATE_PAPERS = Path("data/processed/openalex_candidate_papers.csv")
WORK_NOTES = Path("data/manual/work_notes/missing_affiliation_manual_notes.csv")
OUTPUT = Path("data/manual/key_paper_affiliation_enrichment.csv")

TARGET_SKIP_REASON = "missing_affiliation_records"
SEDID_TITLE = "Exposing the Fake: Effective Diffusion-Generated Images Detection"

OUTPUT_COLUMNS = [
    "title",
    "year",
    "normalized_title",
    "openalex_url",
    "doi",
    "author",
    "author_position",
    "raw_affiliation",
    "institution",
    "city",
    "region",
    "country",
    "country_code",
    "latitude",
    "longitude",
    "institution_source",
    "confidence",
    "needs_manual_review",
    "notes",
]

WORK_NOTE_EVIDENCE_FIELDS = [
    "raw_affiliation_evidence",
    "canonical_institutions",
    "author_institution_mapping",
    "city_region_country",
    "coordinate_notes",
    "evidence_source",
    "manual_notes",
]


class EnrichmentError(RuntimeError):
    """An expected local input or validation error."""


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: Any) -> str:
    title = clean_text(value).casefold()
    title = title.replace("‐", "-").replace("–", "-").replace("—", "-")
    title = title.replace("real-world", "real world")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", title).split())


def normalize_identifier(value: Any) -> str:
    return clean_text(value).casefold().rstrip("/")


def normalize_doi(value: Any) -> str:
    value = re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean_text(value),
        flags=re.IGNORECASE,
    )
    return value.casefold()


def read_csv(
    path: Path,
    required_columns: Iterable[str],
    optional: bool = False,
) -> List[Dict[str, str]]:
    if not path.exists():
        if optional:
            return []
        raise EnrichmentError(f"Required local input does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(set(required_columns) - set(reader.fieldnames or []))
            if missing:
                raise EnrichmentError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise EnrichmentError(f"Could not read {path}: {error}") from error


def parse_authors(value: Any) -> List[str]:
    raw = str(value or "").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [author for author in (clean_text(value) for value in parsed) if author]


def row_key(row: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        normalize_title(row.get("normalized_title") or row.get("title")),
        clean_text(row.get("author")).casefold(),
        clean_text(row.get("author_position")),
    )


def paper_identity_keys(row: Dict[str, Any]) -> List[Tuple[str, Any]]:
    keys: List[Tuple[str, Any]] = []
    openalex = normalize_identifier(
        row.get("openalex_url") or row.get("openalex_id")
    )
    if openalex:
        keys.append(("openalex", openalex))
    doi = normalize_doi(row.get("doi"))
    if doi:
        keys.append(("doi", doi))
    title = normalize_title(row.get("title"))
    year = clean_text(row.get("publication_year") or row.get("year"))
    if title and year:
        keys.append(("title_year", (title, year)))
    return keys


def index_rows(rows: Sequence[Dict[str, str]]) -> Dict[Tuple[str, Any], Dict[str, str]]:
    index: Dict[Tuple[str, Any], Dict[str, str]] = {}
    for row in rows:
        for key in paper_identity_keys(row):
            index.setdefault(key, row)
    return index


def matching_row(
    row: Dict[str, Any],
    index: Dict[Tuple[str, Any], Dict[str, str]],
) -> Optional[Dict[str, str]]:
    return next((index[key] for key in paper_identity_keys(row) if key in index), None)


def note_evidence(row: Optional[Dict[str, str]]) -> Tuple[str, bool]:
    if row is None:
        return "", False
    parts = [
        f"{field}={clean_text(row.get(field))}"
        for field in WORK_NOTE_EVIDENCE_FIELDS
        if clean_text(row.get(field))
    ]
    return " | ".join(parts), bool(parts)


def placeholder_rows(
    targets: Sequence[Dict[str, str]],
    paper_index: Dict[Tuple[str, Any], Dict[str, str]],
    notes_index: Dict[Tuple[str, Any], Dict[str, str]],
) -> Tuple[List[Dict[str, str]], int]:
    rows: List[Dict[str, str]] = []
    work_note_evidence_used = 0
    for target in targets:
        paper = matching_row(target, paper_index)
        work_note = matching_row(target, notes_index)
        evidence_note, evidence_used = note_evidence(work_note)
        work_note_evidence_used += int(evidence_used)
        authors = parse_authors(paper.get("authors_ordered")) if paper else []
        author_entries: List[Tuple[str, str]] = [
            (author, str(position))
            for position, author in enumerate(authors, start=1)
        ] or [("", "")]
        base_note = (
            "Local candidate metadata supplies paper/author identity but no "
            "affiliation or institution evidence; needs_check."
        )
        if evidence_note:
            base_note = f"{base_note} Work-note evidence for manual review: {evidence_note}"
        for author, position in author_entries:
            rows.append(
                {
                    "title": clean_text(target.get("title")),
                    "year": clean_text(target.get("year")),
                    "normalized_title": normalize_title(target.get("title")),
                    "openalex_url": clean_text(
                        target.get("openalex_url")
                        or (paper or {}).get("openalex_url")
                        or (paper or {}).get("openalex_id")
                    ),
                    "doi": clean_text(target.get("doi") or (paper or {}).get("doi")),
                    "author": author,
                    "author_position": position,
                    "raw_affiliation": "",
                    "institution": "",
                    "city": "",
                    "region": "",
                    "country": "",
                    "country_code": "",
                    "latitude": "",
                    "longitude": "",
                    "institution_source": "",
                    "confidence": "unresolved",
                    "needs_manual_review": "yes",
                    "notes": base_note,
                }
            )
    return rows, work_note_evidence_used


def merge_existing(
    proposed: Sequence[Dict[str, str]],
    existing: Sequence[Dict[str, str]],
) -> Tuple[List[Dict[str, str]], int]:
    existing_by_key: Dict[Tuple[str, str, str], Dict[str, str]] = {}
    for row in existing:
        key = row_key(row)
        if key in existing_by_key:
            raise EnrichmentError(f"Existing enrichment contains duplicate row: {key}")
        existing_by_key[key] = {column: clean_text(row.get(column)) for column in OUTPUT_COLUMNS}

    merged: List[Dict[str, str]] = []
    seen = set()
    preserved_nonempty_values = 0
    for proposed_row in proposed:
        key = row_key(proposed_row)
        existing_row = existing_by_key.get(key)
        if existing_row is None:
            merged.append(dict(proposed_row))
        else:
            output_row = dict(proposed_row)
            for column in OUTPUT_COLUMNS:
                existing_value = clean_text(existing_row.get(column))
                if existing_value:
                    output_row[column] = existing_value
                    preserved_nonempty_values += 1
            merged.append(output_row)
        seen.add(key)

    # Preserve manually added rows, including rows outside a limited dry-run batch.
    for key, row in existing_by_key.items():
        if key not in seen:
            merged.append(dict(row))
    return merged, preserved_nonempty_values


def validate(
    rows: Sequence[Dict[str, str]],
    all_targets: Sequence[Dict[str, str]],
    full_run: bool,
) -> None:
    keys = [row_key(row) for row in rows]
    if len(set(keys)) != len(keys):
        raise EnrichmentError(
            "Duplicate normalized_title + author + author_position rows detected"
        )
    for row in rows:
        if not clean_text(row.get("title")):
            raise EnrichmentError("Every enrichment row requires title")
        if not clean_text(row.get("normalized_title")):
            raise EnrichmentError("Every enrichment row requires normalized_title")
        if not clean_text(row.get("needs_manual_review")):
            raise EnrichmentError("Every enrichment row requires needs_manual_review")

    if full_run:
        target_titles = {normalize_title(row.get("title")) for row in all_targets}
        represented = {normalize_title(row.get("title")) for row in rows}
        if len(target_titles) != 13:
            raise EnrichmentError(
                f"Expected 13 missing-affiliation targets, found {len(target_titles)}"
            )
        if not target_titles.issubset(represented):
            missing = sorted(target_titles - represented)
            raise EnrichmentError(f"Enrichment is missing target papers: {missing}")
        if normalize_title(SEDID_TITLE) not in represented:
            raise EnrichmentError("SeDID is missing from affiliation enrichment")


def write_csv(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=OUTPUT_COLUMNS,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise EnrichmentError(f"Could not write {path}: {error}") from error


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare local-only key-paper affiliation enrichment rows."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Atomically write/update the enrichment CSV (default: validation only).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Process at most this many target papers.",
    )
    parser.add_argument(
        "--fetch-openalex",
        action="store_true",
        help="Reserved for a later step; no network fetching is implemented.",
    )
    args = parser.parse_args(argv)
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.fetch_openalex:
        print("OpenAlex fetching is not implemented in this step.", file=sys.stderr)
        return 2
    try:
        diagnostics = read_csv(
            DIAGNOSTICS,
            {"title", "year", "openalex_url", "doi", "skip_reason"},
        )
        all_targets = [
            row
            for row in diagnostics
            if clean_text(row.get("skip_reason")) == TARGET_SKIP_REASON
        ]
        if len(all_targets) != 13:
            raise EnrichmentError(
                f"Expected 13 {TARGET_SKIP_REASON} targets, found {len(all_targets)}"
            )
        selected_targets = (
            all_targets[: args.limit] if args.limit is not None else all_targets
        )
        papers = read_csv(
            CANDIDATE_PAPERS,
            {"title", "year", "openalex_id", "openalex_url", "doi", "authors_ordered"},
        )
        work_notes = read_csv(WORK_NOTES, {"title", "year"}, optional=True)
        existing = read_csv(OUTPUT, OUTPUT_COLUMNS, optional=True)
        proposed, evidence_used = placeholder_rows(
            selected_targets,
            index_rows(papers),
            index_rows(work_notes),
        )
        merged, preserved_values = merge_existing(proposed, existing)
        validate(merged, all_targets, args.limit is None)
        if args.write:
            write_csv(OUTPUT, merged)
    except EnrichmentError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    represented = {normalize_title(row.get("title")) for row in merged}
    institution_values = sum(bool(clean_text(row.get("institution"))) for row in merged)
    coordinate_values = sum(
        bool(clean_text(row.get("latitude")) or clean_text(row.get("longitude")))
        for row in merged
    )
    print("Key-paper affiliation enrichment summary:")
    print(f"  Missing-affiliation papers found: {len(all_targets)}")
    print(f"  Target papers processed: {len(selected_targets)}")
    print(f"  Existing rows loaded: {len(existing)}")
    print(f"  Enrichment rows prepared: {len(merged)}")
    print(f"  All 13 papers represented: {len(all_targets) == 13 and all(normalize_title(row['title']) in represented for row in all_targets)}")
    print(f"  SeDID included: {normalize_title(SEDID_TITLE) in represented}")
    print(f"  Work-notes evidence used: {evidence_used}")
    print(f"  Non-empty institution values: {institution_values}")
    print(f"  Rows with coordinate values: {coordinate_values}")
    print(f"  Existing non-empty values preserved: {preserved_values}")
    print(f"  Output: {OUTPUT}{'' if args.write else ' (dry run; not written)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
