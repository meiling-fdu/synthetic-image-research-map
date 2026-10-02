# Public website refinement — 2026-10-01

The existing public frontend now presents **Synthetic Image Forensics Research Map** with the tagline **Detection · Source Attribution · Localization**. This is a presentation and discovery change; the corpus and its curation are frozen.

## Implemented

- Replaced the obsolete image wordmark in the public header with one visible semantic heading. The existing image file is preserved. Updated page titles, descriptions, canonical URLs, Open Graph and Twitter card metadata, including the repository-root redirect page.
- Narrowed the landing-page scope to synthetic-image forensics, with conditional generative-editing coverage and explicit adjacent-topic boundaries.
- Made Unique Papers the default. Explicit institution and paper views remain supported; shared URLs name the view. No paper-identity, CSV-column, map-interaction, or filtering-dimension rules changed.
- Labeled the existing marker palette, including Unknown and the shared purple for Localization / Mixed. Size text refers to unique papers in the current filtered view; the illustrative sizes do not claim numeric thresholds.
- Added a small Current view cue to the existing statistics and renamed the institution chart Top Mapped Institutions, with mapped-coverage and non-ranking explanations.
- Extended the existing cached search index with abstracts and exact normalized DOI/arXiv identifiers. Versioned arXiv URLs resolve to the base identifier. Full identifiers use delimited tokens so prefix-sharing identifiers do not match. Ordinary text retains the existing normalization and all-term filtering; institution resolution and autocomplete are preserved.
- Added transparent relevance: exact normalized title = 10000, exact identifier = 9000, title prefix = 8000; other queries average each distinct term’s strongest field weight (title 4000, author 1000, institution 500, venue 250, taxonomy 125, abstract 16, year 8). Repeated words and abstract length cannot increase a term’s contribution. Year, title, paper identity, and record identity break ties.
- Automatic sorting uses relevance for a keyword and newest year when cleared. Explicit user/URL sorts, including `year-desc`, remain explicit when copied and restored. Filter undo preserves whether sorting was automatic.
- Added plain-text Copy citation using public publication metadata, DOI first, canonical arXiv second, and an available safe paper URL last. Missing fields are omitted. Keyboard activation and accessible success/failure announcements reuse the existing clipboard path. Copy paper link and Report metadata issue remain available.
- Added the static Methodology page with ten requested sections, raw-documentation/data links, coverage caveats, and citation guidance. Added a minimal `CITATION.cff` with the authoritative maintainer and project URLs.

## Changed files

Public frontend: `index.html`, `web/index.html`, `web/style.css`, `web/app.js`, `web/paper_details_helpers.js`, `web/paper_link_helpers.js`, and new `web/paper_search_helpers.js`.

Public methodology and citation: new `web/methodology.html`, new `CITATION.cff`, and this verification report.

New tests: `tests/test_public_academic_refinement.py` and `tests/public_academic_refinement_browser.cjs`.

Updated existing frontend tests: `test_frontend_active_filter_chips.py`, `test_frontend_chart_filters.py`, `test_frontend_data_unit_semantics.py`, `test_frontend_filter_terminology.py`, `test_frontend_map_help.py`, `test_frontend_no_results_recovery.py`, `test_frontend_paper_issue_reporting.py`, `test_frontend_public_labels_layout.py`, `test_frontend_published_only_filter.py`, `test_frontend_result_cards.py`, `test_frontend_sort_dropdown.py`, `test_frontend_sticky_public_layout.py`, `test_frontend_url_state.py`, and `test_public_header_metadata.py`. These changes update intended presentation/state expectations and test fixtures. The later, separately requested historical snapshot reconciliation is documented below.

## Initial refinement verification

Runtime: `/usr/bin/python3` with the bundled Node executable on PATH. No runtime dependencies were added.

| Check | Result |
| --- | --- |
| All frontend tests, new academic-refinement tests, public-header tests | **323 passed** |
| Full repository suite, outside the socket-restricting sandbox | **1532 passed, 6 failed**, 2 existing pytest return-value warnings |
| New browser regression harness | Passed |
| Existing accessibility browser harness | Passed at 375, 430, 768, 1024, 1440 px |
| Existing feature-freeze browser harness | Passed |
| Methodology at all five widths | No horizontal overflow; navigation and ten sections verified |
| Citation | YAML parsed with Ruby Psych; supplied fields, required fields, types, author structure, patterns, enums, and URI formats checked against the official CFF 1.2.0 schema |
| Curated validator | 0 errors; 245 existing warnings |
| Public map validator | 0 errors; 0 warnings |
| Public paper validator | 0 errors; 22 existing warnings |
| JavaScript syntax, static local links, whitespace | Passed |

The first sandboxed full run had 42 additional localhost endpoint permission failures. All 42 passed in the unrestricted rerun; no timeout or assertion was weakened.

