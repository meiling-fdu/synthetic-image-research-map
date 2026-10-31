# Batch B Wave B3-02 — B2-02 evidence review

Evidence-only checkpoint, 2026-10-29. Completed the existing assigned batch without restarting B2 planning, B3-01 or completed source reviews. All recommendations require separate B4-02 maintainer acceptance. No action was formally resolved.

Published baseline: `7fc8ceae702324628335944cf4b545a3733fdc56`. Remote main was independently checked through the connected GitHub branch API and matches this baseline. The new isolated worktree is `/Users/meilinger/.codex/worktrees/batch-b-b3-02/synthetic-image-research-map`. B4-01 remains an **unpublished pending transaction**: its eight validated files, prior decision history and B5 handoff are unchanged. Its hypothetical local accounting 123/121 is not used as published source accounting.

## Exact assigned coverage

B2-02: 11 papers, 15 distinct actions, priority 1, no batch dependencies. Four publication questions concern canonical venue identity/type and supported short names; 11 institution questions concern paper-relevant sites and coordinates. There are no taxonomy actions. The 11 U actions retain 14 original affiliation instances across 12 distinct institutions; shared U018/U023 sources do not merge the papers or their actions.

| Canonical paper ID | Paper | Actions and provisional outcomes |
|---|---|---|
| `curated:f43871cdbcf21546aa91` | ImageTrust: Multi-Backbone Fusion for AI-Generated Image Detection with Calibrated Uncertainty | `P001` SUPPORTED_ADDITION; `U001` EVIDENCE_INSUFFICIENT |
| `curated:bd8343f176d4b9e38a7b` | A Multi-View and Confusion-Guided Ensemble Framework for Robust Synthetic Image Attribution | `U002` EVIDENCE_INSUFFICIENT |
| `curated:dc0280c881d08395cfac` | Abductive Corroboration of Probabilistic AI Models for Forensic Synthetic Media Detection | `U003` EVIDENCE_INSUFFICIENT |
| `curated:64195610a6d2c2448275` | Conditional Uncertainty-Aware Political Deepfake Detection with Stochastic Convolutional Neural Networks | `P049` SUPPORTED_ADDITION; `U005` SUPPORTED_ADDITION |
| `curated:d129c9180d4a0cff91ad` | Deep Learning for CGI and Visual Forgery Detection: A Comprehensive Survey | `P058` SUPPORTED_ADDITION; `U006` EVIDENCE_INSUFFICIENT |
| `curated:5b2a1ca1ae438916336b` | Detecting AI-Generated Forgeries via Iterative Manifold Deviation Amplification | `U007` EVIDENCE_INSUFFICIENT |
| `curated:e5a9ed970200c293678e` | Detecting Violent Deepfakes: Dataset and a Compact Attention Network with Multi-Scale Supervision | `P068` SUPPORTED_ADDITION; `U008` EVIDENCE_INSUFFICIENT |
| `curated:b14247b031eff3671d2b` | Scalable Black-Box Model Attribution for Images | `U014` EVIDENCE_INSUFFICIENT |
| `curated:26e3335c0d625676a231` | SPECTRA-Net: Scalable Pipeline for Explainable Cross-Domain Tensor Representations for AI-Generated Images Detection | `U016` EVIDENCE_INSUFFICIENT |
| `curated:f7adf12bdae80860a18f` | DeCLIP: Decoding CLIP Representations for Deepfake Localization | `U018` EVIDENCE_INSUFFICIENT |
| `curated:9e6bc47bc75cd7b9b637` | Weakly-Supervised Deepfake Localization in Diffusion-Generated Images | `U023` EVIDENCE_INSUFFICIENT |

Five `SUPPORTED_ADDITION` recommendations: P001, P049, P058 and P068 for source-backed canonical venue bindings; U005 for a qualified approximate school-site point. Ten `EVIDENCE_INSUFFICIENT` holds: U001, U002, U003, U006, U007, U008, U014, U016, U018 and U023. There are no `SUPPORTED_NO_CHANGE`, `NOT_SUPPORTED` or `IDENTITY_BLOCKED` outcomes. All 15 actions remain open in authoritative accounting.

