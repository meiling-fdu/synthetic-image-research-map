# NeurIPS 2026 locked 7+1 metadata recheck — 2026-10-02

**Outcome: 7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA.** No migration, validator change, public export, new candidate, or NeurIPS commit was made.

**Frozen:** reopen the migration only when newly available authoritative NeurIPS 2026 metadata resolves the required conference-track fields. This hygiene task performs no metadata search, migration staging, partial application, or change to locked identities, taxonomy, or decisions.

## Website publication

`git push origin main` completed with `Everything up-to-date`. Both local main and the remote queried with `git ls-remote` equal `3c0a5fbc25d7434cf4c80de27aae16fc8761a921` (zero ahead/behind). The push included committed history only; no NeurIPS file was staged.

## Official metadata findings

The [official NeurIPS 2026 download](https://neurips.cc/Downloads/2026) successfully returned its poster JSON export after a timeout/retry. The export has five fields: `type`, `name`, `virtualsite_url`, `speakers/authors`, and `abstract`. Only the eight locked items were extracted from its 9,109 records. All eight canonical titles and poster IDs match the locked reconciliation. Presentation type `Poster` is not a conference track; no Main, Evaluations & Datasets, workshop, or other track is inferred.

All eight poster URLs return HTTP 403 with the explicit message that the 2026 virtual site is currently closed. The [proceedings index](https://proceedings.neurips.cc/) currently lists 2025 as its newest volume; the 2026 volume URL returns 404. Thus no authoritative conference-track assignment, conference DOI, or proceedings page could be verified. The arXiv DataCite identifiers in the machine-readable audit identify preprints and are not conference DOIs.

| Locked item | Identity / action | Official metadata and primary-paper check | Track |
| --- | --- | --- | --- |
| BIAS-ID: A Framework for Analyzing Transformation Biases in AI-Generated Image Detectors | `curated:07f4e313ba7a093fc94a`; MISSING_ADD | Official poster 139597; [arXiv 2605.31153v1](https://arxiv.org/abs/2605.31153). Author order matches the locked primary-paper metadata. | Unresolved; no published track field |
| MIRROR: Manifold Ideal Reference ReconstructOR for AI-Generated Image Detection | `curated:8fe7cb0db76df68a5e38`; EXISTING_UPDATE_NEEDED | Official poster 149292; [arXiv 2602.02222v1](https://arxiv.org/abs/2602.02222). CONFLICT: official export omits Jing Dong; arXiv v1 and existing authoritative record contain 15 authors. | Unresolved; no published track field |
| Post-hoc Selective Classification for Reliable Synthetic Image Detection | `curated:15bf88ecaf61cad7b226`; MISSING_ADD | Official poster 151954; [arXiv 2605.08574v1](https://arxiv.org/abs/2605.08574). Same author order; official export renders Jacob Seidman, while the primary paper and locked input render Jacob H. Seidman. Preserve both source renderings. | Unresolved; no published track field |
| FARE: Forensic Acceptance Region Estimation for Catching Bait-and-Switch Image Generators | `curated:62f8713f970aa4a95432`; MISSING_ADD | Official poster 151260; [arXiv 2609.30982v1](https://arxiv.org/abs/2609.30982). Author order matches the locked primary-paper metadata. | Unresolved; no published track field |
| Beyond Real or Fake: A Dual-Channel Authenticity and Reasoning Protocol for Photographic Assessment | `curated:712c58079f762c994ad5`; MISSING_ADD | Official poster 154533; [Google Research paper page](https://research.google/pubs/beyond-real-or-fake-a-dual-channel-authenticity-and-reasoning-protocol-for-photographic-assessment/). Same six-person order with display-name/capitalization differences: Xiaoxiao Li vs Xiaoxiao (Shaun) Li; PEI CAO vs Pei Cao. Google paper page verifies the locked rendering. | Unresolved; no published track field |
| SIGMA: Semantic-Difference Instruction-Grounding Mask Annotator for Text-Driven Image Manipulation Localization | `curated:2a62f662dfd346b3f5cb`; MISSING_ADD | Official poster 151764; [arXiv 2605.27924v1](https://arxiv.org/abs/2605.27924). Same nine-person order; official export capitalizes XIAOCHUN CAO. Primary-paper rendering retained. | Unresolved; no published track field |
| SALART-VQA: Diagnosing Whether VLMs Understand Salient Artifacts in Generated Images | `curated:baafdb8ac5488ceea198`; MISSING_ADD | Official poster 139139; [arXiv 2606.12671v1](https://arxiv.org/abs/2606.12671). Author order matches the locked primary-paper metadata. | Unresolved; no published track field |
| Can Pixels Alone Reveal Image Origin? Minimax Limits and Learnable Interfaces for Passive Provenance | `curated:36755a9ffdcb1829037c`; MISSING_ADD | Official poster 154460; [arXiv 2609.30997v1](https://arxiv.org/abs/2609.30997). Author order matches the locked primary-paper metadata. | Unresolved; no published track field |

All seven arXiv records still expose v1. The official MIRROR title omits “Generalizable,” while arXiv v1 retains it, as already captured by the locked update. SalArt-VQA differs only in acronym capitalization between the official and arXiv titles. Beyond Real or Fake has no arXiv ID established by these authoritative sources.

**Additional MIRROR discrepancy:** the new official export contains 14 authors; arXiv v1 and the authoritative database contain 15. Jing Dong appears in arXiv/current metadata and is absent from the conference export. The ordered lists and exact source values are preserved in the machine-readable audit. Do not remove that author or split the paper identity; await an authoritative resolution before changing the accepted author list.

Beyond Real or Fake has matching six-person author order with display-name/case variations. Its conference event-profile affiliations differ from the saved paper first page; those profiles do not replace paper-time evidence. The existing curated input remains untouched.

## SIGMA affiliation evidence

The [arXiv v1 PDF](https://arxiv.org/pdf/2605.27924v1) first page was downloaded, rendered, and visually checked against the HTML. It explicitly assigns the following superscripts; no email-domain or coauthor inference was used.

| Marker | Authors | Paper-time affiliation / exact existing institution IDs |
| --- | --- | --- |
| 1 | Peiyu Zhuang; Jianquan Yang; Zhuoying Cai; Xiaochun Cao | Shenzhen Campus of Sun Yat-sen University, China — `institution:9ab7959736f7be0d` |
| 2 | Haodong Li | Guangdong Provincial Key Laboratory of Intelligent Information Processing and Shenzhen Key Laboratory of Media Security, Shenzhen University, Shenzhen, China — `institution:ad9c8964d01f80d8` |
| 3 | Ruitao Xie | Shenzhen University of Advanced Technology and Shenzhen Institute of Advanced Technology, Chinese Academy of Sciences, China — `institution:498778a17add497f`; `institution:2251558d3f3716fa` |
| 4 | Jishen Zeng; Baoying Chen | Alibaba Group, China — `institution:73f449eb6a3c05d3` |
| 5 | Jiwu Huang | Shenzhen MSU-BIT University, China — `institution:11d4e5b507bbbada` |

This resolves the missing paper-time affiliation evidence: nine authors, ten associations, six already-existing institutions. Marker 3 preserves both affiliations. No institution merge, new location, or current mapping was created. The resolution is recorded separately; the old staged CSVs remain unchanged and still reproduce their old SIGMA coverage warning. Applying that resolution belongs to the complete migration after the official-track blocker is cleared.

## Complete untracked-file hygiene inventory — 2026-10-02

All 45 files present at hygiene-task start are classified below. Counts: **28 KEEP_VERSIONED_EVIDENCE, 11 KEEP_VERSIONED_AUDIT, 1 KEEP_VERSIONED_SCRIPT, 5 GENERATED_INTERMEDIATE, 0 LOCAL_RAW_EVIDENCE, 0 TEMPORARY, 0 UNKNOWN**. The structured recheck records each pre-cleanup SHA-256 and byte count. “KEEP_VERSIONED” describes suitability for a later reviewed commit; nothing is staged or committed by this task.

The repository already versions **31 raw external PDFs**, including `data/raw/primary_curation_2026_09_08/2311.00962.pdf` and `data/raw/primary_curation_2026_09_08/2503.11195.pdf`. SIGMA's PDF therefore follows established evidence practice and remains version-worthy alongside its extracted affiliation findings. Official source captures are dated evidence, not reproducible caches: a future response cannot reproduce the original bytes or establish what fields were available on the recheck date. Existing source manifests retain their hashes and retrieval provenance.

Minimal cleanup: retain every file in its existing location; add five anchored, exact `.git/info/exclude` entries for the staged CSV previews only. Those previews were already reproduced byte-for-byte in the metadata recheck and remain on disk. The locked payload, script, predecessor receipt, and prior validation evidence preserve how they were produced. No deletion or move is proposed or performed; future evidence or new filenames in the same directories are not hidden. Historical audit and evidence receipts are retained even when derived because they establish the reviewed state at that time. The tracked `.gitignore` remains byte-identical: an initial tracked-ignore edit correctly tripped a historical baseline assertion and was reverted. The same five exact paths are excluded locally, where these generated previews exist; source checkouts do not need that local housekeeping.

| Path | Classification | Reason |
| --- | --- | --- |
| `data/manual/neurips_2026_targeted_gap_fill_reconciliation.json` | `KEEP_VERSIONED_AUDIT` | Locked identities and reviewed decisions; authoritative input, not a cache. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/action_plan.json` | `KEEP_VERSIONED_AUDIT` | Frozen action plan and task-gated predictions; no application. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/curation_payload.json` | `KEEP_VERSIONED_AUDIT` | Reviewed curation input required by the locked script. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/evidence/manifest.json` | `KEEP_VERSIONED_AUDIT` | Original source paths and hashes; provenance receipt. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/evidence/neurips2026_benchmark_sources.json` | `KEEP_VERSIONED_EVIDENCE` | Original reviewed source or paper-page evidence; provenance retained by the evidence manifest. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/evidence/neurips2026_beyond_p1p2.txt` | `KEEP_VERSIONED_EVIDENCE` | Original reviewed source or paper-page evidence; provenance retained by the evidence manifest. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/evidence/neurips2026_beyond_page1.png` | `KEEP_VERSIONED_EVIDENCE` | Original reviewed source or paper-page evidence; provenance retained by the evidence manifest. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/evidence/neurips2026_detection_sources.json` | `KEEP_VERSIONED_EVIDENCE` | Original reviewed source or paper-page evidence; provenance retained by the evidence manifest. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/evidence/neurips2026_initial_local_matches.json` | `KEEP_VERSIONED_EVIDENCE` | As-of identity comparison evidence; retain historical results. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/evidence/neurips2026_scope_sources.json` | `KEEP_VERSIONED_EVIDENCE` | Original reviewed source or paper-page evidence; provenance retained by the evidence manifest. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/implementation_review.json` | `KEEP_VERSIONED_AUDIT` | Historical implementation and validation audit. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/metadata_recheck_2026_10_02.json` | `KEEP_VERSIONED_AUDIT` | Central structured recheck evidence and affiliation resolution. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/predecessor_623_snapshot.json` | `KEEP_VERSIONED_AUDIT` | Pre-migration identities and hashes required for reproducible comparison. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/staged/author_institution_mappings.csv` | `GENERATED_INTERMEDIATE` | Reproducible unapplied CSV preview; retained locally under an exact ignore rule. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/staged/institution_location_review.csv` | `GENERATED_INTERMEDIATE` | Reproducible unapplied CSV preview; retained locally under an exact ignore rule. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/staged/institutions.csv` | `GENERATED_INTERMEDIATE` | Reproducible unapplied CSV preview; retained locally under an exact ignore rule. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/staged/paper_taxonomy.csv` | `GENERATED_INTERMEDIATE` | Reproducible unapplied CSV preview; retained locally under an exact ignore rule. |
| `data/processed/neurips_2026_targeted_gap_fill_2026_10/staged/papers.csv` | `GENERATED_INTERMEDIATE` | Reproducible unapplied CSV preview; retained locally under an exact ignore rule. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/arxiv-2602.02222.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/arxiv-2605.08574.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/arxiv-2605.27924.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/arxiv-2605.31153.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/arxiv-2606.12671.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/arxiv-2609.30982.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/arxiv-2609.30997.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/beyond-google.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/downloads-2026-posters.json` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/downloads-2026.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/manifest.json` | `KEEP_VERSIONED_AUDIT` | Retrieval URLs, dates, statuses, hashes, and local paths. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/poster-139139.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/poster-139597.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/poster-149292.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/poster-151260.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/poster-151764.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/poster-151954.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/poster-154460.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/poster-154533.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/proceedings-2026.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/proceedings-index.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/sigma-2605.27924v1.pdf` | `KEEP_VERSIONED_EVIDENCE` | Primary-paper affiliation evidence; comparable external PDFs are already versioned in data/raw/. |
| `data/raw/neurips_2026_metadata_recheck_2026_10_02/sigma-full.html` | `KEEP_VERSIONED_EVIDENCE` | Dated primary-source response; bytes cannot be reconstructed from a changing live URL. |
| `docs/neurips_2026_implementation_review.md` | `KEEP_VERSIONED_AUDIT` | Earlier implementation audit, retained as historical provenance. |
| `docs/neurips_2026_metadata_recheck_2026-10-02.md` | `KEEP_VERSIONED_AUDIT` | Central human-readable blocked-migration and hygiene audit. |
| `docs/neurips_2026_targeted_gap_fill.md` | `KEEP_VERSIONED_AUDIT` | Original locked reconciliation and source decisions. |
| `scripts/curate_neurips_2026_targeted_gap_fill.py` | `KEEP_VERSIONED_SCRIPT` | Deterministic locked staging/apply script; remains frozen and unapplied. |

## Metadata-recheck validation (before hygiene cleanup)

The unchanged migration builder validates the exact seven additions and one existing MIRROR update. Identity checks against both current curated and public records found no new-paper duplicates and exactly the existing MIRROR identity. Exact DOI/arXiv/title/stable-ID checks use the established identity helper; locked method/acronym checks found only the existing MIRROR. No fuzzy merge or new candidate was needed.

All five staged CSVs were regenerated only in a temporary validation directory and compared byte-for-byte with the saved previews. The saved files were not overwritten. Their primary keys, references and deterministic output match. The unchanged full curated validator still rejects exactly eight conference rows for missing `venue_track`; there are no other staged validation errors or duplicate candidates. It reports 246 warnings, versus 245 on the authoritative database. No unsupported `Pending` category was introduced. Missing tracks remain explicit evidence gaps rather than an accepted schema state.

- Targeted conference-track, taxonomy, published-only and public-export regressions: **34 passed**.
- Current curated database: **0 errors, 245 warnings, 0 duplicate candidates** (validated on an identical temporary copy).
- Saved staged proposal: **8 expected blocking track errors, 246 warnings, 0 duplicate candidates**.
- Full existing suite: **1,536 passed, 2 failed, 2 warnings in 350.16 seconds**. The only failures are `tests/test_legacy_scope_exclusion_migration.py::test_ledger_report_and_validation_are_generated_from_locked_sources` and `tests/test_legacy_scope_exclusion_migration.py::test_changed_files_manifest_classifies_every_path_once`. Both independently reproduce against the pre-task archive; those tests and their validators are unchanged. No new test failure occurred.

## Actual counts (unchanged)

| Measure | Before | After |
| --- | ---: | ---: |
| public_papers | 623 | 623 |
| published_only | 514 | 514 |
| mapped_papers_in_paper_export | 602 | 602 |
| paper_institution_relationships | 1392 | 1392 |
| curated_papers | 479 | 479 |
| taxonomy_rows | 666 | 666 |

Current public task memberships: {"detection": 580, "localization": 36, "source_attribution": 79}. No taxonomy changed.

The hypothetical 630-paper total assumes all seven new curated records are public. The locked SalArt-VQA record intentionally has no forensic root task and is excluded by the existing public gate. The original plan therefore predicts 629, not 630. Neither count is an applied result; the actual count remains 623. MIRROR remains the same identity and contributes no additional paper.

## Metadata-recheck evidence and Git scope (before hygiene cleanup)

New files are confined to `data/raw/neurips_2026_metadata_recheck_2026_10_02/` (unaltered official/primary-source captures plus provenance manifest), `data/processed/neurips_2026_targeted_gap_fill_2026_10/metadata_recheck_2026_10_02.json` (derived audit and SIGMA resolution), and this document. Original reconciliation, input payload, script, staged previews, curated data, public exports, validators, and website files are unchanged. Temporary rendering and validation artifacts remain outside the repository.

Nothing was staged or committed for NeurIPS. No push occurred beyond the one explicitly authorized website-history push.


Preservation check at completion of the metadata recheck: **129/129 recheck-start protected hashes** and **105/105 website-audit data hashes** match. All 20 original untracked files are unchanged. There are 25 new evidence/audit files (22 raw source captures, one source manifest, one processed recheck, and this report), giving 45 untracked files total. There are no tracked modifications or staged files. `git diff --check` passes; main and origin/main remain identical at the website commit.

## Legacy manifest repair — 2026-10-02

Both original failures were reproduced before editing code: **2 failed in 5.53 seconds**. The defect is a historical receipt being regenerated from live working-tree status, not a scientific-data discrepancy or an omitted NeurIPS classification.

| Failing test | Exact mismatch and root cause | Correction and retained protection |
| --- | --- | --- |
| `test_ledger_report_and_validation_are_generated_from_locked_sources` | Ledger, report and validation assertions all pass. `check_current()` then compares the historical 59-entry receipt (28 tracked changes, 31 untracked files) with today's 45 untracked NeurIPS entries and reports stale/unclassified paths. With live status replaced by an empty clean-checkout result, it still reports a stale manifest. This is a generator input-lifetime bug. | Generate the historical classification from a separate hash-locked status input. Leave the original byte-for-byte ledger/report/validation/reproducibility/manifest assertions intact. Missing or altered output still fails. |
| `test_changed_files_manifest_classifies_every_path_once` | All 45 current NeurIPS paths are outside the completed legacy migration's groups. The original assertion also requires that migration's manifest itself to be present, which no longer holds after committing the migration. The input describes the wrong event. | Reclassify the archived 59 paths with the same A–F rules, counts and semantic boundaries. Preserve empty-unclassified and non-overlap assertions. Explicit live input still reports unknown/protected paths; it is never filtered into a passing historical receipt. |

The authoritative evidence is baseline commit `c160a7dd6b8b403ed6e268108ee2fe4ab6fb3311`. Its original generator, tests and `data/processed/legacy_scope_exclusion_migration_2026_09/changed_files_manifest.json` match the pre-cleanup files. All 59 archived paths exist in that commit. The archived manifest SHA-256 is `86fb27f3d915d84aacbc254f99ec2e8e84534272dfe90e66ac09e059345eb20f`.

The new `data/processed/legacy_scope_exclusion_migration_2026_09/changed_files_status_snapshot.json` contains only the original entries plus provenance (source commit, source path, source SHA-256, capture command, historical-scope note). Its SHA-256, `0ad484117f640414055f25c6b03837ae5de0803084bcea69c26f4447a7f3d0ab`, is pinned in `scripts/legacy_scope_exclusion_migration.py`. It is an input receipt, not a new working-tree snapshot. Existing groups and counts are computed again rather than trusted from the output manifest. The loader refuses any byte change to this input; duplicate status paths cannot silently collapse.

Two in-memory regeneration rounds reproduced the archived manifest exactly. Consequently no rewrite of the original manifest, ledger, report, validation summary or reproducibility receipt is needed. Neither the original failing tests nor historical hashes, source policy, scientific records or validators were updated. An explicit current inventory remains available through `build_changed_files_manifest(git_status_entries())`; historical `--check` and `--render` use the frozen input and can operate without Git metadata.

`tests/test_legacy_scope_changed_files_manifest.py` adds 13 regression cases: deterministic historical replay independent of clean/unrelated live status; removed/added/status-changed/provenance-changed input rejection; visible unknown and protected paths; duplicate-path rejection; overlapping-group detection; and missing/byte-changed/path-changed/group-changed output rejection through `check_current()`. The original two assertions remain unchanged.

The first broader run had **153 passed, 2 failed, 2 warnings**: the temporary tracked `.gitignore` edit was correctly rejected by an older baseline hash, and a localhost HTTP test was denied by the sandbox. The `.gitignore` edit was reverted byte-for-byte and its five exact paths moved to local `.git/info/exclude`. No historical test or snapshot was relaxed. The validation rerun uses the localhost-server permission required by the existing integration test.

## Final hygiene validation and Git audit — 2026-10-02

| Validation | Passed | Failed | Skipped | Warnings | Duration |
| --- | ---: | ---: | ---: | ---: | --- |
| Two original failures plus new focused regressions | 15 | 0 | 0 | 0 | 15.84 s |
| Related legacy-scope / manifest / ledger and historical-audit tests (11 files, listed in structured audit) | 155 | 0 | 0 | 2 | 208.45 s |
| Full suite, `python3 -m pytest -q --tb=short` | 1551 | 0 | 0 | 2 | 406.44 s |

The two existing `PytestReturnNotNoneWarning` messages concern the imported `test_successor_migration_payload` and `test_successor_migration_text` helpers. They are not hidden or suppressed. Python syntax compilation passes for the changed script and new test file. `git diff --check` passes; the new/extended input, tests, and audit artifacts also pass whitespace checking independently of the index.

Final corpus integrity is unchanged: **623 public papers, 1,392 paper–institution relationships, 514 formally published papers, 602 mapped papers, and 105/105 saved checksums**. All 22 source captures and six original durable-evidence checksums match. All 45 starting files remain present; 43 are byte-identical and only this central report and its structured recheck were extended with hygiene/repair results. No new literature search, migration staging/application, scientific-data edit, taxonomy change, export refresh, or conference-track validator change occurred.

Final scope:

- **Manifest fix:** tracked change to `scripts/legacy_scope_exclusion_migration.py`; new `data/processed/legacy_scope_exclusion_migration_2026_09/changed_files_status_snapshot.json`; new `tests/test_legacy_scope_changed_files_manifest.py`.
- **NeurIPS audit/evidence:** 40 version-worthy untracked files in their original locations, including the two extended audit files; no raw response or locked input was edited. Classification covers every one of the original 45 paths above.
- **Local generated intermediates:** the five unchanged staged CSVs are retained and exactly excluded through `.git/info/exclude`. The tracked `.gitignore` is unchanged. No broad pattern, deletion, relocation, local-only raw evidence, temporary file, or unknown file was introduced by cleanup.
- **Git:** one tracked modification, 42 visible untracked files (40 NeurIPS files plus two manifest-fix files), empty index, no commit, no push, no unrelated changes. HEAD and the local `origin/main` reference remain `3c0a5fbc25d7434cf4c80de27aae16fc8761a921`.

**7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA.** No migration was applied. The commit-readiness verdict below covers repository hygiene and the historical manifest fix, not permission to apply the NeurIPS proposal.

**FULL SUITE GREEN — COMMIT-READY**

## Commit preparation — 2026-10-02

The explicit commit allowlist contains the three manifest-fix files and the 40 version-worthy NeurIPS files listed above. The five generated previews remain excluded only through `.git/info/exclude`. No curated, public-export, website, or unrelated path is staged. The original historical 59-entry manifest and assertions remain unchanged; two regeneration rounds still reproduce the archived manifest byte-for-byte with the commit staged.

The full staged `git diff --cached --check` reports **6,332 source-whitespace findings in 19 downloaded HTML files**: 6,331 trailing-whitespace findings and one final blank line. This is a nonzero check result, newly visible when the raw captures are included in the diff. Every finding is confined to `data/raw/neurips_2026_metadata_recheck_2026_10_02/*.html`; all source-capture hashes still match their provenance manifest. The source bytes are intentionally preserved without normalization, whitespace-rule changes, or suppression. The same check passes for code, tests, audit documents, structured inputs, and derived evidence. Earlier hygiene whitespace checks covered tracked changes and the four new/extended input, test, and audit files; they did not validate all previously untracked raw captures.

Commit-time reruns: **15 focused tests passed in 11.90 seconds**; **155 related audit tests passed with 2 existing warnings in 157.70 seconds**; neither run failed or skipped a test. Syntax checks pass for the manifest generator, preserved NeurIPS helper, and regression file. No functional source or test changed since the verified 1,551-pass full suite, so that full run was not repeated. The only edits in this commit-preparation step extend the two existing audit files with these checks and the raw-source whitespace finding. Corpus counts remain 623 / 1,392 / 514 / 602 and all 105 saved checksums match. No migration was applied and no push is authorized.
