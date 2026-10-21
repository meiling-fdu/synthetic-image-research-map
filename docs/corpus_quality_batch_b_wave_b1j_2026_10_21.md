# Batch B Wave B1J — R100 dataset and R400 benchmark accepted

Maintainer-approved adjudication of the completed evidence-only packet at published baseline `1221cf72f8f77ac3430cad49a49d074d82b36ec2`. The baseline was fetched and verified before application. Existing draft and final lightweight checks **44/44 each**, independent preservation checks **34/34**, and scientific checks **32, 41 and 31** are preserved and reused. Exactly two complete official manuscripts and all prior source/transport receipts remain; no scientific retrieval or extraction was repeated during adjudication.

| Review | Accepted outcome | Previous types | Final types | Tasks |
| --- | --- | --- | --- | --- |
| R100 | `PROPOSE_CORRECTION_ACCEPTED` | `method` | `method;dataset` | `detection`, unchanged |
| R400 | `PROPOSE_CORRECTION_ACCEPTED` | `method;dataset` | `method;dataset;benchmark` | `detection`, unchanged |

Terminal decision IDs: R100 **`review:926fcbf72f575cdf407a`**; R400 **`review:e603cf0e2cfc1e986aec`**. Both use the existing supported `other` queue, `paper` target and `no_action_after_review` action, recording that the approved correction is complete. The action does not assert that no data changed. The registry grows **89 → 91** rows with every original byte preserved as a prefix. Actual application UTC: **2026-10-21T12:54:24Z**. The two taxonomy `audited_at` fields are **2026-10-21**; original source-version dates, retrieval timestamps, prior registry timestamps and evidence-stage history are unchanged.

## R100 — FakeXplained is an independent dataset contribution

Canonical paper: **FakeXplain: AI-Generated Image Detection via Human-Aligned Grounded Reasoning**, `curated:411724cd949b78c1af6a`, ICLR 2026. FakeXplainer remains the substantive method. The complete proceedings manuscript separately establishes FakeXplained as an original annotated research resource: **8,772 images**, **23 trained annotators**, an average **5.42 region-caption pairs**, **six global tags**, a **5% quality-control subset**, final reference IoU **42.35%** and tag agreement **79.67%**. Construction and annotation protocols, resource-specific quality-control experiments and application to other detection methods support reuse independently of the proposed model.

Under locked **R1**, substantive original construction or systematic curation of a reusable resource can support dataset; public download availability is not the sole criterion. **Add `dataset`; retain `method`, `detection` and `fully_generated`.** This classifies the demonstrated resource contribution, not data generated solely for a method's experiments.

All limitations remain explicit. The text claims **28 generators** while Table 1 lists **27**. MLLM annotation assistance is incompletely quantified. Region and caption annotations contain subjective components. Individual baselines outperform FakeXplainer on some reported metrics; the complete favorable and adverse comparisons remain in the original scientific evidence below and in the manifest. The advertised author GitHub repository was empty when inspected. **Public annotation assets, official dataset partitions, licensing, actual download completeness and independent numerical reproduction remain unverified.** The dataset is not claimed already publicly downloadable.

