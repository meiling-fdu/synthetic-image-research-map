# Batch B Wave B1Q — Few-Patch Bias and Chameleon benchmark

Evidence-only review, 2026-10-26. Verified published baseline `dace181c2a9edbb7c467978e9e958e83fdddc143` in the existing isolated worktree. Only the original R026 and R253 research-type actions are reviewed. Scientific sufficiency and maintainer acceptance are separate: both actions remain open, no correction or terminal decision is applied, and all public data remain unchanged.

| Review | Current types | Provisional outcome | Proposed complete types | Contribution / operational confidence |
|---|---|---|---|---|
| R026 | `method` | `ANALYSIS_STUDY_ADDITION_SUPPORTED` | `method;analysis_study` | medium-high / low, unverified |
| R253 | `method;dataset` | `BENCHMARK_ADDITION_SUPPORTED` | `method;dataset;benchmark` | high / low, unverified |

Both current task sets remain `detection`, and both image scopes remain `fully_generated`. Patch supervision and heatmaps do not establish an independently evaluated localization task. Neither paper establishes a source-identity attribution task in this review. Existing method/dataset classifications are not reopened.

## Locked policy and original actions

R3: Assign analysis_study only when systematic empirical or theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps, or supporting interpretability figures do not qualify by themselves.

R2: Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

R026, `curated:386ccd052b812587c286`: verify whether the primary counterfactual/Few-Patch Bias investigation goes beyond ordinary ablations and supports analysis study. The original abstract-based `LIKELY_FIX` is an unresolved hypothesis, not prior acceptance.

R253, `curated:f9eac1aa13a606c6ec88`: verify whether Chameleon's challenging protocol and nine-detector comparison establish an independently reusable benchmark. Its difficult images and number of baselines alone do not settle R2. Exact original records, current authoritative snapshots and policy provenance are preserved in the manifest.

## Verified primary sources and version boundaries

| Review | Official source | Complete PDF | SHA-256 |
|---|---|---|---|
| R026 | [ICLR 2026 proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/file/c5ee2a08fbe743b171b0b4b2bdfd6f86-Paper-Conference.pdf) | 20 pages; 7,455,376 bytes | `49cd7cd8be5752f4c798a2454478dc080f029a4e534805b11d40e187c7c35005` |
| R253 | [ICLR 2025 proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/file/b0303773962ea1b5394c3a83cc7dd066-Paper-Conference.pdf) | 19 pages; 6,321,086 bytes | `f7657547faa18abed349e2bfc280cba433427040c00f5e4eaf19c3f25faa3244` |

R026's eleven official authors and printed byline are identity-matched. Earlier arXiv v1 metadata names Junchi Yan where the publisher lists Zequn Qin; the publisher describes Randomized Patch Reconstruction while inspected arXiv abstract metadata describes Random Patch Replacement. Only these observed metadata/abstract differences are established; neither alternate full body was retrieved or merged. Within the official PDF, Section 4's reconstruction description also differs from inverse replacement wording in Figure 5 and Appendix B. These are observations outside the bounded bibliography action; no author, venue or bibliography field changes.

R253's seven printed authors match the publisher listing, including **Ouxiang Li**. The suggested first-name discrepancy is not confirmed in the inspected sources. No author correction is proposed. ArXiv/publisher full-version equivalence remains unverified.

## R026: primary analysis, intervention limits and distinct method

Sections 3.1–3.2 (pp3–5), Figures 2–4 and Appendix C (pp15–20) investigate existing detectors before the PPL method: patch-local visual artifacts, random single-patch tiling, patch masking, signed-logit effects, spatial concentration and detector/generator variation. The two primary principles and Few-Patch Bias diagnosis are explicit contributions independent of Section 4. This meets R3 provisionally even though its strongest universal and mechanistic interpretations are not established.

The random-patch experiment reports 90% accuracy on the SDv1.4 GenImage subset (p3). It does not establish that every patch works for every detector or generator; exact diagnostic sample size, patch-size specification and uncertainty are incomplete. The introduction reports an 18.7% ±4.1% masking-related accuracy drop, while Figure 3(b) plots UnivFD recall, a median and an impact range for mask sizes 0/14/28/56/112. The estimator, percentage-point versus relative-percent interpretation, sample/seed count and confidence-interval meaning remain unverified.

Equation 1 (pp4–5) computes the original-versus-zero-masked change in `logit_synth - logit_real`. This is a defined functional intervention on a fixed network. Zero masking also changes semantics, context and input distribution; no artifact-only causal identification, natural counterfactual validity or uniquely established Lazy Learner training mechanism follows. Figure 10's exponential normalization relative to each maximum is not an absolute influence probability or a measured proportion of important patches. Exact high-impact thresholds/fractions, semantic/position stratification and repeated-seed confidence bounds are not reported sufficiently to reconstruct them. Attention and Grad-CAM maps are explanatory proxies, not proof of causal reliance.

PPL is a distinct substantive method. Section 4 reconstructs real images with diffusion and replaces aligned selected patches with reconstructed counterparts. The default training crop/test center crop is 224×224, reconstruction patch size 14×14, replacement probability 0.9 and reconstruction fraction 50%; SDv1.4 inpainting uses strength 0.25, 50 steps and guidance 7.5. Patch-wise contrastive learning aligns same-label patch embeddings and separates different labels, with loss weight 0.3 and margin 1.0; image-level binary classification remains the output task. CLIP/DINOv2 with LoRA are reported. Exact implementation, optimization/checkpoint details and operational reproduction remain unverified. The inverse patch-replacement descriptions are preserved rather than silently reconciled.

Quantitative evidence and counterexamples:

- Table 1 (p7): printed GenImage CLIP mean 97.2±1.7; DINOv2 95.9±3.0. The eight printed DINOv2 cells average 95.7875, an unreconciled aggregate discrepancy. Higher average performance does not imply every generator improves.
- Table 2 (p7): printed DRCT-2M CLIP 99.50±0.1 and DINOv2 99.06±0.1. Means reconstruct from the 16 printed cells, but across-generator sample standard deviations are approximately 0.4653 and 1.2764. The printed ±0.1 values are not silently repaired or interpreted as verified seed uncertainty.
- Table 4 (p8): PPL DINOv2 96.05 is below FatFormer 96.08; CLIP 93.85 is below NPR 94.37 and C2P-CLIP 95.83. Table 8 (p15) reports patch size 28 at 97.6 versus default 14 at 97.2. These qualify universal superiority/default-optimum claims.
- Table 5 (p8): All GenImage PPL CLIP is 69.33 overall, fake/real 38.93/92.18; DINOv2 is printed 72.07, 49.68/88.99. With R253's reported class counts, the latter pair gives 72.1232, not 72.07; release/subset identity is not assumed to resolve it. SD-trained CLIP fake recall 17.27 is below AIDE 20.33 despite higher overall accuracy.

The diagnostic question survives removing PPL, supporting proposed `method;analysis_study`. Contribution-role confidence is medium-high; empirical generality is medium and causal/universal-mechanism confidence is low. No verified author implementation, checkpoint, evaluator, split archive or license was identified within the bounded source inspection; this is not proof that none exists elsewhere.

## R253: Chameleon as an independently useful evaluation resource

Table 1 (p4) reports **14,863 real + 11,170 synthetic = 26,033 images**, not a synthetic-only or balanced test set. Scene/object/animal/human counts are real 3,574/3,578/3,998/3,713 and fake 2,976/2,016/313/5,865. Generator examples include Midjourney, DALL-E 3 and Stable Diffusion community adaptations, but exhaustive versions and per-generator counts are not supplied.

