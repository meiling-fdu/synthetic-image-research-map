# Corpus Quality Audit — Batch C decision sheet (2026-10-05)

**Decision preparation only.** Baseline: `0bc98c3e75636899e53114be3d9de0a71986990c`, following audit commit `67ba756bbddc71879a77630e5d918785d3a42e98`. No remediation, network access, export regeneration, staging, commit or push.

**Compression:** 41 actions on 40 paper identities → **12 reusable policy votes**. **6 actions are ready for explicit acceptance on existing evidence; 35 retain paper-specific evidence/interpretation gates.** Those 35 are not claimed resolved by a blanket policy vote. The policy target is achievable; reducing evidence gaps to a handful is not supported by the committed record.

Corpus stays **640 public / 532 formal / 617 mapped / 1,422 relationship rows / 1,422 unique pairs**. Actual remaining audit counts stay **B=159, C=41, D=1,752** until a separately authorized remediation records decisions.

Vote syntax: `T1=A, T2=A, T3=A, R1=A, R2=A, R3=A, R4=A, I1=A, I2=A, P1=A, V1=A, V3=A`. **A** accepts the rule and the explicitly READY dispositions; **H** holds; an alternative should specify the changed rule. HOLD cases still need the fact in section B. Here **R3 means research-type policy**; historical **UCSB R3 is covered by P1**.

## A. Recommended policy decisions

### Evidence and counting conventions

Every original Batch C review ID occurs **once**, in the case tables below. C01–C41 are navigation slots, not new audit actions. Section B links to those slots without duplicating records. Each action has one counting owner; cross-cutting contribution rules do not increase the 41-action total.

Primary local references: [original audit](corpus_quality_audit_2026_10_04.md); [taxonomy queue](../data/raw/corpus_quality_audit_2026_10_04/taxonomy_review.json); [unmapped queue](../data/raw/corpus_quality_audit_2026_10_04/unmapped_papers.json); [relationship queue](../data/raw/corpus_quality_audit_2026_10_04/relationship_review.json); [publication queue](../data/raw/corpus_quality_audit_2026_10_04/publication_metadata_review.json); [saved source checks](../data/raw/corpus_quality_audit_2026_10_04/source_checks.json). URLs below are preserved references, not newly verified sources.

