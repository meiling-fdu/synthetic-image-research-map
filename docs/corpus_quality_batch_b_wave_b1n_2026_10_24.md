# Batch B Wave B1N — R596 benchmark accepted; R234 deferred

Maintainer adjudication recorded on 2026-10-25. Published predecessor `05a89df9e5b3543c1231dc5934f55320aec53fa9`. This section records the current approved transaction; the complete original evidence-only report follows verbatim as historical evidence. Its original pending flags, transport history and timestamps retain their original meaning.

## R596 approved correction

**RepMix: Representation Mixing for Robust Attribution of Synthesized Images**, canonical ID `curated:625ba11125534aedd39d`: research types **method;dataset → method;dataset;benchmark**. Existing **detection;source_attribution** tasks and **fully_generated** scope are unchanged. Accepted disposition **PROPOSE_CORRECTION_ACCEPTED**. Exactly one original R596 action closes through terminal decision **`review:bec491a789b07af83e1e`**, using the established `other` / `no_action_after_review` vocabulary. This terminal action means no further remediation remains for the approved correction; it does not mean no data changed.

Locked **R2** accepts Attribution88 as a separately reusable evaluation benchmark/protocol/resource beyond the RepMix model and its retained dataset role. Section 3 separately defines the source classes, image construction and per-cell base partitions; independent source-attribution approaches use the same held-out evaluation conditions. The rationale does not rely solely on its scale or the word benchmark.

The complete official ECVA ECCV 2022 manuscript is **18 pages**, authors **Tu Bui, Ning Yu, John Collomosse**, canonical DOI **10.1007/978-3-031-19781-9_9**, SHA-256 **5fb6d9576126ad053381669f122ffcda440ffc1cb3e36954809de28aa9bceee0**. Separate Springer and arXiv full-version equivalence remains unverified. No new source was retrieved during adjudication.

The source label space is **Real, ProGAN, CramerGAN, MMDGAN, SNGAN, StyleGAN, StyleGAN2, StyleGAN3**: seven known GAN architectures and one real class, not checkpoint identity labels. Eleven semantic categories are represented, six exposed during attribution training and five held out. Intended semantic-specific generator-instance changes are coupled with semantic changes. Architecture labels remain fixed: **zero held-out architectures and no unknown-architecture open-set evaluation**.

Declared base construction is **12,000 ×8 sources ×11 semantics =1,056,000 images**, with **10,000/1,000/1,000** train/validation/test per source–semantic cell. All-eleven base pools are **880,000/88,000/88,000**, and the six-semantic training subset implies **480,000**. Actual validation semantic membership is unverified; **48,000 is conditional only**. Nineteen corruption types have five severities; four types (glass blur, motion blur, zoom blur, snow) are held out. Corruption/severity variants are not multiplied into a newly verified base-image total.

Main Attribution88 Table 1 results:

| Method | Raw detection accuracy | Eight-way attribution accuracy | NMI |
| --- | ---: | ---: | ---: |
| RepMix | 0.9745 | 0.8207 | 0.6679 |
| Yu reimplementation | 0.9306 | 0.6784 | 0.4666 |

Source accuracy and NMI include Real; detection collapses real versus non-real. The nominal binary ratio is **1:7**, so detection is **raw accuracy, not balanced accuracy**. Conditional attribution declines from **0.9377 seen semantics/seen transformations** to **0.6505 unseen/unseen**. Glass-blur attribution is approximately **0.67 RepMix versus0.77 Yu**; no uniform superiority claim is accepted. The different clean control and ablation protocols, all142 printed transcriptions, Table 2 accuracy-drop versus final-accuracy distinction,0.01 percentage-point prose/table subtraction differences and nonliteral universal2× claim remain in the original evidence. No result is changed to resolve a contradiction.

Author repository revision **b22608ffca12c38a9a13876f0f2e5268991b9afe** advertises archives, split files and code, with CC BY4.0 declaration. Actual archives, image contents, CSV membership, upstream LSUN/CelebA rights, checkpoint/configuration equivalence and numerical reproduction remain unverified. The paper says early stopping by validation accuracy; inspected code uses validation loss. Contribution confidence is **high** and operational reproducibility confidence **medium**.

## R234 remains one unresolved original action

**Universal Denoising Patterns for Diffusion Image Detection**, `curated:03f893b9484ea2d09c22`, remains **EVIDENCE_STILL_INSUFFICIENT under both R1 and R2**. Its administrative **method** classification, **detection** task, **fully_generated** scope, full authoritative rows and two map relationships are unchanged. No terminal R234 decision, partial adjudication or second review action is created; current taxonomy is not scientifically reconfirmed as a no-change finding.

The official ICASSP2026 program verifies identity and six authors. The DOI and actual observed conference manuscript route each reached IEEE document11462468 with HTTP202/empty body; a candidate author homepage failed TLS. No complete manuscript was obtained, and no failed retrieval was retried during this adjudication. DiffuGen originality/reusable contribution,65,000 synthetic plus5,000 real images,13 generators, approximately99% accuracy, generation provenance, splits, independent benchmark protocol, release/license and reproduction remain explicitly **unverified metadata claims**.

Preserve **OUT_OF_SCOPE_BIBLIOGRAPHIC_OBSERVATION**: actual `data/curated/papers.csv` `raw_venue` contains2025, while canonical year/DOI and the official program identify2026. Year,raw_venue,venue_id,venue,DOI,title,authors and every other R234 authoritative field remain unchanged; no new bibliographic review action is created.

## Exact application and deterministic export delta

Applied once at **2026-10-25T02:02:01Z**. Exactly **seven existing CSV cells** change across **two R596 rows**: data/curated/papers.csv: research_types; data/curated/paper_taxonomy.csv: research_types, research_types_review_reason, research_types_evidence_tier, research_types_evidence_source, research_types_evidence_excerpt, audited_at. The registry appends exactly one row, **96→97**, preserving the entire original96-row byte prefix. No other existing CSV row or cell changes.

Measured exporter delta: exactly **one existing public paper (R596)** and **3 existing dependent map records**, only research types and direct research-type review reason. All **673 other public records**, **1407 other map records** and all **1,410 relationship identity tuples** remain unchanged. R234 is entirely unchanged. No paper, institution, affiliation, task, scope or publication metadata is added, removed or reassigned. Generated JSON is produced by the established offline exporter, never manually patched.

Direct generated-report changes are only the deterministic public-report timestamp and key-paper coverage input fingerprint; coverage statistics and generated manual CSVs remain unchanged. The complete semantic receipt with actual dependent IDs is in the companion manifest.

Recomputed corpus: **674 public,557 formal,613 mapped,61 unmapped,1,410 relationships and1,410 unique pairs**. Taxonomy: **621 detection,84 source_attribution,45 localization,578 method,137 dataset,94 benchmark,21 survey,82 analysis_study**.

