# Batch B Wave B1B — adjudication and validation

Artifact key: **2026-10-15** (requested filenames). Review completed: **2026-10-16, Asia/Shanghai**.

**Maintainer accepted exactly three corrections and two no-change resolutions.** The approved changes are applied locally and all five bounded review questions are closed through existing terminal review decisions. Focused/full-suite validation, current validators, independent semantic review and two-pass reproducibility are complete. Publication remains the final Git protocol below.

Pre-adjudication published baseline and fetched `origin/main`: `1ea93c53a3d9f5f822ce27f818d8009274d3b12a` (`fix: exclude out-of-scope batch-b wave b1a papers`); ahead/behind **0/0**. The existing isolated worktree is `/Users/meilinger/.codex/worktrees/batch-c-wave5c-evidence/synthetic-image-research-map`. The primary checkout is preserved.

## Exact review coverage

| Review | Canonical paper identity | Original category and question |
| --- | --- | --- |
| R137 | `curated:246f07c81b9f91e527eb` — IncreFA: Breaking the Static Wall of Generative Model Attribution | research_types. Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: IABench is a new incremental attribution benchmark spanning 28 generators. |
| R611 | `curated:07ee620b8169b67b900f` — Does a GAN Leave Distinct Model-Specific Fingerprints? | research_types. Verify the primary paper contribution/evaluation section before applying the proposed labels. Specific question: The paper seeks to establish the origin and properties of model-specific GAN fingerprints. |
| L013 | `curated:9d04c60c5b0b70859a63` — PatchCraft: Exploring Texture Patch for Efficient AI-Generated Image Detection | AUTHOR_STRING_MISMATCH. Verify paper-time byline and affiliation markers for the listed author strings; distinguish name order/abbreviation or version differences from unsupported authors. No automatic name merge. |
| P139 | `doi:10.1016/j.fsisyn.2026.100704` — Interpol Review of Detection of AI-Generated Image and Video Deepfakes, 2022-2025 | publication_metadata. Journal abbreviation has not been verified; confirm its established short name from the publisher or a bibliographic authority, or explicitly document that the full name is the standard short form. |
| P153 | `doi:10.1016/j.cosrev.2026.100908` — Methods and trends in detecting AI-generated images: A comprehensive review | publication_metadata. Journal abbreviation has not been verified; confirm its established short name from the publisher or a bibliographic authority, or explicitly document that the full name is the standard short form. |

All five are currently public and mapped. R137 and R611 overlap closed Batch C task reviews T137/T611, which did not settle these independent research-type questions. R611 currently has only `source_attribution`; the historical Batch B ledger still records its earlier detection label. Task taxonomy remains unchanged. There are no additional Batch B actions on these five canonical papers. Historical screens or other dimensions are not reopened.

## Locked policies and evidence limits

- **R1:** Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.
- **R2:** Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.
- **R3:** Assign analysis_study only when systematic empirical or theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps, or supporting interpretability figures do not qualify by themselves.
- **R4:** Assign method only when the paper contributes substantive technical novelty: a method, algorithm, model, procedure, or system. Pure surveys, benchmarks, datasets, or analysis studies do not gain method merely because they implement baselines. Multiple legitimate research-type roles remain allowed.
- **V1:** Keep the canonical archival venue identity conceptually distinct from source container/event information and paper track. Do not encode track as a different canonical venue. Use only fields supported by the current schema and do not invent metadata when event/container evidence is absent.
- **P1:** Multiple raw/source provenance records may support the same canonical paper–institution relation. Preserve those provenance records, but expose one normalized public paper–institution relationship when the canonical paper and institution pair are identical.

The existing publication normalization rule states that abbreviations come from official publisher usage or bibliographic authorities, never initials, and that a verified full-name short form needs no redundant acronym. V3 remains specific to IEEE MultiMedia. No new policy is introduced.

