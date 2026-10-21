# Batch B Wave B1I — R574 benchmark added; R215 retained

Maintainer-approved adjudication of the completed evidence-only packet at published baseline `bb4b60b2ee612331b997d7482edaa1e9e657cff2`. The baseline was fetched and verified before application. Existing 84 lightweight and 32 independent packet checks, all reviewer findings, two complete primary manuscripts and their source receipts were recovered; no scientific retrieval was repeated.

| Review | Accepted outcome | Final research types | Authoritative result |
|---|---|---|---|
| R215 | `SUPPORTED_NO_CHANGE` | `method` | No paper/taxonomy/provenance CSV change; one terminal review closure |
| R574 | `PROPOSE_CORRECTION_ACCEPTED` | `method;dataset;benchmark` | Benchmark added; one terminal review closure |

Terminal IDs: R215 **`review:dccd35b22dfc68d14007`**; R574 **`review:ababbf1503d62744757e`**. Both use supported queue `other` / action `no_action_after_review`, recording that the approved bounded action is complete. Registry rows **87 → 89**, with every earlier byte preserved. Actual application UTC: **2026-10-21T01:04:42Z**. R574 `audited_at` is **2026-10-21**, the actual completed evidence/adjudication date; the wave identifier and original filenames remain 2026-10-20. No retrieval timestamp is backdated.

## Accepted R215 policy judgment

TAP is a substantive feature-aggregation method using patch and global VFM features. The independently interpretable comparison is valuable: **42 configurations / 15 encoders / six VFM families**, standardized frozen encoders and linear heads. Table 4 gives PE-G **89.54 F1 / 89.81 accuracy** versus CLIP@336 **75.63 / 77.45**; TAP OpenSDI **92.94 / 92.96**. The GenImage counterexample **97.16 → 95.67** remains explicit.

Under the maintainer's conservative application of locked R2, the evidence does not clearly establish a separate contributed reusable benchmark framework beyond standardized model selection and comparative experiments supporting TAP (§4.2.1 under ablation/evaluation). **Retain `method` and `detection`; add no benchmark.** This is a bounded **medium-confidence policy judgment**, not proof of no reusable value.

The competing **permissive** R2 interpretation remains preserved: the broad standardized comparison could itself qualify as a reusable systematic comparative framework and support `method;benchmark`. New datasets, source code, new split registries or a location outside an ablation section are **not mandatory R2 conditions**; their absence alone does not reject benchmark. The known independent-framework argument was explicitly considered. No clearly independent benchmark specification not considered in the maintainer's rationale was found in the existing B1I primary evidence. The original worker recommendation, its reconsideration and all positive/countervailing evidence remain intact below and in the manifest.

The source is the official **CVPR Workshops 2026** CVF accepted manuscript, not CVPR Main. IEEE-final/arXiv equivalence and exact numerical reproduction remain unverified. All R215 canonical, taxonomy and public fields remain unchanged.

## Accepted R574 benchmark contribution

POSE contributes a progressive open-space method; existing method and dataset roles remain. The separately reusable **OSMA evaluation framework** supplies class definitions, split scenarios, known/unknown protocols, comparison baselines and accuracy/AUC/OSCR metrics. Five configurations each use **15 known classes** and **53 unknown generators: 10 seed / 22 architecture / 21 training-dataset** cases. Table 4 reports **94.81 accuracy / 82.76 combined AUC / 80.50 OSCR**. **PRNU seed AUC 69.20 exceeds POSE 68.15**; no uniform superiority is claimed. Add `benchmark` while preserving `source_attribution` and `fully_generated`.

