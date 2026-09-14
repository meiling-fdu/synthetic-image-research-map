# Baseline test cleanup — 2026-09-09

## Baseline and pre-edit classification

Current working tree preserved, including prior uncommitted curation. HEAD: `3ed3273b9a6ae8b00ee4cf2e2ded5f913fc7cf4b`. Full baseline: **1420 passed, 19 failed** (316.43 s). All failures classified before repository edits. 653 files under `data/` and `web/data/` hashed before tests. No commit or push.

The intentional frontend freeze is documented by commit `1e850da9dd9340c4fb0c80f8a950d71b59fd51c0` (public interactions and URL contracts); taxonomy arrays by `02a324c`. Newer tests cited below independently exercise these contracts.

| # | Test path / name | Classification | Feature | Failing expectation | Current behavior / root cause | First source | Narrow fix | Evidence | Final status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `tests/test_frontend_chart_filters.py` / `test_result_count_tracks_active_view_and_empty_state` | STALE_TEST_EXPECTATION | Empty results | Inline No matching resultNoun string | Contextual renderNoResultsState and zero count | `web/app.js` | Assert zero count and delegated contextual recovery | test_frontend_no_results_recovery.py | PASS |
| 2 | `tests/test_frontend_chart_quick_filters.py` / `test_activation_toggles_each_filter_with_one_render_and_url_update` | STALE_FIXTURE | Task chart activation | Singular task action sets scalar value | tasks action toggles multiselect options | `web/app.js` | Use current action and selected options; retain render, URL and focus counts | 02a324c; activateChartFilter | PASS |
| 3 | `tests/test_frontend_chart_quick_filters.py` / `test_rendered_pressed_state_tracks_external_filter_state` | STALE_FIXTURE | Chart pressed state | Scalar legacy task records, missing helper | Array taxonomy uses selectedFilterValues/getTasks | `web/app.js` | Supply array records and production selection helper | 02a324c; renderTaskChart | PASS |
| 4 | `tests/test_frontend_country_institution_type_filters.py` / `test_dropdowns_are_compact_defaults_near_institution_filters` | STALE_TEST_EXPECTATION | Filter dropdowns | 9 dropdowns | 10 including Publication Status | `web/index.html` | Include Publication Status in exact control count | test_frontend_published_only_filter.py | PASS |
| 5 | `tests/test_frontend_data_unit_semantics.py` / `test_filtered_counts_and_charts_update_from_the_same_record_sets` | STALE_FIXTURE | Chart data units | Missing selection helper and old task total copy | Overlapping array labels and explicit total unique papers | `web/app.js` | Supply array taxonomy fixtures; assert exact total and overlap counts | 02a324c; renderTaskChart | PASS |
| 6 | `tests/test_frontend_map_results_sync.py` / `test_result_institution_controls_select_a_visible_marker_without_filtering` | STALE_FIXTURE | Result institution selection | Old marker-bearing selection object; missing institutionIdentity | Paper identity with contextualInstitutionId and source | `web/app.js` | Assert current selection object and reject unavailable/stale controls | test_frontend_map_results_sync.py; resolveShowInResultsTarget | PASS |
| 7 | `tests/test_frontend_mobile_summary_charts.py` / `test_layout_reuses_existing_accessible_chart_controls_and_pipeline` | STALE_TEST_EXPECTATION | Chart keyboard focus | Optional focus on refreshed button only | Button or viewport-appropriate fallback receives focus | `web/app.js` | Assert fallback expression and focus without scroll | 1e850da; test_frontend_chart_quick_filters.py | PASS |
| 8 | `tests/test_frontend_paper_deep_links.py` / `test_explicit_selection_and_close_push_only_the_paper_url_state` | STALE_FIXTURE | Paper URL selection/clear | Extracted wrapper without selectPaper | Wrapper delegates to shared paper selection | `web/app.js` | Include real shared selection helper and assert identity/history/clear | test_frontend_adaptive_details.py | PASS |
| 9 | `tests/test_frontend_paper_deep_links.py` / `test_restoration_opens_visible_and_filtered_out_papers_without_changing_filters` | STALE_FIXTURE | Deep-link restoration | interactionState.selected embedded record | selectedPaperId/detailMode plus canonical identity index | `web/app.js` | Assert identity, mode, source and unchanged filters for visible/filtered/markerless cases | test_frontend_adaptive_details.py | PASS |
| 10 | `tests/test_frontend_paper_deep_links.py` / `test_stale_identifier_has_a_closable_non_destructive_state` | STALE_FIXTURE | Unavailable deep link | Clears obsolete selected/selectedMarkerId | Clears selectedPaperId and sets empty mode; keeps URL identity | `web/app.js` | Use current state and assert unavailable identity retained until explicit clear | restoreLinkedPaperSelection; public_feature_freeze_browser.cjs | PASS |
| 11 | `tests/test_frontend_paper_details.py` / `test_details_vertical_rhythm_is_compact_and_controls_stay_accessible` | STALE_TEST_EXPECTATION | Details close geometry | First CSS selector is base 32px rule | First occurrence is coarse-pointer 44px minimum override | `web/style.css` | Select base rule precisely and retain coarse-pointer minima assertions | 1e850da; test_frontend_accessibility_hardening.py | PASS |
| 12 | `tests/test_frontend_paper_issue_reporting.py` / `test_context_uses_only_public_display_metadata` | STALE_FIXTURE | Public issue metadata | Missing taxonomy helper dependencies | Issue context includes public tasks and image scopes | `web/app.js` | Supply taxonomy arrays and assert displayed values and internal metadata exclusion | 02a324c; paperIssueContext | PASS |
| 13 | `tests/test_frontend_public_labels_layout.py` / `test_all_select_filters_use_one_custom_dropdown_controller` | STALE_TEST_EXPECTATION | Shared dropdown controller | 9 controls in controller | 10 including Publication Status | `web/index.html` | Add status to exact controller mapping | test_frontend_published_only_filter.py | PASS |
| 14 | `tests/test_frontend_public_labels_layout.py` / `test_compact_filter_geometry_and_overview_responsive_grid` | STALE_TEST_EXPECTATION | Filter geometry | 8px filter grid gap | Frozen 7px gap | `web/style.css` | Assert exact 7px gap | 1e850da web/style.css diff | PASS |
| 15 | `tests/test_frontend_public_labels_layout.py` / `test_filter_order_places_publication_type_immediately_before_venue` | STALE_TEST_EXPECTATION | Filter order | Year after advanced filters | Status/year before More filters; publication type immediately before venue | `web/index.html` | Assert complete current ordering while preserving adjacent type/venue | test_frontend_more_filters.py | PASS |
| 16 | `tests/test_frontend_public_labels_layout.py` / `test_public_controls_and_cards_use_consistent_spacing_rhythm` | STALE_TEST_EXPECTATION | Control spacing | 8px filter grid gap | Frozen 7px filter gap, 8px/10px sticky-toolbar gap, 10px margin and 13px/12px/12px card padding | `web/style.css` | Assert exact freeze spacing; preserve legend assertions | 1e850da web/style.css diff | PASS |
| 17 | `tests/test_frontend_public_labels_layout.py` / `test_renamed_public_filter_labels_and_title_case` | STALE_TEST_EXPECTATION | Filter labels | 8 All options | 9 including Publication Status | `web/index.html` | Include status label and exact All count | test_frontend_published_only_filter.py | PASS |
| 18 | `tests/test_frontend_year_range_slider.py` / `test_year_combines_with_venue_venue_type_country_and_institution_type` | STALE_FIXTURE | Year + combined filters | Missing selectedFilterValues/imageScopeFilter | Independent multiselect taxonomy dimensions | `web/app.js` | Include current selection helper and inactive scope fixture; preserve exact matched IDs | recordMatchesActiveFilters; 02a324c | PASS |
| 19 | `tests/test_workshop_venue_audit.py` / `test_full_dataset_before_after_and_source_preservation` | HISTORICAL_RAW_SNAPSHOT_ISSUE | Research-source preservation | Missing raw .DS_Store hash must match | Historical recursive snapshot accidentally included OS metadata | `scripts/audit_workshop_venues.py` | Exclude explicit OS metadata names in generation and comparison; leave manifest bytes untouched | source_hashes; immutable snapshot guard | PASS |

