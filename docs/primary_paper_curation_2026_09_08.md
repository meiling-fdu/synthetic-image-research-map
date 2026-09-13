# Primary-source curation of ten reconciliation additions — 2026-09-08

This is the current curation audit. The earlier key-paper reconciliation report is a historical snapshot of addition-time review state. No checklist identities or ambiguous cases were re-adjudicated.

Bibliography, taxonomy, author affiliation and location are reviewed independently. A reviewed affiliation means the author–institution relationship is supported; it does not imply a verified coordinate. Campus/headquarters points are representative institutional geography, not personal work-location claims. Full curation requires no remaining material uncertainty.

Verified OpenAlex identities revealed existing July 13 exclusions for Provenance, PLADA and FusionDetect. The earlier reconciliation missed those exclusions because the new rows lacked those identifiers. All ten authoritative rows and their reviewed taxonomy remain in papers.csv and the evidence ledger; the public-only taxonomy registry omits the three excluded identities. No exclusion decision was changed. Public membership and curation completeness are independent.

| Title | Bibliography | Tasks | Image scopes | Research types | Verified institutions | Author–institution pairs | Markers | Public membership | Pending fields | Overall state |
|---|---|---|---|---|---|---|---|---|---|---|
| Detecting Generated Images by Real Images Only | arXiv preprint (2023) | detection | fully_generated;generative_editing;deepfake | method | Chongqing University of Posts and Telecommunications; Tsinghua University; University of California, San Diego | 7 | 3 | included | — | fully_curated |
| Provenance Detection for AI-Generated Images: Combining Perceptual Hashing, Homomorphic Encryption, and AI Detection Models | arXiv preprint (2025); workshop linkage unresolved | detection;source_attribution | fully_generated | method | Zellic; Massachusetts Institute of Technology; ZK Email; Newcastle University; Polish Academy of Sciences | 6 | 0 | excluded | Publication-version relation to CODEML/DINOHash is not established. \| Shree Singhi and Aayan Yadav each carry superscripts 1,2; only 2 (Zellic) is defined. Affiliation 1 remains absent. \| Locations for Zellic, ZK Email, Newcastle University and Polish Academy of Sciences remain pending. | unresolved |
| Prefilled Responses Enhance Zero-Shot Detection of AI-Generated Images | NeurIPS 2025 GenProCC workshop paper | detection | fully_generated;deepfake | method;analysis_study | Observatory on Social Media | 4 | 1 | included | — | fully_curated |
| Pay Less Attention to Deceptive Artifacts: Robust Detection of Compressed Deepfakes on Online Social Networks | arXiv preprint (2025) | detection | fully_generated;generative_editing;deepfake | method | University of Chinese Academy of Sciences; State Key Laboratory of Multimodal Artificial Intelligence Systems; Institute of Information Science, Beijing Jiaotong University | 9 | 0 | excluded | — | fully_curated |
| Redefining Generalization in Visual Domains: A Two-Axis Framework for Fake Image Detection with FusionDetect | arXiv preprint (2025) | detection | fully_generated | method;dataset;benchmark | Sharif University of Technology | 4 | 0 | excluded | — | fully_curated |
| LADLE-MM: Limited Annotation Based Detector with Learned Ensembles for Multimodal Misinformation | arXiv preprint (2025) | detection | deepfake | method | Sapienza University of Rome | 3 | 1 | included | — | fully_curated |
| UniAIDet: A Unified and Universal Benchmark for AI-Generated Image Content Detection and Localization | arXiv preprint (2025) | detection;localization | fully_generated;generative_editing;deepfake | dataset;benchmark;analysis_study | Wangxuan Institute of Computer Technology | 2 | 0 | included | Wangxuan Institute coordinates remain pending: official address is documented, but exact institutional geocoding returned no result. | bibliography_taxonomy_verified_affiliation_pending |
| Can VLMs Detect and Localize Fine-Grained AI-Edited Images? | arXiv preprint (2025) | detection;localization | generative_editing | method;dataset;benchmark | The Hong Kong University of Science and Technology (Guangzhou); Ant Group; Tsinghua University; Shandong University; Wuhan University | 13 | 5 | included | — | fully_curated |
| The SAFE Image Authenticity Challenge: Detecting and Localizing Partial and Fully Synthetic Manipulations | WACV 2026 workshop paper | detection;localization | fully_generated;generative_editing;traditional_manipulation | dataset;benchmark | Drexel University; Underwriters Laboratories; Aptima, Inc. | 7 | 2 | included | Underwriters Laboratories coordinates remain pending; the paper gives no office and an exact institution geocoder query returned no result. | bibliography_taxonomy_verified_affiliation_pending |
| Dynamic Ensemble of Deepfake Detectors Conditioned on CLIP Features | CVWW 2026 conference paper | detection | fully_generated;deepfake | method;dataset;benchmark | Czech Technical University in Prague | 2 | 1 | included | — | fully_curated |

## Review counts

