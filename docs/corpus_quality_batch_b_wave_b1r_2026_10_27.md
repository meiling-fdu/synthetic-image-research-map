# Batch B Wave B1R — maintainer adjudication of R026 and R253

Local adjudication on 2026-10-27 (Asia/Shanghai), against published baseline `dace181c2a9edbb7c467978e9e958e83fdddc143`. The maintainer explicitly approved these two bounded additions. Both are now accepted through unique formal decision records and matching authoritative taxonomy values. This report records contribution classification; it does not certify empirical correctness, causal identification, data availability or numerical reproduction.

## Accepted decisions and formal acceptance

| Original review | Canonical paper | Before | Accepted complete types | Formal decision ID |
|---|---|---|---|---|
| R026 | `curated:386ccd052b812587c286` — All Patches Matter, More Patches Better: Enhance AI-Generated Image Detection via Panoptic Patch Learning | `method` | `method;analysis_study` | `review:001acb4497ed65ffc78b` |
| R253 | `curated:f9eac1aa13a606c6ec88` — A Sanity Check for AI-Generated Image Detection | `method;dataset` | `method;dataset;benchmark` | `review:be6652347897359ff3b3` |

Both retain exactly **`detection`** and **`fully_generated`**. No source-attribution/localization label, scope, publication, institution, affiliation or relationship change is applied. Existing method and dataset roles are retained without reopening them.

The existing registry convention is `review_queue=other`, `target_type=paper`, `action=no_action_after_review`, with an explicit `Rxxx PROPOSE_CORRECTION_ACCEPTED: Batch B review Rxxx;` note. Here `no_action_after_review` means the approved correction is complete, not that no data changed. IDs are the existing seven-field, normalized-identity SHA-256 convention, not newly invented action identifiers. Each record identifies its original research-type question, exact canonical identity, locked rule, final labels, primary source fingerprint and both unchanged B1Q artifact hashes. Creator is `maintainer-approved-batch-b-b1r`; UTC creation/update time is `2026-10-27T01:17:16Z`.

Acceptance is checked against the actual registry identity/action/note, matching corrected paper/taxonomy rows, reviewed status and primary evidence provenance. Negative-control tests reject wrong labels, identity, action, missing evidence or wrong review state. Repeated existing-schema upsert against a temporary copy of the actual registry is byte-idempotent. Exactly R026 and R253 close; no new historical action or unrelated closure is created. All 101 prior rows remain an exact byte prefix, with 103 unique decision rows afterward.

## Evidence inputs and locked rules

The complete B1Q packet is reused **byte-for-byte**, including its original pending language as an historical evidence-only snapshot. B1R's present accepted state is recorded separately in this report and the formal registry; B1Q is not rewritten to erase its provenance.

- [B1Q report](corpus_quality_batch_b_wave_b1q_2026_10_26.md), SHA-256 `bccebf430c6d39b815ae63bed40844fdc92b658bf8078e61a65ccddc174c3686`.
- [B1Q manifest](../data/raw/corpus_quality_batch_b_wave_b1q_2026_10_26/evidence_manifest.json), SHA-256 `07deb03f59a03015bb4e8b055b23e1a0f2e9ece66eba750b7354356d37981002`.
- Locked rule ledger: `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json`; exact R2/R3 records remain unchanged.

R3: Assign analysis_study only when systematic empirical or theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps, or supporting interpretability figures do not qualify by themselves.

R2: Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

### R026 — independent R3 justification and retained limits

Sections 3.1–3.2, Figures 2–4 and Appendix C investigate existing detectors' patch coverage, patch-sensitive predictions, zero-mask signed-logit responses and detector/generator differences before the PPL method. That primary scientific investigation remains informative if PPL is removed. It is therefore independently substantive under R3, rather than ordinary model ablation or a classification inferred from attention figures alone. PPL separately contributes Randomized Patch Reconstruction and Patch-wise Contrastive Learning, so `method` remains.

The official ICLR 2026 20-page source fingerprint remains `49cd7cd8be5752f4c798a2454478dc080f029a4e534805b11d40e187c7c35005`; source: https://proceedings.iclr.cc/paper_files/paper/2026/file/c5ee2a08fbe743b171b0b4b2bdfd6f86-Paper-Conference.pdf. The already completed B1Q primary investigation is reused. No manuscript download or complete scientific review is repeated.

Accepted role confidence is medium-high; empirical generality remains medium and causal/universal-mechanism/operational confidence low or unverified. The 90% random-patch result is bounded to its reported SDv1.4 setup. Zero masking can be off-distribution and changes semantics as well as artifacts. Attention/Grad-CAM and normalized CDE do not establish natural-image artifact causality, universal patch sufficiency, an exact high-impact-patch fraction or a uniquely established Lazy Learner mechanism. Repeated-seed/sample/CI definitions remain incomplete.

