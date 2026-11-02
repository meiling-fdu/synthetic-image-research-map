# Batch B Wave B3-03 — evidence-only review

B2-03’s original membership is preserved: **10 papers / 11 actions**, comprising ten research-type questions and independent publication-track question P231. The baseline is `d109c70f6994906ec3d9197baad51cf9d8e51f7c`. All 11 selected actions remain formally unresolved; none changed status or context between the original B2 snapshot and the published B5 baseline. B5 resolved 11 other actions, so global accounting changed from 131/129 in B2 to 120/118 before this wave. This review does not decrement those totals.

B5-01 is **PUBLISHED — CI ACCEPTED**. Its previously missing append-only completion receipt was archived outside the repository using preserved verified evidence: hosted CI run 41166935536 / job 124436408657 / attempt 1, 2,445 tests and 389 subtests, zero failures; Pages run 41166935300 SUCCESS; live JSON bytes matched. No CI, export, commit or publication was repeated. See [completion receipt](../batch-b-b5-01r3-2026-10-31/completion_receipt.json).

## Scope and decision standard

Locked R1 requires substantive construction, release, curation or systematic provision of reusable data; experiment-only data is insufficient. Locked R2 requires a substantive reusable evaluation resource, protocol, challenge or comparative framework; extensive tables alone are insufficient. V1 keeps canonical venue, event/container and track distinct. Existing detection and method labels are preserved. Contribution support is separate from empirical validity, causal interpretation, availability and operational reproducibility. These are provisional evidence recommendations; a subsequent maintainer decision is required.

## Action-by-action findings

| Action | Exact canonical paper ID | Provisional outcome | Bounded recommendation |
|---|---|---|---|
| R110 | `curated:6976641cbfe602a7e617` | `SUPPORTED_ADDITION` | method;dataset;benchmark |
| R138 | `curated:88b63de59a0eabcd1b02` | `EVIDENCE_INSUFFICIENT` | Hold; preserve authoritative state |
| R154 | `curated:8e9658fa727094695be8` | `IDENTITY_BLOCKED` | Hold; preserve authoritative state |
| R161 | `curated:506d44d3feea2627dd42` | `EVIDENCE_INSUFFICIENT` | Hold; preserve authoritative state |
| R171 | `curated:a570863c3a6ac227b56c` | `SUPPORTED_ADDITION` | method;dataset;benchmark |
| R187 | `curated:08aa2b51bb36247bdda3` | `EVIDENCE_INSUFFICIENT` | Hold; preserve authoritative state |
| P231 | `curated:0d918782407e05ade5bd` | `SUPPORTED_ADDITION` | venue_track=Main (qualified) |
| R231 | `curated:0d918782407e05ade5bd` | `EVIDENCE_INSUFFICIENT` | Hold; preserve authoritative state |
| R256 | `curated:c6bfe8f5199d1d8beb29` | `SUPPORTED_ADDITION` | method;dataset;benchmark |
| R275 | `curated:7cfe39b3bc63f5b55f51` | `SUPPORTED_ADDITION` | method;benchmark |
| R564 | `doi:10.1109/tmm.2023.3313503` | `SUPPORTED_ADDITION` | method;dataset |

### R110 — Forensic Detection of Generated MRI Imagery Using Autoregressive Modeling and Frequency Analysis

MRI-Forensics is a substantive constructed reusable medical forensic dataset and cross-generator/domain evaluation resource. The manuscript supports R1 and R2 independently of the claimed AIM-DWT performance. Table 2 is generated-image-only because all 6,306 real images are allocated to training/validation; its 100% entries are not balanced authenticity accuracy. The RINE prose/Table 2 discrepancy is retained.