Official POSE commit `185b25d9160e09b57c62cea23f08b2b126b62798` confirms split1 **59,998 train / 7,500 validation / 8,000 closed-test / 26,500 unknown-test** entries and **101,998 distinct literal paths**, without literal overlap. This is a split1 metadata footprint, not verified completeness of the full dataset or proof of image-content/subject/video independence. Other four sample-level annotation payloads, complete image/checkpoint availability, source-training equivalence, fixed deployment thresholds and numerical reproduction remain unverified. Only the official CVF accepted CVPR 2023 Main manuscript was reviewed; IEEE-final/alternate-version equivalence remains unverified. Original partial transfer plus matching-ETag continuation still count as **one** R574 manuscript; R215 contributes the other, exactly **two** complete manuscripts across the evidence wave.

## Exact authoritative and deterministic output changes

Seven existing CSV cells change, all on R574: one `papers.csv` compatibility type cell and six `paper_taxonomy.csv` research-type/provenance/audit fields. Existing reviewed statuses, canonical timestamps and all unrelated rows/bytes remain exact. R215 receives no corpus edit. Exactly two terminal decision rows are appended.

The established offline exporter changes **one public paper record** and **three pre-existing R574 map records**, only `research_types` and dependent research-review reason. **All 673 other public paper records**, including R215, and **all 1,410 relationship identities** remain unchanged. All other 1,407 map records are exact. No task, image scope, publication, inclusion, author, affiliation or institution change occurs. The only nonrecord generated changes are a synchronized snapshot timestamp, the same report timestamp and the key-coverage input fingerprint. Other generated report rows and both legacy generated CSVs remain byte-identical. No generated JSON was manually patched.

## Recomputed current corpus and review accounting

| Measure | Current value |
|---|---:|
| Public / formal / mapped / unmapped | 674 / 557 / 613 / 61 |
| Relationship rows / unique pairs | 1410 / 1410 |
| Detection / source attribution / localization | 621 / 84 / 45 |
| Method / dataset / benchmark / survey / analysis study | 578 / 134 / 91 / 21 / 82 |
| Original Batch B actions / historical papers | 159 / 148 |
| Historical unresolved / active-public unresolved / affected public papers | 145 / 143 / 132 |

Only R215 and R574 close. Distinct affected papers were independently recomputed: neither has another pending original Batch B action. All other pending actions and prior decisions remain; R267, T046, T093, T608 and T526/P526 stay open. Batch C's same 13 debts and the independent 39-paper import inventory (14 overlapping taxonomy debts / 12 held candidates) remain unchanged.

## Preservation and validation

The full original JSON/report bytes are authenticated in `evidence_only_packet_archives` as portable gzip/base64 payloads. Original scientific records, tables, reviewer history, source fingerprints, retrieval counts and all transport/version/release limitations are preserved; current accepted dispositions are separate fields. Historical test repairs pin exact B1H transactions to their published `bb4b60b…` endpoint without changing old counts/hashes. Shared current benchmark totals move 90 → 91; live selected-case, prior-decision-prefix, relationship and current-total checks remain strict. New focused regressions cover the complete successor delta. No frozen fixture or historical receipt is rewritten.

<!-- B1I_ADJUDICATION_VALIDATION_START -->
**Focused validation passed: 375 ordinary tests and 12 subtests**, including all 23 B1I regression cases; zero failures/errors/skips. All four current-scope validators passed with zero errors. Existing warnings remain visible: curated 294; public map 0/paper preview 62; exclusions 2; key coverage 0.

**The complete repository suite ran once and passed 2028 ordinary tests and 389 subtests**; zero failures/errors/skips. The two existing legacy return-value warnings remain unchanged. Python 3.14.7, pytest 9.1.1, pytest-subtests 0.15.0 and Node 24.19.0 were used with the documented offline fixtures and authorized localhost. All 4596 source/input/output paths remained byte-identical after completion.

After the successful full suite, **two sequential offline export verification passes passed**. All 4596 compared paths, seven deterministic outputs and 119 operational inputs were byte-identical in each pass. Read-only fixture checks before/after verified 117 inputs, creating/replacing none. One initial correction export and exactly two verification exports completed, without parallel exporters. `EXPORT_REPRODUCIBLE = 1`.