Original Batch B denominator remains **159 actions/148 papers**. Closing only R596 yields **137 historical unresolved actions/127 papers** and **135 active-public unresolved actions/125 papers**. R234 remains open. Batch C's13deferred debts and the separate39-paper inventory remain unchanged.

## Evidence, validation and publication boundary

The original complete manifest/report are losslessly archived in the companion manifest, and the complete original report follows. Every nested scientific review, original source fingerprint, independent result, counterexample, uncertainty and timestamp remains unchanged. Original retrieval accounting stays **R596 one complete manuscript; R234 zero; total one**, with **zero adjudication downloads**. Portable original evidence-stage preservation/packet/science/provenance receipts retain separate43/36/120/42pass counts; worker checks remain50/50 and60/60.

All required final-state validation gates passed.

Focused validation: **110 tests +12 subtests passed**, including **29 B1N regression cases**, with zero failures/errors/skips. All four current-scope validators passed with **zero errors**; actual validator warnings: curated 294, public 62, exclusions 2, coverage 0.

The full repository suite ran **once**: **2165 tests +389 subtests passed**, **zero failures/errors/skips**, **2 warnings**. Its source/output/input inventory is byte-preserved. Existing warning details and exact commands/log/XML hashes are retained in the companion manifest.

Two sequential offline export verification passes completed after the full suite, comparing the complete **4611-path inventory** and all seven export outputs byte-for-byte, with no concurrent exporter and no protected/input/Git drift. Read-only historical fixture checks verified117 inputs before and after, creating zero files. **EXPORT_REPRODUCIBLE =1**. The initial approved correction export is separate from these two verification passes.

`FOCUSED_FAILURES = 0`

`VALIDATOR_ERRORS = 0`

`FULL_SUITE_FAILURES = 0`

`EXPORT_REPRODUCIBLE = 1`

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

The complete required suite ran once against stabilized code/data/scientific evidence and preserved its input inventory. Two sequential final-state offline export passes then preserved every compared byte/mode/path. Afterward, measured validation/publication metadata was attached and one extra trailing LF was removed from the new B1N regression file for git diff --check. Exact Python AST and significant-token equality to the full-suite-tested version was proved; all29 B1N regressions reran successfully. No scientific data, original evidence, test logic, exporter implementation or public output changed.

Primary checkout, all128 protected files, all49 frozen NeurIPS artifacts in both roots, all119 ignored operational inputs, prior decisions/evidence, Batch C's13deferred cases, separate39-paper inventory and other active worktrees passed the measured preservation gates.

<!-- B1N_FINAL_VALIDATION -->

Validated single-commit subject: `fix: classify R596 Attribution88 benchmark`. At commit preparation, validation has passed. Publication success is claimed only after exact explicit staging, the single commit, a safe normal fast-forward and independent remote verification. The containing commit and external post-push receipts supply actual SHA/parent/synchronization without circular self-reference.

7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA

## Complete original B1N evidence-only report — historical, verbatim

# Batch B Wave B1N — Attribution88 and DiffuGen research-type evidence

Evidence-only review, 2026-10-24. Published baseline `05a89df9e5b3543c1231dc5934f55320aec53fa9` was fetched and verified: isolated HEAD equals origin/main, ahead/behind 0/0. Both original actions remain pending. This packet makes no authoritative correction or terminal decision; maintainer acceptance is outstanding.

| Review | Existing research types | Provisional scientific outcome | Complete proposal | Acceptance |
| --- | --- | --- | --- | --- |
| R596 | method;dataset | BENCHMARK_ADDITION_SUPPORTED | method;dataset;benchmark | Pending; no change applied |
| R234 | method | R1 and R2 separately EVIDENCE_STILL_INSUFFICIENT | method retained as administrative hold only | Atomic original action pending |

## Locked policies and boundaries

Source: `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json` (SHA-256 `ee097956eafca891155380e95d13173070fca413aad371f0dc57bfcb86374f55`).

R1: Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.

R2: Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

Dataset and benchmark roles are independent and compatible. Public download availability is not the sole contribution criterion; linked archives do not establish their actual completeness, licensing or reproducibility. The four accepted decisions R574/R400/R335/R034 are bounded precedents, not automatic classifications. Their exact published records are bound in the companion manifest.

## Manuscript budget and source preservation

Exactly one new complete manuscript was obtained: R596=1, R234=0, total 1 of maximum 2. R596's initial HTTP 200 timed out after a partial body; one matching-ETag HTTP 206 continuation completed the same 18-page PDF. These are two transport transactions for one manuscript. R234's two distinct bounded official routes each returned HTTP 202/empty bodies; no complete R234 source is claimed.

R596: official ECVA ECCV 2022 accepted manuscript, DOI `10.1007/978-3-031-19781-9_9`, PDF SHA-256 `5fb6d9576126ad053381669f122ffcda440ffc1cb3e36954809de28aa9bceee0`, 6,642,878 bytes, 18 pages. Separate Springer PDF equivalence and arXiv-version equivalence are unverified. Author-repository revision `b22608ffca12c38a9a13876f0f2e5268991b9afe` was inspected read-only through metadata and individual files. No author code was executed.

R234: the official ICASSP 2026 program verifies the title and six-author order, not complete scientific methods. Program body SHA-256 `700aee3a33d136fd859c425d59cce757d0b66a51d572ea3272fa3c8d196396c9`. Neither the DOI nor the observed `goto_manuscript.php?pn=1775` route yielded a manuscript. Complete-PDF URL/version/hash/page count remain null.

No supplements, datasets/image archives, weights, repository archives or clones were downloaded. Complete manuscripts, downloaded metadata, raw transport receipts, source manifests and scratch scripts remain in `/private/tmp/b1n-evidence-2026-10-24`, outside the repository. The companion manifest preserves frozen worker-review records and authenticated operational pointers; the following scientific case reports retain the source-located evidence and limitations.

## R596 scientific evidence report

**Provisional outcome: BENCHMARK_ADDITION_SUPPORTED.** Proposed complete types: `method;dataset;benchmark`. Contribution confidence is high; operational reproducibility confidence is medium. Maintainer acceptance is pending. No authoritative data, review decision, forensic task, image scope, inclusion, institution, relationship or publication metadata has changed.

### Exact review and source identity

Canonical ID `curated:625ba11125534aedd39d`. Current types `method;dataset`; tasks `detection;source_attribution`; scope `fully_generated`. The original R596 question asks whether Attribution88 is a substantive reusable benchmark under locked R2, beyond the retained method and dataset roles. There are three existing map rows and no independent pending same-paper Batch B action.

The complete [official ECVA ECCV 2022 manuscript](https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136740140.pdf) has 18 pages (14 main plus 4 references), 6,642,878 bytes, SHA-256 `5fb6d9576126ad053381669f122ffcda440ffc1cb3e36954809de28aa9bceee0`. Exact title: **RepMix: Representation Mixing for Robust Attribution of Synthesized Images**. Authors: Tu Bui, Ning Yu and John Collomosse. Canonical DOI: `10.1007/978-3-031-19781-9_9`. All pages were read; pages 4/5/8/10/11/13 were rendered and visually checked. Root independently reviewed the complete source before the worker verdict.

