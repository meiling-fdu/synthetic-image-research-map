# Batch B Wave B1H — R566 corrected; R267 deferred

Maintainer-approved adjudication of the existing **2026-10-19** evidence packet. Scientific review occurred on 2026-10-19; the narrow correction was applied at **2026-10-20T14:28:30Z**. Baseline `445b4f8cc7257b3c87868a666bce43d8c20bda0d` was fetched and verified before applying it. No manuscript retrieval, task adjudication, bibliography remediation or other review wave was repeated.

| Action | Accepted disposition | Current research types | Administrative result |
|---|---|---|---|
| R566 | `PROPOSE_CORRECTION_ACCEPTED` | `analysis_study` | `method` replaced; exactly one terminal decision appended |
| R267 | `EVIDENCE_STILL_INSUFFICIENT` | `method` | Original review remains pending; all14 scientific questions remain unverified |

R566 terminal decision: **`review:7ab9cfc3833aad630f20`**, established queue `other`, action `no_action_after_review`. It records the already applied correction, not a second requested action. Registry rows 86 → 87; every earlier byte remains intact. Both papers retain `detection` and `fully_generated`. Canonical authors, affiliations, DOI/arXiv, publication metadata and institution relationships are unchanged. The canonical CVPR-main/workshop metadata discrepancy is preserved without remediation.

## Accepted scientific judgment

The complete official CVF accepted-version manuscript (10 pages, printed 973–982; SHA256 `5b22d59439f359102c3a73d35018aa1b022704ba41ef83dc521d9dae86d32b6f`) makes systematic forensic characterization its primary contribution. Section 4/Table 1 covers 15 model entries and source averages over 1000 images using an existing denoiser; Figure 3 studies upsampling factors 4/8; Figure 4 uses resize 2.0/1.4/0.7 and JPEG99/95/75; Figures6–7 use 128 radial steps,16 angular steps and cutoff0.1. These are analysis settings and findings, not detector performance scores.

Under locked R3, the original empirical findings substantiate `analysis_study`. Under R4, established measurement tools, existing denoising and reproducible equations do not by themselves substantiate an independently validated novel algorithm. Section5 locates detector design in future work. Therefore `method` is removed. The complete original science, contrary evidence, control limitations and version boundaries are preserved below and in the manifest. IEEE-final and arXiv equivalence remain unverified. R267's inaccessible full text is not replaced by abstract-based inference.

## Exact authoritative and public-data changes

`data/curated/papers.csv`: one R566 compatibility cell (`research_types`). `data/curated/paper_taxonomy.csv`: R566 research types plus five directly required research-review provenance/date fields; seven existing CSV cells in total. Existing reviewed statuses and canonical timestamps remain unchanged. The taxonomy audit date remains the scientific-review date, 2026-10-19; the terminal decision records the actual application timestamp above.

The established offline refresh regenerated outputs without manual JSON edits. Exactly one public paper record and its two pre-existing Naples/NVIDIA map records change, limited to `research_types` and `taxonomy_review.research_types.reason`. All673 other public papers and all1408 other map records are semantically identical. All1410 relationship identities are preserved. Nonrecord changes are the synchronized snapshot timestamp, the same timestamp in the preview report, and the key-coverage input fingerprint. Coverage/mapping report rows and legacy generated CSVs remain identical.

## Current corpus and review accounting

| Measure | Recomputed current value |
|---|---:|
|Public / formal / mapped / unmapped|674 /557 /613 /61|
|Relationship rows / unique pairs|1410 /1410|
|Detection / source attribution / localization|621 /84 /45|
|Method / dataset / benchmark / survey / analysis study|578 /134 /90 /21 /82|
|Original Batch B actions / historical papers|159 /148|
|Historical unresolved / active-public unresolved / affected public papers|147 /145 /134|

Only R566 closes. Distinct affected papers were recomputed from the original action ledger and current public identities: R566 has no other pending original Batch B action. R267, T046, T093, T608 and T526/P526 remain independently pending. The same13 Batch C debts and separate39-paper import inventory (including14 overlapping taxonomy debts and12 held candidates) are unchanged and are not combined with original Batch B action accounting.

