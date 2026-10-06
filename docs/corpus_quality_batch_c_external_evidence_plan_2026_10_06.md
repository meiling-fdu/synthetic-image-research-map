# Corpus Quality Batch C External-Evidence Plan

Date: 2026-10-06

Status: planning only; no external source has been fetched or reviewed

Basis: `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json`

## Scope and retrieval budget

This plan covers all 35 Batch C actions classified as `EXTERNAL_PRIMARY_SOURCE_REQUIRED`. They concern 35 unique paper identities, so no document can resolve actions for two different papers. The minimum first-pass retrieval set is 36 authoritative documents:

- 34 identity-matched primary documents for the ordinary cases;
- 2 independently authoritative documents for the source-conflict case, because the ACL record and arXiv record must be compared rather than inferred from one another.

For the six R1 dataset-role cases, retrieve the official paper PDF first. One PDF can resolve both contribution status and resource contents when it contains a sufficiently specific contribution/data statement. Retrieve an official supplement or author release record only when the PDF does not settle those facts. This makes 36 documents the minimum first-pass set and 42 the conditional maximum if all six R1 cases require a second document.

Documents are identity matched by title, authors, and stable identifier before their contents are used. A publisher or proceedings page may replace a PDF only when it contains the exact evidence required below. Search snippets, citation copies, downstream metadata aggregators, and repeated mirrors are not decision evidence.

## Governing policy shorthand

- **T1:** `source_attribution` does not imply `detection`; detection requires an explicit real/authentic-versus-generated task.
- **T2:** `localization` requires an evaluated spatial forensic prediction, rather than annotations or attention visualization alone.
- **R1:** `dataset` requires a substantive reusable data-resource contribution.
- **R2:** `benchmark` requires a reusable benchmark, challenge, protocol, comparative framework, or evaluation resource.
- **R3:** `analysis_study` requires systematic analysis as a primary scientific contribution.
- **R4:** `method` requires substantive technical novelty.
- **I1:** Shanghai University and Shanghai University of Engineering Science remain distinct; paper-time author assignment requires evidence.
- **I2:** Map a named VNU-HCM member to the member and use the reviewed hierarchy; add a separate parent relation only when the paper lists it separately.
- **V1:** Keep archival venue, source container/event, and track conceptually distinct, and leave unsupported fields empty.
- **Source-conflict review:** authenticate competing title, author, identifier, and abstract associations before choosing a source association or scope outcome.

## Retrieval batches

The batches below group papers by the kind of document and reading pass required. Each row states the exact unresolved factual question carried forward from the policy ledger.

### A. Official publisher or proceedings metadata

Retrieve the identifier-linked paper page and its official volume/event context. Prefer a single official page or PDF that states the archival container, named event, publication form, and any track. Do not infer a track from a DOI component.

| Paper | Review / policy | Exact unresolved factual question | Minimum authoritative source | One-document consolidation |
|---|---|---|---|---|
| `doi:10.2352/ei.2023.35.4.mwsf-380` — *Detecting GAN-generated synthetic images using semantic inconsistencies* | P550 / V1 | Which named scholarly event contains this paper, is it a proceedings contribution, and what track is explicitly documented? | Official IS&T paper or proceedings page linked to the DOI, with volume/event context. | Yes, if that page states container, event, form, and track; otherwise keep the unknown field empty. |
| `doi:10.1016/j.trpro.2022.09.012` — *Deep Learning applied to Road Accident Detection with Transfer Learning and Synthetic Images* | P586 / V1 | Which event is represented by volume 64, what is the paper's publication-form/year relationship, and is any track documented? | Official Elsevier article page or volume front matter identifying the event and publication form. | Yes, if the volume record covers all three facts. |
| `doi:10.2352/issn.2470-1173.2021.4.mwsf-276` — *Detection, Attribution and Localization of GAN Generated Images* | P610 / V1 | Does the primary proceedings identify Electronic Imaging or MWSF as this paper's event, and what publication form/track is evidenced? | Official IS&T paper or proceedings page linked to the DOI. | Yes, if it explicitly distinguishes event, container, form, and track. |
| `curated:60066ef08c2226131085` — *Detecting GAN Generated Fake Images Using Co-Occurrence Matrices* | P633 / V1 | Does the primary proceedings identify Electronic Imaging or MWSF as this paper's event, and what publication form/track is evidenced? | Official IS&T paper or proceedings page, identity matched by title/authors and DOI where available. | Yes, if it explicitly distinguishes event, container, form, and track. |