No usable complete local copy was found after magic-byte/gzip/SHA screening of 34,339 paths and identity inspection of 76 PDF bodies. The single ECVA request timed out after receiving 3,167,823 bytes of an HTTP 200 body. One exact matching-ETag HTTP 206 continuation supplied bytes 3167823–6642877/6642878, or 3,475,055 missing bytes. Both bodies/headers/receipts remain preserved. This reconstructs one complete version, not two downloaded manuscripts. No arXiv PDF, supplement, data archive, model weight or repository archive was obtained.

ArXiv abstract metadata lists v1 on 5 July 2022 and v2 on 12 July 2022 (typo fix and added supplement). The current canonical arXiv v2 is preserved; ECVA-versus-arXiv or separate Springer PDF byte equivalence is unverified. The ECVA PDF creation metadata is not treated as an independently verified publication date.

### Scientific and policy conclusion

RepMix is the model: intermediate representation mixing, a 256-D ResNet50 embedding and a compound hierarchical real/fake plus source-attribution loss. Attribution88 is separately defined before that model: fixed source/semantic construction, partitioning, held-out semantics, held-out corruption types and model-independent metrics, evaluated with five independent baseline families.

> Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

The explicit independent task/data partition/held-out evaluation design and multi-method application go beyond ordinary method-validation tables and meet the reusable evaluation benchmark/protocol/resource limb of R2. A new code library or verified full archive download is not imposed as the sole or mandatory condition. Remaining reproduction restrictions are recorded independently.

**Competing interpretation:** The resource was motivated by the RepMix robustness claim, relies on the authors’ architecture/curation choices and has unverified complete archive/split contents. A conservative reading could limit operational reproducibility or question portability until exact configurations are obtained. The word benchmark, scale and number of sources alone would not suffice.

R1 remains independently documented: Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient. The existing dataset role is retained and is not reopened as a new action.

### Twenty required scientific questions

#### 1. The definition of the source attribution task.

The input is an image and the predicted source is one of eight fixed classes: a real-image class or one of seven known GAN architecture families. Semantic content is a separate nuisance label. The method jointly trains real/fake detection and source attribution, while the benchmark evaluates source prediction across held-out semantics and perturbations.

**Locator:** §§1–3, pp.2–5; §4.1, p.6; §5.2 Metrics, p.9.

**Boundary:** This is explicitly closed-world attribution to a known architecture label set, not discovery or rejection of an unknown GAN architecture. No unknown-source AUC, rejection threshold or OSCR protocol is defined.

#### 2. Whether attribution labels correspond to GAN architectures or specific model instances.

Labels represent architecture families, not unique trained checkpoints. Each architecture is represented by semantic-specific GAN training instances. Figure 1 explicitly says 77 GAN models: seven architecture families × eleven semantic categories. The source label is shared across instances of the same architecture.

**Locator:** §1, p.2; §3 and Fig.1, p.4; §4, p.5.

**Boundary:** The intended semantic holdout also holds out the corresponding semantic-specific GAN instances, but architecture labels remain known. Checkpoint identities, pretraining/training equivalence and exact asset membership are not audited; semantic change and instance change are coupled, not independently controlled factors. This is not a separate random-seed or architecture-holdout experiment.

#### 3. Whether the real-image class is included in the source label space.

Yes. Real is one of eight source classes and participates in eight-way attribution accuracy and NMI. Binary detection accuracy collapses predicted class zero versus all positive GAN-source labels, as test.py:54–58 confirms.

**Locator:** §3, p.4; §4.1–4.2, pp.6–7; §5.2, p.9; pinned test.py:48–58 and utils/analysis.py:163–167.

**Boundary:** Per-source balance gives one real class and seven fake classes: binary real/fake counts are 1:7, so reported detection accuracy is not balanced accuracy. An always-fake rule would score 87.5% on the nominal balanced eight-source base distribution; no such baseline experiment was rerun.

#### 4. The eight source classes.

Real; ProGAN; CramerGAN; MMDGAN; SNGAN; StyleGAN; StyleGAN2; StyleGAN3. The three StyleGAN generations are separate architecture labels; real imagery is pooled as one source class across semantics.

**Locator:** §3, p.4; Fig.7 source-label axes, p.13.

**Boundary:** Class names establish the scientific label space, not independently inspected CSV label mappings or archive contents. The paper’s source-family naming is retained without adding contemporary generators.

#### 5. The seven GAN architectures.

The seven are ProGAN, CramerGAN, MMDGAN, SNGAN, StyleGAN, StyleGAN2 and StyleGAN3. They are unconditional GAN families in this study; conditional GAN expansion is future work. Their nominal 77 semantic-specific instances do not create 77 attribution labels.

**Locator:** §2, p.3; §3, pp.4–5; §6, p.14; refs.5,6,26–29,39.

**Boundary:** The main manuscript does not pin every training-code revision, pretrained checkpoint hash, seed or hyperparameter. Further GAN training detail is deferred to an unretrieved supplement. No diffusion, unknown-generator or conditional-GAN generalization is established.

#### 6. The eleven semantic categories.

Training exposes six categories: CelebA Face, Bedroom, Airplane, Classroom, Cow and Church Outdoor. Five categories are held out from attribution training: Bridge, Bus, Sheep, Kitchen and Cat. Ten scene/object sets come from LSUN, with CelebA adding faces.

**Locator:** §3, pp.4–5.

**Boundary:** CelebA is acknowledged as more aligned/curated than the other sets. Exact sample IDs and semantic CSV codes were not inspected. Held-out semantic labels are not unknown architecture labels.

#### 7. Original GAN training and generated-image curation procedures.

For each semantic category the authors select 100,000 real images for GAN training and a disjoint 12,000 real images for attribution. They use pretrained GANs where available and otherwise train public implementations to generate 128×128 images. One hundred thousand outputs per nominal GAN instance yield 7.7 million synthetic candidates. They extract named InceptionV3 perceptual features, run k-means with k=100, rank generated candidates by distance to a closest real image, and retain 120 per cluster, yielding 12,000 per GAN/semantic cell.

**Locator:** §3 and Fig.1, pp.4–5.

**Boundary:** The exact nearest-real reference pool, distance, feature layer, cluster seed, checkpoint IDs and effects of pretrained reuse are not established in the main source. The named InceptionV3 extractor cites ref.61, a perceptual-metric paper; this citation/detail tension is preserved, not repaired. Curation occurs before attribution partitions; duplicate/content independence and source-image rights are not independently verified.

#### 8. Exact final image counts.

The declared balanced cell size is 12,000 images × eight source classes × eleven semantics = 1,056,000 final base images. Derived totals are 132,000 real and 924,000 synthetic. Seven families × eleven semantic instances × 100,000 candidates = 7.7 million generated candidates before curation. The manuscript rounds the final corpus to approximately one million; the pinned README gives the exact product 1,056,000.

