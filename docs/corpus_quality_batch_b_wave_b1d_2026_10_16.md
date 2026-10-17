# Batch B Wave B1D — T579 task adjudication

The maintainer accepted and applied **T579: `detection;source_attribution` → `detection`** under locked T1. Exactly one original Batch B task action is resolved by decision `review:e28a216810f3dbb03546`. **T608 remains `EVIDENCE_STILL_INSUFFICIENT` with its current tasks unchanged and no terminal decision.** The retained labels are administrative preservation, not a scientific endorsement.

Original evidence baseline: `a74bdf79f4d8b3c4fb64af7b83701dce60238289`. Current publication predecessor: `8e60ee5729ab0b29703078b91cf83fb245048f6c`. The original two evidence-only artifacts are preserved byte-for-byte as gzip/base64 archives in the manifest, including their full scientific findings, retrieval history and provisional limits. Existing evidence was reused; adjudication performed no new scientific retrieval. The requested filenames retain `2026_10_16`; review and adjudication occurred on **2026-10-17, Asia/Shanghai**. Validation succeeded as recorded below. At artifact finalization, commit and verified remote publication remain subsequent Git gates; neither is claimed here.

## Locked rule and original questions

Locked T1, unchanged from `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json`:

> source_attribution does not imply detection. Assign detection only when the paper explicitly performs an authenticity / real-versus-generated task. Classification among already-synthetic generators is attribution only.

The intake report requires a complete experimental check; current labels, titles, abstract cues and generator-specific training sets cannot settle either action. At the preserved evidence-only baseline, both papers had `detection;source_attribution`, research type `method`, and were publicly included. The accepted T579 task correction below changes only its task set; T608 remains unchanged.

| Review | Canonical identity | Exact original review reason |
| --- | --- | --- |
| T579 | `doi:10.24963/ijcai.2023/52` | Multi-view image completion addresses cross-GAN binary detection, not a demonstrated generator-identification output. Verify the full evaluation before removal. |
| T608 | `doi:10.1109/lsp.2021.3130525` | Generator/domain labels supervise representation learning but the stated evaluated target is GAN-versus-pristine classification. Verify the full evaluation before removal. |

Both are source-derived records without persisted curated `paper_id` values; the DOI identities above are existing audit/taxonomy keys. No curated ID was invented. The complete original review rows and current public records are preserved in the manifest.

## T579 — complete primary-text finding

