# Tier 2 HIGH-priority evidence resolution — September 2026

This successor pass resolves only the 12 `HIGH` rows from `queue_c_evidence_required.csv`. The remaining 20 evidence rows, 171 policy exclusions, Tier 3, legacy cleanup, and the prior 648-paper inclusion baseline remain outside this pass.

The canonical ledger is [systematic_tier2_high_priority_evidence_review_2026_09.csv](../data/manual/systematic_tier2_high_priority_evidence_review_2026_09.csv). Counts below are generated from that CSV and the current public exports.

## Evidence resolution

- `EVIDENCE_CONFIRMS_SCOPE`: 9
- `EVIDENCE_EXCLUDES_SCOPE`: 3
- `EVIDENCE_STILL_INSUFFICIENT`: 0

## Identity reconciliation

- `MISSING_ADD`: 9
- `EXISTING_CURRENT`: 0
- `EXISTING_ALTERNATE_TITLE`: 0
- `EXISTING_UPDATE_NEEDED`: 0
- `EXISTING_EXCLUSION`: 0
- `AMBIGUOUS_IDENTITY`: 0

## All 12 decisions

| Title | Original unresolved question | Decisive primary evidence | Evidence outcome | Identity | Added / ID | Taxonomy | Markers | Remaining issue |
|---|---|---|---|---|---|---|---:|---|
| Riemannian-Geometric Fingerprints of Generative Models | Does the evaluated Riemannian fingerprint infer a generator/source from encountered generated images using naturally occurring traces, rather than only authenticating a model service or its parameters? | Sections 3.1, 3.3, and 4.2/Table 3 define artifacts as deviations in generated samples, predict the source generator from an observed image, and evaluate attribution across four image datasets and 27 model architectures. No watermark, embedded signature, service call, or generator parameters are required. | EVIDENCE_CONFIRMS_SCOPE | MISSING_ADD | yes / curated:807b1bfdfd16bf98be30 | task=source_attribution; scope=fully_generated; type=method;analysis_study | 1 | None |
| A Rich Knowledge Space for Scalable Deepfake Detection | Does the stated AIGC benchmark independently evaluate broader fully generated or generatively edited images beyond the 3.6-million facial-image/deepfake collection? | Section 5.2.2 and Table 4 independently evaluate General Synthetic Image Detection beyond facial manipulation: a linear probe trained on Stable Diffusion 1.4 versus ImageNet is tested on eight GenImage generators and reaches 88.50% mean accuracy. | EVIDENCE_CONFIRMS_SCOPE | MISSING_ADD | yes / curated:5305dab76cb75ae5887e | task=detection; scope=fully_generated;deepfake; type=method;dataset;benchmark | 1 | No DOI, arXiv ID, or OpenAlex ID was established. |
| DINOv3 Beats Specialized Detectors: A Simple Foundation Model Baseline for Image Forensics | Do the CAT-Net/MVSS-Net evaluation protocols contain a substantive independently evaluated generative-edit or fully generated-image subset, rather than classical tampering only? | Section 4.1 identifies the CAT-Net/MVSS-Net evaluation sets as CASIA splicing/copy-move, Columbia splicing, NIST16 composite manipulation, Coverage copy-move, and the tampered-image subset of IMD2020. Tables 1–2 contain no independently evaluated generative-edit or fully generated subset. | EVIDENCE_EXCLUDES_SCOPE | N/A after scope exclusion | no | N/A | N/A | None; the evidence-layer scope exclusion is final for this pass. |
| Conditional uncertainty-aware political deepfake detection with stochastic Convolutional Neural Networks | Does the political-deepfake uncertainty study evaluate a broader passive synthetic-image detector, or only face/identity/video deepfakes? The saved publisher summary does not identify its data or evaluation unit. | Sections 3.1–3.5 define an image-level OpenFake subset with 2,000 authentic photographs and 2,000 AI-generated images from multiple generators, filtered for political actors, institutions, events, and discourse, with generator-disjoint out-of-distribution evaluation. | EVIDENCE_CONFIRMS_SCOPE | MISSING_ADD | yes / curated:64195610a6d2c2448275 | task=detection; scope=fully_generated; type=method;analysis_study | 0 | Coordinates pending for: Colegiul Național “Mihai Eminescu” Satu Mare. |
| FreDA: Training-Free Test-Time Adaptation for Deepfake Detection via Non-parametric Cache Retrieval | Does FreDA adapt passive general AI-generated-image detectors beyond pure face/video deepfake detection? The truncated abstract does not identify the target datasets. | Section 5.1 states that all evaluation uses FaceForensics++ in-domain and Celeb-DF-v1 plus DFDCP cross-dataset; Sections 5.2–5.4 retain those facial-deepfake datasets, and Section 4.2 defines retrieval over authentic and manipulated faces. | EVIDENCE_EXCLUDES_SCOPE | N/A after scope exclusion | no | N/A | N/A | None; the evidence-layer scope exclusion is final for this pass. |
| Generating Attribution Reports for Manipulated Facial Images: A Dataset and Baseline | Does Generating Attribution Reports evaluate a broader synthetic-image forensic contribution beyond facial manipulation, and what source is attributed? Only an ACL bibliographic citation is saved. | Section 2/Table 1 uses only CelebAMask-HQ and FFHQ faces for face swap, facial-attribute editing, and facial-component inpainting; Appendix G filters SynthScars to facial manipulations. The report attributes visible facial regions and artifact descriptions, not a source generator. | EVIDENCE_EXCLUDES_SCOPE | N/A after scope exclusion | no | N/A | N/A | None; the evidence-layer scope exclusion is final for this pass. |
| Detecting violent deepfakes: dataset and a compact attention network with multi-scale supervision | Does the violent-deepfake dataset test general generated scenes/images or only face/identity manipulation, and is its image-forensics component independently evaluated? | The abstract and experiments introduce DVID with 17,442 Stable Diffusion violent-scene images and 17,253 real images, report 98% accuracy and 97.8% average precision, and independently test cross-model/color robustness on DiffusionForensics. | EVIDENCE_CONFIRMS_SCOPE | MISSING_ADD | yes / curated:e5a9ed970200c293678e | task=detection; scope=fully_generated; type=method;dataset;benchmark | 0 | IIT Patna affiliation is verified, but its registry location lacks confirmed coordinates. |
| Abductive Corroboration of Probabilistic AI Models for Forensic Synthetic Media Detection | Is there a separable, independently evaluated passive synthetic-image forensic method or passive-detector analysis that remains valid without SynthID or any watermark recovery? Identify the watermark-free results. | Section III defines three passive image classifiers applied independently to 4,000 images. Table III reports their standalone results, and Table VIII reports watermark-free corroboration: two-classifier agreement lowers false-positive rate from 20.7% to 1.7%, while three-classifier agreement yields 0% observed false positives. SynthID is confined to a separate 400-image experiment. | EVIDENCE_CONFIRMS_SCOPE | MISSING_ADD | yes / curated:dc0280c881d08395cfac | task=detection; scope=fully_generated; type=method;analysis_study | 0 | Coordinates pending for: The Alan Turing Institute. |
| SPARK-IL: Spectral Retrieval-Augmented RAG for Knowledge-Driven Deepfake Detection via Incremental Learning | Does SPARK-IL evaluate broader passive AI-generated-image detection beyond face/video deepfakes, and which generator datasets establish that component? | The abstract and Section 4/Table 1 evaluate UniversalFakeDetect across 19 models: ProGAN, CycleGAN, BigGAN, StyleGAN, GauGAN, StarGAN, low-level/perceptual manipulations, LDM, GLIDE, and DALL·E. SPARK-IL reports 94.60% mean accuracy and cross-category generalization. | EVIDENCE_CONFIRMS_SCOPE | MISSING_ADD | yes / curated:d50b63ed7eabda15c19f | task=detection; scope=fully_generated;generative_editing;deepfake; type=method | 2 | Coordinates pending for: Institute of Applied Sciences and Intelligent Systems; University of Salento. |
| Deep learning for CGI and visual forgery detection: a comprehensive survey | Does this CGI/visual-forgery survey substantively cover passive AI-generated-image detection, attribution or generative-edit localization, rather than mainly classical CGI/rendering or traditional manipulation? | Sections 2.3, 3.1, 6.3, and the dataset synthesis cover passive detection of GAN- and diffusion-generated images, including CIFAKE, GenImage, ArtiFact, StyleGAN, ProGAN, Stable Diffusion, Midjourney, ADM, GLIDE, and cross-generator generalization. | EVIDENCE_CONFIRMS_SCOPE | MISSING_ADD | yes / curated:d129c9180d4a0cff91ad | task=detection; scope=fully_generated; type=survey | 0 | Coordinates pending for: Bursa Technical University; Turkish National Defense University. |
| Learning Counterfactually Decoupled Attention for Open-World Model Attribution | Do CDAL’s open-world attribution benchmarks use naturally occurring image-generation traces to identify source generators beyond pure facial-manipulation attribution? Verify inputs, source labels and absence of injected signatures. | Section 2 distinguishes active injected fingerprints from passive attribution and identifies CDAL as passive. Section 4/Table 3 evaluates OSMA source labels over real images, 14 seen GAN classes, and 53 unseen GAN classes; OSMA includes ImageNet, LSUN, COCO, and Yosemite content beyond faces, while OW-DFA supplies face-swap and other generative-editing attacks. | EVIDENCE_CONFIRMS_SCOPE | MISSING_ADD | yes / curated:fe33db0fb528b93deddc | task=source_attribution; scope=fully_generated;generative_editing;deepfake; type=method | 1 | None |
| Language-Guided Hierarchical Fine-Grained Image Forgery Detection and Localization | Does the proposed unified detector independently evaluate the CNN-synthesized image domain as a substantive AI-image forensic task? The saved abstract stops before its method and evaluation. | Sections 4–5 construct the 13-method, 100,000-images-per-method HiFi-IFDL benchmark spanning fully synthetic and partial images. Section 5.4 independently trains a ProGAN detector and tests 18 methods including Stable Diffusion, Sora, Midjourney, DALL·E 3, and InstantID while the main system evaluates image detection and localization. | EVIDENCE_CONFIRMS_SCOPE | MISSING_ADD | yes / curated:614691667df5cf7a50f0 | task=detection;localization; scope=fully_generated;generative_editing;deepfake;traditional_manipulation; type=method;dataset;benchmark | 3 | None |