All numerical and source qualifications remain applicable:

- Table 1 p7 DINOv2 prints 95.9; the eight printed cells average 95.7875. The printed result is preserved separately from the recalculation.
- Table 2 p7 prints ±0.1 for DINOv2/CLIP, while printed-cell across-generator sample SDs are 1.2764076/0.4652580. Its uncertainty definition remains unresolved and is not relabeled as a verified seed variance or CI.
- Table 5 p8 SD-trained UnivFD prints 55.62 and 17.65/93.50. The latter is R253's GramNet pair; R253's UnivFD pair is 74.97/41.09. No source row is silently corrected.
- All GenImage DINOv2 prints 72.07 versus conditional 72.1232271 from R253's counts and the printed class rates. Identical releases, subsets, filtering and counts are unverified. The earlier blanket assessment that all PPL own pairs matched was retracted, not erased.
- Table 8 p15 patch size 28 reports mean 97.6 versus 97.2 for the default 14; generator-specific negative results and nonuniform superiority remain preserved.
- RPR reconstruction/replacement wording, arXiv/publisher byline/abstract observations and unverified implementation/checkpoint/split/license/reproduction remain in B1Q. Bibliography is untouched.

### R253 — independent R2 justification and retained limits

Chameleon provides a separately meaningful dual-class evaluation population, human-conditioned curation and ground truth, broader-training Setting II, common comparative scoring across three stated training regimes, and intended reuse for future methods. This evaluation function survives removing AIDE. R2 is satisfied by this independent resource/protocol role, not merely by difficult images, dataset scale, nine external detector columns or large tables. Existing `method;dataset` roles remain.

The official ICLR 2025 19-page fingerprint remains `f7657547faa18abed349e2bfc280cba433427040c00f5e4eaf19c3f25faa3244`; source: https://proceedings.iclr.cc/paper_files/paper/2025/file/b0303773962ea1b5394c3a83cc7dd066-Paper-Conference.pdf. Contribution confidence is high, empirical comparability medium, operational reproducibility low/unverified.

The accepted benchmark classification preserves these limits:

- Chameleon is 14,863 real +11,170 synthetic =26,033, not synthetic-only or balanced. Twenty workers/two judges condition fake-image selection; this is not population-wide human indistinguishability. Category imbalance, selection and semantic confounds remain.
- Table 5 has nine external columns including GramNet, whereas Section 5.1/Appendix A.1 list LGrad. The discrepancy is preserved.
- All GenImage AIDE: printed raw accuracy 65.77%, weighted recalculation 65.77162755%, fake recall 26.80%, real recall 95.06%, balanced accuracy 60.93%, FPR 4.94%. AP and AUROC are distinct and are not inferred from this operating point.
- All 30 R253 weighted rows agree within 0.008 percentage points. The original scratch claim of inconsistent rows and its explicit correction remain preserved. UnivFD's fake/real 85.52/41.56 and balanced 63.54 counter uniform AIDE superiority. Dataset total versus fake-only size comparisons are not treated as matching units.
- Pinned AIDE revision `6725b710d5c437ab2f59792908ce0377dfc907de` has MIT-licensed code; Chameleon separately has academic-only/noncommercial, email-request and approved signed-EULA access. No unrestricted dataset release or actual access grant is certified.
- Complete assets, image rights, split membership, checkpoint correspondence, training overlap, baseline fairness and end-to-end numerical reproduction remain unverified. Restricted access does not erase the scientific contribution role under locked R2.

R026's imported Chameleon/AIDE baseline scores remain direct reported reuse, not independent replication or verified identical releases. R236/R267 precedents and RefPrint/HieraSIA-Bench suggestions retain their original bounded/hypothetical status; no additional review wave or task claim is opened.

## Exact changed-file and cell scope

| File | Change |
|---|---|
| `data/curated/papers.csv` | Two existing `research_types` cells, R026/R253 only |
| `data/curated/paper_taxonomy.csv` | Two records × six fields: `research_types`, reason, primary evidence tier/source/excerpt and `audited_at` |
| `data/curated/review_decisions.csv` | Exactly two formal terminal appends; prior 101 rows byte-preserved |
| `docs/corpus_quality_batch_b_wave_b1r_2026_10_27.md` | This new adjudication/audit report |

Total: **14 existing CSV cells**, no row insertion/deletion in papers/taxonomy. Every unrelated CSV token/delimiter is preserved. The B1Q report/manifest are pre-existing untracked inputs, not B1R modifications. No repository test, baseline, public export or other tracked file changes.

## Recomputed source counts and explicit no-export boundary

