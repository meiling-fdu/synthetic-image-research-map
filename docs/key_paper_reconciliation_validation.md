# Ten-paper curation and exclusion reconciliation — final validation

This report supersedes the original reconciliation validation snapshot. The public corpus is 620 papers, not the former 623-paper reconciliation milestone. The unchanged manual reconciliation decisions remain historical identity evidence; current coverage and curation are derived from current authoritative records.

## Corpus and checklist

- Public papers: 623 → 620; published-only papers: 519 → 520 (Prefill is one NeurIPS 2025 GenProCC workshop/arXiv work).
- Mapped public papers: 607 → 613; markers: 1425 → 1438; unique paper–institution relationships: 1437.
- All 299 checklist rows accounted for: 287 publicly covered (286 with markers, 1 markerless), 10 excluded, 2 ambiguous, 0 candidate-only and 0 genuinely missing.
- Exactly ten curated additions remain: seven public and three CURATED_BUT_EXCLUDED. Bibliography reviewed 9/10; taxonomy reviewed 10/10; affiliation reviewed 9/10; fully curated 7/10. Six have public markers; UniAIDet is publicly present without a marker.

## Existing exclusion identity traces

The following exclusions were created on July 13, before this task. The verified OpenAlex identifier causes each match; the stable curated ID then links any older preview copy lacking that identifier. Formal DOI fields stay empty for these preprints; the exclusion registry retains its original arXiv-issued DOI. Reason `other`, note `preprint`, activation flags and dates are unchanged.

| Paper | Curated ID | arXiv | OpenAlex | Existing exclusion | Effective UTC |
|---|---|---|---|---|---|
| Provenance Detection for AI-Generated Images: Combining Perceptual Hashing, Homomorphic Encryption, and AI Detection Models | curated:2334b1774b5f65217e7b | 2503.11195 | https://openalex.org/W4417284156 | exclusion-afa362e960d2495eb5c5b44c1431736e | 2026-07-13T20:14:33Z |
| Pay Less Attention to Deceptive Artifacts: Robust Detection of Compressed Deepfakes on Online Social Networks | curated:509324a7a8bc94c3eb78 | 2506.20548 | https://openalex.org/W4414989730 | exclusion-bb870f305db948d18fb473d072844c48 | 2026-07-13T20:15:50Z |
| Redefining Generalization in Visual Domains: A Two-Axis Framework for Fake Image Detection with FusionDetect | curated:40d551857163fa643202 | 2510.05740 | https://openalex.org/W4414978765 | exclusion-17447bd65e3b4aae98831c8d0bf68be0 | 2026-07-13T20:06:06Z |

## Precedence and preservation fixes

1. `_merge_curated_paper` previously treated overall confirmation/formal publication as the only authoritative paths. Field-level primary reviews with intentionally pending fields could lose to stale data. Explicit primary-source review now takes precedence without promoting pending review states. The final `preserve_existing_curation_status` step no longer restores an older generated status over that explicit decision. Legacy manual provenance remains preserved.
2. Excluded curated records were skipped before their new identifiers reached stale public records. `exclusions_with_curated_identities` now builds an in-memory bridge from strong curated identifiers to stable paper IDs before export filtering and shrinkage analysis. The coverage audit uses the same bridge. No fuzzy/title-only matching or exclusion CSV mutation is introduced.
3. `_mark_location_known` now requires an already confirmed location-review decision before normalizing the queue row. A usable canonical location does not authorize export to promote an unrelated pending paper-specific review.

## Strict integrity comparison

- Protected older curated rows changed: 0 of 5,380.
- Protected older public papers changed: 0 of 613; original marker records changed: 0 of 1,425.
- Older location-review rows changed: 0, including the five previously affected rows.
- Exclusion decisions changed: 0. Exactly the three target exclusions explain the decrease to 620.
- Strong-identifier duplicates: 0, including identifiers retained in merged-version provenance.
- New valid relationships: 24 paper–institution rows representing 57 author–institution pairs; all belong to the ten target records. Twelve canonical institutions, six confirmed locations, six pending location reviews, four hierarchy edges and no aliases were added. Unlocated institutions do not receive dummy location rows.
- Per-paper institution/author groupings and unresolved fields: `docs/primary_paper_curation_2026_09_08.csv` and the manual evidence ledger.

## Validation and reproducibility

