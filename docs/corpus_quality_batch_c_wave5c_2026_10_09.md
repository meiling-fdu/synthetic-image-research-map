# Batch C Wave 5C — second-pass task evidence

Evidence date: 2026-10-09. Published starting baseline: `805edcc5bbd2fb5c1afda348e900f32f02fcd450`. This review covers exactly T572 and T503 under locked T1. The maintainer-approved T1 dispositions have been applied to the two authoritative task rows and their deterministic public exports; identity, publication, institution, research-type, and other scientific metadata remain unchanged. The original official BMVC/CVF first-pass failures were preserved and not retried. Exactly two author-deposited full manuscripts were read, one per case, after identity checks on their arXiv abstract records. No supplements, alternate full-paper versions, mirrors, secondary summaries, or unrelated papers were retrieved, and no manuscript text was stored in the repository.

## Identity, provenance, and version limits

| Case | Canonical identity | First pass | Second-pass primary manuscript |
| --- | --- | --- | --- |
| T572 | `curated:5a91cc922c8a3c4c3d0c`; *Open Set Synthetic Image Source Attribution*; Shengbang Fang, Tai D. Nguyen, Matthew C. Stamm; BMVC 2023 | [Official BMVC paper](https://papers.bmvc2023.org/0659.pdf): `HOST_UNREACHABLE_DNS_AND_BROWSER_502` in Wave 3B-1 | [arXiv record](https://arxiv.org/abs/2308.11557) and [complete author manuscript v1](https://arxiv.org/html/2308.11557v1), submitted 2023-08-22. Title, ordered authors, arXiv ID, abstract, and locally recorded BMVC same-work review match. Textual equivalence with the inaccessible BMVC final PDF is unverified. |
| T503 | `curated:34fdf09ae334914a2723`; *ManiFPT: Defining and Analyzing Fingerprints of Generative Models*; Hae Jin Song, Mahyar Khayatkhoei, Wael AbdAlmageed; CVPR 2024 | [Official CVF paper](https://openaccess.thecvf.com/content/CVPR2024/papers/Song_ManiFPT_Defining_and_Analyzing_Fingerprints_of_Generative_Models_CVPR_2024_paper.pdf): `ACCESS_BLOCKED_HTTP_403` in Wave 3B-3 | [arXiv record](https://arxiv.org/abs/2402.10401) and [complete author manuscript v2](https://arxiv.org/html/2402.10401v2), revised 2024-02-29. Exact title, ordered authors, arXiv ID, and abstract match; the arXiv record states acceptance to CVPR 2024. Textual equivalence with the inaccessible CVF final PDF is unverified. |

The locked T1 rule is: `source_attribution does not imply detection. Assign detection only when the paper explicitly performs an authenticity / real-versus-generated task. Classification among already-synthetic generators is attribution only.` In particular, unseen-generator rejection and the mere presence of a Real class inside an attribution classifier are not by themselves detection evidence.

## T572 — known and unseen synthetic generators

The [arXiv v1 manuscript](https://arxiv.org/html/2308.11557v1) claims open-set **source attribution**, not an authenticity classifier. Section 3 defines a nearest-reference candidate source `S(x)` and a distance-threshold rejection rule `R(x)` (equations 5 and 8). Its outputs are one of the known generator architectures or an unknown generator. Section 4.1 and Table 1 use seven image generators; five supply seen classes, while StyleGAN and Stable Diffusion are held out as unseen **synthetic** architectures. Natural-image datasets train the generators, and camera-model identification pretraining initializes the embedding network. Neither makes authentic images a scored class in this source-attribution protocol.

Section 4.3 evaluates average F1 over the five seen generators and correct reject rate (CRR) for unseen synthetic generators (equations 9–10). Table 2 reports a best pretrained AUC of the average-F1–CRR curve of **0.868**; Table 3 reports **0.900** seen-generator average F1 and **0.645** unseen-generator CRR for the proposed method. These are source-identity and unseen-generator metrics. Sections 4.1–4.5 do not define or report a real-versus-generated decision or authenticity metric. The synthetic-generator rejection score cannot stand in for detection.

**Final T1 adjudication: `ATTRIBUTION_ONLY_NO_DETECTION`; evidence outcome `EVIDENCE_RESOLVED_CHANGE`; remediation `APPLIED`.** Tasks changed from `detection;source_attribution` to `source_attribution`. Confidence is high for the arXiv v1 protocol; its equivalence to the inaccessible BMVC final PDF remains unverified.

## T503 — real class inside multiclass attribution

The [arXiv v2 manuscript](https://arxiv.org/html/2402.10401v2) states that its contribution is defining artifacts/fingerprints and differentiating generative models. Sections 1–2 contrast that goal with prior binary real-versus-synthetic detectors. Figure 3 and section 3.4 define a ResNet50-based **model attributor** trained with multiclass cross-entropy. Real samples estimate the natural-image manifold; section 4.2's evaluation protocol also includes `0=Real` beside `1..M` generator identities in four attribution datasets. Thus the classifier can output Real, a fact this review does not erase.

The paper evaluates that classifier as **model attribution**. Section 4.2 and Table 2 report aggregate multiclass source accuracy and feature-space separability, including **74.7%** accuracy for ManiFPT-SSL on GM-CelebA and **72.018%** for ManiFPT-SL on GM-CIFAR10. These are not binary detection accuracies. Section 4.4/Table 4 evaluates cross-dataset attribution (for example **66.3%** ManiFPT-SSL from GM-CIFAR10 to GM-CelebA); section 4.5 and appendix D analyze fingerprint clustering. The manuscript does not report a binary authenticity protocol, real-class accuracy/recall, real-versus-synthetic AUC, or authenticity confusion analysis. Appendix A explicitly distinguishes its multiclass attribution dataset from datasets designed for binary real/synthetic discrimination.

**Final T1 adjudication: `ATTRIBUTION_ONLY_NO_DETECTION`; evidence outcome `EVIDENCE_RESOLVED_CHANGE`; remediation `APPLIED`.** Tasks changed from `detection;source_attribution` to `source_attribution`. The Real class makes a real prediction possible, but aggregate source-attribution accuracy does not establish the distinct, substantively evaluated authenticity task required by T1. The Real source class remains documented; the paper does not separately evaluate an authenticity task. Confidence is moderate-high for the arXiv v2 evaluation and this T1 distinction. Exact equivalence with the inaccessible CVF final PDF remains unverified.

## Evidence accounting and preservation

Both cases are scientifically resolved for the author-deposited manuscripts, and both approved taxonomy remediations are applied. Evidence debt was subtracted once at the evidence stage and is unchanged by remediation:

| Measure | Before | After adjudication |
| --- | ---: | ---: |
| Task evidence | 3 | 1 (T141) |
| Institution evidence | 1 | 1 (U010) |
| Research-type evidence | 11 | 11 |
| External unresolved | 15 | 13 |
| T527 separate scope judgment | 1 | 1 |
| Total unresolved | 16 | 14 |

The public corpus remains **639 public, 531 formal, 617 mapped, 1,421 relationship rows, and 1,421 unique paper–institution pairs**. Detection changes **589 → 587**; source attribution 85, localization 43, method 547, dataset 132, benchmark 88, survey 20, and analysis study 78 remain unchanged. Only T572 and T503 scientific task fields and task provenance change, with corresponding public export records. T141, T527, U010, and all 11 research-type debts remain open; external unresolved 13, total unresolved 14. The published Wave 5B receipt retains its original 589-detection baseline.

## Validation and publication

Validation passed in the isolated worktree: **5 Wave 5C focused tests and 4 targeted historical-boundary tests passed**; the full suite passed **1,700 tests and 389 subtests**, with **zero failures and two existing warnings**. Current-scope curated, public, exclusion, and key-paper-coverage validators returned **zero errors** (existing warning counts: 252, 23, and 2 respectively). The historical Batch A replay validator is restricted to its original delta and is not claimed as a current-corpus validator. Two authorized offline export passes exited successfully and changed none of **4,288** tracked or visible untracked paths: `EXPORT_REPRODUCIBLE = 1`. Generated export hashes are recorded in the manifest. No additional retrieval was made during adjudication.

The approved file-level and semantic diff contains exactly the T572/T503 task and provenance corrections and their deterministic outputs, the Wave 5C evidence record, focused regression coverage, and narrowly required historical test boundaries. The frozen NeurIPS 49-file set and the primary checkout's 128 excluded files matched their checksum receipts. No production frontend file was modified by Wave 5C; independently published frontend successors `f7e6f72` and `ef0d93f` are recognized by the historical test guard. `UNEXPECTED_CHANGED = 0`; `FROZEN_NEURIPS_CHANGED = 0`; `PREEXISTING_LOCAL_FILES_CHANGED = 0`; `IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`. After rebasing onto independently published frontend commit `ef0d93f`, all 19 Wave 5C file blobs matched their pre-rebase contents. A combined post-rebase run passed **113 focused tests and 3 subtests** covering Wave 5C, the historical snapshot guard, and the changed frontend. The full suite was not repeated because Wave 5C scientific/generated files and exporter code were unchanged by the frontend-only rebase. The isolated commit and remote SHA are verified after publication, so this committed evidence does not pre-assert a push outcome.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
