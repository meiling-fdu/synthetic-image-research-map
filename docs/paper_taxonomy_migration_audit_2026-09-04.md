# Paper taxonomy migration audit — 2026-09-04

Audited current public paper identities: **613 / 613**. No literature was added and no source record was deleted. Six records from the prior 582-paper public corpus are preserved as active curated exclusions after focused scope review.

The registry is joined after candidate, preservation, curated-override, version-merge, and exclusion identity reconciliation. The 415 current public identities represented in `papers.csv` reuse their valid prior audit decisions; the other 198 use the stored abstract and linked DOI/arXiv/OpenAlex/project evidence. Taxonomy review state is independent of bibliographic and affiliation review state.

`localization` requires an explicit localization task or evaluation; explanations and heatmaps do not qualify. `generative_editing` requires evidence that a source image is modified by a generative model.

## Focused review resolution

The follow-up audit started with **62 papers** having at least one uncertain taxonomy dimension. All dimension-level cases were resolved: tasks **5 → 0**, image scopes **28 → 0**, and research types **39 → 0**. Bibliographic and affiliation review fields were not part of this registry update.

## tasks

| Value | Papers |
|---|---:|
| `detection` | 577 |
| `source_attribution` | 77 |
| `localization` | 18 |

Multi-label papers: **59**. Taxonomy review cases: **0**.

Exact multi-label combinations:

| Value | Papers |
|---|---:|
| `detection + localization` | 14 |
| `detection + source_attribution` | 43 |
| `detection + source_attribution + localization` | 2 |

Pairwise overlaps (inclusive):

| Value | Papers |
|---|---:|
| `detection + localization` | 16 |
| `detection + source_attribution` | 45 |
| `source_attribution + localization` | 2 |

## image_scopes

| Value | Papers |
|---|---:|
| `fully_generated` | 521 |
| `deepfake` | 161 |
| `generative_editing` | 25 |
| `traditional_manipulation` | 13 |

Multi-label papers: **90**. Taxonomy review cases: **0**.

Exact multi-label combinations:

| Value | Papers |
|---|---:|
| `fully_generated + generative_editing + deepfake` | 8 |
| `fully_generated + generative_editing` | 6 |
| `fully_generated + deepfake` | 65 |
| `generative_editing + traditional_manipulation` | 2 |
| `fully_generated + generative_editing + traditional_manipulation` | 1 |
| `fully_generated + generative_editing + deepfake + traditional_manipulation` | 2 |
| `generative_editing + deepfake + traditional_manipulation` | 1 |
| `fully_generated + deepfake + traditional_manipulation` | 3 |
| `fully_generated + traditional_manipulation` | 2 |

Pairwise overlaps (inclusive):

| Value | Papers |
|---|---:|
| `fully_generated + generative_editing` | 17 |
| `fully_generated + deepfake` | 78 |
| `generative_editing + deepfake` | 11 |
| `generative_editing + traditional_manipulation` | 6 |
| `fully_generated + traditional_manipulation` | 8 |
| `deepfake + traditional_manipulation` | 6 |

## research_types

| Value | Papers |
|---|---:|
| `analysis_study` | 58 |
| `method` | 527 |
| `survey` | 23 |
| `benchmark` | 69 |
| `dataset` | 112 |

Multi-label papers: **145**. Taxonomy review cases: **0**.

Exact multi-label combinations:

| Value | Papers |
|---|---:|
| `benchmark + analysis_study` | 1 |
| `method + dataset` | 54 |
| `method + dataset + benchmark` | 22 |
| `dataset + benchmark + analysis_study` | 4 |
| `method + analysis_study` | 23 |
| `method + dataset + analysis_study` | 1 |
| `dataset + benchmark` | 17 |
| `dataset + analysis_study` | 4 |
| `method + benchmark + analysis_study` | 3 |
| `method + survey` | 2 |
| `method + benchmark` | 12 |
| `method + dataset + survey` | 1 |
| `benchmark + survey` | 1 |

Pairwise overlaps (inclusive):

