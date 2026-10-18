# Batch B Wave B1F — Localization and regional attribution evidence

Maintainer adjudication, 2026-10-18. Original evidence baseline: `cc1e1b3d10c2a030e8b2cdda19fc9aaa1c7e8a0f`, verified equal to fetched `origin/main` before review. The evidence packet was independently published in `990c8221728a44b6ab78cfff5159612edb0983a7`; both files are already tracked. Exactly T303 is now accepted as `SUPPORTED_NO_CHANGE`; T093 remains unresolved. One terminal review decision closes T303 without any taxonomy, bibliographic, relationship, inclusion or public-export change.

| Review | Scientific outcome | Retained tasks | Scientific sufficiency | Maintainer acceptance |
|---|---|---|---|---|
| T093 | `EVIDENCE_STILL_INSUFFICIENT` | Preserve `detection;source_attribution` administratively; no proposed correction | Insufficient for a localization finding | Pending; review remains open |
| T303 | `SUPPORTED_NO_CHANGE` (scientific finding: `RETAIN_SOURCE_ATTRIBUTION`) | `detection;source_attribution;localization` | Sufficient for regional model identity retention | Accepted; terminal `review:75d76227af6d1a934c41` |

The manifest is `data/raw/corpus_quality_batch_b_wave_b1f_2026_10_18/evidence_manifest.json`. It preserves the exact original reviews, full task checks, quantitative tables, source fingerprints and retrieval receipts. The existing tracked artifacts are finalized in place; no duplicate evidence copy or new manuscript is introduced.

## Locked rules and source recovery

Exact final rules from `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json`:

**T1 (ACCEPT, 2026-10-05)**: source_attribution does not imply detection. Assign detection only when the paper explicitly performs an authenticity / real-versus-generated task. Classification among already-synthetic generators is attribution only.

**T2 (ACCEPT, 2026-10-05)**: localization requires an evaluated spatial forensic prediction task such as pixel-, mask-, patch-, region-, or equivalent spatial prediction of synthetic/generated/edited content. Artifact segmentation qualifies. Attention maps, saliency maps, explainability heatmaps, or visualization alone do not qualify.

**T3 (MODIFY_AND_ACCEPT, 2026-10-05)**: Every public paper must remain connected to at least one core forensic task represented by the map: detection, source_attribution, or localization. If careful review establishes that none applies, the record requires scope review rather than an empty task set.

Apply substantive evaluated model identity prediction to `source_attribution` using the existing vocabulary; do not invent a new regional task label. Multiclass annotations, generator domains, saliency and contribution claims alone are insufficient.

Local checks reused the known 49-unique-PDF inventory and retained source records. Neither selected work had a complete identity-matched manuscript in those retained materials. T303 recovery also searched the retained 1,047-unique-gzip payload inventory; no complete scientific text was found. These are bounded local-inventory findings, not a claim to have inspected every possible new file anywhere. No unrelated paper was scientifically reviewed.

## T093 — EXACT

**Canonical identity:** `curated:41a934ce12ecfd2f17e9`; EXACT: An Explainable Adaptive SemantiC-Trace Framework for AI-Generated Image Forensics; Hui Shi, Mingyang Liu, Chengcheng Gong; Computer Vision and Image Understanding, 2026; DOI `10.1016/j.cviu.2026.104871`. Current tasks: `detection;source_attribution`; scope: `fully_generated`; type: `method`.

**Original review:** `EXACT explicitly claims a pixel-level localization head and evaluates localization; existing two task labels omit it.` The original proposal adds localization. Exact intake question: “Primary localization head specification, spatial ground truth and quantitative spatial metrics; the abstract claim of meaningful localization is insufficient by itself. Stored audit and current public/taxonomy excerpts establish the pending question but do not replace the requested contribution/evaluation check. No scientific verdict is made during intake.” The ledger reason is a hypothesis requiring primary evaluation evidence; it is not accepted evidence of a localization head.

