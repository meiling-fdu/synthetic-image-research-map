# Batch B Wave B1A — scope evidence for L015 and P562

**Final adjudication: both `EXCLUDE_OUT_OF_SCOPE` decisions accepted and reversible exclusions applied.** Original affiliation/year questions remain unresolved historical metadata. No canonical record or historical taxonomy was deleted or retagged.

Artifact date: **2026-10-12**, as requested. Manuscript review and exclusion application: **2026-10-13**. Adjudication validation finalized **2026-10-15 (Asia/Shanghai)**. This packet resumes the interrupted review using the original manuscript review and preserved notes; no manuscript was retrieved again. The machine-readable companion is [the evidence manifest](../data/raw/corpus_quality_batch_b_wave_b1a_2026_10_12/evidence_manifest.json).

## Published intake and scope of this wave

The intake was independently committed and published as `91de08a904847c47f60eb3dfd124e3db3300a459`, `docs: add batch-b intake and priority triage`. Its sole committed file is `docs/corpus_quality_batch_b_intake_triage_2026_10_12.md` (462 insertions). The scientific baseline remains `b41a506453cd0a4c985bf7d1a63e6b2a2d391539`.

The previous successful normal push and fetched synchronization were reused. A read-only remote query during continuation again returned `91de08a904847c47f60eb3dfd124e3db3300a459`; local HEAD and `origin/main` agree, ahead/behind **0/0**. Intake publication was not repeated.

Only L015 and P562 are reviewed here. Scope preflight is linked to their existing review IDs, without inventing extra pending actions. No other Batch B case, Batch C debt or Batch D case is reviewed. The original L015 affiliation question and P562 publication-year question remain pending.

## Locked policy

The governing source is [`batch_c_policy_decisions.json`](../data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json), finalized 2026-10-05. T3 has decision `MODIFY_AND_ACCEPT` and states exactly:

> Every public paper must remain connected to at least one core forensic task represented by the map: detection, source_attribution, or localization. If careful review establishes that none applies, the record requires scope review rather than an empty task set.

The finalized rule supersedes the earlier proposal permitting empty task sets. It routes a verified lack of core-task applicability to scope review; it does not automatically apply an exclusion or authorize a placeholder label.

T1 requires an explicit authenticity/real-versus-generated task to justify detection. T2 requires evaluated spatial forensic predictions of synthetic/generated/edited content. Physical-object defect boxes, supplied disclosure labels and generic signal-detection terminology do not establish those tasks. The manifest preserves the exact T1/T2 wording as well. These conclusions concern the evaluated endpoints; they do not establish a new policy excluding human-participant research.

## L015 — canonical identity and history

**Canonical paper:** *"That's Another Doom I Haven't Thought About": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation*.

- Paper ID: `curated:75cbd31c9946c7eb7977`.
- DOI: `10.1145/3772318.3791006`; arXiv: `2505.22845`.
- Ordered authors: Sandra Höltervennhoff; Jonas Ricker; Maike M. Raphael; Charlotte Schwedes; Rebecca Weil; Asja Fischer; Thorsten Holz; Lea Schönherr; Sascha Fahl.
- Evidence-baseline state (before exclusion): public, formal CHI 2026 conference paper; tasks `[]`; research type `analysis_study`; **5 exported relationships / 5 unique pairs**.

The original [relationship ledger](../data/raw/corpus_quality_audit_2026_10_04/relationship_review.json), `records[review_id=L015]`, flags `PUBLIC_INSTITUTION_NOT_IN_CURATED_REGISTRY`: Leibniz University Hannover (`institution:ac9dc63b4bd4669a`) and Hannover Re (Germany) (`institution:aeb3cd858bb22d74`). Its question requires paper-time affiliation evidence to distinguish institution/lab/funder/extraction error before any registry or relationship correction. That question is not adjudicated by this scope review.

The empty task set was deliberate. July commit `cb50812922a57df6a77a5701a7a3de50cc6e9cb2` carried legacy detection. September taxonomy migration `02a324cb8ebc238a9332cb91aabbd902e2bd4090` retained an in-scope analysis study with empty tasks, using the September 4 audit and abstract. The taxonomy receipt explains that no controlled detection, source-attribution or localization task applied. Locked T3 subsequently named this pre-existing empty-task record for scope review. This is not an export omission or a missing-value repair.

Existing local abstract, taxonomy history and identity reconciliation established the question but did not establish every experimental endpoint. Full methods were therefore necessary. Local provenance includes `data/curated/paper_taxonomy.csv`, `docs/paper_taxonomy_migration_audit_2026-09-04.md`, the locked policy ledger, and publisher-deposited `data/raw/key_paper_reconciliation_2026_09_08/crossref_270.json`. Exact locators and hashes are retained in the manifest.

