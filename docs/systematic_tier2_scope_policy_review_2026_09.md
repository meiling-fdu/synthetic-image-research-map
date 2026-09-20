# Tier 2 scope-policy review — September 2026

Policy proposal only. No recommendation is an approved inclusion/exclusion decision. No paper, audit status, taxonomy or public output is changed by this report.

Generated from the [215-row reviewed policy CSV](../data/manual/systematic_tier2_scope_policy_clusters_2026_09.csv) and [11-policy canonical registry](../data/manual/systematic_tier2_scope_policies_2026_09.json). Counts are derived, never duplicated in the manual policy registry.

## Population and method

The [frozen inventory](../data/processed/systematic_tier2_policy_2026_09/inventory.json) preserves every original audit field for exactly 215 rows selected by `final_status == CANDIDATE_ADD_NEEDS_SCOPE_REVIEW`. Selection reads other status values only to exclude them; Tier 1 and Tier 3 evidence is not classified. No broad search or new primary-source adjudication was performed. Cached abstracts, partial summaries and original scope evidence support routing, not final admission.

Assignments were reviewed by contribution, endpoint, mechanism and evaluation unit, rather than generated from title keywords. For example, STD-FD concerns diffusion steps rather than video; sequential face edits need not be video; a diffusion segmentation backbone does not establish generative input manipulations; Guard Me If You Know Me is a detector, whereas NullSwap is prevention. Every row has one primary cluster and optional overlapping descriptive tags.

The primary uncertainty causes are disjoint: `POLICY_CONFLICT` means an unresolved scope rule is the first blocker; `CURRENT_POLICY_APPLIES` means the cached evidence supports provisional application of an existing explicit or inferred rule; `PAPER_SPECIFIC_EVIDENCE` means a clear rule must be tested against missing evaluation details. The CSV also preserves the earlier request vocabulary in `initial_request_category`.

The four provisional outcomes are mutually exclusive. A policy-conflict row is never counted as likely included/excluded. Additional evidence flags may coexist with user-policy conflicts: approving a rule does not verify the paper. When generative coverage is unknown, establish that fact first; if the result is classical-only, the separate TRADITIONAL policy conflict becomes relevant.

### Global provisional outcomes

| Outcome | Papers |
| --- | --- |
| LIKELY_INCLUDE | 21 |
| LIKELY_EXCLUDE | 78 |
| PAPER_SPECIFIC_REVIEW | 41 |
| USER_POLICY_DECISION_REQUIRED | 75 |
| TOTAL | 215 |

Uncertainty causes: 99 current-policy applications; 41 paper-specific evidence checks; 75 policy conflicts. There are 88 paper-specific-review flags in all, including 47 within the user-policy group. These flags are not a fifth outcome.

## Primary policy clusters

| Cluster | Papers | Boundary | Recommendation | Likely include | Likely exclude | Evidence | User |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EMBED — Embedding-centric active provenance | 40 | New watermark/fingerprint injection is the main contribution; paired decoding or payload accuracy alone does not make it an independent forensic evaluation. | RECOMMEND_EXCLUDE | 0 | 40 | 0 | 0 |
| VERIFY — Independent watermark detection and recovery | 5 | Inference on already generated/watermarked images, without making a new embedding mechanism the substantive contribution. | RECOMMEND_INCLUDE_WITH_CONDITION | 3 | 0 | 2 | 0 |
| WM_EVAL — Watermark robustness and evasion | 14 | Independent attacks, benchmarks and analysis of watermark-based image forensic decisions. | RECOMMEND_INCLUDE_WITH_CONDITION | 10 | 0 | 4 | 0 |
| HYBRID — Proactive manipulation forensics | 11 | Premarking or generator intervention coupled to generative-edit localization or separately deployed passive detection. | RECOMMEND_NEEDS_USER_POLICY_DECISION | 0 | 0 | 0 | 11 |
| PROTECT — Protection, ownership and governance without a forensic endpoint | 27 | Image/model IP protection, content transport, identity cloaking, consent infrastructure or metadata whose evaluated target is not synthetic-image forensic inference. | RECOMMEND_EXCLUDE | 0 | 27 | 0 | 0 |
| FACE — Image and frame-level face forensics | 60 | Face-only detection/attribution/localization with a possible image contribution; dataset origin alone cannot resolve eligibility. | RECOMMEND_NEEDS_USER_POLICY_DECISION | 0 | 0 | 0 | 60 |
| MODALITY — Text and temporal-only media boundaries | 15 | Text-only watermarking, video/audio interval decisions, or a video system with no established standalone image contribution. | RECOMMEND_INCLUDE_WITH_CONDITION | 0 | 11 | 4 | 0 |
| TRADITIONAL — Classical-only manipulation | 4 | Copy-move, splicing and document/Photoshop-style edits without a demonstrated generative component. | RECOMMEND_NEEDS_USER_POLICY_DECISION | 0 | 0 | 0 | 4 |
| IMAGE — Generative and mixed image forensics: evidence threshold | 32 | Substantive generated-image/edit detection, spatial localization, mixed benchmarks, rendering or specialized scientific imagery; unknown input provenance remains evidence uncertainty. | RECOMMEND_INCLUDE_WITH_CONDITION | 4 | 0 | 28 | 0 |
| ATTRIBUTION — Passive image-source and provenance attribution | 4 | Image-to-generator/training-source inference versus model-service authentication, parameter inference or legal infringement scoring. | RECOMMEND_INCLUDE_WITH_CONDITION | 1 | 0 | 3 | 0 |
| EVASION — Attacks on passive image forensics | 3 | Attack-only, attack-plus-defense and red-team methods evaluated against passive synthetic-image detectors or source attributors. | RECOMMEND_INCLUDE_WITH_CONDITION | 3 | 0 | 0 | 0 |

## Decisions requiring user input

Only three new decisions are warranted by the inspected precedent. Ranking uses direct affected population, recurring scope ambiguity, conceptual importance and expansion risk. The other eight clusters use existing explicit or defensibly inferred rules; no extra questions are manufactured to reach a target of five to ten.

### 1. Image and frame-level face forensics — 60 directly affected

Should face-only work qualify when it independently evaluates still-image or image-frame forensics, while temporal-only systems and frame extraction without an image-level evaluation remain outside scope?

**Recommended answer: Yes**, subject to this exact condition: Proposed default: accept independently evaluated still-image or image-frame forensic decisions, including facial generative editing, with the deepfake label. A video dataset is permitted only when a standalone image/frame contribution and image/frame evaluation are explicit; frame extraction alone and temporal-only/video-system metrics do not qualify.

**If Yes:** Apply the image-level condition prospectively; later review must check video/frame metrics and existing exclusion identities.

**If No:** Require a substantive non-face generated-image component for new face-only candidates; historical image-face inclusions remain exceptions until separately reviewed.

**Main included precedent:** Face X-Ray for More General Face Forgery Detection.

**Main excluded precedent:** Wavelet-Packet Powered Deepfake Image Detection.; FaceForensics++: Learning to Detect Manipulated Facial Images; Forensics Adapter: Unleashing CLIP for Generalizable Face Forgery Detection.

This resolves a reusable boundary for up to 60 primary-cluster candidates, not 60 guaranteed admissions. Other clusters may carry a secondary dependency, so these direct counts are conservative and non-overlapping.

### 2. Proactive manipulation forensics — 11 directly affected

Should hybrid systems qualify when they separately evaluate generative-edit localization or improvements to an independent passive detector, even when premarking or generator control is required?

**Recommended answer: Yes**, subject to this exact condition: Proposed default: include only a separately evaluated generative-edit localization or passive-detector improvement contribution, measured against edit masks or independent detector decisions. Payload accuracy, mark-region localization and generic image protection alone do not qualify. Disclose premarking/generator-control requirements.

**If Yes:** Apply the stated endpoint condition in a future review; watermark-only region or payload results remain insufficient.

**If No:** Keep generator-controlled and premarked manipulation-forensics systems outside the proposed scope, while retaining independent verification/robustness studies.

**Main included precedent:** AI-generated Image Detection: Passive or Watermark?.

**Main excluded precedent:** The Stable Signature: Rooting Watermarks in Latent Diffusion Models; InvisMark: Invisible and Robust Watermarking for AI-Generated Image Provenance.

This resolves a reusable boundary for up to 11 primary-cluster candidates, not 11 guaranteed admissions. Other clusters may carry a secondary dependency, so these direct counts are conservative and non-overlapping.

### 3. Classical-only manipulation — 4 directly affected

Should new classical-manipulation papers require a substantive evaluated generative-image component, while existing classical-only inclusions remain unchanged pending a separate review?

**Recommended answer: Yes**, subject to this exact condition: Proposed default: require an explicit experimental task/protocol or substantive survey treatment of generative editing or synthetic-image forensics. A generative-model introduction, diffusion backbone, synthetic training mask, or a lone incidental comparator is insufficient. Do not remove the two historical classical-only inclusions in this task.

**If Yes:** Apply the stated generative-component threshold in later reconciliation; classical-only methods and resources do not qualify automatically.

