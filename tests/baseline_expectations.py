"""Reviewed integration baselines for the current curated repository.

These constants describe the checked-in full repository, not isolated unit-test
fixtures. Update them only after reviewing the corresponding curated/Public
data change and the identity and relationship invariants in
``test_repository_baseline.py``.
"""

CURRENT_REPOSITORY_BASELINE = {
    "curated_papers": 255,
    "public_unique_papers": 516,
    "public_map_relationships": 1098,
    "canonical_institution_rows": 604,
    "active_canonical_institutions": 601,
    "inactive_or_merged_institutions": 3,
    "author_institution_mappings": 715,
    "institution_hierarchy_edges": 7,
    "institution_aliases": 81,
}

CANONICAL_INSTITUTION_STATUS_TOTALS = {
    "active": 601,
    "merged": 1,
    "ignored": 2,
}

CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 455,
    "research_unit": 70,
    "company": 59,
    "other": 20,
}

ACTIVE_CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 454,
    "research_unit": 70,
    "company": 57,
    "other": 20,
}

PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS = {
    "university": 484,
    "research_unit": 99,
    "company": 75,
    "other": 40,
}

PUBLICATION_TYPE_TOTALS = {
    "conference": 277,
    "journal": 164,
    "preprint": 57,
    "book": 18,
}

TASK_TOTALS = {
    "detection": 444,
    "source_attribution": 46,
    "detection_and_source_attribution": 26,
}

INFORMATION_ENGINEERING_PUBLIC_RECORD_IDS = {
    "openalex-candidate-f7888db659be7a0c",
    "openalex-candidate-4fc5d76c4c1dde8a",
    "openalex-candidate-aa0d52041ecd0c07",
    "openalex-candidate-919d3c2bcfbdb403",
    "curated-map:44229f2cf573ad44149f",
    "curated-map:92126900d9e371dda577",
    "curated-map:ff03ae3f6aab250e53d0",
}