## Preservation and validation

The original evidence packet passed68 lightweight checks. Its exact manifest/report bytes are preserved as authenticated gzip/base64 archives in the existing manifest, with original source fingerprints and all retrieval history retained. The fresh baseline covers4470 tracked files,4414 primary tracked files and its full HEAD/index/status,14 earlier Batch B artifacts, protected128/original130 primary files,49 frozen NeurIPS artifacts in each checkout and119 ignored operational inputs. All117 historical fixture inputs were already authenticated; no restoration or replacement was needed.

Four narrow test files require current/historical boundary updates: current research totals change to578/82; exact earlier B1E/B1F/B1G transactions remain at their actual published endpoints with their original counts/hashes. Live selected-case, prior-decision-prefix, relationship and current-total guards remain. New B1H regressions enforce the complete exact successor delta. No frozen historical receipt, expected historical value or fixture is rewritten.

<!-- B1H_ADJUDICATION_VALIDATION_START -->
**Focused validation passed: 352 ordinary tests and 12 subtests**, including all 21 new B1H regression cases; zero failures/errors/skips. All four current-scope validators passed with zero errors. Existing warnings remain visible: curated 294; public map 0/paper preview 62; exclusions 2; key coverage 0.

**The complete repository suite ran once and passed 2005 ordinary tests and 389 subtests**; zero failures/errors/skips. The two existing legacy test return-value warnings remain unchanged. Python 3.14.7, pytest 9.1.1, pytest-subtests 0.15.0 and Node 24.19.0 were used with the documented offline fixtures and localhost permission. Its input/output inventory remained byte-identical after completion.

After that successful full suite, **two sequential offline export verification passes passed**, with all 4592 compared paths, seven deterministic outputs and 119 operational inputs byte-identical. Read-only fixture checks before/after verified 117 inputs, creating/replacing none. There was one initial correction export plus exactly two verification exports, with no concurrent exporter. `EXPORT_REPRODUCIBLE = 1`.

The measured semantic/preservation gate passed 60/60 checks. The exact R566-only public delta, all other paper/relationship identities, complete prior decision prefix, R267 deferral, original archives and protected inventories remain proven. The original evidence-only 68-check receipt remains separately preserved.

`FOCUSED_FAILURES = 0`

`VALIDATOR_ERRORS = 0`

`FULL_SUITE_FAILURES = 0`

`EXPORT_REPRODUCIBLE = 1`

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

Test/export completion receipts are recorded after their successful runs. Scientific data, code and original evidence remain the exact validated bytes; only this report and manifest's receipt fields are finalized afterward. A final read-only integrity check verifies the final artifacts before staging. No commit or future push is claimed by these pre-publication receipts.
<!-- B1H_ADJUDICATION_VALIDATION_END -->

## Preserved evidence-only scientific findings

The following sections are the original 2026-10-19 evidence-stage record, preserved verbatim. Their provisional language and then-current `method` snapshots are historical observations. The accepted correction and current administrative state are stated above. R267 remains unchanged; R566's scientific rationale and limitations remain valid. The original report's complete bytes, including its prior accounting/validation/Git observations, are also archived in the manifest.

## Locked policy

**R1 (ACCEPT, 2026-10-05)**: Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.

**R2 (ACCEPT, 2026-10-05)**: Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

**R3 (ACCEPT, 2026-10-05)**: Assign analysis_study only when systematic empirical or theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps, or supporting interpretability figures do not qualify by themselves.

**R4 (ACCEPT, 2026-10-05)**: Assign method only when the paper contributes substantive technical novelty: a method, algorithm, model, procedure, or system. Pure surveys, benchmarks, datasets, or analysis studies do not gain method merely because they implement baselines. Multiple legitimate research-type roles remain allowed.

The method question is governed by R4 and the analysis question by R3. They are independent; an analysis-led paper may also retain method if its algorithmic contribution is substantive. R1/R2 prevent routine experimental sampling and large tables from creating dataset/benchmark roles. No dataset, benchmark or survey addition is proposed. Any genuinely separate resource question would require a new review action.

## R267: quality versus detectability

