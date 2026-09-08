# Key-paper reconciliation: final validation

Validated against the task-start snapshot `/tmp/key-reconciliation-baseline`, not against a reconstructed pre-task corpus. The prior authorized audit-integrity work remains in the working tree. No commit or push was performed.

## Results

| Check | Result |
| --- | --- |
| Standard refresh | Passed (`--skip-search`); no collection or geocoding search |
| Public validation | 0 errors; 21 paper warnings for missing/partial affiliations, 0 map warnings |
| Curated validation | 0 errors; 224 warnings; pending metadata/affiliations remain visible |
| Focused suites | 262 passed |
| Full suite | 1,407 passed; 19 failed |
| HEAD reproduction | All 19 remaining failures reproduced individually on unchanged HEAD |
| Duplicate/identity checks | All 10 additions passed six-part checks against the final public + curated corpus |
| Key audit CSV/Markdown | Byte-fresh; row counts equal summary counts; 299 entries partition completely |
| Public JSON + quality/author reports | Byte-identical to an independent generator run using temporary outputs |
| Reconciliation report/integrity output | Fresh against their generators |
| git diff --check | Passed |

## Corpus and audit

| Metric | Before | After |
| --- | ---: | ---: |
| Public papers | 613 | 623 |
| Published-only | 517 | 519 |
| Unique mapped papers | 607 | 607 |
| Map records | 1,425 | 1,425 |
| Checklist total | 299 | 299 |
| Bibliography-covered | 253 | 290 |
| Covered with markers | 253 | 280 |
| Covered but markerless | 0 | 10 |
| Candidate-only | 3 | 0 |
| Genuinely missing | 26 | 0 |
| Identity/title review | 17 | 2 |
| Excluded checklist rows | 0 | 7 |

The original 17 identity cases resolve to 13 title variants, 3 metadata conflicts, and 1 distinct in-scope work now added. The original 3 candidate-only rows resolve to 2 existing papers and 1 existing exclusion. The original 26 missing rows resolve to 9 existing papers, 9 additions, 6 exclusions, and 2 AMBIGUOUS cases. Row 73 supplies the tenth addition under the resumed authorization. Rows 177 and 223 remain explicitly AMBIGUOUS; no missing entries were silently dropped.

See [the 46-case report](key_paper_reconciliation.md) for every decision, evidence URL and addition identifier.

## Strict existing-data comparison

Only one field of one pre-existing curated paper changed:

| Paper ID | Field | Before | After |
| --- | --- | --- | --- |
| curated:5fde2c559e029508e0c3 | title | Human vs. AI: A Novel Benchmark and a Comparative Study on the Detection\n of Generated Images and the Impact of Prompts | Human vs. AI: A Novel Benchmark and a Comparative Study on the Detection of Generated Images and the Impact of Prompts |

The same title correction propagates to the existing bibliography and map record. Every other field of every pre-existing public paper and marker is unchanged. Dataset export timestamps update normally.

- All 613 prior taxonomy rows are an exact byte prefix of the final file; ten needs_review rows are appended. All three taxonomy dimensions of each addition remain needs_review.
- All ten additions have exactly one taxonomy row, `curation_status=needs_review`, `review_status=pending`, and no author–institution mappings.
- All pre-existing venue aliases are byte-identical; one official-source CVWW alias is appended. `venue:computer-vision-winter-workshop` is produced by the existing venue ID algorithm and resolves through the canonical registry.
- All institution, alias, hierarchy, location, author–institution mapping and institution-review files are byte-identical to the task snapshot. The exporter’s five unrelated location-review status/timestamp changes were detected and restored.
- 82 other curated/manual source files are byte-identical. Source SHA-256 values, every paper-field difference and full new-paper records are retained in [the integrity output](key_paper_reconciliation_integrity.json).

## Exclusion registry changes

No existing exclusion row changed. Exactly these three rows were appended:

| Exclusion ID | Paper | Reason |
| --- | --- | --- |
| exclusion-35748a4440444fa3a830fe3cee14c22e | DBINDS - Can Initial Noise from Diffusion Model Inversion Help Reveal AI-Generated Videos? | Primary arXiv 2511.09184 describes generated-video detection using temporal inversion dynamics; video-only scope is excluded. Evidence: https://arxiv.org/abs/2511.09184 |
| exclusion-9f5d62eaf196470e9eff250d1e9baba9 | Training-free Detection of Text-to-video Generations via Over-coherence | Official WACV 2026 proceedings describe text-to-video detection through temporal over-coherence; video-only method is outside generated-image scope. Evidence: https://openaccess.thecvf.com/content/WACV2026/html/Brokman_Training-free_Detection_of_Text-to-video_Generations_via_Over-coherence_WACV_2026_paper.html |
| exclusion-e90e9f8a47eb43e2b53702037d6e5fe7 | Localizing Perceptual Artifacts in Synthetic Images for Image Quality Assessment via Deep-Learning-Based Anomaly Detection | Publisher/Crossref abstract targets perceptual defects for image quality assurance and editing, not forensic origin detection or manipulation localization. Exclude consistently with existing fidelity-only scope decisions. Evidence: https://www.mdpi.com/2079-9292/15/5/916; https://api.crossref.org/works/10.3390/electronics15050916 |

Four pre-existing exclusions are newly recognized by checklist identity resolution: Reverse Engineering, HFI, LDR-Net and DeepArt. Those are audit-classification changes, not exclusion-data edits. Active exclusion rows increase from 47 to 50; total registry rows (including inactive history) increase from 53 to 56. The seven recognized checklist exclusions each resolve to exactly one authoritative registry row. Over-coherence uses its verified exact title/year because no stronger identifier was verified.

## Tests and baseline failures

Focused suites cover reconciliation, audit, public refresh/export/shrinkage/sync, public validation, missing-author reports, curated institution-review validation, taxonomy, canonical venues, and Admin refresh/publish behavior. The current-corpus assertions were updated for exactly ten pending additions; historical release fixtures, historical counts and unrelated frontend expectations were not changed.

Bundled Node: `/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`. Python: repository-compatible system Python 3.9.

HEAD commit: `9762a1a1ade987bb1702d254219792d9a629b602`. A fresh `git archive HEAD` was checked against every tracked Git blob; zero tracked-file mismatches. The first archive-wide run had two additional failures from missing ignored runtime caches. Supplying those unchanged caches made both pass. The 19 remaining failures were then replayed with caches present and reproduced exactly.

| Remaining failed test | Reproduces on HEAD |
| --- | --- |
| `tests/test_frontend_chart_filters.py::FrontendChartAndInstitutionFilterTests::test_result_count_tracks_active_view_and_empty_state` | Yes |
| `tests/test_frontend_chart_quick_filters.py::FrontendChartQuickFilterTests::test_activation_toggles_each_filter_with_one_render_and_url_update` | Yes |
| `tests/test_frontend_chart_quick_filters.py::FrontendChartQuickFilterTests::test_rendered_pressed_state_tracks_external_filter_state` | Yes |
| `tests/test_frontend_country_institution_type_filters.py::FrontendCountryInstitutionTypeFilterTests::test_dropdowns_are_compact_defaults_near_institution_filters` | Yes |
| `tests/test_frontend_data_unit_semantics.py::FrontendDataUnitSemanticsTests::test_filtered_counts_and_charts_update_from_the_same_record_sets` | Yes |
| `tests/test_frontend_map_results_sync.py::FrontendMapResultsSyncTests::test_result_institution_controls_select_a_visible_marker_without_filtering` | Yes |
| `tests/test_frontend_mobile_summary_charts.py::FrontendMobileSummaryChartTests::test_layout_reuses_existing_accessible_chart_controls_and_pipeline` | Yes |
| `tests/test_frontend_paper_deep_links.py::FrontendPaperDeepLinkTests::test_explicit_selection_and_close_push_only_the_paper_url_state` | Yes |
| `tests/test_frontend_paper_deep_links.py::FrontendPaperDeepLinkTests::test_restoration_opens_visible_and_filtered_out_papers_without_changing_filters` | Yes |
| `tests/test_frontend_paper_deep_links.py::FrontendPaperDeepLinkTests::test_stale_identifier_has_a_closable_non_destructive_state` | Yes |
| `tests/test_frontend_paper_details.py::FrontendPaperDetailsTests::test_details_vertical_rhythm_is_compact_and_controls_stay_accessible` | Yes |
| `tests/test_frontend_paper_issue_reporting.py::FrontendPaperIssueReportingTests::test_context_uses_only_public_display_metadata` | Yes |
| `tests/test_frontend_public_labels_layout.py::FrontendPublicLabelsLayoutTests::test_all_select_filters_use_one_custom_dropdown_controller` | Yes |
| `tests/test_frontend_public_labels_layout.py::FrontendPublicLabelsLayoutTests::test_compact_filter_geometry_and_overview_responsive_grid` | Yes |
| `tests/test_frontend_public_labels_layout.py::FrontendPublicLabelsLayoutTests::test_filter_order_places_publication_type_immediately_before_venue` | Yes |
| `tests/test_frontend_public_labels_layout.py::FrontendPublicLabelsLayoutTests::test_public_controls_and_cards_use_consistent_spacing_rhythm` | Yes |
| `tests/test_frontend_public_labels_layout.py::FrontendPublicLabelsLayoutTests::test_renamed_public_filter_labels_and_title_case` | Yes |
| `tests/test_frontend_year_range_slider.py::FrontendYearRangeSliderTests::test_year_combines_with_venue_venue_type_country_and_institution_type` | Yes |
| `tests/test_workshop_venue_audit.py::WorkshopArtifactTests::test_full_dataset_before_after_and_source_preservation` | Yes |

