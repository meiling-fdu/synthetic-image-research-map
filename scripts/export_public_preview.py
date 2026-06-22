#!/usr/bin/env python3
"""Filter local candidate map data into a commit-safe public preview.

The public preview remains uncurated candidate metadata. This script only reads
an existing map export, calls no APIs, and never writes to data/manual/.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    from .country_normalization import normalize_country_region
    from .export_candidate_map_data import (
        ExportError,
        apply_paper_abstracts,
        apply_institution_author_overrides,
        apply_institution_record_overrides,
        load_institution_author_overrides,
        load_institution_record_overrides,
        read_paper_abstracts,
    )
except ImportError:  # Direct execution from the scripts directory.
    from country_normalization import normalize_country_region
    from export_candidate_map_data import (
        ExportError,
        apply_paper_abstracts,
        apply_institution_author_overrides,
        apply_institution_record_overrides,
        load_institution_author_overrides,
        load_institution_record_overrides,
        read_paper_abstracts,
    )


DEFAULT_INPUT = Path("web/data/openalex_candidate_map_data.json")
DEFAULT_OUTPUT = Path("web/data/public_preview_map_data.json")
DEFAULT_PAPER_VERSION_OVERRIDES = Path("data/manual/paper_version_overrides.csv")
DEFAULT_PAPER_ARXIV_LINKS = Path("data/manual/paper_arxiv_links.csv")
DEFAULT_PUBLICATION_OVERRIDES = Path("data/manual/publication_overrides.csv")
DEFAULT_MAX_RECORDS = 200
DEFAULT_MIN_CONFIDENCE = "medium"
ALLOWED_PUBLIC_TASKS = {
    "detection",
    "source_attribution",
    "detection_and_source_attribution",
}

CONFIDENCE_RANK = {
    "unresolved": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}
MISSING_INSTITUTION_VALUES = {"", "none", "null", "unknown", "n/a", "na"}
PUBLIC_FIELDS = (
    "id",
    "title",
    "in_scope",
    "year",
    "publication_year",
    "publication_date",
    "task",
    "subtask",
    "entry_type",
    "venue",
    "venue_name",
    "venue_type",
    "publisher",
    "publication_type",
    "abstract",
    "abstract_source",
    "ai_summary",
    "doi",
    "arxiv_id",
    "arxiv_url",
    "arxiv_year",
    "has_arxiv_version",
    "paper_url",
    "primary_url",
    "landing_page_url",
    "openalex_url",
    "is_arxiv_preprint",
    "url",
    "authors",
    "institution_authors",
    "institution",
    "country",
    "country_code",
    "region",
    "region_code",
    "raw_country",
    "raw_country_code",
    "city",
    "latitude",
    "longitude",
    "source_database",
    "resolution_method",
    "resolution_confidence",
    "needs_review",
    "notes",
)
PUBLIC_METADATA = {
    "dataset_type": "uncurated_public_preview",
    "generated_from": "OpenAlex candidate metadata",
    "warning": (
        "Automatically generated candidate metadata; not a manually curated "
        "bibliography."
    ),
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


class PreviewExportError(RuntimeError):
    """An expected input or output error that should not show a traceback."""


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a filtered, field-limited public preview from local "
            "OpenAlex candidate map data."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Map-ready candidate JSON (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Public preview JSON (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--max-records",
        type=positive_int,
        default=DEFAULT_MAX_RECORDS,
        help=f"Maximum records to publish (default: {DEFAULT_MAX_RECORDS}).",
    )
    parser.add_argument(
        "--min-confidence",
        choices=tuple(CONFIDENCE_RANK),
        default=DEFAULT_MIN_CONFIDENCE,
        help=(
            "Minimum institution resolution confidence "
            f"(default: {DEFAULT_MIN_CONFIDENCE})."
        ),
    )
    parser.add_argument(
        "--include-needs-review",
        action="store_true",
        help="Include records marked needs_review=true (excluded by default).",
    )
    parser.add_argument(
        "--include-out-of-scope",
        action="store_true",
        help="Include map records not marked in_scope=true for debugging.",
    )
    parser.add_argument(
        "--include-uncertain",
        action="store_true",
        help="Include records labeled uncertain for debugging (excluded by default).",
    )
    parser.add_argument(
        "--include-missing-location",
        action="store_true",
        help=(
            "Include records without a valid institution or coordinate pair for "
            "debugging (excluded by default)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print filtering results without writing the public JSON file.",
    )
    return parser.parse_args(argv)


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().casefold() in {"1", "true", "yes", "y"}


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


def parse_year(value: Any) -> Optional[int]:
    cleaned = clean_text(value)
    if not cleaned:
        return None
    try:
        year = int(cleaned)
    except ValueError:
        return None
    return year if 0 < year < 10000 else None


def institution_name(record: Dict[str, Any]) -> str:
    return clean_text(
        record.get("institution") or record.get("institution_name")
    )


def has_valid_institution(record: Dict[str, Any]) -> bool:
    return institution_name(record).casefold() not in MISSING_INSTITUTION_VALUES


def has_usable_coordinates(record: Dict[str, Any]) -> bool:
    try:
        latitude = float(record.get("latitude"))
        longitude = float(record.get("longitude"))
    except (TypeError, ValueError):
        return False
    return (
        math.isfinite(latitude)
        and math.isfinite(longitude)
        and -90 <= latitude <= 90
        and -180 <= longitude <= 180
    )


def normalize_confidence(value: Any) -> str:
    confidence = str(value or "").strip().casefold()
    return confidence if confidence in CONFIDENCE_RANK else "unresolved"


def read_paper_version_overrides(
    path: Path = DEFAULT_PAPER_VERSION_OVERRIDES,
) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = set(reader.fieldnames or [])
            missing = sorted(PAPER_VERSION_OVERRIDE_COLUMNS - fieldnames)
            if missing:
                raise PreviewExportError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise PreviewExportError(f"Could not read {path}: {error}") from error


def read_paper_arxiv_links(
    path: Path = DEFAULT_PAPER_ARXIV_LINKS,
) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(PAPER_ARXIV_LINK_COLUMNS - set(reader.fieldnames or []))
            if missing:
                raise PreviewExportError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise PreviewExportError(f"Could not read {path}: {error}") from error


def read_publication_overrides(
    path: Path = DEFAULT_PUBLICATION_OVERRIDES,
) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(
                PUBLICATION_OVERRIDE_COLUMNS - set(reader.fieldnames or [])
            )
            if missing:
                raise PreviewExportError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            rows = [dict(row) for row in reader]
    except OSError as error:
        raise PreviewExportError(f"Could not read {path}: {error}") from error

    overrides = []
    for row_number, row in enumerate(rows, start=2):
        title = clean_text(row.get("title"))
        match_year_text = clean_text(row.get("match_year"))
        formal_year = parse_year(row.get("formal_year"))
        match_year = parse_year(match_year_text)
        if not title or formal_year is None:
            raise PreviewExportError(
                f"{path} row {row_number} requires title and a valid formal_year"
            )
        if match_year_text and match_year is None:
            raise PreviewExportError(
                f"{path} row {row_number} has an invalid match_year"
            )
        overrides.append(
            {
                **row,
                "title": title,
                "match_year": match_year,
                "formal_year": formal_year,
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


def append_record_note(record: Dict[str, Any], note: Any) -> None:
    cleaned_note = clean_text(note)
    if not cleaned_note:
        return
    existing = [
        clean_text(part)
        for part in clean_text(record.get("notes")).split("|")
        if clean_text(part)
    ]
    existing.append(cleaned_note)
    unique = []
    seen = set()
    for part in existing:
        if part not in seen:
            seen.add(part)
            unique.append(part)
    record["notes"] = " | ".join(unique)


def apply_paper_version_overrides(
    records: Sequence[Dict[str, Any]],
    overrides: Sequence[Dict[str, str]],
) -> int:
    """Attach manually confirmed arXiv-version metadata before public filtering."""
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
        append_record_note(record, override.get("notes"))
        applied += 1
    return applied


def apply_publication_overrides(
    records: Sequence[Dict[str, Any]],
    overrides: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Correct formal publication display fields before public filtering."""
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
            append_record_note(record, override.get("notes"))
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
    existing = clean_text(record.get(field))
    if not value:
        return
    if not existing:
        record[field] = value
    elif arxiv_values_equivalent(existing, value):
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


