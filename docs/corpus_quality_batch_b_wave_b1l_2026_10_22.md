# Batch B Wave B1L — R181 and R335 dataset contributions accepted

Maintainer-approved adjudication of the completed B1L evidence packet at published baseline `78f6ebae879f630eb6e386d92ab90252af09670d`. Exactly **R181** changes `method` → **`method;dataset`**, and **R335** changes `benchmark` → **`dataset;benchmark`**. Both retain `detection` and `fully_generated`; no `method` is added to R335. Both original research-type reviews close as **`PROPOSE_CORRECTION_ACCEPTED`** after the corrections. No new action, forensic task, image scope, publication or inclusion change is made.

Actual application UTC: **2026-10-23T02:02:20Z**; actual taxonomy audit date: **2026-10-23**. Terminal decisions are **`review:dff9bf2a84a9e1c0607f`** for R181 and **`review:3d7ddf44e6b74745d848`** for R335. Both use supported queue `other`, target `paper`, action `no_action_after_review` after the corrections, signifying no further work for these exact accepted reviews. It does not signify no data changed. Registry rows **92 → 94**, preserving every pre-existing byte as a prefix.

## Accepted R181 dataset rationale and limits

**Quality-Aware Calibration for AI-Generated Image Detection in the Wild**, `curated:bb388762c1cb4bd3bf4a`, retains its substantive QuAD `method`. The complete **10-page arXiv 2604.15027v1** author manuscript dated **16 April 2026** is the reviewed source: `https://arxiv.org/pdf/2604.15027v1`, **1,215,364 bytes**, SHA256 **`50f03fe6fc43c628b763a56d76582706a210e15806a1ac94e2c925ca6cef5415`**. No complete proceedings-final manuscript was retrieved or compared; the stored CVPRW URL is canonical metadata only, not complete cached publisher-final evidence.

Locked **R1** requires original resource construction, release, curation or systematic provision as a substantive contribution rather than routine internal experimental data. **AncesTree** has **100 real + 1,000 synthetic = 1,100 roots**, **five degradation levels**, **124 descendants per root** and **136,400 descendant images**, excluding the roots. Structured crop → resize → compression trees, not merely a large collection, supply reusable propagation and quality research conditions. **ReWIND** extends existing known images with real web near-duplicates: **9,646 instances**, **4,367 real / 5,279 fake**, **162 groups** (**87 real / 75 fake**). Known in-lab construction histories are not conflated with unknown true web histories.

Construction and evaluation using **six detection methods** establish substantive reuse beyond the proposed calibration model. Mean **balanced accuracy / NLL** on AncesTree is naive **73.2/.75** → QuAD **81.6/.43**; ReWIND **63.0/1.27** → **70.3/.63**. These are **+8.4 and +7.3 percentage points** in balanced accuracy, averages across six methods, not universal improvements. CO-SPY ReWIND QuAD **62.3/.83** is worse than naive **65.7/.81**; B-Free AncesTree QuAD **97.1/.14** is below LoDa20 **98.4/.08**. Preserve approximate 50% AncesTree development fitting versus held-out evaluation and distinguish ReWIND transfer QuAD from ReWIND-trained leave-one-out **QuAD***.

The exact root/semantic-group development split safeguards, validation seed, leave-one-out evaluation unit and independence are not established. Correlated near-duplicates make conditional independence approximate; leakage cannot be ruled out. Repository documentation/file listings are evidence of intended provision, not verified image availability, CSV contents, parent-edge annotations or full dataset release. Complete licensing and independent reproduction remain unverified. The source is the pinned arXiv v1, with publisher-final equivalence unverified. These limitations qualify practical reuse without erasing the demonstrated substantive R1 contribution.

## Accepted R335 dataset rationale, limits and chronology

**Forged Calamity: Benchmark for Cross-Domain Synthetic Disaster Detection in the Age of Diffusion**, `curated:5ad6cb3411820ff01a03`, retains **`benchmark`** and gains **`dataset`**; it does not gain `method`. Reviewed source: complete reused **15-page arXiv 2606.18554v1**, dated **17 June 2026**, `https://arxiv.org/pdf/2606.18554v1`, **6,249,493 bytes**, SHA256 **`ac3a0f8e7a8b0751991420898bb31e4b3dadf8f629360cddde4547b2d4d27dc1`**. DOI-matched cached publisher HTML corroborates scientific prose and table captions, but lacks numerical table bodies or verified full final-PDF equivalence. Original cache transport timing is unknown and is not invented.

The resource has **30,000 images = 6,000 real + 24,000 synthetic**, four categories **Fire, Earthquake, Flood, Thunderstorm**, and four generators **SD1.5, SD2.0, SDXL, PixArt**. Each real category and fake generator/category stratum contains 1,500 images; overall binary classes are **1:4**, not balanced. Section 3.1 cites Incident1M **and Internet** real images, unlike the shorter introduction. The documented sequence is real-image curation → **Moondream captions** → **Llama 3 prompt refinement** → text-to-image diffusion generation → cited similarity filtering. Direct image-to-image operation or one-to-one ancestry is not established. This original curated/generated disaster resource is substantive independently of its retained reusable cross-domain benchmark protocol, supporting R1.

Fine-tuning uses **1,500 real + 1,500 SD1.5 earthquake images**, followed by **18 unseen subsets**. **20 zero-shot subsets** use external pretrained weights without adaptation; these protocols remain distinct. Results are **per-subset accuracy percentages**, not pooled detector accuracy, AUROC, AP or certified balanced accuracy. CGL fake-Flood is **99.68% for SD1.5** versus **1.46% for SD2.0**; ViT's relevant Flood value is **99.43**, not the historical checker-label typo. Performance is variable, not uniform generalization.

All contradictions remain: section 4.2 says **eight** backbones but lists/tables **six**; ConvNeXt thunderstorm prose **98.1/49.7** conflicts with printed Table 2 **9.84/0**; **12 CGL fake-subset values repeat** across fine-tuned and zero-shot tables without an established explanation. Every original quantitative cell and interpretation is retained; none is silently repaired. Full assets, exact split files, source/prompt disjointness, duplicate/leakage safeguards, checkpoints, seeds and similarity-filter threshold remain unverified. Manuscript licensing does not establish original image rights or dataset licensing. No complete-release or numerical reproduction claim is made.

Publication chronology remains explicit and **no bibliographic field changes**: **SOICT 2025** conference designation; arXiv v1 **17 June 2026**; publisher first-online **12 August 2026**; citation/copyright **2027**. Canonical year remains **2025**, with venue, DOI **10.1007/978-981-92-2600-9_17**, arXiv identifier and all authors unchanged. A separately authorized bibliographic review may reconcile the canonical convention if needed. It is not a new historical Batch B action or an adjudication within B1L.

## Measured authoritative and public delta

Exactly **14 existing CSV cells across four rows** change: two `papers.csv` research-type compatibility cells; six cells in each existing `paper_taxonomy.csv` row (`research_types`, bounded reason, `primary_paper` evidence tier, pinned arXiv source URL, factual excerpt and actual audit date). All task/scope/status fields, canonical created/updated timestamps, bibliographic metadata, author/affiliation/institution identities and inclusion stay unchanged. R335's original benchmark scientific justification remains in the exact preserved original record and old taxonomy snapshot; the accepted taxonomy adds a dataset rationale without rejecting benchmark. Exactly two terminal registry rows are appended. Full exact before/after values, row identities and source hashes are embedded in the application receipt and adjudication manifest.

The initial deterministic offline export changes **two existing public paper records**, R181/R335, and **six existing dependent map records** (**one R181 / five R335**), only `research_types` and directly related `taxonomy_review.research_types.reason`. The other **672 public papers**, **1,404 map records** and all **1,410 relationship identities** are unchanged. No institution is added, removed or reassigned; no public paper is added or removed. Generated JSON is produced only by the exporter. Measured generated report differences: `docs/public_preview_report.md`; `docs/key_paper_coverage_report.md`.

## Recomputed counts and Batch B accounting

| Measure | Current value |
| --- | ---: |
| Public / formal / mapped / unmapped | 674 / 557 / 613 / 61 |
| Relationships / unique pairs | 1410 / 1410 |
| Detection / source attribution / localization | 621 / 84 / 45 |
| Method / dataset / benchmark / survey / analysis study | 578 / 137 / 91 / 21 / 82 |
| Original Batch B actions / papers | 159 / 148 |
| Historical unresolved actions / papers | 142 / 131 → 140 / 129 |
| Active-public unresolved actions / papers | 140 / 129 → 138 / 127 |

All values are recomputed from current authoritative inputs and original decision ledger. Exactly R181/R335 close; neither target has another independent pending original action. The 159-action / 148-paper denominators do not change. Batch C's **13 deferred debts**, separate **39-paper import inventory**, all prior B1A–K evidence/decisions, **128 protected primary files**, **49 frozen NeurIPS artifacts** and **119 ignored operational inputs** remain protected.

## Preserved evidence and actual validation boundary

Original retrieval accounting remains **R181 one new complete manuscript, R335 zero, total one**, with **zero additional downloads after interruption recovery** and **zero new scientific-source retrievals during adjudication**. No datasets, weights, supplements, source-code archives or other papers are retrieved or executed. Worker checks remain **51/51** and **28/28**, independent scientific checks **61/61** covering **760 numerical values**, preservation **37/37**, completion-boundary **15/15**, and packet-assembly **12/12** as distinct receipts. Original failed checker attempts and the non-scientific ViT checker-label typo remain in their original histories; corrected harness receipts never alter scientific tables or frozen reports.

