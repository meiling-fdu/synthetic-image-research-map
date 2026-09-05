"""Reviewed integration baselines for the current curated repository.

These constants describe the checked-in full repository, not isolated unit-test
fixtures. Update them only after reviewing the corresponding curated/Public
data change and the identity and relationship invariants in
``test_repository_baseline.py``.
"""

CURRENT_REPOSITORY_BASELINE = {
    # Canonical public paper records after the 2026-09-05 Ant/AI-edit gap-fill.
    "public_unique_papers": 613,
    # Distinct paper identities represented by at least one public map marker.
    "public_map_source_papers": 608,
    # Canonical public papers that resolve to at least one public map marker.
    "public_papers_with_map": 607,
    "public_papers_without_map": 6,
    # Registry rows include active identities plus retained merged/ignored history.
    "total_institution_registry_rows": 691,
    "active_canonical_institutions": 675,
    "non_active_institution_registry_rows": 16,
    # Unique public paper–institution relationships; one relationship has two markers.
    "public_paper_institution_relationships": 1402,
    "institution_hierarchy_edges": 11,
    "institution_aliases": 115,
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
    "active": 675,
    "merged": 10,
    "ignored": 6,
}

RELEASE_CANONICAL_INSTITUTION_STATUS_TOTALS = {
    "active": 650,
    "merged": 6,
    "ignored": 6,
}

CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 508,
    "research_unit": 80,
    "company": 79,
    "other": 24,
}

ACTIVE_CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 502,
    "research_unit": 77,
    "company": 77,
    "other": 19,
}

PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS = {
    # Papers associated with each active institution type; one paper may
    # contribute to multiple types, so these are not paper-record totals.
    "university": 583,
    "research_unit": 120,
    "company": 119,
    "other": 35,
}

# Historical release artifacts are immutable; current effective venues have
# changed since the 2026-08-24 checkpoint.
RELEASE_PUBLICATION_TYPE_TOTALS = {"conference": 314, "journal": 167, "preprint": 64, "book": 1}

PUBLICATION_TYPE_TOTALS = {
    # Current public corpus after the 2026-09-05 Ant/AI-edit gap-fill.
    "conference": 359,
    "journal": 157,
    "preprint": 96,
    "book": 1,
}

TASK_TOTALS = {
    # Multi-label public-paper counts after resolving the taxonomy review queue.
    "detection": 577,
    "source_attribution": 77,
    "localization": 18,
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
    # Denoising Trajectory Biases, added from accepted-paper affiliation evidence.
    "curated-map:b2e9ed534727553af0d0",
    "curated-map:ff03ae3f6aab250e53d0",
}
