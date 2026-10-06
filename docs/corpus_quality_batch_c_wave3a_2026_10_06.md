# Corpus Quality Batch C External Evidence and Adjudication — Wave 3A

Date: 2026-10-06

Scope: localization evidence for T236 and T246 only under locked policy T2. No research-type question was reviewed. Adjudication applies one taxonomy remediation for T246 and leaves T236 unresolved.

| Review | Paper | Primary source | Spatial output | Spatial GT | Quantitative localization evaluation | Adjudication | Final disposition | Confidence |
|---|---|---|---|---|---|---|---|---|
| T236 | *Unveiling Perceptual Artifacts: A Fine-Grained Benchmark for Interpretable AI-Generated Image Detection* | [Final ICLR OpenReview PDF](https://openreview.net/pdf/6b5a5d6411ea1778f8c2cbf707a8a5744abe71b0.pdf) | Not established; the accessible record describes artifact annotations and attention alignment, but the final paper body was challenge-blocked and timed out. | Pixel-level categorized perceptual-artifact annotations are confirmed by the official abstract. | Not established; no accessible text demonstrated a scored spatial prediction against those annotations. | `EVIDENCE_STILL_INSUFFICIENT` | `REMEDIATION_NOT_APPLIED` | High |
| T246 | *Zooming In on Fakes: A Novel Dataset for Localized AI-Generated Image Detection with Forgery Amplification Approach* | [Official AAAI proceedings PDF](https://ojs.aaai.org/index.php/AAAI/article/download/37240/41202) | The weighted decoder upsamples hierarchical features to an original-resolution predicted mask M-hat. | BR-Gen retains real-image, mask, forged-image triplets; the segmentation loss compares ground-truth masks M with M-hat. | IoU is the explicit localization metric; NFA-ViT reports 0.907 IoU and localization ablations. | `LOCALIZATION_TASK_SUPPORTED` / `EVIDENCE_RESOLVED_CHANGE` | `REMEDIATION_APPLIED` | High |

## T236

The official record establishes pixel-level artifact annotations and an interpretability/attention-alignment purpose. It does not establish from accessible content that the detector produces a spatial forensic prediction evaluated against those annotations. The final OpenReview PDF was the only permitted paper and remained inaccessible after the challenge page and a timed-out direct retrieval. No alternate version or supplement was used. T236 remains `detection` only and unresolved; `REMEDIATION_NOT_APPLIED`.

## T246

The official AAAI paper explicitly defines a localization branch. Its weighted decoder produces an original-resolution region mask, and the joint objective compares that prediction with the ground-truth region mask using segmentation loss. The evaluation defines IoU as the localization metric and reports 0.907 IoU for NFA-ViT. This satisfies T2. `EVIDENCE_RESOLVED_CHANGE`; `REMEDIATION_APPLIED`: `detection → detection;localization`.

## Resolution

- `LOCALIZATION_TASK_SUPPORTED = 1`
- `VISUALIZATION_ONLY_NO_LOCALIZATION = 0`
- `NO_LOCALIZATION_TASK = 0`
- `EVIDENCE_STILL_INSUFFICIENT = 1`
- `REMEDIATION_APPLIED = 1`
- `REMEDIATION_NOT_APPLIED = 1`
- External Batch C unresolved: `29 → 28`
- Remaining task cases: `13 → 12`
- U010 remains the one institution case; 15 research-type cases remain untouched.
- T527 remains separate as `SCOPE_OR_TASK_EVIDENCE_REQUIRED`.

Two authoritative paper records were budgeted and attempted. One complete primary paper was usable; the other was inaccessible. No raw paper, search page, supplement, or alternate version is stored. The structured evidence ledger is `data/raw/corpus_quality_batch_c_wave3a_2026_10_06/evidence_manifest.json`.

Corpus identity remains 639 public papers, 531 formal publications, 617 mapped papers, and 1,421 unique paper–institution relationships. Taxonomy changes only for T246: localization increases from 41 to 42; every other task and research-type count is unchanged.