## Fixture audit

The nine stale fixtures are manually maintained inline JavaScript harnesses in Python tests, not historical dataset snapshots. They extract current functions from `web/app.js` but retained scalar taxonomy, removed helper boundaries, or the old embedded selection object. They must track the current function dependencies and state contract. Repairs supply current array taxonomy, the actual `selectedFilterValues` helper, and the real shared `selectPaper` implementation. Isolated display/identity dependencies remain small explicit test doubles. No stored dataset fixture was regenerated.

Exact assertions remain for render/history/focus counts, task selections, pressed state, overlapping task totals, matching paper IDs, contextual institution identity, rejected stale controls, selected paper identity, preserved filters, unavailable links, and public-only issue metadata. Markerless and filtered-out selections are checked separately. The new browser smoke harness derives its samples from the current public dataset and performs no data writes.

## Historical source checksums

`source_hashes()` previously recursively hashed every file in raw/manual/curated directories. Finder metadata was therefore accidentally included: the historical manifest contains `data/raw/.DS_Store` and `data/manual/.DS_Store`, both now absent. The failing raw-preservation assertion concerned the former (not `.gitignore`). Neither file is research input.

The historical manifest remains byte-for-byte intact, consistent with the script's existing refusal to overwrite its initial snapshot and this task's data freeze. Snapshot generation and historical source comparison now apply one explicit OS-metadata exclusion policy: `.DS_Store`, `Thumbs.db`, `desktop.ini`, AppleDouble `._*`, and `__MACOSX` paths. No blanket hidden-file exclusion is used. Meaningful raw checksums are unchanged and remain exact comparisons. The new regression creates raw/manual/curated test trees, confirms OS files are omitted, preserves hidden `.evidence.json`, and confirms modified research bytes change the checksum.