Research-type decisions reuse the committed Wave 5A/5B identity-matched primary-paper extractions. The original temporary PDF/HTML payloads are not available for fresh full-text or byte verification; this is disclosed, not silently upgraded to a new manuscript review. Source URLs below are provenance locators and were not requested in B1B.

## R137 — IncreFA

- **Canonical identity:** `curated:246f07c81b9f91e527eb`; arXiv `2604.17736`; canonical CVPR 2026 record has five authors.
- **Before → accepted and applied:** `method;dataset` → `method;dataset;benchmark`. Tasks remain `detection;source_attribution`.
- **Primary extraction:** Wave 5B T137, §3.1/Fig. 2, §5.1 EP1/EP2, Tables 1–2. IABench specifies real, known-generator and withheld unseen-generator decision spaces, incremental schedules, static attribution and separate authenticity metrics. This is a reusable evaluation framework under R2, rather than a generator count or large experimental table alone.
- **Existing labels:** retain method for the incremental attribution framework and dataset for the explicitly contributed IABench resource. Distribution/license and architecture derivations are not freshly verified. No analysis-study addition is proposed.
- **Quantitative context preserved:** EP1 attribution 78.80%, unseen-generator 98.93%; EP2 attribution 95.93%, unseen-generator 98.78%, authenticity 99.97%, real-class 99.66%. These are distinct metrics, not interchangeable task evidence.
- **Disposition:** `PROPOSE_CORRECTION_ACCEPTED`; `benchmark` added under the maintainer-approved remediation. High confidence within the preserved arXiv v2 protocol evidence.
- **Limit:** v2 (2026-04-21) has six authors, including Yuexuan Tan between Yueying Gao and Lei Chen; the canonical CVPR record has five. Same-work identity was established in Wave 5B; CVF-final equivalence and authorship reconciliation remain unverified. No HTML payload hash was preserved, so committed extraction hashes are the verification boundary.

## R611 — Does a GAN Leave Distinct Model-Specific Fingerprints?

- **Canonical identity:** `curated:07ee620b8169b67b900f`; DOI `10.5244/c.35.53`; Yuzhen Ding, Nupur Thakur, Baoxin Li; BMVC 2021.
- **Before → accepted and applied:** `method` → `method;analysis_study`. Current sole task `source_attribution` remains unchanged.
- **Primary extraction:** Wave 5A T611, main-paper §3 (PDF p.3), §4 simulation (pp.5–6), §§5.1–5.2/Tables 1–3 (pp.7–10). Controlled fingerprint simulation plus architecture, initialization-seed, dataset and transformation investigations address fingerprint distinctness and origins as the central scientific question.
- **R3/R4 finding:** this primary investigation independently supports analysis_study alongside the substantive fingerprint-extraction model. The proposal is grounded in the central contribution and controlled multi-factor investigation, not routine ablations or a robustness table alone. No dataset/benchmark label is proposed from the experimental inputs or comparison tables.
- **Disposition:** `PROPOSE_CORRECTION_ACCEPTED`; `analysis_study` added under the maintainer-approved remediation. High confidence within the complete-main-paper extraction.
- **Limit:** original 13-page BMVC PDF historical SHA256 `3ece0cc9c4818a21ae62726b1783548fd109af10f26615f55da2be237227dc7e` is a preserved retrieval receipt, not newly reverified manuscript bytes. The separately linked supplement remains unseen.

## L013 — PatchCraft author string