### Source and version

One complete manuscript was retrieved: [arXiv 2505.22845v2](https://arxiv.org/pdf/2505.22845v2), revised **2026-03-09**, 32 PDF pages including its bound appendices. Title, all nine ordered authors, arXiv version and CHI DOI were checked on the first page and against the existing canonical record. The paper identifies itself as an author version and points to the definitive CHI publication. No publisher-final equivalence is claimed; no ACM manuscript or separate supporting material was retrieved.

SHA-256: `e6bac57d853d5d7b33c8b068eafd128885de79bbe393baf93f016563f5aa3e8c`.

### Scientific task, classes and evaluated outputs

The research asks how AI-image labels and label errors affect expectations, factual beliefs and trust. Study 1 comprises five focus groups with 18 participants and thematic coding of labeling opinions (sections 3.1–3.2 and Appendix A).

Study 2 uses **1,354 valid participants**, after 51 exclusions from 1,405 completions. Its design crosses image origin (human/AI), claim veracity (true/false) and assigned group (control/labeling/mislabeling). Each participant sees the same 24 posts, six per image-origin/claim cell, plus two attention checks (section 4.1, Tables 2–3, Figure 1).

The inputs are simulated social posts containing human-made or AI-generated images and factual captions. AI origin and label presence/correctness are controlled stimulus factors. The measured response for each post is a **yes/no judgment about its factual claim**, followed by confidence on a four-point scale. The answer classes are not human-versus-AI image origin. True claims can accompany generated images; false claims can accompany human-made images. Captions were adjusted where needed to construct the AI/true cell. Appendix B.5–B.7 and Table 7 enumerate the full instrument and stimuli.

Section 4.1 defines accuracy using claim truth. Hits are true claims rated true; false alarms are false claims rated true. Sensitivity is `d′ = z(H) − z(FA)` and response bias is `c = −(z(H) + z(FA))/2`. Section 4.2 models claim accuracy with a GLMM and analyzes sensitivity/bias with ANOVA. These metrics do not measure image-origin detection.

| Locator | Reported result | What is measured |
| --- | --- | --- |
| PDF p. 11, section 4.2 / Figure 2a; contrasts in Table 5 | AI/false claim correctness: **84.9% labeled versus 82.1% unlabeled**; control-versus-treatment contrast `z = 3.47`, `p < 0.001` | Correct rejection of false factual claims, stratified by known stimulus origin |
| PDF p. 11, section 4.2 | Mean claim sensitivity **0.47 control versus 0.41 treatment**, `p = 0.046` | Discrimination of true versus false claims |
| PDF p. 13, Figure 3b; p. 26, Appendix B.5 Q4/Q5 | **67.3%** of labeling-group and **72%** of mislabeling-group participants thought they noticed unlabeled AI images | Retrospective global impression; no identified-image origin prediction or scored authenticity accuracy |

### Counterexamples and scope finding

The strongest counterexample is the supplementary questioning about image mislabeling. Q4/Q5 ask whether participants had the impression that some earlier images were wrongly labeled; they do not identify which images or solicit image-by-image origin predictions. The correctly labeled group nevertheless reports substantial perceived mislabeling. These results address perceptions and trust, not an independently evaluated authenticity task. Appendix A.5's focus-group recognition questions likewise concern prior experiences and opinions, not scored trials.

The paper discusses detectors, C2PA and watermarking as background or possible labeling mechanisms. No independent computational authenticity detector, generator/model-source predictor or spatial forensic prediction is evaluated in the examined main paper or bound instruments. The presence of human participants alone is not the exclusion basis: the decisive distinction is **claim-veracity response versus image-origin response**.

**Accepted outcome: `EXCLUDE_OUT_OF_SCOPE`; reversible exclusion applied.** Evidence is scientifically sufficient for this scope proposal under existing T3. Confidence is **high within arXiv v2**; publisher-final equivalence remains unverified. The conclusion concerns what is reported and evaluated in that version, not what any discussed system could theoretically do.

The maintainer accepted the scope decision. The established exclusion registry now suppresses this paper and its five exported relationships while retaining canonical metadata, affiliations and historical empty-task/analysis-study taxonomy. One public, formal and mapped paper and one public analysis-study contribution were removed. No placeholder task was assigned. The original affiliation question remains unresolved and no longer applies to an active public paper.

## P562 — canonical identity and history

**Canonical paper:** *Generating Synthetic Training Images to Detect Split Defects in Stamped Components*.

- Paper ID: `doi:10.1109/tii.2023.3329711`; DOI: `10.1109/TII.2023.3329711`.
- Ordered authors: Aru Ranjan Singh; Thomas Bashford-Rogers; Sumit Hazra; Kurt Debattista. The public name uses a typographic hyphen; the manifest preserves that literal form separately.
- Evidence-baseline state (before exclusion): public, formal journal paper in *IEEE Transactions on Industrial Informatics*, year **2023**, publication date `2023-11-14`; task `detection`; research type `method`; **1 exported relationship / 1 unique pair**, University of Warwick.

The original [publication ledger](../data/raw/corpus_quality_audit_2026_10_04/publication_metadata_review.json), `formal_records[review_id=P562]`, has `SOURCE_CONFLICT`: current 2023 versus cached publisher-deposited 2024. Its question is to check publisher online/issue dates against the repository year convention. **That review status and every bibliographic field remain unchanged.**

Local ingestion provenance matched generation and detection keywords; the existing abstract-tier taxonomy receipt has a title-only task excerpt. The abstract describes synthetic data for industrial inspection, but it did not establish the complete set of evaluated tasks. Exact DOI, title and four ordered author identities were recovered from `data/raw/venue_audit_crossref/b4d3dd6ca60b58bc701a.json`. Full methods and results were needed to determine whether a separate forensic endpoint existed.

### Source, identity exception and version

One complete manuscript was retrieved from the author institution: [Warwick Research Archive Portal item 180984](https://wrap.warwick.ac.uk/id/eprint/180984/), [accepted-manuscript PDF](https://wrap.warwick.ac.uk/id/eprint/180984/7/WRAP-generating-synthetic-training-images-detect-split-defects-stamped-components-2023.pdf). It contains **11 PDF pages: one repository cover and ten article pages**.

The repository supplies the exact title, DOI and four ordered authors and binds them to the saved PDF. The title page visibly prints **Thomas Bashfod-Rogers**, an apparent missing-r draft typo; this is disclosed rather than asserted to be a perfect character match. A DOI was not observed in the extracted article, so DOI identity relies on the repository and saved publisher metadata. Some running headers retain a different title about HDR split-defect detection; the front title, repository binding and continuous article body establish this manuscript's identity. No canonical author or title correction is applied.

The cover expressly identifies an **author accepted manuscript** that may differ from the Version of Record. Repository dates provide version context (accepted October 18, 2023; available November 14, 2023; publication March 2024), not authorization to resolve the separate year question. No publisher-final comparison was performed.

SHA-256: `38da430f65cd32c2cc73af4b827ea1a061ed7fbdc9835f2f1bced73947e38fd1`.

### Method, classes and evaluated outputs

Sections III–IV present a synthetic-data pipeline for physical stamped-metal split defects. Finite-element geometry/strain and a forming-limit curve identify plausible defect sites. Captured crack textures, reflectance/impurities and rendering produce training imagery. Neck and split defects are grouped as split defects.

Inputs are captured or rendered HDR component images. Synthetic imagery augments scarce industrial training data. The evaluated predictors—YOLOv5, Faster R-CNN and DETR—output **physical defect regions/bounding boxes and confidence**. The target class concerns splits in manufactured objects; numeric class IDs are not enumerated in the examined manuscript. “Real” and “synthetic” identify data domains, not predicted authenticity classes.

Section V describes 120 in-house defective Nakajima parts, ten real samples for the split-texture dictionary, human annotations of real defects and automatically generated synthetic defect annotations. Label randomization adjusts synthetic boxes. Models are trained for 2,000 epochs with five-fold cross-validation and matching fold test sets across experimental combinations. Figure 9 shows defect-mask construction; Figures 12–13 show predicted defect boxes against ground truth.

Section VI.A defines `mAP50` and `mAP` across IoU thresholds 0.50–0.95 at 0.05 intervals. All numerical values below use the manuscript's **mAP50 (mAP)** notation and refer to physical defect detection.

| Locator | Reported result | Interpretation |
| --- | --- | --- |
| PDF p. 8 / article p. 7, Table II, YOLOv5, 80-real row | **0.978 (0.665)** real-only baseline; **0.981 (0.688)** with 80 additional synthetic samples | Rows count real training images; columns count added synthetic images |
| PDF p. 9 / article p. 8, Table III, 80-real column | Pre-trained **0.928 (0.613)**; Stable Diffusion **0.933 (0.605)**; DFMGAN **0.956 (0.623)**; proposed method **0.981 (0.688)** | Alternative training-data approaches evaluated through the same defect task, not generator attribution |
| PDF p. 10 / article p. 9, Table IV, C2+C3 | Synthetic test domain **0.990 (0.756)**; real test domain **0.822 (0.456)** | Defect performance in two test domains, not authenticity-classification performance |

### Counterexamples and scope finding

All reported protocols were checked: varying real/synthetic training counts, comparison with pretraining/GAN/diffusion augmentation, qualitative predictions and synthesis ablations. The boxes and masks mark physical cracks or splits, not synthetic or manipulated image provenance. Comparing generators as augmentation sources does not create a source-attribution predictor. Real/synthetic realism illustrations (Figures 10–11) do not supply a scored authenticity classifier.

No evaluated synthetic-origin detection, generator/model attribution or manipulated-region forensic endpoint is reported in this manuscript. This is a statement about the examined work's task, not an assertion that its network architectures cannot be used elsewhere for forensics.

**Accepted outcome: `EXCLUDE_OUT_OF_SCOPE`; reversible exclusion applied.** The manuscript supplies scientifically sufficient evidence, with **high confidence within the accepted version** and unverified publisher-final equivalence. The accepted reversible exclusion now removes one public, formal and mapped paper, one relationship/pair and one public detection/method contribution. Canonical bibliography, historical taxonomy and the unresolved publication-year question remain intact; there is no publication update or retagging.

## Evidence budget and accounting

Exactly **two full manuscripts were retrieved and reviewed, one per case**. Both successful saved downloads were reused. There were **zero full-manuscript retries, zero separate supplements and zero new manuscript retrievals during continuation**. L015's bound appendices belong to the same PDF. No unrelated manuscript, analysis code or participant dataset was downloaded.

Before the interruption, P562's exact DOI was used for one targeted manuscript-location search. The author-institution landing page was inspected and its HTML saved to recover the supplied PDF link. A search-service IEEE robots notice was not a failed full-manuscript request; no IEEE PDF was requested or retried. Known ACM/IEEE publisher locators remained unrequested. The manifest records URLs, HTTP results, timestamps, byte counts, hashes and version restrictions. PDFs, extracted text and renderings were kept only as temporary files outside the repository. Those old temporary files are no longer present; preserved provenance and scientific notes were reused without another retrieval.

## Final scope and review accounting

Two scope decisions are completed and two reversible exclusions applied. **Zero original metadata questions are scientifically resolved or formally closed.** L015's affiliation-registry uncertainty and P562's publication-year conflict remain in the unchanged original ledgers. They are no longer applicable to active public papers but are retained as unresolved historical metadata; no new authoritative status vocabulary is introduced.

| Review dimension | Historical pending actions | Active-public applicable actions |
| --- | ---: | ---: |
| Unmapped | 20 | 20 |
| Task taxonomy | 9 | 9 |
| Research type | 43 | 43 |
| Relationships | 25 | 24 |
| Publication | 62 | 61 |
| **Total actions** | **159** | **157** |
| **Unique affected papers** | **148** | **146** |

All 11 papers with independent multiple questions retain those questions. The two excluded-paper actions are retained/deferred for historical provenance, not deleted or counted as metadata resolutions. Batch C remains 41 total actions, 28 resolved, 13 deferred external debts and zero maintainer judgments.

## Actual public-data delta

The recovered offline export was verified against published `91de08a904847c47f60eb3dfd124e3db3300a459`. Exactly L015 and P562 are removed. Every retained public paper and relationship is semantically identical and remains in the same order; top-level data is unchanged apart from the generated timestamp. Institution registries and canonical paper/taxonomy/affiliation sources are byte-preserved.

| Measure | Before | After |
| --- | ---: | ---: |
| Public papers | 638 | 636 |
| Formal publications | 530 | 528 |
| Mapped papers | 616 | 614 |
| Unmapped papers | 22 | 22 |
| Relationship rows | 1,419 | 1,413 |
| Unique paper–institution pairs | 1,419 | 1,413 |
| Detection | 587 | 586 |
| Source attribution | 84 | 84 |
| Localization | 43 | 43 |
| Method | 546 | 545 |
| Dataset | 132 | 132 |
| Benchmark | 88 | 88 |
| Survey | 20 | 20 |
| Analysis study | 78 | 77 |

L015 loses five exported relationships: Leibniz University Hannover; CISPA Helmholtz Center for Information Security; Hannover Re (Germany); Ruhr University Bochum; Max Planck Institute for Security and Privacy. This is paper-scope suppression, not verification, merging or correction of those affiliations. P562 loses its University of Warwick relationship. The manifest records all six row IDs and institution IDs. No unrelated relationship is removed or modified.

The generated missing-author report removes only these two papers and reranks retained rows. Key-paper coverage changes only checklist row 270 (L015), from public marker coverage to excluded. The initial completed export was reused; generated JSON was never manually edited.

## Validation and preservation

B1A evidence-only validation previously passed 51 lightweight checks. That historical result is preserved separately and does not substitute for adjudication validation. The recovered environment uses Python 3.14.7, pytest 9.1.1 and bundled Node 24.19.0. Local cached wheels supplied the recovered runtime; 104 operational inputs and 15 historical fixtures match the previously validated source worktree. No manuscript retrieval or new review wave occurred.

The first full-suite run completed with **1,735 passed, 3 failed, 389 subtests passed and 2 existing warnings** (exit 1). Each failure was diagnosed before its authorized correction and rerun:

1. The result-card test selected excluded L015 and raised `StopIteration`. It now uses still-public ForensicHub with the same five-affiliation/nine-author coverage; rendering assertions and production frontend behavior are unchanged.
2. The institution-audit test wrote to its default tracked output even under `--check`, dropping two L015-only public institution rows and causing the later frozen migration receipt check to fail. Its output now goes to a temporary directory and the test checks that the historical report is untouched. Only the accidental report rewrite was restored; the frozen receipt digest remains `382a3094b144ca6c3336095248d9327d4474ddfbc7a46b09838ae28f760aa82d`.
3. The current key-paper verifier expected 13 excluded checklist rows; L015 makes 14. The verifier now checks active-registry evidence and absent public/map membership for each excluded row. Current coverage assertions are 283 bibliography, 282 mapped, 1 list-only, 14 excluded and 2 ambiguous. Frozen primary-curation counts and historical traces remain unchanged.

The second run completed with **1,736 passed, 2 failed, 389 subtests passed and 2 existing warnings**. Both remaining historical guards reported exactly one extra path, `tests/test_institution_type_audit.py` (28 versus 27 and 27 versus 26). Their shared helper now verifies this exact file against its pinned published pre-B1A version and complete reviewed successor digest, then retains exact changed-path and count comparisons. Frozen receipts and baseline hashes are untouched. Negative tests confirm that an unrelated path, altered successor bytes or wrong predecessor digest still fail. The two original guards passed first, followed by the institution-audit test and four boundary regression cases.

| Validation | Result |
| --- | --- |
| Prior focused checks, reused | 184 passed; 12 subtests passed; 0 failures |
| Exact affected tests, including side-effect regression | 4 passed; 0 failures |
| Historical integrity guards | 2 passed; 0 failures |
| Institution audit and boundary regressions | 5 passed; 0 failures |
| Final full suite | 1,742 passed; 389 subtests passed; 0 failures; 0 skips; 2 existing warnings |
| Curated database validator | 0 errors; 254 warnings |
| Public preview validator | 0 errors; 0 map warnings; 23 paper warnings |
| Exclusion validator | 0 errors; 2 restored-record warnings |
| Key-paper coverage freshness check | Exit 0; 0 errors |
| Two sequential offline export passes | Both exit 0; 4,420 paths byte-identical on each pass; all 7 expected generated outputs unchanged |

`HISTORICAL_INTEGRITY_FAILURES = 0`

`FULL_SUITE_FAILURES = 0`

`EXPORT_REPRODUCIBLE = 1`

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

The explicit scope contains 32 files: two exclusion/review CSVs, seven dependent outputs, two evidence artifacts, twenty test files (including the current baseline and historical-boundary helpers), and one read-only audit-verification helper. Temporary analysis scripts, manuscripts and all 119 ignored inputs are excluded from staging. Final staged-content and remote-state checks are required before reporting publication.

All 49 frozen NeurIPS artifacts and Batch C's 13 evidence debts are preserved. The primary checkout is read-only and remains on its independent HEAD; its 128 protected excluded files and two older Wave 5B evidence artifacts are not staged. Recovery re-established full byte snapshots for finalization after temporary files were cleared. Historical receipts independently matched 102 complete protected files and 20 response payloads; six diagnostic files lack a recovered historical digest. Earlier verified preservation is retained, while the new snapshot provides exact before/after verification through this finalization.

7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA

The publication gate requires one commit with subject `fix: exclude out-of-scope batch-b wave b1a papers`, normal fast-forward push and subsequent remote-SHA verification. No primary-checkout advancement or frontend behavior change is part of this wave.