Full original manifest/report bytes are authenticated by deterministic gzip/base64 archives and the entire original report follows verbatim. All original science, source versions, retrieval failures, timestamps, release limitations, rendered-page checks and scientific receipts remain intact. Only four original administrative flags per accepted record change; accepted classifications, decisions and application evidence are separate new fields. Historical `current_*`, provisional proposals and prior no-change statements remain explicitly historical. All original **17 source fingerprints** are preserved; a separate current set changes only papers, taxonomy, decisions and the two dependent public JSON files.

<!-- B1L_ADJUDICATION_VALIDATION_START -->
Focused validation: **451 tests and 12 subtests passed**, including **28 B1L regression cases**; zero failures, errors or skips. All four current-scope validators passed with zero errors; actual warning counts are preserved.

The complete repository suite ran **once**: **2104 tests and 389 subtests passed**, zero failures, errors or skips, **2 existing warnings**. Python 3.14.7, pytest 9.1.1, pytest-subtests 0.15.0 and Node 24.19.0; checksum-matched historical fixtures and authorized localhost. All **4605 compared paths** remained unchanged by the suite.

Two sequential offline export verification passes then passed. All **4605 paths**, seven deterministic outputs and 119 ignored operational inputs remained byte-identical across both passes. Both read-only fixture checks verified 117 inputs and created none. Exactly one initial correction export and two verification exports ran, with no concurrent exporter. `EXPORT_REPRODUCIBLE = 1`.

Integrity gate: **69/69 checks passed**. Exactly two public records and six existing dependent map records change only research types and directly related review reasons. All 672 other papers, 1,404 other map records and 1,410 relationship identities remain unchanged. Fourteen existing CSV cells across four rows and two files change; two terminal decisions append, registry 92 → 94. Dataset is 137; all other corpus and taxonomy totals remain unchanged. Historical unresolved actions: 140; active-public actions: 138 across 127 papers.

Original evidence-stage worker checks 51/51 and 28/28, scientific cross-checks 61/61 covering 760 numerical values, preservation 37/37 and completion-boundary 15/15 remain intact. All original findings, contradictions, failed retrievals, source hashes, timestamps and version limitations are preserved. No additional retrieval occurred.

`FOCUSED_FAILURES = 0`

`VALIDATOR_ERRORS = 0`

`FULL_SUITE_FAILURES = 0`

`EXPORT_REPRODUCIBLE = 1`

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

One full suite and two sequential verification exports ran on byte-identical scientific data, code, original evidence and pending-receipt packet bytes. Only manifest/report completion receipts are finalized afterward; they are not exporter inputs. The final read-only gate binds their final bytes and all other tested inputs. No additional suite or export run after its own receipt is claimed.

Validated for the explicit 12-file allowlist. Publication is pending until normal fast-forward push and independent remote-SHA verification.
<!-- B1L_ADJUDICATION_VALIDATION_END -->

Required final integrity: `UNEXPECTED_CHANGED = 0`, `FROZEN_NEURIPS_CHANGED = 0`, `PREEXISTING_LOCAL_FILES_CHANGED = 0`, `IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`. These remain requirements until measured final gates pass. The dirty primary checkout and concurrent frontend work remain protected.

Planned single commit: `fix: classify R181 and R335 dataset contributions`. Publication requires fresh remote fetch, normal safe fast-forward, independently verified exact remote SHA, `HEAD == origin/main`, ahead/behind **0/0**, clean isolated tree/index and untouched primary. No force push. The containing commit and external publication receipts supply actual Git identity without circular self-reference.

Exact explicit allowlist:

- `data/curated/paper_taxonomy.csv`
- `data/curated/papers.csv`
- `data/curated/review_decisions.csv`
- `data/raw/corpus_quality_batch_b_wave_b1l_2026_10_22/evidence_manifest.json`
- `docs/corpus_quality_batch_b_wave_b1l_2026_10_22.md`
- `docs/key_paper_coverage_report.md`
- `docs/public_preview_report.md`
- `tests/baseline_expectations.py`
- `tests/test_corpus_quality_batch_b_wave_b1k.py`
- `tests/test_corpus_quality_batch_b_wave_b1l.py`
- `web/data/public_preview_map_data.json`
- `web/data/public_preview_papers.json`

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Preserved complete evidence-only report

Everything below is the complete original evidence-stage report, preserved verbatim. Original provisional outcomes, then-current counts, no-change flags and untracked-file observations describe that historical phase. The accepted dispositions above supersede administrative status only; original scientific findings, contradictory evidence and source limitations remain part of the audit trail.

---

# Batch B Wave B1L — dataset-resource evidence only

Published baseline: `78f6ebae879f630eb6e386d92ab90252af09670d`. Isolated HEAD matches fetched `origin/main`, ahead/behind **0/0**. This wave covers exactly **R181** and **R335** under locked **R1**. Both original review actions remain pending and all authoritative classifications stay unchanged. Proposed dataset additions require separate maintainer acceptance and authorized remediation.

| Review | Current research types | Provisional outcome | Proposed complete research types |
| --- | --- | --- | --- |
| R181 | `method` | `DATASET_ADDITION_SUPPORTED` | `method;dataset` |
| R335 | `benchmark` | `DATASET_ADDITION_SUPPORTED` | `dataset;benchmark` |

## Recovery, policy and evidence budget

The interrupted session's existing baseline, source inventory, manuscript downloads, text, rendered pages, partial scientific findings and preservation work were recovered. The same worker tasks resumed unfinished consolidation; no worktree or duplicate reviewer was created. No successful manuscript download was repeated. **One newly retrieved complete manuscript in total: R181 = 1, R335 = 0.** R335 reuses one complete local arXiv v1, present as two identical copies; R181 reuses its successful pre-interruption single pinned v1 transfer. **No new full manuscript was retrieved after the resume.**

Locked R1, copied exactly from `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json`:

> Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.

Names, image counts and normal method-validation data alone are insufficient. A substantively constructed reusable resource can qualify despite incomplete public-release verification. Neither original photography nor all-new underlying image sources is required when systematic new curation is independently substantive. Dataset and benchmark can coexist; this wave neither adds a benchmark to R181 nor adds method to R335.

Root independently read the primary scientific sections and checked critical rendered counts/construction/result pages before reviewing the consolidated worker recommendations. Separate source/recovery, metadata-provenance and scientific cross-review findings are retained in full in the manifest. Exact per-worker checks remain distinct; none is represented as a repository test suite.

## Corpus and unresolved accounting remain unchanged

| Measure | Actual unchanged value |
| --- | ---: |
| Public / formal / mapped / unmapped | 674 / 557 / 613 / 61 |
| Relationships / unique pairs | 1,410 / 1,410 |
| Detection / source attribution / localization | 621 / 84 / 45 |
| Method / dataset / benchmark / survey / analysis study | 578 / 135 / 91 / 21 / 82 |
| Original Batch B actions / papers | 159 / 148 |
| Historical unresolved actions / affected papers | 142 / 131 |
| Active-public unresolved actions / affected papers | 140 / 129 |

These values and all pending IDs were recomputed from the authoritative registry and public records. Evidence proposals do not close reviews or decrement accounting. Batch C’s same 13 deferred cases, the separate 39-paper inventory, 22 prior B1A–K artifacts, 128 protected local files, 49 frozen NeurIPS artifacts, 119 ignored operational inputs, and primary checkout remain protected.

## Release metadata and bounded failures