The measured semantic/preservation gate passed 69/69 checks. R574 alone changes in one public record and three existing map rows; all 673 other papers, all 1,407 other map records and all 1,410 relationship identities remain unchanged. R215's entire canonical/taxonomy/public data remain unchanged. Exactly two terminal rows close R215 and R574; all prior decisions and remaining review questions are preserved. Original 84 lightweight checks and 32 independent packet checks remain separately preserved.

`FOCUSED_FAILURES = 0`

`VALIDATOR_ERRORS = 0`

`FULL_SUITE_FAILURES = 0`

`EXPORT_REPRODUCIBLE = 1`

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

The complete suite and both sequential exports ran on byte-identical scientific data, code, original evidence and pending-receipt packet bytes. Only this manifest and report completion-receipt fields are finalized afterward. They are not exporter inputs. A final read-only gate verifies final receipt bytes and rechecks every invariant. No additional full-suite or export run after its own receipt is claimed.

This packet is validated for the explicit 12-file commit allowlist. Publication remains pending; successful publication will be verified externally against the actual remote SHA after normal fast-forward push.
<!-- B1I_ADJUDICATION_VALIDATION_END -->

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Preserved complete evidence-only report

Everything following is the original evidence-stage report, preserved verbatim. Its provisional decisions, then-current counts, zero-authoritative-change observations and untracked-file state describe that earlier stage. They are superseded administratively by the accepted dispositions above. The scientific findings, counterevidence, source restrictions and original validation remain part of the audit trail.

---

# Batch B Wave B1I — benchmark contribution evidence

Evidence-only review of **R215 and R574**, based on fetched `bb4b60b2ee612331b997d7482edaa1e9e657cff2`. Wave filenames retain the requested 2026-10-20 date; completion receipts use actual UTC timestamps. No taxonomy, task, inclusion, publication, institution, review-decision or export change is applied.

| Review | Provisional outcome | Current complete types | Proposed complete types |
|---|---|---|---|
| R215 | `MAINTAINER_DECISION_REQUIRED` | `method` | Retain `method` pending R2 threshold decision; conditional `method;benchmark` |
| R574 | `BENCHMARK_ADDITION_SUPPORTED` | `method;dataset` | `method;dataset;benchmark`, only if accepted |

Both original actions remain unresolved. Evidence completion closes zero reviews. Scientific sufficiency and maintainer acceptance are separate: R215 has sufficient facts but a contribution-threshold judgment; R574 has sufficient scientific benchmark evidence, pending acceptance.

## Locked policy and recovered work

**R1 (ACCEPT, 2026-10-05)**: Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.

**R2 (ACCEPT, 2026-10-05)**: Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

**R3 (ACCEPT, 2026-10-05)**: Assign analysis_study only when systematic empirical or theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps, or supporting interpretability figures do not qualify by themselves.

**R4 (ACCEPT, 2026-10-05)**: Assign method only when the paper contributes substantive technical novelty: a method, algorithm, model, procedure, or system. Pure surveys, benchmarks, datasets, or analysis studies do not gain method merely because they implement baselines. Multiple legitimate research-type roles remain allowed.

The original local search found no complete identity-matched manuscripts. The prior workers recovered canonical identities, exact original questions, 87 unchanged decision rows, current totals and protected snapshots. Both complete PDF downloads, R574 byte recovery, R215 full-paper/table review and the initial 32-check preservation receipt are reused. The resumed work completes bounded POSE release checks and consolidates the existing worker findings.

## R215 — TAP into the Patch Tokens

Canonical ID `curated:98977aa8b726ead071fe`. Ahmed Abdullah, Nikolas Ebert, Oliver Wasenmüller. **CVPR Workshops 2026 / SAFE**, not the main conference. The canonical DOI is empty; existing arXiv ID `2604.26772` is preserved without asserting equivalence. Current task `detection` and type `method` are retained.

