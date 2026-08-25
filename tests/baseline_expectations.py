"""Reviewed integration baselines for the current curated repository.

These constants describe the checked-in full repository, not isolated unit-test
fixtures. Update them only after reviewing the corresponding curated/Public
data change and the identity and relationship invariants in
``test_repository_baseline.py``.
"""

CURRENT_REPOSITORY_BASELINE = {
    "curated_papers": 324,
    "public_unique_papers": 546,
    "public_map_source_papers": 535,
    "public_papers_with_map": 534,
    "public_papers_without_map": 12,
    "public_map_relationships": 1224,
    "canonical_institution_rows": 644,
    "active_canonical_institutions": 640,
    "inactive_or_merged_institutions": 4,
    "author_institution_mappings": 877,
    "institution_hierarchy_edges": 7,
    "institution_aliases": 55,
}

CANONICAL_INSTITUTION_STATUS_TOTALS = {
    "active": 640,
    "merged": 2,
    "ignored": 2,
}

CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 465,
    "research_unit": 66,
    "company": 65,
    "other": 48,
}

ACTIVE_CANONICAL_INSTITUTION_TYPE_TOTALS = {
    "university": 463,
    "research_unit": 66,
    "company": 63,
    "other": 48,
}

PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS = {
    "university": 513,
    "research_unit": 104,
    "company": 81,
    "other": 55,
}

PUBLICATION_TYPE_TOTALS = {
    "conference": 314,
    "journal": 166,
    "preprint": 65,
    "book": 1,
}

TASK_TOTALS = {
    "detection": 471,
    "source_attribution": 46,
    "detection_and_source_attribution": 29,
}

PUBLIC_PAPERS_WITHOUT_MAP = {
    "Cover-Source Mismatch in Deepfake Detection: A Systematic Study":
        "missing_affiliation_rows",
    "Diffusion-Driven Forgery Detection: Distilling Latent Features for Generalized Image Forensics":
        "missing_affiliation_rows",
    "Fake Detection Based on Balanced Attention and Information Guidance for Collaborative Image Processing Tasks":
        "missing_affiliation_rows",
    "FALCON-Net: Feature Aggregation of Local Patterns for AI-Generated Image Detection":
        "missing_affiliation_rows",
    "Geometric-Semantic Dual-Adaptation for Generalizable AI-Generated Image Detection":
        "missing_affiliation_rows",
    "Lightweight Image Forgery Detection via Tucker Decomposition for Efficient Edge Deployment":
        "missing_affiliation_rows",
    "NSFF: Noise and Semantic Features Fusion for AI-Generated Image Detection":
        "missing_affiliation_rows",
    "Spatial Flatness-Curvature Mask Driven Generalized Detection of Synthetic Images":
        "missing_affiliation_rows",
    "The Deployment Gap in AI Media Detection: Platform-Aware and Visually Constrained Adversarial Evaluation":
        "missing_affiliation_rows",
    "Unified Detection of Synthetic and Manipulated Images via Dual-Stream Artifact Fusion":
        "missing_affiliation_rows",
    "Weakly‐Aligned Region‐Language Transformer for Real‐Time Artistic Content Detection in SAGIN":
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