```json
{
  "bibliography_verified": 9,
  "taxonomy_reviewed": 10,
  "affiliation_reviewed": 9,
  "fully_curated": 7,
  "marker_bearing": 6,
  "public_papers": 620,
  "public_mapped_papers": 613,
  "published_only": 520,
  "before_counts": {
    "public_papers": 623,
    "published_only": 519,
    "public_mapped_papers": 607,
    "map_records": 1425
  },
  "markerless": [
    "UniAIDet: A Unified and Universal Benchmark for AI-Generated Image Content Detection and Localization"
  ],
  "excluded": [
    "Provenance Detection for AI-Generated Images: Combining Perceptual Hashing, Homomorphic Encryption, and AI Detection Models",
    "Pay Less Attention to Deceptive Artifacts: Robust Detection of Compressed Deepfakes on Online Social Networks",
    "Redefining Generalization in Visual Domains: A Two-Axis Framework for Fake Image Detection with FusionDetect"
  ],
  "new_institutions": [
    "University of California, San Diego",
    "Zellic",
    "ZK Email",
    "Newcastle University",
    "Polish Academy of Sciences",
    "Observatory on Social Media",
    "State Key Laboratory of Multimodal Artificial Intelligence Systems",
    "Institute of Information Science, Beijing Jiaotong University",
    "Sharif University of Technology",
    "Wangxuan Institute of Computer Technology",
    "Underwriters Laboratories",
    "Aptima, Inc."
  ],
  "new_aliases": 0,
  "new_hierarchy_relationships": 4
}
```

## Strict regression audit

```json
{
  "pre_existing_changes": [],
  "pre_existing_rows_preserved": 5380,
  "appended_rows": {
    "data/curated/author_institution_mappings.csv": 24,
    "data/curated/institution_audit_log.csv": 91,
    "data/curated/institution_hierarchy.csv": 4,
    "data/curated/institution_location_audit_log.csv": 6,
    "data/curated/institution_location_review.csv": 6,
    "data/curated/institution_locations.csv": 6,
    "data/curated/institutions.csv": 12
  },
  "pre_existing_public_changes": [],
  "pre_existing_public_records_preserved": {
    "web/data/public_preview_papers.json": 613,
    "web/data/public_preview_map_data.json": 1425
  },
  "strong_identifier_duplicates": {}
}
```

## Evidence and unresolved decisions

### Detecting Generated Images by Real Images Only

Paper ID: `curated:8aa00584c346440e0c41`. Bibliography: reviewed; taxonomy: reviewed; affiliations: reviewed; locations: reviewed.

No remaining material curation uncertainty in inspected sources.

Public membership: included.