**If No:** Define broader classical-forensics coverage before adding these candidates; neither the current taxonomy nor two exceptions specifies a maintainable limit.

**Main included precedent:** IoT-Oriented Security for Small Sensor Systems Using DnCNN Denoising and Multimodal Feature Fusion for Image Forgery Detection.

**Main excluded precedent:** No matching explicit classical-only exclusion was found; the conflict is between stated generated-image scope and two included classical-only records.

This resolves a reusable boundary for up to 4 primary-cluster candidates, not 4 guaranteed admissions. Other clusters may carry a secondary dependency, so these direct counts are conservative and non-overlapping.

## Precedent checks and policy options

The inspected current corpus contains 636 papers. Taxonomy comes from [paper_taxonomy.py](../scripts/paper_taxonomy.py) and the [taxonomy registry](../data/curated/paper_taxonomy.csv). [AGENTS.md](../AGENTS.md) establishes the generated-image boundary. The [README](../README.md) automatic candidate filter is a discovery rule, not an infallible description of all manual curation. Current Tier 1 reconciliation is consulted read-only for existing generative editing and scientific-image precedent.

The ordinary watermark conflict is reconciled at moderate confidence by contribution type, not by banning all active provenance or pretending embedding papers lack decoders. Face-only and classical-only practice cannot be reconciled fully by task, modality or method-versus-analysis distinctions. Hybrid manipulation forensics is an unresolved extension between embedding and independent forensic evaluation. Opaque exclusion notes such as “ML” do not prove the curator’s intent; the report distinguishes observed practice from explicit rationale.

Each option below affects at most the cluster population shown. These are candidates whose policy treatment would be reconsidered, not estimated additions; evidence gaps and later identity/exclusion checks can reduce the realized impact. Recommendation selection follows conceptual fit and precedent, not candidate volume.

<a id="policy-EMBED"></a>

### EMBED — Embedding-centric active provenance (40 papers)

**Boundary:** New watermark/fingerprint injection is the main contribution; paired decoding or payload accuracy alone does not make it an independent forensic evaluation.

**Precedent assessment:** APPARENT_CONFLICT_RECONCILED: contribution type explains the inspected records. ImageDetectBench and WEvade evaluate forensic systems; EKILA combines visual attribution with credentials, rather than proposing signal embedding. Stable Signature and InvisMark are excluded embedding methods. Their notes say only ML, so this is a moderate-confidence inferred practice, not an explicit universal rule. No comparable embedding-centric inclusion was identified in the current title/abstract scan.

**Included precedents:**

- **AI-generated Image Detection: Passive or Watermark?** — `10.48550/arxiv.2411.13553`; tasks=detection; image_scopes=fully_generated; research_types=benchmark. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Evading Watermark based Detection of AI-Generated Content** — `10.1145/3576915.3623189`; tasks=detection; image_scopes=fully_generated; research_types=analysis_study. Source: [current public corpus](../web/data/public_preview_papers.json).
- **EKILA: Synthetic Media Provenance and Attribution for Generative Art** — `10.1109/cvprw59228.2023.00098`; tasks=source_attribution; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **The Stable Signature: Rooting Watermarks in Latent Diffusion Models** — `exclusion-78b444d274874e47acbaee80631a942a`; reason `out_of_scope`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).
- **InvisMark: Invisible and Robust Watermarking for AI-Generated Image Provenance** — `exclusion-84f3cb6f4b844e938bebca64d8415fcf`; reason `out_of_scope`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Mechanism check:** The cached Stable Signature abstract explicitly describes decoder fine-tuning, watermark extraction and a statistical source-model test with an image-origin accuracy/false-positive evaluation. It is not embedding-only and does not lack forensic metrics. InvisMark describes high-resolution embedding, UUID payloads, decoding and robustness. Thus the defensible inferred distinction is new mark construction plus its paired verification versus an independent forensic evaluation, not 'embedding has no detector'. This explains observed outcomes but cannot establish the intent behind the opaque ML notes.

Cached source abstracts: [20260619T193231Z_005_diffusion-generated-image-detection.json](../data/raw/openalex/20260619T193231Z_005_diffusion-generated-image-detection.json), [20260619T211726Z_017_generated-image-provenance.json](../data/raw/openalex/20260619T211726Z_017_generated-image-provenance.json).


**Representative Tier 2 candidates:**

