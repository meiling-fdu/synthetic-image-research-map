"""Reviewed integration baselines for the current curated repository.

These constants describe the checked-in full repository, not isolated unit-test
fixtures. Update them only after reviewing the corresponding curated/Public
data change and the identity and relationship invariants in
``test_repository_baseline.py``.
"""

CURRENT_REPOSITORY_BASELINE = {
    "curated_papers": 224,
    "public_unique_papers": 512,
    "public_map_relationships": 1077,
    "canonical_institution_rows": 595,
    "active_canonical_institutions": 593,
    "inactive_or_merged_institutions": 2,
    "author_institution_mappings": 660,
    "institution_hierarchy_edges": 6,
}

CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 452,
    "research_unit": 69,
    "company": 61,
    "other": 13,
}

ACTIVE_CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 451,
    "research_unit": 69,
    "company": 60,
    "other": 13,
}

PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS = {
    "university": 482,
    "research_unit": 99,
    "company": 73,
    "other": 39,
}

PUBLICATION_TYPE_TOTALS = {
    "conference": 247,
    "journal": 182,
    "preprint": 63,
    "book": 20,
}

TASK_TOTALS = {
    "detection": 439,
    "source_attribution": 46,
    "detection_and_source_attribution": 27,
}

INFORMATION_ENGINEERING_PUBLIC_RECORD_IDS = {
    "openalex-candidate-f7888db659be7a0c",
    "openalex-candidate-4fc5d76c4c1dde8a",
    "openalex-candidate-aa0d52041ecd0c07",
    "openalex-candidate-919d3c2bcfbdb403",
    "openalex-candidate-e0b2b9196a6705c5",
    "curated-map:44229f2cf573ad44149f",
    "curated-map:92126900d9e371dda577",
}
