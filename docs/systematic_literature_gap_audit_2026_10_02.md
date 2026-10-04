# Systematic literature gap audit — 2026-10-02

Started 2 October; completed 3 October 2026 (Asia/Shanghai). Continuation of the interrupted audit, preserving its paths and captures. **Audit only: no additions or metadata updates applied.**

## 1. Executive summary

**12 high-confidence proposed additions (Set A), 11 maintainer decisions (Set B), and 12 separate metadata updates.** The work ledger contains 263 ordinary adjudications plus one frozen MIRROR reference encountered during deduplication. Four inaccessible-primary leads are quarantined outside both actionable sets.

The public baseline remains **623 papers, 1,392 paper–institution relationships, 514 formally published papers, and 602 mapped papers**. All 105 established protected corpus checksums match. An unrelated committed homepage-branding change since the initial baseline is documented rather than reverted.

## 2. Scope and methodology

Include passive forensic detection, source-generator/model identification and generative-region localization in images. Standalone datasets, benchmarks, surveys and forensic analyses qualify. Exclude active watermark/fingerprint embedding, source-training-data attribution, generic model explanations, text/audio/video-only tasks, face-only work, classical manipulation without substantive generative evaluation, and image-quality defect diagnosis without an authenticity task.

The continuation used the saved ICML screen, ten partial identity-check records, primary metadata and source captures. It did not repeat the general crawl. The original interrupted files are retained. Remaining retrieval concentrated on source/version evidence, BPL and AdaParse full papers, ViGText experiments, and the already surfaced journal leads.

Deduplication checks DOI, version-stripped arXiv ID, normalized title, paper/source ID, method acronym, the three closest title strings, and author overlap within one year. All curated/manual CSV identity, version and exclusion layers are inspected. Name order/accents are normalized for suggestions only; authors and institutions are never merged. Missing IDs are marked unavailable, not interpreted as evidence of absence. Fuzzy/acronym/author overlap never establishes identity on its own. Every Set A record includes reviewed suggestions and a written conclusion.

Formal versions are folded into one work and reported as metadata updates when already present. `DUPLICATE_VERSION = 0` means no extra standalone version rows remain in this work-level ledger; it does not mean the sources contain no repeated versions. Unresolved potential extensions remain `AMBIGUOUS_IDENTITY` and are not silently merged.

Taxonomy proposals use existing root tasks and research types; `analysis_study` is displayed as analysis. Core image scopes are `fully_generated` and `generative_editing`; ViGText also retains a `deepfake` scope label. Empty scope arrays on uncertain items are intentional. All proposed labels retain `manual_review: true`.

## 3. Sources and bounded coverage

**84 saved query strings in 42 search captures; 728 returned search-result occurrences screened by title/identifier, plus 157 ICML gate records = 885 raw discovery records inspected.** Duplicates across queries are retained in this raw count. The complete ICML index contains 6,552 automatically enumerated titles; that number is not a full-paper review count.

**263 unique work candidates received final ordinary statuses.** The unresolved Tasnim arXiv/SSRN family is counted as one decision unit pending identity confirmation, not as a confirmed merge or two additions. These include 137 ICML exclusions, largely based on official titles. Existing-current records receive identity reconciliation, not an automatic claim of renewed full-text review. Primary abstract, programme, full-paper and failed-retrieval checks are distinguished per evidence record. One additional frozen work was referenced indirectly, making 264 distinct work references including the frozen exception.

The 515 unpromoted search occurrences are explicitly marked `discovery_only_not_promoted` in `discovery_records.json`; they include non-paper pages, irrelevant hits, snippets and leads without completed work-level adjudication. They are not counted as reviewed unique works or silently declared absent. Consequently, this is a completed bounded gap audit, not a claim of exhaustive literature coverage.

