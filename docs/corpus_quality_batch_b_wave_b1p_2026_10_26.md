# Batch B Wave B1P — Maintainer adjudication

R024 and R482 are accepted under locked R3 and R2 respectively. Exactly two original research-type actions close; all scientific task classifications, image scopes, bibliographic fields, institutions and relationship identities remain unchanged. T024 is neither reopened nor re-closed. No new source retrieval occurred during adjudication.

| Action | Previous types | Approved final types | Terminal decision |
|---|---|---|---|
| R024 | `method` | `method;analysis_study` | `review:d8baba67e917010328d4` |
| R482 | `method;dataset` | `method;dataset;benchmark` | `review:575332a380a54630756b` |

## Accepted scientific basis and limits

**R024 — locked R3**. R024 accepted under locked R3: formal architecture-level source-homology definitions and a primary systematic investigation of embedding interaction strategies, transfer from detection and attribution representations, nominal GAN/diffusion source generalization, pairwise protocols and perturbation/augmentation behavior remain informative independently of one particular Siamese model. This is not classified from routine ablations or first-study wording alone. Add analysis_study; retain method, source_attribution and fully_generated. Pairwise same-source verification is not single-image authenticity detection; preserve the completed T024 resolution without another task decision. Architecture-level labels do not establish exact checkpoint, trained-instance, lineage, content/prompt or operator identity. Exact source/image separation, semantic independence and shared-image leakage remain unverified. Interaction comparisons change loss/head as well as operation; average fine-tuning/augmentation gains have subset counterexamples. Contribution confidence medium-high; generalization interpretation medium-low; operational reproducibility low. Pinned repository contains only README with a placeholder paper link; no verified implementation, splits, weights, training scripts, reproduction instructions or license. Preserve KSEM 2026 versus printed 2027 copyright/citation observation without bibliographic edits.

Official Springer DOI 10.1007/978-981-92-2856-0_1, 17-page chapter with five authors; contribution section and section 4 establish independently informative homology analysis. Sections 3.1-3.2 define architecture-level pair relations, not instance identity. Section 4.1 reports 224000 training pairs and 68000 testing pairs, not unique-image counts; underlying image and exact training/test source independence are unverified. Table 2 mean Accuracy/AP: cosine 63.8/64.2, subtraction 69.9/72.2, multiplication 75.7/85.6; LDM_100 cosine accuracy 68.3 exceeds multiplication 67.8. Figures 1-2 NPR mean pair accuracy 78.1 to 81.0 and POSE 74.1 to 76.6, with subset degradation. Table 3 AttGAN mixed accuracy 76.0 exceeds asymmetric 74.8; symmetric AP 80.6 exceeds asymmetric 73.7. Canonical Glide_50_27 symmetric AP 74.4 corrects a preserved scratch transcription, not the paper. Printed summaries and rounded-cell arithmetic remain separate. Repository 32456adac2e97de8c906eb378bd332d402a62099 is README-only; no numerical reproduction. KSEM 2026 with printed 2027 footer remains an observation only.

Primary SHA-256: `caf9ac0ae36bf58177409776c0079a7814dbb0a792b84d191d4496b70169d159`.

**R482 — locked R2**. R482 accepted under locked R2: SynRIS independently contributes a reusable binary-authenticity evaluation protocol and real-image population construction through reverse image search, stated visual/thematic matching, pre-2021 page-date restriction, controlled real-pool sensitivity experiments, common scoring and independent detector comparisons. Its intended reuse by future detectors qualifies independently of FakeInversion and beyond extra images or large tables. Add benchmark; retain method, dataset, detection and fully_generated without reopening the accepted dataset role. Reduced semantic/style mismatch is not perfect matching, deployment representativeness or causal validity; balanced samples do not establish deployment prevalence. Search ranking/index changes, page-date reliability, matching-score distributions, duplicates, source overlap and exact split membership remain unverified. Preserve 18-row AUROC averaging, nonuniform baseline comparisons and unresolved Table 3/4 differences. Contribution confidence high; bounded empirical validity medium; operational reproducibility low. Release announcement is not verified executable code, complete archive, license or reproduction. Original ZIP viewer probe rejected unsupported MIME and transfer bytes are unknown; no archive saved/extracted/read. Main CVF version only; appendices and IEEE-final/arXiv equivalence unverified. Unseen-generator detection is not generator identity attribution.

