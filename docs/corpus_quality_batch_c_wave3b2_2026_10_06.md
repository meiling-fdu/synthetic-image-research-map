# Corpus Quality Batch C External Evidence and Adjudication — Wave 3B-2

Evidence date: 2026-10-06. Completed: 2026-10-07.

Scope: locked T1 attribution-versus-detection review for T024, T136, T137, and T141 only. The resumed review used only the previously downloaded T024 and T136 primary papers. The approved adjudication removes `detection` from T024 and T136; T137 and T141 remain unchanged.

| Review | Paper | Primary source | Evaluated decision/class space | Real-image role | Authenticity task/metric | Attribution/homology task | Adjudication | Evidence outcome | Final disposition | Final taxonomy |
|---|---|---|---|---|---|---|---|---|---|---|
| T024 | *AI-Generated Image Homology Detection* | [Official Springer paper](https://link.springer.com/content/pdf/10.1007/978-981-92-2856-0_1.pdf) | Binary image-pair decision: homologous versus non-homologous | Real-real pairs are homologous; real-generated pairs can be non-homologous. Real is a source category in pair construction, not an individual authenticity class. | None. Accuracy and average precision score same/different-source homology. | Architecture-level same-source verification over real, GAN, and diffusion image pairs | `ATTRIBUTION_ONLY_NO_DETECTION` | `EVIDENCE_RESOLVED_CHANGE` | `REMEDIATION_APPLIED` | `source_attribution` |
| T136 | *ImageAttributionBench: How Far Are We from Generalizable Attribution?* | [Authoritative arXiv paper](https://arxiv.org/pdf/2605.12967) | 32-way attribution: one real source class plus 31 generator classes; balanced and semantic-split protocols | One class in the attribution label space and semantic source material; no separate binary protocol | None. No binary accuracy/AUROC or separate detection stage; detection methods are adapted to attribution. | Attribution accuracy under clean, degraded, and cross-semantic conditions, with 32-source confusion matrices | `ATTRIBUTION_ONLY_NO_DETECTION` | `EVIDENCE_RESOLVED_CHANGE` | `REMEDIATION_APPLIED` | `source_attribution` |
| T137 | *IncreFA: Breaking the Static Wall of Generative Model Attribution* | [Official CVF paper](https://openaccess.thecvf.com/content/CVPR2026/papers/Qin_IncreFA_Breaking_the_Static_Wall_of_Generative_Model_Attribution_CVPR_2026_paper.pdf) | Not established; the bounded official transfer did not complete | Not established | Not established | Not established | `EVIDENCE_STILL_INSUFFICIENT` | `EVIDENCE_STILL_INSUFFICIENT` | `REMEDIATION_NOT_APPLIED` | unchanged |
| T141 | *Learning a Semantic Similarity Orthogonal Space for Model-Level AI-Generated Image Source Attribution* | [Official Wiley paper](https://onlinelibrary.wiley.com/doi/pdf/10.1111/exsy.70359) | Not established; the official PDF returned HTTP 403 | Not established | Not established | Not established | `EVIDENCE_STILL_INSUFFICIENT` | `EVIDENCE_STILL_INSUFFICIENT` | `REMEDIATION_NOT_APPLIED` | unchanged |

## T024

The paper expressly separates homology from authenticity detection. Its classifier receives an image pair and predicts whether the sources match. The balanced protocol labels real-real and same-generator pairs as homologous and real-generated or different-generator pairs as non-homologous. Accuracy and average precision evaluate this pairwise relationship, not whether an individual image is real or generated. Under T1, the evidence supports source attribution/homology only. The approved remediation changes `detection;source_attribution` to `source_attribution`.

## T136

ImageAttributionBench defines image attribution as identifying the source model of an AI-generated image and evaluates methods only through attribution protocols. Its dataset contains 20,000 real images and images from 31 generators; the real samples form one source label in the 32-way classifier. The standard and semantic-split tasks report multiclass attribution accuracy, including under degradation. No separate real-vs-generated task or metric is defined, and methods originally designed for detection are explicitly adapted to attribution. Under T1, real-class presence does not support a detection label. The approved remediation changes `detection;source_attribution` to `source_attribution`.

## T137 and T141

T137 remains `EVIDENCE_STILL_INSUFFICIENT` because the single permitted official CVF primary-document transfer did not complete within the bounded retrieval window. T141 remains `EVIDENCE_STILL_INSUFFICIENT` because the single permitted official Wiley primary PDF returned HTTP 403. Neither source was retried, and no alternate version or local metadata was used to fill the gaps.

## Resolution

- `DETECTION_TASK_SUPPORTED = 0`
- `ATTRIBUTION_ONLY_NO_DETECTION = 2`
- `EVIDENCE_STILL_INSUFFICIENT = 2`
- External Batch C unresolved: `26 → 24`
- Remaining task evidence: `10 → 8`
- Institution evidence remains 1; research-type evidence remains 15.
- T527 is outside this external-evidence count and was not touched.
- External unresolved plus T527: `24 + 1 = 25`.

Four primary-document targets exhausted the wave budget. Two previously downloaded local papers yielded usable evidence during the resumed review. No additional source was retrieved and no source copy was stored in the repository. Corpus identity remains 639 public papers, 531 formal publications, 617 mapped papers, 1,421 relationship rows, and 1,421 unique paper–institution pairs. The direct taxonomy effect is detection `592 → 590`; source attribution remains 85, localization 42, method 547, dataset 133, benchmark 88, survey 20, and analysis study 78.
