# Tier 2 application of the approved narrowed scope — September 2026

The user-approved policy supersedes the earlier precedent-based proposal for NEW candidates. This is a policy-eligibility layer only: POLICY_INCLUDE does not add a paper, POLICY_EXCLUDE does not enter an exclusion registry, and legacy flags do not authorize removal.

Sources: [exact approved request](../data/processed/systematic_tier2_application_2026_09/approved_policy_request.txt), [reviewed application CSV](../data/manual/systematic_tier2_policy_application_2026_09.csv), [audit-only legacy CSV](../data/manual/legacy_scope_review_candidates_2026_09.csv), and [unchanged prior Tier 2 inventory](../data/processed/systematic_tier2_policy_2026_09/inventory.json). No new literature search was conducted.

## Applied rules

- **P1 — Active mechanisms and protection:** exclude watermark construction, detection, verification, robustness, removal, injected fingerprints, generator-controlled forensic signatures, credentials/C2PA, content authentication and ownership/copyright protection. Keyless or zero-watermark authentication is not automatically passive generator-trace analysis.
- **P1_EXCEPTION:** only a separable, independently evaluated passive synthetic-image method that does not require the active mechanism can qualify. No such exception is asserted as verified in this pass. Abductive Corroboration remains an evidence check for watermark-free results.
- **P2 — Pure deepfake:** face swapping, reenactment, facial/identity manipulation and video/frame deepfake work do not qualify alone. Entire-face GAN/diffusion synthesis or facial localization does not establish the required broader contribution.
- **P3 — Substantive synthetic-image forensics:** general fully generated-image detection and diffusion/generative inpainting, editing or partial-region forensics remain eligible. Manipulated regions are not an exclusion reason.
- **P4 — Classical-only:** conventional copy-move, splicing, compositing and document edits are excluded unless a substantive generative component is independently evaluated. A diffusion detector backbone is not that evidence.
- **P5 — Passive attribution:** inference from naturally occurring image-generation traces to generators/models/sources remains core. Deliberately injected signatures and generic model-ownership tests do not qualify.
- **P6 — Passive-detector robustness/evasion:** analysis or attacks against in-scope AI-generated-image detectors may qualify. Watermark and otherwise out-of-scope face/video detector attacks do not.
- **P7 — Multimodal:** require a substantive independently evaluated synthetic-image forensic component; frame extraction and text-image misinformation consistency alone are insufficient.
- **P8 — Specialized domains:** scientific, biomedical and other domains qualify on their synthetic-image forensic task; specialization alone is not exclusionary.

## Revised Tier 2 result

| Outcome | Papers |
| --- | --- |
| POLICY_INCLUDE | 12 |
| POLICY_EXCLUDE | 171 |
| PAPER_SPECIFIC_EVIDENCE_REQUIRED | 32 |
| TOTAL | 215 |

**Remaining user-policy decisions: 0.** Evidence questions concern the actual paper, not conflicting historical decisions.

The application preserves the exact 215 candidate IDs and the original 11 primary clusters. The historical audit and prior policy proposal remain unchanged. Saved titles/opening abstracts can establish an unambiguous central task without completing bibliographic or experimental curation; missing details become Queue C only when they affect the substantive scope boundary.

### By original policy cluster

| Cluster | Papers | POLICY_INCLUDE | POLICY_EXCLUDE | PAPER_SPECIFIC_EVIDENCE_REQUIRED |
| --- | --- | --- | --- | --- |
| EMBED | 40 | 0 | 40 | 0 |
| VERIFY | 5 | 0 | 4 | 1 |
| WM_EVAL | 14 | 0 | 14 | 0 |
| HYBRID | 11 | 0 | 11 | 0 |
| PROTECT | 27 | 0 | 27 | 0 |
| FACE | 60 | 0 | 55 | 5 |
| MODALITY | 15 | 0 | 15 | 0 |
| TRADITIONAL | 4 | 0 | 4 | 0 |
| IMAGE | 32 | 8 | 0 | 24 |
| ATTRIBUTION | 4 | 1 | 1 | 2 |
| EVASION | 3 | 3 | 0 | 0 |

