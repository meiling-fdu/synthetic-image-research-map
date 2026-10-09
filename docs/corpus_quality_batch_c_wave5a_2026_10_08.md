# Batch C Wave 5A — finalized adjudication

Evidence review: 2026-10-08. Maintainer adjudication: 2026-10-09.

## Scope and publication

The triage report was independently committed and pushed as `114d2e5f352f39f6c3a484e43f3aac593eb7cf64` (`docs: add batch-c evidence-debt triage`). Push result: `0f859a4..114d2e5 main -> main`. A subsequent fetch verified `HEAD = origin/main` and ahead/behind `0 / 0` before this review began.

Exactly two T1 cases were reviewed: **T576 and T611**. Exactly two full papers were retrieved, one different authoritative work document per case. The other 17 external debts and T527 were not revisited. Exactly one authoritative task correction is applied: T611 loses `detection` and retains `source_attribution`. T576 requires no authoritative change. Research types, publication and institution metadata remain unchanged.

## Retrieval and source provenance

The initial browsing-tool requests could not read the authorized endpoints: T576 returned a tool-level unsupported `application/octet-stream` error; T611 was inaccessible through that tool. A bounded direct GET to each same URL succeeded. These were transport fallbacks, not new paper sources or retries of the first-pass URLs.

- **T576:** [PMLR-linked PDF](https://raw.githubusercontent.com/mlresearch/v235/main/assets/laszkiewicz24a/laszkiewicz24a.pdf) returned HTTP 200, 4,232,171 bytes, 36 PDF pages. The server's octet-stream response has a valid PDF signature and parses completely. SHA-256: `449bb229bee4b6f1cfe225f76e1a01854c1e57498f41bab2793a438f111a785d`. Authority is the saved official PMLR volume listing linking this publisher-owned mlresearch PDF.
- **T611:** [original official BMVA record](https://www.bmva.org/bmvc/2021/conference/papers/paper_0197.html) returned HTTP 200 with an explicit JavaScript redirect to the [same-paper BMVA archive record](https://www.bmva-archive.org.uk/bmvc/2021/conference/papers/paper_0197.html). That identity-matched record directly linked the [paper PDF](https://www.bmva-archive.org.uk/bmvc/2021/assets/papers/0197.pdf), which returned HTTP 200, 3,724,588 bytes, 13 PDF pages. SHA-256: `3ece0cc9c4818a21ae62726b1783548fd109af10f26615f55da2be237227dc7e`. The exact same-work archive path came from the official record; no unrelated redirect or mirror was followed.

There were six endpoint requests in total, including the two initial tool failures and the T611 record-to-archive-to-PDF chain. No automatic retry or HTTP redirect following was enabled in direct requests. No original failed URL, alternate arXiv version, supplement, unrelated paper, code repository or broad search was requested. T576's embedded appendices belong to its single PDF; T611's separately linked supplement was not retrieved. Temporary source copies and extraction/rendering files remain under `/tmp`; only this report and the manifest are new repository files.

## T576 — Single-Model Attribution of Generative Models Through Final-Layer Inversion

**Canonical identity:** `curated:62b0a9ae8be24d9f02e0`; canonical arXiv association `2306.06210`. The PDF's exact title and ordered authors — Mike Laszkiewicz, Jonas Ricker, Johannes Lederer, Asja Fischer — match the canonical record and the existing official PMLR listing. Rendered page 1 identifies ICML 2024/PMLR 235. The canonical year remains 2023; the source version/date distinction is recorded without metadata remediation. No arXiv version was fetched.

**First pass:** `ACCESS_BLOCKED_HTTP_403` at `https://openreview.net/pdf?id=Hs9GcILuZN`. **Second pass:** `COMPLETE_PRIMARY_PAPER_RETRIEVED_IDENTITY_MATCHED`. Retrieval success and the following scientific finding are separate determinations.

- **Claimed task and decisions:** Sections 2 and 4.1 (pages 2–3) formulate target-generator membership, G versus not-G, using an anomaly score. Section 2 also explicitly places fake/real discrimination within that framework. The experiments separately compare G with another generator or real images; this is not an N+1 source-classification result.
- **Real-image role:** Section 5.1 (page 6) uses real negative training examples where available. Crucially, real images are also independently scored test comparators: Table 8 (page 34) has separate Real columns for CelebA and LSUN, and Table 4 (page 8) has a real FFHQ comparator for StyleGAN2.
- **Authenticity-specific evidence:** Table 8 gives FLIPAD/DCGAN real-comparator accuracy of **99.72% on CelebA and 99.69% on LSUN**. Section G.2 (page 24) specifies 1,000 test examples per source; the table averages five runs. Section G.1 specifies target-model validation for threshold selection. Table 4 independently reports **99.93% DCTPAD accuracy for StyleGAN2 versus real**; FLIPAD was not used in that style-based setting. These are generator-specific binary real/generated comparisons, not a claim that any unknown generated image can be distinguished from real images by a universal detector.
- **Attribution-only evaluations:** Other cells/experiments compare target and competing generators, model seeds, perturbations and diffusion versions. Those comparisons do not themselves support detection. Likewise, real training negatives and the term anomaly would be insufficient without the explicit real-comparator tests.

**Evidence classification: `DETECTION_TASK_SUPPORTED`.** Final resolution: `EVIDENCE_RESOLVED_NO_CHANGE`; remediation: `NOT_REQUIRED` (`REMEDIATION_NOT_REQUIRED`). Retain **`detection;source_attribution`**. The T1 judgment rests on separately quantified binary authenticity comparisons across models/datasets, beyond mere inclusion of real images. The paper's primary framing remains single-model attribution. Confidence is **high** in identity and quantitative evidence, **moderate** in the policy interpretation that these systematic generator-specific tests constitute a substantive detection component. No authoritative change is applied.

Maintainer-accepted limitation: **Detection evidence is generator-specific real-versus-generated discrimination, not a demonstrated universal synthetic-image detector.**

## T611 — Does a GAN Leave Distinct Model-Specific Fingerprints?

**Canonical identity:** `curated:07ee620b8169b67b900f`; DOI `10.5244/c.35.53`. The official archive record gives the matching DOI, title and authors. Rendered PDF page 1 confirms Yuzhen Ding, Nupur Thakur and Baoxin Li, the title after capitalization/line-break/ligature normalization, and the 2021 work. The PDF was obtained from that exact record's Paper link.

**First pass:** `UNSAFE_REDIRECT_TO_UNRELATED_DOMAIN_NONRETRYABLE` at `https://www.bmvc2021-virtualconference.com/assets/papers/0197.pdf`. That obsolete virtual-conference URL was not retried. **Second pass:** `COMPLETE_PRIMARY_PAPER_RETRIEVED_IDENTITY_MATCHED` through the official archive.

- **Claimed task and decisions:** Section 3 (page 3) defines fingerprint representations for groups of GAN-generated images. Sections 5.1–5.2 compare GAN architectures and initialization seeds, including previously unseen GANs/seeds. The reported decision space is source/fingerprint association, not an authentic-versus-generated classifier.
- **Real-image role:** Section 4 (pages 5–6) uses real CelebA images as bases for simulated added fingerprints. Section 5 (pages 7–10) uses CelebA/LSUN-based GAN datasets. Real-image bases/training data do not establish an evaluated authenticity class.
- **Authenticity-specific evaluation:** None is reported in the complete main paper. Introductory discussion of binary fake detection is motivation/related work; the paper's own formal task and results do not supply an authenticity decision rule, real-image class or real/generated metric.
- **Attribution-specific evaluation:** Tables 1–2 (pages 8–9) measure Jensen–Shannon divergence and correlation between GAN fingerprints across architectures and seeds; Table 3 (page 10) tests transformed generated images. These measures support source association and fingerprint analysis, not detection. The paper points to separate supplemental experiments, which were not retrieved; their contents are not assumed.

**Evidence classification: `ATTRIBUTION_ONLY_NO_DETECTION`.** Final resolution: `EVIDENCE_RESOLVED_CHANGE`; remediation: `APPLIED` (`REMEDIATION_APPLIED`). The authoritative taxonomy and existing compatibility task field now contain **`source_attribution`**, removing only `detection`. Confidence is **high within the complete main-paper scope**. The maintainer accepted this correction. Every non-task attribute and research-type assignment is preserved. No claim is made about unseen supplemental material.

## Resolution accounting

| Evidence status | Before | After accepted adjudication |
| --- | ---: | ---: |
| Task evidence debts | 7 | 5 |
| Institution evidence debts | 1 | 1 |
| Research-type evidence debts | 11 | 11 |
| External unresolved | 19 | 17 |
| Separate T527 maintainer judgment | 1 | 1 |
| Total unresolved | 20 | 18 |

**2 resolved; 0 still insufficient in Wave 5A:** T576 resolves without change; T611 resolves with the approved task correction applied. The ledger is derived from the unchanged Phase 1 residual inventory and finalized wave outcomes; historical first-pass evidence remains intact. T527 remains `SCOPE_OR_TASK_EVIDENCE_REQUIRED` with its current task assignment intact. The 15/15 research-type first-pass baseline is unchanged; none of those cases was re-reviewed.

Remaining external IDs: T236, T137, T141, T572, T503; U010; R117, R176, R376, R455, R460, R535, R537, R548, R549, R580, R615.

## Authoritative and export effect

The T611 record alone changes in `data/curated/paper_taxonomy.csv`: tasks, task-review reason, evidence tier/source/excerpt, and audit date. Its compatibility `tasks` field alone changes in `data/curated/papers.csv`. Each update replaces only the target physical CSV record; all other bytes, including the 16 embedded CRLF sequences in each CSV, are preserved. T576's complete authoritative rows remain unchanged.

Public outputs and companion reports are regenerated by the established offline refresh using existing local inputs. No generated JSON is edited by hand. The scientific semantic diff is limited to T611's task assignment and task-review provenance; dependent export summaries, timestamp and audit fingerprints are checked separately.

| Corpus measure | Before | After |
| --- | ---: | ---: |
| Public | 639 | 639 |
| Formal | 531 | 531 |
| Mapped | 617 | 617 |
| Relationship rows | 1,421 | 1,421 |
| Unique pairs | 1,421 | 1,421 |

| Taxonomy label | Before | After |
| --- | ---: | ---: |
| detection | 590 | 589 |
| source_attribution | 85 | 85 |
| localization | 42 | 42 |
| method | 547 | 547 |
| dataset | 132 | 132 |
| benchmark | 88 | 88 |
| survey | 20 | 20 |
| analysis_study | 78 | 78 |

## Validation and integrity

The published frontend snapshot repair `2a8c485235a73ee8307be6d8693d8885610d9473` was fast-forwarded into the primary checkout before final Wave 5A validation. Its sole file is `tests/public_refinement_snapshot.py`. The 13 pre-existing tracked Wave 5A edits, three untracked Wave 5A files and 128 excluded local files survived that fast-forward byte-for-byte. The frontend repair is an ancestor of the scoped Wave 5A commit, not part of its diff.

Validation in the corrected environment:

- Historical snapshot checks: **4 passed, 0 failed**. The immutable 2026-10-01 snapshot and approved successor commits remain independently checked.
- Frontend tests with bundled Node v24.19.0: **323 passed, 36 subtests passed, 0 failed**.
- Wave 5A focused and current-count checks: **77 passed, 0 failed**.
- Authorized localhost smoke check: **1 passed, 27 subtests passed**. The earlier recovery had already passed all 42 previously blocked localhost tests and their 42 subtests, plus all 13 previously blocked Node tests.
- Complete repository suite, run once after preflight: **1,680 passed, 389 subtests passed, 0 failed, 0 skipped, 2 existing warnings**. The warnings are `PytestReturnNotNoneWarning` in the two legacy scope-exclusion tests and were not suppressed. The earlier 66-failure run preceded the corrected environment and separate frontend repair.
- Validators: **0 errors**. Curated database: 252 warnings; public map: 0 warnings; public bibliography: 23 warnings; exclusion registry: 2 warnings. Key-paper coverage `--check` passed. Existing warnings were not suppressed.

All 104 offline export inputs and 14 historical fixtures were present and checksum-identical; no new scientific source or dependency was downloaded. The first offline export passed. The second identical refresh changed **none of 4,408 tracked or visible untracked paths**, including all seven generated outputs checked by the refresh:

```text
EXPORT_REPRODUCIBLE = 1
```

The authoritative scientific diff changes only T611's `tasks` assignment and task-evidence provenance. Its compatibility `tasks` field matches; T576 and all other curated records remain unchanged. The two edited CSVs retain all 16 embedded CRLF sequences and every unrelated physical line. Each public export changes only T611's record; public inclusion, relationships and research-type labels remain unchanged. Corpus and taxonomy totals are shown above and reconciled with the unchanged Phase 1 residual inventory plus finalized wave outcomes.

The final allowlist and checksum audit confirms:

```text
UNEXPECTED_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0
```

All 128 excluded local files and 49 frozen NeurIPS files remain byte-identical. No unrelated frontend production file or Batch B case was changed. No Wave 5B work was started.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
