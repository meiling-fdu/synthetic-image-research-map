# CI-STABILITY-01 — Mapping-registration follow-up

Published predecessor: b5f838ec639a13587864bc5fd718fe23ed77244f. This is an independently validated follow-up within CI-STABILITY-01, not a new scientific wave or B1S republication. B1S remains **PUBLISHED — CI ACCEPTANCE PENDING** until the follow-up commit's hosted regression and downstream checks succeed.

## Distinct hosted failure

[Run 40516240311](https://github.com/meiling-fdu/synthetic-image-research-map/actions/runs/40516240311), job 122230774784, ran the exact first fixture-isolation commit. It finished with 2,272 tests passed, one failed, 389 subtests passed and two existing warnings in 594.38 seconds. Corpus/frontend preservation passed; downstream data validators were skipped.

The original institution case passed (JUnit 0.506 seconds), the three venue lifecycle cases passed (0.642–0.789 seconds), and both new boundary guards passed (0.510/0.733 seconds). The controlled first fix applied successfully.

The new, unchanged failing case was MappingInstitutionRegistrationEndpointTests.test_create_endpoint_reports_provisional_registration, POST /api/paper/mapping/create. Its client exceeded its existing 3-second deadline; the server eventually logged 201. JUnit node time was 3.103 seconds. Previous failed-run attempts had passed this different node in 1.559/2.021 seconds; the initial local full baseline passed it in 1.588 seconds. These are whole-test durations, not request timings.

Full failed-job log SHA-256: ac0d6cd13c6d09df8594583e0567952df45bc8c70a89ac5ed81e8a670dfd0b62.
JUnit SHA-256: 8a0963fd1140a315b7f38e0efc696020239386c83197a6a5d6ef424cb8819d11.

Both are retained with completed run/job metadata and checksums in the persistent archive /Users/meilinger/.codex/ci-audits/ci-stability-01-2026-10-27/failed-first-fix-ci-40516240311. Original B1S attempts 1/2 and the first investigation checkpoint remain unchanged and separately archived.

## Measurements and lifecycle diagnosis

The original mapping endpoint was reproduced in isolation without changing its client deadline or assertions. Temporary instrumentation delegates real functions and records monotonic wall time and thread CPU time.

| Stage | Original full-corpus fixture | Final scoped fixture |
|---|---:|---:|
| Mapping POST | 4,737 ms; original client timed out | 61.98 ms |
| Request load_admin_data | 4,630 ms | 60.30 ms |
| Actual create_mapping | temporary CSV already removed by late cleanup | 1.31 ms; actual persisted rows verified |
| Cleanup/mapping lock waits | below 0.01 ms | negligible |
| Read-only catalog enrichment | included in cold loader | 3,587.60 ms during real fixture preparation; 0.046 ms cache lookup during request |

The initial local full-suite trace also identified incidental work: load_admin_data 977.56 ms plus two full-map reads of 100.68/100.42 ms. The fixture supplies temporary mapping/institution registries but otherwise defaulted to the entire live corpus and a historical candidate map.

A diagnostic join after the unchanged failing test exposed a second harness problem: its daemon request worker outlived the test's TemporaryDirectory and encountered a missing mappings.csv. Joining only the serve_forever thread had not joined request workers.

A scoped-identity prototype with joined request workers still failed the unchanged 3-second client deadline (POST 3,608 ms) but completed its real 201 write before cleanup. This preserves the timeout failure rather than masking it, and demonstrates the corrected file lifetime. A further trace attributed 3,683.82 ms of initial loader time to read_venue_aliases, including 3,587.60 ms of actual cached catalog enrichment. The next actual request used the same real venue audit and loader without repeating that immutable initialization.

The final fixture first establishes and verifies its actual admin identity and active exclusion. It then starts the unchanged timed HTTP test. Preparation takes 3,746 ms in the cold trace; the real POST takes 61.98 ms. No HTTP response, venue audit or persisted write is fabricated or bypassed. No sleeps or timeout increases are introduced.

The venue catalog's cold initialization cost remains an operational/performance limitation. Production code and cold-first-request latency are not corrected or certified by this test-only change. A production deadlock or corruption defect is not established.

## Exact fixture scope

- tests/admin_http_fixtures.py adds matching source subsets, real fixture precondition loading, and JoinedFixtureHTTPServer. Non-daemon request workers and block_on_close make existing server_close wait before temporary-file removal.
- tests/conftest.py opts in only the demonstrated mapping-registration node.
- tests/test_admin_http_fixture_isolation.py adds a live-read boundary and runs the original HTTP case. It delegates create_mapping and verifies actual mapping, canonical institution and location-review records, including replacement of the stale preview ID.
- docs/ci_stability_01_mapping_followup_2026_10_27.md records this follow-up.

The fixture copies the complete existing curated record curated:75cbd31c9946c7eb7977 and its matching durable exclusion, not an invented paper or altered scope. Public/map/candidate subsets are copied by the same identity keys. The real loader confirms has_active_exclusion; no authoritative inclusion, taxonomy, publication or relationship record changes. Existing test sources, assertions, 3-second deadline and historical receipts remain byte-identical.

A separate audit of remaining HTTP fixtures found no additional demonstrated full-loader overrun under 2/3-second deadlines. Longer ActionRequired and curation tests have 30-second budgets; author-coverage dashboards lack an explicit short deadline. Their contracts and deliberate current-corpus comparisons remain unchanged.

## Validation and preservation

- Focused regression: 197 tests and 12 subtests passed in 51.14 seconds, zero failures.
- Final complete regression: 2,274 tests and 389 subtests passed, zero failures, two existing warnings, 513.61 seconds.
- Data validators and historical fixtures: both validators passed with zero errors; baseline warnings unchanged (294 curated, 62 public-paper, 0 map); all 117 historical fixtures checksum-matched.
- Independent source review: 34/34 checks passed; receipt SHA-256: 015622e67b478e5341458492cc8b7847b10c5622941fb95dd1c40b6a6b5126a8.
- Preservation preflight: 8,944 checks passed, zero failures. Receipt SHA-256: 07a4d8684b53519d94b490c07cce730cae3ff4207a2aa743bfe1c6504138a57b. Staged and published gates remain required; their receipts are retained separately in the audit archive.

Source and public counts remain 674 public, 557 formal, 613 mapped, 1,410 relationships/unique pairs; tasks 621 detection/84 attribution/45 localization; types 578 method/138 dataset/97 benchmark/21 survey/86 analysis study. Batch B unresolved 131 historical/129 active-public, Batch C 13 deferred debts and the separate 39 inventory are preserved.

```
AUTHORITATIVE_CORPUS_CHANGED = 0
PUBLIC_EXPORTS_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
UNEXPECTED_CHANGED = 0
IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0

All 128 protected files and 49 frozen artifacts remain unchanged. Primary/CLIP/BCP work and the B1S worktree are preserved. No public export or scientific review is repeated. Existing data-validator warnings and the two legacy pytest warnings remain separate debt.

7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA
```

## Conditional delivery

The first report and failed-hosted evidence are immutable. Publish this four-file follow-up only after complete validation and preservation, as one normal child of b5f838ec639a13587864bc5fd718fe23ed77244f. Require exact remote SHA, 0/0 synchronization and successful hosted regression, data validation and preservation before closing B1S acceptance. This pre-publication report does not claim hosted success in advance; the final acceptance receipt belongs to the independent persistent audit archive.
