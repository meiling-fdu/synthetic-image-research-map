# Test failure root-cause investigation — 18 October 2026

## Outcome and scope

**Three confirmed root causes explain all 16 original failures: four stale frontend-successor checks, ten missing historical OS-metadata fixtures, and two ignored OpenAlex-cache dependencies. None of these failures demonstrates a current research-data or public-website regression.** A separate, confirmed setup omission explains 76 additional failures/errors in a pristine checkout.

The investigation is pinned to `990c8221728a44b6ab78cfff5159612edb0983a7`, the fetched `origin/main` when the diagnostic checkout was created. The primary Desktop checkout remains on its independent historical branch; it was not used as the test subject. Source locations below refer to the pinned diagnostic checkout, not that older branch.

This is a diagnostic result, not an implemented repair. Production code, test assertions, canonical data, exports, historical evidence and immutable manifests were not edited. No commits or pushes were made. The only project addition is this report. The 304 excluded primary-checkout files retain their starting SHA-256 values.

## Evidence and execution history

The recovered synchronization audit is `/private/tmp/sirm-sync-audit-20261018/`. New diagnostic evidence is `/private/tmp/sirm-test-failures-20261018/`. Both original full-suite JUnit and the original failure replay were recovered. Complete original and new tracebacks remain in the XML/JSON/log files; the table below identifies the first failing project operation rather than replacing those tracebacks with a summary.

| Run | Result | Evidence |
| --- | --- | --- |
| Previous audit, `990c822`, with 14 archived inputs restored | 1,909 passed; 16 failed; 389 subtests passed; no errors/skips | Previous `final-full.xml`, `final-full.log`, `full-test-summary.json` |
| Previous unchanged-remote replay, `cc1e1b3` | The same 16 failures, with identical normalized messages | Previous `remote-baseline-failures.xml`, `baseline-comparison.json` |
| Fresh diagnostic checkout, before fixture bootstrap | 1,833 passed; 28 failed; 64 setup errors; 389 subtests passed; no skips; 298.86 s | `clean-full.xml`, `clean-full.stdout.log`, `clean-full.stderr.log` |
| Each original failure in a separate pytest process | 16/16 reproduced; all messages match the audit after normalizing checkout paths | `individual/01.xml` through `16.xml`, corresponding stdout/stderr, `individual-results.json`, `individual-comparison.json` |
| Original 16 after restoring the existing 14 archived inputs | 16 failed; all 16 messages still match; 21.81 s | `restored-original-16.xml`, stdout/stderr, `restored-original-16-comparison.json` |
| Only the 76 additional pristine-checkout failures/errors, after bootstrap | **76 passed**, 67.81 s | `restored-additional-76.xml`, stdout/stderr |

JUnit counts the 389 subtests in its 2,314 total entries; pytest's ordinary case total is 1,925. The pristine run therefore has 92 failing/error cases: the original 16 plus 76 setup-dependent cases. No full suite was repeated after resumption. The post-bootstrap targeted results do not constitute a new full-suite pass.

The earlier attempted combined bootstrap/retest command was not executed: automatic approval review hit a usage limit. This was an execution-review interruption, not a test failure. Resumption used small separate commands and the existing checkpoints.

### Environment comparison

- Full local Git history was available; `git rev-parse --is-shallow-repository` returned `false`.
- Python 3.14.7; pytest 9.1.1; pytest-subtests 0.15.0; Node v24.19.0. The external pytest environment was reused, with no repository dependency changes.
- The repository has mixed pytest functions and unittest classes. The preserved literature receipts use pytest; plain unittest discovery cannot execute the complete suite. README does not provide a single complete test-bootstrap command.
- The original audit explicitly materialized 14 inputs using the committed `scripts.literature51_reproducibility.materialize_export_inputs()` helper. A pristine worktree does not contain those ignored files. After resumption, that unchanged helper restored only those 14 hash-verified files in the disposable checkout. All 14 match the earlier audit's copies byte for byte (`bootstrap.json`, `environment-fixture-comparison.json`). Existing differing files would cause the helper to fail, not be overwritten.
- Tests requiring temporary localhost servers need localhost permission. The earlier synchronization audit's partial unittest/environment errors are separate from the authoritative pytest failures; they were not counted among these 16.
- Four browser smoke scripts contain machine-specific Playwright paths. Chrome 155.0.8059.84 and the bundled runtime are installed here. Those scripts are portability concerns, but none is the source of these 16 Python failures. This investigation did not repeat browser smoke tests.
- Absolute paths printed by these 16 Python failures are derived from `__file__` and the selected checkout root. They are not evidence of hardcoded Desktop paths in the failing readers.

## Complete 16-case root-cause matrix

`R1`, `R2` and `R3` identify the shared causes detailed below. Every row failed on unchanged `cc1e1b3` in the recovered audit, individually on `990c822`, and again on `990c822` after the 14-input bootstrap. “Remote: yes” means reproduction on the unchanged remote commit, not execution inside GitHub Actions.

Expected repair files:

- **F1:** `tests/public_refinement_snapshot.py` and a new focused `tests/test_public_refinement_successors.py`. No frontend asset or historical snapshot edit.
- **F2:** three new lossless fixture archives under `tests/fixtures/historical_os_metadata/`; a new `tests/fixtures/historical_test_fixture_manifest.json` declaring the four paths and their existing hashes; a proposed `scripts/restore_historical_test_fixtures.py`, its negative tests in `tests/test_historical_test_fixtures.py`, and a README setup command. Keep all existing historical manifests and assertions byte-identical.
- **F3:** the same proposed `scripts/restore_historical_test_fixtures.py` and declared fixture manifest, negative tests and README setup command, extended with the exact 99 root-cache paths and existing committed Tier 1 sources. No new API responses, raw archives or assertion changes. The new bootstrap can delegate the original fourteen-input restoration to the unchanged existing helper.

| # | Exact test | Error and first failing project operation | Cause / classification | Unchanged remote | Related history | Minimal correction / files | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `tests/test_corpus_quality_batch_b_wave_b1b.py::test_manifest_preserves_original_source_provenance_and_current_source_hashes` | `FileNotFoundError` for `data/raw/openalex/20260619T211726Z_001_ai-generated-image-detection.json`; direct `(ROOT / path).read_bytes()` at line 453 fails before its hash assertion. | R3; missing historical fixture / ignored-cache environment dependency. | Yes | B1B `65e9422764c34eaad1d151fff2895e6c7503835f`; later endpoint reader updates preserve this direct-read special case. | F3; restore the exact response from the committed Tier 1 copy and retain the asserted digest. | Low |
| 2 | `tests/test_legacy_scope_cleanup_audit.py::test_predecessor_receipt_distinguishes_inventory_from_verified_bytes` | `historical artifacts missing: [...]`; line 168 calls `verify_baseline()`, which delegates to `verify_predecessor()` and raises at `scripts/frozen_predecessor_666.py:184`. | R2; four missing OS-metadata fixtures, not an invalid reconstructed corpus. | Yes | Frozen 666 predecessor in `c160a7dd6b8b403ed6e268108ee2fe4ab6fb3311`. | F2; restore all four exact archived paths. Keep inventory/byte-verification accounting intact. | Low; archive payload review required |
| 3 | `tests/test_legacy_scope_cleanup_audit.py::test_all_audit_artifacts_reproduce_byte_for_byte_twice` | Same missing-artifacts exception; line 189 reaches `verify_predecessor():184` before reproduction comparisons. | R2; same missing fixtures. | Yes | Same frozen 666 predecessor. | F2; retain both reproduction rounds and exact generated-artifact comparisons. | Low; archive payload review required |
| 4 | `tests/test_legacy_scope_exclusion_migration.py::test_predecessor_receipt_counts_actual_historical_file_reads` | Same missing-artifacts exception from `verify_predecessor():184`, called at test line 71. Its observed-read-set assertion is not reached. | R2; same missing fixtures. | Yes | Same frozen 666 predecessor and retained actual-file-read contract. | F2; materialize the original files so every expected historical file is still read and hashed. | Low; archive payload review required |
| 5 | `tests/test_legacy_scope_exclusion_migration.py::test_historical_receipts_reproduce_with_explicit_partial_scope` | Same exception through `historical_verification_receipts():225` → `verify_predecessor():184`, called at test line 82. | R2; same missing fixtures. | Yes | Same predecessor and partial-byte-verification receipts. | F2; preserve receipt fields/counts and historical claims. | Low; archive payload review required |
| 6 | `tests/test_legacy_scope_exclusion_migration.py::test_curated_and_historical_files_are_preserved` | Line 241: `assert result["historical_artifacts_changed"] == []`; the returned list contains exactly the four absent `.DS_Store` paths. | R2; absence is reported as “changed” by `preservation_audit()`. | Yes | `scripts/legacy_scope_exclusion_migration.py:1029`; frozen predecessor `c160a7d`. | F2; preserve the exact empty-list assertion. | Low; archive payload review required |
| 7 | `tests/test_legacy_scope_exclusion_migration.py::test_ledger_report_and_validation_are_generated_from_locked_sources` | Line 257: stored validation JSON differs from computed validation. The sole differing top-level field is `preservation`; only its four-path `historical_artifacts_changed` list differs. | R2; derived receipt mismatch caused by missing fixtures. | Yes | Same migration; `legacy-validation-diff.json` confirms the precise difference. | F2; do not rewrite the stored validation receipt. | Low; archive payload review required |
| 8 | `tests/test_systematic_literature_audit.py::test_frozen_pre_audit_files_are_byte_identical` | `FileNotFoundError` for `data/processed/systematic_tier1_2026_09/baseline/data/.DS_Store`; hashing comprehension at line 107 cannot finish. | R2; historical directory snapshot omitted an ignored OS file. | Yes | Tier 1 snapshot `f06a59cee24b90faba685be94fe9c71ae1cbce26`. | F2; keep the 670-entry baseline and byte-equality assertion unchanged. | Low; archive payload review required |
| 9 | `tests/test_systematic_tier2_application.py::test_pre_application_baseline_includes_and_preserves_previous_policy_pass` | Line 174 enters the historical guard; `tests/public_refinement_snapshot.py:101` asserts `actual == expected` and raises `Public refinement differs from its reviewed snapshot`. | R1; outdated exact successor expectation. | Yes | Approved desktop `ef0d93f`; omitted SRI successor `c589f61`. | F1. R2 also blocks the subsequent predecessor verification, so repair/validate together. | Low |
| 10 | `tests/test_systematic_tier2_high_priority_evidence.py::test_authoritative_append_is_exact_and_preserves_existing_rows` | `FileNotFoundError` for `<checkout>/web/.DS_Store`; test line 89 calls `diff_audit()`, whose line 388 reads `frozen_high_path(relative)`. | R2; missing NORMAL baseline file triggers fallback to a missing live OS file. | Yes | HIGH/NORMAL immutable successor layers; NORMAL manifest history includes `8105eb9` and `2c3230a`. | F2; restore the NORMAL archived path, allowing the existing frozen-path resolver to select it. Do not fabricate a current OS file. | Low; archive payload review required |
| 11 | `tests/test_systematic_tier2_high_priority_evidence.py::test_report_reproduces_byte_for_byte` | Same `web/.DS_Store` error via report `diff_audit():388`, called at test line 161. | R2; same frozen-path fallback. | Yes | Same HIGH/NORMAL layers. | F2; preserve the exact report comparison. | Low; archive payload review required |
| 12 | `tests/test_systematic_tier2_normal_priority_evidence.py::test_authoritative_append_is_exact_and_preserves_existing_rows` | Line 105 calls `historical_normal_priority_diff()`; the guard fails at `public_refinement_snapshot.py:101` with the public-refinement message. | R1; stale successor expectation. | Yes | `c589f61`, after guard's last registered `ef0d93f`. | F1 + F2: the next step reads the missing NORMAL baseline `.DS_Store`. | Low |
| 13 | `tests/test_systematic_tier2_normal_priority_evidence.py::test_frozen_high_predecessor_remains_reproducible` | `FileNotFoundError` for `<checkout>/web/.DS_Store`; `frozen_high_diff_audit()` at test line 185 reaches HIGH report line 388. | R2; same missing NORMAL snapshot and fallback. | Yes | Same HIGH/NORMAL layers. | F2; retain the frozen 648/657-paper counts and original report checks. | Low; archive payload review required |
| 14 | `tests/test_systematic_tier2_normal_priority_evidence.py::test_report_reproduces_byte_for_byte` | Line 196 calls `historical_normal_priority_diff()`; public-refinement guard fails at line 101. | R1; stale successor expectation. | Yes | `c589f61`, after `ef0d93f`. | F1 + F2; preserve the stored report and historical comparison. | Low |
| 15 | `tests/test_systematic_tier2_policy.py::test_pre_task_repository_files_are_byte_identical` | Line 92 enters `assert_historical_integrity_with_public_refinement()`; its frontend guard fails at line 101. | R1; stale successor expectation. | Yes | `c589f61`, after `ef0d93f`. | F1. R2 blocks later predecessor verification; validate both fixes together. | Low |
| 16 | `tests/test_workshop_venue_audit.py::WorkshopArtifactTests::test_full_dataset_before_after_and_source_preservation` | Line 193: the historical raw hash dictionary differs from `source_hashes()` projected onto that dictionary; 99 required raw paths return `None`. | R3; missing ignored raw-cache paths, although exact committed copies exist. | Yes | Workshop baseline `da0d57e959aea8b87e86d8efafdb756918017187`; OS-only exclusion precedent in `docs/baseline_test_cleanup.md`. | F3; restore all 99 declared paths and retain all 258 meaningful raw-source hash comparisons. | Low |

## R1 — Published Leaflet SRI successor is absent from the historical guard

**Confirmed; 4 original failures.** `PUBLISHED_FRONTEND_SUCCESSORS` ends at `ef0d93fa2658c532fff54df2bfaf21fec65f5b57`. The read-only reconstruction of the guard's expected/actual dictionaries finds exactly one mismatching path: `web/index.html`.

| Bytes | SHA-256 |
| --- | --- |
| Guard's registered desktop successor; also `c589f61^:web/index.html` | `ba43571ce429f16d422277597d7e51d95ca1f612d08ecfb02aba18bb8dbf3f58` |
| Current `990c822` index; exactly `c589f61:web/index.html` | `f080d23a34c9863eb439b857eb2bf9032b80b8abb659631d6b49ac5de58510c1` |

`c589f61b628b787251410964ed50a0fe696a4038` changes only the Leaflet stylesheet SRI in that HTML file and adds `tests/test_frontend_leaflet_assets.py`. Its HTML diff changes the invalid hash to `sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=`. Both its parent index and the registered desktop index have the first digest above. This is precise evidence for the current failure, not a blanket assumption that every frontend edit is approved.

Proposed minimal addition to `PUBLISHED_FRONTEND_SUCCESSORS`, after the desktop entry:

```python
("c589f61b628b787251410964ed50a0fe696a4038", (
    "web/index.html",
)),
```

Leave `REFINEMENT_COMMIT`, `tests/fixtures/public_website_refinement_2026_10_01.json`, branding receipts and all earlier successor entries unchanged. Keep the immutable-fixture-to-originating-commit checks, exact current-byte comparison and exact frontend inventory check. Add negative regression coverage rejecting an unrelated index edit and any extra changed path. Do not read `HEAD` or approve hashes from the current worktree as expected values.

`proposed-successor-analysis.json` records that substituting only the fixed-commit digest removes the sole dictionary mismatch. This is a read-only analysis; the guard itself was not changed or rerun as if repaired. Earlier literature receipts also recorded four failures with this generic message before `c589f61` existed. Their historical failure causes must not be retroactively relabeled; the single-path diagnosis here applies to `990c822`.

## R2 — Four ignored historical OS files are required but absent

**Confirmed; 10 original failures, plus a later dependency of the four R1 cases.** The legacy predecessor manifest protects 1,014 historical artifacts, including four `.DS_Store` files. The files are ignored by `.gitignore:222`; their blobs are absent from the local Git object database. Their exact frozen copies remain in the primary checkout and match the recorded digests.

| Required historical path | SHA-256 | Bytes |
| --- | --- | ---: |
| `data/processed/systematic_tier1_2026_09/baseline/data/.DS_Store` | `1d7480faeebe24871c938c8c1751eea1883ace7f057716eccfff35ec167a3079` | 16,388 |
| `data/processed/systematic_tier1_2026_09/baseline/web/.DS_Store` | `6df64df87f90aed4dee71be480b2e5d710d5aa2ab24924f04eb409432b83b773` | 6,148 |
| `data/processed/systematic_tier2_high_priority_evidence_review_2026_09/baseline/web/.DS_Store` | `a68cb7b62b51611eadfae68c198f05dd4990a76e7cbfc523c33c74c7b7a1c3eb` | 6,148 |
| `data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/baseline/web/.DS_Store` | `a68cb7b62b51611eadfae68c198f05dd4990a76e7cbfc523c33c74c7b7a1c3eb` | 6,148 |

There are only **three distinct payloads**. The current primary `web/.DS_Store` has a different digest, `9a498d8cb9a99e214837c23bec8ef45eb32323eb0f38e21064bd2b666e6b91fd`, and is not a substitute. `frozen_high_path()` falls back to the live path when its NORMAL snapshot copy is absent; restoring the correct NORMAL snapshot avoids that fallback.

The legacy validation mismatch is entirely attributable to these files: its ten protected authoritative files, unrelated public records and unrelated map records all remain unchanged. Only `preservation.historical_artifacts_changed` differs (`legacy-validation-diff.json`). The Tier 2 policy/application baseline manifests do not contain live `.DS_Store` entries; no conflicting live OS metadata needs to be created to satisfy those guards.

The narrowest repair that preserves every existing assertion is to archive the three original payloads losslessly, record a four-path restoration map tied to the existing immutable digests, and restore them only as declared historical test inputs in a disposable checkout. Verify archive and decompressed hashes; fail on missing/corrupted archives or differing destination bytes. Inspect the opaque OS payloads before including them as fixtures. Do not copy arbitrary current Finder metadata or regenerate any baseline/report.

The September cleanup correctly excluded OS metadata from meaningful raw-source checks. That precedent explains why these files are incidental, but applying a new exclusion here would change several historical file-read/count/receipt contracts. It is unnecessary for the proposed exact-fixture repair and is not recommended as a shortcut. No historical manifest, 670-entry baseline, 1,014-artifact count or partial-verification receipt needs changing.

## R3 — Readers require ignored root caches despite exact committed snapshots

**Confirmed; 2 original failures.** The workshop baseline contains 258 meaningful raw-source hashes after the existing OS-metadata policy is applied. The clean checkout lacks 99 root `data/raw/openalex/*.json` paths. All 99 exist under the committed `data/processed/systematic_tier1_2026_09/baseline/data/raw/openalex/` directory, with exactly the same hashes as the workshop baseline. All 99 also match the preserved local raw copies. Total response bytes are 385,113,279; duplicating this data in new Git archives is unnecessary.

The B1B case's single response is part of those same 99 files. Its required SHA-256 is `8947d198999a1f066c344640747d472f2e99d722d0980a2570901f62430bbdbd`, matching both B1B's immutable manifest and its committed Tier 1 copy. This is shared fixture-path availability, not a second scientific-provenance defect.

Proposed minimal repair: a declared test-bootstrap mapping from each of those 99 root paths to its existing committed frozen copy, checked against the unchanged historical expected hash before materialization. Use only the explicit manifest entries; never a broad “accept current hashes” rule. Fail on changed existing raw bytes rather than replacing them. Retain the B1B hash assertion and every meaningful workshop raw-source comparison. No API query, new download, replacement metadata or duplicate raw dataset is needed.

`openalex-fixture-inventory.json` enumerates all 258 hashes; `committed-cache-resolution.json` records all 99 exact committed matches and zero unresolved files. Production `source_hashes()` need not silently invent present-day sources from a historical directory: explicit fixture setup can satisfy the unchanged tests.

## Separate setup cause — The 14 archived inputs were never bootstrapped

This is a **fourth confirmed cause across the entire pristine-checkout investigation**, but not one of the three causes of the original 16. It accounts for all 76 additional cases: 64 setup errors and 12 failed cases.

The 64 errors share one chain: `scripts.corpus_quality_history.predecessor_root()` needs ignored historical protected inputs, cannot find their local files, then attempts `git show ecfde6b1fc459a748e34114634fbf21cb9286f65:data/processed/neurips_2026_targeted_gap_fill_2026_10/staged/institutions.csv`. The commit exists, but this ignored input was not a tracked path in that commit. More Git history or an external fetch would not restore that file. The existing committed lossless archive does.

The other 12 cases need missing candidate paper/affiliation CSVs, the local candidate map JSON, or frozen NeurIPS validation logs. The existing reproducibility helper supplies all required files from fourteen committed archives. These include four canonical/export metadata inputs and ten historical protected inputs. The latter must also match the protected/frozen hashes in the October 3 baseline.

After restoring exactly these fourteen files, the 76 selected cases passed. The original 16 still failed unchanged. This directly establishes the difference between the prior audit environment and the pristine worktree; it is not inferred from passing totals.

Future setup documentation should state this precondition and use the existing helper explicitly. A small unified historical-test bootstrap can call it, add R2/R3's narrow declared mappings, verify all digests and refuse overwrites. It should run in a disposable checkout and not refresh the corpus or modify a maintainer's manual data. No requirement to update canonical datasets or legacy assertions follows from these setup errors.

## Research integrity and diagnostic side effects

Fresh validators after restoring the existing bootstrap inputs report:

- Curated database: **0 errors, 0 duplicate candidates**, 294 existing warnings.
- Public map: **0 errors, 0 warnings**.
- Public bibliography: **0 errors**, 62 existing unresolved-affiliation warnings.

Read-only counts remain **674 public, 557 formal, 613 mapped, 61 unmapped, 1,410 rows and 1,410 unique paper–institution relationships**. Publication types are 400 conference, 156 journal, 117 preprint and 1 book. Task totals remain 621 detection, 84 source attribution and 45 localization; labels overlap. Classifications, mappings, institutions, evidence and exports were not changed or regenerated.

Before testing, all 4,455 tracked diagnostic-checkout files were hashed. The pristine full run changed none; it created only pytest/bytecode caches and one local export lock. The existing helper subsequently created fourteen declared ignored fixture inputs in this disposable checkout. New test outputs, inventories and tracebacks were written outside project trees. Final preservation evidence is `final-preservation.json`; it checks tracked hashes, the 304 original excluded-file hashes and existing worktree states. No branch was advanced and no existing worktree was switched, reset, removed or cleaned.

The final cross-worktree observation found concurrent work in `/Users/meilinger/.codex/worktrees/batch-c-wave5c-evidence/synthetic-image-research-map`: four modified paths (`data/curated/review_decisions.csv`, its B1F manifest and report, and `tests/test_corpus_quality_batch_b_wave_b1e.py`) plus untracked `tests/test_corpus_quality_batch_b_wave_b1f.py`. These differ from the investigation's earlier status checkpoint and were not written by this investigation. They remain in that worktree and are outside the pinned diagnostic subject. All existing worktree HEADs remain unchanged; the primary checkout has only this new report in addition to its original 304 excluded files.

## Exact reproduction commands and evidence files

These are the commands used; select a fresh scratch path if reproducing later. Do not recreate a worktree on top of an existing directory. Commands that apply/import/refresh corpus data in older literature documentation were intentionally not run for this diagnosis.

```sh
git worktree add --detach /private/tmp/sirm-test-failures-20261018/checkout \
  990c8221728a44b6ab78cfff5159612edb0983a7
cd /private/tmp/sirm-test-failures-20261018/checkout
git rev-parse HEAD
git status --porcelain=v1 --untracked-files=all
```

The full pristine run used the existing external environment:

```sh
PATH=/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH \
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
/private/tmp/sirm-sync-audit-20261018/test-env/bin/python -m pytest -q tests \
  --junitxml=/private/tmp/sirm-test-failures-20261018/clean-full.xml \
  --basetemp=/private/tmp/sirm-test-failures-20261018/pytest-full \
  > /private/tmp/sirm-test-failures-20261018/clean-full.stdout.log \
  2> /private/tmp/sirm-test-failures-20261018/clean-full.stderr.log
```

Only the existing archive helper was used to match the prior audit's setup:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
from pathlib import Path
from scripts.literature51_reproducibility import materialize_export_inputs
print(materialize_export_inputs(Path.cwd()))
PY
```

Each original test was run independently as `python -m pytest -q <exact-node-id> --junitxml=<individual-output>`, using the same PATH/PYTHONPATH settings. All sixteen exact commands, tracebacks and exits are in `individual-results.json`. The after-bootstrap selections and complete command arrays are in `restored-original-16-command.json` and `restored-additional-76-command.json`; no full-suite selection was used after resumption.

Useful machine-readable evidence:

| File under `/private/tmp/sirm-test-failures-20261018/` | Purpose |
| --- | --- |
| `original-16-failures.json`, `failure-inventory.json` | Complete original node IDs, assertions, source locations and tracebacks |
| `clean-full-summary.json` | All pristine failure/error cases, including the 76 additional setup cases |
| `individual-results.json`, `individual-comparison.json` | Per-process reproducibility and message comparison |
| `bootstrap.json`, `environment-fixture-comparison.json` | Exact fourteen-file restoration and parity with the prior audit |
| `restored-original-16.xml`, `restored-original-16-comparison.json` | Confirmed unchanged original failures after bootstrap |
| `restored-additional-76.xml` | Passing replay of every additional pristine failure/error |
| `frontend-mismatch.json`, `proposed-successor-analysis.json` | Single-path SRI diagnosis and exact proposed successor digest |
| `os-metadata-manifests.json`, `os-fixture-availability.json` | Original OS-file paths, locked hashes, exact local availability and absent Git blobs |
| `openalex-fixture-inventory.json`, `committed-cache-resolution.json` | Complete raw-source comparison and existing committed replacements |
| `legacy-validation-diff.json` | Exact four-path preservation-only receipt difference |
| `environment.json`, `research-integrity.json`, `final-preservation.json` | Runtime, current corpus counts and final no-change checks |

## Confirmed findings, limits and prioritized follow-up

Confirmed: all sixteen failures reproduce individually and after the original bootstrap; their messages match the older unchanged-remote replay. They are deterministic in the tested environments. There is no evidence of order dependence or intermittency. The frontend mismatch, every missing fixture path, exact replacement bytes and the additional setup failure chain are identified. No external OpenAlex request was made.

Not yet demonstrated: that implementing the proposed repairs produces a completely green full suite. No repair was applied, and no guard constant, assertion or historical payload was changed to run a counterfactual passing suite. Fixing R1 alone will expose the shared R2 dependency in those four tests; that is a confirmed source-level dependency, not a new independent cause. Portability outside the inspected Python/Node/browser environment was not experimentally established.

Safe prioritized repair plan:

1. **Make fixture setup explicit.** Reuse the existing fourteen-input helper and add the 99 hash-locked root-cache mappings from already committed Tier 1 copies. This needs fixture-support code and documentation, not a network call or data migration. Add negative tests for a missing source, corrupt bytes and a differing destination that must not be overwritten.
2. **Preserve the four exact historical OS inputs.** Add three lossless, reviewed payload archives plus the four-path manifest and checksum-checked temporary restoration. Keep all original manifests, receipt counts, read-set assertions and generated historical reports intact. Do not substitute current `.DS_Store` bytes or reduce the protected set.
3. **Register the exact SRI successor.** Add only `c589f61b628b787251410964ed50a0fe696a4038` / `web/index.html` to the historical successor tuple and add narrow acceptance/tamper regressions. Do not change the immutable October 1 fixture or approve current hashes broadly.
4. **Validate in that order:** the fourteen-input bootstrap cases and cache pair; the ten OS-fixture cases; all sixteen original cases together; containing historical modules and new negative fixture/successor tests; then one full suite, both data validators and tracked-data hash checks. Preserve the six requested corpus counts and all existing research decisions.

These test-reproducibility and exact-successor changes can safely be implemented together in a scoped follow-up because the four frontend failures otherwise remain blocked by the OS fixtures. Expected edits are fixture/bootstrap support, three new lossless test fixture payloads with a manifest, `tests/public_refinement_snapshot.py`, new negative regressions and setup documentation. **No canonical research CSV, public JSON, frontend asset, historical evidence record or existing historical assertion needs modification.**

A durable copy of the full diagnostic evidence, the complete JSON/CSV root-cause matrix and the report is retained at `/Users/meilinger/.codex/visualizations/2026/10/18/01a14e1e-0479-7ba2-8ebd-19928bcbfa4f/test-failure-diagnostics/`. `artifact-manifest.json` identifies the copied files by SHA-256.