Official CVF accepted CVPR 2024 main paper, DOI 10.1109/CVPR52733.2024.01023, 11 pages/four authors. Contributions 3-5, section 4 and Tables 1-3 define SynRIS evaluation separately from RGB plus SDv1.5 inversion-derived detector features. For each fake, reverse image search selects a visually/thematically similar real on a page created before 2021-01-01; nominal matched class sizes do not certify unique pairs or perfect semantics. Table 2 SD-trained UFD on DALL-E 2 holds fakes and fake-positive recall 0.8 fixed: real-image FPR LAION 0.043 versus RIS 0.406, not fake detection accuracy. Table 3 printed FakeInversion average AUROC 0.798/0.759 covers 18 rows including three academic populations, not SynRIS alone. SD-trained DALL-E 2 UFD 0.776 exceeds FakeInversion 0.747; SDXL CNNDet 0.814 exceeds 0.807. Table 4 ProGAN DALL-E 3 residual 0.672 exceeds full-input 0.642; SDXL Table 3 0.764/0.807 versus Table 4 0.691/0.884 remains unreconciled. Announced JSON URLs/prompts/seeds/code archive, executable evaluator, splits, rights and numerical reproduction were not verified. No supplement or alternate full version retrieved.

Primary SHA-256: `9a2f9d0c6b67198daf0fdbcf9c98340cca9895c8369f832dd3103a6a7f2f1ca7`.

## Exact authoritative and public-data delta

There are fourteen approved CSV cell changes: two `papers.csv` compatibility `research_types` cells, plus six fields in each selected `paper_taxonomy.csv` row (`research_types`, `research_types_review_reason`, `research_types_evidence_tier`, `research_types_evidence_source`, `research_types_evidence_excerpt`, `audited_at`). Every other CSV token is byte-preserved. Exactly two terminal rows append to the prior 99-row registry, producing 101 rows without altering the original bytes. `no_action_after_review` records completion of the approved correction, not absence of a data change.

Deterministic export changes research-type metadata for exactly two public papers and 7 dependent map rows; all other 672 public records, all paper identities and all 1,410 relationship identities remain unchanged. Public JSON is exporter-generated, not manually patched. The companion manifest records exact per-record differences and all fourteen cell values.

## Recomputed final counts

| Corpus | Count | Taxonomy | Count |
|---|---:|---|---:|
| public | 674 | detection | 621 |
| formal | 557 | method | 578 |
| mapped | 613 | analysis_study | 85 |
| unmapped | 61 | survey | 21 |
| relationship_rows | 1410 | source_attribution | 84 |
| unique_paper_institution_pairs | 1410 | dataset | 138 |
|  |  | benchmark | 96 |
|  |  | localization | 45 |

Original Batch B remains 159 actions / 148 papers. Historical unresolved: 133 actions / 123 papers. Active-public unresolved: 131 actions / 121 papers. Only R024 and R482 close; R234 and all unrelated pending questions remain unchanged. Batch C's thirteen debts and the separate 39-paper inventory remain frozen.

## Validation and publication transaction

Focused regressions, four current-scope validators, one full suite and two sequential offline reproducibility passes are required before publication. Actual results are appended in the final administrative validation receipt section. Original evidence-only checks remain historical and are not represented as adjudication validation. Historical fixtures use the non-mutating checksum check; no scientific source is downloaded again.

Exactly one commit is authorized: `fix: classify R024 and R482 research contributions`. Its actual SHA, parent, remote verification, file inventory and final working-tree status are recorded in `/private/tmp/b1p-adjudication-2026-10-26/publication-receipt.json` and the final response. A commit cannot contain its own SHA. No publication success is asserted until the remote SHA is verified.

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Preserved evidence-only report — historical snapshot

The following original report is preserved verbatim. Its pending decisions, old corpus research-type totals and untracked-file statements describe the completed evidence-only phase, not the approved state above. Full original manifest and report bytes are also losslessly archived with their fingerprints in the companion manifest.

<!-- BEGIN PRESERVED EVIDENCE-ONLY REPORT -->

# Batch B Wave B1P — Homology analysis and SynRIS benchmark evidence

Date: 2026-10-26. Published baseline: `2d204d42174bd975cedfc0a3d3699b1c2070237c`.

This packet reviews exactly the original research-type actions R024 and R482. It is evidence only: both remain unresolved, maintainer acceptance is pending, and no authoritative taxonomy, review registry, inclusion, institution, relationship, or public export changed. Proposals below are not terminal decisions. No exporter, full suite, staging, commit, push, or next wave was performed.

| Review | Current complete types | Provisional proposal | Proposed complete types | Contribution confidence | Operational reproducibility |
|---|---|---|---|---|---|
| R024 | `method` | `ANALYSIS_STUDY_ADDITION_SUPPORTED` | `method;analysis_study` | Medium-high | Low |
| R482 | `method;dataset` | `BENCHMARK_ADDITION_SUPPORTED` | `method;dataset;benchmark` | High | Low |

