#!/usr/bin/env python3
"""Project canonical entities into deterministic curated public records."""

from __future__ import annotations

from typing import Any, Dict, Mapping

try:
    from .canonical_authorship import load_canonical_dataset
except ImportError:
    from canonical_authorship import load_canonical_dataset


PUBLIC_PAPER_FIELDS = {
    "id", "paper_id", "title", "year", "publication_year", "authors", "venue",
    "venue_name", "doi", "arxiv_id", "openalex_url", "paper_url", "primary_url",
    "publication_type", "abstract", "task", "subtask", "source_database",
    "metadata_source", "provenance_sources", "canonical_authorship",
    "author_institution_affiliations", "author_institution_indices", "in_scope",
    "needs_review", "has_map_location", "map_record_count", "missing_affiliation",
    "missing_coordinates", "coverage_status", "aggregated_institutions",
    "aggregated_country_names", "aggregated_country_codes", "aggregated_regions",
}
PUBLIC_MARKER_FIELDS = PUBLIC_PAPER_FIELDS | {
    "institution_id", "institution", "institution_authors", "city", "region",
    "region_code", "country", "country_code", "latitude", "longitude", "resolution_confidence",
    "resolution_method",
}


def _project(record: Mapping[str, Any], fields: set[str]) -> Dict[str, Any]:
    return {field: record[field] for field in fields if field in record}


def curated_export() -> Dict[str, list[Dict[str, Any]]]:
    dataset = load_canonical_dataset()
    return {
        "papers": [_project(record, PUBLIC_PAPER_FIELDS) for record in dataset["papers"]],
        "markers": [_project(record, PUBLIC_MARKER_FIELDS) for record in dataset["markers"]],
    }