**Canonical identity:** `curated:7693a9c0107feaf90e10`; *Are High-Quality AI-Generated Images More Difficult for Models to Detect?*; ICML 2025. Current taxonomy is `detection` / `fully_generated` / `method`.

**Exact original review question:** Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: The work systematically analyzes the counterintuitive relation between image quality and detectability.

The historical action is `LIKELY_FIX`, proposing `method;analysis_study` from the current `method`; its confidence and abstract basis are historical audit observations, not accepted evidence. Current canonical and public records are recovered verbatim in the manifest.

### Identity and access

The [official PMLR record](https://proceedings.mlr.press/v267/xiao25g.html) verifies the exact title, ICML 2025, PMLR volume 267, pages 68491–68512, and ten ordered authors: Yao Xiao, Binbin Yang, Weiyan Chen, Jiahao Chen, Zijie Cao, Ziyi Dong, Xiangyang Ji, Liang Lin, Wei Ke and Pengxu Wei. The canonical string contains both `Yao Xiao` and `Yao_Xiao`; this pre-existing discrepancy and spelling differences are recorded without merging or correcting authors. No canonical DOI/arXiv identifier is invented.

The official page links the [publisher PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/xiao25g/xiao25g.pdf). No complete manuscript was obtained:

| Operation | Actual result | Scientific coverage |
|---|---|---|
| Initial sandbox PDF transport | DNS failure before HTTP; zero response bytes | None |
| Same URL with network permission, no automatic retry, 120-second bound | HTTP 200 declared 13,757,845 bytes; timed out after 10,759 bytes; no PDF EOF | Incomplete response, not used as manuscript evidence |
| Same official URL through PDF parser | Unsupported `application/octet-stream` response, tool error 400 | No PDF pages/text |
| HEAD-only derived PMLR static asset route | HTTP 404, HTML; no body requested | None |
| Final [canonical OpenReview PDF](https://openreview.net/pdf?id=sKYdVKE1tS) fallback | Browser-verification HTML redirected to a challenge | No complete version or scientific pages |

The incomplete payload SHA256 is `4ad66065c072261994deb0437b0266b47de8967fd626052138c66cc4d19e8c1d`; it is explicitly **not** the full-paper hash. The publisher's inclusive 22-page bibliographic span does not mean 22 pages were retrieved or read. **Complete manuscripts: 0; scientific pages read: 0.** OpenReview version identity/content equivalence could not be verified. Requests stopped after the final fallback.

### Contributions: author claims versus verified evidence

The PMLR abstract advertises a counterintuitive quality–detectability association, prompt-length associations, clustering/regression involving saturation, contrast and texture, and regression-guided patch selection for existing detectors. These are author claims only. They are not substituted for contribution-level methods or evaluation evidence, and no causal inference is made.

All fourteen requested checks are explicitly `UNVERIFIED` in the manifest: hypotheses; quality/preference scores; generators/datasets/sampling; detector protocols; stratified quality results; prompt/content confounding; clustering/correlation/regression details; statistical controls; generalization; concrete patch-selection inputs/outputs/rules; technical novelty; baseline-controlled numerical improvement; frozen-detector versus regression-training requirements; and independent dataset/benchmark roles. No section, figure, result table, effect size, regression coefficient, detector score or improvement is invented.

**Provisional disposition:** `EVIDENCE_STILL_INSUFFICIENT`. The scientific final research-type set remains `null`; current `method` is administratively preserved, not newly validated or rejected. Whether to add `analysis_study`, and whether method is independently substantive, remain unresolved. Access failure is not negative evidence about either contribution. Confidence is high in identity recovery and the documented access limitation; no full-text classification confidence is claimed. A complete identity-matched primary manuscript with contributions, methods, evaluation and relevant bundled appendix is still required. No remediation is proposed or applied.

## R566: synthetic-image properties across generator families

**Canonical identity:** `curated:67d37f98e44fa9d7d06e`; *Intriguing Properties of Synthetic Images: From Generative Adversarial Networks to Diffusion Models*; Riccardo Corvi, Davide Cozzolino, Giovanni Poggi, Koki Nagano and Luisa Verdoliva; DOI `10.1109/cvprw59228.2023.00104`; stored arXiv identifier `2304.06408`. Current taxonomy is `detection` / `fully_generated` / `method`.

**Exact original review question:** Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: The main work is a systematic cross-family study of Fourier, autocorrelation, bias and spectral-power properties.

The historical `LIKELY_FIX` action proposes `method;analysis_study`; the independent method assessment here is explicitly provisional and awaits maintainer adjudication.

### Primary version and coverage

The [official CVF record](https://openaccess.thecvf.com/content/CVPR2023W/WMF/html/Corvi_Intriguing_Properties_of_Synthetic_Images_From_Generative_Adversarial_Networks_to_CVPRW_2023_paper.html) identifies CVPR Workshops 2023, pages 973–982, and links the [reviewed PDF](https://openaccess.thecvf.com/content/CVPR2023W/WMF/papers/Corvi_Intriguing_Properties_of_Synthetic_Images_From_Generative_Adversarial_Networks_to_CVPRW_2023_paper.pdf).

The complete file is **2,097,562 bytes / 10 PDF pages**, SHA256 `5b22d59439f359102c3a73d35018aa1b022704ba41ef83dc521d9dae86d32b6f`. All ten pages were reviewed; pages 1–8 contain the main paper and 9–10 references. Figures/tables were visually checked, including an independent check of pages 4–8. This is the CVF open-access accepted-paper version. Its watermark describes accepted-version correspondence; neither IEEE final bytes nor an arXiv version was separately retrieved or compared. The existing canonical CVPR-main venue label is preserved and not silently reconciled with the workshop source during this research-type action.

Two metadata web accesses returned 403; a sandbox HTML request failed before HTTP, then the official HTML was saved successfully. The first PDF GET returned HTTP 200 but timed out at 1,190,618 of 2,097,562 bytes. One bounded Range continuation returned HTTP 206 for bytes 1,190,618–2,097,561, with the same ETag and exactly 906,944 bytes. Concatenation, final byte count, PDF EOF, title/byline and all ten parsed pages were verified. This is **one complete manuscript version**, assembled from two GET responses, not two retrieved manuscripts. Original partials, headers, failures and exact response provenance are retained externally and described in the manifest.

### Analysis protocols and quantitative evidence

The introduction's contribution list (PDF pp2–3 / printed 974–975) and Section 4 identify three primary original findings: persistent architecture-related traces across generator families, transfer of training-data artifacts, and differences between real/generated spectral statistics. This is systematic source-level forensic characterization rather than a supporting ablation section.

Table 1 (p4/976) lists 15 named rows: BigGAN, StyleGAN2, StyleGAN3, StyleGAN-T and GALIP; Taming Transformers and DALL·E Mini; Score-SDE, ADM, GLIDE, DALL·E 2 and eDiff-I; Latent Diffusion, Stable Diffusion and DiT. Family groups are GAN, VQ, diffusion and latent diffusion. Training sets include ImageNet, FFHQ, LSUN and web image/text collections; variants mean 15 rows are not exactly 15 experimental sources. DALL·E 2/eDiff-I training data are explicitly unknown.

| Locator | Actual measurement or controlled parameter | Supported observation and boundary |
|---|---|---|
| Section 4, pp4–5/976–977, Eqs1–6 | `I=1000` images per source; existing Zhang denoiser, `sigma=1`; source-averaged autocorrelation and squared Fourier magnitudes normalized by average power; central `65×65` autocorrelation crop | Multi-image second-order measurements, not anecdotal single-image visualization or a new trained detector |
| Figure 3, p5/977 | Latent upsampling factors `4,4,8`; spectral peaks at multiples of `1/4` versus `1/8`, with spatial periodicities `4` versus `8` | Architecture-linked regularity; datasets/architectures also differ, so this is not a one-factor causal ablation |
| Figure 4, p6/978 | Stable Diffusion post-processing: blur/sharpen, scaling `2.0×,1.4×,0.7×`; JPEG qualities `99,95,75` | Post-processing changes or masks generation-related autocorrelation; no detector accuracy/robustness score is supplied |
| Figure 5, Section 4.2, p6/978 | ADM/Latent Diffusion compared with ImageNet and LSUN-bedroom training images; `8×8` JPEG grid and textual `Q=75` discussion | Training-data artifacts can reappear in generated images; the comparison is dataset-dependent and not universal proof about every generator |
| Figure 6, Section 4.3, Eq7, p7/979 | Radial coordinate `0–0.5` in `128` steps; focus `0.2–0.5`; average over `1000` images; ImageNet/FFHQ/LAION groups; natural-image power-law reference exponent approximately `2` | Curves show deviations from real-source spectral distributions, with FFHQ interpolation as an explicit exception/qualification |
| Figure 7, Eqs8–9, pp7–8/979–980 | `16` angular steps over `0–pi`, high-pass cutoff `0.1`; per-direction standardized real/synthetic mean differences with variance denominator, called square-root Fisher discriminant ratio | Quantitative angular/statistical separation; neither classification AUC/accuracy nor independently evaluated decision thresholds |

Equations 7–9 are preserved as printed rather than silently correcting their notation. Figures 6–7 are numerical plots, but exact per-model curve samples and statistical significance values are not tabulated. No plotted point is relabeled as an exact reported result or classifier metric. Figure 5's visible panels do not show a separate UCID control; extraneous text-extraction tokens are not treated as a plotted experiment.

### Is method independently supported?

The concrete inputs are source groups of real/generated images and their residuals; outputs are averaged autocorrelation maps, spectral densities, radial/angular profiles and standardized separation plots. The denoiser is explicitly reused. Fourier transforms, averaging, autocorrelation and Fisher-style measurements are established tools. Equations and reproducibility in outline do not independently establish new technical novelty under R4.

The complete main paper does not introduce and independently evaluate a new deployable detection algorithm, learned forensic classifier, novel representation/decision procedure, or a substantively new analytical algorithm beyond applying these measurements to modern generator families. Section 5 (p8/980) places forensic detector design in future work. No ROC/AUC/F1, detector accuracy table, learned prediction head, decision threshold or method-versus-baseline performance improvement is supplied for a proposed detector. References to existing detectors are motivation and context, not this paper's method evaluation. Its new scientific observations are substantive without automatically constituting an additional method role.

**Provisional research types: `analysis_study` only.** Add `analysis_study` under R3 and propose removing `method` under R4. Confidence is high within the complete reviewed main-paper version. This is a scientific recommendation, not an accepted correction: current `method` and `detection` remain unchanged, and R566 remains unresolved pending maintainer acceptance. No dataset/benchmark/survey role is proposed from the experimental image collections, model inventory or related-work section.

### Contradictory evidence and limits

The work does contain explicit equations and a reproducible measurement pipeline; those are positive methodological details and are not ignored merely because the title frames a study. The limiting distinction is missing independently supported substantive technical novelty, not absence of implementation. Empirical novelty is supported by the complete contribution and results sections.

Training-source matching is an author-stated design, not independently verified for every model: Table 1 marks DALL·E 2/eDiff-I training data unknown although Figure 6 includes them in a LAION comparison. Different datasets accompany Figure 3's architecture factors. Resolution, prompt selection, blur/sharpen kernels and all generation settings are not fully harmonized/specified for every source. FFHQ interpolation and JPEG/resizing confounding restrict generalization. Variance in Equation 9 is not a reported confidence interval or significance test; no p-values, uncertainty intervals or isolated causal effects are claimed. The study supports forensic understanding, not guaranteed detector generalization to arbitrary post-processed images. Current task labels are not adjudicated here.


## Retrieval and publication boundaries

Original retrieval accounting is unchanged: R267 zero complete manuscripts; R566 one complete official CVF accepted manuscript, assembled from two authenticated HTTP responses. All timeout/parser/challenge and Range-provenance records remain preserved. No source request was made during adjudication. Manuscripts, partials, renders, scripts, runtime caches and operational test/export logs remain outside Git.

This report records reviewed commit inputs. The containing commit supplies its own identity; actual post-push SHA, remote equality,0/0 synchronization and final preservation are verified separately after publication. No future push is represented as already successful.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
