"""Reviewed integration baselines for the current curated repository.

These constants describe the checked-in full repository, not isolated unit-test
fixtures. Update them only after reviewing the corresponding curated/Public
data change and the identity and relationship invariants in
``test_repository_baseline.py``.
"""

CURRENT_REPOSITORY_BASELINE = {
    "public_unique_papers": 574,
    "public_map_source_papers": 569,
    "public_papers_with_map": 568,
    "public_papers_without_map": 6,
    # Registry rows include active identities plus retained merged/ignored history.
    "total_institution_registry_rows": 663,
    "active_canonical_institutions": 648,
    "non_active_institution_registry_rows": 15,
    # Unique public paper–institution relationships; one relationship has two markers.
    "public_paper_institution_relationships": 1302,
    "institution_hierarchy_edges": 11,
    "institution_aliases": 114,
}

RELEASE_REPOSITORY_BASELINE = {
    "curated_papers": 342,
    "public_unique_papers": 546,
    "public_map_source_papers": 540,
    "public_papers_with_map": 539,
    "public_papers_without_map": 7,
    "public_map_relationships": 1264,
    "canonical_institution_rows": 662,
    "active_canonical_institutions": 650,
    "inactive_or_merged_institutions": 12,
    "author_institution_mappings": 942,
    "institution_hierarchy_edges": 8,
    "institution_aliases": 80,
}

CANONICAL_INSTITUTION_STATUS_TOTALS = {
    "active": 648,
    "merged": 9,
    "ignored": 6,
}

RELEASE_CANONICAL_INSTITUTION_STATUS_TOTALS = {
    "active": 650,
    "merged": 6,
    "ignored": 6,
}

CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 492,
    "research_unit": 77,
    "company": 77,
    "other": 17,
}

ACTIVE_CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 486,
    "research_unit": 74,
    "company": 75,
    "other": 13,
}

PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS = {
    # 2026-08-28: active curated affiliations only, including paper-only rows.
    "university": 545,
    "research_unit": 109,
    "company": 105,
    "other": 29,
}

# Historical release artifacts are immutable; current effective venues have
# changed since the 2026-08-24 checkpoint.
RELEASE_PUBLICATION_TYPE_TOTALS = {"conference": 314, "journal": 167, "preprint": 64, "book": 1}

PUBLICATION_TYPE_TOTALS = {
    "conference": 350,
    "journal": 161,
    "preprint": 62,
    "book": 1,
}

TASK_TOTALS = {
    "detection": 499,
    "source_attribution": 46,
    "detection_and_source_attribution": 29,
}

RELEASE_TASK_TOTALS = {
    "detection": 471,
    "source_attribution": 46,
    "detection_and_source_attribution": 29,
}

PUBLIC_PAPERS_WITHOUT_MAP = {
    "Diffusion-Driven Forgery Detection: Distilling Latent Features for Generalized Image Forensics":
        "missing_affiliation_rows",
    "FALCON-Net: Feature Aggregation of Local Patterns for AI-Generated Image Detection":
        "missing_affiliation_rows",
    "NSFF: Noise and Semantic Features Fusion for AI-Generated Image Detection":
        "missing_affiliation_rows",
    "Spatial Flatness-Curvature Mask Driven Generalized Detection of Synthetic Images":
        "missing_affiliation_rows",
    "Unified Detection of Synthetic and Manipulated Images via Dual-Stream Artifact Fusion":
        "missing_affiliation_rows",
    "Explainable Artifacts for Synthetic Western Blot Source Attribution":
        "missing_affiliation_rows",
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
