#!/usr/bin/env python3
"""Export uncurated OpenAlex candidate CSVs for exploratory map viewing.

The generated JSON is candidate data only, not curated final literature data. This
script performs no geocoding, calls no APIs, and never writes to data/manual/.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from .country_normalization import normalize_country_region
except ImportError:  # Direct execution from the scripts directory.
    from country_normalization import normalize_country_region


DEFAULT_PAPERS_CSV = Path(
    "data/processed/openalex_candidate_papers_in_scope.csv"
)
DEFAULT_AFFILIATIONS_CSV = Path(
    "data/processed/openalex_candidate_affiliations_geocoded.csv"
)
DEFAULT_OUTPUT = Path("web/data/openalex_candidate_map_data.json")
DEFAULT_PAPER_VERSION_OVERRIDES = Path("data/manual/paper_version_overrides.csv")
DEFAULT_PAPER_ARXIV_LINKS = Path("data/manual/paper_arxiv_links.csv")
DEFAULT_PUBLICATION_OVERRIDES = Path("data/manual/publication_overrides.csv")
DEFAULT_INSTITUTION_AUTHOR_OVERRIDES = Path(
    "data/manual/institution_author_overrides.csv"
)
DEFAULT_INSTITUTION_RECORD_OVERRIDES = Path(
    "data/manual/institution_record_overrides.csv"
)

PAPER_REQUIRED_COLUMNS = {
    "openalex_id",
    "title",
    "year",
    "venue",
    "url",
    "preliminary_task",
    "preliminary_subtask",
    "source_database",
    "manual_review",
    "notes",
}
AFFILIATION_REQUIRED_COLUMNS = {
    "openalex_id",
    "author_name",
    "institution_name",
    "city",
    "country",
    "latitude",
    "longitude",
    "manual_review",
    "notes",
}
PAPER_VERSION_OVERRIDE_COLUMNS = {
    "published_openalex_url",
    "published_doi",
    "title",
    "arxiv_id",
    "arxiv_url",
    "notes",
}
PAPER_ARXIV_LINK_COLUMNS = {
    "title",
    "year",
    "doi",
    "openalex_url",
    "arxiv_id",
    "arxiv_url",
    "arxiv_year",
    "match_status",
}
PUBLICATION_OVERRIDE_COLUMNS = {
    "title",
    "match_year",
    "formal_year",
    "formal_venue",
    "formal_doi",
    "formal_paper_url",
    "publication_type",
    "notes",
}
INSTITUTION_AUTHOR_OVERRIDE_COLUMNS = {
    "title",
    "year",
    "institution",
    "authors",
    "notes",
}
INSTITUTION_RECORD_OVERRIDE_COLUMNS = {
    "title",
    "year",
    "mode",
    "institution",
    "city",
    "region",
    "country",
    "country_code",
    "latitude",
    "longitude",
    "institution_authors",
    "notes",
}


class ExportError(RuntimeError):
    """An expected input or output error that should not show a traceback."""


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export processed OpenAlex candidate CSVs as local map JSON. "
            "Automatic rows require valid coordinates; confirmed manual "
            "overrides may remain coordinate-pending."
        )
    )
    parser.add_argument(
        "--papers-csv",
        type=Path,
        default=DEFAULT_PAPERS_CSV,
        help=f"Candidate papers CSV (default: {DEFAULT_PAPERS_CSV}).",
    )
    parser.add_argument(
        "--affiliations-csv",
        type=Path,
        default=DEFAULT_AFFILIATIONS_CSV,
        help=f"Candidate affiliations CSV (default: {DEFAULT_AFFILIATIONS_CSV}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Generated map JSON path (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--max-records",
        type=positive_int,
        help="Maximum number of grouped map records to export.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read, join, and summarize CSVs without writing JSON.",
    )
    parser.add_argument(
        "--include-out-of-scope",
        action="store_true",
        help=(
            "Include papers marked in_scope=false for debugging. By default, "
            "paper IDs and affiliation rows are restricted to in-scope papers."
        ),
    )
    return parser.parse_args(argv)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalize_entry_type(record: Dict[str, Any]) -> str:
    """Return the current entry type, translating legacy material labels."""
    value = clean_text(record.get("entry_type")).casefold()
    if value in {"method", "dataset", "benchmark", "survey", "analysis"}:
        return value
    legacy = clean_text(record.get("material_type")).casefold()
    return {
        "dataset": "dataset",
        "benchmark": "benchmark",
        "survey": "survey",
    }.get(legacy, "method")


def normalize_identifier_url(value: Any) -> str:
    return clean_text(value).casefold().rstrip("/")


def normalize_doi(value: Any) -> str:
    doi = clean_text(value)
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    return doi.casefold()


def normalize_title(value: Any) -> str:
    normalized = re.sub(r"[^\w]+", " ", clean_text(value).casefold())
    return " ".join(normalized.replace("_", " ").split())


def unique_strings(values: Iterable[Any]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        cleaned = clean_text(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def split_notes(value: Any) -> List[str]:
    note = clean_text(value)
    return [note] if note else []


def parse_bool(value: Any) -> bool:
    return clean_text(value).casefold() in {"1", "true", "yes", "y"}


def paper_is_in_scope(row: Dict[str, str]) -> bool:
    # Older explicitly scoped CSVs may predate the column; current extraction always adds it.
    return parse_bool(row.get("in_scope")) if "in_scope" in row else True


def select_scope_rows(
    paper_rows: Sequence[Dict[str, str]],
    affiliation_rows: Sequence[Dict[str, str]],
    include_out_of_scope: bool,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], Dict[str, int]]:
    in_scope_papers = [paper for paper in paper_rows if paper_is_in_scope(paper)]
    selected_papers = list(paper_rows) if include_out_of_scope else in_scope_papers
    selected_ids = {
        clean_text(paper.get("openalex_id"))
        for paper in selected_papers
        if clean_text(paper.get("openalex_id"))
    }
    in_scope_ids = {
        clean_text(paper.get("openalex_id"))
        for paper in in_scope_papers
        if clean_text(paper.get("openalex_id"))
    }
    in_scope_affiliation_count = sum(
        clean_text(row.get("openalex_id")) in in_scope_ids
        for row in affiliation_rows
    )
    selected_affiliations = [
        row
        for row in affiliation_rows
        if clean_text(row.get("openalex_id")) in selected_ids
    ]
    counts = {
        "total_candidate_papers": len(paper_rows),
        "in_scope_papers": len(in_scope_papers),
        "out_of_scope_papers": len(paper_rows) - len(in_scope_papers),
        "total_affiliation_rows": len(affiliation_rows),
        "in_scope_affiliation_rows": in_scope_affiliation_count,
        "downstream_rows_processed": len(selected_affiliations),
    }
    return selected_papers, selected_affiliations, counts


def parse_year(value: Any) -> Optional[int]:
    cleaned = clean_text(value)
    if not cleaned:
        return None
    try:
        year = int(cleaned)
    except ValueError:
        return None
    return year if 0 < year < 10000 else None


def parse_positive_int(value: Any) -> Optional[int]:
    cleaned = clean_text(value)
    if not cleaned:
        return None
    try:
        parsed = int(cleaned)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def parse_ordered_authors(value: Any) -> List[str]:
    """Parse the JSON-encoded paper-level author list from the candidate CSV."""
    raw_value = str(value or "").strip()
    if not raw_value:
        return []
    try:
        authors = json.loads(raw_value)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(authors, list):
        return []
    return [name for name in (clean_text(author) for author in authors) if name]


def fallback_authors_by_paper(
    affiliation_rows: Sequence[Dict[str, str]],
) -> Dict[str, List[str]]:
    """Reconstruct one ordered list per paper for pre-authors_ordered CSVs."""
    authors: Dict[str, Dict[str, Tuple[int, int, str]]] = {}
    for row_index, affiliation in enumerate(affiliation_rows):
        openalex_id = clean_text(affiliation.get("openalex_id"))
        author_name = clean_text(affiliation.get("author_name"))
        if not openalex_id or not author_name:
            continue
        author_order = parse_positive_int(affiliation.get("author_order"))
        author_id = clean_text(affiliation.get("author_openalex_id"))
        identity = author_id or f"{author_order or ''}:{author_name.casefold()}"
        paper_authors = authors.setdefault(openalex_id, {})
        if identity not in paper_authors:
            paper_authors[identity] = (
                author_order if author_order is not None else 10**9,
                row_index,
                author_name,
            )
    return {
        openalex_id: [item[2] for item in sorted(paper_authors.values())]
        for openalex_id, paper_authors in authors.items()
    }


def normalize_institution_name(value: Any) -> str:
    """Normalize a complete display name for exact, non-substring matching."""
    normalized = re.sub(r"[^\w]+", " ", clean_text(value).casefold())
    return " ".join(normalized.replace("_", " ").split())


def normalize_ror_id(value: Any) -> str:
    return re.sub(
        r"^https?://ror\.org/",
        "",
        clean_text(value),
        flags=re.IGNORECASE,
    ).casefold()


def institution_match_key(
    affiliation: Dict[str, str],
    institution_name: str,
) -> Tuple[str, str]:
    """Return the strongest conservative identity available for grouping."""
    openalex_id = clean_text(
        affiliation.get("institution_openalex_id")
    ).casefold().rstrip("/")
    if openalex_id:
        return "openalex", openalex_id

    ror_id = normalize_ror_id(affiliation.get("ror_id"))
    if ror_id:
        return "ror", ror_id

    normalized_name = normalize_institution_name(institution_name)
    if normalized_name:
        return "name", normalized_name
    return "unresolved", ""


def institution_author_entry(
    affiliation: Dict[str, str],
    paper_authors: Sequence[str],
) -> Optional[Tuple[int, str, str]]:
    """Return a canonical ordered author entry, or None when it is ambiguous."""
    author_name = clean_text(affiliation.get("author_name"))
    if not author_name:
        return None

    author_order = parse_positive_int(affiliation.get("author_order"))
    if author_order is not None and author_order <= len(paper_authors):
        display_name = paper_authors[author_order - 1]
        identity = clean_text(affiliation.get("author_openalex_id")) or (
            f"order:{author_order}"
        )
        return author_order, display_name, identity

    matching_positions = [
        index
        for index, display_name in enumerate(paper_authors, start=1)
        if display_name.casefold() == author_name.casefold()
    ]
    if len(matching_positions) == 1:
        matched_order = matching_positions[0]
        identity = clean_text(affiliation.get("author_openalex_id")) or (
            f"order:{matched_order}"
        )
        return matched_order, paper_authors[matched_order - 1], identity
    return None


def parse_coordinate(value: Any, minimum: float, maximum: float) -> Optional[float]:
    cleaned = clean_text(value)
    if not cleaned:
        return None
    try:
        coordinate = float(cleaned)
    except ValueError:
        return None
    if not math.isfinite(coordinate) or not minimum <= coordinate <= maximum:
        return None
    return coordinate


def read_csv(path: Path, required_columns: set) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = set(reader.fieldnames or [])
            missing = sorted(required_columns - fieldnames)
            if missing:
                raise ExportError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise ExportError(f"Could not read {path}: {error}") from error


def read_paper_version_overrides(
    path: Path = DEFAULT_PAPER_VERSION_OVERRIDES,
) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    return read_csv(path, PAPER_VERSION_OVERRIDE_COLUMNS)


def read_paper_arxiv_links(
    path: Path = DEFAULT_PAPER_ARXIV_LINKS,
) -> List[Dict[str, str]]:
    """Load the optional, partial arXiv enrichment table."""
    if not path.exists():
        return []
    return read_csv(path, PAPER_ARXIV_LINK_COLUMNS)


def read_publication_overrides(
    path: Path = DEFAULT_PUBLICATION_OVERRIDES,
) -> List[Dict[str, Any]]:
    """Load and validate auditable formal-publication corrections."""
    if not path.exists():
        return []
    rows = read_csv(path, PUBLICATION_OVERRIDE_COLUMNS)
    overrides = []
    for row_number, row in enumerate(rows, start=2):
        title = clean_text(row.get("title"))
        match_year_text = clean_text(row.get("match_year"))
        formal_year = parse_year(row.get("formal_year"))
        match_year = parse_year(match_year_text)
        if not title or formal_year is None:
            raise ExportError(
                f"{path} row {row_number} requires title and a valid formal_year"
            )
        if match_year_text and match_year is None:
            raise ExportError(f"{path} row {row_number} has an invalid match_year")
        overrides.append(
            {
                **row,
                "title": title,
                "match_year": match_year,
                "formal_year": formal_year,
            }
        )
    return overrides


def load_institution_author_overrides(
    path: Path = DEFAULT_INSTITUTION_AUTHOR_OVERRIDES,
) -> List[Dict[str, Any]]:
    """Load and validate manual institution-specific author corrections."""
    if not path.exists():
        return []

    rows = read_csv(path, INSTITUTION_AUTHOR_OVERRIDE_COLUMNS)
    overrides = []
    for row_number, row in enumerate(rows, start=2):
        title = clean_text(row.get("title"))
        institution = clean_text(row.get("institution"))
        authors = [
            clean_text(author)
            for author in str(row.get("authors") or "").split(";")
            if clean_text(author)
        ]
        year_text = clean_text(row.get("year"))
        year = parse_year(year_text)
        if not title or not institution or not authors:
            raise ExportError(
                f"{path} row {row_number} requires title, institution, and authors"
            )
        if year_text and year is None:
            raise ExportError(f"{path} row {row_number} has an invalid year")
        overrides.append(
            {
                "title": title,
                "year": year,
                "institution": institution,
                "authors": authors,
                "notes": clean_text(row.get("notes")),
            }
        )
    return overrides


def load_institution_record_overrides(
    path: Path = DEFAULT_INSTITUTION_RECORD_OVERRIDES,
) -> List[Dict[str, Any]]:
    """Load validated paper-level institution record corrections."""
    if not path.exists():
        return []

    rows = read_csv(path, INSTITUTION_RECORD_OVERRIDE_COLUMNS)
    overrides = []
    for row_number, row in enumerate(rows, start=2):
        title = clean_text(row.get("title"))
        year = parse_year(row.get("year"))
        mode = clean_text(row.get("mode")).casefold()
        institution = clean_text(row.get("institution"))
        latitude_text = clean_text(row.get("latitude"))
        longitude_text = clean_text(row.get("longitude"))
        latitude = parse_coordinate(row.get("latitude"), -90.0, 90.0)
        longitude = parse_coordinate(row.get("longitude"), -180.0, 180.0)
        if not title or year is None or not institution:
            raise ExportError(
                f"{path} row {row_number} requires title, year, and institution"
            )
        if mode not in {"replace", "add", "remove"}:
            raise ExportError(
                f"{path} row {row_number} has unsupported mode: {mode or '(empty)'}"
            )
        if (latitude_text or longitude_text) and (
            latitude is None or longitude is None
        ):
            raise ExportError(
                f"{path} row {row_number} must provide both valid coordinates or "
                "leave both blank"
            )
        overrides.append(
            {
                **row,
                "title": title,
                "year": year,
                "mode": mode,
                "doi": clean_text(row.get("doi")),
                "openalex_url": clean_text(row.get("openalex_url")),
                "institution": institution,
                "latitude": latitude,
                "longitude": longitude,
                "institution_authors": [
                    clean_text(author)
                    for author in str(row.get("institution_authors") or "").split(";")
                    if clean_text(author)
                ],
            }
        )
    return overrides


def build_override_indexes(
    overrides: Sequence[Dict[str, str]],
) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]:
    by_openalex_url: Dict[str, Dict[str, str]] = {}
    by_doi: Dict[str, Dict[str, str]] = {}
    by_title: Dict[str, Dict[str, str]] = {}
    for override in overrides:
        openalex_key = normalize_identifier_url(override.get("published_openalex_url"))
        doi_key = normalize_doi(override.get("published_doi"))
        title_key = normalize_title(override.get("title"))
        if openalex_key and openalex_key not in by_openalex_url:
            by_openalex_url[openalex_key] = override
        if doi_key and doi_key not in by_doi:
            by_doi[doi_key] = override
        if title_key and title_key not in by_title:
            by_title[title_key] = override
    return by_openalex_url, by_doi, by_title


def paper_version_override_for_record(
    record: Dict[str, Any],
    override_indexes: Tuple[
        Dict[str, Dict[str, str]],
        Dict[str, Dict[str, str]],
        Dict[str, Dict[str, str]],
    ],
) -> Optional[Dict[str, str]]:
    by_openalex_url, by_doi, by_title = override_indexes
    openalex_key = normalize_identifier_url(record.get("openalex_url"))
    if openalex_key and openalex_key in by_openalex_url:
        return by_openalex_url[openalex_key]
    doi_key = normalize_doi(record.get("doi"))
    if doi_key and doi_key in by_doi:
        return by_doi[doi_key]
    title_key = normalize_title(record.get("title"))
    if title_key and title_key in by_title:
        return by_title[title_key]
    return None


def append_record_note(record: Dict[str, Any], note: str) -> None:
    existing_notes = split_notes(record.get("notes"))
    existing_notes.extend(split_notes(note))
    record["notes"] = " | ".join(unique_strings(existing_notes))


def apply_paper_version_overrides(
    records: Sequence[Dict[str, Any]],
    overrides: Sequence[Dict[str, str]],
) -> int:
    """Attach manually confirmed alternate-version metadata to map records."""
    if not overrides:
        return 0
    override_indexes = build_override_indexes(overrides)
    applied = 0
    for record in records:
        override = paper_version_override_for_record(record, override_indexes)
        if not override:
            continue
        arxiv_id = clean_text(override.get("arxiv_id"))
        arxiv_url = clean_text(override.get("arxiv_url"))
        if arxiv_id and not arxiv_url:
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
        if arxiv_id:
            record["arxiv_id"] = arxiv_id
            record["has_arxiv_version"] = True
        if arxiv_url:
            record["arxiv_url"] = arxiv_url
            record["has_arxiv_version"] = True
        append_record_note(record, "manual arXiv version override applied")
        append_record_note(record, override.get("notes", ""))
        applied += 1
    return applied


def apply_publication_overrides(
    records: Sequence[Dict[str, Any]],
    overrides: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Replace display publication metadata without changing source records."""
    applied_indexes = set()
    for record in records:
        record_title = normalize_title(record.get("title"))
        record_year = parse_year(
            record.get("publication_year") or record.get("year")
        )
        for index, override in enumerate(overrides):
            if normalize_title(override.get("title")) != record_title:
                continue
            match_year = override.get("match_year")
            if match_year is not None and match_year != record_year:
                continue
            formal_year = override["formal_year"]
            formal_venue = clean_text(override.get("formal_venue"))
            formal_doi = clean_text(override.get("formal_doi"))
            formal_paper_url = clean_text(override.get("formal_paper_url"))
            publication_type = clean_text(override.get("publication_type"))
            record["year"] = formal_year
            record["publication_year"] = formal_year
            record["venue"] = formal_venue
            record["venue_name"] = formal_venue
            record["doi"] = formal_doi
            record["paper_url"] = formal_paper_url
            record["primary_url"] = formal_paper_url
            record["landing_page_url"] = formal_paper_url
            record["url"] = formal_paper_url
            record["publication_type"] = publication_type
            append_record_note(record, "manual publication metadata override applied")
            append_record_note(record, override.get("notes", ""))
            applied_indexes.add(index)
            break
    unmatched = [
        {
            "title": override["title"],
            "match_year": override.get("match_year"),
        }
        for index, override in enumerate(overrides)
        if index not in applied_indexes
    ]
    return {
        "publication_overrides_loaded": len(overrides),
        "publication_overrides_applied": len(applied_indexes),
        "publication_overrides_unmatched": unmatched,
    }