Sections 3.2.1–3.2.3 (pp4–5) describe community-image collection, query-aligned real photographs, filtering below 448×448, a safety checker, hash deduplication and CLIP-based filtering. Fake filtering uses source prompts while real filtering uses category-template embeddings. 20 workers participate; two independently judge each candidate fake without being informed of synthetic origin, retaining it only if both call it real. This is a documented human-conditioned selection protocol, not an independently held-out estimate of all humans' detection ability. Rater composition, inter-rater agreement, stagewise attrition, detailed similarity thresholds, perceptual deduplication and full training/pretraining leakage safeguards remain unverified. Semantic class distributions differ substantially and may confound detectors.

Chameleon has an external evaluation objective beyond AIDE: a curated challenge population with both authenticity classes, broader-training Setting II, three named training regimes, comparative detector scoring and intended reuse by future methods. That function remains after removing AIDE and supports R2. The primary contribution is not inferred merely from difficult images or large tables.

Table 5 (p9) actually evaluates nine external columns: CNNSpot, FreDect, Fusing, GramNet, LNP, UnivFD, DIRE, PatchCraft and NPR, plus AIDE. Section 5.1 and Appendix A.1 instead list LGrad where Table 5 has GramNet. This roster discrepancy remains unresolved.

All 30 printed Table 5 overall scores agree within 0.008 percentage points with sample-weighted accuracy from Table 1 class counts and printed fake/real rates. These metrics remain distinct:

| All GenImage training | Overall accuracy | Fake recall | Real specificity | Derived balanced accuracy |
|---|---:|---:|---:|---:|
| AIDE | 65.77 | 26.80 | 95.06 | 60.93 |
| UnivFD | 60.42 | 85.52 | 41.56 | 63.54 |

Always predicting real yields 57.0929% on these class proportions. High overall accuracy need not imply high fake recall, and AIDE is not uniformly superior. Under ProGAN training its 58.37 overall is below GramNet 58.94. Reported GenImage mean 86.88 versus PatchCraft 82.30 also has generator-specific counterexamples. B1 perturbation results do not establish Chameleon corruption robustness; FreDect can improve under blur, contrary to a universal degradation claim. Table 2's magnitude comparison mixes Chameleon's total count with other fake-only counts; its largest-testset claim is not endorsed.

AIDE separately combines DCT-selected high/low-frequency patch features and OpenCLIP semantics; this wave does not reopen its method/dataset roles. Nominal shared test populations and training regimes are reported, but exact checkpoint versions, identical preprocessing, compute/tuning fairness, source overlap and immutable test membership remain unverified.

Pinned author repository revision **`6725b710d5c437ab2f59792908ce0377dfc907de`** contains model/training/generic evaluation code. The inspected root code license is MIT. Chameleon separately has academic-only/noncommercial terms, email-request access and a required approved signed EULA (Appendix E, p19). Checkpoints are advertised but not downloaded. No unrestricted direct dataset release, full image rights audit, complete benchmark assets, fixed Chameleon manifest or all-baseline executable reproduction was verified. Research access restrictions qualify operational reproducibility; they do not erase the primary evaluation-resource role under R2. Proposed complete types are `method;dataset;benchmark`, with high contribution confidence, medium empirical comparability and low/unverified operational reproducibility.

## Shared experiments and bounded research comparison

R026 Table 5 explicitly uses Chameleon, cites AIDE and imports eight baseline columns for SDv1.4 and All GenImage training. All 16 imported overall scores match R253's Table 5; 15 class-rate pairs match. The exception is R026's SD-trained UnivFD: overall 55.62 is paired with 17.65/93.50, which belongs to R253's GramNet row, while R253's UnivFD pair is 74.97/41.09. Neither source is silently relabeled. Exact dataset release, subset, asset hashes, checkpoint overlap and preprocessing identity are unverified. Copied baseline results are not an independent rerun.

R026 studies spatial response concentration and artificial mask sensitivity; R253 studies detector failure on human-conditioned community imagery. Bounded published B1O precedents describe R236's artifact ground truth/spatial explanation alignment and R267's image-property/preference-score associations with detectability. Attention overlap, human selection, learned perceptual preference and classification correctness are different measurements. Neither those precedents nor these papers establish one universal causal explanation or directly comparable effect sizes. R236's Chameleon accuracy regression and R267's AP/accuracy divergence remain relevant counterexamples, not new reviews.

Source attribution might suffer analogous spatial fingerprint shortcuts. That is an **untested research hypothesis here**, requiring dedicated generator-identity predictions, attribution metrics and controlled spatial interventions. These detection results do not demonstrate it and authorize no source-attribution label changes.

## Retrieval, checks and preservation

Local PDF/gzip inventories were searched before downloading. Exactly **two new complete official manuscripts** were obtained, one per review. R026 used one complete HTTP 200 transfer. R253 preserved one failed partial transport and used one bounded same-source complete response; its ignored Range response was not concatenated. No alternate full versions, separate supplements, dataset archives, checkpoints, clones or contact requests were obtained. Source-owner outputs and transport histories are recovered and embedded/fingerprinted in the manifest; manuscript files and operational receipts remain outside Git.

Root independently parsed both complete sources, inspected key rendered figures/tables, and completed 37 R026, 48 R253 and 7 cross-paper checks. A separate reviewer completed 22 R026 and 38 R253 scientific/source checks. Source-owner checks and independent baseline accounting receipts are preserved separately. Faithful capture of a manuscript inconsistency is a successful provenance check, not a claim that the printed numbers reconcile. No full repository suite, exporter or model experiment was run. Final packet and preservation checks are recorded externally at `/private/tmp/b1q-evidence-2026-10-26/final-delivery-checks.json` and `/private/tmp/b1q-evidence-2026-10-26/integrity/final-preservation.json`; these references do not pre-claim their execution.

Recomputed before/after corpus: **674 public, 557 formal, 613 mapped, 61 unmapped, 1410 relationships and 1410 unique pairs**. Tasks: **621 detection, 84 source attribution, 45 localization**. Types: **578 method, 138 dataset, 96 benchmark, 21 survey, 85 analysis study**.

Batch B remains **159 original actions /148 papers; 133 historical unresolved actions /123 papers; 131 active-public unresolved actions /121 papers**. Both selected actions remain open. All 101 prior terminal decisions, completed task decisions, T024, pending R234, Batch C's 13 deferred debts, the separate 39-paper inventory and all 1,410 relationship identities remain unchanged. Primary checkout, protected 128 files, frozen 49 NeurIPS artifacts, ignored inputs, historical evidence and other worktrees are protected by fresh inventories.

Delivery consists of exactly this report and `data/raw/corpus_quality_batch_b_wave_b1q_2026_10_26/evidence_manifest.json`, untracked, unstaged, uncommitted and unpushed. No adjudication, bibliography correction, remediation or B1R begins.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Detailed source-owner scientific records

The following records preserve the individual reviews, all requested evidence questions, numerical tables, locators and source qualifications. Root and the independent reviewer provide additional checks above and in the manifest; reviewer agreement is not maintainer acceptance.

## R026 — Few-Patch Bias, provisional R3 review

**Provisional: ANALYSIS_STUDY_ADDITION_SUPPORTED → method;analysis_study.** The authoritative record remains method; its original research-type action is open, pending maintainer acceptance. No correction is applied.

### Identity and source