Official manuscript: [Official ICLR 2026 proceedings conference PDF; publication header throughout. PDF CreationDate: 2026-02-28 10:14:16 UTC.](https://proceedings.iclr.cc/paper_files/paper/2026/file/701ec28790b29a5bc33832b7bdc4c3b6-Paper-Conference.pdf); **22 pages**, SHA256 `dc58c87cd13f7ad52102cc6f6b9c5f95f35a7ae24c0c1629bc39de01ad38aed9`. Its original creation/modification dates and actual retrieval receipts are preserved. No equivalence with a separately retrieved alternate version is asserted.

### OUT_OF_SCOPE_TASK_TAXONOMY_OBSERVATION — preserved without adjudication

The manuscript reports **98.2% detection accuracy** and **36.0% artifact-localization IoU**. Its structured spatial boxes target synthesis artifacts and are evaluated against annotated artifact regions, rather than serving only as unscored attention maps. This remains positive evidence for a **separately authorized future T2 localization review**. The original observation, metrics, ground-truth and matching uncertainties remain exact in the existing record and full evidence report.

**No localization label is added.** R100 retains `tasks: detection`. No task review is closed, no task terminal decision is appended, no new historical Batch B action ID is invented, and the original denominators remain **159 actions / 148 papers**. The accepted dataset correction is not a spatial-task adjudication.

## R400 — FakeART is an independent benchmark framework

Canonical paper: **Secret Lies in Color: Enhancing AI-Generated Images Detection with Color Distribution Analysis**, `curated:b2fccf1dd66cc2d64374`, CVPR 2025 Main Conference, DOI `10.1109/CVPR52734.2025.01255`. CoD remains the color-distribution method and FakeART remains the contributed image resource.

FakeART separately defines a **photo-to-art cross-domain evaluation setting**: COCO/LSUN training sources; **SD v1.4 and ProGAN** training generators; **7,000 real WikiArt test artworks**; seven named test-generator variants (**SD-1.5, SD-2.1, SD-Turbo, SD-XL, SD-3, PlayGround-2.5 and PixArt-α**); binary **ACC threshold 0.5**; accuracy/AP metrics; and comparisons against existing detectors. Another detector can be evaluated under this setting independently of CoD. This is substantive reusable evaluation-task/protocol evidence under locked **R2**, not merely benchmark wording or a large table. R2 does not impose a separately packaged evaluation library as an additional mandatory condition.

Table 4 reports CoD mean **66.5% ACC / 68.2% AP**, versus PatchCraft **58.7% / 59.5%**, differences of **7.8 / 8.7 percentage points**. These are published comparisons, not independently reproduced results. **Add `benchmark`; retain `method`, `dataset`, `detection` and `fully_generated`.** This is a **medium-confidence contribution-based judgment**, not blanket certification of benchmark reproducibility.

The paper states **50,000 COCO/LSUN training-source images**, but synthetic training totals, generated evaluation totals, per-generator counts and test class balance are unverified. Exact split files, identical baseline retraining conditions, evaluation code, full resource availability and licensing remain unverified. An author-linked dataset host exists; this does not prove a complete downloadable FakeART release. No unsupported synthetic totals or balanced-class assumption is introduced.

Content, visual style, source-domain and generator-family shifts are not independently isolated. The descriptive GenImage-to-FakeART drop is not a controlled style-only causal effect. Prior-benchmark wording gives **350,000 ProGAN synthetics** but **20 × 18,000 = 360,000**; it also mentions four ProGAN datasets. Table 1 CoD GAN mean ACC **98.2** versus Table 5 combined-image/color GAN ACC **98.7** remains unexplained. Table 4 printed AP means **CNNDet 43.4 / NPR 54.6 / SAFE 58.4** differ from simple means of the seven displayed cells (approximately **43.457 / 54.657 / 58.529**); hidden precision, weighting or aggregation is unspecified. Printed values are retained; not every published mean is claimed arithmetically reproduced. CoD **66.5 / 68.2** does reconcile. All original adverse evidence and reproducibility boundaries remain intact.

Official manuscript: [CVF CVPR 2025 Main Conference paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Jia_Secret_Lies_in_Color_Enhancing_AI-Generated_Images_Detection_with_Color_CVPR_2025_paper.pdf); **10 pages**, printed **13445–13454**, SHA256 `6fab4d3e07ea14ea2c111f4c5b87635bc5c587d485e2fb6e73b380bd0e5bab70`. DOI registration identity is matched, but a separate IEEE-hosted PDF and alternate-version equivalence are not verified. The original timed-out HTTP 200 transfer and identical-ETag HTTP 206 continuation reconstruct **one manuscript**, not two versions. Combined with R100's 22-page proceedings paper, the evidence wave still contains exactly **two complete manuscripts**. No additional retrieval occurred.

## Exact authoritative and deterministic-output delta

Exactly **14 existing CSV cells** change across R100 and R400: one `papers.csv` compatibility type field plus six `paper_taxonomy.csv` type/provenance/audit fields for each paper. Existing reviewed statuses, canonical timestamps and every other original field and byte remain unchanged. Exactly **two** terminal decision rows are appended. No inclusion/exclusion, forensic task, image-scope, bibliography, publication, author, affiliation or institution change occurs.

The established offline exporter changes exactly **two existing public paper records** and **three existing map records**: R100's two map records and R400's one map record. Substantive fields are limited to `research_types` and the dependent research-type review reason. The other **672 public papers**, other **1,407 map records**, and all **1,410 relationship identities** remain semantically unchanged. No generated JSON was manually edited. Legitimate deterministic report differences are recorded in the measured semantic receipt: `docs/public_preview_report.md`: line 14; `docs/key_paper_coverage_report.md`: line 7. No other generated difference is authorized.

## Recomputed corpus and Batch B accounting

| Measure | Current value |
| --- | ---: |
| Public / formal / mapped / unmapped | 674 / 557 / 613 / 61 |
| Relationships / unique pairs | 1410 / 1410 |
| Detection / source attribution / localization | 621 / 84 / 45 |
| Method / dataset / benchmark / survey / analysis study | 578 / 135 / 92 / 21 / 82 |
| Original Batch B actions / historical papers | 159 / 148 |
| Historical unresolved | 145 → 143 |
| Active-public unresolved | 143 → 141 |
| Distinct affected public papers | 132 → 130 |

All totals are recomputed from authoritative data and the original review ledger. Only R100 and R400 close. Neither paper has another original pending Batch B action; the distinct-paper result is calculated, not assumed. All other pending questions, review IDs and prior decisions remain. No R100 localization action is added. Batch C's same **13 deferred debts** and the separate **39-paper import inventory** remain unchanged.

## Historical evidence, preservation and validation boundary

The full original manifest and report bytes are losslessly authenticated in `evidence_only_packet_archives` using deterministic gzip/base64 payloads. All original scientific reviews, source fingerprints, exact experimental tables, independent checks, retrieval counts, failures, range receipts, release restrictions and R100's separate localization observation remain intact. Original provisional and administrative states are preserved as historical snapshots; accepted dispositions are recorded in new fields. The complete original report follows verbatim.

Any narrow historical/current-state test repairs are restricted to individually reviewed and fingerprinted allowlist extras. Historical expected counts, hashes and checksum-locked fixtures remain preserved; the shared current dataset/benchmark totals become **135 / 92**. Current successor regressions must check the complete two-paper delta, prior decision prefix and unchanged task/scope/relationship identities. No frozen historical receipt is rewritten to accommodate a new live total.

The primary checkout, its pre-existing untracked files, all **128 protected files**, **49 frozen NeurIPS artifacts**, **119 ignored operational inputs**, prior B1A–I receipts, Batch C debts and separate import inventory remain protected. Final measured integrity, validation and publication gates are pending below; no publication is claimed at this stage.

<!-- B1J_ADJUDICATION_VALIDATION_START -->
**Focused validation passed: 397 ordinary tests and 12 subtests**, including B1J regression coverage; zero failures/errors/skips. All four current-scope validators passed with zero errors. All reported validator warnings remain visible in the manifest.

**The complete repository suite ran once and passed 2050 ordinary tests and 389 subtests**; zero failures/errors/skips and 2 existing warnings. Python 3.14.7, pytest 9.1.1, pytest-subtests 0.15.0 and Node 24.19.0 were used with documented offline fixtures and authorized localhost. All 4599 input/output paths were unchanged after completion.

After the full suite, **two sequential offline export verification passes passed**. All 4599 compared paths, seven deterministic outputs and 119 operational inputs remained byte-identical in each pass. Both read-only fixture checks verified 117 inputs, creating none. One initial correction export and exactly two verification exports completed without parallel exporters. `EXPORT_REPRODUCIBLE = 1`.

The independent semantic/preservation gate passed 67/67 checks. Exactly R100 and R400 change in 2 public records and 3 existing map records. All 672 other papers, 1,407 other map records and 1,410 relationship identities remain unchanged. Exactly 2 terminal decisions close only R100/R400. The complete original 44+44/34 evidence gates and 32/41/31 scientific checks remain preserved. R100 localization remains a non-authoritative observation.

`FOCUSED_FAILURES = 0`

`VALIDATOR_ERRORS = 0`

`FULL_SUITE_FAILURES = 0`

`EXPORT_REPRODUCIBLE = 1`

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

The complete suite and both sequential exports ran on byte-identical scientific data, code, original evidence and pending-receipt packet bytes. Only this manifest and report completion-receipt fields are finalized afterward. They are not exporter inputs. A final read-only gate verifies final receipt bytes and rechecks every invariant. No additional full-suite or export run after its own receipt is claimed.

The packet is validated for the explicit 12-file allowlist. Publication remains pending until normal fast-forward push and remote-SHA verification.
<!-- B1J_ADJUDICATION_VALIDATION_END -->

Required final integrity flags: `UNEXPECTED_CHANGED = 0`, `FROZEN_NEURIPS_CHANGED = 0`, `PREEXISTING_LOCAL_FILES_CHANGED = 0`, `IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`. These are requirements until independently measured by the final gate.

Planned single commit subject: `fix: classify R100 dataset and R400 benchmark`. Publication requires a safe normal fast-forward after a fresh fetch, exact remote SHA verification, `HEAD == origin/main`, ahead/behind **0/0**, a clean isolated tree/index and an unchanged primary checkout. The containing commit supplies its own identity; external post-push receipts verify the actual SHA without circular self-reference.

The exact reviewed explicit allowlist is:

- `data/curated/paper_taxonomy.csv`
- `data/curated/papers.csv`
- `data/curated/review_decisions.csv`
- `data/raw/corpus_quality_batch_b_wave_b1j_2026_10_21/evidence_manifest.json`
- `docs/corpus_quality_batch_b_wave_b1j_2026_10_21.md`
- `docs/key_paper_coverage_report.md`
- `docs/public_preview_report.md`
- `tests/baseline_expectations.py`
- `tests/test_corpus_quality_batch_b_wave_b1i.py`
- `tests/test_corpus_quality_batch_b_wave_b1j.py`
- `web/data/public_preview_map_data.json`
- `web/data/public_preview_papers.json`

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Preserved complete evidence-only report

Everything following is the original evidence-stage report, preserved verbatim. Its provisional decisions, then-current counts, zero-authoritative-change observations and untracked-file state describe that earlier stage. Accepted dispositions above supersede only administrative status. All scientific findings, quantitative counterexamples, source restrictions, original validation and future localization observation remain part of the audit trail.

---

# Batch B Wave B1J — dataset and benchmark evidence

Evidence-only review of exactly **R100 and R400** at fetched published baseline `1221cf72f8f77ac3430cad49a49d074d82b36ec2`. No authoritative taxonomy, task, bibliography, inclusion, affiliation, institution, review decision or public export is changed. Both original actions remain pending.

| Review | Current complete types | Provisional proposal |
|---|---|---|
| R100 | `method` | `PROPOSE_CORRECTION`: `method;dataset`, pending maintainer acceptance |
| R400 | `method;dataset` | `PROPOSE_ADD_BENCHMARK`: `method;dataset;benchmark`, pending maintainer acceptance |

## Locked policies

**T2**: localization requires an evaluated spatial forensic prediction task such as pixel-, mask-, patch-, region-, or equivalent spatial prediction of synthetic/generated/edited content. Artifact segmentation qualifies. Attention maps, saliency maps, explainability heatmaps, or visualization alone do not qualify.

**R1**: Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.

**R2**: Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

Scientific evidence sufficiency, public asset availability and maintainer acceptance are separate judgments. The R100 localization observation is outside this research-type adjudication; it creates no task action and changes no historical denominator.

## R100 — FakeXplain / FakeXplained evidence review

This is an evidence-only review of the unresolved original Batch B research-type action R100. The provisional proposal is to **add `dataset` while retaining `method`**, producing `method;dataset`. Scientific support for a substantive dataset contribution is high. Actual public release and annotation licensing remain unverified because the author-linked repository is empty at inspection. Maintainer acceptance remains pending; no authoritative field, task label or terminal decision has been changed.

### Identity and source

Canonical paper: `curated:411724cd949b78c1af6a` — *FakeXplain: AI-Generated Image Detection via Human-Aligned Grounded Reasoning*, ICLR 2026. Authors: Yikun Ji, Yan Hong, Qi Fan, Jun Lan, Huijia Zhu, Weiqiang Wang, Liqing Zhang, Jianfu Zhang. Current tasks: `detection`; current research types: `method`; active public inclusion. Canonical DOI/arXiv fields are empty and remain so.

The [official ICLR proceedings manuscript](https://proceedings.iclr.cc/paper_files/paper/2026/file/701ec28790b29a5bc33832b7bdc4c3b6-Paper-Conference.pdf) is a complete **22-page** conference PDF, **2,117,533 bytes**, SHA-256 `dc58c87cd13f7ad52102cc6f6b9c5f95f35a7ae24c0c1629bc39de01ad38aed9`. Its title, eight authors, institution block and ICLR 2026 header match the canonical work. PDF metadata records creation/modification `D:20260228101416Z`. All main text and Appendices A–H were read; pages 3, 4, 5, 8, 9, 16, 18, 21 and 22 were rendered and inspected for layout-sensitive claims.

The one new manuscript request returned HTTP 200, curl exit 0, Content-Length/download 2,117,533 bytes, after 112.671 seconds. No range continuation, alternate paper, separate supplement, data or weights were retrieved. Manuscript, headers, transport JSON and text remain operational files outside the repository.

Before and during recovery, local raw/registry evidence was inspected. A read-only scan of isolated and primary data trees covered 2,213 PDF/gzip paths, 1,078 distinct raw hashes and 48 PDF identities, including decompressed PDF captures. The related local file `data/raw/systematic_tier1_2026_09/86824f5539d4ac814197.pdf` is the earlier *Interpretable and Reliable Detection of AI-Generated Images via Grounded Reasoning in MLLMs*, arXiv 2506.07045v1, 8 June 2025, SHA-256 `954dff240528e18c51e0dcc37ab877ab5167b577b9f841b40412e1833b05d6ab`. Only its identity was checked; its title and author-name ordering differ. It was not downloaded again or assumed equivalent to the official 2026 paper. Existing ICLR index metadata confirms the final work but is not a full manuscript. A 2024 index hash collision concerns an unrelated paper.

### Original question and governing policies

The original `LIKELY_FIX`, medium-confidence R100 question asks whether FakeXplained is a contributed annotated image dataset with boxes and captions, requiring the primary contribution/evaluation sections before changing labels. The original proposal is `method` → `method;dataset`; this action remains pending.

- **R1**, `docs/corpus_quality_batch_c_decision_sheet_2026_10_05.md:326`: Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.

- **R2**, `docs/corpus_quality_batch_c_decision_sheet_2026_10_05.md:327`: Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

- **T2**, `docs/corpus_quality_batch_c_decision_sheet_2026_10_05.md:324`: localization requires an evaluated spatial forensic prediction task such as pixel-, mask-, patch-, region-, or equivalent spatial prediction of synthetic/generated/edited content. Artifact segmentation qualifies. Attention maps, saliency maps, explainability heatmaps, or visualization alone do not qualify.


### Separate contributions

**Method:** FakeXplainer fine-tunes MLLMs using SFT followed by progressive GRPO; structured verdict, region-caption and tag outputs; and classification, output-format and bounding-box IoU rewards. The method contribution remains independently supported (Section 4, pp. 5–6).

**Dataset:** FakeXplained contains 8,772 selected synthetic images with original region-caption and global-tag annotations. It is a separately named major contribution with detailed construction and quality control, annotation-component ablations, and demonstrated use for other detectors.

**Benchmark:** The paper uses same-data four-fold accuracy/IoU comparisons and external out-of-distribution tests. These do not alone establish a separately substantive benchmark under R2. No additional benchmark type is proposed within this bounded R100/R1 review.

FakeXplainer uses Qwen2.5-VL-Instruct, SFT and progressive GRPO. Verdict accuracy and output-format rewards each have weight 1; the box-overlap weight increases linearly from 0.5 to 1. The training grounding reward is `min(1, 1.1×IoU)`. Regions, captions, image tags and verdict are emitted as structured text. This is independently substantive method evidence, so `method` remains supported.

### Dataset questions — complete findings

1. **Original images.** The paper reports 8,772 original selected AI-generated images, without real images inside FakeXplained itself (Section 3.1, p. 4; Appendix A, p. 15; A.4, p. 18). It reports a mean of 5.42 region-caption pairs per image, not an exact total annotation count.

2. **Generator models.** Section 3.1 (p. 4) states 28 generators across diffusion, GAN, DiT and other families. Table 1 (p. 8) names 27: 15 diffusion (DALL·E 2/3, DDIM, DDPM, FLUX.1-dev/schnell, GLIDE, Midjourney v4/v5, SD 1.4/1.5/2.1/3.5 Large/3.5 Large Turbo, VQDM); 4 GAN (BigGAN, GALIP, VQGAN, StyleGAN-XL); 4 DiT (PixArtAlpha/Delta/Sigma, DiT); 4 other (VAR, Infinity, MaskGIT, LlamaGen). This published discrepancy is unresolved. Per-generator image counts, seeds and checkpoint digests are not specified.

3. **Source provenance and prompts.** Section 3.1 (p. 4) describes generation across 1,000 ImageNet categories using a realistic-image/class-name prompt and MS COCO 2017 captions. Most images are 512×512; native 1024×1024 outputs are downsampled before annotation. Manual screening removes low-quality or unrecognizable examples and images described as having no real-looking part. Exact category/caption assignments, prompts, seeds and source-image identifiers are unavailable. Table 1’s real-image row cites ImageNet (Deng et al., 2009), but exact real-image identifiers and sampling are not supplied.

4. **Bounding box format.** Section 3.2 (p. 4) represents each region as (R_i,T_i): a rectangular box and associated text. Figures 2 (p. 3) and 8 (p. 18) illustrate textual integer-coordinate boxes emitted with captions inside structured reasoning. The reported mean is 5.42 box-caption pairs per image. An exact machine-readable file schema and coordinate normalization convention are not fully specified; actual annotation files were unavailable.

5. **Regional captions.** Section 3.2 (p. 4) and Appendix A.1 (p. 16) pair each box with a concise anomaly/artifact explanation. The instructions require a noun-led description confined to visible content in the selected region. Examples include physical/common-sense violations, repetitive patterns and illegible text. Figure 9 (p. 20) compares human and model region-caption examples.

6. **Global tags.** Appendix A.1 (p. 16) defines six independently assignable tags: perspective errors, artistic styles, unknown objects, structure/attribute errors, texture errors and other anomalies. Images may receive zero or several tags. Rare or unfamiliar objects are not automatically impossible. Artistic style is an image-level judgment; a small local stylized part alone should not trigger it.

7. **Guidelines and experts.** Section 3.2 (p. 4) reports 23 trained annotators. Appendix A.1 (pp. 15–16) describes prior photography experience, exposure to generated images, basic photographic literacy and a standardized handout with positive/negative examples and box/tag instructions. This establishes trained human annotators, not independently certified specialist credentials.

8. **Manual vs automated stages.** Sections 3.1–3.3 and Appendix A.1 describe manual image screening, human region/caption/tag annotation, manually curated control references and algorithmic IoU/tag checks. However, Section H (p. 22) explicitly says MLLMs generated or assisted annotation generation. The assisted stages, records, fraction, models and human verification are not quantified. It is therefore unsupported to call the entire dataset purely manual.

9. **Agreement and quality control.** Section 3.3 (p. 5) and A.1 (p. 16) compare 5% of annotated images with research-team controls. An annotator’s preceding work is rejected if average box IoU is below 20% or tag agreement below 1/3; the fraction was visually verified, not misread as 13. Final control-reference IoU is 42.35% and tag agreement 79.67%. These are control-reference quality results, not formal all-pair inter-annotator agreement or kappa/alpha statistics. Caption reliability is not separately quantified.

10. **Partitions.** Section 5.2 (p. 7) defines four-fold cross-validation: 75% synthetic images plus an equal number of real images for training; 25% synthetic images plus equal real images for testing. If all 8,772 images are divided exactly, arithmetic gives 6,579 synthetic training and 2,193 synthetic test images per fold; these are derived figures, not published index files. Separate validation indices, seeds, stratification, deduplication and SFT-versus-GRPO allocations are not fully specified. The 5% quality-control subset is annotation validation, not an independently specified model-validation partition. Earlier-preprint SFT/GRPO split percentages are not transferred to this version.

11. **External evaluation relationship.** Table 3 (p. 8) and Table 6 (p. 19) evaluate FakeClue, Chameleon, GPT-Image-1, FaceForensics++ and MMFR (eval) as external detection datasets. They are not included in the original 8,772-image FakeXplained count. Table 3 reports accuracy of 85.2%, 84.3%, 80.1%, 86.4% and 87.4%, respectively. No external spatial ground truth or localization result is established there.

12. **Reuse beyond fakexplainer.** Section 5.1 (p. 7) trains ObjectFormer and SegFormer on FakeXplained, converting boxes into binary masks. Image classifiers use image-level labels. Table 2 (p. 8) also uses several MLLM backbones. This demonstrates that the annotated resource can support architectures other than FakeXplainer, independently of its proposed method. Actual outside-team reuse cannot be verified without released assets.

13. **Release and license.** The abstract claims code and data are available at the author-linked Gennadiyev/FakeXplain repository. On 2026-10-21, GitHub HTML explicitly showed an empty repository; repository metadata returned HTTP 200, size 0, license null and last push 2026-02-14T03:10:49Z; the contents endpoint returned HTTP 404 with an explicit empty-repository message. No README, annotation files, splits, data, dataset license or commit could be inspected. This is a point-in-time failure to verify release at the supplied link, not proof that no alternative authorized release exists. No alternative assets were sought.

14. **Dataset specific experiments.** Table 4 (p. 9): full model 98.2% accuracy/36.0% IoU, BLEU-2 0.267 and ROUGE-L 0.251; no-box 95.2% accuracy; no-caption 94.2% accuracy/26.5% IoU; no-tags 96.2% accuracy/35.8% IoU; label-only 93.7% accuracy. Table 6 gives label-only external accuracy 60.3%/64.0%/61.2% versus full 80.1%/86.4%/87.4% on GPT-Image-1/FF++/MMFR. These ablate annotation components. They are not a controlled substitute-dataset experiment: FakeShield uses pretrained weights and LEGION uses SynthScars.

15. **Limitations.** Important limits are subjective human/common-sense criteria; control-reference rather than exhaustive pixel ground truth; unspecified MLLM annotation assistance; one annotation language; visible-artifact selection; no annotated real-image component; ImageNet/COCO content bias; the 28-versus-27 generator discrepancy; incomplete newest-generator coverage; unavailable release/license/splits; unspecified spatial matching and leakage checks; and restricted medical/industrial/artistic-domain evaluation. Fully realistic synthetic images lacking visible flaws are explicitly outside the authors’ stated scope (Section 6, p. 10; Appendix F, p. 22).


### Numerical and experimental checks

Section 5.2 (p. 7) defines four-fold cross-validation with balanced real/generated training and test sets. Detection accuracy and region overlap are separate metrics; IoU is reported on generated images. Table 1 (p. 8) reports:

| Method | Accuracy | Artifact-region IoU |
|---|---:|---:|
| FakeXplainer | 98.2% | 36.0% |
| ObjectFormer | 95.4% | 29.9% |
| SegFormer | 94.5% | 28.9% |

The aggregate result must not be generalized to every generator. In Table 1, ObjectFormer has **42.9% IoU on LlamaGen versus FakeXplainer’s 35.1%**. On GALIP, FakeXplainer has **88.2% accuracy**, below **94.1%** for both ObjectFormer and SegFormer. DMD exceeds it on SD 1.4 (97.0% versus 96.8%); ComFor exceeds it on StyleGAN-XL (98.0% versus 96.0%). The table’s named generator rows total 27, whereas Section 3.1 states 28. These discrepancies are retained, not silently repaired.

Table 2 (p. 8) gives Qwen2.5-VL-32B before/after accuracy **73.4% → 98.2%**, IoU **4.4% → 36.0%**, BLEU-2 **0.080 → 0.267** and ROUGE-L **0.076 → 0.251**. Accuracy also improves for InternVL3-8B (58.4% → 92.8%), InternVL3-14B (56.8% → 95.1%), Ovis2.5-9B (62.4% → 90.9%) and MiMo-VL-7B-RL (51.5% → 92.0%). This supports transfer of the training resource across architectures, while not independently verifying released assets.

Table 4 (p. 9) measures the value of annotation components:

| Configuration | Accuracy | IoU |
|---|---:|---:|
| Full | 98.2% | 36.0% |
| No bounding boxes | 95.2% | Not reported |
| No captions | 94.2% | 26.5% |
| No tags | 96.2% | 35.8% |
| Binary labels only | 93.7% | Not reported |
| SFT only | 89.3% | 4.3% |
| Constant GRPO grounding weight 1 | 93.7% | 26.5% |
| Constant GRPO grounding weight 0.5 | 97.4% | 22.3% |

These are annotation-component ablations, not a matched experiment replacing FakeXplained with an alternative annotation source. Section 5.3 contains prose percentages and a fixed-reward IoU description that do not consistently agree with Table 4. The exact table values above govern the evidence record.

Table 3 (p. 8) reports external detection accuracy **85.2% FakeClue, 84.3% Chameleon, 80.1% GPT-Image-1, 86.4% FaceForensics++ and 87.4% MMFR (eval)**. Table 6 (p. 19) gives label-only accuracy **60.3% / 64.0% / 61.2%** on the last three, versus **80.1% / 86.4% / 87.4%** with full annotations. No external localization score is established. Comparison conditions differ: FakeShield uses author-provided pretrained weights; LEGION follows its SynthScars training protocol. They are not all equally trained on FakeXplained.

The preference study reports **1,525 non-neutral votes**; human annotations are preferred over FakeXplainer in **52.9%** of comparisons. The reported **99.75%** preference against LEGION/FakeShield is subjective preference, not formal reliability of annotations. Table 7 (p. 21) shows overlapping tag prevalence: structure/attribute errors 80.52%, texture errors 42.65%, artistic style 12.18%, other anomalies 5.78%, unrecognizable objects 3.12% and perspective errors 1.16%.

### Release and reuse boundary

The [author-linked project](https://github.com/Gennadiyev/FakeXplain) was inspected because the paper’s abstract asserts that code and data are available there. On 21 October 2026 the GitHub page explicitly showed an empty repository. The [repository metadata API](https://api.github.com/repos/Gennadiyev/FakeXplain) returned HTTP 200, repository ID `1157610337`, size `0`, no language, `license: null`, creation `2026-02-14T03:10:49Z`, and the same last-push timestamp. The [contents API](https://api.github.com/repos/Gennadiyev/FakeXplain/contents/) returned HTTP 404 and explicitly described an empty repository. Both transport/header and response-checksum receipts were retained.

There is no README, dataset card, annotation file, split definition, evaluation code, dataset license or commit available to pin at that supplied location. No alternative resource was sought. This does not establish universal or permanent unavailability. It does mean that the paper’s public-release claim cannot be verified from the author link and that code permission cannot be substituted for dataset permission. Scientific reuse within the paper is established by the separately trained ObjectFormer/SegFormer and multiple MLLM backbones; practical outside-team reuse remains unverified.

### Policy assessment and provisional proposal

**R1 is scientifically supported.** FakeXplained is an explicitly named original contribution with independently described construction, annotations, quality control, generic region-caption/tag structure, component ablations and training of other models. It is more than incidental samples generated solely to run one method’s experiments. The locked policy allows substantive construction/curation/systematic provision and does not impose an additional mandatory working-download or permissive-license test. The empty release endpoint remains a major availability limitation, not a fact to conceal or a new policy to invent.

**Provisional outcome: `PROPOSE_CORRECTION` — add `dataset`, retain `method`; proposed complete set `method;dataset`.** Scientific confidence is high; actual public resource availability is not verified. Maintainer acceptance is pending and authoritative remediation would be required if accepted. No review is closed.

**No benchmark type is proposed.** The available generic cross-validation and comparison tables primarily validate this method and resource; they alone do not establish a separate R2 contribution. This bounded R1 action does not silently add another research-type review. Lack of newly released code is not itself a disqualifier under R2.

### OUT_OF_SCOPE_TASK_TAXONOMY_OBSERVATION

A separate future **localization** review is recommended under locked T2. FakeXplainer explicitly predicts rectangular artifact regions with captions and scores those predictions against human artifact-region annotations. This is a substantive scored spatial output, beyond attention maps or unscored explainability visualization. Sections 4 and 5.2, Figures 2 and 5, and Tables 1/2/4 jointly establish the prediction, forensic ground truth and spatial metric.

The ground truth marks visible synthesis artifacts or common-sense anomalies; it is not an exhaustive map of all generated pixels or a manipulated-versus-pristine edit mask. Box-to-mask conversion is used for segmentation baselines. The paper reports 36.0% IoU, but does not fully specify multi-box correspondence/union aggregation, handling of missing regions, coordinate conventions, or any application of the relaxed reward formula during test scoring. Evaluation code was unavailable at the author link. These implementation limitations should accompany a future task review.

**Current tasks remain `detection`. No new Batch B action is created, no denominator is changed, and no existing task action is closed.** The observation is separated from the R100 dataset adjudication candidate.

### Remaining scientific limitations

- Sections 3.1–3.3 and Appendix A.1 describe manual image screening, human region/caption/tag annotation, manually curated control references and algorithmic IoU/tag checks. However, Section H (p. 22) explicitly says MLLMs generated or assisted annotation generation. The assisted stages, records, fraction, models and human verification are not quantified. It is therefore unsupported to call the entire dataset purely manual.

- Section 5.2 (p. 7) defines four-fold cross-validation: 75% synthetic images plus an equal number of real images for training; 25% synthetic images plus equal real images for testing. If all 8,772 images are divided exactly, arithmetic gives 6,579 synthetic training and 2,193 synthetic test images per fold; these are derived figures, not published index files. Separate validation indices, seeds, stratification, deduplication and SFT-versus-GRPO allocations are not fully specified. The 5% quality-control subset is annotation validation, not an independently specified model-validation partition. Earlier-preprint SFT/GRPO split percentages are not transferred to this version.

- The abstract claims code and data are available at the author-linked Gennadiyev/FakeXplain repository. On 2026-10-21, GitHub HTML explicitly showed an empty repository; repository metadata returned HTTP 200, size 0, license null and last push 2026-02-14T03:10:49Z; the contents endpoint returned HTTP 404 with an explicit empty-repository message. No README, annotation files, splits, data, dataset license or commit could be inspected. This is a point-in-time failure to verify release at the supplied link, not proof that no alternative authorized release exists. No alternative assets were sought.

- Important limits are subjective human/common-sense criteria; control-reference rather than exhaustive pixel ground truth; unspecified MLLM annotation assistance; one annotation language; visible-artifact selection; no annotated real-image component; ImageNet/COCO content bias; the 28-versus-27 generator discrepancy; incomplete newest-generator coverage; unavailable release/license/splits; unspecified spatial matching and leakage checks; and restricted medical/industrial/artistic-domain evaluation. Fully realistic synthetic images lacking visible flaws are explicitly outside the authors’ stated scope (Section 6, p. 10; Appendix F, p. 22).

- No assets or code were executed; dataset completeness, content independence and numerical reproducibility were not verified. The official 2026 PDF is not assumed equivalent to the canonical OpenReview revision or retained 2025 preprint.

- Method comparison conditions differ: FakeShield uses pretrained weights and LEGION trains on SynthScars. Section 5.1 states 8 A100 GPUs for SFT and 16 for GRPO, whereas Appendix B.2 describes 41.0 hours on 8 A100 GPUs overall. No independent reproduction was performed.


The most important annotation-provenance contradiction is Section H (p. 22): it expressly acknowledges MLLM generation/assistance of annotations, whereas the main methods emphasize trained-human annotation. The extent and verification of that assistance remain unspecified. Control-reference quality scores cannot eliminate hallucination, subjectivity or selection bias. No code, image assets, annotation files or checkpoints were executed or downloaded, and no numerical reproduction or dataset leakage/content-independence check was attempted.

### Retrieval accounting and administrative boundary

New complete scientific manuscripts: **1**; PDF transport requests/responses: **1/1**, HTTP 200, exit 0; range requests: **0**; new alternate manuscripts/supplements: **0**; dataset or weight payload downloads: **0**. Author release inspection: one GitHub HTML lookup and two metadata-only API responses. A retained older preprint was identity-checked locally, without retrieving it or treating it as the final version. All review outputs here are under `/private/tmp/b1j-evidence-2026-10-21/r100/`. No repository edit, terminal decision, export, test-suite invocation, staging, commit or push was performed by this reviewer.

#### R400 — Secret Lies in Color / FakeART

**Provisional proposal: add `benchmark`, yielding `method;dataset;benchmark`.** Scientific contribution evidence is sufficient; overall confidence in the taxonomy proposal is medium and maintainer acceptance is pending. Confidence is high that the published evaluation contribution is separate from CoD, while exact practical reproducibility is unverified. The initial worker judgment was medium-high; independent cross-review favored a medium overall rating because baseline comparability and exact split reproduction are incomplete. No authoritative edit or review closure is applied. Tasks remain `detection`.

**Identity and original question.** Canonical ID `curated:b2fccf1dd66cc2d64374`. The original pending R2 action asks whether FakeART is explicitly contributed as a cross-domain benchmark rather than merely reused as evaluation data. Current types are `method;dataset`. The DOI `10.1109/CVPR52734.2025.01255`, exact title, all ten authors, CVPR 2025 conference identity and printed pages 13445–13454 match the official CVF PDF and the DOI-matched Crossref record. The author publication page confirms the same work. DOI resolution reaches IEEE document 11093000 but the page requires JavaScript; no repeated IEEE retrieval was attempted.

**Official manuscript.** The [CVF CVPR 2025 Main Conference PDF](https://openaccess.thecvf.com/content/CVPR2025/papers/Jia_Secret_Lies_in_Color_Enhancing_AI-Generated_Images_Detection_with_Color_CVPR_2025_paper.pdf) is 10 pages and 8,738,548 bytes; SHA256 `6fab4d3e07ea14ea2c111f4c5b87635bc5c587d485e2fb6e73b380bd0e5bab70`. It was read in full, including all reference pages. PDF pages 6–8 (printed 13450–13452) were also rendered and visually checked. This is the official CVF conference version. A separate IEEE-hosted PDF or another version was not retrieved or byte-compared.

**Three independent contribution roles.** CoD is the technical method: repeated noisy color-depth quantization/restoration produces a color-difference map, and two convolutional feature paths feed a lightweight ResNet binary authenticity classifier. The abstract rounds the model size to 1.4M parameters; §4.2 reports 1.44M. FakeART is the contributed curated/generated data resource. Its separately stated photo-to-artwork train/test challenge, fixed source collections and test-model subsets, ACC threshold and comparative protocol establish the additional evaluation-framework role under locked R2. An arbitrary detector can be assessed without adopting CoD. The benchmark proposal does not follow merely from author terminology or the presence of many results.

**All fifteen bounded questions.**

1. **Scientific motivation.** FakeART is a separately stated evaluation resource for generalization from natural photographs to human-created artworks and images from newer generators. The aim is to reduce reliance on semantic/style features, not merely provide CoD training examples. The stronger claim that the design eliminates semantic confounding is not experimentally established. Locator: §1, PDF p.1 / printed p.13445; contribution list p.2 / 13446; §4.1.2 p.6 / 13450; §5 p.8 / 13452.

2. **Training and evaluation domains.** Training uses natural photographic scenes from COCO and LSUN plus SD v1.4 and ProGAN synthetic images. Testing uses human-created WikiArt artworks and corresponding artistic synthetic images. Figure 5 visibly distinguishes photographic training examples from artistic test examples. Locator: §4.1.2 and Fig.5, PDF p.6 / printed p.13450.

3. **Source datasets and image provenance.** COCO and LSUN are named training sources and WikiArt the source of real test artworks. The paper does not specify exact source-image IDs, download dates, selection seeds, prompts, image-to-image versus text-to-image generation details for each artwork, or content deduplication. Corresponding synthetic images must not be interpreted as a verified one-to-one pairing. Locator: §4.1.2 and Fig.5, PDF p.6 / printed p.13450.

4. **Real and generated image counts.** The text states 50,000 images from COCO and LSUN for the training collection and 7,000 real WikiArt artworks for evaluation. The exact number of generated training images, balance between SD v1.4 and ProGAN, generated test counts per model, total test size, and complete class balance are not given. No 49,000-synthetic or 56,000-test total is inferred. Locator: §4.1.2, PDF p.6 / printed p.13450.

5. **Generator families and model versions.** Training explicitly names GAN-based ProGAN and Stable Diffusion v1.4. Fig.5 and Table 4 name seven diffusion test variants: SD-1.5, SD-2.1, SD-Turbo, SD-XL, SD-3, PlayGround-2.5, and PixArt-α. These are seven model labels, not seven independently established generator families. Exact checkpoint revisions and sampling configurations are not specified. Locator: Fig.5 p.6 / 13450; Table 4 p.8 / 13452.

6. **Newer unseen generators.** The seven Table 4 test labels differ from the two §4.1.2 training model labels; newer diffusion systems are therefore part of the declared held-out-generator challenge. SD1.4 and SD1.5 are related variants; independence of generator lineages or pretraining exposure is not established. Locator: §4.1.2 p.6 / 13450; Table 4 p.8 / 13452.

7. **Photographic versus artwork domain.** Training natural photographs and testing on human-created and generated artworks are explicit. Figure 5 shows that the negative real class is artwork, not ordinary camera photographs. This is an authenticity decision about human versus generated visual works; human-created does not mean photographic. Locator: Fig.5 and §4.1.2 p.6 / 13450.

8. **Dataset construction and train/test protocol.** The paper establishes a reusable train-domain/test-domain rule, fixed source datasets, two training generator labels, seven evaluation generator labels, binary real/fake outputs, ACC at threshold 0.5 and AP/mAP. A validation partition, immutable sample lists, split seeds, precise train fake counts, prompt registry and all baseline training/checkpoint instructions are not established. Locator: §3.3 p.5 / 13449; §4.1.2–4.2 p.6 / 13450; Table 4 p.8 / 13452.

9. **Isolation of semantic and stylistic shifts.** The design imposes a substantial joint shift, but no complete factorial experiment holds semantic content, visual style, renderer, source collection, image processing and generator constant while changing one factor. It tests cross-domain stress; it does not isolate a causal effect of style or prove absence of high-level semantic shortcuts. Locator: §4.1.2 p.6 / 13450; §4.4 and Table 4 p.8 / 13452.

10. **Reusable comparative framework.** FakeART is introduced in the contribution list separately from the CoD feature and network, has a dedicated dataset/protocol section, and fixes a transferable photo-to-art challenge plus metrics, threshold and generator-wise comparison for six independent baseline detectors and CoD. Another detector can be evaluated under that task without adopting CoD. This protocol/resource role, rather than the number of table entries or authors' benchmark wording, supports R2. Locator: Contributions p.2 / 13446; §4.1.2–4.1.3 p.6 / 13450; §4.4/Table 4 p.8 / 13452.

11. **Actual metrics.** §4.1.3 specifies ACC and mean average precision, with a fixed 0.5 threshold for ACC. Table 4 prints ACC/AP pairs per generator and mean ACC/mAP; §4.4 confirms CoD 66.5% average accuracy and 68.2% average precision. The exact AP integration implementation and positive-class convention are not given. Tables 1–3 captions refer only to accuracy although cells contain paired scores. Locator: §4.1.3 p.6 / 13450; Tables 1–3 p.7 / 13451; §4.4/Table 4 p.8 / 13452.

12. **Performance change from conventional datasets.** CoD means are 98.2/99.6 on the GAN benchmark, 97.5/99.4 on Ojha, 96.2/99.4 on GenImage, and 66.5/68.2 on FakeART. The GenImage-to-FakeART difference is 29.7 ACC percentage points and 31.2 AP percentage points. These are descriptive comparisons across different published datasets/setups, not controlled style-only effects. Locator: Tables 1–3 p.7 / 13451; Table 4 p.8 / 13452.

13. **Identical training and operating conditions.** A shared FakeART evaluation task, seven test variants and global ACC threshold are specified. §4.2 describes CoD training with Adam, learning rate 1e-4, batch 256, weight decay 0.01,40 epochs, 256×256 crops and two A10 GPUs. It does not establish identical retraining schedules, data budgets, checkpoint versions, augmentation or score calibration for every baseline. Table 4 comparability is therefore reported, not independently verified under identical conditions. Locator: §4.2 p.6 / 13450; §4.4/Table 4 p.8 / 13452.

14. **Public resource and implementation availability.** The exact author publication page links its Data button to huggingface.co/datasets/wechat-prcap/domain_dataset. The rendered host page lists 22.1GB but no dataset card and a streaming viewer error. File-tree inspection failed, CLI metadata failed with SSL EOF and a single exact API request timed out at connection with 0 bytes. No data files, splits, image samples, evaluation code, license, immutable release revision or completeness were verified; no assets were downloaded. The paper itself remains a reusable framework specification. Locator: Author publication page exact title entry, observed 2026-10-21; author-linked dataset host page observed 2026-10-21; actual failures in retrieval receipts.

15. **Weaknesses and reproducibility limits.** Unknown synthetic counts/class balance, prompts, IDs, validation lists, sampling settings and baseline retraining details limit exact replication and calibration checks. Simultaneous semantic/style/generator/source shifts confound causal interpretation. Source/codec/resolution shortcuts, pretraining contamination, artwork overlap and generator-training leakage were not audited. The paper provides no seed-wise uncertainty or statistical significance. In prior-benchmark training it states350,000 ProGAN synthetics but also20 classes×18,000=360,000; §4.3 mentions four ProGAN datasets. Table 1 CoD GAN ACC98.2 and Table 5 combined-image/color GAN ACC98.7 are unexplained. Main-method CLIP use is also not fully clear across §3.3, §4.2 and Table 5 variants. These observations constrain reproducibility and strong superiority claims without automatically negating the R2 protocol contribution. Locator: §4.1.1 p.5 / 13449; §4.2 p.6 / 13450; §4.3/Table 1 p.7 / 13451; Table 5 p.8 / 13452.

**Table 4: exact FakeART results** (PDF p.8 / printed 13452; visually verified). Each entry is ACC/AP in percent. Section 4.1.3 calls the measures ACC/mAP, with ACC threshold 0.5; the reported means are transcribed rather than treated as a verified evaluation implementation.

| Detector | SD-1.5 | SD-2.1 | SD-Turbo | SD-XL | SD-3 | PlayGround-2.5 | PixArt-α | Reported mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CNNDet | 45.1/50.4 | 42.9/43.4 | 48.7/47.6 | 49.1/46.4 | 37.5/36.1 | 37.3/40.6 | 38.3/39.7 | 42.7/43.4 |
| UFD | 36.7/38.5 | 44.1/42.3 | 24.5/34.6 | 27.3/34.1 | 32.6/32.1 | 35.6/37.3 | 28.9/31.2 | 32.8/35.7 |
| PatchCraft | 70.2/71.4 | 66.8/68.3 | 55.5/56.3 | 53.0/55.1 | 56.3/57.7 | 57.3/58.2 | 51.6/49.3 | 58.7/59.5 |
| NPR | 63.5/63.7 | 63.1/62.9 | 52.2/52.8 | 42.5/47.6 | 55.9/57.1 | 47.5/46.8 | 51.0/51.7 | 53.7/54.6 |
| FatFormer | 68.3/69.4 | 66.2/67.8 | 57.7/58.6 | 50.1/53.2 | 58.7/56.9 | 53.2/58.6 | 51.2/50.3 | 57.9/59.3 |
| SAFE | 63.7/66.3 | 62.8/65.2 | 54.6/57.8 | 53.7/55.6 | 51.4/52.3 | 53.7/55.6 | 54.6/56.9 | 56.4/58.4 |
| CoD (Ours) | 76.8/78.9 | 72.1/73.4 | 65.8/66.2 | 61.9/63.4 | 61.7/62.8 | 62.3/64.6 | 65.2/68.1 | 66.5/68.2 |

CoD exceeds the strongest other reported mean, PatchCraft, by 7.8 ACC points and 8.7 AP points. CoD improves every Table 4 generator column over the other listed detectors, but its 66.5% mean ACC still leaves substantial error. CNNDet 42.7% and UFD 32.8% mean ACC are below 50%; class balance, score calibration and random-baseline significance are not independently verified. They are not proof that the benchmark isolates a specific cause of failure.

Table 4 also has an aggregation limitation: the printed AP means are 43.4 for CNNDet, 54.6 for NPR and 58.4 for SAFE, while ordinary means of their seven displayed AP cells are approximately 43.457, 54.657 and 58.529 (rounding to 43.5, 54.7 and 58.5). Printed values are preserved. Hidden precision, weighting or other aggregation rules are unspecified, so exact agreement for every mean is not claimed. CoD 66.5/68.2 does reconcile from its displayed cells.

**Supporting ablations and contradictory details.** Table 5 FakeART ACC is 56.9 for image features, 59.3 for color features and 66.5 for combined image/color;200/300/500 noisy-image settings give 65.1/65.7/66.5. Its CLIP-only variant gives 54.8, and CLIP plus color gives 64.3;4-bit/8-bit/2-bit quantization gives 66.5/63.9/61.1. These support CoD design but are not the independent basis for the benchmark label. Table 1 reports CoD GAN mean 98.2 ACC while the Table 5 combined image/color setting reports 98.7, unexplained in the inspected paper. The prior-benchmark section also says 350,000 ProGAN synthetics but 20×18,000 implies 360,000; §4.3 separately mentions four ProGAN datasets. These are preserved as internal protocol limitations, not silently repaired.

**Resource provenance and limits.** The exact paper entry on the [first author publication page](https://zexijia.github.io/) links Data to the [author-linked dataset host](https://huggingface.co/datasets/wechat-prcap/domain_dataset). The rendered host metadata lists 22.1GB, no dataset card and a streaming viewer error. This does not establish complete FakeART availability. The file tree returned cache miss; `hf datasets info` failed with SSL EOF, and one exact metadata API request timed out at connection with 0 bytes. No further host retries, datasets, images, weights, archives, split lists or evaluation code were retrieved. A pinned release revision, license, complete sample inventory and immutable evaluation implementation remain unverified. Their absence is not imposed as a new mandatory R2 criterion.

**R1/R2 decision boundary.** Locked R1 requires a substantive reusable data-resource contribution; FakeART is separately proposed and described, so retain dataset. Locked R2 includes a reusable challenge, protocol, systematic comparative framework or benchmark resource. The explicit cross-domain challenge and independently usable data/metric/subset specification support adding benchmark. This is contribution-level sufficiency, not a claim that identical baseline training, exact numerical replication, complete release accessibility, or causal isolation have been demonstrated. No other research-type or task correction is proposed.

**Actual retrieval accounting.** Search of 1,051 unique gzip/PDF captures across the isolated and primary `data/raw` trees checked 48 distinct PDF bodies by metadata and opening pages. No identity-matched R400 manuscript was available; an unrelated UniAIDet PDF mentioned FakeART. Exactly one new full scientific manuscript was obtained: a zero-byte sandbox DNS failure, an HTTP200 partial body (2,796,338 bytes;180-second timeout), then one HTTP206 continuation for bytes 2,796,338–8,738,547. Both HTTP bodies have ETag `"8556f4-6357c4bd91a40"`, jointly matching the 8,738,548-byte advertised length. This is one manuscript reconstructed from two nonoverlapping body responses, not two manuscripts. Original headers, error logs, transport JSON, Crossref JSON and SHA receipts are preserved in the temporary review directory. Supplements, alternate PDFs, assets, archives and additional scientific manuscripts: zero.

**Evidence-only status.** This candidate remains pending maintainer adjudication. No terminal decision was appended, no scientific record or export changed, no tests or exports ran, and no staging, commit or push occurred in this worker. Global corpus, inventory and preservation checks belong to the root evidence packet.


## Provenance and preservation

Exactly two new complete official manuscripts were reviewed, one per paper. Complete source identities, PDF hashes, page/table locators, actual transport attempts, release-document limitations and worker findings are preserved in the manifest. No alternate complete manuscript, separate supplement, dataset assets, model weights or repository archive was downloaded. Source/evaluation code was not executed. Failed access and same-version range recovery are recorded without overstating successful retrievals.

Current corpus remains **674 public / 557 formal / 613 mapped / 61 unmapped / 1410 relationship rows / 1410 unique pairs**.

Taxonomy remains **621 detection / 84 source attribution / 45 localization / 578 method / 134 dataset / 91 benchmark / 21 survey / 82 analysis study**.

Original Batch B inventory remains **159 actions / 148 papers**; **145 historical unresolved actions**, **143 active-public unresolved actions across 132 papers**. Evidence completion closes zero actions.

All prior B1A–I decisions and receipts, historical fixtures, Batch C’s 13 debts, the separate 39-paper import inventory, primary checkout and its protected local files remain preserved.

<!-- B1J_VALIDATION_START -->
**Lightweight evidence validation: PASS — 44/44 checks, zero failures.** The interrupted draft command had completed with exit code 0 and 44/44 passing checks; its saved hashes matched the recovered drafts. Final-path checks also passed 44/44, covering exact identities, all scientific question records, manuscript/page/source fingerprints, numerical transcription, policy boundaries, transport accounting and durable evidence URLs.

**Independent preservation gate: PASS — 34/34 checks, zero failures.** All 4,477 isolated tracked files retain their bytes and modes; index is empty and exactly the two requested B1J files are untracked. The primary checkout's 4,414 tracked and 305 existing untracked files retain their bytes, names, HEAD, status and index. All 128 protected local files, 49 frozen NeurIPS artifacts, 119 ignored operational inputs, 18 prior B1A–I artifacts, historical fixtures, Batch C's 13 debts and the separate 39-paper import inventory are preserved. Actual corpus, taxonomy and all pending-review identities were independently recomputed unchanged.

Independent scientific reviews passed **32 checks for R100**, **41 for the R400 cross-review**, and **31 for a second R400 review**. The full reports, source bindings, disagreement/limitation notes and receipt reconciliation history are retained in the manifest. R100 supports the provisional `method;dataset` proposal with high contribution-level confidence and unverified public release. R400 supports `method;dataset;benchmark` with medium overall confidence and explicit protocol/resource limits. All maintainer acceptance remains pending.

`LIGHTWEIGHT_VALIDATION_FAILURES = 0`

`AUTHORITATIVE_CORPUS_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

No full repository suite or public exporter was run. No review decision, new Batch B action, staging, commit or push occurred. No source retrieval was repeated after recovery. Completion receipts are stamped after the successful checks; a final read-only verification checks the resulting receipt bytes and confirms that scientific content and all preserved sources remain unchanged.
<!-- B1J_VALIDATION_END -->

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