| Venue/source family | Search and evidence | Outcome / limits |
| --- | --- | --- |
| ICML 2026 | Official PMLR volume 306; 6,552 index titles enumerated, 157 keyword-gated titles inspected, plus one separately discovered position paper. Relevant primary pages checked. Evidence: `icml2026_screening.json; p03–p06, p11, p13; sources/701210428e9ea6004049.gz`. | 5 additions, 5 scope reviews, 11 metadata updates, 137 title/full-paper exclusions. This is a broad title gate, not an abstract census of all 6,552 papers. |
| CVPR / ICCV / ECCV / WACV | 2024–2026 venue-keyword checks, emphasizing source attribution, partial generation and localization; CVF/ECVA official links. Evidence: `search1, s02, s30–s33; p03`. | Known attribution/localization records repeatedly reconciled; SAFE challenge already present. ECCV 2026 full index captured but not re-screened; no claim of a complete ECCV census. |
| ICLR / NeurIPS | 2024–2025 proceedings queries plus 2026 ICLR forensic leads; title/identity checks against prior review. Evidence: `search1, s34–s37, s39, s42`. | Known ICLR forensic works already present. Training-data attribution rejected as wrong meaning of attribution. Frozen NeurIPS 2026 migration excluded; no official-metadata recheck performed. |
| ACM Multimedia | 2024–2026 publisher-keyword checks and official 2026 programme retrieval. Evidence: `s06, s09, s26; p08`. | 2026 programme returned an unusable verification shell. AGIDefect-4K verified through arXiv and excluded as perceptual-defect quality diagnosis. No proceedings-completeness claim. |
| WIFS / ICIP / MMSP | 2024–2026 keyword/category searches, with older attribution references inspected selectively. Evidence: `s03, s07, s10, s11, s19, s39`. | Known WIFS resynthesis and attribution works reconciled. No newly verified in-scope addition from these targeted checks; sparse primary retrieval leaves uncertainty, especially MMSP/ICIP. |
| ICASSP | 2024–2026 keyword checks, exact-title follow-up, official 2026 programme and arXiv. Evidence: `s03, s18; p01, p07; official PaperNum=13550 source capture`. | Beyond Spectral Peaks is a verified missing ICASSP 2026 work, Information Forensics and Security track. DOI remains unverified. |
| TIFS / TIP / TMM / SPL | Publisher-focused 2024–2026 forensic terms, source identification and exact-title follow-ups. Evidence: `s04, s16, s17, s38, s41; p03, p11–p15; adaparse_pdf_text.json`. | AdaParse requires taxonomy decision. Several TMM/SPL hits already represented. Spectral Forensics remains quarantined because primary retrieval failed. TIP query yielded no verified new gap; not an exhaustive negative finding. |
| Pattern Recognition / PR Letters / Information Fusion / Signal Processing: Image Communication | 2024–2026 publisher and venue-keyword searches. Evidence: `s05, s07, s15, s29`. | Existing HRR and other records reconciled. Search noise from face-only, classical CGI, video and unrelated fusion work limits negative conclusions. |
| CVIU / IJCV; adjacent journals | CVIU/IJCV 2024–2026 keyword searches, plus journal/survey leads surfaced by the same queries. Evidence: `s06, s09, s27, s38, s39; p02, p09, p11, p15`. | CJIG survey verified missing. Proto-LeakNet, BM-DDFN and SCA-Det quarantined pending accessible primary evidence. No inference of a new gap from an inaccessible publisher snippet. |
| USENIX Security / IEEE S&P / CCS / NDSS | 2024–2026 targeted synthetic-image security searches; official NDSS/USENIX primary follow-ups. Evidence: `s08, s12–s14; p07, p08, p12–p14`. | ViGText verified missing with independent general-image experiments; Chimera scope decision remains. S&P/CCS queries did not establish additional gaps; generic AI security and watermark work excluded. |
| Attribution / localization / challenge / survey families | Source-model, hierarchical/open-set, diffusion attribution, passive provenance, local/partial generation, benchmarks and reviews. Evidence: `s20–s28, s40–s42; p01, p02, p07, p09`. | Few-shot attribution and EditTrack verified; two DLMMDD participant reports reserved for publication-type decisions. MediaEval 2025 is an independently documented benchmark overview; the Kaggle competition itself is not a paper. |
| Adjacent primary leads | IJCAI official proceedings and MICCAI official accepted-paper page. Evidence: `p09, p13, p14`. | IJCAI missing DOI/proceedings link is metadata only. MICCAI author-page inconsistency reserved for review; no guessed DOI. |

Every saved search capture contains the actual queries and response. `source_manifest.json` preserves retrieval timestamps, HTTP/network outcomes and SHA-256 hashes of original response bytes. HTTP 200 is not treated as proof of useful content: ACM MM and direct MICCAI responses contain verification shells; MICCAI substantive evidence comes from the separately saved web-reader response.

## 4. Reconciliation

| Status | Count |
| --- | ---: |
| `EXISTING_CURRENT` | 84 |
| `EXISTING_METADATA_UPDATE` | 12 |
| `MISSING_HIGH_CONFIDENCE` | 12 |
| `MISSING_NEEDS_SCOPE_REVIEW` | 9 |
| `DUPLICATE_VERSION` | 0 |
| `EXCLUDE_OUT_OF_SCOPE` | 140 |
| `AMBIGUOUS` | 6 |
| **Ordinary work total** | **263** |
| `EXISTING_PENDING_FROZEN_NEURIPS_2026` | 1 |
| **Including frozen reference** | **264** |

Set B contains nine scope-review works and two ambiguous works (Tasnim identity family and MICCAI metadata/scope). The remaining four ambiguous works are evidence holds outside the actionable sets.

| Set A task membership | Count |
| --- | ---: |
| Detection | 11 |
| Source attribution | 2 |
| Localization | 2 |

| Set A research-type membership | Count |
| --- | ---: |
| Method | 10 |
| Dataset | 1 |
| Benchmark | 2 |
| Survey | 1 |
| Analysis (`analysis_study`) | 1 |

Counts are non-exclusive memberships: both tables sum to 15 memberships across 12 works. DNA contributes method/dataset/benchmark; Beyond Spectral Peaks contributes method/analysis. EditTrack and the contrastive few-shot work contribute detection/attribution; MediaEval contributes detection/localization. Set A years: 2025 = 3; 2026 = 9; no newly verified 2024 addition in this bounded sample.

## 5. Set A — high-confidence proposed additions

All twelve are absent from the public corpus by every available exact identifier/title check. All are proposals requiring later curation, not imports. Unknown formal DOIs and unverified tracks are left blank.

### A01. Where Detectors Fail: Probing Generative Space for Generalizable AI-Generated Image Detection

