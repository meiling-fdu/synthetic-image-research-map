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
    "author_order",
    "raw_affiliation",
    "openalex_institution_id",
    "institution_city",
    "institution_country",
    "institution_latitude",
    "institution_longitude",
    "provenance_source",
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
    "canonical_institution_name",
    "detected_language",
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
    "matched_institution",
    "suggested_canonical_institution",
    "match_method",
    "similarity_score",
    "confidence",
    "openalex_institution_id",
    "ror_id",
    "wikidata_id",
    "review_status",
    "location_status",
    "coordinate_status",
    "review_note",
    "created_at",
    "updated_at",
)

INSTITUTION_ALIAS_COLUMNS = (
    "alias_name",
    "canonical_institution_name",
    "alias_language",
    "alias_source",
    "review_status",
    "notes",
)

INSTITUTION_LOCATION_COLUMNS = (
    "location_id",
    "institution",
    "normalized_institution",
    "city",
    "region",
    "country",
    "country_code",
    "lat",
    "lon",
    "coordinate_source",
    "coordinate_source_url",
    "coordinate_status",
    "review_note",
    "created_at",
    "updated_at",
    "created_by",
)

REVIEW_DECISION_COLUMNS = (
    "decision_id",
    "review_queue",
    "target_type",
    "title",
    "year",
    "doi",
    "openalex_url",
    "institution",
    "action",
    "review_note",
    "created_at",
    "updated_at",
    "created_by",
)

PAPER_VERSION_MERGE_COLUMNS = (
    "merge_id",
    "canonical_title",
    "canonical_year",
    "canonical_doi",
    "canonical_arxiv_id",
    "canonical_openalex_url",
    "duplicate_title",
    "duplicate_year",
    "duplicate_doi",
    "duplicate_arxiv_id",
    "duplicate_arxiv_url",
    "duplicate_openalex_url",
    "status",
    "reason",
    "is_active",
    "created_at",
    "created_by",
)

EXPECTED_COLUMNS: Dict[str, Tuple[str, ...]] = {
    "papers.csv": PAPERS_COLUMNS,
    "author_institution_mappings.csv": AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    "paper_exclusions.csv": PAPER_EXCLUSION_COLUMNS,
    "institution_location_review.csv": INSTITUTION_LOCATION_REVIEW_COLUMNS,
    "institution_aliases.csv": INSTITUTION_ALIAS_COLUMNS,
    "institution_locations.csv": INSTITUTION_LOCATION_COLUMNS,
    "review_decisions.csv": REVIEW_DECISION_COLUMNS,
    "paper_version_merges.csv": PAPER_VERSION_MERGE_COLUMNS,
}

ALLOWED_TASKS = {
    "detection",
    "detection_and_source_attribution",
    "source_attribution",
    "uncertain",
}

ALLOWED_SUBTASKS = {
    "ai_generated_image_detection",
    "deepfake_image_detection",
    "detection_and_source_attribution",
    "generated_image_source_attribution",
    "source_identification",
    "synthetic_image_detection",
    "unknown",
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
    "needs_coordinate_review",
}

ALLOWED_INSTITUTION_REVIEW_STATUSES = {
    "confirmed",
    "pending_review",
    "needs_coordinates",
    "ambiguous",
    "alias_candidate",
    "alias_of_confirmed",
    "ignore",
    "excluded",
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

ALLOWED_SCOPE_STATUSES = {
    "in_scope",
    "out_of_scope",
    "uncertain",
    "needs_review",
}

ALLOWED_REVIEW_QUEUES = {
    "high_risk_marker",
    "marker_blocker",
    "key_paper_coverage",
    "manual_import",
    "title_match",
    "other",
}

ALLOWED_REVIEW_ACTIONS = {
    "confirm_marker",
    "replace_author_institution_mapping",
    "exclude_wrong_mapping",
    "send_to_location_review",
    "exclude_paper_scope",
    "add_paper",
    "add_manually",
    "retry_search",
    "no_action_after_review",
    "unresolved",
    "other",
}