Counts are derived from source: the unchanged set of 674 active public identities is matched to authoritative taxonomy CSV rows. Original review actions are reconciled against formal terminal rows, with target identity/action/evidence acceptance checked. Nothing is forced by decrementing totals alone.

| Taxonomy | Authoritative before | Authoritative after B1R | Stored public JSON, unchanged |
|---|---:|---:|---:|
| detection | 621 | 621 | 621 |
| source_attribution | 84 | 84 | 84 |
| localization | 45 | 45 | 45 |
| method | 578 | 578 | 578 |
| dataset | 138 | 138 | 138 |
| benchmark | 96 | 97 | 96 |
| survey | 21 | 21 | 21 |
| analysis_study | 85 | 86 | 85 |

Corpus remains **674 public /557 formal /613 mapped /61 unmapped /1410 relationships /1410 unique pairs**. No public identity, inclusion, publication status or paper–institution relation changes.

**The stored public JSON deliberately remains the last exported snapshot** (benchmark 96, analysis study 85). No exporter is authorized in this task. Authoritative source totals are benchmark 97 and analysis study 86. This local accepted transaction is not a claim that the website has been refreshed or published; a future separately authorized export would synchronize those displayed roles.

| Original Batch B accounting | Before | After |
|---|---:|---:|
| Historical actions /distinct papers | 159 /148 | 159 /148 |
| Historical unresolved actions /distinct papers | 133 /123 | 131 /121 |
| Active-public unresolved actions /distinct papers | 131 /121 | 129 /119 |

Each target has exactly one original Batch B action. Exactly R026/R253 close once; prior resolutions, pending R234, all task-taxonomy decisions, Batch C's 13 deferred debts and the separate 39-paper inventory remain unchanged.

## Validation and auditable receipts

- Independent B1Q/policy/provenance decision review: **62/62 passed**, no mandatory blocker.
- Independent post-application review: **76/76 passed**, actual notes/schema/identities/cells/prefix and source limitations verified.
- Targeted pytest: **91 tests +6 subtests passed; 0 failures/errors/skips/warnings**. These include 29 B1R transaction cases, 38 generic/schema/history cases and 24 preserved B1P cases.
- Formal acceptance negative controls and actual-registry-copy repeated-upsert idempotency pass.
- Curated database validator: exit 0, **0 errors /294 existing warnings**. Exclusion validator: exit 0, **0 errors /2 existing warnings**.
- No full suite, public export pipeline, manuscript retrieval, scientific experiment, staging, commit, push or publication occurred.

Existing historical B1P whole-transaction tests assert their old 101-row/14-cell endpoint against mutable current data. They were neither rewritten nor weakened. The targeted selection retains B1P science/source/identity/history tests and supplies strict current B1R transaction tests in TMP. No repository tests or baseline expectations were edited. Historical fixtures and frozen receipts are preserved. The exact command, test selection, JUnit and complete log remain outside Git.

Primary operational receipts (all outside Git):

- `/private/tmp/b1r-adjudication-2026-10-27/plan.json` and `/private/tmp/b1r-adjudication-2026-10-27/application-receipt.json`.
- `/private/tmp/b1r-adjudication-2026-10-27/policy/independent-decision-review.json` and `/private/tmp/b1r-adjudication-2026-10-27/policy/post-application-independent-review.json`.
- `/private/tmp/b1r-adjudication-2026-10-27/validation/test-selection.json`, `/private/tmp/b1r-adjudication-2026-10-27/validation/targeted-result.json`, `/private/tmp/b1r-adjudication-2026-10-27/validation/targeted-analysis.json`.
- Targeted log SHA-256 `cd87c1ed855f728a7d87318ff0c897eeea48c106ff2ab603b95bcfd349f1d59d`; JUnit SHA-256 `a12aeb2c2d861c38262d29e892ddd910bd774eb935fbd579b9064f17a0d649fa`.
- `/private/tmp/b1r-adjudication-2026-10-27/curated-result.json` and `/private/tmp/b1r-adjudication-2026-10-27/exclusions-result.json`. A wrapper-only JSON trailing-newline/regex serialization issue was repaired from preserved completed logs; original raw receipt bytes remain archived, validators were not rerun or altered.
- `/private/tmp/b1r-adjudication-2026-10-27/integrity/baseline.json` and the final preservation receipt `/private/tmp/b1r-adjudication-2026-10-27/integrity/final-preservation.json`. Final receipt hashes are recorded externally to avoid a self-referential report hash.

An early read-only pre-report audit verified the data/accounting/preservation checks but correctly failed the not-yet-created report-presence condition. That diagnostic is retained and does not represent a scientific or data failure. Full post-report preservation is measured below.

## Measured preservation and final local Git boundary