Official ICLR2026 paper, 20 pages, 7,455,376 bytes; SHA-256 `49cd7cd8be5752f4c798a2454478dc080f029a4e534805b11d40e187c7c35005`. All eleven listed authors and the normalized title match. One successful official-PDF transport; no alternate full manuscript or supplement.

### Primary scientific contribution

The first two explicit primary contributions and Section 3 investigate patch information and model sensitivity before Section 4 introduces PPL. Multi-architecture attention, patch occlusion, logit-margin contrasts and generator-specific diagnostics remain informative without the method. This meets R3 independently of routine PPL ablations. It does not validate universal all-patch information, identified causality or a unique Lazy Learner mechanism.

The source’s first two explicit contributions and Section3 precede the PPL method. The diagnostic findings remain scientifically informative without the intervention method. Contribution-role confidence is high; empirical sensitivity confidence is medium; universal/causal mechanism confidence and operational reproducibility are low.

### Requested scientific questions

#### 1. Patch partition and preprocessing

PPL uses 224 x 224 random training crops, center test crops and default 14 x 14 reconstruction patches. Figure 3b masks square sides 14, 28, 56 and 112; Table 8 varies reconstruction sizes 112, 56, 28 and 14. The diagnostic CDE mask grid and stride are not explicitly stated; do not automatically assign the training patch size to all diagnostics.
Locator: Section 5 p7; Figure 3b p4; Table 8 p15. Status: PARTIALLY_REPORTED.

#### 2. Synthetic and real populations

Main PPL training uses the SDv1.4 subset of GenImage. Appendix A also mentions reconstructing real images in the SDv1.4 subset from GenImage and DRCT. Figure 2 compares MSCOCO real and reconstructed images. Figure 4 uses selected DRCT-2M generated images; appendix diagnostics use GenImage. Diagnostic sample counts, complete sampling frame, source overlap and leakage safeguards are not established.
Locator: Figure 2 p4; Figure 4 p5; Appendix A p14; Appendix C pp16-20. Status: PARTIALLY_REPORTED.

#### 3. Generators and holdouts

GenImage columns are Midjourney, SDv1.4, SDv1.5, ADM, GLIDE, Wukong, VQDM and BigGAN. Training is SDv1.4; that column is in-generator. DRCT has 16 LDM/SD, Turbo, LCM, ControlNet and DR variant columns. Related SD variants are not independent evidence of unseen-family transfer; image/checkpoint overlap is unverified.
Locator: Tables 1-4 pp7-8. Status: PARTIALLY_REPORTED.

#### 4. Detector architectures

Figure 3a compares UnivFD/CLIP, CLIP+LoRA, DINOv2 and DINOv2+LoRA. Figure 4 compares UnivFD, DRCT, Breaking and PPL. Appendix C includes ConvNeXt-Base Stage 3 blocks 0/1/2. Different training, architectures and checkpoints confound a universal causal comparison.
Locator: Figures 3-4 pp4-5; Appendix C pp16,20. Status: REPORTED_WITH_LIMITS.

#### 5. Individual patch information

Section 3.1 reports 90% accuracy when a single randomly selected patch is replicated across an image on the SDv1.4 subset of GenImage. It does not state the detector identity, patch size, population N, class weighting, repeated seeds or full protocol for this result. Tiling changes texture/context and is not proof every individual patch is sufficient.
Locator: Section 3.1 p3. Status: PARTIALLY_SUPPORTED.

#### 6. All patches contain artifacts

The authors motivate universal artifact distribution from fully generated provenance, prior local detectors, selected visual examples and the single-patch result. There is no exhaustive all-patch/per-image/per-generator experiment or theorem that every patch has measurable discriminative or generator-specific information for every detector.
Locator: Section 1 pp1-2; Section 3.1 p3; Figure 2 p4. Status: NOT_UNIVERSALLY_ESTABLISHED.

#### 7. Single versus multiple patches

The single-patch claim, qualitative distribution diagnostics and PPL results support studying distributed cues. They are not a matched single-versus-multiple-patch dose-response experiment. Table 8 changes augmentation patch size, not an independently controlled number of authentic forensic cues.
Locator: Section 3.1 p3; Table 8 p15. Status: PARTIALLY_SUPPORTED.

#### 8. Counterfactual masking and replacement

CDE sets a selected patch to zero while fixing other pixels. Figure 3b varies occluded square sizes for UnivFD. RPR instead mixes corresponding reconstructed and original real patches during training. Zero masks add black boundaries, remove semantics and can be off distribution; a matched natural-replacement or sham control for CDE is not established.
Locator: Equation 1 pp4-5; Figure 3 p4; Section 4 p5. Status: REPORTED_WITH_LIMITS.

#### 9. Patch importance definition

CDE(i,j) = delta(I) - delta(I minus patch i,j), with delta = synthetic logit minus real logit. Appendix C applies exp(TDE(i,j)-TDEmax), as printed, while describing CDE. This removes absolute scale and does not establish uniform causal necessity.
Locator: Equation 1 pp4-5; Appendix C p16. Status: REPORTED.

#### 10. Intervention estimates

Figure 4 has selected-image heatmaps. Figure 10 compares normalized distributions for SDv1.4, VQDM, BigGAN and Glide. The introduction reports an average 18.7% +/- 4.1% accuracy drop from masking one patch; Figure 3b actually plots recall with median impact and impact range. No complete aggregation protocol, numerical CDE table or uncertainty definition is supplied.
Locator: Introduction p2; Figures 3-4 pp4-5; Figure 10 p16. Status: PARTIALLY_REPORTED.

#### 11. Causal identification

The implemented quantity is a deterministic model-input sensitivity contrast. The paper does not establish a structural causal model, mediator identification, confounder adjustment or a validated in-distribution real-world intervention. A patch logit difference alone does not identify a causal artifact effect or the unique learning mechanism.
Locator: Section 3.2 pp4-5. Status: NOT_ESTABLISHED.

#### 12. Attention concentration measures

Attention, Grad-CAM and CDE maps visually compare localized and broader responses; normalized CDE violin plots compare generators. There is no reported entropy/Gini/effective-support measure, thresholded population coverage or proof that attention maps measure actual causal reliance.
Locator: Figures 3-4 pp4-5; Figure 10 p16; Figures 17-18 pp19-20. Status: PARTIALLY_REPORTED.

#### 13. Highly influential patch proportion

The source says few or minority dominant patches but supplies no specified percentage, dominance threshold, sample count or population estimate. No fraction is invented.
Locator: Section 3.2 pp4-5; Appendix C pp16-20. Status: NOT_REPORTED.

#### 14. Detector-specific variation

Selected UnivFD maps tend to concentrate more than DRCT, Breaking and PPL; CLIP/DINO variants and ConvNeXt differ. Some UnivFD examples are already diffuse and PPL regions can remain weak. Selected images do not establish universal prevalence across models and images.
Locator: Figures 3-4 pp4-5; Figure 10 p16; Figures 17-18 pp19-20. Status: SUPPORTED_DESCRIPTIVELY.

#### 15. Position and semantic confounds

Table 7 compares fixed upper/lower/left/right reconstruction halves (95.0/94.4/94.3/90.0 mAcc) with random reconstruction (97.2), all with PCL. This is an augmentation control, not a fully stratified diagnostic CDE analysis; foreground/background and semantic-content matching are not established.
Locator: Table 7 p15. Status: PARTIALLY_CONTROLLED.

#### 16. Generator-specific artifact distribution

