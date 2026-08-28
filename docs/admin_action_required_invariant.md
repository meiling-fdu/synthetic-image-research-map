# Action Required: effective queue contract

## Diagnosis (2026-08-28 working tree)

There were two independent failure classes:

1. **Client snapshot inconsistency.** `loadDashboardAndQueues` cleared and rendered
   all four queues as empty before fetching, retaining the previous dashboard.
   Its `Promise.all` included unrelated institution cleanup; any failed request
   left the old nonzero summary beside zero unresolved / zero hidden rows. There
   was no request-generation guard. Coverage rendering also ran before queue
   rendering, so a rendering exception could leave newly received detail data
   unrendered. The failed-refresh path is reproduced by the runtime regression.
   Successful unfiltered queue loads from the initial working tree were not
   empty. The original browser's failed request/history was not available, so
   this audit does not claim to identify that particular request's error.
2. **Incomplete unresolved semantics and scope drift.** Dashboard queue loaders
   used default paths instead of the handler's configured evidence paths.
   Readers applied some mapping/exclusion overrides, but did not consult saved
   review decisions, paper/institution lifecycle, version merges, completed
   diagnostics, current import presence, or cross-file duplicate identities.
   Title-only diagnostics failed to match stronger curated identities. The
   high-risk report mixed individual marker candidates and paper-level findings;
   the dashboard called the combined count “High-risk papers” and routed it to
   Marker Review. Missing-location summary and detail state refreshed separately.

The API and Admin static files already used `Cache-Control: no-store`; the issue
was not an HTTP cache deliberately serving stale totals. Institution registry
has its own stat-invalidated cache, but Action Required did not use it. Generated
CSV/public JSON state can lag curation; it is evidence, not the unresolved count.
Long-running Python servers retain imported code and must be restarted for this
change. The new client detects the old snapshot contract and reports that need.

### Previous count semantics

| Category | Previous source/meaning |
| --- | --- |
| Marker blockers | Partially suppressed rows from `paper_marker_blocker_report.csv`, including `already_mapped` / `no_action`; 537 of 546 raw rows were already mapped. |
| Missing institution locations | `location_review_payload.summary.needs_coordinates`: pending review rows without usable confirmed coordinates, not unique institutions; loaded independently of the dashboard on Refresh. |
| High-risk papers | Combined high-risk diagnostic rows (401 institution-marker rows and 54 paper-level rows before suppression), not a count of distinct papers. |
| High-risk Marker Review | The same mixed high-risk report, despite marker-only interface wording; cleared to zero before Refresh completed. |
| Key-paper coverage | Partially suppressed full coverage audit; 252 of 299 raw rows were already covered as map markers. |
| Manual imports | Concatenated candidate-file rows after limited mapping/exclusion suppression; included imported records and repeated candidates. |
| Missing author mappings | Zero-mapping papers in the coverage report, without a category-specific effective queue. |
| Missing affiliations | Admin aggregate of paper-level missing-affiliation flags, routed to a independently filtered paper list. |

## Authoritative definition

For each category, `value == count == total_unresolved == len(records)` under the
same evidence snapshot. Only rows with `actionable: true` and
`effective_review_status: unresolved` are returned in an actionable queue.

`ReviewContext` loads request-local curated papers, mappings, exclusions,
institutions, review decisions, manual overrides, current public records and
confirmed version merges. `actionable_payload` resolves status and deduplicates
work items before counting. Explicit terminal states, durable exclusions,
inactive entities, superseded versions, saved completed decisions, and applicable
curated corrections suppress candidates. Explicit reopening beats stale
diagnostic status, but never a durable paper exclusion/inactive institution.
Covered/no-action diagnostics and already-imported candidates are not work.

Confirmation is scoped: confirming paper metadata does not confirm every marker;
confirming an author mapping does not supply missing institution coordinates.
Public visibility is a separate annotation, not a universal resolved status.
A visible marker can still have unresolved marker evidence. Missing-location
items use effective location review plus active paper/institution scope.

Exact DOI/OpenAlex/paper-ID identities deduplicate diagnostics. Exact normalized
title/year is used only when unambiguous; no fuzzy paper or institution merging
is performed. Marker work is keyed by paper + institution + author group;
paper work by paper identity; missing locations by institution identity. Duplicate
source references are retained in `diagnostic_sources`. `raw_count`,
`hidden_resolved` and `suppression_reasons` are separate debugging fields.

## API and UI

