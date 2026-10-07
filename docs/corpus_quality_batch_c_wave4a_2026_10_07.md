# Corpus Quality Batch C External Evidence and Adjudication — Wave 4A

Adjudication date: 2026-10-07.

Scope: finalized R1 dataset-role adjudication for R099, R176, R190, and R455 only. This wave asks whether a reusable dataset or data resource is itself a substantive paper contribution. It does not adjudicate method, benchmark, analysis-study, or task labels. Exactly one primary full paper was attempted per case. R099 is the sole authoritative research-type correction.

| Review | Paper | Current types before adjudication | Primary source | Dataset/resource contribution | Reuse evidence | Adjudication | Evidence outcome | Final disposition | Final/proposed types |
|---|---|---|---|---|---|---|---|---|---|
| R099 | *Fake-HR1: Rethinking Reasoning of Vision Language Model for Synthetic Image Detection* | `method;dataset` | [Authoritative arXiv paper](https://arxiv.org/pdf/2602.10042) | The claimed contributions are the hybrid-reasoning framework and Fake-HR1 model. An unnamed dual-mode training mixture uses existing GenImage and FakeClue data: 1.834M non-reasoning and 94,188 reasoning samples for SFT, then 15,712 FakeClue samples after reject sampling for RL. | The mixture is method-training input, not a standalone data contribution or released resource. | `EXPERIMENTAL_DATA_ONLY_NO_DATASET` | `EVIDENCE_RESOLVED_CHANGE` | `REMEDIATION_APPLIED` | `method` |
| R176 | *PRADA: Probability-Ratio-Based Attribution and Detection of Autoregressive-Generated Images* | `method;dataset` | [Official CVF paper](https://openaccess.thecvf.com/content/CVPR2026F/papers/Damm_PRADA_Probability-Ratio-Based_Attribution_and_Detection_of_Autoregressive-Generated_Images_CVPRF_2026_paper.pdf) | Not established; the single permitted official PDF returned an internal retrieval error. | Not established. | `EVIDENCE_STILL_INSUFFICIENT` | `EVIDENCE_STILL_INSUFFICIENT` | `REMEDIATION_NOT_APPLIED` | unchanged; unresolved |
| R190 | *Representation and Reference Selection in Training-Free Synthetic Image Attribution* | `dataset;analysis_study` | [Authoritative arXiv paper](https://arxiv.org/pdf/2607.12052) | The contribution list explicitly claims BC-Attr-6 and COCO-Attr. BC-Attr-6 has 12,000 images from 10 generators across six categories, split into 1,200 queries and 10,800 references. COCO-Attr uses the same generators and MSCOCO captions, with 1,000 held-out queries and remaining images as references. | The named datasets, documented construction, and query/reference specifications support reuse as an attribution resource. A public-download statement is not required under R1 when the resource is a substantive contribution. | `DATASET_ROLE_SUPPORTED` | `EVIDENCE_RESOLVED_NO_CHANGE` | `REMEDIATION_NOT_REQUIRED` | retain `dataset;analysis_study` |
| R455 | *Deep Image Fingerprint: Towards Low Budget Synthetic Image Detection and Model Lineage Analysis* | `method;dataset` | [Official CVF paper](https://openaccess.thecvf.com/content/WACV2024/papers/Sinitsa_Deep_Image_Fingerprint_Towards_Low_Budget_Synthetic_Image_Detection_and_WACV_2024_paper.pdf) | Not established; the single permitted official PDF returned an internal retrieval error. | Not established. | `EVIDENCE_STILL_INSUFFICIENT` | `EVIDENCE_STILL_INSUFFICIENT` | `REMEDIATION_NOT_APPLIED` | unchanged; unresolved |

## Resolution

- `DATASET_ROLE_SUPPORTED = 1`
- `EXPERIMENTAL_DATA_ONLY_NO_DATASET = 1`
- `EVIDENCE_STILL_INSUFFICIENT = 2`
- `EVIDENCE_RESOLVED_CHANGE = 1`
- `EVIDENCE_RESOLVED_NO_CHANGE = 1`
- `REMEDIATION_APPLIED = 1`
- `REMEDIATION_NOT_REQUIRED = 1`
- `REMEDIATION_NOT_APPLIED = 2`
- External Batch C unresolved: `23 → 21`
- Research-type evidence: `15 → 13`
- Task evidence remains 7; institution evidence remains 1.
- T527 remains separate and is excluded from the external-evidence count. Total unresolved Batch C including T527 is 22.

The four-document budget was exhausted exactly. R176 and R455 stopped after their first terminal retrieval error; no alternate version, supplement, or mirror was substituted. R099 changes from `method;dataset` to `method`. R190 remains `dataset;analysis_study`. Public outputs are regenerated deterministically from the authoritative curated taxonomy; no public JSON is edited by hand.

## Local execution and validation

This adjudication reused the evidence already collected. No browsing, API call, download, alternate-source retrieval, or R176/R455 retry was performed.

The isolated worktree required 104 ignored operational inputs consumed by the offline refresh: `web/data/openalex_candidate_map_data.json`, `data/processed/openalex_candidate_papers.csv`, `data/processed/openalex_candidate_papers_in_scope.csv`, `data/processed/openalex_candidate_affiliations.csv`, `data/processed/institution_resolution_cache.json`, and 99 `data/raw/openalex/*.json` abstract-enrichment captures. The first two were already present; the other 102 were identified from the pipeline dependency chain and copied from the primary checkout before one complete refresh. Each copy was verified against its source and made read-only.

Historical validation additionally required 14 ignored baseline fixtures: `data/manual/institution_consistency_audit.csv`; four logs and five staged CSVs under `data/processed/neurips_2026_targeted_gap_fill_2026_10/`; and four archived `.DS_Store` files under the Tier 1, Tier 2 high-priority, and Tier 2 normal-priority baseline directories. All came from existing local copies with the exact recorded checksums and were made read-only. None of these 118 input files belongs to the 128 excluded-file inventory, and none is part of this commit. The primary checkout and its branding files remained read-only throughout.

The CSV correction preserves all unrelated bytes, including the 16 embedded CRLF sequences in each authoritative CSV. Exactly one physical line changes per CSV. R176, R190, and R455 authoritative rows are byte-equivalent to the baseline. Every public paper and relationship outside R099 is semantically identical, in the same order; R099 changes only research types and their review provenance. The only other generated differences are the established export timestamp and audit input hash.

| Corpus measure | Before | After |
|---|---:|---:|
| Public papers | 639 | 639 |
| Formal publications | 531 | 531 |
| Mapped papers | 617 | 617 |
| Relationship rows | 1,421 | 1,421 |
| Unique paper–institution pairs | 1,421 | 1,421 |

| Taxonomy label | Before | After |
|---|---:|---:|
| detection | 590 | 590 |
| source_attribution | 85 | 85 |
| localization | 42 | 42 |
| method | 547 | 547 |
| dataset | 133 | 132 |
| benchmark | 88 | 88 |
| survey | 20 | 20 |
| analysis_study | 78 | 78 |

Focused validation passed 122 tests and 24 subtests. The final full suite passed 1,671 tests and 389 subtests with zero failures and the two existing `PytestReturnNotNoneWarning` warnings. The first full-suite run passed 1,657 tests and failed 14 historical checks because four ignored archived `.DS_Store` inputs were absent; the final full run followed the verified local fixture correction. No assertion was weakened. Earlier focused environment failures were resolved using locally installed Python 3.14 and pytest 9.1.1 plus the checksum-verified historical fixtures, without installing dependencies.

Curated-database, public-preview, paper-exclusion, and key-paper-audit validators all returned zero errors. Existing validator warnings remain: curated database 252, public papers 23, map 0, paper exclusions 2. A second offline regeneration, solely for reproducibility, produced identical bytes for both public exports and all five companion report files, with no tracked file changes. Historical Wave 3A and Wave 3B-2 boundary tests now read their exact adjudicated commits; their current-case checks remain in place.

- `EXPORT_REPRODUCIBLE = 1`
- `UNEXPECTED_CHANGED = 0`
- `FROZEN_NEURIPS_CHANGED = 0`
- `PREEXISTING_LOCAL_FILES_CHANGED = 0`
- `7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

The remaining Batch C ledger is recomputed from Phase 1 residual triage and the finalized wave outcomes: task evidence 7, institution evidence 1, research-type evidence 13, external total 21, and T527 maintainer scope judgment 1, for 22 unresolved actions. Batch B remains 159; T527, U010, the UCSB provenance records, and all frozen NeurIPS material remain unchanged.