Conventions: [taxonomy and hierarchy schema](data_schema.md#paper-taxonomy), [collection and review boundaries](data_collection.md), [taxonomy audit](paper_taxonomy_migration_audit_2026-09-04.md), [venue normalization and track policy](publication_venue_normalization.md), [Batch A report](corpus_quality_batch_a_remediation_2026_10_04.md). Additional existing evidence is the [canonical taxonomy registry](../data/curated/paper_taxonomy.csv), [committed paper abstracts](../web/data/public_preview_papers.json), institution registries and the offline venue evidence files referenced below. An earlier `reviewed` flag is evidence history, not proof against the current audit question.

**Read columns carefully:** “Current → audit possibility” preserves the audit proposal; “Recommendation” is this decision review and can reject that proposal. HOLD means retain current data until the stated evidence supports a branch; absence from an abstract does not establish absence from the paper.

### T-POLICY-1 — Attribution versus detection (T1)

**Question:** Does generator recognition also warrant detection?

**Recommend A:** Assign `detection` only for an explicit real-versus-generated/authenticity task; source-model classification, same-source verification, unseen-generator rejection and single-generator membership alone warrant only `source_attribution`.

**Fit:** Substantive tasks are independent in the schema; all eleven removals were conditional in the audit. **Effect / limits:** If no authenticity task exists, remove detection only; otherwise keep both. Missing abstract detail cannot establish absence. Unknown-generator rejection is not a real-image class.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-01"></a>C01 / **T024**<br>AI-Generated Image Homology Detection<br>`curated:1a8e996ef9ce73efc0ef` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The recorded homology task tests whether two generated images share a source. A real-versus-generated protocol is not established. [Recorded source](https://doi.org/10.1007/978-981-92-2856-0_1). |
| <a id="case-02"></a>C02 / **T136**<br>ImageAttributionBench: How Far Are We from Generalizable Attribution?<br>`curated:d59bffe554500b241a3e` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The recorded ImageAttributionBench settings test degradation and semantic generalization of attribution, without a separately documented authenticity task. [Recorded source](https://arxiv.org/abs/2605.12967). |
| <a id="case-03"></a>C03 / **T137**<br>IncreFA: Breaking the Static Wall of Generative Model Attribution<br>`curated:246f07c81b9f91e527eb` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The saved abstract identifies 28 generators and reports 98.93% unseen-generator detection; that number does not demonstrate a real-image class. [Recorded source](https://openaccess.thecvf.com/content/CVPR2026/papers/Qin_IncreFA_Breaking_the_Static_Wall_of_Generative_Model_Attribution_CVPR_2026_paper.pdf). |
| <a id="case-04"></a>C04 / **T141**<br>Learning a Semantic Similarity Orthogonal Space for Model-Level AI-Generated Image Source Attribution<br>`curated:268336295435cfbbbd5d` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The saved abstract describes reconstruct-and-compare model tracing for assumed synthetic queries. [Recorded source](https://doi.org/10.1111/exsy.70359). |
| <a id="case-05"></a>C05 / **T299**<br>Detecting Origin Attribution for Text-to-Image Diffusion Models<br>`curated:161b6d5ca391d238f7e9` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The saved abstract studies 12 generators, seeds and inference hyperparameters. Its broad “detectable” conclusion does not specify a separate authenticity experiment. [Recorded source](https://doi.org/10.1109/wacv61041.2025.00850). |
| <a id="case-06"></a>C06 / **T446**<br>Are CLIP Features All You Need for Universal Synthetic Image Origin Attribution?<br>`curated:8bc69db49ef4b9db3cd6` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The saved abstract promises open-set source attribution and generalization; detection is background motivation unless a real class is demonstrated. [Recorded source](https://doi.org/10.1007/978-3-031-92648-8_22). |
| <a id="case-07"></a>C07 / **T503**<br>ManiFPT: Defining and Analyzing Fingerprints of Generative Models<br>`curated:34fdf09ae334914a2723` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The saved abstract defines artifacts/fingerprints and tests source-model identification; earlier real/fake work is discussed as motivation. [Recorded source](https://doi.org/10.1109/cvpr52733.2024.01026). |
| <a id="case-08"></a>C08 / **T572**<br>Open Set Synthetic Image Source Attribution<br>`curated:5a91cc922c8a3c4c3d0c` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The saved abstract accepts/rejects a candidate generator in embedding space. Batch A’s formal BMVC 2023 upgrade does not answer this separate task question. [Recorded source](https://arxiv.org/abs/2308.11557). |
| <a id="case-09"></a>C09 / **T576**<br>Single-Model Attribution of Generative Models Through Final-Layer Inversion<br>`curated:62b0a9ae8be24d9f02e0` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | FLIPAD tests membership in one generator using anomaly detection; non-membership is not necessarily a real-image class. [Recorded source](https://openreview.net/pdf?id=Hs9GcILuZN). |
| <a id="case-10"></a>C10 / **T611**<br>Does a GAN Leave Distinct Model-Specific Fingerprints?<br>`curated:07ee620b8169b67b900f` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The saved abstract motivates authenticity and tests GAN-specific fingerprints, but does not specify the complete class/evaluation protocol. [Recorded source](https://doi.org/10.5244/c.35.53). |
| <a id="case-11"></a>C11 / **T634**<br>Do GANs Leave Artificial Fingerprints?<br>`doi:10.1109/mipr.2019.00103` | `detection; source_attribution` → `source_attribution` | HOLD under T1. | The saved abstract explicitly reports source-identification experiments with several GANs; a separate authenticity task remains unverified. [Recorded source](https://doi.org/10.1109/mipr.2019.00103). |

### T-POLICY-2 — Localization threshold (T2)

**Question:** Which spatial outputs count as localization?

**Recommend A:** Require an explicit spatial forensic prediction objective and evaluation (pixel, mask, patch, region or bounding region). Include evaluated artifact segmentation of fully generated images; exclude mere attention, explanations, local features and annotation-only masks.

**Fit:** The schema requires an explicit forensic spatial objective and evaluation. **Effect / limits:** Add localization to LEGION; hold the other two pending scored spatial-output evidence. Artifact segmentation counts even on fully synthetic images; attention/metadata or auxiliary segmentation alone does not.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-12"></a>C12 / **T236**<br>Unveiling Perceptual Artifacts: A Fine-Grained Benchmark for Interpretable AI-Generated Image Detection<br>`curated:64635535d7b7b6a12a32` | `detection` → `detection; localization` | HOLD: keep detection pending spatial-task proof. | X-AIGD supplies pixel-level artifact annotations and attention-alignment/interpretability evaluation. The saved abstract does not establish a scored spatial prediction task. [Recorded source](https://openreview.net/forum?id=Tk8ujiOgHM). |
| <a id="case-13"></a>C13 / **T246**<br>Zooming In on Fakes: A Novel Dataset for Localized AI-Generated Image Detection with Forgery Amplification Approach<br>`doi:10.1609/aaai.v40i4.37240` | `detection` → `detection; localization` | HOLD: keep detection pending spatial-task proof. | BR-Gen supplies local-forgery annotations; NFA-ViT mines regions and propagates cues for image detection. A predicted region/mask evaluation is not established. [Recorded source](https://doi.org/10.1609/aaai.v40i4.37240). |
| <a id="case-14"></a>C14 / **T363**<br>LEGION: Learning to Ground and Explain for Synthetic Image Detection<br>`curated:14272073fa5bc0e301b5` | `detection` → `detection; localization` | READY: `detection; localization` after explicit T2 approval. | The saved abstract explicitly proposes artifact segmentation, with SynthScars mIoU and F1 comparisons. This satisfies the proposed artifact-localization boundary. [Recorded source](https://doi.org/10.1109/iccv51701.2025.01760). |

### T-POLICY-3 — Existing vocabulary applicability (T3)

**Question:** Must every included paper fit one of the three task labels?

**Recommend A:** Keep training-example provenance retrieval distinct from generator/source-model attribution. Permit an explicitly reviewed empty task set when the recorded scientific task fits none of the controlled values, while retaining the paper and its locked scope.

**Fit:** The schema permits explicitly reviewed empty tasks; CS-SLIP’s recorded target is training-image retrieval. **Effect / limits:** T3=A explicitly approves the proposed empty task set for a later authorized update, preserving inclusion and other dimensions. This is a reusable boundary, not automatic label clearing. Hold if training-image provenance should instead broaden source_attribution.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-15"></a>C15 / **T527**<br>Towards Generated Image Provenance Analysis via Conceptual-Similar-Guided-SLIP Retrieval<br>`doi:10.1109/lsp.2024.3388958` | `source_attribution` → `[]` | READY: `tasks=[]` only after explicit T3 approval; preserve inclusion and other dimensions. | The saved abstract explicitly retrieves similar original training images using cross-modal retrieval to trace replication, rather than identifying the generating model. [Recorded source](https://doi.org/10.1109/lsp.2024.3388958). |

### R-POLICY-1 — Dataset contribution (R1)

**Question:** When is a dataset a scientific contribution?

**Recommend A:** Use `dataset` for construction, release or curation of a reusable data resource that is itself a contribution; experimental sampling or reuse alone is insufficient. Public release is strong evidence but is not an absolute prerequisite.

**Fit:** The schema labels substantive contributions; the stored primary-full-text contribution statement supports the dynamic ensemble’s three roles. **Effect / limits:** Retain those three roles. Other removals need a contribution/data check. A release mention alone does not prove a dataset contribution; abstract silence does not disprove one.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-16"></a>C16 / **R084**<br>Dynamic Ensemble of Deepfake Detectors Conditioned on CLIP Features<br>`curated:980afddea0a156b5020b` | `method; dataset; benchmark` → `method` | READY: retain `method; dataset; benchmark`; reject the proposed removal. | Stronger existing evidence: the canonical taxonomy row is tagged primary_full_text and records a contribution list containing an approximately 50k-image dataset, a fourteen-detector benchmark and the dynamic ensemble. Prefer this over the audit’s weaker abstract-only doubt. [Recorded source](https://cmp.felk.cvut.cz/cvww2026/assets/pdfs/CVWW2026-31-final.pdf). |
| <a id="case-17"></a>C17 / **R099**<br>Fake-HR1: Rethinking Reasoning of Vision Language Model for Synthetic Image Detection<br>`curated:9c39067ac73e7354c2f3` | `method; dataset` → `method` | HOLD under the owning contribution rule. | The saved authoritative abstract contributes HFT/HGRPO and adaptive reasoning. It does not establish whether training examples form a reusable contributed data resource. [Recorded source](https://arxiv.org/abs/2602.10042). |
| <a id="case-18"></a>C18 / **R176**<br>PRADA: Probability-Ratio-Based Attribution and Detection of Autoregressive-Generated Images<br>`curated:f6ad15b01df18aadfe1a` | `method; dataset` → `method` | HOLD under the owning contribution rule. | The saved PRADA abstract explicitly says code and data are released. The contribution status/substance of that data remains unclear; a removal cannot follow from silence. [Recorded source](https://openaccess.thecvf.com/content/CVPR2026F/papers/Damm_PRADA_Probability-Ratio-Based_Attribution_and_Detection_of_Autoregressive-Generated_Images_CVPRF_2026_paper.pdf). |
| <a id="case-19"></a>C19 / **R190**<br>Representation and Reference Selection in Training-Free Synthetic Image Attribution<br>`curated:c84b04cb8e921be753db` | `dataset; analysis_study` → `analysis_study` | HOLD under the owning contribution rule. | The saved abstract reports controlled reference-selection/representation analysis. The possible additional data-resource contribution is not established. [Recorded source](https://arxiv.org/abs/2607.12052). |
| <a id="case-20"></a>C20 / **R455**<br>Deep Image Fingerprint: Towards Low Budget Synthetic Image Detection and Model Lineage Analysis<br>`curated:04932cb03f767948ddf4` | `method; dataset` → `method` | HOLD under the owning contribution rule. | The saved abstract proposes a CNN-based detector and lineage analysis and tests GAN/diffusion images; it does not specify a contributed data resource. [Recorded source](https://doi.org/10.1109/wacv57701.2024.00402). |
| <a id="case-21"></a>C21 / **R535**<br>Which Model Generated This Image? A Model-Agnostic Approach for Origin Attribution<br>`curated:98c0322e2f8dd41d3e9e` | `method; dataset` → `method` | HOLD under the owning contribution rule. | The saved abstract proposes OCC-CLIP with few-shot one-class experiments and a code release. A dataset contribution is not established. [Recorded source](https://doi.org/10.1007/978-3-031-73033-7_16). |
| <a id="case-22"></a>C22 / **R580**<br>Towards Universal Fake Image Detectors That Generalize Across Generative Models<br>`curated:1ef55e4fc03eb4880beb` | `method; dataset` → `method` | HOLD under the owning contribution rule. | The saved abstract proposes training-free real/fake classification and evaluates generalization; whether a new reusable collection was contributed remains open. [Recorded source](https://doi.org/10.1109/cvpr52729.2023.02345). |

The dynamic-ensemble row invokes R2 and the multi-role convention as well as R1; it is counted only once here. The primary-full-text contribution statement is already in the registry; this task did not fetch that paper.

### R-POLICY-2 — Benchmark contribution (R2)

**Question:** When does evaluation constitute a benchmark?

**Recommend A:** Use `benchmark` for a reusable evaluation challenge, protocol, systematic comparative framework or benchmark resource/procedure intended to evaluate methods. Large result tables alone do not qualify; new images are not required.

**Fit:** Benchmark is independent of dataset and method. **Effect / limits:** DE-FAKE keeps method/analysis; benchmark depends on a reusable protocol, not whether its images are new. This rule also covers the dynamic ensemble under R1 and the detector study under R4, without double-counting.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-23"></a>C23 / **R548**<br>DE-FAKE: Detection and Attribution of Fake Images Generated by Text-to-Image Generation Models<br>`doi:10.1145/3576915.3616588` | `method; benchmark; analysis_study` → `method; analysis_study` | HOLD under the owning contribution rule. | The saved abstract calls DE-FAKE a systematic detection/attribution study using four generators and two existing prompt-image datasets. Reuse alone does not settle whether its protocol is a benchmark contribution. [Recorded source](https://doi.org/10.1145/3576915.3616588). |

### R-POLICY-3 — Analysis as a contribution (R3)

**Question:** Is scientific analysis primary or supporting validation?

**Recommend A:** Use `analysis_study` when systematic empirical/theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps and explanation figures supporting a method do not suffice.

**Fit:** Multiple contribution types are allowed. GAP-SAM’s saved abstract records controlled cross-localizer findings and boundary adhesion. **Effect / limits:** Retain GAP-SAM’s types. Other removals need the study/validation distinction checked. Analysis can motivate a method and still be primary; routine performance tables alone are insufficient.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-24"></a>C24 / **R121**<br>GAP-SAM: A Global Artifact Prior for Generalizable AI-Generated Image Manipulation Localization<br>`curated:bada2e715200e9fccb7a` | `method; dataset; analysis_study` → `method; dataset` | READY: retain `method; dataset; analysis_study`; reject the proposed removal. | The stored authoritative abstract compares COCO-ControlNet and Mask-VAE alignment across localizers, identifies transfer limitations and boundary adhesion, then motivates GAP-SAM. Recommend retaining analysis alongside method and dataset. [Recorded source](https://arxiv.org/abs/2608.20929). |
| <a id="case-25"></a>C25 / **R127**<br>GlobalForge: Towards Robust AI-Generated Image Detection<br>`curated:807cbb7fa6b003585c72` | `method; analysis_study` → `method` | HOLD under the owning contribution rule. | The saved abstract attributes fragility to local artifacts, proposes LIB/GSR and introduces RealDeg-Bench. The C question is only whether the causal/robustness analysis is independently substantive; no new benchmark action is opened here. [Recorded source](https://arxiv.org/abs/2607.14684). |
| <a id="case-26"></a>C26 / **R189**<br>Reduce the Artifact Bias for More Generalizable AI-Generated Image Detection<br>`curated:685065a3632a185a230d` | `method; analysis_study` → `method` | HOLD under the owning contribution rule. | The saved abstract motivates ACEF/LACF through complementary artifact domains and reports 13-benchmark validation. An independently supported scientific analysis is not established. [Recorded source](https://arxiv.org/abs/2605.14486). |
| <a id="case-27"></a>C27 / **R460**<br>Detecting AI Generated Images Through Texture and Frequency Analysis of Patches<br>`doi:10.1109/aivrv63595.2024.10860248` | `method; analysis_study` → `method` | HOLD under the owning contribution rule. | The saved abstract proposes patch/frequency preprocessing plus a classifier and reports accuracy/generalization. It does not establish analysis beyond validation. [Recorded source](https://doi.org/10.1109/aivrv63595.2024.10860248). |
| <a id="case-28"></a>C28 / **R537**<br>X-Transfer: A Transfer Learning-Based Framework for GAN-Generated Fake Image Detection<br>`doi:10.1109/ijcnn60899.2024.10650566` | `method; analysis_study` → `method` | HOLD under the owning contribution rule. | The saved abstract proposes interleaved gradient transfer and loss changes, then validates on face/non-face datasets. A separate analysis contribution remains unestablished. [Recorded source](https://doi.org/10.1109/ijcnn60899.2024.10650566). |
| <a id="case-29"></a>C29 / **R615**<br>Towards Discovery and Attribution of Open-world GAN Generated Images<br>`doi:10.1109/iccv48922.2021.01383` | `method; analysis_study` → `method` | HOLD under the owning contribution rule. | The saved abstract proposes iterative discovery, clustering and refinement, with open-world and real/fake evaluations. Analysis beyond method validation is not established. [Recorded source](https://doi.org/10.1109/iccv48922.2021.01383). |

No removal is recommended for GAP-SAM: the recorded cross-localizer comparisons and explicit boundary-adhesion finding meet the contribution-level analysis rule. This is a proposed rejection of the old audit signal, not an applied label change.

### R-POLICY-4 — Method and independent contributions (R4)

**Question:** Does the work propose a substantive technical method?

**Recommend A:** Use `method` for a substantive new algorithm/system/technical procedure, not merely implemented baselines. Retain every independently supported role: method, dataset, benchmark, survey and analysis are not mutually exclusive.

**Fit:** R-POLICY-5 (multi-role papers) is already the schema convention and is incorporated here rather than added as a vote. **Effect / limits:** Use analysis for the frequency study, benchmark/analysis for the detector comparison, and survey for the review; retain method as well only if FSI, the ensemble or IBMM is substantive. Each novelty question remains open.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-30"></a>C30 / **R117**<br>Frequency-Aware Robustness Analysis of Deepfake Detection Models<br>`curated:748ed5e2cf27aea70f6a` | `method` → `analysis_study` | HOLD: `analysis_study`, plus `method` if FSI is substantive; do not settle method removal yet. | The saved abstract reports controlled perturbation/frequency tests on three detectors and explicitly describes FSI-drop as score stability. Analysis is supported; whether FSI constitutes a new method remains open. [Recorded source](https://doi.org/10.32604/jai.2026.078014). |
| <a id="case-31"></a>C31 / **R376**<br>No Detector to Rule Them All<br>`curated:cda6067db322246e8195` | `method` → `benchmark; analysis_study` | HOLD: `benchmark; analysis_study`, plus `method` if the ensemble is substantive. | The saved abstract explicitly describes comprehensive benchmarking and feature-level analysis, but only explores simple detector ensembles. The unresolved issue is whether any ensemble is a substantive new method. [Recorded source](https://doi.org/10.1145/3746265.3759659). |
| <a id="case-32"></a>C32 / **R549**<br>Deepfake Generation and Detection: Case Study and Challenges<br>`curated:616984c24ff3792431e6` | `method` → `survey` | HOLD: `survey`, plus `method` if IBMM is substantive. | The saved abstract explicitly presents a comprehensive survey and calls IBMM a unique case study. That wording alone does not establish whether IBMM is an original technical contribution. [Recorded source](https://doi.org/10.1109/access.2023.3342107). |

**R-POLICY-5 evaluated:** multi-role classification is a shared constraint within R1–R4, not a thirteenth vote. Examples include retaining the dynamic ensemble’s method/dataset/benchmark and GAP-SAM’s method/dataset/analysis; the three rows above may also legitimately retain method alongside their study/survey roles.

### I-POLICY-1 — Distinct Shanghai institutions (I1)

**Question:** Are Shanghai University and SUES aliases?

**Recommend A:** `KEEP_DISTINCT_CANONICAL_INSTITUTIONS`. They are separate existing active canonical institutions; decide the affected paper’s affiliation separately.

**Fit:** Two active canonical IDs already exist: Shanghai University `institution:dbc08517e4f1ed6e`, SUES `institution:07ba242d76aafb0e`. **Effect / limits:** Keep them separate. Correct only evidence-supported author assignments after paper-time markers are known. A raw candidate string or available coordinates cannot settle that assignment.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-33"></a>C33 / **U010**<br>Diffusion-Driven Forgery Detection: Distilling Latent Features for Generalized Image Forensics<br>`curated:d0eec7c4fce8929c295a` | Unmapped; candidate parent/institution mapping `needs_review` → evidence-confirmed author assignment (not yet determined) | HOLD: preserve unmapped/review state. | Candidate mapping mapping:b2df8c5c3dcef11ea3b6 assigns all four authors to SUES although the raw string says School of Computer Engineering and Science, Shanghai University. Paper-time and identity flags are false; mapping status is needs_review. [Recorded source](https://doi.org/10.1109/lsp.2026.3687792). |

### I-POLICY-2 — VNU-HCM member and parent (I2)

**Question:** How should a VNU-HCM member affiliation be represented?

**Recommend A:** Map an explicitly named member institution to its existing canonical child. Add/confirm a reviewed child–parent hierarchy edge so parent searches include it. Add a separate parent paper relation only if paper-time affiliation markers explicitly support it.

**Fit:** Reviewed hierarchy expands parent search without changing affiliations. The active member institution already exists. **Effect / limits:** After author markers are verified, use child `institution:806523d1aae41484` and parent `institution:19d2ee8d44bfb9f0`, with a confirmed hierarchy edge. The raw “and” may denote two affiliations. Never revive merged duplicate `institution:329f39cda413f721`.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-34"></a>C34 / **U017**<br>Unified Detection of Synthetic and Manipulated Images via Dual-Stream Artifact Fusion<br>`curated:0d918782407e05ade5bd` | Unmapped; candidate parent/institution mapping `needs_review` → evidence-confirmed author assignment (not yet determined) | HOLD: preserve unmapped/review state. | Candidate mapping mapping:6307736ef459cb62af5a currently contains only VNU-HCM, needs_review, and is not exported. The raw text names University of Science and VNU-HCM. The active child has a known location and confirmed aliases but no matching confirmed row in institution_hierarchy.csv. [Recorded source](https://doi.org/10.1145/3810988.3812660). |

Current registry details: the active child has known coordinates **10.76262, 106.68218** and `parent_institution_id` pointing to VNU-HCM; the parent has **10.86896, 106.79623**. The relevant edge is absent from [institution_hierarchy.csv](../data/curated/institution_hierarchy.csv). A later reviewed hierarchy edge is consistent with [documented parent-search expansion](data_schema.md), while author assignment still requires the ACM paper’s numbered affiliations. Current public relationships for this paper remain zero.

### P-POLICY-1 — Equivalent relations and source provenance (P1)

**Question:** Can source multiplicity produce duplicate public relations?

**Recommend A:** `RECOMMEND_ACCEPT` for the UCSB R3 case: retain distinct source records in the durable audit/snapshot trail and expose one equivalent normalized public relation after canonical identity, author-group and location equivalence are established.

**Fit:** Batch A establishes corrected relation equivalence; the current relationship key includes paper, institution, location and author set. **Effect / limits:** Accept the existing collapse and durable audit-level provenance as resolving UCSB R3. No manual merge is needed. A universal same-pair collapse ignoring different authors/locations would require further policy; it is not approved by this vote.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-35"></a>C35 / **L001**<br>Detection, Attribution and Localization of GAN Generated Images<br>`doi:10.2352/issn.2470-1173.2021.4.mwsf-276` | Audit: two UCSB rows → one equivalent relation; **already one after Batch A**, provenance approval pending | READY: accept the existing equivalent-relation collapse and durable provenance; no manual merge. | Current Batch A state: one UCSB relation, corrected author groups, zero duplicate public pairs. Source works W3179128750 and W3043994911 and the three original paper map rows remain in the original queue, results ledger and checksummed predecessor archive. [Recorded source](https://arxiv.org/pdf/2007.10466). |

Provenance acceptance is **audit-trail traceability**, not a claim that both work IDs are exposed on the surviving public row. Existing evidence: [relationship key](../scripts/public_relationships.py), [Batch A ledger](../data/raw/corpus_quality_batch_a_2026_10_04/results.json), [snapshot manifest](../data/raw/corpus_quality_batch_a_2026_10_04/predecessor_640_manifest.json), and [snapshot archive](../data/raw/corpus_quality_batch_a_2026_10_04/predecessor_640.json.gz). Under this bounded policy, R3 is fully resolvable now; it is still `REQUIRES_MAINTAINER_DECISION` until approved. `DETERMINISTIC_EXPORT_COLLAPSE_AFTER_R1_R2`; `NO MANUAL R3 MERGE APPLIED`.

### V-POLICY-1 — Canonical venue, container and track (V1)

**Question:** Does venue mean a container, event, or canonical identity?

**Recommend A:** Use a normalized canonical scholarly venue: the verified event for conference proceedings, the journal for a journal article. Retain deposited container strings as provenance. Keep paper-level track separate from venue identity and year; unknown event/type/track stays under review.

**Fit:** Existing venue normalization keeps canonical identity, raw container, year and paper track separate. **Effect / limits:** Preserve current fields until event/type/track evidence exists. Do not infer Workshop from MWSF, Main from absence, or conference type solely from a series name. Named standalone workshops can retain independent venue identities.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-36"></a>C36 / **P550**<br>Detecting GAN-generated synthetic images using semantic inconsistencies<br>`doi:10.2352/ei.2023.35.4.mwsf-380` | Electronic Imaging; `journal`; 2023; acronym/track empty → event/type/track conditional on primary proceedings evidence | HOLD: preserve metadata pending event/type/track evidence. | Existing queue/cache: Electronic Imaging, deposited journal-article, volume 35 issue 4, pages 380-1–380-6; MWSF in DOI. Primary event/type/track is still unresolved. [Recorded source](https://doi.org/10.2352/ei.2023.35.4.mwsf-380). |
| <a id="case-37"></a>C37 / **P586**<br>Deep Learning applied to Road Accident Detection with Transfer Learning and Synthetic Images<br>`doi:10.1016/j.trpro.2022.09.012` | Transportation research procedia; `journal`; 2022; acronym/track empty → event/type/track conditional on primary proceedings evidence | HOLD: preserve metadata pending event/type/track evidence. | Existing queue/cache: Transportation Research Procedia, deposited journal-article, volume 64 pages 90–97. The underlying event and paper-level track are not established. Scope is locked in this task. [Recorded source](https://doi.org/10.1016/j.trpro.2022.09.012). |
| <a id="case-38"></a>C38 / **P610**<br>Detection, Attribution and Localization of GAN Generated Images<br>`doi:10.2352/issn.2470-1173.2021.4.mwsf-276` | Electronic Imaging; `journal`; 2021; acronym/track empty → event/type/track conditional on primary proceedings evidence | HOLD: preserve metadata pending event/type/track evidence. | Existing queue/cache: Electronic Imaging, deposited journal-article, volume 33 issue 4, pages 276-1–276-11; MWSF in DOI. Batch A changed affiliations/tasks, not this venue decision. [Recorded source](https://doi.org/10.2352/issn.2470-1173.2021.4.mwsf-276). |
| <a id="case-39"></a>C39 / **P633**<br>Detecting GAN Generated Fake Images Using Co-Occurrence Matrices<br>`curated:60066ef08c2226131085` | Electronic Imaging; `journal`; 2019; acronym/track empty → event/type/track conditional on primary proceedings evidence | HOLD: preserve metadata pending event/type/track evidence. | Existing queue/cache: Electronic Imaging, deposited journal-article, volume 31 issue 5, pages 532-1–532-7; MWSF in DOI. A proceedings/event assignment still needs paper-specific evidence. [Recorded source](https://doi.org/10.2352/issn.2470-1173.2019.5.mwsf-532). |

**V-POLICY-2 evaluated:** event identity and paper track are already separate fields, so this is part of V1 rather than an extra vote. The three Electronic Imaging records share one policy but retain three evidence gates. Procedia shares that schema rule but has a distinct event-identification gap. Existing deposited metadata is referenced in each publication queue row’s `cached_crossref_check`; no service was called.

### V-POLICY-3 — Unambiguous journal identity and aliases (V3)

**Question:** Should an abbreviation collision change journal identity?

**Recommend A:** Keep the canonical full journal identity and only unambiguous, evidence-backed aliases. Abbreviations shared by different venues must not merge their identities. A full-name display with an empty optional acronym is acceptable.

**Fit:** Existing policy protects full identities and does not require an acronym; the queue records the MM collision. **Effect / limits:** Retain `venue:ieee-multimedia`, IEEE MultiMedia, journal, and empty acronym; reject the ambiguous alias. This resolves the optional-alias decision without inventing a short name or merging distinct venues.

| Case / original review / paper identity | Current → audit possibility | Recommendation if policy accepted | Existing evidence and remaining boundary |
| --- | --- | --- | --- |
| <a id="case-40"></a>C40 / **P222**<br>Toward Generalizable AI-Generated Image Detection with a New Realistic Dataset: Performance Evaluation and Improvement<br>`curated:e9594b5466110ca009aa` | IEEE MultiMedia; `journal`; 2026; acronym/track empty → keep full identity; omit colliding optional abbreviation | READY: retain IEEE MultiMedia / journal / existing ID; leave acronym empty; decline MM alias. | Current journal identity and DOI are present; the authority evidence records MM as a short name, while the queue records a collision. Omitting this optional acronym needs no new publication claim. [Recorded source](https://doi.org/10.1109/mmul.2026.3710370). |

Evidence: [stored venue authorities](../data/processed/venue_authority_evidence.json), [paper-specific venue evidence](../data/processed/venue_paper_evidence.json), and the publication queue’s cache reference. Existing policy permits a full-name short form without an acronym. There is no need to manufacture a new journal identity to solve an alias collision.

### Source-conflict exception — no new policy vote

This is a paper-specific identity/evidence problem, not a research-type threshold. Applying any contribution rule before the source association is resolved would turn conflicting text metadata into image-paper labels.

| Case / original review / paper identity | Current → audit possibility | Recommendation | Existing evidence |
| --- | --- | --- | --- |
| <a id="case-41"></a>C41 / **R188**<br>Reasoning-Aware AIGC Detection via Alignment and Reinforcement<br>`curated:6c2f591bf6fda3abecbb` | `method` → `method` | HOLD: retain current `method`; do not change scope/labels from contradictory metadata. | The image-detection title conflicts with a stored abstract about LLM text authorship, AIGC-textbank and REVEAL. Both are already recorded; no abstract/source correction has been made. [Recorded source](https://doi.org/10.18653/v1/2026.findings-acl.1043). |

## B. Paper-specific residual decisions

**35 unresolved case-level gates.** These are evidence questions, not 35 different policy rules. Each link supplies the paper identity, current/proposed value and existing evidence in section A. No new evidence collection is performed here. “If yes/if no” options are contingent recommendations; when unknown, **hold the current data**.

**Shared decision tests (options and missing evidence):**

- **AUTH:** explicit real/authenticity task → retain detection; no such task → attribution only. Need complete class definitions and evaluation protocol.
- **SPACE:** evaluated spatial prediction → add localization; attention/metadata only → retain detection. Need output definition, ground truth and spatial metric.
- **DATA:** contributed reusable resource → retain dataset; experiment-only data → audit-proposed set. Need contribution/data/supplement details.
- **BENCH:** reusable evaluation framework → retain benchmark; own experiments only → method + analysis. Need contribution/protocol details.
- **ANALYSIS:** primary systematic finding → retain analysis; supporting validation → method. Need claims and controlled-study evidence.
- **METHOD:** new substantive algorithm → retain method alongside the indicated study/survey types; baseline/case study → omit method. Need technical novelty/contribution evidence.
- **AFFILIATION:** assign only institutions explicitly supported for each author, preserving dual affiliations. Need paper-time affiliation block and superscripts.
- **VENUE:** verified proceedings → event/conference; verified journal → journal; separately verify track. Need identifier-linked paper/volume proceedings evidence.
- **IDENTITY:** repair the source association before any label decision; a scope change is outside this task. Need matching title, authors, identifier and abstract.

**Recommended now for every unresolved case: HOLD.** Unknown facts do not select either branch. The case link contains the existing evidence; the test supplies its exact options and required evidence.

| Case (existing evidence above) | Exact unresolved question | Options / evidence test |
| --- | --- | --- | --- |
| [C01](#case-01) | Does the evaluation include authentic images as a real-vs-generated task, beyond same-source pair verification? | AUTH; HOLD |
| [C02](#case-02) | Is there a separate real-image/authenticity protocol outside the two recorded attribution settings? | AUTH; HOLD |
| [C03](#case-03) | Does any IABench protocol classify real images, rather than only known versus unseen generators? | AUTH; HOLD |
| [C04](#case-04) | Is real-vs-generated authenticity evaluated beyond reconstruction-based source matching? | AUTH; HOLD |
| [C05](#case-05) | Is real/fake discrimination a distinct task, rather than generator/seed/hyperparameter identification? | AUTH; HOLD |
| [C06](#case-06) | Does the open-set protocol contain a real/authentic class and evaluate it as detection? | AUTH; HOLD |
| [C07](#case-07) | Does the full protocol evaluate real/fake detection in addition to fingerprint/model identification? | AUTH; HOLD |
| [C08](#case-08) | Does the BMVC protocol include a separate authenticity evaluation beyond unknown-generator rejection? | AUTH; HOLD |
| [C09](#case-09) | Are real images part of an explicit authenticity task, rather than merely examples of non-membership? | AUTH; HOLD |
| [C10](#case-10) | Do the reported fingerprint experiments include binary authenticity detection? | AUTH; HOLD |
| [C11](#case-11) | Does the complete experiment protocol include real/fake detection beyond source identification? | AUTH; HOLD |
| [C12](#case-12) | Are spatial artifact predictions scored against the pixel annotations, or are masks used only to analyze/align attention? | SPACE; HOLD |
| [C13](#case-13) | Is a predicted edited-region mask/patch/box evaluated, or is the output only an image-level decision? | SPACE; HOLD |
| [C17](#case-17) | Are Fake-HR1 training examples a separately contributed reusable resource or only method training data? | DATA; HOLD |
| [C18](#case-18) | What is in the released PRADA data, and is its construction/curation a substantial reusable contribution? | DATA; HOLD |
| [C19](#case-19) | Does the reference collection constitute a contributed reusable dataset, rather than inputs for controlled analysis? | DATA; HOLD |
| [C20](#case-20) | Is there a documented new reusable image collection beyond detector/lineage experiments? | DATA; HOLD |
| [C21](#case-21) | Does OCC-CLIP contribute a dataset beyond the samples used for few-shot evaluation? | DATA; HOLD |
| [C22](#case-22) | Which new reusable data resource, if any, is contributed beyond evaluating on existing detection data? | DATA; HOLD |
| [C23](#case-23) | Does DE-FAKE contribute a reusable evaluation protocol/framework rather than only its own comparative experiments? | BENCH; HOLD |
| [C25](#case-25) | Is the local-artifact fragility diagnosis independently tested as a principal finding, beyond motivating/validating LIB/GSR? | ANALYSIS; HOLD |
| [C26](#case-26) | Is there independent systematic evidence for artifact-bias claims beyond motivating and validating ACEF? | ANALYSIS; HOLD |
| [C27](#case-27) | Is any systematic scientific analysis a primary contribution beyond preprocessing/classifier accuracy? | ANALYSIS; HOLD |
| [C28](#case-28) | Is there an independent transfer-learning analysis beyond validating the new algorithm? | ANALYSIS; HOLD |
| [C29](#case-29) | Is open-world discovery analysis independently substantive, beyond demonstrating the iterative method? | ANALYSIS; HOLD |
| [C30](#case-30) | Is FSI/associated machinery a substantive new technical method, or only a measurement used by the study? | METHOD; HOLD |
| [C31](#case-31) | Is the ensemble a new technical contribution with its own specification, or an exploratory combination of baselines? | METHOD; HOLD |
| [C32](#case-32) | Is IBMM proposed as an original algorithm/system, or an illustrative survey case study? | METHOD; HOLD |
| [C33](#case-33) | Which paper-time affiliation marker belongs to each of Kaiwen Qian, Yutao Xu, Yifan Xu and Yuchun Fang: Shanghai University, SUES, or genuinely both? | AFFILIATION; HOLD |
| [C34](#case-34) | How do the ACM paper’s affiliation markers assign Thinh-Phat Vo, Daniel Mai, Minh–Triet Tran and Trong-Le Do to the member and parent; are those separately listed affiliations? | AFFILIATION; HOLD |
| [C36](#case-36) | Which named scholarly event contains this paper, is it a proceedings contribution, and what track is explicitly documented? | VENUE; HOLD |
| [C37](#case-37) | Which event is represented by volume 64, what is the paper’s publication form/year relationship, and is any track documented? | VENUE; HOLD |
| [C38](#case-38) | Does the primary proceedings identify Electronic Imaging or MWSF as this paper’s event, and what publication form/track is evidenced? | VENUE; HOLD |
| [C39](#case-39) | Does the primary proceedings identify Electronic Imaging or MWSF as this paper’s event, and what publication form/track is evidenced? | VENUE; HOLD |
| [C41](#case-41) | Which title/abstract/identifier combination actually belongs to the included image paper, and which text-paper evidence was misassociated? | IDENTITY; HOLD |

Residual reconciliation: 11 authenticity + 2 spatial + 15 contribution + 2 affiliation + 4 proceedings + 1 source-conflict checks = 35. Shared checklists do not establish missing paper facts.

## C. Decision summary

| Policy | Recommended decision | Affected Batch C actions (owning count) | Remaining paper-specific decisions |
| --- | --- | ---: | ---: |
| T-POLICY-1 / T1 | A — Attribution versus detection; 0 ready | 11 | 11 |
| T-POLICY-2 / T2 | A — Localization threshold; 1 ready | 3 | 2 |
| T-POLICY-3 / T3 | A — Existing vocabulary applicability; 1 ready | 1 | 0 |
| R-POLICY-1 / R1 | A — Dataset contribution; 1 ready | 7 | 6 |
| R-POLICY-2 / R2 | A — Benchmark contribution; 0 ready | 1 | 1 |
| R-POLICY-3 / R3 | A — Analysis as a contribution; 1 ready | 6 | 5 |
| R-POLICY-4 / R4 | A — Method and independent contributions; 0 ready | 3 | 3 |
| I-POLICY-1 / I1 | A — Distinct Shanghai institutions; 0 ready | 1 | 1 |
| I-POLICY-2 / I2 | A — VNU-HCM member and parent; 0 ready | 1 | 1 |
| P-POLICY-1 / P1 | A — Equivalent relations and source provenance; 1 ready | 1 | 0 |
| V-POLICY-1 / V1 | A — Canonical venue, container and track; 0 ready | 4 | 4 |
| V-POLICY-3 / V3 | A — Unambiguous journal identity and aliases; 1 ready | 1 | 0 |
| Source-conflict exception | Hold pending correct paper evidence; no added policy | 1 | 1 |
| **Total** | **12 policy votes; 6 ready actions** | **41** | **35** |

Category reconciliation: **15 task + 18 research-type + 2 institution + 1 provenance + 5 venue/publication = 41**. The research-type total includes the standalone source-conflict exception. Cross-cutting R2, R3 and multi-role guidance are not extra actions.

**Immediate effect if all recommended policies are explicitly accepted:** six action decisions can be closed on existing evidence: two task dispositions, two research-type retention decisions, one provenance acceptance and one optional-abbreviation rejection. That means **6/41 resolved in principle, 35 still evidence-gated**; it does not mean six data edits or that this task has closed any audit record. The ready task dispositions require a future authorized taxonomy update; the other four need only a future recorded review outcome. Corpus counts are not recalculated or changed here.

**Scope guard:** Batch B and Batch D were not promoted, even where they concern the same paper as a C case. No new research-type action is opened for a dataset/benchmark mentioned incidentally in a C abstract. Missing evidence is not a reason to reclassify papers as preprints, alter inclusion, remove affiliations or collapse institution identities.

**Lightweight validation:** all 41 original C IDs occur exactly once; all IDs come from committed C rows; policy ownership plus the source-conflict exception reconciles to 41; six READY plus 35 HOLD cases reconcile to 41; all 35 HOLD cases have a linked residual question. No full suite or repository migration validator was run.

```text
AUTHORITATIVE_CORPUS_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
```

Final state for this task: one new Markdown decision sheet, all previously tracked file hashes unchanged, original 128 excluded local files unchanged, index empty, no commit and no push. Existing corpus remains 640 / 532 / 617 / 1,422 / 1,422. NeurIPS remains `7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`.


## D. Maintainer decisions — Batch C Phase 1, 2026-10-05

This section supersedes the recommendations and readiness counts in sections A–C, which are preserved verbatim as pre-decision history. The committed baseline is `0bc98c3e75636899e53114be3d9de0a71986990c`. Only local repository evidence was inspected: no browsing, APIs or downloads.

The [audit-specific policy ledger](../data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json) records all final rules, owning review IDs, whether policy alone resolves each item, the five dispositions, and one evidence entry for every residual action. Its evidence entries retain local file paths, paper/review locators, hashes at review, observed facts and precise follow-up requirements.

### D1. Twelve policies locked

Eleven policies are **ACCEPT**; T3 is **MODIFY_AND_ACCEPT**. The final maintainer wording below governs this phase. P1 is accepted as stated; no exporter-wide implementation change or new manual merge is made. R084 and R121 follow the explicit paper-specific dispositions, superseding the earlier retention recommendations.

| Policy | Decision | Final rule |
| --- | --- | --- |
| T1 | `ACCEPT` | source_attribution does not imply detection. Assign detection only when the paper explicitly performs an authenticity / real-versus-generated task. Classification among already-synthetic generators is attribution only. |
| T2 | `ACCEPT` | localization requires an evaluated spatial forensic prediction task such as pixel-, mask-, patch-, region-, or equivalent spatial prediction of synthetic/generated/edited content. Artifact segmentation qualifies. Attention maps, saliency maps, explainability heatmaps, or visualization alone do not qualify. |
| T3 | `MODIFY_AND_ACCEPT` | Every public paper must remain connected to at least one core forensic task represented by the map: detection, source_attribution, or localization. If careful review establishes that none applies, the record requires scope review rather than an empty task set. |
| R1 | `ACCEPT` | Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient. |
| R2 | `ACCEPT` | Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient. |
| R3 | `ACCEPT` | Assign analysis_study only when systematic empirical or theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps, or supporting interpretability figures do not qualify by themselves. |
| R4 | `ACCEPT` | Assign method only when the paper contributes substantive technical novelty: a method, algorithm, model, procedure, or system. Pure surveys, benchmarks, datasets, or analysis studies do not gain method merely because they implement baselines. Multiple legitimate research-type roles remain allowed. |
| I1 | `ACCEPT` | Shanghai University and Shanghai University of Engineering Science are distinct canonical institutions and must never be merged through alias normalization. The affected paper assignment remains evidence-dependent. |
| I2 | `ACCEPT` | When a paper explicitly names a specific VNU-HCM member institution, map the affiliation to that member institution. Represent VNU-HCM through the reviewed parent-child hierarchy so parent searches include the member. Do not create an additional duplicate parent-level paper relationship unless the paper explicitly lists the parent organization as a separate affiliation. Explicit dual affiliations must be preserved when genuinely present. |
| P1 | `ACCEPT` | Multiple raw/source provenance records may support the same canonical paper–institution relation. Preserve those provenance records, but expose one normalized public paper–institution relationship when the canonical paper and institution pair are identical. |
| V1 | `ACCEPT` | Keep the canonical archival venue identity conceptually distinct from source container/event information and paper track. Do not encode track as a different canonical venue. Use only fields supported by the current schema and do not invent metadata when event/container evidence is absent. |
| V3 | `ACCEPT` | Preserve IEEE MultiMedia as the canonical full venue identity. Do not populate or normalize to an optional acronym when that acronym is ambiguous or unsupported. |

### D2. Five approved dispositions resolved

`5/5 APPROVED IMMEDIATE ACTIONS APPLIED` means three authoritative taxonomy edits and two resolutions with no corpus-data edit.

| Review | Disposition | Corpus effect |
| --- | --- | --- |
| T363 | `APPLIED_TAXONOMY_CHANGE` | `detection` → `detection;localization` |
| R084 | `APPLIED_TAXONOMY_CHANGE` | `method;dataset;benchmark` → `method` |
| R121 | `APPLIED_TAXONOMY_CHANGE` | `method;dataset;analysis_study` → `method;dataset` |
| L001 | `R3_RESOLVED_BY_PROVENANCE_POLICY` | No data change |
| P222 | `ALREADY_COMPLIANT_NO_DATA_CHANGE` | No data change |

The three changes update `data/curated/paper_taxonomy.csv` and the corresponding compatibility fields in `data/curated/papers.csv`. Existing source evidence is retained; review reasons identify the maintainer disposition. Both public JSON files were regenerated through `scripts/export_public_preview.py --preserve-existing`. The key-paper report’s generated input fingerprint was refreshed; its coverage rows and manual CSV remain unchanged.

L001 records `R3_RESOLVED_BY_PROVENANCE_POLICY`. The already-correct public UCSB relation and every source provenance record remain unchanged. `DETERMINISTIC_EXPORT_COLLAPSE_AFTER_R1_R2` and `NO MANUAL R3 MERGE APPLIED` remain true. Earlier Batch A records retain their historical pending-R3 wording.

P222 is `ALREADY_COMPLIANT_NO_DATA_CHANGE`: canonical/public identity `IEEE MultiMedia`, `venue:ieee-multimedia`, journal, blank optional acronym. No cosmetic source-spelling change, alias change or public-paper change was made.

T527 retains `source_attribution` and `SCOPE_OR_TASK_EVIDENCE_REQUIRED`. Its stored abstract explicitly describes training-image retrieval. Whether that task substantively fits a represented core forensic task, or requires a scope decision, remains unresolved. It receives no empty task set.

T3 also reveals two pre-existing empty-task public records: “That’s Another Doom I Haven’t Thought About”: A User Study on AI Labels as a Safeguard Against Image-Based Misinformation; and TWIGMA: A Dataset of AI-Generated Images with Metadata from Twitter. Their baseline values are preserved. The new rule requires scope review where none of the core tasks applies; this phase creates no new empty task set and does not open or apply an additional Batch B/D action.

### D3. Residual local-evidence triage

Reconciled from original review IDs: **41 − 5 = 36 remaining Batch C actions**. Batch B remains **159**; Batch D remains **1,752**. T527 is included in the 36.

| Evidence status | Actions |
| --- | ---: |
| `LOCAL_EVIDENCE_SUFFICIENT` | 0 |
| `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | 35 |
| `MAINTAINER_SCOPE_JUDGMENT_REQUIRED` | 1 |

**Complete LOCAL_EVIDENCE_SUFFICIENT list: none. No residual factual disposition is proposed for application.** Positive partial findings do not settle a complete contested replacement: for example, R117 supports an analysis role but not removal of method; R549 supports survey but not the novelty status of IBMM. Likewise, dataset release alone does not establish a substantial resource contribution, and an abstract’s silence does not establish the absence of a task or independent contribution.

The local search covered committed identity/title/DOI/arXiv/OpenAlex matches, decompressed captures, available HTML/metadata and 33 saved PDF payloads. Matching conference listings and references were distinguished from the target paper’s primary full text. Existing audit statements requiring a full-paper check were not treated as that check. The ledger records the per-item local findings and source locators; this is the single residual-evidence table.

| Review / paper | Policy | Evidence status | Proposed factual result | Missing evidence or scope decision |
| --- | --- | --- | --- | --- |
| **P550** — Detecting GAN-generated synthetic images using semantic inconsistencies | V1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain identifier-linked official publisher/proceedings paper and volume/event evidence establishing archival container, named event, publication form and any explicitly documented track; keep unknown track empty. Case question: Which named scholarly event contains this paper, is it a proceedings contribution, and what track is explicitly documented? |
| **P586** — Deep Learning applied to Road Accident Detection with Transfer Learning and Synthetic Images | V1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain identifier-linked official publisher/proceedings paper and volume/event evidence establishing archival container, named event, publication form and any explicitly documented track; keep unknown track empty. Case question: Which event is represented by volume 64, what is the paper’s publication form/year relationship, and is any track documented? |
| **P610** — Detection, Attribution and Localization of GAN Generated Images | V1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain identifier-linked official publisher/proceedings paper and volume/event evidence establishing archival container, named event, publication form and any explicitly documented track; keep unknown track empty. Case question: Does the primary proceedings identify Electronic Imaging or MWSF as this paper’s event, and what publication form/track is evidenced? |
| **P633** — Detecting GAN Generated Fake Images Using Co-Occurrence Matrices | V1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain identifier-linked official publisher/proceedings paper and volume/event evidence establishing archival container, named event, publication form and any explicitly documented track; keep unknown track empty. Case question: Does the primary proceedings identify Electronic Imaging or MWSF as this paper’s event, and what publication form/track is evidenced? |
| **R099** — Fake-HR1: Rethinking Reasoning of Vision Language Model for Synthetic Image Detection | R1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contribution/data section and supplement or author release documentation specifying resource contents, reuse and whether its construction/curation is a substantive contribution. Case question: Are Fake-HR1 training examples a separately contributed reusable resource or only method training data? |
| **R117** — Frequency-Aware Robustness Analysis of Deepfake Detection Models | R4 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contribution list and technical specification to establish substantive novelty versus a measurement, baseline ensemble or illustrative survey case study. Case question: Is FSI/associated machinery a substantive new technical method, or only a measurement used by the study? |
| **R127** — GlobalForge: Towards Robust AI-Generated Image Detection | R3 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary introduction/contribution list and controlled-analysis sections to distinguish an independent principal scientific finding from method-supporting validation. Case question: Is the local-artifact fragility diagnosis independently tested as a principal finding, beyond motivating/validating LIB/GSR? |
| **R176** — PRADA: Probability-Ratio-Based Attribution and Detection of Autoregressive-Generated Images | R1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contribution/data section and supplement or author release documentation specifying resource contents, reuse and whether its construction/curation is a substantive contribution. Case question: What is in the released PRADA data, and is its construction/curation a substantial reusable contribution? |
| **R188** — Reasoning-Aware AIGC Detection via Alignment and Reinforcement | Source conflict | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the official ACL Anthology paper/PDF for DOI 10.18653/v1/2026.findings-acl.1043 and authoritative arXiv 2604.19172 record/PDF, matching title, authors, identifiers and abstract before choosing a source association or scope outcome. Case question: Which title/abstract/identifier combination actually belongs to the included image paper, and which text-paper evidence was misassociated? |
| **R189** — Reduce the Artifact Bias for More Generalizable AI-Generated Image Detection | R3 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary introduction/contribution list and controlled-analysis sections to distinguish an independent principal scientific finding from method-supporting validation. Case question: Is there independent systematic evidence for artifact-bias claims beyond motivating and validating ACEF? |
| **R190** — Representation and Reference Selection in Training-Free Synthetic Image Attribution | R1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contribution/data section and supplement or author release documentation specifying resource contents, reuse and whether its construction/curation is a substantive contribution. Case question: Does the reference collection constitute a contributed reusable dataset, rather than inputs for controlled analysis? |
| **R376** — No Detector to Rule Them All | R4 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contribution list and technical specification to establish substantive novelty versus a measurement, baseline ensemble or illustrative survey case study. Case question: Is the ensemble a new technical contribution with its own specification, or an exploratory combination of baselines? |
| **R455** — Deep Image Fingerprint: Towards Low Budget Synthetic Image Detection and Model Lineage Analysis | R1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contribution/data section and supplement or author release documentation specifying resource contents, reuse and whether its construction/curation is a substantive contribution. Case question: Is there a documented new reusable image collection beyond detector/lineage experiments? |
| **R460** — Detecting AI Generated Images Through Texture and Frequency Analysis of Patches | R3 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary introduction/contribution list and controlled-analysis sections to distinguish an independent principal scientific finding from method-supporting validation. Case question: Is any systematic scientific analysis a primary contribution beyond preprocessing/classifier accuracy? |
| **R535** — Which Model Generated This Image? A Model-Agnostic Approach for Origin Attribution | R1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contribution/data section and supplement or author release documentation specifying resource contents, reuse and whether its construction/curation is a substantive contribution. Case question: Does OCC-CLIP contribute a dataset beyond the samples used for few-shot evaluation? |
| **R537** — X-Transfer: A Transfer Learning-Based Framework for GAN-Generated Fake Image Detection | R3 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary introduction/contribution list and controlled-analysis sections to distinguish an independent principal scientific finding from method-supporting validation. Case question: Is there an independent transfer-learning analysis beyond validating the new algorithm? |
| **R548** — DE-FAKE: Detection and Attribution of Fake Images Generated by Text-to-Image Generation Models | R2 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contributions and protocol/release documentation specifying a reusable benchmark/framework, rather than only this method’s experiments. Case question: Does DE-FAKE contribute a reusable evaluation protocol/framework rather than only its own comparative experiments? |
| **R549** — Deepfake Generation and Detection: Case Study and Challenges | R4 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contribution list and technical specification to establish substantive novelty versus a measurement, baseline ensemble or illustrative survey case study. Case question: Is IBMM proposed as an original algorithm/system, or an illustrative survey case study? |
| **R580** — Towards Universal Fake Image Detectors That Generalize Across Generative Models | R1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary contribution/data section and supplement or author release documentation specifying resource contents, reuse and whether its construction/curation is a substantive contribution. Case question: Which new reusable data resource, if any, is contributed beyond evaluating on existing detection data? |
| **R615** — Towards Discovery and Attribution of Open-world GAN Generated Images | R3 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary introduction/contribution list and controlled-analysis sections to distinguish an independent principal scientific finding from method-supporting validation. Case question: Is open-world discovery analysis independently substantive, beyond demonstrating the iterative method? |
| **T024** — AI-Generated Image Homology Detection | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Does the evaluation include authentic images as a real-vs-generated task, beyond same-source pair verification? |
| **T136** — ImageAttributionBench: How Far Are We from Generalizable Attribution? | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Is there a separate real-image/authenticity protocol outside the two recorded attribution settings? |
| **T137** — IncreFA: Breaking the Static Wall of Generative Model Attribution | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Does any IABench protocol classify real images, rather than only known versus unseen generators? |
| **T141** — Learning a Semantic Similarity Orthogonal Space for Model-Level AI-Generated Image Source Attribution | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Is real-vs-generated authenticity evaluated beyond reconstruction-based source matching? |
| **T236** — Unveiling Perceptual Artifacts: A Fine-Grained Benchmark for Interpretable AI-Generated Image Detection | T2 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary method/evaluation sections specifying spatial output, forensic ground truth and a spatial metric; distinguish scored predictions from annotations/attention visualization. Case question: Are spatial artifact predictions scored against the pixel annotations, or are masks used only to analyze/align attention? |
| **T246** — Zooming In on Fakes: A Novel Dataset for Localized AI-Generated Image Detection with Forgery Amplification Approach | T2 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the primary method/evaluation sections specifying spatial output, forensic ground truth and a spatial metric; distinguish scored predictions from annotations/attention visualization. Case question: Is a predicted edited-region mask/patch/box evaluated, or is the output only an image-level decision? |
| **T299** — Detecting Origin Attribution for Text-to-Image Diffusion Models | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Is real/fake discrimination a distinct task, rather than generator/seed/hyperparameter identification? |
| **T446** — Are CLIP Features All You Need for Universal Synthetic Image Origin Attribution? | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Does the open-set protocol contain a real/authentic class and evaluate it as detection? |
| **T503** — ManiFPT: Defining and Analyzing Fingerprints of Generative Models | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Does the full protocol evaluate real/fake detection in addition to fingerprint/model identification? |
| **T527** — Towards Generated Image Provenance Analysis via Conceptual-Similar-Guided-SLIP Retrieval | T3 | `MAINTAINER_SCOPE_JUDGMENT_REQUIRED` | —; not applied | Does training-image provenance retrieval substantively fit a represented core task? If none applies, should this paper remain public under the narrow scope? Preserve source_attribution until that decision. |
| **T572** — Open Set Synthetic Image Source Attribution | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Does the BMVC protocol include a separate authenticity evaluation beyond unknown-generator rejection? |
| **T576** — Single-Model Attribution of Generative Models Through Final-Layer Inversion | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Are real images part of an explicit authenticity task, rather than merely examples of non-membership? |
| **T611** — Does a GAN Leave Distinct Model-Specific Fingerprints? | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Do the reported fingerprint experiments include binary authenticity detection? |
| **T634** — Do GANs Leave Artificial Fingerprints? | T1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the identity-matched primary paper/supplement class definitions and complete evaluation protocol: explicit real/authentic-versus-generated evaluation, or an explicit exhaustive attribution-only protocol. Case question: Does the complete experiment protocol include real/fake detection beyond source identification? |
| **U010** — Diffusion-Driven Forgery Detection: Distilling Latent Features for Generalized Image Forensics | I1 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the IEEE paper-time author superscripts and affiliation block for Kaiwen Qian, Yutao Xu, Yifan Xu and Yuchun Fang; distinguish Shanghai University, SUES and any genuine dual affiliation. Case question: Which paper-time affiliation marker belongs to each of Kaiwen Qian, Yutao Xu, Yifan Xu and Yuchun Fang: Shanghai University, SUES, or genuinely both? |
| **U017** — Unified Detection of Synthetic and Manipulated Images via Dual-Stream Artifact Fusion | I2 | `EXTERNAL_PRIMARY_SOURCE_REQUIRED` | —; not applied | Obtain the ACM paper-time author superscripts and affiliation block for Thinh-Phat Vo, Daniel Mai, Minh–Triet Tran and Trong-Le Do; establish the named member and any explicitly separate parent affiliation. Case question: How do the ACM paper’s affiliation markers assign Thinh-Phat Vo, Daniel Mai, Minh–Triet Tran and Trong-Le Do to the member and parent; are those separately listed affiliations? |

External requirements group into **13 task**, **15 research-type**, **2 institution**, **4 venue** and **1 source-conflict** checks. Task checks need evaluated class/protocol or spatial-output/metric evidence; research-type checks need contribution-level resource/protocol/analysis/novelty evidence; institution checks need paper-time affiliation blocks and author superscripts; venue checks need identifier-linked official paper/volume/event/type/track evidence. These are future evidence requirements, not authorized collection in this phase.

R188 was reviewed separately across all locally retained matches. Its current title is generic AIGC rather than literally “image”; the historical image/text association warning is preserved without adopting that wording as a new fact. The substantive abstract copies consistently discuss AIGC-textbank/REVEAL and text authorship. Downstream repetition is not independent authentication. Obtain matching official ACL Anthology and arXiv title/author/identifier/abstract evidence before any label or scope decision.

### D4. Recomputed corpus and taxonomy

Public **640**; formal **532**; mapped **617**; relationship rows **1,422**; unique paper–institution pairs **1,422**.

| Label | Before | After |
| --- | ---: | ---: |
| `detection` | 593 | 593 |
| `source_attribution` | 85 | 85 |
| `localization` | 40 | 41 |
| `method` | 548 | 548 |
| `dataset` | 134 | 133 |
| `benchmark` | 89 | 88 |
| `survey` | 20 | 20 |
| `analysis_study` | 79 | 78 |

These totals were counted from the authoritative registry and checked against the public paper export. Three public papers and their nine map rows change only their approved taxonomy dimension and review reason. No public identities, affiliations, provenance, coordinates or relationship pairs change.

### D5. Focused validation and integrity

Focused tests: **14 passed, 0 failures**. Broader targeted regression: **240 passed, 9 subtests passed, 0 failures**. Full repository suite: **1,641 passed, 389 subtests passed, 0 failures, 2 existing warnings** in 299.09 seconds. The warnings remain the two `PytestReturnNotNoneWarning` instances in the legacy scope-migration receipt helpers. Curated validator: **0 errors, 252 existing warnings**. Public validator: **0 errors, 23 existing warnings**. Key-paper freshness check: **0 errors**. `git diff --check`: passed.

The first collected full run exposed thirteen missing-Node invocation failures, one stale Phase 1 localization-count expectation and four historical tests treating unarchived `.DS_Store` bytes as semantic content. The final run used the established Node runtime, updated the reviewed current-task baseline and excluded OS metadata from semantic historical integrity while retaining it for old report replay. No corpus remediation was added.

The second established-pipeline export was byte-identical for both public JSON files: `EXPORT_REPRODUCIBLE = 1`. The original audit queues, all other tracked inputs, 49 frozen NeurIPS artifacts and all 128 excluded local files were verified against the phase-start hashes.

```text
UNEXPECTED_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
```

Tracked modifications: `data/curated/paper_taxonomy.csv`, `data/curated/papers.csv`, `web/data/public_preview_map_data.json`, `web/data/public_preview_papers.json`, `docs/key_paper_coverage_report.md` (generated fingerprint only), `tests/baseline_expectations.py`, `tests/public_refinement_snapshot.py`, and `tests/test_corpus_quality_batch_a.py`. The three test-support changes update the reviewed localization count, keep historical Batch A validation bound to its committed receipt, and exclude `.DS_Store` from semantic historical integrity. Audit-specific untracked files: this decision sheet, `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json`, and `tests/test_corpus_quality_batch_c_phase1.py`. The other 128 untracked files are the unchanged excluded local captures/diagnostics/responses, totaling 131 untracked files.

Index empty; HEAD remains the committed Batch A baseline; no commit and no push. NeurIPS remains `7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`.

`BATCH C PHASE 1 COMPLETE — LOCAL EVIDENCE TRIAGED`
