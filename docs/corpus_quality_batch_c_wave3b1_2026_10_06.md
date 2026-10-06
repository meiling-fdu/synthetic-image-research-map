# Corpus Quality Batch C External Evidence and Adjudication — Wave 3B-1

Date: 2026-10-06

Scope: finalized locked T1 attribution-versus-detection review for T299, T446, T572, and T576 only. No research-type question was reviewed, and no corpus remediation was applied.

| Review | Paper | Primary source | Evaluated class space | Real-image role | Authenticity metric/task | Adjudication | Evidence result | Proposed taxonomy |
|---|---|---|---|---|---|---|---|---|
| T299 | *Detecting Origin Attribution for Text-to-Image Diffusion Models* | [Official WACV/CVF paper](https://openaccess.thecvf.com/content/WACV2025/papers/Xu_Detecting_Origin_Attribution_for_Text-to-Image_Diffusion_Models_WACV_2025_paper.pdf) | Balanced 13-way classifier: real plus 12 T2I generators; separate within-generator hyperparameter classifiers | Explicit thirteenth class using real MS-COCO images | The paper explicitly unifies real-vs-fake classification and attribution. Its joint classifier reports up to 90.96% 13-way accuracy and analyzes real/synthetic confusion; no separate binary metric is reported. | `DETECTION_TASK_SUPPORTED` | `EVIDENCE_RESOLVED_NO_CHANGE` | retain `detection;source_attribution` |
| T446 | *Are CLIP Features All You Need for Universal Synthetic Image Origin Attribution?* | [Authoritative arXiv full paper](https://arxiv.org/pdf/2408.09153) | Real plus known-generator classes; unseen synthetic generators form the rejected unknown class | Explicit Seen Real class using ImageNet; the stated decision is real versus generated, then known-source assignment or synthetic-unknown rejection | Closed-set accuracy evaluates Seen Real and Seen Fake classes. Open-set AUROC/OSCR concerns unseen-synthetic rejection and is not treated as authenticity evidence. | `DETECTION_TASK_SUPPORTED` | `EVIDENCE_RESOLVED_NO_CHANGE` | retain `detection;source_attribution` |
| T572 | *Open Set Synthetic Image Source Attribution* | [Official BMVC paper](https://papers.bmvc2023.org/0659.pdf) | Not established; official host was unreachable | Not established | Not established | `EVIDENCE_STILL_INSUFFICIENT` | `EVIDENCE_STILL_INSUFFICIENT` | none |
| T576 | *Single-Model Attribution of Generative Models Through Final-Layer Inversion* | [Official OpenReview paper](https://openreview.net/pdf?id=Hs9GcILuZN) | Not established; official PDF returned HTTP 403 | Not established | Not established | `EVIDENCE_STILL_INSUFFICIENT` | `EVIDENCE_STILL_INSUFFICIENT` | none |

## T299

The paper defines a joint forensic task rather than merely placing real images incidentally in an attribution dataset. It states that it unifies real-vs-fake classification and image attribution, uses a balanced real-plus-12-generator label space, and evaluates that joint classifier with accuracy and confusion analyses. Real images are therefore an explicit evaluated authenticity class. Under T1, detection remains supported even though the principal summary metric is 13-way accuracy rather than a separate binary score. Final result: `EVIDENCE_RESOLVED_NO_CHANGE`; retain `detection;source_attribution`.

## T446

The problem statement explicitly asks whether an image is real or generated and, for generated images, which known model produced it or whether it came from an unknown synthetic generator. Real ImageNet images form the Seen Real class. Closed-set accuracy covers Seen Real and Seen Fake labels. The paper's open-set AUROC and OSCR evaluate rejection of unseen synthetic generators, so those metrics are not used as proof of authenticity detection; detection is supported by the explicit integrated real/generated decision and its inclusion in the evaluated known-class classifier. Final result: `EVIDENCE_RESOLVED_NO_CHANGE`; retain `detection;source_attribution`.

## T572 and T576

The single permitted primary source for T572 could not be reached through the official BMVC host. The single permitted T576 OpenReview PDF returned HTTP 403. Per the retrieval stop rule, no alternate versions, supplements, or corroborating papers were opened. Both remain `EVIDENCE_STILL_INSUFFICIENT`, with no proposed taxonomy change.

## Resolution

- `DETECTION_TASK_SUPPORTED = 2`
- `ATTRIBUTION_ONLY_NO_DETECTION = 0`
- `EVIDENCE_STILL_INSUFFICIENT = 2`
- `EVIDENCE_RESOLVED_NO_CHANGE = 2`
- External Batch C unresolved: `28 → 26`
- Remaining task evidence: `12 → 10`
- Institution evidence remains 1; research-type evidence remains 15.
- T527 is outside this external-evidence count and was not touched.

Four primary-document URLs were attempted, exactly one per paper. Two yielded usable task evidence. No source copy, search page, alternate paper version, or separate supplement is stored in the repository. Corpus and taxonomy data remain unchanged.
