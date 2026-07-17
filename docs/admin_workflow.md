# Local Admin Workflow

## Paper arXiv enrichment

Open **Papers → arXiv enrichment** to review public-map papers that have no
effective arXiv ID. **Find candidates** searches the arXiv Atom API by title and
keeps the results in the local Admin process only; discovery does not modify
curated or generated files.

Each candidate displays its arXiv ID, evidence, source, and confidence.
**Accept** requires explicit confirmation and writes the confirmed override
atomically to `data/curated/paper_arxiv_links.csv`. **Ignore** also requires
confirmation, records the outcome in `data/curated/review_decisions.csv`, and
leaves the arXiv-link file unchanged. Preview export and validation remain
separate release steps.

## Institution management safety boundary

Use **Institution Management** for identity, alias, parent, status, and merge
actions. Use **Institution Alias and Location Review** only for location and
geocoding evidence. Location writes are bound to the row's stable
`institution_id`; changing coordinates cannot rename an institution or reassign
a paper author.

Global merge displays affected papers, author mappings, markers, and authors,
then requires the exact `REPLACE … WITH … GLOBALLY` phrase and writes an audit
row. Ignore confirms that the institution is hidden from public outputs without
deleting data. Geocoding combines canonical name with reviewed city, region,
country, and parent context; candidate selection remains manual.

## Institution cleanup queue

Run `python3 scripts/audit_institution_consistency.py` to regenerate
`data/manual/institution_consistency_audit.csv`, then run
`python3 scripts/sync_institution_review_queue.py` to import its findings into
`data/curated/institution_review_queue.csv`. Full refresh performs both steps.
The sync also migrates legacy terminal statuses to `archived`, archives stale
findings tied to excluded or replaced mappings, and preserves their resolution
notes and timestamps. Institution Cleanup only treats `open` rows as actionable.
The **Institution Cleanup** Admin section reads only the persistent curated
queue. The generated audit CSV is reporting-only.

The default table contains one review case per paper-author pair, not one row
per finding. Opening a case shows all current and suggested institutions, raw
affiliation evidence, every child finding, normalized mapping provenance, and
the risk explanation. Filters cover severity, open/resolved/ignored status,
provenance, issue type, and paper/author/institution text. Original findings
remain in the queue for audit history.

Accept Suggestion updates the linked author-institution mapping through the
protected mapping API and records the resolution on the queue row. Ignore and
Mark Manually Resolved retain the finding and its evidence without changing a
mapping. Keep Multiple Affiliations resolves the grouped case without removing
supported mappings. Replace Mapping opens the existing mapping editor; Add
Alias and Set Parent Institution open institution management. Compatible
suggestions may be selected and accepted as one transactional batch; any
failed or conflicting fix rolls back the entire batch.

Resolution decisions use an inline form showing the issue, paper, author,
current institution, and selected action. Presets cover a correct existing
mapping, alias/name variation, parent-child relationships, confirmed multiple
affiliations, and custom notes. Notes are optional for manual resolution,
ignore, and keep-multiple decisions; an empty note receives a stable default
audit explanation. Mapping replacement and institution merge explanations
remain mandatory. Multiple compatible review cases may be selected and marked
manually resolved together; each child queue row retains the same generated
batch note, reviewer, action, and timestamp.

Use **View Evidence** to inspect a case without leaving Institution Cleanup.
The read-only dialog combines paper and author metadata, current mapping
IDs/status/provenance, raw affiliations, parsed suggestions, source and
confidence fields, canonical aliases, confirmed parent/child relationships,
the audit explanation, and risk factors. Suspicious replacements include a
before/evidence/after comparison. Resolution shortcuts close the evidence
dialog and enter the existing protected resolution, mapping, alias, or parent
workflow; opening the dialog itself never writes curated data.

After an author-institution mapping is excluded or retargeted, Admin mapping
writes immediately reconcile linked cleanup findings. The old queue row is
marked non-current and retained as historical audit evidence; a later queue
sync cannot reopen it from a stale report. Cleanup cases derive **Current
active institutions** only from mappings with `active` or `needs_review`
status, and list excluded or superseded mappings separately under
**Historical/excluded institutions**. Curated validation applies the same
mapping-status guard so an excluded mapping cannot recreate a publish blocker.

Only unresolved high-severity corruption findings (`confirmed_mapping_changed`
and `suspicious_replacement`) fail curated validation and block Publish
Changes. Other high findings are review cases, medium findings remain warnings,
and low findings are report-only. Ignored or otherwise resolved queue findings
do not block publishing. Trusted mappings are not challenged for ordinary name
variation; ignored institutions and explicitly confirmed aliases, parents, and
merges do not generate blockers.

