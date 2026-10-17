# Literature51 local commit validation — 17 October 2026

Completed disposition: **39 imported + 12 held = 51**. Public bibliography **678**, formally published **561**, map relationships **1,421**, pending taxonomy reviews **14**. No new research, source retrieval, paper import or metadata migration occurred during finalization.

## Independent index-only results

- Focused tests: **151 passed, 12 subtests passed, 0 failed, 0 errors, 0 skipped**. This includes all changed historical Batch A/C test files and the new negative reproduction-boundary tests.
- Unchanged curated validator: **0 errors, 0 duplicates**, 291 existing affiliation/metadata warnings.
- Unchanged public validator: map **0 errors / 0 warnings**; bibliography **0 errors / 62 warnings**.
- Two canonical exporter runs reproduced **both public JSON files byte-for-byte**, including timestamps. Export outputs and location-review side products stayed in temporary directories.
- Every validation input came from the Git index/tree or a checksum-verified lossless fixture archive. All 130 pre-existing untracked files and all 172 excluded intermediates were absent. The five untracked files created within the disposable snapshot were explicitly declared historical fixture outputs restored from committed archives, with no unexpected input files.
- Disposable Git metadata retained the original object history for tests that use `git show`; the real repository’s HEAD/branches were untouched during testing.
- All paper identities, DOI values and arXiv IDs are unique. Every import is present exactly once, all twelve HOLDs remain absent, historical reviews/exclusions are preserved, and all 1,421 map objects and their order match the predecessor.
- 676/677 previous public objects are unchanged; E17 changes only its approved taxonomy review status/reasons. All 38 original imported bibliographic rows and the new B03 preprint remain intact.

## Manifest corrections

The original 126-path proposal could not reproduce independently. It referenced unrelated local untracked files, omitted ignored inputs needed by unchanged validators/exporters, and omitted hash-protected fixtures needed by historical tests. Saved JUnit failure transcripts also contain trailing whitespace.

The corrected manifest contains **147 explicit paths** in [proposed_staging.txt](../data/processed/literature51_2026_10_16/followup/proposed_staging.txt):

1. Replace the two plain full-suite JUnit files with lossless `.xml.gz` archives. Their decompressed bytes exactly match the original saved receipts; the original XML files remain untouched locally. No failure text or assertion is rewritten.
2. Add fourteen lossless legacy input archives: four canonical export/metadata inputs, plus ten previously untracked historical protected fixtures. Each is public corpus metadata, an audit table or test/validation output. Historical fixtures additionally match the immutable October 3 protected-input hashes. None is one of the 130 unrelated untracked files.
3. Add two reproduction helpers, eight negative tests, a preflight manifest and three final audit artifacts. Existing local files must match their hashes; materialization never overwrites differing content.
4. Remove one surplus terminal blank line from the new, uncommitted integration Markdown report. Its text and research results are unchanged.
5. The original workspace continues to require all 130 local files and exact hashes. A clean checkout instead requires the exact approved tracked inventory and absence of excluded payloads. No canonical validator, corpus assertion, taxonomy policy, historical review receipt or frontend source was changed.

## Test provenance

The focused tests and canonical export checks ran against index tree `f2cb86c30a92fb081ec99f182ab859e19ba4f578`. The final additions are validation receipts/reporting and the final path list; the verifier also explicitly rejects undeclared untracked inputs. No production data or import logic changes after those successful tests. The final index is rechecked independently before the local commit.

Full suite: **not rerun**. Its saved **1,701 passed / 4 failed** checkpoint remains intact. The four final failures have the exact pre-existing baseline names and messages:

- `test_systematic_tier2_application::test_pre_application_baseline_includes_and_preserves_previous_policy_pass` — AssertionError: Public refinement differs from its reviewed snapshot
- `test_systematic_tier2_normal_priority_evidence::test_authoritative_append_is_exact_and_preserves_existing_rows` — AssertionError: Public refinement differs from its reviewed snapshot
- `test_systematic_tier2_normal_priority_evidence::test_report_reproduces_byte_for_byte` — AssertionError: Public refinement differs from its reviewed snapshot
- `test_systematic_tier2_policy::test_pre_task_repository_files_are_byte_identical` — AssertionError: Public refinement differs from its reviewed snapshot

## Security, history and local files

The staged content is checked after decompressing all gzip files. The 172 local-only intermediates, 34 non-evidence payloads, 14 broad retrieval logs and 130 unrelated untracked files remain outside the commit. Full paper PDFs/manuscript HTML, credentials, authenticated session payloads and bot-challenge tokens are excluded. Compressed fixture tables contain existing public bibliographic/affiliation metadata, not private datasets or experiments.

All 39 imports, twelve explicit HOLDs and fourteen pending taxonomy reviews remain reviewable. No institution, mapping, location, exclusion, source cache or manual correction is changed. Canonical validators, existing historical receipts and frontend snapshots remain unchanged.

After the commit, the expected working-tree remainder is **304 untracked files**: 130 pre-existing files, 172 excluded intermediates and the two uncompressed JUnit originals. The index and tracked working tree should be clean. No push is authorized or performed.

Validation receipt: [staged_validation.json](../data/processed/literature51_2026_10_16/followup/staged_validation.json). Focused JUnit: [staged_focused.xml](../data/processed/literature51_2026_10_16/followup/staged_focused.xml). Earlier reports remain addition-time checkpoints; this report records the final commit preparation.