## Recovery and source budget

The existing isolated worktree and all three original workers were recovered. The workers had stopped at the previous usage limit; their source files and transport receipts survived. They were resumed under the same identities rather than replaced by duplicate reviewers. No complete B1P report, manifest, or original completed B1P baseline/context receipt was located on resume; none is assumed to have existed. The recovery baseline is explicitly a fresh capture; it authenticates protected groups against the earlier B1O publication receipt and captures the primary checkout and five concurrent worktrees without modifying them.

Both complete primary manuscripts were obtained by their original successful PDF requests. R024's Springer response and R482's CVF response were verified and reused; recovery retrieved **zero new manuscripts**. R482's original successful curl receipt spans 03:38:13–03:42:13 UTC. A recovery process snapshot found no active matching retrieval processes. No partial bytes were concatenated or promoted to a complete manuscript.

| Source | Transport | Complete bodies across original B1P and recovery | Structure |
|---|---|---:|---|
| R024 official Springer PDF | One PDF request, curl 0 / HTTP 200 | 1 | 628,993 bytes; 17 pages; strict parse, header/EOF, identity and all pages checked |
| R482 official CVF PDF | One PDF request, curl 0 / HTTP 200 | 1 | 9,886,237 bytes; 11 pages; strict parse, header/EOF, identity and all pages checked |

Total: **two newly obtained complete manuscripts**, one per paper; no alternate manuscript version or supplement. Existing local PDF/gzip inventories contained metadata or historical extracts, but no complete identity-matched reusable body. Historical R024 Wave 3B-2 evidence recorded a complete reading without saved raw bytes or a checksum; that history is preserved and not asserted to be byte-equivalent to the present PDF.

Other operations are distinguished from manuscript retrievals. R024's DOI web-open was inaccessible, its repository web-open returned a cache miss, and one pinned raw README request failed TLS before a body (curl 35 / HTTP 000 / 0 bytes). The exact README blob already identified by the pinned tree was then obtained through GitHub's API. R482's official HTML entry returned 403, whereas project and release HTML returned 200. One exact GitHub metadata request during recovery returned a rate-limit 403; no retry followed.

The original R482 web viewer also followed the announced ZIP URL and rejected its unsupported `application/zip` type. No archive was saved, extracted or inspected, and no dataset payload, supplement, model weights or complete repository clone was retained. The viewer's transfer size is unknown: this is **not** a claim of zero archive-URL requests or zero transferred HTTP bytes. No further archive probes were made. The full transport receipts remain outside Git; the manifest keeps compact operational facts and hashes, not TLS certificate payloads or full manuscript text.

## R024 — AI-Generated Image Homology Detection

Canonical ID: `curated:1a8e996ef9ce73efc0ef`. Ordered printed authors: Hang Gao, Rui Ba, Kaiye Yu, Han Xing and Mengting Hu. DOI: `10.1007/978-981-92-2856-0_1`.