This runbook covers the local **Interactive Curation Console**. Run all commands from the repository root. Ordinary edit and save actions write durable human decisions locally and never stage, commit, or push them. Publishing is a separate, explicit, confirmed action.

The data boundaries are deliberate:

- `data/curated/*.csv`: source of truth for durable maintainer decisions.
- `data/manual/*.csv`: generated diagnostic and review queues, never durable UI state.
- `web/data/*.json`: generated public-preview output, regenerated by export workflows only.
- `data/processed/*.csv`: OpenAlex/processed source layer, never edited by Admin.

## Start a maintenance session

1. Check the working tree so existing changes are understood:

   ```bash
   git status --short
   ```

2. Start the local admin server:

   ```bash
   python3 scripts/serve_admin.py
   ```

3. Open the tokenized `http://127.0.0.1:8765/admin/?token=...` URL printed in the terminal. Keep the server on loopback and treat the token as temporary local access.
4. When finished, stop the server with `Ctrl-C`.

## Add Paper

1. Choose **Add Paper** and search by title, DOI, arXiv ID, or paper URL.
2. Select the correct OpenAlex result and verify every prefilled field. If no result is correct, use **Add manually instead**.
3. Confirm the task, optional subtask, provenance, links, and review note before saving. OpenAlex authorships are retained as mapping candidates. For manual or arXiv-only records, enter affiliation rows as `authors | institution | raw affiliation`.
4. Saving creates reviewable author–institution mapping candidates. Exact confirmed institution or alias matches are eligible immediately; unresolved names use `needs_review`.

The paper record is written to `data/curated/papers.csv`, and candidates are written to `data/curated/author_institution_mappings.csv`. A paper with no affiliation evidence is blocked until the maintainer explicitly acknowledges the missing-mapping diagnostic. Saving does not invent coordinates, create markers directly, or update generated preview JSON.

## Paper Metadata Editor

Select a paper, open **Paper Metadata**, and compare its effective record, original public-preview record, and curated override. Editing a preview-only paper creates a row in `data/curated/papers.csv`; editing an existing curated or manually added paper updates that row, preserves `created_at`, and advances `updated_at`. Identity collisions are rejected. Saving does not edit public JSON.

## Delete / Scope Review

1. Select the paper and choose **Delete / Exclude from site**.
2. Select the most specific reason and record a review note that explains the decision.
3. Use **Restore** if the scope decision is later reversed.

This creates or updates an auditable decision in `data/curated/paper_exclusions.csv`; it does not delete source or processed metadata. The exclusion reaches the public preview only after a full refresh.

## Author–Institution Mappings

1. Select a paper and review **Current exported/public evidence** for context.
2. Under **Author–Institution Mappings**, add or edit one row for each supported institution.
3. Record the canonical institution name, every author associated with it, the raw affiliation or evidence, mapping status, and a review note.
4. Use **Replace all mappings** only when intentionally superseding all active mappings; prior rows remain in the audit history.

Mappings are written to `data/curated/author_institution_mappings.csv`. Do not assign the whole paper to the first author's institution. Missing or ambiguous institution coordinates are handled in the separate location-review queue.

## Institution Location Review

1. Choose **Institution Location Review** and select a queued institution.
2. Verify the institution and coordinates against a reliable source.
3. Enter the location labels, uppercase two-letter country code, latitude, longitude, source or source URL, and a review note.
4. Confirm the location, or mark the row **ambiguous** or **unresolved** when the evidence is insufficient.

Confirmed coordinates are written to `data/curated/institution_locations.csv`, and the corresponding row in `data/curated/institution_location_review.csv` is updated. Never guess coordinates or resolve ambiguity merely to create a marker.

### Institution review statuses and aliases

Use the status chips to separate `pending_review`, `needs_coordinates`, `ambiguous`, `alias_candidate`, `confirmed`, `ignore`, and `excluded` rows. `alias_of_confirmed` rows are included with confirmed work in the summary and resolve through their selected canonical institution.

- **Confirm location** only after verifying the canonical name, city, country, latitude, and longitude.
- **Confirm as alias** when the raw name is another language, acronym, or historical name for a selected confirmed institution. This writes `data/curated/institution_aliases.csv`; it does not create another location.
- **Mark ambiguous** when identity or location is uncertain. Use **Needs coordinate review** for a valid institution whose coordinates still need verification.
- **Ignore** parsed non-institutions. Use **Exclude** for valid records that must not appear publicly.