Logs: `/tmp/reconciliation-final-targeted.log`, `/tmp/reconciliation-final-full.log`, `/tmp/reconciliation-head-full.log`, `/tmp/reconciliation-head-inputs-check.log`, `/tmp/reconciliation-head-failures-reproduced.log`, `/tmp/reconciliation-refresh-complete.log`, `/tmp/reconciliation-public-final.log`, `/tmp/reconciliation-curated-final.log`.

## Changed files

This list includes the retained, previously authorized audit-integrity edits as well as reconciliation changes. No unrelated frontend implementation, institution decision or historical fixture changed.

- `data/curated/paper_exclusions.csv`
- `data/curated/paper_taxonomy.csv`
- `data/curated/papers.csv`
- `data/curated/venue_aliases.csv`
- `data/manual/key_paper_coverage_report.csv`
- `data/manual/missing_author_mappings_report.csv`
- `docs/key_paper_coverage_report.md`
- `docs/missing_author_mappings_report.md`
- `docs/public_preview_report.md`
- `scripts/admin_review_queues.py`
- `scripts/admin_workflows.py`
- `scripts/audit_key_paper_coverage.py`
- `scripts/diagnose_key_paper_exports.py`
- `scripts/refresh_public_preview.py`
- `scripts/report_high_risk_markers.py`
- `scripts/report_missing_author_mappings.py`
- `scripts/report_public_preview.py`
- `scripts/validate_public_preview.py`
- `tests/baseline_expectations.py`
- `tests/test_admin_action_required.py`
- `tests/test_author_affiliation_evidence_repairs.py`
- `tests/test_frontend_published_only_filter.py`
- `tests/test_paper_metadata_consistency_audit.py`
- `tests/test_paper_taxonomy_migration.py`
- `tests/test_public_preview_deduplication.py`
- `tests/test_repository_baseline.py`
- `web/data/public_preview_map_data.json`
- `web/data/public_preview_papers.json`
- `data/manual/key_paper_reconciliation.json`
- `docs/key_paper_coverage_methodology.md`
- `docs/key_paper_reconciliation.md`
- `docs/key_paper_reconciliation_integrity.json`
- `scripts/key_paper_reconciliation.py`
- `scripts/report_key_paper_reconciliation.py`
- `scripts/verify_key_paper_reconciliation.py`
- `tests/test_key_paper_coverage.py`
- `tests/test_key_paper_reconciliation.py`
- `docs/key_paper_reconciliation_validation.md`
- `data/raw/key_paper_reconciliation_2026_09_08/`: 69 evidence/manifest/documentation files; individual evidence names and hashes are listed in its manifest.

## Reproduction

```sh
python3 scripts/refresh_public_preview.py --skip-search --user-agent targeted-key-reconciliation
python3 scripts/validate_public_preview.py
python3 scripts/validate_curated_database.py
python3 scripts/audit_key_paper_coverage.py --check
python3 scripts/report_key_paper_reconciliation.py --check
python3 scripts/verify_key_paper_reconciliation.py --baseline /tmp/key-reconciliation-baseline --check
git diff --check
```

The standard exporter still updates its institution-location review cache; the strict snapshot verifier detects this known unrelated side effect. Restore only those five verified status/timestamp changes before asserting an institution-neutral reconciliation diff. The independent reproduction run redirects this cache to a temporary file.