| Value | Papers |
|---|---:|
| `benchmark + analysis_study` | 8 |
| `method + dataset` | 78 |
| `method + benchmark` | 37 |
| `dataset + benchmark` | 43 |
| `dataset + analysis_study` | 9 |
| `method + analysis_study` | 27 |
| `method + survey` | 3 |
| `dataset + survey` | 1 |
| `benchmark + survey` | 1 |

## Taxonomy-only review cases

### tasks

Cases: **0**.

| Value | Papers |
|---|---:|

| Taxonomy ID | Title | Reason |
|---|---|---|

### image_scopes

Cases: **0**.

| Value | Papers |
|---|---:|

| Taxonomy ID | Title | Reason |
|---|---|---|

### research_types

Cases: **0**.

| Value | Papers |
|---|---:|

| Taxonomy ID | Title | Reason |
|---|---|---|

## Eight originally reviewed empty-task records

| Paper | Decision | Basis |
|---|---|---|
| "That's Another Doom I Haven't Thought About": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation | Remain empty | In-scope analysis of labels and human recognition of AI-image misinformation. |
| DynEval: Holistic Evaluations of T2I Generative Models in the Wild | Excluded after scope review | Generator-quality evaluator/datasets, without a detection, attribution, or localization task. |
| DeepArt: A Benchmark to Advance Fidelity Research in AI-Generated Content | Excluded after scope review | Generator-fidelity benchmark, without a controlled taxonomy task. |
| TWIGMA: A Dataset of AI-Generated Images with Metadata from Twitter | Remain empty | In-scope dataset/analysis resource; it does not evaluate a controlled taxonomy task. |
| How spammers and scammers leverage AI-generated images on Facebook for audience growth | Excluded after scope review | Societal-use analysis, without a controlled taxonomy task. |
| Does an emotional connection to art really require a human artist? Emotion and intentionality responses to AI- versus human-created art and impact on aesthetic experience | Excluded after scope review | Aesthetic-perception study, without a controlled taxonomy task. |
| Fourier Spectrum Discrepancies in Deep Network Generated Images | Add detection | Reports real/generated classification accuracy for a proposed detector. |
| Watch Your Up-Convolution: CNN Based Generative Deep Neural Networks Are Failing to Reproduce Spectral Distributions | Add detection | Explicitly evaluates detection of generated data on public benchmarks. |

## Focused corpus-scope review decisions

All six reviewed records are preserved in the layered source data and curated exclusion history but omitted from the current public paper and map exports.

| Paper | Decision | Reason | Authoritative source |
|---|---|---|---|
| Can Model Attribution Bridge AI's Accountability Gap in Safety-Critical Domains? | `EXCLUDE_OUT_OF_SCOPE` | Generic remote-service model attribution; no image domain or image scope is established. | https://doi.org/10.1098/rsta.2025.0117 |
| Cascade learning from adversarial synthetic images for accurate pupil detection | `EXCLUDE_OUT_OF_SCOPE` | GAN-refined synthetic eyes are training augmentation for pupil localization on real images rather than a forensic target. | https://doi.org/10.1016/j.patcog.2018.12.014 |
| DynEval: Holistic Evaluations of T2I Generative Models in the Wild | `EXCLUDE_OUT_OF_SCOPE` | Evaluates T2I alignment and output quality rather than authenticity detection or source attribution. | https://arxiv.org/abs/2607.11199 |
| DeepArt: A Benchmark to Advance Fidelity Research in AI-Generated Content | `EXCLUDE_OUT_OF_SCOPE` | Benchmarks GPT-4 image-synthesis fidelity rather than image forensics. | https://arxiv.org/abs/2312.10407 |
| How spammers and scammers leverage AI-generated images on Facebook for audience growth | `EXCLUDE_OUT_OF_SCOPE` | Studies platform misuse and audience awareness rather than an image-forensic task. | https://doi.org/10.37016/mr-2020-151 |
| Does an emotional connection to art really require a human artist? Emotion and intentionality responses to AI- versus human-created art and impact on aesthetic experience | `EXCLUDE_OUT_OF_SCOPE` | Uses computer-generated art as a stimulus for aesthetic-response research rather than image forensics. | https://doi.org/10.1016/j.chb.2023.107875 |

The dimension-specific evidence tier, linked source, excerpt, status, and review reason are stored in `data/curated/paper_taxonomy.csv`.