def arxiv_link_key(row: Dict[str, Any]) -> Optional[Tuple[str, Any]]:
    """Use only the strongest available identity on an enrichment row."""
    openalex_key = normalize_identifier_url(row.get("openalex_url"))
    if openalex_key:
        return "openalex", openalex_key
    doi_key = normalize_doi(row.get("doi"))
    if doi_key:
        return "doi", doi_key
    title_key = normalize_title(row.get("title"))
    year = parse_year(row.get("year"))
    if title_key and year is not None:
        return "title_year", (title_key, year)
    return None


def record_arxiv_keys(record: Dict[str, Any]) -> List[Tuple[str, Any]]:
    keys: List[Tuple[str, Any]] = []
    openalex_key = normalize_identifier_url(record.get("openalex_url"))
    if openalex_key:
        keys.append(("openalex", openalex_key))
    doi_key = normalize_doi(record.get("doi"))
    if doi_key:
        keys.append(("doi", doi_key))
    title_key = normalize_title(record.get("title"))
    year = parse_year(record.get("publication_year") or record.get("year"))
    if title_key and year is not None:
        keys.append(("title_year", (title_key, year)))
    return keys


def normalize_arxiv_id(value: Any) -> str:
    normalized = clean_text(value)
    normalized = re.sub(
        r"^https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/",
        "",
        normalized,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\.pdf$", "", normalized, flags=re.IGNORECASE).casefold()


def arxiv_values_equivalent(left: Any, right: Any) -> bool:
    left_id = normalize_arxiv_id(left)
    right_id = normalize_arxiv_id(right)
    if not left_id or not right_id:
        return False
    return re.sub(r"v\d+$", "", left_id) == re.sub(r"v\d+$", "", right_id)


def merge_arxiv_value(record: Dict[str, Any], field: str, value: str) -> None:
    """Fill missing metadata and retain a conflicting existing known version."""
    existing = clean_text(record.get(field))
    if not value:
        return
    if not existing:
        record[field] = value
    elif arxiv_values_equivalent(existing, value):
        # A versioned identifier is more specific than its unversioned equivalent.
        if field == "arxiv_id" and "v" not in existing.casefold() and re.search(
            r"v\d+$", value, flags=re.IGNORECASE
        ):
            record[field] = value


def arxiv_enrichment_is_compatible(
    record: Dict[str, Any], arxiv_id: str, arxiv_url: str
) -> bool:
    existing = clean_text(record.get("arxiv_id")) or clean_text(
        record.get("arxiv_url")
    )
    incoming = arxiv_id or arxiv_url
    return not existing or arxiv_values_equivalent(existing, incoming)


def apply_paper_arxiv_links(
    records: Sequence[Dict[str, Any]],
    rows: Sequence[Dict[str, str]],
) -> Dict[str, int]:
    """Apply confirmed rows from the partial enrichment table conservatively."""
    linked_rows = [
        row
        for row in rows
        if clean_text(row.get("match_status")).casefold() == "linked_to_arxiv"
    ]
    by_key: Dict[Tuple[str, Any], List[Tuple[int, Dict[str, str]]]] = {}
    for index, row in enumerate(linked_rows):
        key = arxiv_link_key(row)
        has_arxiv_value = clean_text(row.get("arxiv_id")) or clean_text(
            row.get("arxiv_url")
        )
        if key is not None and has_arxiv_value:
            by_key.setdefault(key, []).append((index, row))
    matched_indexes = set()
    applied_indexes = set()
    for record in records:
        matches = next(
            (by_key[key] for key in record_arxiv_keys(record) if key in by_key),
            [],
        )
        if not matches:
            continue
        for row_index, row in matches:
            matched_indexes.add(row_index)
            arxiv_id = clean_text(row.get("arxiv_id"))
            arxiv_url = clean_text(row.get("arxiv_url"))
            if arxiv_id and not arxiv_url:
                arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
            if not arxiv_enrichment_is_compatible(record, arxiv_id, arxiv_url):
                continue
            applied_indexes.add(row_index)
            merge_arxiv_value(record, "arxiv_id", arxiv_id)
            merge_arxiv_value(record, "arxiv_url", arxiv_url)
            if not clean_text(record.get("arxiv_year")):
                record["arxiv_year"] = parse_year(row.get("arxiv_year"))
            record["has_arxiv_version"] = bool(
                clean_text(record.get("arxiv_id"))
                or clean_text(record.get("arxiv_url"))
            )
    return {
        "arxiv_enrichment_rows_loaded": len(rows),
        "linked_to_arxiv_rows_available": len(linked_rows),
        "arxiv_links_applied": len(applied_indexes),
        "unmatched_linked_to_arxiv_rows": len(linked_rows) - len(matched_indexes),
    }


def apply_institution_author_overrides(
    records: Sequence[Dict[str, Any]],
    overrides: Sequence[Dict[str, Any]],
) -> Tuple[int, List[Dict[str, Any]]]:
    """Replace institution authors on exact normalized manual matches."""
    applied_override_indexes = set()
    for record in records:
        record_title = normalize_title(record.get("title"))
        record_year = parse_year(
            record.get("publication_year") or record.get("year")
        )
        record_institution = normalize_institution_name(record.get("institution"))
        for index, override in enumerate(overrides):
            if normalize_title(override.get("title")) != record_title:
                continue
            override_year = override.get("year")
            if override_year is not None and override_year != record_year:
                continue
            if (
                normalize_institution_name(override.get("institution"))
                != record_institution
            ):
                continue
            record["institution_authors"] = list(override["authors"])
            append_record_note(
                record,
                "manual institution-author override applied",
            )
            append_record_note(record, override.get("notes", ""))
            applied_override_indexes.add(index)

    unmatched = [
        override
        for index, override in enumerate(overrides)
        if index not in applied_override_indexes
    ]
    return len(applied_override_indexes), unmatched


def record_id(openalex_id: str, institution_key: Tuple[Any, ...]) -> str:
    identity = "|".join([openalex_id, *(str(value) for value in institution_key)])
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return f"openalex-candidate-{digest}"


def preferred_value(row: Dict[str, str], resolved_column: str, original_column: str) -> str:
    return clean_text(row.get(resolved_column)) or clean_text(row.get(original_column))


def preferred_coordinates(
    row: Dict[str, str],
) -> Tuple[Optional[float], Optional[float], str, str]:
    """Choose a complete valid coordinate pair without mixing resolution sources."""
    pairs = (
        (
            clean_text(row.get("resolved_latitude")),
            clean_text(row.get("resolved_longitude")),
            "resolved",
        ),
        (
            clean_text(row.get("latitude")),
            clean_text(row.get("longitude")),
            "original",
        ),
    )
    has_complete_pair = False
    for latitude_text, longitude_text, source in pairs:
        if not latitude_text or not longitude_text:
            continue
        has_complete_pair = True
        latitude = parse_coordinate(latitude_text, -90.0, 90.0)
        longitude = parse_coordinate(longitude_text, -180.0, 180.0)
        if latitude is not None and longitude is not None:
            return latitude, longitude, source, ""
    failure = "invalid" if has_complete_pair else "missing"
    return None, None, "", failure


def has_resolution_metadata(row: Dict[str, str]) -> bool:
    return any(
        column in row
        for column in (
            "resolution_method",
            "resolution_confidence",
            "needs_review",
            "resolution_notes",
        )
    )


def group_map_records(
    paper_rows: Sequence[Dict[str, str]],
    affiliation_rows: Sequence[Dict[str, str]],
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    papers_by_id = {}
    for paper in paper_rows:
        openalex_id = clean_text(paper.get("openalex_id"))
        if openalex_id and openalex_id not in papers_by_id:
            papers_by_id[openalex_id] = paper

    legacy_authors = fallback_authors_by_paper(affiliation_rows)
    authors_by_paper = {
        openalex_id: (
            parse_ordered_authors(paper.get("authors_ordered"))
            or legacy_authors.get(openalex_id, [])
        )
        for openalex_id, paper in papers_by_id.items()
    }

    institution_author_entries: Dict[
        Tuple[str, Tuple[str, str]],
        Dict[str, Tuple[int, str]],
    ] = {}
    unresolved_institution_authors = set()
    for affiliation in affiliation_rows:
        openalex_id = clean_text(affiliation.get("openalex_id"))
        institution = preferred_value(
            affiliation, "resolved_institution_name", "institution_name"
        )
        identity = institution_match_key(affiliation, institution)
        author_key = (openalex_id, identity)
        author_entry = institution_author_entry(
            affiliation,
            authors_by_paper.get(openalex_id, []),
        )
        if identity[0] == "unresolved" or author_entry is None:
            unresolved_institution_authors.add(author_key)
            continue
        author_order, author_name, author_identity = author_entry
        institution_author_entries.setdefault(author_key, {}).setdefault(
            author_identity,
            (author_order, author_name),
        )

    grouped: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    missing_coordinates = 0
    invalid_coordinates = 0
    unmatched_papers = 0
    skipped_record_keys = set()

    for affiliation in affiliation_rows:
        institution = preferred_value(
            affiliation, "resolved_institution_name", "institution_name"
        )
        city = preferred_value(affiliation, "resolved_city", "city")
        raw_country = preferred_value(
            affiliation, "resolved_country", "country"
        )
        raw_country_code = clean_text(affiliation.get("country_code"))
        normalized_location = normalize_country_region(
            raw_country,
            raw_country_code,
        )
        country = normalized_location["country"]
        country_code = normalized_location["country_code"]
        region = normalized_location["region"]
        region_code = normalized_location["region_code"]
        institution_openalex_id = clean_text(
            affiliation.get("institution_openalex_id")
        )
        institution_identity = institution_match_key(affiliation, institution)
        latitude, longitude, coordinate_source, coordinate_failure = (
            preferred_coordinates(affiliation)
        )
        if latitude is None or longitude is None:
            if coordinate_failure == "missing":
                missing_coordinates += 1
            else:
                invalid_coordinates += 1
            skipped_record_keys.add(
                (
                    clean_text(affiliation.get("openalex_id")),
                    institution,
                    city,
                    country,
                    region,
                )
            )
            continue

        openalex_id = clean_text(affiliation.get("openalex_id"))
        paper = papers_by_id.get(openalex_id)
        if paper is None:
            unmatched_papers += 1
            continue

        institution_key = (
            institution_identity,
            clean_text(city).casefold(),
            clean_text(country).casefold(),
            clean_text(region_code).casefold(),
            latitude,
            longitude,
        )
        group_key = (openalex_id, *institution_key)
        group = grouped.get(group_key)
        if group is None:
            publication_year = parse_year(
                clean_text(paper.get("publication_year")) or paper.get("year")
            )
            venue_name = clean_text(paper.get("venue_name")) or clean_text(
                paper.get("venue")
            )
            primary_url = clean_text(paper.get("primary_url")) or clean_text(
                paper.get("url")
            )
            group = {
                "id": record_id(openalex_id, institution_key),
                "title": clean_text(paper.get("title")),
                "in_scope": paper_is_in_scope(paper),
                # Keep legacy aliases so existing sample/front-end behavior remains valid.
                "year": publication_year,
                "publication_year": publication_year,
                "publication_date": clean_text(paper.get("publication_date")),
                "task": clean_text(paper.get("preliminary_task")) or "uncertain",
                "subtask": clean_text(paper.get("preliminary_subtask")),
                "entry_type": normalize_entry_type(paper),
                "venue": venue_name,
                "venue_name": venue_name,
                "venue_type": clean_text(paper.get("venue_type")),
                "publisher": clean_text(paper.get("publisher")),
                "publication_type": clean_text(paper.get("publication_type")),
                "doi": clean_text(paper.get("doi")),
                "arxiv_id": clean_text(paper.get("arxiv_id")),
                "arxiv_url": clean_text(paper.get("arxiv_url")),
                "arxiv_year": parse_year(paper.get("arxiv_year")),
                "has_arxiv_version": parse_bool(paper.get("has_arxiv_version")),
                "primary_url": primary_url,
                "landing_page_url": clean_text(paper.get("landing_page_url")),
                "openalex_url": clean_text(paper.get("openalex_url")) or openalex_id,
                "is_arxiv_preprint": parse_bool(paper.get("is_arxiv_preprint")),
                "url": primary_url,
                "authors": list(authors_by_paper.get(openalex_id, [])),
                "institution_authors": [],
                "institution_openalex_id": institution_openalex_id,
                "institution": institution,
                "country": country,
                "country_code": country_code,
                "region": region,
                "region_code": region_code,
                "raw_country": normalized_location["raw_country"],
                "raw_country_code": normalized_location["raw_country_code"],
                "city": city,
                "latitude": latitude,
                "longitude": longitude,
                "source_database": clean_text(paper.get("source_database"))
                or "OpenAlex",
                "manual_review": parse_bool(paper.get("manual_review"))
                or parse_bool(affiliation.get("manual_review")),
                "notes": [],
                "_coordinate_sources": set(),
                "_has_resolution_metadata": False,
                "_resolution_notes": [],
                "_institution_author_key": (openalex_id, institution_identity),
                "_institution_record_source": "automatic",
            }
            grouped[group_key] = group

        group["_coordinate_sources"].add(coordinate_source)
        if has_resolution_metadata(affiliation):
            group["_has_resolution_metadata"] = True
            if not group.get("resolution_method"):
                group["resolution_method"] = clean_text(
                    affiliation.get("resolution_method")
                )
            if not group.get("resolution_confidence"):
                group["resolution_confidence"] = clean_text(
                    affiliation.get("resolution_confidence")
                )
            group["needs_review"] = group.get("needs_review", False) or parse_bool(
                affiliation.get("needs_review")
            )
            group["_resolution_notes"].extend(
                split_notes(affiliation.get("resolution_notes"))
            )

        group["manual_review"] = group["manual_review"] or parse_bool(
            affiliation.get("manual_review")
        )
        group["notes"].extend(split_notes(affiliation.get("notes")))
        group["notes"].extend(split_notes(paper.get("notes")))

    records = []
    for group in grouped.values():
        group["notes"] = " | ".join(unique_strings(group["notes"]))
        author_key = group["_institution_author_key"]
        if author_key not in unresolved_institution_authors:
            group["institution_authors"] = [
                author_name
                for _, author_name in sorted(
                    institution_author_entries.get(author_key, {}).values()
                )
            ]
        if group["_has_resolution_metadata"]:
            group["resolution_notes"] = " | ".join(
                unique_strings(group["_resolution_notes"])
            )
        records.append(group)

    counters = {
        "affiliation_rows_skipped_missing_coordinates": missing_coordinates,
        "affiliation_rows_skipped_invalid_coordinates": invalid_coordinates,
        "affiliation_rows_skipped_unmatched_paper": unmatched_papers,
        "map_records_skipped_missing_coordinates": len(skipped_record_keys),
    }
    return records, counters


def apply_institution_record_overrides(
    records: List[Dict[str, Any]],
    overrides: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Apply replace, remove, and add corrections to institution records."""
    replace_groups: Dict[Tuple[str, int], List[Tuple[int, Dict[str, Any]]]] = {}
    add_rows: List[Tuple[int, Dict[str, Any]]] = []
    remove_rows: List[Tuple[int, Dict[str, Any]]] = []
    for index, override in enumerate(overrides):
        key = (normalize_title(override.get("title")), override["year"])
        if override["mode"] == "replace":
            replace_groups.setdefault(key, []).append((index, override))
        elif override["mode"] == "add":
            add_rows.append((index, override))
        else:
            remove_rows.append((index, override))

    def matching_paper_indexes(
        override_rows: Sequence[Tuple[int, Dict[str, Any]]],
    ) -> List[int]:
        title_keys = {
            (normalize_title(row.get("title")), row["year"])
            for _, row in override_rows
        }
        doi_keys = {
            normalize_doi(row.get("doi"))
            for _, row in override_rows
            if normalize_doi(row.get("doi"))
        }
        openalex_keys = {
            normalize_identifier_url(row.get("openalex_url"))
            for _, row in override_rows
            if normalize_identifier_url(row.get("openalex_url"))
        }
        seed_indexes = [
            index
            for index, record in enumerate(records)
            if (
                normalize_title(record.get("title")),
                parse_year(record.get("publication_year") or record.get("year")),
            )
            in title_keys
            or normalize_doi(record.get("doi")) in doi_keys
            or normalize_identifier_url(record.get("openalex_url"))
            in openalex_keys
        ]
        if not seed_indexes:
            return []

        target_doi_keys = doi_keys | {
            normalize_doi(records[index].get("doi"))
            for index in seed_indexes
            if normalize_doi(records[index].get("doi"))
        }
        target_openalex_keys = openalex_keys | {
            normalize_identifier_url(records[index].get("openalex_url"))
            for index in seed_indexes
            if normalize_identifier_url(records[index].get("openalex_url"))
        }
        return [
            index
            for index, record in enumerate(records)
            if (
                normalize_title(record.get("title")),
                parse_year(record.get("publication_year") or record.get("year")),
            )
            in title_keys
            or normalize_doi(record.get("doi")) in target_doi_keys
            or normalize_identifier_url(record.get("openalex_url"))
            in target_openalex_keys
        ]

    def manual_record(
        template: Dict[str, Any],
        override: Dict[str, Any],
    ) -> Dict[str, Any]:
        replacement = copy.deepcopy(template)
        normalized_location = normalize_country_region(
            override.get("country"),
            override.get("country_code"),
            override.get("region"),
        )
        institution = override["institution"]
        city = clean_text(override.get("city"))
        latitude = override["latitude"]
        longitude = override["longitude"]
        location = ", ".join(
            unique_strings(
                [
                    city,
                    normalized_location["region"],
                    normalized_location["country"],
                ]
            )
        )
        institution_identity = (
            "name",
            normalize_institution_name(institution),
        )
        institution_key = (
            institution_identity,
            city.casefold(),
            normalized_location["country"].casefold(),
            normalized_location["region_code"].casefold(),
            latitude,
            longitude,
        )
        paper_identity = clean_text(replacement.get("openalex_url")) or clean_text(
            replacement.get("id")
        )
        replacement.update(
            {
                "id": record_id(paper_identity, institution_key),
                "institution_openalex_id": "",
                "institution": institution,
                "institution_authors": list(override["institution_authors"]),
                "city": city,
                "country": normalized_location["country"],
                "country_code": normalized_location["country_code"],
                "region": normalized_location["region"],
                "region_code": normalized_location["region_code"],
                "raw_country": normalized_location["raw_country"],
                "raw_country_code": normalized_location["raw_country_code"],
                "latitude": latitude,
                "longitude": longitude,
                "location": location,
                "resolution_method": "manual_institution_record_override",
                "_coordinate_sources": {"manual"}
                if latitude is not None and longitude is not None
                else set(),
                "_institution_record_source": "manual_override",
                "_institution_author_key": (
                    paper_identity,
                    institution_identity,
                ),
            }
        )
        append_record_note(
            replacement,
            f"manual institution-record {override['mode']} override applied",
        )
        append_record_note(replacement, override.get("notes", ""))
        return replacement

    applied_indexes = set()
    papers_replaced = 0
    automatic_records_removed = 0
    replacement_records_created = 0
    for (_, year), replacement_rows in replace_groups.items():
        matching_indexes = matching_paper_indexes(replacement_rows)
        if not matching_indexes:
            continue
        matched_records = [records[index] for index in matching_indexes]
        template = matched_records[0]
        automatic_records_removed += sum(
            clean_text(record.get("resolution_method"))
            != "manual_institution_record_override"
            for record in matched_records
        )
        replacement_records: List[Dict[str, Any]] = []
        for override_index, override in replacement_rows:
            replacement_records.append(manual_record(template, override))
            applied_indexes.add(override_index)

        matching_index_set = set(matching_indexes)
        insertion_index = sum(
            index not in matching_index_set
            for index in range(matching_indexes[0])
        )
        remaining_records = [
            record
            for index, record in enumerate(records)
            if index not in matching_index_set
        ]
        records[:] = (
            remaining_records[:insertion_index]
            + replacement_records
            + remaining_records[insertion_index:]
        )
        replacement_indexes = matching_paper_indexes(replacement_rows)
        automatic_survivors = [
            records[index]
            for index in replacement_indexes
            if records[index].get("_institution_record_source") == "automatic"
        ]
        if automatic_survivors:
            raise ExportError(
                "Institution record replacement sanity check failed for "
                f"{replacement_rows[0][1]['title']} ({year}): "
                f"{len(automatic_survivors)} automatic records remain"
            )
        papers_replaced += 1
        replacement_records_created += len(replacement_records)

    for override_index, override in remove_rows:
        matching_indexes = matching_paper_indexes([(override_index, override)])
        if not matching_indexes:
            continue
        institution_key = normalize_institution_name(override["institution"])
        removal_indexes = [
            index
            for index in matching_indexes
            if normalize_institution_name(records[index].get("institution"))
            == institution_key
        ]
        if not removal_indexes:
            continue
        removal_index_set = set(removal_indexes)
        records[:] = [
            record
            for index, record in enumerate(records)
            if index not in removal_index_set
        ]
        applied_indexes.add(override_index)

    for override_index, override in add_rows:
        matching_indexes = matching_paper_indexes([(override_index, override)])
        if not matching_indexes:
            continue
        institution_key = normalize_institution_name(override["institution"])
        if any(
            normalize_institution_name(records[index].get("institution"))
            == institution_key
            for index in matching_indexes
        ):
            applied_indexes.add(override_index)
            continue
        insertion_index = matching_indexes[-1] + 1
        records.insert(
            insertion_index,
            manual_record(records[matching_indexes[0]], override),
        )
        applied_indexes.add(override_index)

    unmatched = [
        {
            "title": override["title"],
            "year": override["year"],
            "mode": override["mode"],
            "institution": override["institution"],
        }
        for index, override in enumerate(overrides)
        if index not in applied_indexes
    ]
    return {
        "institution_record_overrides_loaded": len(overrides),
        "institution_record_override_papers_marked": len(replace_groups),
        "institution_record_override_replace_mode_papers": len(replace_groups),
        "institution_record_override_add_mode_records": len(add_rows),
        "institution_record_override_remove_mode_records": len(remove_rows),
        "institution_record_override_papers_replaced": papers_replaced,
        "institution_record_automatic_records_removed": automatic_records_removed,
        "institution_record_replacements_created": replacement_records_created,
        "institution_record_override_coordinate_missing_records": sum(
            override["mode"] != "remove"
            and (override["latitude"] is None or override["longitude"] is None)
            for override in overrides
        ),
        "institution_record_overrides_unmatched": unmatched,
    }


def build_export(
    paper_rows: Sequence[Dict[str, str]],
    affiliation_rows: Sequence[Dict[str, str]],
    max_records: Optional[int],
    paper_version_overrides: Sequence[Dict[str, str]],
    institution_author_overrides: Sequence[Dict[str, Any]] = (),
    paper_arxiv_links: Sequence[Dict[str, str]] = (),
    publication_overrides: Sequence[Dict[str, Any]] = (),
    institution_record_overrides: Sequence[Dict[str, Any]] = (),
) -> Dict[str, Any]:
    records, counters = group_map_records(paper_rows, affiliation_rows)
    institution_record_override_summary = apply_institution_record_overrides(
        records,
        institution_record_overrides,
    )
    institution_author_overrides_applied, unmatched_author_overrides = (
        apply_institution_author_overrides(
            records,
            institution_author_overrides,
        )
    )
    paper_version_overrides_applied = apply_paper_version_overrides(
        records,
        paper_version_overrides,
    )
    arxiv_enrichment_summary = apply_paper_arxiv_links(records, paper_arxiv_links)
    publication_override_summary = apply_publication_overrides(
        records,
        publication_overrides,
    )
    available_records = len(records)
    if max_records is not None:
        records = records[:max_records]

    resolved_coordinate_records = sum(
        "resolved" in record["_coordinate_sources"] for record in records
    )
    original_coordinate_records = sum(
        "resolved" not in record["_coordinate_sources"]
        and "original" in record["_coordinate_sources"]
        for record in records
    )
    records_needing_review = sum(
        record.get("needs_review") is True for record in records
    )
    for record in records:
        record.pop("_coordinate_sources", None)
        record.pop("_has_resolution_metadata", None)
        record.pop("_resolution_notes", None)
        record.pop("_institution_author_key", None)
        record.pop("_institution_record_source", None)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    summary = {
        "candidate_papers_read": len(paper_rows),
        "affiliation_rows_read": len(affiliation_rows),
        "map_records_available_before_limit": available_records,
        "map_records_exported": len(records),
        "map_records_using_resolved_coordinates": resolved_coordinate_records,
        "map_records_using_original_coordinates": original_coordinate_records,
        "map_records_marked_needs_review": records_needing_review,
        "paper_version_overrides_applied": paper_version_overrides_applied,
        "institution_author_overrides_loaded": len(institution_author_overrides),
        "institution_author_overrides_applied": institution_author_overrides_applied,
        "institution_author_overrides_unmatched": [
            {
                "title": override["title"],
                "year": override["year"],
                "institution": override["institution"],
            }
            for override in unmatched_author_overrides
        ],
        **arxiv_enrichment_summary,
        **publication_override_summary,
        **institution_record_override_summary,
        **counters,
    }
    return {
        "dataset_type": "openalex_candidate_map_data",
        "notice": (
            "Automatically generated OpenAlex candidate data for exploratory local "
            "visualization only. These records are not curated final data."
        ),
        "generated_at": generated_at.replace("+00:00", "Z"),
        "records": records,
        "summary": summary,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary_path.replace(path)
    except OSError as error:
        raise ExportError(f"Could not write {path}: {error}") from error


def print_summary(summary: Dict[str, Any]) -> None:
    print("Export summary:")
    print(f"  Total candidate papers: {summary['total_candidate_papers']}")
    print(f"  In-scope papers: {summary['in_scope_papers']}")
    print(f"  Out-of-scope papers: {summary['out_of_scope_papers']}")
    print(f"  Total affiliation rows: {summary['total_affiliation_rows']}")
    print(f"  In-scope affiliation rows: {summary['in_scope_affiliation_rows']}")
    print(f"  Downstream rows processed: {summary['downstream_rows_processed']}")
    print(f"  Candidate papers read: {summary['candidate_papers_read']}")
    print(f"  Affiliation rows read: {summary['affiliation_rows_read']}")
    print(f"  Map records exported: {summary['map_records_exported']}")
    print(
        "  Map records using resolved coordinates: "
        f"{summary['map_records_using_resolved_coordinates']}"
    )
    print(
        "  Map records using original coordinates: "
        f"{summary['map_records_using_original_coordinates']}"
    )
    print(
        "  Map records skipped because coordinates were missing or invalid: "
        f"{summary['map_records_skipped_missing_coordinates']}"
    )
    print(
        "  Exported records marked needs_review=true: "
        f"{summary['map_records_marked_needs_review']}"
    )
    print(
        "  Paper-version overrides applied: "
        f"{summary['paper_version_overrides_applied']}"
    )
    print(f"  arXiv enrichment rows loaded: {summary['arxiv_enrichment_rows_loaded']}")
    print(
        "  linked_to_arxiv rows available: "
        f"{summary['linked_to_arxiv_rows_available']}"
    )
    print(f"  arXiv links applied: {summary['arxiv_links_applied']}")
    print(
        "  Unmatched linked_to_arxiv rows: "
        f"{summary['unmatched_linked_to_arxiv_rows']}"
    )
    print(
        "  Publication overrides loaded: "
        f"{summary['publication_overrides_loaded']}"
    )
    print(
        "  Publication overrides applied: "
        f"{summary['publication_overrides_applied']}"
    )
    print(
        "  Unmatched publication overrides: "
        f"{len(summary['publication_overrides_unmatched'])}"
    )
    for override in summary["publication_overrides_unmatched"]:
        print(
            "  Unmatched publication override: "
            f"{override['title']} ({override['match_year'] or 'any year'})"
        )
    print(
        "  Institution-author overrides loaded: "
        f"{summary['institution_author_overrides_loaded']}"
    )
    print(
        "  Institution-author overrides applied: "
        f"{summary['institution_author_overrides_applied']}"
    )
    for override in summary["institution_author_overrides_unmatched"]:
        print(
            "  Unmatched institution-author override: "
            f"{override['title']} ({override['year'] or 'any year'}) / "
            f"{override['institution']}"
        )
    print(
        "  Institution record overrides loaded: "
        f"{summary['institution_record_overrides_loaded']}"
    )
    print(
        "  Replace-mode papers: "
        f"{summary['institution_record_override_replace_mode_papers']}"
    )
    print(
        "  Add-mode records: "
        f"{summary['institution_record_override_add_mode_records']}"
    )
    print(
        "  Remove-mode records: "
        f"{summary['institution_record_override_remove_mode_records']}"
    )
    print(
        "  Automatic institution records removed by replacement: "
        f"{summary['institution_record_automatic_records_removed']}"
    )
    print(
        "  Replacement institution records created: "
        f"{summary['institution_record_replacements_created']}"
    )
    print(
        "  Coordinate-missing override records: "
        f"{summary['institution_record_override_coordinate_missing_records']}"
    )
    print(
        "  Unmatched institution record overrides: "
        f"{len(summary['institution_record_overrides_unmatched'])}"
    )
    for override in summary["institution_record_overrides_unmatched"]:
        print(
            "  Unmatched institution record override: "
            f"{override['title']} ({override['year']}) / "
            f"{override['institution']}"
        )
    print(
        "  Rows skipped because coordinates were missing: "
        f"{summary['affiliation_rows_skipped_missing_coordinates']}"
    )
    if summary["affiliation_rows_skipped_invalid_coordinates"]:
        print(
            "  Rows skipped because coordinates were invalid: "
            f"{summary['affiliation_rows_skipped_invalid_coordinates']}"
        )
    if summary["affiliation_rows_skipped_unmatched_paper"]:
        print(
            "  Rows skipped because no matching paper was found: "
            f"{summary['affiliation_rows_skipped_unmatched_paper']}"
        )


def run(args: argparse.Namespace) -> int:
    try:
        all_paper_rows = read_csv(args.papers_csv, PAPER_REQUIRED_COLUMNS)
        all_affiliation_rows = read_csv(
            args.affiliations_csv, AFFILIATION_REQUIRED_COLUMNS
        )
        paper_rows, affiliation_rows, scope_counts = select_scope_rows(
            all_paper_rows,
            all_affiliation_rows,
            args.include_out_of_scope,
        )
        paper_version_overrides = read_paper_version_overrides()
        paper_arxiv_links = read_paper_arxiv_links()
        publication_overrides = read_publication_overrides()
        institution_author_overrides = load_institution_author_overrides()
        institution_record_overrides = load_institution_record_overrides()
        payload = build_export(
            paper_rows,
            affiliation_rows,
            args.max_records,
            paper_version_overrides,
            institution_author_overrides,
            paper_arxiv_links,
            publication_overrides,
            institution_record_overrides,
        )
        payload["summary"].update(scope_counts)
    except ExportError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("DRY RUN: no files were written.")
        print(f"Would write: {args.output}")
    else:
        try:
            write_json(args.output, payload)
        except ExportError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print(f"Wrote exploratory candidate map data: {args.output}")

    print_summary(payload["summary"])
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
