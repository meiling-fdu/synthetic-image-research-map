# Corpus Quality Batch C External Evidence and Adjudication — Wave 4F

Date: 2026-10-08. Baseline: `58fb5e557e5d5cfc8e70ad5b36e89e6b2a92d39b` (independently published Wave 4E evidence).
Status: FINAL; maintainer-approved evidence-only adjudication. R535 and R580 remain `EVIDENCE_STILL_INSUFFICIENT` / `REMEDIATION_NOT_APPLIED`, retaining `method;dataset`. Zero additional retrievals during finalization; no authoritative remediation. The 15-case census found exactly two never-reviewed cases, both governed by R1: R535 and R580. No other-policy action qualified. They were selected in ascending review-ID order; none of the nine existing research-type evidence debts was revisited.

Locked R1: Assign dataset only when a reusable dataset or data resource is itself a substantive scientific contribution. Data created or collected solely for the paper's experiments is insufficient. Public release is positive evidence, not mandatory. Only `dataset` is assessed; all other established research roles remain unchanged.

| Review | Paper | Current types | Primary source | Dataset contribution | Adjudication | Proposed types |
|---|---|---|---|---|---|---|
| R535 | Which Model Generated This Image? A Model-Agnostic Approach for Origin Attribution | `method;dataset` | [Official Springer PDF target](https://link.springer.com/content/pdf/10.1007/978-3-031-73033-7_16.pdf) | Not established from subscription preview | `EVIDENCE_STILL_INSUFFICIENT` | none |
| R580 | Towards Universal Fake Image Detectors That Generalize Across Generative Models | `method;dataset` | [Official CVPR/CVF PDF target](https://openaccess.thecvf.com/content/CVPR2023/papers/Ojha_Towards_Universal_Fake_Image_Detectors_That_Generalize_Across_Generative_Models_CVPR_2023_paper.pdf) | Not established: retrieval error | `EVIDENCE_STILL_INSUFFICIENT` | none |

**R535** — `curated:98c0322e2f8dd41d3e9e`. The PDF request redirected to the [matching publisher chapter preview](https://link.springer.com/chapter/10.1007/978-3-031-73033-7_16). Title, authors, and DOI match. Only preview content was available; the contribution/data sections were not obtained. The abstract mentions source code, which does not establish a dataset contribution. Resource identity/composition, reuse, dataset specification, experimental-only status, and dataset release/access remain unestablished. Missing evidence: an accessible authoritative full paper distinguishing a contributed reusable resource from few-shot evaluation samples. No supplement, code repository, or alternate paper was retrieved.

**R580** — `curated:1ef55e4fc03eb4880beb`. The sole CVF PDF attempt returned an internal retrieval error; no HTTP status or detailed cause was supplied. Document identity, dataset contribution, resource contents, reusability/specification, experimental role, and release/access remain unestablished. Missing evidence: an accessible authoritative full paper establishing any reusable data-resource contribution beyond evaluation on existing detection data.

Both cases remain `method;dataset` with no proposed change. Confidence is high in evidence insufficiency; scientific dataset roles are unassessed. Retrieval limitations do not establish that a dataset role is unsupported. Two primary-document attempts produced one publisher preview and one retrieval error, zero full papers, and zero sources sufficient for R1 adjudication. No retries, alternate versions, mirrors, secondary sources, search snippets, or failed response bodies.

## Research-type coverage census

Population: the 15 original residual research-type evidence actions in the approved policy ledger. Earlier Phase 1 dispositions R084 and R121 are outside these 15; R188 belongs to source-conflict review. The census was reconciled against the original decision sheet, evidence plan, approved ledger, and all eleven prior finalized wave manifests. Each of the 15 actions has exactly one disposition at each checkpoint.

| Review | Policy | Prior wave | Before Wave 4F | After Wave 4F |
|---|---|---|---|---|
| R099 | R1 | 4A | `RESOLVED_CHANGE` | `RESOLVED_CHANGE` |
| R117 | R4 | 4E | `FIRST_PASS_INSUFFICIENT` | `FIRST_PASS_INSUFFICIENT` |
| R127 | R3 | 4B | `RESOLVED_NO_CHANGE` | `RESOLVED_NO_CHANGE` |
| R176 | R1 | 4A | `FIRST_PASS_INSUFFICIENT` | `FIRST_PASS_INSUFFICIENT` |
| R189 | R3 | 4B | `RESOLVED_NO_CHANGE` | `RESOLVED_NO_CHANGE` |
| R190 | R1 | 4A | `RESOLVED_NO_CHANGE` | `RESOLVED_NO_CHANGE` |
| R376 | R4 | 4E | `FIRST_PASS_INSUFFICIENT` | `FIRST_PASS_INSUFFICIENT` |
| R455 | R1 | 4A | `FIRST_PASS_INSUFFICIENT` | `FIRST_PASS_INSUFFICIENT` |
| R460 | R3 | 4B | `FIRST_PASS_INSUFFICIENT` | `FIRST_PASS_INSUFFICIENT` |
| R535 | R1 | — | `NEVER_FIRST_PASS_REVIEWED` | `FIRST_PASS_INSUFFICIENT` |
| R537 | R3 | 4B | `FIRST_PASS_INSUFFICIENT` | `FIRST_PASS_INSUFFICIENT` |
| R548 | R2 | 4D | `FIRST_PASS_INSUFFICIENT` | `FIRST_PASS_INSUFFICIENT` |
| R549 | R4 | 4E | `FIRST_PASS_INSUFFICIENT` | `FIRST_PASS_INSUFFICIENT` |
| R580 | R1 | — | `NEVER_FIRST_PASS_REVIEWED` | `FIRST_PASS_INSUFFICIENT` |
| R615 | R3 | 4C | `FIRST_PASS_INSUFFICIENT` | `FIRST_PASS_INSUFFICIENT` |

Before Wave 4F: `RESOLVED_CHANGE = 1`, `RESOLVED_NO_CHANGE = 3`, `FIRST_PASS_INSUFFICIENT = 9`, `NEVER_FIRST_PASS_REVIEWED = 2`. After Wave 4F: `RESOLVED_CHANGE = 1`, `RESOLVED_NO_CHANGE = 3`, `FIRST_PASS_INSUFFICIENT = 11`, `NEVER_FIRST_PASS_REVIEWED = 0`. Total: 15 at both checkpoints. Complete first-pass coverage does not mean all actions are resolved.

Wave 4F outcomes: `DATASET_ROLE_SUPPORTED = 0`; `EXPERIMENTAL_DATA_ONLY_NO_DATASET = 0`; `EVIDENCE_STILL_INSUFFICIENT = 2`. Resolved changes: 0; resolved no-changes: 0. Research-type unresolved: `11 → 11`; external unresolved: `19 → 19`; total including T527: `20 → 20`. Remaining: task 7, institution 1, research type 11, external 19, T527 1, total unresolved 20. T527 is outside external totals.

Corpus unchanged: public 639, formal 531, mapped 617, relationship rows 1,421, unique pairs 1,421. Taxonomy unchanged: detection 590, source attribution 85, localization 42, method 547, dataset 132, benchmark 88, survey 20, analysis_study 78. No curated CSV changes, public export changes or regeneration, or full-suite run. Wave 4F publication is limited to this report and its manifest. The 128 excluded local files are unchanged and uncommitted.

`AUTHORITATIVE_CORPUS_CHANGED = 0` · `FROZEN_NEURIPS_CHANGED = 0` · `PREEXISTING_LOCAL_FILES_CHANGED = 0`

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
