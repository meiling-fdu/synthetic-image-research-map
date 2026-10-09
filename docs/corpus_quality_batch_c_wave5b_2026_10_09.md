# Batch C Wave 5B — finalized adjudication

Evidence review and maintainer adjudication: 2026-10-09. Published starting baseline: `70a0bd330b76a493597c53f6117dcfa18f2a3c4e` (`fix: adjudicate corpus quality batch-c wave five-a`). This wave examines exactly T236 and T137. The sole approved scientific metadata correction adds `localization` to T236; T137 retains its current tasks. Prior evidence, T527, and all other authoritative metadata remain unchanged.

## Source coverage and identity

Exactly two alternative author-deposited full papers were read, one per case, after checking their arXiv abstract records against local canonical identities. The full papers are their arXiv HTML renderings, including material embedded in the same manuscript's appendices. The inaccessible first-pass OpenReview and CVF PDFs were not retried. No other paper, separate supplement, alternative full-paper version, mirror, or secondary summary was retrieved; no broad search was run. No source text was saved in the repository.

| Review | Canonical identity | First pass | Alternative source and identity |
| --- | --- | --- | --- |
| T236 | `curated:64635535d7b7b6a12a32`; *Unveiling Perceptual Artifacts: A Fine-Grained Benchmark for Interpretable AI-Generated Image Detection*; ICLR 2026, [OpenReview forum](https://openreview.net/forum?id=Tk8ujiOgHM) | [Official final PDF](https://openreview.net/pdf/6b5a5d6411ea1778f8c2cbf707a8a5744abe71b0.pdf): `ACCESS_BLOCKED_OPENREVIEW_CHALLENGE_TIMEOUT` | [arXiv record](https://arxiv.org/abs/2601.19430) and [full author manuscript v1](https://arxiv.org/html/2601.19430v1), dated 2026-01-27: exact title, all 11 ordered authors after normalizing capitalization of Jiahao Chen, abstract, and canonical arXiv ID match. This establishes the same work; byte-for-byte or scientific equivalence to the inaccessible ICLR final version is unverified. |
| T137 | `curated:246f07c81b9f91e527eb`; *IncreFA: Breaking the Static Wall of Generative Model Attribution*; CVPR 2026 | [Official CVF final PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Qin_IncreFA_Breaking_the_Static_Wall_of_Generative_Model_Attribution_CVPR_2026_paper.pdf): `TRANSFER_STALLED_BOUNDED_WAIT_EXCEEDED` | [arXiv record](https://arxiv.org/abs/2604.17736) and [full author manuscript v2](https://arxiv.org/html/2604.17736v2), dated 2026-04-21: exact title, canonical arXiv ID, matching abstract, five canonical authors in order, and the arXiv record's “Accepted to CVPR 2026” statement identify the same work. The arXiv v2 author block also includes **Yuexuan Tan** between Yueying Gao and Lei Chen, whereas the canonical field has five authors. This 5/6 difference was already recorded in `docs/missing_author_mappings_audit_2026-08-27.md`; it is documented here without changing either metadata source. Equivalence to the inaccessible CVF final PDF is unverified. |

The arXiv manuscripts are primary sources for the scientific observations below. Their version limits remain explicit in this final adjudication, and the identity checks go beyond title similarity. The exact retrieval outcomes and evidence locators are in the [Wave 5B manifest](../data/raw/corpus_quality_batch_c_wave5b_2026_10_09/evidence_manifest.json).

## T236 — T2 localization versus interpretation

Locked T2 requires an **explicitly performed and quantitatively evaluated spatial forensic prediction**. Pixel annotations, saliency, attention, or explanation heatmaps alone do not qualify.

The [full author manuscript](https://arxiv.org/html/2601.19430v1) makes this distinction possible. Section 3.3 formally divides interpretable AI-generated image detection into Authenticity Judgment (AJ), a binary real/fake label, and Perceptual Artifact Detection (PAD), which predicts each artifact instance's region and one of seven categories. Section 3.2 describes human polygon masks and category ground truth. Section 5 evaluates a PAD-only model and a jointly trained AJ/PAD model. Appendix B.2 specifies semantic segmentation heads, multiclass loss with a background class and seven artifact classes, and a predicted pixel-level mask at inference. These are model outputs; they are not merely the dataset's annotations or post hoc saliency.

Section 3.3 and appendix A.5 specify overlap-based scoring against annotated regions: IoU, pixel precision, pixel recall, pixel F1, and weaker instance matching. Table 2 reports category-agnostic PAD **IoU 27.2 / PixF1 42.7** for PAD-only and **IoU 27.3 / PixF1 42.8** for the multi-task model, in the paper's reported units. Table 3 breaks down pixel precision/recall by artifact category. Existing AIGI detectors' binarized Grad-CAM or relevance maps, and section 6's attention-alignment experiment, are separate interpretation analyses; those alone would not establish a localization task. The dedicated PAD segmentation output and spatial scores do.

**T2 final adjudication: `LOCALIZATION_TASK_SUPPORTED`; resolution `EVIDENCE_RESOLVED_CHANGE`; remediation `APPLIED` (`REMEDIATION_APPLIED`).** The authoritative T236 tasks and compatibility field now read `detection;localization`, adding only `localization`. Confidence is high for the spatial task in arXiv v1. Scope limit: the predicted regions are perceptual artifacts in generated images, not necessarily composited manipulation regions; the inaccessible ICLR final version could differ.

## T137 — T1 detection versus generator attribution

Locked T1 requires substantive, evaluated real-versus-generated authenticity discrimination. A real class inside attribution, or rejection of an unknown synthetic generator, does not suffice alone.

The [full author manuscript](https://arxiv.org/html/2604.17736v2) defines a source-model task in section 3.1 with decision space `{real, known generators, unseen generator}`. Figure 2 describes a top-level real/fake/unseen split and generator-family attribution beneath fake. In section 5.1, incremental protocol EP1 starts with real images and one generator, then adds synthetic generators; Nano-Banana and Imagen3 are withheld as **unknown synthetic generators**, not real examples. Real images come from COCO (appendix dataset description). The open-set confidence threshold in section 4.4 rejects unknown generators. Its unseen-generator metric is therefore attribution/open-set evidence, not authenticity evidence.

The paper also makes a separate, explicit authenticity claim and measurement. Section 5.1 says static protocol EP2 assesses **attribution and authenticity recognition** and defines `Auth. Acc.` as accuracy for distinguishing real from generated images. Table 2 reports **99.97% Auth. Acc.** for IncreFA and a **99.66% real-class accuracy** row. Table 1 reports **99.97% Auth. Acc.** in the incremental comparison. The explicit real-versus-generated metric, rather than real-class inclusion alone, supports detection. Separately, Table 1 gives **78.80%** final-task generator attribution accuracy and **98.93%** unseen-synthetic-generator accuracy; Table 2 gives **95.93%** average static attribution accuracy and **98.78%** unseen-generator accuracy. These attribution/open-set numbers are not counted as real/fake detection results.

**T1 final adjudication: `DETECTION_TASK_SUPPORTED`; resolution `EVIDENCE_RESOLVED_NO_CHANGE`; remediation `NOT_REQUIRED` (`REMEDIATION_NOT_REQUIRED`).** T137 retains `detection;source_attribution` with no authoritative data change. Confidence is high for the explicit authenticity metric in arXiv v2 and same-work identity. The six-versus-five author difference and unexamined CVF final text remain visible provenance limits; no author remediation is part of this wave.

## Resolution accounting

Both cases were **scientifically resolved by second-pass evidence**; zero remain evidence-insufficient in this wave. The maintainer accepted the single T236 label addition and T137 no-change disposition. Evidence resolution had already reduced the ledger before remediation, so the T236 edit does **not** subtract either case a second time. Final Batch C accounting is:

| Measure | Before Wave 5B | After accepted adjudication |
| --- | ---: | ---: |
| Task evidence | 5 | 3 |
| Institution evidence | 1 | 1 |
| Research-type evidence | 11 | 11 |
| External unresolved | 17 | 15 |
| T527 separate maintainer scope judgment | 1 | 1 |
| Total unresolved | 18 | 16 |

The remaining task evidence cases are T141, T572, and T503. U010 and the eleven research-type debts remain untouched. T527 remains `SCOPE_OR_TASK_EVIDENCE_REQUIRED` with its current labels. All earlier evidence debt remains in its prior manifests; this review does not retroactively mark a previous wave remediated.

## Authoritative and export effect

The T236 record alone changes in `data/curated/paper_taxonomy.csv`: `tasks`, task-review reason, evidence tier/source/excerpt, and audit date. Its `tasks` compatibility field alone changes in `data/curated/papers.csv`. Each physical CSV row is updated without rewriting unrelated rows or the 16 embedded CRLF sequences. T137's complete authoritative rows are unchanged. The T236 source is the identity-matched author-deposited arXiv v1 manuscript; byte-level equivalence to the inaccessible ICLR final PDF was not verified.

| Corpus measure | Before | After |
| --- | ---: | ---: |
| Public | 639 | 639 |
| Formal | 531 | 531 |
| Mapped | 617 | 617 |
| Relationship rows | 1,421 | 1,421 |
| Unique pairs | 1,421 | 1,421 |

| Taxonomy label | Before | After |
| --- | ---: | ---: |
| Detection | 589 | 589 |
| Source attribution | 85 | 85 |
| Localization | 42 | 43 |
| Method | 547 | 547 |
| Dataset | 132 | 132 |
| Benchmark | 88 | 88 |
| Survey | 20 | 20 |
| Analysis study | 78 | 78 |

## Validation and integrity

Validation in isolated worktree `codex/batch-c-wave5b-adjudication` passed: **60 focused tests and 12 subtests**, then **1,689 full-suite tests and 389 subtests**, with zero failures and the two existing pytest warnings. Curated, public, exclusion, and key-paper-coverage validators returned **zero errors**; their existing warning counts were 252, 23, and 2 respectively. The two established offline export passes each exited successfully and changed none of 4,283 tracked or visible untracked paths: `EXPORT_REPRODUCIBLE = 1`.

The 104 required ignored offline-export inputs and 15 historical test fixtures were copied into the isolated worktree with matching SHA-256 checksums; none are staged for publication. The final scope audit finds `UNEXPECTED_CHANGED = 0`, `FROZEN_NEURIPS_CHANGED = 0`, `PREEXISTING_LOCAL_FILES_CHANGED = 0`, and `IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`. In the primary checkout, the original Wave 5B evidence and all 128 excluded local files remain byte-identical and unmodified by this wave. Three frontend files independently progressed after the initial snapshot (`tests/public_explorer_browser.cjs`, `tests/test_frontend_explorer_facets.py`, and `web/app.js`); those changes are expressly outside the protected scientific/evidence comparison and were neither copied nor edited here.

At validation freeze, a fresh fetch placed `origin/main` at `f7e6f721dcca4c992285a86f3fc75706d6d3f091` (`feat: improve scholarly exploration workflow`), one commit after the Wave 5A baseline. Its ten changed paths are frontend or frontend tests and have no path overlap with Wave 5B. This report records the validated pre-publication state; the Wave 5B commit and remote verification are performed separately. No paper was retrieved during adjudication.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