### B. Primary contribution and evaluation sections

Retrieve the official paper PDF. Read the contribution list together with the relevant method, data, evaluation, and analysis sections; abstracts alone are insufficient.

| Paper | Review / policy | Exact unresolved factual question | Minimum authoritative source | One-document consolidation |
|---|---|---|---|---|
| `curated:9c39067ac73e7354c2f3` — *Fake-HR1: Rethinking Reasoning of Vision Language Model for Synthetic Image Detection* | R099 / R1 | Are Fake-HR1 training examples a separately contributed reusable resource or only method training data? | Official full paper PDF containing the contribution and data statements. | Yes if the PDF specifies contents, release/reuse, and contribution status; otherwise add the official supplement or release record. |
| `curated:748ed5e2cf27aea70f6a` — *Frequency-Aware Robustness Analysis of Deepfake Detection Models* | R117 / R4 | Is FSI or its associated machinery a substantive new technical method, or only a measurement used by the study? | Official full paper PDF, especially contributions and FSI technical specification. | Yes; the same PDF should establish both novelty claims and technical substance. |
| `curated:807cbb7fa6b003585c72` — *GlobalForge: Towards Robust AI-Generated Image Detection* | R127 / R3 | Is the local-artifact fragility diagnosis independently tested as a principal finding, beyond motivating or validating LIB/GSR? | Official full paper PDF, including contribution list and controlled-analysis sections. | Yes; one PDF can establish the claimed role and independence of the analysis. |
| `curated:f6ad15b01df18aadfe1a` — *PRADA: Probability-Ratio-Based Attribution and Detection of Autoregressive-Generated Images* | R176 / R1 | What is in the released PRADA data, and is its construction or curation a substantial reusable contribution? | Official full paper PDF containing the data and availability statements. | Yes if the PDF specifies resource contents, reuse, and contribution status; otherwise add the official supplement or release record. |
| `curated:685065a3632a185a230d` — *Reduce the Artifact Bias for More Generalizable AI-Generated Image Detection* | R189 / R3 | Is there independent systematic evidence for artifact-bias claims beyond motivating and validating ACEF? | Official full paper PDF, including contributions and controlled analyses. | Yes; one PDF can establish whether the analysis is a principal contribution. |
| `curated:c84b04cb8e921be753db` — *Representation and Reference Selection in Training-Free Synthetic Image Attribution* | R190 / R1 | Does the reference collection constitute a contributed reusable dataset, rather than inputs for controlled analysis? | Official full paper PDF containing contribution, data, and availability statements. | Yes if the PDF settles resource status; otherwise add the official supplement or release record. |
| `curated:cda6067db322246e8195` — *No Detector to Rule Them All* | R376 / R4 | Is the ensemble a new technical contribution with its own specification, or an exploratory combination of baselines? | Official full paper PDF, especially contribution list and ensemble specification. | Yes; one PDF can establish both authors' novelty claim and technical detail. |
| `curated:04932cb03f767948ddf4` — *Deep Image Fingerprint: Towards Low Budget Synthetic Image Detection and Model Lineage Analysis* | R455 / R1 | Is there a documented new reusable image collection beyond detector and lineage experiments? | Official WACV paper PDF containing contribution, data, and availability statements. | Yes if the PDF settles construction and reuse; otherwise add an official supplement or release record. |
| `doi:10.1109/aivrv63595.2024.10860248` — *Detecting AI Generated Images Through Texture and Frequency Analysis of Patches* | R460 / R3 | Is any systematic scientific analysis a primary contribution beyond preprocessing and classifier accuracy? | Official IEEE paper PDF, including contributions and experimental design. | Yes; one PDF can establish the role and independence of any analysis. |
| `curated:98c0322e2f8dd41d3e9e` — *Which Model Generated This Image? A Model-Agnostic Approach for Origin Attribution* | R535 / R1 | Does OCC-CLIP contribute a dataset beyond the samples used for few-shot evaluation? | Official full paper PDF containing contribution, data, and availability statements. | Yes if the PDF settles resource status; otherwise add an official supplement or release record. |
| `doi:10.1109/ijcnn60899.2024.10650566` — *X-Transfer: A Transfer Learning-Based Framework for GAN-Generated Fake Image Detection* | R537 / R3 | Is there an independent transfer-learning analysis beyond validating the new algorithm? | Official IEEE paper PDF, including contributions and controlled analyses. | Yes; one PDF can establish whether analysis is independently substantive. |
| `doi:10.1145/3576915.3616588` — *DE-FAKE: Detection and Attribution of Fake Images Generated by Text-to-Image Generation Models* | R548 / R2 | Does DE-FAKE contribute a reusable evaluation protocol or framework rather than only its own comparative experiments? | Official ACM paper PDF, including contributions, evaluation protocol, and release statement. | Yes; one PDF can establish intent, specification, and reusability. |
| `curated:616984c24ff3792431e6` — *Deepfake Generation and Detection: Case Study and Challenges* | R549 / R4 | Is IBMM proposed as an original algorithm or system, or used as an illustrative survey case study? | Official full paper PDF, especially contributions and the IBMM section. | Yes; one PDF can establish authorship claim and technical novelty. |
| `curated:1ef55e4fc03eb4880beb` — *Towards Universal Fake Image Detectors That Generalize Across Generative Models* | R580 / R1 | Which new reusable data resource, if any, is contributed beyond evaluation on existing detection data? | Official full paper PDF containing contribution, data, and availability statements. | Yes if the PDF settles resource status; otherwise add an official supplement or release record. |
| `doi:10.1109/iccv48922.2021.01383` — *Towards Discovery and Attribution of Open-world GAN Generated Images* | R615 / R3 | Is open-world discovery analysis independently substantive, beyond demonstrating the iterative method? | Official ICCV paper PDF, including contributions and controlled analyses. | Yes; one PDF can establish whether analysis is a principal independent contribution. |