**Towards Robust Gan-Generated Image Detection: A Multi-View Completion Representation**, Chi Liu, Tianqing Zhu, Sheng Shen and Wanlei Zhou; DOI `10.24963/ijcai.2023/52`; IJCAI 2023 main track, pp. 464–472. The [official proceedings record](https://www.ijcai.org/proceedings/2023/52) identifies the work; the [official full manuscript](https://www.ijcai.org/proceedings/2023/0052.pdf) was retrieved once, HTTP200, nine pages, SHA256 `d998d16126393572799c7fa17fc401677befbed988dfa0d2b72029acc25bde23`. PDF title/author metadata and the first page match the canonical work. All nine pages were read; printed pp. 467–470, equations and Tables 1–5 were also visually checked. No arXiv version, supplement or code was retrieved; no cross-version equivalence is claimed.

**Output and training.** Section 3.3/equation 7 (p. 467) defines real as 0 and fake as 1. Three view-specific classifiers produce fake probabilities; inference averages them and thresholds at 0.5. Real-only completion restorers learn masked-image, gray-to-RGB and edge-to-RGB views. Subsequent Xception classifiers learn authenticity. The three views are not generator classes. This is a substantively evaluated binary forensic task, not merely real-image pretraining or a real class added to a source classifier.

**Data and protocol.** Sections 4.1–4.4/Table 1 (p. 468): the 128×128 detector trains on 60,000 CelebA real and 60,000 ProGAN fake images; tests use 6,000 real and 6,000 fake images per ProGAN/CramerGAN/SNGAN/MMDGAN source. At 1024×1024, ProGAN and StyleGAN detectors are trained independently, each with 25,000 CelebA-HQ real and 25,000 corresponding fake images. Tests use 2,500 real and 2,500 per source, including StyleGAN2 generated from a model pretrained on FFHQ. ProGAN/StyleGAN pretraining uses CelebA-HQ. These are source-domain transfer experiments, not a joint source-label classification protocol.

**Table 2 (p. 468), 128×128 authenticity performance.** Acc.=accuracy, A.P.=average precision; all values below are reported percentages, not rerun results.

| Test fake-source domain; training fake source=ProGAN | Acc. | A.P. |
| --- | ---: | ---: |
| ProGAN | 100.0 | 100.0 |
| CramerGAN | 91.1 | 89.2 |
| SNGAN | 80.2 | 83.3 |
| MMDGAN | 85.4 | 86.1 |

**Table 3 (p. 469), 1024×1024 authenticity performance.** P=ProGAN, S=StyleGAN, S2=StyleGAN2; arrows denote train-source → test-source, not the predicted class.

| Transfer setting | Acc. | A.P. |
| --- | ---: | ---: |
| P → P | 100.0 | 100.0 |
| S → S | 100.0 | 100.0 |
| P → S | 98.1 | 95.5 |
| S → P | 99.2 | 98.9 |
| P → S2 | 95.3 | 90.0 |
| S → S2 | 97.7 | 96.0 |

**Table 4 (p. 469), binary detection robustness.** The detector trains with CelebA/ProGAN and is evaluated with the listed perturbations of ProGAN samples. FGSM/PGD examples are crafted on vanilla Xception with epsilon 8/255. Common-manipulation settings are delegated by the paper to prior work; unreported JPEG/cropping/blur parameters and per-class aggregation details are not invented.

| Condition | Acc. | A.P. |
| --- | ---: | ---: |
| Clean | 100.0 | 100.0 |
| Blurring | 96.4 | 98.5 |
| Cropping | 98.2 | 99.1 |
| Compression | 93.8 | 96.9 |
| Noise | 94.7 | 94.4 |
| Mix | 91.3 | 94.4 |
| FGSM | 81.6 | 80.3 |
| PGD | 81.3 | 81.9 |
| SDN | 93.2 | 95.6 |

**Table 5 (p. 470)** reports the final binary detector's within-distribution 100.0/100.0, cross-GAN mean 85.6/86.2, and cross-perturbation mean 91.3/92.6 Acc./A.P. The view/module ablations remain authenticity evaluations.

**Attribution and contradictory cues.** Complete methods/evaluation review found no generator-ID prediction head, source-class loss, source confusion matrix or independently scored attribution metric for MCCL. GAN names label training/testing domains. Figure 5's known-source spectral curves and the GAN-fingerprint baseline do not establish an attribution endpoint. Results are not uniformly best: Table 3 P→S SRR 99.1/99.4 exceeds MCCL 98.1/95.5; Table 2 CramerGAN SRR has higher A.P. 95.1 than MCCL 89.2. These comparison limits do not weaken the existence of a substantive detection task.

**Accepted and applied outcome: `DETECTION_ONLY`. Current tasks: `detection`; removed task: `source_attribution`.** Scientific sufficiency: yes; confidence: high. Maintainer acceptance is complete for T579 only. Six scoped taxonomy/evidence fields were updated and one terminal review decision was appended; public inclusion, `method`, image scopes, canonical bibliography and all relationships remain unchanged. Evidence remains limited to the complete official proceedings main paper; no new source was retrieved and no scientific experiments were independently rerun during adjudication.

## T608 — primary-text accessibility limit

**Detection of GAN-Generated Images by Estimating Artifact Similarity**, Weichuang Li, Peisong He, Haoliang Li, Hongxia Wang and Ruimei Zhang; DOI `10.1109/lsp.2021.3130525`; stored IEEE Signal Processing Letters 2021 record. The [first-author homepage](https://www.waytron.net/) confirms the exact title and five authors. Its link labelled PDF actually targets the [IEEE document 9626582 identity page](https://ieeexplore.ieee.org/abstract/document/9626582); it is not a locally available author manuscript. The [author-linked implementation README](https://github.com/WeichuangLi/GASENet) identifies the same work but supplies no inspected scientific evaluation tables. Repository training/evaluation code was not inspected or run.

The single [IEEE full-text access attempt](https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=9626582&ref=) returned **HTTP 418**, HTML rather than PDF, on 2026-10-17 UTC. The failure response SHA256 is `a4deef7c02079c7b86f3d51c1ca075a6dba87425cf427e70cd83d3c5f44edf24`. **Zero full manuscripts were retrieved for T608; zero IEEE retries.** No title-page manuscript/version or publisher-final equivalence could be verified. Exact-title institutional discovery returned no results. A search-only ResearchGate request record and author poster appeared; neither was opened or adopted as complete scientific evidence. The coauthor homepage and implementation README did not supply a full manuscript.

Stored abstract-level descriptions mention a ResNet-50/shallow-instance-normalization embedding, artifact-similarity comparison, GAN/pristine categories and category/domain-aware loss. These motivate the review but do not verify its answer. In particular, source/domain labels could be supervision for representation learning; their mention does not establish an evaluated attribution output. Conversely, lack of accessible full text does not prove the absence of an attribution experiment.

| Required scientific check | Status after this wave |
| --- | --- |
| Actual output space and artifact-similarity decision rule | Unverified from complete primary text |
| Distinct real-image authenticity class and test negatives | Unverified |
| Substantive real/fake evaluation | Unverified beyond abstract claims |
| Explicit generator/model-identity prediction | Unverified |
| Independent attribution metrics | Unverified; no absence claim |
| Generator labels used only for training/domain generalization | Historical hypothesis remains unverified |
| Exact datasets, splits, tables, metrics and numeric results | Not available; no numbers transcribed from snippets or other papers |

**Provisional outcome: `EVIDENCE_STILL_INSUFFICIENT`. Proposed corrected taxonomy: none (`null`).** Current `detection;source_attribution` is preserved administratively, not endorsed scientifically from a title or abstract. Confidence is high in the evidence insufficiency, not in a detection-only or both-task classification. Remediation necessity cannot yet be determined; original T608 remains unresolved. An identity-matched complete original manuscript with methods and all evaluations is still required. No further retrieval is scheduled by this packet.

## Retrieval budget and source versions

| Review | Full-text attempts before interruption | Full-text attempts after resume | New full manuscripts obtained | Version/result |
| --- | ---: | ---: | ---: | --- |
| T579 | 0 | 1 | 1 | Official IJCAI 2023 proceedings PDF, 9 pages |
| T608 | 0 | 1 | 0 | IEEE HTTP 418 HTML; manuscript version unknown |
| **Total** | **0** | **2** | **1** | Maximum permitted:2 manuscripts, 1 per paper |

Nine metadata/source-discovery requests are separately recorded in the manifest:2 for T579, 7 for T608. They include the recovered same-page T579 metadata duplicate and the T608 author-HTML href recovery; they are not hidden as manuscript successes. Search-engine poster snippets were not used as quantitative evidence. No supplement, alternate manuscript version, dataset, model or experiment output was downloaded. Manuscript and temporary response bytes remain outside the repository; only their provenance, hashes and bounded scientific findings are in the two evidence artifacts.

## Applied correction and current accounting

The independent published commit `8e60ee5729ab0b29703078b91cf83fb245048f6c` adds 39 papers to the earlier 635-paper baseline. It was fetched and preserved before carrying the exact accepted T579 row and single terminal decision forward. The original a74 validation and scientific evidence remain historical receipts; current publication gates validate the integrated successor separately. Relative to this 674-paper predecessor, B1D changes only one paper and three existing map records; all other **673 papers and 1,407 map records** are identical. No upstream import, literature decision or scientific receipt was rewritten.

The standard offline refresh also synchronizes two generated reports that the upstream commit left at 635 papers: `data/manual/missing_author_mappings_report.csv` and `docs/missing_author_mappings_report.md`. They now describe the existing 674-paper public dataset. Exactly the 39 already-published import IDs are added to the report, no row is removed, and all 635 retained rows preserve every non-ranking value (634 priorities are renumbered). The Markdown is the exact canonical rendering of the audited CSV. These derived reports apply no author or institution mapping decision and are included so the standard refresh is reproducible.

The authoritative taxonomy row retains its existing DOI identity and empty persisted `paper_id`. Only `tasks`, `tasks_review_reason`, `tasks_evidence_tier`, `tasks_evidence_source`, `tasks_evidence_excerpt` and `audited_at` changed. Every other target-field token and unrelated taxonomy byte is preserved. The old task evidence is retained in the archived packet and exact application receipt. Review decisions retain their complete previous byte prefix, with one appended existing-schema `other` / `no_action_after_review` row documenting the correction already applied.

Current corpus: **674 public, 557 formal, 613 mapped, 1,410 relationships and 1,410 unique pairs**. No public paper or relationship was added or removed. Exactly one public record and its three existing map records changed only the approved task and task-review reason; all retained identities, mappings and unrelated records are identical.

Current taxonomy: **621 detection, 86 source attribution, 45 localization, 579 method, 134 dataset, 90 benchmark, 21 survey, 81 analysis study**. The only numerical change is source attribution −1.

Historical inventory remains **159 actions / 148 papers**. Seven original questions are now resolved: `L013`, `P139`, `P153`, `P490`, `R137`, `R611`, `T579`. **152 historical unresolved actions** remain, including the two excluded-paper questions L015/P562. **150 active-public unresolved actions / 139 papers** remain. T608, T526 and P526 remain pending. Batch C’s 13 deferred cases are unchanged.

## Validation and publication state

Current integrated state `8e60ee5729ab0b29703078b91cf83fb245048f6c`: **one full-suite execution and two sequential export verification passes** supply the publication gates. Earlier validation is preserved separately below.

Focused checks: **310 tests and 12 subtests passed**, zero failures/errors/skips.

Full repository suite: **1,885 tests and 389 subtests passed**, zero failures/errors/skips; **2 existing warnings**, matched to the two unchanged legacy return-value warning signatures.

All four current-scope validators completed with **zero errors**.

Two sequential offline export verification passes preserved **4,568 compared paths**, including **119** checksum-matched operational inputs and all **seven** deterministic outputs. `EXPORT_REPRODUCIBLE = 1`.

`FULL_SUITE_FAILURES = 0`

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

The pre-finalization integrity receipt passed **55 checks**, zero failures. It predates only these validation-receipt artifact edits; fresh read-only integrity and staged-byte checks remain mandatory. Scientific records, T608, archives, retrieval history, source hashes and accounting are unchanged by this finalization. No additional test or export was run here.

Historical pre-integration state `a74bdf79f4d8b3c4fb64af7b83701dce60238289`: **276 focused tests + 12 subtests; 1,851 full-suite tests + 389 subtests; two export verification passes** had already passed. Those receipts do not validate the subsequent remote integration. The task therefore records **two full-suite executions and four export verification passes across two separately identified states**, plus one initial offline export per state. No validation is concealed or counted twice.

**Publication status at artifact finalization:** validated locally; commit and verified remote publication are subsequent Git gates. Neither is claimed by this receipt.

The manifest embeds exact application, semantic-diff and recomputed-accounting receipts. It retains the 61-check evidence-only validation as historical evidence rather than presenting it as completed adjudication validation. Current source fingerprints are separate from the original 12 historical source hashes.

The primary checkout and concurrent work remain outside this wave’s write scope. Preserve all 128 protected primary files, 49 frozen NeurIPS artifacts, 119 operational inputs and all earlier published Batch B/Batch C receipts. Temporary scripts, manuscripts, response files and caches are operational inputs and are not publication artifacts. Stage only the explicit reviewed allowlist after validation; create one commit and publish only through a verified normal fast-forward.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