Only `confirmed` and `alias_of_confirmed` are exportable, and aliases use the canonical institution's verified coordinates. Fuzzy or translation-only suggestions remain `alias_candidate` or `ambiguous` until a reviewer decides. Raw multilingual affiliation text remains evidence even after canonicalization.

## Diagnostic review queues and mapping coverage

The console exposes four generated queues:

- **High-risk Marker Review** reads `data/manual/high_risk_marker_review.csv`, grouped by P0/P1/P2.
- **Marker Blocker Review** reads `data/manual/paper_marker_blocker_report.csv`.
- **Key Paper Coverage Review** reads `data/manual/key_paper_coverage_report.csv`.
- **Manual Import Review** discovers the supported `key_papers_*` candidate CSVs.

The Dashboard starts with a grouped **Project Health** module covering the corpus, author mapping, institution/location maintenance, review queues, and publication/exclusion state. Metrics use green, amber, red, and blue/gray states for good, warning, critical, and contextual values. Queue metrics reuse their generated queue summaries and show the largest breakdown categories. Metrics link to their corresponding review workflow where one exists; Author Mapping links also apply the relevant status or missing-author sort. **Refresh Project Health**, **Reload all review queues**, and a successful full refresh all reload the same dashboard aggregation. Missing generated reports appear as **Report missing** rather than as a zero or a file-system error.

Project Health reuses the public-preview JSON counts, Admin corpus counts, location review payload, the four generated review queue loaders listed above, and `data/manual/missing_author_mappings_report.csv`. The queue breakdown remains directly below it as an expanded secondary summary; the former duplicate top-level statistics row has been removed.

The overall score is a bounded 0–100 heuristic maintenance score, not a paper-quality rating. It starts at 100 and deducts 0.25 per uncovered author-mapping percentage point (maximum 25), 0.5 per missing coordinate (maximum 15), 0.1 per missing affiliation (maximum 15), one point per 150 combined high-risk/blocker rows (maximum 20), and one point per 50 missing author links (maximum 15). Scores of 90 or more are **Excellent**, 75–89 **Needs attention**, and lower scores **Critical maintenance**. If a score input report is absent, the score reads **Needs refresh**.

The Dashboard also shows a read-only **Author Mapping Coverage** card with complete, partial, and missing-mapping counts, full-paper coverage percentage, and the ten highest-priority gaps. Its dedicated tab defaults to warnings and provides search, status, triage, and key-paper filters, rank/missing-author sorting, and direct links into the paper's Author–Institution Mapping Editor. Each warning exposes current canonical institutions, mapping state and author text, raw affiliation evidence when it already exists in curated mappings, stable source identifiers, a public-impact cue, and a deterministic suggested action. **Likely auto-fixable** requires a displayed conservative name-reconciliation suggestion between a missing public author and an existing active curated mapping author; it is a suggestion, not a confirmed mapping or an automatic edit. **Map missing authors** opens a new mapping draft with the missing names prefilled; institution and affiliation evidence still require maintainer confirmation.

- Dashboard data source: `data/manual/missing_author_mappings_report.csv`
- Full narrative report: `docs/missing_author_mappings_report.md`

The Admin server checks for the CSV at startup and generates it once when absent. If generation cannot complete, the UI shows **Author mapping report has not been generated.** with a **Generate Report** action. **Reload mapping coverage** bypasses browser caching and rereads only this report. The Admin full-refresh workflow also regenerates both report artifacts.

### Canonical venue metadata

The paper-metadata editor loads `GET /api/venues`, whose records are built only from confirmed `data/curated/venue_aliases.csv` identities. Options use the shared type order (Conference, Journal, Preprint, Book), then unique-paper count descending and canonical name. Search covers canonical name, audited acronym, venue type, track, confirmed aliases, and historical `raw_venue` variants. Selecting an option saves `venue_id`, `venue_name`, `venue_acronym`, `venue_type`, and `venue_track`; the combined label is display-only.

The selected venue synchronizes formal `publication_type`. Workshops are canonical Conference venues with `venue_track=workshops`, so their distinct identity remains in the venue ID and track rather than a separate public type. The control remains disabled until **Override publication type** is chosen, and both the browser and API warn or reject an unconfirmed conflict. Historical `raw_venue` is retained unless the reviewer explicitly selects the provenance-replacement checkbox.

Unknown text is never saved directly. **Create new canonical venue** submits a reviewed canonical name, optional acronym, type, track, raw alias, and note to `POST /api/venues/create`. Exact normalized duplicates are rejected. Similar names, aliases, or acronyms return possible matches and require explicit distinct-venue confirmation before the alias registry is atomically updated. Metadata updates reject nonexistent IDs or structured fields that conflict with their registry identity; legacy venue-only records are resolved through `scripts/venues.py` on load and unresolved or ambiguous values remain review cases.

