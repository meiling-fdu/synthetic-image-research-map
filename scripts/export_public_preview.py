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
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    from .curated_export import (
        DEFAULT_CURATED_MAPPINGS_PATH,
        DEFAULT_CURATED_PAPERS_PATH,
        DEFAULT_INSTITUTION_RESOLUTION_CACHE_PATH,
        DEFAULT_INSTITUTION_ALIASES_PATH,
        DEFAULT_LOCATION_REVIEW_PATH,
        CuratedExportError,
        enforce_affiliation_source_precedence,
        integrate_curated_records,
        load_curated_mappings,
        load_curated_papers,
        load_institution_resolution_cache,
        load_institution_aliases,
        load_location_review_queue,
        save_location_review_queue,
        stable_institution_id,
    )
    from .publication_types import normalize_publication_type
    from .curated_locations import (
        DEFAULT_INSTITUTION_LOCATIONS_PATH,
        load_confirmed_locations,
    )
    from .curated_institutions import (
        DEFAULT_AUDIT_PATH,
        DEFAULT_INSTITUTIONS_PATH,
        load_institutions,
    )
    from .country_normalization import normalize_country_region, public_location_display
    from .paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        build_active_exclusion_index,
        read_exclusion_rows,
        record_is_excluded,
    )
    from .paper_version_merges import (
        DEFAULT_PAPER_VERSION_MERGES_PATH,
        PaperVersionMergeError,
        apply_confirmed_version_merges,
        read_paper_version_merges,
    )
    from .name_matching import (
        canonical_name_key,
        names_match,
        unique_matching_name,
    )
    from .export_candidate_map_data import (
        ExportError,
        apply_paper_abstracts,
        apply_institution_author_overrides,
        apply_institution_record_overrides,
        apply_paper_arxiv_links,
        apply_publication_overrides,
        index_papers_by_identity,
        load_institution_author_overrides,
        load_institution_record_overrides,
        match_row_by_identity,
        normalize_export_task_labels,
        parse_ordered_authors,
        paper_identity_keys,
        read_all_candidate_papers,
        read_key_paper_affiliation_enrichment,
        read_local_openalex_abstracts,
        read_paper_abstracts,
    )
except ImportError:  # Direct execution from the scripts directory.
    from curated_export import (
        DEFAULT_CURATED_MAPPINGS_PATH,
        DEFAULT_CURATED_PAPERS_PATH,
        DEFAULT_INSTITUTION_RESOLUTION_CACHE_PATH,
        DEFAULT_INSTITUTION_ALIASES_PATH,
        DEFAULT_LOCATION_REVIEW_PATH,
        CuratedExportError,
        enforce_affiliation_source_precedence,
        integrate_curated_records,
        load_curated_mappings,
        load_curated_papers,
        load_institution_resolution_cache,
        load_institution_aliases,
        load_location_review_queue,
        save_location_review_queue,
        stable_institution_id,
    )
    from publication_types import normalize_publication_type
    from curated_locations import (
        DEFAULT_INSTITUTION_LOCATIONS_PATH,
        load_confirmed_locations,
    )
    from curated_institutions import (
        DEFAULT_AUDIT_PATH,
        DEFAULT_INSTITUTIONS_PATH,
        load_institutions,
    )
    from country_normalization import normalize_country_region, public_location_display
    from paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        build_active_exclusion_index,
        read_exclusion_rows,
        record_is_excluded,
    )
    from paper_version_merges import (
        DEFAULT_PAPER_VERSION_MERGES_PATH,
        PaperVersionMergeError,
        apply_confirmed_version_merges,
        read_paper_version_merges,
    )
    from name_matching import (
        canonical_name_key,
        names_match,
        unique_matching_name,
    )
    from export_candidate_map_data import (
        ExportError,
        apply_paper_abstracts,
        apply_institution_author_overrides,
        apply_institution_record_overrides,
        apply_paper_arxiv_links,
        apply_publication_overrides,
        index_papers_by_identity,
        load_institution_author_overrides,
        load_institution_record_overrides,
        match_row_by_identity,
        normalize_export_task_labels,
        parse_ordered_authors,
        paper_identity_keys,
        read_all_candidate_papers,
        read_key_paper_affiliation_enrichment,
        read_local_openalex_abstracts,
        read_paper_abstracts,
    )