### C. Complete task protocols

Retrieve the official paper PDF and inspect class definitions, evaluation datasets, metrics, and supplementary protocol material embedded in or linked from that record. The decision turns on what the paper actually evaluates, not on background motivation or broad terminology.

| Paper | Review / policy | Exact unresolved factual question | Minimum authoritative source | One-document consolidation |
|---|---|---|---|---|
| `curated:1a8e996ef9ce73efc0ef` — *AI-Generated Image Homology Detection* | T024 / T1 | Does the evaluation include authentic images as a real-versus-generated task, beyond same-source pair verification? | Official paper PDF with complete classes and evaluation protocol. | Yes if the PDF contains the complete protocol; use an official supplement only if referenced details are omitted. |
| `curated:d59bffe554500b241a3e` — *ImageAttributionBench: How Far Are We from Generalizable Attribution?* | T136 / T1 | Is there a separate real-image or authenticity protocol outside the two recorded attribution settings? | Official paper PDF with complete class inventory and evaluation protocol. | Yes if complete; otherwise add the official supplement. |
| `curated:246f07c81b9f91e527eb` — *IncreFA: Breaking the Static Wall of Generative Model Attribution* | T137 / T1 | Does any IABench protocol classify real images, rather than only known versus unseen generators? | Official CVPR paper PDF with complete IABench protocol and classes. | Yes if complete; otherwise add the official supplement. |
| `curated:268336295435cfbbbd5d` — *Learning a Semantic Similarity Orthogonal Space for Model-Level AI-Generated Image Source Attribution* | T141 / T1 | Is real-versus-generated authenticity evaluated beyond reconstruction-based source matching? | Official paper PDF with complete task definitions and evaluation protocol. | Yes if the complete protocol is in the PDF. |
| `curated:64635535d7b7b6a12a32` — *Unveiling Perceptual Artifacts: A Fine-Grained Benchmark for Interpretable AI-Generated Image Detection* | T236 / T2 | Are spatial artifact predictions scored against the pixel annotations, or are masks used only to analyze or align attention? | Official paper PDF specifying model outputs, ground truth, and spatial metrics. | Yes if all three are explicit; otherwise add the official supplement containing evaluation details. |
| `doi:10.1609/aaai.v40i4.37240` — *Zooming In on Fakes: A Novel Dataset for Localized AI-Generated Image Detection with Forgery Amplification Approach* | T246 / T2 | Is a predicted edited-region mask, patch, or box evaluated, or is the output only an image-level decision? | Official AAAI paper PDF specifying output, ground truth, and metrics. | Yes if the full spatial evaluation protocol is present. |
| `curated:161b6d5ca391d238f7e9` — *Detecting Origin Attribution for Text-to-Image Diffusion Models* | T299 / T1 | Is real/fake discrimination a distinct task, rather than generator, seed, or hyperparameter identification? | Official paper PDF with complete task classes and evaluation protocol. | Yes if the protocol is complete. |
| `curated:8bc69db49ef4b9db3cd6` — *Are CLIP Features All You Need for Universal Synthetic Image Origin Attribution?* | T446 / T1 | Does the open-set protocol contain a real or authentic class and evaluate it as detection? | Official paper PDF with complete open-set class definitions and metrics. | Yes if the protocol is complete. |
| `curated:34fdf09ae334914a2723` — *ManiFPT: Defining and Analyzing Fingerprints of Generative Models* | T503 / T1 | Does the full protocol evaluate real/fake detection in addition to fingerprint or model identification? | Official paper PDF with complete experimental protocol and classes. | Yes if the protocol is complete. |
| `curated:5a91cc922c8a3c4c3d0c` — *Open Set Synthetic Image Source Attribution* | T572 / T1 | Does the BMVC protocol include a separate authenticity evaluation beyond unknown-generator rejection? | Official BMVC paper PDF with complete class definitions and evaluation protocol. | Yes if the protocol is complete. |
| `curated:62b0a9ae8be24d9f02e0` — *Single-Model Attribution of Generative Models Through Final-Layer Inversion* | T576 / T1 | Are real images part of an explicit authenticity task, rather than merely examples of non-membership? | Official paper PDF with complete membership classes, datasets, and evaluation protocol. | Yes if the protocol is complete. |
| `curated:07ee620b8169b67b900f` — *Does a GAN Leave Distinct Model-Specific Fingerprints?* | T611 / T1 | Do the reported fingerprint experiments include binary authenticity detection? | Official paper PDF with complete experimental tasks, classes, and metrics. | Yes if the protocol is complete. |
| `doi:10.1109/mipr.2019.00103` — *Do GANs Leave Artificial Fingerprints?* | T634 / T1 | Does the complete experiment protocol include real/fake detection beyond source identification? | Official IEEE paper PDF with complete experimental protocol and classes. | Yes if the protocol is complete. |