## Scope and frozen behavior

Real frontend bugs fixed: **0**. Stale expectations updated: **9**. Stale fixtures corrected: **9**. Historical snapshot issue corrected: **1**. Unknown failures: **0**. No test removed or skipped, no tolerance introduced, and no public or Admin production frontend file changed. User-visible behavior and deep-link contracts are unchanged.

The previous uncommitted curation remains in place. This cleanup does not modify baseline counts, paper/taxonomy decisions, exclusions, institutions, aliases, affiliations, hierarchy, locations, review decisions, evidence registries, or public identities. Independently regenerated paper/map JSON from the full-suite export test matches the checked-in working-tree artifacts byte-for-byte. Public and curated validators both report zero errors; existing review warnings are retained.

## Final validation

| Gate | Result |
|---|---|
| Original failures individually | 19 failed → 19 passed |
| Containing modules | 152 passed |
| Frontend | 310 passed |
| Admin | 169 passed |
| Public/deep-link/map | 271 passed |
| Full repository | 1440 passed, 0 failed, 0 skipped (308.32 s) |
| Public and curated validators | 0 errors; existing 11 public / 215 curated warnings unchanged |
| Frozen data comparison | All 653 files byte-identical |
| Meaningful historical raw checksums | 258 / 258 identical |
| Public JSON regeneration | Both files byte-identical |
| git diff --check | Passed |

The existing feature-freeze browser harness passed. The accessibility harness passed at 375, 430, 768, 1024 and 1440 px with no horizontal overflow, toolbar overlap or page errors. The new core harness passed at 1440 and 375 px: default map, Publication Status (620 → 520), More filters, taxonomy, paper/author/institution autocomplete, laboratory-to-parent provenance, marker selection, Details, clear, zero-results recovery, valid/filtered-out/unavailable deep links and markerless Unique Papers discovery. No responsive regression was observed.

Two new smoke-harness assumptions were corrected during validation: direct parent matches correctly omit descendant-only provenance, so the check uses the reviewed Observatory on Social Media → Indiana University relationship; card assertions wait for asynchronous rendering after filtered identities update. These were harness corrections, with no production changes. One module run initially lacked localhost-bind permission; rerunning with the baseline test-server permissions passed.

Public papers remain **620**, published-only **520**, mapped papers **613**, and checklist accounting **299/299** (287 covered, 10 excluded, 2 ambiguous, 0 candidate-only, 0 missing). See `baseline_test_cleanup_integrity.json` for machine-readable validation evidence.

## Files changed by this cleanup

- `scripts/audit_workshop_venues.py`
- The 12 test modules named in the failure inventory above
- `tests/baseline_cleanup_browser.cjs`
- `docs/baseline_test_cleanup.md`
- `docs/baseline_test_cleanup_integrity.json`

Prior uncommitted curation changes are outside this cleanup and were preserved. No commit or push occurred.

Run Python tests with the bundled Node bin directory on PATH, and allow localhost test-server binding. Browser checks require a local static server for `web/` (default port 8899); the new smoke script accepts `PUBLIC_PREVIEW_URL`, `CHROME_EXECUTABLE`, and standard Node module resolution for Playwright.