- **Canonical identity:** `curated:9d04c60c5b0b70859a63`; arXiv `2311.12397`; DOI `10.48550/arxiv.2311.12397`.
- **Evidence-only baseline state:** canonical ordered authors are Nan Zhong; Yiran Xu; Sheng Li; Zhenxing Qian; Xinpeng Zhang. Existing Fudan relationship `openalex-candidate-09d45f2a778956e5` (`institution:baa1df7c4adddbda`) retains `Li, Sheng` in its third institution-author slot. Fudan has no parent-institution assignment in this registry row.
- **Evidence:** two retained arXiv Atom responses identify v3 and the same five-author order, with Sheng Li third. They are two captures of the same authority, not independent authorities. The September 1 primary-source audit explicitly documents the identity-preserving Li, Sheng → Sheng Li correction.
- **Disposition:** `PROPOSE_CORRECTION_ACCEPTED`; high confidence for this paper-local name-order correction only. Applied one reviewed `institution_author_overrides.csv` row matched to exact title, year 2023 and Fudan University; use `Nan Zhong; Yiran Xu; Sheng Li; Zhenxing Qian; Xinpeng Zhang`. One matching override row is now appended; pre-existing roster rows are byte-preserved.
- **Preserve:** the five existing memberships, order, paper/institution/relationship IDs and raw/enrichment provenance. Canonical bibliography is already correct. No new relationship, person merge, institution merge, hierarchy or coordinate change is proposed.
- **Affiliation limit:** no complete primary author–affiliation block is retained in the inspected packet. The historical manual receipt has five individual rows and records the reviewer’s explicit all-author Fudan finding; it is preserved as a prior finding, not freshly certified. Cached arXiv entries have no affiliation elements and OpenAlex’s third person ID/ORCID are null. Any new or re-adjudicated affiliation claim requires the complete identity-matched primary block. This bounded string correction does not supply that missing evidence.

## P139 and P153 — deposited full-name short forms

| Review | DOI / canonical journal | Existing → proposed venue/acronym | Disposition |
| --- | --- | --- | --- |
| P139 | `10.1016/j.fsisyn.2026.100704` / Forensic Science International: Synergy | Preserve full canonical name and empty optional acronym | `SUPPORTED_NO_CHANGE` |
| P153 | `10.1016/j.cosrev.2026.100908` / Computer Science Review | Preserve full canonical name and empty optional acronym | `SUPPORTED_NO_CHANGE` |

Both saved Elsevier publisher deposits match exact DOI, normalized title and ordered authors. In each, `response.message.short-container-title[0]` equals `container-title[0]` and the full current journal name. Under the existing normalization rule, this supports the deposited full-name display without inventing a redundant optional acronym. Confidence is high for this exact bounded question. Neither outcome certifies a universal journal abbreviation, publisher-final text, scientific methods or complete publication history.

| Date/status observation | P139 | P153 |
| --- | --- | --- |
| Current year / type | 2026 / journal | 2026 / journal |
| Current public date | 2026-06-14 | 2026-01-21 |
| Deposited print/issue month | December 2026 | May 2026 |
| Explicit published-online / acceptance date | Absent / absent | Absent / absent |

The current public dates coincide with DOI-record `created` dates. DOI creation/deposit is not proof of online publication or acceptance. P139’s December issue is future relative to this October review; its version-of-record license start (2026-05-29) is also not a certified publication date. Preserve current dates and formal status without certifying those semantics or proposing a new date action. For P153, arXiv 2502.15176 remains preprint provenance, not the basis for the journal year or proof of version equivalence. Exact publication history would require an official publisher date/history record; no retrieval is authorized here.

Both bounded no-data-change outcomes are accepted and recorded through `publication_venues` / `no_action_after_review` with current venue-state fingerprints. The generated review diagnostics clear; journal names, empty acronyms and all publication-history fields remain unchanged. These decisions do not certify precise publication dates or any broader unresolved question.

## Final adjudications and preserved limitations

| Review | Final disposition | Applied data correction | Persisted decision |
| --- | --- | --- | --- |
| R137 | `PROPOSE_CORRECTION_ACCEPTED` | Applied | `review:f96c8d6c86921d78709b` |
| R611 | `PROPOSE_CORRECTION_ACCEPTED` | Applied | `review:36a56e9be2b3df6b3008` |
| L013 | `PROPOSE_CORRECTION_ACCEPTED` | Applied | `review:d95ce6927b2e190e8f4b` |
| P139 | `SUPPORTED_NO_CHANGE` | Not required | `review:60280bb5fd3f6d14a510` |
| P153 | `SUPPORTED_NO_CHANGE` | Not required | `review:8e7c592bf5b3920ed952` |

