# Batch C evidence-debt triage — 2026-10-08

## Executive summary

Wave 4F is already published as `0f859a4c6221cafca8463b7828267b0fa8605030` (`docs: add batch-c wave four-f evidence`). Local `main` and the previously fetched `origin/main` are synchronized at `0 / 0`. No publication was repeated for this continuation. This report is evidence planning only and remains untracked, unstaged, uncommitted and unpushed.

**19 external evidence debts remain: 7 task, 11 research-type and 1 institution review. One separate maintainer scope case brings the total to 20 unresolved.** All 15 research-type cases received a first-pass attempt: 1 resolved change (R099), 3 resolved without change (R127, R189, R190), 11 insufficient, and 0 never reviewed. This triage resolves no scientific question.

The existing `/tmp/batch-c-debt-triage-input.json` and `/tmp/batch-c-debt-local-candidates.json` were reused. The completed local inventory and targeted source-record audit identified no identity-matched preserved full paper suitable for recheck. Its earlier PDF screening used metadata/first pages and is not a claim that every page of every historical file was scientifically reviewed. Abstracts, bibliographic records, citations, publisher listings and historical affiliation notes do not answer the outstanding full-text questions. No new broad archive scan, second-pass retrieval, browser request or external API request was performed.

Inventory authority: `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json` (approved policies/residual ledger), the successive committed evidence manifests cited below, and `data/raw/corpus_quality_batch_c_wave4f_2026_10_08/evidence_manifest.json` (`research_type_coverage`). Current assignments come from the canonical public records, reconciled with `data/curated/paper_taxonomy.csv`; historical suggested labels are not applied.

## Complete evidence-debt table

Priorities below order external follow-up by forensic-task correctness, research-type correctness, institution mapping correctness, then feasibility within those groups. The separate scope decision takes overall precedence. Every external review appears exactly once in this inventory. Current assignments are preserved; each scientific status remains `EVIDENCE_STILL_INSUFFICIENT`, independently of source feasibility.