**Locator:** §3, pp.4–5; Fig.1; pinned README, The Attribution88 benchmark.

**Boundary:** These are source-specified/derived counts, not archive-verified sample counts. Intermediate candidates, corruptions and final processed test assets must not be added together as unique base images.

#### 9. Training, validation and test splits.

Each source/semantic cell is partitioned into 10,000 training, 1,000 validation and 1,000 test images. Across all eleven semantics this defines base pools of 880,000/88,000/88,000. With the six default training semantics, the nominal training subset is 480,000 images. The repository requires externally supplied train/validation/test CSV files.

**Locator:** §3, p.5; README training/evaluation commands; train.py:42–64,107–109; utils/folder.py:63–99.

**Boundary:** The actual validation semantic membership is not explicit in the main manuscript or inspected CSV bodies. A 48,000 validation set is only conditional on using the six training semantics and is not reported as verified. The CSV files are advertised inside an undownloaded archive, so exact disjointness, identifiers, shuffling and processed-test multiplicity remain unverified.

#### 10. Seen versus unseen semantic categories.

Default evaluation trains on the six named semantics and tests all eleven. Figure 7 reports attribution accuracy 0.9377 for seen semantics/seen transformations, 0.8405 for seen/unseen, 0.7192 for unseen/seen and 0.6505 for unseen/unseen. The benchmark therefore measures semantic and perturbation generalization within a fixed eight-source label space, with a substantial remaining performance gap.

**Locator:** §3, p.5; §5.4, p.10; Fig.7, p.13.

**Boundary:** The intended semantic-specific model instances associated with held-out categories are unseen, but this does not isolate model-instance shift from semantic shift or test unknown architectures. The four conditional scores are not the overall Table 1 score and should not be pooled without known weighting.

#### 11. Perturbation types and severity levels.

The paper uses nineteen ImageNet-C corruption types, each with five severity levels. Figure 3 names Gaussian/shot/impulse noise; defocus blur; frost; fog; brightness; contrast; elastic transform; pixelate; JPEG compression; speckle noise; Gaussian blur; spatter; saturate; glass/motion/zoom blur; and snow. The pinned wrapper samples integer severity 1–5, resizes to 224 before corruption and back to original size afterward.

**Locator:** §3, p.5; Fig.3, p.8; utils/augment_imagenetc.py:26–73.

**Boundary:** The exact ImageNet-C dependency revision, random corruption realizations and whether every base test image receives all 95 type/severity combinations are not verified. These are synthetic benign transformations, not a measured live-platform upload/download study.

#### 12. Seen versus unseen perturbations.

Fifteen corruption types are exposed during training; four are held out. Figure 3 marks glass blur, motion blur, zoom blur and snow as unseen. The pinned helper uses train IDs [0,1,2,3,8,9,10,11,12,13,14,15,16,17,18] and held-out IDs [4,5,6,7], explicitly citing speed/fork-safety constraints. Main testing covers all types; Figure 4 right separately evaluates four held-out types while varying training augmentation count.

**Locator:** §3, p.5; Fig.3, p.8; §5.4 and Fig.4, p.10; utils/augment_imagenetc.py:26–39,95–127.

**Boundary:** The four held-out types are not unseen GANs. The generic test.py loads a preprocessed test directory and applies a clean resize transform; it does not itself generate the full nineteen-type benchmark sweep. The processed archive/CSV realizations and paper-time code equivalence remain unverified.

#### 13. Detection accuracy versus generator attribution accuracy.

Attribution88 Table 1 reports RepMix raw binary detection accuracy 0.9745, eight-way source attribution accuracy 0.8207 and source NMI 0.6679. The closest Yu reimplementation has 0.9306/0.6784/0.4666: differences are 4.39 and 14.23 percentage points for detection and attribution. The single-semantic five-source clean control instead reports 1.0000/0.9994/0.9975 and is a different task condition.

**Locator:** Table 1, p.8; §5.2, p.9; test.py:54–58.

**Boundary:** High detection accuracy does not imply equally high source classification. Detection is an auxiliary real-versus-rest raw accuracy on a 1:7 binary class distribution, not balanced accuracy or an independent unknown-generator test. Control results must not be substituted for full Attribution88 performance.

#### 14. Attribution-specific Normalized Mutual Information.

NMI measures dependence between predicted and true source labels. The pinned compute_nmi uses sklearn.normalized_mutual_info_score(labels,pred); test.py passes all source labels without removing Real. Table 1 full benchmark NMI is RepMix 0.6679, Yu reimplementation 0.4666, original Yu code 0.4028, DCT-CNN 0.4061, Reverse Engineering 0.3653, EigenFace 0.0034 and PRNU 0.0003.

**Locator:** §5.2 Metrics, p.9; Table 1, p.8; utils/analysis.py:163–167; test.py:48–58.

**Boundary:** NMI is not a probability, semantic classification score or unknown-model rejection metric. It complements source accuracy and can be invariant to label permutations; its value must not be restated as percent correct attribution. No numerical experiment was reproduced.

#### 15. Independent baseline methods and their evaluation conditions.

Five baseline families are Yu et al., DCT-CNN, Reverse Engineering, EigenFace and PRNU; Yu has both the authors’ reimplementation and the original public-code row, giving six comparator rows. The paper says public code and the same data augmentation are used. The clean control uses five source classes, one semantic, no ImageNet-C and minimal crop/flip. Full Attribution88 has eight sources and semantic/corruption tests. RepMix uses ResNet50, 256-D embedding, beta 0.4 mixing, random image pairs, resize 256, crop 224, flip, 95% corruption probability, Adam 1e-4, decay 0.85 and at most 30 epochs.

**Locator:** §5.1–5.2, pp.7–9; Table 1, p.8.

**Boundary:** Further baseline settings are in the unretrieved supplement; identical architectures, compute, checkpoints and all hyperparameters are not independently verified. The inspected training script monitors validation loss for early stopping/checkpoints, whereas the paper says validation accuracy. The current default code starts with ImageNet-pretrained ResNet50 and batch 32, but exact paper commands and seeds are not bound to that snapshot.

#### 16. Whether the published protocol is independent of RepMix.

Yes in scientific definition: Section 3 separately specifies architecture source classes, multiple semantic-specific instances, fixed per-cell partitions and a nineteen-corruption stress test before introducing RepMix in Section 4. The authors motivate fixed image/split release to address inconsistent prior baseline evaluations. Multiple independent source-attribution algorithms are actually compared under that framework.

**Locator:** §3, pp.4–5; §4, pp.5–7; §5.2 and Table 1, pp.8–9.

**Boundary:** It was designed to evaluate the authors’ robustness claim and shares their chosen GAN families/curation biases. Exact operational reuse is limited by undownloaded split assets and incomplete configuration verification. The benchmark label is justified by the independent protocol, not the paper’s use of the word benchmark or the number of images alone.