Evidence record: [per_paper/R110.json](per_paper/R110.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://openaccess.thecvf.com/content/WACV2026W/SAFE-2026/papers/Mahara_Forensic_Detection_of_Generated_MRI_Imagery_Using_Autoregressive_Modeling_and_WACVW_2026_paper.pdf).

### R138 — Incremental Learning for AI-Generated Image Detection

The DOI and author FakeCOCO repository correspond, but the IEEE full-text request returned an empty HTTP 202 challenge. A dataset release/abstract claim does not establish the missing manuscript-level construction and contribution protocol. Retain the Xinhan/Xinghan spelling caveat and research-only dataset terms; do not infer a verified repository license from uncaptured material.

Evidence record: [per_paper/R138.json](per_paper/R138.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://api.crossref.org/works/10.1109%2Ftmm.2026.3716041), [source2](https://raw.githubusercontent.com/ac-miracle/FakeCOCO/main/README.md), [source3](https://doi.org/10.1109/tmm.2026.3716041).

### R154 — MIRAGE: Towards AI-Generated Image Detection in the Wild

The inspected arXiv 2508.13223v1 candidate provides conditional R1/R2 support, but first author Cheng Xia conflicts with canonical/DOI OuCheng Huang. Eight other authors and title match; an authoritative work/version bridge is absent. Preserve 20,000-versus-2,000 training, 53-versus-64 model, 64-versus-8-GPU and robustness discrepancies, and the nonuniform OOD results. No publisher-final equivalence or unconditional addition is proposed.

Evidence record: [per_paper/R154.json](per_paper/R154.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://arxiv.org/pdf/2508.13223v1), [source2](https://api.crossref.org/works/10.1609%2Faaai.v40i7.37421), [source3](https://doi.org/10.1609/aaai.v40i7.37421).

### R161 — No Pixel Left Behind: A Detail-Preserving Architecture for Robust High-Resolution AI-Generated Image Detection

The official identity record is available, but no complete identity-matched scientific manuscript was obtained through the recorded endpoints. Dataset/benchmark contribution claims cannot be accepted from title, abstract or identity evidence alone. Preserve the exact failed requests and hold for full construction/protocol evidence.

Evidence record: [per_paper/R161.json](per_paper/R161.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://proceedings.iclr.cc/paper_files/paper/2026/hash/820e42f39773c6cbbd875553db45658f-Abstract-Conference.html), [source2](https://proceedings.iclr.cc/paper_files/paper/2026/file/820e42f39773c6cbbd875553db45658f-Paper-Conference.pdf), [source3](https://openreview.net/pdf?id=9QQ3Kc2hj6).

### R171 — PGC: Peak-Guided Calibration for Generalizable AI-Generated Image Detection

CommGen15 is evaluated as a named resource rather than inferred from the size of result tables. Table 1 mixes 19,472 static generated images and 13,922 video-derived frames (33,394 generated samples), with 33,394 COCO real controls. Do not describe it as wholly static imagery or infer a separate video-forensics task. Reported 97.9% versus 85.6% mean accuracy is a 12.3 percentage-point difference, not a relative percentage improvement; pooled accuracy and independence of frames were not verified. The detailed record separates R1 construction/curation from R2 reusable comparative protocol, and preserves all source-specific numerical and metric limitations. Consult the manuscript locators and independent QC before maintainer acceptance.

Evidence record: [per_paper/R171.json](per_paper/R171.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://raw.githubusercontent.com/mlresearch/v306/main/assets/zhou26h/zhou26h.pdf), [source2](https://proceedings.mlr.press/v306/zhou26h.html).

### R187 — RealNet: Efficient and Unsupervised Detection of AI-Generated Images via Real-Only Representation Learning

DOI metadata establishes identity but the publisher endpoints returned browser challenges and the alternative primary endpoint was inaccessible. Medical application claims alone do not establish a reusable dataset contribution. Missing full construction, provenance, partitions and contribution evidence remains an explicit hold.

Evidence record: [per_paper/R187.json](per_paper/R187.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://api.crossref.org/works/10.1609%2Faaai.v40i45.41234), [source2](https://doi.org/10.1609/aaai.v40i45.41234), [source3](https://ojs.aaai.org/index.php/AAAI/article/download/41234/45195).

### P231 — Unified Detection of Synthetic and Manipulated Images via Dual-Stream Artifact Fusion

The official MAD 2026 final program lists the exact title and all four canonical authors in regular Session 2. Proposed Workshop→Main is a repository-normalized regular-paper role under V1; the program never literally prints Main. Preserve venue:mad, the standalone archival workshop identity, DOI and all other metadata. Co-location does not authorize changing the venue to ICMR. Earlier program-date/edition inconsistencies remain documented.

Evidence record: [per_paper/P231.json](per_paper/P231.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://mad2026.aimultimedialab.ro/program/).

### R231 — Unified Detection of Synthetic and Manipulated Images via Dual-Stream Artifact Fusion

P231 program and earlier U017 page 1 receipt establish identity/affiliations only. One official ACM full-text request returned HTTP 403 challenge HTML. NESS 210,776-image and DAFNet numerical claims remain inherited, unverified claims; no manuscript methods/evaluation basis is available for accepting dataset or benchmark. This hold is independent of P231.

Evidence record: [per_paper/R231.json](per_paper/R231.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://dl.acm.org/doi/pdf/10.1145/3810988.3812660), [source2](https://mad2026.aimultimedialab.ro/program/).

### R256 — Adaptive Test-Time Semantic Debiasing for AI-Generated Image Detection

The official CVF manuscript supplies the bounded CSAIID construction and cross-semantic evaluation evidence. R1 and R2 must be justified separately from ATTSD performance, generalization claims and code/data availability. Section 4 reports six categories, each 1,000 real plus 1,000 synthetic images (12,000 total), and states a 1:1:1 generator balance across subsets. Independent QC notes that 6,000 synthetic images can be balanced globally (2,000 per generator); a global contradiction is not established. Exact per-category generator allocations remain unspecified. The original reviewer observation about non-divisibility within a 1,000-image category is preserved additively, without assuming that the paper requires equality within each category. Table 1 reports ATTSD 82.30%/90.42% versus NPR 71.33%/84.02% under two training regimes that change both real-source semantics and fake generator. This does not isolate semantic shift causally. Exact protocols, table locators and limitations are preserved in the evidence record.

Evidence record: [per_paper/R256.json](per_paper/R256.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://openaccess.thecvf.com/content/ICCV2025W/APAI/papers/Cai_Adaptive_Test-Time_Semantic_Debiasing_for_AI-Generated_Image_Detection_ICCVW_2025_paper.pdf).

### R275 — Breaking Latent Prior Bias in Detectors for Generalizable AIGC Image Detection

Accepted NeurIPS 2025 PDF supports R2 through GenImage++ construction, explicit future-evaluation purpose and comparative protocol. Table 3 has 13 external variants plus OMAT; the OMAT stratum macro mean is 96.78%, not a balanced real/fake accuracy. Appendix C.4 says the resource has no real images; reported values are generated-class performance. Nine Table 7 counts total 138,900 using rounded source counts. Preserve Bin/Bing Fan source spelling conflict, OMAT terminology and model-validity limits. Dataset classification is outside R275 scope.

Evidence record: [per_paper/R275.json](per_paper/R275.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://papers.neurips.cc/paper_files/paper/2025/file/2c2be72635379ec8600eea13df4743e3-Paper-Conference.pdf), [source2](https://papers.neurips.cc/paper_files/paper/2025/hash/2c2be72635379ec8600eea13df4743e3-Abstract-Conference.html).

### R564 — GLFF: Global and Local Feature Fusion for AI-Synthesized Image Detection

The inspected GLFF author manuscript supports DF3 as a substantive constructed data contribution under R1. Tables I/II total 46,476 synthetic derivatives, versus approximately 46,400 in prose; these share 6,160 base generated images. DF3 itself has no real images; 1,000 FFHQ real controls are sampled separately for evaluation. Preserve author-version versus publisher-final boundaries, face blending/swapping and post-processing distinctions. A promised future release does not verify current data availability. Benchmark status is not part of the assigned R564 action and is not proposed.

Evidence record: [per_paper/R564.json](per_paper/R564.json). Exact claim locators, source hashes, protocols, quantitative evidence and limitations are preserved there.

Primary source references: [source1](https://arxiv.org/pdf/2211.08615v7).

## Outcome accounting and follow-up

**SUPPORTED_ADDITION: 6**; **EVIDENCE_INSUFFICIENT: 4**; **IDENTITY_BLOCKED: 1**.

Proposed changes are enumerated in [batch_dispositions.json](batch_dispositions.json) and [b4_handoff.json](b4_handoff.json). Holds are not negative contribution findings. R154’s conditional resource support does not resolve its identity boundary. P231’s normalization is explicitly qualified and requires maintainer acceptance. No new review inventory entry or unrelated task, research-type, venue identity, author or institution correction was created.

Formal decisions remain **127**; historical unresolved **120**; active-public unresolved **118**. All 11 reviewed actions remain formally open. The 13 Batch C deferred debts and separate 39-paper inventory remain unchanged.

## Evidence cost and effort

Six new complete manuscript files were obtained (64,721,117 bytes, approximately 61.72 MiB), including one identity-blocked candidate version (R154). The other four paper identities have no obtained full manuscript. Metadata/program requests and failed retrievals are preserved separately; failure HTML is never counted as a PDF. No datasets, weights, supplements or scientific experiments were downloaded/run.

Local evidence was inspected first, including earlier U017 affiliation/identity and GenImage++ lineage receipts. Request timings and response bytes are recorded where instrumented. [effort_and_retrievals.json](effort_and_retrievals.json) distinguishes observed elapsed wall time from measured network durations. Exclusive analyst person-time was not instrumented; estimates in individual records are not reported as actual labor or used to claim a complete B2 effort recalibration. Browser discovery requests lack a complete byte/time ledger and are explicitly outside the measured capture totals.

## Quality control and preservation

Independent reviewers checked actual primary captures and claim locators, not only agreement between JSON fields. [Independent scientific QC](qc/independent_scientific_QC.md) records each original recommendation separately from its independent verdict; all classification outcomes agree, with an additive R256 numerical-interpretation refinement (original reviewer record preserved). See [GroupA QC](qc/groupA-independent-review.json), [GroupB QC](qc/groupB-independent-review.json), [P231/R231/R275 QC](qc/root-group-review.json) and [final batch QC](qc/final_batch_QC.json). Nonblocking provenance fixes were recorded additively, with previous records/captures retained: R138 license qualification, R154 screenshot locator, P231 V1 policy link and R231 receipt hash. R256’s original reviewer observation is preserved alongside the independent caveat addendum. Scientific outcomes were not silently changed.

Lightweight checks cover exact 11-action/10-paper membership, canonical identity, hashes, scoped proposals, formal-open status, accounting and read-only Git state. See [validation](validation.json) and [final preservation](qc/preservation_final.json). No full suite, export or publication was run for this evidence wave.

Published data is preserved: 674 public, 557 formal, 613 mapped, 1,410 relationships/unique pairs; task totals 621 detection, 84 source attribution, 45 localization; types 578 method, 138 dataset, 97 benchmark, 21 survey, 86 analysis study.

All 128 protected primary files, 49 frozen NeurIPS artifacts, both B4 pending worktrees/archives, B5 accepted source/archive, B1S/CI-STABILITY-01 history, Batch C debts and separate inventory are covered by preservation receipts. Nine ignored frozen inputs were deliberately not materialized in the fresh worktree; their existing original bytes remain checked in protected roots. Concurrent primary work is preserved.

`AUTHORITATIVE_CORPUS_CHANGED = 0`  
`FROZEN_NEURIPS_CHANGED = 0`  
`PREEXISTING_LOCAL_FILES_CHANGED = 0`

## Git and stop state

Fresh isolated worktree: `/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map`, detached at published `d109c70f6994906ec3d9197baad51cf9d8e51f7c`. Evidence artifacts are external to the checkout at `/Users/meilinger/.codex/visualizations/2026/10/02/01a0fd3f-53f2-7811-a204-a10941e224b5/batch-b-b3-03-2026-10-31`. Exact final status is recorded in validation/preservation receipts: clean tracked tree, empty index, zero untracked/ignored files in this new worktree. No authoritative records, formal decisions, exports or website code changed. Nothing staged, committed or pushed. B4-03 was not started.

7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA
