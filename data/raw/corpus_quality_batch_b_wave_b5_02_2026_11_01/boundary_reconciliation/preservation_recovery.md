# B5-02R recovery preservation audit

Preservation: **PRESERVATION_PASS_WITH_THREE_EXACT_APPROVED_IGNORED_EVIDENCE_LOGS**. Workflow: **RECOVERED_B5_02_CHECKPOINT_FOR_AUTHORIZED_BOUNDARY_RECONCILIATION**.

Captured 2026-11-01T11:10:08.232466+00:00; 74,879 streaming hashes over 22,529,577,274 bytes. All audit writes are external.

Exactly 120 approved paths match their pinned hashes and sizes: three changed tracked CSVs and 117 new files, classified as 114 untracked plus three ignored evidence logs. Existing tracked inventory remains 4,658 files. No staged changes or nonallowlisted untracked/ignored files.

The three historical source-sensitive guards failed on the old taxonomy hash, old taxonomy bytes, and the old 127-decision expectation versus 138 decisions. Work stopped before export, full suite, and validators; no original test, source, or evidence repair was performed. This receipt establishes preservation, not integration acceptance.

B4-03 original worktree and all 62 external archive files are unchanged. Also preserved: B3 sealed123/full126 including the separately recorded old unsealed extra; accepted B5 sealed281/full282; protected128; frozen49 across six physical roots and both native logical streams; B4 old pending8 each; C13, separate39, B2 and immutable evidence/CI632.

All 19 zero-change flags true: **True**. Failures: none. External differences: 0.

## Exact ignored evidence packaging limitation

These existing ignore rules hide three approved archived logs from ordinary untracked discovery. Their bytes remain exact. A future authorized packaging step must explicitly handle only these three exact paths; this stopped checkpoint performs no deletion, rename, ignore-rule change, staging, or repair.

- `data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/curated_validator.log`
- `data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/exclusions_validator.log`
- `data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/public_pair_validator.log`

## Final Git status

3 modified tracked; 114 untracked; 3 approved ignored; 0 staged.

```text
 M data/curated/paper_taxonomy.csv
 M data/curated/papers.csv
 M data/curated/review_decisions.csv
?? data/raw/corpus_quality_batch_b_wave_b4_03_2026_11_01/adjudication_manifest.json
?? data/raw/corpus_quality_batch_b_wave_b4_03_2026_11_01/b5_02_handoff.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/b4_03_original.diff
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/b4_compact_preservation_receipt.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/b4_handoff.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/batch_dispositions.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/batch_review.md
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/checksums.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/completion.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/effort_and_retrievals.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R110-canonical.txt
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R110-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R110-table2-3.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R138-canonical.html
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R138-doi-registration-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R138-doi-registration.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R138-official-readme-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R138-official-readme.txt
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R138-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R154-appendix-p17-SFT-details.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R154-appendix-p17-SFT-details.provenance.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R154-author-v1-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R154-author-v1.txt
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R154-canonical.html
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R154-doi-registration-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R154-doi-registration.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R154-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R154-tables2-4.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R187-canonical.html
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R187-doi-registration-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R187-doi-registration.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R187-openreview-version-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R187-publisher-vor-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R187-publisher-vor.html
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/R187-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupA/record_validation.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R161-alternate-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R161-landing-retrieval.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R161-official-landing.html
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R171-local-pmlr.html
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R171-pages.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R171-text.txt
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R256-pages.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R256-text.txt
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R564-pages.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/R564-text.txt
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/official-discovery.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/pdf_extraction.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/primary_retrievals.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/rendered/R171-p03.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/rendered/R171-p06.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/rendered/R171-p13.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/rendered/R256-p04.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/rendered/R256-p05.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/rendered/R256-p06.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/rendered/R564-p06.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/rendered/R564-p09.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/groupB/resource_links_in_primary_pdf.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/root/P231-official-program.html
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/root/R231-acm-primary.response
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/root/R275-official-landing.html
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/root/R275-pages.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/root/R275-table3-08.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/root/R275-table7-20.png
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/root/metadata-retrievals.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/evidence/root/retrievals.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/P231.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R110.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R138.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R154.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R161.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R171.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R187.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R231.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R256.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R275.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/per_paper/R564.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/P231-before-policy-traceability-fix.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/R231-before-source-hash-annotation.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/R256-independent-caveat-addendum.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/before-independent-caveat-refinement/b4_handoff.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/before-independent-caveat-refinement/batch_dispositions.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/before-independent-caveat-refinement/batch_review.md
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/before-independent-caveat-refinement/per_paper__R256.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/final_batch_QC.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/groupA-independent-review.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/groupA-traceability-amendments.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/groupB-independent-review.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/independent_scientific_QC.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/preservation_final.md
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/qc/root-group-review.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b3_03/validation.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/B403_current_tests.xml
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/B403_track_tests.xml
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/B403_track_tests_run.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/changed_file_inventory.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/checksums.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/completion.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/investigation/B3_input_verification.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/investigation/P231_semantics_review.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/investigation/P231_semantics_review.md
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/investigation/schema_preflight.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/acceptance_accounting_qc.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/historical_snapshot_tests.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/historical_snapshot_tests.xml
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/independent_acceptance_summary.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/independent_adjudication_review.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/independent_preapply_review.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/preservation_final.md
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/qc/preservation_receipt_hashes.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/evidence_archive/b4_03/validation.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/integration_manifest.json
?? data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01/portable_evidence_manifest.json
?? docs/corpus_quality_batch_b_wave_b4_03_2026_11_01.md
```

## Zero-change flags

- `unsupported_tracked_changes_zero`: **True**
- `unsupported_untracked_files_zero`: **True**
- `nonallowlisted_ignored_files_zero`: **True**
- `staged_changes_zero`: **True**
- `logical_index_changes_zero`: **True**
- `physical_index_changes_zero`: **True**
- `HEAD_branch_changes_zero`: **True**
- `existing_manual_data_changes_zero`: **True**
- `existing_raw_processed_changes_zero`: **True**
- `existing_code_tests_documentation_changes_zero`: **True**
- `public_site_exports_changes_zero`: **True**
- `B4_03_original_worktree_changes_zero`: **True**
- `B4_03_sealed60_plus_seals62_changes_zero`: **True**
- `all_old_protected_group_changes_zero`: **True**
- `all_other_preserved_worktree_changes_zero`: **True**
- `all_additional_live_worktree_changes_zero`: **True**
- `primary_current_baseline_changes_zero`: **True**
- `native_movement_during_audit_zero`: **True**
- `unstable_streaming_reads_zero`: **True**