def read_candidate_records(path: Path) -> List[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise PreviewExportError(f"Could not read {path}: {error}") from error

    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise PreviewExportError(f"{path} must contain a JSON object with a records list")
    if not all(isinstance(record, dict) for record in payload["records"]):
        raise PreviewExportError(f"{path} contains a non-object map record")
    return payload["records"]


def build_preview(
    records: Sequence[Dict[str, Any]],
    max_records: int,
    min_confidence: str,
    include_needs_review: bool,
    paper_version_overrides: Sequence[Dict[str, str]],
    include_out_of_scope: bool = False,
    include_uncertain: bool = False,
    include_missing_location: bool = False,
    paper_arxiv_links: Sequence[Dict[str, str]] = (),
    publication_overrides: Sequence[Dict[str, Any]] = (),
    institution_record_overrides: Sequence[Dict[str, Any]] = (),
    institution_author_overrides: Sequence[Dict[str, Any]] = (),
    paper_abstracts: Sequence[Dict[str, Any]] = (),
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    records = [dict(record) for record in records]
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
    abstract_summary = apply_paper_abstracts(records, paper_abstracts)
    minimum_rank = CONFIDENCE_RANK[min_confidence]
    selected = []
    below_confidence = 0
    excluded_needs_review = 0
    excluded_out_of_scope = 0
    excluded_task = 0
    missing_institution = 0
    missing_coordinates = 0
    excluded_missing_location = 0

    for record in records:
        in_scope = parse_bool(record.get("in_scope"))
        if not in_scope and not include_out_of_scope:
            excluded_out_of_scope += 1
            continue

        task = str(record.get("preliminary_task") or record.get("task") or "").strip()
        task_is_allowed = task in ALLOWED_PUBLIC_TASKS
        task_is_debug_uncertain = include_uncertain and task == "uncertain"
        if not task_is_allowed and not task_is_debug_uncertain:
            excluded_task += 1
            continue

        record_missing_institution = not has_valid_institution(record)
        record_missing_coordinates = not has_usable_coordinates(record)
        missing_institution += int(record_missing_institution)
        missing_coordinates += int(record_missing_coordinates)
        if (
            record_missing_institution or record_missing_coordinates
        ) and not include_missing_location:
            excluded_missing_location += 1
            continue

        confidence = normalize_confidence(record.get("resolution_confidence"))
        if CONFIDENCE_RANK[confidence] < minimum_rank:
            below_confidence += 1
            continue

        needs_review = parse_bool(record.get("needs_review"))
        if needs_review and not include_needs_review:
            excluded_needs_review += 1
            continue

        # Whitelisting prevents source-only or future internal fields from being
        # published accidentally when the local candidate schema expands.
        public_record = {
            field: record.get(field) for field in PUBLIC_FIELDS if field in record
        }
        public_record["entry_type"] = normalize_entry_type(record)
        public_record["institution"] = institution_name(record)
        public_record.update(
            normalize_country_region(
                record.get("country"),
                record.get("country_code"),
                record.get("region"),
                record.get("region_code"),
                record.get("raw_country") if "raw_country" in record else None,
                (
                    record.get("raw_country_code")
                    if "raw_country_code" in record
                    else None
                ),
            )
        )
        public_record["resolution_confidence"] = confidence
        public_record["needs_review"] = needs_review
        public_record["in_scope"] = in_scope
        selected.append(public_record)

    eligible_records = len(selected)
    selected = selected[:max_records]
    summary = {
        "candidate_records_read": len(records),
        "records_excluded_out_of_scope": excluded_out_of_scope,
        "records_excluded_task": excluded_task,
        "records_missing_institution": missing_institution,
        "records_missing_coordinates": missing_coordinates,
        "records_excluded_missing_location": excluded_missing_location,
        "records_excluded_below_confidence": below_confidence,
        "records_excluded_needs_review": excluded_needs_review,
        "records_eligible_before_limit": eligible_records,
        "records_exported": len(selected),
        "exported_records_with_abstract": sum(
            bool(clean_text(record.get("abstract"))) for record in selected
        ),
        "paper_version_overrides_applied": paper_version_overrides_applied,
        **arxiv_enrichment_summary,
        **publication_override_summary,
        **abstract_summary,
        **institution_record_override_summary,
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
    }
    return {"metadata": dict(PUBLIC_METADATA), "records": selected}, summary


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary_path.replace(path)
    except OSError as error:
        raise PreviewExportError(f"Could not write {path}: {error}") from error


def print_summary(summary: Dict[str, Any], output: Path, dry_run: bool) -> None:
    print("Public preview export summary:")
    print(f"  Candidate records read: {summary['candidate_records_read']}")
    print(
        "  Records excluded as out of scope: "
        f"{summary['records_excluded_out_of_scope']}"
    )
    print(
        "  Records excluded by task label: "
        f"{summary['records_excluded_task']}"
    )
    print(
        "  Scoped records missing an institution: "
        f"{summary['records_missing_institution']}"
    )
    print(
        "  Scoped records missing usable coordinates: "
        f"{summary['records_missing_coordinates']}"
    )
    print(
        "  Records excluded for missing institution/location: "
        f"{summary['records_excluded_missing_location']}"
    )
    print(
        "  Records excluded below confidence threshold: "
        f"{summary['records_excluded_below_confidence']}"
    )
    print(
        "  Records excluded because they need review: "
        f"{summary['records_excluded_needs_review']}"
    )
    print(
        "  Records eligible before maximum: "
        f"{summary['records_eligible_before_limit']}"
    )
    print(f"  Records exported: {summary['records_exported']}")
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
        "  Manual abstract rows loaded: "
        f"{summary['paper_abstract_rows_loaded']}"
    )
    print(
        "  Exported records with non-empty abstract before preview filtering: "
        f"{summary['records_with_abstract']}"
    )
    print(
        "  Public preview records with non-empty abstract: "
        f"{summary['exported_records_with_abstract']}"
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
        "  Institution-author overrides loaded: "
        f"{summary['institution_author_overrides_loaded']}"
    )
    print(
        "  Institution-author overrides applied: "
        f"{summary['institution_author_overrides_applied']}"
    )
    print(f"  Downstream rows processed: {summary['records_exported']}")
    print(f"  Output: {output}{' (not written; dry run)' if dry_run else ''}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        records = read_candidate_records(args.input)
        paper_version_overrides = read_paper_version_overrides()
        paper_arxiv_links = read_paper_arxiv_links()
        publication_overrides = read_publication_overrides()
        paper_abstracts = read_paper_abstracts()
        institution_record_overrides = load_institution_record_overrides()
        institution_author_overrides = load_institution_author_overrides()
        payload, summary = build_preview(
            records,
            args.max_records,
            args.min_confidence,
            args.include_needs_review,
            paper_version_overrides,
            args.include_out_of_scope,
            args.include_uncertain,
            args.include_missing_location,
            paper_arxiv_links,
            publication_overrides,
            institution_record_overrides,
            institution_author_overrides,
            paper_abstracts,
        )
        if not args.dry_run:
            write_json(args.output, payload)
        print_summary(summary, args.output, args.dry_run)
    except (PreviewExportError, ExportError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