**Access and identity:** Retained OpenAlex metadata/abstract and DOI/PII-linked discovery records agree on the work. The [official article page](https://www.sciencedirect.com/science/article/pii/S1077314226002389) returned HTTP403. One exact-title discovery search exposed indexed official abstract/introduction/section snippets, not complete methods/tables. One standard publisher [PDF-route candidate](https://www.sciencedirect.com/science/article/pii/S1077314226002389/pdfft?isDTMRedir=true&download=true) returned HTTP403 with 832,803 bytes of HTML, SHA256 `274df033d55d7098c168403fc1d5df0ab7e5d9ac74e56b2070ac2b042690215f`. That route was derived from the matched PII, not an observed verified PDF link. No manuscript or publication-version identity could be verified from that response; it is not counted as a full manuscript. No retry, alternate full version, challenge interaction or author contact was performed. A request-only ResearchGate search snippet supplied no scientific text and was not opened.

**Available claims:** The abstract describes semantic and wavelet/Transformer trace branches, adaptive fusion and frozen multimodal reporting, with detection, attribution and localization claims. Its reported detection figures are 99.49% in-domain accuracy, 84.88% extended cross-dataset accuracy and 94.18% average precision. These are partial-source image-level detection claims with unverified full protocol; none is a localization score. The accessible material does not provide the complete output heads, losses, spatial supervision or evaluation needed here.

| Required check | Status | Evidence boundary |
|---|---|---|
| 1. spatial_output | Unverified | The abstract claims pixel-level localization but a complete output/head specification and actual prediction label space are unavailable. |
| 2. mechanism | Unverified | Partial architecture descriptions identify semantic/trace feature branches and adaptive fusion, but do not establish a learned localization head, its loss, or its relation to attention/explanation maps. |
| 3. spatial_ground_truth | Unverified | No complete spatial annotation construction, forensic target definition, sample counts, split protocol or ground-truth evaluation procedure was obtained. |
| 4. spatial_metrics | Unverified | No full localization metric definitions or numerical localization results were obtained. Abstract detection accuracy/AP values cannot substitute for spatial metrics. |
| 5. localization_baselines | Unverified | Complete localization tables, baseline identities, training/evaluation conditions and exact comparative values are unavailable. |
| 6. task_separation | Unverified | The abstract describes a unified framework supporting these tasks, but separate heads/decision spaces, losses, protocols and quantitative task-specific evaluations cannot be verified. |
| 7. natural_language_reporting | Unverified | The abstract/partial description says a frozen Large Multimodal Model produces reports from model outputs; the complete reporting inputs, protocol, independence and evaluation remain unverified. |

**Provisional decision:** `EVIDENCE_STILL_INSUFFICIENT`. High confidence in the evidence limitation; localization itself is undetermined. Do not turn failed access into `LOCALIZATION_NOT_SUPPORTED`. No material contradiction justifying a separate change to existing detection/attribution was established. Preserve them administratively without claiming this wave newly certified their full protocols. Needed evidence is an accessible complete identity-matched main manuscript showing heads/losses, spatial targets, splits, metric definitions, localization baselines and task-specific results. No correction or closure is proposed now.

## T303 — DiffSeg30k

**Canonical identity:** `curated:33788a5e5e6efbd6bddd`; DiffSeg30k: A Multi-Turn Diffusion Editing Benchmark for Localized AIGC Detection; Hai Ci, Ziheng Peng, Pei Yang, Yingxin Xuan, Mike Zheng Shou. Current tasks: `detection;source_attribution;localization`; scope: `generative_editing`; types: `dataset;benchmark;analysis_study`. Canonical publication type is preprint; no DOI or publisher-final equivalence is asserted.

**Original question:** `Fresh arXiv abstract describes edit masks and whole-image classification; no source-generator identification task is established. Verify the full evaluation before removal.` Exact intake question: “Reconcile the ledger reason with the current abstract explicitly naming editing-model identification: full semantic class definitions, generator/model-ID outputs, and attribution-specific metrics or exhaustive task evaluation. Conflicting local cues: the old action reason says no generator-identification task was established, but the current abstract explicitly states simultaneous localization and identification of editing models. Preserve current labels; prioritize source-level reconciliation rather than assuming the proposed removal.” The original captured arXiv abstract already contains an editing-model identification claim. The demonstrated conflict is the audit interpretation versus its own retained primary abstract, not proof that the abstract changed in a later version. Independent R303/P303 historical BatchD questions are not adjudicated here.

**Verified manuscript:** One GET of [arXiv2511.19111v2](https://arxiv.org/pdf/2511.19111v2), HTTP200, 4,166,186 bytes, SHA256 `3cd4e425289716e7389a65c13d2bc1ec5fa25b90aa8f16633258dd63c6ef2f65`. Complete title and all five ordered authors match; the first-page stamp is v2, 26Nov2025. The [arXiv metadata page](https://arxiv.org/abs/2511.19111) reports v1 on 2025-11-24, v2 on 2025-11-26 and a 16-page comment. The downloaded PDF actually has 17 pages: scientific text pp1–8, references pp9–12, and bundled Supplementary Material pp13–17. No separate supplement or extra version was retrieved. All17 pages were read; the coordinator visually inspected pp1,3,4,5,7,8 and the reviewer checked key tables/figures. The finding below rests on main-paper evidence, not bundled supplementary experiments.

### Task definitions, data and outputs

Sections3–4 (pp2–5), Figures1–3 and Figure6 define up to three sequential inpainting operations using eight editing models. VLM-selected object categories are turned into Grounded-SAM masks; masks with pairwise IoU greater than70% are filtered as redundant; one to three masks are chosen. Editing prompts cover addition, removal and attribute changes. The selected model operates on each known mask. The resultant target masks are separate from trained baseline predictions, although automatic annotation can be imperfect. Approximately half the bases are real COCO images and half are AI-generated from COCO prompts (Figure3:47.9%/52.1%). Background therefore means unedited by the local benchmark operation, not necessarily camera-origin content.

FCN-8s and DeepLabv3+ (ResNet50) plus SegFormer-B2 are trained for binary and semantic segmentation. The reported split is8:2 training/validation, with results on validation and training at512×512;5,000 extra real COCO training images suppress false positives. The paper describes use of defaults, not explicit task-loss equations or output tensor implementation details. Exact validation sample counts, sequence-level split controls and evaluation-negative composition are not fully specified. The dataset is described as30k edited images; current web-card preview totals are not substituted for this experimental corpus.

| Requested point | Finding and main-paper anchor |
|---|---|
| Binary image-level edited/unedited detection | pp7–8/Table5: mask foreground area greater than1% predicts edited. CNNSpot and UniversalFakeDet receive30k additional real COCO negatives for training. Acc/mAP are separately reported. This detects local editing presence, not whole-image generator identity. |
| Binary spatial localization | pp4–5/Table2: learned foreground/background masks are evaluated against editing-mask ground truth with pixel accuracy, mIoU and boundary-F1. |
| Multiclass protocol | Section4.1/Table2 explicitly evaluates semantic segmentation as localizing edits and attributing them to editing models. Figure5 has true and predicted model-class axes. |
| Actual output classes | Nine semantic classes: background, SD2, Kolors, SD3.5, Flux, SDXL, Glide, HunyuanDiT, Kandinsky2.2. One model class is predicted per evaluated edited pixel/region. |
| Annotation versus prediction | The card establishes integer annotation encoding. The paper independently supplies trained model-specific predictions, quantitative semantic results and confusion matrices. |
| Identity metrics | Table2 semantic mIoU/Acc/bF1 and Figure5 model-specific confusions evaluate identity-aware spatial predictions; they are not binary-mask scores reused as attribution metrics. |
| Multiple sources per image | Sections3.1/Figures1–3 and p8 describe multi-turn, interleaved edits from different models. More than one editing-model label can occur in a single image. Random model choice does not guarantee distinct models on every turn. |
| Overlapping/overwritten regions | The>70% duplicate-mask filter does not exclude partial overlap. Neither the full PDF nor reviewed card states an explicit final-label overwrite/last-writer rule or overwritten-region evaluation. This remains unverified. |
| Attribution granularity | Closed-set regional editing-model attribution is supported. A single whole-image generator-ID classifier, original-base attribution, complete editing-history recovery and open-set model identification are not established. |
| Detection/attribution distinction | Table5 and Table2/Figure5 are separate evaluated tasks. Tables4/6 cross-generator binary transfer alone would not establish attribution. |

### Exact quantitative evidence

Table2 (p5), all values as reported, in Acc/mIoU/bF1 order. The text calls mIoU mask Intersection-over-Union; an explicit class-averaging formula is not supplied. Semantic mIoU/bF1 exclude background. Boundary-F1 is a spatial boundary measure, not model-ID macro-F1.

| Model | Binary Acc | Binary mIoU | Binary bF1 | Semantic Acc | Semantic mIoU | Semantic bF1 |
|---|---:|---:|---:|---:|---:|---:|
| SegFormer | 0.989 | 0.961 | 0.678 | 0.952 | 0.825 | 0.532 |
| DeepLabv3+ | 0.984 | 0.974 | 0.761 | 0.916 | 0.760 | 0.431 |
| FCN-8s | 0.838 | 0.699 | 0.457 | 0.331 | 0.203 | 0.024 |

Figure5 (p7) compares predicted and true background plus eight named editing-model classes. SegFormer’s displayed diagonal values for SD2/Kolors/SD3.5/Flux/SDXL/Glide/HunyuanDiT/Kandinsky2.2 are0.95/0.88/0.87/0.83/0.93/0.98/0.92/0.95 (background0.98). These are normalized confusion entries, not per-model IoU or whole-image attribution accuracy. Flux→SD2 confusion is0.12. Figure6 (p8) shows separate ground-truth and predicted binary/model-colored masks. Together with semantic Table2, these establish actual evaluated model identity prediction, independently of the card.

Table5 (p7), binary image-level edited/unedited results:

| Model | Acc | mAP |
|---|---:|---:|
| CNNSpot | 0.942 | 0.979 |
| UniversalFakeDet | 0.860 | 0.934 |
| SegFormer | 0.997 | 0.999 |
| DeepLabv3+ | 0.980 | 0.994 |

The1% mask-area rule is described, but the continuous score used for mAP is not detailed. These are reported results, not a replication.

**Stress tests and counterevidence:** Table3(p5) shows semantic performance is fragile: SegFormer semantic mIoU falls from0.825 to0.032 with JPEG60 and0.188 with JPEG80; DeepLabv3+ falls from0.760 to0.013/0.014. Table4(p7) trains on six models and tests binary localization on two unseen models (SegFormer mIoU0.930/0.926/0.951 for Flux–Hunyuan/SD2–SD3.5/Glide–Kolors). Table6 reports the corresponding binary classification transfer (SegFormer Acc/mAP0.978/0.986,0.982/0.986,0.987/0.996). Those transfer experiments do not evaluate identification of unseen model classes. All main table rows are preserved in the manifest.

**Internal discrepancies:** Table2 reports FCN semantic mIoU0.203 while adjacent prose says0.23. SegFormer semantic accuracy is0.952 in Table2 and0.953 in Table3’s baseline; the0.825 mIoU and0.532 bF1 agree. Exact table values are retained without silently repairing the paper. Split details, automatic-mask errors and unstated overlap ownership limit reproduction and history claims, without erasing the observed regional task.

### Dataset card boundary

The [official Diffseg30k card](https://huggingface.co/datasets/Chaos2629/Diffseg30k) is annotation documentation. One `hf datasets card` metadata call exited0 but returned empty stdout, so its receipt records no usable card content. One official web fallback supplied the card; no dataset payload, code or image preview was downloaded. The card is current and unpinned, so equivalence to the v2 experimental snapshot is unverified.

| Integer | Card annotation identity |
|---:|---|
| 0 | Background |
| 1 | `stabilityai/stable-diffusion-2-inpainting` |
| 2 | `kolors` |
| 3 | `stabilityai/stable-diffusion-3.5-medium` |
| 4 | `flux` |
| 5 | `diffusers/stable-diffusion-xl-1.0-inpainting-0.1` |
| 6 | `glide` |
| 7 | `Tencent-Hunyuan/HunyuanDiT-Diffusers` |
| 8 | `kandinsky-community/kandinsky-2-2-decoder-inpaint` |

The card confirms multiple model labels can occur in one grayscale mask, but does not supply an overwrite rule. Figure5’s ordering is not assumed to define the integer encoding. Annotation capability supports interpreting the labels; Table2 and Figure5 provide independent experimental proof.

**Accepted decision:** `SUPPORTED_NO_CHANGE`; retain exactly `detection;source_attribution;localization` and `dataset;benchmark;analysis_study`. The prior scientific finding `RETAIN_SOURCE_ATTRIBUTION` is accepted with its reported-protocol/version/overlap/robustness limitations. Terminal decision `review:75d76227af6d1a934c41` uses the established `other` / `paper` / `no_action_after_review` schema. Source attribution is regional editing-model prediction; no separate whole-image single-generator classifier is required. No task, compatibility field, canonical metadata, affiliation or relationship is changed. Only T303 closes; T093 and independent historical R303/P303 questions do not.

## Retrieval budget and provenance

| Case | New full-text requests | Successful manuscripts | Source/version | Failures and limitations |
|---|---:|---:|---|---|
| T093 | 1 | 0 | DOI/PII-matched official PDF-route candidate | HTTP403 HTML; no full version verified; no retry |
| T303 | 1 | 1 | arXiv2511.19111v2,2025-11-26 |17actual pages versus16-page comment; preprint; bundled supplement in same PDF; no extra version |
| Total | 2 | 1 | Within one-per-case/two-total budget |0separate supplements,0code/data payloads,0retries |

Metadata-only access was one official article landing, one arXiv abstract/version page, one exact-title primary discovery search, one HF CLI card call with no content, and one HF web-card fallback. The manifest distinguishes these from manuscript retrievals, preserves failed access, and does not invent a raw search-response hash. PDFs and operational receipts remain outside Git under `/private/tmp/b1f-evidence-2026-10-18/`.

## Accounting and preservation

| Corpus | Count |
|---|---:|
| Public / formal |674 /557|
| Mapped / unmapped |613 /61|
| Relationships / unique pairs |1,410 /1,410|
| Detection / source attribution / localization |621 /84 /45|
| Method / dataset / benchmark / survey / analysis study |579 /134 /90 /21 /81|

Original Batch B remains **159 actions / 148 historical papers**. Recomputed unresolved accounting is **149 historical actions / 147 active-public actions / 136 distinct active-public papers**, previously150/148/137. The ten terminal IDs cover L013,P139,P153,P490,R137,R611,T056,T303,T345,T579. T303 has no other unresolved original Batch B action; that fact was checked against the ledger rather than assumed. T093 and pending carryovers T608/T526/P526 remain open. Independent historical R303/P303 questions are unchanged. The separate import inventory remains39affiliation-debt papers,14overlapping taxonomy-review papers and12held candidates; it is not combined with the original BatchB ledger. BatchC remains41total/28resolved/13deferred/0maintainer judgments, with the same13debt IDs.

The fresh published baseline contains4,455 tracked files. All unchanged paths are compared by content hash; the review ledger must retain its exact prior byte prefix plus one T303 row. Authoritative paper/taxonomy/relationship files, public exports, ten prior B1A–E artifacts and frozen receipts remain byte-identical. The128protected and original130primary-checkout files,49frozen NeurIPS artifacts in each checkout,119ignored operational inputs and four BatchC receipt files are preserved. Primary HEAD/index/status are checked read-only; no primary change is made. The exact `other/no_action_after_review` append is ignored by production-affecting venue, mapping and institution decision consumers; coverage input fingerprints do not depend on this ledger. No public/review derived output needs regeneration. The repository has no universal full-suite mandate for this Git adjudication. Run focused regressions and all four current-scope validators; do not regenerate unaffected exports or claim export reproducibility was rerun.

<!-- B1F_VALIDATION_START -->
Recovered successful validation: **128 focused tests and 12 subtests passed**, zero failures, errors, skips or pytest warnings. The four current-scope validators passed with zero errors: curated database, public preview, paper exclusions and key-paper coverage (`--check`). Existing warning lines are unchanged from published B1E: curated294, public62, exclusions2, coverage0. They are validator data warnings, distinct from pytest warnings.

The tested five-file hashes were checked before receipt finalization. No test process is repeated: only this receipt section and manifest validation/publication bookkeeping are finalized. Original evidence-only49/49 and independent20/20 results remain explicitly historical. Current semantic/preservation gate:31checks passed, zero failures.

Full suite: **not run**. Public exports/two-pass exporter: **not run**, because the exact `other/no_action_after_review` decision affects only review accounting and no production export consumer or dependent generated output. Existing public paper/relationship JSON and all scientific tables remain byte-identical; no fresh export-reproducibility claim is made.

`UNEXPECTED_CHANGED = 0`
`FROZEN_NEURIPS_CHANGED = 0`
`PREEXISTING_LOCAL_FILES_CHANGED = 0`
`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

The staged publication allowlist is the one-row registry append, this tracked report and manifest, the new focused B1F regression module, and the narrow B1E historical endpoint repair. Historical B1E exact-transaction/accounting/source fingerprints use published `cc1e1b3d10c2a030e8b2cdda19fc9aaa1c7e8a0f`; their expected values, receipts, fixtures and live NeurIPS guards are unchanged. No public export, manuscript, operational cache or protected file is included.
<!-- B1F_VALIDATION_END -->

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Original evidence source fingerprints

The following evidence-phase hashes are retained as historical provenance at `cc1e1b3`. The manifest separately records current adjudication source fingerprints, including the intentional one-row review-ledger append.

| Source | SHA256 |
|---|---|
| `data/curated/paper_taxonomy.csv` | `17b59d6a33ae77ebfad1d58f3791b051197f5117834faa4c93342f8a79323417` |
| `data/curated/papers.csv` | `edb1744a04968fb8a63d20f04aaa088866e9b37c0d261a94e6f98beb8947bc38` |
| `data/curated/review_decisions.csv` | `471b5542bb3619cce2997b244114f047b36ece15dcdfa43e67dfbb864aa73506` |
| `data/processed/literature51_2026_10_16/followup/receipt.json` | `b24deabfd36186ed278d2afd4ac60814a4c78d71e04151c25cee52d27460d4f3` |
| `data/processed/literature51_2026_10_16/followup/review.json` | `cdf83d05b4ab57fe5a37034f5213aef40f7c6ee0095c5d22d3988ca784d03312` |
| `data/processed/literature51_2026_10_16/main_integration/manifest.json` | `5959e8628cc7e272ac45f0a2afd5e508412a416615c61d411b4529e135077a79` |
| `data/processed/literature51_2026_10_16/plan.json` | `b6af4975b2be41958176448000d240dcdbc2dd00a507e8edc3a7a7b0027356ab` |
| `data/raw/ant_gap_fill_2026_09_05/openalex_exact_title_results.json` | `01786d62d432542cab8184bcb65c486990a1c9b3111b65400bf3e2977608769f` |
| `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json` | `ee097956eafca891155380e95d13173070fca413aad371f0dc57bfcb86374f55` |
| `data/raw/corpus_quality_audit_2026_10_04/publication_metadata_review.json` | `b2ef27b7c70dd991f5ee29a794001bbd9f6ff6da2e9eff5cdb5d30c246d0726c` |
| `data/raw/corpus_quality_audit_2026_10_04/source_checks.json` | `78c2aed641161705a0a22658a2df38cc7e53550eb1857d119106a4a419b02227` |
| `data/raw/corpus_quality_audit_2026_10_04/taxonomy_review.json` | `ad84e82b3dd82d0018d57caeed93353585ca4e83e3e2d800c00c0db656d637a1` |
| `data/raw/systematic_gap_audit_2026_10_02/discovery_records.json` | `6ec9e001aa007ef4fcd528243c0e2da099a8e9fed359d8050cb27ef8088edc0d` |
| `data/raw/systematic_literature_2026_09/a58a312ed612f8266c74.gz` | `6c0ce05348d64215ccf0195281b51d197a685af17680e4c0ebe7dda5d6d81962` |
| `docs/corpus_quality_batch_b_intake_triage_2026_10_12.md` | `a40d37dc3abd8198ea4d00384d19b25905a036519ee691718fac1d11a19e5459` |
| `docs/literature51_main_integration_2026_10_17.md` | `6f0e138d4bbdbd1d8032f84479cca0fae791f819ac998003f502faecc59101c4` |
| `web/data/public_preview_map_data.json` | `09b6f815597b2c14349dffc359b7844eab9c2b9a758ec02ef669476e009b627b` |
| `web/data/public_preview_papers.json` | `9b1565482ab2095fa43ab3b9e60504c733fd0d43cd84bc4d5f3f8d98f2eb9781` |

## Publication receipts

The original two-file evidence packet is already published at `990c8221728a44b6ab78cfff5159612edb0983a7`, verified by fetch and ancestry. This adjudication is identified by the Git commit containing the finalized packet. Exact created-commit SHA and post-push fetched remote equality are recorded after publication in `/private/tmp/b1f-adjudication-2026-10-18/publication.json` and the final response; a successful future push is not asserted in advance. Publication uses one normal fast-forward commit, with no primary-checkout update.