`/api/dashboard` returns `action_required`, complete `action_queues`, location
review state and mapping coverage in one response. Counts are projections of
those queue records, not separately computed totals. The UI validates the
contract before replacing its snapshot; failure retains the last complete
snapshot with an error. A generation counter rejects late older responses.
Auxiliary institution cleanup cannot veto the actionable snapshot. Review links
reset queue filters. There is no hidden 500-row truncation or five-category cap.
Full Refresh/Export completion also reloads this snapshot; ordinary Refresh is
read-only and does not rewrite generated diagnostics or curation.

| Category | GET queue endpoint | Review target |
| --- | --- | --- |
| Marker blockers | `/api/review/marker-blockers` | `marker-blockers` |
| Missing author mappings | `/api/review/missing-author-mappings` | `missing-author-mappings` |
| Missing affiliations | `/api/review/missing-affiliations` | `missing-affiliations` |
| Missing institution locations | `/api/review/missing-locations` | `missing-locations` |
| High-risk markers | `/api/review/high-risk-markers` | `high-risk` |
| High-risk papers | `/api/review/high-risk-papers` | `high-risk-papers` |
| Key-paper coverage | `/api/review/key-paper-coverage` | `key-coverage` |
| Manual imports | `/api/review/manual-import` | `manual-import` |

Paper-level high-risk decisions retain the existing durable `high_risk_marker`
decision namespace with `target_type: paper` and an empty institution. Their GET
queue is separate. Location/mapping queues link into their existing curated
editors. All endpoints retain loopback/token protection and no-store headers.

## Recomputed working-tree counts

| Category | Summary | Actionable detail rows |
| --- | ---: | ---: |
| Marker blockers | 7 | 7 |
| Missing author mappings | 0 | 0 |
| Missing affiliations | 0 | 0 |
| Missing institution locations | 7 | 7 |
| High-risk markers | 270 | 270 |
| High-risk papers | 47 | 47 |
| Key-paper coverage | 40 | 40 |
| Manual imports | 62 | 62 |

These are audit results, not hard-coded application/test expectations. No curation
records were changed to obtain them. The static public website remains unchanged
by this fix and still requires no Admin server.

## Verification

Invariant tests cover all eight categories, resolved/ignored/inactive states,
curated decision precedence and reopening, exclusion updates without report
regeneration, duplicate identities, title-only coverage, confirmed mapping versus
missing location, real location status resolution, configured API paths,
summary/detail equality, correct Review targets, and failed/out-of-order Refresh.
JavaScript tests execute actual snapshot loading, queue rendering and navigation
with a minimal DOM harness. Browser visual inspection was unavailable because
the in-app browser blocked the local URL; no screenshot verification is claimed.

Five existing curation/baseline tests also fail with the original location module
loaded directly from Git in memory against this working tree: Griffith's newly
confirmed status; Chongqing's pending geographic relationship; a fixed expected
457 locations versus 458; a fixed expected 342 curated papers versus 344; and
fixed publication-type totals. They were not changed or hidden by this fix.

Final full-suite run: **1,156 passed, 49 skipped, 5 pre-existing failures**.
Final focused run (`tests/test_admin*.py`, curated location resolution, location
confirmation identity, and paper metadata editing): **209 passed**. The focused
run includes API/data tests and the executable frontend Refresh regressions.
All eight real GET endpoints matched the dashboard snapshot, and a subsequent
dashboard Refresh returned identical actionable records. Both JavaScript syntax
checks and `git diff --check` passed.

## Changed files

- `scripts/admin_review_queues.py`: effective evidence resolver, unique work items,
  category/endpoint definitions, and snapshot-derived counts.
- `scripts/serve_admin.py`: configured context, shared snapshot and review APIs.
- `scripts/curated_locations.py`: effective confirmation, lifecycle suppression,
  and duplicate location-review rows.
- `web/admin.js`, `web/admin.html`: snapshot Refresh, accurately scoped Review
  panels/links, complete row/category rendering, and asset cache version.
- `tests/test_admin_action_required.py`,
  `tests/test_admin_action_required_frontend.py`,
  `tests/admin_action_required_frontend.cjs`: invariant regressions.
- `tests/test_admin_dashboard_frontend.py`,
  `tests/test_admin_review_visibility.py`,
  `tests/test_admin_paper_categories_frontend.py`: updated frontend contracts.
- `docs/admin_action_required_invariant.md`: this audit and contract.

No curation, generated diagnostic, or public-export data files were changed by
this implementation. Existing user edits remain in the working tree. Restart
the existing Admin server and reload Admin to activate the updated Python/API
contract; the independently running user server was not stopped by this audit.
