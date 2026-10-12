# Batch C final closeout — T527 scope resolved

Final adjudication: 2026-10-12. Starting published baseline: `829b3c79e28c02c622dde2129bd6ce7b62eeb27f`. This final section supersedes the pre-T527 freeze preserved below. The [T527 decision packet](corpus_quality_batch_c_t527_scope_decision_2026_10_11.md) and [closeout manifest](../data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json) document the conditional maintainer approval, verified manuscript, final scope judgment, reversible exclusion and version limits.

**Final coverage: 41 actions = 28 resolved + 13 external evidence debts; zero remaining maintainer judgments.** The 28 resolutions consist of 14 authoritative changes (the prior 13 plus T527's scope exclusion) and 14 no-change/policy-only resolutions. The completed Phase 1 through Wave 5C history and commit references are preserved below. This closeout opens no further evidence wave and reopens no resolved action.

## Current corpus and taxonomy

Counts are computed from the exported active identities and canonical paper–institution pairs. T527's actual prior membership is one journal paper and two distinct Fujitsu relationships; its historical metadata and source records remain intact.

| Measure | Published Wave 5C | Final closeout |
| --- | ---: | ---: |
| Public | 639 | **638** |
| Formal | 531 | **530** |
| Mapped | 617 | **616** |
| Unmapped | 22 | **22** |
| Relationship rows | 1,421 | **1,419** |
| Unique pairs | 1,421 | **1,419** |
| Detection | 587 | **587** |
| Source attribution | 85 | **84** |
| Localization | 43 | **43** |
| Method | 547 | **546** |
| Dataset | 132 | **132** |
| Benchmark | 88 | **88** |
| Survey | 20 | **20** |
| Analysis study | 78 | **78** |

## External evidence freeze — 13 unresolved

**Ten deferred alternative-source candidates:** R117, R176, R455, R460, R535, R537, R548, R549, R580 and R615. **Three blocked within the completed local audit:** T141, R376 and U010. Their scientific status remains `EVIDENCE_STILL_INSUFFICIENT`, with task 1, institution 1 and research type 11. The case-by-case reasons, original access failures, candidate identities and reopening conditions in the preserved inventory below remain applicable and unchanged. Deferred/blocked does not mean scientifically resolved or permanently inaccessible.

T527 is now resolved as `T527_SCOPE_EXCLUDE`, reason `TRAINING_IMAGE_PROVENANCE_RETRIEVAL_OUTSIDE_CORE_FORENSIC_SCOPE`, and is no longer counted as a separate maintainer judgment. The accepted five-page manuscript supports the narrow-scope exclusion; third-party hosting, the author-accepted version and uninspected final-IEEE/appendix contents remain explicit limits. Its historical task label is retained off the public map, satisfying T3 without an empty active task set.

## Validation, integrity and publication

Validation in the existing isolated worktree passed **137 focused tests and 12 subtests**, then one complete suite: **1,719 tests and 389 subtests passed, zero failures, zero skips, two existing warnings**. Current-scope curated, public, exclusion and key-paper-coverage validators returned **zero errors**. Curated warnings are 253 (one additional expected alternate-identity warning for T527's blank curated `paper_id`); public bibliography warnings remain 23 and exclusion warnings 2. No identifier was fabricated to hide that warning.

The T527 semantic check removes exactly one paper and two Fujitsu relationships; all other public records and non-timestamp metadata are unchanged. Original bibliography, taxonomy, affiliations and prior scientific evidence remain byte-identical. All 49 frozen NeurIPS files and the 128 protected primary-checkout files match their receipts. The temporary audit script and manuscript stay outside the repository and commit.

```text
FULL_SUITE_FAILURES = 0
EXPORT_REPRODUCIBLE = 1
UNEXPECTED_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0
```

Two sequential offline export verification passes completed with exit code 0. Each left all 4,296 checked paths byte-identical, including the seven deterministic outputs. No search or new source retrieval was performed.

These are pre-publication validation receipts. Commit and remote-SHA verification follow separately; no push result is pre-asserted here.

The primary checkout is not modified or fast-forwarded. The 128 excluded files, prior Batch C evidence, independent frontend work and frozen NeurIPS artifacts are protected. Only the T527 exclusion/review decision, deterministic dependent outputs, two closeout reports, supporting manifest and directly related tests belong to this change. No manuscript PDF, cache, ignored operational input or unrelated local file is staged.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

---

## Preserved pre-T527 freeze — historical, superseded where noted

The following audit was completed before the full manuscript was inspected. Its 27/14 resolution counts, 639-paper public baseline and pending T527 recommendation are historical. The final figures and disposition above supersede them. Its completed-wave history and all 13 external-debt reasons and reopening conditions remain valid.

# Batch C closeout audit and evidence-debt freeze

Evidence freeze: 2026-10-11. Published scientific baseline: Wave 5C at `829b3c79e28c02c622dde2129bd6ce7b62eeb27f` on `origin/main`. This report reconciles the original **41 Batch C actions** against the committed [Phase 1 decision sheet](corpus_quality_batch_c_decision_sheet_2026_10_05.md), the [published evidence-debt triage](corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md), successive wave reports and their paired `data/raw/corpus_quality_batch_c_wave*/evidence_manifest.json` ledgers. It does not re-adjudicate them or change authoritative data.

## Reconciled baseline and current counts

The published Phase 1 state before Wave 1 had 640 public papers, 532 formal publications, 617 mapped papers and 1,422 relationships/unique paper–institution pairs. Wave 1 excluded the text-only R188 paper, reducing public/formal by one and relationships by three; Wave 2's U017 dual affiliation added one mapped paper and two relationships. Subsequent task/type corrections changed taxonomy totals but not these corpus counts. The current figures below were recomputed from the local public export and curated context, then checked against [Wave 5C](corpus_quality_batch_c_wave5c_2026_10_09.md).

| Measure | Phase 1 published state | Current Wave 5C state |
| --- | ---: | ---: |
| Public papers | 640 | **639** |
| Formal publications | 532 | **531** |
| Mapped papers | 617 | **617** |
| Paper–institution relationship rows | 1,422 | **1,421** |
| Unique paper–institution pairs | 1,422 | **1,421** |
| Detection | 593 | **587** |
| Source attribution | 85 | **85** |
| Localization | 41 | **43** |
| Method | 548 | **547** |
| Dataset | 133 | **132** |
| Benchmark | 88 | **88** |
| Survey | 20 | **20** |
| Analysis study | 78 | **78** |

These are the present authoritative counts; projected effects of any future T527 decision are only in the separate [T527 packet](corpus_quality_batch_c_t527_scope_decision_2026_10_11.md).

## Published wave history and scientific resolutions

Each abbreviated SHA below denotes a published commit in the ancestry of Wave 5C. The linked report and its paired committed raw manifest are the action-level evidence record. The first-pass evidence waves did not settle questions merely by documenting a failed retrieval.

| Stage | Commit | Action-level result |
| --- | --- | --- |
| [Phase 1](corpus_quality_batch_c_decision_sheet_2026_10_05.md#d-maintainer-decisions--batch-c-phase-1-2026-10-05) | `ccb3fab` | Locked 12 policies; T363, R084 and R121 taxonomy corrections; L001 UCSB policy-only and P222 already-compliant/no-op. |
| [Wave 1](corpus_quality_batch_c_wave1_2026_10_06.md) | `b5766b0` | R188 text-only exclusion; P550, P586, P610 and P633 publication metadata retained. |
| [Wave 2](corpus_quality_batch_c_wave2_2026_10_06.md) | `196c9a9` | U017 author identity and explicit dual affiliation corrected; U010 left open. |
| [Wave 3A](corpus_quality_batch_c_wave3a_2026_10_06.md) | `a24a9e6` | T246 localization added; T236 remained evidence-dependent until Wave 5B. |
| [Wave 3B-1](corpus_quality_batch_c_wave3b1_2026_10_06.md) | `1e2c728` | T299 and T446 task labels retained after review. |
| [Wave 3B-2](corpus_quality_batch_c_wave3b2_2026_10_06.md) | `9b7dec4` | T024 and T136 unsupported detection labels removed. |
| [Wave 3B-3](corpus_quality_batch_c_wave3b3_2026_10_07.md) | `ea9a984` | T634 task labels retained. |
| [Wave 4A](corpus_quality_batch_c_wave4a_2026_10_07.md) | `68b61d6` | R099 dataset role removed; R190 roles retained. |
| [Wave 4B](corpus_quality_batch_c_wave4b_2026_10_07.md) | `34c5568` | R127 and R189 roles retained; R460/R537 remained insufficient. |
| [Waves 4C](corpus_quality_batch_c_wave4c_2026_10_07.md), [4D](corpus_quality_batch_c_wave4d_2026_10_08.md), [4E](corpus_quality_batch_c_wave4e_2026_10_08.md), [4F](corpus_quality_batch_c_wave4f_2026_10_08.md) | `920682a`, `de8e748`, `58fb5e5`, `0f859a4` | First-pass evidence for remaining R2/R3/R4/R1 cases; no scientific action resolved and no label changed. |
| [Evidence-debt triage](corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md) | `114d2e5` | Documented alternative primary-source candidates and three local access blocks; resolved no scientific question. |
| [Wave 5A](corpus_quality_batch_c_wave5a_2026_10_08.md) | `70a0bd3` | T611 detection removed; T576 retained after full-paper evidence. |
| [Wave 5B](corpus_quality_batch_c_wave5b_2026_10_09.md) | `805edcc` | T236 localization added; T137 detection retained after explicit authenticity evidence. |
| [Wave 5C](corpus_quality_batch_c_wave5c_2026_10_09.md) | `829b3c7` | T572 and T503 unsupported detection labels removed; final published count 13 external + T527. |

**Scientifically resolved: 27/41 actions.** Thirteen required an authoritative change: taxonomy T363, R084, R121, T246, T024, T136, R099, T611, T236, T572 and T503; R188's reversible public exclusion; and U017's affiliation correction. The eleven taxonomy changes comprise two localization additions (T246/T236) plus T363, five detection removals (T024/T136/T611/T572/T503), and three research-type corrections (R084/R121/R099). The Wave 1 exclusion removed an image-out-of-scope text paper while retaining its source provenance. U017 preserved two genuinely stated institutions rather than merging them.

Fourteen actions resolved **without authoritative corpus edits**: L001 (`R3_RESOLVED_BY_PROVENANCE_POLICY`), P222 (`ALREADY_COMPLIANT_NO_DATA_CHANGE`), P550, P586, P610, P633, T299, T446, T634, R190, R127, R189, T576 and T137. A no-change scientific resolution is not an unresolved evidence debt. The UCSB L001 source records remain intact with `DETERMINISTIC_EXPORT_COLLAPSE_AFTER_R1_R2` and `NO MANUAL R3 MERGE APPLIED`. T527 was not included among these 27 resolutions.

## Frozen external evidence debt — exactly 13

All rows below remain `EVIDENCE_STILL_INSUFFICIENT` with current assignments preserved. The source-candidate category describes a **possible next primary document**, not a successful retrieval or a scientific decision. Exact URLs, identity provenance and first-pass failure receipts are in the [published triage](corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md#complete-evidence-debt-table). Waves 5A–5C resolved six of that triage's 16 alternative-source task cases, leaving the **ten** candidates below; the **three** locally blocked cases persist. No earlier resolved action is reopened.

| Case / current assignment | Why still unresolved | Previously identified primary candidate or local block |
| --- | --- | --- |
| **R117** / `method` | Whether FSI is a substantive technical method rather than a study metric remains unverified; removing the sole current type also needs a positive replacement-role assessment. | Tech Science Press publisher PDF/record for the matching DOI; access `NOT_TESTED`. |
| **R176** / `method;dataset` | Need evidence that PRADA contributes a new reusable dataset, not merely experimental data. | Identity-matched arXiv author manuscript `2511.20068`; `NOT_TESTED`. |
| **R455** / `method;dataset` | Need construction/release evidence for a reusable dataset distinct from detector/lineage experiments. | Identity-matched arXiv author manuscript `2303.10762`; `NOT_TESTED`. |
| **R460** / `method;analysis_study` | Need independent texture/frequency/patch analysis questions and findings beyond classifier validation. | Official IEEE record for document `10860248`; possible full HTML is unverified and access `NOT_TESTED`. |
| **R535** / `method;dataset` | Need a newly contributed reusable data resource, composition and role beyond few-shot evaluation collections. | Official ECVA ECCV archive PDF `07930`; `NOT_TESTED`. |
| **R537** / `method;analysis_study` | Need independent transfer-analysis contribution beyond framework validation and ablations. | Identity-matched arXiv author manuscript `2310.04639`; `NOT_TESTED`. |
| **R548** / `method;benchmark;analysis_study` | Need a reusable evaluation benchmark/protocol, not just DE-FAKE's own comparative experiments. | Identity-matched arXiv author manuscript `2210.06998`; `NOT_TESTED`. |
| **R549** / `method` | Need IBMM technical novelty and evaluation to distinguish a real method from an illustrative survey case; any sole-type removal needs a positive role decision. | Cape Peninsula University of Technology institutional deposit, same-paper PDF; version/identity and access `NOT_TESTED`. |
| **R580** / `method;dataset` | Need a newly contributed reusable resource rather than use of existing generated-image collections. | Identity-matched arXiv author manuscript `2302.10174`; `NOT_TESTED`. |
| **R615** / `method;analysis_study` | Need independently posed open-world analysis and findings beyond validation of the proposed method. | Identity-matched arXiv author manuscript `2105.04580`; `NOT_TESTED`. |

The ten rows above are `ALTERNATIVE_PRIMARY_SOURCE_CANDIDATE`: **deferred, not permanently blocked**. The following three are `BLOCKED_PENDING_AUTHORITATIVE_EVIDENCE` only in the completed local audit; this is not a claim that no authoritative source exists elsewhere.

| Case / current state | Missing decisive evidence and why locally blocked |
| --- | --- |
| **T141** / `detection;source_attribution` | Authenticity class/protocol and real-versus-generated results distinct from model-level attribution. The known Wiley PDF returned HTTP 403; local metadata provides no defensible alternate full-text target. |
| **R376** / `method` | Ensemble specification/novelty and positive alternative research role if `method` were removed. The known ACM PDF returned HTTP 403; local DOI/bibliographic material has no verified alternate manuscript. |
| **U010** / `needs_review` | Complete identity-matched IEEE author–affiliation block after the stamp endpoint returned HTTP 418. Shanghai University and Shanghai University of Engineering Science remain separate under I1; neither city nor similar names settle the mapping. |

The external ledger is **task 1 (T141) + institution 1 (U010) + research type 11 = 13**. Exactly 10 have alternative primary candidates and 3 are locally blocked. No case is counted both ways.

## Separate T527 maintainer judgment

**T527 is the fourteenth unresolved action, not an external-debt row.** Its canonical identity is `doi:10.1109/lsp.2024.3388958`; current `source_attribution` remains public. The local abstract substantiates training-image retrieval but not an evaluated generator-identity, authenticity, or localization endpoint. No complete identity-matched manuscript is saved locally. The definitive local-evidence recommendation is `INSUFFICIENT_EVIDENCE` pending the maintainer's explicit scope interpretation and, if needed, targeted full-paper review. The [decision packet](corpus_quality_batch_c_t527_scope_decision_2026_10_11.md) evaluates `RETAIN`, `RETAG`, `EXCLUDE` and `INSUFFICIENT_EVIDENCE` and describes the reversible exclusion path. Locked T3 forbids leaving an active public paper with an empty core-task set; no T527 label or inclusion change is made here.

## Freeze, reopening and integrity

**Resolved** means a committed evidence-based disposition, whether changed or unchanged. **Deferred** means a documented alternative primary candidate with access and scientific interpretation still untested. **Blocked** means the local audit has no defensible accessible different primary target after a recorded first-pass failure. **Maintainer-pending** applies only to T527's scope choice. Frozen debts are not scientifically resolved by this report.

To reopen a deferred case, first confirm title/authors/DOI or other canonical identifiers and version for its documented primary candidate; then inspect the full method, contribution and evaluation passages that answer its row's specific question. A URL or abstract alone does not resolve a task or research-type label. To reopen T141, R376 or U010, obtain an identity-matched accessible authoritative paper or full author–affiliation block; do not infer a conclusion from inaccessible PDFs, name resemblance or a venue listing. Reopen T527 only through an explicit maintainer scope decision and, if needed, targeted full-text evidence. Any later remediation needs its own authorized, tested change and deterministic export; this freeze performs none.

The published [Wave 5C validation receipt](corpus_quality_batch_c_wave5c_2026_10_09.md#validation-and-publication) records 1,700 full-suite tests and 389 subtests passed, zero failures, two existing warnings, and two successful offline export passes that left 4,288 checked paths unchanged (`EXPORT_REPRODUCIBLE = 1`). These are historical results, not tests rerun for this evidence-only freeze.

Lightweight local reconciliation found the required corpus/taxonomy totals, 13 unique external IDs, T527 separate, and all 27 resolved IDs outside the debt list. The tracked tree and index at the Wave 5C baseline are clean; this closeout and the T527 packet are the only new untracked files in the isolated worktree. No curated, manual, raw source, public export, frontend or test file was changed; no paper was retrieved, and no full suite or export refresh was run. The 49 frozen NeurIPS file hashes and 128 protected primary-checkout excluded-file hashes match their saved receipts. Thus:

```text
AUTHORITATIVE_CORPUS_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
```

The frozen NeurIPS status remains `7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`.