#### 17. Whether another source-attribution model can use the same evaluation protocol.

Yes: another model can train on the fixed known source labels and permitted semantic/corruption subset, then predict eight source labels on the common test resource, scored by source accuracy, NMI and auxiliary real/fake accuracy. Actual comparison of CNN, frequency-based, reverse-engineering, EigenFace and PRNU methods substantiates model-independent application.

**Locator:** §3; §5.2; Table 1; README; CSV interface in utils/folder.py:63–99.

**Boundary:** The published test.py itself loads a RepMix checkpoint, not a generic plug-in evaluator. Reusing the scientific benchmark does not require adopting RepMix, but would require a model adapter and access to the advertised archive/split definitions. No independent end-to-end installation or evaluation was run.

#### 18. Dataset release references and split-file definitions.

At repository commit b22608ffca12c38a9a13876f0f2e5268991b9afe, README advertises Attribution88.tar.gz (30 GB) and a processed Attribution88_test.tar.gz (5.4 GB) on the author’s CVSSP host, and states train/validation/test splits are inside the full archive. Commands pass train.csv, val.csv and test.csv. The fetched untruncated tree has 24 paths and includes training, evaluation, loader, augmentation and metric code. The loader requires path,label,dlabel columns, separating source and semantic labels.

**Locator:** Pinned README and recursive tree; train.py:107–109; test.py:67–69; utils/folder.py:63–99.

**Boundary:** No archive URL was requested, so archive accessibility, byte completeness, sample contents, CSV membership, label mappings and exact final resource counts are not verified. No standalone split CSV is listed in the fetched tree. Filename/path interfaces establish a design and release claim, not inspected split payloads.

#### 19. Dataset and source-image licensing.

The pinned README shows a CC BY 4.0 badge and the fetched root LICENSE is the Creative Commons Attribution 4.0 International text. The repository therefore has an explicit license declaration, unlike a bare public link. The manuscript identifies LSUN and CelebA as real-image sources.

**Locator:** Pinned README; LICENSE blob 2f244ac814036ecd9ba9f69782e89ce6b1dca9eb; §3, pp.4–5.

**Boundary:** A repository license and badge do not independently verify every external archive asset’s license or the underlying LSUN/CelebA redistribution rights. The archive was not opened, and no separate image-license manifest or third-party rights audit was inspected. No legal permission or complete licensed release is inferred from public visibility.

#### 20. Remaining content leakage, semantic overlap, GAN-instance and reproduction limitations.

The paper’s disjoint 100k GAN-training versus 12k real-attribution selection and semantic holdout are meaningful controls. Nonetheless, nominal random per-cell partitions do not prove image-content/near-duplicate independence. Semantics, training instances, GAN quality and curation may covary. Similar StyleGAN generations remain confused, strong perturbations cause failures, and Figure 7 shows substantial held-out semantic/perturbation degradation.

**Locator:** §3, pp.4–5; Figs.7–9 and §§5.7–6, pp.12–14; pinned code/release metadata.

**Boundary:** Actual CSVs, deduplication, source-image identity, checkpoint hashes, repeated seeds, uncertainty intervals, preprocessing realizations, supplement details and numerical reproduction remain unverified. No claim of content leakage having occurred is made. Closed-set semantic/instance generalization must not be upgraded to unknown-architecture open set, guaranteed robustness or measured social-platform deployment.

### Exact quantitative evidence

All three printed tables below retain their original precision: 81 numeric cells. Another 57 explicitly printed Figure 3 attribution bar labels and four Figure 7 matrix-title accuracies are preserved in quantitative_tables.json. Unlabelled detection bars/curves were not digitized, and no numerical experiment was rerun.

#### Table 1 — PDF page 8

Control: one semantic, five source classes (Real + four GANs), no ImageNet-C, crop/flip. Attribution88: eight source classes, six seen and five held-out semantic categories, 19 perturbations. Accuracy/NMI are unitless printed fractions, not percentages; detection collapses real versus non-real and is not balanced accuracy.

| Method | control_detection_accuracy | control_attribution_accuracy | control_attribution_NMI | Attribution88_detection_accuracy | Attribution88_attribution_accuracy | Attribution88_attribution_NMI |
| --- | --- | --- | --- | --- | --- | --- |
| RepMix | 1.0000 | 0.9994 | 0.9975 | 0.9745 | 0.8207 | 0.6679 |
| Yu et al. reimplementation | 0.9910 | 0.9838 | 0.9458 | 0.9306 | 0.6784 | 0.4666 |
| Yu et al. original public code | 0.9888 | 0.9844 | 0.9455 | 0.9190 | 0.6322 | 0.4028 |
| DCT-CNN | 0.9922 | 0.9838 | 0.9526 | 0.9001 | 0.6447 | 0.4061 |
| Reverse Engineering | 0.9976 | 0.9960 | 0.9834 | 0.8665 | 0.5637 | 0.3653 |
| EigenFace | 0.8262 | 0.6538 | 0.4515 | 0.7829 | 0.1515 | 0.0034 |
| PRNU | 0.8544 | 0.8482 | 0.7389 | 0.7845 | 0.1252 | 0.0003 |

#### Table 2 — PDF page 10

Attribution accuracy drop before minus after 20-iteration untargeted white-box I-FGSM. Lower is better; not attacked accuracy itself.

| Method | epsilon_2_over_255 | epsilon_4_over_255 | epsilon_8_over_255 | epsilon_16_over_255 | epsilon_24_over_255 | epsilon_32_over_255 |
| --- | --- | --- | --- | --- | --- | --- |
| RepMix | 0.1509 | 0.1952 | 0.2454 | 0.3008 | 0.3333 | 0.3572 |
| Yu et al. | 0.2113 | 0.2709 | 0.3328 | 0.3945 | 0.4303 | 0.4534 |
| DCT-CNN | 0.1545 | 0.2190 | 0.2831 | 0.3375 | 0.3642 | 0.3812 |

#### Table 3 — PDF page 11

Ablation subset: all eight source classes, two training semantic classes and four test semantic classes (two seen/two unseen). This is not the full Table 1 setting.

| Method | detection_accuracy | attribution_accuracy | attribution_NMI |
| --- | --- | --- | --- |
| All components | 0.9426 | 0.7400 | 0.5546 |
| Without compound loss | 0.9364 | 0.7204 | 0.5280 |
| Without RepMix | 0.9296 | 0.7188 | 0.5205 |
| Without RepMix and compound loss | 0.9283 | 0.7129 | 0.5167 |
| Without augmentation | 0.7044 | 0.2762 | 0.0856 |
| VGG16 | 0.9493 | 0.7150 | 0.5315 |
| AlexNet | 0.8818 | 0.5280 | 0.2817 |

#### Printed figure evidence