- Standard final refresh: PASS; public validation: 0 errors, 11 existing unindexed-author warnings; map validation: 0 errors and 0 warnings.
- Curated database validation: 0 errors, 0 duplicate candidates, 215 warnings (HEAD: 224). The one newly exposed author-name warning is Aayush Gupta’s explicit MIT + ZK Email block; both directly supported affiliations are retained without merging institutions.
- Active exclusion validation: all 50 active exclusions absent from public output; 0 errors, two existing restored-but-absent warnings.
- Metadata consistency: 11,160 checks across 620 papers; 0 true inconsistencies, 0 fallback risks, 0 affiliation mismatches.
- Public paper/map JSON, public quality report and missing-author report reproduced byte-for-byte across repeated refreshes. The coverage report input digest appropriately changed when authoritative identifiers/CSV normalization changed, then passed its final exact freshness check.
- Ten derived audit files (coverage CSV/Markdown, reconciliation Markdown/integrity JSON, curation CSV/JSON/Markdown, metadata consistency CSV/Markdown and public institution integrity JSON) were regenerated twice: 0 byte differences.
- Focused suites: 278 passed; additional metadata and published-only filter suites: 11 passed. The complete run exposed two further issues: an obsolete four-case pending-location expectation and noncanonical Prefill title capitalization. The expectation now names the two evidence-backed pending institutions and the curated title is canonicalized; their affected suites pass 35 tests.
- Final full suite: **1420 passed, 19 failed** (1439 tests). Valid unchanged HEAD: 1407 passed, 19 failed. Exact failed-test sets are identical; NEW REGRESSION: 0; TEST-ENVIRONMENT ARTIFACT: 0.
- HEAD comparison: commit `3ed3273b9a6ae8b00ee4cf2e2ded5f913fc7cf4b`; all 866 tracked files match their Git blobs, with no missing tracked files. Original ignored candidate/raw/processed inputs were supplied before comparison. The initial incomplete archive comparison is not used for classification.
- Final independent export: both public JSON files from the export regression are byte-identical to the repository outputs, including generation metadata.
- `git diff --check`: PASS.

### Remaining failures

All 19 are PRE-EXISTING ON VALID HEAD BASELINE. Eighteen are frontend expectations already failing on unchanged code. The final historical raw-source hash check expects an absent `data/raw/.gitignore`; that file is absent in both the real repository and the valid HEAD checkout. No historical source or unrelated frontend assertion was changed to conceal these failures.

| Test | Classification |
|---|---|
| `tests.test_frontend_chart_filters.FrontendChartAndInstitutionFilterTests::test_result_count_tracks_active_view_and_empty_state` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_chart_quick_filters.FrontendChartQuickFilterTests::test_activation_toggles_each_filter_with_one_render_and_url_update` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_chart_quick_filters.FrontendChartQuickFilterTests::test_rendered_pressed_state_tracks_external_filter_state` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_country_institution_type_filters.FrontendCountryInstitutionTypeFilterTests::test_dropdowns_are_compact_defaults_near_institution_filters` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_data_unit_semantics.FrontendDataUnitSemanticsTests::test_filtered_counts_and_charts_update_from_the_same_record_sets` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_map_results_sync.FrontendMapResultsSyncTests::test_result_institution_controls_select_a_visible_marker_without_filtering` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_mobile_summary_charts.FrontendMobileSummaryChartTests::test_layout_reuses_existing_accessible_chart_controls_and_pipeline` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_paper_deep_links.FrontendPaperDeepLinkTests::test_explicit_selection_and_close_push_only_the_paper_url_state` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_paper_deep_links.FrontendPaperDeepLinkTests::test_restoration_opens_visible_and_filtered_out_papers_without_changing_filters` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_paper_deep_links.FrontendPaperDeepLinkTests::test_stale_identifier_has_a_closable_non_destructive_state` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_paper_details.FrontendPaperDetailsTests::test_details_vertical_rhythm_is_compact_and_controls_stay_accessible` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_paper_issue_reporting.FrontendPaperIssueReportingTests::test_context_uses_only_public_display_metadata` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_public_labels_layout.FrontendPublicLabelsLayoutTests::test_all_select_filters_use_one_custom_dropdown_controller` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_public_labels_layout.FrontendPublicLabelsLayoutTests::test_compact_filter_geometry_and_overview_responsive_grid` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_public_labels_layout.FrontendPublicLabelsLayoutTests::test_filter_order_places_publication_type_immediately_before_venue` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_public_labels_layout.FrontendPublicLabelsLayoutTests::test_public_controls_and_cards_use_consistent_spacing_rhythm` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_public_labels_layout.FrontendPublicLabelsLayoutTests::test_renamed_public_filter_labels_and_title_case` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_frontend_year_range_slider.FrontendYearRangeSliderTests::test_year_combines_with_venue_venue_type_country_and_institution_type` | PRE-EXISTING ON VALID HEAD BASELINE |
| `tests.test_workshop_venue_audit.WorkshopArtifactTests::test_full_dataset_before_after_and_source_preservation` | PRE-EXISTING ON VALID HEAD BASELINE |

Machine-readable run evidence: `/tmp/primary-final-confirmed-full.xml`, `/tmp/primary-head-tests.xml`, `/tmp/primary-final-validation.json`. Final public SHA-256 hashes:
- `public_preview_papers.json`: `8fd68f2c487dbc8872698205db7e1a8158c886e6bb14c58245005b964a6f523d`.
- `public_preview_map_data.json`: `4c959c175da31a6b7fe3f92591f4950d02f14f79b5a1f55fe7b6c1cfa7b81125`.

## Reproduction commands

```sh
python3 scripts/refresh_public_preview.py --skip-search --user-agent synthetic-image-research-map-primary-curation/1.0
python3 scripts/report_primary_paper_curation.py --check
python3 scripts/audit_key_paper_coverage.py --check
python3 scripts/report_key_paper_reconciliation.py --check
python3 scripts/verify_key_paper_reconciliation.py --check
python3 scripts/validate_curated_database.py
python3 scripts/validate_paper_exclusions.py
python3 scripts/audit_paper_metadata_consistency.py
git diff --check
```

Full tests use system Python 3.9 with the bundled Node directory added to PATH. Localhost permission is needed for the Admin server tests. No commit or push was performed.

## Changed files

The expected diff contains only target curation data, append-only relationships/evidence, exporter and audit logic, affected tests and regenerated artifacts. All protected source/public comparisons report zero unexpected changes.

- `data/curated/author_institution_mappings.csv`
- `data/curated/institution_audit_log.csv`
- `data/curated/institution_hierarchy.csv`
- `data/curated/institution_location_audit_log.csv`
- `data/curated/institution_location_review.csv`
- `data/curated/institution_locations.csv`
- `data/curated/institutions.csv`
- `data/curated/paper_taxonomy.csv`
- `data/curated/papers.csv`
- `data/manual/key_paper_coverage_report.csv`
- `data/manual/missing_author_mappings_report.csv`
- `data/manual/primary_paper_curation_2026_09_08.json`
- `data/processed/primary_curation_baseline_2026_09_08.json`
- `docs/data_schema.md`
- `docs/key_paper_coverage_report.md`
- `docs/key_paper_reconciliation.md`
- `docs/key_paper_reconciliation_integrity.json`
- `docs/key_paper_reconciliation_validation.md`
- `docs/missing_author_mappings_report.md`
- `docs/paper_metadata_consistency_audit.csv`
- `docs/paper_metadata_consistency_audit.md`
- `docs/primary_curation_public_integrity.json`
- `docs/primary_paper_curation_2026_09_08.csv`
- `docs/primary_paper_curation_2026_09_08.json`
- `docs/primary_paper_curation_2026_09_08.md`
- `docs/public_preview_report.md`
- `scripts/audit_key_paper_coverage.py`
- `scripts/curated_export.py`
- `scripts/export_public_preview.py`
- `scripts/paper_exclusions.py`
- `scripts/report_key_paper_reconciliation.py`
- `scripts/report_primary_paper_curation.py`
- `scripts/verify_key_paper_reconciliation.py`
- `tests/baseline_expectations.py`
- `tests/test_author_affiliation_evidence_repairs.py`
- `tests/test_frontend_published_only_filter.py`
- `tests/test_institution_hierarchy.py`
- `tests/test_key_paper_reconciliation.py`
- `tests/test_manual_location_audit_20260827.py`
- `tests/test_paper_metadata_consistency_audit.py`
- `tests/test_paper_taxonomy_migration.py`
- `tests/test_primary_paper_curation.py`
- `tests/test_repository_baseline.py`
- `web/data/public_preview_map_data.json`
- `web/data/public_preview_papers.json`
- `data/raw/primary_curation_2026_09_08/`: 47 evidence/manifest files. Cached sources are checked against the SHA-256 manifest.
