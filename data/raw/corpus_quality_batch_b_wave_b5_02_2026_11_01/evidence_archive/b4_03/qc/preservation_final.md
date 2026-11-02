# B4-03 independent final preservation audit

Status: **PASS_WITH_PRESERVED_PREEXISTING_UNSEALED_B3_EXTRA**.

Captured 2026-11-01T08:42:10.284155+00:00 with 65,260 streaming hashes over 20,086,722,569 bytes. The audit wrote only external deliverables.

Native HEAD remains `d109c70f6994906ec3d9197baad51cf9d8e51f7c`. Exactly 3 approved CSVs differ from the 4,658-file baseline; the complete native tree matches the manifest after-hashes. No staging, new untracked or ignored files.

Observed 35 exact source-cell edits and 11 exact appended decision rows. Existing decision bytes, headers and source row order are preserved.

Protected bytes rehashed: B3 sealed123 plus seals and its one previously observed unsealed receipt; accepted B5 sealed281 plus receipt; primary protected128; frozen49 across six physical roots and native logical streams; B4-01 and B4-02 pending8 each; C13, separate39, B2, and immutable evidence/CI632.

All seven prior source worktrees, five additional worktrees, and the primary checkout are fully recaptured by tracked/untracked/ignored inventory and Git metadata. External differences are reported separately and never reset or attributed without evidence.

All zero-change flags true: **True**.

Failures: none.

Observed external differences: 0.

## Native Git status

```text
 M data/curated/paper_taxonomy.csv
 M data/curated/papers.csv
 M data/curated/review_decisions.csv
```

## Approved final hashes

- `data/curated/papers.csv`: `e38c269bb4870ef03914f993a247f809cdbb5c0daf06ae01efa526c762b15d87`
- `data/curated/paper_taxonomy.csv`: `98026dec50ed5b81b60b4792da623e89468da5ee3da96ef7a4a9fc5910da05d3`
- `data/curated/review_decisions.csv`: `9d2a5cd8190634b8bf85afb969549b0a62652e50697c5b129d64970fd64a44ea`

## Zero-change flags

- `unsupported_native_tracked_changes_zero`: **True**
- `staged_changes_zero`: **True**
- `new_native_files_zero`: **True**
- `manual_data_changes_zero`: **True**
- `raw_processed_data_changes_zero`: **True**
- `public_site_and_exports_changes_zero`: **True**
- `code_test_documentation_changes_zero`: **True**
- `B3_sealed123_changes_zero`: **True**
- `B3_seals_and_known_unsealed_extra_changes_zero`: **True**
- `accepted_B5_sealed281_and_receipt_changes_zero`: **True**
- `B4_old_pending8_each_changes_zero`: **True**
- `primary_protected128_changes_zero`: **True**
- `frozen49_physical_logical_and_presence_changes_zero`: **True**
- `C13_receipt_changes_zero`: **True**
- `separate39_receipt_changes_zero`: **True**
- `B2_planning_changes_zero`: **True**
- `immutable_evidence_CI632_changes_zero`: **True**
- `all_old_source_worktree_changes_zero`: **True**
- `all_additional_live_worktree_changes_zero`: **True**
- `primary_concurrent_observation_changes_zero`: **True**
