"""Reviewed integration baselines for the current curated repository.

These constants describe the checked-in full repository, not isolated unit-test
fixtures. Update them only after reviewing the corresponding curated/Public
data change and the identity and relationship invariants in
``test_repository_baseline.py``.
"""

# Approved gap migration and Corpus Quality Batches A/C Phase 1 plus Batch C
# Waves 1, 2, 3A, 3B-1, and 3B-2: R188 is excluded; U017 has its explicit
# affiliations; T246 has evaluated localization; T024 and T136 retain only
# source attribution. T527 closeout excludes training-image retrieval from the
# narrow forensic scope. Batch B B1A additionally excludes the L015 user study
# and P562 industrial defect detector. B1B accepts R137 benchmark and R611
# analysis-study contributions. B1C excludes P490 through the reversible scope
# registry without changing historical taxonomy. The approved literature import
# adds 39 papers; B1D removes only T579 source attribution, retaining detection
# and method. B1E removes only T056/T345 source attribution, retaining detection
# and their research types. B1H changes only R566 from method to analysis_study;
# B1I adds only the independently reviewed R574 benchmark contribution;
# B1J adds the R100 dataset and R400 benchmark roles; task totals, prior
# baselines and literature additions remain frozen. B1K removes only the R542
# benchmark role, retaining survey and all task/scope assignments. B1L adds only
# the R181/R335 dataset roles, preserving methods, benchmark, tasks and scopes.
# B1M adds only the R034/R359 benchmark roles; identities, publication fields,
# institutions, task labels and image scopes remain unchanged.
# B1N adds only R596's independently reusable Attribution88 benchmark role;
# R234's atomic dataset/benchmark review and bibliographic observation stay open.
CURRENT_REPOSITORY_BASELINE = {
    "public_unique_papers": 674,
    "public_map_source_papers": 613,
    "public_papers_with_map": 613,
    "public_papers_without_map": 61,
    "total_institution_registry_rows": 748,
    "active_canonical_institutions": 727,
    "non_active_institution_registry_rows": 21,
    "public_paper_institution_relationships": 1410,
    "institution_hierarchy_edges": 16,
    "institution_aliases": 120
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

PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS = {'university': 603, 'research_unit': 136, 'company': 127, 'other': 27}

# Historical release artifacts are immutable; current effective venues have
# changed since the 2026-08-24 checkpoint.
RELEASE_PUBLICATION_TYPE_TOTALS = {"conference": 314, "journal": 167, "preprint": 64, "book": 1}

PUBLICATION_TYPE_TOTALS = {'conference': 400, 'journal': 156, 'preprint': 117, 'book': 1}

TASK_TOTALS = {'detection': 621, 'source_attribution': 84, 'localization': 45}


CURRENT_CORPUS_COUNTS = {
    "public": 674,
    "formal": 557,
    "mapped": 613,
    "unmapped": 61,
    "relationship_rows": 1410,
    "unique_paper_institution_pairs": 1410
}

RESEARCH_TYPE_TOTALS = {'method': 578, 'analysis_study': 82, 'survey': 21, 'dataset': 137, 'benchmark': 94}

CURRENT_TAXONOMY_TOTALS = {**TASK_TOTALS, **RESEARCH_TYPE_TOTALS}

# Exact contributions of the 39 reviewed bibliography additions.
LITERATURE51_TASK_ADDITIONS = {'detection': 36, 'source_attribution': 3, 'localization': 2}
LITERATURE51_RESEARCH_ADDITIONS = {'method': 34, 'dataset': 2, 'benchmark': 1, 'survey': 1, 'analysis_study': 4}
LITERATURE51_TAXONOMY_ADDITIONS = {**LITERATURE51_TASK_ADDITIONS, **LITERATURE51_RESEARCH_ADDITIONS}

CURRENT_TAXONOMY_SUPPRESSED_ROWS = 48

CURRENT_EMPTY_CORE_TASK_TITLES = {'TWIGMA: A Dataset of AI-Generated Images with Metadata from Twitter'}

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
# Bibliography imports have unresolved affiliations without a completed
# paper-specific author affiliation review; keep that distinct from reviewed
# unresolved author events in the earlier medical-paper audit.
BIBLIOGRAPHY_ONLY_PENDING_AFFILIATIONS = {
    'DinoLizer: Separating VAE and Diffusion Artifacts in Generative Inpainting Localization',
    'A Sanity Check for AI-Generated Underwater Image Detection',
    'ASAP: Visual Analytics for Identifying and Analyzing Image Patterns in AI-Generated Images',
    'Asymmetric Anchoring: Opening the MLLM Black Box for Forgery Detection',
    'DSC2F: A Multimodal AI-Generated Image Detection System Using Dual-Stream Convolutional Neural Networks with Fast Fourier Transform',
    'Dissecting Agentic Forensics: The Role of Triage, Prompting, and Evidence Arbitration in Open-World Fake Image Detection',
    'Diversity Matters: Dataset Diversification and Dual-Branch Network for Generalized AI-Generated Image Detection',
    'Dual-Branch Asymmetric Discrepancy Learning Based on Fake Image Pattern-Coexistence for AI-Generated Image Detection',
    'Dual-Path AI-Generated Image Detection: Leveraging Texture-Rich and Texture-Poor Patches with Global Semantic Features',
    'Explainable AI-Generated Image Forensics: A Low-Resolution Perspective with Novel Artifact Taxonomy',
    'Exploring Real–Synthetic Boundaries in Diffusion Latent Space',
    'Face-Trace: Open-Set Attribution and Progressive Discovery of Synthetic Face Generators',
    'GRE-Net: A Forgery Image Detection Framework Based on Gradient Feature and Reconstruction Error',
    'Hierarchical Channel Stacking: A Structured Decision Framework for AI-Generated Image Detection',
    'Improving Generalization in AI-Generated Facial Image Detection via Explainable Recovery',
    'Improving Synthesized Image Detection by Disentangling Generator-Shared and Generator-Specific Image Artifacts',
    'LEGO: LoRA-Enabled Generator-Oriented Framework for Synthetic Image Detection',
    'Leveraging Arbitrary Data Sources for AI-Generated Image Detection Without Sacrificing Generalization',
    'Lightweight AI-Generated Image Detection Based on Enhanced Common Artifact Features',
    'LiteUpdate: A Lightweight Framework for Updating AI-Generated Image Detectors',
    'MF²DA: Multi-Level Feature Fusion for Robust Detection and Attribution of Universal AI-Generated Images',
    'MIDNet: Multi-Scale Interaction and Dynamic Hard-Sample Mining for AI-Generated Image Detection',
    'MS-DCL: Multi-Scale Decoupled Contrastive Learning for Universal AI-Generated Image Detection',
    'One Patch Is Not Enough: A General Framework for Full-Resolution AI Image Detection',
    'Proto-LeakNet: Towards Signal-Leak Aware Attribution in Synthetic Human Face Imagery',
    'REALIS: A Curated Dataset for Studying the Challenges of AI Image Detection',
    'RED: Reconstruction Evolution Dynamics for Generalizable AI-Generated Image Detection',
    'Relative Patch Response Learning for Generalizable AI-Generated Image Detection',
    'Revisiting DIRE: Towards Universal AI-Generated Image Detection',
    'Robust AIGC Image Detection via Unidirectional Consistency Regularization',
    'S-AODP++: Structure-Aware AOI-Guided Scanpath Attention for AI-Generated Image Identification',
    'SCA-Det: A Structure-Context Artifact Detector for AI-Generated Image Detection',
    'SDA-Det: A Subpixel-Aware Dual-Domain Artifact Detector for AI-Generated Image Detection',
    'Spotting the Fakes: A Deep Dive Into GAN-Generated Face Detection',
    'Structure Searchable Network Model for Deepfake Image Detection',
    'Synthetic Frequency Patterns Injection for Data-Agnostic Deepfake Detection',
    'S²F-Net: A Robust Spatial-Spectrum Fusion Framework for Cross-Model AIGC Detection',
    'Unifying Semantic Priors and High-Frequency Traces: Enhancing V-JEPA with Mixture-of-Experts for Robust Synthetic Image Forensics',
    'Unleashing the Potential of Vision-Language Models for Generalizable AI-Generated Image Detection',
}

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