Figure 10 compares four generators. Figures 11-16 show SDv1.4, Midjourney, BigGAN, ADM, Glide and VQDM maps. Generator-specific artifact ground truth, statistical uniformity tests and full sample provenance are not supplied. No generator-identity prediction is evaluated.
Locator: Figure 10 p16; Figures 11-16 pp17-19. Status: SUPPORTED_DESCRIPTIVELY.

#### 17. Compression, resize and perturbation controls

Figure 6 measures GenImage balanced accuracy under JPEG quality 100/90/80/70/60, blur sigma 0/1/2/3, and scale 0.5/0.75/1/1.25/1.5. PPL CLIP/DINO and named baselines differ and degrade. These method robustness controls do not validate CDE causality; raw outputs and uncertainty are unavailable.
Locator: Figure 6 p9. Status: REPORTED_WITH_LIMITS.

#### 18. In-distribution versus unseen generators

Tables 1/2 include SDv1.4 and other generators. Tables 3/4 compare SD-trained PPL with ProGAN/GAN-trained baselines. Table 5 uses SDv1.4 and All GenImage conditions. Borrowed baseline values and unequal training populations are not a fully matched rerun; exact test assets/checkpoints remain unverified.
Locator: Tables 1-5 pp7-8. Status: REPORTED_WITH_LIMITS.

#### 19. Mask artifacts and off-distribution interventions

Zero masking is explicit. Appendix B notes dropout creates incomplete inputs whereas reconstruction preserves more appearance. There is no control isolating removed synthetic artifacts from newly introduced edges and missing semantics, and RPR is not an identified natural counterfactual.
Locator: Section 3.2 p5; Appendix B p15; Figure 9 p16. Status: LIMITATION_UNCONTROLLED.

#### 20. Confidence intervals and repeated seeds

No declared repeated-seed count, formal confidence interval, p value or patch-study N is established. Figure 3 shading is labeled impact range, not a confidence interval. Table 2 printed +/-0.1 does not reconstruct the across-generator dispersion and cannot be reinterpreted as seed uncertainty without evidence.
Locator: Introduction p2; Figure 3 p4; Tables 1-4 pp7-8. Status: NOT_ESTABLISHED.

### PPL as a separate method

Section 4 p5 reconstructs the whole real image with diffusion, then replaces selected original patches with their corresponding reconstructed patches. This mixes aligned real/reconstructed content rather than unrelated semantic patches.

Figure 5 caption p6 and Appendix B p15 instead describe replacing fake/dominant patches with real counterparts. Appendix A p14 describes restoring original counterparts from reconstructed real images. Both descriptions are preserved. A 50% fraction makes complementary patch counts equal, but does not settle implementation without code.

Same-label patch embeddings are pulled together and differing real/fake labels pushed apart. Equation 2 is printed as sum[Y*d^2 + (1-Y)*max(0,alpha-d^2)]. Alpha is 1.0; image loss weight is 0.7 and contrastive weight 0.3. Algorithm 1 p6 emits two image-class logits, not source identity.

CLIP and DINOv2 with LoRA. CLIP-Large is named in Appendix A resource comparison. Exact checkpoint versions, LoRA rank/target layers, optimizer, learning rate, batch size, epoch count and seeds are not fully specified in this PDF.

Appendix A p14 reports CLIP-Large memory 16 to 19 GB and a GenImage epoch from 3 to 4 hours on V100.

### Numerical results and counterevidence

#### Table1 p7 GenImage

```json
{
  "CLIP_cells_in_header_order": [
    94.8,
    98.5,
    98.3,
    94.7,
    96.1,
    98.6,
    98.5,
    98.0
  ],
  "DINO_cells_in_header_order": [
    90.4,
    98.2,
    97.7,
    91.8,
    96.3,
    98.0,
    97.7,
    96.2
  ],
  "header": [
    "Midjourney",
    "SDv1.4",
    "SDv1.5",
    "ADM",
    "GLIDE",
    "Wukong",
    "VQDM",
    "BigGAN"
  ],
  "printed_CLIP": "97.2 +/-1.7",
  "printed_DINO": "95.9 +/-3.0",
  "counterexamples": [
    "C2P-CLIP GLIDE99.0 exceeds PPL CLIP96.1; BigGAN98.7 exceeds98.0.",
    "SAFE Midjourney95.3 exceeds PPL CLIP94.8; SDv1.4 99.4 exceeds98.5.",
    "DINO printed mean95.9 differs from arithmetic mean95.7875 of its eight rounded cells. Preserve both, without editing the source."
  ]
}
```

#### Table2 p7 DRCT

```json
{
  "printed_CLIP": "99.50 +/-0.1",
  "printed_DINO": "99.06 +/-0.1",
  "DINO_SDXL_refiner": 94.7,
  "DINO_SDXL_DR": 97.42,
  "CLIP_SDXL_DR": 97.8,
  "reconstruction": {
    "DINO_mean": 99.061875,
    "DINO_sample_std": 1.2764075563862813,
    "CLIP_mean": 99.49875,
    "CLIP_sample_std": 0.4652579929458502
  },
  "limitation": "Means reconstruct, but across-generator sample standard deviations are1.2764 and0.4653, not0.1 (population values1.2359 and0.4505). Seed uncertainty is not specified; do not invent that interpretation."
}
```

#### Tables3 4 p8 cross dataset

```json
{
  "AIGCDetectionBenchmark_CLIP": "93.36 +/-6.31",
  "AIGCDetectionBenchmark_DINO": "94.41 +/-4.20",
  "AIGCDetectionBenchmark_AIDE": "92.77 +/-7.66",
  "UniversalFakeDetect_CLIP": "93.85 +/-6.78",
  "UniversalFakeDetect_DINO": "96.05 +/-3.58",
  "UniversalFakeDetect_FatFormer": "96.08 +/-5.95",
  "limitations": [
    "PPL uses SDv1.4 training; baselines use ProGAN/GAN training and borrowed results, not a common training rerun.",
    "UFD FatFormer96.08 slightly exceeds PPL DINO96.05.",
    "AIGC ProGAN AIDE99.99 exceeds PPL CLIP89.12; GauGAN NPR82.50 exceeds CLIP75.29."
  ]
}
```

#### Figure8 p9 modules

```json
{
  "with_reconstruction": [
    91.2,
    92.1,
    92.6,
    97.2
  ],
  "without_reconstruction": [
    88.7,
    89.5,
    90.1,
    90.5
  ],
  "columns": [
    "+LoRA",
    "+RPR",
    "+PCL",
    "+RPR+PCL"
  ],
  "limit": "Method-development ablation, not the independent basis for R3; data augmentation and losses change together."
}
```

#### Tables6 9 p15 ablations

```json
{
  "loss_InfoNCE": 95.8,
  "loss_margin_cosine": 92.8,
  "loss_margin_Euclidean": 97.2,
  "fixed_upper_lower_left_right_random": [
    95.0,
    94.4,
    94.3,
    90.0,
    97.2
  ],
  "patch_sizes112_56_28_14": [
    96.6,
    96.8,
    97.6,
    97.2
  ],
  "dropout10_15_20_25percent": [
    88.5,
    94.2,
    89.1,
    90.2
  ],
  "replacement": 97.2,
  "counterexamples": [
    "Patch28 mAcc97.6 exceeds default patch14 mAcc97.2; no universal optimality or monotonic smaller-patch claim.",
    "Fixed halves have SDv1.4 accuracy99.7-99.8 versus random98.5 despite lower mean.",
    "Some dropout conditions achieve SDv1.4 99.9 versus replacement98.5."
  ]
}
```

#### single patch p3

