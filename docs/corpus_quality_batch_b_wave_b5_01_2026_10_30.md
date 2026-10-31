# Batch B Wave B5-01 — Controlled integration

Eight supported publication URLs and three supported journal bindings are integrated from the independently validated B4-01 and B4-02 transactions. Their original reports, evidence and decisions remain immutable. This report records passed local gates; final publication requires the exact remote commit, Pages/live-byte checks and hosted CI.

## Exact transaction

- Exactly 15 paper CSV-cell changes: six paper_url cells and three venue_id/name/type triples.
- Exactly two publication-URL override rows and three venue aliases are appended.
- The registry preserves the original 103 decision rows byte-for-byte and appends B4-01’s nine followed by B4-02’s fifteen records. All 127 decision IDs and all 24 new action/evidence bindings are unique; no remapping occurred.
- Eleven actions close; thirteen new holds stay open: P028, P001, U001/U002/U003/U005/U006/U007/U008/U014/U016/U018/U023.
- No canonical ID, author, DOI/arXiv identity, publication year/type, task, research type, institution mapping or relationship is incidentally corrected.

## Recomputed accounting

| Metric | Before | Integrated |
|---|---:|---:|
| historical_unresolved_actions | 131 | 120 |
| active_public_unresolved_actions | 129 | 118 |
| historical_unresolved_papers | 121 | 113 |
| active_public_unresolved_papers | 119 | 111 |
| terminal_actions | 28 | 39 |

Corpus remains 674 public, 557 formal, 613 mapped and 1,410 relationship rows/unique pairs. Tasks remain 621 detection, 84 source attribution, 45 localization. Research types remain 578 method, 138 dataset, 97 benchmark, 21 survey, 86 analysis study. Source-based accounting and the full public identity/pair comparison establish these values; none was forced into source records.

## Deterministic public effects

The exact public difference is eleven accepted paper records plus P001’s related hold-reason projection. Eight publication records expose the accepted landing URLs. Twenty-three existing map rows receive only their corresponding URL/status/override-note changes, retaining each row’s original affiliation provenance. The three journal records gain their accepted canonical fields; existing aggregate metadata-status logic continues to expose affiliation debts. P001 receives no invented track or binding; U005 receives no location.

Exactly eight URL cells change in the pipeline-generated missing-author mapping CSV; this is a derived report, not a manual correction table. The public JSON pair, quality-report timestamp and key-paper input receipt are the other required generated differences. Seven direct output artifacts from the post-suite offline refresh match the authenticated first export byte-for-byte: `EXPORT_REPRODUCIBLE = 1`. No unrelated export churn is accepted.

## Historical and live regression boundaries

Original B1 transaction assertions retain their immutable published endpoints, source hashes, question/policy checks and scientific evidence. Independently guarded current B5 tests verify the exact source appends, all unaffected fields, current accepted URLs, journal bindings and generated effects. B1M retains the original pending-P034 observation, twelve canonical versus thirteen publisher authors, blank DOI, numerical caveats, exact scientific labels and relationships. Only its later separately accepted URL is admitted by current-state coverage.

B5-01R3 avoids a cascade of successor exceptions: the protected publish test and historical helper are restored to exact published bytes. A function-scoped pytest fixture supplies per-instance temporary coordinator state only to the selected legacy publish-test module. Production defaults, stable flock inodes, original assertions and HTTP deadlines are unchanged. The independently reviewed R2 experiment and all 20 cases remain authenticated archival evidence; no R2 exemption is active in the live helper. See the companion R3 report and pinned archive manifest.

## Executed validation

- B1G guard: 1 passed; historical/HTTP/archive gate: 76 passed; B4/B5 integration: 130 passed. These selections overlap; they are not a unique full-suite count.
- Complete offline suite: 2,445 tests and 389 subtests passed; zero failures; two existing legacy warnings. All 14 prior failures pass.
- Authoritative validator: 0 errors, 294 retained warnings. Public validators: 0 errors; 0 relationship warnings and 62 paper/affiliation warnings. No warnings are hidden or resolved incidentally.
- Established pre-report preservation: 29,140 checks; additional sealed-history preservation: 986 checks; zero failures. Final source/staged/committed/published audits are recorded separately after this report exists.
- Source and public identity/taxonomy/geography preservation, exact 127-row decisions,120/118 unresolved accounting, thirteen holds, first-export 537-check semantic review and seven-output byte reproduction are all checked.
- All 117 checksum-authenticated operational inputs remain ignored/local and excluded from the commit. No manuscript retrieval or scientific adjudication was repeated.

## Preserved limitations

P028 remains evidence-insufficient; P001’s conference identity has no verified track; U005’s approximate school point cannot be represented faithfully in the current precision schema. Ten other institution-site holds retain their paper-time campus and coordinate limitations. The U002 correction remains additive: SAMR 510630; 2021 patent 510663. Original B3 records and corrected later assessments remain traceable. P034’s 12/13-author discrepancy is preserved. No empirical reproduction or publisher-version equivalence is invented.

Both B4 source worktrees, 128 protected primary files, 49 frozen NeurIPS artifacts, Batch C’s 13 deferred debts, the separate 39-paper inventory and B1Q/B1R/B1S/CI-STABILITY-01 history remain unchanged. Concurrent primary/CLIP/BCP work is preserved. No B3-03 review begins.

The exact file inventory is `file_inventory.json` in the B5 packet. It distinguishes editable source/tests/reports from byte-preserved raw captures, diffs and historical evidence. Immutable evidence is authenticated, not whitespace-normalized. Operational caches and temporary scripts are excluded.

## Publication acceptance

The appended completion manifest preserves the original integration snapshot instead of rewriting it. One reviewed integration commit may be pushed only through normal fast-forward ancestry after staged audit. Remote SHA, Pages deployment, live committed-JSON bytes and the automatically triggered full hosted CI/downstream validators must all pass before publication is accepted. No failed hosted job is automatically retried. Actual post-commit evidence is recorded in the external completion archive and GitHub Actions.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