### Exclusion reasons

Each excluded candidate receives one primary reason, so these counts sum to the exclusion queue. Where boundaries overlap, a watermark-primary mechanism takes precedence, including text watermarks and temporal watermark recovery. Generic temporal forgery localization without a specific deepfake/image task is OTHER. Secondary context remains in each rationale; reasons are not added together twice.

| Primary reason | Papers |
| --- | --- |
| WATERMARK_ACTIVE_PROVENANCE | 94 |
| PURE_DEEPFAKE_FACE_ONLY | 55 |
| VIDEO_ONLY_DEEPFAKE | 10 |
| CLASSICAL_MANIPULATION | 4 |
| PROTECTION_GOVERNANCE | 7 |
| OTHER | 1 |

## Queue A — POLICY_INCLUDE

12 papers. These pass the scope gate only; a later task must handle identity/exclusion reconciliation, metadata, publication status and primary-source curation before corpus addition.

[Machine-readable Queue A](../data/processed/systematic_tier2_application_2026_09/queue_a_policy_include.csv)

- **STD-FD: Spatio-Temporal Distribution Fitting Deviation for AIGC Forgery Identification** (`audit:032ad7d6b71836a2`) — STD-FD analyzes reconstruction/distribution-fitting traces of diffusion-generated images for AIGC forgery detection. Temporal refers to diffusion steps, not video; no injected provenance is required. [Saved primary link](https://proceedings.mlr.press/v267/lou25a.html).
- **TGIF2: extended text-guided inpainting forgery dataset and benchmark** (`audit:07194f58b4540acc`) — The title and saved opening explicitly identify a text-guided generative-inpainting forgery dataset and benchmark. Its central subject satisfies generative-edit forensics; abbreviated metadata is a later curation limitation, not an unresolved scope boundary. [Saved primary link](https://doi.org/10.1186/s13635-026-00235-9).
- **Vulnerabilities in AI-generated Image Detection: The Challenge of Adversarial Attacks** (`audit:2ec9b9251586d3bb`) — FPBA evaluates adversarial vulnerability of passive AI-generated-image detectors across GAN/diffusion generators. No watermark-verification or face-only target is described. [Saved primary link](https://arxiv.org/abs/2407.20836).
- **Towards Reliable Identification of Diffusion-based Image Manipulations** (`audit:3e3ef129a9a7d54a`) — RADAR detects/localizes diffusion edits; BBC-PAIR evaluates manipulations from 28 diffusion models, including changes to gestures and backgrounds, beyond pure facial manipulation. [Saved primary link](https://proceedings.neurips.cc/paper_files/paper/2025/hash/36721d1209a059dcb7a090dd543f34c4-Abstract-Conference.html).
- **Untraceable DeepFakes via Traceable Fingerprint Elimination** (`audit:5413d2706f713d11`) — The evaluated attack removes naturally occurring generated-image traces to evade source-generator attributors across 12 GMs and 6 AMs. DeepFakes in this abstract refers to generated-image source inference, not a face-swap-only task; no injected fingerprint is described. [Saved primary link](https://proceedings.iclr.cc/paper_files/paper/2026/hash/8e8399e5e7aed601c9f135f40be26564-Abstract-Conference.html).
- **PolyJuice Makes It Real: Black-Box, Universal Red Teaming for Synthetic Image Detectors** (`audit:5a3a0232762bb033`) — PolyJuice red-teams passive synthetic-image detectors of text-to-image outputs and also improves them through fine-tuning. The target is an in-scope image detector, not a watermark. [Saved primary link](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b9b228d28770dc2a18922de5cd49f1d9-Abstract-Conference.html).
- **Detecting AI-Generated Forgeries via Iterative Manifold Deviation Amplification** (`audit:6bf3721fdb65fc44`) — IFA-Net explicitly reports IoU/F1 on four diffusion-based inpainting benchmarks and generalization to traditional manipulation. MAE prior injection is internal detector guidance, not a provenance signal embedded in released images. [Saved primary link](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_Detecting_AI-Generated_Forgeries_via_Iterative_Manifold_Deviation_Amplification_CVPR_2026_paper.html).
- **Scalable Black-Box Model Attribution for Images** (`audit:80dc647f134b129b`) — RPA asks which generative model produced a given image and evaluates passive black-box source attribution on DRAGON and OpenFake. No active fingerprint injection is described. [Saved primary link](https://arxiv.org/abs/2608.15652).
- **NeuroRenderedFake: A Challenging Benchmark to Detect Fake Images Generated by Advanced Neural Rendering Methods** (`audit:96a08f643278af6c`) — NeuroRenderedFake independently evaluates image detectors across neural-rendering, generative and combined synthesis methods. This is image authenticity forensics, not rendering quality or video-only analysis. [Saved primary link](https://proceedings.neurips.cc/paper_files/paper/2025/hash/56bdf726a96d43ee1e66172d14c63a61-Abstract-Datasets_and_Benchmarks_Track.html).
- **ImageTrust: Multi-backbone Fusion for AI-Generated Image Detection with Calibrated Uncertainty** (`audit:a1d31a96ac288ab0`) — ImageTrust explicitly proposes an AI-generated-image detection system with recompression robustness and calibrated uncertainty. The saved title and opening establish the central passive image-forensic task; detailed experiments remain future curation work. [Saved primary link](https://doi.org/10.1007/978-3-032-29430-2_19).
- **UniShield: An Adaptive Multi-Agent Framework for Unified Forgery Image Detection and Localization** (`audit:bb665e920e4e26be`) — UniShield explicitly evaluates detection/localization across image manipulation, documents, deepfakes and AI-generated images; the synthetic-image component is part of its substantive cross-domain contribution. [Saved primary link](https://arxiv.org/abs/2510.03161).
- **Dual-scale model collaborative reasoning with multi-feature fusion for robust AI-generated image detection** (`audit:f49729ba31773bd0`) — The saved title explicitly identifies robust AI-generated-image detection and the abstract opening describes the real/synthetic image boundary. The central task is in scope; a truncated abstract alone does not turn a clear detector topic into a new policy question. [Saved primary link](https://doi.org/10.1007/s00530-026-02425-4).

## Queue B — POLICY_EXCLUDE

171 papers. Every title, primary reason and supporting rationale is retained in [Queue B](../data/processed/systematic_tier2_application_2026_09/queue_b_policy_exclude.csv); none has been written to the authoritative exclusion registry.

## Queue C — PAPER_SPECIFIC_EVIDENCE_REQUIRED

32 papers. [Machine-readable Queue C](../data/processed/systematic_tier2_application_2026_09/queue_c_evidence_required.csv). A clear face-only or watermark-primary contribution is not held here merely because older similar papers were included.

| Priority | Paper / candidate ID | Exact question |
| --- | --- | --- |
| HIGH | Riemannian-Geometric Fingerprints of Generative Models (`audit:07f15e7e8a78398a`) | Does the evaluated Riemannian fingerprint infer a generator/source from encountered generated images using naturally occurring traces, rather than only authenticating a model service or its parameters? |
| HIGH | A Rich Knowledge Space for Scalable Deepfake Detection (`audit:0b72dded38f87a65`) | Does the stated AIGC benchmark independently evaluate broader fully generated or generatively edited images beyond the 3.6-million facial-image/deepfake collection? |
| HIGH | DINOv3 Beats Specialized Detectors: A Simple Foundation Model Baseline for Image Forensics (`audit:0dc47031ed0bccc5`) | Do the CAT-Net/MVSS-Net evaluation protocols contain a substantive independently evaluated generative-edit or fully generated-image subset, rather than classical tampering only? |
| HIGH | Conditional uncertainty-aware political deepfake detection with stochastic Convolutional Neural Networks (`audit:202541800aaec592`) | Does the political-deepfake uncertainty study evaluate a broader passive synthetic-image detector, or only face/identity/video deepfakes? The saved publisher summary does not identify its data or evaluation unit. |
| NORMAL | ILLUSION: Unveiling Truth with a Comprehensive Multi-Modal, Multi-Lingual Deepfake Dataset (`audit:29fa62c1fc9fd79d`) | Does ILLUSION independently benchmark broader synthetic-image detection beyond faces, audio spoofing and talking-head/video forgeries? Identify the image subset and its separate results. |
| NORMAL | Omni-IML: Towards Unified Interpretable Image Manipulation Localization (`audit:2fa7c05b3b864bfe`) | Which of Omni-IML’s four tasks and Omni-273k manipulation types involve generative AI edits or fully generated images, and are their forensic results reported separately? |
| NORMAL | M2SFormer: Multi-Spectral and Multi-Scale Attention with Edge-Aware Difficulty Guidance for Image Forgery Localization (`audit:305b25515850fed3`) | Which evaluated M2SFormer datasets contain generatively produced manipulations, and are localization results for those manipulations substantive rather than a classical-only evaluation? |
| NORMAL | AdaIFL: Adaptive Image Forgery Localization via a Dynamic and Importance-aware Transformer Network (`audit:3be864bb29fef423`) | Does AdaIFL evaluate generative inpainting/editing or partially synthesized images separately from classical tampering? Identify those datasets and results. |
| HIGH | FreDA: Training-Free Test-Time Adaptation for Deepfake Detection via Non-parametric Cache Retrieval (`audit:46984fabc086b053`) | Does FreDA adapt passive general AI-generated-image detectors beyond pure face/video deepfake detection? The truncated abstract does not identify the target datasets. |
| NORMAL | Image Manipulation Detection With Implicit Neural Representation and Limited Supervision (`audit:4f169a0ad566bd1d`) | Do the INR limited-supervision experiments include independently evaluated generative edits or generated images, rather than only conventional image manipulation? |
| NORMAL | IMDL-BenCo: A Comprehensive Benchmark and Codebase for Image Manipulation Detection & Localization (`audit:5485e42ab03970ce`) | Do IMDL-BenCo’s two evaluation protocols substantively cover generative-image forensics? Identify the generative datasets/results; general-purpose code reuse alone is insufficient. |
| NORMAL | Towards Modern Image Manipulation Localization: A Large-Scale Dataset and Novel Methods (`audit:6338fbc2cd19a1bf`) | Do the 123,150 manually forged images or evaluation sets include substantive generative inpainting/editing, or only human-made classical edits? Identify the manipulation provenance and separate results. |
| NORMAL | Pre-Training-Free Image Manipulation Localization through Non-Mutually Exclusive Contrastive Learning (`audit:67fabc63d5da6e37`) | Which of NCL-IML’s five benchmarks evaluate generatively produced manipulations? Real/tampered/contour patch labels alone do not identify how a manipulation was made. |
| HIGH | Generating Attribution Reports for Manipulated Facial Images: A Dataset and Baseline (`audit:6880617d9c9040d4`) | Does Generating Attribution Reports evaluate a broader synthetic-image forensic contribution beyond facial manipulation, and what source is attributed? Only an ACL bibliographic citation is saved. |
| NORMAL | Noise-assisted Prompt Learning for Image Forgery Detection and Localization (`audit:6de8f49b49f65330`) | Do CLIP-IFDL’s tests include substantive fully generated or generatively edited images with separate forensic metrics, rather than classical forgery only? |
| NORMAL | SAFL-Net: Semantic-Agnostic Feature Learning Network with Auxiliary Plugins for Image Manipulation Detection (`audit:7aba8c4410d51d0a`) | Does SAFL-Net independently evaluate generative-image manipulations, rather than only conventional editing? Identify the generative test data and results. |
| HIGH | Detecting violent deepfakes: dataset and a compact attention network with multi-scale supervision (`audit:854cc239481946ba`) | Does the violent-deepfake dataset test general generated scenes/images or only face/identity manipulation, and is its image-forensics component independently evaluated? |
| NORMAL | Diffusion Models Meet Image Counter-Forensics (`audit:9089a0b84b74868b`) | Do the detectors attacked by diffusion purification detect AI-generated/generatively edited images, or only camera-pipeline disruption and classical tampering? Using diffusion as the attack tool is insufficient. |
| NORMAL | UnionFormer: Unified-Learning Transformer with Multi-View Representation for Image Manipulation Detection and Localization (`audit:93f2de88b5a876c9`) | Which UnionFormer evaluation datasets contain generative editing or fully generated images, and are the corresponding detection/localization results substantive? |
| NORMAL | Learnable Frequency Decomposition for Image Forgery Detection and Localization (`audit:a06bf41dfd2ab933`) | Does F2D-Net evaluate AI-generated regions or generative editing independently, rather than classical tampering alone? Identify the input manipulation types, not just frequency features. |
| NORMAL | ForgerySleuth: Empowering Multimodal Large Language Models for Image Manipulation Detection (`audit:b5b43c8e6e91325d`) | Does ForgeryAnalysis contain generatively edited or fully generated images with independently evaluated detection/localization results, beyond generic tamper segmentation and reasoning? |
| NORMAL | THEMIS: Towards Holistic Evaluation of MLLMs for Scientific Paper Fraud Forensics (`audit:b666c0f0f497632a`) | Which THEMIS fraud types involve AI-generated scientific images or generative edits, and do standalone image-forensic results distinguish them from classical duplication/tampering and text reasoning? |
| NORMAL | ForgDiffuser: General Image Forgery Localization with Diffusion Models (`audit:bcd4cedccc0c34eb`) | Do ForgDiffuser’s six benchmarks include generatively manipulated input images? Diffusion-generated segmentation masks do not establish that the tested forgeries are generative. |
| NORMAL | DiffForensics: Leveraging Diffusion Prior to Image Forgery Detection and Localization (`audit:ced0c9f8fe10fbb9`) | Do DiffForensics evaluation sets contain substantive generative manipulation? A diffusion pretraining prior for the detector is not sufficient evidence about the input images. |
| HIGH | Abductive Corroboration of Probabilistic AI Models for Forensic Synthetic Media Detection (`audit:cf16307ced603a1d`) | Is there a separable, independently evaluated passive synthetic-image forensic method or passive-detector analysis that remains valid without SynthID or any watermark recovery? Identify the watermark-free results. |
| NORMAL | Uncertainty-guided Learning for Improving Image Manipulation Detection (`audit:e094e552be6fbe85`) | Does UEN evaluate detection of AI-generated/generatively edited images independently, rather than only uncertainty on conventional image manipulation datasets? |
| HIGH | SPARK-IL: Spectral Retrieval-Augmented RAG for Knowledge-Driven Deepfake Detection via Incremental Learning (`audit:ea0d7f9972aa1b1c`) | Does SPARK-IL evaluate broader passive AI-generated-image detection beyond face/video deepfakes, and which generator datasets establish that component? |
| HIGH | Deep learning for CGI and visual forgery detection: a comprehensive survey (`audit:f12e2be8d1320201`) | Does this CGI/visual-forgery survey substantively cover passive AI-generated-image detection, attribution or generative-edit localization, rather than mainly classical CGI/rendering or traditional manipulation? |
| HIGH | Learning Counterfactually Decoupled Attention for Open-World Model Attribution (`audit:f293e205186b3f59`) | Do CDAL’s open-world attribution benchmarks use naturally occurring image-generation traces to identify source generators beyond pure facial-manipulation attribution? Verify inputs, source labels and absence of injected signatures. |
| HIGH | Language-Guided Hierarchical Fine-Grained Image Forgery Detection and Localization (`audit:f55fbb498b42444f`) | Does the proposed unified detector independently evaluate the CNN-synthesized image domain as a substantive AI-image forensic task? The saved abstract stops before its method and evaluation. |
| NORMAL | ADCD-Net: Robust Document Image Forgery Localization via Adaptive DCT Feature and Hierarchical Content Disentanglement (`audit:fa8eef7eb10763d0`) | Do ADCD-Net’s document tests include generative-AI edits with separate localization results, rather than only conventional document tampering and distortion robustness? |
| NORMAL | Towards Generic Image Manipulation Detection with Weakly-Supervised Self-Consistency Learning (`audit:fed41b0363b5f8c1`) | Do WSCL’s in-/out-of-distribution tests include generatively edited or fully generated images? Multi-source and inter-patch consistency alone do not establish generative input provenance. |

## Important boundary applications

- Watermark verification and robustness no longer inherit eligibility from ImageDetectBench or WEvade. FARI, ROAR and keyless watermark detection are excluded. Abductive Corroboration is held only to check an explicitly separable watermark-free contribution.
- FFIM and AdvMark improve passive detection through generator control or injected marks; downstream detector scores alone do not make their contribution independent of the active mechanism.
- VLForgery, VIPGuard and specular-reflection face detection remain pure face-forensics applications despite using diffusion, full-face synthesis, localization or source attribution. A Rich Knowledge Space is held because its saved abstract explicitly also claims an AIGC benchmark, whose broader coverage must be checked.
- STD-FD uses temporal diffusion-process evidence, not video. IFA-Net’s complete saved abstract explicitly reports four diffusion-inpainting benchmarks; that supports inclusion. ForgDiffuser instead generates segmentation masks, leaving the origin of the input tampering unverified.
- Naturally occurring image-source fingerprints in RPA and passive detector attacks in FPBA/PolyJuice differ from injected training signatures in Artificial fingerprinting. A detector-training prompt/prior is not automatically a released provenance signal.
- TGIF2, ImageTrust and Dual-scale model collaborative reasoning have an unambiguous central generative-image forensic task in the saved title/opening. Their abbreviated abstracts remain curation limitations, not unresolved policy choices.

## Legacy scope diagnostic — no changes to 636 existing records

This is a current-metadata/abstract screening list for a later audit, not an approved exclusion list. A [636-row screening ledger](../data/processed/systematic_tier2_application_2026_09/legacy_screening_636.json) records coverage and source-record hashes. Every flagged row keeps its original taxonomy, identity, abstract and review rationale. Unflagged records are not certified compliant with every narrowed rule.

| Potential legacy category | Records |
| --- | --- |
| LEGACY_SCOPE_REVIEW_WATERMARK | 3 |
| LEGACY_SCOPE_REVIEW_DEEPFAKE | 71 |
| LEGACY_SCOPE_REVIEW_CLASSICAL | 2 |

### Confidence and safeguards

| Exact confidence | Records |
| --- | --- |
| HIGH | 32 |
| MEDIUM | 1 |
| LOW | 43 |

The normalized diagnostic distinguishes likely pure-deepfake scope drift from metadata-insufficient records and a possible broader synthetic-image contribution. The broader-work record is not counted as a likely scope violation.

| Diagnostic disposition | Records |
| --- | --- |
| LIKELY_PURE_DEEPFAKE | 27 |
| LIKELY_SCOPE_DRIFT | 5 |
| METADATA_INSUFFICIENT | 43 |
| POSSIBLE_BROADER_SYNTHETIC_IMAGE_WORK | 1 |

The source CSV retains the original reviewed wording; the normalized exact confidence and disposition fields are in [the derived legacy diagnostic](../data/processed/systematic_tier2_application_2026_09/legacy_scope_diagnostic.csv).

| Diagnostic basis | Records |
| --- | --- |
| deepfake_only_taxonomy_scope_unverified | 43 |
| face_or_video_evaluation_evidence | 27 |
| face_primary_with_possible_broader_exception | 1 |
| mechanism_evidence | 3 |
| taxonomy_and_evaluation_evidence | 2 |

The 71 deepfake flags comprise 27 supported by face/video evidence, 43 low-confidence deepfake-only taxonomy records whose broader component is not settled by saved evidence, and 1 possible broader-contribution exception (Gram-Net). These are **not confirmed pure-deepfake exclusions**. The low-confidence subgroup can contain false positives and must receive evidence review before any removal proposal.

The screen checks explicit broader counterevidence rather than treating the deepfake taxonomy label as sufficient. Examples not flagged as pure face-only include Forging the Unknown (GenImage plus FaceForensics++), the Multi-Graph Attention method (GenImage/CIFAKE), Faster Than Lies (COCOFake/CIFAKE), OpenFake, and general image-source/robustness studies. Their stored taxonomy is not changed.

### Watermark/provenance flags

- **EKILA: Synthetic Media Provenance and Attribution for Generative Art** — EKILA combines visual attribution with C2PA credentials, tokenized ownership/rights and royalty attribution. Review whether its visual attribution is separable from the active provenance framework.
- **Evading Watermark based Detection of AI-Generated Content** — WEvade centrally attacks watermark-based detection, now excluded for new candidates even though it is an existing analysis study.
- **AI-generated Image Detection: Passive or Watermark?** — ImageDetectBench compares passive and watermark detectors. Review whether its independent passive evaluation qualifies under the narrow exception; the watermark component itself no longer qualifies.

### Classical-only flags

- **IoT-Oriented Security for Small Sensor Systems Using DnCNN Denoising and Multimodal Feature Fusion for Image Forgery Detection** — Current taxonomy is classical-only; saved evaluation concerns conventional CASIA/copy-move forensics without a demonstrated generative-image component.
- **Copy-Move Forgery Detection (CMFD) Using Deep Learning for Image and Video Forensics** — Current taxonomy is classical-only; saved evaluation concerns conventional CASIA/copy-move forensics without a demonstrated generative-image component.

All deepfake diagnostic titles and evidence/confidence fields are in the [legacy CSV](../data/manual/legacy_scope_review_candidates_2026_09.csv). Watermark-independent visual source retrieval is not flagged merely because provenance or copyright appears in its motivation; EKILA is flagged because it also incorporates the active credential/rights framework, with the separability exception left for later review.

## Integrity, tests and reproduction

The [new pre-application hash baseline](../data/processed/systematic_tier2_application_2026_09/baseline_sha256.json) protects all pre-existing files, including the completed Tier 2 policy analysis. Neither reviewed manual CSV is written by the report/queue generator. Original systematic-audit statuses are still CANDIDATE_ADD_NEEDS_SCOPE_REVIEW.

```sh
python3 scripts/report_systematic_tier2_application.py --check --verify-integrity
python3 scripts/report_systematic_tier2_application.py --output-dir /tmp/tier2-application-reproduction
/usr/bin/python3 -m pytest -q tests/test_systematic_tier2_application.py tests/test_systematic_tier2_policy.py
git diff --check
```

`--write` explicitly regenerates only the derived Markdown, summary, three queue CSVs and normalized legacy diagnostic. `--output-dir` writes those same outputs to a separate directory. Manual decisions, the exact approved request and the screening ledger remain read-only inputs.

See [validation results](../data/processed/systematic_tier2_application_2026_09/validation.json), [reproducibility evidence](../data/processed/systematic_tier2_application_2026_09/reproducibility.json) and [full-suite output](../data/processed/systematic_tier2_application_2026_09/full_suite.txt). No papers are added or removed, no policies are retroactively applied to the corpus, and nothing is committed or pushed.
