# Batch B Wave B1G — T631 accepted; T046 evidence deferred

Adjudicated **2026-10-19** (Asia/Shanghai), using the existing evidence packet. The original evidence baseline was `3bcd95fd45b12b3d7a711232b0ba3ae687e8771d`; the isolated worktree was subsequently fast-forwarded to the published historical-test repair `3feff7d6b609183cb8dda4949d2c087e77639003`. That completed integration was recovered without repeating it. No scientific evidence was retrieved again.

| Review | Final administrative disposition | Retained tasks / type | Review status |
|---|---|---|---|
| T046 | `EVIDENCE_STILL_INSUFFICIENT` | `detection` / `method`; no localization addition | Open; complete published spatial evaluation remains unverified |
| T631 | `SUPPORTED_NO_CHANGE` | `source_attribution` / `method`; no detection addition | Maintainer accepted and closed by exactly one terminal decision |

T631 decision: `review:09ce07963903ecd891c5`, queue `other`, action `no_action_after_review`. The only authoritative mutation is one appended registry row (85 → 86), preserving all earlier bytes. Canonical papers, task/research-type classifications, affiliations, exclusions, relationships and public exports remain byte-identical. T046's complete record is unchanged.

The companion manifest remains `data/raw/corpus_quality_batch_b_wave_b1g_2026_10_19/evidence_manifest.json`. It preserves the original packet as authenticated inline archives and retains the original scientific evidence, access failures, URLs, manuscript hashes and retrieval accounting. Original evidence-stage proposals and receipts are historical observations; this section records subsequent maintainer acceptance of T631 alone.

## Locked scientific policies

Exact rules from the existing policy ledger:

**T1 (ACCEPT, 2026-10-05)**: source_attribution does not imply detection. Assign detection only when the paper explicitly performs an authenticity / real-versus-generated task. Classification among already-synthetic generators is attribution only.

**T2 (ACCEPT, 2026-10-05)**: localization requires an evaluated spatial forensic prediction task such as pixel-, mask-, patch-, region-, or equivalent spatial prediction of synthetic/generated/edited content. Artifact segmentation qualifies. Attention maps, saliency maps, explainability heatmaps, or visualization alone do not qualify.

**T3 (MODIFY_AND_ACCEPT, 2026-10-05)**: Every public paper must remain connected to at least one core forensic task represented by the map: detection, source_attribution, or localization. If careful review establishes that none applies, the record requires scope review rather than an empty task set.

T046 requires a quantitatively evaluated spatial forensic prediction, beyond explanation maps. T631 requires substantive authenticity evaluation, beyond a real source in a model-attribution classifier. T3 does not authorize placeholder task additions: each paper already retains a supported core-task label.

## Local evidence recovery

The intake report and original task-taxonomy ledger were read, along with canonical/public/taxonomy rows and independent review questions. The known 49-unique-PDF identity inventory contains no matching complete manuscript for either work. Retained metadata and gzip/text searches likewise provided abstracts, registry/export records or references, not the complete target experiments. T631 recovery checked the 1,050-unique-gzip payload inventory. These are bounded searches of retained materials, not a claim to inspect every possible new file anywhere. No unrelated scientific paper was reviewed.

## T046 — CLIP-SegFusion

**Identity:** `curated:9b7e6c57a9f75e06fddf`; CLIP-SegFusion: An Attention-Guided Feature Fusion Framework for Multi-Level Detection on AI-Generated Artworks; Yuqian Zheng, Hyeongjin Ahn, Juyeob Lee, Eunil Park; ACM ICMR2026 main conference; DOI `10.1145/3805622.3810639`. Current tasks **`detection`**, type **`method`**, scope **`fully_generated`**. No field is changed.

**Original action:** “Joint image classification and pixel segmentation explicitly localize manipulated regions.” It proposes `detection;localization`. The exact intake question is: “Primary method and evaluation: spatial prediction head, forensic ground truth and spatial metric; distinguish segmentation scores from image-classification F1 and attention visualization. Stored audit and current public/taxonomy excerpts establish the pending question but do not replace the requested contribution/evaluation check. No scientific verdict is made during intake.” This is a hypothesis to check, not an accepted taxonomy correction. Independent historical R046/P046 screens remain untouched.

