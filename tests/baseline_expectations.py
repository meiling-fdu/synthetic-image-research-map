"""Reviewed integration baselines for the current curated repository.

These constants describe the checked-in full repository, not isolated unit-test
fixtures. Update them only after reviewing the corresponding curated/Public
data change and the identity and relationship invariants in
``test_repository_baseline.py``.
"""

# Tier 1 primary curation: sixteen additions, ten with reusable map locations.
# Pre-existing rows and exclusions are unchanged; six additions await coordinates.
CURRENT_REPOSITORY_BASELINE = {
    "public_unique_papers": 636,
    # Map source identities include one identity resolved to a canonical paper.
    "public_map_source_papers": 624,
    "public_papers_with_map": 623,
    "public_papers_without_map": 13,
    "total_institution_registry_rows": 722,
    "active_canonical_institutions": 701,
    "non_active_institution_registry_rows": 21,
    # One paper–institution relationship has two markers (1466 markers total).
    "public_paper_institution_relationships": 1465,
    "institution_hierarchy_edges": 15,
    "institution_aliases": 120,
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

CANONICAL_INSTITUTION_STATUS_TOTALS = {'active': 701, 'ignored': 6, 'merged': 15}

RELEASE_CANONICAL_INSTITUTION_STATUS_TOTALS = {
    "active": 650,
    "merged": 6,
    "ignored": 6,
}

CANONICAL_INSTITUTION_TYPE_TOTALS = {'university': 523, 'company': 86, 'research_unit': 89, 'other': 24}

ACTIVE_CANONICAL_INSTITUTION_TYPE_TOTALS = {'university': 515, 'company': 84, 'research_unit': 85, 'other': 17}

PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS = {'university': 603, 'research_unit': 126, 'other': 33, 'company': 130}

# Historical release artifacts are immutable; current effective venues have
# changed since the 2026-08-24 checkpoint.
RELEASE_PUBLICATION_TYPE_TOTALS = {"conference": 314, "journal": 167, "preprint": 64, "book": 1}

PUBLICATION_TYPE_TOTALS = {'conference': 369, 'preprint': 108, 'journal': 158, 'book': 1}

TASK_TOTALS = {'detection': 598, 'source_attribution': 77, 'localization': 25}

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

# Affiliation identity is reviewed; a defensible location is still pending.
CURATED_PAPERS_AWAITING_COORDINATES = {
    'UniAIDet: A Unified and Universal Benchmark for AI-Generated Image Content Detection and Localization',
    'Detective SAM: Adaptive AI-Image Forgery Localization',
    'Fractal Characterization of Low-Correlation Signals in AI-Generated Image Detection',
    'SPECTRA-Net: Scalable Pipeline for Explainable Cross-Domain Tensor Representations for AI-Generated Images Detection',
    'DeCLIP: Decoding CLIP Representations for Deepfake Localization',
    'FUSE: Unifying Spectral and Semantic Cues for Robust AI-Generated Image Detection',
    'Weakly-Supervised Deepfake Localization in Diffusion-Generated Images',
}