### Six failures before snapshot reconciliation

The following two failures reproduce on the pre-task snapshot (HEAD `c160a7dd6b8b403ed6e268108ee2fe4ab6fb3311` plus the original unrelated untracked files and required ignored historical artifacts):

- `test_legacy_scope_exclusion_migration.py::test_ledger_report_and_validation_are_generated_from_locked_sources`
- `test_legacy_scope_exclusion_migration.py::test_changed_files_manifest_classifies_every_path_once`

Their old changed-file manifest cannot classify the pre-existing NeurIPS reconciliation work; the current frontend additions also appear as unclassified paths.

The following four tests pass on that pre-task snapshot but fail on the requested frontend changes because they freeze historical repository hashes or the exact set of frontend files:

- `test_systematic_tier2_application.py::test_pre_application_baseline_includes_and_preserves_previous_policy_pass`
- `test_systematic_tier2_normal_priority_evidence.py::test_authoritative_append_is_exact_and_preserves_existing_rows`
- `test_systematic_tier2_normal_priority_evidence.py::test_report_reproduces_byte_for_byte`
- `test_systematic_tier2_policy.py::test_pre_task_repository_files_are_byte_identical`

The baseline reproduction ran unchanged tests against a temporary source archive, without resetting the working tree or changing assertions. The six-test baseline result was **4 passed, 2 failed**. The subsequent request authorized narrowly updating these four test expectations while preserving historical data and report receipts.

## Final snapshot reconciliation

Reproduced all six failures before editing: **6 failed**. Independently reran the unchanged six tests in the pre-task source archive: **4 passed, 2 failed**. The archive is HEAD `c160a7dd6b8b403ed6e268108ee2fe4ab6fb3311` with the original unrelated NeurIPS files and required ignored historical artifacts. Git status in that archive uses the original Git directory with the archive as `GIT_WORK_TREE`; the live checkout and index were never reset or staged.

| Test (under `tests/`) | Classification | Evidence and reconciliation |
| --- | --- | --- |
| `test_legacy_scope_exclusion_migration.py::test_ledger_report_and_validation_are_generated_from_locked_sources` | `PRE_EXISTING` | Fails unchanged in the pre-task archive because the historical changed-files manifest is stale and does not classify the original NeurIPS work. Left untouched. |
| `test_legacy_scope_exclusion_migration.py::test_changed_files_manifest_classifies_every_path_once` | `PRE_EXISTING` | Fails unchanged in the pre-task archive with 20 unclassified NeurIPS paths. Left untouched. |
| `test_systematic_tier2_application.py::test_pre_application_baseline_includes_and_preserves_previous_policy_pass` | `EXPECTED_SNAPSHOT_UPDATE` | Passed before refinement; rejected the 19 approved existing frontend/test file changes. Now checks the exact approved successor bytes and exact remaining changed-path set, retaining the previous-policy baseline entries and all original integrity checks. |
| `test_systematic_tier2_policy.py::test_pre_task_repository_files_are_byte_identical` | `EXPECTED_SNAPSHOT_UPDATE` | Passed before refinement; rejected the same 19 approved file changes. Now accepts only the byte-checked successor snapshot, including the narrow reconciliation test edits; unrelated protected-file changes still fail. |
| `test_systematic_tier2_normal_priority_evidence.py::test_authoritative_append_is_exact_and_preserves_existing_rows` | `EXPECTED_SNAPSHOT_UPDATE` | Passed before refinement; its 16-file historical frontend inventory rejected exactly `web/methodology.html` and `web/paper_search_helpers.js`. Now verifies the exact 18-file current frontend and the archived historical frontend separately. Original curated-row, publication-record, and marker-record comparisons are unchanged. |
| `test_systematic_tier2_normal_priority_evidence.py::test_report_reproduces_byte_for_byte` | `EXPECTED_SNAPSHOT_UPDATE` | The same two approved frontend additions blocked report reproduction. The test now verifies current frontend bytes before replaying the historical audit using its byte-verified archived frontend. The report still reproduces byte for byte; no report or data receipt was regenerated. |

Classification: **2 `PRE_EXISTING`, 4 `EXPECTED_SNAPSHOT_UPDATE`, 0 `REAL_REGRESSION`**. Reviewed all production and test diffs: the mismatches match the approved name/tagline, scope, default Unique Papers view, explicit shared views, map legend/statistics, search/relevance, citation, Methodology, and public metadata changes. No unrelated behavioral or structural mismatch was accepted.

This reconciliation changes only those four tests in three files, adds `tests/public_refinement_snapshot.py` and `tests/fixtures/public_website_refinement_2026_10_01.json`, and updates this document. The JSON contains exact SHA-256 values for 40 frontend/citation/supporting-test files, including the unchanged files required by the historical frontend inventory. It contains no corpus data or replacement historical receipts. The helper checks the full current inventory, archived frontend hashes, and original integrity results. Its historical audit reads the real current data through a temporary symlink; data checks are neither mocked nor replaced.