All five decisions use the existing `no_action_after_review` action. For R137, R611 and L013, this records that the approved correction is already applied and no further action remains for that exact question. P139/P153 use the existing publication-venue confirmation mechanism. No new review status or schema was introduced. The manifest binds each persisted decision to its exact historical review ID, canonical identity and original question.

R137's five/six-author discrepancy and inaccessible CVF-final equivalence remain unresolved. R611 relies on the preserved main-paper extraction; original PDF bytes are unavailable and the supplement remains unseen. L013 retains the same third person, all five ordered Fudan memberships and the same relationship ID. This source has no global third-author identifier; its absence is preserved rather than creating an identity. Its complete primary affiliation block remains unavailable. Neither publication no-change decision certifies universal abbreviations, acceptance/online-publication dates or publisher-final text.

## Batch B accounting

| Measure | Count |
| --- | ---: |
| Historical intake actions / unique papers | 159 / 148 |
| Historical review records retained | 159 |
| Active-public applicable actions / papers before B1B | 157 / 146 |
| B1B bounded questions resolved | 5 |
| Authoritative corrections applied / no-change resolutions | 3 / 2 |
| Remaining active-public unresolved actions / distinct papers | 152 / 141 |
| Historical unresolved actions including inactive L015/P562 | 154 |
| Original multi-action papers retaining independent questions | 11 |

The remaining active-public actions are U20, T9, R41, L23 and P59. Counts are recomputed by joining each exact original Batch B review ID and canonical identity to its persisted terminal decision and verified applied state or venue-state fingerprint, then counting unresolved rows whose identities remain public. All five selected papers were checked for independent Batch B actions; none has another one. All 159 original records and their historical status vocabulary remain byte-identical. L015/P562 exclusions remain applied, and their original affiliation/year questions remain historically unresolved rather than scientifically closed. Batch C's 13 deferred external debts remain untouched.

## Recomputed corpus and semantic public-data delta

| Measure | Before | After |
| --- | ---: | ---: |
| Public | 636 | 636 |
| Formal | 528 | 528 |
| Mapped | 614 | 614 |
| Unmapped | 22 | 22 |
| Relationships | 1,413 | 1,413 |
| Unique pairs | 1,413 | 1,413 |
| Detection | 586 | 586 |
| Source attribution | 84 | 84 |
| Localization | 43 | 43 |
| Method | 545 | 545 |
| Dataset | 132 | 132 |
| Benchmark | 88 | 89 |
| Survey | 20 | 20 |
| Analysis study | 77 | 78 |

No public paper or paper–institution pair is added or removed. The generated payloads retain the exact original record identities, ordering and relationship membership. Exactly five paper records and seven relationship rows change:

- R137: one paper and two relationships gain `benchmark` and the supporting taxonomy-review explanation.
- R611: one paper and one relationship gain `analysis_study` and its supporting explanation; sole task remains `source_attribution`.
- L013: one paper and one Fudan relationship normalize only the third institution-author string `Li, Sheng` to `Sheng Li`; existing override precedence changes derived mapping-source diagnostics to `curated_admin` and appends the override provenance note. Ordered person identities, identifiers (including existing missingness), affiliation memberships, coordinates and relationship ID are unchanged.
- P139: one paper and two relationships clear only the bounded venue-review diagnostics; all bibliographic and publication-history fields remain unchanged.
- P153: one paper and one relationship clear only those same bounded diagnostics; all bibliographic and publication-history fields remain unchanged.

The only top-level public-payload metadata change is the deterministic generated-at timestamp. The complete field-level diff and unchanged-core checksums are retained in the manifest. Two existing curated `papers.csv` research-type compatibility values are synchronized with the two authoritative taxonomy corrections; no other bibliographic field changes.