### Primary access and implementation provenance

The [DOI](https://doi.org/10.1145/3805622.3810639) and author-listing publisher link were inaccessible through the web tool. One direct [official ACM PDF-route candidate](https://dl.acm.org/doi/pdf/10.1145/3805622.3810639) returned **HTTP403**, 5,590 bytes of HTML, SHA256 `6fbd1f11ecffaa708cef94dfce330190363d1f499854e0c5a3c00d8a6b6ab178`. The candidate is the standard DOI-derived route, not an observed verified PDF link. No complete manuscript/version or paper section/table numbering was verified; no retry or alternate manuscript was retrieved.

The [authors’ publication listing](https://sites.google.com/view/dxlab/publications), entry c74, matches the title, ordered four-author byline, ICMR2026 and pages2486–2495, and links the [target repository](https://github.com/dxlabskku/CLIP-SegFusion). Its HTML code pages provide supporting implementation evidence. These are unpinned `main` captures, with different browser cache ages; no immutable release or correspondence to the published experiment is established. Two raw train/evaluate link clicks failed with cache misses; no clone, weights, dataset, code execution or separate raw-code download occurred.

### What is supported, and what is still missing

| Requested check | Finding |
|---|---|
| 1. Model input and output dimensions | Captured model accepts image tensors plus caption text. Image loader uses RGB images; transformation details are delegated to uncaptured get_transforms. Default outputs are two image-class logits per sample and one 224x224 mask-logit plane per sample. The exact published input/crop protocol is unavailable. |
| 2. Classification heads versus segmentation heads | A linear image classifier is separate from a convolutional mask head with one output channel by default. Training explicitly includes mask_head parameters and a mask loss. This is positive evidence for a learned mask branch. |
| 3. Pixel, patch, mask or region predictions | Visual patch tokens are reshaped to a spatial map, passed through the mask head, and bilinearly upsampled to 224x224. Raw mask logits are returned alongside class logits. |
| 4. Whether spatial predictions represent AI-generated/edited content | The identity-matched abstract describes localization of manipulated regions, and the repository loads a separate mask_label path. Captured code alone does not document what each target pixel means, how edited regions were created or how mask semantics correspond to the published experiment. |
| 5. Availability of forensic spatial ground truth | Existing mask files are loaded as grayscale targets. Training uses a validity flag when a mask path exists and substitutes a zero target with false validity when absent. Evaluation also substitutes zero masks for absent paths. Annotation origin, correctness, binarization/transform behavior, sample counts and forensic interpretation cannot be established without the full protocol or dataset metadata. |
| 6. Independent spatial prediction metrics | The captured evaluator computes spatial pixel accuracy, IoU, precision, recall and F1 into separate *_seg output fields, alongside image-classification accuracy/macro-F1/AP/precision/recall/AUC. No executed outputs, paper spatial table values or localization-baseline comparison were obtained. |
| 7. Segmentation outputs evaluated against ground-truth masks | The evaluator compares binarized predicted masks with loaded target masks and calculates TP/FP/FN. It includes only samples whose target mask sum is positive. This establishes a coded comparison path, not proof that the target paper quantitatively reported it under an identified split/baseline protocol. |
| 8. Whether reported F1/AUC are image-level or pixel/region-level | README ID tables contain accuracy/precision/recall/F1/AUC and OOD tables contain F1/AUC. They lack IoU or separately named spatial-score columns. The evaluator separately names image macro_f1/auc and spatial f1_seg/iou_seg. The README values support classification-style detection claims and must not be relabeled as localization metrics. Precise mapping to a pinned paper table remains unverified. |
| 9. Attention/saliency visualization confused with localization | The predicted mask also weights spatial features through sigmoid attention, but it has its own returned output, trainable convolutional head and supervised mask loss. Therefore an attention-only or no-spatial-output description would contradict available code. The missing published GT/protocol/numerical evidence still prevents a confident T2 task-addition proposal. |

The positive machinery is stronger than an attention illustration: [models.py](https://github.com/dxlabskku/CLIP-SegFusion/blob/main/models.py) has separate default **B×2 class logits** and **B×1×224×224 mask logits**, with a convolutional spatial head and upsampling. The mask also weights features used for classification. [train.py](https://github.com/dxlabskku/CLIP-SegFusion/blob/main/train.py) combines image cross-entropy with mask BCE-with-logits on valid mask samples. [evaluate.py](https://github.com/dxlabskku/CLIP-SegFusion/blob/main/evaluate.py) contains separate prediction-versus-target IoU and spatial F1 calculations. These describe the captured code, not verified publisher methods or completed experimental results.

**Implementation limits:** Spatial evaluation includes only examples with positive target-mask sums. It thresholds returned raw mask logits at0.5, whereas training/validation use sigmoid(mask logits)>0.5, a different operating point. Mask annotation semantics, construction, transforms, sample counts, negative-image handling, splits and exact paper/code correspondence remain unverified. No code was run. Browser-text L-numbers in the manifest locate preserved captures, not native repository line numbers. There is no basis for saying the method is attention-only, nor for treating a metric routine as proof of reported spatial performance.

### Quantitative evidence boundary

The retained abstract claims ID average F1 **92.63%**, OOD average F1 **83.66%** and a **5.80 percentage-point** OOD advantage. These are not verified pixel/region scores. The repository’s displayed ID rows are classification-style results:

| README setting | Accuracy % | Precision % | Recall % | F1 % | AUC % |
|---|---:|---:|---:|---:|---:|
| LA_Inpainting |94.80|94.80|94.80|94.80|98.77|
| Inpainting |90.47|90.55|90.47|90.46|96.88|

The six displayed OOD rows likewise report classification-style F1/AUC:

| Generator/domain | F1 % | AUC % |
|---|---:|---:|
| Latent Diffusion | 77.22 | 89.80 |
| Midjourney | 87.77 | 95.03 |
| DALLE | 82.96 | 92.48 |
| Imagen | 68.61 | 85.99 |
| Janus | 91.50 | 97.27 |
| StyleGAN2 | 93.93 | 98.51 |

No displayed row supplies a verified paper IoU, spatial F1, localization-baseline comparison or spatial sample/split protocol. Domain columns and inpainting dataset names do not turn image-classification F1 into localization scores. The repository is not uniformly best in every displayed comparison, and no such claim is made. These are transcribed claims, not replicated experiments.

**Provisional outcome:** `EVIDENCE_STILL_INSUFFICIENT`. Retain `detection` administratively, preserve `method`, and leave T046 open. High confidence in the observed learned-mask implementation and the evidence limitation; published localization sufficiency is unresolved. Needed evidence is a complete identity-matched target manuscript with exact head/loss definitions, forensic mask provenance, spatial protocol and numerical results/baselines. The unavailable paper reference list also prevents verifying reliance on any related2025 precursor; no precursor manuscript was retrieved or reviewed, and none supplies substitute results.

## T631 — GAN fingerprints

**Identity:** `curated:170f07b3d7020611e566`; Attributing Fake Images to GANs: Learning and Analyzing GAN Fingerprints; Ning Yu, Larry Davis, Mario Fritz; ICCV2019 main; DOI `10.1109/iccv.2019.00765`. Current tasks **`source_attribution`**, type **`method`**, scope **`fully_generated`**. Canonical arXiv `1811.08180v3` and the taxonomy’s version-normalized `1811.08180` are preserved; no author/identifier correction is attempted.

**Original action:** “Abstract explicitly describes real-versus-GAN classification before source attribution; detection is missing.” It proposes `detection;source_attribution`. Exact intake question: “Primary real/generated decision rule and authenticity-specific metric, distinguished from a real source class in multiclass source attribution. Stored audit and current public/taxonomy excerpts establish the pending question but do not replace the requested contribution/evaluation check. No scientific verdict is made during intake.” Historical R631/P631 screens are separate and unchanged.

### Verified official manuscript

One GET of the [official CVF ICCV main-paper PDF](https://openaccess.thecvf.com/content_ICCV_2019/papers/Yu_Attributing_Fake_Images_to_GANs_Learning_and_Analyzing_GAN_Fingerprints_ICCV_2019_paper.pdf) succeeded: **HTTP200**, 1,860,415 bytes, SHA256 `be717607d2204d42d4a8e96f092bcbbef4e749a43df587bd9e0940afea5cebea`. It contains **11 pages**, printed7556–7566; complete title and ordered byline match. PDF metadata expands Larry Davis to Larry S.Davis, which does not authorize a canonical-author edit. All11 pages were read; relevant methods/tables were visually inspected. Main scientific text is pp1–8, references pp9–11, with no bundled supplement.

The first-page CVF notice identifies the open-access accepted version, with IEEE hosting the final proceedings. This review is of that official CVF file, not an arXiv-v3/IEEE byte-equivalence verification. Its external code, data, models and supplement were not retrieved. The initially supplied CVF HTML page failed in the web tool; the DOI/title-matched conventional CVF PDF route succeeded directly and its actual identity was checked.

### Prediction space and evaluated protocols

Section3.1 (PDFp3/printed7558) defines supervised image-source labels comprising the real world and known GAN instances. Figure2 (p4/7559) maps **128×128×3** images through a **1×1×512** feature to a final **#labels** source head, trained with cross-entropy. The primary output is one source identity; there is no separately specified binary head or reported real-versus-sum-of-GAN score/threshold. The Section3.3 reconstruction critic regularizes fingerprint visualization, not an independently evaluated forensic detector.

Section4.1 (p5/7560) explicitly evaluates **image attribution accuracy**. Table1’s five-way setup is real/ProGAN/SNGAN/CramerGAN/MMDGAN. Table3 uses real plus ten separately seeded ProGAN instances, hence eleven source classes. The paper reports100,000 training and10,000 testing images per source in its architecture experiment. It varies source architecture, training data, initialization, frequency bands, patch statistics, perceptual selection and attacks while measuring source correctness.

| Requested check | Finding |
|---|---|
| 1. Are real images included in the prediction label space? | Yes. Section3.1 defines a finite source-ground-truth set consisting of pretrained GAN instances plus the real world. Table1 explicitly uses five classes: real, ProGAN, SNGAN, CramerGAN and MMDGAN. |
| 2. Is a real-versus-GAN decision rule explicitly defined? | The paper repeatedly states that it distinguishes real and generated images, and a real source can be predicted by the source classifier. It does not specify a separate binary head, a real-versus-sum-of-GAN score, threshold, source-collapse rule or distinct two-stage real/fake decision protocol. The operationally specified output is a source label from finiteY. |
| 3. Is genuine authenticity detection quantitatively evaluated? | No independently scored authenticity endpoint was found in the complete main paper. The reported classification accuracies evaluate correctness of the exact source label, including real as one source. Such joint correctness is not a separately measured real/fake metric. |
| 4. Are detection results separated from generator-attribution results? | No. There is no separate detection table, binary ROC/PR curve, authenticity confusion table or binary subgroup result. Tables1–8 retain source-attribution settings; FD ratios quantify feature separation across source classes. |
| 5. Are real images treated as another source class? | Yes in the defined and evaluated classifier. A real-source label is trained alongside GAN instance labels. The authors also motivate visual-forensics use, so describing this as a mere absence of a real/GAN claim would be inaccurate; the distinction is claim/joint capability versus independent detection evaluation. |
| 6. Would generator-ID accuracy be incorrectly reused as detection accuracy? | Yes if the joint-source scores were relabeled as binary accuracy. A ProGAN→SNGAN error is an attribution error while leaving binary generated status unchanged. A real→GAN error changes authenticity. The aggregate source accuracy does not supply the full binary error breakdown, and no binary score is derived here. |
| 7. Are binary accuracy, ROC/AUC, F1 or equivalent authenticity-specific measures reported? | None found for the proposed forensic classifier in the main paper. Accuracy percentages are exact source-class accuracy; FD ratio is an inter-/intra-source Fréchet distance ratio. No ROC/AUC, F1, authenticity AP or real-class sensitivity/specificity/operating point is provided. |
| 8. Are separate detection operating points or protocols evaluated? | None found. The experiments vary source architecture, GAN training data, initialization seed, frequency band, effective patch size, perceptual selection and perturbation immunization while retaining attribution labels. These variations do not create an independently measured binary protocol. |

### Exact quantitative findings

Every accuracy below is **source-attribution accuracy**, including real as a source; none is a separately reported binary detection score.

| Table and locator | Evaluated setting | CelebA accuracy % | LSUN accuracy % |
|---|---|---:|---:|
|1, p6/7561|Real plus four GAN architectures; proposed model|99.43|98.58|
|1, p6/7561|Same source setting; PRNU baseline|86.61|67.84|
|2, p6/7561|Real plus ProGAN training-data variants|99.50|97.66|
|3, p6/7561|Real plus ten ProGAN seed identities|99.14|97.04|
|3, p6/7561|Same setting; visualization network|97.07|96.58|
|6, p7/7562|Perceptually selected top10% test images|99.93|98.16|

Table1 fingerprint FD ratios are454.76/226.59 versus inception2.36/5.27 (CelebA/LSUN). These measure inter-/intra-source feature separation, not detector operating points. Table2 notation describes multiple ProGAN data-variant sources, not a separately scored two-class result; an uncertain exact total class count is not forced.

Tables4–5 (p6) retain source classification after frequency/patch restrictions. At8×8 resolution, low-/high-frequency source accuracy is67.44/78.74% on CelebA and63.80/80.58% on LSUN. A24×24 effective patch gives99.24/88.36%; a52×52 patch gives99.30/95.94%. These are patch-evidence experiments ending in source predictions, not localization or independently scored detection.

Tables7–8 (p8/7563) compare the attacked pretrained source classifier (Atk) with attack-category-aware fine-tuning (Dfs):

| Perturbation | CelebA Atk/Dfs % | LSUN Atk/Dfs % |
|---|---:|---:|
|Noise|9.14 /93.02|11.80 /95.30|
|Blur|49.64 /97.20|74.48 /96.68|
|Cropping|46.80 /98.28|86.20 /97.30|
|JPEG compression|8.77 /88.02|24.73 /92.40|
|Relighting|94.02 /98.66|62.21 /97.36|
|Combination|19.31 /72.64|24.44 /83.42|

All main Tables1–8, baseline rows, metric labels and perturbation definitions are transcribed in the manifest. Figure7’s sample fingerprint interactions are not an aggregate binary confusion matrix. No binary accuracy, ROC/AUC, F1, real-class sensitivity/specificity, authenticity AP or separate operating point was found in the complete main paper. No metric is calculated by collapsing source classes.

### Contrary evidence, confidence and proposal

The abstract/introduction and Section4.2 explicitly discuss distinguishing GAN images from real ones, interpreting the joint classifier as useful for visual forensics. That positive claim is preserved. It is inaccurate to say the work never considers authenticity or cannot enable a derived real/fake decision. The missing piece under this bounded review standard is an independently defined and scored authenticity endpoint. A wrong GAN-to-GAN prediction is an attribution error without necessarily being a real/fake error; aggregate source accuracy cannot be copied as exact binary accuracy. Section3.1’s service “authenticity” discussion concerns membership in a desired source/API, not a separately scored camera-real-versus-generated task.

**Accepted outcome:** `SUPPORTED_NO_CHANGE`; retain `source_attribution` and `method`. Confidence is high for the reported source task and numbers, and bounded for the no-addition recommendation under the required independent-authenticity criterion. The original evidence-only recommendation has now been accepted by the maintainer; terminal decision `review:09ce07963903ecd891c5` closes T631 without a taxonomy edit. The main paper’s20,000-real-image dataset statement conflicts with later100,000-image real subsets/per-source sampling; it is retained rather than silently repaired. External supplementary contents are unreviewed, and no broader absence claim is made about them.

## Retrieval accounting

| Case | Full-text attempts | Complete new manuscripts | Outcome |
|---|---:|---:|---|
|T046|1|0|Official DOI-derived ACM PDF route, HTTP403 HTML; no full version verified|
|T631|1|1|Official ICCV2019 CVF main paper,11pages, identity verified|
|Total|2|1|Within one new manuscript per paper/two total; no retries or extra versions|

Metadata/implementation access is separately enumerated in the manifest: DOI and author-listing link failures, target repository/three code pages and cached continuations, one exact-identity PDF search with no results, two raw-code cache-miss clicks, and the initial CVF HTML failure. Logical cached displays are not represented as newly measured HTTP requests. None is hidden as a successful manuscript. **Zero supplements, precursor manuscripts, unrelated papers, dataset/weight payloads, repository clones or code executions.** PDFs, failures, captures, rendered pages and operational receipts stay outside Git in `/private/tmp/b1g-evidence-2026-10-19/`.

## Corpus, review accounting and preservation

| Measure | Current count |
|---|---:|
|Public / formal / mapped / unmapped|674 /557 /613 /61|
|Relationship rows / unique pairs|1,410 /1,410|
|Detection / source attribution / localization|621 /84 /45|
|Method / dataset / benchmark / survey / analysis study|579 /134 /90 /21 /81|
|Original Batch B actions / historical papers|159 /148|
|Historical unresolved / active-public unresolved / distinct public papers before T631|149 /147 /136|
|Historical unresolved / active-public unresolved / distinct public papers after T631|148 /146 /135|

Only T631 closes. It has no other independent pending original Batch B action, so the distinct active-public paper count decreases by one. T046, T093, T608, T526 and P526 remain independently open. Batch C remains 41 total /28 resolved /13 deferred /0 maintainer judgments with the same debts. The separate 39-paper intake inventory, overlapping 14 taxonomy-debt papers and 12 held candidates remain unchanged and are not combined with original Batch B actions.

The fresh integrated baseline guards all 4,467 tracked files, all 4,414 primary tracked files, twelve prior B1A–F artifacts, protected 128/original 130 primary files, 49 frozen NeurIPS artifacts in each checkout, 119 ignored operational inputs and four C13 debt receipts. The isolated five-file allowlist consists of the decision registry, this existing report and manifest, new B1G regressions, and two directly required B1F historical transaction/accounting boundaries. The latter preserve exact original assertions at the published B1F endpoint and add live prefix/unique-T303 checks. All twelve independent historical-test repair files remain unchanged.

The documented Python 3.14.7 / pytest 9.1.1 / pytest-subtests 0.15.0 / Node 24.19.0 environment is used. All 117 offline historical inputs were already checksum-matched; read-only preflight required no restoration or replacement. Shared excludes, fixtures and historical receipt bytes are unchanged. No runtime-cache dependency is added to tests.

The current publication policy does not require a new full suite for this bounded administrative change. The predecessor's 1,963 ordinary tests and 389 subtests are a historical receipt, not a combined B1G full-suite result. The actual integrated-state focused results and four validators are recorded below. `other/no_action_after_review` does not trigger venue confirmations, mapping exclusions or institution overrides; public output dependencies are unchanged. No exporter is run and no new export-reproducibility claim is made.

<!-- B1G_VALIDATION_START -->
Integrated-state validation passed: **21 B1G regression tests**, plus **254 historical/consumer/B1F tests and 18 subtests**; zero failures, errors or skips. The two existing legacy test return-value warnings remain visible. All four current-scope validators passed with zero errors: curated database (294 existing warnings), public map (0 warnings) / paper preview (62 existing warnings), exclusions (2 existing warnings), and key-paper coverage. Read-only fixture checks before and after verified all 117 inputs; zero created or overwritten.



The measured pre-stage preservation gate passed 49/49 checks. Original evidence-only 43/43 and independent 45/45 receipts remain separately preserved. No B1G full suite or exporter was run; the predecessor's full-suite receipt is not represented as a new run.



`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`



The validated commit inputs are restricted to the five-file allowlist. The exact single T631 registry append, complete earlier decision prefix, both original scientific records, all public bytes, predecessor test repairs, primary checkout and protected inventories are checked. Staging and remote publication receive separate final read-only gates; this pre-commit document does not assert a future push.
<!-- B1G_VALIDATION_END -->

The commit's own SHA and post-push remote equality are verified outside its contents. This packet does not claim that a future push has already succeeded.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Source fingerprints

These are original evidence-baseline source hashes, retained as historical provenance. Only the current decision-registry hash differs after the single append; current source hashes and exact before/after registry hashes are recorded separately in the manifest. External capture/PDF hashes and exact provenance remain unchanged.

| Repository source | SHA256 |
|---|---|
| `data/curated/paper_taxonomy.csv` | `17b59d6a33ae77ebfad1d58f3791b051197f5117834faa4c93342f8a79323417` |
| `data/curated/papers.csv` | `edb1744a04968fb8a63d20f04aaa088866e9b37c0d261a94e6f98beb8947bc38` |
| `data/curated/review_decisions.csv` | `59023f2bf9e0f88a2f83bffc06b5947e8ce3855cee5ca90a188e5a61066a6a6e` |
| `data/processed/literature51_2026_10_16/followup/receipt.json` | `b24deabfd36186ed278d2afd4ac60814a4c78d71e04151c25cee52d27460d4f3` |
| `data/processed/literature51_2026_10_16/followup/review.json` | `cdf83d05b4ab57fe5a37034f5213aef40f7c6ee0095c5d22d3988ca784d03312` |
| `data/processed/literature51_2026_10_16/main_integration/manifest.json` | `5959e8628cc7e272ac45f0a2afd5e508412a416615c61d411b4529e135077a79` |
| `data/processed/literature51_2026_10_16/plan.json` | `b6af4975b2be41958176448000d240dcdbc2dd00a507e8edc3a7a7b0027356ab` |
| `data/processed/systematic_tier2_application_2026_09/legacy_screening_636.json` | `005509ff252b0bf4d04769c6c1a65c8796f58db8f9844b871d4b0b39e02eab47` |
| `data/raw/ant_gap_fill_2026_09_05/openalex_exact_title_results.json` | `01786d62d432542cab8184bcb65c486990a1c9b3111b65400bf3e2977608769f` |
| `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json` | `ee097956eafca891155380e95d13173070fca413aad371f0dc57bfcb86374f55` |
| `data/raw/corpus_quality_audit_2026_10_04/publication_metadata_review.json` | `b2ef27b7c70dd991f5ee29a794001bbd9f6ff6da2e9eff5cdb5d30c246d0726c` |
| `data/raw/corpus_quality_audit_2026_10_04/source_checks.json` | `78c2aed641161705a0a22658a2df38cc7e53550eb1857d119106a4a419b02227` |
| `data/raw/corpus_quality_audit_2026_10_04/taxonomy_review.json` | `ad84e82b3dd82d0018d57caeed93353585ca4e83e3e2d800c00c0db656d637a1` |
| `data/raw/openalex/20260619T122106Z_009_source-attribution-generated-images.json` | `839f6f68766637be72cdefa9265d35b412a871b5e84d0b219aee22af01964690` |
| `data/raw/systematic_gap_audit_2026_10_02/discovery_records.json` | `6ec9e001aa007ef4fcd528243c0e2da099a8e9fed359d8050cb27ef8088edc0d` |
| `data/raw/systematic_gap_audit_2026_10_02/icml2026_screening.json` | `09c1387fd655d3ef6dc6340b29c11b3d52a1a1c4a99c88f260b862123515ee5d` |
| `data/raw/systematic_literature_2026_09/2554e5b57b6a121f3e5b.gz` | `14df2b9f22f52e28cf8f239f237d9c6be71ce1c7a17e36268cdb7c3dc53037bb` |
| `data/raw/systematic_literature_2026_09/a58a312ed612f8266c74.gz` | `6c0ce05348d64215ccf0195281b51d197a685af17680e4c0ebe7dda5d6d81962` |
| `docs/corpus_quality_batch_b_intake_triage_2026_10_12.md` | `a40d37dc3abd8198ea4d00384d19b25905a036519ee691718fac1d11a19e5459` |
| `docs/literature51_main_integration_2026_10_17.md` | `6f0e138d4bbdbd1d8032f84479cca0fae791f819ac998003f502faecc59101c4` |
| `web/data/public_preview_map_data.json` | `09b6f815597b2c14349dffc359b7844eab9c2b9a758ec02ef669476e009b627b` |
| `web/data/public_preview_papers.json` | `9b1565482ab2095fa43ab3b9e60504c733fd0d43cd84bc4d5f3f8d98f2eb9781` |