Primary evidence: [source 1](https://arxiv.org/abs/2311.00962) · [source 2](https://arxiv.org/pdf/2311.00962v1)

### Provenance Detection for AI-Generated Images: Combining Perceptual Hashing, Homomorphic Encryption, and AI Detection Models

Paper ID: `curated:2334b1774b5f65217e7b`. Bibliography: needs_review; taxonomy: reviewed; affiliations: needs_review; locations: needs_review.

arXiv v1, 2025-03-14, five authors. IIT Roorkee newsletter associates the title with ICML CODEML 2025, while the located DINOHash workshop record has a different title/author list. OpenReview full-text access returned 403/challenge; do not transfer workshop metadata or missing superscript 1 from that other work.

Public membership: excluded. Existing exclusions: exclusion-afa362e960d2495eb5c5b44c1431736e.

Exclusion identity trace: curated ID `curated:2334b1774b5f65217e7b`; formal DOI `none established`; arXiv `2503.11195`; OpenAlex https://openalex.org/W4417284156. Match: `openalex:https://openalex.org/w4417284156`; exclusion DOI `https://doi.org/10.48550/arxiv.2503.11195`; reason `other`; effective 2026-07-13T20:14:33Z. The unchanged exclusion predates this task.

Primary evidence: [source 1](https://arxiv.org/abs/2503.11195) · [source 2](https://arxiv.org/pdf/2503.11195v1) · [source 3](https://www.iitr.ac.in/mfsdsai/docs/MFSDSAI_Newsletter_July_2025.pdf) · [source 4](https://openreview.net/forum?id=HrGa8Mq2NE)

### Prefilled Responses Enhance Zero-Shot Detection of AI-Generated Images

Paper ID: `curated:168e13e349336a266783`. Bibliography: reviewed; taxonomy: reviewed; affiliations: reviewed; locations: reviewed.

No remaining material curation uncertainty in inspected sources.

Public membership: included.



Primary evidence: [source 1](https://arxiv.org/abs/2506.11031) · [source 2](https://arxiv.org/pdf/2506.11031v4) · [source 3](https://neurips.cc/virtual/2025/128273) · [source 4](https://neurips.cc/media/neurips-2025/Slides/128273.pdf)

### Pay Less Attention to Deceptive Artifacts: Robust Detection of Compressed Deepfakes on Online Social Networks

Paper ID: `curated:509324a7a8bc94c3eb78`. Bibliography: reviewed; taxonomy: reviewed; affiliations: reviewed; locations: reviewed.

No remaining material curation uncertainty in inspected sources.

Public membership: excluded. Existing exclusions: exclusion-bb870f305db948d18fb473d072844c48.

Exclusion identity trace: curated ID `curated:509324a7a8bc94c3eb78`; formal DOI `none established`; arXiv `2506.20548`; OpenAlex https://openalex.org/W4414989730. Match: `openalex:https://openalex.org/w4414989730`; exclusion DOI `https://doi.org/10.48550/arxiv.2506.20548`; reason `other`; effective 2026-07-13T20:15:50Z. The unchanged exclusion predates this task.

Primary evidence: [source 1](https://arxiv.org/abs/2506.20548) · [source 2](https://arxiv.org/pdf/2506.20548v1)

### Redefining Generalization in Visual Domains: A Two-Axis Framework for Fake Image Detection with FusionDetect

Paper ID: `curated:40d551857163fa643202`. Bibliography: reviewed; taxonomy: reviewed; affiliations: reviewed; locations: reviewed.

No remaining material curation uncertainty in inspected sources.

Public membership: excluded. Existing exclusions: exclusion-17447bd65e3b4aae98831c8d0bf68be0.

Exclusion identity trace: curated ID `curated:40d551857163fa643202`; formal DOI `none established`; arXiv `2510.05740`; OpenAlex https://openalex.org/W4414978765. Match: `openalex:https://openalex.org/w4414978765`; exclusion DOI `https://doi.org/10.48550/arxiv.2510.05740`; reason `other`; effective 2026-07-13T20:06:06Z. The unchanged exclusion predates this task.

Primary evidence: [source 1](https://arxiv.org/abs/2510.05740) · [source 2](https://arxiv.org/pdf/2510.05740v2)

### LADLE-MM: Limited Annotation Based Detector with Learned Ensembles for Multimodal Misinformation

Paper ID: `curated:fc87c72c7e8c831652ea`. Bibliography: reviewed; taxonomy: reviewed; affiliations: reviewed; locations: reviewed.

No remaining material curation uncertainty in inspected sources.

Public membership: included.



Primary evidence: [source 1](https://arxiv.org/abs/2512.20257) · [source 2](https://arxiv.org/pdf/2512.20257v1)

### UniAIDet: A Unified and Universal Benchmark for AI-Generated Image Content Detection and Localization

Paper ID: `curated:0e0f70c0146b624226ca`. Bibliography: reviewed; taxonomy: reviewed; affiliations: reviewed; locations: needs_review.

Wangxuan Institute coordinates remain pending: official address is documented, but exact institutional geocoding returned no result.

Public membership: included.



Primary evidence: [source 1](https://arxiv.org/abs/2510.23023) · [source 2](https://arxiv.org/pdf/2510.23023v1)

### Can VLMs Detect and Localize Fine-Grained AI-Edited Images?

Paper ID: `curated:4bafe8e39a3e39ed2088`. Bibliography: reviewed; taxonomy: reviewed; affiliations: reviewed; locations: reviewed.

No remaining material curation uncertainty in inspected sources.

Public membership: included.



Primary evidence: [source 1](https://arxiv.org/abs/2505.15644) · [source 2](https://arxiv.org/pdf/2505.15644v2)

### The SAFE Image Authenticity Challenge: Detecting and Localizing Partial and Fully Synthetic Manipulations

Paper ID: `curated:f0a62826c32151c731c7`. Bibliography: reviewed; taxonomy: reviewed; affiliations: reviewed; locations: needs_review.

Underwriters Laboratories coordinates remain pending; the paper gives no office and an exact institution geocoder query returned no result.

Public membership: included.



Primary evidence: [source 1](https://openaccess.thecvf.com/content/WACV2026W/SynRDinBAS/html/Nguyen_The_SAFE_Image_Authenticity_Challenge_Detecting_and_Localizing_Partial_and_WACVW_2026_paper.html) · [source 2](https://openaccess.thecvf.com/content/WACV2026W/SynRDinBAS/papers/Nguyen_The_SAFE_Image_Authenticity_Challenge_Detecting_and_Localizing_Partial_and_WACVW_2026_paper.pdf)

### Dynamic Ensemble of Deepfake Detectors Conditioned on CLIP Features

Paper ID: `curated:980afddea0a156b5020b`. Bibliography: reviewed; taxonomy: reviewed; affiliations: reviewed; locations: reviewed.

No remaining material curation uncertainty in inspected sources.

Public membership: included.



Primary evidence: [source 1](https://cmp.felk.cvut.cz/cvww2026/assets/pdfs/CVWW2026-31-final.pdf)

The field-specific rationales, exact author groupings, version notes, explicit code URLs, institution provenance and representative-location limitations are in `data/manual/primary_paper_curation_2026_09_08.json`. Full source PDFs and secondary/geocoding responses are cached separately under `data/raw/primary_curation_2026_09_08/`.

Regenerate with `python3 scripts/report_primary_paper_curation.py`; verify without writes with `--check`. Run `--regression-only` before a refresh to check source preservation independently of public outputs.