## Validation, integrity and publication gates

Focused regression checks: **197 passed, 12 subtests passed**, zero failures/errors/skips; `197 passed, 12 subtests passed in 89.68s (0:01:29)`.

Packet reconciliation: **5 checks passed**, zero failures/errors/skips, verified by JUnit and the successful command exit.

Complete suite: **1,775 passed, 389 subtests passed**, zero failures/errors/skips and **2 existing warnings**; `1775 passed, 2 warnings, 389 subtests passed in 336.04s (0:05:36)`.

All four current validators exited zero with **0 errors**. Their reported warnings are retained separately from pytest warnings: curated=254; public=0+23; exclusions=2; coverage=no warning summary emitted.

Independent semantic audit: **PASS**; exactly **five paper records and seven relationship rows** changed within the approved field limits; all 13 Batch C debts and unchanged core registries remain preserved.

**Two sequential offline export passes passed**. pass 1: exit 0, 72.830s, 4,423 paths byte-identical; pass 2: exit 0, 69.191s, 4,423 paths byte-identical. All seven generated outputs and all 119 operational/historical inputs retained exact hashes in both passes.

`FULL_SUITE_FAILURES = 0`

`EXPORT_REPRODUCIBLE = 1`

Initial focused validation reported seven failures confined to the new regression draft's assumptions about DOI-backed candidate identities and optional location fields. Those test assumptions were corrected without scientific or production changes. The initial public validator also caught a stale key-paper audit input fingerprint after the approved compatibility-column synchronization; regenerating that derived audit report restored synchronization. The final focused checks, current validators and full suite passed afterward.