The independent post-report preservation audit passed **4,738/4,738 checks; zero failed**. Receipt: `/private/tmp/b1r-adjudication-2026-10-27/integrity/pre-stamp-preservation.json`, SHA-256 `122526853fc80496e122068fb02c442b144095cd8f2d14a3af25fc5c7fb43ace`. This measurement precedes only the documentation-only insertion of these results. The final external receipt `integrity/final-preservation.json` binds the completed report and repeats the preservation gates without changing scientific records.

```text
UNEXPECTED_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
PUBLIC_EXPORTS_CHANGED = 0
IGNORED_OPERATIONAL_INPUTS_STAGED = 0
```

All 128 protected primary-checkout files, all 49 frozen NeurIPS artifacts, Batch C's 13 deferred debts and the separate 39-paper inventory are unchanged. The primary checkout, concurrent frontend work and all other extant worktrees match their captured pre-B1R states. Both B1Q repository artifacts and all 156 previously preserved B1Q operational evidence files remain unchanged. Existing ignored operational inputs remain outside the index.

In this isolated worktree the only tracked modifications are the three intended curated CSVs. The two original B1Q inputs and this new B1R report are untracked; the index is empty, and HEAD remains `dace181c2a9edbb7c467978e9e958e83fdddc143`. `git diff --check` passes. No staged, committed, pushed, exported or published result is asserted.

Exact `git status --short --untracked-files=all`:

```text
 M data/curated/paper_taxonomy.csv
 M data/curated/papers.csv
 M data/curated/review_decisions.csv
?? data/raw/corpus_quality_batch_b_wave_b1q_2026_10_26/evidence_manifest.json
?? docs/corpus_quality_batch_b_wave_b1q_2026_10_26.md
?? docs/corpus_quality_batch_b_wave_b1r_2026_10_27.md
```

## Machine-readable local adjudication summary

```json
{
  "wave": "B1R",
  "date": "2026-10-27",
  "status": "LOCAL_ADJUDICATION_ACCEPTED_NOT_PUBLISHED",
  "baseline_commit": "dace181c2a9edbb7c467978e9e958e83fdddc143",
  "decisions": {
    "R026": {
      "paper_id": "curated:386ccd052b812587c286",
      "decision_id": "review:001acb4497ed65ffc78b",
      "before": "method",
      "after": "method;analysis_study",
      "locked_policy": "R3"
    },
    "R253": {
      "paper_id": "curated:f9eac1aa13a606c6ec88",
      "decision_id": "review:be6652347897359ff3b3",
      "before": "method;dataset",
      "after": "method;dataset;benchmark",
      "locked_policy": "R2"
    }
  },
  "authoritative_existing_cells_changed": 14,
  "prior_terminal_rows": 101,
  "terminal_rows_after": 103,
  "B1Q_inputs_sha256": {
    "data/raw/corpus_quality_batch_b_wave_b1q_2026_10_26/evidence_manifest.json": "07deb03f59a03015bb4e8b055b23e1a0f2e9ece66eba750b7354356d37981002",
    "docs/corpus_quality_batch_b_wave_b1q_2026_10_26.md": "bccebf430c6d39b815ae63bed40844fdc92b658bf8078e61a65ccddc174c3686"
  },
  "authoritative_taxonomy_before": {
    "detection": 621,
    "method": 578,
    "analysis_study": 85,
    "survey": 21,
    "source_attribution": 84,
    "dataset": 138,
    "benchmark": 96,
    "localization": 45
  },
  "authoritative_taxonomy_after": {
    "detection": 621,
    "method": 578,
    "analysis_study": 86,
    "survey": 21,
    "source_attribution": 84,
    "dataset": 138,
    "benchmark": 97,
    "localization": 45
  },
  "unchanged_corpus": {
    "public": 674,
    "formal": 557,
    "mapped": 613,
    "unmapped": 61,
    "relationship_rows": 1410,
    "unique_paper_institution_pairs": 1410
  },
  "batch_b_before": {
    "historical_actions": 159,
    "historical_papers": 148,
    "historical_unresolved_actions": 133,
    "historical_unresolved_papers": 123,
    "active_public_unresolved_actions": 131,
    "active_public_unresolved_papers": 121
  },
  "batch_b_after": {
    "historical_actions": 159,
    "historical_papers": 148,
    "historical_unresolved_actions": 131,
    "historical_unresolved_papers": 121,
    "active_public_unresolved_actions": 129,
    "active_public_unresolved_papers": 119
  },
  "targeted_tests": {
    "passed_regular": 91,
    "passed_subtests": 6,
    "failed": 0,
    "errors": 0,
    "skipped": 0,
    "warnings": 0
  },
  "public_exporter_runs": 0,
  "full_suite_runs": 0,
  "staging_operations": 0,
  "commits": 0,
  "pushes": 0
}
```

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