Negative checks in a temporary copy confirmed rejection of a one-byte frontend change, an additional unapproved frontend file, and an unrelated protected-data change. No tests were deleted, skipped, loosened to substring checks, or marked as expected failures.

### Final verification — 2026-10-02

The full-suite process that was pending at the usage-limit interruption completed successfully as a test run: **1,536 passed, 2 failed, 2 warnings in 357.42 seconds**. Its exit code is 1 because of the two documented failures. On resume, recovered the completed process result and inspected its entire log; no incomplete run or estimated total is used. No production or test file changed after that run began. The final “Edited a file” action before the interruption updated only this audit document with the reconciliation explanation.

| Check | Final result |
| --- | --- |
| Original complete targeted frontend/header/refinement set | **323 passed** |
| Three affected historical test files | **30 passed** |
| Four reconciled guard tests, rerun after resuming | **4 passed** |
| Full existing suite with established Python/Node runtime and localhost access | **1,536 passed, 2 failed**, 2 existing return-value warnings |
| Independent unchanged pre-task six-test reproduction | **4 passed, 2 failed** |
| JavaScript syntax, rerun after resuming | **13 files passed** |
| Local/static links and HTML anchors, rerun after resuming | **42 targets passed** |
| `CITATION.cff`, rerun after resuming | YAML parsed; applicable supplied-field constraints checked against the official CFF 1.2.0 schema |
| Original data checksums, rerun after resuming | **105/105 unchanged** |
| Public exports | **623 papers; 1,392 paper–institution relationships** |
| Reconciliation-start protected files | **3,991 byte-identical**, including data, frontend, scripts, citation, the untouched pre-existing test file, and NeurIPS documents |
| Exact reviewed frontend/test snapshot | **40/40 hashes unchanged** |
| `git diff --check` | Passed |

The only remaining failures are:

- `tests/test_legacy_scope_exclusion_migration.py::test_ledger_report_and_validation_are_generated_from_locked_sources`
- `tests/test_legacy_scope_exclusion_migration.py::test_changed_files_manifest_classifies_every_path_once`

Both independently reproduce against the pre-task archive and remain untouched. Their current diagnostics also list the intended public frontend files, which the historical changed-file manifest does not classify. The four refinement-induced failures are gone; there are no additional failures.

Reviewed the full tracked diff and every intended new file. The task comprises **23 modified tracked files and 8 intended new files**, grouped as public frontend, Methodology/citation, focused tests/snapshot support, and this audit document. The **20 unrelated untracked NeurIPS paths** match the pre-task archive; all **24 NeurIPS files including ignored historical artifacts** were also checked byte for byte. No debug output, browser artifacts, temporary files, generated data, dependency changes, or unrelated edits were introduced into the repository.

No production frontend file changed during reconciliation or resumption, so the successful earlier browser checks remain applicable and were not repeated. HEAD remains `c160a7dd6b8b403ed6e268108ee2fe4ab6fb3311`; the index is empty. Nothing was staged, committed, or pushed.

Verdict: **COMMIT-READY WITH 2 DOCUMENTED PRE-EXISTING FAILURES**.

## Data and Git audit

- All **105** saved SHA-256 checksums for curated/manual CSV/JSON and public JSON match the pre-edit manifest.
- Public export counts remain **623 unique papers** and **1,392 paper–institution records**. No rebuild was needed.
- Comparing original and refined JavaScript in Chrome yields identical paper/map identities, **623 papers**, **1,391 canonicalized institution records**, **564 institutions**, **48 countries**, and **681 location markers**. The existing browser canonicalization accounts for the difference between 1,392 exported rows and 1,391 rendered relationships; this behavior was not changed.
- Paper corpus, taxonomy, exclusions, affiliations, institution mappings, coordinates, identity/deduplication logic, and source/public data are unchanged. No admin code was changed.
- The original unrelated NeurIPS files remain untouched: the manual reconciliation JSON, processed gap-fill directory, two NeurIPS documents, and curation script.
- Browser screenshots, logs, schema download, and baseline-reproduction artifacts remain outside the repository in temporary directories. No debug logging or temporary generated files were added to the application.
- Nothing was staged, committed, or pushed.

## Maintainer decision and deferred work

No explicit authoritative project code or data redistribution license exists. No license was invented or granted. A maintainer decision is required.

No DOI, ORCID, affiliation, release version, or release date was invented for the project citation. The CFF schema reference is the [official Citation File Format 1.2.0 schema](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema.json).

A favicon and social preview image remain deferred: the only existing project image contains the obsolete title and is not suitable for the updated identity. No new asset, analytics, backend, or external runtime dependency was introduced.