DEFAULT_INPUT = Path("web/data/openalex_candidate_map_data.json")
DEFAULT_OUTPUT = Path("web/data/public_preview_map_data.json")
DEFAULT_PAPER_OUTPUT = Path("web/data/public_preview_papers.json")
DEFAULT_CANDIDATE_PAPERS = Path("data/processed/openalex_candidate_papers_in_scope.csv")
DEFAULT_ALL_CANDIDATE_PAPERS = Path("data/processed/openalex_candidate_papers.csv")
DEFAULT_AFFILIATIONS = Path("data/processed/openalex_candidate_affiliations.csv")
DEFAULT_EXPORT_DIAGNOSTICS = Path("data/manual/key_paper_export_diagnostics.csv")
DEFAULT_PAPER_VERSION_OVERRIDES = Path("data/manual/paper_version_overrides.csv")
DEFAULT_PAPER_ARXIV_LINKS = Path("data/manual/paper_arxiv_links.csv")
DEFAULT_PUBLICATION_OVERRIDES = Path("data/manual/publication_overrides.csv")
DEFAULT_KEY_PAPERS = Path("data/manual/key_papers.csv")
DEFAULT_PAPER_EXCLUSIONS = DEFAULT_EXCLUSIONS_PATH
DEFAULT_REVIEW_DECISIONS = (
    Path("data/curated/review_decisions.csv")
)
DEFAULT_CURATED_ARXIV_LINKS = Path("data/curated/paper_arxiv_links.csv")
DEFAULT_INSTITUTION_HIERARCHY = Path("data/curated/institution_hierarchy.csv")
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
    "authors_text",
    "institution_authors",
    "institution",
    "country",
    "country_code",
    "region",
    "region_code",
    "raw_country",
    "raw_country_code",
    "city",
    "location_display",
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
PAPER_PUBLIC_METADATA = {
    "dataset_type": "uncurated_public_preview_papers",
    "generated_from": "OpenAlex candidate metadata and local manual review caches",
    "warning": (
        "Automatically generated paper-level candidate metadata. Papers without "
        "usable institution coordinates are included for coverage/search but do "
        "not produce map markers."
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
KEY_PAPER_COLUMNS = {
    "title",
    "year",
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
        "--paper-output",
        type=Path,
        default=DEFAULT_PAPER_OUTPUT,
        help=f"Paper-level public preview JSON (default: {DEFAULT_PAPER_OUTPUT}).",
    )
    parser.add_argument(
        "--max-map-records",
        "--max-records",
        dest="max_records",
        type=positive_int,
        default=None,
        help=(
            "Maximum map records to publish (default: no maximum; "
            "--max-records is an alias)."
        ),
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
    parser.add_argument(
        "--preserve-existing",
        action="store_true",
        help=(
            "Union the existing public outputs into a no-search refresh so a "
            "partial local candidate snapshot cannot shrink published coverage."
        ),
    )
    parser.add_argument(
        "--paper-exclusions",
        type=Path,
        default=DEFAULT_PAPER_EXCLUSIONS,
        help=(
            "Durable paper exclusion CSV "
            f"(default: {DEFAULT_PAPER_EXCLUSIONS})."
        ),
    )
    parser.add_argument(
        "--curated-papers",
        type=Path,
        default=DEFAULT_CURATED_PAPERS_PATH,
        help=f"Curated paper CSV (default: {DEFAULT_CURATED_PAPERS_PATH}).",
    )
    parser.add_argument(
        "--curated-mappings",
        type=Path,
        default=DEFAULT_CURATED_MAPPINGS_PATH,
        help=(
            "Curated author–institution mapping CSV "
            f"(default: {DEFAULT_CURATED_MAPPINGS_PATH})."
        ),
    )
    parser.add_argument(
        "--paper-version-merges",
        type=Path,
        default=DEFAULT_PAPER_VERSION_MERGES_PATH,
        help=(
            "Confirmed paper-version merge CSV "
            f"(default: {DEFAULT_PAPER_VERSION_MERGES_PATH})."
        ),
    )
    parser.add_argument(
        "--review-decisions",
        type=Path,
        default=DEFAULT_REVIEW_DECISIONS,
        help=(
            "Durable admin review decisions CSV "
            f"(default: {DEFAULT_REVIEW_DECISIONS})."
        ),
    )
    parser.add_argument(
        "--location-review",
        type=Path,
        default=DEFAULT_LOCATION_REVIEW_PATH,
        help=(
            "Curated institution location-review CSV "
            f"(default: {DEFAULT_LOCATION_REVIEW_PATH})."
        ),
    )
    parser.add_argument(
        "--institution-locations",
        type=Path,
        default=DEFAULT_INSTITUTION_LOCATIONS_PATH,
        help=(
            "Confirmed curated institution-location CSV "
            f"(default: {DEFAULT_INSTITUTION_LOCATIONS_PATH})."
        ),
    )
    parser.add_argument(
        "--institution-aliases",
        type=Path,
        default=DEFAULT_INSTITUTION_ALIASES_PATH,
        help=(
            "Curated confirmed institution aliases "
            f"(default: {DEFAULT_INSTITUTION_ALIASES_PATH})."
        ),
    )
    parser.add_argument(
        "--institution-hierarchy",
        type=Path,
        default=DEFAULT_INSTITUTION_HIERARCHY,
        help=(
            "Curated confirmed institution parent/child relationships "
            f"(default: {DEFAULT_INSTITUTION_HIERARCHY})."
        ),
    )
    parser.add_argument(
        "--institutions",
        type=Path,
        default=DEFAULT_INSTITUTIONS_PATH,
        help=f"Canonical institution entities (default: {DEFAULT_INSTITUTIONS_PATH}).",
    )
    parser.add_argument(
        "--institution-audit-log",
        type=Path,
        default=DEFAULT_AUDIT_PATH,
        help=f"Institution merge audit log (default: {DEFAULT_AUDIT_PATH}).",
    )
    parser.add_argument(
        "--institution-resolution-cache",
        type=Path,
        default=DEFAULT_INSTITUTION_RESOLUTION_CACHE_PATH,
        help=(
            "Processed institution-resolution cache used only when no "
            "confirmed curated location exists "
            f"(default: {DEFAULT_INSTITUTION_RESOLUTION_CACHE_PATH})."
        ),
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


def author_display_name(value: Any) -> str:
    """Read an author name from either the legacy string or object schema."""
    if isinstance(value, dict):
        name = clean_text(
            value.get("name") or value.get("display_name") or value.get("author")
        )
    else:
        name = clean_text(value)
    return "" if name.casefold() == "[object object]" else name


def normalized_author_name(value: Any) -> str:
    """Normalize display-order and ``Family, Given`` author names alike."""
    return canonical_name_key(value)


def relaxed_author_name(value: Any) -> str:
    """Ignore middle initials only when matching an existing author roster."""
    tokens = normalized_author_name(value).split()
    if len(tokens) < 3:
        return " ".join(tokens)
    return " ".join(
        token for index, token in enumerate(tokens)
        if index in (0, len(tokens) - 1) or len(token) > 1
    )


def detail_paper_identity(record: Dict[str, Any]) -> Tuple[str, Any]:
    """Group publication versions conservatively for affiliation unioning."""
    doi = normalize_doi(record.get("doi"))
    if doi:
        return ("doi", doi)
    arxiv_id = clean_text(record.get("arxiv_id")).casefold().removeprefix("arxiv:")
    if arxiv_id:
        return ("arxiv", arxiv_id)
    return (
        "title_year",
        (
            normalize_title(record.get("title")),
            parse_year(record.get("publication_year") or record.get("year")),
        ),
    )


def detail_institution_identity(value: Dict[str, Any]) -> str:
    institution_id = clean_text(
        value.get("institution_id") or value.get("canonical_institution_id")
    )
    if institution_id:
        return f"id:{institution_id.casefold()}"
    name = clean_text(
        value.get("canonical_name")
        or value.get("canonical_institution_name")
        or value.get("name")
        or value.get("institution")
        or value.get("institution_name")
    )
    return f"name:{normalize_title(name)}"


def _affiliation_values(record: Dict[str, Any]) -> List[Any]:
    """Normalize legacy scalar/dict affiliations to the current list shape."""
    raw_affiliations = record.get("affiliations")
    if raw_affiliations in (None, "", []):
        raw_affiliations = record.get("author_institution_affiliations")
    if raw_affiliations in (None, ""):
        return []
    if isinstance(raw_affiliations, list):
        return raw_affiliations
    return [raw_affiliations]


def _detail_affiliation(value: Any) -> Optional[Dict[str, Any]]:
    if isinstance(value, str):
        value = {"name": value}
    if not isinstance(value, dict):
        return None
    name = clean_text(
        value.get("name")
        or value.get("canonical_name")
        or value.get("institution")
        or value.get("institution_name")
    )
    if not name:
        return None
    institution_id = clean_text(
        value.get("institution_id") or value.get("canonical_institution_id")
    ) or stable_institution_id(name)
    authors = [
        author_display_name(author)
        for author in value.get("authors", [])
        if author_display_name(author)
    ]
    location = normalize_country_region(
        value.get("country"),
        value.get("country_code"),
        value.get("region"),
        value.get("region_code"),
    )
    country = location["country"]
    country_code = location["country_code"]
    region = location["region"]
    source_names = [
        clean_text(name)
        for name in (
            value.get("source_institution_names")
            if isinstance(value.get("source_institution_names"), list)
            else [value.get("source_institution")]
        )
        if clean_text(name)
    ]
    return {
        "index": parse_year(value.get("index")),
        "name": name,
        "canonical_name": clean_text(value.get("canonical_name")) or name,
        "institution_id": institution_id,
        "institution_type": clean_text(value.get("institution_type")),
        "country": country,
        "country_code": country_code,
        "region": region,
        "location_display": public_location_display(region, country, country_code),
        "authors": authors,
        "mapping_source": _author_mapping_source(
            value.get("mapping_source")
        ),
        "mapping_fallback": value.get("mapping_fallback") is True,
        "source_institution_names": source_names,
    }


def _record_authors(record: Dict[str, Any]) -> List[str]:
    values = record.get("authors") or []
    if not isinstance(values, list):
        values = [values]
    authors = []
    for value in values:
        author = author_display_name(value)
        if not author:
            continue
        # Semicolons are the repository's unambiguous person delimiter. Commas
        # are deliberately preserved because "Family, Given" is also valid.
        authors.extend(
            clean_text(part)
            for part in author.split(";")
            if clean_text(part)
        )
    return authors


def _ordered_export_authors(
    record_authors: Sequence[str],
    mapped_authors: Sequence[str],
) -> List[str]:
    """Keep paper order and use mapped authors only as a fallback roster."""
    ambiguous_author_line = (
        len(record_authors) == 1 and record_authors[0].count(",") >= 2
    )
    ordered = []
    seen = set()
    if not ambiguous_author_line:
        for author in record_authors:
            key = normalized_author_name(author)
            if key and key not in seen:
                ordered.append(author)
                seen.add(key)
        if ordered:
            return ordered

    author_line = (
        clean_text(record_authors[0]).casefold()
        if ambiguous_author_line
        else ""
    )
    positioned = []
    mapped_keys = set()
    for author in mapped_authors:
        key = normalized_author_name(author)
        if not key or key in mapped_keys:
            continue
        mapped_keys.add(key)
        position = author_line.find(clean_text(author).casefold())
        if position >= 0:
            positioned.append((position, author))
    if mapped_keys and len(positioned) == len(mapped_keys):
        return [author for _position, author in sorted(positioned)]
    if record_authors:
        return list(record_authors)
    return [
        author for author in mapped_authors if normalized_author_name(author)
    ]


AUTHOR_MAPPING_SOURCE_PRIORITY = {
    "curated_admin": 1,
    "canonical_author_mapping": 2,
    "raw_affiliation": 3,
    "paper_institution_fallback": 4,
    "unmapped": 99,
}


def _author_mapping_source(
    value: Any,
    default: str = "raw_affiliation",
) -> str:
    source = clean_text(value)
    return source if source in AUTHOR_MAPPING_SOURCE_PRIORITY else default


def add_public_detail_fields(
    paper_records: Sequence[Dict[str, Any]],
    map_records: Sequence[Dict[str, Any]],
) -> None:
    """Export one stable author/affiliation schema to papers and markers.

    Existing confirmed affiliation lists and author mappings take precedence.
    Marker institutions are unioned as paper-level affiliations, but an author
    is only assigned to one when the source record explicitly names that author
    in ``institution_authors``.
    """
    map_record_ids = {id(record) for record in map_records}
    grouped: Dict[Tuple[str, Any], List[Dict[str, Any]]] = defaultdict(list)
    for record in [*paper_records, *map_records]:
        grouped[detail_paper_identity(record)].append(record)

    for records in grouped.values():
        affiliations: List[Dict[str, Any]] = []
        affiliation_by_identity: Dict[str, Dict[str, Any]] = {}
        source_index_identities: Dict[int, Dict[int, str]] = {}
        author_affiliation_identities: Dict[str, List[str]] = defaultdict(list)
        author_mapping_sources: Dict[str, str] = {}
        author_mapping_fallbacks: Dict[str, bool] = {}
        marker_current_identities: Dict[int, str] = {}

        def add_author_mapping(
            author: Any,
            identity: str,
            *,
            source: str,
            fallback: bool = False,
        ) -> None:
            author_key = normalized_author_name(author)
            if not author_key or not identity:
                return
            matched_key = unique_matching_name(
                author,
                list(author_affiliation_identities),
            )
            if matched_key is not None:
                author_key = matched_key
            normalized_source = _author_mapping_source(source)
            incoming_priority = AUTHOR_MAPPING_SOURCE_PRIORITY[normalized_source]
            current_source = author_mapping_sources.get(author_key, "unmapped")
            current_priority = AUTHOR_MAPPING_SOURCE_PRIORITY[current_source]
            if incoming_priority < current_priority:
                author_affiliation_identities[author_key] = []
                author_mapping_sources[author_key] = normalized_source
                author_mapping_fallbacks[author_key] = bool(fallback)
            elif incoming_priority > current_priority:
                return
            else:
                author_mapping_fallbacks[author_key] = (
                    author_mapping_fallbacks.get(author_key, False)
                    or bool(fallback)
                )
            if identity not in author_affiliation_identities[author_key]:
                author_affiliation_identities[author_key].append(identity)

        def add_affiliation(
            raw_affiliation: Any,
            *,
            source_record: Optional[Dict[str, Any]] = None,
        ) -> Optional[str]:
            affiliation = _detail_affiliation(raw_affiliation)
            if affiliation is None:
                return None
            identity = detail_institution_identity(affiliation)
            existing = affiliation_by_identity.get(identity)
            if existing is None:
                affiliation["index"] = len(affiliations) + 1
                affiliations.append(affiliation)
                affiliation_by_identity[identity] = affiliation
                existing = affiliation
            else:
                for field in (
                    "canonical_name", "institution_type", "country", "country_code", "region",
                    "location_display",
                ):
                    if not clean_text(existing.get(field)) and clean_text(
                        affiliation.get(field)
                    ):
                        existing[field] = affiliation[field]
                known_authors = {
                    normalized_author_name(author)
                    for author in existing.get("authors", [])
                }
                for author in affiliation.get("authors", []):
                    if normalized_author_name(author) not in known_authors:
                        existing["authors"].append(author)
                        known_authors.add(normalized_author_name(author))
                existing["source_institution_names"] = list(dict.fromkeys([
                    *existing.get("source_institution_names", []),
                    *affiliation.get("source_institution_names", []),
                ]))
            mapping_source = _author_mapping_source(
                raw_affiliation.get("mapping_source")
                if isinstance(raw_affiliation, dict)
                else None
            )
            mapping_fallback = bool(
                isinstance(raw_affiliation, dict)
                and raw_affiliation.get("mapping_fallback") is True
            )
            for author in affiliation.get("authors", []):
                add_author_mapping(
                    author,
                    identity,
                    source=mapping_source,
                    fallback=mapping_fallback,
                )
            if source_record is not None:
                original_index = parse_year(
                    raw_affiliation.get("index")
                    if isinstance(raw_affiliation, dict)
                    else None
                )
                if original_index is not None:
                    source_index_identities.setdefault(id(source_record), {})[
                        original_index
                    ] = identity
            return identity

        # Prefer already exported/confirmed lists so their numbering remains
        # stable across refreshes. Curated export currently writes the legacy
        # field; the new field is consumed first on subsequent transformations.
        for record in records:
            for raw_affiliation in _affiliation_values(record):
                add_affiliation(raw_affiliation, source_record=record)

        # Preserve paper-level institutions even when no author-level mapping
        # exists. This intentionally does not assign authors.
        for record in records:
            if id(record) not in map_record_ids:
                continue
            current = {
                "name": institution_name(record),
                "canonical_name": clean_text(
                    record.get("canonical_institution_name")
                )
                or institution_name(record),
                "institution_id": clean_text(record.get("institution_id")),
                "country": clean_text(record.get("country")),
                "region": clean_text(record.get("region")),
                "source_institution": clean_text(
                    record.get("source_institution")
                ),
                "source_institution_names": record.get(
                    "source_institution_names", []
                ),
            }
            current_identity = add_affiliation(current)
            if current_identity is None:
                continue
            marker_current_identities[id(record)] = current_identity
            current_affiliation = affiliation_by_identity[current_identity]
            for author in record.get("institution_authors") or []:
                author_name = author_display_name(author)
                author_key = normalized_author_name(author_name)
                if not author_key:
                    continue
                source = (
                    "curated_admin"
                    if clean_text(record.get("source_database")).casefold()
                    == "curated"
                    else "raw_affiliation"
                )
                add_author_mapping(
                    author_name,
                    current_identity,
                    source=source,
                )
                if not any(
                    names_match(existing, author_name)
                    for existing in current_affiliation["authors"]
                ):
                    current_affiliation["authors"].append(author_name)

        # Consume stable and legacy index mappings only after every source record's
        # original index-to-institution relationship is known.
        for record in records:
            source_indices = source_index_identities.get(id(record), {})
            stable_mappings = record.get("author_affiliation_indices")
            canonical_mappings = record.get("canonical_author_mappings")
            legacy_mappings = record.get("author_institution_indices")
            mappings = [
                *[
                    (mapping, "raw_affiliation")
                    for mapping in (
                        stable_mappings
                        if isinstance(stable_mappings, list)
                        else []
                    )
                ],
                *[
                    (mapping, "canonical_author_mapping")
                    for mapping in (
                        canonical_mappings
                        if isinstance(canonical_mappings, list)
                        else []
                    )
                ],
                *[
                    (mapping, "raw_affiliation")
                    for mapping in (
                        legacy_mappings
                        if isinstance(legacy_mappings, list)
                        else []
                    )
                ],
            ]
            for mapping, default_source in mappings:
                if not isinstance(mapping, dict):
                    continue
                author_key = normalized_author_name(
                    mapping.get("author") or mapping.get("name")
                )
                if not author_key:
                    continue
                for raw_index in (
                    mapping.get("indices")
                    or mapping.get("institution_indices")
                    or mapping.get("affiliation_indices")
                    or []
                ):
                    index = parse_year(raw_index)
                    identity = source_indices.get(index or -1)
                    if identity:
                        add_author_mapping(
                            mapping.get("author") or mapping.get("name"),
                            identity,
                            source=_author_mapping_source(
                                mapping.get("source"),
                                default_source,
                            ),
                            fallback=mapping.get("fallback") is True,
                        )

        exported_affiliations = [
            {
                "index": affiliation["index"],
                "name": affiliation["name"],
                "canonical_name": affiliation["canonical_name"],
                "institution_id": affiliation["institution_id"],
                "institution_type": affiliation["institution_type"],
                "country": affiliation["country"],
                "country_code": affiliation["country_code"],
                "region": affiliation["region"],
                "location_display": affiliation["location_display"],
                **(
                    {"source_institution_names": affiliation["source_institution_names"]}
                    if affiliation.get("source_institution_names")
                    else {}
                ),
            }
            for affiliation in affiliations
        ]
        mapped_authors = []
        mapped_author_keys = set()
        for affiliation in affiliations:
            for author in affiliation.get("authors", []):
                author_key = normalized_author_name(author)
                if author_key and author_key not in mapped_author_keys:
                    mapped_authors.append(author)
                    mapped_author_keys.add(author_key)

        for record in records:
            current_identity = marker_current_identities.get(id(record), "")
            current_affiliation = affiliation_by_identity.get(current_identity)
            current_index = (
                current_affiliation.get("index") if current_affiliation else None
            )
            author_objects = []
            legacy_indices = []
            stable_indices = []
            record_authors = _record_authors(record)
            author_names = _ordered_export_authors(
                record_authors, mapped_authors
            )
            ambiguous_legacy_text = (
                len(author_names) == 1
                and author_names[0].count(",") >= 2
            )
            if ambiguous_legacy_text:
                record["authors_text"] = author_names[0]
                author_names = []
            else:
                record.pop("authors_text", None)
            for author in author_names:
                author_key = normalized_author_name(author)
                evidence_key = author_key
                if evidence_key not in author_affiliation_identities:
                    matched_key = unique_matching_name(
                        author,
                        list(author_affiliation_identities),
                    )
                    if matched_key is not None:
                        evidence_key = matched_key
                    else:
                        relaxed_key = relaxed_author_name(author)
                        relaxed_matches = [
                            candidate
                            for candidate in author_affiliation_identities
                            if relaxed_author_name(candidate) == relaxed_key
                        ]
                        if len(relaxed_matches) == 1:
                            evidence_key = relaxed_matches[0]
                indices = sorted(
                    {
                        affiliation_by_identity[identity]["index"]
                        for identity in author_affiliation_identities.get(
                            evidence_key, []
                        )
                        if identity in affiliation_by_identity
                    }
                )
                is_current = bool(
                    current_index is not None
                    and current_index in indices
                )
                author_objects.append(
                    {
                        "name": author,
                        "affiliation_indices": indices,
                        "is_current_marker_author": is_current,
                        "affiliation_source": author_mapping_sources.get(
                            evidence_key, "unmapped"
                        ),
                        "affiliation_fallback": author_mapping_fallbacks.get(
                            evidence_key, False
                        ),
                    }
                )
                stable_indices.append(
                    {
                        "author": author,
                        "indices": indices,
                        "institution_ids": [
                            affiliations[index - 1]["institution_id"]
                            for index in indices
                        ],
                        "source": author_mapping_sources.get(
                            evidence_key, "unmapped"
                        ),
                        "fallback": author_mapping_fallbacks.get(
                            evidence_key, False
                        ),
                    }
                )
                if indices:
                    legacy_indices.append(
                        {
                            "author": author,
                            "institution_indices": indices,
                            "institution_ids": [
                                affiliations[index - 1]["institution_id"]
                                for index in indices
                            ],
                        }
                    )

            record["authors"] = author_objects
            record["affiliations"] = [dict(item) for item in exported_affiliations]
            record["current_institution"] = (
                dict(exported_affiliations[current_index - 1])
                if current_index is not None
                else None
            )
            # Keep the existing fields available to older consumers.
            record["author_institution_affiliations"] = [
                {
                    "index": affiliation["index"],
                    "institution_id": affiliation["institution_id"],
                    "institution": affiliation["name"],
                    "institution_type": affiliation["institution_type"],
                    "authors": list(affiliation["authors"]),
                    "mapping_source": _author_mapping_source(
                        affiliation.get("mapping_source")
                    ),
                    "mapping_fallback": bool(
                        affiliation.get("mapping_fallback") is True
                    ),
                    **(
                        {"source_institution_names": affiliation["source_institution_names"]}
                        if affiliation.get("source_institution_names")
                        else {}
                    ),
                }
                for affiliation in affiliations
            ]
            record["author_affiliation_indices"] = stable_indices
            record["author_institution_indices"] = legacy_indices


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


def has_formal_publication_evidence(record: Dict[str, Any]) -> bool:
    """Return whether DOI or venue identifies a non-preprint publication."""
    venue = clean_text(
        record.get("venue") or record.get("venue_name")
    ).casefold()
    doi = normalize_doi(record.get("doi"))
    return bool(
        (doi and not doi.startswith("10.48550/arxiv."))
        or (
            venue
            and not re.search(r"\b(?:arxiv|pre[\s-]?print)\b", venue)
        )
    )


def is_preprint_only_record(record: Dict[str, Any]) -> bool:
    """Return whether a record represents only an arXiv/preprint publication."""
    venue = clean_text(
        record.get("venue") or record.get("venue_name")
    ).casefold()
    publication_type = clean_text(record.get("publication_type")).casefold()
    doi = normalize_doi(record.get("doi"))
    return not has_formal_publication_evidence(record) and bool(
        parse_bool(record.get("is_arxiv_preprint"))
        or publication_type in {"preprint", "posted-content"}
        or re.search(r"\b(?:arxiv|pre[\s-]?print)\b", venue)
        or doi.startswith("10.48550/arxiv.")
    )


def is_formal_publication(record: Dict[str, Any]) -> bool:
    """Return whether a record has evidence of a non-preprint publication."""
    return has_formal_publication_evidence(record)


def exclude_preprint_versions(
    records: Sequence[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int]:
    """Drop preprint-only rows when a formal record has the same normalized title."""
    formal_titles = {
        normalize_title(record.get("title"))
        for record in records
        if is_formal_publication(record)
    }
    formal_titles.discard("")
    filtered = [
        record
        for record in records
        if not (
            normalize_title(record.get("title")) in formal_titles
            and is_preprint_only_record(record)
        )
    ]
    return filtered, len(records) - len(filtered)


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
    name = clean_text(record.get("institution") or record.get("institution_name"))
    if name:
        return name
    current = record.get("current_institution")
    if isinstance(current, dict):
        return clean_text(
            current.get("name")
            or current.get("canonical_name")
            or current.get("institution")
        )
    return clean_text(current)


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


def read_key_papers(path: Path = DEFAULT_KEY_PAPERS) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(KEY_PAPER_COLUMNS - set(reader.fieldnames or []))
            if missing:
                raise PreviewExportError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise PreviewExportError(f"Could not read {path}: {error}") from error


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError as error:
        raise PreviewExportError(f"Could not read {path}: {error}") from error


def paper_is_retracted(row: Dict[str, Any]) -> bool:
    publication_type = clean_text(row.get("publication_type")).casefold()
    title = clean_text(row.get("title")).casefold()
    exclusion_reason = clean_text(row.get("exclusion_reason")).casefold()
    notes = clean_text(row.get("notes")).casefold()
    return (
        publication_type in {"retraction", "retracted"}
        or any(
            parse_bool(row.get(field))
            for field in ("is_retracted", "retracted")
        )
        or bool(re.match(r"^(?:\[\s*retracted\s*\]|retracted\s*:)", title))
        or "retracted" in exclusion_reason
        or "retraction" in exclusion_reason
        or "retracted" in notes
    )


def exclude_retracted_records(
    records: Sequence[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int]:
    """Remove retractions from any candidate, preserved, or curated layer."""
    kept = [record for record in records if not paper_is_retracted(record)]
    return kept, len(records) - len(kept)


def paper_url(row: Dict[str, Any]) -> str:
    for field in ("paper_url", "primary_url", "landing_page_url", "url", "openalex_url"):
        value = clean_text(row.get(field))
        if value:
            return value
    return ""


def paper_record_from_candidate(row: Dict[str, str]) -> Dict[str, Any]:
    year = parse_year(row.get("publication_year") or row.get("year"))
    arxiv_id = clean_text(row.get("arxiv_id"))
    arxiv_url = clean_text(row.get("arxiv_url"))
    task_labels = normalize_export_task_labels(row)
    if task_labels is None:
        raise PreviewExportError(
            "generated_video_detection records are not eligible for public preview"
        )
    task, subtask = task_labels
    return {
        "title": clean_text(row.get("title")),
        "in_scope": True,
        "year": year,
        "publication_year": year,
        "publication_date": clean_text(row.get("publication_date")),
        "task": task,
        "subtask": subtask,
        "entry_type": normalize_entry_type(row),
        "venue": clean_text(row.get("venue")),
        "venue_name": clean_text(row.get("venue_name") or row.get("venue")),
        "venue_type": clean_text(row.get("venue_type")),
        "publisher": clean_text(row.get("publisher")),
        "publication_type": normalize_publication_type(
            row.get("publication_type"),
            venue=row.get("venue") or row.get("venue_name"),
            venue_type=row.get("venue_type"),
        ),
        "abstract": clean_text(row.get("abstract")),
        "abstract_source": clean_text(row.get("abstract_source")),
        "ai_summary": clean_text(row.get("ai_summary")),
        "doi": clean_text(row.get("doi")),
        "arxiv_id": arxiv_id,
        "arxiv_url": arxiv_url,
        "arxiv_year": parse_year(row.get("arxiv_year")),
        "has_arxiv_version": bool(arxiv_id or arxiv_url or parse_bool(row.get("has_arxiv_version"))),
        "paper_url": paper_url(row),
        "primary_url": clean_text(row.get("primary_url")),
        "landing_page_url": clean_text(row.get("landing_page_url")),
        "openalex_url": clean_text(row.get("openalex_url") or row.get("openalex_id")),
        "is_arxiv_preprint": parse_bool(row.get("is_arxiv_preprint")),
        "url": clean_text(row.get("url")),
        "authors": parse_ordered_authors(row.get("authors_ordered")),
        "source_database": clean_text(row.get("source_database")),
        "needs_review": parse_bool(row.get("manual_review")),
        "notes": clean_text(row.get("notes")),
    }


def identity_key(record: Dict[str, Any]) -> Tuple[str, Any]:
    keys = paper_identity_keys(record)
    if keys:
        return keys[0]
    return ("title_year", (normalize_title(record.get("title")), parse_year(record.get("year"))))


def apply_mapping_exclusion_decisions(
    records: Sequence[Dict[str, Any]],
    decisions: Sequence[Dict[str, str]],
) -> Tuple[List[Dict[str, Any]], int]:
    """Remove marker records explicitly rejected through an admin review queue."""
    exclusions = [
        row
        for row in decisions
        if clean_text(row.get("action")) == "exclude_wrong_mapping"
        and clean_text(row.get("institution"))
    ]
    kept: List[Dict[str, Any]] = []
    removed = 0
    for record in records:
        record_keys = set(paper_identity_keys(record))
        institution = normalize_title(record.get("institution"))
        excluded = any(
            institution == normalize_title(decision.get("institution"))
            and bool(
                record_keys
                & set(paper_identity_keys(dict(decision)))
            )
            for decision in exclusions
        )
        if excluded:
            removed += 1
        else:
            kept.append(record)
    return kept, removed


def build_identity_lookup(records: Sequence[Dict[str, Any]]) -> Dict[Tuple[str, Any], List[Dict[str, Any]]]:
    lookup: Dict[Tuple[str, Any], List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        lookup[identity_key(record)].append(record)
    return lookup


def matching_records(
    row: Dict[str, Any],
    lookup: Dict[Tuple[str, Any], List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    seen = set()
    matches: List[Dict[str, Any]] = []
    for record in lookup.get(identity_key(row), []):
        marker = id(record)
        if marker not in seen:
            seen.add(marker)
            matches.append(record)
    return matches


def ordered_paper_location_summary(
    institution_records: Sequence[Dict[str, Any]],
) -> Dict[str, List[Any]]:
    """Derive every paper location field from one canonical institution order."""
    locations: List[Dict[str, str]] = []
    seen_institutions = set()
    for record in institution_records:
        identity = detail_institution_identity(record)
        if identity in seen_institutions:
            continue
        seen_institutions.add(identity)
        normalized = normalize_country_region(
            record.get("country"),
            record.get("country_code"),
            record.get("region"),
            record.get("region_code"),
            record.get("raw_country") if "raw_country" in record else None,
            record.get("raw_country_code") if "raw_country_code" in record else None,
        )
        record.update(normalized)
        record["location_display"] = public_location_display(
            normalized["region"], normalized["country"], normalized["country_code"]
        )
        locations.append({
            "institution_name": institution_name(record),
            "institution_id": clean_text(record.get("institution_id")),
            "institution_type": clean_text(record.get("institution_type")),
            "country": normalized["country"],
            "country_code": normalized["country_code"],
            "region": normalized["region"],
            "region_code": normalized["region_code"],
            "location_display": record["location_display"],
        })

    def ordered_unique(field: str) -> List[str]:
        values = []
        seen = set()
        for location in locations:
            value = clean_text(location.get(field))
            key = value.casefold()
            if value and key not in seen:
                values.append(value)
                seen.add(key)
        return values

    return {
        "aggregated_locations": locations,
        "aggregated_institutions": ordered_unique("institution_name"),
        "aggregated_institution_types": ordered_unique("institution_type"),
        "aggregated_country_names": ordered_unique("country"),
        "aggregated_country_codes": ordered_unique("country_code"),
        "aggregated_regions": ordered_unique("region"),
        "aggregated_region_codes": ordered_unique("region_code"),
    }


def apply_ordered_paper_location_summaries(
    paper_records: Sequence[Dict[str, Any]],
    map_records: Sequence[Dict[str, Any]],
) -> None:
    maps_by_paper: Dict[Tuple[str, Any], List[Dict[str, Any]]] = defaultdict(list)
    for record in map_records:
        maps_by_paper[detail_paper_identity(record)].append(record)
    for paper in paper_records:
        matches = maps_by_paper.get(detail_paper_identity(paper), [])
        paper.update(ordered_paper_location_summary(matches))
        paper["map_record_count"] = len(matches)
        paper["has_map_location"] = bool(matches)


def affiliation_status_by_openalex(
    affiliation_rows: Sequence[Dict[str, str]],
    key_affiliation_rows: Sequence[Dict[str, str]],
    all_candidate_papers: Sequence[Dict[str, str]],
) -> Dict[str, Dict[str, bool]]:
    status: Dict[str, Dict[str, bool]] = defaultdict(
        lambda: {"has_affiliation": False, "has_coordinates": False}
    )
    for row in affiliation_rows:
        openalex_id = normalize_identifier_url(row.get("openalex_id"))
        if not openalex_id:
            continue
        has_affiliation = bool(
            clean_text(row.get("institution_name"))
            or clean_text(row.get("raw_affiliation_text"))
        )
        has_coordinates = has_usable_coordinates(row)
        status[openalex_id]["has_affiliation"] |= has_affiliation
        status[openalex_id]["has_coordinates"] |= has_coordinates

    candidate_index = index_papers_by_identity(all_candidate_papers)
    for row in key_affiliation_rows:
        candidate, _match_type = match_row_by_identity(row, candidate_index)
        if candidate is None:
            continue
        openalex_id = normalize_identifier_url(
            candidate.get("openalex_id") or candidate.get("openalex_url")
        )
        if not openalex_id:
            continue
        has_affiliation = bool(clean_text(row.get("institution")) or clean_text(row.get("raw_affiliation")))
        has_coordinates = has_usable_coordinates(row)
        status[openalex_id]["has_affiliation"] |= has_affiliation
        status[openalex_id]["has_coordinates"] |= has_coordinates
    return status


def diagnostic_status_by_title(
    diagnostic_rows: Sequence[Dict[str, str]],
) -> Dict[Tuple[str, Optional[int]], Dict[str, str]]:
    diagnostics: Dict[Tuple[str, Optional[int]], Dict[str, str]] = {}
    for row in diagnostic_rows:
        title = normalize_title(row.get("title"))
        if title:
            diagnostics[(title, parse_year(row.get("year")))] = row
    return diagnostics


def build_paper_preview(
    map_records: Sequence[Dict[str, Any]],
    candidate_rows: Sequence[Dict[str, str]],
    all_candidate_rows: Sequence[Dict[str, str]],
    key_papers: Sequence[Dict[str, str]],
    paper_arxiv_links: Sequence[Dict[str, str]],
    publication_overrides: Sequence[Dict[str, Any]],
    paper_abstracts: Sequence[Dict[str, Any]],
    local_abstracts: Sequence[Dict[str, Any]],
    affiliation_rows: Sequence[Dict[str, str]],
    key_affiliation_rows: Sequence[Dict[str, str]],
    diagnostic_rows: Sequence[Dict[str, str]],
    exclusion_rows: Sequence[Dict[str, str]] = (),
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    exclusion_index = build_active_exclusion_index(exclusion_rows)
    excluded_paper_keys = set()
    candidate_rows, preprint_versions_excluded = exclude_preprint_versions(
        candidate_rows
    )
    all_candidate_rows, _ = exclude_preprint_versions(all_candidate_rows)
    selected_by_key: Dict[Tuple[str, Any], Dict[str, str]] = {}
    for row in candidate_rows:
        if paper_is_retracted(row) or normalize_export_task_labels(row) is None:
            continue
        record = paper_record_from_candidate(row)
        if record_is_excluded(record, exclusion_index):
            excluded_paper_keys.add(identity_key(record))
            continue
        selected_by_key.setdefault(identity_key(record), row)

    all_candidate_index = index_papers_by_identity(
        all_candidate_rows,
        include_title_only=True,
    )
    key_papers_matched = 0
    for key_paper in key_papers:
        candidate, _match_type = match_row_by_identity(
            key_paper,
            all_candidate_index,
            allow_title_only=True,
        )
        if (
            candidate is None
            or paper_is_retracted(candidate)
            or normalize_export_task_labels(candidate) is None
        ):
            continue
        record = paper_record_from_candidate(candidate)
        if record_is_excluded(record, exclusion_index):
            excluded_paper_keys.add(identity_key(record))
            continue
        key_papers_matched += 1
        selected_by_key.setdefault(identity_key(record), candidate)

    paper_records = [paper_record_from_candidate(row) for row in selected_by_key.values()]
    map_lookup = build_identity_lookup(map_records)
    affiliation_status = affiliation_status_by_openalex(
        affiliation_rows,
        key_affiliation_rows,
        all_candidate_rows,
    )
    diagnostics = diagnostic_status_by_title(diagnostic_rows)

    for record in paper_records:
        marker_matches = matching_records(record, map_lookup)
        map_record_count = len(marker_matches)
        openalex_key = normalize_identifier_url(record.get("openalex_url"))
        local_status = affiliation_status.get(openalex_key, {})
        diagnostic = diagnostics.get(
            (normalize_title(record.get("title")), parse_year(record.get("year")))
        ) or {}
        skip_reason = clean_text(diagnostic.get("skip_reason")).casefold()

        has_map_location = map_record_count > 0
        has_affiliation = bool(local_status.get("has_affiliation")) or has_map_location
        has_coordinates = bool(local_status.get("has_coordinates")) or has_map_location
        missing_affiliation = not has_map_location and (
            not has_affiliation or skip_reason == "missing_affiliation_records"
        )
        missing_coordinates = not has_map_location and not missing_affiliation and (
            not has_coordinates or skip_reason == "missing_valid_coordinates"
        )

        if has_map_location:
            coverage_status = "map_ready"
        elif missing_affiliation:
            coverage_status = "missing_affiliation"
        elif missing_coordinates:
            coverage_status = "missing_coordinates"
        else:
            coverage_status = "paper_only_review"

        record["has_map_location"] = has_map_location
        record["map_record_count"] = map_record_count
        record["missing_affiliation"] = missing_affiliation
        record["missing_coordinates"] = missing_coordinates
        record["needs_review"] = bool(
            record.get("needs_review") or missing_affiliation or missing_coordinates
        )
        record["coverage_status"] = coverage_status

        if marker_matches:
            first_marker = marker_matches[0]
            record.update(ordered_paper_location_summary(marker_matches))
            for field in ("abstract", "abstract_source", "ai_summary"):
                if not clean_text(record.get(field)) and clean_text(first_marker.get(field)):
                    record[field] = clean_text(first_marker.get(field))
        else:
            record["aggregated_locations"] = []
            record["aggregated_institutions"] = []
            record["aggregated_institution_types"] = []
            record["aggregated_country_names"] = []
            record["aggregated_country_codes"] = []
            record["aggregated_regions"] = []
            record["aggregated_region_codes"] = []

    arxiv_summary = apply_paper_arxiv_links(paper_records, paper_arxiv_links)
    publication_summary = apply_publication_overrides(paper_records, publication_overrides)
    abstract_summary = apply_paper_abstracts(
        paper_records,
        paper_abstracts,
        local_abstracts,
    )
    paper_records.sort(
        key=lambda record: (
            -(parse_year(record.get("publication_year") or record.get("year")) or 0),
            normalize_title(record.get("title")),
        )
    )
    summary = {
        "paper_preview_records_exported": len(paper_records),
        "paper_preview_records_with_map_location": sum(
            bool(record.get("has_map_location")) for record in paper_records
        ),
        "paper_preview_records_missing_affiliation": sum(
            bool(record.get("missing_affiliation")) for record in paper_records
        ),
        "paper_preview_records_missing_coordinates": sum(
            bool(record.get("missing_coordinates")) for record in paper_records
        ),
        "paper_preview_key_papers_matched": key_papers_matched,
        "paper_preview_papers_excluded_curated": len(excluded_paper_keys),
        "paper_preview_preprint_versions_excluded": preprint_versions_excluded,
        **arxiv_summary,
        **publication_summary,
        **abstract_summary,
    }
    return {"metadata": dict(PAPER_PUBLIC_METADATA), "records": paper_records}, summary


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
            publication_type = normalize_publication_type(
                override.get("publication_type"), venue=formal_venue
            )
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


def synchronize_publication_types(
    paper_records: Sequence[Dict[str, Any]],
    map_records: Sequence[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Normalize canonical papers, then copy their type to every map marker.

    The returned review list is paper-level, so affiliation expansion cannot
    multiply an unresolved publication type into duplicate admin items.
    """
    unresolved: Dict[Tuple[str, Any], Dict[str, str]] = {}

    marker_lookup = build_identity_lookup(map_records)

    def normalize_record(
        record: Dict[str, Any], evidence: Optional[Dict[str, Any]] = None
    ) -> str:
        evidence = evidence or {}
        return normalize_publication_type(
            record.get("publication_type"),
            venue=record.get("venue") or record.get("venue_name"),
            venue_type=record.get("venue_type"),
            arxiv_id=record.get("arxiv_id") or evidence.get("arxiv_id"),
            arxiv_url=record.get("arxiv_url") or evidence.get("arxiv_url"),
            doi=record.get("doi"),
        )

    for paper in paper_records:
        raw_publication_type = clean_text(paper.get("publication_type"))
        marker_matches = matching_records(paper, marker_lookup)
        normalized = normalize_record(
            paper, marker_matches[0] if marker_matches else None
        )
        paper["publication_type"] = normalized
        if not normalized:
            unresolved.setdefault(
                identity_key(paper),
                {
                    "title": clean_text(paper.get("title")),
                    "publication_type": raw_publication_type,
                },
            )

    paper_lookup = build_identity_lookup(paper_records)
    for marker in map_records:
        matches = matching_records(marker, paper_lookup)
        if matches:
            marker["publication_type"] = clean_text(matches[0].get("publication_type"))
            continue
        raw_publication_type = clean_text(marker.get("publication_type"))
        normalized = normalize_record(marker)
        marker["publication_type"] = normalized
        if not normalized:
            unresolved.setdefault(
                identity_key(marker),
                {
                    "title": clean_text(marker.get("title")),
                    "publication_type": raw_publication_type,
                },
            )
    return list(unresolved.values())


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


def merge_existing_records(
    existing: Sequence[Dict[str, Any]],
    fresh: Sequence[Dict[str, Any]],
    *,
    map_records: bool,
) -> List[Dict[str, Any]]:
    """Merge a committed preview baseline with newly derived local records."""
    merged: Dict[Any, Dict[str, Any]] = {}
    order: List[Any] = []
    for record in [*existing, *fresh]:
        if map_records:
            key = clean_text(record.get("id")) or (
                detail_paper_identity(record),
                detail_institution_identity(record),
                clean_text(record.get("latitude")),
                clean_text(record.get("longitude")),
            )
        else:
            key = identity_key(record)
        if key not in merged:
            order.append(key)
        merged[key] = dict(record)
    return [merged[key] for key in order]


def has_resolved_coordinate_metadata(record: Dict[str, Any]) -> bool:
    """Return whether coordinates came through a resolution/manual layer."""
    method = clean_text(record.get("resolution_method")).casefold()
    return bool(method and method != "openalex_institution_geo")


def select_public_map_records(
    eligible_records: Sequence[Dict[str, Any]],
    max_records: Optional[int],
    key_paper_titles: set[str],
) -> Tuple[List[Dict[str, Any]], int]:
    """Maximize paper coverage first, then retain additional institutions."""
    indexed_records = list(enumerate(eligible_records))
    effective_max_records = (
        len(indexed_records) if max_records is None else max_records
    )
    records_by_paper: Dict[Tuple[str, Any], List[Tuple[int, Dict[str, Any]]]] = (
        defaultdict(list)
    )
    for index, record in indexed_records:
        records_by_paper[identity_key(record)].append((index, record))

    def quality_key(item: Tuple[int, Dict[str, Any]]) -> Tuple[Any, ...]:
        index, record = item
        confidence = normalize_confidence(record.get("resolution_confidence"))
        return (
            -CONFIDENCE_RANK[confidence],
            not has_resolved_coordinate_metadata(record),
            parse_bool(record.get("needs_review")),
            index,
        )

    representatives = [
        min(paper_records, key=quality_key)
        for paper_records in records_by_paper.values()
    ]
    representatives.sort(
        key=lambda item: (
            normalize_title(item[1].get("title")) not in key_paper_titles,
            *quality_key(item),
        )
    )
    selected_items = representatives[:effective_max_records]
    selected_indexes = {index for index, _record in selected_items}

    if len(selected_items) < effective_max_records:
        remaining = [
            item for item in indexed_records if item[0] not in selected_indexes
        ]
        # Preserve the previous stable key-paper-first ordering for additional
        # institution records after unique-paper coverage is maximized.
        remaining.sort(
            key=lambda item: (
                normalize_title(item[1].get("title")) not in key_paper_titles,
                item[0],
            )
        )
        selected_items.extend(
            remaining[: effective_max_records - len(selected_items)]
        )

    return [record for _index, record in selected_items], len(representatives)


def build_preview(
    records: Sequence[Dict[str, Any]],
    max_records: Optional[int],
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
    key_papers: Sequence[Dict[str, str]] = (),
    exclusion_rows: Sequence[Dict[str, str]] = (),
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    records = [dict(record) for record in records]
    candidate_records_read = len(records)
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
    records, preprint_versions_excluded = exclude_preprint_versions(records)
    minimum_rank = CONFIDENCE_RANK[min_confidence]
    selected = []
    below_confidence = 0
    excluded_needs_review = 0
    excluded_out_of_scope = 0
    excluded_task = 0
    missing_institution = 0
    missing_coordinates = 0
    excluded_missing_location = 0
    excluded_curated_records = 0
    excluded_curated_paper_keys = set()
    exclusion_index = build_active_exclusion_index(exclusion_rows)

    for record in records:
        if record_is_excluded(record, exclusion_index):
            excluded_curated_records += 1
            excluded_curated_paper_keys.add(identity_key(record))
            continue
        if paper_is_retracted(record):
            continue
        in_scope = parse_bool(record.get("in_scope"))
        if not in_scope and not include_out_of_scope:
            excluded_out_of_scope += 1
            continue

        task_labels = normalize_export_task_labels(record)
        if task_labels is None:
            excluded_task += 1
            continue
        task, subtask = task_labels
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
        public_record["task"] = task
        public_record["subtask"] = subtask
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
        public_record["location_display"] = public_location_display(
            public_record.get("region"),
            public_record.get("country"),
            public_record.get("country_code"),
        )
        public_record["resolution_confidence"] = confidence
        public_record["needs_review"] = needs_review
        public_record["in_scope"] = in_scope
        selected.append(public_record)

    eligible_records = len(selected)
    key_paper_titles = {normalize_title(row.get("title")) for row in key_papers}
    key_paper_titles.discard("")
    eligible_key_paper_records = sum(
        normalize_title(record.get("title")) in key_paper_titles
        for record in selected
    )
    selected, eligible_unique_papers = select_public_map_records(
        selected,
        max_records,
        key_paper_titles,
    )
    summary = {
        "candidate_records_read": candidate_records_read,
        "preprint_version_records_excluded": preprint_versions_excluded,
        "records_excluded_out_of_scope": excluded_out_of_scope,
        "records_excluded_task": excluded_task,
        "records_missing_institution": missing_institution,
        "records_missing_coordinates": missing_coordinates,
        "records_excluded_missing_location": excluded_missing_location,
        "records_excluded_below_confidence": below_confidence,
        "records_excluded_needs_review": excluded_needs_review,
        "records_excluded_curated": excluded_curated_records,
        "papers_excluded_curated": len(excluded_curated_paper_keys),
        "records_eligible_before_limit": eligible_records,
        "unique_papers_eligible_before_limit": eligible_unique_papers,
        "eligible_key_paper_records_before_limit": eligible_key_paper_records,
        "maximum_cap_applied": max_records is not None,
        "maximum_map_records": max_records,
        "key_paper_records_exported": sum(
            normalize_title(record.get("title")) in key_paper_titles
            for record in selected
        ),
        "records_exported": len(selected),
        "unique_papers_exported": len({identity_key(record) for record in selected}),
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


def exclude_nonpublic_institutions(
    paper_records: Sequence[Dict[str, Any]],
    map_records: Sequence[Dict[str, Any]],
    institutions: Sequence[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:
    """Hide ignored/deprecated/merged entities without deleting traceable data."""
    hidden_ids = {
        clean_text(row.get("institution_id"))
        for row in institutions
        if clean_text(row.get("institution_status")) in {"ignored", "deprecated", "merged"}
    }
    hidden_ids.discard("")
    maps = [
        row for row in map_records
        if clean_text(row.get("institution_id")) not in hidden_ids
    ]
    removed = len(map_records) - len(maps)
    papers = []
    for source in paper_records:
        paper = dict(source)
        old_affiliations = paper.get("affiliations")
        if isinstance(old_affiliations, list):
            kept = [
                dict(row) for row in old_affiliations
                if isinstance(row, dict)
                and clean_text(row.get("institution_id")) not in hidden_ids
            ]
            old_to_new = {}
            for new_index, row in enumerate(kept, start=1):
                old_to_new[parse_year(row.get("index")) or new_index] = new_index
                row["index"] = new_index
            paper["affiliations"] = kept
            for author in paper.get("authors") or []:
                if isinstance(author, dict):
                    author["affiliation_indices"] = [
                        old_to_new[index]
                        for value in author.get("affiliation_indices") or []
                        if (index := parse_year(value)) in old_to_new
                    ]
        author_affiliations = paper.get("author_institution_affiliations")
        if isinstance(author_affiliations, list):
            filtered = [
                dict(row) for row in author_affiliations
                if isinstance(row, dict)
                and clean_text(row.get("institution_id")) not in hidden_ids
            ]
            for index, row in enumerate(filtered, start=1):
                row["index"] = index
            paper["author_institution_affiliations"] = filtered
        papers.append(paper)
    return papers, maps, removed


def exclude_stale_curated_mapping_markers(
    map_records: Sequence[Dict[str, Any]],
    mappings: Sequence[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int]:
    """Drop preserved markers that contradict an active explicit mapping.

    This protects a repaired mapping from being shadowed by a location that was
    generated before the repair. Multiple affiliations remain valid because
    matching is scoped to the paper and the exact mapped author set.
    """
    targets: Dict[Tuple[Tuple[str, Any], Tuple[str, ...]], set[str]] = defaultdict(set)
    for mapping in mappings:
        if clean_text(mapping.get("mapping_status")) != "active":
            continue
        authors = tuple(sorted(
            normalized_author_name(author)
            for author in clean_text(mapping.get("institution_authors")).split(";")
            if normalized_author_name(author)
        ))
        if not authors:
            continue
        institution_id = clean_text(mapping.get("institution_id")) or stable_institution_id(mapping.get("institution"))
        targets[(detail_paper_identity(mapping), authors)].add(institution_id)
    kept = []
    removed = 0
    for record in map_records:
        record_authors = record.get("institution_authors") or []
        if isinstance(record_authors, str):
            record_authors = record_authors.split(";")
        authors = tuple(sorted(
            normalized_author_name(author)
            for author in record_authors
            if normalized_author_name(author)
        ))
        expected = targets.get((detail_paper_identity(record), authors))
        actual = clean_text(record.get("institution_id")) or stable_institution_id(record.get("institution"))
        if expected and actual not in expected:
            removed += 1
            continue
        kept.append(record)
    return kept, removed


def normalize_institution_lookup(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean_text(value)).casefold()
    text = "".join(character for character in text if not unicodedata.combining(character))
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def legacy_canonical_name(value: Any) -> str:
    """Return the pre-acronym form of a canonical public display name."""
    name = clean_text(value)
    match = re.fullmatch(r"(.+?)\s*\(([A-Z][A-Z0-9*.+&-]{1,15})\)", name)
    return clean_text(match.group(1)) if match else ""


def institution_id_redirects(
    institutions: Sequence[Dict[str, Any]],
    audit_rows: Sequence[Dict[str, Any]],
) -> Dict[str, str]:
    """Return transitive merged-ID redirects whose final target is active."""
    active_ids = {
        clean_text(row.get("institution_id"))
        for row in institutions
        if clean_text(row.get("institution_status")) == "active"
    }
    direct = {
        clean_text(row.get("previous_institution_id")): clean_text(row.get("institution_id"))
        for row in audit_rows
        if clean_text(row.get("action")) == "merge"
        and clean_text(row.get("previous_institution_id"))
        and clean_text(row.get("institution_id"))
    }
    redirects: Dict[str, str] = {}
    for source in direct:
        target = direct[source]
        visited = {source}
        while target in direct and target not in visited:
            visited.add(target)
            target = direct[target]
        if target in active_ids and target != source:
            redirects[source] = target
    return redirects


def public_institution_aliases(
    aliases: Sequence[Dict[str, Any]],
    location_reviews: Sequence[Dict[str, Any]] = (),
    institutions: Sequence[Dict[str, Any]] = (),
) -> List[Dict[str, str]]:
    """Return unambiguous confirmed and exact legacy aliases for public lookup."""
    candidates = []
    for row in aliases:
        alias_name = clean_text(row.get("alias_name"))
        canonical_name = clean_text(row.get("canonical_institution_name"))
        if (
            clean_text(row.get("review_status")) != "confirmed"
            or not alias_name
            or not canonical_name
        ):
            continue
        candidates.append({
            "alias_name": alias_name,
            "canonical_institution_name": canonical_name,
            "canonical_institution_id": clean_text(row.get("institution_id"))
            or stable_institution_id(canonical_name),
            "alias_language": clean_text(row.get("alias_language")),
            "alias_source": clean_text(row.get("alias_source")),
        })
    for row in location_reviews:
        alias_name = clean_text(row.get("institution"))
        canonical_name = clean_text(row.get("canonical_institution_name"))
        if (
            clean_text(row.get("review_status"))
            not in {"confirmed", "alias_of_confirmed"}
            or not alias_name
            or not canonical_name
            or normalize_institution_lookup(alias_name)
            == normalize_institution_lookup(canonical_name)
        ):
            continue
        candidates.append({
            "alias_name": alias_name,
            "canonical_institution_name": canonical_name,
            "canonical_institution_id": clean_text(row.get("institution_id"))
            or stable_institution_id(canonical_name),
            "alias_language": clean_text(row.get("detected_language")),
            "alias_source": "institution-location-review",
        })
    # Older public records predate the canonical display-name suffix. Treat
    # only an exact, unique trailing-acronym variant as a compatibility alias;
    # this does not infer parent/child relationships or merge similar names.
    legacy_targets: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in institutions:
        if clean_text(row.get("institution_status")) != "active":
            continue
        canonical_name = clean_text(row.get("canonical_name"))
        alias_name = legacy_canonical_name(canonical_name)
        if alias_name:
            legacy_targets[normalize_institution_lookup(alias_name)].append({
                "alias_name": alias_name,
                "canonical_institution_name": canonical_name,
                "canonical_institution_id": clean_text(row.get("institution_id")),
                "alias_language": "",
                "alias_source": "legacy-canonical-name",
            })
    for rows in legacy_targets.values():
        if len({row["canonical_institution_id"] for row in rows}) == 1:
            candidates.append(rows[0])
    targets_by_alias: Dict[str, set[str]] = defaultdict(set)
    for candidate in candidates:
        targets_by_alias[normalize_institution_lookup(candidate["alias_name"])].add(
            candidate["canonical_institution_id"]
        )
    result = []
    seen = set()
    for candidate in candidates:
        alias_key = normalize_institution_lookup(candidate["alias_name"])
        key = (alias_key, candidate["canonical_institution_id"])
        if len(targets_by_alias[alias_key]) != 1 or key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    return sorted(
        result,
        key=lambda row: (
            normalize_title(row["canonical_institution_name"]),
            normalize_title(row["alias_name"]),
        ),
    )


def public_canonical_institution_search_index(
    institutions: Sequence[Dict[str, Any]],
    aliases: Sequence[Dict[str, str]],
) -> Dict[str, Dict[str, Any]]:
    """Build an active-only canonical-name index for public institution search.

    Confirmed aliases created by an institution merge retain the merged source
    name, but always resolve to the active target ID. Merged entities themselves
    are deliberately omitted so they cannot become separate public results.
    """
    active = {
        clean_text(row.get("institution_id")): {
            "canonical_name": clean_text(row.get("canonical_name")),
            "institution_type": clean_text(row.get("institution_type")),
        }
        for row in institutions
        if clean_text(row.get("institution_status")) == "active"
        and clean_text(row.get("institution_id"))
        and clean_text(row.get("canonical_name"))
    }
    names_by_id: Dict[str, List[str]] = {
        institution_id: [institution["canonical_name"]]
        for institution_id, institution in active.items()
    }
    for alias in aliases:
        institution_id = clean_text(alias.get("canonical_institution_id"))
        alias_name = clean_text(alias.get("alias_name"))
        if institution_id in names_by_id and alias_name:
            names_by_id[institution_id].append(alias_name)

    result: Dict[str, Dict[str, Any]] = {}
    for institution_id, names in names_by_id.items():
        unique_names: Dict[str, str] = {}
        for name in names:
            normalized = normalize_institution_lookup(name)
            if normalized:
                unique_names.setdefault(normalized, name)
        result[institution_id] = {
            "canonical_name": active[institution_id]["canonical_name"],
            "institution_type": active[institution_id]["institution_type"],
            "names": list(unique_names.values()),
            "normalized_names": list(unique_names),
        }
    return result


def public_institution_hierarchy(
    relationships: Sequence[Dict[str, Any]],
    confirmed_locations: Sequence[Dict[str, Any]],
    institutions: Sequence[Dict[str, Any]] = (),
) -> List[Dict[str, str]]:
    """Export confirmed active canonical relationships without creating markers."""
    names_by_id = {
        (clean_text(row.get("institution_id")) or stable_institution_id(row.get("institution"))): clean_text(row.get("institution"))
        for row in confirmed_locations
        if clean_text(row.get("institution"))
    }
    active_by_id = {
        clean_text(row.get("institution_id")): row
        for row in institutions
        if clean_text(row.get("institution_status")) == "active"
        and clean_text(row.get("institution_id"))
        and clean_text(row.get("canonical_name"))
    }
    names_by_id.update({
        institution_id: clean_text(row.get("canonical_name"))
        for institution_id, row in active_by_id.items()
    })
    candidates = sorted(
        relationships,
        key=lambda row: (
            clean_text(row.get("parent_institution_id")),
            clean_text(row.get("child_institution_id")),
            clean_text(row.get("relationship_type")),
            clean_text(row.get("evidence_source")),
            clean_text(row.get("evidence_url")),
        ),
    )
    registry_candidates = ({
        "parent_institution_id": clean_text(row.get("parent_institution_id")),
        "child_institution_id": institution_id,
        "relationship_type": "affiliated_institute",
        "review_status": "confirmed",
        "evidence_source": "canonical institution registry",
        "evidence_url": "",
    } for institution_id, row in active_by_id.items()
        if clean_text(row.get("parent_institution_id"))
    )
    candidates.extend(sorted(
        registry_candidates,
        key=lambda row: (
            row["parent_institution_id"], row["child_institution_id"]
        ),
    ))
    exported = []
    seen = set()
    for row in candidates:
        parent_id = clean_text(row.get("parent_institution_id"))
        child_id = clean_text(row.get("child_institution_id"))
        key = (parent_id, child_id)
        if (
            clean_text(row.get("review_status")) != "confirmed"
            or clean_text(row.get("relationship_type")) != "affiliated_institute"
            or (
                bool(active_by_id)
                and (parent_id not in active_by_id or child_id not in active_by_id)
            )
            or parent_id not in names_by_id
            or child_id not in names_by_id
            or parent_id == child_id
            or key in seen
        ):
            continue
        seen.add(key)
        exported.append({
            "parent_institution_id": parent_id,
            "parent_institution_name": names_by_id[parent_id],
            "child_institution_id": child_id,
            "child_institution_name": names_by_id[child_id],
            "relationship_type": "affiliated_institute",
            "review_status": "confirmed",
            "evidence_source": clean_text(row.get("evidence_source")),
            "evidence_url": clean_text(row.get("evidence_url")),
        })
    return sorted(exported, key=lambda row: (
        normalize_institution_lookup(row["parent_institution_name"]),
        normalize_institution_lookup(row["child_institution_name"]),
    ))


def canonicalize_public_institutions(
    paper_records: Sequence[Dict[str, Any]],
    map_records: Sequence[Dict[str, Any]],
    aliases: Sequence[Dict[str, str]],
    confirmed_locations: Sequence[Dict[str, Any]] = (),
    institutions: Sequence[Dict[str, Any]] = (),
    id_redirects: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Canonicalize public copies and dedupe canonical paper–institution rows."""
    resolver: Dict[str, Dict[str, str]] = {}
    canonical_by_id: Dict[str, Dict[str, str]] = {
        clean_text(row.get("institution_id")): {
            "name": clean_text(row.get("canonical_name")),
            "id": clean_text(row.get("institution_id")),
            "type": clean_text(row.get("institution_type")),
        }
        for row in institutions
        if clean_text(row.get("institution_status")) == "active"
        and clean_text(row.get("institution_id"))
        and clean_text(row.get("canonical_name"))
    }
    for alias in aliases:
        canonical = {
            "name": clean_text(alias.get("canonical_institution_name")),
            "id": clean_text(alias.get("canonical_institution_id")),
            "type": clean_text(
                canonical_by_id.get(
                    clean_text(alias.get("canonical_institution_id")), {}
                ).get("type")
            ),
        }
        resolver[normalize_institution_lookup(alias.get("alias_name"))] = canonical
        resolver[normalize_institution_lookup(canonical["name"])] = canonical
        if canonical["id"]:
            canonical_by_id[canonical["id"]] = canonical
    for row in confirmed_locations:
        name = clean_text(row.get("institution"))
        if name:
            resolver.setdefault(normalize_institution_lookup(name), {
                "name": name,
                "id": stable_institution_id(name),
                "type": "",
            })

    def canonicalize_value(value: Dict[str, Any]) -> None:
        name_field = "name" if "name" in value else "institution"
        original_name = clean_text(
            value.get(name_field)
            or value.get("institution_name")
            or value.get("canonical_name")
            or value.get("canonical_institution_name")
        )
        source_name = clean_text(value.get("source_institution"))
        original_id = clean_text(
            value.get("institution_id") or value.get("canonical_institution_id")
        )
        redirected_id = (id_redirects or {}).get(original_id, original_id)
        source_canonical = resolver.get(normalize_institution_lookup(source_name))
        id_canonical = canonical_by_id.get(redirected_id)
        canonical = id_canonical
        name_canonical = resolver.get(normalize_institution_lookup(original_name))
        if not canonical:
            canonical = name_canonical
        if not id_canonical and source_canonical and (
            not canonical or source_canonical["id"] != canonical["id"]
        ):
            canonical = source_canonical
        if not canonical:
            return
        if canonical.get("type"):
            value["institution_type"] = canonical["type"]
        if (
            original_name == canonical["name"]
            and (not canonical["id"] or original_id == canonical["id"])
        ):
            return
        if original_name and original_name != canonical["name"]:
            source_names = value.get("source_institution_names")
            if not isinstance(source_names, list):
                source_names = []
            value["source_institution_names"] = list(dict.fromkeys([
                *[clean_text(name) for name in source_names if clean_text(name)],
                original_name,
            ]))
            value.setdefault("source_institution", original_name)
        if original_id and original_id != canonical["id"]:
            value.setdefault("source_institution_id", original_id)
        value[name_field] = canonical["name"]
        if "institution_name" in value:
            value["institution_name"] = canonical["name"]
        value["canonical_name"] = canonical["name"]
        value["canonical_institution_name"] = canonical["name"]
        value["institution_id"] = canonical["id"]

    def collapse_stale_alias_shadows(values: Any) -> Any:
        """Undo a prior alias split without using hierarchy as affiliation data.

        Older previews can contain both a restored canonical source and the full
        institution that the same row previously resolved to. The provenance list
        identifies that exact case. Replace the shadow at its existing index so
        author numbering remains stable, then let normal identity deduplication
        combine it with the full institution row.
        """
        if not isinstance(values, list):
            return values
        by_name = {
            normalize_institution_lookup(
                value.get("canonical_name")
                or value.get("canonical_institution_name")
                or value.get("name")
                or value.get("institution")
                or value.get("institution_name")
            ): value
            for value in values
            if isinstance(value, dict)
        }
        collapsed = []
        for value in values:
            if not isinstance(value, dict):
                collapsed.append(value)
                continue
            current_name = normalize_institution_lookup(
                value.get("canonical_name")
                or value.get("canonical_institution_name")
                or value.get("name")
                or value.get("institution")
                or value.get("institution_name")
            )
            raw_source_names = value.get("source_institution_names")
            source_names = [
                clean_text(name)
                for name in (
                    raw_source_names if isinstance(raw_source_names, list) else []
                )
                if clean_text(name)
            ]
            source_keys = [
                normalize_institution_lookup(name) for name in source_names
            ]
            replacement = next((
                by_name[source_key]
                for source_key in source_keys
                if source_key != current_name and source_key in by_name
            ), None) if current_name in set(source_keys) else None
            if replacement is None or (
                detail_institution_identity(replacement)
                == detail_institution_identity(value)
            ):
                collapsed.append(value)
                continue
            merged = dict(replacement)
            if "index" in value:
                merged["index"] = value["index"]
            merged["authors"] = list(dict.fromkeys([
                *(replacement.get("authors") or []),
                *(value.get("authors") or []),
            ]))
            merged["source_institution_names"] = list(dict.fromkeys([
                *source_names,
                *(replacement.get("source_institution_names") or []),
            ]))
            collapsed.append(merged)
        return collapsed

    for record in [*paper_records, *map_records]:
        if clean_text(record.get("institution") or record.get("institution_name")):
            canonicalize_value(record)
        for field in ("affiliations", "author_institution_affiliations"):
            values = record.get(field)
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, dict):
                        canonicalize_value(value)
                record[field] = collapse_stale_alias_shadows(values)
        old_to_new: Dict[int, int] = {}
        affiliations = record.get("affiliations")
        if isinstance(affiliations, list):
            deduplicated_affiliations = []
            by_identity: Dict[str, Dict[str, Any]] = {}
            for raw_index, affiliation in enumerate(affiliations, start=1):
                if not isinstance(affiliation, dict):
                    continue
                original_index = parse_year(affiliation.get("index")) or raw_index
                identity = detail_institution_identity(affiliation)
                existing = by_identity.get(identity)
                if existing is None:
                    affiliation["index"] = len(deduplicated_affiliations) + 1
                    deduplicated_affiliations.append(affiliation)
                    by_identity[identity] = affiliation
                    existing = affiliation
                else:
                    existing["source_institution_names"] = list(dict.fromkeys([
                        *(existing.get("source_institution_names") or []),
                        *(affiliation.get("source_institution_names") or []),
                    ]))
                old_to_new[original_index] = existing["index"]
            record["affiliations"] = deduplicated_affiliations

        author_affiliations = record.get("author_institution_affiliations")
        if isinstance(author_affiliations, list):
            deduplicated_author_affiliations = []
            by_identity = {}
            for affiliation in author_affiliations:
                if not isinstance(affiliation, dict):
                    continue
                identity = detail_institution_identity(affiliation)
                existing = by_identity.get(identity)
                if existing is None:
                    affiliation["index"] = len(deduplicated_author_affiliations) + 1
                    deduplicated_author_affiliations.append(affiliation)
                    by_identity[identity] = affiliation
                    existing = affiliation
                else:
                    existing["authors"] = list(dict.fromkeys([
                        *(existing.get("authors") or []),
                        *(affiliation.get("authors") or []),
                    ]))
                    existing["source_institution_names"] = list(dict.fromkeys([
                        *(existing.get("source_institution_names") or []),
                        *(affiliation.get("source_institution_names") or []),
                    ]))
            record["author_institution_affiliations"] = deduplicated_author_affiliations

        if old_to_new:
            def remap_indices(values: Any) -> List[int]:
                return sorted({
                    old_to_new.get(index, index)
                    for value in (values if isinstance(values, list) else [])
                    if (index := parse_year(value)) is not None
                })

            canonical_affiliations = record.get("affiliations") or []
            for author in record.get("authors") or []:
                if isinstance(author, dict):
                    author["affiliation_indices"] = remap_indices(
                        author.get("affiliation_indices")
                    )
            for field, index_field in (
                ("author_affiliation_indices", "indices"),
                ("author_institution_indices", "institution_indices"),
            ):
                for mapping in record.get(field) or []:
                    if not isinstance(mapping, dict):
                        continue
                    indices = remap_indices(mapping.get(index_field))
                    mapping[index_field] = indices
                    mapping["institution_ids"] = [
                        canonical_affiliations[index - 1]["institution_id"]
                        for index in indices
                        if 0 < index <= len(canonical_affiliations)
                    ]
        current = record.get("current_institution")
        if isinstance(current, dict):
            canonicalize_value(current)
            current_index = parse_year(current.get("index"))
            if current_index in old_to_new:
                current["index"] = old_to_new[current_index]
        aggregated = record.get("aggregated_institutions")
        if isinstance(aggregated, list):
            canonical_names = []
            for name in aggregated:
                canonical = resolver.get(normalize_institution_lookup(name))
                canonical_names.append(canonical["name"] if canonical else clean_text(name))
            record["aggregated_institutions"] = list(dict.fromkeys(filter(None, canonical_names)))

    deduplicated: Dict[Tuple[Any, str], Dict[str, Any]] = {}
    order: List[Tuple[Any, str]] = []
    for record in map_records:
        key = (identity_key(record), detail_institution_identity(record))
        if key not in deduplicated:
            deduplicated[key] = record
            order.append(key)
            continue
        existing = deduplicated[key]
        existing["institution_authors"] = list(dict.fromkeys([
            *(existing.get("institution_authors") or []),
            *(record.get("institution_authors") or []),
        ]))
        existing["source_institution_names"] = list(dict.fromkeys([
            *(existing.get("source_institution_names") or []),
            *(record.get("source_institution_names") or []),
            *([record.get("source_institution")] if record.get("source_institution") else []),
        ]))

    maps_by_paper: Dict[Tuple[str, Any], List[Dict[str, Any]]] = defaultdict(list)
    for record in deduplicated.values():
        maps_by_paper[detail_paper_identity(record)].append(record)
    for paper in paper_records:
        paper_maps = maps_by_paper.get(detail_paper_identity(paper), [])
        if paper_maps:
            paper["map_record_count"] = len(paper_maps)
            paper["has_map_location"] = True
            paper["aggregated_institutions"] = list(dict.fromkeys(
                institution_name(record) for record in paper_maps if institution_name(record)
            ))
    return [deduplicated[key] for key in order]


def print_summary(summary: Dict[str, Any], output: Path, dry_run: bool) -> None:
    print("Public preview export summary:")
    print(f"  Candidate records read: {summary['candidate_records_read']}")
    print(
        "  Preprint-version map records excluded in favor of formal publications: "
        f"{summary['preprint_version_records_excluded']}"
    )
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
        "  Records excluded by curated paper exclusions: "
        f"{summary['records_excluded_curated']}"
    )
    print(
        "  Unique papers excluded by curated paper exclusions: "
        f"{summary['papers_excluded_curated']}"
    )
    print(
        "  Records eligible before maximum: "
        f"{summary['records_eligible_before_limit']}"
    )
    print(
        "  Unique papers eligible before maximum: "
        f"{summary['unique_papers_eligible_before_limit']}"
    )
    print(
        "  Eligible key-paper records before maximum: "
        f"{summary['eligible_key_paper_records_before_limit']}"
    )
    maximum = summary["maximum_map_records"]
    print(
        "  Maximum cap applied: "
        f"{'yes (' + str(maximum) + ')' if maximum is not None else 'no'}"
    )
    print(f"  Records exported: {summary['records_exported']}")
    print(f"  Unique papers exported: {summary['unique_papers_exported']}")
    print(
        "  Key-paper records exported: "
        f"{summary['key_paper_records_exported']}"
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
    print(
        "  Curated mappings loaded: "
        f"{summary.get('curated_mappings_loaded', 0)}"
    )
    print(
        "  Curated coordinate-bearing markers created: "
        f"{summary.get('curated_markers_created', 0)}"
    )
    print(
        "  Existing markers replaced by curated mappings: "
        f"{summary.get('curated_markers_replaced', 0)}"
    )
    print(
        "  Curated mappings missing/ambiguous coordinates: "
        f"{summary.get('curated_mappings_missing_coordinates', 0) + summary.get('curated_mappings_ambiguous_coordinates', 0)}"
    )
    print(
        "  Marker exclusion review decisions applied: "
        f"{summary.get('review_mapping_exclusions_applied', 0)}"
    )
    print(
        "  Retracted map records excluded after integration: "
        f"{summary.get('retracted_map_records_excluded', 0)}"
    )
    print(f"  Output: {output}{' (not written; dry run)' if dry_run else ''}")


def print_paper_summary(summary: Dict[str, Any], output: Path, dry_run: bool) -> None:
    print("Paper-level public preview export summary:")
    print(
        "  Paper preview records exported: "
        f"{summary['paper_preview_records_exported']}"
    )
    print(
        "  Preprint-only paper versions excluded in favor of formal publications: "
        f"{summary['paper_preview_preprint_versions_excluded']}"
    )
    print(
        "  Paper preview records with map locations: "
        f"{summary['paper_preview_records_with_map_location']}"
    )
    print(
        "  Paper preview records missing affiliations: "
        f"{summary['paper_preview_records_missing_affiliation']}"
    )
    print(
        "  Paper preview records missing coordinates: "
        f"{summary['paper_preview_records_missing_coordinates']}"
    )
    print(
        "  Key papers matched into paper preview: "
        f"{summary['paper_preview_key_papers_matched']}"
    )
    print(
        "  Papers excluded by curated paper exclusions: "
        f"{summary['paper_preview_papers_excluded_curated']}"
    )
    print(
        "  Retracted paper records excluded after integration: "
        f"{summary.get('paper_preview_retracted_records_excluded', 0)}"
    )
    print(
        "  Paper preview records with non-empty abstract: "
        f"{summary['records_with_abstract']}"
    )
    print(
        "  Local abstract rows loaded: "
        f"{summary['local_abstract_rows_loaded']}"
    )
    print(
        "  Curated papers added / merged: "
        f"{summary.get('curated_papers_added', 0)} / "
        f"{summary.get('curated_papers_merged', 0)}"
    )
    print(
        "  Curated mappings matched to preview papers: "
        f"{summary.get('curated_mappings_matched_papers', 0)}"
    )
    print(
        "  Confirmed paper-version merges applied: "
        f"{summary.get('confirmed_version_merges_applied', 0)} "
        f"({summary.get('duplicate_papers_removed', 0)} paper records, "
        f"{summary.get('duplicate_markers_removed', 0)} marker records removed)"
    )
    print(
        "  Location-review rows created / updated: "
        f"{summary.get('location_review_rows_created', 0)} / "
        f"{summary.get('location_review_rows_updated', 0)}"
    )
    print(f"  Output: {output}{' (not written; dry run)' if dry_run else ''}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        records = read_candidate_records(args.input)
        if args.preserve_existing and args.output.exists():
            records = merge_existing_records(
                read_candidate_records(args.output),
                records,
                map_records=True,
            )
        paper_version_overrides = read_paper_version_overrides()
        paper_arxiv_links = [
            *read_paper_arxiv_links(),
            *read_csv_rows(DEFAULT_CURATED_ARXIV_LINKS),
        ]
        publication_overrides = read_publication_overrides()
        paper_abstracts = read_paper_abstracts()
        local_abstracts = read_local_openalex_abstracts()
        key_papers = read_key_papers()
        institution_record_overrides = load_institution_record_overrides()
        institution_author_overrides = load_institution_author_overrides()
        exclusion_rows = read_exclusion_rows(args.paper_exclusions)
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
            key_papers,
            exclusion_rows,
        )
        paper_payload, paper_summary = build_paper_preview(
            payload["records"],
            read_csv_rows(DEFAULT_CANDIDATE_PAPERS),
            read_all_candidate_papers(DEFAULT_ALL_CANDIDATE_PAPERS),
            key_papers,
            paper_arxiv_links,
            publication_overrides,
            paper_abstracts,
            local_abstracts,
            read_csv_rows(DEFAULT_AFFILIATIONS),
            read_key_paper_affiliation_enrichment(),
            read_csv_rows(DEFAULT_EXPORT_DIAGNOSTICS),
            exclusion_rows,
        )
        if args.preserve_existing and args.paper_output.exists():
            previous_papers = read_candidate_records(args.paper_output)
            exclusion_index = build_active_exclusion_index(exclusion_rows)
            previous_papers = [
                record
                for record in previous_papers
                if not record_is_excluded(record, exclusion_index)
            ]
            paper_payload["records"] = merge_existing_records(
                previous_papers,
                paper_payload["records"],
                map_records=False,
            )
        curated_papers = load_curated_papers(args.curated_papers)
        curated_mappings = load_curated_mappings(args.curated_mappings)
        location_review_rows = load_location_review_queue(
            args.location_review
        )
        confirmed_location_rows = load_confirmed_locations(
            args.institution_locations
        )
        institution_alias_rows = load_institution_aliases(
            args.institution_aliases
        )
        institution_hierarchy_rows = read_csv_rows(args.institution_hierarchy)
        processed_cache_rows = load_institution_resolution_cache(
            args.institution_resolution_cache
        )
        (
            integrated_papers,
            integrated_maps,
            integrated_location_reviews,
            curated_summary,
        ) = integrate_curated_records(
            paper_payload["records"],
            payload["records"],
            curated_papers,
            curated_mappings,
            exclusion_rows,
            records,
            location_review_rows,
            confirmed_location_rows,
            processed_cache_rows,
            institution_alias_rows,
        )
        integrated_maps, stale_mapping_markers_excluded = (
            exclude_stale_curated_mapping_markers(integrated_maps, curated_mappings)
        )
        (
            integrated_papers,
            integrated_maps,
            version_merge_summary,
        ) = apply_confirmed_version_merges(
            integrated_papers,
            integrated_maps,
            read_paper_version_merges(args.paper_version_merges),
        )
        stale_mapping_markers_excluded += enforce_affiliation_source_precedence(
            integrated_papers,
            integrated_maps,
            curated_mappings,
            curated_papers,
        )
        integrated_papers, curated_preprint_papers_excluded = (
            exclude_preprint_versions(integrated_papers)
        )
        integrated_maps, curated_preprint_map_records_excluded = (
            exclude_preprint_versions(integrated_maps)
        )
        review_decisions = read_csv_rows(args.review_decisions)
        integrated_maps, review_mapping_exclusions_applied = (
            apply_mapping_exclusion_decisions(
                integrated_maps, review_decisions
            )
        )
        integrated_papers, retracted_papers_excluded = (
            exclude_retracted_records(integrated_papers)
        )
        integrated_maps, retracted_map_records_excluded = (
            exclude_retracted_records(integrated_maps)
        )
        unresolved_publication_types = synchronize_publication_types(
            integrated_papers, integrated_maps
        )
        if unresolved_publication_types:
            details = "; ".join(
                f"{row['title']!r} ({row['publication_type'] or 'missing'})"
                for row in unresolved_publication_types
            )
            raise PreviewExportError(
                "Unresolved publication types require admin review: " + details
            )
        institution_rows = load_institutions(args.institutions)
        institution_audit_rows = read_csv_rows(args.institution_audit_log)
        exported_aliases = public_institution_aliases(
            institution_alias_rows,
            integrated_location_reviews,
            institution_rows,
        )
        exported_id_redirects = institution_id_redirects(
            institution_rows,
            institution_audit_rows,
        )
        canonical_institution_search_index = (
            public_canonical_institution_search_index(
                institution_rows,
                exported_aliases,
            )
        )
        exported_hierarchy = public_institution_hierarchy(
            institution_hierarchy_rows,
            confirmed_location_rows,
            institution_rows,
        )
        integrated_maps = canonicalize_public_institutions(
            integrated_papers,
            integrated_maps,
            exported_aliases,
            confirmed_location_rows,
            institution_rows,
            exported_id_redirects,
        )
        for record in integrated_maps:
            record["institution_id"] = (
                clean_text(record.get("institution_id"))
                or stable_institution_id(
                    record.get("canonical_institution_name")
                    or record.get("institution_name")
                    or record.get("institution")
                )
            )
        integrated_papers, integrated_maps, ignored_institution_records = (
            exclude_nonpublic_institutions(
                integrated_papers,
                integrated_maps,
                institution_rows,
            )
        )
        apply_ordered_paper_location_summaries(
            integrated_papers, integrated_maps
        )
        add_public_detail_fields(integrated_papers, integrated_maps)
        payload["records"] = integrated_maps
        paper_payload["records"] = integrated_papers
        payload["institution_aliases"] = exported_aliases
        paper_payload["institution_aliases"] = exported_aliases
        payload["canonical_institution_search_index"] = (
            canonical_institution_search_index
        )
        paper_payload["canonical_institution_search_index"] = (
            canonical_institution_search_index
        )
        payload["institution_id_redirects"] = exported_id_redirects
        paper_payload["institution_id_redirects"] = exported_id_redirects
        payload["institution_hierarchy"] = exported_hierarchy
        paper_payload["institution_hierarchy"] = exported_hierarchy
        summary["preprint_version_records_excluded"] += (
            curated_preprint_map_records_excluded
        )
        paper_summary["paper_preview_preprint_versions_excluded"] += (
            curated_preprint_papers_excluded
        )
        paper_summary["paper_preview_retracted_records_excluded"] = (
            retracted_papers_excluded
        )
        summary["retracted_map_records_excluded"] = (
            retracted_map_records_excluded
        )
        summary["ignored_institution_records_excluded"] = ignored_institution_records
        summary["stale_mapping_markers_excluded"] = stale_mapping_markers_excluded

        if (
            curated_summary.get("curated_markers_created", 0)
            or curated_summary.get("curated_markers_replaced", 0)
        ):
            payload["metadata"] = {
                **payload["metadata"],
                "dataset_type": "mixed_candidate_and_curated_public_preview",
                "generated_from": (
                    "OpenAlex candidate metadata and maintainer-confirmed "
                    "curated mappings"
                ),
                "warning": (
                    "Contains automatically generated candidate records plus "
                    "explicitly identified maintainer-confirmed curated markers."
                ),
            }
        if (
            curated_summary.get("curated_papers_eligible", 0)
            or curated_summary.get("curated_mappings_matched_papers", 0)
        ):
            paper_payload["metadata"] = {
                **paper_payload["metadata"],
                "dataset_type": "mixed_candidate_and_curated_preview_papers",
                "generated_from": (
                    "OpenAlex candidate metadata, local review caches, and "
                    "maintainer-confirmed curated records"
                ),
                "warning": (
                    "Record provenance fields distinguish automatically "
                    "generated candidates from maintainer-confirmed curation."
                ),
            }

        curated_summary.update(version_merge_summary)
        summary.update(curated_summary)
        summary["review_mapping_exclusions_applied"] = (
            review_mapping_exclusions_applied
        )
        summary["records_exported"] = len(integrated_maps)
        summary["unique_papers_exported"] = len(
            {identity_key(record) for record in integrated_maps}
        )
        key_paper_titles = {
            normalize_title(row.get("title")) for row in key_papers
        }
        key_paper_titles.discard("")
        summary["key_paper_records_exported"] = sum(
            normalize_title(record.get("title")) in key_paper_titles
            for record in integrated_maps
        )
        if args.max_records is None:
            summary["records_eligible_before_limit"] = len(integrated_maps)
            summary["unique_papers_eligible_before_limit"] = summary[
                "unique_papers_exported"
            ]
            summary["eligible_key_paper_records_before_limit"] = summary[
                "key_paper_records_exported"
            ]
        else:
            summary["records_eligible_before_limit"] += (
                curated_summary.get("curated_markers_created", 0)
                - curated_summary.get("curated_markers_replaced", 0)
            )
        summary["exported_records_with_abstract"] = sum(
            bool(clean_text(record.get("abstract")))
            for record in integrated_maps
        )
        paper_summary.update(curated_summary)
        paper_summary["paper_preview_records_exported"] = len(
            integrated_papers
        )
        paper_summary["paper_preview_records_with_map_location"] = sum(
            bool(record.get("has_map_location"))
            for record in integrated_papers
        )
        paper_summary["paper_preview_records_missing_affiliation"] = sum(
            bool(record.get("missing_affiliation"))
            for record in integrated_papers
        )
        paper_summary["paper_preview_records_missing_coordinates"] = sum(
            bool(record.get("missing_coordinates"))
            for record in integrated_papers
        )
        paper_summary["records_with_abstract"] = sum(
            bool(clean_text(record.get("abstract")))
            for record in integrated_papers
        )
        paper_summary["paper_preview_papers_excluded_curated"] += (
            curated_summary.get("curated_papers_skipped_exclusion", 0)
        )
        if not args.dry_run:
            write_json(args.output, payload)
            write_json(args.paper_output, paper_payload)
            if integrated_location_reviews != location_review_rows:
                save_location_review_queue(
                    integrated_location_reviews,
                    args.location_review,
                )
        print_summary(summary, args.output, args.dry_run)
        print_paper_summary(paper_summary, args.paper_output, args.dry_run)
    except (
        PreviewExportError,
        ExportError,
        PaperExclusionError,
        PaperVersionMergeError,
        CuratedExportError,
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