Sources: [official Springer PDF](https://link.springer.com/content/pdf/10.1007/978-981-92-2856-0_1.pdf), [DOI](https://doi.org/10.1007/978-981-92-2856-0_1), [author repository](https://github.com/gaohangcodes/AI-generated-Image-Homology-Detection).

The official PDF is 17 pages, printed pages 3–19, KSEM 2026 / LNAI 16633. Its copyright/citation footer says **2027** while the canonical record says **2026**. That discrepancy is an observation outside this research-type action; bibliographic metadata is unchanged. PDF metadata names only Hang Gao, but the printed byline contains all five authors. The original literal spaced-author extraction check failed because extraction inserted spaces between letters in several names. That receipt remains unchanged; a separate normalized and visual identity receipt confirms the byline. No author-version comparison was performed.

SHA-256: `caf9ac0ae36bf58177409776c0079a7814dbb0a792b84d191d4496b70169d159`.

### Original action and governing policy

The historical R024 question asks whether introduction and systematic investigation of source homology, including transferability and robustness, supports `analysis_study`; it requires primary contribution/evaluation evidence. Its historical task context includes detection, but the accepted current task is solely `source_attribution`. T024 was already resolved and is neither reopened nor duplicated.

Locked R3 is applied verbatim:

> Assign analysis_study only when systematic empirical or theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps, or supporting interpretability figures do not qualify by themselves.

### Formal task and protocol

Sections 3.1–3.2 (PDF page 6, printed page 8) define homology as a same-source relationship. The evaluated source granularity is **generator architecture**. Different trained instances with the same architecture may be homologous even with different seeds, data or schedules; instance-level identity is distinguished but left for future work. There is no controlled checkpoint, training-lineage, operator or camera-identity evaluation.

All real-real pairs are treated as homologous. Same-source generated-generated pairs are positive; real-generated and different-source generated-generated pairs are negative. The prediction is one pair relationship score/label, not a named generator class or a single-image real/fake decision. Binary pair labels therefore provide no reason to re-add `detection`.

For each generator subset, section 4.1 (PDF page 9) specifies N real-real positives, N same-generator positives and 2N negatives: 4N balanced pairs. Training uses eight GAN and eight nominal diffusion subsets, N=3,500: 224,000 pair instances. Validation N=500 implies 32,000 pairs across those 16 subsets. Testing uses nine GAN and eight nominal diffusion subsets, N=1,000: 68,000 pairs. These are pair counts, not unique-image counts. Both families occur during training; this does not establish a train-only-GAN to held-out-diffusion protocol. DALL-E-mini is placed in a nominal diffusion group by the paper; its actual architecture is not independently certified here.

The generic shared extractor uses global pooling; ResNet-50 is specified for the naive baseline. Cosine similarity uses cosine embedding loss (margin zero), while absolute shared-FFN difference and elementwise shared-FFN multiplication use BCE and a classifier. These comparisons change objective/head as well as interaction, so they do not isolate a purely interaction-caused gain. Absolute difference, product and cosine are symmetric mathematical comparators; learned transitivity and empirical swap consistency are not measured.

The recipe reports Adam 5e-4, batch 32, up to 50 epochs, validation-based LR reduction/stopping and best-validation-accuracy selection; resize to 256, crop 224 and horizontal flip during training. Exact checkpoints, subset membership, seeds, thresholds, image-disjoint splits, duplicate checks and pair sampler definitions are absent. Collection names and claims of unseen generators do not independently prove architecture/checkpoint/image separation.

### Findings and negative evidence

| Locator | Result as printed | Interpretation |
|---|---|---|
| Table 2, PDF page 10 | Mean accuracy/AP: cosine 63.8/64.2; subtraction 69.9/72.2; multiplication 75.7/85.6 | Multiplication leads these means, not every subset; head/loss differences remain confounds. |
| Figures 1–2, PDF page 11 | NPR frozen→fine-tuned mean pair accuracy 78.1→81.0; POSE 74.1→76.6 | Transfer is useful but limited. Some subset bars worsen; unlabeled bar values are not invented. |
| Table 3, PDF page 13 | Mean accuracy/AP: symmetric 71.2/76.3; asymmetric 74.7/76.9; mixed 72.6/76.7; no perturbation-related augmentation 64.1/69.4 | Asymmetric training leads printed means on mixed-perturbation testing. This is not uniform or causal superiority. |

Table 2 LDM_100 cosine accuracy **68.3** exceeds multiplication **67.8**. Table 3 AttGAN mixed accuracy **76.0** exceeds asymmetric **74.8**; symmetric AP **80.6** exceeds asymmetric **73.7**. RelGAN symmetric AP **80.3** exceeds asymmetric **71.1**. NPR/POSE fine-tuning visibly worsens SNGAN; NPR also worsens Glide_50_27. Figures do not label those individual bars with exact numbers.

Perturbations include JPEG quality 75–100 and Gaussian blur sigma uniformly 0–3. Symmetric training applies the same perturbation type(s) to both images; asymmetric uses different types; mixed randomly chooses those regimes and is also used for testing. Exact probabilities, coupled severities, seeds and held-out schedules are not fully specified. Semantic suppression and causal trace explanations are hypotheses; no content-matched intervention, explicit semantic holdout, source-specific real control or shared-image leakage audit establishes them.

All 252 Table 2/3 cells and four labeled transfer means are retained in the manifest, with an independent transcription reconciliation. Printed summary values are retained even where arithmetic on rounded displayed AP cells does not reproduce them exactly. Mean AP and pooled AP can differ; aggregation is unspecified, so no forced correction or proven paper error is asserted.

### R3 judgment, competing interpretation and release status

**Provisional:** `ANALYSIS_STUDY_ADDITION_SUPPORTED`; proposed complete types `method;analysis_study`; current authoritative types remain `method`.

The principal evidence is the contribution structure (PDF pages 3–4) and section 4's explicit task-science objective using a generic adopted framework rather than a specialized SOTA architecture. The three research questions study interaction families, transfer from detection and attribution representations, and pair-aware robustness. The task formalization and bounded transfer/robustness findings remain informative about relational forensic modeling without retaining one specific optimized detector. RQ1 or augmentation ablations alone would be insufficient under R3.

A competing reading treats all experiments as validation of one Siamese method. That remains plausible because there are few representations, limited source collections, coupled design changes and no controlled semantics or source-instance hierarchy. The explicit primary study objective and cross-representation investigation support the role proposal; they do not establish universal mechanisms. R611 and R267 are bounded precedents for primary investigations, not automatic classification templates or evidence supplying R024's missing controls.

At pinned repository revision `32456adac2e97de8c906eb378bd332d402a62099`, the nontruncated tree contains only `README.md` (349 decoded bytes), with a placeholder paper link. No implementation, dataset, weights, splits, checkpoints or license file is present in that inspected tree, despite the manuscript's code-availability statement. No numerical reproduction was performed.

Confidence: **medium-high contribution role; medium-low empirical generalization; low operational reproducibility**. Maintainer acceptance is pending. An accepted future edit would add only `analysis_study`, preserving `method`, `source_attribution`, `fully_generated` and T024.

## R482 — FakeInversion and SynRIS

Canonical ID: `curated:1eef07ebb6bd7e596f61`. Ordered authors: George Cazenavette, Avneesh Sud, Thomas Leung and Ben Usman. CVPR 2024, printed pages 10759–10769. Canonical DOI: `10.1109/CVPR52733.2024.01023`; arXiv identity: `2406.08603`.

Sources: [official CVF main PDF](https://openaccess.thecvf.com/content/CVPR2024/papers/Cazenavette_FakeInversion_Learning_to_Detect_Images_from_Unseen_Text-to-Image_Models_by_CVPR_2024_paper.pdf), [official entry](https://openaccess.thecvf.com/content/CVPR2024/html/Cazenavette_FakeInversion_Learning_to_Detect_Images_from_Unseen_Text-to-Image_Models_by_CVPR_2024_paper.html), [DOI](https://doi.org/10.1109/CVPR52733.2024.01023), [project](https://fake-inversion.github.io/), [release announcement](https://fake-inversion.github.io/soon.html).

The complete authorized **11-page CVF main file** has eight body pages and three reference pages. It refers to appendices A–E not present in this file; they were not retrieved. The watermark states that, apart from the watermark, it matches the accepted version and directs readers to IEEE for final proceedings. That is a publisher statement, not an independent IEEE-final or arXiv byte comparison. The DOI is from canonical identity, not printed in the PDF; title, authors, venue, official source URL and pages establish the source match.

SHA-256: `9a2f9d0c6b67198daf0fdbcf9c98340cca9895c8369f832dd3103a6a7f2f1ca7`.

### Original action and governing policy

R482 asks whether the reverse-image-search protocol and benchmarks constitute an independent `benchmark`. Existing `method;dataset` roles are retained and not re-adjudicated; the task remains `detection`.

Locked R2 is applied verbatim:

> Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

### Method, task and training boundary

Figure 1 explicitly labels **SDv1.5** inversion/denoising; detector-training fakes separately come from ProGAN or SDv1/DiffusionDB. Sections 3–4 describe BLIP-2 automatic captioning (sometimes abbreviated BLIP), CLIP text conditioning, deterministic DDIM forward inversion without classifier-free guidance, reverse reconstruction, and VAE decoding of both inverted noise and reconstruction. Original RGB plus these two decoded images feed a ResNet-50 trained from scratch with BCE. Original generator prompts are not required; no per-image null-text fine-tuning is described.

The full method is not a residual-only DIRE detector. Its approximate likelihood argument assumes model-misspecification similarity; it is not a verified calibrated likelihood estimator. Inference requires captioning, encoding, iterative inversion/reconstruction and classification. Exact model weight revisions, steps, scheduler, latency and computational budget lie outside verified main-file detail; no numerical runtime is invented. XRAI illustrations are qualitative explanations, not scored localization or causal trace proof.

Training regimes use 350k ProGAN fakes plus LSUN reals, or 300k SDv1 DiffusionDB fakes plus 300k LAION reals. The main paper does not state the exact LSUN real count. Best checkpoints use held-out validation from the same source collections. Exact memberships, underlying overlap and training checkpoint revisions are unverified. Generator names in evaluation are not predicted source identities, and detection of unseen models is not source attribution or unknown-source rejection.

### SynRIS population and acquisition protocol

The manuscript names **SynRIS** and expands RIS as reverse image search; it does not explicitly spell out a complete expansion for SynRIS. For each fake, an image-query search API obtains a visually/thematically similar real image, limited to pages created before **2021-01-01**. This describes nominal per-fake matching, not a verified globally unique bijection. Its operational real class means not text-to-image generated; Photoshop modifications are permitted. An old page date does not prove image capture/upload date, prevent replaced assets, or eliminate older generated content.

Fifteen new populations comprise four commercial sources (DALL-E 2, DALL-E 3, Midjourney v5/6, Imagen) and eleven open sources (Kandinsky 2/3, PixArt-alpha, Playground 2.5, SDXL-DPO, SDXL, Seg-MOE, SSD-1B, Stable Cascade, Segmind Vega and Wurstchen 2). Table 1 states eleven; its footnote lists ten and omits Playground 2.5, which appears in Table 3. Exact checkpoint identity is not recovered for every source.

Table 1 prints balanced per-class sizes of 700/700, 3.3k/3.3k, 4.4k/4.4k, 700/700 and 3.5k/3.5k for each of eleven open sources. These rounded strings are not independently verified asset totals. Three separate academic evaluation rows are also used, including an imbalanced 1k/5k DALL-E 2(A) row whose class orientation is not established by that header alone.

All images are resized to a 256-pixel shorter side and saved losslessly. That controls a size/encoding convention, but does not prove matched aspect-ratio distributions or erase prior compression history. Search provider, index date, ranks, score thresholds, failure policy, score distributions and human matching audits are absent from the main file. No duplicate, source-host, prompt-family or train/test image-overlap audit is verified. FID/KID compare aggregate distributions; they do not certify each pair's semantics, perfect style balance or causal validity.

### Independent comparisons, exact results and contradictions

Table 2 (PDF page 6) fixes fakes and UFD's fake-positive recall at 0.8 while changing the real pool. Its metric is real-image FPR, not AUROC: higher FPR means the chosen reals are harder at that fixed operating point.

| Population/control | Exact reported result |
|---|---|
| DALL-E 2, ProGAN-trained UFD, LAION→RIS | FPR 0.233→0.457 |
| DALL-E 2, SD-trained UFD, LAION→RIS | FPR 0.043→0.406 |
| Imagen, SD-trained UFD, LAION / WebLI / RIS | FPR 0.360 / 0.664 / 0.720 |
| Imagen, LAION / WebLI / RIS distribution distance | FID 127.1 / 101.9 / 83.6; KID printed ×10^-2 values 2.1 / 1.2 / 0.2 |

Table 3 (PDF page 7) evaluates DIRE, CNNDet, DMDet, UFD and FakeInversion with binary-authenticity AUROC on common described populations. DMDet's right panel uses an LDM-trained model rather than identical SD training; reported DIRE checkpoint issues also limit uniform comparison. Shared population descriptions are not independently verified pixel-level identity.

FakeInversion's printed average AUROC is **0.798 ProGAN / 0.759 SD**, averaging **18 rows: 15 SynRIS plus three academic populations**. Arithmetic on rounded cells gives 0.797611/0.759444 over 18, versus 0.7988/0.748933 over the 15 SynRIS rows alone. Those derived values do not replace printed results.

Counterexamples matter: Table 3 SD-trained DALL-E 2 UFD **0.776** exceeds FakeInversion **0.747**; SDXL CNNDet **0.814** exceeds **0.807**. On the academic rows, FakeInversion is below a leading baseline. Table 4 ProGAN DALL-E 3 residual **0.672** exceeds full-input **0.642**. Several Table 4 full-method values differ from Table 3 without reconciliation in the main file: SDXL is **0.764/0.807** in Table 3 but **0.691/0.884** in Table 4. These contexts are kept separate; checkpoint/sampling equivalence is not asserted. Some perturbations in Table 5 improve scores; universal degradation or robustness claims are not justified.

The paper argues that matched evaluation aligns with in-the-wild behavior. The verified main-file support is real-pool difficulty and distribution-distance comparisons, including WebLI; it gives no independent prospective deployment cohort or numeric cross-detector correlation coefficient. WebLI and RIS values are not equal. Different academic-versus-SynRIS fake pools cannot isolate matching as the sole cause of rank changes; Table 2 directly supports sensitivity to real-pool selection for UFD, not a causal ranking result for every detector.

### R2 judgment and release limits

**Provisional:** `BENCHMARK_ADDITION_SUPPORTED`; proposed complete types `method;dataset;benchmark`; authoritative current types remain `method;dataset`.

Contributions 3–5 explicitly separate protocol construction, comparison and future reuse from the detector itself. Section 4 fixes evaluation populations, matching conventions and scoring; Table 2 studies a separate UFD detector under controlled real-pool changes, Table 3 compares independent detector families, and section 6 invites future evaluation. The protocol can score future binary detectors without FakeInversion features. This supports R2 beyond extra test images or large tables, while imperfect controls limit empirical claims rather than negate the evaluation-protocol role.

The project/release HTML advertises a Google-hosted ZIP with code, JSON real-image URLs and fake-generation prompts/seeds. It has 13 preview links; dataset payloads were not inspected. No executable evaluator, actual split manifest, fixed code revision, asset checksum, license or complete operational resource was verified. The exact GitHub metadata pin attempt was rate-limited. Announcement and protocol intention are not proof of executable release or successful reproduction.

Confidence: **high contribution role; medium empirical validity within bounded populations; low operational reproducibility**. Maintainer acceptance is pending. A future accepted correction would add only `benchmark`, retaining `method;dataset`, `detection` and `fully_generated`.

## Bounded attribution comparison and research hypotheses

| Dimension | Evidence boundary |
|---|---|
| Pair verification | R024 predicts whether two images share an architecture-level source; it does not name the source. |
| Binary authenticity | R482 scores single-image real/fake origin. Search pairing constructs evaluation data; it does not turn inference into homology. |
| Closed-set source identification | Accepted R596 Attribution88 uses fixed known architecture/source labels including Real, accuracy/NMI and semantic/corruption holdouts. Held-out image content is not held-out architecture labels. |
| Unknown-source rejection | Accepted R574 POSE separately evaluates known-source classification and unknown-generator rejection using AUC/OSCR, five splits and seed/architecture/data scenarios. Those endpoints are absent from R024/R482. |
| Semantic holdout | R596's semantics-related holdouts and R482's matched real pools answer different questions; neither supplies R024's missing explicit content independence. |
| Instance shift | R024 conceptually groups instances under architecture, but does not evaluate controlled instance/checkpoint discrimination. R574 treats shifts separately. |
| Architecture shift | Named unseen target populations do not prove exact architecture-disjoint training. Split manifests and lineage controls are needed. |
| Metrics | Pair accuracy/AP, source accuracy/NMI, authenticity AUROC and open-set AUC/OSCR cannot be transferred or ranked without matching populations, definitions and operating points. |

R611's fingerprint study and R267's quality/detectability investigation are bounded R3 precedents. R034 RealChain's ND/CD chains and R359 LAID's independent comparative interfaces are bounded R2 precedents. LAID's label-dependent Oracle Fusion Accuracy is not a deployable prediction score; its max-fake-probability F1/AUROC analysis is separate. Prior accepted evidence is reused locally; no new review action or retrieval for those papers occurred.

Possible RefPrint or HieraSIA-Bench ideas below are **new research hypotheses**, not verified features of those projects or demonstrated conclusions of either paper:

1. Define family, architecture, checkpoint, seed and training-data identities hierarchically; distinguish same-architecture/different-instance pairs from exact-instance positives at each granularity.
2. Split unique images, content groups and model instances before constructing pairs. Audit duplicate and training overlap; estimate uncertainty by image/source clusters instead of treating all shared-image pairs as independent.
3. Test matched-content/style controls in source/pair evaluation using frozen URLs, dates, pixel hashes, ranking rules, match scores and audits. Measure which nuisance variables matching actually controls.
4. Keep authenticity, known-source ID, unknown rejection and pair verification as separate endpoints with separate calibration and held-out validation. Do not substitute one task's metric for another.

No implementation, additional wave or numerical reproduction is authorized by these hypotheses.

## Independent checks and unchanged accounting

Both owners completed source-first reviews. The independent preservation reviewer read all 17 and 11 pages and selected rendered tables before reading owner verdicts. The root also read all pages and nine rendered pages before owner verdicts; root notes were saved after receipt of the independent reviewer's message, so no fully blinded pre-peer written freeze is claimed. Owner notes, root notes, independent notes, raw transcriptions, original failures and later reconciliations have separate hashes; none is silently rewritten to manufacture agreement. An initial R482 checker counted the 2.5 in Playground model labels as a metric (64 passed / 3 failed); the preserved first receipt is superseded by an exact row-label selector, with unchanged source/transcribed metrics and 67/67 checks passing. No repository tests or historical fixtures were changed.

Fresh recovery counts were recomputed from current authoritative/effective records. Accounting recognizes the two published B1O terminal IDs as well as older note patterns; relying only on an older free-text prefix would miss them. Evidence proposals do not close actions or reduce unresolved counts.

| Corpus | Count | Taxonomy | Count |
|---|---:|---|---:|
| Public | 674 | Detection | 621 |
| Formal | 557 | Source attribution | 84 |
| Mapped | 613 | Localization | 45 |
| Unmapped | 61 | Method | 578 |
| Relationships | 1,410 | Dataset | 138 |
| Unique pairs | 1,410 | Benchmark | 95 |
| | | Survey | 21 |
| | | Analysis study | 84 |

Batch B remains **159 actions / 148 papers** originally; **135 actions / 125 papers** historically unresolved; **133 actions / 123 papers** active-public unresolved. The terminal registry remains **99 rows**. R024 and R482 remain open; T024 and all prior decisions are unchanged. Batch C retains all **13 deferred debts**; the separate **39-paper import inventory** is unchanged.

The protected 128 files, original 130-file group, 49 frozen NeurIPS artifacts in both checkouts, 119 historical ignored inputs, all 140 current isolated ignored paths, historical fixtures, all 1,410 relationship identities, 30 prior B1A–O artifacts and 53 Batch C/audit artifacts are preserved. The primary checkout's tracked/untracked/ignored content, status, index, branch and HEAD are preserved, along with five other worktrees.

Only the two requested B1P evidence files are created in the isolated worktree. Tracked diff and index remain empty; neither file is committed or pushed. Source PDFs, scripts, HTML and operational receipts remain outside Git. Final content hashes are recorded in an external validation receipt to avoid a manifest hashing itself.

`AUTHORITATIVE_CORPUS_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Numerical reconciliation and validation receipt

R024Table3Glide_50_27 symmetricAP is74.4,not originalowner71.4. Five roottranscriptioncells separatelycorrected: mixedBEGAN88.0,S3GAN66.1,Glide_100_27 76.2; noaugmentationGlide_50_27 73.6,LDM_100 71.5. Originalowner/root/independentnotesremainfrozen. All252printedTable2/3cells verified in correctedcanonicalprojection. RoundedrowAPmeans76.270588/76.847059/76.7/69.464706 remainseparatefromprinted76.3/76.9/76.7/69.4; pooling/roundingnotfullyspecified, no forcedpapermeanrepair.

R024 owner scoped checks: 65 passed. R482 owner scoped checks: 67 passed. Initial independent preservation: 56/56 passed. Final postwrite preservation and packet identity/provenance/content-binding results are recorded outside Git in `independent-preservation-final.json` and `final-packet-validation.json` under the B1P operational directory. These are evidence checks, not the repository full suite.

The companion manifest contains both original questions, all 20 R024 questions, 10 FakeInversion method questions, 20 SynRIS questions, exact table transcriptions, reconciled arithmetic, scientific counterexamples and separate source/worker/independent receipts. Original scratch outputs remain preserved outside Git; the final packet uses explicitly reconciled values.

<!-- END PRESERVED EVIDENCE-ONLY REPORT -->

## Final measured validation receipts

Focused regressions completed successfully: 155 tests and 12 subtests; JUnit failures/errors/skips 0/0/0.

All four current-scope validators completed with zero errors. Warning counts are preserved separately: curated 294, public 62, exclusions 2, coverage 0. These are distinct from the full-suite warning count.

The full repository suite executed once successfully: 2234 tests, 389 subtests, 2 warnings; JUnit failures/errors/skips 0/0/0. Interpreter, bundled Node, localhost authorization, command and log/XML fingerprints are retained in the manifest.

The first full-suite invocation did not execute because automatic approval review encountered an account usage limit. The unchanged original command and wrapper were later accepted through normal require_escalated review. The refusal is not counted as a test run, failure or success; the successful execution has a separate immutable receipt.

Two sequential offline verification exports completed with exit status 0. All 4,638 input/output paths and all 7 direct generated outputs matched the pre-pass byte/mode/hash inventory after each pass. Historical fixture checks before/after verified 117 inputs and created 0 files. `EXPORT_REPRODUCIBLE = 1`.

Independent semantic audit: 99/99 checks passed; independent precommit review: 56 checks passed; independent pre-stamp protection: 175/175 passed. All four final protection flags are zero.

The scientific fields, original evidence archives, authoritative inputs, public JSON, regression code and generated outputs were unchanged by this administrative stamp. Only validation/status/integrity/receipt-index fields and this appended section changed. Scoped post-stamp checks bind the final artifacts; no full-suite rerun or scientific edit is needed for the receipt-only stamp.

Actual commit SHA, parent, exact file statistics, remote SHA and final Git state will be recorded only after publication in `/private/tmp/b1p-adjudication-2026-10-26/publication-receipt.json` and the final response. This snapshot does not claim remote publication before that check.
