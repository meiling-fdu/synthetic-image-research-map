# Historical test repair — 19 October 2026

## Validated result

All sixteen diagnosed failures are repaired without changing production code,
research records, historical decisions, immutable manifests or frontend assets.
The independent full run collected and passed **1,963 ordinary tests and 389
subtests**, with **zero failures, zero errors and zero skips**. The full suite
was run once. No test discovery, assertions, skips or warning filters were weakened.

The implementation starts from fetched `origin/main`
`3bcd95fd45b12b3d7a711232b0ba3ae687e8771d`, including the published B1F/T303
review. The [diagnostic report](test_failure_root_cause_2026_10_18.md) is included
byte for byte from the preceding investigation; its statements describe that
completed diagnostic phase, before these repairs.

## Three repairs

1. **R1: four stale frontend guards.**
   `tests/public_refinement_snapshot.py` now accepts only `web/index.html` from
   successor `c589f61b628b787251410964ed50a0fe696a4038`. It verifies the actual
   parent `d02b952489b10df438f79ed1b87aee4170ee8aa5`, both complete HTML hashes,
   and the exact single SRI substitution. Before:
   `ba43571ce429f16d422277597d7e51d95ca1f612d08ecfb02aba18bb8dbf3f58`;
   after: `f080d23a34c9863eb439b857eb2bf9032b80b8abb659631d6b49ac5de58510c1`.
   The original refinement fixture, original commit pin, prior successors,
   inventory and exact-byte protections remain intact. New positive/negative
   tests reject altered commit bytes, a different parent, unrelated edits to
   index/style/app, and an extra frontend file.
2. **R2: ten missing historical OS-fixture failures.** Three original payloads
   were recovered read-only from the primary checkout's frozen snapshots,
   verified against existing historical hashes, inspected for private paths and
   credentials, and archived losslessly under `tests/fixtures/`. Four declared
   historical destinations are restored; the HIGH and NORMAL paths share the
   same authenticated payload. The live Finder file is not used. Deterministic
   gzip archives have zero timestamps and no embedded filenames; all three
   together occupy 2,901 bytes. No OS payload is added to research/public data.
3. **R3: two implicit OpenAlex-cache dependencies.** All 99 declared responses
   are copied offline from existing committed Tier 1 snapshot files. Every full
   response hash and size is verified before use. Their 385,113,279 original
   bytes are not duplicated in Git, edited or fetched again.

`scripts/restore_historical_test_fixtures.py` is the single bootstrap entry point.
It delegates the original fourteen archived inputs to the unchanged existing
`literature51_reproducibility.materialize_export_inputs` helper, then restores
the 103 additional declared historical destinations. It preflights every source
and existing destination before writing, refuses differing destinations, uses
exclusive creation for new fixtures and verifies all 117 outputs. Repeated setup
creates zero files; `--check` is read-only. Negative tests cover all four restored
OS paths, representative response/legacy tampering, missing/corrupt archives and
responses, altered authorities/inventories, path escapes and destination links.
No test setup makes OpenAlex requests or regenerates canonical data.

[Setup instructions](testing.md) and `requirements-test.txt` provide the complete
workflow. Existing README bytes were retained to avoid altering unrelated frozen
history; the new testing document contains the setup command.

## Historical fixture authentication

| Original payload SHA-256 | Gzip archive SHA-256 | Expanded bytes |
| --- | --- | ---: |
| `1d7480faeebe24871c938c8c1751eea1883ace7f057716eccfff35ec167a3079` | `917a6300c0acc8bdcd864ea8ef2c017940699ec9217bf1cb52bd2bc9a249e2f9` | 16,388 |
| `6df64df87f90aed4dee71be480b2e5d710d5aa2ab24924f04eb409432b83b773` | `ab0f42facfcdab41c209f847cc2c33c5274fd0d9c5270e8bfa0e192988ba2cfa` | 6,148 |
| `a68cb7b62b51611eadfae68c198f05dd4990a76e7cbfc523c33c74c7b7a1c3eb` | `1ce5a1cca51dc522337b5f7011c15eacd741daa96f6eae1f987a582de7bb0871` | 6,148 |

The complete four-path OS and 99-path response inventory, including every source,
full SHA-256 and size, is in
`tests/fixtures/historical_test_fixture_manifest.json`. Its authorities remain:

- `data/processed/legacy_scope_exclusion_migration_2026_09/predecessor_666_snapshot.json`:
  `2999da7901044df18f64c29e68f58daedc6d5b9c23dad774ef79a7fe18d8e6ec`.
- `data/processed/workshop_venue_baseline.json`:
  `9e7a6f89e6a261a738b05e2e3de3d2d45cca76b0aaed4b5c3a0acc9e54f6575e`.

The inventory cannot redefine those authorities or omit required paths. Original
Tier 1/HIGH/NORMAL manifests and the fourteen-input preflight remain unchanged.

## Original sixteen: before and after

The before column is the recovered audit plus individual diagnostic reproductions
on the unchanged published baseline, including replay after its fourteen-input
bootstrap. All sixteen now pass in the targeted run and the independent full run.
R1 cases also need R2's fixtures to reach their later historical assertions.

| # | Exact test | Root cause | Before | After |
| --- | --- | --- | --- | --- |
| 1 | `tests/test_corpus_quality_batch_b_wave_b1b.py::test_manifest_preserves_original_source_provenance_and_current_source_hashes` | R3 | Fail | Pass |
| 2 | `tests/test_legacy_scope_cleanup_audit.py::test_predecessor_receipt_distinguishes_inventory_from_verified_bytes` | R2 | Fail | Pass |
| 3 | `tests/test_legacy_scope_cleanup_audit.py::test_all_audit_artifacts_reproduce_byte_for_byte_twice` | R2 | Fail | Pass |
| 4 | `tests/test_legacy_scope_exclusion_migration.py::test_predecessor_receipt_counts_actual_historical_file_reads` | R2 | Fail | Pass |
| 5 | `tests/test_legacy_scope_exclusion_migration.py::test_historical_receipts_reproduce_with_explicit_partial_scope` | R2 | Fail | Pass |
| 6 | `tests/test_legacy_scope_exclusion_migration.py::test_curated_and_historical_files_are_preserved` | R2 | Fail | Pass |
| 7 | `tests/test_legacy_scope_exclusion_migration.py::test_ledger_report_and_validation_are_generated_from_locked_sources` | R2 | Fail | Pass |
| 8 | `tests/test_systematic_literature_audit.py::test_frozen_pre_audit_files_are_byte_identical` | R2 | Fail | Pass |
| 9 | `tests/test_systematic_tier2_application.py::test_pre_application_baseline_includes_and_preserves_previous_policy_pass` | R1 | Fail | Pass |
| 10 | `tests/test_systematic_tier2_high_priority_evidence.py::test_authoritative_append_is_exact_and_preserves_existing_rows` | R2 | Fail | Pass |
| 11 | `tests/test_systematic_tier2_high_priority_evidence.py::test_report_reproduces_byte_for_byte` | R2 | Fail | Pass |
| 12 | `tests/test_systematic_tier2_normal_priority_evidence.py::test_authoritative_append_is_exact_and_preserves_existing_rows` | R1 | Fail | Pass |
| 13 | `tests/test_systematic_tier2_normal_priority_evidence.py::test_frozen_high_predecessor_remains_reproducible` | R2 | Fail | Pass |
| 14 | `tests/test_systematic_tier2_normal_priority_evidence.py::test_report_reproduces_byte_for_byte` | R1 | Fail | Pass |
| 15 | `tests/test_systematic_tier2_policy.py::test_pre_task_repository_files_are_byte_identical` | R1 | Fail | Pass |
| 16 | `tests/test_workshop_venue_audit.py::WorkshopArtifactTests::test_full_dataset_before_after_and_source_preservation` | R3 | Fail | Pass |

## Validation and independent environment

| Run | Ordinary tests collected/passed | Subtests passed | Failed/errors/skipped | Seconds |
| --- | ---: | ---: | --- | ---: |
| Original sixteen first | 16/16 | 0 | 0/0/0 | 46.570 |
| Related snapshot/baseline/export/fixture modules | 241/241 | 18 | 0/0/0 | 104.931 |
| Independent full suite, once | 1963/1963 | 389 | 0/0/0 | 412.884 |

The full JUnit suite reports 2,352 tests including its 389 subtests; there are
1,963 ordinary testcase elements. The earlier audit had 1,925 ordinary tests;
twelve intervening B1F tests and twenty-six new repair regressions account for
the increase. Pytest prints 412.90 seconds for the full run. Two existing
`PytestReturnNotNoneWarning` messages remain in the legacy successor payload/text
helper tests; they were not suppressed or changed.

Runtime: Python 3.14.7, pytest 9.1.1, pytest-subtests 0.15.0, Node v24.19.0.
The external environment contains only pytest, pytest-subtests and their normal
transitive dependencies. `PYTEST_ADDOPTS` and `PYTEST_PLUGINS` were unset.
`PYTHONPATH=.` and `PYTHONDONTWRITEBYTECODE=1` were set; the Node runtime was
prepended to PATH. Localhost permission was enabled for temporary HTTP tests.

The fresh independent checkout was created using a local shared-object clone
with `--no-checkout`, followed by `git read-tree` and `git checkout-index -a`
for staged tree `dd76935cb174a076266847ee9998974ce29b4f7a`. It had complete
Git history, no ignored/untracked files, no caches and no unstaged differences
before bootstrap. The candidate changes were indexed against the published base;
no repair commit was created before successful full validation. Only the 117
checksum-authenticated inputs were then materialized. Five of the existing
fourteen legacy inputs are nonignored untracked files; all are declared staged
NeurIPS fixtures, not changes for publication. All 117 still verify after testing,
and the indexed source files have no unstaged differences. The implementation
report itself is the only later addition to the validated source tree.

Curated database validation: zero errors, 294 pre-existing warnings. Public map:
zero errors/warnings, 1,410 records. Paper preview: zero errors, 62 pre-existing
warnings. `git diff --cached --check` passes. The warnings remain visible because
changing historical metadata or review state is outside this repair.

## Research and worktree preservation

Before and after tests, all **3,921 tracked files under `data/` and `web/`** have
exactly their baseline SHA-256 values. This covers canonical CSVs, historical
manifests/review decisions, frozen responses, generated public JSON and every
frontend asset. Full public JSON equality was also checked against the base Git
blobs. Paper records were keyed by the exporter's `identity_key`, relationships
by `public_relationship_key`; all fields, identity sets and per-paper map counts
match. Semantic payload SHA-256:
`5a3874bef87406cd5297546073faee6f6b361e1cb6ff4d1e4d57122aa503a3a1`.

| Public invariant | Before | After |
| --- | ---: | ---: |
| Papers | 674 | 674 |
| Formally published | 557 | 557 |
| Mapped papers | 613 | 613 |
| Unmapped papers | 61 | 61 |
| Unique paper–institution/location/author relationships | 1,410 | 1,410 |

The formal counter mirrors `web/app.js::isFormallyPublished` using
`publication_type` conference/journal/book. It is distinct from the exporter's
broader evidence predicate used during deduplication.

All thirteen pre-existing accessible worktrees keep their starting HEADs, Git
status and untracked hashes. The primary checkout's 304 excluded files, plus the
preceding diagnostic report, remain unchanged (305 verified files). The stale
inaccessible worktree registration was left alone. The B1F owning worktree stays
clean at its published `3bcd95f` commit; no concurrent work was modified.

## Local evidence and exact commands

The local evidence directory is
`/private/tmp/sirm-historical-repair-20261019/`. Each run has separate stdout,
stderr, JUnit XML and a command JSON; the full run additionally records cwd, PATH,
environment overrides, tree identity and exit status. Setup/check receipts record
all 117 hashes. `integrity-repair.json` and
`integrity-independent-after-full.json` preserve the byte and semantic comparisons
and owning-worktree audit. Scratch evidence is not required for reproducing tests.

| JUnit file | SHA-256 |
| --- | --- |
| `original-16.xml` | `5c050d3d174efef051ecb96183256251f14ad2447f92a958904e113a920233ea` |
| `focused.xml` | `076b76d64a4b4f529c11d3345baf76770da9c327bb92602ecce308605ada0404` |
| `full.xml` | `5c3dc041c99f6e10b1eeb83e9ddd648cb7f9799dcb76a3c73a2ab2e841671102` |

The exact pytest argument vectors follow; stdout/stderr were redirected to the
evidence directory by the external runner. Original/focused cwd was `repair/`;
full-suite cwd was `independent/` under that directory.

```sh
/private/tmp/sirm-sync-audit-20261018/test-env/bin/python -m pytest -q tests/test_corpus_quality_batch_b_wave_b1b.py::test_manifest_preserves_original_source_provenance_and_current_source_hashes tests/test_legacy_scope_cleanup_audit.py::test_predecessor_receipt_distinguishes_inventory_from_verified_bytes tests/test_legacy_scope_cleanup_audit.py::test_all_audit_artifacts_reproduce_byte_for_byte_twice tests/test_legacy_scope_exclusion_migration.py::test_predecessor_receipt_counts_actual_historical_file_reads tests/test_legacy_scope_exclusion_migration.py::test_historical_receipts_reproduce_with_explicit_partial_scope tests/test_legacy_scope_exclusion_migration.py::test_curated_and_historical_files_are_preserved tests/test_legacy_scope_exclusion_migration.py::test_ledger_report_and_validation_are_generated_from_locked_sources tests/test_systematic_literature_audit.py::test_frozen_pre_audit_files_are_byte_identical tests/test_systematic_tier2_application.py::test_pre_application_baseline_includes_and_preserves_previous_policy_pass tests/test_systematic_tier2_high_priority_evidence.py::test_authoritative_append_is_exact_and_preserves_existing_rows tests/test_systematic_tier2_high_priority_evidence.py::test_report_reproduces_byte_for_byte tests/test_systematic_tier2_normal_priority_evidence.py::test_authoritative_append_is_exact_and_preserves_existing_rows tests/test_systematic_tier2_normal_priority_evidence.py::test_frozen_high_predecessor_remains_reproducible tests/test_systematic_tier2_normal_priority_evidence.py::test_report_reproduces_byte_for_byte tests/test_systematic_tier2_policy.py::test_pre_task_repository_files_are_byte_identical tests/test_workshop_venue_audit.py::WorkshopArtifactTests::test_full_dataset_before_after_and_source_preservation --junitxml=/private/tmp/sirm-historical-repair-20261019/original-16.xml --basetemp=/private/tmp/sirm-historical-repair-20261019/pytest-original-16
```

```sh
/private/tmp/sirm-sync-audit-20261018/test-env/bin/python -m pytest -q tests/test_corpus_quality_batch_b_wave_b1b.py tests/test_frontend_leaflet_assets.py tests/test_historical_integrity_successors.py tests/test_historical_test_fixtures.py tests/test_legacy_scope_cleanup_audit.py tests/test_legacy_scope_exclusion_migration.py tests/test_literature51_reproducibility.py tests/test_public_export_metadata.py tests/test_public_preview_deduplication.py tests/test_public_refinement_successors.py tests/test_repository_baseline.py tests/test_systematic_literature_audit.py tests/test_systematic_tier2_application.py tests/test_systematic_tier2_high_priority_evidence.py tests/test_systematic_tier2_normal_priority_evidence.py tests/test_systematic_tier2_policy.py tests/test_workshop_venue_audit.py --junitxml=/private/tmp/sirm-historical-repair-20261019/focused.xml --basetemp=/private/tmp/sirm-historical-repair-20261019/pytest-focused
```

```sh
/private/tmp/sirm-sync-audit-20261018/test-env/bin/python -m pytest -q tests --junitxml=/private/tmp/sirm-historical-repair-20261019/full.xml --basetemp=/private/tmp/sirm-historical-repair-20261019/pytest-full
```

Each disposable checkout was bootstrapped with:

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/sirm-sync-audit-20261018/test-env/bin/python scripts/restore_historical_test_fixtures.py
PYTHONDONTWRITEBYTECODE=1 /private/tmp/sirm-sync-audit-20261018/test-env/bin/python scripts/restore_historical_test_fixtures.py --check
```

Both validation CLIs were run separately with the same external Python:

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/sirm-sync-audit-20261018/test-env/bin/python scripts/validate_curated_database.py
PYTHONDONTWRITEBYTECODE=1 /private/tmp/sirm-sync-audit-20261018/test-env/bin/python scripts/validate_public_preview.py
```

The machine-specific executable paths above record this run only. The portable
setup in `docs/testing.md` uses a newly created external environment and `node`
on PATH. Complete Git history and the explicit fixture bootstrap are required;
tests do not require a developer's ignored/private cache or live OpenAlex access.