Figure 7 conditional attribution accuracy: seen semantic/seen transformation **0.9377**; seen/unseen **0.8405**; unseen/seen **0.7192**; unseen/unseen **0.6505**. These separate conditions show remaining generalization loss, not open-set unknown-generator evaluation.

Figure 3 attribution counterexample: glass blur gives RepMix **0.67**, Yu **0.77**, DCT-CNN **0.24**. Across corruptions the paper reports detection/attribution standard deviations of **2.8%/8.0%** for RepMix, **3.7%/12.1%** for Yu and **9.3%/16.8%** for DCT-CNN. The semantic sweep prose states **59%** attribution with two training semantics and **90%** with all eleven.

At I-FGSM epsilon 32/255, Table 2 gives accuracy drops 0.3572/0.4534/0.3812. Subtracting them from Table 1 gives final accuracy 46.35/22.50/26.35%, while the prose reports 46.35/22.49/26.34%; hidden precision is unverified. These are not original error rates. The roughly 2x comparison is not exact against DCT (approximately 1.76x).

### Counterevidence and reproduction limits

- **Generalization is partial rather than perfect semantic invariance.** Conditional attribution accuracy drops from 0.9377 (seen semantics/seen transformations) to 0.6505 (unseen/unseen). Unknown source architectures are never introduced as new labels. (Fig.7, p.13)
- **RepMix is not best on every benign perturbation.** Glass-blur attribution is RepMix 0.67 versus Yu et al. 0.77; its detection bar is also below Yu without printed exact detection labels. Do not invent those unlabelled bar values or claim uniform superiority. (Fig.3, p.8)
- **Some alternative backbone detection scores exceed the default.** VGG16 detection 0.9493 exceeds All/ResNet50 0.9426, while its attribution 0.7150 is below 0.7400. Table 3 uses two training/four test semantics and cannot replace Table 1. (Table 3 and §5.6, p.11)
- **Adversarial table values are drops, not attacked accuracy or direct error rate.** At epsilon 32/255, drops are 0.3572/0.4534/0.3812. Printed baseline-minus-drop gives 46.35/22.50/26.35% for RepMix/Yu/DCT, whereas prose reports 46.35/22.49/26.34%. Rounding/hidden precision is not established; both printed statements remain. The prose roughly 2x claim is not literal against DCT (about 1.76x). (Table 2, p.10; §5.5, p.11)
- **Binary detection accuracy has a different class baseline.** Source classes are balanced but binary real/fake is 1:7. The no-augmentation detection 0.7044 is below a derived always-fake 0.875 but above uniform binary random 0.5. The prose below-random-guess statement has no explicit comparator; no silent reinterpretation as balanced accuracy is made. (§5.2, p.9; Table 3, p.11; test.py:54–58)
- **Early-stopping criterion differs between paper and pinned script.** Paper says validation accuracy; script monitors validation total loss. Public code availability is not verification that every reported result was reproduced. (§5.1, p.8; train.py:67–78)
- **Cleaning extractor/citation details remain incomplete.** The text names InceptionV3 perceptual features while ref.61 is The Unreasonable Effectiveness of Deep Features as a Perceptual Metric. Feature layer/distance and exact nearest-real pool are not resolved from the main source. (§3, p.5; ref.61, p.17)
- **Qualitative heatmaps do not establish causal guarantees.** The paper reasons that real-image background and GAN edges aid discrimination, while t-SNE and failure examples show residual overlap and StyleGAN confusion. These are qualitative observations, not proof of universal forensic cues or real-world deployment. (Figs.6,8,9 and §5.7, pp.12–14)

### Release, splits and license boundary