```json
{
  "reported_accuracy_percent": 90.0,
  "limit": "Random-patch tiling; detector, patch size, N and uncertainty are not specified."
}
```

#### one patch mask p2 p4

```json
{
  "reported_text": "18.7% +/-4.1% average accuracy drop",
  "limit": "Figure3 uses recall, median impact and impact range. No statistical definition establishes confidence interval, seed spread, relative-percent versus percentage-point interpretation."
}
```

### Chameleon connection and scoring

R026 explicitly evaluates Chameleon and imports AIDE-paper baselines. SDv1.4 and All GenImage AIDE overall62.60/65.77 and fake/real20.33/94.38,26.80/95.06 match R253 Table5. This is a direct reported evaluation connection, not only a shared name.

R026 does not print sample counts, fixed manifest, revision or a distinct new subset. R253 reports14,863 real plus11,170 fake, total26,033. Several weighted R026 scores are consistent with that class mix, but asset/version identity is not independently verified.

```json
{
  "SDv1.4": {
    "AIDE": [
      62.6,
      20.33,
      94.38
    ],
    "PPL_CLIP": [
      63.94,
      17.27,
      99.01
    ],
    "PPL_DINO": [
      66.63,
      64.65,
      68.12
    ]
  },
  "All_GenImage": {
    "AIDE": [
      65.77,
      26.8,
      95.06
    ],
    "PPL_CLIP": [
      69.33,
      38.93,
      92.18
    ],
    "PPL_DINO": [
      72.07,
      49.68,
      88.99
    ]
  },
  "array_order": [
    "overall_accuracy",
    "fake_class_recall",
    "real_class_specificity"
  ]
}
```

- R026 SD UnivFD prints overall55.62 with fake/real17.65/93.50. R253 assigns that pair to GramNet(overall60.95), while original UnivFD55.62 has74.97/41.09. The R026 pair weights to60.95498 using R253 counts, not55.62. This discrepancy remains unreconciled.
- R026 All GenImage DINO49.68/88.99 weights to72.12323 with R253 counts, not printed72.07. This exceeds rounding-only precision.
- PPL CLIP SD overall63.94 exceeds AIDE62.60 but fake recall17.27 is below20.33.
- DINO All GenImage overall72.07 exceeds SD66.63 but fake recall49.68 is below64.65.
- With R253 counts an always-real rule achieves57.09%;50% is not the majority-class baseline.
- No assets or exact shared sample subset verified.
- Checkpoint bytes, preprocessing, training-source overlap and dataset-release equality remain unverified.
- Borrowed baseline results are not verified independent reruns.
- Overall accuracy uses this dataset prior; it is not balanced accuracy, fake recall or accuracy at realistic deployment priors.

### Version and operational boundaries

Confirmed differences refer only to bylines and abstract descriptions. Neither earlier complete manuscript nor current arXiv PDF was retrieved; no exhaustive text diff or version-equivalence claim. Bibliography remains untouched.

Earlier arXivv1 includes Junchi Yan where official/currentv3 metadata includes Zequn Qin. The older/current arXiv abstracts describe Random Patch Replacement; the official abstract describes Randomized Patch Reconstruction. Only metadata/abstract differences were compared; bibliography is unchanged.

No author code/download URL was found in the inspected complete20-page PDF or publisher/arXiv abstract metadata. A single bounded exact-title discovery search did not establish a verified author repository; secondary summaries were not used as scientific evidence.

Do not infer that code is absent worldwide. No dataset, image archive, model, weight, checkpoint, supplement or repository clone was downloaded.

### Bounded comparison

R026 investigates spatial concentration/input sensitivity; R253 tests high-fidelity image generalization; R236 studies detector-artifact spatial alignment and auxiliary-task mismatch; R267 studies learned preference/image-property associations with correctness. These are related but non-equivalent measurements. None alone identifies causal reliance or a universal perceptual-quality mechanism. Spatial shortcut learning in source attribution is a hypothesis, not an experimentally demonstrated attribution result here.

### Preservation

TMP outputs only. No authoritative corpus/public export, taxonomy, decisions, task/scope, bibliography, primary checkout, index, commit or push was changed by this worker. No exporter or full suite was run. R026 remains method, detection, fully_generated and its original action stays open.

## R253: Chameleon benchmark evidence review

Provisional outcome: **BENCHMARK_ADDITION_SUPPORTED**. Proposed complete research types: **method;dataset;benchmark**. The scientific evidence is sufficient for this proposal; maintainer acceptance remains pending. No authoritative correction is applied. Existing detection and fully_generated labels remain unchanged.

### Source identity and retrieval

Official ICLR 2025 proceedings manuscript: *A Sanity Check for AI-Generated Image Detection*. Seven authors are Shilin Yan, Ouxiang Li, Jiayin Cai, Yanbin Hao, Xiaolong Jiang, Yao Hu and Weidi Xie. The complete file has 19 pages, including its appendix, and 6,321,086 bytes. SHA-256: f7657547faa18abed349e2bfc280cba433427040c00f5e4eaf19c3f25faa3244.