The author-linked [QuAD project](https://grip-unina.github.io/QuAD/) and [repository README](https://github.com/grip-unina/QuAD/blob/main/README.md) were inspected only for resource documentation. Root made **10 bounded metadata/documentation GETs**: seven succeeded, while `LICENSE.txt` and both dataset READMEs each timed out once after 35 seconds with **HTTP status unavailable/0, zero body bytes and curl exit 28**. No timeout was retried. The web-rendered dataset link was denied by robots.txt; that failure is preserved separately from API results.

Directory responses establish names, sizes and Git blob/tree IDs for AncesTree development/test/calibrated CSVs, source metadata, ReWIND score/calibration CSVs, and AncesTree generator-script filenames. **None of these CSV, NumPy, image, script or archive bodies was downloaded.** The top README states calibration can use supplied CSVs without image downloads; this does not prove complete image availability, split contents or parent-child annotation coverage. Its informational/nonprofit software terms and GitHub `NOASSERTION` license metadata do not establish dataset-specific image rights; full license text was not retrieved. Metadata is bound to main as observed on 2026-10-22 and individual Git object identities, not certified as the submission-date release.

R181 provenance clarification: the preserved worker report’s phrase ‘stored CVPRW proceedings-final source’ refers to the canonical record’s stored proceedings URL. No complete CVPRW publisher-final manuscript was found or inspected; the reviewed source is the pinned arXiv v1, with no publisher byte-equivalence claim.

R335's primary manuscript links no specific Forged Calamity release endpoint. Dataset images, annotations, splits, copyright permissions and complete release remain unverified. Its manuscript license is not substituted for image-data rights. The publisher metadata date discrepancy is documented as an observation; canonical publication metadata is unchanged.

<!-- B1L_FINAL_VALIDATION_START -->
**Lightweight evidence validation passed.** R181's 51/51 and R335's 28/28 worker checks remain distinct. Independent source/recovery checks passed 23/23, and the incremental metadata supplement passed 8/8. The combined independent scientific cross-review passed 61/61, including all 406 R181 and 354 R335 reported numerical result values. Its earlier R335 30-check subset is reused within those 61 and is not double-counted. Final prepared-packet assembly checks passed 12/12, preserving both complete worker records and reports verbatim.

Initial operational checker path/whitespace-selector failures and their narrow repairs remain in the manifest; scientific findings and frozen source/worker bytes did not change. One prior check label contained `9993`, while the actual assertion, source and table value are 99.43; the label-only annotation is preserved without rewriting the frozen receipt.

**The exact evidence/worktree preservation gate passed 37/37 checks**: all 4,483 isolated tracked files, 4,414 primary tracked files and 305 primary untracked files retained their bytes, modes and inventories. The 128 protected files, both sets of 49 frozen NeurIPS artifacts, 119 ignored inputs, 22 prior B1A–K artifacts, historical fixtures/decisions, Batch C's 13 debts and separate 39-paper inventory remain unchanged. Corpus and Batch B counts were independently recomputed and remain as reported above. Both original review actions remain unresolved; no terminal decision was added.

`AUTHORITATIVE_CORPUS_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

Only this report and its evidence manifest exist as new untracked, unstaged artifacts. The index is empty, tracked tree clean, and isolated HEAD equals fetched origin/main at the published B1K baseline with ahead/behind 0/0. No full repository suite, public exporter, commit, push or additional wave was run. No manuscript/data binaries or operational scripts are staged or added to Git in B1L. The newly retrieved manuscript and working artifacts remain in TMP; pre-existing cached sources are unchanged. Only completion-receipt fields are finalized after the measured gate; final read-only checks bind the resulting artifact bytes and confirm all scientific evidence remains exact.
<!-- B1L_FINAL_VALIDATION_END -->

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Complete R181 scientific evidence

# R181 — Quality-Aware Calibration for AI-Generated Image Detection in the Wild

Evidence-only finding: **DATASET_ADDITION_SUPPORTED**. Proposed complete research types: **method;dataset**. The review remains unresolved pending maintainer acceptance. No benchmark, task, scope or publication change is proposed.

## Identity and primary source

Canonical ID: `curated:bb388762c1cb4bd3bf4a`. Authors: Fabrizio Guillaro, Vincenzo De Rosa, Davide Cozzolino and Luisa Verdoliva. The complete [arXiv v1 author manuscript](https://arxiv.org/pdf/2604.15027v1) has 10 pages and is dated 16 April 2026. It is not verified byte-equivalent to the stored CVPRW proceedings-final source. Canonical bibliography is preserved.

PDF: 1,215,364 bytes; SHA256 `50f03fe6fc43c628b763a56d76582706a210e15806a1ac94e2c925ca6cef5415`. Extracted-text SHA256 `ebf83d7610c6ecfa1b4955e63a59158d03e5d606703a9293e93d5c6beb8e5117`. All 10 pages, including references, were read. Pages 3, 4, 7 and 8 were rendered and visually checked.

## Original question and locked policy

Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: AncesTree and ReWIND are introduced as reusable degradation-tree and web-reposting datasets.

Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.

## Fifteen bounded questions

### 1. What do AncesTree and ReWIND represent?

AncesTree is a controlled collection of related degraded versions organized as stochastic trees. ReWIND is a curated real-web collection of near-duplicates of viral real and AI-generated images. They address version-dependent authenticity decisions; neither is merely a list of the QuAD detector outputs.

Locator: Section 3, pp.3–4; Figure 5 p.4; Tables 1–3.

### 2. Are the two resources new rather than renamed existing datasets or ordinary perturbation variants?

ReWIND reuses known source images but expands their online near-duplicate retrieval and adds fact-checked sources; it is a new assembled collection, not wholly new source content. AncesTree deliberately uses simulated perturbations, but contributes a systematic multilevel branching degradation structure whose distributions are motivated by ReWIND. Originality is in curation, grouping and controlled histories, not an unsupported assertion that every root image or generator output was newly created.

Locator: Contribution list p.2; Section 3 pp.3–4; Table 1; Figure 5.

### 3. How many source images exist and what is their provenance?

AncesTree starts from 100 real RAISE images and 1,000 semantically aligned synthetic counterparts across ten named generator families, then generates 124 non-root variants per source: 1,100×124=136,400. The source paragraph explicitly credits previously provided synthetic material to Synthbuster [1] and B-Free [12]. ReWIND contains 162 source groups, 87 real and 75 fake, comprising 9,646 retrieved instances, 4,367 real and 5,279 fake. Its Table 1 provenance is retained row by row below.

Locator: Section 3 pp.3–4; Table 1 p.3; references [1],[8],[10],[12],[16],[18].

### 4. What operations, order and severity produce AncesTree?

Each edge is a random crop→resize→lossy-compression pipeline. Crop probability is 50%, retaining 60–99.9% of image area, one dimension at a time; repeated edges can crop both dimensions. Resize probability is 60%, setting the shorter side in [256,2048] pixels, with Pillow/OpenCV and bilinear/bicubic/Lanczos interpolation chosen randomly. Compression probability is 95%, JPEG or WebP with format/QF distributions matched to the real-web collection; Figure 5 gives QF 50–100. JPEG encoders vary between Pillow and OpenCV. These are stochastic distributions, not five fixed scalar severity labels. Blur/noise/brightness/gamma in Figure 3 are illustrative IQA analyses, not additional stated AncesTree pipeline operations.

Locator: Section 3 p.4; Figure 5 p.4; Figure 3 p.2 and Figure 4 p.3.

### 5. Is ancestry or an ordered version sequence explicitly represented?

Yes for the in-lab construction: depth L=5, four first-level branches, then binary branching, yielding 4+8+16+32+64=124 descendants. The clean root is discarded from the reported dataset. Each branch/node has a known generated lineage and level in the construction; the L 1 oracle and level-conditioned detector plots use this structure. This does not establish that downloadable metadata includes a complete independently verified parent-edge annotation schema. ReWIND has source-group association but its actual web history/ancestors are explicitly unknown.

Locator: Figure 5 p.4; Section 3 p.4; Figure 6 p.5; oracle protocol p.6/Table 2 p.7; ReWIND limitations p.8.

### 6. How are web repostings and near-duplicates collected?

The authors repeat online searches for viral B-Free/FOSID seeds and add AMMeBa fact-checking images, RRDataset real news images and Google Fact Check Tools sources confirmed as AI-generated. Google Cloud Vision is used to find additional near-duplicates. They remove images whose shorter side is below 256 px and exact duplicates with equal MD 5, and retain source groups with at least 10 near-duplicates. Exact retrieval dates, query/result logs, completeness, human matching-error rates, per-file rights and exhaustive cross-source overlap controls are not specified in the manuscript.

Locator: Section 3 pp.3–4; Table 1; footnotes 1–2 p.4; future retrieval-error analysis p.8.

### 7. How do real and simulated degradations differ?

ReWIND consists of retrieved web files with unknown, potentially long and incomplete dissemination histories; earlier copies can disappear and timestamps can mislead. AncesTree is a simulated five-level process motivated by observed crop, format and JPEG-QF distributions. It allows controlled depth/oracle analyses, but cannot certify authentic upload order or reproduce every platform operation. The wild collection does not have known degradation-tree ground truth.

Locator: Figures 2–5 pp.2–4; Section 3; Section 5/ReWIND p.8.

### 8. Are the resources substantively separate from QuAD training?

The manuscript explicitly lists both resources as contributions and defines them in a separate data-construction section before the calibration method. It evaluates six public pretrained detectors, simple aggregation and quality/date/size selection as well as QuAD, so the resources can support analyses without training QuAD or accepting its Gaussian model. Around half of AncesTree is nevertheless used to fit QuAD calibration; the resource is not claimed to be wholly independent of the authors' experimental design. Scientific separability means reusable grouped data and controlled histories, not an external provenance or independent-team validation claim.

Locator: Contribution list p.2; Section 3 pp.3–4; development fitting p.6; Sections 5/Tables 2–3 pp.6–8.

### 9. What are the split and leakage safeguards?

Eight linear Gaussian calibration coefficients are maximum-likelihood fitted on around 50% of AncesTree, with remaining data for evaluation. The manuscript does not specify exact indices, random seed, source-group/semantic-family grouping, validation partition or whether near-duplicates of one source can cross development/test. It is unsafe to assume a leakage-free root-level split. On ReWIND, plain QuAD transfers AncesTree-fitted coefficients; QuAD* refits via leave-one-out on ReWIND. The leave-one-out unit and exact exclusion of related near-duplicates are not specified. MD 5 filtering is exact-file deduplication, not proof of cross-split content independence.

Locator: Gaussian fitting p.6; Table 3 caption p.8; Section 3 deduplication p.4.

### 10. Is resource construction claimed as a substantive contribution?

Yes. The p.2 contribution list separately identifies collection of the real-world ReWIND dataset and construction of the in-lab AncesTree dataset, alongside QuAD and detector evaluation. Section 3 provides quantitative curation/generation rules, source groups and known-versus-unknown histories. This is stronger R1 evidence than size or the abstract's public-availability assertion alone.

Locator: Contribution list p.2; Section 3 pp.3–4; Table1/Figure5.

### 11. Can methods other than QuAD use the resources?

Yes in the scientific design: six independent base detectors (DMID, CoDE, D 3, B-Free, DRCT, CO-SPY) are evaluated under random, naive aggregation, QF, size, IQA and, for the wild set, date selection. Figures 6/8 analyze version depth, quality ranking and missing instances. These are method-independent uses of grouped image data. No independently reproduced external research-team reuse was verified.

Locator: Section5 pp.6–8; Tables2–3; Figures6–8 pp.5–6.

### 12. What release contents and licenses are independently established?

The complete top README and successful API listings confirm public repository documentation and named CSV/code entries, not complete image or split contents. The README says calibration uses provided CSVs without dataset downloads. API lists AncesTree development/test/calibrated CSVs and source metadata, plus ReWIND score/calibration CSVs and AncesTree generation-script filenames. No CSV, image payload, script, NumPy array or archive body was downloaded. The two dataset README and full LICENSE.txt requests each timed out after 35 seconds with zero bytes and no retry. GitHub reports NOASSERTION, and the top README describes informational/nonprofit software use with all rights reserved. Full dataset/image rights, official split grouping, parent-edge schema and release completeness therefore remain unverified.

Locator: Abstract p.1; root-owned top README and seven successful GitHub API/raw-text observations with preserved byte receipts; three failed text receipts in release_review.

### 13. Which experiments isolate degradation history or diversity benefits?

Figure 6 stratifies detector distributions by known tree depth, showing increasing overlap. Figure 8 left compares QF/size/IQA ranking and number of selected instances; right varies available instance count, comparing all-logit mean, best 10 LoDa and QuAD. Tables 2–3 compare controlled versus genuinely retrieved web data and AncesTree-to-ReWIND calibration transfer versus ReWIND leave-one-out refitting. These show consequences of quality/history/availability, not a clean randomized dataset-diversity ablation or independent proof that extra sources alone cause the gains. Exact curve points beyond printed table/text values were not digitized.

Locator: Figures6–8 pp.5–6; Section5 pp.7–8; Tables2–3.

### 14. What are baselines, metrics and quantitative findings?

Metrics are balanced accuracy (percent) and negative log likelihood. All table cells are transcribed below. On AncesTree, mean naive aggregation is 73.2/0.75 versus QuAD 81.6/0.43 (+8.4 percentage points in bAcc). On ReWIND, naive is 63.0/1.27 versus transferred QuAD 70.3/0.63 (+7.3 points); earliest-date single selection 67.3/1.29 and QuAD*71.4/0.57 are distinct comparisons. Improvements are not universal: AncesTree B-Free QuAD 97.1 is below oracle 97.3 and LoDa 20 98.4; ReWIND CO-SPY QuAD 62.3/0.83 is worse than naive 65.7/0.81. QuAD* is not a held-out cross-dataset result.

Locator: Tables2–3 pp.7–8; method configurations pp.6–7; Figure8 p.6.

### 15. What limitations constrain resource and release conclusions?

AncesTree is simulated with only 100 real semantic roots and 1,000 generator counterparts; variants are correlated and not 136,400 independent scenes. ReWIND contains only 162 source groups, unknown generator/version histories and incomplete retrieval, fact-checking provenance dependencies, selection bias from the 10-copy/256 px filters and unknown rights/completeness. Gaussian conditional independence is an explicit approximation for correlated versions. Split grouping and ReWIND leave-one-out unit remain unverified. This is arXiv v1, not byte-verified CVPRW final; a scientific R1 contribution may be supported despite unverified public release and numerical reproduction.

Locator: Sections3–5 pp.3–8; independence approximation p.5; future work p.8; source/release limits below.

## Exact resource accounting

AncesTree starts from 100 real RAISE images and 1,000 semantically aligned synthetic counterparts. Each root has 124 retained descendants: 1,100 × 124 = 136,400 files. The clean root is excluded. Four first-level branches followed by binary branching yield 4 + 8 + 16 + 32 + 64 = 124 nodes over five levels. The ten generator families are SD1.4, SD2, SD-XL, Midjourney v5, DALL-E 2, DALL-E 3, Firefly, Flux, SD3 and Latent Diffusion. Previously provided base imagery is explicitly acknowledged; these are correlated descendants, not 136,400 independent scenes.

Each edge applies cropping, resizing and compression in that order, with probabilities 50%, 60% and 95%. Crops retain 60–99.9% of area, one axis at a time; resizing places the shorter side between 256 and 2,048 pixels. JPEG/WebP distributions reflect ReWIND; Figure 5 gives QF 50–100. Pillow/OpenCV encoders and bilinear/bicubic/Lanczos interpolation vary. Blur, noise and brightness/gamma shown in Figure 3 are IQA illustrations rather than extra declared generation operations.

| ReWIND source | Real sources | Fake sources | Real instances | Fake instances |
|---|---:|---:|---:|---:|
| B-Free | 20 | 15 | 1261 | 1851 |
| FOSID | 0 | 3 | 0 | 517 |
| AMMeBa | 44 | 39 | 1929 | 2135 |
| Fact-Check Tool | 0 | 18 | 0 | 776 |
| RRDataset | 23 | 0 | 1177 | 0 |
| Total | 87 | 75 | 4,367 | 5,279 |

ReWIND therefore has 162 source groups and 9,646 retrieved instances. Source-table dashes mean zero applicable images. Groups need at least 10 copies; files below a 256-pixel shorter side and exact MD5 duplicates are removed. True web ancestry remains unknown. Table 1, p.3; construction pp.3–4.

## Protocol and leakage boundary

Around 50% of AncesTree fits eight class-specific Gaussian calibration coefficients; the remaining data evaluate them. The manuscript does not identify exact source-group or semantic-family separation, fixed IDs, random seed or validation split. Do not presume a leakage-free root-level split. Plain QuAD transfers these coefficients to ReWIND; QuAD* instead uses ReWIND leave-one-out fitting, whose omitted unit is unspecified. MD5 filtering only removes byte-identical files. No root-level split or leave-one-out exclusion was verified from CSV filenames.

Six existing pretrained detectors are evaluated: DMID, CoDE, D3, B-Free, DRCT and CO-SPY. Their selection/averaging, quality ranking and level analyses support method-independent use of the resources. None was downloaded or run by this review. Conditional independence of related copies is an explicit simplifying assumption rather than an empirically established property.

## Full quantitative evidence

Each cell is balanced accuracy (%) / negative log likelihood (NLL), exactly as printed. These are reported results, not independently reproduced measurements.

### Table 2 — AncesTree, p.7

| Strategy | Instances | DMID | CoDE | D3 | B-Free | DRCT | CO-SPY | AVG |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| oracle | L1 | 75.5 / 1.24 | 73.9 / 0.85 | 79.7 / 0.59 | 97.3 / 0.09 | 68.6 / 0.59 | 77.6 / 0.60 | 78.8 / 0.66 |
| random | 1 | 63.3 / 1.68 | 65.9 / 1.01 | 74.5 / 0.92 | 88.4 / 0.32 | 57.9 / 1.10 | 74.4 / 0.77 | 70.7 / 0.97 |
| naive | all | 62.1 / 1.17 | 71.8 / 0.72 | 77.4 / 0.77 | 94.3 / 0.16 | 57.9 / 0.98 | 75.9 / 0.70 | 73.2 / 0.75 |
| QF | 1 | 61.6 / 1.16 | 65.7 / 0.87 | 75.2 / 0.82 | 85.9 / 0.33 | 50.5 / 1.21 | 75.8 / 0.70 | 69.1 / 0.85 |
| QF | 10 | 65.0 / 1.39 | 70.7 / 0.76 | 77.6 / 0.70 | 93.5 / 0.16 | 52.9 / 1.04 | 76.0 / 0.66 | 72.6 / 0.78 |
| QF | 20 | 62.5 / 1.40 | 69.9 / 0.78 | 79.7 / 0.69 | 94.3 / 0.15 | 51.9 / 1.07 | 76.3 / 0.68 | 72.4 / 0.79 |
| Size | 1 | 58.1 / 1.12 | 57.2 / 1.02 | 72.2 / 0.94 | 84.2 / 0.40 | 55.9 / 1.41 | 72.5 / 0.78 | 66.7 / 0.95 |
| Size | 10 | 60.7 / 0.81 | 58.7 / 0.87 | 77.0 / 0.72 | 93.0 / 0.27 | 53.0 / 1.26 | 75.5 / 0.65 | 69.6 / 0.76 |
| Size | 20 | 60.8 / 0.76 | 61.1 / 0.83 | 79.8 / 0.70 | 95.7 / 0.23 | 53.0 / 1.24 | 75.9 / 0.65 | 71.1 / 0.73 |
| LoDa | 1 | 74.3 / 1.48 | 69.2 / 1.06 | 79.3 / 0.69 | 96.1 / 0.10 | 67.9 / 0.85 | 77.2 / 0.63 | 77.3 / 0.80 |
| LoDa | 10 | 73.3 / 1.09 | 75.5 / 0.74 | 79.9 / 0.64 | 98.0 / 0.08 | 62.2 / 0.83 | 76.8 / 0.62 | 77.6 / 0.66 |
| LoDa | 20 | 72.0 / 1.04 | 76.2 / 0.70 | 79.4 / 0.67 | 98.4 / 0.08 | 60.7 / 0.85 | 77.4 / 0.62 | 77.4 / 0.66 |
| QuAD | all | 79.6 / 0.61 | 79.6 / 0.51 | 81.2 / 0.41 | 97.1 / 0.14 | 70.2 / 0.57 | 82.0 / 0.34 | 81.6 / 0.43 |

### Table 3 — ReWIND, p.8

| Strategy | Instances | DMID | CoDE | D3 | B-Free | DRCT | CO-SPY | AVG |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| random | 1 | 55.9 / 2.77 | 57.2 / 1.72 | 66.4 / 1.39 | 78.4 / 0.63 | 57.8 / 1.18 | 64.4 / 0.92 | 63.4 / 1.44 |
| naive | all | 50.0 / 2.58 | 60.8 / 1.43 | 67.4 / 1.24 | 80.1 / 0.48 | 53.8 / 1.06 | 65.7 / 0.81 | 63.0 / 1.27 |
| Date | 1 | 62.9 / 2.16 | 56.2 / 1.62 | 69.1 / 1.27 | 79.6 / 0.53 | 70.9 / 1.23 | 65.3 / 0.95 | 67.3 / 1.29 |
| Date | 10 | 51.3 / 2.09 | 60.4 / 1.39 | 68.9 / 1.27 | 79.4 / 0.47 | 73.0 / 0.99 | 70.6 / 0.82 | 67.3 / 1.17 |
| Date | 20 | 50.7 / 2.22 | 60.9 / 1.38 | 67.6 / 1.26 | 79.4 / 0.46 | 73.0 / 1.01 | 68.7 / 0.84 | 66.7 / 1.20 |
| QF | 1 | 52.9 / 5.29 | 60.3 / 1.55 | 71.2 / 1.23 | 81.2 / 0.48 | 55.2 / 2.00 | 61.6 / 0.89 | 63.7 / 1.91 |
| QF | 10 | 50.0 / 4.26 | 58.8 / 1.46 | 67.4 / 1.21 | 81.4 / 0.46 | 52.7 / 1.36 | 68.4 / 0.80 | 63.1 / 1.59 |
| QF | 20 | 50.0 / 3.71 | 60.8 / 1.46 | 68.7 / 1.21 | 80.1 / 0.48 | 53.4 / 1.22 | 65.7 / 0.79 | 63.1 / 1.48 |
| Size | 1 | 62.9 / 2.16 | 56.2 / 1.62 | 69.1 / 1.27 | 79.6 / 0.53 | 59.8 / 1.13 | 65.3 / 0.95 | 65.5 / 1.28 |
| Size | 10 | 51.3 / 2.09 | 60.4 / 1.39 | 68.9 / 1.27 | 79.4 / 0.47 | 52.3 / 1.07 | 70.6 / 0.82 | 63.8 / 1.19 |
| Size | 20 | 50.7 / 2.22 | 60.9 / 1.38 | 67.6 / 1.26 | 79.4 / 0.46 | 53.1 / 1.08 | 68.7 / 0.84 | 63.4 / 1.21 |
| LoDa | 1 | 64.1 / 1.62 | 59.0 / 1.71 | 70.4 / 1.30 | 84.9 / 0.41 | 57.2 / 1.17 | 60.7 / 1.07 | 66.1 / 1.21 |
| LoDa | 10 | 56.7 / 2.01 | 64.9 / 1.26 | 69.7 / 1.20 | 85.4 / 0.39 | 56.6 / 0.98 | 62.7 / 0.95 | 66.0 / 1.13 |
| LoDa | 20 | 53.3 / 2.29 | 62.2 / 1.29 | 68.7 / 1.22 | 84.8 / 0.42 | 55.6 / 0.99 | 65.0 / 0.91 | 64.9 / 1.19 |
| QuAD | all | 66.7 / 0.64 | 64.0 / 0.63 | 72.0 / 0.77 | 86.1 / 0.35 | 70.5 / 0.58 | 62.3 / 0.83 | 70.3 / 0.63 |
| QuAD* | all | 61.0 / 0.64 | 70.0 / 0.59 | 71.5 / 0.61 | 89.6 / 0.32 | 70.9 / 0.60 | 65.4 / 0.62 | 71.4 / 0.57 |

AncesTree mean bAcc rises from 73.2 to 81.6 (+8.4 percentage points), with NLL 0.75 → 0.43. ReWIND transferred QuAD rises from naive 63.0 to 70.3 (+7.3 points), with NLL 1.27 → 0.63. Earliest-date single selection gives 67.3 / 1.29; QuAD* gives 71.4 / 0.57 under a distinct leave-one-out fitting protocol. The text reports alternative-IQA AncesTree means of 81.5% for TReS and 81.4% for QCN.

Counterexamples remain explicit: AncesTree B-Free QuAD 97.1 / 0.14 is below oracle 97.3 / 0.09 and LoDa-20 98.4 / 0.08. ReWIND CO-SPY transferred QuAD 62.3 / 0.83 is worse than naive 65.7 / 0.81; QuAD* bAcc 65.4 is still below naive. DRCT date-10/20 bAcc 73.0 exceeds QuAD 70.5 and QuAD* 70.9. CoDE LoDa-10 bAcc 64.9 exceeds transferred QuAD 64.0, although its NLL is worse. The result is not uniform superiority.

Figure 6 stratifies detector scores by tree depth; Figure 8 varies quality-based selection and available instance count. Tables 2–3 compare controlled and wild data and cross-resource versus within-resource calibration. These are not a clean causal dataset-diversity-only ablation. Curves were not digitized and experiments were not rerun.

## R1 contribution assessment

The complete manuscript establishes systematic construction and curation of two named reusable grouped-image resources as separate substantive contributions. Known tree histories and genuinely retrieved web groups support analyses and six base-detector evaluations beyond QuAD itself. This crosses R1 contribution threshold despite reused roots, correlated variants and unverified release completeness; the judgment does not rest on size, a name, public-download availability or an automatic method-plus-data rule.

The resources are tightly motivated by the calibration experiments and include simulation/reuse, so treating every augmentation set as a dataset would be too broad. Explicit contribution status, systematic structure, real-world curation and method-independent usage together distinguish this case.

Confidence in substantive resource construction and R1 addition is high, with explicit reuse, simulation, split and release limitations. Maintainer acceptance remains pending. Method remains supported; no benchmark adjudication is authorized.

## Release observations and limitations

The author-linked [project](https://grip-unina.github.io/QuAD/) and top [repository README](https://github.com/grip-unina/QuAD/blob/main/README.md) describe both resources. The README says calibration uses provided CSVs without image downloads. Its retrieved SHA256 is `c760178ee37a7600d4daca3e5a687c8415d4db95d500bd6de092a95959302c2b`; Git blob ID is `227ec487657365965bc62b9faeeaa483236f1202`. Metadata was observed on mutable `main` on 22 October 2026; no full repository commit or correspondence of every resource to arXiv v1 was verified.

Successful GitHub API listings expose AncesTree development/test/calibrated CSV entries (44,915,237 / 44,844,502 / 44,913,695 bytes) and sources.csv (241,384 bytes). ReWIND entries are ReWIND.csv (3,437,683), calibrated_AT (3,450,878) and calibrated_LOO (3,455,749). The AncesTree code listing names run_ancestree.py, ancestree_utils.py and ReWIND_QFs.npy. No CSV, script or NumPy body was fetched. Filenames, byte counts and Git blob/tree IDs do not verify contents, split grouping, parent-edge annotations, generated-image access or completeness.

The top README describes informational/nonprofit software use with all rights reserved. GitHub classifies the license as NOASSERTION. Full LICENSE.txt and the two dataset README requests each timed out after 35 seconds with HTTP 0 and zero bytes, without retry. The full legal terms and dataset/image rights are unverified; software wording cannot establish third-party image rights. A GitHub web dataset link also had a robots denial, while API listings succeeded. The manuscript claim of public availability is not a certified complete release.

## Retrieval and preservation

One new complete manuscript was retrieved: one pinned-v1 GET, HTTP 200, curl exit 0, no redirect, retry or alternate version. Started 2026-10-22T11:12:11.444467+00:00; completed 2026-10-22T11:12:12.241316+00:00. Root separately obtained seven successful bounded text/API metadata responses and three zero-byte timeouts, all retained with transport/header/body receipts. These are not additional complete manuscripts.

The preceding local search examined 80 distinct PDF bodies from 1,113 distinct retained PDF/gzip captures over all worktrees, primary data and TMP, finding no complete R181 copy. Seven disclosed errors concern unrelated lock files or earlier partial papers. No image/data payload, supplement, model weight or repository archive was downloaded; no source code was executed.

This worker wrote TMP evidence only. Authoritative data, review decisions, public outputs and primary checkout were not modified. No review closes, no new action is created, and no full suite, exporter, commit or push was run. Root independently reconciles current corpus/accounting and protected-file integrity.


## Complete R335 scientific evidence

# R335 — Forged Calamity dataset contribution evidence

Provisional outcome: **`DATASET_ADDITION_SUPPORTED`**. Proposed complete research types: **`dataset;benchmark`**. Retain **`detection`** and **`fully_generated`**. No method label, task/scope/publication correction, review closure or authoritative edit is applied. Maintainer acceptance remains pending.

Canonical identity: `curated:5ad6cb3411820ff01a03`, **Forged Calamity: Benchmark for Cross-Domain Synthetic Disaster Detection in the Age of Diffusion**, publisher DOI `10.1007/978-981-92-2600-9_17`. The original Batch B R335 question asks whether its image corpus is substantively reusable beyond the existing benchmark evaluation role. Its authoritative types remain **`benchmark`** and the original review remains open at baseline `78f6ebae879f630eb6e386d92ab90252af09670d`.

## Recovered primary manuscript and publication-version boundary

The already preserved complete [arXiv 2606.18554v1 manuscript](https://arxiv.org/abs/2606.18554v1) is **15 pages / 6,249,493 bytes**, SHA256 `ac3a0f8e7a8b0751991420898bb31e4b3dadf8f629360cddde4547b2d4d27dc1`. Its PDF metadata and first page identify v1, submitted **17 June 2026 at 00:08:35 UTC**. Both primary and isolated copies have identical bytes; a TMP copy is used for reading/rendering. All 15 pages and four tables were read; construction and tables were visually checked on pages 5, 6, 7, 9 and 11. **Zero new complete manuscripts were retrieved.**

All twelve authors match the canonical and DOI-matched publisher identities: Duc-Manh Phan, Quoc-Duy Tran, Duy-Khang Do, Anh-Tuan Vo, Hai-Dang Nguyen, Trong Le Do, Mai-Khiem Tran, Vinh-Tiep Nguyen, Tam V. Nguyen, Isao Echizen, Minh-Triet Tran, Trung-Nghia Le. The retained publisher [chapter record](https://link.springer.com/chapter/10.1007/978-981-92-2600-9_17), DOI registration cache and live official book metadata distinguish the **SOICT 2025 conference edition**, a **12 August 2026 chapter first-online date**, and **2027 publisher citation/copyright year**, pages **217–232**. The [official proceedings record](https://link.springer.com/book/10.1007/978-981-92-2600-9) dates the conference to **12–14 December 2025 in Nha Trang**. These are separate date concepts; canonical year **2025 remains unchanged** and is not asserted to be the first-online publication year.

The retained Springer HTML contains scientific prose and four table captions but **no numerical table bodies**. It corroborates the dataset/protocol narrative. All numerical tables below are bound to the **arXiv v1 PDF**, not claimed independently matched to the final 16-page Springer chapter. Publisher PDF equivalence, later amendments and final-edition numeric differences remain unverified. No publisher PDF, supplement or alternate complete manuscript was requested.

Metadata-only history is retained in the JSON: one live Springer chapter open failed **“Cache miss”** with no exposed HTTP code/bytes/time; one arXiv abstract open succeeded; one bounded exact-DOI official-domain search returned the book and page variants. A cache miss is not invented as HTTP 403. Existing cache acquisition timestamps and original transfer receipts are unverified, even though present local hashes are verified.

## What resource was constructed

The manuscript explicitly lists the dataset as its **first contribution on p.3** and devotes **Sections 3.1–3.3, pp.4–6** to resource construction. It curates real disaster images from **Incident-1M and the Internet** (the introduction abbreviates this to Incident-1M alone). Four classes are used: **Fire, Earthquake, Flood and Thunderstorm**.

For each class, **1,500 real images** are selected. **Figure 2 / Section 3.2, p.5** show real images feeding a vision-language description stage using **Moondream**, followed by **Llama 3** prompt refinement and then text-to-image synthesis. Each refined prompt is used with **Stable Diffusion 1.5, Stable Diffusion 2.0, SDXL and PixArt**. PixArt reference 3 is PixArt-Sigma, but the actual checkpoint is not pinned. Moondream reference 31 names revision **92d3d73**; exact Llama weights, prompts, generator IDs/hashes, seeds, steps, guidance and generation resolutions are not supplied.

Each generator contributes **1,500 synthetic images per disaster class**. The authors cite a similarity-filtering method to remove highly similar generated images. Exact filtering thresholds, candidate/rejection counts and any replacement procedure are absent. Figure 2 supports semantic real-image-derived text conditioning; it does not establish a direct image-to-image pipeline or a fully released one-to-one real/prompt/output lineage.

### Verified Table 1 arithmetic — p.6

| Category | Real | SD 1.5 | SD 2.0 | SDXL | PixArt | Derived category total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fire | 1,500 | 1,500 | 1,500 | 1,500 | 1,500 | 7,500 |
| Earthquake | 1,500 | 1,500 | 1,500 | 1,500 | 1,500 | 7,500 |
| Flood | 1,500 | 1,500 | 1,500 | 1,500 | 1,500 | 7,500 |
| Thunderstorm | 1,500 | 1,500 | 1,500 | 1,500 | 1,500 | 7,500 |
| Total | 6,000 | 6,000 | 6,000 | 6,000 | 6,000 | 30,000 |

Thus **6,000 real + 24,000 synthetic = 30,000**, with **6,000 synthetics per generator** and **7,500 total images per class**. These are reconciled published counts, not a downloaded asset inventory. Although the prose calls the corpus balanced, its global binary real:fake ratio is **1:4**. It is balanced across disaster classes and generator/category cells; the specified single-generator training pair is 1:1.

## All fifteen requested dataset questions

**1. Original disaster categories.** Fire, Earthquake, Flood and Thunderstorm are explicitly named and each contains 1,500 real images plus 1,500 images from each of four generators. Source: Sections 3.1-3.3 pp.4-6; Table 1 p.6. Limit: Supported for the four classes. Category annotation guidelines and ambiguous/multi-disaster handling are not specified.

**2. Geographic, temporal and disaster-type coverage.** The corpus spans four disaster types. Geographic distribution, event IDs, capture dates, temporal windows and per-region representation are not reported. The general disaster-response motivation and diverse image examples do not establish global or historical coverage. Source: Sections 3.1-3.3 pp.4-6; Figures 1-3. Limit: Four-type coverage is supported; geographical and temporal coverage remain unknown.

**3. Real-image source and copyright provenance.** Section 3.1 names Incident-1M and the Internet, whereas the introduction describes the real images only as an Incident-1M subset. A targeted high-quality selection yields 1,500 images per category. The manuscript supplies no per-image source URLs, split between Internet/Incident-1M sources, capture/event provenance, rights audit or redistribution license for the image corpus. Source: Introduction p.2; Section 3.1 p.4; reference 34 p.15. Limit: Reused-source curation is established; exact source allocation and image rights are not verified. No source dataset or image asset was retrieved.

**4. Synthetic generator identities and versions.** The paper names Stable Diffusion 1.5, Stable Diffusion 2.0, Stable Diffusion XL and PixArt. Reference 3 identifies PixArt-Sigma, but the experimental checkpoint is not explicitly pinned; reference 26 is a general latent-diffusion paper. Exact model IDs, weight hashes, sampler, guidance, steps, seeds and generation resolutions are not supplied. Source: Section 3.2 p.5; Table 1 p.6; references 3/23/26 pp.13-15. Limit: Named generator families and SD versions are supported; fully reproducible checkpoint/parameter identities are not.

**5. Prompt generation methodology.** The pipeline uses Moondream to describe disaster imagery and Llama 3 to refine concise semantically coherent generation prompts. Figure 2 explicitly begins with real images, a vision-language description stage and an LLM refinement/augmentation stage before text-to-image synthesis. Reference 31 identifies moondream2 revision 92d3d73; Llama 3 is cited via its model card. Prompt templates, final prompt files, sampling rules and precise Llama checkpoint are absent. Source: Section 3.2 and Figure 2 p.5; references 1 and 31 pp.13/15. Limit: Two-stage image-conditioned caption/prompt construction is supported; exact prompt-level reproducibility is not.

**6. Relationship between real references and generated images.** Real images feed the description/prompt pipeline, and each refined prompt is used across the four text-to-image generators. This is semantic reference conditioning through text, not a documented direct image-to-image copying protocol. The manuscript does not release a real-image-to-prompt-to-output mapping or prove a one-to-one pairing after similarity filtering. Source: Figure 2 and Section 3.2 p.5. Limit: Reference-guided semantic construction is supported; exact paired correspondence, prompt counts and lineage records are unknown.

**7. Category and generator distribution and image-count reconciliation.** Table 1 gives 1,500 real images and four sets of 1,500 synthetic images in each of four categories: 4 times 1,500 = 6,000 real; 4 generators times 4 categories times 1,500 = 24,000 synthetic; total 30,000. Each generator contributes 6,000 images and each disaster category 7,500 total. The complete corpus has a real:fake ratio of 1:4, despite the text calling it balanced; it is balanced by category and within each generator/category cell, and the single-generator training comparison is 1:1. Source: Section 3.3 p.5; Table 1 p.6; conclusion p.12. Limit: Counts reconcile exactly as published claims. No image archive inventory was independently counted, and post-filter candidate/rejection/replenishment counts are unspecified.

**8. Training, validation and test splits.** Section 4.1 specifies 1,500 real plus 1,500 SD 1.5 synthetic earthquake images for fine-tuning. Eighteen remaining subsets are reported: three other real categories and fifteen synthetic category/generator combinations. No explicit validation partition, held-out in-distribution earthquake split, sample-ID lists, threshold-tuning set, repeated-run seed schedule or event/prompt-disjoint split specification is supplied. Zero-shot models use external pretrained weights and are evaluated on twenty subsets without dataset-specific fine-tuning. Source: Section 4.1 pp.6-7; Sections 4.3-4.4 pp.9-10; Tables 2-4. Limit: Stated train-domain membership and OOD subset structure are supported. Do not infer that all 27,000 remaining corpus images were evaluated or that a hidden validation partition is known.

**9. Cross-domain detection protocols.** The prediction is binary real/fake, with synthetic samples called the negative class. Semantic OOD tests other disaster categories while keeping SD 1.5; generative OOD tests SD 2.0, SDXL and PixArt across four categories. These form transferable content/generator partition definitions. Numeric tables show performance for individual real or fake subsets, not a single aggregate binary detection score. Source: Sections 3.3/4.1 pp.5-7; Tables 2-4. Limit: Category/generator evaluation role is supported; exact operating thresholds, preprocessing and aggregation are not specified.

**10. Open-versus-closed generator evaluation.** Fine-tuned models see SD 1.5 earthquake fakes. SD 1.5 fakes in the other categories are seen-generator/unseen-content tests; SD 2.0, SDXL and PixArt are generator-held-out relative to this narrow fine-tuning set. This is cross-generator generalization, not a claim that unknown generators are identified as source classes or a formal open-set attribution protocol. Zero-shot models may have prior exposure through external pretraining that is not exhaustively audited. Source: Section 4.1 pp.6-7; Sections 4.3-4.4 pp.9-10. Limit: Relative unseen-generator evaluation is supported; no source-attribution task change or universally clean open-world exposure claim is warranted.

**11. Dataset curation and quality control.** The authors curate high-quality real imagery and construct semantic prompts with Moondream/Llama 3. They apply the similarity-filtering method of Nguyen et al. reference 18 to remove highly similar generated images. No annotation personnel/count, human acceptance study, contamination audit, near-duplicate threshold, similarity feature definition in this paper or rejection rate is stated. Source: Sections 3.1-3.2 pp.4-5; reference 18 p.14. Limit: Systematic curation is documented, but quality-control implementation and factual disaster/image correctness are not independently verified. No cited source paper was downloaded.

**12. Duplicate and leakage safeguards.** Similarity filtering explicitly targets redundancy among generated images. The manuscript does not establish duplicate screening of real images, cross-source event overlap, near-duplicate or prompt ancestry separation across partitions, hash-based deduplication, memorization checks against generator/pretraining data or a leakage-safe official split. This matters because the real images condition prompts used across generators. Source: Section 3.2 p.5; Section 4.1 pp.6-7. Limit: A limited synthetic redundancy safeguard is supported; broad duplicate/leakage protection remains unverified, not silently assumed.

**13. Public data, annotations, split files and licensing.** The complete reviewed manuscript contains no author-linked Forged Calamity dataset or code release endpoint, no frozen split/annotation file listing and no corpus-specific license. PDF links are author ORCIDs, arXiv and cited-source resources, rather than a dataset package. The PDF metadata specifies CC BY-NC-SA 4.0 for this arXiv manuscript; this does not establish rights for reused Internet/Incident-1M images or a license for the dataset. Cached Springer text gives an exclusive Springer license for the chapter, which likewise does not license image assets. Source: Complete manuscript pp.1-15, PDF link inventory; cached publisher rights metadata. Limit: Resource availability, completeness, annotation schema, split files and redistribution rights remain unverified. No asset download or broad repository search was undertaken.

**14. Independent baseline comparisons and evaluation metrics.** The constructed resource is evaluated by six named generic backbones, seven fine-tuned forensic detectors and six external-pretrained zero-shot forensic detectors. Tables 2-4 supply individual-subset accuracy percentages. This is empirical use by methods independent of any new proposed algorithm and positive evidence of reusability. Precise checkpoints, training hyperparameters, threshold selection, per-row sample denominators, repeated-run uncertainty and aggregate AUROC/AP/balanced accuracy are not reported. Source: Sections 4.2-4.4 pp.7-11; Tables 2/3/4 pp.7/9/11. Limit: Independent-method applicability and published numeric comparisons are supported. All reported numbers remain source claims, not reproduction or controlled causal proof.

**15. Separate substantive dataset contribution beyond the benchmark role.** The first contribution on p.3 explicitly offers a dedicated reusable image corpus; Sections 3.1-3.3 independently specify real-source curation, image-conditioned semantic prompts, four-generator construction, similarity filtering and category/generator strata. Multiple unrelated detectors use that same resource. This material image-resource construction is distinct from Section 4 evaluation partitions/comparison protocol. Under locked R1, it supports dataset in addition to the existing benchmark, rather than data produced solely to validate a new method. The decision does not follow merely from 30,000 images or the phrase benchmark dataset. Source: Contributions p.3; Sections 3.1-3.3 pp.4-6; Sections 4.1-4.4 pp.6-11; locked R1. Limit: DATASET_ADDITION_SUPPORTED provisionally, with dataset;benchmark. Release/version/numerical uncertainties remain explicit; no method, task or publication change is applied.

## Experimental protocols and quantitative evidence

Fine-tuning uses **1,500 real earthquake images + 1,500 SD 1.5 earthquake images**. The paper then reports **18 other subsets**: three other real classes and fifteen synthetic category/generator combinations. It does not identify a validation set, held-out in-distribution test split, official sample IDs or threshold-selection set. Do not infer that all 27,000 remaining images were necessarily tested. Zero-shot evaluation uses externally pretrained models without Forged Calamity fine-tuning and reports **20 subsets**.

The endpoint is binary real/fake. Semantic OOD changes disaster class with SD 1.5 fixed; generator OOD uses SD 2.0/SDXL/PixArt. These are relative held-out generator tests, not source-attribution predictions or a certified exposure-free open-world protocol. Each printed row is accuracy on a single real or fake subset; **it is not an aggregate binary accuracy, balanced accuracy, AUROC or AP**. Per-row denominators, thresholds, seed uncertainty and exact training settings are not documented.

### Table 2, p.7 — generic backbones, fine-tuned; accuracy (%)

| Subset | ConvNeXt | Swin | ViT | SigLIPv2 | DINOv2 | ResNet152 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Real - Fire | 99.67 | 99.67 | 88.13 | 97.87 | 100.00 | 98.20 |
| Real - Flood | 99.87 | 99.13 | 91.80 | 97.67 | 93.33 | 94.47 |
| Real - Thunderstorm | 100.00 | 98.07 | 70.40 | 85.93 | 95.13 | 96.67 |
| Earthquake - PixArt | 36.13 | 79.17 | 82.79 | 68.57 | 89.02 | 52.06 |
| Earthquake - SD 2.0 | 21.08 | 82.98 | 95.11 | 76.19 | 97.46 | 79.17 |
| Earthquake - SDXL | 35.87 | 70.48 | 64.57 | 84.19 | 88.00 | 45.02 |
| Fire - PixArt | 9.78 | 43.87 | 68.00 | 17.40 | 1.46 | 6.98 |
| Fire - SD 1.5 | 66.03 | 73.27 | 96.83 | 85.71 | 45.40 | 58.10 |
| Fire - SD 2.0 | 1.14 | 3.24 | 94.10 | 55.11 | 19.94 | 26.35 |
| Fire - SDXL | 11.11 | 18.29 | 81.14 | 73.11 | 8.76 | 27.24 |
| Flood - PixArt | 2.35 | 42.86 | 65.97 | 34.60 | 35.62 | 5.65 |
| Flood - SD 1.5 | 64.00 | 80.89 | 99.43 | 85.21 | 92.00 | 71.81 |
| Flood - SD 2.0 | 2.48 | 36.06 | 97.33 | 63.62 | 78.60 | 30.79 |
| Flood - SDXL | 3.56 | 29.21 | 73.46 | 63.49 | 58.67 | 19.17 |
| Thunderstorm - PixArt | 0.00 | 12.23 | 12.79 | 4.33 | 0.75 | 5.02 |
| Thunderstorm - SD 1.5 | 9.84 | 77.78 | 95.30 | 81.90 | 57.59 | 37.52 |
| Thunderstorm - SD 2.0 | 0.13 | 41.46 | 93.14 | 55.68 | 58.79 | 25.59 |
| Thunderstorm - SDXL | 0.13 | 33.88 | 43.61 | 36.43 | 10.87 | 19.33 |

### Table 3, p.9 — forensic detectors, fine-tuned; accuracy (%)

| Subset | RINE | UA | LGrad | DIRE | FreqNet | ADOF | CGL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Real - Fire | 50.13 | 99.53 | 97.00 | 99.47 | 94.07 | 97.33 | 100.00 |
| Real - Flood | 50.30 | 76.00 | 89.73 | 96.87 | 93.60 | 92.73 | 99.93 |
| Real - Thunderstorm | 52.13 | 70.87 | 92.73 | 98.13 | 93.00 | 96.60 | 99.00 |
| Earthquake - PixArt | 93.33 | 85.84 | 69.84 | 49.27 | 1.59 | 89.02 | 82.73 |
| Earthquake - SD 2.0 | 81.33 | 92.89 | 94.35 | 64.89 | 25.52 | 67.05 | 11.05 |
| Earthquake - SDXL | 83.70 | 92.57 | 89.40 | 45.02 | 16.63 | 92.76 | 88.44 |
| Fire - PixArt | 94.08 | 43.49 | 11.37 | 10.48 | 7.62 | 77.90 | 84.32 |
| Fire - SD 1.5 | 98.11 | 79.11 | 60.19 | 33.14 | 75.87 | 80.00 | 85.52 |
| Fire - SD 2.0 | 56.29 | 53.65 | 33.14 | 2.92 | 9.02 | 5.27 | 0.70 |
| Fire - SDXL | 64.81 | 58.48 | 46.73 | 18.16 | 10.10 | 24.83 | 29.27 |
| Flood - PixArt | 74.80 | 89.27 | 34.29 | 72.38 | 11.49 | 86.73 | 35.75 |
| Flood - SD 1.5 | 98.99 | 99.56 | 86.67 | 90.41 | 94.86 | 93.27 | 99.68 |
| Flood - SD 2.0 | 67.80 | 98.67 | 76.51 | 55.81 | 41.02 | 79.62 | 1.46 |
| Flood - SDXL | 67.64 | 93.46 | 77.27 | 56.25 | 56.44 | 87.81 | 50.86 |
| Thunderstorm - PixArt | 67.23 | 68.34 | 5.83 | 62.07 | 5.71 | 97.12 | 39.06 |
| Thunderstorm - SD 1.5 | 96.94 | 95.68 | 63.94 | 92.51 | 95.75 | 94.92 | 99.11 |
| Thunderstorm - SD 2.0 | 67.22 | 93.46 | 61.33 | 80.44 | 43.75 | 65.84 | 4.44 |
| Thunderstorm - SDXL | 74.29 | 86.08 | 56.01 | 94.15 | 84.55 | 88.18 | 93.71 |

### Table 4, p.11 — external-pretrained zero-shot forensic detectors; accuracy (%)

| Subset | UniFD | DAE | SPAI | FatFormer | ADOF | CGL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Real - Earthquake | 97.10 | 100.00 | 74.40 | 99.53 | 83.33 | 99.07 |
| Real - Fire | 88.80 | 100.00 | 82.80 | 98.13 | 85.07 | 99.13 |
| Real - Flood | 94.30 | 100.00 | 78.27 | 98.00 | 78.13 | 98.73 |
| Real - Thunderstorm | 91.60 | 100.00 | 70.93 | 96.67 | 80.47 | 92.80 |
| PixArt - Earthquake | 2.10 | 67.75 | 70.98 | 5.97 | 99.17 | 82.73 |
| PixArt - Fire | 6.00 | 73.52 | 94.16 | 5.02 | 99.81 | 84.32 |
| PixArt - Flood | 2.00 | 70.98 | 96.63 | 8.83 | 99.68 | 35.75 |
| PixArt - Thunderstorm | 4.80 | 59.56 | 96.49 | 13.86 | 100.00 | 39.06 |
| SD 1.5 - Earthquake | 9.10 | 64.70 | 100.00 | 27.62 | 99.81 | 87.62 |
| SD 1.5 - Fire | 17.90 | 96.51 | 99.94 | 24.95 | 95.17 | 69.78 |
| SD 1.5 - Flood | 8.30 | 90.16 | 100.00 | 36.70 | 99.68 | 74.35 |
| SD 1.5 - Thunderstorm | 17.30 | 95.24 | 99.75 | 50.92 | 100.00 | 80.25 |
| SD 2.0 - Earthquake | 0.30 | 100.00 | 92.06 | 4.83 | 97.78 | 11.05 |
| SD 2.0 - Fire | 11.00 | 99.11 | 87.68 | 0.19 | 29.02 | 0.70 |
| SD 2.0 - Flood | 0.30 | 100.00 | 97.08 | 6.35 | 99.17 | 1.46 |
| SD 2.0 - Thunderstorm | 3.80 | 98.16 | 89.59 | 11.17 | 99.43 | 4.44 |
| SDXL - Earthquake | 4.00 | 68.38 | 98.86 | 23.81 | 99.94 | 88.44 |
| SDXL - Fire | 6.00 | 34.67 | 95.17 | 11.05 | 99.24 | 29.27 |
| SDXL - Flood | 1.70 | 55.75 | 99.68 | 33.59 | 100.00 | 50.86 |
| SDXL - Thunderstorm | 6.70 | 56.52 | 97.58 | 28.61 | 100.00 | 93.71 |

These tables demonstrate use of the resource by independent generic and forensic detectors. For example, fine-tuned CGL fake-Flood accuracy is **99.68% with SD 1.5 versus 1.46% with SD 2.0**; its fake-Fire results are **85.52% versus 0.70%**. Zero-shot DAE gives **100.00% on all four real subsets** and **99.11% on fake SD 2.0 Fire**, whereas ADOF gives **29.02%** on that fake subset and **99.81% on PixArt Fire**. FatFormer gives **0.19%** on SD 2.0 Fire. These are published subset comparisons, not independently reproduced operating-point or aggregate detection claims.

## Contradictions and practical limitations

- Scientific findings and all table numbers are bound to the complete fifteen-page arXiv 2606.18554v1 author manuscript, not certified as byte-identical to the sixteen-page Springer chapter. Cached publisher prose corroborates major construction/protocol text but omits numerical table bodies; no publisher PDF or alternate complete manuscript was retrieved.

- Canonical year 2025 matches the conference edition but is not independently established as the chapter publication year: publisher first-online is 12 August 2026 and citation/copyright year 2027. This is an out-of-scope publication/version observation only. Canonical bibliographic metadata is preserved without correction.

- Real-image source coverage is inconsistently abbreviated: introduction says Incident-1M, whereas section 3.1 also says the Internet. Geographic/event/time allocation, URLs, copyright permissions and redistribution terms are absent.

- The corpus is globally 6,000 real versus 24,000 synthetic (1:4), although the manuscript calls it balanced. Category/generator cells and the specified real-versus-one-generator training pair are balanced; global binary class balance is not.

- Exact model checkpoints, generation seeds/steps/guidance/resolutions, prompt corpus, per-image lineage, post-filter rejection/replenishment accounting, validation/sample splits and leakage-safe event/prompt partitions are not documented.

- Section 4.2 says eight backbones but enumerates six, and Table 2 contains six named columns. Preserve the discrepancy rather than invent two missing models.

- Page 8 prose says ConvNeXt thunderstorm accuracy drops from 98.1% (SD 1.5) to 49.7% (PixArt), while Table 2 prints 9.84% and 0.00% respectively. Both statements are recorded; the prose is not substituted for the table or treated as reproduced.

- Twelve CGL fake-subset entries for PixArt, SD 2.0 and SDXL are exactly identical in fine-tuned Table 3 and zero-shot Table 4. Their identical printed values do not independently verify common checkpoint conditions; why they repeat across differently described protocols is unexplained.

- Tables report accuracy for individual real or fake subsets, not combined accuracy, balanced accuracy, AUROC or AP. Per-row denominators, threshold selection, training hyperparameters, seed variance, error bars and controlled isolation of generator versus content effects are not supplied. The claimed up-to-50% drop is an author summary, not a computed independently verified aggregate.

- No author-linked dataset endpoint, released image inventory, split/annotation package or corpus-specific license is identified in the reviewed manuscript. The arXiv manuscript license does not establish rights to reused image assets. No datasets, images, supplements, repository archives, weights or cited full papers were downloaded, and no evaluation code was executed.

- Reused local PDF/cache acquisition dates and original network transport receipts are not independently established. Current local byte identity and the version embedded in the PDF are verified. No new full-manuscript transfer receipt is fabricated.

The **twelve repeated CGL values** across fine-tuned Table 3 and zero-shot Table 4 are retained exactly:

| Fake category/generator | Both printed CGL accuracies (%) |
| --- | ---: |
| Earthquake - PixArt | 82.73 |
| Earthquake - SD 2.0 | 11.05 |
| Earthquake - SDXL | 88.44 |
| Fire - PixArt | 84.32 |
| Fire - SD 2.0 | 0.70 |
| Fire - SDXL | 29.27 |
| Flood - PixArt | 35.75 |
| Flood - SD 2.0 | 1.46 |
| Flood - SDXL | 50.86 |
| Thunderstorm - PixArt | 39.06 |
| Thunderstorm - SD 2.0 | 4.44 |
| Thunderstorm - SDXL | 93.71 |

No dataset-specific endpoint is linked by the complete manuscript. Existing PDF links to Moondream/Llama are cited construction tools, **not a Forged Calamity release**. The arXiv PDF's **CC BY-NC-SA 4.0** metadata license covers the manuscript; it does not prove asset copyright permissions or a corpus redistribution license. Public images, per-image annotations, split files, exact reproduction scripts and current download completeness remain unverified. No datasets, image archives, supplements, repository archives, weights or cited papers were downloaded; no evaluation code was run.

## R1 contribution analysis and provisional disposition

Locked R1 states: **Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.**

The material resource contribution is supported independently of the paper's benchmarking role: an explicit central dataset contribution; documented source selection, caption/refinement/generation/filtering construction; a structured category/generator corpus; and empirical applicability to independent methods. Section 4's train-domain partitions and comparisons supply the **benchmark role**; Section 3's curated/generated image corpus supplies the separate **dataset role**. A reusable resource and benchmark may coexist.

The finding does not follow from corpus size or the phrase “benchmark dataset.” It also does not assume new original photography or certify current public downloads. The countercase—that the corpus supports the authors' evaluation and lacks released assets/splits/rights—limits practical reproducibility, but does not erase the independently specified substantive resource construction under R1. Public availability is not imposed as a sole criterion.

**Propose `DATASET_ADDITION_SUPPORTED`, complete types `dataset;benchmark`.** Contribution support is high for this version-pinned manuscript, with material release/version/numerical limitations above. Preserve the existing benchmark; no method label is proposed. Scientific evidence is sufficient for a bounded provisional resource judgment, while maintainer acceptance and any authorized correction remain pending. R335 stays open, authoritative `benchmark` is unchanged, and no terminal decision is appended.

## Lightweight preservation boundary

The worker writes only this TMP review and its JSON/check artifacts. Original canonical fields, taxonomy, public JSON, map identities and decision registry remain unchanged. Global baseline remains **674 public / 557 formal / 613 mapped / 1,410 relationships and pairs**; original Batch B **159 actions / 148 papers**, pending **142 historical / 140 active actions across 129 public papers**. Parent-owned preservation checks cover all 128 protected files, 49 frozen NeurIPS artifacts, Batch C's 13 deferred debts, prior receipts and the separate 39-paper inventory. No full suite, exporter, commit or push is run.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
