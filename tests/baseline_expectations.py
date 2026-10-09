"""Reviewed integration baselines for the current curated repository.

These constants describe the checked-in full repository, not isolated unit-test
fixtures. Update them only after reviewing the corresponding curated/Public
data change and the identity and relationship invariants in
``test_repository_baseline.py``.
"""

# Approved gap migration and Corpus Quality Batches A/C Phase 1 plus Batch C
# Waves 1, 2, 3A, 3B-1, and 3B-2: R188 is excluded; U017 has its explicit
# affiliations; T246 has evaluated localization; T024 and T136 retain only
# source attribution. Prior baselines remain in dated receipts.
CURRENT_REPOSITORY_BASELINE = {
    "public_unique_papers": 639,
    "public_map_source_papers": 617,
    "public_papers_with_map": 617,
    "public_papers_without_map": 22,
    "total_institution_registry_rows": 748,
    "active_canonical_institutions": 727,
    "non_active_institution_registry_rows": 21,
    "public_paper_institution_relationships": 1421,
    "institution_hierarchy_edges": 16,
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

CANONICAL_INSTITUTION_STATUS_TOTALS = {'active': 727, 'ignored': 6, 'merged': 15}

RELEASE_CANONICAL_INSTITUTION_STATUS_TOTALS = {
    "active": 650,
    "merged": 6,
    "ignored": 6,
}

CANONICAL_INSTITUTION_TYPE_TOTALS = {'university': 537, 'company': 88, 'research_unit': 98, 'other': 25}

ACTIVE_CANONICAL_INSTITUTION_TYPE_TOTALS = {'university': 529, 'company': 86, 'research_unit': 94, 'other': 18}

PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS = {'university': 606, 'research_unit': 137, 'other': 28, 'company': 128}

# Historical release artifacts are immutable; current effective venues have
# changed since the 2026-08-24 checkpoint.
RELEASE_PUBLICATION_TYPE_TOTALS = {"conference": 314, "journal": 167, "preprint": 64, "book": 1}

PUBLICATION_TYPE_TOTALS = {'conference': 389, 'preprint': 108, 'journal': 141, 'book': 1}

TASK_TOTALS = {'detection': 589, 'source_attribution': 85, 'localization': 43}

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
    "Explainable Artifacts for Synthetic Western Blot Source Attribution":
        "missing_affiliation_rows",
}

# New reviewed papers use the curated author-review ledger; the older manual
# marker-blocker report remains a historical input and is not rewritten.
CURATED_PAPERS_AWAITING_AFFILIATIONS = {
    "Beyond Visual Forensics: Auditing Multimodal Robustness for Synthetic Medical Image Detection",
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
    'A Multi-View and Confusion-Guided Ensemble Framework for Robust Synthetic Image Attribution',
    'ILLUSION: Unveiling Truth with a Comprehensive Multi-Modal, Multi-Lingual Deepfake Dataset',
    'Abductive Corroboration of Probabilistic AI Models for Forensic Synthetic Media Detection',
    'Conditional Uncertainty-Aware Political Deepfake Detection with Stochastic Convolutional Neural Networks',
    'Deep Learning for CGI and Visual Forgery Detection: A Comprehensive Survey',
    'Detecting Violent Deepfakes: Dataset and a Compact Attention Network with Multi-Scale Supervision',
    'ImageTrust: Multi-Backbone Fusion for AI-Generated Image Detection with Calibrated Uncertainty',
    'Detecting AI-Generated Forgeries via Iterative Manifold Deviation Amplification',
    'Scalable Black-Box Model Attribution for Images',
    'UniAIDet: A Unified and Universal Benchmark for AI-Generated Image Content Detection and Localization',
    'Detective SAM: Adaptive AI-Image Forgery Localization',
    'Fractal Characterization of Low-Correlation Signals in AI-Generated Image Detection',
    'SPECTRA-Net: Scalable Pipeline for Explainable Cross-Domain Tensor Representations for AI-Generated Images Detection',
    'DeCLIP: Decoding CLIP Representations for Deepfake Localization',
    'FUSE: Unifying Spectral and Semantic Cues for Robust AI-Generated Image Detection',
    'Weakly-Supervised Deepfake Localization in Diffusion-Generated Images',
}