- **Authors, in source order:** Zijie Cao; Weijie Tu; Yao Xiao; Weijian Deng; Weiyan Chen; Liang Lin; Pengxu Wei.
- **Publication:** ICML, 2026.
- **Tasks / types:** detection / method.
- **Evidence:** [primary source](https://proceedings.mlr.press/v306/cao26s.html); [arXiv 2605.24906](https://arxiv.org/abs/2605.24906); formal DOI not verified.
- **Scope:** Explores hard regions of generator space to train generalizable synthetic-image detectors.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “Reduce the Artifact Bias for More Generalizable AI-Generated Image Detection” (similarity 0.7211); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded. Same-group SACG work uses post-hoc confidence calibration; PROBE trains through generator-space exploration. Distinct work identities.
- **Confidence:** high. Ledger key: `gap-e1c1b108b05d`.
- **Version note:** PMLR includes Weiyan Chen in fifth position; saved arXiv 2605.24906 lists six authors without Chen. Preserve both version author lists and use PMLR order for the formal record.

### A02. DNA: Uncovering Universal Latent Forgery Knowledge

- **Authors, in source order:** Jingtong Dou; Chuancheng Shi; Anqi Yi; Shiming Guo; Wenhua Wu; Yemin Wang; Li Zhang; Fei Shen; Tat-Seng Chua.
- **Publication:** ICML, 2026.
- **Tasks / types:** detection / method, dataset, benchmark.
- **Evidence:** [primary source](https://proceedings.mlr.press/v306/dou26b.html); [arXiv 2601.22515](https://arxiv.org/abs/2601.22515); formal DOI not verified.
- **Scope:** Passive pretrained-unit forensics plus a new high-fidelity synthetic image benchmark HIFI-Gen.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “Towards Generalizable Detector for Generated Image” (similarity 0.4494); not an identity match. Acronym collision with DNA: Dual-Stage Native Attribution for Generated Image Source Tracing (curated:0b6c1b00c1b39838db42). Different full title, authors, arXiv ID and forensic task; no identity merge.
- **Confidence:** high. Ledger key: `gap-847aa30be0f5`.
- **Version note:** PMLR and arXiv 2601.22515 have different author ordering; preserve both and use PMLR order for the formal record.

### A03. Deep Residual Injection for Full-Spectrum Forensic Signal Perception in Multimodal Large Language Models

- **Authors, in source order:** Kaiqing Lin; Zhiyuan Yan; Ruoxin Chen; Ke-Yue Zhang; Yue Zhou; Caiyong Piao; Bin Li; Taiping Yao; Bo Wang; Youchang Xiao; Shouhong Ding.
- **Publication:** ICML, 2026.
- **Tasks / types:** detection / method.
- **Evidence:** [primary source](https://proceedings.mlr.press/v306/lin26an.html); [arXiv 2606.15880](https://arxiv.org/abs/2606.15880); formal DOI not verified.
- **Scope:** Residual injection learns generator artifacts for standalone synthetic-image authenticity detection.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “FakeShield: Explainable Image Forgery Detection and Localization via Multi-Modal Large Language Models” (similarity 0.5556); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded. Same-group Forensic-Chat (2509.25502) and AlignGemini (2512.06746) have distinct methods, titles and manuscripts: conversational artifact perception and two-branch task-model specialization, versus intermediate residual injection. MIRROR is frozen and is not reopened.
- **Confidence:** high. Ledger key: `gap-9e3410359ab4`.

### A04. RA-Det: Towards Universal Detection of AI-Generated Images via Robustness Asymmetry

- **Authors, in source order:** Xinchang Wang; Yunhao Chen; Yuechen Zhang; Congcong Bian; Zihao Guo; Xingjun Ma; Hui Li.
- **Publication:** ICML, 2026.
- **Tasks / types:** detection / method.
- **Evidence:** [primary source](https://proceedings.mlr.press/v306/wang26ad.html); [arXiv 2603.01544](https://arxiv.org/abs/2603.01544); formal DOI not verified.
- **Scope:** Perturbation-induced feature drift detects images from fourteen generative models; no embedding or watermark.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “Training-Free Detection of AI-Generated Images via Cropping Robustness” (similarity 0.6970); not an identity match. Historical row data/manual/key_papers_enriched.csv:86 contains RA-Det only as a rejected low-similarity search suggestion for the distinct DRCT work (2024). It is neither an accepted RA-Det identity nor an exclusion. Author/year/title comparisons do not establish a duplicate.
- **Confidence:** high. Ledger key: `gap-923484c8a9ee`.
- **Version note:** PMLR and arXiv report different improvement figures (12.92% and 7.81%). Do not blend results across versions; this audit imports neither result.

### A05. Order within Chaos: Capturing Intrinsic Energy Anomalies for AI-Manipulated Image Forgery Localization

- **Authors, in source order:** Yiming Wang; Baiqi Wu; Qingming Li; Jiahao Chen; Tong Zhang; Shouling Ji.
- **Publication:** ICML, 2026.
- **Tasks / types:** localization / method.
- **Evidence:** [primary source](https://proceedings.mlr.press/v306/wang26iy.html); [arXiv 2606.02178](https://arxiv.org/abs/2606.02178); formal DOI not verified.
- **Scope:** Pixel-level masks explicitly localize diffusion-generated editing regions. EditStream is a synthesis pipeline; no unsupported standalone dataset label.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “Detective SAM: Adaptive AI-Image Forgery Localization” (similarity 0.5185); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded.
- **Confidence:** high. Ledger key: `gap-ae64f73095cc`.

### A06. Supervised Contrastive Learning for Few-Shot AI-Generated Image Detection and Attribution

- **Authors, in source order:** Jaime Álvarez Urueña; David Camacho; Javier Huertas Tato.
- **Publication:** arXiv, 2025.
- **Tasks / types:** detection, source_attribution / method.
- **Evidence:** [primary source](https://arxiv.org/abs/2511.16541); formal DOI not verified.
- **Scope:** A standalone image detector with explicit open-set source attribution AUC and OSCR evaluations; passive learned embeddings.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “Incremental Learning for AI-Generated Image Detection” (similarity 0.6560); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded.
- **Confidence:** high. Ledger key: `gap-c20ac70e43cc`.

### A07. Learning Continuous Source Responses For Generalizable AI-Generated Image Detection

- **Authors, in source order:** Manni Cui; Ruiqi Liu; Zijian Yu; Hao Tan; Zibo Wei; Zian Wang; Ziheng Qin; Huijia Zhu; Weiqiang Wang; Jun Lan; Shu Wu.
- **Publication:** arXiv, 2026.
- **Tasks / types:** detection / method.
- **Evidence:** [primary source](https://arxiv.org/abs/2609.14316); formal DOI not verified.
- **Scope:** Continuous source-response regression improves binary image authenticity classification; it does not output generator identities.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “All-Around Forgery Clues for Generalizable AI-Generated Image Detection” (similarity 0.7647); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded. GlobalForge (2607.14684) uses local-information bottlenecks/global structural reasoning, versus continuous mixing-ratio regression here. MIRROR remains frozen.
- **Confidence:** high. Ledger key: `gap-7ac7fada32cf`.

### A08. Beyond Spectral Peaks: Interpreting the Cues Behind Synthetic Image Detection

- **Authors, in source order:** Sara Mandelli; Diego Vila-Portela; David Vázquez-Padín; Paolo Bestagini; Fernando Pérez-González.
- **Publication:** ICASSP, 2026. Track: Information Forensics and Security; IFS-P18.6 poster.
- **Tasks / types:** detection / method, analysis_study.
- **Evidence:** [primary source](https://www.cmsworkshops.com/ICASSP2026/view_paper.php?PaperNum=13550&bare=1); [arXiv 2510.05633](https://arxiv.org/abs/2510.05633); formal DOI not verified.
- **Scope:** Direct analysis of spectral cues used by synthetic-image detectors, with an interpretable linear detector.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “LEGION: Learning to Ground and Explain for Synthetic Image Detection” (similarity 0.5920); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded.
- **Confidence:** high. Ledger key: `gap-6052b6ee0021`.

### A09. EditTrack: Detecting and Attributing AI-assisted Image Editing

- **Authors, in source order:** Zhengyuan Jiang; Yuyang Zhang; Moyang Guo; Neil Zhenqiang Gong.
- **Publication:** arXiv, 2025.
- **Tasks / types:** detection, source_attribution / method.
- **Evidence:** [primary source](https://arxiv.org/abs/2510.01173); formal DOI not verified.
- **Scope:** Given base and suspicious images, identifies AI edits and the editing model using five models and six image datasets; no injected watermark.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “Detecting Origin Attribution for Text-to-Image Diffusion Models” (similarity 0.5688); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded.
- **Confidence:** high. Ledger key: `gap-3d4856c630d6`.
- **Publication note:** OpenReview submission found, but acceptance not verified; retain preprint venue.

### A10. A comprehensive survey on visual forensics for AI-Generated image detection

- **Authors, in source order:** Li JiaYe; Zhang MinQing; Huang SiYuan; Feng Pei; Liu Lang.
- **Publication:** Journal of Image and Graphics, 2026.
- **Tasks / types:** detection / survey.
- **Evidence:** [primary source](https://www.cjig.cn/en/article/doi/10.11834/jig.250624/); DOI `10.11834/jig.250624`.
- **Scope:** Survey centrally reviews visual forensic detection of GAN/diffusion-generated images; online-first publisher DOI establishes identity.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “Rethinking the Use of Vision Transformers for AI-Generated Image Detection” (similarity 0.6822); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded.
- **Confidence:** high. Ledger key: `gap-844d4535b37b`.
- **Publication note:** Online first 27 January 2026, pages 1–26; preserve publisher author rendering.

### A11. Synthetic Images at MediaEval 2025: Advancing detection of generative AI in real-world online images

- **Authors, in source order:** Olga Papadopoulou; Manos Schinas; Riccardo Corvi; Dimitrios Karageorgiou; Christos Koutlis; Fabrizio Guillaro; Efstratios Gavves; Hannes Mareen; Luisa Verdoliva; Symeon Papadopoulos.
- **Publication:** MediaEval 2025 Workshop, 2025.
- **Tasks / types:** detection, localization / benchmark.
- **Evidence:** [primary source](https://2025.multimediaeval.com/paper47.pdf); formal DOI not verified.
- **Scope:** Official scholarly task-overview paper specifies generated-image detection and AI-edit mask localization protocols. Not a Kaggle page or a duplicate of component datasets SAGI/TGIF.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “Online Detection of AI-Generated Images” (similarity 0.5042); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded.
- **Confidence:** high. Ledger key: `gap-ff14127991ec`.

### A12. ViGText: Deepfake Image Detection with Vision-Language Model Explanations and Graph Neural Networks

- **Authors, in source order:** Ahmad ALBarqawi; Mahmoud Nazzal; Issa Khalil; Abdallah Khreishah; NhatHai Phan.
- **Publication:** NDSS, 2026.
- **Tasks / types:** detection / method.
- **Evidence:** [primary source](https://www.ndss-symposium.org/ndss-paper/vigtext-deepfake-image-detection-with-vision-language-model-explanations-and-graph-neural-networks/); DOI `10.14722/ndss.2026.230303`.
- **Scope:** Independent general-image diffusion-detection experiments satisfy scope despite additional face-robustness evaluations.
- **Deduplication:** No exact public DOI/arXiv/title/paper-ID match. Nearest title: “A Deepfake Image Detection Method Based on a Multi-Graph Attention Network” (similarity 0.5772); not an identity match. Top three title suggestions and author/year overlaps reviewed; no evidence of a renamed version among those suggestions. Missing external identifiers are explicitly recorded.
- **Confidence:** high. Ledger key: `gap-fb883d3f464b`.

## 6. Set B — maintainer decision required

Each item has captured primary or official author evidence, but a precise scope, publication-type or identity decision remains. No review item is counted as a high-confidence addition.

### B01. Can We Build a Monolithic Model for Fake Image Detection? SICA: Semantic-Induced Constrained Adaptation for Unified-Yet-Discriminative Artifact Feature Space Reconstruction

**MISSING_NEEDS_SCOPE_REVIEW** · ICML, 2026 · provisional tasks: detection; types: method.

Authors: Bo Du; Xiaochen Ma; Xuekang Zhu; Zhe Yang; Chaoqun Niu; Jian Liu; Ji-Zhe Zhou.

[Primary evidence](https://proceedings.mlr.press/v306/du26g.html). Official abstract establishes image forensics but does not resolve the narrowed synthetic-image boundary.

**Decision:** Decide whether OpenMMSec provides a substantive, independently evaluated generated-image subset within its four forensic subdomains; retain detection only if that subset satisfies the narrowed scope.

Deduplication: no exact public identity match; full seven-check results in `gap-597b9e58e04b`. Confidence: medium; no identity merge authorized.

### B02. Divide and Conquer: Reliable Multi-View Evidential Learning for Deepfake Detection

**MISSING_NEEDS_SCOPE_REVIEW** · ICML, 2026 · provisional tasks: detection; types: method.

Authors: Xiaolu Kang; Zhongyuan Wang; Jikang Cheng; Baojin Huang; Zhanhe Lei; Gang Wu; Qin Zou; Qian Wang.

[Primary evidence](https://proceedings.mlr.press/v306/kang26o.html). Official abstract establishes image forensics but does not resolve the narrowed synthetic-image boundary.

**Decision:** Decide inclusion only after identifying an independent general synthetic-image evaluation beyond face/video benchmarks; the official abstract does not name its benchmark datasets.

Deduplication: no exact public identity match; full seven-check results in `gap-475047af959c`. Confidence: medium; no identity merge authorized.

### B03. PRPO: Paragraph-level Policy Optimization for Vision-Language Deepfake Detection

**MISSING_NEEDS_SCOPE_REVIEW** · ICML, 2026 · provisional tasks: detection; types: method.

Authors: Tuan Nguyen; Naseem Khan; Khang Tran; Hai Phan; Issa Khalil.

[Primary evidence](https://proceedings.mlr.press/v306/nguyen26f.html). Official abstract establishes image forensics but does not resolve the narrowed synthetic-image boundary.

**Decision:** Decide whether the reasoning-annotated dataset and reported image results independently cover general generated images rather than only face/deepfake-video frames.

Deduplication: no exact public identity match; full seven-check results in `gap-97036bf7d3f3`. Confidence: medium; no identity merge authorized.

### B04. OmniVL-Guard: Towards Unified Vision-Language Forgery Detection and Grounding via Balanced RL

**MISSING_NEEDS_SCOPE_REVIEW** · ICML, 2026 · provisional tasks: detection, localization; types: method.

Authors: Jinjie Shen; Jing Wu; Yaxiong Wang; Lechao Cheng; Shengeng Tang; Tianrui Hui; Nan Pu; Zhun Zhong.

[Primary evidence](https://proceedings.mlr.press/v306/shen26u.html). Official abstract establishes image forensics but does not resolve the narrowed synthetic-image boundary.

**Decision:** Decide whether its interleaved image/text/video benchmark contains an independent generative-image detection or mask-localization contribution; misinformation grounding alone is insufficient.

Deduplication: no exact public identity match; full seven-check results in `gap-44d3346b0c68`. Confidence: medium; no identity merge authorized.

### B05. Forensic Prompting with Dual-Action Policy Optimization for Vision-Language Forgery Detection and Localization

**MISSING_NEEDS_SCOPE_REVIEW** · ICML, 2026 · provisional tasks: detection, localization; types: method.

Authors: Ye Zhu; Ai Zhao; Jinwei Wang.

[Primary evidence](https://proceedings.mlr.press/v306/zhu26bg.html). Official abstract establishes image forensics but does not resolve the narrowed synthetic-image boundary.

**Decision:** Decide whether diffusion-content experiments independently evaluate generative-region masks and make a central contribution; otherwise retain exclusion of generic manipulation localization.

Deduplication: no exact public identity match; full seven-check results in `gap-95d61d3debba`. Confidence: medium; no identity merge authorized.

### B06. A Multi-View and Confusion-Guided Ensemble Framework for Robust Synthetic Image Attribution

**MISSING_NEEDS_SCOPE_REVIEW** · arXiv, 2026 · provisional tasks: source_attribution; types: method.

Authors: Zuomin Qu.

[Primary evidence](https://arxiv.org/abs/2609.11188). Standalone arXiv method report on the DLMMDD generator-attribution challenge; conference proceedings identity not verified.

**Decision:** Decide whether this participant method report warrants its own scholarly work record, distinct from the challenge overview and other teams; if accepted, use arXiv 2026 until official workshop publication is verified.

Deduplication: no exact public identity match; full seven-check results in `gap-244d54f4c08b`. Confidence: medium; no identity merge authorized.

### B07. Hybrid Semantic and Spectral Ensemble for Robust Synthetic Image Source Attribution

**MISSING_NEEDS_SCOPE_REVIEW** · arXiv, 2026 · provisional tasks: source_attribution; types: method.

Authors: Md. Ajwad Hossain.

[Primary evidence](https://arxiv.org/abs/2607.22808). Independent passive attribution ensemble evaluated on ten source generators; workshop acceptance is an author claim, not a verified proceedings identity.

**Decision:** Decide whether this challenge participant report qualifies as a standalone method contribution; preserve it separately from Qu’s report and do not claim a formal ICANN workshop publication without its official record.

Deduplication: no exact public identity match; full seven-check results in `gap-6f54ea382cde`. Confidence: medium; no identity merge authorized.

### B08. AI-Generated Image Detection: An Empirical Study and Future Research Directions

**AMBIGUOUS** · arXiv, 2025 · provisional tasks: detection; types: benchmark, analysis_study.

Authors: Nusrat Tasnim; Kutub Uddin; Khalid Mahmood Malik.

[Primary evidence](https://arxiv.org/abs/2511.02791). Image-specific benchmarking is clear; a later SSRN title by the same authors may be an extension or replacement.

**Decision:** Resolve whether SSRN 6032054 is a renamed/extended version of arXiv 2511.02791 before creating any identity; do not automatically merge or count them twice.

Deduplication: no exact public identity match; full seven-check results in `gap-d59604897b0c`. Confidence: medium; no identity merge authorized.

### B09. AdaParse: Personalized Fingerprinting for Visual Generative Model Reverse Engineering

**MISSING_NEEDS_SCOPE_REVIEW** · IEEE Transactions on Information Forensics and Security, 2026 · provisional tasks: source_attribution; types: method.

Authors: Yu Zheng; Zhuoxun Li; Bingyao Yu; Jie Zhou; Jiwen Lu.

[Primary evidence](https://github.com/lizhuoxun/AdaParse). Passive extraction of hyperparameter-specific traces, evaluated on 123/124-model benchmark; no generator watermark insertion.

**Decision:** Decide whether passive prediction of generator architecture/loss hyperparameters qualifies as source attribution under the map taxonomy; do not label it active fingerprint embedding. Verify publisher metadata before formal import.

Deduplication: no exact public identity match; full seven-check results in `gap-d5c62e3fe662`. Confidence: medium; no identity merge authorized.

TIFS acceptance reported on official author repository; publisher endpoint 11422036 inaccessible, DOI not verified.

### B10. Beyond Visual Forensics: Auditing Multimodal Robustness for Synthetic Medical Image Detection

**AMBIGUOUS** · MICCAI, 2026 · provisional tasks: detection; types: benchmark, analysis_study.

Authors: Ching-Hao Chiu; Hao-Wei Chung; Gelei Xu; Xueyang Li; Pin-Yu Chen; John Kheir; Meysam Ghaffari; Carlos Morato; Ahmed Abbasi; Yiyu Shi.

[Primary evidence](https://papers.miccai.org/miccai-2026/0103-Paper2865.html). Synthetic medical-image authenticity benchmark with record-context intervention; author-page inconsistency needs resolution.

**Decision:** Confirm the author list against the accepted paper because the official page header conflicts with Author(s)/BibTeX; then decide whether image-plus-record robustness remains a substantive image-forensic benchmark within scope.

Deduplication: no exact public identity match; full seven-check results in `gap-661e383aa4c7`. Confidence: medium; no identity merge authorized.

Author(s) and BibTeX agree on ten authors; page header separately displays Kitty K. Wong; main PDF fetch failed. DOI explicitly unavailable.

### B11. Chimera: Creating Digitally Signed Fake Photos by Fooling Image Recapture and Deepfake Detectors

**MISSING_NEEDS_SCOPE_REVIEW** · USENIX Security, 2025 · provisional tasks: detection; types: method.

Authors: Seongbin Park; Alexander Vilesov; Jinghuai Zhang; Hossein Khalili; Yuan Tian; Achuta Kadambi; Nader Sehatbakhsh.

[Primary evidence](https://www.usenix.org/conference/usenixsecurity25/presentation/park). Official security paper attacks signed-camera provenance and deepfake/recapture detectors; passive general-image component needs separation.

**Decision:** Decide whether the general synthetic-image detector-evasion experiments are independently substantive enough to include, despite the central signed-camera provenance bypass objective; exclude if only active-provenance circumvention remains.

Deduplication: no exact public identity match; full seven-check results in `gap-f6ee3e8afe33`. Confidence: medium; no identity merge authorized.

## 7. Existing metadata updates — separate from additions

Twelve existing identities need bibliographic enrichment. Three are genuine arXiv-only → ICML upgrades; eight other ICML records already have formal conference status and need the final PMLR citation/link. The IJCAI record already has formal status and needs its DOI/link. None increases the work count.

| Existing work / evidence | Exact proposed change | Identity retained |
| --- | --- | --- |
| [OmniAID: Decoupling Semantics and Artifacts for Universal AI-Generated Image Detection in the Wild](https://proceedings.mlr.press/v306/guo26ag.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Upgrade arXiv-only record to ICML 2026 formal publication; retain original arXiv year. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/guo26ag.html", "proceedings_identity": "pmlr-v306-guo26ag", "pages": "38614-38641", "venue": "International Conference on Machine Learning", "publication_type": "conference", "year": 2026}` | `curated:d8667aa1db5ef69d199a` |
| [Dissect and Prune: Enhancing Robustness in AI-Generated Image Detection](https://proceedings.mlr.press/v306/kim26k.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/kim26k.html", "proceedings_identity": "pmlr-v306-kim26k", "pages": "57385-57410"}` | `curated:c87f234ea256991903e1` |
| [TranX-Adapter: Bridging Artifacts and Semantics within MLLMs for Robust AI-generated Image Detection](https://proceedings.mlr.press/v306/wang26cj.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Upgrade arXiv-only record to ICML 2026 formal publication; retain original arXiv year. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/wang26cj.html", "proceedings_identity": "pmlr-v306-wang26cj", "pages": "127025-127039", "venue": "International Conference on Machine Learning", "publication_type": "conference", "year": 2026}` | `curated:3514b00c17a56ec752cd` |
| [Fleet: Few Shots Lead Effective AI-generated Image Detection](https://proceedings.mlr.press/v306/wang26eo.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Upgrade arXiv-only record to ICML 2026 formal publication; retain original arXiv year. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/wang26eo.html", "proceedings_identity": "pmlr-v306-wang26eo", "pages": "128302-128326", "venue": "International Conference on Machine Learning", "publication_type": "conference", "year": 2026}` | `curated:f8bc8386ea043eef0a7c` |
| [Breaking Manifold Continuity: Vector Quantized Modeling for Real-Centric Deepfake Detection](https://proceedings.mlr.press/v306/wang26it.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/wang26it.html", "proceedings_identity": "pmlr-v306-wang26it", "pages": "131124-131139"}` | `curated:7287cadbc4b8408fd16b` |
| [GenShield: Unified Detection and Artifact Correction for AI-Generated Images](https://proceedings.mlr.press/v306/xu26cl.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/xu26cl.html", "proceedings_identity": "pmlr-v306-xu26cl", "pages": "142838-142863"}` | `curated:d6fe2666a64b0c70ff6b` |
| [DGS-Net: Distillation-Guided Gradient Surgery for CLIP Fine-Tuning in AI-Generated Image Detection](https://proceedings.mlr.press/v306/yan26h.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Use the ordered author rendering in the official proceedings; retain previous version rendering in provenance. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/yan26h.html", "proceedings_identity": "pmlr-v306-yan26h", "pages": "143760-143774", "authors": ["Jiazhen Yan", "Ziqiang Li", "Fan Wang", "Boyu Wang", "Ziwen He", "Zhangjie Fu"]}` | `curated:7ed4e932c4dac57d0136` |
| [FiSeR: Fine-Grained Source Representations for Cross-Domain AI Image Detection](https://proceedings.mlr.press/v306/zhang26bi.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/zhang26bi.html", "proceedings_identity": "pmlr-v306-zhang26bi", "pages": "155726-155743"}` | `curated:f380c0d31081fc59f1eb` |
| [PGC: Peak-Guided Calibration for Generalizable AI-Generated Image Detection](https://proceedings.mlr.press/v306/zhou26h.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/zhou26h.html", "proceedings_identity": "pmlr-v306-zhou26h", "pages": "164828-164848"}` | `curated:a570863c3a6ac227b56c` |
| [ForensicConcept: Transferable Forensic Concepts for AIGI Detection](https://proceedings.mlr.press/v306/zhou26bt.html) | Add official PMLR proceedings landing page, volume 306, page range and proceedings identity; preserve arXiv and OpenReview links. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/zhou26bt.html", "proceedings_identity": "pmlr-v306-zhou26bt", "pages": "166559-166582"}` | `curated:078ade9edabe304013a7` |
| [Position: We need to re-think the concept of "real" images.](https://proceedings.mlr.press/v306/keuper26a.html) | Add official PMLR landing page, volume/pages and proceedings identity; retain existing OpenReview evidence. Proposed: `{"formal_url": "https://proceedings.mlr.press/v306/keuper26a.html", "proceedings_identity": "pmlr-v306-keuper26a", "pages": "170978-170988"}` | `curated:b45849aa3f89cc8b64ef` |
| [Fast and Generalizable AI-Generated Image Detection via Model-Agnostic Feature Reconstruction](https://www.ijcai.org/proceedings/2026/131) | Add missing formal DOI, official proceedings landing page, Main Track and pages; retain existing paper identity. Proposed: `{"doi": "10.24963/ijcai.2026/131", "formal_url": "https://www.ijcai.org/proceedings/2026/131", "pages": "1170–1178"}` | `curated:773aa77291d6869eaad8` |

Current values and proposed values are stored separately per record. PMLR pages were published in the volume on 29 September 2026, so their final citation information postdates the earlier September reconciliation. ArXiv DOIs must not be misrepresented as conference DOIs.

## 8. Frozen NeurIPS encounters

No frozen work was rediscovered as a candidate through the 42 saved search captures. **MIRROR (arXiv 2602.02222)** appeared as an author/year-overlap suggestion while comparing Deep-VRM and CuRe, and is explicitly recorded as `EXISTING_PENDING_FROZEN_NEURIPS_2026`. This is one indirect deduplication encounter, not a publication-metadata check. It is excluded from ordinary candidate and new-gap counts.

All eight records in the separately frozen 7+1 reconciliation remain protected. Their migration, identities, metadata, root-task policy and public gate are untouched. The existing MIRROR identity is not an addition.

**7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA**

## 9. Compact exclusions and evidence holds

| Exclusion reason | Works |
| --- | ---: |
| active_provenance | 37 |
| other_non_forensic | 49 |
| text_or_generic_ml | 30 |
| non_image_media | 15 |
| training_data_attribution | 6 |
| face_or_video_only | 2 |
| image_quality_not_forensics | 1 |

Examples that prevent recurrent false positives: BPL’s full paper evaluates Celeb-DF/DF40 and FF++/DFDC/DFDCP at video level; AGIDefect-4K localizes perceptual defects rather than forged origin; ICML memorized-region localization and GUDA attribute training influence; virtual-face TIVDiff embeds a watermark. Generic manipulation/omni-modal papers remain in Set B where the abstract does not resolve generative-image centrality.

Four **non-actionable evidence holds** remain `AMBIGUOUS`; these are not a third proposal set. Publisher URLs/DOIs from discovery are provisional identifiers until primary retrieval succeeds.

| Lead | Primary endpoint / unresolved requirement |
| --- | --- |
| BM-DDFN: Bilinear cross-domain modeling for AIGC image source attribution | [Endpoint](https://www.sciencedirect.com/science/article/abs/pii/S0950705126003953). Retrieve primary bibliographic/scope evidence; no addition proposed. |
| SCA-Det: A structure-context artifact detector for AI-generated image detection | [Endpoint](https://www.sciencedirect.com/science/article/pii/S0925231226010246). Retrieve primary bibliographic/scope evidence; no addition proposed. |
| Spectral Forensics: Detecting Diffusion-Generated Imagery via 1/f^β Power Law Violations | [Endpoint](https://doi.org/10.1109/LSP.2026.3672388). Retrieve primary bibliographic/scope evidence; no addition proposed. |
| Proto-LeakNet: Towards signal-leak aware attribution in synthetic human face imagery | [Endpoint](https://www.sciencedirect.com/science/article/pii/S1077314226002158). Retrieve primary bibliographic/scope evidence; no addition proposed. Also establish a substantive non-face image task before considering inclusion. |

## 10. Coverage observations

- **ICML 2026 has an identifiable ingestion gap:** five verified additions and three preprint-to-formal upgrades, plus five unresolved scope candidates. Eight further records already have ICML status but lack final proceedings citation data. This finding does not measure a recall rate for all ICML papers.
- **Source attribution remains a targeted gap:** two verified additions cover open-set/few-shot recognition and AI-editing model attribution. Two participant reports and AdaParse need explicit inclusion decisions; BM-DDFN remains an evidence hold. “Fingerprint” is interpreted by mechanism, not keyword.
- **Localization is smaller but undercovered in the inspected sample:** FLAME and the MediaEval benchmark add substantive generative-region evaluation. FPDA and OmniVL-Guard cannot be promoted from generic forgery/grounding wording alone. Perceptual explanations and defects are not counted as forensic masks.
- **Signal-processing coverage remains uncertain:** one verified ICASSP gap; existing TMM/SPL/WIFS identities account for many results. The TIFS hyperparameter-attribution boundary and blocked publisher pages prevent a strong completeness claim for TIFS/TIP/TMM/SPL/ICIP/MMSP.
- **Benchmark/report vocabulary causes misses:** the MediaEval overview does not use the conventional detection phrase in its title. Participant reports may describe genuine methods yet lack stable proceedings identities. They should not be auto-added because they have leaderboard numbers.
- **Many apparent gaps were existing identities:** 96 work-level leads reconcile to 84 current records plus 12 metadata updates. Only three metadata updates change preprint-only status; URL enrichment must not inflate a formal-publication migration count.
- **Year comparisons are bounded:** nine Set A works are dated 2026 and three 2025. The lack of a newly verified 2024 addition in these searches is not evidence of complete 2024 coverage. Search selection, prior curation and publisher access differ by year/venue.
- **Residual recall limits:** title-gated ICML screening can miss neutral titles; 515 discovery-only occurrences were not promoted to work-level review. No systematic forward-citation census was completed. ECCV/ACM MM programme limitations and inaccessible primary journal pages remain documented uncertainty.

## 11. Corpus integrity and validation

The validator checks all 4,147 files in the saved interrupted baseline, all 105 established corpus checksums, source-byte hashes, public counts, candidate identity uniqueness, DOI/arXiv/title duplicates, status reconciliation, primary evidence for actionable records, exact maintainer decisions, metadata deltas and frozen-work isolation.

| Protected public measure | Before | After |
| --- | ---: | ---: |
| Papers | 623 | 623 |
| Paper–institution relationships | 1,392 | 1,392 |
| Formally published | 514 | 514 |
| Mapped papers | 602 | 602 |

All 105 protected checksums match. No changes to curated/manual papers, taxonomy, exclusion decisions, institution mappings, coordinates, identities or public data exports. No backend or website runtime changes were made by this audit; the existing static deployment contract is unaffected. No export regeneration or broad frontend suite was needed.

The original baseline HEAD is `cfce65abe3465d6d5c1817912c865e4ea9fe2e61`; observed HEAD on resumption is `ecfde6b1fc459a748e34114634fbf21cb9286f65` (homepage branding). Five previously tracked UI/test files have different hashes, and that commit adds two branding assets. Those differences exactly match committed content and are itemized in `external_changes.json`. They are not audit edits and do not affect any of the 105 corpus checksums. The baseline was not rewritten to hide this difference.

Verification: `python3 -m unittest tests.test_audit_gap_2026_10_02` — 8 tests pass. `python3 scripts/audit_gap_2026_10_02.py validate` — pass, no candidate/schema/source errors or unexplained baseline differences. Full machine-readable results: `validation.json`.

## 12. Artifacts, Git state and next action

- `docs/systematic_literature_gap_audit_2026_10_02.md`: this report.
- `data/raw/systematic_gap_audit_2026_10_02/`: isolated raw source caches, search responses, preserved partial checks, final candidate/discovery ledger, source coverage, validation and external-change evidence. `README.md` describes the layers.
- `scripts/audit_gap_2026_10_02.py`: read-only comparison, isolated capture and validation helper.
- `tests/test_audit_gap_2026_10_02.py`: duplicate, frozen, evidence, decision and reconciliation guard tests.

All four paths are audit-generated and untracked. `git diff --stat` and `git diff --check` are empty because tracked files are unchanged in this worktree; the helper and tests are checked separately as untracked files. Nothing is staged. No commit or push was performed by this audit. The separate branding commit predates this final Git check.

**Next action:** review Set A identities/version notes, answer the eleven Set B decisions, and approve the separate twelve metadata deltas in a later curation task. Obtain accessible primary evidence for the four quarantined leads before promoting them. Keep the frozen NeurIPS migration separate.

**GAP AUDIT COMPLETE — READY FOR MAINTAINER REVIEW**

## 13. Approved successor migration — October 3

The preceding report and its counts describe the completed discovery audit before maintainer approval. The maintainer later approved 17 additions and 12 existing-identity metadata updates. These are applied without restarting discovery; the current public corpus has 640 papers and 617 mapped papers.

Original discovery statuses, counts, evidence and frozen encounters remain intact. The candidate ledger adds separate maintainer-decision and migration-outcome fields, and its complete original form is preserved in `data/raw/systematic_gap_migration_2026_10_03/discovery_snapshot.json`. Five former Set B works were approved; four were excluded under the narrow policy; DiCoME remains on a scope-evidence hold; the empirical-study identity remains ambiguous. The four evidence-insufficient leads remain holds.

The [migration report](systematic_literature_gap_migration_2026_10_03.md) supersedes only the pending next action above and records the full approved result, affiliation limitations, test results and current integrity classification. Historical audit receipts are not rewritten to pretend the intentional corpus migration left all 105 files unchanged.

**7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA**