### D. Paper-time affiliation blocks

Retrieve the official formatted paper PDF. The author superscripts and affiliation block must be read together; current institutional coordinates, name similarity, and hierarchy assumptions cannot establish a paper-time assignment.

| Paper | Review / policy | Exact unresolved factual question | Minimum authoritative source | One-document consolidation |
|---|---|---|---|---|
| `curated:d0eec7c4fce8929c295a` — *Diffusion-Driven Forgery Detection: Distilling Latent Features for Generalized Image Forensics* | U010 / I1 | Which paper-time affiliation marker belongs to each of Kaiwen Qian, Yutao Xu, Yifan Xu, and Yuchun Fang: Shanghai University, Shanghai University of Engineering Science, or genuinely both? | Official IEEE formatted paper PDF with author markers and full affiliation block. | Yes; one formatted PDF can resolve all four authors without merging the two institutions. |
| `curated:0d918782407e05ade5bd` — *Unified Detection of Synthetic and Manipulated Images via Dual-Stream Artifact Fusion* | U017 / I2 | How do the ACM paper's affiliation markers assign Thinh-Phat Vo, Daniel Mai, Minh–Triet Tran, and Trong-Le Do to the member and parent; are those separately listed affiliations? | Official ACM formatted paper PDF with author markers and full affiliation block. | Yes; one formatted PDF can resolve all four authors and whether the parent is separately listed. |

### E. Competing source identity records

This case cannot be resolved from a single document because the disputed records must be authenticated independently and compared.

| Paper | Review / policy | Exact unresolved factual question | Minimum authoritative source | One-document consolidation |
|---|---|---|---|---|
| `curated:6c2f591bf6fda3abecbb` — *Reasoning-Aware AIGC Detection via Alignment and Reinforcement* | R188 / source-conflict review | Which title, abstract, and identifier combination actually belongs to the included image paper, and which text-paper evidence was misassociated? | Two documents: the official ACL Anthology record/PDF for DOI `10.18653/v1/2026.findings-acl.1043` and the authoritative arXiv `2604.19172` record/PDF. Match title, authors, identifiers, and abstract. | No. Two independent records are mandatory; neither may authenticate the other. |

## Decision recording after retrieval

For each paper, record the stable source URL or identifier, retrieval date, document hash when saved locally, precise page/section locator, and the factual finding before proposing any corpus change. Keep unsupported fields empty. If the minimum source does not answer the stated question, retain `EXTERNAL_PRIMARY_SOURCE_REQUIRED` and record the missing evidence rather than inferring an outcome.

No Batch B action is included in this plan. T527 remains `MAINTAINER_SCOPE_JUDGMENT_REQUIRED` and is outside this external-evidence queue.