Author repository [TuBui/image_attribution](https://github.com/TuBui/image_attribution) is pinned to `b22608ffca12c38a9a13876f0f2e5268991b9afe`. The untruncated tree has 24 paths. README blob `b57510f1c4a177126e9f2e88290334ff9a0b24bd` advertises a **30 GB** full dataset archive and **5.4 GB** processed test archive; neither URL was requested. Train/validation/test CSVs are claimed inside the full archive. No standalone split CSV body is listed in the fetched tree. The loader requires `path,label,dlabel`, and separate source/semantic labels are used.

Eight small source files were passively inspected and authenticated to Git blobs: train.py, test.py, utils/folder.py, utils/analysis.py, utils/eval_metrics.py, utils/hparams.py, utils/augment_imagenetc.py and models/RepMix.py. No author code was executed. The evaluator’s real-vs-rest accuracy, eight-class accuracy and NMI definitions are explicit, but it loads a RepMix checkpoint and a supplied preprocessed dataset; this does not certify the complete benchmark sweep or numerical reproduction.

The README badge and root LICENSE explicitly declare CC BY 4.0; the actual LICENSE text was preserved. This is repository licensing evidence, not independent verification of rights for all externally hosted images, LSUN/CelebA sources or archive-specific material. Public dataset links do not establish complete download availability, content, image counts or verified split independence.

Nominal base partitions across all eleven semantics are 880,000/88,000/88,000. The six-semantic training subset implies 480,000 images. Actual validation semantic membership is unverified: **48,000 is conditional only**, not an observed validation count. No exact CSV paths, image-content deduplication, checkpoint availability, error bars, repeated seeds or source-generation provenance were independently audited.

### Bounded precedent comparison

- **R574:** POSE OSMA explicitly evaluates unknown generator scenarios with AUC/OSCR. Attribution88 instead keeps eight known architecture labels, holding out semantics and their intended GAN instances. Its benchmark eligibility does not import an open-set claim.
- **R400:** FakeART contributes cross-domain photo-to-art binary detection. Attribution88 contributes architecture-source labels and semantic/corruption partitions. Both are separately specified evaluation designs, but their tasks/metrics are different.
- **R335:** Forged Calamity shows that an image-resource contribution and a benchmark role can coexist. R596 already has dataset; this action evaluates benchmark independently rather than transferring a dataset verdict.
- **R034:** RealChain separates clean versus chain-degraded binary detection; Attribution88 separates known architecture-source classes, semantics and single-corruption types. R034 balanced accuracy and platform-chain claims are not imported into R596 raw detection accuracy.

### Retrieval and integrity boundary

Complete scientific manuscripts obtained: **one** official ECVA body, through **two transport attempts** (one timed-out prefix and one ETag/range-verified continuation). No alternate complete version or supplement. Bounded source metadata: **12 GitHub API GETs** (ref, tree, README, LICENSE and eight source files) and **two web metadata opens** (arXiv abstract and author repository). No archive/image/data/weight payloads, clones or source execution.

The proposal would add only benchmark if later accepted by the maintainer. Current method/dataset, detection/source_attribution, fully_generated, bibliography, three map rows and original pending R596 remain unchanged. Evidence-only completion decrements no review counts: original Batch B 159 actions/148 papers; historical unresolved 138/128; active-public unresolved 136/126. Parent-owned receipts separately verify all global corpus/protected-file invariants.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## R234 — Universal Denoising Patterns for Diffusion Image Detection

Evidence-only review at 2026-10-24T15:40:42.349334+00:00; baseline `05a89df9e5b3543c1231dc5934f55320aec53fa9`.

**Provisional outcome: `EVIDENCE_STILL_INSUFFICIENT` under both R1 (dataset) and R2 (benchmark).** The current `method` label is held unchanged; this does not independently reconfirm that label or establish a supported no-change verdict. R234 remains one original open action. No remediation or terminal decision is applied.

### Identity and original question

Canonical ID: `curated:03f893b9484ea2d09c22`. DOI: `10.1109/icassp55912.2026.11462468`. Authors: Yurui Qian; Qi Cai; Yingwei Pan; Ting Yao; Yan Chen; Tao Mei. Current task: `detection`; image scope: `fully_generated`; research type: `method`. Two existing map relationships and no independent pending review on the same paper are preserved.

Original review question (verbatim): Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: DiffuGen is a newly constructed 70K-image benchmark covering 13 generators.

The [official ICASSP 2026 program](https://www.cmsworkshops.com/ICASSP2026/view_paper.php?PaperNum=1775&bare=1) lists the exact title and all six authors in canonical order, session IFS-P6.7. Saved HTML: 12,387 bytes, SHA-256 `700aee3a33d136fd859c425d59cce757d0b66a51d572ea3272fa3c8d196396c9`. Title is at source line64 and authors at line68. This verifies bibliographic identity, not scientific methods or evaluation.

### Manuscript retrieval and version boundary

The local-first inventory checked 56 unique PDFs and 1,050 unique gzip captures across the isolated repository, primary checkout and existing TMP inputs. It found zero complete identity-matched PDFs. Seventeen identity-bearing captures contain API, CSV, JSON or historical public metadata, not a complete scientific manuscript. Original inputs were read only. PDF metadata and first pages were used for identity screening; unrelated papers were not scientifically reviewed.

The official program displays a View Manuscript anchor with an empty href, but its actual HTML onclick at lines105 and157 invokes `goto_manuscript.php?pn=1775`. The [observed official manuscript route](https://www.cmsworkshops.com/ICASSP2026/goto_manuscript.php?pn=1775) was followed once. It and the separately bounded [DOI route](https://doi.org/10.1109/ICASSP55912.2026.11462468) each ended at `https://ieeexplore.ieee.org/document/11462468/` with HTTP202 and zero body bytes. Neither returned a PDF. The earlier web-tool DOI failure is preserved separately, with no invented HTTP status. No further IEEE endpoint was tried.

A candidate coauthor homepage, `https://deepfun.club/`, failed TLS with curl exit35 and supplied no author content. Bounded exact-title, arXiv, author and institutional discovery identified no verified author PDF. [ResearchGate discovery](https://www.researchgate.net/publication/404384875_Universal_Denoising_Patterns_for_Diffusion_Image_Detection) was request-only. A supposed Yingwei Pan personal-website link on a secondary profile pointed to LinkedIn, rather than a manuscript repository. Secondary profiles and search results were used only to discover possible primary routes; they were never accepted as methods or evaluation evidence.

**New complete manuscripts: 0. Reused complete manuscripts: 0. Complete manuscripts read: 0.** No manuscript version or publisher-final equivalence is verified. No supplement, dataset or image archive, model weight, complete repository archive or clone was downloaded. The bounded source routes are exhausted for this review; this does not claim that no manuscript exists elsewhere.

### Locked policies and independent R1/R2 conclusions

**R1, accepted rule (verbatim):** Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.

**R2, accepted rule (verbatim):** Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

**R1 remains insufficient.** A resource name and image count in the stored abstract do not establish a substantive reusable dataset contribution. The complete contribution, construction and provenance sections are missing. The absence of retrieved text does not show that the paper lacks such a contribution.

**R2 remains insufficient.** No reusable evaluation protocol, controlled comparison framework, fixed split, baseline condition or method-independent benchmark role could be inspected. A benchmark name, generator count and experimental scale do not suffice. Public download availability is not imposed as a sole or mandatory criterion.

The stored abstract claims 65K synthetic images, 5K real images, 13 modern diffusion models and average accuracy of99%. The original intake summarizes 70K images and13 generators. **These remain unverified metadata claims.** The arithmetic 65,000+5,000=70,000 is compatible, but does not verify the resource, model inventory, partitions or accuracy denominator. No primary table cells, numerical results under verified experimental conditions, or compatible baseline comparisons are available.

The abstract also describes single-step denoising to produce minimal fake images, blending these with real counterparts, and a feature separation loss. These statements are preserved as abstract-level claims. They are not a reconstructed method or independently verified contribution. No new label is inferred from them.

### All twenty original scientific questions

| # | Question | Evidence finding |
|---|---|---|
| 1 | Whether DiffuGen is actually introduced in the reviewed paper. | The stored abstract names DiffuGen, but the contribution section is unavailable; the program supplies identity only. |
| 2 | Whether it is original to these authors. | No complete primary contribution/related-work section was obtained; originality is unverified. |
| 3 | Whether it has 70,000 images. | The original review says70K and the local abstract says65K synthetic plus5K real; these are metadata claims, not an independently verified construction/count. |
| 4 | Whether it covers13 generators. | The local abstract claims13 modern diffusion models; the exact model inventory is unavailable. |
| 5 | Exact synthetic and real-image distributions. | The abstract claims65K synthetic/5K real; per-model/class counts and deduplication cannot be checked. |
| 6 | Diffusion model identities and versions. | No model table, checkpoint/version list or generation configuration was available. |
| 7 | Whether GANs or other generator families are included. | The abstract mentions diffusion models only; absence of other families is not established by that silence. |
| 8 | Prompt sources, image provenance and licensing. | No complete collection/generation section or verified release/license was obtained. |
| 9 | Image collection and generation procedures. | No complete primary construction procedures were obtained. |
| 10 | Whether the resource is constructed for this paper or reused from prior work. | The abstract says constructed, but substantive originality, systematic provision and reuse boundaries cannot be inspected. |
| 11 | Dataset partitions and generator holdouts. | No train/validation/test or seen/unseen generator partition was verified. |
| 12 | Whether a reusable benchmark protocol is separately specified. | No complete evaluation protocol was obtained; scale and a benchmark name cannot substitute underR2. |
| 13 | Whether any new test benchmark is independent of the denoising-pattern method. | A method-independent protocol cannot be inferred from the abstract performance claim. |
| 14 | Which quantitative metrics are reported. | The abstract claims average accuracy99%; averaging unit, split, baseline conditions and all tables remain unverified. |
| 15 | Whether cross-model robustness is independently measured. | Generalization is claimed in the abstract, but no cross-model/robustness protocol or result table was available. |
| 16 | Whether named baselines use compatible training and inference conditions. | Named baselines, training sets, checkpoints and inference controls were not obtained. |
| 17 | Whether a release of data, split files or evaluation scripts is actually verifiable. | No identity-matched author release repository or artifact was identified in bounded discovery; no archive was retrieved. This is not proof of non-release. |
| 18 | Whether the resource could be used independently by other detectors. | No schema, split definition or reusable evaluation procedure was inspected; independent reuse remains unverified. |
| 19 | Whether the benchmark claim depends solely on generator count or experimental scale. | Only the abstract/intake name and scale are available; they are insufficient for an affirmativeR2 decision and do not prove the full paper lacks a protocol. |
| 20 | Any inconsistencies in the dataset name, size, generator count or publication version. | DiffuGen/70K/13 are mutually arithmetically compatible metadata claims, not independently verified. The actual storedraw_venue2025 conflicts with canonicalyear/DOI2026 and official2026program; record only the out-of-scope bibliographic observation. No manuscript version was obtained. |

### Release, contradictions and reproducibility

No identity-matched data release, split files, evaluation scripts, license or reproduction recipe was verified. This records unavailable evidence, not proof of non-release or a negative scientific judgment. Without the full paper, this review cannot distinguish the method training corpus from an independently reusable resource.

Accepted R574, R400, R335 and R034 decisions relied on complete primary protocol or resource evidence. Their accepted labels cannot be transferred to R234 because of a name, image count, generator count or conference identity. All required construction and evaluation questions remain open.

### OUT_OF_SCOPE_BIBLIOGRAPHIC_OBSERVATION

Actual curated year: `2026`. Actual DOI: `10.1109/icassp55912.2026.11462468`. Actual stored raw_venue: `2025 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)`. The official ICASSP2026 program lists this exact paper and author order. The cached API primary_location.raw_source_name also reads `ICASSP 2026 - 2026 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)`. The stored2025 proceedings description therefore conflicts with the canonical2026 identity and official program. This is a separate bibliographic observation: no publication field is corrected and no historical review action is created.

### Provisional disposition and preservation

R1: `EVIDENCE_STILL_INSUFFICIENT`. R2: `EVIDENCE_STILL_INSUFFICIENT`. Proposed complete research types remain `method` solely as an administrative hold. Task `detection` and image scope `fully_generated` remain unchanged. Confidence is high for identity and for the insufficiency of the bounded available evidence; scientific dataset/benchmark classification is undetermined. Maintainer acceptance remains pending. The original R234 action remains open and atomic.

The worker wrote only TMP evidence and provenance records. No authoritative corpus, review, exclusion, institution, public output or Git state was modified. No exporter or full suite was run. Lightweight worker checks bind identity, the source budget, twenty-question coverage, pending-review state and authoritative source hashes. Independent global preservation remains the integrity worker’s responsibility. Evidence collection does not decrement corpus or BatchB accounting.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Independent review, accounting and preservation

Root independently read all 18 RepMix text pages and visually checked pages 4,5,8,10,11,13 before receiving the worker verdict. All 81 table cells independently match the actual primary text. A separate source/provenance reviewer checks preserved transports and scientific transcriptions. Root also checked pinned test/metric/CSV-reader code without execution, and independently verified R234's actual canonical fields, official program HTML and insufficient-source boundary. Worker and independent receipts, hashes and any reconciliations are retained in the companion manifest and temporary receipt directory.

One frozen R596 worker confidence phrase, “held-out source-architecture evaluation design,” is clarified in the manifest: it means semantic/corruption holdouts within fixed architecture labels. Zero architecture labels are held out; unknown-architecture open-set evaluation is not claimed. The primary source, report, question matrix and explicit protocol fields agree on this boundary.

Current public baseline, recomputed from authoritative/public records: public 674, formal 557, mapped 613, unmapped 61, relationships 1410, unique pairs 1410.

Taxonomy: detection 621, source_attribution 84, localization 45, method 578, dataset 137, benchmark 93, survey 21, analysis_study 82.

Batch B: 159 original actions/148 papers; 138 historical unresolved actions/128 papers; 136 active-public unresolved actions/126 papers. Both R596 and the atomic R234 action remain unresolved; no new historical action, partial closure or terminal decision is created. Prior B1A–M evidence and all 96 registry rows remain unchanged.

Batch C remains 41 total/28 resolved/13 deferred/0 maintainer judgments, with all 13 debt identities preserved. The separate 39-paper inventory remains 39 unmapped/0 relationships/14 taxonomy reviews/12 held. Its identities and historical receipts remain unchanged.

Preserve all 4,489 isolated tracked files, all 4,414 primary tracked and 305 primary untracked files, the 128 protected local files, original 130 broader local group, 49 frozen NeurIPS artifacts in both checkouts, 119 ignored operational inputs and 26 prior B1A–M artifacts. No scientific data, tasks, scopes, publications, exclusions, institutions, maps, review decisions or public exports are changed. No full suite or exporter is run. Only this report and its companion manifest may be new untracked, unstaged files; nothing is committed or pushed.

7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA

<!-- FINAL_LIGHTWEIGHT_VALIDATION -->
Lightweight validation passed:

- Worker scientific/provenance checks: R596 **50/50**, R234 **60/60**.
- Separate independent scientific cross-review: **120/120** (R596 83, R234 37), including all **81 table cells + 57 Figure 3 labels + 4 Figure 7 title scores = 142 printed scalars**. This verifies transcription, not numerical reproduction.
- Separate saved-source provenance review: **42/42**, not counted again in the 120 scientific checks.
- Root independent source/policy/scientific checks: R596 **33/33**, R234 **11/11**, reported separately with overlap acknowledged.
- Evidence-packet/report reconciliation: **36/36**. The initial report-title omission was corrected by restoring R234's exact canonical title; the original failed receipt is preserved. The scientific records were unchanged.
- Global preservation/accounting gate: **43/43**, with all tracked bytes/modes, primary HEAD/index/status, protected inventories, prior decisions/evidence and current public counts unchanged.

`AUTHORITATIVE_CORPUS_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

No full repository suite, public exporter, authoritative remediation, staging, commit or push occurred. Worker source records remain frozen; minor TMP checker/schema selector repairs and all original failed/exception receipts are preserved without changing source evidence or weakening a scientific condition.

The measured pre-summary receipts and their SHA-256 identities are recorded in the companion manifest. A final read-only packet check and preservation boundary receipt authenticate the completed two files at `/private/tmp/b1n-evidence-2026-10-24/packet-validation-final.json` and `/private/tmp/b1n-evidence-2026-10-24/integrity-final.json`. They stay outside the repository to avoid circular self-hashes. No scientific or authoritative file changes are permitted after that boundary.

Final delivery: exactly the two requested evidence files remain untracked, unstaged, uncommitted and unpushed in the isolated evidence worktree. HEAD and fetched origin/main remain `05a89df9e5b3543c1231dc5934f55320aec53fa9`, ahead/behind 0/0; tracked working tree clean and index empty. The primary checkout is unchanged.

7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA
