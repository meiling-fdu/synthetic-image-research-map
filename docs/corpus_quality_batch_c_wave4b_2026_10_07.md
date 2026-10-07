# Corpus Quality Batch C External Evidence and Adjudication — Wave 4B

Date: 2026-10-07. Baseline: `68b61d6d9a3fdaa919053617ad7b4faf1e94af09`.
Status: FINAL; maintainer-approved evidence-only adjudication. R127 and R189 are `EVIDENCE_RESOLVED_NO_CHANGE` / `REMEDIATION_NOT_REQUIRED`. R460 and R537 remain `EVIDENCE_STILL_INSUFFICIENT` / `REMEDIATION_NOT_APPLIED`. No authoritative remediation. Scope is locked R3 (`analysis_study`) only. Four previously unreviewed cases were selected in ascending review-ID order. One primary document was attempted per case; two were accessible. No retries, alternate versions, mirrors, secondary sources, or remediation.

| Review | Paper | Current types | Primary source | Analysis as primary contribution? | Systematic scope | Adjudication | Proposed types |
|---|---|---|---|---|---|---|---|
| R127 | GlobalForge: Towards Robust AI-Generated Image Detection | `method;analysis_study` | [arXiv paper](https://arxiv.org/pdf/2607.14684) | Yes | Preprocessing and detector fragility | `ANALYSIS_STUDY_SUPPORTED` | retain `method;analysis_study` |
| R189 | Reduce the Artifact Bias for More Generalizable AI-Generated Image Detection | `method;analysis_study` | [arXiv paper](https://arxiv.org/pdf/2605.14486) | Yes | Artifact-source bias and gradient conflict | `ANALYSIS_STUDY_SUPPORTED` | retain `method;analysis_study` |
| R460 | Detecting AI Generated Images Through Texture and Frequency Analysis of Patches | `method;analysis_study` | [IEEE paper target](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10860248) | Not established | Not established | `EVIDENCE_STILL_INSUFFICIENT` | none |
| R537 | X-Transfer: A Transfer Learning-Based Framework for GAN-Generated Fake Image Detection | `method;analysis_study` | [IEEE paper target](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10650566) | Not established | Not established | `EVIDENCE_STILL_INSUFFICIENT` | none |

**R127.** Contribution 1 and section 3 (pp. 2–4, figures 2–3) separately establish a detector-fragility diagnosis. Controlled preprocessing and attention comparisons support R3; section 6.4 ablations alone would not. Confidence: high.

**R189.** Contribution 1 and sections III-A/B (pp. 2–5, figures 2–4) separately characterize artifact bias through matched training comparisons and gradient diagnostics. Conditional theory accompanies those findings; routine ACEF evaluation is not the basis. Confidence: high.

**R460.** The sole official IEEE paper target returned an internal retrieval error. Contribution framing, analysis scope/methodology, independent findings and routine-evaluation signals remain unestablished. No proposal; high confidence in the insufficiency determination, not in a scientific-role classification.

**R537.** The sole official IEEE paper target returned an internal retrieval error. Contribution framing, analysis scope/methodology, independent findings and routine-evaluation signals remain unestablished. No alternative arXiv version was retrieved. No proposal; high confidence in the insufficiency determination, not in a scientific-role classification.

Evidence outcomes: `ANALYSIS_STUDY_SUPPORTED = 2`; `ROUTINE_EVALUATION_NO_ANALYSIS_STUDY = 0`; `EVIDENCE_STILL_INSUFFICIENT = 2`. External unresolved: `21 → 19`; research-type evidence: `13 → 11`. Remaining: task 7, institution 1, research-type 11, external total 19, T527 1, total unresolved 20. Existing evidence debts remain unresolved; T527 is outside external totals.

No corpus/export edits: public 639, formal 531, mapped 617, relationships 1,421, unique pairs 1,421. Taxonomy remains detection 590, source attribution 85, localization 42, method 547, dataset 132, benchmark 88, survey 20, analysis_study 78. Publication includes only this evidence report and its manifest.

`AUTHORITATIVE_CORPUS_CHANGED = 0` · `FROZEN_NEURIPS_CHANGED = 0` · `PREEXISTING_LOCAL_FILES_CHANGED = 0`

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