| Priority | Review | Paper and current authoritative assignment | Policy | Missing evidence / original failure | Source candidate | Next-action category | Scientific conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | T576 | Single-Model Attribution of Generative Models Through Final-Layer Inversion<br>`curated:62b0a9ae8be24d9f02e0`<br>tasks: `detection;source_attribution`; types: `method` | T1 | Full task definition, real-image role, decision rule and scored real-versus-generated evaluation; model membership/non-membership alone does not establish detection.<br>First attempt: `ACCESS_BLOCKED_HTTP_403` ([target](https://openreview.net/pdf?id=Hs9GcILuZN)). | [PMLR / mlresearch proceedings PDF](https://raw.githubusercontent.com/mlresearch/v235/main/assets/laszkiewicz24a/laszkiewicz24a.pdf) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 2 | T611 | Does a GAN Leave Distinct Model-Specific Fingerprints?<br>`curated:07ee620b8169b67b900f`<br>tasks: `detection;source_attribution`; types: `method` | T1 | Full class definitions and evaluation showing an authentic/real-versus-GAN decision beyond model-specific fingerprint/source identification.<br>First attempt: `UNSAFE_REDIRECT_TO_UNRELATED_DOMAIN_NONRETRYABLE` ([target](https://www.bmvc2021-virtualconference.com/assets/papers/0197.pdf)). | [BMVA official BMVC proceedings record](https://www.bmva.org/bmvc/2021/conference/papers/paper_0197.html) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 3 | T236 | Unveiling Perceptual Artifacts: A Fine-Grained Benchmark for Interpretable AI-Generated Image Detection<br>`curated:64635535d7b7b6a12a32`<br>tasks: `detection`; types: `method` | T2 | A model-produced spatial mask, patch, box or equivalent prediction, corresponding ground truth and quantitative spatial scoring; artifact annotations or attention alignment alone are insufficient.<br>First attempt: `ACCESS_BLOCKED_OPENREVIEW_CHALLENGE_TIMEOUT` ([target](https://openreview.net/pdf/6b5a5d6411ea1778f8c2cbf707a8a5744abe71b0.pdf)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2601.19430) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 4 | T137 | IncreFA: Breaking the Static Wall of Generative Model Attribution<br>`curated:246f07c81b9f91e527eb`<br>tasks: `detection;source_attribution`; types: `method;dataset` | T1 | Incremental/open-set class definitions and evaluation showing whether real/authentic images form an evaluated forensic class, rather than only known/unknown generator identities.<br>First attempt: `TRANSFER_STALLED_BOUNDED_WAIT_EXCEEDED` ([target](https://openaccess.thecvf.com/content/CVPR2026/papers/Qin_IncreFA_Breaking_the_Static_Wall_of_Generative_Model_Attribution_CVPR_2026_paper.pdf)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2604.17736) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 5 | T503 | ManiFPT: Defining and Analyzing Fingerprints of Generative Models<br>`curated:34fdf09ae334914a2723`<br>tasks: `detection;source_attribution`; types: `method` | T1 | A real-versus-generated decision and detection-specific evaluation distinct from fingerprint/model identification experiments.<br>First attempt: `ACCESS_BLOCKED_HTTP_403` ([target](https://openaccess.thecvf.com/content/CVPR2024/papers/Song_ManiFPT_Defining_and_Analyzing_Fingerprints_of_Generative_Models_CVPR_2024_paper.pdf)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2402.10401) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 6 | T572 | Open Set Synthetic Image Source Attribution<br>`curated:5a91cc922c8a3c4c3d0c`<br>tasks: `detection;source_attribution`; types: `method` | T1 | The actual open-set class space, role of real images and scored authenticity decision; rejecting an unknown generator is not sufficient.<br>First attempt: `HOST_UNREACHABLE_DNS_AND_BROWSER_502` ([target](https://papers.bmvc2023.org/0659.pdf)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2308.11557) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 7 | T141 | Learning a Semantic Similarity Orthogonal Space for Model-Level AI-Generated Image Source Attribution<br>`curated:268336295435cfbbbd5d`<br>tasks: `detection;source_attribution`; types: `method` | T1 | A real-versus-generated protocol and results beyond reconstruction/semantic matching for model-level attribution.<br>First attempt: `ACCESS_BLOCKED_HTTP_403` ([target](https://onlinelibrary.wiley.com/doi/pdf/10.1111/exsy.70359)). | No defensible different primary target established locally | `BLOCKED_PENDING_AUTHORITATIVE_EVIDENCE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 8 | R535 | Which Model Generated This Image? A Model-Agnostic Approach for Origin Attribution<br>`curated:98c0322e2f8dd41d3e9e`<br>tasks: `source_attribution`; types: `method;dataset` | R1 | Contribution and dataset sections specifying a newly contributed reusable data resource, its size/composition and release/reuse role, rather than few-shot OCC-CLIP evaluation collections.<br>First attempt: `PRIMARY_PDF_REDIRECTED_TO_SUBSCRIPTION_PREVIEW` ([target](https://link.springer.com/content/pdf/10.1007/978-3-031-73033-7_16.pdf)). | [ECVA official ECCV archive](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07930.pdf) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 9 | R117 | Frequency-Aware Robustness Analysis of Deepfake Detection Models<br>`curated:748ed5e2cf27aea70f6a`<br>tasks: `detection`; types: `method` | R4 | Contribution list and FSI specification/mechanism, novelty and evaluation sufficient to distinguish a substantive technical method from a study measurement.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_INACCESSIBLE` ([target](https://doi.org/10.32604/jai.2026.078014)). | [Tech Science Press publisher PDF and record](https://cdn.techscience.cn/files/jai/2026/8-6/TSP_JAI_78014/TSP_JAI_78014.pdf) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 10 | R549 | Deepfake Generation and Detection: Case Study and Challenges<br>`curated:616984c24ff3792431e6`<br>tasks: `detection`; types: `method` | R4 | IBMM technical specification, contribution claim and supporting evaluation distinguishing an original method from an illustrative case within a survey/study.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_INACCESSIBLE` ([target](https://doi.org/10.1109/access.2023.3342107)). | [Cape Peninsula University of Technology institutional deposit](https://digitalknowledge.cput.ac.za/bitstream/11189/9706/1/Deepfake_Generation_and_Detection.pdf) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 11 | R176 | PRADA: Probability-Ratio-Based Attribution and Detection of Autoregressive-Generated Images<br>`curated:f6ad15b01df18aadfe1a`<br>tasks: `detection;source_attribution`; types: `method;dataset` | R1 | Explicit newly contributed data resource, construction, size/composition and release/reuse evidence, beyond PRADA detector/attributor evaluation.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR_NONRETRYABLE` ([target](https://openaccess.thecvf.com/content/CVPR2026F/papers/Damm_PRADA_Probability-Ratio-Based_Attribution_and_Detection_of_Autoregressive-Generated_Images_CVPRF_2026_paper.pdf)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2511.20068) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 12 | R455 | Deep Image Fingerprint: Towards Low Budget Synthetic Image Detection and Model Lineage Analysis<br>`curated:04932cb03f767948ddf4`<br>tasks: `detection`; types: `method;dataset` | R1 | Explicit reusable dataset contribution and construction/release evidence, beyond detector and model-lineage experiments assembled for the paper.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR_NONRETRYABLE` ([target](https://openaccess.thecvf.com/content/WACV2024/papers/Sinitsa_Deep_Image_Fingerprint_Towards_Low_Budget_Synthetic_Image_Detection_and_WACV_2024_paper.pdf)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2303.10762) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 13 | R537 | X-Transfer: A Transfer Learning-Based Framework for GAN-Generated Fake Image Detection<br>`doi:10.1109/ijcnn60899.2024.10650566`<br>tasks: `detection`; types: `method;analysis_study` | R3 | Independent scientific analysis questions, design and findings beyond transfer-learning framework validation/ablations.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR` ([target](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10650566)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2310.04639) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 14 | R548 | DE-FAKE: Detection and Attribution of Fake Images Generated by Text-to-Image Generation Models<br>`doi:10.1145/3576915.3616588`<br>tasks: `detection;source_attribution`; types: `method;benchmark;analysis_study` | R2 | A reusable evaluation framework with defined task/protocol, datasets, metrics and comparative baselines, rather than experiments evaluating DE-FAKE itself.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_INACCESSIBLE` ([target](https://dl.acm.org/doi/pdf/10.1145/3576915.3616588)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2210.06998) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 15 | R580 | Towards Universal Fake Image Detectors That Generalize Across Generative Models<br>`curated:1ef55e4fc03eb4880beb`<br>tasks: `detection`; types: `method;dataset` | R1 | Explicit newly contributed reusable data resource and its contents/release role, rather than evaluation on existing generated-image collections.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR` ([target](https://openaccess.thecvf.com/content/CVPR2023/papers/Ojha_Towards_Universal_Fake_Image_Detectors_That_Generalize_Across_Generative_Models_CVPR_2023_paper.pdf)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2302.10174) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 16 | R615 | Towards Discovery and Attribution of Open-world GAN Generated Images<br>`doi:10.1109/iccv48922.2021.01383`<br>tasks: `detection;source_attribution`; types: `method;analysis_study` | R3 | Independent open-world discovery/attribution analysis questions and findings beyond evaluating the proposed method.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_FORBIDDEN_403` ([target](https://openaccess.thecvf.com/content/ICCV2021/papers/Girish_Towards_Discovery_and_Attribution_of_Open-World_GAN_Generated_Images_ICCV_2021_paper.pdf)). | [arXiv author-deposited manuscript record](https://arxiv.org/abs/2105.04580) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 17 | R460 | Detecting AI Generated Images Through Texture and Frequency Analysis of Patches<br>`doi:10.1109/aivrv63595.2024.10860248`<br>tasks: `detection`; types: `method;analysis_study` | R3 | Independent texture/frequency/patch analysis questions, experimental design and findings beyond classifier performance validation.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR` ([target](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10860248)). | [IEEE Xplore official paper record](https://ieeexplore.ieee.org/document/10860248/) — `NOT_TESTED` | `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 18 | R376 | No Detector to Rule Them All<br>`curated:cda6067db322246e8195`<br>tasks: `detection`; types: `method` | R4 | An ensemble specification and claimed technical novelty, scientific role and supporting evaluation distinguishing a new method from exploratory baseline combinations.<br>First attempt: `PRIMARY_DOCUMENT_RETRIEVAL_FORBIDDEN_403` ([target](https://dl.acm.org/doi/pdf/10.1145/3746265.3759659)). | No defensible different primary target established locally | `BLOCKED_PENDING_AUTHORITATIVE_EVIDENCE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |
| 19 | U010 | Diffusion-Driven Forgery Detection: Distilling Latent Features for Generalized Image Forensics<br>`curated:d0eec7c4fce8929c295a`<br>tasks: `detection`; types: `method`; institution: SUES review candidate for Kaiwen Qian, Yutao Xu, Yifan Xu and Yuchun Fang; `mapping_status=needs_review`; raw affiliation names Shanghai University; public map rows = 0 | I1 | Complete paper-time author names, superscript markers and affiliation block distinguishing Shanghai University, SUES or dual affiliations for all four authors.<br>First attempt: `HTTP_418_UNUSABLE` ([target](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=11494515)). | No defensible different primary target established locally | `BLOCKED_PENDING_AUTHORITATIVE_EVIDENCE` | `EVIDENCE_STILL_INSUFFICIENT`; no label or mapping change |

## Category reconciliation

| Next-action category | Count | External review IDs |
| --- | ---: | --- |
| `LOCAL_EVIDENCE_RECHECK` | 0 | None |
| `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE` | 16 | R117, R176, R455, R460, R535, R537, R548, R549, R580, R615, T137, T236, T503, T572, T576, T611 |
| `MAINTAINER_DECISION_REQUIRED` | 0 | None among the 19 external debts; one separate scope case follows |
| `BLOCKED_PENDING_AUTHORITATIVE_EVIDENCE` | 3 | T141, R376, U010 |

`0 + 16 + 0 + 3 = 19`. Research-type insufficiency remains 11; task evidence debt remains 7; institution debt remains 1. Discovering a candidate does not close a review, and retrieval failure does not show that a current label is wrong.

## Alternative primary-source candidates

**Accessibility for every candidate below: `NOT_TESTED`.** URLs are copied from identified local records, except the ECVA absolute links, which are mechanically resolved from saved relative hrefs and the saved archive base URL. No guessed PDF endpoints are supplied. Different URLs/representations are documented; distinct retrieval success or redirect destinations are not asserted. Any later scientific review must verify title, authors, identifier and manuscript version, then inspect the relevant full text.

### T576 — PMLR / mlresearch proceedings PDF

Candidate: [https://raw.githubusercontent.com/mlresearch/v235/main/assets/laszkiewicz24a/laszkiewicz24a.pdf](https://raw.githubusercontent.com/mlresearch/v235/main/assets/laszkiewicz24a/laszkiewicz24a.pdf). Official companion record: [https://proceedings.mlr.press/v235/laszkiewicz24a.html](https://proceedings.mlr.press/v235/laszkiewicz24a.html).

Local provenance: `data/raw/systematic_literature_2026_09/e50f3037063dc47ed5cc.gz`, matching title and Mike Laszkiewicz, Jonas Ricker, Johannes Lederer, Asja Fischer; pages 26007–26042. The saved official PMLR volume page explicitly links this PDF in the publisher-owned mlresearch repository. This is an official proceedings distribution, distinct from the failed OpenReview PDF.

Original attempt: [https://openreview.net/pdf?id=Hs9GcILuZN](https://openreview.net/pdf?id=Hs9GcILuZN) — `ACCESS_BLOCKED_HTTP_403`, recorded in `data/raw/corpus_quality_batch_c_wave3b1_2026_10_06/evidence_manifest.json`. Required evidence: Full task definition, real-image role, decision rule and scored real-versus-generated evaluation; model membership/non-membership alone does not establish detection. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### T611 — BMVA official BMVC proceedings record

Candidate: [https://www.bmva.org/bmvc/2021/conference/papers/paper_0197.html](https://www.bmva.org/bmvc/2021/conference/papers/paper_0197.html).

Local provenance: `data/raw/venue_audit_crossref/fd1594deb540228076e9.json`, response.message.resource.primary.URL; DOI 10.5244/c.35.53. Publisher-deposited Crossref metadata names the British Machine Vision Association and this official paper record. It may identify the canonical proceedings manuscript, unlike the obsolete virtual-conference host that redirected elsewhere.

Original attempt: [https://www.bmvc2021-virtualconference.com/assets/papers/0197.pdf](https://www.bmvc2021-virtualconference.com/assets/papers/0197.pdf) — `UNSAFE_REDIRECT_TO_UNRELATED_DOMAIN_NONRETRYABLE`, recorded in `data/raw/corpus_quality_batch_c_wave3b3_2026_10_07/evidence_manifest.json`. Required evidence: Full class definitions and evaluation showing an authentic/real-versus-GAN decision beyond model-specific fingerprint/source identification. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### T236 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2601.19430](https://arxiv.org/abs/2601.19430).

Local provenance: `web/data/public_preview_papers.json`, curated:64635535d7b7b6a12a32. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://openreview.net/pdf/6b5a5d6411ea1778f8c2cbf707a8a5744abe71b0.pdf](https://openreview.net/pdf/6b5a5d6411ea1778f8c2cbf707a8a5744abe71b0.pdf) — `ACCESS_BLOCKED_OPENREVIEW_CHALLENGE_TIMEOUT`, recorded in `data/raw/corpus_quality_batch_c_wave3a_2026_10_06/evidence_manifest.json`. Required evidence: A model-produced spatial mask, patch, box or equivalent prediction, corresponding ground truth and quantitative spatial scoring; artifact annotations or attention alignment alone are insufficient. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### T137 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2604.17736](https://arxiv.org/abs/2604.17736).

Local provenance: `web/data/public_preview_papers.json`, curated:246f07c81b9f91e527eb. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://openaccess.thecvf.com/content/CVPR2026/papers/Qin_IncreFA_Breaking_the_Static_Wall_of_Generative_Model_Attribution_CVPR_2026_paper.pdf](https://openaccess.thecvf.com/content/CVPR2026/papers/Qin_IncreFA_Breaking_the_Static_Wall_of_Generative_Model_Attribution_CVPR_2026_paper.pdf) — `TRANSFER_STALLED_BOUNDED_WAIT_EXCEEDED`, recorded in `data/raw/corpus_quality_batch_c_wave3b2_2026_10_06/evidence_manifest.json`. Required evidence: Incremental/open-set class definitions and evaluation showing whether real/authentic images form an evaluated forensic class, rather than only known/unknown generator identities. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### T503 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2402.10401](https://arxiv.org/abs/2402.10401).

Local provenance: `web/data/public_preview_papers.json`, curated:34fdf09ae334914a2723. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://openaccess.thecvf.com/content/CVPR2024/papers/Song_ManiFPT_Defining_and_Analyzing_Fingerprints_of_Generative_Models_CVPR_2024_paper.pdf](https://openaccess.thecvf.com/content/CVPR2024/papers/Song_ManiFPT_Defining_and_Analyzing_Fingerprints_of_Generative_Models_CVPR_2024_paper.pdf) — `ACCESS_BLOCKED_HTTP_403`, recorded in `data/raw/corpus_quality_batch_c_wave3b3_2026_10_07/evidence_manifest.json`. Required evidence: A real-versus-generated decision and detection-specific evaluation distinct from fingerprint/model identification experiments. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### T572 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2308.11557](https://arxiv.org/abs/2308.11557).

Local provenance: `web/data/public_preview_papers.json`, curated:5a91cc922c8a3c4c3d0c. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://papers.bmvc2023.org/0659.pdf](https://papers.bmvc2023.org/0659.pdf) — `HOST_UNREACHABLE_DNS_AND_BROWSER_502`, recorded in `data/raw/corpus_quality_batch_c_wave3b1_2026_10_06/evidence_manifest.json`. Required evidence: The actual open-set class space, role of real images and scored authenticity decision; rejecting an unknown generator is not sufficient. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R535 — ECVA official ECCV archive

Candidate: [https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07930.pdf](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07930.pdf). Official companion record: [https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/7930_ECCV_2024_paper.php](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/7930_ECCV_2024_paper.php).

Local provenance: `data/raw/systematic_literature_2026_09/63731d98eca600658d63.gz`, matching title/authors and DOI 10.1007/978-3-031-73033-7_16; href papers/eccv_2024/papers_ECCV/papers/07930.pdf. The saved official ECVA archive links the matching ECCV paper and PDF. The absolute URL is resolved from the recorded relative href against the saved https://www.ecva.net/papers.php base; it is a different official host from the Springer subscription preview.

Original attempt: [https://link.springer.com/content/pdf/10.1007/978-3-031-73033-7_16.pdf](https://link.springer.com/content/pdf/10.1007/978-3-031-73033-7_16.pdf) — `PRIMARY_PDF_REDIRECTED_TO_SUBSCRIPTION_PREVIEW`, recorded in `data/raw/corpus_quality_batch_c_wave4f_2026_10_08/evidence_manifest.json`. Required evidence: Contribution and dataset sections specifying a newly contributed reusable data resource, its size/composition and release/reuse role, rather than few-shot OCC-CLIP evaluation collections. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R117 — Tech Science Press publisher PDF and record

Candidate: [https://cdn.techscience.cn/files/jai/2026/8-6/TSP_JAI_78014/TSP_JAI_78014.pdf](https://cdn.techscience.cn/files/jai/2026/8-6/TSP_JAI_78014/TSP_JAI_78014.pdf). Official companion record: [https://www.techscience.com/jai/v8n1/66558](https://www.techscience.com/jai/v8n1/66558).

Local provenance: `data/raw/venue_audit_crossref/8428098558c27318927f.json`, response.message.link[0].URL (content-version=vor) and resource.primary.URL; DOI 10.32604/jai.2026.078014. The publisher deposit explicitly supplies these direct publisher endpoints for the matching title/DOI. They differ from the failed DOI resolver target. The PDF link was deposited for similarity checking; its public access is not established.

Original attempt: [https://doi.org/10.32604/jai.2026.078014](https://doi.org/10.32604/jai.2026.078014) — `PRIMARY_DOCUMENT_RETRIEVAL_INACCESSIBLE`, recorded in `data/raw/corpus_quality_batch_c_wave4e_2026_10_08/evidence_manifest.json`. Required evidence: Contribution list and FSI specification/mechanism, novelty and evaluation sufficient to distinguish a substantive technical method from a study measurement. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R549 — Cape Peninsula University of Technology institutional deposit

Candidate: [https://digitalknowledge.cput.ac.za/bitstream/11189/9706/1/Deepfake_Generation_and_Detection.pdf](https://digitalknowledge.cput.ac.za/bitstream/11189/9706/1/Deepfake_Generation_and_Detection.pdf).

Local provenance: `data/curated/institution_location_review.csv`, paper_id curated:616984c24ff3792431e6; also data/curated/institution_audit_log.csv. Existing affiliation-review records associate this exact institutional-repository PDF with the paper and note an earlier title-page review. The repository belongs to a listed author institution. Those notes do not preserve the full paper or establish the method contribution; identity/version still require checking.

Original attempt: [https://doi.org/10.1109/access.2023.3342107](https://doi.org/10.1109/access.2023.3342107) — `PRIMARY_DOCUMENT_RETRIEVAL_INACCESSIBLE`, recorded in `data/raw/corpus_quality_batch_c_wave4e_2026_10_08/evidence_manifest.json`. Required evidence: IBMM technical specification, contribution claim and supporting evaluation distinguishing an original method from an illustrative case within a survey/study. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R176 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2511.20068](https://arxiv.org/abs/2511.20068).

Local provenance: `web/data/public_preview_papers.json`, curated:f6ad15b01df18aadfe1a. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://openaccess.thecvf.com/content/CVPR2026F/papers/Damm_PRADA_Probability-Ratio-Based_Attribution_and_Detection_of_Autoregressive-Generated_Images_CVPRF_2026_paper.pdf](https://openaccess.thecvf.com/content/CVPR2026F/papers/Damm_PRADA_Probability-Ratio-Based_Attribution_and_Detection_of_Autoregressive-Generated_Images_CVPRF_2026_paper.pdf) — `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR_NONRETRYABLE`, recorded in `data/raw/corpus_quality_batch_c_wave4a_2026_10_07/evidence_manifest.json`. Required evidence: Explicit newly contributed data resource, construction, size/composition and release/reuse evidence, beyond PRADA detector/attributor evaluation. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R455 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2303.10762](https://arxiv.org/abs/2303.10762).

Local provenance: `web/data/public_preview_papers.json`, curated:04932cb03f767948ddf4. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://openaccess.thecvf.com/content/WACV2024/papers/Sinitsa_Deep_Image_Fingerprint_Towards_Low_Budget_Synthetic_Image_Detection_and_WACV_2024_paper.pdf](https://openaccess.thecvf.com/content/WACV2024/papers/Sinitsa_Deep_Image_Fingerprint_Towards_Low_Budget_Synthetic_Image_Detection_and_WACV_2024_paper.pdf) — `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR_NONRETRYABLE`, recorded in `data/raw/corpus_quality_batch_c_wave4a_2026_10_07/evidence_manifest.json`. Required evidence: Explicit reusable dataset contribution and construction/release evidence, beyond detector and model-lineage experiments assembled for the paper. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R537 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2310.04639](https://arxiv.org/abs/2310.04639).

Local provenance: `web/data/public_preview_papers.json`, doi:10.1109/ijcnn60899.2024.10650566. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10650566](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10650566) — `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR`, recorded in `data/raw/corpus_quality_batch_c_wave4b_2026_10_07/evidence_manifest.json`. Required evidence: Independent scientific analysis questions, design and findings beyond transfer-learning framework validation/ablations. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R548 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2210.06998](https://arxiv.org/abs/2210.06998).

Local provenance: `web/data/public_preview_papers.json`, doi:10.1145/3576915.3616588. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://dl.acm.org/doi/pdf/10.1145/3576915.3616588](https://dl.acm.org/doi/pdf/10.1145/3576915.3616588) — `PRIMARY_DOCUMENT_RETRIEVAL_INACCESSIBLE`, recorded in `data/raw/corpus_quality_batch_c_wave4d_2026_10_08/evidence_manifest.json`. Required evidence: A reusable evaluation framework with defined task/protocol, datasets, metrics and comparative baselines, rather than experiments evaluating DE-FAKE itself. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R580 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2302.10174](https://arxiv.org/abs/2302.10174).

Local provenance: `web/data/public_preview_papers.json`, curated:1ef55e4fc03eb4880beb. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://openaccess.thecvf.com/content/CVPR2023/papers/Ojha_Towards_Universal_Fake_Image_Detectors_That_Generalize_Across_Generative_Models_CVPR_2023_paper.pdf](https://openaccess.thecvf.com/content/CVPR2023/papers/Ojha_Towards_Universal_Fake_Image_Detectors_That_Generalize_Across_Generative_Models_CVPR_2023_paper.pdf) — `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR`, recorded in `data/raw/corpus_quality_batch_c_wave4f_2026_10_08/evidence_manifest.json`. Required evidence: Explicit newly contributed reusable data resource and its contents/release role, rather than evaluation on existing generated-image collections. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R615 — arXiv author-deposited manuscript record

Candidate: [https://arxiv.org/abs/2105.04580](https://arxiv.org/abs/2105.04580).

Local provenance: `web/data/public_preview_papers.json`, doi:10.1109/iccv48922.2021.01383. The canonical public record associates this exact arXiv record with the paper. An author-deposited manuscript is a primary scientific source; title, authors and version correspondence must be checked before using its full text.

Original attempt: [https://openaccess.thecvf.com/content/ICCV2021/papers/Girish_Towards_Discovery_and_Attribution_of_Open-World_GAN_Generated_Images_ICCV_2021_paper.pdf](https://openaccess.thecvf.com/content/ICCV2021/papers/Girish_Towards_Discovery_and_Attribution_of_Open-World_GAN_Generated_Images_ICCV_2021_paper.pdf) — `PRIMARY_DOCUMENT_RETRIEVAL_FORBIDDEN_403`, recorded in `data/raw/corpus_quality_batch_c_wave4c_2026_10_07/evidence_manifest.json`. Required evidence: Independent open-world discovery/attribution analysis questions and findings beyond evaluating the proposed method. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

### R460 — IEEE Xplore official paper record

Candidate: [https://ieeexplore.ieee.org/document/10860248/](https://ieeexplore.ieee.org/document/10860248/).

Local provenance: `data/raw/venue_audit_crossref/5cd6d81e14ca5642dde2.json`, response.message.resource.primary.URL; DOI 10.1109/aivrv63595.2024.10860248. The IEEE publisher deposit identifies a different official representation from the failed stamp PDF endpoint. A full-text HTML representation could answer the question if offered; neither full-text availability nor access is established. The deposited staging-host URL is not proposed.

Original attempt: [https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10860248](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10860248) — `PRIMARY_DOCUMENT_RETRIEVAL_INTERNAL_ERROR`, recorded in `data/raw/corpus_quality_batch_c_wave4b_2026_10_07/evidence_manifest.json`. Required evidence: Independent texture/frequency/patch analysis questions, experimental design and findings beyond classifier performance validation. Accessibility: `NOT_TESTED`; scientific conclusion: `EVIDENCE_STILL_INSUFFICIENT`.

## Blocked cases

- **T141:** The known Wiley PDF failed with HTTP 403. Existing DOI/abstract metadata and migration discovery notes identify the paper but provide neither the necessary evaluated class space nor a documented different full-text target. Preserve both task labels until authoritative method/evaluation evidence is available.
- **R376:** The known ACM PDF failed with HTTP 403. Existing DOI/bibliographic records do not supply the ensemble specification or a verified different manuscript endpoint. Preserve `method`. A later finding that the paper is only an analysis would require a positive role assessment; removing its sole research type without a replacement/maintainer review is not proposed.
- **U010:** The IEEE stamp target returned unusable HTTP 418. No alternative author-affiliation block was established in the completed local audit. The SUES review candidate conflicts with raw text naming Shanghai University. Keep these canonical institutions distinct and retain `needs_review`; do not infer affiliations from name similarity, city or coordinates.

These are evidence-availability blocks within the completed local audit, not claims that no authoritative source exists anywhere. No new endpoint was constructed or searched. Method-only R117 and R549 likewise require a later substantive role decision if evidence would remove their sole current type; that conditional guard does not turn their current evidence debt into a settled policy issue.

## T527 — separate maintainer scope decision

**Identity:** `doi:10.1109/lsp.2024.3388958`, *Towards Generated Image Provenance Analysis via Conceptual-Similar-Guided-SLIP Retrieval* (2024). The current public assignment is `source_attribution`; research type is `method`; the paper remains public and contributes two map relationship rows. The review remains `SCOPE_OR_TASK_EVIDENCE_REQUIRED` and is classified separately as `MAINTAINER_DECISION_REQUIRED`. It is excluded from the 19 external rows and their category totals.

**Existing evidence:** The locally stored abstract describes CS-SLIP: self-supervised, contrastive and conceptual-similarity branches for image/text representations, with bidirectional cross-modal retrieval and re-ranking to find replicated or similar training images behind generated images. The canonical public record and local OpenAlex captures `data/raw/openalex/20260619T193231Z_017_generated-image-provenance.json` and `data/raw/openalex/20260619T211726Z_017_generated-image-provenance.json` preserve this identity/abstract. The examined source record supplies a publisher location, not a saved full manuscript.

**Core-task fit:** This abstract supports training-image provenance retrieval. It does not substantively establish real-versus-generated detection, generator/model source attribution, or an evaluated spatial forensic prediction. Training-image retrieval may fall outside the intentionally narrow core task vocabulary. Lack of full-text evidence is not proof that none of these tasks appears in the paper. Local evidence is inadequate to recommend a final retain/retag/exclude outcome.

**Locked T3 rule:** “Every public paper must remain connected to at least one core forensic task represented by the map: detection, source_attribution, or localization. If careful review establishes that none applies, the record requires scope review rather than an empty task set.” The maintainer-modified rule supersedes any earlier empty-task proposal.

| Maintainer choice | Evidence/decision required | Consequence |
| --- | --- | --- |
| Retain | Decide whether the demonstrated training-image provenance task substantively fits the existing narrow source-attribution definition, or require primary task evidence before final retention. | Keep the paper and relationships; current source-attribution label is provisional while review remains open. Do not silently broaden scope. |
| Retag | Identify an actually supported core forensic task from authoritative scientific evidence. Current local material does not justify selecting detection, localization or generator attribution. | Update labels only through a separately authorized remediation; preserve at least one supported core task on an active public paper. |
| Exclude from public scope | Decide that the demonstrated contribution is outside the intended scope and no supported core task applies. | A separately authorized change would remove the public paper and its two map rows while preserving bibliographic provenance and the review record. No exclusion is performed here. |

Recommended maintainer action: decide the scope boundary explicitly, then request narrowly targeted task evidence if that decision still depends on the full paper. Until then preserve the current assignment and review status; never clear the task set while keeping the paper public.

## Proposed next batch — maximum four, not executed

The separate scope decision above has first priority. For a possible later external-evidence batch, recommend these four task cases. Research-type alternatives R535 and R117 remain valuable but follow task correctness under the requested ordering. Within task cases, explicit official proceedings targets are prioritized, followed by concrete author-manuscript records that could settle the decision space.

| Order | Review | Exact scientific question | Authoritative document needed |
| --- | --- | --- | --- |
| 1 | T576 | Does final-layer inversion evaluate real-versus-generated detection, or only source-model membership? | The PMLR proceedings main paper: task definition, real-image role, decision rule and detection-specific metrics/results. |
| 2 | T611 | Are authentic images evaluated as a forensic class beyond source-specific GAN fingerprints? | The BMVA canonical proceedings paper identified through its official archive record: class definitions and evaluation/results. |
| 3 | T236 | Is there a quantitatively evaluated spatial prediction, rather than only artifact annotation/attention interpretation? | The author manuscript identified by the stored arXiv record, matched to the reviewed paper: output definition, spatial ground truth and scoring/results. |
| 4 | T137 | Does the incremental/open-set evaluation include an actual real/authentic class rather than unknown-generator rejection? | The author manuscript identified by the stored arXiv record: label space, dataset splits, decision rule and class-specific results. |

No retrieval is authorized or performed by this report. These proposals do not apply taxonomy changes.

## Lightweight validation and preserved baseline

Programmatic reconciliation checks the 19 inventory rows for unique review IDs and exactly one allowed category each, against the approved residual ledger and committed outcomes. It checks the separate scope case, the 15-case research-type census (1 changed, 3 retained, 11 insufficient, 0 unreviewed), all candidate URLs against their identified local provenance, and current assignments against canonical data. Candidate endpoints are distinct from recorded first-pass targets; accessibility remains untested.

Recomputed current corpus: **639 public, 531 formal, 617 mapped, 22 unmapped, 1,421 relationship rows and 1,421 unique paper–institution pairs.** Recomputed taxonomy: **590 detection; 85 source attribution; 42 localization; 547 method; 132 dataset; 88 benchmark; 20 survey; 78 analysis study.** Batch B remains 159 and is untouched.

All tracked file bytes are compared with `/tmp/batch-c-debt-triage-baseline.json`; the 128 excluded files and 49 frozen paths are compared with `/private/tmp/batch-c-phase1-baseline.json`. The only new repository file is this report. `git diff --check` and report whitespace checks pass. No export regeneration or full test suite is run.

```text
AUTHORITATIVE_CORPUS_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA
```

Final local Git state: `HEAD = origin/main = 0f859a4c6221cafca8463b7828267b0fa8605030`; ahead/behind `0 / 0`; tracked working tree clean; index empty; 129 untracked files = 128 pre-existing excluded files, byte-for-byte unchanged, plus this report. No stage, commit, push, fetch, export regeneration, download or deletion was performed during this continuation. Existing temporary audit artifacts are retained.