[Official PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/b0303773962ea1b5394c3a83cc7dd066-Paper-Conference.pdf) and [publisher record](https://proceedings.iclr.cc/paper_files/paper/2025/hash/b0303773962ea1b5394c3a83cc7dd066-Abstract-Conference.html). Both the visually inspected PDF and current publisher record spell Ouxiang Li. No first-name discrepancy was confirmed; no bibliography change is authorized. The arXiv full text was not retrieved or silently merged.

Local PDF and gzip inventories contained no identity-matched complete copy. One official transport timed out after 120 seconds at 1,599,681 of 6,321,086 bytes, exit 28. The partial, headers and receipt remain preserved. One bounded recovery of the same source requested Range; the server returned HTTP 200 with a full body, so the partial was not concatenated. Exactly one new complete manuscript was acquired. No supplements, dataset archives, checkpoints, full repository clones or emails were involved.

### Original review and locked R2

Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: Chameleon is used to compare nine existing detectors under a novel challenging protocol.

Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

### Dataset construction

1. **exact count.** Table 1, p4: 11,170 synthetic plus 14,863 real images, totaling 26,033. The abstract foregrounds generated images, but the reviewed official version is not synthetic-only.

2. **generator identities.** Sections 3.2.1, pp4-5 give examples of Midjourney, DALLE-3 and Stable Diffusion with community LoRA modules or in-house finetuning. Exact models and versions, per-image provenance and generator counts are not reported.

3. **prompt or source origins.** GPT-4-generated query terms retrieve community fakes from ArtStation, Civitai and Liblib and real photographs from Unsplash-like platforms. Fake image-text filtering uses website generation prompts; real filtering uses the mean embedding from 80 CLIP category templates. Actual query terms, prompts and source-image lists are unverified.

4. **quality selection.** The three design aims are visual realism, category variety and high quality. The pipeline discards images below 448 by 448 pixels, uses a Stable Diffusion safety checker, deduplicates hashes and filters CLIP image-text similarity. Complete thresholds and ranking rules are unavailable in the reviewed paper.

5. **meaning of human challenging.** Two workers independently judge each candidate fake without being told its synthetic origin, using whether a camera could capture it. Retention requires both to label it real. This is conditional selection, not an independent population-level human detection estimate.

6. **human evaluation performed.** Section 3.2.3, p5 describes an annotation platform and 20 recruited human workers performing the annotation procedure. This supports actual human screening beyond an author assertion of plausibility, but it was not independently replicated here.

7. **rater number composition.** Twenty workers were recruited, with two independent judges per image. Expertise, demographics, geographic or language composition, compensation, worker training and assignment details are not reported.

8. **human agreement.** Two-judge unanimity determines retained fakes. Raw disagreement rates, kappa or alpha, a held-out human cohort and confidence intervals are not reported. The selected unanimity does not establish broad human indistinguishability.

9. **filtering.** The initial collections contain more than 150,000 synthetic and more than 20,000 real images. Filtering includes resolution, safety, hash duplicates, CLIP matching and human category/realism screens. Full stage-by-stage attrition and reproducible thresholds are absent.

10. **generator semantic distribution.** Table 1 gives scene/object/animal/human counts of 3,574/3,578/3,998/3,713 for real images and 2,976/2,016/313/5,865 for synthetic images. Generator-wise counts are absent. The category/class imbalance may confound semantic detectors; no causal effect is established here.

11. **duplicate leakage.** Hash deduplication is explicit. The hash algorithm, perceptual near-duplicate handling, source-content grouping, generator-training leakage, foundation-model contamination and detector train/test intersection audits are unverified.

12. **resolution compression.** Curation removes images below 448 by 448 pixels. Table 2 summarizes Chameleon as 720P to 4K, while the introduction says most images exceed 720P. A complete resolution histogram, JPEG provenance, uniform baseline resizing and compression distribution are absent. Table 6 perturbations concern B1, not Chameleon controls.

13. **real comparison.** The resource includes 14,863 purported real photographs retrieved with corresponding query terms. These are not per-image matches and are not category-balanced. The sentence about real annotation refers to the same procedure and four-category retention without fully specifying an equivalent realism threshold.

14. **synthetic only.** No. Table 1 in the verified official manuscript includes both real and synthetic classes. A fake-only scoring assumption from an unverified earlier manuscript must not be transferred to this version.

15. **provenance rights.** Section 3.2.1 says every image has CC BY 4.0 licensing or owner permission for research. Individual rights and provenance records were not inspected. The pinned README restricts the dataset to academic research, and Appendix E, p19 requires EULA approval. Universal CC licensing or unrestricted redistribution is not verified.

16. **release access.** The pinned README announces a release dated 2024-12-29 but requires an email request and prohibits commercial use. Appendix E requires review and approval of a signed EULA. No request, email, archive retrieval or image-asset inspection was performed.

17. **splits.** Chameleon is the external test set in Setting II. Table 5 uses ProGAN, SD v1.4 or All GenImage training. No Chameleon training/validation partition, immutable test manifest, asset hash list or checkpoint mapping was verified.

18. **annotations ground truth.** Binary camera-versus-generated labels, four semantic categories and realism screening are described. Asset-level label files, exact annotation schema, prompts and source identifiers were not retrieved or verified as released.

### Benchmark methodology

1. **nine detector identities.** Section 5.1, p7 and Appendix A.1, p16 list CNNSpot, FreDect, Fusing, LNP, LGrad, UnivFD, DIRE, PatchCraft and NPR. Chameleon Table 5, p9 substitutes GramNet for LGrad and adds AIDE. Preserve this source inconsistency: no LGrad Chameleon column is available, and GramNet is not silently relabeled.

2. **identical test population.** Table 5 reports evaluation on Chameleon across the detector columns. The class counts and weighted accuracies are consistent with a common population. Per-model input manifests, omissions, unreadable-file records and asset hashes do not verify that all models saw identical bytes.

3. **training checkpoints.** Table 5 specifies ProGAN, SD v1.4 and All GenImage training conditions. Table 3 uses ProGAN except DIRE-D, which uses ADM. Appendix Tables 10 and 11 specify 360,000 ProGAN fakes and 324,000 SD v1.4 fakes plus equal real populations. Baseline checkpoint identifiers, source commits and full retraining hyperparameters are not pinned. The AIDE checkpoint folder is advertised but unverified.

4. **metric definition.** Section 5.1, p8 reports classification accuracy and average precision over real and generated images. Table 5 provides overall and separate fake/real class accuracy. Pinned engine_finetune.py uses class-1 softmax probability greater than 0.5 with sklearn accuracy and average precision. This current AIDE code does not verify historical baseline calibration or checkpoint versions.

5. **accuracy recall balance.** Table 5 overall accuracy is weighted by empirical class frequency. Fake class accuracy is sensitivity; real class accuracy is specificity. Overall accuracy is neither fake recall nor balanced accuracy. Always predicting real yields 57.0929205%. All GenImage AIDE has 65.77% overall accuracy, 26.80% sensitivity and 95.06% specificity; its derived balanced accuracy is 60.93%.

6. **detector generalization.** Setting II allows broader GAN/diffusion training and then tests on perceptually selected community images, in contrast with B1/B2. This measures a useful conditional distribution-shift challenge. It is not representative internet prevalence or an identified causal mechanism linking image quality to detectability.

7. **fixed future protocol.** The paper specifies a reusable external test resource, three common training conditions and binary scoring, and explicitly intends future detector evaluation. Reuse is possible in principle after access approval. No immutable manifest, current release identifier or Chameleon-specific runner was verified.

8. **generatorwise results.** Chameleon generator-wise accuracy or average precision is not reported. Table 5 aggregates by training condition rather than test generator. Four-category population counts are known, but category-specific performance is absent. Tables 3 and 4 concern other benchmarks.

9. **failure mode analysis.** Table 5 separately analyzes fake and real errors and training-condition sensitivity. Most detectors miss many fakes, but UnivFD under SD/All GenImage is an important counterexample with higher fake recall and poor real specificity. The comparison does not identify causal failure mechanisms or provide a complete error audit.

10. **alternative datasets.** The study also evaluates B1 AIGCDetectBenchmark across sixteen test sets and B2 GenImage across eight generator conditions, with B1 average precision and JPEG/blur checks. Those experiments are distinct from Chameleon. Table 2 compares Chameleon total image counts with earlier fake-only counts, so its largest-size assertion is not based on matched counting units.

11. **AIDE fairness.** AIDE and external detectors share the three named Table 5 training conditions, and the challenge remains scientifically useful without AIDE. Exact compute budgets, checkpoint versions, preprocessing and model-selection independence are unverified. CLIP curation could couple selection to CLIP-based features, but no benefit is causally demonstrated.

12. **training independence.** The paper treats Chameleon as external to ProGAN/GenImage training; no named Chameleon training use is shown. Deduplication against detector training, foundation-model pretraining and hyperparameter-selection data is unverified. Absence of named training use does not prove absence of leakage.

13. **evaluator manifest.** The pinned tree provides generic AIDE model, loader and evaluation code. It does not include a verified Chameleon-specific immutable manifest, splits, generator labels or a complete nine-baseline checkpoint harness. Available generic code is distinct from verified complete benchmark assets.

14. **access restriction.** Academic-only email requests and mandatory reviewed EULA approval limit immediate independent evaluation. No access grant was requested or verified. This qualifies reproducibility without erasing the paper’s primary evaluation-resource contribution under R2.

15. **distinct function.** Chameleon is an explicitly primary external evaluation challenge: a curated real/fake population selected for perceptual difficulty, broader training protocol, common detector comparisons and intended future reuse. Its evaluation function is scientifically distinct from validating AIDE and supports R2 beyond merely having difficult data or many baselines.

### Table 5 numerical evidence, page 9

Columns preserve the printed overall accuracy, fake sensitivity and real specificity, in percent. Balanced accuracy is separately derived from the two class rates.

| Training | Detector | Overall | Fake | Real | Derived balanced |
|---|---|---:|---:|---:|---:|
| ProGAN | CNNSpot | 56.94 | 0.08 | 99.67 | 49.875 |
| ProGAN | FreDect | 55.62 | 13.72 | 87.12 | 50.420 |
| ProGAN | Fusing | 56.98 | 0.01 | 99.79 | 49.900 |
| ProGAN | GramNet | 58.94 | 4.76 | 99.66 | 52.210 |
| ProGAN | LNP | 57.11 | 0.09 | 99.97 | 50.030 |
| ProGAN | UnivFD | 57.22 | 3.18 | 97.83 | 50.505 |
| ProGAN | DIRE | 58.19 | 3.25 | 99.48 | 51.365 |
| ProGAN | PatchCraft | 53.76 | 1.78 | 92.82 | 47.300 |
| ProGAN | NPR | 57.29 | 2.20 | 98.70 | 50.450 |
| ProGAN | AIDE | 58.37 | 5.04 | 98.46 | 51.750 |
| SD v1.4 | CNNSpot | 60.11 | 8.86 | 98.63 | 53.745 |
| SD v1.4 | FreDect | 56.86 | 1.37 | 98.57 | 49.970 |
| SD v1.4 | Fusing | 57.07 | 0.00 | 99.96 | 49.980 |
| SD v1.4 | GramNet | 60.95 | 17.65 | 93.50 | 55.575 |
| SD v1.4 | LNP | 55.63 | 0.57 | 97.01 | 48.790 |
| SD v1.4 | UnivFD | 55.62 | 74.97 | 41.09 | 58.030 |
| SD v1.4 | DIRE | 59.71 | 11.86 | 95.67 | 53.765 |
| SD v1.4 | PatchCraft | 56.32 | 3.07 | 96.35 | 49.710 |
| SD v1.4 | NPR | 58.13 | 2.43 | 100.00 | 51.215 |
| SD v1.4 | AIDE | 62.60 | 20.33 | 94.38 | 57.355 |
| All GenImage | CNNSpot | 60.89 | 9.86 | 99.25 | 54.555 |
| All GenImage | FreDect | 57.22 | 0.89 | 99.55 | 50.220 |
| All GenImage | Fusing | 57.09 | 0.02 | 99.98 | 50.000 |
| All GenImage | GramNet | 59.81 | 8.23 | 98.58 | 53.405 |
| All GenImage | LNP | 58.52 | 7.72 | 96.70 | 52.210 |
| All GenImage | UnivFD | 60.42 | 85.52 | 41.56 | 63.540 |
| All GenImage | DIRE | 57.83 | 2.09 | 99.73 | 50.910 |
| All GenImage | PatchCraft | 55.70 | 1.39 | 96.52 | 48.955 |
| All GenImage | NPR | 57.81 | 1.68 | 100.00 | 50.840 |
| All GenImage | AIDE | 65.77 | 26.80 | 95.06 | 60.930 |

The real-class share is 57.0929205%, so an always-real predictor already attains that overall accuracy. All 30 overall figures agree with weighting by Table 1 populations within 0.008 percentage points using displayed class rates; printed numbers are retained. The 65.77% all-GenImage AIDE result must be read with its 26.80% fake sensitivity, 95.06% real specificity and derived balanced accuracy 60.93%. UnivFD provides the counterexample of 85.52% fake sensitivity but 41.56% real specificity, yielding derived balanced accuracy 63.54%.

### Separate AIDE method contribution

Use 32-by-32 DCT-ranked patches; select two highest-frequency and two lowest-frequency patches, resize them to 256-by-256, apply SRM filters and encode them with two ResNet-50 branches. Fuse these with global OpenCLIP ConvNeXt semantic features and an MLP for binary authenticity prediction.

AdamW; learning rates 1e-4 for B1 and 5e-4 for B2; batch size 32, eight A100 GPUs, five epochs. Training adds JPEG with quality 30-100 and Gaussian blur with sigma 0.1-3.0, each with probability 0.1. No independent reproduction was conducted.

The benchmark function is independent of AIDE: a specified external real/fake challenge, explicit broader training protocol, common comparisons and intended evaluation of future methods. This supports locked R2 beyond a difficult dataset or large tables. Existing method and dataset roles are not reopened.

### Counterevidence and limitations

- Table5p9: ProGAN AIDE overall accuracy 58.37% is below GramNet 58.94%. All GenImage UnivFD fake sensitivity is 85.52%, versus AIDE 26.80%, while its real specificity is 41.56%, versus AIDE 95.06%. AIDE is not uniformly superior.
- Table5p9: All GenImage AIDE overall accuracy 65.77% exceeds an always-real baseline of 57.0929%, but derived balanced accuracy 60.93% and fake recall 26.80% reveal substantial limitations. UnivFD balanced accuracy 63.54% exceeds AIDE 60.93% despite lower overall accuracy.
- Table4p8: AIDE mean GenImage accuracy is 86.88%, versus PatchCraft 82.30%. Its Midjourney accuracy 79.38% is below GenDet 89.60%, VQDM 80.26% is below PatchCraft 83.70%, and BigGAN 66.89% is below GenDet 75.00%. Mean superiority does not imply per-condition dominance.
- Table6p9: B1 JPEG and Gaussian-blur results are not Chameleon controls. FreDect at Gaussian sigma 4 reaches 69.64%, above its original 64.03%; the broad claim that every perturbation degrades every method is not supported.
- Tables2p5and10/11p17: Chameleon 26.0k is a total count across classes, whereas Appendix Tables 10/11 describe earlier counts as fakes plus an equal number of real images. The largest-size claim is not based on matched counting units and is not the basis for accepting R2.
- Table1p4;§3.2.2p5: Class/category imbalance and different CLIP text filtering for real and synthetic images may introduce semantic or curation confounds. Exact matching and causal generalization have not been established.
- Table3p8/Table12p18: DIRE-G/D behavior is not cleanly aligned across the accuracy and average-precision tables. This review neither resolves it by relabeling nor relies on those rows for R2.
- AppendixCp18/Ep19: The authors acknowledge limited scale and unsatisfactory Chameleon performance. Mandatory EULA approval and academic-only access requests constrain direct operational reproducibility.

### Pinned code, access and licensing

[Author repository](https://github.com/shilinyan99/AIDE), inspected at revision **6725b710d5c437ab2f59792908ce0377dfc907de** through small metadata and raw file requests only. Model code, a generic data loader and evaluation scripts exist. Root LICENSE is MIT, copyright 2024 Shilin Yan. Some source files retain upstream Meta copyright notices. No legal conclusion about third-party assets is made.

Pinned README restricts Chameleon to academic research and prohibits commercial use. The paper claims individual images are CC BY 4.0 or used with research permission; individual assets were not verified.

The authors advertise research access by email. Appendix E, p19 requires review and approval of a signed EULA. Neither a request nor actual access verification was performed.

A Google Drive folder is advertised. It was not opened, downloaded or verified.

Generic TestDataset reads 0_real and 1_fake folders. The evaluator uses class-1 softmax above 0.5 for accuracy and average precision. main_finetune.py iterates dataset folders and includes hard-coded names for sixteen/eight standard benchmark subsets; it is not a Chameleon-specific immutable manifest. A distributed-evaluation duplicate-padding warning is present. Code was not executed or repaired.

No unrestricted public dataset download, complete benchmark assets, immutable Chameleon manifest, exact historical checkpoint mapping or independent reproduction is claimed. The current repository postdates the paper. The scientific contribution classification remains distinct from whether a reader can immediately reproduce every reported comparison.

### Provisional disposition and confidence

Chameleon is an explicitly primary external evaluation resource: it combines a human-perceptual challenge population with both binary classes, specified curation, broader-training Setting II, common comparative scoring across independent detectors and intended future-method evaluation. Its scientific function survives removing AIDE. R2 support therefore does not rely merely on difficult images, nine baselines or large tables. Request-gated access and unverified assets qualify operational reproducibility rather than the paper’s contribution classification.

- Scientific contribution confidence: **high**.
- Empirical comparison confidence: **medium**.
- Operational reproducibility confidence: **low / unverified**.
- Maintainer acceptance: **pending**.
- Authoritative changes applied: **none**.

### Version boundaries

- Only the official 19-page ICLR 2025 manuscript was used. The arXiv full text was not retrieved, and manuscript equivalence is unverified.
- Printed PDF and current official publisher HTML both spell Ouxiang Li. The anticipated first-name discrepancy was not confirmed. No author or bibliography change was made.
- The pinned repository revision postdates publication. MIT-licensed code availability does not prove historical Table 5 reproduction or unrestricted dataset licensing.
- No Chameleon archive or manifest was retrieved. A later paper mentioning Chameleon would not prove that release, split or checkpoint versions are identical.

### Lightweight verification

All 16 source, identity, numerical and evidence checks passed. The record covers all 18 dataset-construction and 15 benchmark questions, preserves the exact original action and current authoritative rows, ties values to Tables 1 and 5, verifies source/code fingerprints and retains transport history. These checks are not detector reproduction or a full repository suite.

No repository files were written by this worker; no terminal decisions, exports, full suite, commit or push occurred. Global repository preservation and Batch B accounting are verified separately by the root agent. All manuscript, render, code-inspection and operational receipts remain outside Git under /private/tmp/b1q-evidence-2026-10-26/r253.


## Recovery finalization — 2026-10-27 (Asia/Shanghai)

The complete original draft and worker records are preserved. The saved independent packet review completed before interruption: **128/128 passed**, no material findings. The existing **83/83** packet checks, source-owner **43/43 R026 and 16/16 R253**, independent scientific **22/22 and 38/38**, and root **37/37, 48/48 and 7/7 cross-paper** receipts are recovered. Their content hashes match the original reviewed packet and source files. Those reviews are reused; only these explicit recovery clarifications and final delivery/preservation checks are new. No additional manuscript was downloaded during recovery. The original 2026-10-26 artifact names and scientific dates remain intact.

### Numerical audit history: printed results, context and analyst mistakes

No published result is overwritten. Where no different earlier local digit transcription survives, none is invented. A copied source-context pair or a mistaken analytical assessment is distinguished from a digit-transcription mistake.

| Source and condition | Original printed / previously transcribed observation | Independently checked result and classification |
|---|---|---|
| R026 Table 5 p8, SDv1.4 UnivFD | Overall 55.62; fake/real 17.65/93.50, retained as printed | R253 Table 5 p9 UnivFD is 55.62 with 74.97/41.09. The 17.65/93.50 pair belongs to R253 GramNet. Conditional weighting using R253 counts gives 60.9549802, not 55.62. This is a source-context inconsistency, not an invented local digit correction. Exact R026 sample membership remains unknown. |
| R026 Table 1 p7, DINOv2 GenImage | Printed 95.9±3.0, originally retained as printed | Arithmetic mean of eight printed cells is 95.7875; sample SD is 3.0092417. Preserve the unreconciled printed aggregate and the cell-derived mean separately. Neither is an independently reproduced experiment. |
| R026 Table 2 p7, DRCT-2M DINOv2/CLIP | Printed 99.06±0.1 /99.50±0.1 | Sixteen-cell means are 99.061875 /99.49875; sample SDs 1.2764076 /0.4652580, population SDs 1.2358763 /0.4504841. Printed means round consistently; the ±0.1 definition remains unreconciled. It is not reclassified as a verified seed variance or CI. |
| R026 Table 5 p8, All GenImage DINOv2 | Printed 72.07 with fake/real 49.68/88.99 | Conditional weighting with R253 counts gives 72.1232271. An earlier progress message prematurely said all PPL pairs matched; that analytical generalization was retracted. The SD PPL rows and All GenImage CLIP do match; All GenImage DINOv2 is an exception. No paper digit or population is silently changed. |
| R253 scratch assessment of Table 5 p9 | An original scratch note called ProGAN FreDect/UnivFD and SDv1.4 UnivFD weighted scores inconsistent | Recalculation shows all 30 rows agree within 0.008 percentage points (maximum 0.00730765), compatible with rounded class rates. The scratch prose was wrong; the manuscript numbers did not change. The exact original note and explicit correction remain in the manifest's numerical audit history. |

The full original numerical arrays, original scratch-history object, source locators and formulas are preserved in the manifest. These source or assessment discrepancies do not substitute for R2/R3 contribution reasoning.

### R253 metrics: explicit positive-class and population definitions

Treat synthetic/fake as positive. For the strongest reported AIDE row (All GenImage training; Table 5 p9), use the 11,170 fake and 14,863 real counts from Table 1 p4:

`raw Acc (%) = (11170 × 26.80 + 14863 × 95.06) / 26033 = 65.77162754964852`

This differs from printed **65.77%** by only **0.00162755 percentage points**, ordinary rounding-compatible residual. The class rates are printed rounded percentages and do not establish exact integer prediction counts.

- **Raw accuracy:** frequency-weighted accuracy at the evaluated class proportions, here 65.77% printed.
- **Balanced accuracy:** `(26.80 + 95.06)/2 = 60.93%`, giving equal weight to the two classes.
- **Fake recall / sensitivity:** 26.80%; fake miss rate (FNR) is 73.20%.
- **Real-image recall / specificity:** 95.06%; false-positive rate (FPR), the real-image false-alarm rate, is **4.94%**.
- **Average precision (AP):** a precision-recall ranking/threshold-sweep metric, distinct from accuracy and AUROC. R253 Appendix Table 12 p18 reports AP for B1; it does not supply Chameleon AP in Table 5.
- **AUROC:** a threshold-swept TPR/FPR measure; it cannot be inferred from this one operating point. No Chameleon AUROC is reported in the inspected Table 5.

Always predicting real yields 57.0929205% raw accuracy on these proportions. Raw accuracy therefore can conceal poor fake recall. These empirical class priors do not establish real-world deployment prevalence. Chameleon remains a dual-class, imbalanced benchmark; its total 26,033 is not substituted for fake-only image counts in other collections.

### RefPrint / HieraSIA-Bench: untested research hypotheses only

For possible future RefPrint or HieraSIA-Bench work, test the hypothesis that generator-identity attribution may rely on sparse spatial fingerprint regions. A suitable study would use explicit generator-ID predictions, independent attribution metrics, source/content-grouped held-out splits, checkpoint controls, repeated seeds and carefully qualified spatial interventions. Compare masking/reconstruction sensitivity while controlling for semantic position, compression and resizing. **These are untested research hypotheses, not demonstrated attribution findings, implemented system features or claims about either project's architecture.** Neither reviewed detection paper verifies them. No source-attribution or localization label change is authorized or applied.

Scientific dispositions remain provisional and maintainer acceptance remains pending. R026 stays `method`; R253 stays `method;dataset`; both retain `detection` / `fully_generated`. Both original research-type reviews stay unresolved. The final delivery consists of exactly the two named evidence artifacts, with no staging, commit, push, exporter, full suite or next review wave.
