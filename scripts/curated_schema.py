#!/usr/bin/env python3
"""Shared schema and controlled vocabularies for the curated CSV layer."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
CURATED_DATA_DIR = REPOSITORY_ROOT / "data" / "curated"

PAPERS_COLUMNS = (
    "paper_id",
    "title",
    "year",
    "authors",
    "venue",
    "doi",
    "arxiv_id",
    "openalex_url",
    "paper_url",
    "publication_type",
    "abstract",
    "task",
    "subtask",
    "scope_status",
    "source_database",
    "metadata_source",
    "curation_status",
    "review_status",
    "review_note",
    "created_at",
    "updated_at",
)

AUTHOR_INSTITUTION_MAPPING_COLUMNS = (
    "mapping_id",
    "paper_id",
    "title",
    "year",
    "doi",
    "openalex_url",
    "institution",
    "institution_authors",
    "raw_affiliation",
    "evidence_source",
    "evidence_url",
    "affiliation_note",
    "mapping_status",
    "review_note",
    "created_at",
    "updated_at",
)

PAPER_EXCLUSION_COLUMNS = (
    "exclusion_id",
    "paper_id",
    "title",
    "year",
    "doi",
    "openalex_url",
    "reason",
    "review_note",
    "excluded_from_public_preview",
    "excluded_from_map",
    "is_active",
    "created_at",
    "created_by",
    "restored_at",
    "restore_note",
    "source_database",
    "metadata_source",
)

INSTITUTION_LOCATION_REVIEW_COLUMNS = (
    "institution",
    "related_paper_id",
    "title",
    "year",
    "doi",
    "openalex_url",
    "institution_authors",
    "raw_affiliation",
    "evidence_source",
    "evidence_url",
    "suggested_city",
    "suggested_country",
    "location_status",
    "coordinate_status",
    "review_note",
    "created_at",
    "updated_at",
)

EXPECTED_COLUMNS: Dict[str, Tuple[str, ...]] = {
    "papers.csv": PAPERS_COLUMNS,
    "author_institution_mappings.csv": AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    "paper_exclusions.csv": PAPER_EXCLUSION_COLUMNS,
    "institution_location_review.csv": INSTITUTION_LOCATION_REVIEW_COLUMNS,
}

ALLOWED_TASKS = {
    "detection",
    "detection_and_source_attribution",
    "source_attribution",
    "uncertain",
}

ALLOWED_CURATION_STATUSES = {
    "auto_imported",
    "manually_added",
    "manually_confirmed",
    "corrected_by_admin",
    "needs_review",
}

ALLOWED_REVIEW_STATUSES = {
    "pending",
    "reviewed",
    "needs_check",
}

ALLOWED_MAPPING_STATUSES = {
    "active",
    "excluded",
    "needs_review",
}

ALLOWED_LOCATION_STATUSES = {
    "missing",
    "known",
    "ambiguous",
    "needs_location_review",
}

ALLOWED_EXCLUSION_REASONS = {
    "out_of_scope",
    "downstream_synthetic_data_only",
    "medical_or_agriculture_or_industrial_only",
    "remote_sensing_only",
    "deepfake_only_not_core",
    "policy_or_perception_only",
    "duplicate",
    "retracted",
    "wrong_metadata",
    "other",
}

ALLOWED_COORDINATE_STATUSES = {
    "missing",
    "known",
    "ambiguous",
    "needs_coordinate_review",
}
