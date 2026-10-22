# Batch B Wave B1K — R542 benchmark removed; R467 deferred

Maintainer-approved adjudication of the completed evidence-only packet at published baseline `b2f17505f2d3a1b65d43fcf3c6582436b4fe44f8`. Exactly **R542** changes from `benchmark;survey` to `survey`; its original research-type review closes. **R467 remains `EVIDENCE_STILL_INSUFFICIENT`**, with no authoritative change or terminal decision. Its existing `method;benchmark` is held administratively and is not scientifically reconfirmed. Independent publication action **P467 remains pending**.

The actual application UTC is **2026-10-22T09:03:19Z** and the taxonomy audit date is **2026-10-22**. Terminal decision **`review:1691b3f56711c58a7861`** uses the supported `other` queue, `paper` target and `no_action_after_review` action after the correction, meaning that no further work remains for this bounded accepted review. It does not claim no data was changed. The registry grows **91 → 92** rows, preserving every pre-existing byte as a prefix. No new review action or denominator change occurs.

## R542 — accepted contribution-level R2 judgment

Accepted disposition: **`PROPOSE_CORRECTION_ACCEPTED`**.

**A Survey of Detection and Mitigation for Fake Images on Social Media Platforms**, DOI `10.3390/app131910980`, *Applied Sciences* **2023, 13(19), 10980**. The complete **36-page**, **4,761,099-byte** [institutionally hosted publisher-formatted manuscript](https://www.um.edu.mt/library/oar/bitstream/123456789/123188/1/A%20survey%20of%20detection%20and%20mitigation%20for%20fake%20images%20on%20social%20media%20platforms%202023.pdf) matches the title, DOI and all six authors: Dilip Kumar Sharma, Bhuvanesh Singh, Saurabh Agarwal, Lalit Garg, Cheonshik Kim and Ki-Hyun Jung. SHA256: `430e00965954d8c1d69f017c70e567b12a973691fe8b2bd6825276a154f82ef9`.

The publisher PDF returned **HTTP 403** and publisher HTML **HTTP 429**. The reviewed source is the University of Malta institutional copy. **Direct equivalence to inaccessible publisher bytes or later corrections remains unverified.** Its original manuscript creation/modification dates, printed publication date and actual retrieval receipts remain intact. No new retrieval or scientific extraction was performed during adjudication.

Locked **R2** permits a reusable evaluation benchmark, challenge, protocol, systematic comparative framework or benchmark resource. New code, new data and independent reruns are not mandatory prerequisites. The accepted finding is a **medium-confidence contribution-level judgment**: the paper substantiates a comparative survey and catalog of existing methods, datasets and metrics, but does not sufficiently establish a distinct substantive reusable benchmark beyond that synthesis. **Remove `benchmark`; retain `survey`.** This does not impose a blanket survey disqualification.

Tables **1–7** attribute prior studies' results; p.25 explicitly takes att-RNN scores from Khattar. Tables **8–9**, pp.26–27, summarize standard confusion-matrix measures. Table **10**, p.28, catalogs **14 external datasets**, and p.31 points to public datasets in the references. Existing comparisons include RRU-Net F1 **0.915 / 0.841** on Columbia/CASIA2.0 and MFCN **0.611 / 0.541 / 0.571** on Columbia/CASIA1.0/NIST16; SAFE accuracy **87.40 / 83.80** and SpotFake **77.77 / 89.23** on MediaEval/Weibo. These remain attributed source measurements, not a claim of new survey reruns or independent numerical reproduction.

### Positive and contradictory evidence remains material

Section **1.3**, p.4, expressly claims performance-comparison guidance; section **4**, p.8, and the Table 5–6 grouping restrict comparisons to the same metric/dataset. These organized comparisons support a competing **permissive systematic-framework interpretation** under R2 and remain part of the accepted record.

Section **6.2**, p.27, contains the genuine first-person Fakeddit statement about selecting **two-way fake/real labels in an experiment**. Its referent remains unresolved: the reviewed evidence does not connect it to a specified model, split, scoring protocol or Fakeddit result establishing a separate reusable benchmark. **No claim is made that no experiments ever occurred.** Existing completed worker, root and independent reviews considered this evidence; no omitted independently specified reusable benchmark was identified. A materially new independently defined framework would require stopping closure and reporting the contradiction.

All original source issues remain unresolved: Hussain CASIA1/2 accuracies **92.08/95.70** in Table 2 versus **94.19/96.61** in Table 5; He **89.76** in differing CASIA columns; Table 7 att-RNN/EANN **reference 129** and RoBERTa/BERT naming; Table 9 ungrouped FPR/FNR/HTER formulas and **mPA** spelling; Table 10 **COCO versus INRIA Holidays/Copydays** naming. Values are preserved as printed. Same dataset and metric names do not establish common samples, splits, checkpoints, preprocessing, hardware or scoring implementation. External resource availability, licenses and independent numerical reproduction were not newly verified.

Tasks remain **`detection`**; image scopes remain **`fully_generated;deepfake;traditional_manipulation`**. Broad conventional manipulation, generated-image/deepfake and genuine-image false-context observations are retained without scope or task remediation. No new dataset action is created.

## R467 — evidence debt remains open

R467, DOI `10.3390/ai5030076`, remains **`EVIDENCE_STILL_INSUFFICIENT`**. Its entire original record is preserved exactly. The incomplete institutional body has **15,024,008 of 38,629,090 expected bytes**; the single missing-byte range attempt was ignored and aborted without an appended body. Official PDF, HTML and XML barriers and all transport receipts remain. No complete-source hash, full scientific-method review or direct-publisher equivalence is claimed. The abstract's **97.32% CIFAKE** result remains an unverified abstract claim.

The satellite dataset observation remains outside this adjudication: transformed training variants and independently GAN-generated detection images are distinct; the two descriptions of **50,000** items are not conflated. No dataset label, scope/task change or new review action is authorized. **R467 and P467 remain independently pending**; administrative type retention is not a scientific endorsement.

## Exact authoritative and public-data delta

Exactly **six existing CSV cells** change in R542's existing DOI-keyed `paper_taxonomy.csv` row: research types, bounded review reason, evidence tier, actual institutional source URL, factual excerpt and audit date. Its `paper_id` stays empty. No curated `papers.csv` row exists for this legacy work, and **none is invented**: the existing DOI/OpenAlex identity-based taxonomy overlay already joins the public record and all map relationships. No processed input is edited solely for symmetry. All other taxonomy cells and rows, tasks, scopes, statuses, bibliographic data, authors, affiliations, institutions and inclusion decisions remain unchanged. Exactly one terminal decision is appended.

The measured deterministic offline export changes **one of 674 public paper records** and **six of 1410 map records**, only in `research_types` and the dependent research-type review reason. The other **673 papers**, **1,404 map records** and all **1410 relationship identities** remain unchanged. Generated JSON is not manually patched. Reviewed deterministic report differences: `docs/public_preview_report.md`: line 14; `docs/key_paper_coverage_report.md`: line 7.

## Recomputed corpus and original Batch B accounting

| Measure | Current value |
| --- | ---: |
| Public / formal / mapped / unmapped | 674 / 557 / 613 / 61 |
| Relationships / unique pairs | 1410 / 1410 |
| Detection / source attribution / localization | 621 / 84 / 45 |
| Method / dataset / benchmark / survey / analysis study | 578 / 135 / 91 / 21 / 82 |
| Original Batch B actions / papers | 159 / 148 |
| Historical unresolved actions / papers | 143 / 132 → 142 / 131 |
| Active-public unresolved actions / papers | 141 / 130 → 140 / 129 |

Counts and distinct identities are recomputed from the live data and original ledger. Only R542 closes; R467 and P467 remain pending. Original denominators remain **159 actions / 148 papers**. Batch C's same **13 deferred debts**, the separate **39-paper import inventory**, prior B1A–J receipts, all **128 protected primary files**, **49 frozen NeurIPS artifacts** and **119 ignored operational inputs** remain protected.

## Evidence-receipt reconciliation and validation boundary

The final R467 worker receipt contains **38/38 passing checks**, SHA256 `9f8dd7f313d042502ce0301da7e1933c105335d8bba2f4dfffc23fa9508f85dc`. The final R542 worker receipt contains **35/35 passing checks**, SHA256 `67449cadf26475c5d2fa81624d2536142bea37851dc4fffb2c358d220c836e62`. These are **73 final worker checks across two distinct receipts**. The earlier **38/35** shorthand is not a pass/total ratio. Root spotchecks, independent primary-first/cross-reviews, packet checks and preservation receipts remain separately identified and are not double-counted.

The initial R542 verifier selected two Khattar author rows; its preserved **34/35** receipt records that selector-harness failure. Narrowing the selector by the printed reference IDs produced the final **35/35** receipt without changing scientific review or source bytes. The original validation and initial-verifier history remain exact.

Complete original manifest and report bytes are authenticated with deterministic gzip/base64 archives. All source findings, original provisional outcomes, prior administrative states, manuscript versions, quantitative comparisons, failures, partial and rejected-range receipts, source fingerprints and limitations remain intact. The full original report follows verbatim. R467 is unchanged; only four original R542 administrative acceptance flags change, while separate accepted fields describe the approved correction. All original **17 source fingerprints** remain historical; current fingerprints retain the same keys and update only taxonomy, decisions and the two dependent public JSON files.

<!-- B1K_ADJUDICATION_VALIDATION_START -->
**Focused validation passed: 421 ordinary tests and 12 subtests**, including **22 B1K regression cases**; zero failures/errors/skips. The preserved first focused attempt had two diagnostic failures, repaired narrowly by using the committed checksum-bound source authority for an ignored legacy input and adding the accepted-status literal to the current report. Its failed result, log/XML hashes and repair receipts remain in the manifest; neither failure altered scientific data or weakened the current-source assertion.

All four current-scope validators passed with zero errors. Reported validator warnings remain visible in their actual receipts.

**The complete repository suite ran once and passed 2074 ordinary tests and 389 subtests**; zero failures/errors/skips and 2 existing warnings. Python 3.14.7, pytest 9.1.1, pytest-subtests 0.15.0 and Node 24.19.0 were used with the established checksum-matched offline fixtures and authorized localhost. All **4602 input/output paths** remained unchanged after the suite.

After that successful suite, **two sequential offline export verification passes passed**. All **4602 compared paths**, seven deterministic outputs and 119 operational inputs remained byte-identical in each pass. Both read-only fixture checks verified 117 inputs, creating none. One initial correction export and exactly two verification exports completed without parallel exporters. `EXPORT_REPRODUCIBLE = 1`.

The independent semantic/preservation gate passed **67/67 checks**. Only R542 changes in **one public record and six existing map records**; **673 other papers**, **1,404 other map records** and all **1,410 relationship identities** remain unchanged. Six existing taxonomy cells and one appended terminal decision close only R542. R467 remains evidence-insufficient and its independent P467 publication action remains pending. Benchmark becomes **91**; all other corpus and taxonomy totals remain unchanged.

Original evidence-stage receipts remain preserved: R467 **38/38** and R542 **35/35** are separate final worker receipts totaling **73** checks, not a 38/35 pass ratio. The initial R542 **34/35** selector-harness failure, root and independent reviews remain distinct historical receipts. The complete original evidence packet, all quantitative and Fakeddit counterevidence, manuscript-version limits and R467 partial-source failures remain intact.

`FOCUSED_FAILURES = 0`

`VALIDATOR_ERRORS = 0`

`FULL_SUITE_FAILURES = 0`

`EXPORT_REPRODUCIBLE = 1`

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

The single complete suite and both sequential verification exports ran on byte-identical scientific data, code, original evidence and pending-receipt packet bytes. Only this manifest and report completion-receipt fields are finalized afterward. They are not exporter inputs. The final read-only receipt gate checks their final bytes and rechecks every invariant. No additional full-suite or export run after its own receipt is claimed.

The packet is validated for the explicit **11-file allowlist**. Publication remains pending until a safe normal fast-forward push and exact remote-SHA verification.
<!-- B1K_ADJUDICATION_VALIDATION_END -->

Required final integrity: `UNEXPECTED_CHANGED = 0`, `FROZEN_NEURIPS_CHANGED = 0`, `PREEXISTING_LOCAL_FILES_CHANGED = 0`, `IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`. These are requirements until the independent final measured gate succeeds. The dirty primary checkout and concurrent frontend work must remain unchanged.

Planned single commit: `fix: remove R542 unsupported benchmark classification`. Publication requires a fresh fetch and safe normal fast-forward, exact verified remote SHA, `HEAD == origin/main`, ahead/behind **0/0**, a clean isolated tree/index and preserved primary checkout. No force push is permitted. The containing commit and external post-push receipts supply actual publication identity without circular self-reference.

The exact reviewed explicit allowlist is:

- `data/curated/paper_taxonomy.csv`
- `data/curated/review_decisions.csv`
- `data/raw/corpus_quality_batch_b_wave_b1k_2026_10_22/evidence_manifest.json`
- `docs/corpus_quality_batch_b_wave_b1k_2026_10_22.md`
- `docs/key_paper_coverage_report.md`
- `docs/public_preview_report.md`
- `tests/baseline_expectations.py`
- `tests/test_corpus_quality_batch_b_wave_b1j.py`
- `tests/test_corpus_quality_batch_b_wave_b1k.py`
- `web/data/public_preview_map_data.json`
- `web/data/public_preview_papers.json`

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Preserved complete evidence-only report

Everything following is the complete original evidence-stage report, preserved verbatim. Its provisional findings, then-current counts, zero-authoritative-change flags and untracked-file observations describe that historical stage. The accepted disposition above supersedes only R542's administrative status; every scientific finding, source and evidence limitation remains part of the audit trail.

---

# Batch B Wave B1K — potential benchmark overclassification: evidence only

Published baseline `b2f17505f2d3a1b65d43fcf3c6582436b4fe44f8` was freshly fetched and verified with clean isolated tracked state and ahead/behind 0/0. This packet reviews exactly R467 and R542. Every outcome is provisional; both original reviews and independent P467 remain pending. No taxonomy, review decision, public export, inclusion, scope, publication or relationship record is changed.

| Review | Canonical identity | Current research types | Provisional outcome | Proposed complete research types |
|---|---|---|---|---|
| R467 | `doi:10.3390/ai5030076` | `method;benchmark` | `EVIDENCE_STILL_INSUFFICIENT` | `method;benchmark` |
| R542 | `doi:10.3390/app131910980` | `benchmark;survey` | `BENCHMARK_REMOVAL_SUPPORTED` | `survey` |

Locked R2: Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

Code release and a new dataset are not mandatory conditions. Ordinary method validation, summaries of established datasets/metrics and literature performance tables must be distinguished from an independently substantive reusable evaluation contribution. The full supporting and contradictory evidence and limitations are retained below. R215/R574/R400 are bounded precedents, not mechanically copied verdicts.

Actual unchanged corpus: public 674, formal 557, mapped 613, unmapped 61, relationship rows 1410 and unique pairs 1410.

Actual unchanged tasks: detection 621, source attribution 84, localization 45. Research types: method 578, dataset 135, benchmark 92, survey 21, analysis study 82.

Batch B: original 159 actions/148 papers; historical unresolved 143; active-public unresolved 141 actions/130 papers. These counts are recomputed and do not decrement for evidence-only proposals. R467 retains its independent P467 publication question. No new dataset/scope review action or historical ID is created.

The existing DOI-based identities are preserved. These papers do not have curated papers.csv rows; their taxonomy rows use taxonomy_id with an empty paper_id. No placeholder curated identity is inserted. Both detection tasks and all current image scopes remain exact.

## R467 — scientific review and evidence limitations

# R467 — Incomplete primary evidence; benchmark decision deferred

**Outcome: `EVIDENCE_STILL_INSUFFICIENT`.** Keep the existing `method;benchmark` set as an administrative hold. This is **not** a scientifically supported retention verdict. The original R467 action remains pending; no correction, terminal decision or new review action is proposed/applied.

## Identity and current authoritative state

*Detection of AI-Generated Synthetic Images with a Lightweight CNN*, DOI `10.3390/ai5030076`, *AI* 2024, 5(3), 1575–1593. The canonical public byline is Adrian Lokner Lađević, Tin Kramberger, Renata Kramberger and Dino Vlahek. The published span is 19 pages; no complete readable 19-page PDF was obtained. Current tasks remain `detection`; image scopes remain `fully_generated;traditional_manipulation`; research types remain `method;benchmark`. The target is resolved by taxonomy ID, with no canonical row in `data/curated/papers.csv`. The independent P467 publication question is untouched.

The original review asks for the full contribution/evaluation sections to determine whether the CNN independently contributes a reusable benchmark, rather than merely being evaluated on two existing benchmarks and custom satellite data. The original proposed removal remains a hypothesis, not an accepted conclusion.

## Source recovery and exact blocker

- [Official publisher article](https://www.mdpi.com/2673-2688/5/3/76): direct web retrieval returned HTTP 429. An exact-work search exposed a cached publisher extract with a middle gap. It is not a complete byte-captured manuscript and has no whole-source checksum.

- [Official PDF](https://www.mdpi.com/2673-2688/5/3/76/pdf): one request returned HTTP 403, curl exit 56, zero downloaded body bytes. It was not retried.

- [Institutional record](https://dk.um.si/IzpisGradiva.php?id=91710&lang=eng): the University of Maribor catalog identifies an exact-DOI/title/page candidate as Version of Record, filename `ai-05-00076-v2.pdf`, expected 38,629,090 bytes and published MD5 `AF62811927CC5E07C613F637C5D3B637`. The catalog names Renata Kovačević, while the publisher/canonical byline names Renata Kramberger. This variation is preserved without merging names.

- [Observed institutional PDF URL](https://dk.um.si/Dokument.php?lang=eng&id=203330&dn=): the single initial request returned HTTP 200 but timed out after 300.007 seconds with **15,024,008 of 38,629,090 bytes**. The partial body is retained; it is not a full manuscript.

- One missing-byte request beginning at byte 15,024,008 was ignored: the server returned HTTP 200 and the full original Content-Length, rather than the required HTTP 206/Content-Range. A remaining-size guard aborted curl with exit 63 and **zero body bytes**. Nothing was appended and no full-file restart occurred. No ETag or Last-Modified was exposed; whole-file MD5 could not be verified.

- Root made one [observed publisher XML-format check](https://www.mdpi.com/2673-2688/5/3/76/xml). It returned HTTP 403 and a **406-byte HTML denial**, not scientific XML. Curl process exit 0 does not establish HTTP success.

No additional retrieval is authorized or attempted. No complete manuscript, complete HTML/XML source or experimental table was obtained. Source failures therefore prevent the requested full scientific audit.

Publisher version notes identify original VOR on 3 September 2024, updated PDF/XML on 4 September 2024 and an HTML update on 26 June 2025. The institutional record was deposited on 29 January 2025. Catalog version metadata is not proof of byte equivalence with the blocked current publisher files.

## What the partial primary extract does and does not establish

The visible introduction and abstract identify the lightweight eight-convolution/two-hidden-layer CNN, StyleGAN transfer-learning generation and Grad-CAM++ explanation as contributions. The abstract claims 97.32% CIFAKE accuracy and comparison against four state-of-the-art approaches. These statements were not verified against complete architecture specifications or experimental rows. Exact CIFAKE and Midjourney v6 training/test usage, metrics, splits, sample IDs, comparison conditions and numerical table results remain unverified.

The visible Section 3.1 describes 50,000 cleaned 256×256 Copernicus satellite slices, plus 50,000 rotated/mirrored variants to form 100,000 GAN-training examples. Section 3.2 describes StyleGANv3 transfer learning, 900 ticks and four kimgs per tick. **Those 50,000 transformed variants must not be called 50,000 StyleGAN-generated outputs.** The separate 50,000-real/50,000-StyleGAN detection-pool claim supplied for verification is not established by the accessible partial extract.

Missing evidence includes Section 3.3, Sections 4.1–4.2, complete experimental tables, full model-comparison provenance and the final satellite detection protocol. The cached Data Availability Statement describes reporting the generation process and availability of other data online; it does not establish a verified original satellite data/split/code release.

## Fourteen review questions

1. **Primary CNN novelty.** The cached official publisher extract presents an eight-convolution/two-hidden-layer detector as the primary contribution, plus StyleGAN transfer-learning generation and Grad-CAM++ explanations. This is a source-derived contribution claim from the introduction, not a verified complete architecture or parameter-count review. Missing Section 3.3 prevents full verification. Locator: Publisher partial HTML, introduction/contribution list; Section 3.3 unavailable. Status: `PARTIAL_PRIMARY_CLAIM_ONLY`.

2. **Prediction and detection metrics.** The abstract describes real-versus-AI-generated image discrimination and reports 97.32% CIFAKE accuracy. The complete metric definitions, confusion matrices, classwise precision/recall/F1, operating threshold and experimental rows were not obtained. Do not treat the abstract claim as verified table evidence. Locator: Publisher partial HTML, abstract; Sections 4.1–4.2 and tables unavailable. Status: `EVALUATION_PROTOCOL_UNVERIFIED`.

3. **Original versus reused evaluation datasets.** The abstract says two benchmark datasets and custom Sentinel-2-derived data are used. CIFAKE is identified, but the complete data/evaluation sections needed to verify the provenance and role of each evaluation set were not obtained. Existing benchmark use does not itself establish a newly contributed benchmark. Locator: Publisher partial HTML, abstract and contribution list; missing experimental sections. Status: `EVIDENCE_INCOMPLETE`.

4. **Exact CIFAKE and Midjourney v6 usage.** CIFAKE and 97.32% are visible in the abstract. The partial Section 4.3 text refers to explanations for CIFAKE and Midjourney v6, but does not establish their exact training/test counts, image provenance, partitions, generator version usage or cross-dataset protocol. Figure labels or the user-provided source description are not substitutes for the missing experimental sections. Locator: Publisher partial HTML, abstract and Section 4.3; Sections 4.1–4.2 unavailable. Status: `EXACT_USAGE_UNVERIFIED`.

5. **Satellite construction and purpose.** Partial Section 3.1 describes collecting Copernicus imagery from cities, coasts, deserts, lowlands and tundras, extracting and cleaning 256×256 PNG slices, retaining 50,000 slices, and adding 50,000 rotated/mirrored variants to make 100,000 GAN-training examples. Section 3.2 describes StyleGANv3 transfer learning. These visible 50,000 transformed images must not be relabeled as 50,000 StyleGAN-generated images. The separate 50,000-real/50,000-StyleGAN detection-pool description supplied for verification remains unverified because the relevant later data/evaluation text and tables are unavailable. Locator: Publisher partial HTML, Sections 3.1–3.2; missing experimental sections. Status: `PARTIAL_CONSTRUCTION_ONLY`.

6. **Separately reusable satellite evaluation resource.** The visible introduction and Section 3.1 motivate satellite generation for this study and describe data preparation. That suggests a possible original resource, but a separately contributed reusable evaluation resource, final detection pool, release contents and independent evaluation role cannot be established from the incomplete source. Locator: Publisher partial HTML, introduction and Sections 3.1–3.2. Status: `R1_R2_SUBSTANCE_UNRESOLVED`.

7. **Standard benchmark splits or protocol.** No complete scientific text containing actual splits, fixed sample identifiers, validation rules, generator partitions or reusable benchmark definition was obtained. Their absence in an incomplete extract is not evidence that the full paper lacks them. Locator: Missing Sections 3.3, 4.1–4.2 and experimental tables. Status: `NOT_ESTABLISHED`.

8. **Other models under a newly contributed protocol.** The abstract claims comparison with four state-of-the-art methods, but the complete table, whether results were re-executed or literature-sourced, fairness of training conditions and whether comparison defines a separate transferable protocol are unverified. A comparison claim alone is insufficient under locked R2. Locator: Publisher abstract; unavailable experimental comparison tables. Status: `NOT_ESTABLISHED`.

9. **Future independent-method evaluation setting.** The visible stated contributions emphasize a lightweight detector, satellite generation and explanation. This creates a provisional method-validation interpretation, but the unreviewed experimental sections may contain a separate evaluation contribution. Future independent-method intent cannot be determined safely. Locator: Publisher contribution list; complete protocol unavailable. Status: `MAINTAINER_THRESHOLD_NOT_REACHED`.

10. **Ordinary use of existing benchmarks.** The abstract explicitly describes evaluation on two benchmarks rather than explicitly naming a new benchmark contribution. That supports an ordinary-validation hypothesis but is insufficient to remove an existing role without the full contribution/protocol evidence requested by the audit. Locator: Publisher abstract and introduction. Status: `REMOVAL_HYPOTHESIS_NOT_VERDICT`.

11. **Satellite benchmark versus method-specific test.** Visible satellite generation is a stated contribution and potentially reusable beyond the CNN. Whether the final satellite experiment is only a custom validation test or a substantial independent benchmark cannot be resolved without the complete protocol, baselines and data-role discussion. Locator: Publisher partial HTML, Sections 3.1–3.2; unavailable evaluation sections. Status: `UNRESOLVED`.

12. **Release of data, splits and evaluation code.** The cached publisher Data Availability Statement describes reporting the generation process and says other used data are online. No complete satellite resource release, immutable split files, evaluation package, dataset license or complete asset inventory was verified. This limited statement does not certify a public release or prove none exists. No datasets, code or supplements were downloaded. Locator: Publisher partial HTML, Data Availability Statement. Status: `RESOURCE_AVAILABILITY_UNVERIFIED`.

13. **Model comparison mistaken for benchmark.** There is a plausible overclassification concern because visible contribution statements center on the CNN and its validation. It remains an untested explanation of the current label: the inaccessible full comparison/protocol text could support a systematic framework. R2 requires substantive contribution evidence, not either automatic retention or automatic removal based on table presence. Locator: Original R467 audit question; publisher partial introduction/abstract. Status: `POSSIBLE_NOT_DEMONSTRATED`.

14. **Positive evidence against removal.** A custom, geographically varied satellite collection and documented StyleGAN transfer-learning process are genuine positive hints; applying several classifiers to a reusable fixed protocol could in principle satisfy R2. The incomplete source does not show whether this independent benchmark role is actually established. Preserve this competing interpretation and do not resolve the original review. Locator: Publisher partial Sections 3.1–3.2 and contribution list; original full-paper question. Status: `POSITIVE_HINT_NOT_SUFFICIENT`.


## Locked R2 and competing interpretations

Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

A reasonable removal hypothesis is that the visible comparisons and custom data primarily validate the CNN. A reasonable retention counterargument is that a separately reusable satellite setting or comparative framework may exist in the full paper. Neither can be decided from an incomplete source. Missing public code or a newly generated dataset is not an extra mandatory criterion under R2.

R215 supplies a conservative precedent for distinguishing substantial model-selection experiments from a separately contributed benchmark, while preserving a permissive framework interpretation. R574 supplies positive evidence of a separate open-set evaluation contribution. Their outcomes are not copied mechanically to R467. The missing new full-paper evidence prevents applying either precedent conclusively.

## OUT_OF_SCOPE_DATASET_TAXONOMY_OBSERVATION

The partial primary methods describe an original cleaned satellite collection, augmentation and StyleGANv3 transfer learning. This is a **provisional resource-contribution hint**, not an established independent R1 dataset verdict. Complete evidence is needed to determine the final real/generated counts, reusable data-resource role and availability. No `dataset` label, task label, scope change or historical Batch B action is added.

## Confidence and proposed complete types

**`EVIDENCE_STILL_INSUFFICIENT`; proposed complete set `method;benchmark` as a hold.** Confidence is high in the recorded access failures and preservation requirement. Scientific confidence in retaining or removing `benchmark` is not established. Maintainer acceptance remains pending and the original review remains unresolved.

## Retrieval accounting

New complete scientific manuscripts: **0**. Complete PDFs: **0**. Complete HTML/XML manuscripts: **0**. One blocked publisher PDF request, one partial institutional body, one rejected zero-body range attempt, and one blocked root XML-format check are all recorded separately. The exact institutional partial SHA-256 is `d129dc07bd121a6b22f08b52f1a19193776e66fe8b6f88e5d11dbfb97fcc85d0`. No whole-file checksum, complete source page count, download completeness, numerical reproduction or benchmark certification is claimed. No supplements, datasets, code archives, models or weights were downloaded.

All operational files remain in `/private/tmp/b1k-evidence-2026-10-22/r467/`. No repository edits, review decisions, exports, test-suite runs, staging, commits or pushes were performed by this reviewer.


Root assessment: Complete scientific evidence remains unavailable. Keep method;benchmark as an administrative hold, without affirming benchmark support. Missing sections 3.3/4.1/4.2 and experimental tables prevent the requested R2 contribution test. Cached construction hints do not turn augmented satellite slices into verified generated detection examples; no dataset/task/scope action is created.

Separate non-authoritative observation: {"label": "OUT_OF_SCOPE_DATASET_TAXONOMY_OBSERVATION", "status": "PROVISIONAL_PARTIAL_PRIMARY_HINT_REQUIRES_FULL_PAPER", "finding": "The partial official methods describe an original cleaned Copernicus satellite collection, spatial slices, augmentation and StyleGANv3 transfer learning. This may warrant a separately authorized R1 dataset-role question if a substantive reusable original resource is established by complete evidence. The visible 50,000 augmented variants are not 50,000 StyleGAN outputs; the separately supplied 50,000-real/50,000-generated detection-pool claim could not be verified.", "independent_R1_dataset_contribution_established": false, "dataset_addition_proposed_in_this_wave": false, "new_Batch_B_actions_added": 0, "tasks_changed": false, "image_scopes_changed": false, "current_types_preserved": ["method", "benchmark"], "future_review_boundary": "A provisional hint only, not a new review action, approval or dataset verdict."}

## R542 — scientific review and evidence limitations

### R542 — Survey versus an independently contributed benchmark

**Provisional outcome: `BENCHMARK_REMOVAL_SUPPORTED`; proposed complete types: `survey`.** This is an evidence-only proposal with **medium overall confidence**, pending maintainer acceptance. Retain `detection` and the three current image scopes; no authoritative review action closes.

**Canonical identity and original question.** `doi:10.3390/app131910980` — **A Survey of Detection and Mitigation for Fake Images on Social Media Platforms**, by Dilip Kumar Sharma, Bhuvanesh Singh, Saurabh Agarwal, Lalit Garg, Cheonshik Kim and Ki-Hyun Jung; *Applied Sciences* **2023,13(19),10980**, published **5 October 2023**. The DOI-keyed taxonomy row has a blank `paper_id`; the public legacy source record supplies the canonical paper. There is no matching curated `papers.csv` row or terminal R542 decision. Current types are `benchmark;survey`. The original R542 question asks whether an overview of existing datasets/benchmarking tools contributes an independent benchmark, requiring the full paper before any removal.

**Primary source and version boundary.** The single complete [institutional manuscript](https://www.um.edu.mt/library/oar/bitstream/123456789/123188/1/A%20survey%20of%20detection%20and%20mitigation%20for%20fake%20images%20on%20social%20media%20platforms%202023.pdf) is linked from the [University of Malta author-institution record](https://www.um.edu.mt/library/oar/handle/123456789/123188). It is **36 pages / 4,761,099 bytes**, SHA256 `430e00965954d8c1d69f017c70e567b12a973691fe8b2bd6825276a154f82ef9`; the entire paper, all ten tables and all 138 numbered references were read. It has MDPI journal layout, the exact DOI/title/six authors/date, a p.1 CC BY 4.0 statement and consistent page numbering. It is a publisher-formatted repository copy. The [official publisher PDF](https://www.mdpi.com/2076-3417/13/19/10980/pdf) returned **403 / 411-byte HTML denial**, while the [article HTML](https://www.mdpi.com/2076-3417/13/19/10980) returned **429**. Neither endpoint was retried. A direct byte comparison with the publisher file or later corrections was not possible; full publisher-version equivalence is not claimed.

**What the paper contributes.** Section 1.3 (p.4) claims comprehensive technique coverage, summarized performance comparisons, emphasis on deep learning, research challenges, and an existing dataset/metric catalog. Figure 5 (p.5) organizes image-based fake-news methods; Figure 6 (p.6) illustrates generic detection workflows. Sections 4–5 synthesize forensic,semantic,statistical,web-retrieval,neural and multimodal approaches. Section 7 (pp.29–30) identifies future research needs. These substantiate `survey`.

**All twelve benchmark questions.**

1. **Is the primary contribution a survey of existing methods?** Yes. Section 1.3 lists comprehensive coverage, summarized performance comparisons, emphasis on deep learning, future challenges and information on existing datasets/metrics. Figure 5 supplies a detection taxonomy, Figure 6 explains generic detection workflows, Sections 4–5 synthesize cited methods, and the conclusion reiterates survey findings. The paper has 138 numbered references, not an independently specified new detector or benchmark section. Locator: §1.3 p.4; Figs.5–6 pp.5–6; §§4–6 pp.8–28; §8 pp.30–31; references pp.31–36.

2. **Are technical comparisons literature-sourced or independently re-executed?** Tables 1–7 attribute rows to named source works and reference numbers. Page 25 expressly says att-RNN results are taken from Khattar and that the original att-RNN literature is not discussed. The text describes each cited method and its reported evaluation, without supplying a common re-execution environment, model checkpoints, splits, training schedules or survey-specific run outputs. This supports literature-derived comparisons. The first-person Fakeddit experiment statement on p.27 is genuine unresolved counterevidence; it prevents asserting that the authors never performed any experiment. It does not identify a reproducible survey-specific benchmark. Locator: Tables 1–7 pp.10–16,24,26; §5.2 p.25; §6.2 p.27.

3. **Does the paper contribute an original experimental benchmark?** No separately substantive original experimental benchmark is established by the complete manuscript. The tabulated outputs are attributed source-method results on existing datasets. There is no identified new benchmark name, original survey evaluation dataset, method-independent experimental output or new test-set construction tied to those tables. This is a finding about the published contribution, not proof that no unpublished or unreported experiments occurred. Locator: §1.3 p.4; Tables 1–7; §§6–8 pp.26–31.

4. **Is a new evaluation protocol explicitly defined?** The paper states a comparison-selection rule: techniques are compared when metric and dataset match (§4 p.8); it repeats accuracy/similar-dataset selection for Table 5 and similar-parameter/dataset selection for Table 6. This is positive comparative-framework evidence. However, these general grouping criteria and Figure 6 generic workflows do not specify a new operational evaluation protocol, common sample IDs, split/threshold rules, baseline retraining procedure, or a new scoring construction that can be applied as this paper's distinct contribution. No mandatory code requirement is imposed. Locator: §4 p.8; Figure 6 p.6; Table 5 introduction p.16; Table 6 discussion p.21.

5. **Is a new reusable challenge or test resource provided?** No separately contributed challenge or test resource is identified. Section 6.2 catalogs known external datasets. Section 7.1 calls for new continuously updated labeled datasets and Section 7.2 calls for cross-platform/multi-source training as future work. These motivations are useful research challenges, but the paper does not instantiate a new standardized challenge/test collection for others. Locator: §6.2 pp.26–28; §§7.1–7.2 p.29; §8 pp.30–31.

6. **Are dataset descriptions summaries of existing resources?** Yes. Table 10 contains 14 catalog rows with historical source collections, access dates and external hosts: BuzzFeed, CASIA1.0, CASIA2.0, CelebA, a row called COCO whose description refers to INRIA Holidays/Copydays, Columbia, CoMoFoD, FakeNewsNet, FNC, MediaEval2015, NIST Nimble16, PGGAN, PHEME and Weibo. Fakeddit is additionally discussed in the text and attributed as an existing benchmark in reference 127. Entries marked self-made describe source datasets, not an established new dataset produced by this survey. Resource identity/count inconsistencies remain as printed and were not externally resolved. Locator: §6.2 pp.26–28; Table 10 p.28; reference 127 p.36.

7. **Are metrics newly proposed or existing measures reviewed?** Existing measures are reviewed. Table 8 gives a conventional binary confusion matrix and Table 9 lists precision, recall, accuracy, F1, false-positive rate, false-negative rate, HTER, ROC, AUROC and a row spelled mPA that describes mean average precision. The paper presents these as prominent measures already used by researchers. FPR/FNR/HTER denominator parentheses are ambiguous as printed; they are not silently corrected or treated as new metric definitions. Locator: §6.1 and Table 8 p.26; Table 9 p.27.

8. **Do comparative tables establish an independently original benchmark framework?** They establish a structured comparative survey organized by detection category, dataset and metric, with pros/cons and representative performance. A permissive R2 reading could value this as a reusable systematic comparative framework. Under the established conservative separate-contribution threshold, the evidence remains a synthesis/catalog of published evaluations, without a separately specified method-evaluation procedure, challenge or benchmark resource beyond that synthesis. The proposed removal does not follow merely from the paper being a survey or from a lack of newly generated images. Locator: §1.3 p.4; §4 p.8; Tables 1–7; §8 pp.30–31.

9. **Is an original benchmark implementation, standardized split or protocol released?** No original benchmark implementation, immutable sample/split list, evaluation package or distinct protocol release is established in the paper. The Data Availability Statement points to publicly available datasets and links in references. Table 10 links external resource providers. No linked assets, code archives or supplements were downloaded; actual current availability of each dataset was not tested. Absence of code alone is not the reason to remove benchmark. Locator: Table 10 p.28; Data Availability Statement p.31.

10. **Is the central contribution taxonomy, synthesis and research challenges?** Yes. Figure 5 organizes image-based fake-news detection, Sections 3–5 survey tampering techniques and methods, and Section 7 synthesizes eight challenge areas: labeled datasets, cross-platform training, satire versus fake, interpretability, audio splicing, multimodal detection, deepfakes and active methods. The conclusion calls for further multimodal research and larger real-time labeled datasets. Survey is strongly supported and no survey removal is proposed. Locator: Figure 5 p.5; §§3–5 pp.6–25; §7 pp.29–30; §8 pp.30–31.

11. **Is any independent benchmark contribution substantiated?** The strongest possible evidence is the stated performance-comparison contribution, the same-metric/dataset grouping principle and the isolated first-person Fakeddit two-way-label experiment description. These are preserved rather than dismissed. But no Fakeddit result column, named survey model, split specification, scoring procedure or run is connected to that clause in Tables 5–7 or the rest of the manuscript. Selecting an existing binary label convention does not by itself establish a new reusable benchmark contribution, even if some experiment was performed. Its intended referent remains unresolved without further evidence. Locator: §1.3 p.4; §4 p.8; Tables 5–7 pp.16,24,26; Fakeddit bullet §6.2 p.27.

12. **Is retaining both survey and benchmark scientifically defensible?** The permissive interpretation is defensible as a policy reading: an openly available, organized comparison and source catalog can be reused for method selection, and R2 allows systematic comparative frameworks without new code/data. The competing conservative reading distinguishes a useful comparative survey from a separately substantive evaluation contribution. On the full published evidence, benchmark removal is provisionally supported under that conservative threshold, yielding survey only. The policy judgment has medium confidence; the survey identity and literature attribution are high-confidence findings. Maintainer acceptance remains pending. Locator: Locked R2; §1.3 p.4; §4 p.8; Tables 1–10; §§7–8 pp.29–31.

**All ten tables inspected.**

| Table | PDF page | Role and source boundary |
| --- | ---: | --- |
| 1 | 10 | Computational efficiency comparison—copy-and-move: Literature-attributed feature-dimensionality comparison, not measured common-hardware runtime. |
| 2 | 11 | Comparison of techniques used in copy–move detection using forensic features: Literature methods, heterogeneous datasets/results, pros and cons. |
| 3 | 13 | Computational efficiency comparison—image splicing: Literature-attributed feature dimensions, not a new executed speed benchmark. |
| 4 | 14 | Comparison of techniques used in splicing detection using forensic features: Literature methods, datasets, accuracy/AUC/AP, strengths and limitations. |
| 5 | 16 | Accuracy comparison of forensic methods: Dataset-indexed literature performance matrix. |
| 6 | 24 | F1-score comparison of deep learning approach: Literature F1 matrix on Columbia, CASIA1.0, CASIA2.0 and NIST16. |
| 7 | 26 | Accuracy comparison of multi-modal approach: Literature accuracy matrix on MediaEval and Weibo; p.25 explicitly attributes att-RNN scores to Khattar. |
| 8 | 26 | Confusion matrix: Generic binary classification illustration, not run-derived counts. |
| 9 | 27 | Evaluation parameters: Ten existing metric descriptions; FPR/FNR/HTER typography is ambiguous. |
| 10 | 28 | Datasets: 14 external dataset catalog rows with source providers and historical access dates. |

**Exact representative results are source-attributed literature results, not demonstrated new survey runs.** Table 1 (p.10) compares feature lengths **64/32/8/45/16/10** for DCT/PCA/DWT+SVD/FMT/improved-DCT/DCT+KPCA; Table 3 (p.13) gives **100/60/100/50/972/768** for its six cited feature sets. Their computational-efficiency captions do not establish measured common-hardware runtimes. Table 4 (p.14) reports source49 Columbia accuracy **80.79% without PCA /98.78% with PCA**, source51 **98.3/99.5/98.8%** on CASIA1.0/CASIA2.0/Columbia, and source56 AP **0.918** on Columbia.

**Table 6 (p.24), F1.** RRU-Net [96] is listed at **0.915 Columbia /0.841 CASIA2.0**; MFCN [90] at **0.611 Columbia /0.541 CASIA1.0 /0.571 NIST16**; Bappy [91] **0.764 NIST16**. Each row names a cited source; no new survey model or shared rerun specification is identified. The full matrix is retained in the JSON evidence.

**Table 7 (p.26), reported accuracy values.**

| Source model | MediaEval | Weibo |
| --- | ---: | ---: |
| att-RNN [129] | 66.40 | 77.90 |
| EANN [129] | 71.50 | 82.70 |
| SAME [130] | 77.24 | 81.58 |
| SpotFake [131] | 77.77 | 89.23 |
| MVAE [132] | 74.50 | 82.40 |
| SAFE [133] | 87.40 | 83.80 |
| EfficientNet + BERT, as printed [135] | 85.30 | 81.20 |

The text on p.25 expressly attributes att-RNN results to Khattar. Table 7 has only MediaEval and Weibo columns, not Fakeddit. The displayed source129 citation for Khattar att-RNN conflicts with the EANN entry/source129; it remains as printed. The text describes source135 with EfficientNet-B0/RoBERTa while Table 7 says EfficientNet+BERT; no correction or inference is applied.

**Retention evidence and unresolved empirical clause.** The performance-comparison contribution and same-metric/dataset rule (p.8, repeated around Tables 5–6) are meaningful positive evidence for a permissive R2 framework interpretation. The organized survey itself can be reused for method selection. Also, the Fakeddit bullet (p.27) literally states: “In the experiment, we have selected a two-way labeling of fake vs. real.” This is a genuine first-person primary-text clause, visually confirmed. It could indicate empirical activity; **the review does not assert that the authors never performed any experiment**. However, the paper provides no corresponding Fakeddit result column, survey-specific model/run, sample split or new scoring procedure that establishes an independent contributed benchmark. The intended referent remains unresolved. Even an experiment using an existing binary label choice would not automatically constitute a new benchmark.

**Metrics and resource catalog.** Tables 8–9 (pp.26–27) review a generic confusion matrix and ten established measures. Table 9 prints FPR/FNR/HTER without clear denominator grouping, and spells mean average precision `mPA`; these source issues are preserved rather than silently corrected or presented as novel metrics. Table 10 (p.28) catalogs fourteen existing external resource rows, including CASIA1.0 **800 real/921 fake**, CASIA2.0 **7,200/5,123**, Columbia **933/912**, MediaEval **193/218**, PGGAN **100,000 generated**, and Weibo **3,774/1,363**, as claimed by the survey. Fakeddit is separately discussed in text/reference 127. The table's row named COCO instead refers in text/link to INRIA Holidays/Copydays; provenance/counts are not independently verified or repaired. Entries called self-made refer to existing resource origins, not an established newly created survey dataset. The p.31 Data Availability Statement points to public datasets in references; no new survey benchmark release/splits/evaluation implementation is established. No dataset/code assets were downloaded.

**Other internal cautions.** Hussain/MultiWLD CASIA1.0/CASIA2.0 values differ between Table 2 (**92.08/95.70**) and Table 5 (**94.19/96.61**); Columbia **94.17** agrees. He et al. **89.76** appears under CASIA1.0 in Table 4 and CASIA2.0 in Table 5. These are printed survey inconsistencies, not adjudicated errors in the original studies. Same dataset/metric names do not verify common samples, scoring, preprocessing, train/test splits or operating conditions. Claims of general method superiority remain literature-synthesis judgments.

**Locked R2 judgment and precedents.** R2 permits a substantive reusable benchmark, challenge,protocol,systematic comparative framework or benchmark resource. New code, new images and independent rerunning are **not mandatory prerequisites**. R215 demonstrates the conservative distinction between valuable comparisons and a separately contributed benchmark; R574 illustrates explicit independent evaluation protocols and splits. Neither verdict is copied mechanically. For this survey, the contribution is an organized synthesis of existing evaluations; a distinct operational method-evaluation framework is not established beyond that synthesis. This supports removing benchmark under the conservative threshold. A broad framework interpretation could retain `benchmark;survey`; that competing policy reading and the first-person Fakeddit clause remain explicit. Maintainer acceptance is still required.

**Scope observation, without a new action.** The survey covers GAN/full-face synthesis and deepfakes (§3.5 p.8;§4.1.5 p.15), conventional mirroring,resampling,copy–move,splicing and JPEG manipulation, and some genuine images paired with false context in multimodal fake-news settings (§5.2). It also discusses source work on videos/audio. These endpoints are distinguished. Current `detection` and `fully_generated;deepfake;traditional_manipulation` remain unchanged; no scope/task review is created or closed.

**Retrieval accounting.** The raw-tree search scanned 1,051 unique gzip/PDF captures and 48 PDF identities; the additional TMP search scanned 1,277 unique candidate files and 58 PDF identities. Only historical metadata snapshots matched, not a complete R542 source. One official publisher-PDF attempt returned 403 with 411 HTML bytes (curl exit0 means successful transport, not manuscript success). One institutional-PDF request followed an HTTP307 redirect to HTTP200, downloaded4,761,099 bytes in 3.751763seconds and produced the complete 36-page manuscript above. The official article web access returned 429; two exact-identity search queries found the repository, and one institutional record metadata page verified identity. No repeated inaccessible endpoint retries, alternate complete versions, supplements, datasets, weights, archives or other papers were retrieved. All available transport/header/body checksums are recorded; web tools do not expose raw HTTP byte counts or exact request timestamps, so these are not invented.

**Evidence status.** Scientific evidence is sufficient for the bounded provisional `survey` proposal, with medium overall R2 confidence and high confidence in the survey/literature-source findings. Resource availability, exact source-study replication and the ambiguous Fakeddit referent remain unresolved. No authoritative metadata, review registry, public export, Git index, commit or remote reference was changed by this worker; root performs corpus/accounting/preservation checks.


Root assessment: The complete 36-page institutional manuscript supports survey and provisional benchmark removal under the conservative R2 contribution threshold. Medium confidence: same-metric/dataset comparisons and the first-person Fakeddit experiment clause support a competing permissive framework interpretation. A distinct reusable evaluation contribution is not established. No automatic survey disqualification or mandatory-code/new-data rule is imposed; maintainer acceptance remains pending.

Separate non-authoritative observation: {"label": "PRESERVED_SCOPE_OBSERVATION_NO_AUTHORITY_CHANGE", "generated_image_coverage": "§3.5 p.8 and §4.1.5 p.15 discuss GAN imagery, full face synthesis, swaps and deepfakes; §5 includes generated-face detectors.", "conventional_manipulation_coverage": "§§3.1–3.4 pp.7–8 and forensic sections cover mirroring,resampling,copy–move,splicing,JPEG manipulation and tamper-region detection.", "additional_endpoint_boundary": "§5.2 also discusses genuine images paired with misleading text/context; this is fake-news veracity and not necessarily a generated-image authenticity task. Some source work concerns videos/audio. These endpoints are not conflated.", "existing_tasks_preserved": ["detection"], "existing_image_scopes_preserved": ["fully_generated", "deepfake", "traditional_manipulation"], "new_scope_or_task_review_action_added": false, "scope_or_taxonomy_change_proposed_in_this_wave": false}

## Retrieval and version boundary

Exactly one new complete scientific manuscript was obtained: R542, a 36-page publisher-formatted University of Malta repository copy. Separate publisher byte-equivalence remains unverified. R467 produced zero complete manuscripts: publisher PDF 403, article 429, institutional 15,024,008/38,629,090-byte timeout, rejected zero-body HTTP 200 range response, and publisher XML 403. The institutional R467 Version-of-Record candidate and its expected MD5 remain unverified as a whole. No full-file restart or repeated inaccessible endpoint retry occurred; all six known document-endpoint attempts and observed metadata/search access outcomes are retained.

No supplementary resources, datasets, weights, code archives or unrelated manuscripts were downloaded or executed. All actual HTTP failures, successful repository sources, checksums and version/equivalence limitations are retained in the manifest.

## Preservation and lightweight validation

The primary checkout and all 305 existing untracked files, including 128 protected local files, remain protected. All 49 frozen NeurIPS artifacts, 119 ignored operational inputs, historical fixtures, 20 prior Batch B artifacts, Batch C’s 13 deferred debts and the separate 39-paper import inventory remain unchanged.

<!-- B1K_EVIDENCE_VALIDATION_START -->
Final lightweight checks passed: **R467 worker 38/38; R542 worker 35/35; root source/evidence checks 20/20; independent R542 cross-review 52/52** (29 primary-first checks plus 23 cross-comparisons); **preservation 38/38; independent assembled-packet review 36/36**. These validate the evidence/provenance and preservation boundaries; they do not establish a complete R467 scientific source.

R467 remains `EVIDENCE_STILL_INSUFFICIENT`; its existing types are held pending complete evidence. R542 has a complete source and a medium-confidence provisional `survey` proposal, pending maintainer acceptance. Both original actions and P467 stay unresolved. No full repository suite or offline exporter was run.

One R542 local verifier initially used an ambiguous author-only selector for two Khattar rows. It was corrected with the printed 129/132 references; the final 35 checks pass. The initial receipt is retained, and scientific evidence was unchanged.

The fresh baseline and final preservation checks authenticate all 4,480 isolated tracked files, all 4,414 primary tracked files and 305 primary untracked files, six protection groups and 20 prior Batch B artifacts. The isolated index remains empty and the tracked tree clean. Exactly the two requested B1K evidence files remain untracked, unstaged, uncommitted and unpushed. Corpus, taxonomy and Batch B counts remain as recomputed above.

`AUTHORITATIVE_CORPUS_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

All source findings, scientific records, manuscript/partial-file checksums, retrieval history and proposals were verified before these administrative completion receipts were finalized. Only validation/integrity/Git-observation fields and the report completion section change afterward. A final read-only gate records the actual finalized artifact hashes externally, avoiding a self-referential checksum.
<!-- B1K_EVIDENCE_VALIDATION_END -->

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

Only `docs/corpus_quality_batch_b_wave_b1k_2026_10_22.md` and `data/raw/corpus_quality_batch_b_wave_b1k_2026_10_22/evidence_manifest.json` are created in the repository. They remain untracked, unstaged, uncommitted and unpushed. The primary checkout is unchanged. No adjudication, remediation or subsequent wave is started.