Final prepublication preservation snapshot: **24 checks passed, 0 failed**. `UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

`IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`

Publication state: **VALIDATED_READY_FOR_PUBLICATION**. This is a validated precommit snapshot. The actual commit SHA, normal push result and fetched remote-SHA equality are verified and reported outside the immutable commit; this packet does not claim a publication event.

The earlier evidence-only review passed 258 lightweight checks (244 evidence/provenance/count checks and 14 preservation checks) against 31 local sources. That result is archived as evidence-only validation and does not substitute for remediation validation. The original manifest and report are embedded as deterministic gzip/base64 payloads with exact original SHA256 hashes; decoding and decompression reproduce every original byte, including the original 31-source hashes and scientific/quantitative findings.

Focused regression checks, current-scope validators, the complete zero-failure suite and two-pass offline export verification passed before staging. The verified preservation snapshot confirms `UNEXPECTED_CHANGED = 0`, `FROZEN_NEURIPS_CHANGED = 0`, `PREEXISTING_LOCAL_FILES_CHANGED = 0` and `IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0`. No current `AUTHORITATIVE_CORPUS_CHANGED = 0` claim is made: exactly the approved three corrections have been applied.

The primary checkout, its 130 pre-existing untracked files (including 128 protected files: 115 redundant raw captures, 10 generated/diagnostic files and three transient responses), all 49 frozen NeurIPS artifacts, ignored operational/historical inputs and Batch C's 13 deferred debts are preserved in the verified snapshot and remain requirements through publication. No new manuscript, source or scientific network retrieval occurs. No new review wave is started. Commit/push status must be reported only after actual Git and remote-SHA verification.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Evidence-only baseline local source inventory

The hashes below describe the exact pre-remediation evidence-only baseline. Current source hashes and the six approved changed-source hashes are recorded separately in the manifest. Canonical identity, original review records, evidence extraction text, quantitative findings and limitations are preserved verbatim under the manifest's `evidence_only_review` records and recoverable original-artifact archives.


Every source hash and its committed-or-local preservation basis is recorded in the manifest. Detailed JSON/XML/section/table locators and original retrieval/version limits are preserved per case.

| Source | Repository path | SHA256 |
| --- | --- | --- |
| S01 | [AGENTS.md](../AGENTS.md) | `20dbe722ae6a9a7b2c07d33d984f55b3ea74e3f03a6376ec8adc8510523a191f` |
| S02 | [data/curated/institution_author_overrides.csv](../data/curated/institution_author_overrides.csv) | `85bcc8eaa9738bdb29740a9eea31cd948b5693021511c9028a9f2365323febc5` |
| S03 | [data/curated/institutions.csv](../data/curated/institutions.csv) | `64c4a79abf95622d6440d3e151ac8732193d902d4fd98248ddbe4428b01a7326` |
| S04 | [data/curated/paper_exclusions.csv](../data/curated/paper_exclusions.csv) | `e113ff7fdf31e216e55c22053ec55417fdeba3e215a4cc9476de83ad4f5b95e3` |
| S05 | [data/curated/paper_taxonomy.csv](../data/curated/paper_taxonomy.csv) | `9bdef74c2be67e0c7ee5fc162bcf0514344ba476372ac7d24aa1ebb3e8c6563d` |
| S06 | [data/curated/papers.csv](../data/curated/papers.csv) | `2d71358418da758a1d257cb5b4bc170d373cff39d2be9d191d4b34f430978b88` |
| S07 | [data/curated/review_decisions.csv](../data/curated/review_decisions.csv) | `5120539686b0353decb6841ccdbce21ae18e648b4fb442925f4fff3f5c3c7e67` |
| S08 | [data/manual/key_paper_affiliation_enrichment.csv](../data/manual/key_paper_affiliation_enrichment.csv) | `4745a305c1c8b5ae0601119b50ea4038cd66fd562f0f9fd21ae214195a5992d5` |
| S09 | [data/processed/canonical_venues.json](../data/processed/canonical_venues.json) | `63f521785f743e356f7e2ad97c0a1e71e58ee261b9ed51760aecc32885b32009` |
| S10 | [data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json](../data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json) | `ee097956eafca891155380e95d13173070fca413aad371f0dc57bfcb86374f55` |
| S11 | [data/raw/corpus_quality_audit_2026_10_04/publication_metadata_review.json](../data/raw/corpus_quality_audit_2026_10_04/publication_metadata_review.json) | `b2ef27b7c70dd991f5ee29a794001bbd9f6ff6da2e9eff5cdb5d30c246d0726c` |
| S12 | [data/raw/corpus_quality_audit_2026_10_04/relationship_review.json](../data/raw/corpus_quality_audit_2026_10_04/relationship_review.json) | `509a34edaeaf4648aa1bdeddc598ec069a9a547dc4fe90c5e5fc8d4cc52122ed` |
| S13 | [data/raw/corpus_quality_audit_2026_10_04/taxonomy_review.json](../data/raw/corpus_quality_audit_2026_10_04/taxonomy_review.json) | `ad84e82b3dd82d0018d57caeed93353585ca4e83e3e2d800c00c0db656d637a1` |
| S14 | [data/raw/corpus_quality_audit_2026_10_04/unmapped_papers.json](../data/raw/corpus_quality_audit_2026_10_04/unmapped_papers.json) | `5e6c6dacd77959f674414bc94f9302afe96cb30ed23387d5b496b67eb7b63dbf` |
| S15 | [data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json](../data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json) | `39b8f7e4dc6643352d3858b36cfe5b53a8ad3f8b4fbf1b5761cdfe356cd32ecb` |
| S16 | [data/raw/corpus_quality_batch_c_wave5a_2026_10_08/evidence_manifest.json](../data/raw/corpus_quality_batch_c_wave5a_2026_10_08/evidence_manifest.json) | `1539b28d74528a405aae8720b72cbadf213e1cbe73c5c5e0f6c54a103b8bdf5e` |
| S17 | [data/raw/corpus_quality_batch_c_wave5b_2026_10_09/evidence_manifest.json](../data/raw/corpus_quality_batch_c_wave5b_2026_10_09/evidence_manifest.json) | `8a72ecfe455d58fdfb32f934d5a3abccd9e75715a61723582fdf8025d420c269` |
| S18 | [data/raw/openalex/20260619T211726Z_001_ai-generated-image-detection.json](../data/raw/openalex/20260619T211726Z_001_ai-generated-image-detection.json) | `8947d198999a1f066c344640747d472f2e99d722d0980a2570901f62430bbdbd` |
| S19 | [data/raw/venue_audit_crossref/21c4f23b3edc409a068c.json](../data/raw/venue_audit_crossref/21c4f23b3edc409a068c.json) | `3b05d517703ea6fcbb26b1a002f3c8df97ccb1fb7884ff3499ef07cd0e5a9df8` |
| S20 | [data/raw/venue_audit_crossref/8144a3dada70c0065d83.json](../data/raw/venue_audit_crossref/8144a3dada70c0065d83.json) | `f8bb37a81c74201c73febf2794881114bca56566a0e1eb849b4e9f7d00ff425c` |
| S21 | [data/raw/venue_audit_crossref/arxiv-full-048f53e8e62bbcb5.xml](../data/raw/venue_audit_crossref/arxiv-full-048f53e8e62bbcb5.xml) | `153484ddb11e3ea621ad92e801985c2b5e9adc34cd01092bfde46c88aa8fdf8e` |
| S22 | [data/raw/venue_audit_crossref/arxiv-full-f90a706b575cace5.xml](../data/raw/venue_audit_crossref/arxiv-full-f90a706b575cace5.xml) | `b521c5997fe8dcb0ed61a7e51f74e7932c7253b3dcea2351f37bf1fac28a350f` |
| S23 | [docs/corpus_quality_batch_b_intake_triage_2026_10_12.md](../docs/corpus_quality_batch_b_intake_triage_2026_10_12.md) | `a40d37dc3abd8198ea4d00384d19b25905a036519ee691718fac1d11a19e5459` |
| S24 | [docs/corpus_quality_batch_c_decision_sheet_2026_10_05.md](../docs/corpus_quality_batch_c_decision_sheet_2026_10_05.md) | `e5f329b7620e62bb041268059de60094d17284c3ae66b186abecd63a40d27d45` |
| S25 | [docs/corpus_quality_batch_c_wave5a_2026_10_08.md](../docs/corpus_quality_batch_c_wave5a_2026_10_08.md) | `78c558b7a402900929b53560538eafbf47325b47a25cfba85ecf55a3142e4d23` |
| S26 | [docs/corpus_quality_batch_c_wave5b_2026_10_09.md](../docs/corpus_quality_batch_c_wave5b_2026_10_09.md) | `45fa32f8eabd12ae72f272c5af85eb9abd4aea608be4dac799d8e88ac1308e94` |
| S27 | [docs/publication_venue_normalization.md](../docs/publication_venue_normalization.md) | `987d1d18ab5e7b11fea62f5a147c7fc32f79c7e2a7f75b0066c4075f4a0ec4af` |
| S28 | [docs/targeted_literature_coverage_audit_2026-09-01.md](../docs/targeted_literature_coverage_audit_2026-09-01.md) | `9a5595b23800d6a70f9e4172175533bf8bc7b3fc217ec03ba5a675327887877d` |
| S29 | [scripts/export_candidate_map_data.py](../scripts/export_candidate_map_data.py) | `ac7ecfb49845edfde91c89e8d693adec7378e84b830a8d21da29a22deb70d739` |
| S30 | [web/data/public_preview_map_data.json](../web/data/public_preview_map_data.json) | `c9faf509b7c6e646bdb8531af0b8d4b74f1255ec7ff371c64078e57331f4687b` |
| S31 | [web/data/public_preview_papers.json](../web/data/public_preview_papers.json) | `5dd92e10da0f312e842bc31fe42f9ed2da279a42a820316194b2e1b010462940` |