## Publication findings and bounded proposals

- **P001:** The DOI-matched [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-032-29430-2_19) confirms the title, ordered Iancu/Galiş/Stefaniga authors and canonical International Conference on Complex, Intelligent, and Software Intensive Systems identity; `citation_conference_abbrev=CISIS`. The proceedings book and LNDECT series are separate containers. First online2 August2026 / CISIS 2026 and citation/copyright2027 coexist in the publisher record. Preserve the current2027 field; no date/status correction is proposed.
- **P049:** The [DOI-matched journal record](https://jhss.scholasticahq.com/article/156299) confirms the title, single author and Journal of High School Science journal identity. Publisher ASCII spelling Rafael-Petrut Gardos does not authorize changing canonical diacritics. The existing arXiv 2602.10343 linkage is reused, without claiming a fresh version-equivalence review. `citation_journal_abbrev` repeats the full journal name: keep the optional acronym empty in the bounded proposal.
- **P058:** The [Springer article](https://link.springer.com/article/10.1007/s41060-026-01192-9) confirms title, ordered Ahmet Korkmaz / Mustafa Özden authors and International Journal of Data Science and Analytics journal identity. `Int J Data Sci Anal` is an explicit bibliographic short form, not a newly invented letter acronym. Online29 June2026 and December2026 issue citation remain distinct observations; no date correction.
- **P068:** The [Springer article](https://link.springer.com/article/10.1007/s00138-026-01836-7) confirms title, ordered Surbhi Raj / Jimson Mathew / Arijit Mondal authors and Machine Vision and Applications journal identity. Publisher abbreviation metadata repeats the full title, so no acronym is invented. Online30 May2026 versus July2026 issue citation is retained.

All four existing public venue names and publication types are already correct. `SUPPORTED_ADDITION` refers to proposed canonical venue binding/registry confirmation under the original questions, not a claim that those names need factual replacement. B4 must inspect the live venue schema, select/create valid bindings and satisfy current fingerprint/decision acceptance rules. Existing DOI/arXiv, author sequence, title, year, URLs, track, task and research-type fields are preserved. No invented venue ID is written into source.

## Institution identity, address, paper-time site and coordinates

| Action | Primary identity/address finding | Paper-time site finding | Coordinate finding / B4 barrier |
|---|---|---|
| U001 | West University of Timișoara faculty; [faculty contact](https://info.uvt.ro/contact/) identifies4 Vasile Pârvan. | Paper names faculty/university/city; current street address does not establish historical continuity by itself. | Exact-address cached query empty; no point proposed. Need paper-time site corroboration and traceable point. |
| U002 | Institute legal identity and No. 11 Kexiang Road research base supported by [SAMR](https://std.samr.gov.cn/search/orgDetailViewCNF?data_id=09CEBB11CDCE440DE06397BE0A0A1F8A) and [CSEE2020 HVDC conference contact](https://dcpe2020.scimeeting.cn/). The current510663 and historical510630 postal-code difference is preserved, not silently normalized. | A2020 contact /2021 patent does not establish this2026 paper’s exact laboratory site. | No authenticated coordinate or declared CRS. Do not substitute utility headquarters or silently use Chinese-map coordinates as WGS84. |
| U003 | [Official institute directions](https://www.turing.ac.uk/contact-us/how-get-alan-turing-institute) identify first floor, British Library, 96 Euston Road, NW1 2DB. | Paper identifies Defence and National Security Programme / London; no paper-time premises established. | Cached OSM research-office node9641710068 matches current address at51.5302275,−0.1270026. Secondary geocode corroborates current geography, not author/programme paper-time site. Hold. |
| U005 | Paper expressly gives school street5 Mihai Eminescu,440014; [school contact](https://www.eminescusm.ro/contact) independently matches it. | Exact paper-time school address is established without geocoder inference. | Official embed selects47.789438,22.876378 at zoom 19. Proposed approximate representative site point only; not explicit marker, survey or independently verified geocode. CRS not declared; positional uncertainty unmeasured. B4 must accept those limits or retain coordinate hold. |
| U006 | Publisher independently links Korkmaz to Army NCO school in Balıkesir and Özden to BTU EEE,16310 Yıldırım. [Official Army contact](https://www.kkk.tsk.tr/kkksablonmaster/header/hizmetler/okullar/KKAMYO/index.html) is preserved as indexed evidence; direct access failed. [BTU departmental bulletin](https://depo.btu.edu.tr/dosyalar/elektrik/Dosyalar/E-Bulten_2020_Aralik.pdf) gives Mimar Sinan /177 Eflak in2020. | Balıkesir school identity/city verified; BTU department’s2020-to-2026 campus continuity unverified. | No qualifying point for either site. Do not use National Defense University’s Istanbul headquarters or assume a six-year-old campus assignment. |
| U007 | Wuhan University of Technology identity verified; [official campus evidence](https://alumni.whut.edu.cn/article/10177) distinguishes Nanhu, Mafangshan and Yujiatou. | Preserved paper affiliation gives university only; specific campus unresolved. | No campus selected or point proposed. Other Wuhan universities are distinct entities. |
| U008 | DOI-matched affiliation and postcode 801106 plus [official IIT Patna directions](https://www.iitp.ac.in/visit/find-us) support Bihta campus. | Supported at campus level; no exact building claimed. | [Admissions brochure](https://www.iitp.ac.in/acad/files/phdadmissionbrochure.pdf) gives25°32′0.18″N84°51′16.08″E; [2015–16 annual report](https://morya.iitp.ac.in/images/pdf/IIT_Patna_Annual_Report%202015_16_English.pdf) gives25°32′56.96″N84°51′21.64″E. Points differ~1760.6m; source reference points/CRS/cause unresolved. Neither adopted or averaged. |
| U014 | Preserved arXiv 2608.15652 and ordered authors match. [Current university contact](https://english.tau.ac.il/node/3120) / [campus page](https://www.tau.ac.il/gc-map-test) give Ramat Aviv /30 Haim Levanon. | Generic university paper affiliation does not directly prove authors’ paper-time campus. | Captured campus HTML has no verified coordinate. Current contact is not a substitute for paper-time site evidence. |
| U016 | English/French [ENSIA identity](https://www.ensia.edu.dz/) and official domain match the paper. [Campus page](https://www.ensia.edu.dz/campus-life/) describes Sidi Abdellah Technology Park; [WIPO record](https://www.wipo.int/tisc/en/search/details.jsp?id=14132) gives Mahelma and short pluscodeMVQ8+9GP. | Raw paper first page names school/Algiers; publication-time exact-campus link not established. | Short code preserved undecoded; completed geocode empty. No guessed full code, decimal point or Algiers centroid. |
| U018 | Retained WACV 2025 affiliation evidence supports Bitdefender and POLITEHNICA Bucharest. | Neither a Bitdefender research office nor exact university paper-time campus established. | Company registered address is not author site. Broad university embed viewport is not a campus marker. Retain both affiliations and hold. |
| U023 | Retained WACV 2024 evidence supports same two institutions, independently of U018. | Shared organization names do not prove shared offices across2023/2024/2025. | Same site gaps remain. Preserve arXiv 2023 / final WACV 2024 boundary and Tântaru / Oneață diacritics; do not merge actions. |

Current addresses are useful partial evidence. They are never upgraded to paper-time sites solely because a geocoder returned a matching institution. Exact missing gates, source locators, official/indexed versus raw representations, confidence and version limitations are recorded per action in `batch_dispositions.json` and the11 `paper_evidence/` records. No material taxonomy inconsistency was established; no taxonomy follow-up review was added.

## Provenance, effort and retrieval costs

The 38 source records include raw official HTML, preserved tool-produced official-page extracts and explicitly identified indexed official-source excerpts. A hash of an excerpt authenticates that saved excerpt, not an inaccessible complete document. Earlier DNS/SSL/HTTP failures remain preserved. Reviewer outputs and earlier assessments are copied unchanged under `checkpoint/`; corrected source locators appear as additive QC notes.

Recovery required zero new source retrievals, zero manuscript downloads and zero geocoding requests. The remote branch API read is repository verification, not a scientific-source retrieval. Original completed captures include 26 direct HTTP attempts (10 successful payloads,2,818,647 bytes),14 group web-tool capture files, and four cached geocoding responses (one institute-specific match and three empty arrays). Backend HTTP request counts for web tools are not exposed and are not fabricated. No paid API was used; monetary and model-compute costs were not measured.

The subsequent four-query geocoding command was declined by automatic approval review because its usage limit prevented review. It did not execute: no queue3 file, requests or responses exist. No alternate route or retry was used to bypass that restriction. The exact pending requests and resulting evidence gaps are preserved in `checkpoint/geocoding-declined-command.json`.

Reviewer recovery windows and measured request latencies are reported in `effort_and_retrievals.json`. They measure agent wall-clock intervals, including tool waits, and are not human analyst hours. Original pre-interruption active labor cannot be reconstructed reliably; the usage-limit interruption is excluded rather than billed as review effort. B2’s340–710-minute planning estimate is preserved; this institution-heavy batch provides limited calibration because ten site actions remain evidence-insufficient.

## QC, accounting and preservation

Three primary reviewers recovered their independent source groups. Different reviewers independently checked each other’s evidence-to-claim mapping, with additional root checks of all four DOI/venue records and U005’s exact address/map distinction. Any QC qualification is retained with the original reviewer output. Independent cross-review passed 224 checks; lightweight identity/provenance/accounting validation passed 412; preservation passed 19,202, all with zero failures. See `independent_qc.json`, `validation.json` and `preservation.json` for exact results. The initial lightweight harness incorrectly required an external URL for the checksum-pinned local ledger; its 1-failure report and the explicit local-source/URL distinction are preserved. No evidence claim or functional assertion was removed.

Published accounting remains159 original actions /148 papers,28 formally terminal actions,131 historical unresolved actions /121 papers,129 active-public unresolved actions /119 papers. B3-02 resolves zero actions. B4-01’s pending local 123/121 accounting remains separate. The evidence-only recommendations do not decrement any ledger.

Corpus unchanged:674 public,557 formal,613 mapped,61 unmapped,1,410 relationships and 1,410 unique pairs. Tasks remain621 detection,84 source attribution,45 localization. Research types remain578 method,138 dataset,97 benchmark,21 survey,86 analysis study. All totals are recomputed from the pinned published source/public context and preservation checked; nothing is exported or hard-coded into authoritative records.

The final audit covers all 4,508 tracked files in the clean B3-02 worktree, all eight pending B4-01 files and its full worktree state, existing independent worktree states, protected 128 files, 49 frozen NeurIPS artifacts in the preserved full inventories, prior B2/B3/B4 and CI-acceptance archives, Batch C debts and the separate39-paper inventory. The new clean checkout naturally contains40 tracked frozen artifacts; nine historical ignored artifacts were absent on creation and were not recreated or deleted. All49 remain intact in the established source/primary/B4 inventories. Concurrent primary work is observed and never reset or edited.

No authoritative CSVs, formal review decisions, institution mappings, public exports or website code changed. No staging, commit, push, export, deployment, full suite or B4-02 was performed. The new worktree remains detached at the verified remote commit, ahead/behind0/0, with empty index and empty `git status --short --untracked-files=all` output. Evidence artifacts live outside the repository so they remain uncommitted without dirtying the checkout.

`AUTHORITATIVE_CORPUS_CHANGED = 0`  
`FROZEN_NEURIPS_CHANGED = 0`  
`PREEXISTING_LOCAL_FILES_CHANGED = 0`  
`UNEXPECTED_CHANGED = 0`

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## B4-02 handoff

`b4_handoff.json` carries all 15 actions exactly once, the five qualified supported proposals, ten holds, source references, explicit precision/identity gates and the unchanged B4-01 pending fingerprints. It authorizes no execution. Stop here; any adjudication or integration requires a separate instruction.
