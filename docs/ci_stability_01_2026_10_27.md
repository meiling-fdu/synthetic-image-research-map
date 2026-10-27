# CI-STABILITY-01 — HTTP lifecycle fixture isolation

Date: 2026-10-27. Published B1S baseline: `df9774b64f717d535d3f299a727545f4b9488adb`.

This is an independent test-stability change. B1S remains **PUBLISHED — CI ACCEPTANCE PENDING** at this pre-publication checkpoint. The new commit's complete hosted CI must pass before acceptance closes; its final run, commit and checksum receipts are recorded separately in the persistent audit archive. B1Q/B1R/B1S science, decisions, exports and prior successful Pages/live-JSON verification are unchanged.

## Diagnosis

The demonstrated defect is incomplete isolation of small HTTP test fixtures from unrelated, evolving repository inputs. Their original two- and three-second clients accidentally cover full-corpus JSON parsing, generated diagnostic queues and checkout-wide Git status. The tests remain functionally meaningful; their workload was not bounded by their intended temporary records.

The institution cleanup POST reads the 19,788,529-byte public map under the cleanup and mapping locks before applying its one-mapping action. The confirmed-change branch does not consume that map. Its GET also reads the 9,085,050-byte public-paper file. Neither institution route runs dashboard computation or Git.

The venue fixture already patches the server's public paths, but ReviewContext has definition-bound defaults and dashboard_data separately reads the original JSON. The snapshot's load_admin_data also falls back to live mappings and the historical candidate map. Its synchronous Git status uses a 15-second subprocess budget, although the test client allows three seconds.

This establishes a fragile fixture workload. Local measurements did not reproduce the hosted timeout, and the archived CI attempts have no request-level monotonic traces or scheduler counters. Runner contention, a deadlock, or a production server correctness defect is not proven. Both affected solo tests and the final focused run leave no HTTP worker threads behind. The unchanged full baseline had one unrelated daemon public-preview-sync worker at process exit; it is not demonstrated to cause these failures.

## Original failed CI evidence

Both attempts ran exactly `df9774b64f717d535d3f299a727545f4b9488adb`; neither original attempt is overwritten or rerun by this change.

| Attempt | Job | Result |
|---|---|---|
| [1](https://github.com/meiling-fdu/synthetic-image-research-map/actions/runs/40467247931/attempts/1) | 122065531757 | 2,270 passed, 1 failed; 389 subtests |
| [2](https://github.com/meiling-fdu/synthetic-image-research-map/actions/runs/40467247931/attempts/2) | 122074663429 | 2,269 passed, 2 failed; 389 subtests |

Both fail the institution cleanup POST test. Attempt 2 also fails the initial dashboard GET in VenueSaveLifecycleTests.test_uncertain_book_container_remains_visible_in_editor_and_dashboard. The older baseline's post-save dashboard timeout and BrokenPipeError are separate evidence. A late HTTP 200 establishes eventual response generation, not completion before the client's deadline; a later broken pipe can follow client disconnection.

In both attempts, the failed regression step skips the downstream data validators; corpus/frontend preservation and JUnit upload still succeed. JUnit has 2,271 regular testcase elements and tests=2660 including 389 subtests.

| Artifact | SHA-256 |
|---|---|
| Attempt 1 full log | 07b12a0b752dd82adec95772ac01c3857a02a502f3d52ff8f77333ef182e44bb |
| Attempt 1 JUnit XML | 8654a87c8eb830bb3d0979fb10d4ada81a5b31654db9c8613a7b9cb4d60e6664 |
| Attempt 2 full log | 6cd7c31c1a9c9eff37c8d610f39f91f870b2d9acc60477f2f6289c31890c8e38 |
| Attempt 2 JUnit XML | 85b569fbdfb58f3d59005818a04599bdc9bca2641dc6dcf0e3bc4c2039a4a148 |

The downloaded artifacts are pytest-junit-40467247931-1 (ID12716834216) and pytest-junit-40467247931-2 (ID12718428728). Original artifact archive digests and API provenance are in the individual evidence receipts.

Persistent archive, outside every Git worktree:
`/Users/meilinger/.codex/ci-audits/ci-stability-01-2026-10-27`

The initial archive-checksums.json has SHA-256 cdaff786856e381b51dd1ffb2ba3c6ed9be881626c4de1aa42d00b0130a39cd7. Local investigation checkpoints, including unsuccessful trials, remain separately under /private/tmp/ci-stability-01-2026-10-27.

## Monotonic measurements

Temporary instrumentation delegates actual functions and records perf_counter_ns wall time and thread_time_ns CPU time. It preserves the actual HTTP clients and deadlines; its timings are observational, not new performance thresholds. The final full acceptance run has no timing wrappers.

| Request/stage | Unchanged solo | Unchanged full suite | Final focused fixtures |
|---|---:|---:|---:|
| Institution GET | 206 ms | 163 ms | 0.61 ms |
| Institution POST | 100 ms | 103 ms | 1.11 ms |
| POST map read | 93 ms | 95 ms | tiny fixture JSON |
| Cleanup action | 1.31 ms | 1.34 ms | 0.95 ms |
| Cleanup/mapping lock waits | about 0.001 ms | below 0.01 ms | no observed contention |
| Venue dashboard GETs | 634–1,128 ms | 649–1,918 ms | 67–71 ms |
| Separate dashboard public-data stage | 160–164 ms | up to 1,438 ms | tiny fixture JSON |
| Dashboard Git status | 23–454 ms | 30–34 ms | 13 ms, actual temporary-repository Git |

Across 2,269 tests passing both hosted attempts, summed JUnit durations rise 472.927→708.035 seconds (+49.7%). Modules without HTTP symbols rise 52.5%; the median paired ratio for nodes at least 10 ms is 1.476. These include setup/teardown and show broad run-condition variability, not its exact cause.

The unchanged local full suite passed 2,271 tests and 389 subtests in 509.00 seconds, with two existing warnings. It therefore does not independently reproduce the hosted timeout. It does confirm significant incidental work under full-suite conditions.

Final timing receipt: preserved-final-focused.json. Original traces remain baseline-institution.json, baseline-venue.json and baseline-full.json; the independent JUnit comparison is static/junit-duration-comparison.json.

## Final change — new files only

- tests/admin_http_fixtures.py supplies tiny real JSON/CSV files around the unchanged institution test and metadata-server factory. It routes definition-bound JSON reads through the real parser; supplies fixture mappings and candidate-map inputs; uses real empty diagnostic files; and runs real Git status in an initialized temporary repository.
- tests/conftest.py applies those inputs only to designated lifecycle fixtures and their boundary tests. It handles both pytest's top-level and namespace-package module identities, including publication and workshop venue callers.
- tests/test_admin_http_fixture_isolation.py rejects reads of live public/candidate/mapping/diagnostic paths; executes the original institution lifecycle; and verifies actual fixture counts, Git cwd/output, HTTP save, persisted venue metadata and queue/dashboard agreement.
- docs/ci_stability_01_2026_10_27.md records this audit.

Every pre-existing tracked file is byte-identical to the B1S baseline. No HTTP server code, timeout, semantic assertion, historical receipt, export or workflow definition changes. Original factory setup, actual handlers, durable writes, review decisions, queues, background preview coordination and teardown all still execute. There are no sleeps, disabled tests, fabricated responses or blanket historical exceptions.

The two boundary tests initially failed on escaped live-data reads. The first direct-edit prototype passed HTTP checks but failed two strict historical source-byte guards. A trial exact-successor approach encountered an additional historical helper boundary and was stopped. All four trial source edits were archived and restored exactly from B1S. The final additive fixture approach passes these guards without changing any of them. Unsuccessful trial logs and the explicit restoration receipt are retained.

## Validation

- Final focused regression: 181 tests and 12 subtests passed in 51.42 seconds; zero failures. This covers original HTTP/persistence/workflow assertions, workshop callers, the new boundaries and the original historical guards.
- Final uninstrumented complete regression: 2,273 tests and 389 subtests passed, zero failures, two existing pytest warnings, 522.21 seconds (additive-full.xml and additive-full-result.json).
- Authoritative validator: passed, zero errors; 294 pre-existing warnings, identical to the B1S validation baseline.
- Public validator: passed, zero errors; map warnings=0, paper warnings=62, identical to the B1S baseline.
- Authenticated offline historical inputs: 117/117 checksum-matched, no input recreated during final check.
- Independent final source review: 34/34 checks passed; SHA-256 5c5834d0b910775fa36948d860d52576bd10700c7d7513425648796b21ad3555.
- Preservation gate: 8,931/8,931 checks passed; all integrity counters zero. Receipt integrity/working-three-operational.json SHA-256 2628d34d1f52514d810ff5d7fd4f31bb8116af1866f659ad48237105e21c1980.

The final suite's two warnings are existing PytestReturnNotNoneWarning receipts in legacy exclusion successor tests. No test dependency or Python/Node version is changed. Local tests use the established Python3.12.14/pytest9.1.1 and Node24.22.1 environment; hosted CI independently uses Python3.14.7 and Node24.19.0.

## Data and preservation

Public=674; formal=557; mapped=613; relationships=1,410; unique paper–institution pairs=1,410. Tasks remain detection621, source attribution84, localization45. Types remain method578, dataset138, benchmark97, survey21, analysis study86. Batch B unresolved remains historical131 / active-public129.

All authoritative data and public JSON remain byte-identical; no export is run. Preserve all six B1Q/B1R inputs, B1S evidence, Batch C's13 deferred debts, the separate39-paper inventory, NeurIPS7+1 records and all49 frozen artifacts. The128 protected files and original305 primary untracked files remain unchanged. Concurrent primary CLIP/BCP changes are observed and preserved rather than reset; the original B1S worktree is unchanged.

```
AUTHORITATIVE_CORPUS_CHANGED = 0
PUBLIC_EXPORTS_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
UNEXPECTED_CHANGED = 0

7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA
```

The unchanged baseline test suite created one ignored empty process-lock file, `.admin/public_preview_sync.json.export.lock`. Its exact SHA-256 is e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855. It remains operational-only and is excluded from staging; no ignore rule is changed.

## Publication gate

Only these four new test/document files may enter one separate focused commit. Require a fresh remote ancestry check, normal fast-forward push, exact remote SHA and zero ahead/behind. The automatically triggered complete regression must succeed, including downstream data validation and preservation. No additional B1S deployment is manually requested.

This report is the pre-publication checkpoint and does not assert hosted CI success in advance. The independently archived final acceptance receipt and required GitHub Actions result establish closure once every gate passes.