Original question: Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: The paper presents a comparative VFM benchmark across families, objectives, resolutions and scales.

[Official CVF PDF](https://openaccess.thecvf.com/content/CVPR2026W/SAFE/papers/Abdullah_TAP_into_the_Patch_Tokens_Leveraging_Vision_Foundation_Model_Features_CVPRW_2026_paper.pdf): **759,249 bytes, 11 pages, proceedings 379–389**, SHA256 `f287854182676a679bde7ae3ce022fff0769b7ec792f3a31ec587125ccb558ec`. All 11 pages were reviewed, including scientific content through p.386 and references. This is the official CVF accepted workshop manuscript; IEEE-final/arXiv equivalence was not independently checked. The HTML parser returned 403; the single direct PDF transfer returned HTTP 200.

### Contributions and protocol

TAP is an independent detection method: a frozen encoder supplies final CLS and patch tokens; a learned query attends to normalized tokens, a residual two-layer MLP and projection produce a pooled token, and pooled/CLS features feed a binary classifier (§3, Eqs.1–3, Fig.3). No intermediate-layer sweep is established. Table 4 separately fits a linear classifier to frozen encoders; “out of the box” does not mean zero-shot authenticity classification. Non-ViT feature-pooling details are incomplete.

The full Table 4 matrix is preserved in the manifest: **6 families, 15 named encoders, 42 encoder/resolution configurations**, with F1 and accuracy for SD1.5, SD2.1, SDXL, SD3 and Flux. SD1.5 is the training family; the other four are unseen-generator conditions. The reported mean includes all five.

| Family | Encoders and input resolutions | Configurations |
|---|---|---:|
| DINOv2 | ViT-L/G/14, each 224/448/672/896 | 8 |
| DINOv3 | ViT-L/16, ConvNeXt-Large, ViT-H+/16, ViT-7B/16, each 256/512/768/1024 | 16 |
| SAM2.1 | Hiera-Large, 1024 | 1 |
| CLIP | ViT-L/14, 224/336 | 2 |
| SIGLIP2 | L/16 and SO400M/16: 256/384/512; SO400M/14: 224/378; NaFlex/16: 256/384/512; gopt/16: 256/384 | 13 |
| PE-Core | ViT-L/14 at 336; ViT-G/14 at 448 | 2 |

The manuscript contrasts image-text CLIP-style models with self-supervised DINO teacher–student learning and includes SAM2.1 segmentation features. Exact per-family pretraining losses, source checkpoints and complete recipes are not supplied; no unretrieved model-paper details are invented.

All forensic datasets are existing resources: **GenImage**, **Chameleon**, and **OpenSDI**. GenImage/Chameleon training uses 162k SD1.4 images plus 162k ImageNet real images; OpenSDI uses 100k Megalith-10M real images plus 100k fully generated/inpainted SD1.5 images. The latter mixture ratio is not specified. The VFM comparison uses existing OpenSDI partitions rather than newly released split annotations.

Implementation (§4): AdamW, learning rate 1e-4, weight decay 1e-2, betas 0.9/0.999, batch 128; one-epoch-equivalent 2,532 GenImage/Chameleon or 1,569 OpenSDI iterations; JPEG quality 30–100 and Gaussian blur kernels 3/5, each probability 0.5; one H100. Exact scheduler, seeds, head-loss/threshold, checkpoints, validation selection, crop/normalization and run uncertainty remain underspecified.

### Quantitative evidence and counterexamples

| Location / setting | Exact result (%) |
|---|---|
| Table 4, CLIP L/14@336 versus PE G/14@448, no TAP | Mean F1/accuracy 75.63/77.45 → 89.54/89.81; accuracy +12.36 percentage points |
| Table 4, CLIP L/14@224 | 70.54/67.10; do not conflate this with CLIP@336 |
| Tables 2/5, PE G on OpenSDI | No TAP 89.54 F1 / 89.81 accuracy; TAP 92.94 / 92.96 |
| Table 2, DualSight comparator | 88.57 F1 / 89.13 accuracy; TAP gain 4.37 / 3.83 points |
| Table 3, Chameleon | PE G+TAP accuracy 95.64 versus OMAT 66.05 (+29.59 points); matched no-TAP accuracy 92.11 |
| Table 3, class trade-off | Generated accuracy 99.19 → 91.47; real accuracy 86.78 → 98.78 with TAP |
| Table 1, GenImage counterexample | PE G mean accuracy falls 97.16 → 95.67 with TAP; Midjourney 94.92 → 82.11 |

Table 5 contains seven matched TAP comparisons across CLIP, SIGLIP2 and PE; all are retained in the manifest. Baseline Table 1 results marked by the authors are inherited from prior papers, not all independently retrained. Model family, scale, input resolution and pretraining data covary; comparisons do not isolate a causal pretraining-objective effect.

### R2 boundary and provisional disposition

**`MAINTAINER_DECISION_REQUIRED`**. Contribution (i) separately claims the VFM benchmark; Table 4 supplies a shared fitting recipe and independently interpretable original comparisons without TAP. Those facts plausibly satisfy R2’s **systematic comparative framework** route. No new task, dataset, split registry, code release, or placement outside an ablation section is required by the locked rule. Their absence cannot establish a factual disqualification.

The initial worker recommended `SUPPORTED_NO_CHANGE` with medium confidence because the comparison supports backbone selection and method evaluation. That complete review is preserved unchanged in the manifest, alongside an explicit reconsideration recognizing that no concrete mandatory framework criterion was shown absent. This is a genuine contribution-threshold question, not an inaccessible-manuscript outcome or a new policy.

Maintainer question: does the independently usable 42-configuration comparison and published shared recipe on inherited OpenSDI data meet the accepted R2 framework route? If yes, the complete proposed set is `method;benchmark`; otherwise retain `method`. Current administrative proposal is `method` pending that decision. Factual confidence is high; threshold confidence is medium. No `analysis_study` adjudication is made. No new release/evaluation suite was verified within the reviewed manuscript; no R215 repository or alternate paper was retrieved.

## R574 — Progressive Open Space Expansion

Canonical ID `curated:297bed46b62fdf89c9ab`. Tianyun Yang, Danding Wang, Fan Tang, Xinying Zhao, Juan Cao, Sheng Tang. DOI `10.1109/cvpr52729.2023.01522`; CVPR 2023 main conference, pp.15856–15865. Current task `source_attribution` and types `method;dataset` are retained.

Original question: Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: The work constructs an OSMA benchmark covering three unknown-generator scenarios.

[Official CVF PDF](https://openaccess.thecvf.com/content/CVPR2023/papers/Yang_Progressive_Open_Space_Expansion_for_Open-Set_Model_Attribution_CVPR_2023_paper.pdf): **2,768,471 bytes, 10 readable pages**, SHA256 `5ddd9e1df687106483b1d6f2504119042088daf818ad51521bb42a2f8157e891`. All pages were reviewed and Tables 1–6 visually checked. The official CVF accepted version was reviewed; IEEE-final/alternate-version equivalence is unverified.

### Separate scientific roles

**Method:** POSE progressively introduces small two-convolution augmentation networks with reconstruction/diversity objectives to simulate unknown-source fingerprints, paired with DCT/convolution features and an MLP task classifier (§3, Algorithm 1). Inputs are resized to 128 pixels; task/augmentation learning rates are 1e-4/1e-2 with Adam and a step scheduler. This is independent of the evaluation resource.

**Dataset:** curated real-source and generator-domain imagery supports controlled source-model comparisons (§4.1, Table 1). Existing `dataset` remains administratively intact; this wave does not re-adjudicate it.

**Benchmark:** OSMA defines known-source classification plus unknown-generator rejection, three controlled unknown conditions, five split configurations, known/open testing groups, metrics and adapted attribution/OSR baselines. These reusable design elements and released annotations independently support R2; the judgment does not rest on the authors’ benchmark word or repository existence alone.

Each published split has **15 known classes** (real plus 14 generators) and **53 unknown generator classes**: 10 different-seed, 22 different-architecture, and 21 different-training-dataset cases. Seed cases hold architecture/data fixed; architecture cases retain training data; dataset cases reuse known architectures on different data (Tables 1–2). The complete class lists are retained in the manifest. Seven known real-source groups include CelebA, Face-HQ, ImageNet, YouTube/FaceForensics-derived frames and LSUN bedroom/cat/bus. Unknown COCO and Summer real images remain in the known real class at test time (Table 3). Unknown-model rejection is not reinterpreted as a newly adjudicated binary detection task.

### Release correspondence and sample accounting

[Author-linked POSE release](https://github.com/ICTMCG/POSE/tree/185b25d9160e09b57c62cea23f08b2b126b62798) is pinned to commit `185b25d9160e09b57c62cea23f08b2b126b62798` (2023-10-22). Its complete tree and all five configuration class lists were inspected. Twelve bounded text documents/metadata files (8,053,911 bytes) were read and verified against exact Git blob hashes: README, configuration, dataset loader, test/evaluation definitions, and seven split1 annotation files. No code was executed and no image, checkpoint, archive or supplementary manuscript was downloaded.

All five configurations have disjoint 15/10/22/21 class lists and train/validation/known-test/all-unknown/three-scenario annotation paths. Their union names **81 generator domains plus real**, so the paper’s 67 generators/68 total classes is a **per-split** statement, not the complete released universe. Names are not a verified model-weight inventory.

| Released split1 annotation | Exact rows / distinct literal image paths | Classes |
|---|---:|---:|
| Train | 59,998 | 15 |
| Validation | 7,500 | 15 |
| Closed test | 8,000 | 15 |
| Combined unknown test | 26,500 | 53 |
| Unknown seed | 5,000 | 10 |
| Unknown architecture | 11,000 | 22 |
| Unknown dataset | 10,500 | 21 |

The four core sets have **101,998 distinct literal paths**, zero pairwise overlap and no within-file duplicate paths. The three scenario files are disjoint and exactly reproduce the combined unknown set; each unknown source has 500 listed examples. Combined unknown labels use offsets 0/10/32; scenario-local labels are a separate namespace. Known class 0 is real, including 250 COCO and 250 Summer closed-test entries. Unknown label 0 denotes a generator, not real. These observations directly support correspondence with the published scenario design.

These are metadata counts for split1, not verified physical image counts for the approximately 50GB hosted dataset. The other four annotation payloads, image-content/subject/video/near-duplicate independence, all source-model training equivalences, hosted asset accessibility and checkpoint completeness were not verified. Zero literal overlap does not establish those stronger claims. The README’s script paths and test flag differ from the pinned tree/parser; these discrepancies are recorded without changing upstream code or running reproduction.

### Metrics, comparisons and exact results

Inference uses a maximum softmax confidence threshold for known-source acceptance; otherwise unknown. No fixed numeric deployment threshold or independently validated selection rule was established. Known accuracy uses argmax; AUC measures known/unknown confidence discrimination; OSCR integrates correct known classification versus unknown acceptance. Pinned test/evaluation definitions compute confidence curves rather than introducing a fixed binary real/fake protocol.

Tables 4 and 6 average five splits. Full baseline matrices and clustering Table 5 are retained in the manifest.

| Table 4 / POSE | Accuracy | Seed AUC / OSCR | Architecture AUC / OSCR | Dataset AUC / OSCR | All AUC / OSCR |
|---|---:|---|---|---|---|
| POSE | 94.81 | 68.15 / 67.25 | 84.17 / 81.62 | 88.24 / 85.64 | 82.76 / 80.50 |
| DNA-Det | 93.56 | 61.46 / 59.34 | 80.93 / 76.45 | 66.14 / 63.27 | 71.40 / 68.00 |
| PRNU | 55.27 | 69.20 / 49.16 | 70.02 / 49.49 | 67.68 / 48.57 | 68.94 / 49.06 |

PRNU’s seed AUC **69.20 exceeds POSE 68.15**; do not claim uniform superiority. Other attribution comparators are Yu et al., DCT-CNN and RepMix. Table 6 compares a common base model with OpenMax, PROSER, ARPL+CS and DIAS; Base all-unknown AUC/OSCR is 73.78/70.97, Base+AM 80.31/77.80, POSE 82.76/80.50. The reported comparisons are not independently rerun. Table 5 additionally reports clustering purity/NMI/ARI at k=49 and k=68; no all-metric advantage is claimed.

### Provisional disposition

**`BENCHMARK_ADDITION_SUPPORTED` → `method;dataset;benchmark`**, high scientific confidence, pending maintainer acceptance. The original OSMA task/split/scenario/metric framework is supported independently of the POSE algorithm and underlying data, with bounded release correspondence verified. Existing `source_attribution` is preserved. No taxonomy change, review closure or terminal decision is applied.

## Retrieval and integrity boundaries

Exactly **two complete primary manuscripts** were retrieved in this wave, one per paper; none was redownloaded during recovery. R215 used one HTTP 200 PDF response. R574’s first response timed out after **1,182,618 / 2,768,471 bytes**; the single HTTP 206 continuation supplied exactly **1,585,853 remaining bytes**, range 1182618–2768470, with matching ETag `"2a3e57-5fb32ecc7b1c0"`. Their concatenation, full length, checksum, PDF structure and all ten readable pages were verified. Partial and continuation receipts remain intact; two R574 HTTP responses count as one manuscript. No alternate versions or supplements were retrieved.

The two evidence files are the only intended repository outputs. Baseline corpus: **674 public, 557 formal, 613 mapped, 61 unmapped, 1,410 relationship rows and unique pairs**. Tasks: **621 detection / 84 source attribution / 45 localization**. Research types: **578 method / 134 dataset / 90 benchmark / 21 survey / 82 analysis study**. Original Batch B inventory remains **159 actions / 148 papers**, with **147 historical unresolved actions** and **145 active-public unresolved actions across 134 papers**. Both B1I actions remain pending. Batch C’s 13 deferred cases and the separate 39-paper inventory remain unchanged.

<!-- B1I_VALIDATION_START -->
**84 lightweight checks passed, zero failures:** 51 scientific/provenance checks and 33 preservation/accounting checks. Independent scientific review and 32 draft-packet checks also passed. PDF identity, byte counts, checksums, page readability, exact R574 range assembly, pinned documentation hashes, quantitative matrices, annotation counts and policy boundaries were verified. These are scoped evidence checks, not the full repository suite; no exporter or scientific code was run.

All 4,474 isolated tracked files, the 87-row decision registry and 16 prior B1A–H artifacts remain byte-identical. Primary HEAD/status, all 4,414 tracked files and all 305 pre-existing untracked files are preserved, including the protected 128. All 49 frozen NeurIPS artifacts, ignored operational/historical inputs, Batch C’s 13 deferred cases and the separate 39-paper inventory remain intact.

`AUTHORITATIVE_CORPUS_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

The isolated tracked tree is clean, index empty, and HEAD/fetched origin remain `bb4b60b2ee612331b997d7482edaa1e9e657cff2` with ahead/behind 0/0. Exactly the requested report and manifest are untracked and unstaged; no review was closed, no terminal decision appended, and nothing committed or pushed. Check receipts are recorded after completion; final read-only checks bind the finalized artifacts without modifying scientific findings.
<!-- B1I_VALIDATION_END -->

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