- Watermark-based Attribution of AI-Generated Content (`audit:043066940501b9cf`) — Cached contribution constructs or changes an embedded signature and evaluates its recovery; apply the contribution-based boundary rather than the presence of a decoder. [Original primary link](https://proceedings.iclr.cc/paper_files/paper/2026/hash/ad77a15531fbccefa8be5e434b4b7908-Abstract-Conference.html).
- GROW: Watermark Generation with Progressive Guidance for Diffusion Models (`audit:047b19fc2f05aeb1`) — Cached contribution constructs or changes an embedded signature and evaluates its recovery; apply the contribution-based boundary rather than the presence of a decoder. [Original primary link](https://openaccess.thecvf.com/content/CVPR2026/html/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.html).
- MaxMark: High-Capacity Diffusion-Native Watermarking via Robust and Invertible Latent Embedding (`audit:1344bf26dae2967b`) — Cached contribution constructs or changes an embedded signature and evaluates its recovery; apply the contribution-based boundary rather than the presence of a decoder. [Original primary link](https://openaccess.thecvf.com/content/CVPR2026/html/Chang_MaxMark_High-Capacity_Diffusion-Native_Watermarking_via_Robust_and_Invertible_Latent_Embedding_CVPR_2026_paper.html).

**Recommendation:** `RECOMMEND_EXCLUDE`. Keep new signal-injection/embedding mechanisms outside the proposed scope when their forensic result is only recovery of their own mark. Independent evaluation and hybrid manipulation forensics use separate clusters.

**Confidence:** moderate. **Future recurrence:** high.

**Over-inclusion risk:** Expanding into the whole watermark engineering and model-distribution literature.

**Under-inclusion risk:** Missing useful proactive attribution mechanisms.

**Provisional counts:** include 0; exclude 40; evidence review 0; user decision 0. Additional paper-specific flags: 0.

**A — Retain contribution-based boundary (recommended)**

- Rationale: Prioritize analysis of generated images over engineering their signatures.
- Taxonomy fit: No new task category; detection/attribution labels describe the endpoint, not automatic eligibility.
- Current-corpus impact: Explains the two embedding exclusions while retaining watermark benchmarks and C2PA-assisted visual attribution.
- Approximate Tier 2 population affected: up to 40; no existing record is changed.
- Future literature: Keep new embedding systems out; include independent forensic assessments separately.
- Scope-creep risk: Low.

**B — Include embedding with forensic verification**

- Rationale: Treat the paired verification pipeline as sufficient forensic contribution.
- Taxonomy fit: Detection/source_attribution may fit; would need explicit mechanism metadata later.
- Current-corpus impact: Broadens beyond Stable Signature and InvisMark decisions; does not authorize restoring them.
- Approximate Tier 2 population affected: up to 40; no existing record is changed.
- Future literature: Many future watermark engineering papers become candidates.
- Scope-creep risk: High; ordinary bit recovery may masquerade as image authenticity.

**C — Include active provenance broadly**

- Rationale: Map the full provenance ecosystem.
- Taxonomy fit: Credentials, ownership and consent are not always existing forensic tasks.
- Current-corpus impact: Would require a wider scope revision than existing inclusions establish.
- Approximate Tier 2 population affected: up to 40; no existing record is changed.
- Future literature: Includes embedding, model distribution and copyright infrastructure.
- Scope-creep risk: Very high.

<a id="policy-VERIFY"></a>

### VERIFY — Independent watermark detection and recovery (5 papers)

**Boundary:** Inference on already generated/watermarked images, without making a new embedding mechanism the substantive contribution.

**Precedent assessment:** CURRENT_RULE: ImageDetectBench and WEvade establish detection/verification as forensic endpoints; EKILA allows credentials when coupled to visual attribution. Detecting a watermark is not by itself proof of AI origin, and keyless recovery is not synonymous with passive natural-fingerprint attribution.

**Included precedents:**

- **AI-generated Image Detection: Passive or Watermark?** — `10.48550/arxiv.2411.13553`; tasks=detection; image_scopes=fully_generated; research_types=benchmark. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Evading Watermark based Detection of AI-Generated Content** — `10.1145/3576915.3623189`; tasks=detection; image_scopes=fully_generated; research_types=analysis_study. Source: [current public corpus](../web/data/public_preview_papers.json).
- **EKILA: Synthetic Media Provenance and Attribution for Generative Art** — `10.1109/cvprw59228.2023.00098`; tasks=source_attribution; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **The Stable Signature: Rooting Watermarks in Latent Diffusion Models** — `exclusion-78b444d274874e47acbaee80631a942a`; reason `out_of_scope`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).
- **InvisMark: Invisible and Robust Watermarking for AI-Generated Image Provenance** — `exclusion-84f3cb6f4b844e938bebca64d8415fcf`; reason `out_of_scope`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- Rel-Zero: Harnessing Patch-Pair Invariance for Robust Zero-Watermarking Against AI Editing (`audit:25b0f7c849e22db6`) — Zero-watermark uses existing patch relations without pixel modification. Verify that content authentication means image provenance/edit evidence, not only robust copyright matching. [Original primary link](https://openaccess.thecvf.com/content/CVPR2026/html/Chen_Rel-Zero_Harnessing_Patch-Pair_Invariance_for_Robust_Zero-Watermarking_Against_AI_Editing_CVPR_2026_paper.html).
- FARI: Robust One-Step Inversion for Watermarking in Diffusion Models (`audit:84d718fd64786342`) — FARI improves inversion for watermark verification on generated images; it is routed to recovery rather than new watermark embedding. [Original primary link](https://proceedings.iclr.cc/paper_files/paper/2026/hash/dad66bb085bab14fbca07cfa4271f00b-Abstract-Conference.html).
- Finding a needle in a haystack: A Black-Box Approach to Invisible Watermark Detection (`audit:ae545b58fc6849bd`) — Black-box detector distinguishes marked from unmarked images; establish the linkage to synthetic origin/source verification rather than assume any watermark AUC is sufficient. [Original primary link](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/4872_ECCV_2024_paper.php).

**Recommendation:** `RECOMMEND_INCLUDE_WITH_CONDITION`. Require an independently evaluated image-level AI-origin, source/provenance attribution or generative-edit verification endpoint. State key/reference assumptions and false-positive controls; generic watermark-presence AUC or extraction accuracy without this link remains a paper-specific check.

**Confidence:** moderate. **Future recurrence:** high.

**Over-inclusion risk:** Including every decoder optimization or watermark-presence detector.

**Under-inclusion risk:** Excluding useful inference because an earlier producer embedded a mark.

**Provisional counts:** include 3; exclude 0; evidence review 2; user decision 0. Additional paper-specific flags: 2.

**A — Forensic verification only (recommended)**

- Rationale: The evaluated inference endpoint determines relevance.
- Taxonomy fit: Detection/source_attribution/localization only where the endpoint actually matches.
- Current-corpus impact: Consistent with ImageDetectBench, WEvade and EKILA.
- Approximate Tier 2 population affected: up to 5; no existing record is changed.
- Future literature: Admit independent forensic recovery while testing its threat model.
- Scope-creep risk: Bounded by explicit origin or edit verification.

**B — Any watermark recovery**

- Rationale: Make watermark detection itself sufficient.
- Taxonomy fit: Payload recovery is not always a forensic task.
- Current-corpus impact: Goes beyond included evaluation precedents.
- Approximate Tier 2 population affected: up to 5; no existing record is changed.
- Future literature: Large decoder and steganalysis literature enters.
- Scope-creep risk: High.

<a id="policy-WM_EVAL"></a>

### WM_EVAL — Watermark robustness and evasion (14 papers)

**Boundary:** Independent attacks, benchmarks and analysis of watermark-based image forensic decisions.

**Precedent assessment:** APPARENT_CONFLICT_RECONCILED: method versus analysis is not the boundary. WEvade is an attack-only study and ImageDetectBench is a benchmark. Their targets are AI-image forensic decisions, whereas embedding exclusions concern new mark construction.

**Included precedents:**

- **AI-generated Image Detection: Passive or Watermark?** — `10.48550/arxiv.2411.13553`; tasks=detection; image_scopes=fully_generated; research_types=benchmark. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Evading Watermark based Detection of AI-Generated Content** — `10.1145/3576915.3623189`; tasks=detection; image_scopes=fully_generated; research_types=analysis_study. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **The Stable Signature: Rooting Watermarks in Latent Diffusion Models** — `exclusion-78b444d274874e47acbaee80631a942a`; reason `out_of_scope`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).
- **InvisMark: Invisible and Robust Watermarking for AI-Generated Image Provenance** — `exclusion-84f3cb6f4b844e938bebca64d8415fcf`; reason `out_of_scope`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- Image Watermarks are Removable using Controllable Regeneration from Clean Noise (`audit:25416ed25286799a`) — Cached contribution attacks or evaluates image watermarks; independent AI-origin/source verification is the required endpoint. [Original primary link](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d9750da8aec3b79cf14dd29e7ab6605a-Abstract-Conference.html).
- Transferable Black-Box One-Shot Forging of Watermarks via Image Preference Models (`audit:37dd9d92bc5d6431`) — Cached contribution attacks or evaluates image watermarks; independent AI-origin/source verification is the required endpoint. [Original primary link](https://proceedings.neurips.cc/paper_files/paper/2025/hash/47fee9cd8a252161dec7cb48ec0ca2f2-Abstract-Conference.html).
- Robust watermarking using generative priors against image editing: From benchmarking to advances (`audit:2e6496efd94c0b4c`) — W-Bench plus VINE combines editing robustness with embedding; verify that the benchmark evaluates image forensic verification beyond generic copyright payload survival. [Original primary link](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d077bc9ea82a2998ca6b2d0158b5ac6e-Abstract-Conference.html).

**Recommendation:** `RECOMMEND_INCLUDE_WITH_CONDITION`. Include attack-only, attack-plus-defense, benchmark or analytical work when it evaluates AI-image origin/source verification errors under a stated attack or distortion protocol. Generic copyright watermark destruction without this endpoint needs evidence review.

**Confidence:** high. **Future recurrence:** high.

**Over-inclusion risk:** Absorbing generic copyright/steganography attacks merely using a diffusion tool.

**Under-inclusion risk:** Losing important limitations of deployed forensic detectors.

**Provisional counts:** include 10; exclude 0; evidence review 4; user decision 0. Additional paper-specific flags: 4.

**A — Include endpoint-matched evaluations (recommended)**

- Rationale: Forensic reliability includes failures and attacks.
- Taxonomy fit: method, benchmark and analysis_study all fit; no new detector required.
- Current-corpus impact: Directly supported by WEvade and ImageDetectBench.
- Approximate Tier 2 population affected: up to 14; no existing record is changed.
- Future literature: Continue tracking realistic forensic threat models.
- Scope-creep risk: Low with explicit endpoint.

**B — Require a new defense/detector**

- Rationale: Only constructive methods count.
- Taxonomy fit: Would artificially narrow existing research types.
- Current-corpus impact: Conflicts with included evasion and benchmark records.
- Approximate Tier 2 population affected: up to 14; no existing record is changed.
- Future literature: Misses attack-only and comparative evaluation literature.
- Scope-creep risk: Low volume but high under-coverage.

<a id="policy-HYBRID"></a>

### HYBRID — Proactive manipulation forensics (11 papers)

**Boundary:** Premarking or generator intervention coupled to generative-edit localization or separately deployed passive detection.

**Precedent assessment:** UNRESOLVED_EXTENSION: engineering versus independent evaluation explains ordinary embedding precedents, but does not settle a system that modifies the generator to improve a separate passive detector or localizes later edits via premarking. EKILA prevents a blanket ban on active provenance; it is not direct precedent for marker-dependent spatial localization. Task and mechanism distinctions narrow, but do not eliminate, this question.

**Included precedents:**

- **AI-generated Image Detection: Passive or Watermark?** — `10.48550/arxiv.2411.13553`; tasks=detection; image_scopes=fully_generated; research_types=benchmark. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Evading Watermark based Detection of AI-Generated Content** — `10.1145/3576915.3623189`; tasks=detection; image_scopes=fully_generated; research_types=analysis_study. Source: [current public corpus](../web/data/public_preview_papers.json).
- **EKILA: Synthetic Media Provenance and Attribution for Generative Art** — `10.1109/cvprw59228.2023.00098`; tasks=source_attribution; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Face X-Ray for More General Face Forgery Detection** — `10.1109/cvpr42600.2020.00505`; tasks=detection; image_scopes=deepfake; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **The Stable Signature: Rooting Watermarks in Latent Diffusion Models** — `exclusion-78b444d274874e47acbaee80631a942a`; reason `out_of_scope`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).
- **InvisMark: Invisible and Robust Watermarking for AI-Generated Image Provenance** — `exclusion-84f3cb6f4b844e938bebca64d8415fcf`; reason `out_of_scope`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- RecoverMark: Robust Watermarking for Localization and Recovery of Manipulated Faces (`audit:2725362891bb9c1a`) — Cached contribution combines proactive marking and downstream manipulation evidence; the proposed condition requires independent generative-edit or passive-detector results. [Original primary link](https://openaccess.thecvf.com/content/CVPR2026/html/An_RecoverMark_Robust_Watermarking_for_Localization_and_Recovery_of_Manipulated_Faces_CVPR_2026_paper.html).
- Where is the Watermark? Interpretable Watermark Detection at the Block Level (`audit:2f7b1948567ef159`) — Block-wise embedding produces watermark maps; distinguish mark location from ground-truth generative manipulation localization. [Original primary link](https://openaccess.thecvf.com/content/WACV2026/html/Bulychev_Where_is_the_Watermark_Interpretable_Watermark_Detection_at_the_Block_WACV_2026_paper.html).
- Are Watermarks Bugs for Deepfake Detectors? Rethinking Proactive Forensics (`audit:784cc3f2bbbc72c2`) — AdvMark tunes watermarking to improve downstream passive face detectors while recovering marks; this is a true hybrid-policy question. [Original primary link](https://www.ijcai.org/proceedings/2024/673).

**Recommendation:** `RECOMMEND_NEEDS_USER_POLICY_DECISION`. Proposed default: include only a separately evaluated generative-edit localization or passive-detector improvement contribution, measured against edit masks or independent detector decisions. Payload accuracy, mark-region localization and generic image protection alone do not qualify. Disclose premarking/generator-control requirements.

**Confidence:** moderate. **Future recurrence:** high.

**Over-inclusion risk:** Mark recovery and ordinary tamper protection may be mislabeled as generative forensics.

**Under-inclusion risk:** Missing systems that directly improve image forensic evidence.

**Provisional counts:** include 0; exclude 0; evidence review 0; user decision 11. Additional paper-specific flags: 3.

**A — Admit separately evaluated hybrid forensics (recommended)**

- Rationale: Focus on the downstream forensic contribution, with preconditions explicit.
- Taxonomy fit: Detection/localization fit only measured image forensics; mechanism tags would be a future change.
- Current-corpus impact: Extends between excluded embedding and included verification; no direct identical precedent.
- Approximate Tier 2 population affected: up to 11; no existing record is changed.
- Future literature: Admits controlled-generation forensic systems under a bounded endpoint rule.
- Scope-creep risk: Medium; independent metrics must be checked.

**B — Exclude all premarking/generator-dependent hybrids**

- Rationale: Require naturally occurring evidence for manipulation forensics.
- Taxonomy fit: Would restrict mechanism, not task vocabulary.
- Current-corpus impact: Closest to embedding exclusions; broader active-provenance ban would conflict with EKILA.
- Approximate Tier 2 population affected: up to 11; no existing record is changed.
- Future literature: Keeps FFIM/AdvMark-style interventions outside scope.
- Scope-creep risk: Low, but useful forensic contributions omitted.

<a id="policy-PROTECT"></a>

### PROTECT — Protection, ownership and governance without a forensic endpoint (27 papers)

**Boundary:** Image/model IP protection, content transport, identity cloaking, consent infrastructure or metadata whose evaluated target is not synthetic-image forensic inference.

**Precedent assessment:** CURRENT_ENDPOINT_RULE, with limits: EKILA and CS-SLIP mean copyright motivation alone cannot exclude a paper. The distinction is image-to-model/training-source attribution versus ownership, consent, energy metadata or prevention without a forensic decision. Context-only inclusions elsewhere show historical exceptions, but do not establish scope for generic foundation-model governance.

**Included precedents:**

- **EKILA: Synthetic Media Provenance and Attribution for Generative Art** — `10.1109/cvprw59228.2023.00098`; tasks=source_attribution; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Towards Generated Image Provenance Analysis via Conceptual-Similar-Guided-SLIP Retrieval** — `10.1109/lsp.2024.3388958`; tasks=source_attribution; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **Can Model Attribution Bridge AI's Accountability Gap in Safety-Critical Domains?** — `exclusion-f25e1b4e-a6fa-491e-b4eb-a26bfe607e97`; reason `out_of_scope`; exact note: 2026-09-04 focused corpus-scope audit: the publisher abstract reviews attribution of generic remotely deployed machine-learning services and establishes no synthetic-image forensic target.. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).
- **DynEval: Holistic Evaluations of T2I Generative Models in the Wild** — `exclusion-7c618a08-1159-4b87-b057-5c82a36e3b2a`; reason `out_of_scope`; exact note: 2026-09-04 focused corpus-scope audit: the official paper and project evaluate T2I alignment and output quality against human preferences rather than authenticity detection attribution or forgery localization.. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- PlugMark: A Plug-in Zero-Watermarking Framework for Diffusion Models (`audit:01b05b2bc014eb90`) — PlugMark extracts a model knowledge/decision-boundary representation for IP protection; it is not passive attribution from an encountered generated image. [Original primary link](https://openaccess.thecvf.com/content/ICCV2025/html/Chen_PlugMark_A_Plug-in_Zero-Watermarking_Framework_for_Diffusion_Models_ICCV_2025_paper.html).
- Position: Data Authenticity, Consent, & Provenance for AI are all broken: what will it take to fix them? (`audit:03989fcdc1f35433`) — Position paper addresses foundation-model data authenticity, consent and provenance infrastructure; no independently evaluated synthetic-image forensic endpoint is described. [Original primary link](https://proceedings.mlr.press/v235/longpre24b.html).
- Bridging Privacy and Provenance: Traceable Virtual Identity Generation (`audit:0d966331a800104a`) — Virtual identity consistency, anonymity and token-based ownership are the stated evaluations; real-vs-generated forensic evaluation is not established. [Original primary link](https://openaccess.thecvf.com/content/CVPR2026/html/Zeng_Bridging_Privacy_and_Provenance_Traceable_Virtual_Identity_Generation_CVPR_2026_paper.html).

**Recommendation:** `RECOMMEND_EXCLUDE`. Provisionally exclude when the cached contribution is only content/model protection, prevention, generic governance or watermark transport, with no evaluated synthetic-image detection, attribution or generative-edit localization. A concrete image-origin attribution component overrides this boundary and must be examined under VERIFY/ATTRIBUTION/HYBRID.

**Confidence:** moderate. **Future recurrence:** high.

**Over-inclusion risk:** Admitting all generative-model security, consent and image copyright literature.

**Under-inclusion risk:** Overlooking actual visual attribution because it is motivated by copyright.

**Provisional counts:** include 0; exclude 27; evidence review 0; user decision 0. Additional paper-specific flags: 0.

**A — Require an image-forensic endpoint (recommended)**

- Rationale: Align contribution with the project purpose rather than the motivation.
- Taxonomy fit: Protection, quality, consent and energy metadata are not taxonomy tasks.
- Current-corpus impact: Retains EKILA/CS-SLIP on their attribution contribution; aligns with generic-service exclusion.
- Approximate Tier 2 population affected: up to 27; no existing record is changed.
- Future literature: No generic security or provenance infrastructure expansion.
- Scope-creep risk: Low.

**B — Include provenance/security infrastructure**

- Rationale: Offer a broader trust-and-safety map.
- Taxonomy fit: Needs new non-forensic task or contextual scope conventions.
- Current-corpus impact: Some context-only inclusions exist, but generic-service and quality exclusions oppose a blanket expansion.
- Approximate Tier 2 population affected: up to 27; no existing record is changed.
- Future literature: Large IP/security/governance corpus beyond generated-image forensics.
- Scope-creep risk: Very high.

<a id="policy-FACE"></a>

### FACE — Image and frame-level face forensics (60 papers)

**Boundary:** Face-only detection/attribution/localization with a possible image contribution; dataset origin alone cannot resolve eligibility.

**Precedent assessment:** GENUINE_CONFLICT: the image-level principle is conceptually coherent but not consistently applied. Face X-Ray uses facial blending boundaries; excluded Forensics Adapter also targets facial blending boundaries, and Wavelet-Packet explicitly concerns images. Both detection task and image modality overlap. Dataset/benchmark status does not explain all exclusions. Historical scope drift is possible but undocumented; deepfake taxonomy alone is not blanket approval.

**Included precedents:**

- **Face X-Ray for More General Face Forgery Detection** — `10.1109/cvpr42600.2020.00505`; tasks=detection; image_scopes=deepfake; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).
- **GAN Generated Fake Human Face Image Detection** — `10.1109/iitcee59897.2024.10467257`; tasks=detection; image_scopes=deepfake; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Forging the Unknown: Open-Set Deepfake Attribution via Adaptive Fingerprint Learning** — `curated:ed5f779be1e71edddcee`; tasks=source_attribution; image_scopes=deepfake; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **Wavelet-Packet Powered Deepfake Image Detection.** — `exclusion-65b94ab70e6845ffaafb5779ed2dcc6d`; reason `deepfake_only_not_core`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).
- **FaceForensics++: Learning to Detect Manipulated Facial Images** — `exclusion-e65368f3147c43c5ab519a01037afd6d`; reason `deepfake_only_not_core`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).
- **Forensics Adapter: Unleashing CLIP for Generalizable Face Forgery Detection** — `exclusion-a6b1b904db49e1500107889210ef0b5d`; reason `deepfake_only_not_core`; exact note: 2026-09-05 closed Ant/AI-edit gap audit: Face-forgery-only detector.. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- Texture Shape and Order Matter: A New Transformer Design for Sequential DeepFake Detection (`audit:0799f182cbe4cfc0`) — Sequential means recovering the manipulation order from an image; do not misclassify it as temporal video detection. [Original primary link](https://openaccess.thecvf.com/content/WACV2025/html/Li_Texture_Shape_and_Order_Matter_A_New_Transformer_Design_for_WACV_2025_paper.html).
- Tutor-Student Reinforcement Learning: A Dynamic Curriculum for Robust Deepfake Detection (`audit:0847e682e96c182c`) — Cached contribution targets face forensics. Current face-image inclusions and explicit face-only exclusions cannot be reconciled by the deepfake label alone; apply no decision until the boundary is approved. [Original primary link](https://openaccess.thecvf.com/content/CVPR2026/html/Lei_Tutor-Student_Reinforcement_Learning_A_Dynamic_Curriculum_for_Robust_Deepfake_Detection_CVPR_2026_paper.html).
- AuthGuard: Generalizable Deepfake Detection via Language Guidance (`audit:09d9a70b11aa1641`) — Cached contribution targets face forensics. Current face-image inclusions and explicit face-only exclusions cannot be reconciled by the deepfake label alone; apply no decision until the boundary is approved. [Original primary link](https://openaccess.thecvf.com/content/WACV2026/html/Shen_AuthGuard_Generalizable_Deepfake_Detection_via_Language_Guidance_WACV_2026_paper.html).

**Recommendation:** `RECOMMEND_NEEDS_USER_POLICY_DECISION`. Proposed default: accept independently evaluated still-image or image-frame forensic decisions, including facial generative editing, with the deepfake label. A video dataset is permitted only when a standalone image/frame contribution and image/frame evaluation are explicit; frame extraction alone and temporal-only/video-system metrics do not qualify.

**Confidence:** high on conflict; moderate on individual modality. **Future recurrence:** high.

**Over-inclusion risk:** Importing the entire video deepfake literature via frame extraction.

**Under-inclusion risk:** Excluding substantive still-image face synthesis/manipulation forensics.

**Provisional counts:** include 0; exclude 0; evidence review 0; user decision 60. Additional paper-specific flags: 44.

**A — Image-level contribution regardless of face-only focus (recommended)**

- Rationale: Apply the project image boundary consistently.
- Taxonomy fit: Existing deepfake scope plus detection/attribution/localization suffice.
- Current-corpus impact: Fits Face X-Ray but conflicts with face-only exclusions; these remain unchanged until separate approval.
- Approximate Tier 2 population affected: up to 60; no existing record is changed.
- Future literature: Admit substantive image/frame work; require modality evidence.
- Scope-creep risk: Medium; video-only benchmarks must stay separate.

**B — Exclude face-only, require a non-face generative-image component**

- Rationale: Keep the map focused on broader synthetic imagery.
- Taxonomy fit: Restricts use of the existing deepfake scope to mixed work.
- Current-corpus impact: Fits recent face-only exclusions but conflicts with existing image-face inclusions.
- Approximate Tier 2 population affected: up to 60; no existing record is changed.
- Future literature: Far fewer new face-only papers; historical exceptions need separate policy treatment.
- Scope-creep risk: Low expansion, substantial under-coverage.

**C — Include all deepfake systems**

- Rationale: Treat deepfake as sufficient regardless of modality.
- Taxonomy fit: Would broaden beyond generated images to temporal/audio tasks.
- Current-corpus impact: Contradicts AGENTS.md and explicit video-only exclusions.
- Approximate Tier 2 population affected: up to 60; no existing record is changed.
- Future literature: Opens a large video/audio detection literature.
- Scope-creep risk: Very high.

<a id="policy-MODALITY"></a>

### MODALITY — Text and temporal-only media boundaries (15 papers)

**Boundary:** Text-only watermarking, video/audio interval decisions, or a video system with no established standalone image contribution.

**Precedent assessment:** CURRENT_RULE: AGENTS.md focuses on generated images, not audio/video. The temporal-only exclusions implement that rule. A video dataset may support an image method, so unclear frame-level evaluation is an evidence gap rather than automatic exclusion. Temporal diffusion steps and sequential edits to one image are not video.

**Included precedents:**

- **Face X-Ray for More General Face Forgery Detection** — `10.1109/cvpr42600.2020.00505`; tasks=detection; image_scopes=deepfake; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **Training-free Detection of Text-to-video Generations via Over-coherence** — `exclusion-9f5d62eaf196470e9eff250d1e9baba9`; reason `out_of_scope`; exact note: Official WACV 2026 proceedings describe text-to-video detection through temporal over-coherence; video-only method is outside generated-image scope. Evidence: https://openaccess.thecvf.com/content/WACV2026/html/Brokman_Training-free_Detection_of_Text-to-video_Generations_via_Over-coherence_WACV_2026_paper.html. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- PMark: Towards Robust and Distortion-free Semantic-level Watermarking with Channel Constraints (`audit:2a168f7bcfaf6f3d`) — Cached abstract concerns sentence-level LLM watermarking, not image watermarking. [Original primary link](https://proceedings.iclr.cc/paper_files/paper/2026/hash/2d8911db9ecedf866015091b28946e15-Abstract-Conference.html).
- Through the Lens: Benchmarking Deepfake Detectors Against Moiré-Induced Distortions (`audit:3b7fe82da01522f0`) — Moiré benchmark collects videos and tests detectors; standalone image/frame evaluation is not established in the cached abstract. [Original primary link](https://proceedings.neurips.cc/paper_files/paper/2025/hash/75c4f24bf8a51f0b0870f0f9bceea4ea-Abstract-Datasets_and_Benchmarks_Track.html).
- TalkingHeadBench: A Multi-Modal Benchmark & Analysis of Talking-Head DeepFake Detection (`audit:403cc651d6af061c`) — Cached contribution is text-only or a temporal/video-only system; frames or neural architecture alone do not establish an image-forensic contribution. [Original primary link](https://openaccess.thecvf.com/content/WACV2026/html/Xiong_TalkingHeadBench_A_Multi-Modal_Benchmark__Analysis_of_Talking-Head_DeepFake_Detection_WACV_2026_paper.html).

**Recommendation:** `RECOMMEND_INCLUDE_WITH_CONDITION`. Include only an explicitly evaluated standalone image/frame forensic contribution; otherwise text-only, audio-only and temporal/video-only work is provisionally excluded. Per-frame payload recovery in a temporal watermark system is not independently evaluated image-origin detection.

**Confidence:** high. **Future recurrence:** high.

**Over-inclusion risk:** Treating every video frame as proof of an image contribution.

**Under-inclusion risk:** Discarding valid image methods because their data originated in videos.

**Provisional counts:** include 0; exclude 11; evidence review 4; user decision 0. Additional paper-specific flags: 4.

**A — Standalone image contribution (recommended)**

- Rationale: Use the unit of forensic inference and evaluation.
- Taxonomy fit: Image detection/attribution/spatial localization, not time intervals.
- Current-corpus impact: Matches project boundary and temporal-only exclusions.
- Approximate Tier 2 population affected: up to 15; no existing record is changed.
- Future literature: Mixed-modality studies need an independently evaluated image component.
- Scope-creep risk: Low.

**B — Any system processing frames**

- Rationale: Image pixels suffice for entry.
- Taxonomy fit: Temporal/audio tasks exceed current image taxonomy.
- Current-corpus impact: Contradicts the explicit image-only boundary.
- Approximate Tier 2 population affected: up to 15; no existing record is changed.
- Future literature: Video benchmarks, talking-head and audio-visual methods flood scope.
- Scope-creep risk: High.

<a id="policy-TRADITIONAL"></a>

### TRADITIONAL — Classical-only manipulation (4 papers)

**Boundary:** Copy-move, splicing and document/Photoshop-style edits without a demonstrated generative component.

**Precedent assessment:** GENUINE_CONFLICT_WITH_STATED_SCOPE: mixed generative/traditional papers are explained by a substantive generative component, but two current records are traditional_manipulation only: IoT-Oriented Security evaluates CASIA 2.0, and CMFD evaluates copy-move. Thus a blanket traditional-only exclusion is not established current practice. No clean traditional-only exclusion with an explicit, matching rationale was found; quality-artifact exclusions concern the task, not classical manipulation. Historical scope drift/legacy exceptions are plausible, not verified.

**Included precedents:**

- **IoT-Oriented Security for Small Sensor Systems Using DnCNN Denoising and Multimodal Feature Fusion for Image Forgery Detection** — `curated:3ea88dc6c3224d22d416`; tasks=detection; image_scopes=traditional_manipulation; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Copy-Move Forgery Detection (CMFD) Using Deep Learning for Image and Video Forensics** — `10.3390/jimaging7030059`; tasks=detection; image_scopes=traditional_manipulation; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).
- **FakeShield: Explainable Image Forgery Detection and Localization via Multi-Modal Large Language Models** — `curated:e69688740a4586c62c5d`; tasks=detection,localization; image_scopes=generative_editing,deepfake,traditional_manipulation; research_types=method,dataset. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **Localizing Perceptual Artifacts in Synthetic Images for Image Quality Assessment via Deep-Learning-Based Anomaly Detection** — `exclusion-e90e9f8a47eb43e2b53702037d6e5fe7`; reason `out_of_scope`; exact note: Publisher/Crossref abstract targets perceptual defects for image quality assurance and editing, not forensic origin detection or manipulation localization. Exclude consistently with existing fidelity-only scope decisions. Evidence: https://www.mdpi.com/2079-9292/15/5/916; https://api.crossref.org/works/10.3390/electronics15050916. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- DOCFORGE-BENCH: A Comprehensive 0-shot Benchmark for Document Forgery Detection and Analysis (`audit:203bb622e535dd5a`) — Cached abstract explicitly says all eight document datasets predate generative AI; diffusion/LLM edits are presented as a future gap. [Original primary link](https://doi.org/10.48550/arxiv.2603.01433).
- IMDPrompter: Adapting SAM to Image Manipulation Detection by Cross-View Automated Prompt Learning (`audit:ba8b9da330652e1c`) — Cached evaluation concerns classical tampering. Prospective generative-only policy conflicts with current classical-only inclusions. [Original primary link](https://proceedings.iclr.cc/paper_files/paper/2025/hash/bda5c35eded86adaf0231748e3ce071c-Abstract-Conference.html).
- Toward Real-world Text Image Forgery Localization: Structured and Interpretable Data Synthesis (`audit:d3f42894e53e74d2`) — FSTS replays human editing traces from PSD/logs; procedurally synthetic tampering data are not proof of generative-AI manipulation. [Original primary link](https://proceedings.neurips.cc/paper_files/paper/2025/hash/df34ea73a7e2108b816194200f1442be-Abstract-Datasets_and_Benchmarks_Track.html).

**Recommendation:** `RECOMMEND_NEEDS_USER_POLICY_DECISION`. Proposed default: require an explicit experimental task/protocol or substantive survey treatment of generative editing or synthetic-image forensics. A generative-model introduction, diffusion backbone, synthetic training mask, or a lone incidental comparator is insufficient. Do not remove the two historical classical-only inclusions in this task.

**Confidence:** high on exception; moderate on prospective boundary. **Future recurrence:** high.

**Over-inclusion risk:** Expanding into all image forgery, sensor and document authentication.

**Under-inclusion risk:** Omitting reusable classical-forensics methods and benchmark infrastructure.

**Provisional counts:** include 0; exclude 0; evidence review 0; user decision 4. Additional paper-specific flags: 0.

**A — Substantive generative component required (recommended)**

- Rationale: Preserve the map purpose while admitting mixed forensics.
- Taxonomy fit: traditional_manipulation remains valid as a secondary scope.
- Current-corpus impact: Fits mixed papers but requires acknowledging two standalone historical exceptions.
- Approximate Tier 2 population affected: up to 4; no existing record is changed.
- Future literature: Classical-only methods/codebases stay out unless generative coverage is substantive.
- Scope-creep risk: Low.

**B — Include classical manipulation broadly**

- Rationale: Interpret the traditional_manipulation taxonomy value as an independent scope.
- Taxonomy fit: Fits existing vocabulary.
- Current-corpus impact: Fits two current standalone inclusions but broadens the stated generated-image purpose.
- Approximate Tier 2 population affected: up to 4; no existing record is changed.
- Future literature: Large copy-move, splicing and document-forensics literature becomes eligible.
- Scope-creep risk: High.

**C — Include classical benchmarks/infrastructure only**

- Rationale: Retain transferable resources but not all methods.
- Taxonomy fit: dataset/benchmark types provide a boundary, but method resources can be hybrid.
- Current-corpus impact: Does not fully explain the two included classical methods.
- Approximate Tier 2 population affected: up to 4; no existing record is changed.
- Future literature: Adds another contribution-type exception requiring maintenance.
- Scope-creep risk: Medium.

<a id="policy-IMAGE"></a>

### IMAGE — Generative and mixed image forensics: evidence threshold (32 papers)

**Boundary:** Substantive generated-image/edit detection, spatial localization, mixed benchmarks, rendering or specialized scientific imagery; unknown input provenance remains evidence uncertainty.

**Precedent assessment:** CURRENT_RULE for a substantive generative component: current Tier 1 and mixed-forensics inclusions establish image-level detection/localization in both general and scientific domains. A diffusion detector/backbone is not evidence that the input manipulation is generative. Traditional-only eligibility remains the separate TRADITIONAL conflict; unclear candidates first need their evaluated manipulation types established.

**Included precedents:**

- **Weakly-Supervised Deepfake Localization in Diffusion-Generated Images** — `curated:9e6bc47bc75cd7b9b637`; tasks=detection,localization; image_scopes=fully_generated,generative_editing,deepfake; research_types=method,dataset,analysis_study. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Forensic Analysis of Synthetically Generated Western Blot Images** — `curated:d9ecbce63bbd80b54180`; tasks=detection; image_scopes=fully_generated; research_types=method,dataset,analysis_study. Source: [current public corpus](../web/data/public_preview_papers.json).
- **ForensicHub: A Unified Benchmark & Codebase for All-Domain Fake Image Detection and Localization** — `curated:4c4e9ffacf08b5eb2355`; tasks=detection,localization; image_scopes=fully_generated,deepfake,traditional_manipulation; research_types=dataset,benchmark. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **Cascade learning from adversarial synthetic images for accurate pupil detection** — `exclusion-f7ba6941-52b6-4ea5-8228-6f67e18cd369`; reason `downstream_synthetic_data_only`; exact note: 2026-09-04 focused corpus-scope audit: the publisher methodology uses GAN-refined synthetic eyes as training augmentation for pupil localization on real images rather than treating synthetic-image forensics as the target.. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).
- **Localizing Perceptual Artifacts in Synthetic Images for Image Quality Assessment via Deep-Learning-Based Anomaly Detection** — `exclusion-e90e9f8a47eb43e2b53702037d6e5fe7`; reason `out_of_scope`; exact note: Publisher/Crossref abstract targets perceptual defects for image quality assurance and editing, not forensic origin detection or manipulation localization. Exclude consistently with existing fidelity-only scope decisions. Evidence: https://www.mdpi.com/2079-9292/15/5/916; https://api.crossref.org/works/10.3390/electronics15050916. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- STD-FD: Spatio-Temporal Distribution Fitting Deviation for AIGC Forgery Identification (`audit:032ad7d6b71836a2`) — Spatio-temporal describes diffusion reconstruction/distribution fitting here, not a video-only contribution. [Original primary link](https://proceedings.mlr.press/v267/lou25a.html).
- TGIF2: extended text-guided inpainting forgery dataset and benchmark (`audit:07194f58b4540acc`) — Image-forgery detection/localization is described, but the evaluated generative manipulation types are not established in the cached evidence. [Original primary link](https://doi.org/10.1186/s13635-026-00235-9).
- DINOv3 Beats Specialized Detectors: A Simple Foundation Model Baseline for Image Forensics (`audit:0dc47031ed0bccc5`) — DINOv3/LoRA and pixel F1 establish localization, but a generative-model introduction does not establish generative inputs in CAT-Net/MVSS evaluation protocols. [Original primary link](https://arxiv.org/abs/2604.16083).

**Recommendation:** `RECOMMEND_INCLUDE_WITH_CONDITION`. Require a named generative-image/edit evaluation protocol with corresponding detection, source-attribution or spatial manipulation results; for a survey, substantive coverage of that task. Multimodal papers require independently evaluated image forensics. Biomedical domain, neural rendering and use of language are not exclusions. Quality/aesthetic defects, downstream recognition and mere synthetic training-data use do not qualify.

**Confidence:** high on rule; variable cached evidence. **Future recurrence:** high.

**Over-inclusion risk:** Mistaking any diffusion model, synthetic training data or visual fraud for synthetic-image forensics.

**Under-inclusion risk:** Missing generative editing, neural rendering, domain-specific or mixed benchmarks.

**Provisional counts:** include 4; exclude 0; evidence review 28; user decision 0. Additional paper-specific flags: 28.

**A — Substantive image-forensic evaluation (recommended)**

- Rationale: Match the contribution rather than the architecture or application domain.
- Taxonomy fit: Detection/source_attribution/localization with method/dataset/benchmark/survey/analysis_study all allowed.
- Current-corpus impact: Directly supported by current mixed-forensics and Western-blot inclusions.
- Approximate Tier 2 population affected: up to 32; no existing record is changed.
- Future literature: Require a reproducible task/protocol for methods and benchmarks, substantive coverage for surveys.
- Scope-creep risk: Low.

**B — Any generative-AI mention or synthetic training data**

- Rationale: Use broad discovery language as final eligibility.
- Taxonomy fit: Confuses training method with image scope.
- Current-corpus impact: Contradicts pupil-detection and quality-only exclusions.
- Approximate Tier 2 population affected: up to 32; no existing record is changed.
- Future literature: Imports general vision and classical manipulation papers indiscriminately.
- Scope-creep risk: High.

<a id="policy-ATTRIBUTION"></a>

### ATTRIBUTION — Passive image-source and provenance attribution (4 papers)

**Boundary:** Image-to-generator/training-source inference versus model-service authentication, parameter inference or legal infringement scoring.

**Precedent assessment:** CURRENT_ENDPOINT_RULE: source-generator and training-image provenance are included, including retrieval and C2PA-assisted visual attribution. Generic service attribution is explicitly excluded. Reverse Engineering has only an opaque ML note; it cannot establish a blanket ban on image-based model analysis. Per-paper endpoint checks remain necessary.

**Included precedents:**

- **ManiFPT: Defining and Analyzing Fingerprints of Generative Models** — `curated:34fdf09ae334914a2723`; tasks=detection,source_attribution; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Towards Generated Image Provenance Analysis via Conceptual-Similar-Guided-SLIP Retrieval** — `10.1109/lsp.2024.3388958`; tasks=source_attribution; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).
- **EKILA: Synthetic Media Provenance and Attribution for Generative Art** — `10.1109/cvprw59228.2023.00098`; tasks=source_attribution; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **Can Model Attribution Bridge AI's Accountability Gap in Safety-Critical Domains?** — `exclusion-f25e1b4e-a6fa-491e-b4eb-a26bfe607e97`; reason `out_of_scope`; exact note: 2026-09-04 focused corpus-scope audit: the publisher abstract reviews attribution of generic remotely deployed machine-learning services and establishes no synthetic-image forensic target.. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).
- **Reverse Engineering of Generative Models: Inferring Model Hyperparameters From Generated Images** — `exclusion-7e31577d29a2427bac4e8985f6286cf4`; reason `out_of_scope`; exact note: ML. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- Riemannian-Geometric Fingerprints of Generative Models (`audit:07f15e7e8a78398a`) — Geometric fingerprints cover Vision and Vision-Language models; verify image-source attribution inputs and reference labels rather than assuming all model authentication qualifies. [Original primary link](https://openaccess.thecvf.com/content/ICCV2025/html/Song_Riemannian-Geometric_Fingerprints_of_Generative_Models_ICCV_2025_paper.html).
- Scalable Black-Box Model Attribution for Images (`audit:80dc647f134b129b`) — RPA explicitly asks which model produced a given image and evaluates source-model classification; current source-attribution precedent applies. [Original primary link](https://arxiv.org/abs/2608.15652).
- MCID: Multi-aspect Copyright Infringement Detection for Generated Images (`audit:b38746fd3d64e802`) — MCID evaluates legal infringement types; inspect whether it recovers responsible visual sources as CS-SLIP/EKILA do, rather than only predicting infringement labels. [Original primary link](https://openaccess.thecvf.com/content/ICCV2025/html/Huang_MCID_Multi-aspect_Copyright_Infringement_Detection_for_Generated_Images_ICCV_2025_paper.html).

**Recommendation:** `RECOMMEND_INCLUDE_WITH_CONDITION`. Require forensic source inference from generated images (generator, lineage, or responsible training-image/source provenance), evaluated against known source/reference truth. Generic query-only ownership tests, hyperparameter characterization or legal infringement labels alone do not suffice; visual source-recovery components must be identified.

**Confidence:** moderate. **Future recurrence:** high.

**Over-inclusion risk:** Expanding into all model IP, membership and legal infringement detection.

**Under-inclusion risk:** Rejecting meaningful visual provenance because it concerns ownership or analysis rather than a detector.

**Provisional counts:** include 1; exclude 0; evidence review 3; user decision 0. Additional paper-specific flags: 3.

**A — Image-source inference (recommended)**

- Rationale: Keep attribution tied to an image and an identifiable source.
- Taxonomy fit: source_attribution; analysis_study need not propose a detector.
- Current-corpus impact: Consistent with ManiFPT, CS-SLIP and EKILA; does not overread opaque exclusions.
- Approximate Tier 2 population affected: up to 4; no existing record is changed.
- Future literature: Allows passive source and lineage analysis with endpoint checks.
- Scope-creep risk: Bounded.

**B — All model/ownership attribution**

- Rationale: Include any identification of models or rights.
- Taxonomy fit: Generic model-service and legal tasks need broader scope.
- Current-corpus impact: Contradicts explicit generic-service exclusion.
- Approximate Tier 2 population affected: up to 4; no existing record is changed.
- Future literature: Large model-security/IP literature enters.
- Scope-creep risk: High.

<a id="policy-EVASION"></a>

### EVASION — Attacks on passive image forensics (3 papers)

**Boundary:** Attack-only, attack-plus-defense and red-team methods evaluated against passive synthetic-image detectors or source attributors.

**Precedent assessment:** CURRENT_RULE: attack-only studies are already included. No-new-detector is not an exclusion rule. Attacking a generator to prevent unwanted synthesis is a different endpoint from attacking a forensic detector; the former belongs to PROTECT unless forensic evidence is also evaluated.

**Included precedents:**

- **Sanitizing Diffusion-Generated Images via Fingerprint Removal and Adversarial Perturbation for Forensic Evasion** — `curated:82a6421311c4d39076d9`; tasks=detection; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).
- **Evasion on General GAN-Generated Image Detection by Disentangled Representation** — `curated:4b042ad660312ec3b338`; tasks=detection; image_scopes=fully_generated; research_types=method. Source: [current public corpus](../web/data/public_preview_papers.json).

**Excluded or contrasting precedents:**

- **Cascade learning from adversarial synthetic images for accurate pupil detection** — `exclusion-f7ba6941-52b6-4ea5-8228-6f67e18cd369`; reason `downstream_synthetic_data_only`; exact note: 2026-09-04 focused corpus-scope audit: the publisher methodology uses GAN-refined synthetic eyes as training augmentation for pupil localization on real images rather than treating synthetic-image forensics as the target.. Source: [active exclusion registry](../data/curated/paper_exclusions.csv).

**Representative Tier 2 candidates:**

- Vulnerabilities in AI-generated Image Detection: The Challenge of Adversarial Attacks (`audit:2ec9b9251586d3bb`) — The target is a synthetic-image forensic detector or attributor; existing attack-only inclusions support the proposed rule. [Original primary link](https://arxiv.org/abs/2407.20836).
- Untraceable DeepFakes via Traceable Fingerprint Elimination (`audit:5413d2706f713d11`) — Multiplicative attacks erase generated-image traces to evade source attributors across 12 generators and 6 attribution models; existing attack precedent applies. [Original primary link](https://proceedings.iclr.cc/paper_files/paper/2026/hash/8e8399e5e7aed601c9f135f40be26564-Abstract-Conference.html).
- PolyJuice Makes It Real: Black-Box, Universal Red Teaming for Synthetic Image Detectors (`audit:5a3a0232762bb033`) — The target is a synthetic-image forensic detector or attributor; existing attack-only inclusions support the proposed rule. [Original primary link](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b9b228d28770dc2a18922de5cd49f1d9-Abstract-Conference.html).

**Recommendation:** `RECOMMEND_INCLUDE_WITH_CONDITION`. Require measured evasion or robustness of an image synthetic-origin detector/source attributor, including an explicit threat model. No new detector or defense is required. Traditional-only and temporal-only targets follow their separate boundaries.

**Confidence:** high. **Future recurrence:** high.

**Over-inclusion risk:** Including generic adversarial ML or generation-prevention methods.

**Under-inclusion risk:** Missing detector weaknesses essential to forensic reliability.

**Provisional counts:** include 3; exclude 0; evidence review 0; user decision 0. Additional paper-specific flags: 0.

**A — Include forensic attacks and defenses (recommended)**

- Rationale: Failures of a forensic system are part of its evidence base.
- Taxonomy fit: method or analysis_study; target task supplies taxonomy.
- Current-corpus impact: Directly matches Sanitizing and Evasion inclusions.
- Approximate Tier 2 population affected: up to 3; no existing record is changed.
- Future literature: Continue including scoped red-team evaluations.
- Scope-creep risk: Low.

**B — Require constructive detection**

- Rationale: Exclude attack-only work.
- Taxonomy fit: Would constrain existing analysis/method coverage.
- Current-corpus impact: Contradicts current attack-only inclusions.
- Approximate Tier 2 population affected: up to 3; no existing record is changed.
- Future literature: Misses vulnerabilities and realistic threat models.
- Scope-creep risk: Low expansion; high under-coverage.

## Subgroup crosswalks

These tags are descriptive and can overlap; only primary-cluster/outcome tables sum to 215. Counts of zero mean no case was established from this inventory, not a claim about the literature. “Embedding-centric” includes a paired decoder; no paper was asserted to be strictly embedding-only without recovery. Cryptographic tags include non-image/general theory candidates and must not be read as three image-credential systems.

Each subgroup inherits the exact condition, included/excluded precedents and hidden-rule assessment from the listed policy sections. A mixed subgroup cannot be reduced to one yes/no: its user count shows only the unresolved primary-policy subset.

### Watermark, provenance and security

| Subgroup | Tagged papers | Applicable policies / precedents | User input | Evidence flags |
| --- | --- | --- | --- | --- |
| watermark_embedding_centric | 50 | [EMBED](#policy-EMBED), [HYBRID](#policy-HYBRID) | 10 | 3 |
| active_fingerprint_injection | 6 | [EMBED](#policy-EMBED) | 0 | 0 |
| provenance_recovery | 14 | [ATTRIBUTION](#policy-ATTRIBUTION), [EMBED](#policy-EMBED), [VERIFY](#policy-VERIFY) | 0 | 3 |
| cryptographic_provenance | 3 | [EMBED](#policy-EMBED), [MODALITY](#policy-MODALITY), [PROTECT](#policy-PROTECT) | 0 | 0 |
| watermark_detection | 46 | [EMBED](#policy-EMBED), [HYBRID](#policy-HYBRID), [VERIFY](#policy-VERIFY), [WM_EVAL](#policy-WM_EVAL) | 1 | 2 |
| watermark_verification | 49 | [EMBED](#policy-EMBED), [VERIFY](#policy-VERIFY), [WM_EVAL](#policy-WM_EVAL) | 0 | 2 |
| hybrid_active_passive | 11 | [HYBRID](#policy-HYBRID) | 11 | 3 |
| watermark_robustness_evasion | 20 | [MODALITY](#policy-MODALITY), [PROTECT](#policy-PROTECT), [WM_EVAL](#policy-WM_EVAL) | 0 | 4 |
| independent_watermark_detection | 2 | [VERIFY](#policy-VERIFY) | 0 | 1 |
| verification_recovery | 3 | [VERIFY](#policy-VERIFY) | 0 | 1 |
| watermark_embedding_only | 0 | No established candidate; no new policy question | 0 | 0 |
| credentials_metadata | 2 | [PROTECT](#policy-PROTECT) | 0 | 0 |
| copyright_or_model_ownership | 22 | [ATTRIBUTION](#policy-ATTRIBUTION), [EMBED](#policy-EMBED), [PROTECT](#policy-PROTECT) | 0 | 1 |
| generation_prevention | 3 | [PROTECT](#policy-PROTECT) | 0 | 0 |

### Face and modality crossover

| Subgroup | Tagged papers | Applicable policies / precedents | User input | Evidence flags |
| --- | --- | --- | --- | --- |
| still_image_face_detection | 13 | [FACE](#policy-FACE) | 13 | 0 |
| image_level_deepfake_localization | 4 | [FACE](#policy-FACE) | 4 | 0 |
| video_only_deepfake | 8 | [MODALITY](#policy-MODALITY) | 0 | 1 |
| frame_method_video_system_evaluation | 4 | [FACE](#policy-FACE), [MODALITY](#policy-MODALITY) | 1 | 3 |
| mixed_image_video | 3 | [FACE](#policy-FACE) | 3 | 3 |
| identity_authenticity_without_detection | 3 | [PROTECT](#policy-PROTECT) | 0 | 0 |
| facial_generative_editing | 11 | [EMBED](#policy-EMBED), [FACE](#policy-FACE), [HYBRID](#policy-HYBRID) | 10 | 1 |
| face_evaluation_unit_unverified | 41 | [FACE](#policy-FACE) | 41 | 41 |
| text_only | 3 | [MODALITY](#policy-MODALITY) | 0 | 0 |

### Manipulation, endpoint and contribution type

| Subgroup | Tagged papers | Applicable policies / precedents | User input | Evidence flags |
| --- | --- | --- | --- | --- |
| copy_move | 2 | [TRADITIONAL](#policy-TRADITIONAL) | 2 | 0 |
| splicing | 2 | [TRADITIONAL](#policy-TRADITIONAL) | 2 | 0 |
| classical_compositing | 2 | [TRADITIONAL](#policy-TRADITIONAL) | 2 | 0 |
| photoshop_style | 4 | [IMAGE](#policy-IMAGE), [TRADITIONAL](#policy-TRADITIONAL) | 2 | 2 |
| retouching | 0 | No established candidate; no new policy question | 0 | 0 |
| generative_inpainting_editing | 10 | [FACE](#policy-FACE), [HYBRID](#policy-HYBRID), [IMAGE](#policy-IMAGE), [PROTECT](#policy-PROTECT) | 7 | 1 |
| mixed_traditional_generative | 1 | [IMAGE](#policy-IMAGE) | 0 | 0 |
| mixed_benchmark_coverage | 2 | [IMAGE](#policy-IMAGE) | 0 | 0 |
| benchmark_generative_coverage_unverified | 4 | [IMAGE](#policy-IMAGE) | 0 | 4 |
| multimodal_image_forensics | 17 | [FACE](#policy-FACE), [IMAGE](#policy-IMAGE), [VERIFY](#policy-VERIFY) | 12 | 11 |
| scientific_biomedical | 1 | [IMAGE](#policy-IMAGE) | 0 | 1 |
| neural_rendering | 2 | [IMAGE](#policy-IMAGE) | 0 | 1 |
| analysis_or_benchmark | 23 | [FACE](#policy-FACE), [IMAGE](#policy-IMAGE), [MODALITY](#policy-MODALITY), [PROTECT](#policy-PROTECT), [VERIFY](#policy-VERIFY), [WM_EVAL](#policy-WM_EVAL) | 12 | 16 |
| attack_only | 15 | [EVASION](#policy-EVASION), [FACE](#policy-FACE), [WM_EVAL](#policy-WM_EVAL) | 2 | 5 |
| attack_plus_defense | 2 | [EVASION](#policy-EVASION), [WM_EVAL](#policy-WM_EVAL) | 0 | 1 |
| adversarial_training_detection | 4 | [FACE](#policy-FACE) | 4 | 3 |
| distortion_robustness | 7 | [FACE](#policy-FACE), [MODALITY](#policy-MODALITY) | 5 | 5 |
| possible_existing_exclusion_identity | 1 | [FACE](#policy-FACE) | 1 | 1 |
| training_aid_not_release_injection | 2 | [FACE](#policy-FACE) | 2 | 2 |
| image_quality_not_authenticity | 0 | No established candidate; no new policy question | 0 | 0 |
| human_perception_component | 1 | [MODALITY](#policy-MODALITY) | 0 | 1 |

### Boundaries not promoted to separate policy questions

- Face candidates without an established still-image, spatial-localization, mixed-modality or frame-system subgroup retain an explicit evaluation-unit evidence flag. They remain in the policy-conflict outcome because settling that rule is the first blocker; they are not silently assumed to satisfy the proposed image condition.
- Multimodality and scientific imagery are secondary tags. THEMIS still needs an actual generative-image forensic endpoint checked; specialized domain is not a reason to exclude it. MLLM reasoning is not automatically misinformation-only.
- Passive attribution includes model/source and training-image provenance. Copyright motivation alone is insufficient to exclude MCID; its legal labels versus actual visual-source recovery need paper-specific checking.
- No quality/aesthetic-only cluster or general human-perception policy question is created from the selected candidates. HICOM has a human-study component but a video/image evaluation question. Existing Organic or Diffused and perception benchmarks show that controlled forensic discrimination can qualify without a new detector.
- Analysis type is not automatic admission. Current context-only exceptions include TWIGMA and the AI-label user study, while a GPT-Image-2 Twitter collection and platform-engagement studies are excluded for lacking forensic evaluation. These historical exceptions do not establish a general governance-infrastructure rule; the selected Position paper concerns foundation-model data governance rather than an evaluated image-forensic task.
- Training-data fingerprints used to teach a passive detector (FingerprintNet) differ from signatures injected into released model outputs (Artificial fingerprinting). Sequential image edits and diffusion timesteps differ from temporal video intervals.
- A candidate title/version may match an existing exclusion (Forensics Adapter). This is a flagged future identity check, not a restoration or modification of the original 215-row population.

## Integrity and reproducibility

The [pre-task SHA-256 baseline](../data/processed/systematic_tier2_policy_2026_09/baseline_sha256.json) covers pre-existing nonignored repository files outside this new Tier 2 layer. It protects the current 636-paper corpus, taxonomy, exclusions, institutions, affiliations, locations, hierarchy, public JSON, frontend, Tier 1 artifacts and historical audit. Hash verification and validation results are recorded separately so this policy report remains deterministic.

Reproduce from the repository root:

```sh
python3 scripts/prepare_systematic_tier2_policy.py
python3 scripts/report_systematic_tier2_policy.py --check --verify-integrity
python3 scripts/report_systematic_tier2_policy.py --output-dir /tmp/tier2-policy-reproduction
/usr/bin/python3 -m pytest -q tests/test_systematic_tier2_policy.py
git diff --check
```

`--output-dir` regenerates only the derived report and summary in a separate directory. `--write` explicitly writes the derived report and summary to their canonical paths. Neither mode writes either manual registry or any corpus file. Manual policy recommendations are never recomputed from keywords.

See [validation results](../data/processed/systematic_tier2_policy_2026_09/validation.json) and [full-suite output](../data/processed/systematic_tier2_policy_2026_09/full_suite.txt). Approval and actual reconciliation are future layers. No policy is applied here.