Use queue actions to open the metadata, scope, mapping, location, or Add Paper editor. Explicit reviewed/no-action, unresolved, marker-confirmation, and candidate outcomes are written to `data/curated/review_decisions.csv`; location-review actions also update `data/curated/institution_location_review.csv`. Confirm-marker actions create or activate a curated mapping only when paper, institution, and institution-author evidence are present. Exclude-wrong-mapping decisions exclude matching curated mappings and suppress matching automatic markers during export. The queue source CSV is never edited as durable state.

For title-match review, compare DOI, OpenAlex URL, normalized title, year, and suggested matches in the selected row. Confirm a match, add the paper, exclude it from scope, or leave an explicit unresolved decision.

## Run the full refresh pipeline

After curation changes, choose **Run full refresh pipeline**. It runs, in order:

```text
python3 scripts/validate_curated_database.py
python3 scripts/validate_paper_exclusions.py
python3 scripts/export_public_preview.py --preserve-existing
python3 scripts/validate_public_preview.py
python3 scripts/audit_key_paper_coverage.py
python3 scripts/diagnose_paper_marker_blockers.py
python3 scripts/report_high_risk_markers.py
python3 scripts/report_missing_author_mappings.py
```

The pipeline stops at the first failure. The preserve-existing export unions the
current complete public preview with the local candidate snapshot, so a
no-search admin refresh cannot silently replace full coverage with a partial
cache. Counts are also guarded by
`data/curated/public_export_baseline.json`; an unexpected decrease stops the
export before either public JSON file is written. Only an explicitly reviewed
replacement file passed with `--approved-baseline` may authorize lower counts.
The final export still reapplies active exclusions and retraction checks
to that union; preserved JSON cannot keep a paper whose current title starts
with `[Retracted]` or `Retracted:`, whose publication type/flag marks a
retraction, or whose exclusion metadata marks it retracted. The same rule is
applied to both the paper list and map markers. Read the command log, correct
the underlying curated record, and run it again. **Reload preview data** only
rereads existing JSON; it does not export changes.

After a successful local refresh:

1. Inspect the changed-file list and command log.
2. Review `git status --short` and the relevant diffs, especially curated CSVs and `web/data/public_preview_*.json`.
3. Check that paper coverage, mappings, exclusions, and markers match the intended decisions.
4. Choose **Publish Changes** only when the local changes are ready to publish.

## Publish Changes

The intended publishing workflow is:

```text
Admin edit
→ Publish Changes
→ full refresh pipeline runs
→ public preview validation runs
→ selected files are committed and pushed
→ GitHub Pages updates after deployment
```

**Publish Changes** always asks for confirmation and cannot start while another
admin workflow is running. It runs
`python3 scripts/admin_publish_changes.py`, stops immediately on refresh or
validation failure, shows the final command output, and does not create an
empty commit. Before refresh and again before Git staging, it counts both
public-preview datasets and reports their sizes and shrinkage percentages. It
aborts without staging, committing, or pushing if either dataset shrinks by
more than 5%, or if the result falls below 700 map records or 350 paper
records. There is intentionally no override.

Small decreases of at most 5% are accepted because confirmed version merges
and newly recognized retractions can intentionally remove duplicate or
ineligible records. The absolute floors and post-export validation remain in
force, so a partial refresh cannot be published merely because its percentage
change is small.

The publish set is calculated from Git's changed tracked files after refresh. It
includes the complete durable admin layer under `data/curated/`, review outputs
under `data/manual/`, generated `web/data/` previews, and the generated reports
declared by the canonical admin workflow. Modified frontend assets under `web/`
are included only when Git reports an actual change. `data/backups/` and
temporary `data/manual/key_papers_missing_*` or
`data/manual/key_papers_query_failed_*` batches are excluded. Unrelated staged
files are not included. The result log lists changed and generated files, every
validation/export step, and the commit/push outcome; a failed step stops before
staging and retains its command output.

Recommended order: fix P0 public-marker issues; confirm P1 candidates; resolve missing coordinates; resolve missing affiliations; review missing key papers; only then expand OpenAlex coverage.

The server binds to `127.0.0.1` by default, requires its random token for every API, requires explicit `--unsafe-bind-all` for non-loopback binding, and runs only fixed `shell=False` command lists. Git commit and push are available only through the confirmed **Publish Changes** workflow.