## Corpus impact

- Public papers: 648 → 657
- Published-only papers: 538 → 546
- Mapped papers: 632 → 637
- Map markers: 1,486 → 1494
- Actual papers added: 9
- Added papers awaiting coordinates: Abductive Corroboration of Probabilistic AI Models for Forensic Synthetic Media Detection; Conditional Uncertainty-Aware Political Deepfake Detection with Stochastic Convolutional Neural Networks; Deep Learning for CGI and Visual Forgery Detection: A Comprehensive Survey; Detecting Violent Deepfakes: Dataset and a Compact Attention Network with Multi-Scale Supervision

## Authoritative record changes

| Layer | Existing rows changed | Added rows |
|---|---:|---:|
| `papers.csv` | 0 | 9 |
| `paper_taxonomy.csv` | 0 | 9 |
| `author_institution_mappings.csv` | 0 | 15 |
| `institutions.csv` | 0 | 6 |
| `institution_location_review.csv` | 0 | 6 |
| `institution_locations.csv` | 0 | 0 |
| `institution_aliases.csv` | 0 | 0 |
| `institution_hierarchy.csv` | 0 | 0 |
| `paper_exclusions.csv` | 0 | 0 |
| `venue_aliases.csv` | 0 | 0 |
| Public paper records | 0 | 9 |
| Public marker records | 0 | 8 |

No institution aliases, confirmed locations, hierarchy edges, exclusion decisions, or frontend files changed. Six new institutions retain primary affiliation evidence in pending coordinate-review rows. Markerless papers remain visible in the paper list.

## Integrity and validation

All nine confirmed papers were reconciled against the pre-task 648-paper export and active exclusions by DOI, arXiv ID, OpenAlex ID, normalized title, alternate-version evidence, author/year/venue, method/acronym, and bounded fuzzy title. The final export has no duplicate scientific identity and no active-exclusion leak. The three out-of-scope results remain evidence-layer decisions and were not appended to `paper_exclusions.csv`.

Validation and deterministic-regeneration receipts are stored in `data/processed/systematic_tier2_high_priority_evidence_review_2026_09/`. Historical audit layers remain frozen. No commit or push was performed.
