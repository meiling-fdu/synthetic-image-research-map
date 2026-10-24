# Batch B Wave B1M — RealChain and LAID benchmark adjudication

Maintainer-approved changes at baseline `53c2a9aa0fa3a36427ea8e71966e29cdfba70153`: **R034 `method;dataset` → `method;dataset;benchmark`** and **R359 `method` → `method;benchmark`**. Both retain **`detection`**, **`fully_generated`**, public inclusion and all bibliographic/author/institution/relationship data. Exactly the two original R034/R359 research-type actions close as **`PROPOSE_CORRECTION_ACCEPTED`**. Independent **P034 remains pending**.

Actual application UTC: **2026-10-23T13:32:14Z**; taxonomy audit date **2026-10-23**. Terminal R034 decision **`review:f58480d5cff48573783e`**; terminal R359 decision **`review:8613ac0d21d46c5ba17b`**. Both supported `other`/`paper`/`no_action_after_review` rows append after the corrections, recording no further work for these bounded accepted reviews, rather than claiming no data changed. The registry grows **94 → 96**, with every pre-existing byte preserved as a prefix. No historical action or denominator is added.

## R034 — independently reusable RealChain protocol

The complete **19-page ECCV2026 Springer publisher chapter**, DOI **10.1007/978-3-032-37429-5_14**, establishes RealChain as an independent evaluation contribution beyond REM (`method`) and its constructed image resource (`dataset`). Its exact primary source, publisher-version identity, bytes and checksum remain in the complete original evidence below and unchanged record: SHA256 **`ee8012fd5021f6ac40f9fc336f81d94e2d734630bface9c333d37cc975e49fe9`**. Under locked R2, add **`benchmark`** while retaining both existing roles. Contribution confidence is **high**; reproducibility confidence is **medium**.

The protocol defines **7,000 real /7,000 synthetic source images**, **seven source/mode strata**, **50 degradation-chain configurations**, no-degradation (**ND**) and chain-degradation (**CD**) conditions, **Balanced Accuracy**, and **nine independent detector baselines**. On the cited RealChain setting, REM ND/CD bAcc is **92.4/84.2** versus DDA **88.8/65.8**; the CD difference is **18.4 percentage points**. These setting-specific percentages and percentage-point difference are not merged with averages across other datasets or manuscript versions. The protocol evaluates detectors other than REM, independently supporting the reusable evaluation benchmark/protocol/resource limb of R2.

Preserve limits: not every degradation-chain definition is independently verified; the bounded chain-JSON metadata request timed out without retry; complete archive contents, exact frozen splits and full evaluator implementation remain unverified. Metadata does not certify every released image/file. REM does not dominate every subset; DRCT ND discrepancies, backbone-to-average association and incompletely reconciled CDC ablation claims remain material. The preserved arithmetic receipt clarifies calculations without replacing printed claims or rewriting independent root notes. Repository commit **c1e8aacf68f041d3abe6509dc01425c5e42ab01e** and RealChain release revision **0f0007d05cbd5ab6213783ad9ec3c2d38ab457c0** remain pinned. No new source or dataset retrieval occurs during adjudication.

## R034 — OUT_OF_SCOPE_BIBLIOGRAPHIC_VERSION_OBSERVATION

The early arXiv2512.20937v1 metadata has **12 authors**, **eight benchmark evaluations** and **7.5%** reported mean improvement. The reviewed ECCV publisher has **13 authors including Manni Cui**, **12 benchmark evaluations** and **6.9%**. The early abstract alone cannot establish all underlying data/protocol changes. Source versions are not assumed equivalent and numerical claims are not averaged or merged. Canonical authors, institutions, title, DOI, venue, year and bibliographic provenance remain unchanged. **P034 stays independently unresolved**, with no terminal P034 decision and no new historical action. This research-type acceptance does not authorize bibliographic correction.

## R359 — bounded framework-based R2 acceptance

The complete **10-page author arXiv2507.05162v1**, submitted **7July2025**, by **Nicholas Chivaran and Jianbing Ni**, is the reviewed LAID source, SHA256 **`ac331d68d67e6ac2a97bff929ffc410a756bba411a4c1ddfbeb304e593f090c0`**. The official DOI request returned **HTTP202 with an empty body**; IEEE publisher-final and paper-time source-code equivalence remain unverified. Add **`benchmark`** while retaining `method`; no dataset or analysis-study label is added. This is a **medium-confidence contribution judgment**, not certification of all results or complete reproduction.

The separately intended comparative framework specifies **ten generic lightweight architectures and two prior detector baselines**, model-agnostic train/test interfaces, explicit resource constraints, spatial and spectral/FFT representations, common training/evaluation axes, joint accuracy/resource metrics and bounded postprocessing perturbations. It reuses GenImage (**100,000 train /16,000 validation /16,000 test**) rather than introducing a new dataset. Future architecture comparisons can use the workflow independently of a preferred model. This independent protocol structure, rather than merely twelve compared models or large tables, distinguishes the accepted R2 framework from ordinary model selection.

Historical R215 conservatively retained method for extensive VFM comparisons. Its exact decision is preserved. R359 is accepted through the narrower combination of reusable architecture-independent interfaces, standardized resource constraints, training/testing workflow, accuracy/resource/perturbation dimensions and independently inspectable implementation. R215, R574 and R400 are bounded precedents, not automatic templates. A competing method-selection interpretation remains preserved in the complete evidence.

## Mandatory R359 Oracle Fusion Accuracy qualification

**Oracle Fusion Accuracy is label-dependent and is not approved as deployable detector accuracy.** Pinned [LAID `test.py` lines272–277](https://github.com/nchivar/LAID/blob/9bd6f07db6c220e53d4f2e07ea00bbda761874e3/test.py#L272-L277), commit **9bd6f07db6c220e53d4f2e07ea00bbda761874e3**, function **`test_attacked`**, counts correctness as **`(img_preds[i] == labels[i]) or (freq_preds[i] == labels[i])`**. This statistic can describe an oracle upper bound on complementary component errors in labelled evaluation. It does not construct a binary class for an unseen image without a separate inference rule.

The same code separately computes **maximum fake probability** for score-based **F1/AUROC**. Those metrics are distinct from the oracle accuracy counter. Code-rule correspondence was inspected; **independent execution reproducing TableIII was not completed**, and no such claim is made. The approved benchmark role covers the broader independently reusable comparison framework, excluding validation of the oracle statistic as deployable accuracy.

FastViT combined perturbation **65.09% spatial** versus **90.91% Oracle Fusion Accuracy** is preserved in its exact evaluation context. The difference is **not demonstrated practical fusion improvement**, real-world performance or deployable fusion accuracy. Keep separate: clean spatial/spectral classification, ordinary postprocessing robustness, Oracle Fusion Accuracy, score-based fusion metrics and a deployable fusion prediction rule (not established by the cited expression). These restrictions are explicit machine-checkable fields in `R359_oracle_fusion_qualification` and the accepted R359 record.

Reported clean spatial/spectral accuracy is **MobileViT97.17/99.89**, **FastViT98.87/99.91**, **MnasNet78.11/50.36**, all percentages in the stated clean settings. Spectral collapse under perturbations, weak blur robustness, eligibility OR/AND wording, loss/checkpoint/README-script differences, rounded resource-denominator discrepancies and negative selection-score correlation remain preserved. Complete checkpoints and exact sampled split membership are unverified; no independent cross-generator holdout or source-content independence is established. Ordinary stochastic transformations are not certified optimized adversarial attacks or measured real social-media transmission. No causal conclusion follows from reported correlations.

## Exact authoritative and deterministic public-data delta

Exactly **14 existing CSV cells across four rows and two files** change: the two `papers.csv` research-type compatibility cells and six research-type/provenance/audit cells per existing `paper_taxonomy.csv` row. All other cells, including tasks, image scopes, status, canonical created/updated timestamps, bibliographic fields, authors, affiliations, institutions and inclusion remain unchanged. Exact before/after rows/cells and source hashes are embedded in the accepted application receipt. Two terminal registry rows append; all prior decisions remain exact.

Measured offline export changes **two existing public papers** and **8 existing dependent map records** (R034: 7, R359: 1), only research types and directly related research-type review reasons. The other **672 public papers**, **1402 map records** and all **1,410 relationship identities** remain semantically unchanged. No public paper/institution is added, removed or reassigned; no task, scope, publication or author metadata changes. Generated JSON is produced only by the deterministic exporter. Direct report differences: `docs/public_preview_report.md`; `docs/key_paper_coverage_report.md`.

## Recomputed counts and original Batch B accounting

| Measure | Current value |
| --- | ---: |
| Public / formal / mapped / unmapped | 674 / 557 / 613 / 61 |
| Relationships / unique pairs | 1410 / 1410 |
| Detection / source attribution / localization | 621 / 84 / 45 |
| Method / dataset / benchmark / survey / analysis study | 578 / 137 / 93 / 21 / 82 |
| Historical Batch B actions / papers | 159 / 148 |
| Historical unresolved actions / papers | 140 / 129 → 138 / 128 |
| Active-public unresolved actions / papers | 138 / 127 → 136 / 126 |

Only R034/R359 close; **P034 remains pending**, so both papers are not assumed to disappear from the unresolved-paper set. All counts/IDs are recomputed from the authoritative context and original ledger. Denominators stay159 actions/148 papers. Batch C’s13 deferred debts, separate39-paper import inventory, all earlier B decisions/evidence,128 protected primary files,49 frozen NeurIPS artifacts and119 ignored operational inputs remain protected.

## Original evidence preserved and actual validation boundary

Both complete original manuscripts and their versions/checksums, rendered pages, full worker/root records, all numerical tables, counterevidence, code/release provenance, prior alternative interpretations, failed retrievals, checker failures and historical timestamps remain intact. The entire original manifest/report is archived losslessly; the original report follows verbatim. Original outer flags alone change to accepted status; R034’s embedded raw scientific worker stays exact with its historical pending flags. Current fingerprints preserve the same17 source keys; only papers, taxonomy, decisions and the two dependent public JSON hashes change.

Evidence-stage checks remain **R03457/57**, **R35959/59**, independent provenance21/21, release10/10, combined science76/76 (R03428 plus18 table checks covering810 cells plus reusedR35930), packet assembly23/23, preservation39/39 and completion-boundary25/25. R359’s360 source table values and all oracle/code qualifications remain intact. Subset checks are not added again to the aggregate. Initial selector/type-harness failures remain separate and scientifically unchanged. Original retrieval accounting stays **one publisher manuscript R034 +one author manuscript R359 =two**, **zero additional complete manuscripts after recovery**, and **zero source retrievals during adjudication**.

<!-- B1M_ADJUDICATION_VALIDATION_START -->
Focused validation: **480 tests and 12 subtests passed**, including **27 B1M regression cases**; zero failures, errors or skips. All four current-scope validators passed with zero errors; actual warning counts are preserved.

The complete repository suite ran **once**: **2133 tests and 389 subtests passed**, zero failures, errors or skips, **2 warnings**. Python 3.14.7, pytest 9.1.1, pytest-subtests 0.15.0 and Node 24.19.0; checksum-matched historical fixtures and authorized localhost. All **4608 compared paths** remained unchanged by the suite.

Two sequential offline export verification passes then passed. All **4608 paths**, seven deterministic outputs and 119 ignored operational inputs remained byte-identical across both passes. Both read-only fixture checks verified 117 inputs and created none. Exactly one initial correction export and two verification exports ran, with no concurrent exporter. `EXPORT_REPRODUCIBLE = 1`.

Integrity gate: **70/70 checks passed**. Exactly two public records and 8 existing dependent map records change only research types and directly related review reasons. All672 other papers, 1402 other map records and 1,410 relationship identities remain unchanged. Fourteen existing CSV cells across four rows and two files change; two terminal decisions append, registry94 →96. Benchmark is93, dataset137; all other corpus and taxonomy totals remain unchanged. Historical unresolved actions:138 across128 papers; active-public actions:136 across126 papers. Independent P034 remains pending.

R359 remains a bounded framework-based benchmark acceptance. Its label-dependent Oracle Fusion Accuracy is not approved as deployable performance; FastViT combined65.09% spatial versus90.91% oracle is not an established practical fusion improvement. The pinned code separately computes maximum fake probability forF1/AUROC; independent TableIII numerical reproduction and publisher/paper-time-code equivalence remain unverified. R034’s bibliographic-version observation and all canonical bibliographic fields remain unchanged; P034 remains independently unresolved.

Original evidence-stage worker checks57/57 and59/59; provenance21/21, release10/10, scientific cross-review76/76 (R03428,table18 covering810 values,reusedR35930), assembly23/23, preservation39/39 and completion-boundary25/25 remain intact. R359’s360 printed table values,16 framework questions and10 fusion questions remain preserved. Subsets are not double-counted. All original findings, contradictions, failed retrievals, source hashes, timestamps and version limitations are preserved. No additional retrieval occurred.

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
<!-- B1M_ADJUDICATION_VALIDATION_END -->

Final required integrity: `UNEXPECTED_CHANGED = 0`, `FROZEN_NEURIPS_CHANGED = 0`, `PREEXISTING_LOCAL_FILES_CHANGED = 0`, `IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`. These remain requirements until measured final gates pass. Primary checkout and unrelated concurrent work remain protected.

Planned single commit: `fix: classify R034 and R359 benchmark contributions`. Publication remains pending until successful validation, exact explicit staging, normal safe fast-forward and independently verified remote SHA, `HEAD == origin/main`, ahead/behind0/0 and clean isolated tree/index. The containing commit and external post-push receipt supply the actual publication identity without circular self-reference. No force push or additional wave is authorized.

Explicit reviewed allowlist:

- `data/curated/paper_taxonomy.csv`
- `data/curated/papers.csv`
- `data/curated/review_decisions.csv`
- `data/raw/corpus_quality_batch_b_wave_b1m_2026_10_23/evidence_manifest.json`
- `docs/corpus_quality_batch_b_wave_b1m_2026_10_23.md`
- `docs/key_paper_coverage_report.md`
- `docs/public_preview_report.md`
- `tests/baseline_expectations.py`
- `tests/test_corpus_quality_batch_b_wave_b1l.py`
- `tests/test_corpus_quality_batch_b_wave_b1m.py`
- `web/data/public_preview_map_data.json`
- `web/data/public_preview_papers.json`

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Preserved complete evidence-only report

Everything below is the full original evidence-stage report, preserved verbatim. Its provisional outcomes, then-current counts, pending flags and historical no-change/untracked observations describe that phase. The acceptance layer above supersedes outer administrative status only; every scientific finding and limitation remains part of the audit history.

---

# Batch B Wave B1M — independent benchmark evidence review

Published baseline: `53c2a9aa0fa3a36427ea8e71966e29cdfba70153`. This evidence-only wave covers exactly **R034** and **R359**, applying locked **R2**. Both original research-type actions remain pending; both scientific proposals require maintainer acceptance and separately authorized remediation. No task, image-scope, inclusion, publication or authoritative research-type changes occur.

| Review | Current types | Provisional outcome | Proposed complete types |
| --- | --- | --- | --- |
| R034 | `method;dataset` | `BENCHMARK_ADDITION_SUPPORTED` | `method;dataset;benchmark` |
| R359 | `method` | `BENCHMARK_ADDITION_SUPPORTED` | `method;benchmark` |

## Recovery, policy and evidence budget

Existing B1M work was recovered after the usage-limit interruption, retaining both full manuscripts, original retrieval receipts, complete readings, rendered pages, pinned release/code metadata and root scientific notes. The same reviewers resumed unfinished work in the same isolated worktree. **Two new complete manuscripts total: R034 one, R359 one; zero repeated successful downloads and zero additional complete manuscripts after recovery.** No datasets, weights, supplements, repository clones/archives or other papers were downloaded; no author code was executed.

Locked R2, copied exactly:

> Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

A systematic comparative framework can qualify while reusing data. A routine model-selection or validation experiment does not automatically qualify. R215, R574 and R400 remain carefully bounded precedents. Their exact decisions are preserved; none is mechanically transferred.

## R359 fusion implementation and numerical boundary

LAID’s complete pinned author manuscript and independently inspected code agree on a critical limitation: **fusion accuracy counts `(spatial_prediction == ground_truth) OR (spectral_prediction == ground_truth)`**. Pinned `test.py`, function `test_attacked`, line272, implements this label-dependent correctness union. It is an **oracle upper bound** on complementary errors, which can be measured on labelled data; it does not supply an inference-time class choice. The manuscript calls it decision-level fusion and uses it to motivate deployable robustness, without identifying an oracle upper bound.

The code separately sends **maximum fake probability** to F1/AUROC; this is not the same construction as its fusion-accuracy counter. Exact numerical reproduction, paper-time code/checkpoints and complete release are unverified. Paper Equations4–5 use `Mp` for spectral predictions; code uses the separate spectral model. Paper/code loss, checkpoint and count differences, eligibility OR/AND wording, resource-denominator ambiguity, MnasNet failures, attacked spectral collapse and negative efficiency-score correlation remain material. These limits qualify the numerical/deployment claims while leaving the independently intended clean and single-domain comparative framework as a separate R2 question.

Exact requested observations remain **MobileViT clean spatial/spectral accuracy97.17/99.89**, **FastViT98.87/99.91**, **MnasNet78.11/50.36**, and **FastViT combined-attack spatial65.09 versus oracle-fusion90.91**. They are different conditions, not pooled or deployable fusion results. The full R359 record includes sixteen framework questions, ten code/fusion questions and360 printed scalar table cells, with exact commit/source-line bindings and competing interpretation.

## R034 — OUT_OF_SCOPE_BIBLIOGRAPHIC_VERSION_OBSERVATION

R034’s complete report below distinguishes RealChain’s constructed resources, reusable evaluation protocol and REM method. Its independently pending **P034** publication action remains open. Version-specific early-arXiv versus publisher counts, author differences and performance claims stay bound to their actual sources; no incompatible figures are averaged or merged. A separately preserved later arithmetic receipt clarifies rounded-table calculations without rewriting original root notes or silently replacing printed claims. No canonical author, title, DOI, venue or year is edited, and no new historical review action is created. Publisher/author manuscript equivalence and release limitations are stated precisely in the complete R034 evidence, without inferring full availability from a README alone.

## Unchanged corpus, taxonomy and accounting

| Measure | Recomputed unchanged value |
| --- | ---: |
| Public / formal / mapped / unmapped | 674 / 557 / 613 / 61 |
| Relationships / unique pairs | 1410 / 1410 |
| Detection / source attribution / localization | 621 / 84 / 45 |
| Method / dataset / benchmark / survey / analysis study | 578 / 137 / 91 / 21 / 82 |
| Historical Batch B actions / papers | 159 / 148 |
| Historical unresolved actions / papers | 140 / 129 |
| Active-public unresolved actions / papers | 138 / 127 |

Evidence sufficiency does not close either review or decrement counts. Batch C’s same **13 deferred debts**, the **39-paper import-review inventory**, **24 prior B1A–L artifacts**, **128 protected local files**, all **49 frozen NeurIPS artifacts** in both checkouts, **119 ignored operational inputs**, original decisions and concurrent primary-checkout work remain protected.

## Preserved independent findings and validation boundary

Complete frozen worker JSON records and Markdown reports, full source manifests, worker receipt histories and independent root scientific/code notes are retained. Exact passing worker checks: R034: 57/57; R359: 59/59. Exact independent checks: independent-source-provenance.json: 21/21; r034-independent-release-provenance.json: 10/10; r034-independent-table-checks.json: 18/18; r359-independent-crossreview.json: 30/30; independent-scientific-crossreview.json: 76/76. These are lightweight source/provenance checks, not repository test-suite counts. The30-check R359 cross-review and18-check R034 all-table verification are reused within the combined scientific review and are not added again to any aggregate.

R034’s complete worker receipt preserves its initial heterogeneous-record selector KeyError and narrow `.get()` repair without scientific changes. Its later independent all-table receipt passed18/18 across810 cells; the earlier17/18 numeric-string assertion history is preserved separately. R359’s initial58/59 checker receipt had only a title-line-wrap selector mismatch. Its narrow whitespace normalization produced59/59 with no scientific-record/table/source change. The initial receipt, checker history and pre-continuation drafts remain authenticated separately. Oracle-fusion findings were verified from existing pinned code after recovery with **zero additional requests**. All source-version, access-failure, numerical counterevidence, dataset-release/license and reproduction limits remain intact.

<!-- B1M_FINAL_VALIDATION_START -->
**Lightweight evidence validation passed.** Frozen worker checks: R034 **57/57**, R359 **59/59**. Independent source/provenance checks **21/21**; separate later R034 release-metadata checks **10/10**; R034 all-table verification **18/18** covering810 cells; combined independent scientific cross-review **76/76**. The R359-only **30/30** cross-review and R034’s18-check table verification are reused within the combined receipt and are not counted again. R359’s360 printed scalar cells,16 framework questions and10 exact fusion questions remain intact, including oracle-versus-deployable and maximum-probability metric boundaries. Original58/59 line-wrap selector failure remains distinct from final59/59; no source/scientific/table bytes were changed by that harness repair.

Independent exact prepared-packet assembly checks passed **23/23**. The measured preservation gate passed **39/39**, retaining all **4486 isolated tracked files**, **4414 primary tracked files** and **305 primary untracked files**, their inventories, bytes, modes, HEAD and index state. The128 protected local files,49 frozen NeurIPS artifacts in each checkout,119 ignored operational inputs,24 prior B1A–L artifacts, historical fixtures/decisions, Batch C’s13 debts and independent39-paper inventory remain unchanged. All corpus/taxonomy and Batch B pending counts were independently recomputed. R034 andR359 remain unresolved; P034 remains independently pending.

`AUTHORITATIVE_CORPUS_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

Only this report and its evidence manifest are new untracked, unstaged files; the isolated tracked tree is clean and index empty. HEAD and fetched origin/main remain at `53c2a9aa0fa3a36427ea8e71966e29cdfba70153` with ahead/behind0/0. No full suite, public export, authoritative correction, terminal decision, commit, push or next wave ran. Exactly **two** complete manuscripts were newly retrieved during original evidence collection, **one per paper**, with **no repeated successful manuscript retrieval and zero additional complete manuscripts after recovery**. Operational binaries, caches and scripts remain outside the two Git artifacts. Only completion-receipt fields are stamped after the measured gate; the final read-only boundary proof authenticates the resulting bytes and all frozen scientific records.
<!-- B1M_FINAL_VALIDATION_END -->

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Complete R034 scientific evidence

# R034 — RealChain benchmark evidence review

**Provisional outcome: BENCHMARK_ADDITION_SUPPORTED.** Proposed complete types: `method;dataset;benchmark`. The evidence is sufficient to propose adding `benchmark` under locked R2; maintainer acceptance is pending. No authoritative change, terminal decision, publication correction or review closure has been applied.

Canonical ID: `curated:aa7dceb70828cdd6ad39`. Current types: `method;dataset`; task: `detection`; scope: `fully_generated`. The original R034 question concerns only whether RealChain contributes a reusable evaluation benchmark. Its seven existing map rows and the independent pending P034 publication question remain untouched.

## Identity and complete primary source

[Official publisher chapter](https://link.springer.com/chapter/10.1007/978-3-032-37429-5_14), DOI `10.1007/978-3-032-37429-5_14`, ECCV 2026, LNCS 17041, pp.225–243; first online 12 September 2026. The actual complete 19-page publisher PDF was read, SHA-256 `ee8012fd5021f6ac40f9fc336f81d94e2d734630bface9c333d37cc975e49fe9`, 3,126,434 bytes. One successful full-manuscript transport; no arXiv PDF, alternate full version or supplement. All 19 main-chapter pages were read; worker visual checks used pages 10, 11 and 14. Root independently read all pages and visually checked 9, 10, 11, 14 and 15 before seeing the worker verdict.

Publisher authors: Ruiqi Liu; Yi Han; Zhengbo Zhang; Liwei Yao; Zhiyuan Yan; Jialiang Shen; ZhiJin Chen; Manni Cui; Boyi Sun; Lubin Weng; Jing Dong; Yan Wang; Shu Wu.

The local-first inventory inspected 79 distinct PDF bodies after magic-byte and gzip/SHA screening of 48,456 files and found no usable identity-matched full R034 source. Historical compressed metadata was not substituted for a manuscript. The original search receipt and its seven unrelated access/partial-PDF errors are preserved.

## Scientific contribution and R2 assessment

REM is the method: perturbed VAE reconstructions create near-real examples (MBR), an envelope estimator learns a binary/tangency boundary (EE), and cross-domain consistency stabilizes clean/degraded representations (CDC). RealChain is the existing dataset and, independently, a detector evaluation resource with ND/CD settings, source/mode strata, operation-chain construction and balanced accuracy.

> Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

The positive R2 threshold is nevertheless met by the independently specified ND/CD task, resource construction, metric and actual multi-detector application. This is a substantive evaluation resource beyond routine comparisons solely selecting a REM variant. Newly generated images and released evaluation code are not imposed as mandatory R2 conditions. Dataset and method roles remain unchanged.

**Competing interpretation.** RealChain is motivated by REM’s robustness claims and overlaps its existing dataset role; large tables, seven strata, the word benchmark or a release link alone would not qualify. Missing complete configurations, fixed splits and an evaluator limit exact independent replication. A conservative reader can therefore question the strength of present operational reuse.

R215 is a bounded model-selection counterprecedent, R574 emphasizes reusable protocols rather than new image creation, and R400 allows a separately defined framework with explicit replication limits. None is mechanically transferred. Scientific R2 confidence is high; confidence in exact operational reproducibility is medium.

## Eighteen required construction and protocol questions

### 1. The complete RealChain construction protocol.

Section 4 separates RealChain from the REM method: collect 7,000 real images; generate 6,000 text-to-image samples and 1,000 image-to-image samples; evaluate clean No Degradation (ND) and random Chain Degradation (CD) outputs. Fifty chains each process 140 real and 140 synthetic images; operation outputs feed the next operation and only the final output is evaluated. These are a separately defined detection evaluation resource and protocol, not merely REM training examples.

**Locator:** §4–4.2, PDF pp.9–10 / printed pp.233–234; Fig.5.

**Boundary:** The main chapter is complete but not a complete operational specification: only 20 chain examples are shown; full configurations, image assignments and source identifiers were not obtained. The version-pinned chain JSON attempt timed out with zero bytes.

### 2. Real and synthetic source-image counts.

RealChain contains 7,000 real images plus 7,000 synthetic images, or 14,000 clean source samples. Six text-to-image generators each render the same designed set of 1,000 prompts, producing 6,000 samples; Seedream 4.0 image-to-image generation adds 1,000 samples. Fifty CD chains × (140 real + 140 fake) imply 14,000 final CD instances, not a stated 50 × 14,000 cross product.

**Locator:** §4.1–4.2, PDF pp.9–10 / printed pp.233–234.

**Boundary:** The exact number of unique base images assigned across chains, repeat assignments, failed generations and intermediate stored-image totals are not specified or independently counted from archives.

### 3. The exact generator list and versions.

The chapter names QwenImage, SDv3.5, Flux.1, Hunyuan 3.0, NanoBanana and Seedream 4.0 for text-to-image generation, plus Seedream 4.0 in image-to-image mode. This is six named generator families and seven source/mode strata. Reference 16 identifies NanoBanana with Gemini 2.5 Flash Image. Table 5 preserves the seven source/mode result pairs.

**Locator:** §4.1, PDF p.9 / printed p.233; Table 5, PDF p.11 / printed p.235; refs.5,16,23,43,46,50.

**Boundary:** Exact checkpoints, API snapshots, generation seeds, sampling settings and hashes are not supplied in the reviewed main chapter or verified metadata. Seven strata must not be restated as seven distinct generator families.

### 4. Text-to-image versus image-to-image composition.

Text-to-image: 1,000 prompts × six generators = 6,000 fake images. Image-to-image: 1,000 prompts rendered with Seedream 4.0 using real references for style transfer and local editing = 1,000 fake images. Table 5 reports a separate i2i stratum; REM balanced accuracy is 83.7 ND / 78.8 CD, versus DDA 80.4 / 65.9.

**Locator:** §4.1, PDF p.9 / printed p.233; Table 5, PDF p.11 / printed p.235.

**Boundary:** Reference-image identities, edit extent, correspondence to real ND samples, masks and operation quotas are not specified. This wave does not change image scopes or forensic tasks on the basis of image-to-image content.

### 5. Open-source versus commercial generator sources.

The paper classifies QwenImage, SDv3.5 and Flux.1 as open-source sources, and Hunyuan 3.0, NanoBanana and Seedream 4.0 as commercial sources. The six text-to-image strata each have 1,000 samples, with an additional 1,000-image Seedream image-to-image stratum.

**Locator:** §4.1, PDF p.9 / printed p.233; pinned author README, Source Images.

**Boundary:** This records the authors’ source categorization, not an independent audit of each generator’s licensing or API availability. Source-mode overlap and content differences can confound open/commercial comparisons.

### 6. Image-content, prompt and provenance relationships.

The real pool is sourced from MSCOCO, OpenImage-v7, Unsplash (printed as Unplash) and ImageNet. The 1,000 text-to-image prompts consist of 500 coarse and 500 fine prompts, rendered across six models. Image-to-image examples use real reference images and a separate stated set of 1,000 prompts. Saving each intermediate degradation output preserves a described chain of operations.

**Locator:** §4.1–4.2, PDF pp.9–10 / printed pp.233–234.

**Boundary:** Real-source quotas, image identifiers, prompt texts, reference-parent links, semantic matching across real/fake pools, deduplication and individual chain lineage are not independently verified. Shared prompts can correlate generator strata, while unmatched real/fake content can induce semantic confounding.

### 7. The number and definitions of degradation chains.

The chapter specifies 50 randomly generated chains. Figure 5 explicitly lists chains 01–10 and 41–50, including X → Crop → Facebook → Screenshot and TikTok → Baidu → Facebook → Sticker → Screenshot. The other 30 chain definitions are not enumerated in the main chapter. The public HF sibling listing includes degradation_chains.json, but its one pinned retrieval failed with HTTP 0 / curl 28 and zero body bytes.

**Locator:** §4.2 and Fig.5, PDF pp.9–10 / printed pp.233–234; HF revision 0f0007d05cbd5ab6213783ad9ec3c2d38ab457c0 sibling metadata.

**Boundary:** Fifty configurations are a manuscript/README claim supported by partial examples, not 50 verified configuration bodies. No retry or alternate source was used to fill the gap.

### 8. Degradation-chain lengths and operation ordering.

The main chapter constructs each chain from 1–3 propagation operations and 0–2 post-processing operations, implying a possible 1–5 total operations. Operations are ordered; each intermediate result becomes the next input and the final result is evaluated. The pinned README instead says length 2–5. Neither statement is silently substituted for the other.

**Locator:** §4.2, PDF pp.9–10 / printed pp.233–234; Fig.5; README at c1e8aacf68f041d3abe6509dc01425c5e42ab01e, Chain Degradations.

**Boundary:** No fixed five-level severity schedule is defined. Exact sampling probabilities, ordering constraints, random seeds and whether a one-operation chain actually occurs are not verified. The inaccessible full JSON prevents reconciliation of paper versus README bounds.

### 9. Social-media platform simulations.

Figure 5 uses six platform labels: X, Facebook, TikTok, WeChat, Baidu and Instagram. The operation library covers PC→PC, mobile→mobile, PC→mobile and mobile→PC upload/download routes, then filters, stickers, crops/aspect changes and screenshots. The README names WeChat, TikTok, Baidu, Instagram and X, omitting Facebook from its shorter list.

**Locator:** §4.2 and Fig.5, PDF pp.9–10 / printed pp.233–234; pinned README, Propagation.

**Boundary:** Platform labels and example chains do not establish exact application versions, devices, codec parameters or faithful implementation of each service. The repository’s platform list is not a verified correction to the paper.

### 10. Whether platform effects are measured or only synthetically approximated.

The paper calls the benchmark a realistic simulation and describes upload/download propagation operations. This is sufficient to identify the intended evaluation stressor, but not to verify empirical measurement of actual deployed platform transformations. No independently validated codec/device calibration is supplied in the reviewed source or fetched metadata.

**Locator:** §4 introduction and §4.2, PDF pp.9–10 / printed pp.233–234; Fig.5; README.

**Boundary:** Whether every operation involved actual live platform transmission or a programmatic approximation remains unresolved. No app/network experiments were performed. JPEG quality 96 elsewhere in the paper concerns selected external benchmark format alignment, not a measured RealChain platform effect.

### 11. No-degradation versus chain-degradation protocols.

ND evaluates directly collected real and cleanly generated fake images. CD evaluates final outputs after each assigned multi-operation chain. Table 5 applies both settings to all seven synthetic source/mode strata and nine independent baselines plus REM. Overall REM ND/CD is 92.4/84.2 balanced accuracy; DDA is 88.8/65.8.

**Locator:** §4.2, PDF pp.9–10 / printed pp.233–234; Tables 1 and 5, PDF pp.10–11.

**Boundary:** Per-image ND/CD pairing, exact chain partition membership and cross-setting weighting are not verified. DRCT ND differs between Table 1 (69.1) and Table 5 (68.6); both are retained. No data regeneration or independent evaluation was performed.

### 12. Dataset and source-class balance.

The clean resource is balanced at 7,000 real and 7,000 fake; each of the seven synthetic source/mode strata contributes 1,000 images. Each of 50 CD chains is applied to 140 real and 140 fake images. Balanced accuracy averages real-class and fake-class accuracy.

**Locator:** §4.1–4.2, PDF pp.9–10; §5.1 Metrics, PDF p.12 / printed p.236; Table 5.

**Boundary:** Exact real-pool proportions and synthetic-source balance within each individual chain are not stated. One must not infer 20 images per source per chain or file-level class balance from archive filenames alone.

### 13. Training/test separation and generator holdout.

REM trains on MSCOCO real images with MBR-generated near-real samples rather than on the seven RealChain fake strata; this motivates testing generalization to newer generators. The method uses a pretrained SD VAE and DINOv3 backbone. RealChain’s real pool also names MSCOCO.

**Locator:** §3, PDF pp.5–8 / printed pp.229–232; §4.1, PDF p.9; §5.1, PDF p.12; Fig.7.

**Boundary:** The main source does not provide train/test image IDs, source-disjoint splits, real-content deduplication or an auditable generator holdout registry. MSCOCO source overlap raises an unverified content-leakage risk; pretrained VAE/backbone exposure also prevents a claim that all generator-family priors were unseen. Neither risk is evidence that leakage actually occurred.

### 14. Reusable evaluation splits and metrics.

The model-independent task is real/fake detection under ND and CD, scored by balanced accuracy (mean real and fake accuracy). Section 4 specifies the resource and chain assignment counts; Table 5 exposes seven paired source-mode evaluations. This supports reuse by new detectors in principle.

**Locator:** §4–4.2, PDF pp.9–10; §5.1 Metrics, PDF p.12; Table 5, PDF p.11.

**Boundary:** No explicit train/validation/test file registry, fixed threshold protocol, per-seed repetitions, confidence intervals, complete chain configuration or executable evaluator was verified. It is a partly specified reusable benchmark, not a fully reproduced evaluation library.

### 15. Independent baselines and their operating conditions.

The nine baselines are NPR, UnivFD, FatFormer, SAFE, C2P-CLIP, AIDE, DRCT, Aligned and DDA. The authors use official implementations and pretrained checkpoints. Table 1 spans six ideal and five external in-the-wild benchmarks plus RealChain ND/CD. JPEG quality 96 is applied to fake images in AIGCDetect, ForenSynths and GenImage following DDA to mitigate format bias. REM settings include DINOv3, SD VAE FT-MSE, shorter-side 512 resizing for large images, 224 crops, Adam 1e-4, batch 256, one epoch, four A100s and approximately 30 minutes.

**Locator:** §5.1, PDF pp.11–12 / printed pp.235–236; Tables 1–6, PDF pp.10–11.

**Boundary:** The baselines are not all retrained under one identical recipe, and exact checkpoint/threshold hashes are not preserved by the paper. Section 5.1’s H+/16 statement, Table 8’s backbone means and Table 1’s headline mean do not fully identify a consistent model/aggregation association. Training, hardware or generation cost comparisons must not be assumed matched.

### 16. Actual benchmark release status, version and license.

At Git commit c1e8aacf68f041d3abe6509dc01425c5e42ab01e, the author README declares a March 2026 HF release, CC BY-NC 4.0 for RealChain and MIT for code. The pinned root directory contains only README.md and fig, and says training/inference code will be released soon. A read-only HF info call verifies a public non-gated repository at revision 0f0007d05cbd5ab6213783ad9ec3c2d38ab457c0 with seven synthetic archive names, Real.tar and degradation_chains.json; created and last modified on 2026-03-18. No image/archive payload was downloaded.

**Locator:** Pinned GitHub API README/root metadata; HF CLI datasets info receipt and sibling listing.

**Boundary:** An author-declared dataset license is not a license inferred from code. The fetched HF metadata has no cardData/license field and no README sibling; no separate LICENSE is present in the fetched Git root. Archive contents, image counts, full usability, final-publication equivalence and complete chain definitions are not verified. The single small chain JSON access timed out without a body.

### 17. Reproducibility limitations, leakage risks and benchmark confounders.

Material limitations include incomplete chain definitions and severities, paper/README length and platform differences, no audited content-disjoint split, real-source overlap with training, checkpoint/API drift, unmatched baseline training, unclear decision thresholds, source-mode/content confounding and version differences. Tables also contain explicit numerical/reporting tensions documented below. These restrict exact replication and headline attribution while leaving the separate evaluation-resource contribution observable.

**Locator:** §§3–5; Fig.5–7; Tables 1–8; publisher/arXiv metadata; pinned README/HF receipts.

**Boundary:** No hidden parameter is filled by assumption. No claim is made that independent reproduction succeeded, data leakage occurred, all platform effects were measured, every baseline was uniformly inferior, or all publisher-final resources were released.

### 18. Whether RealChain can evaluate detection methods other than REM.

Yes in scientific design: Section 4 defines an ND/CD real-versus-fake task and resource independently of the REM architecture, and Table 5 actually evaluates nine different detectors across all seven source/mode pairs. This exceeds merely testing one proposed method. Under locked R2, it supports adding benchmark while retaining the already recognized method and dataset roles.

**Locator:** §4–4.2, PDF pp.9–10; Tables 1 and 5; locked R2.

**Boundary:** Operational reuse is limited by incomplete released configuration/split/evaluator verification. Code release and newly generated images are not mandatory R2 conditions. The result is a provisional scientific recommendation, not a maintainer-accepted taxonomy change.

## Quantitative results and counterevidence

All eight printed tables are transcribed below, preserving 810 numeric result cells and their original decimal precision. These are source-reported balanced-accuracy values, not independently reproduced experiments. Table 1 REM 94.9 versus DDA 88.0 yields 6.9 percentage points; Table 5 CD 84.2 versus 65.8 yields 18.4 points. REM is not best on every generator/subset.

RealChain Table 5: REM ND/CD by source is Flux.1 96.5/86.7, Hunyuan3 93.8/85.3, NanoBanana 91.9/84.8, QwenImage 94.1/87.3, SDv3.5 92.9/84.5, Seedream4 94.2/81.9 and i2i 83.7/78.8. Overall ND/CD is 92.4/84.2, versus DDA 88.8/65.8. These are binary authenticity metrics, not generator-identity attribution results.

- **Nonuniform detector superiority.** REM ForenSynths 91.5 is below C2P-CLIP 92.0. REM ProGAN 97.4 is below UnivFD 99.4, FatFormer 98.5 and C2P-CLIP 99.3; REM StarGAN 90.2 is below C2P-CLIP 99.6. The overall headline is not uniform per-subset dominance. (Table 1, PDF p.10; Table 2, PDF p.10)
- **Printed DRCT RealChain ND mismatch.** Table 1 prints 69.1; Table 5 prints 68.6. Both are preserved without correction. (Table 1, PDF p.10; Table 5, PDF p.11)
- **Backbone and average association unresolved.** Section 5.1 specifies DINOv3 ViT-H+/16 for comparisons and ablations. Table 8 H+/16 Avg is 93.6, whereas 7B/16 Avg is 94.9; Table 1 headline Avg is 94.9 across a different inventory of settings. The repeated number does not prove Table 1 used 7B. Table 1 REM WildRF is 97.8, whereas Table 8 H+ WildRF is 97.9. (§5.1, PDF p.12; Table 1, PDF p.10; Table 8, PDF p.14)
- **Ablation setting and claimed CDC drop unresolved.** Table 7 RealChain column is not labeled ND/CD. Full MBR+EE+CDC is 88.3 and MBR+EE without CDC is 79.4: 8.9 percentage points. The prose claims a 16.4% drop. Full 88.3 happens to equal (92.4+84.2)/2; that is arithmetic consistency, not verified setting identification. (§5.3, PDF p.13; Table 7, PDF p.14)
- **Twelve benchmarks versus thirteen displayed settings.** There are 12 distinct benchmarks but 13 ND/CD setting columns. A simple mean of those 13 printed settings reproduces REM 94.9 and DDA 88.0 after rounding. This is a possible reconstruction, not proof of intended weighting. Alternative 12-benchmark averages differ. (§5.2; Table 1, PDF p.10; arithmetic-receipt.json)
- **Paper versus README chain bounds and platform list.** The paper permits 1–3 propagation plus 0–2 post-process steps (possible total 1–5); README says 2–5. Fig.5 includes Facebook among six platforms; README lists five without Facebook. The unavailable full JSON prevents reconciliation. (§4.2 and Fig.5; README at c1e8aacf68f041d3abe6509dc01425c5e42ab01e)

The separate arithmetic receipt computes a possible unweighted mean over 13 displayed ND/CD settings: REM 94.93846 → 94.9 and DDA 87.97692 → 88.0. It does not prove the authors’ intended weights. Fig.7 generation costs (GPU-hours per 1,000 samples) are SDXL 1.33, SD3.5 3.61, Flux 6.94, Qwen 6.67 and MBR 0.10; exact matched settings/hardware are not established. No unprinted Fig.6 curve values were invented.

### Table 1 — PDF page 10, printed page 234

| Method | AIGCDetect | Synthbuster | EvalGEN | ForenSynths | GenImage | DRCT-2M | Ideal_Avg | Chameleon | SynthWildx | WildRF | AIGIBench | Bfree-Online | Wild_Avg | RealChain_ND | RealChain_CD | Overall_Avg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NPR | 53.1 | 50.0 | 2.9 | 47.9 | 51.5 | 37.3 | 40.5 | 59.9 | 49.8 | 63.5 | 54.2 | 49.5 | 55.4 | 74.3 | 55.7 | 50.0 |
| UnivFD | 72.5 | 67.8 | 15.4 | 77.7 | 64.1 | 61.8 | 59.9 | 50.7 | 52.3 | 55.3 | 53.0 | 49.0 | 52.1 | 54.2 | 51.3 | 55.8 |
| FatFormer | 85.0 | 56.1 | 45.6 | 90.0 | 62.8 | 52.2 | 65.3 | 51.2 | 52.1 | 58.9 | 54.4 | 50.0 | 53.3 | 54.9 | 51.2 | 58.8 |
| SAFE | 50.3 | 46.5 | 1.1 | 49.7 | 50.3 | 59.3 | 42.9 | 59.2 | 49.1 | 57.2 | 56.5 | 50.5 | 54.5 | 61.4 | 49.8 | 49.3 |
| C2P-CLIP | 81.4 | 68.5 | 38.9 | 92.0 | 74.4 | 59.2 | 69.1 | 51.1 | 57.1 | 59.6 | 53.7 | 50.0 | 54.3 | 51.3 | 51.3 | 60.7 |
| AIDE | 63.6 | 53.9 | 19.1 | 59.4 | 61.2 | 64.6 | 53.6 | 63.1 | 48.8 | 58.4 | 55.5 | 53.1 | 55.8 | 60.4 | 50.0 | 54.7 |
| DRCT | 81.4 | 84.8 | 77.8 | 73.9 | 84.7 | 90.5 | 82.2 | 56.6 | 55.1 | 50.6 | 72.1 | 55.7 | 58.0 | 69.1 | 55.4 | 69.8 |
| Aligned | 66.6 | 77.4 | 68.0 | 53.9 | 79.0 | 95.5 | 73.4 | 71.0 | 78.8 | 80.1 | 72.7 | 68.5 | 74.2 | 68.7 | 58.0 | 72.2 |
| DDA | 87.8 | 90.1 | 97.2 | 81.4 | 91.7 | 98.1 | 91.1 | 82.4 | 90.9 | 90.3 | 84.1 | 95.1 | 88.6 | 88.8 | 65.8 | 88.0 |
| REM | 97.9 | 99.0 | 99.2 | 91.5 | 98.8 | 98.9 | 97.6 | 91.3 | 95.4 | 97.8 | 91.3 | 96.5 | 94.5 | 92.4 | 84.2 | 94.9 |

### Table 2 — PDF page 10, printed page 234

| Method | ADM | DALLE2 | GLIDE | Midjourney | VQDM | BigGAN | CycleGAN | GauGAN | ProGAN | SDXL | SD1.4 | SD1.5 | StarGAN | StyleGAN | StyleGAN2 | WFR | Wukong | Avg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NPR | 43.8 | 20.0 | 41.2 | 53.4 | 48.4 | 53.1 | 76.6 | 42.2 | 58.7 | 59.6 | 55.1 | 55.0 | 67.4 | 57.9 | 54.6 | 58.8 | 57.4 | 53.1 |
| UnivFD | 62.5 | 50.0 | 61.3 | 55.1 | 76.9 | 87.5 | 96.9 | 98.8 | 99.4 | 58.2 | 55.6 | 55.7 | 95.1 | 80.0 | 69.4 | 69.2 | 61.1 | 72.5 |
| FatFormer | 80.2 | 68.5 | 91.1 | 54.4 | 88.0 | 99.2 | 99.5 | 99.1 | 98.5 | 71.7 | 67.5 | 67.2 | 99.4 | 98.0 | 98.8 | 88.3 | 75.6 | 85.0 |
| SAFE | 49.5 | 49.5 | 53.0 | 49.0 | 50.2 | 52.2 | 51.9 | 50.0 | 50.0 | 49.8 | 49.7 | 49.8 | 50.1 | 50.0 | 50.0 | 49.8 | 50.3 | 50.3 |
| C2P-CLIP | 71.6 | 52.3 | 73.5 | 56.6 | 73.7 | 98.4 | 96.8 | 98.8 | 99.3 | 62.3 | 77.5 | 76.9 | 99.6 | 93.1 | 79.4 | 94.8 | 79.4 | 81.4 |
| AIDE | 52.9 | 51.1 | 60.2 | 49.8 | 69.3 | 70.1 | 93.6 | 60.6 | 89.0 | 49.6 | 51.6 | 51.0 | 72.1 | 66.5 | 59.0 | 80.6 | 54.5 | 63.6 |
| DRCT | 79.9 | 89.2 | 89.2 | 85.5 | 88.6 | 81.4 | 91.0 | 93.8 | 71.1 | 88.3 | 91.4 | 91.0 | 53.0 | 62.7 | 63.8 | 73.9 | 90.8 | 81.4 |
| Aligned | 51.6 | 52.0 | 55.6 | 96.2 | 72.1 | 51.2 | 49.5 | 50.8 | 50.7 | 95.1 | 99.7 | 99.6 | 53.8 | 52.7 | 51.6 | 50.0 | 99.6 | 66.6 |
| DDA | 89.5 | 94.6 | 89.6 | 95.6 | 76.6 | 91.0 | 72.5 | 92.7 | 92.8 | 99.4 | 98.7 | 98.6 | 72.7 | 87.8 | 90.2 | 52.1 | 98.8 | 87.8 |
| REM | 98.1 | 99.3 | 98.6 | 96.5 | 99.3 | 99.4 | 98.1 | 99.8 | 97.4 | 99.8 | 99.3 | 99.5 | 90.2 | 95.1 | 96.3 | 98.4 | 99.5 | 97.9 |

### Table 3 — PDF page 11, printed page 235

| Method | DALLE2 | DALLE3 | Firefly | GLIDE | Midjourney | SD1.3 | SD1.4 | SD2 | SDXL | Avg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NPR | 51.1 | 49.3 | 46.5 | 48.5 | 52.8 | 51.4 | 51.8 | 46.0 | 52.8 | 50.0 |
| UnivFD | 83.5 | 47.4 | 89.9 | 53.3 | 52.5 | 70.4 | 69.9 | 75.7 | 68.0 | 67.8 |
| FatFormer | 59.4 | 39.5 | 60.3 | 72.7 | 44.4 | 53.7 | 54.0 | 52.3 | 69.1 | 56.1 |
| SAFE | 58.0 | 9.9 | 10.3 | 52.2 | 56.7 | 59.4 | 59.1 | 53.0 | 59.5 | 46.5 |
| C2P-CLIP | 55.6 | 63.2 | 59.5 | 86.7 | 52.9 | 75.2 | 76.7 | 69.2 | 77.7 | 68.5 |
| AIDE | 34.9 | 33.7 | 24.8 | 65.0 | 57.5 | 74.1 | 73.7 | 53.2 | 68.4 | 53.9 |
| DRCT | 77.2 | 86.6 | 84.1 | 82.6 | 73.7 | 86.6 | 86.6 | 83.2 | 71.3 | 84.8 |
| Aligned | 50.2 | 48.9 | 51.7 | 53.5 | 98.7 | 98.8 | 98.8 | 98.6 | 97.3 | 77.4 |
| DDA | 86.3 | 90.0 | 91.9 | 76.5 | 93.5 | 92.9 | 92.7 | 93.3 | 93.5 | 90.1 |
| REM | 99.1 | 99.9 | 93.5 | 98.8 | 99.9 | 100.0 | 100.0 | 99.9 | 99.9 | 99.0 |

### Table 4 — PDF page 11, printed page 235

| Method | Flux | GoT | Infinity | NOVA | OmiGen | Avg |
| --- | --- | --- | --- | --- | --- | --- |
| NPR | 0.7 | 0.2 | 6.5 | 4.7 | 2.2 | 2.9 |
| UnivFD | 4.0 | 9.2 | 15.7 | 8.3 | 39.6 | 15.4 |
| FatFormer | 9.9 | 47.9 | 44.7 | 98.3 | 27.3 | 45.6 |
| SAFE | 1.0 | 0.5 | 1.9 | 0.6 | 1.6 | 1.1 |
| C2P-CLIP | 8.7 | 49.6 | 35.3 | 86.4 | 14.5 | 38.9 |
| AIDE | 17.9 | 24.7 | 3.4 | 16.3 | 33.4 | 19.1 |
| DRCT | 72.5 | 81.4 | 77.9 | 84.6 | 72.5 | 77.8 |
| Aligned | 32.0 | 72.3 | 74.0 | 84.8 | 77.0 | 68.0 |
| DDA | 89.9 | 99.5 | 97.8 | 99.5 | 99.5 | 97.2 |
| REM | 97.2 | 100.0 | 98.9 | 99.9 | 99.9 | 99.2 |

### Table 5 — PDF page 11, printed page 235

| Method | Flux.1_ND | Flux.1_CD | Hunyuan3_ND | Hunyuan3_CD | NanoBanana_ND | NanoBanana_CD | QwenImage_ND | QwenImage_CD | SDv3.5_ND | SDv3.5_CD | Seedream4_ND | Seedream4_CD | i2i_ND | i2i_CD | Avg_ND | Avg_CD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NPR | 84.2 | 57.6 | 70.7 | 55.4 | 64.7 | 53.1 | 53.0 | 54.4 | 78.3 | 56.0 | 75.4 | 54.4 | 93.6 | 59.0 | 74.3 | 55.7 |
| UnivFD | 54.2 | 52.1 | 55.8 | 51.7 | 56.5 | 51.9 | 53.2 | 50.7 | 52.6 | 49.6 | 51.5 | 51.5 | 55.4 | 51.9 | 54.2 | 51.3 |
| FatFormer | 52.2 | 48.1 | 57.3 | 53.2 | 59.8 | 50.5 | 54.1 | 50.2 | 52.5 | 54.2 | 54.7 | 51.9 | 53.6 | 50.6 | 54.9 | 51.2 |
| SAFE | 55.4 | 49.7 | 59.6 | 49.7 | 66.1 | 49.5 | 50.8 | 48.5 | 64.6 | 50.3 | 69.8 | 49.8 | 63.8 | 50.9 | 61.4 | 49.8 |
| C2P-CLIP | 51.4 | 52.3 | 52.6 | 48.7 | 53.1 | 52.5 | 50.9 | 53.2 | 49.6 | 51.1 | 49.2 | 50.8 | 52.3 | 50.4 | 51.3 | 51.3 |
| AIDE | 69.4 | 48.6 | 64.5 | 51.7 | 66.3 | 50.6 | 57.7 | 46.3 | 52.0 | 57.3 | 52.6 | 47.3 | 60.0 | 48.4 | 60.4 | 50.0 |
| DRCT | 54.4 | 58.3 | 51.9 | 55.2 | 77.5 | 57.8 | 63.8 | 52.6 | 70.8 | 53.8 | 78.0 | 56.2 | 83.6 | 53.7 | 68.6 | 55.4 |
| Aligned | 71.8 | 56.0 | 61.6 | 54.9 | 65.8 | 53.8 | 62.8 | 55.6 | 63.1 | 64.1 | 79.3 | 65.9 | 76.6 | 55.7 | 68.7 | 58.0 |
| DDA | 90.5 | 67.0 | 88.0 | 62.5 | 83.4 | 63.6 | 93.5 | 70.2 | 92.1 | 67.7 | 93.4 | 63.5 | 80.4 | 65.9 | 88.8 | 65.8 |
| REM | 96.5 | 86.7 | 93.8 | 85.3 | 91.9 | 84.8 | 94.1 | 87.3 | 92.9 | 84.5 | 94.2 | 81.9 | 83.7 | 78.8 | 92.4 | 84.2 |

### Table 6 — PDF page 11, printed page 235

| Method | SynthWildx_DALLE3 | SynthWildx_Firefly | SynthWildx_Midjourney | WildRF_Facebook | WildRF_Reddit | WildRF_Twitter | AIGIBench_SocRF | AIGIBench_ComAI | Avg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NPR | 43.6 | 61.3 | 44.5 | 78.1 | 61.0 | 51.3 | 53.3 | 55.1 | 57.1 |
| UnivFD | 45.4 | 65.3 | 46.2 | 49.1 | 60.2 | 56.5 | 54.6 | 51.4 | 53.3 |
| FatFormer | 46.5 | 61.6 | 48.3 | 54.1 | 68.1 | 54.4 | 56.9 | 51.9 | 54.9 |
| SAFE | 49.4 | 48.2 | 49.6 | 50.9 | 74.1 | 37.5 | 58.4 | 54.5 | 52.7 |
| C2P-CLIP | 56.9 | 61.4 | 53.0 | 54.4 | 68.4 | 55.9 | 56.4 | 51.0 | 57.3 |
| AIDE | 63.4 | 48.8 | 51.9 | 57.8 | 71.5 | 45.8 | 57.3 | 53.7 | 57.5 |
| DRCT | 58.3 | 56.4 | 50.5 | 46.6 | 53.1 | 55.2 | 67.5 | 76.7 | 53.8 |
| Aligned | 85.5 | 58.5 | 92.2 | 89.4 | 69.1 | 81.8 | 73.5 | 71.9 | 78.2 |
| DDA | 92.3 | 87.3 | 93.1 | 93.1 | 86.4 | 91.5 | 79.6 | 88.6 | 88.3 |
| REM | 96.5 | 92.8 | 96.9 | 97.2 | 98.1 | 98.2 | 92.2 | 90.4 | 94.8 |

### Table 7 — PDF page 14, printed page 238

| Configuration | MBR | EE | CDC | Ideal_Bench | Wild_Bench | RealChain |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | — | — | — | 85.5 | 80.9 | 76.4 |
| 2 | ✓ | ✓ | — | 93.6 | 85.8 | 79.4 |
| 3 | — | ✓ | ✓ | 91.5 | 86.3 | 83.6 |
| 4 | ✓ | — | ✓ | 93.3 | 89.5 | 84.3 |
| 5 | ✓ | ✓ | ✓ | 97.6 | 94.5 | 88.3 |

### Table 8 — PDF page 14, printed page 238

| Backbone | AIGCDetect | DRCT-2M | Chameleon | SynthWildx | WildRF | AIGIBench | RealChain_ND | RealChain_CD | Avg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DINOv2-L/14 | 95.1 | 97.9 | 84.6 | 91.4 | 95.8 | 87.2 | 89.3 | 78.5 | 90.0 |
| DINOv2-g/14 | 96.3 | 97.8 | 85.5 | 91.0 | 95.8 | 89.8 | 89.4 | 80.7 | 90.8 |
| DINOv3-L/16 | 97.0 | 98.1 | 89.7 | 93.2 | 96.3 | 89.1 | 91.1 | 83.3 | 92.2 |
| DINOv3-H+/16 | 97.9 | 98.9 | 91.3 | 95.4 | 97.9 | 91.3 | 92.4 | 84.2 | 93.6 |
| DINOv3-7B/16 | 98.2 | 99.4 | 93.7 | 96.5 | 98.2 | 93.7 | 93.6 | 86.1 | 94.9 |

## Release provenance and operational limits

The author repository is pinned to `c1e8aacf68f041d3abe6509dc01425c5e42ab01e`; README Git blob `adbd88f800e765de97e779614cc0e9a39229014d`, decoded SHA-256 `4d58fc49c5fd8eb3fa7be74f5782b0d9c7ff067e0f726b051dadb2fceff09178`. Its fetched root lists only `README.md` and `fig`. Training/inference code is described as forthcoming; no evaluator, code archive or checkpoint was obtained or executed. The README declares code MIT separately from RealChain CC BY-NC 4.0. No separate LICENSE file appears in the fetched root.

Read-only HF CLI metadata identifies `handsomerich/RealChain` at revision `0f0007d05cbd5ab6213783ad9ec3c2d38ab457c0`, public and non-gated, created/last modified 18 March 2026. Its sibling names are: `.gitattributes`, `Flux1.zip`, `Hunyuan3.zip`, `NanoBanana.zip`, `QwenImage.zip`, `Real.tar`, `SDv3.5.zip`, `Seedream4.zip`, `degradation_chains.json`, `i2i.zip`. No cardData/license was returned and no README sibling is listed. Archive listings establish named public resources, not verified asset contents, sample counts, installation success or equivalence to publisher-final data. No images, datasets, archives or model weights were downloaded.

The one revision-pinned `degradation_chains.json` request started 23 October 2026 at 07:12:05.940077 UTC and ended at 07:12:20.964751 UTC: HTTP 0, curl 28, zero body bytes, no retries. It remains an access limitation; full configurations and reconciliation of the paper/README chain differences are unverified.

Important remaining risks include unidentified train/test image membership, shared MSCOCO source pools, possible pretrained-prior exposure, unavailable exact generator API/checkpoint versions, unknown source/chain sampling and thresholds, unmatched baseline training, and source/content/operation confounding. These are limitations and risks, not demonstrated leakage or proof that all reported results are invalid.

## OUT_OF_SCOPE_BIBLIOGRAPHIC_VERSION_OBSERVATION

The official arXiv abstract identifies only v1 (24 December 2025, 04:41:04 UTC), 12 authors, eight evaluations and 7.5% average improvement. Its full manuscript was not requested or read. The actual ECCV publisher chapter has 13 authors, adding **Manni Cui between ZhiJin Chen and Boyi Sun**, and reports 12 evaluations, 6.9% average and 18.4% RealChain improvement. The publisher full source is used for scientific tables; these figures are not merged with the earlier abstract.

The early abstract cannot establish changed construction details or explain whether added datasets/backbones caused the differences. Table 8 and Table 1 themselves leave model/aggregation associations unresolved. The current README repeats publisher figures but retains an arXiv 2025 citation; the March HF revision is not verified as publisher-final. No alternate complete scientific version was downloaded just to compare metadata.

P034 remains independently pending. Canonical authors, DOI (currently empty), venue, year, title and arXiv identity remain unchanged. This observation closes no action, creates no action and changes no historical denominator.

## Retrieval accounting and disposition boundary

One new complete manuscript; one successful publisher PDF transport; zero alternate complete versions, arXiv PDF requests, supplements, dataset/image/weight payloads, clones, archives or source execution. Bounded metadata: three GitHub API calls, one read-only HF info CLI call, one failed small chain-JSON request. Four web metadata opens (one generic DOI reader failure) and one exact publisher-domain metadata search are counted separately. No retry was made.

The proposal is `method;dataset;benchmark`, with maintainer acceptance pending. Current `method;dataset`, detection task, fully_generated scope, inclusion, seven map relationships and all bibliographic fields remain unchanged. Original B totals remain 159 actions / 148 papers; unresolved 140 / 129, active-public unresolved 138 / 127. P034 is not resolved by this review. No repository tests, exporter, staging, commit or push was performed by this worker. Parent-owned integrity receipts separately cover the 128 protected files, 49 frozen NeurIPS artifacts, 13 Batch C debts and 39-paper inventory.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`


## Complete R359 scientific evidence

# R359 — LAID: independent benchmark contribution review

Provisional **BENCHMARK_ADDITION_SUPPORTED**; proposed complete research types **`method;benchmark`**, with **medium confidence**. Current `method`, `detection` and `fully_generated` remain authoritative and unchanged. The original R359 action remains open; maintainer acceptance is pending. No analysis-study or dataset label, metadata edit or new review action is proposed.

## Identity, source and retrieval

Canonical `curated:e688194977fa7bbf7db3`; exact title **LAID: Lightweight AI-Generated Image Detection in Spatial and Spectral Domains**, authors **Nicholas Chivaran and Jianbing Ni**, Queen’s University. DOI **10.1109/PST65910.2025.11268874** remains canonical; the existing empty arXiv field is not edited. Reviewed complete **10-page arXiv 2507.05162v1**, submitted **7 July 2025 16:18:19 UTC**, author manuscript “to appear PST2025”: [pinned primary PDF](https://arxiv.org/pdf/2507.05162v1). Size **1,502,619 bytes**; SHA256 **`ac331d68d67e6ac2a97bff929ffc410a756bba411a4c1ddfbeb304e593f090c0`**. All ten pages, all four tables and figures were read; pages5–9 were rendered and visually checked. Rotated-text extraction warnings were addressed with complementary plain extraction and visual inspection.

Local targeted filename/identity searches in isolated, primary and existing TMP evidence found no reusable manuscript. DOI web access failed with no HTTP status; the single bounded DOI curl followed one redirect to IEEE document11268874 and returned **HTTP202, zero bytes**, not a complete proceedings manuscript. One author-PDF GET returned **HTTP200**, with no redirect/retry, at **2026-10-23T03:13:17.002741+00:00 to03:13:17.989481+00:00**. Exactly **one** new complete manuscript, no alternate version, dataset, weights, supplement or repository archive. **Publisher-final byte equivalence and later corrections are unverified.** All original transport/metadata fingerprints are retained.

## Original question and exact locked policy

Original question: Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: LAID compares off-the-shelf lightweight networks under a common efficiency/performance protocol; dataset reuse is not a new dataset contribution.

Locked R2, accepted5October2026: **Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.**

R215, R574 and R400 are bounded precedents, not mechanical outcomes. No new data, evaluation library or newly learned architecture is a mandatory condition. Routine method validation alone would not suffice.

## Contribution and evaluated protocol

LAID explicitly sets a reusable **accuracy/scalability comparative framework**, selecting existing lightweight CNNs and transformer/hybrid architectures. It specifies resource eligibility, ImageNet-derived ranking, initialization, common training, spatial and spectral input conditions, five perturbation families and multiple accuracy/resource metrics. This product can compare future architectures without dependence on one bespoke learned model; the efficiency score and simple spatial/spectral pipeline are also method components, which remain labeled method.

The paper’s §IV-A eligibility is **parameters<10M OR FLOPs<1G**, while §V-C and TableI describe both constraints; all ten selected entries satisfy both, but the candidate-universe wording is not silently repaired. Equation1 defines `E=.5*(AccTop1/maxAcc)+.25*(minFLOPs/FLOPs)+.25*(minParams/Params)`. One variant per parent architecture is selected, top10 after deduplication; two published detector baselines are exceptions to constraints.

GenImage is reused, with approximately1.33M real and1.35M fake images from **SD1.4, SD1.5, Midjourney, ADM, GLIDE, Wukong, VQDM and BigGAN**. The paper halves GenImage’s original test pool into validation/test and samples **100,000 train /16,000 validation /16,000 test** across class-generator pairs. The stated training example is6,250 of each class per generator. Equal16-stratum sampling implies50,000/50,000 train and8,000/8,000 val/test, but exact asset counts, IDs, seeds and content/source disjointness are unverified. All8 generators are sampled; **cross-generator holdout and cross-dataset generalization are future work, not evaluated here**.

Two independent architecturally identical detectors are trained on raw spatial images and zero-centered2D FFT plots. Paper preprocessing is normalize[0,255], resize256×256 and store tensors. Common paper training is ImageNet1K initialization, except random Ladevic and mixed pretrained/random SpottingDiffusion; BCE, Adam, lr1e-4, weight decay0,100epochs maximum, ReduceLROnPlateau(patience5,factor.1), AMP, batch512, early stopping after10epochs without validation-accuracy gain, best-accuracy checkpoint. No training or inference was run by this review.

Generic stochastic “adversarial” degradations are crop5–20% thenresize, Gaussian blur kernel{3,5,7,9} andsigma{1,2,3,4}, Gaussian noise **variance5–20 as printed**, JPEG quality25–90, and compound application of each transformation with50% probability. They are synthetic social-media approximations, not measured upload roundtrips or adaptive attacks. Shared realizations across models, order, seeds and trial uncertainty remain unverified.

Clean metrics are accuracy%,F1,AUROC; robustness TableIII gives attack accuracy. Resource proxies are parameters/GFLOPs andaccuracy perMparameter/MFLOP, not certified latency, energy, peak-memory or platform throughput. Reported environment: NVIDIA A100, Intel Xeon Platinum8362,128GB,Python3.12.4,PyTorch2.1.2,CUDA12.1. Exact library/run configurations are incomplete.

## Serious fusion and numerical counterevidence

**Fusion accuracy is oracle correctness union, not a deployable fusion prediction.** On p5, §V-D counts a sample successful when `(yp=G) OR (yf=G)`. Pinned author `test.py` lines271–277 explicitly uses `correct=(img_preds[i]==labels[i]) or (freq_preds[i]==labels[i])`. It separately uses max fake probability for F1/AUROC. The TableIII fusion accuracies therefore cannot establish deployable decision-level-fusion robustness. The manuscript also prints `Mp` for spectral predictions in Equations4–5 despite distinct `Mf` elsewhere. The read-only code uses separate spectral_model, but does not erase the printed notation or oracle issue.

MnasNet fails at **78.11% spatial /50.36% spectral**. Spectral perturbation results are near chance, e.g. FastViT compression49.50 andMobileNetV3 compression49.88; fusion blur remains around53–57, not broad robustness. Spatial MobileNetV3 compression84.09 versusMobileViT65.06 illustrates architecture-dependent degradation. FastViT clean spectral99.91 does not certify cross-generator generalization or attacked performance. Figure4 omits MnasNet and both baselines; reportedR² are.27 parameters,.33FLOPs,.55E, with **negative E–accuracy relation**, qualifying the ranking’s efficacy. The paper’s §VI-D sentence repeats spatial where a spectral comparison appears intended; retain the source wording rather than silently repair it.

TableI pretrained catalog parameters/GFLOPs and TableIV efficiency ratios have different apparent denominators. Current code replaces binary heads and profiles one actual input viaTHOP, a plausible explanation for part of the difference, **not verification of historical counts or a FLOP/MAC convention**. Preserve both tables. No source numeric value is changed to force agreement.

## Release and paper/code boundary

Author-linked [repository](https://github.com/nchivar/LAID), pinned **`9bd6f07db6c220e53d4f2e07ea00bbda761874e3`**, commit **2025-12-01T05:05:43Z**, was inspected through six bounded read-only API requests: repository metadata, commit, recursive tree, README and individual train.py/test.py bodies. No clone/archive, helper body, dataset or weights was downloaded; no source code was executed.

README and tree provide an implementation entry point, model choices, saved-sampling arguments and test script. Tree lists dataset generation/attack/load helpers and two baseline modules, but **no frozen split-list file, requirements lock or LICENSE file**. GitHub license metadata is null; public visibility does not establish licensing. The advertised weights link was not followed.

Pinned code materially differs from the paper: **CrossEntropyLoss instead of BCE**, minimum **validation-loss** checkpointing/early stopping instead of validation-accuracy selection, defaults **batch64 /validation12,500** rather than paper512/16,000 (arguments can override, exact paper command not archived). Its resource output is **Acc/GFLOP**, while TableIV labels Acc/MFLOP. Code inspection corroborates implementation presence and oracle fusion, not a paper-faithful rerun or complete reproducible release. Exact split membership, stochastic pairing and helper behavior remain uncertified.

## R2 finding and competing interpretation

**Addition supported, medium confidence:** independent comparative intent is established by the actual framework objective, interchangeable subjects, shared training/evaluation axes, explicit constraints and public recipe structure, not by title, abstract, word “benchmark,” table size or number of generators. Existing data reuse does not defeat the systematic-comparative-framework limb of R2. The defective fusion statistic and reproduction limitations qualify numerical validity and deployment claims; they do not eliminate the independently specified clean and single-domain comparison framework.

A conservative alternative is that efficiency ranking and one-dataset comparisons are method-selection experiments without a separate sufficiently stable benchmark. This competing interpretation remains material for maintainer adjudication. R215’s VFM decision is not mechanically transferred; R574’s open-set splits andR400’s cross-domain setting are examples of independently intended protocols, not mandatory novelty templates. **No authoritative review closes here.**

## Sixteen required questions


1. **Which lightweight architectures were compared?** Ten selected off-the-shelf architectures plus two existing lightweight detection baselines are evaluated: ShuffleNet, EdgeNeXt, MobileNetV3, MobileViT, MobileViTV2, MnasNet, SqueezeNet, MobileNetV2, FastViT, RegNet, Ladevic et al. and SpottingDiffusion. Initialization variants are preserved in Table I. Source: §V-C,pp5–8,TablesI–IV.

2. **Parameter counts and computational costs?** Table I reports 1.2–4.3 million pretrained parameters and 0.04–0.70 GFLOPs for the ten selections. The two exception baselines are described as 13.46 GFLOPs (Ladevic) and 23M parameters (SpottingDiffusion). Table IV ratios use a different apparent basis; binary heads and profiling are visible in code, but exact historical reconciliation is unverified. Source: TableI,p5;TableIV/§VI-C,p8;test.py41–74,144–151.

3. **Spatial, spectral and fusion representations?** Independent architecturally identical models operate on spatial RGB and zero-centered 2D FFT plots. The paper defines fusion success as either prediction matching ground truth; current code confirms this oracle union. It is not a deployable label-fusion accuracy rule. Code max-probability F1/AUROC uses a different scoring construction. Source: §IV-A/B,p3;§V-D,p5,Eqs2–5;test.py198–277.

4. **Relationship to GenImage?** GenImage is reused, with approximately 1.33M natural and 1.35M synthetic images across eight generator sources. No new dataset classification is proposed. Source: §V-A,p4.

5. **Subset sampling and splits?** The paper halves original GenImage test data into validation/test before random class-generator subsampling: 100,000 train, 16,000 validation and 16,000 test. The training example is 6,250 per class per generator. No frozen sample IDs or seed were verified. Source: §V-A,p4;README/trainingrecipes.

6. **Balance and generator test protocol?** Intended equal class-generator sampling implies 50,000 real/50,000 fake training and 8,000/8,000 validation/test if equal sampling is followed. All eight generators are represented; no generator holdout or cross-dataset evaluation is established. Asset-level balance and duplicate/content overlap are unverified. Source: §V-A,p4;§VII,p9.

7. **Standardized recipes?** A common stated training recipe exists, with initialization exceptions for the two prior baselines. Pinned code instead uses CrossEntropyLoss, checkpointing/early stopping on validation loss, and default batch/validation counts of 64/12,500 rather than the paper’s BCE, accuracy-based selection and 512/16,000. These differences limit exact reproducibility. Source: §IV-C,pp3–4;train.py44–52,331–359,381–395.

8. **Accuracy, efficiency, robustness metrics?** Clean accuracy, F1 and AUROC; five attack-family accuracies; parameter/GFLOP counts, accuracy per Mparameter/MFLOP, ImageNet-derived efficiency selection and R-squared plots are supplied. End-to-end latency, energy and production throughput are not demonstrated. Source: §V-F/G,p6;TablesII–IV,pp6–8;Figure4,p9.

9. **Operating/resource constraints reproducible?** Explicit resource limits, initialization variants, input size, hardware and some software versions enable partial reproduction. Eligibility OR versus AND language, catalog versus profiled resource denominators, FLOP/MAC conventions and unpinned library/run details remain unresolved. Source: §IV-A,p3;TableI,p5;§V-G,p6.

10. **Robustness perturbations controlled and consistent?** Crop, Gaussian blur, Gaussian noise, JPEG and compound degradations have bounded ranges. Exact shared random draws, sequence ordering and seeds across all architectures are not verified. These are synthetic generic degradations rather than measured platform uploads or adaptive gradient attacks. Fusion is an oracle statistic. Source: §V-D/E,pp5–6;test.py209–277.

11. **Independently reusable framework?** The independently intended contribution is an accuracy-scalability comparison framework with eligibility/ranking rules, common data/training recipe, spatial/spectral/perturbation axes and multiple efficiency/accuracy metrics, backed by public train/test recipes. It can compare detectors beyond a single new model; numerical and fusion-validity limitations remain. Source: §I,p1;§IV–V,pp3–6;README/test/train.

12. **Comparisons merely method selection?** The competing reading is a model-selection study using an efficiency score and a simple detection pipeline on one reused dataset. Against this, the stated end product and actual experiments systematically compare twelve existing architectures rather than validate only one bespoke learned detector. Reuse does not depend on a particular LAID architecture. Source: §I/IV/V-C;§VI-D,p8.

13. **New technical components?** An efficiency-based selection score and combined spatial/spectral evaluation harness are technical components. The networks, pretrained initialization, FFT and baselines are established. R2 does not require a new network, new images or a separately packaged evaluation library; method is retained without re-review. Source: §I,p1;§IV,p3;§V-C,p5.

14. **Scripts, splits, baseline settings released?** The pinned author repository contains train.py/test.py, README and listed data/baseline helpers. Two recipe bodies were inspected without execution. No frozen split lists, package lock or license file is listed. A weights link is advertised but not retrieved; script availability does not certify a complete reproducible release. Source: PinnedGitHubtree/READMEandtrain/testbodiesobserved23October2026.

15. **Contradictory findings?** Contradictions and limits include MnasNet failure, spectral collapse under perturbations, oracle fusion accuracy, weak blur robustness, negative efficiency-score correlation, inconsistent parameter/FLOP bases, eligibility wording, BCE/CE and checkpoint differences, and the paper’s Mp spectral notation and spatial-versus-spatial sentence. Printed values are preserved. Source: TablesII–IV;§V-D,p5;§VI,p6–8;code.

16. **Future detectors independently evaluable?** Future detectors can be inserted into the specified common comparative axes and public recipe structure, supporting an independently reusable framework under R2. Exact paper replication and deployable fusion are not certified. The provisional addition carries medium confidence and requires maintainer acceptance. Source: §IV–V;README/train/test;R2.

## Full printed table transcription

| Model | rank | original_filtered_variant_rank | ImageNet_top1_accuracy_percent | pretrained_parameters_millions | GFLOPs_per_sample | selection_efficiency_score_E |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ShuffleNet | 1 | 1 | 60.55 | 1.4 | 0.04 | 0.806 |
| EdgeNeXt | 2 | 2 | 71.20 | 1.3 | 0.26 | 0.671 |
| MobileNetV3 | 3 | 3 | 67.67 | 2.5 | 0.06 | 0.669 |
| MobileViT | 4 | 4 | 69.00 | 1.3 | 0.40 | 0.645 |
| MobileViTV2 | 5 | 5 | 70.20 | 1.4 | 0.50 | 0.631 |
| MnasNet | 6 | 6 | 67.73 | 2.2 | 0.10 | 0.619 |
| SqueezeNet | 7 | 8 | 58.18 | 1.2 | 0.35 | 0.607 |
| MobileNetV2 | 8 | 16 | 72.15 | 3.5 | 0.30 | 0.526 |
| FastViT | 9 | 19 | 75.60 | 3.6 | 0.70 | 0.524 |
| RegNet | 10 | 20 | 75.80 | 4.3 | 0.40 | 0.523 |

| Model | spatial_accuracy_percent | spatial_F1 | spatial_AUROC | spectral_accuracy_percent | spectral_F1 | spectral_AUROC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ShuffleNet | 92.40 | 0.9229 | 0.9782 | 99.44 | 0.9944 | 0.9983 |
| EdgeNeXt | 95.64 | 0.9563 | 0.9916 | 99.77 | 0.9977 | 0.9999 |
| MobileNetV3 | 95.19 | 0.9523 | 0.9911 | 99.67 | 0.9968 | 0.9995 |
| MobileViT | 97.17 | 0.9716 | 0.9943 | 99.89 | 0.9989 | 0.9999 |
| MobileViTV2 | 97.01 | 0.9700 | 0.9962 | 99.50 | 0.9950 | 0.9997 |
| MnasNet | 78.11 | 0.7837 | 0.8642 | 50.36 | 0.6631 | 0.6892 |
| SqueezeNet | 92.47 | 0.9245 | 0.9796 | 99.37 | 0.9937 | 0.9996 |
| MobileNetV2 | 97.86 | 0.9786 | 0.9976 | 99.55 | 0.9955 | 0.9997 |
| FastViT | 98.87 | 0.9887 | 0.9989 | 99.91 | 0.9991 | 0.9999 |
| RegNet | 97.98 | 0.9798 | 0.9973 | 99.89 | 0.9989 | 1.000 |
| Ladevic et al. | 99.22 | 0.9923 | 0.9993 | 99.79 | 0.9979 | 0.9998 |
| SpottingDiffusion | 98.74 | 0.9874 | 0.9982 | 99.61 | 0.9961 | 0.9997 |


### TableIII — spatial

| Model | crop_accuracy_percent | blur_accuracy_percent | noise_accuracy_percent | compression_accuracy_percent | combined_accuracy_percent |
| --- | ---: | ---: | ---: | ---: | ---: |
| ShuffleNet | 80.50 | 52.66 | 79.38 | 82.31 | 68.16 |
| EdgeNeXt | 80.41 | 53.09 | 77.47 | 78.69 | 67.72 |
| MobileNetV3 | 82.84 | 55.62 | 83.41 | 84.09 | 73.44 |
| MobileViT | 81.50 | 52.12 | 78.75 | 65.06 | 63.53 |
| MobileViTV2 | 82.81 | 52.44 | 80.09 | 62.47 | 64.97 |
| MnasNet | 69.25 | 51.66 | 76.16 | 74.75 | 61.41 |
| SqueezeNet | 79.84 | 54.22 | 81.91 | 81.94 | 68.94 |
| MobileNetV2 | 84.03 | 52.72 | 77.44 | 58.44 | 63.56 |
| FastViT | 88.75 | 55.47 | 82.44 | 60.94 | 65.09 |
| RegNet | 83.41 | 52.94 | 87.09 | 63.44 | 65.66 |
| Ladevic et al. | 80.78 | 51.03 | 82.54 | 54.59 | 59.59 |
| SpottingDiffusion | 86.12 | 52.78 | 79.16 | 58.81 | 62.59 |

### TableIII — spectral

| Model | crop_accuracy_percent | blur_accuracy_percent | noise_accuracy_percent | compression_accuracy_percent | combined_accuracy_percent |
| --- | ---: | ---: | ---: | ---: | ---: |
| ShuffleNet | 50.16 | 50.09 | 49.97 | 50.03 | 50.12 |
| EdgeNeXt | 50.09 | 50.09 | 50.00 | 49.97 | 50.06 |
| MobileNetV3 | 50.38 | 50.03 | 50.00 | 49.88 | 50.00 |
| MobileViT | 50.03 | 50.03 | 50.00 | 49.97 | 50.06 |
| MobileViTV2 | 50.00 | 50.00 | 50.00 | 49.84 | 49.94 |
| MnasNet | 46.88 | 49.81 | 49.41 | 50.00 | 49.81 |
| SqueezeNet | 50.06 | 50.00 | 50.00 | 49.78 | 49.94 |
| MobileNetV2 | 50.81 | 50.28 | 50.00 | 49.84 | 50.03 |
| FastViT | 51.06 | 51.06 | 50.00 | 49.50 | 50.22 |
| RegNet | 50.06 | 50.00 | 50.12 | 50.12 | 49.91 |
| Ladevic et al. | 50.00 | 50.19 | 50.00 | 49.91 | 50.00 |
| SpottingDiffusion | 50.09 | 50.00 | 50.00 | 50.06 | 50.03 |

### TableIII — fusion_oracle_correctness_union

| Model | crop_accuracy_percent | blur_accuracy_percent | noise_accuracy_percent | compression_accuracy_percent | combined_accuracy_percent |
| --- | ---: | ---: | ---: | ---: | ---: |
| ShuffleNet | 85.88 | 53.09 | 96.62 | 95.91 | 84.25 |
| EdgeNeXt | 86.47 | 53.97 | 99.31 | 96.78 | 88.50 |
| MobileNetV3 | 87.38 | 56.09 | 97.50 | 93.88 | 83.19 |
| MobileViT | 87.59 | 53.22 | 99.25 | 99.50 | 89.97 |
| MobileViTV2 | 87.16 | 53.00 | 96.94 | 99.34 | 89.28 |
| MnasNet | 75.31 | 57.47 | 91.75 | 84.28 | 68.44 |
| SqueezeNet | 85.81 | 55.03 | 97.22 | 96.66 | 84.34 |
| MobileNetV2 | 87.41 | 53.66 | 98.97 | 99.09 | 90.66 |
| FastViT | 92.56 | 56.50 | 98.31 | 98.34 | 90.91 |
| RegNet | 86.19 | 53.06 | 99.81 | 99.59 | 88.53 |
| Ladevic et al. | 98.38 | 55.84 | 98.59 | 99.19 | 90.50 |
| SpottingDiffusion | 89.62 | 53.69 | 99.72 | 99.66 | 91.19 |

| Model | spatial_accuracy_percent_per_million_parameter | spatial_accuracy_percent_per_MFLOP | spectral_accuracy_percent_per_million_parameter | spectral_accuracy_percent_per_MFLOP |
| --- | ---: | ---: | ---: | ---: |
| ShuffleNet | 268.72 | 1.62 | 289.21 | 1.75 |
| EdgeNeXt | 82.66 | 0.37 | 86.23 | 0.39 |
| MobileNetV3 | 62.62 | 1.19 | 65.58 | 1.25 |
| MobileViT | 102.55 | 0.29 | 105.42 | 0.30 |
| MobileViTV2 | 88.03 | 0.21 | 90.29 | 0.21 |
| MnasNet | 83.09 | 0.52 | 53.57 | 0.33 |
| SqueezeNet | 127.80 | 0.27 | 137.34 | 0.29 |
| MobileNetV2 | 43.96 | 0.23 | 44.72 | 0.23 |
| FastViT | 30.54 | 0.14 | 30.87 | 0.14 |
| RegNet | 25.10 | 0.18 | 25.58 | 0.18 |
| Ladevic et al. | 20.44 | 0.01 | 20.56 | 0.01 |
| SpottingDiffusion | 4.26 | 0.22 | 4.29 | 0.22 |

Exactly360 scalar numeric table cells are transcribed across TablesI–IV (including both TableIrank columns). These are source observations, not numerical reproduction. Full source provenance, access failures and bounded metadata receipts are in source_manifest.json. Repository writes, decisions, exports, full-suite runs, commits and pushes by this worker: zero.

## Interruption recovery — ten exact fusion implementation questions

Existing source-code and manuscript verification were recovered without any additional network request or download. The previous draft remains preserved byte-for-byte in an operational backup; no root notes were overwritten. The following extends the review, leaving its16 original framework questions and360 printed table cells intact.

1. **Actual spatial-model prediction output?** test_attacked receives perturbed spatial tensors and computes img_outputs=spatial_model(img_images), followed by img_preds=argmax(img_outputs,dim=1) and softmax fake probability. The two output logits correspond to natural/synthetic binary labels; no generator identity is predicted. Source: test.py198–233, especially225–231.

2. **Actual spectral-model prediction output?** The same perturbed spatial tensors are converted to NumPy, passed through the listed FFT conversion helpers, stacked and sent to spectral_model. freq_preds is argmax and freq_probs is softmax fake probability. Separate models are used in code, unlike the paper’s Mp notation in spectral Equations4–5. Source: test.py209–233, especially213–219 and227–233.

3. **Is a joint or fused class prediction constructed??** No joint fused class variable or learned fused classifier is constructed in the inspected attack routine. fusion_prob is maximum of the two fake probabilities and is stored for F1/AUROC; fused accuracy is accumulated separately from an OR of correctness indicators. The scoring value is not itself a selected class in this routine. Source: test.py271–277 and300–305.

4. **Does fusion require ground truth??** The published fusion accuracy explicitly references labels[i] in correct=(img_preds[i]==labels[i]) or (freq_preds[i]==labels[i]). This statistic depends on ground truth to decide correctness and cannot choose the correct model’s predicted class at inference without an independent decision rule. The maximum fake-probability score itself does not reference labels. Source: test.py272–275.

5. **Oracle upper bound or practical classifier??** The accuracy is an oracle correctness-union upper bound on choosing between two predictions for each labelled example. This can validly quantify error complementarity as an explicitly identified oracle statistic. The manuscript calls it decision-level fusion and uses it to support deployable robustness, without identifying an oracle upper bound; therefore those deployment interpretations are unsupported by this statistic. This does not invalidate all clean or single-domain results. Source: Paper§V-D,p5;§VI-B.3,p7;§VII,p8;test.py272–274.

6. **What inference-time combination is implemented??** The routine computes a maximum fake-probability score for separate F1/AUROC accounting. It does not implement an OR or AND over predicted class labels, voting, probability averaging, confidence-based model selection or a learned fusion module for its reported fusion accuracy. BinaryF1Score is instantiated without an explicit threshold; the exact external-library default is not independently pinned here. Source: test.py201–202,272–277,300–305.

7. **Do evaluation success and inference scores differ??** Yes. fusion_acc uses label-dependent OR-correctness, whereas fusion_f1 and fusion_auc consume the maximum probability score with ground-truth targets through metric objects. They measure different constructions, so fusion accuracy is not shown to be the accuracy of the maximum-probability predictor. TableIII reports only the former accuracy statistic. Source: test.py300–310;TableIII,p7.

8. **Do Table III Fusion results correspond to executable code??** The read-only pinned test.py implements exactly the paper’s OR-correctness rule and prints fusion accuracy by attack, conceptually corresponding to TableIII. This is source-code verification, not an execution or numeric reproduction. No run receipt, paper-time checkpoint or exact paper source commit binds the printed values to this later repository snapshot. FastViT combined65.09% is spatial accuracy;90.91% is the printed oracle-union fusion accuracy. Source: test.py271–274,300–310;TableIII,p7;repositorycommit9bd6f07d dated1December2025.

9. **Required checkpoints and inference settings available??** README advertises an optional Google Drive weights link, but no weights were retrieved. The pinned tree contains no checkpoint blobs. test.py loads model_state_dict from .pth files, matches model names in filenames, and seeks paired <model>_img_checkpoint.pth/<model>_freq_checkpoint.pth. Required exact model weights, hashes, training sampling and attack helper details remain unverified. Public script presence does not certify executable paper reproduction. Source: READMEsetup;test.py40–83,317–359;recursivepinnedtree.

10. **Can the evaluation protocol reproduce without label-dependent selection??** The clean and single-domain evaluation structure is conventional labelled evaluation and can define ground-truth-free predictions before scoring. The published fusion-accuracy statistic intrinsically uses label-dependent selection; its oracle upper-bound measurement can be repeated on labelled data, but a deployable fusion predictor cannot be recovered from that success criterion alone. The existing max-probability score could be evaluated as a separate predictor, but its accuracy is not the printed oracle statistic and no remediation or rerun is authorized. Source: test.py154–171,271–277,300–310;Paper§V-D,p5.

A valid oracle upper-bound interpretation must be distinguished from the manuscript’s deployable fusion claims. The OR-correctness measure can describe complementary errors on labelled data, but supplies no ground-truth-free class choice. Current code also produces a separate maximum fake-probability score; its inference accuracy was not independently established by this review. No code repair, method implementation, taxonomy change or authoritative closure is performed.
