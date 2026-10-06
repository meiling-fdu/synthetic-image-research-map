# Corpus Quality Batch C External Evidence — Wave 1

Date: 2026-10-06

Scope: P550, P586, P610, P633, and R188 only. The maintainer accepted all five evidence findings and this report records their final adjudication. No Batch B action, other Batch C action, T527 classification, Batch D action, or NeurIPS 7+1 record was changed.

## Final adjudication

| Review ID | Paper | Source(s) | Final disposition | Applied result |
|---|---|---|---|---|
| P550 | *Detecting GAN-generated synthetic images using semantic inconsistencies* | [Official IS&T record](https://library.imaging.org/ei/articles/35/4/MWSF-380) | `WAVE1_RESOLVED_NO_CHANGE` | Retained `Electronic Imaging`, publication type `journal`, and an empty track. MWSF 2023 remains event context in the evidence layer. |
| P586 | *Deep Learning applied to Road Accident Detection with Transfer Learning and Synthetic Images* | [Official ScienceDirect record](https://www.sciencedirect.com/science/article/pii/S2352146522006263) | `WAVE1_RESOLVED_NO_CHANGE` | Retained `Transportation Research Procedia`, publication type `journal`, and an empty track. The conference relationship remains evidence context. |
| P610 | *Detection, Attribution and Localization of GAN Generated Images* | [Official IS&T record](https://library.imaging.org/ei/articles/33/4/art00007) | `WAVE1_RESOLVED_NO_CHANGE` | Retained `Electronic Imaging`, publication type `journal`, and an empty track. The symposium/MWSF relationship remains event context. |
| P633 | *Detecting GAN Generated Fake Images Using Co-Occurrence Matrices* | [Official IS&T record](https://library.imaging.org/ei/articles/31/5/art00008) | `WAVE1_RESOLVED_NO_CHANGE` | Retained `Electronic Imaging`, publication type `journal`, and an empty track. The symposium/MWSF relationship remains event context. |
| R188 | *Reasoning-Aware AIGC Detection via Alignment and Reinforcement* | [Official ACL Anthology record](https://aclanthology.org/2026.findings-acl.1043/); [authoritative arXiv record](https://arxiv.org/abs/2604.19172) | `WAVE1_RESOLVED_CHANGE` / `SOURCE_RECORD_CORRUPTION` | Added active exclusion `exclusion:713b062c413880d72166` with schema reason `out_of_scope` and review semantics `TEXT_ONLY_OUT_OF_SCOPE`. The text-only paper and its three relationships were removed from public outputs through the deterministic exclusion gate. |

V1 required no schema change. The archival-container and event distinction is preserved in the evidence layer without adding a venue event or track field.

## R188 audit trail

The ACL and arXiv records agree on the title, four authors, and the work's text-generation subject. They describe AIGC-text-bank and REVEAL for LLM-generated text/authorship detection and provide no synthetic-image forensic evidence.

The active exclusion preserves the canonical paper ID, title, year, DOI, ACL identity, arXiv identity, OpenAlex identity, source provenance, and Wave 1 evidence as a single historical work. The curated paper, taxonomy, and affiliation records remain available for audit; the public paper and map exports contain no active match by paper ID, DOI, arXiv ID, normalized title, ACL identifier, or OpenAlex URL.

## Corpus impact

| Measure | Before | After | Change |
|---|---:|---:|---:|
| Public papers | 640 | 639 | -1 |
| Formal publications | 532 | 531 | -1 |
| Mapped papers | 617 | 616 | -1 |
| Unmapped papers | 23 | 23 | 0 |
| Paper–institution relationship rows | 1,422 | 1,419 | -3 |
| Unique paper–institution pairs | 1,422 | 1,419 | -3 |

## Taxonomy impact

| Dimension | Before | After | Change |
|---|---:|---:|---:|
| Detection | 593 | 592 | -1 |
| Source attribution | 85 | 85 | 0 |
| Localization | 41 | 41 | 0 |
| Method | 548 | 547 | -1 |
| Dataset | 133 | 133 | 0 |
| Benchmark | 88 | 88 | 0 |
| Survey | 20 | 20 | 0 |
| Analysis study | 78 | 78 | 0 |

## Reconciliation

- `WAVE1_RESOLVED_NO_CHANGE = 4`
- `WAVE1_RESOLVED_CHANGE = 1`
- `WAVE1_STILL_INSUFFICIENT = 0`
- External-primary-source actions before Wave 1: 35.
- Actions resolved by Wave 1: 5.
- External-primary-source actions remaining: 30.
- T527 remains `MAINTAINER_SCOPE_JUDGMENT_REQUIRED` with state `SCOPE_OR_TASK_EVIDENCE_REQUIRED`.
- Total unresolved Batch C actions: 31.

The structured evidence and adjudication ledger is `data/raw/corpus_quality_batch_c_wave1_2026_10_06/evidence_manifest.json`. It contains six authoritative-document references for five actions. No raw webpage, search-result page, mirror, transient error response, or newly retrieved evidence was added during adjudication.
