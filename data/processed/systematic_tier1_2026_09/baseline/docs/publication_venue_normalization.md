# Publication venue normalization

The interrupted work contained a draft audit engine and checked venue authorities. The completed implementation shares one source-preserving venue resolver across Admin, review queues, and static exports.

## Data and precedence

- Original `data/curated/` and `data/manual/` files are not rewritten by the automatic audit. Explicit Admin saves remain the only user-directed curation changes.
- `data/processed/venue_authority_evidence.json` records checked journal/conference identities. `venue_paper_evidence.json` records DOI/arXiv-specific publication and proceedings evidence. Locally cached publisher-deposited Crossref and arXiv responses live in `data/raw/venue_audit_crossref/`.
- `scripts/venue_evidence.py` interprets this evidence offline. `scripts/venue_audit.py` combines it with the reviewed venue registry and preserves raw provenance. It does not change author, affiliation, location, abstract, task, category, or general curation fields.
- Confirmed registry identities and valid existing abbreviations take precedence over inferred abbreviations. Demonstrated errors such as the King Saud journal's conference type and the IJSREM misspelling have explicit source-backed repairs. Suspect or conflicting deposits are not certified automatically.
- Abbreviations are copied from official publisher usage or bibliographic authorities, including Clarivate's 2018 Journal Citation Reports (page-specific evidence links). They are never generated from initials. A verified full-name short form needs no redundant acronym. Unverified journal abbreviations stay in review without blocking independently verified name/type corrections; a short name that collides with an existing alias is proposed for review, not inserted into the registry.
- Year, canonical venue ID/name, and paper-level track remain separate. Editions, year suffixes, and generic track suffixes do not create new venue identities. A named standalone workshop can remain its own scholarly venue; a book series cannot stand in for a verified conference.
- A publisher's `book-chapter` label alone is insufficient to classify a conference proceedings contribution as a book. Checked proceedings-volume evidence resolves ECCV, NetACT, ICIAP, AINA, CSS, PAKDD and ECAI cases.
- A repository copy is not evidence that the work is unpublished. Conversely, a deposited DOI explicitly typed `posted-content`/`preprint` with the publisher's repository URL can identify that version as a preprint. Acceptance-only claims without a verified final publication stay reviewable.

## Persistence and live review

`python3 scripts/venue_audit.py --write` writes the effective paper fields in JSON/CSV, canonical venue registry, audit JSON, actionable review CSV, and human-readable report under `data/processed/` and `docs/`. The preserved initial snapshot prevents repeated runs from double-counting corrections. Runtime consumers recompute from current sources; they never use a stale audit report as authority.

Admin → Dashboard → Publication venues shows the paper, DOI, current/proposed type, canonical name/ID, abbreviation, track, reason/evidence and Open/Edit action. The Dashboard metric and rows share one request-local queue snapshot. Saving corrected metadata refreshes that snapshot immediately. Uncertainty does not mark a paper as curated or confirmed.

For a legitimate exception or inconclusive publisher deposit, select the desired venue/type/track and explicitly check the venue-review confirmation box with a source/reason note. The normal review-decision CSV stores that user decision, bound to a fingerprint of the saved bibliographic/venue fields. It expires on relevant changes, not unrelated edits. Explicit type overrides without this confirmation remain protected and reviewable. Automatic jobs never create manual confirmations.

The existing public export uses the same resolver and copies the final paper's venue fields to every map marker, ensuring cards, filters, statistics and map details agree. Unverified text is kept as source/display text and is not promoted to a guessed canonical ID. The static website needs no backend; the existing localhost Admin server handles editing only.

## Reproduction

```sh
python3 scripts/venue_audit.py --write
python3 scripts/export_public_preview.py --preserve-existing
python3 scripts/venue_audit.py --write
python3 scripts/validate_curated_database.py
python3 scripts/validate_public_preview.py
```

Evidence collection is optional and separate: `python3 scripts/collect_venue_evidence.py` caches unresolved DOI metadata and preprint publication status; `--doi DOI` adds a verified published-version lookup. Runtime/export paths do not access the network.

See [current audit and exact review reasons](publication_venue_audit_report.md). No commit, staging, deployment or publication is performed by the audit commands.

## Implementation map

- Audit/evidence: `scripts/venue_audit.py`, `venue_evidence.py`, `collect_venue_evidence.py`, and the processed evidence/registry/audit files.
- Shared identity/type resolution: `scripts/venues.py` and `publication_types.py`.
- Admin API, live queues and explicit decisions: `scripts/serve_admin.py`, `admin_review_queues.py`, `curated_schema.py`, `admin_workflows.py`, `web/admin.html`, and `web/admin.js`.
- Exports: `scripts/curated_export.py`, `export_public_preview.py`, regenerated public JSON files and `docs/public_preview_report.md`.
- Regressions: `tests/test_publication_venue_audit.py`; existing venue, paper-metadata, Dashboard, curated-location, frontend-filter and repository-publication expectations updated for stable IDs and corrected types. The dated release checkpoint retains its historical totals.

Verification checks compare all public paper and map identities plus unrelated fields against the pre-audit data. Author rosters, affiliation relationships, locations, tasks, categories, abstracts, curation statuses and existing provenance remain unchanged. The database and public-preview validators pass; their remaining affiliation/institution warnings are outside the venue audit.

The full test suite also contains pre-existing author/institution/location expectation failures. These were reproduced in an isolated `git archive HEAD` copy before any venue changes; no institution or author curation was modified to satisfy them. A test-generated unrelated institution-type report is not part of this change.

## Verification results (2026-08-28)

- Scoped venue/Admin/frontend/export regressions: **138 passed, 4 skipped**, including 19 audit-specific tests.
- Full suite: **1,180 passed, 19 failed, 49 skipped**. Remaining failures are the reproduced baseline issues: two author-roster expectations, one institution-count expectation, eleven location-review expectations, two geographic-relationship/confirmed-location checks, and three repository-count/status checks.
- Curated database validator: zero errors, 172 existing warnings. Public validator: zero errors, zero map warnings, seven existing paper-author warnings.
- Browser: 22 Dashboard items equal 22 review rows; the source-backed MM collision has current/proposed metadata, evidence and a working Open/Edit review-confirmation control. Fixture HTTP tests verify count/row removal immediately after save and persistent explicit confirmations.
- All 546 public papers and 1,233 map records retain identical unrelated fields. Existing nonempty source venue provenance is preserved (HTML entity encoding is semantically equivalent); export regeneration cannot drop it when rejecting an uncertain canonical ID.
- King Saud renders as Journal / JKSUCI. The CLIP proceedings example resolves to ECCV / conference / 2024 / Workshop. No active canonical venue remains an identifiable LNCS/CCIS or other resolvable proceedings series.
- No files in `data/curated/` or `data/manual/` were changed automatically. Nothing was staged, committed, published or deployed.

## Workshop field roles (2026-08-29)

`scripts/venue_tracks.py` owns the singular controlled paper-track vocabulary, including Main, Workshop, Tutorial, Demo, Challenge and Short Paper. Legacy plural/case spellings are accepted at input boundaries but effective/API/export values are canonical. Source titles, acronyms and alias text are not track fields and are never plural-normalized.

`workshop_venue_evidence.json` records verified parent proceedings aliases and independent workshop identities. The pre-audit `workshop_venue_baseline.json` is immutable. Its disputed standalone Workshop assignments are retained as explicit observations so an automatic rebuild cannot silently select Main; an explicit manual track or review confirmation supersedes the observation. Cross-Forgery's prior ICMR selection is similarly retained pending the conflicting MAD evidence review. These observations preserve state, not newly inferred tracks.

`python3 scripts/audit_workshop_venues.py` regenerates the role-aware JSON/CSV inventory and [workshop report](workshop_venue_audit_report.md). Run it after the export and venue-audit commands above. The inventory distinguishes canonical fields, paper tracks, source/provenance fields and historical snapshots. Source-file hashes and exact raw-venue comparisons guard preservation. No snapshot is overwritten on rerun.

### Final workshop verification

- Focused venue/schema/resolver/Admin HTTP/frontend/filter/export regressions: **140 passed**, with Node enabled. Additional result-card/cache-key and cross-surface artifact checks: **32 passed**.
- Final full suite with Node enabled: **1,241 passed, 19 failed**, in 215.82 seconds. Only the same previously reproduced baseline author/institution/location/count failures remain; no venue, Admin, frontend or export regression remains.
- Curated database and public-preview validators: zero errors; 172 existing curated warnings and seven existing public author warnings.
- All 551 effective records checked; 328 populated tracks normalized, including exactly 53 `workshops` → `Workshop`. Three parent acronyms corrected, one parent identity/name corrected, 35 prior workshop-related aliases retained, zero raw-venue changes. Five standalone identities and their 21 papers retained. Seventeen standalone-track cases plus one ICMR/MAD conflict and 22 earlier findings remain actionable: 40 total.
- Processed records, Admin effective records, Dashboard counts/rows, public papers and all map markers agree. HTTP tests verify immediate queue removal after a saved Main correction and persistent explicit review confirmation. A second effective-state pass changes zero venue fields.
- SHA-256 checks confirm all 351 raw/manual/curated source files unchanged. All 546 public papers and 1,233 map records preserve every unrelated field against the pre-audit repository data. Only the full suite's own unrelated institution-type report side effect was removed.
- `node --check` passed for both application scripts; `git diff --check` passed. No staging, commit or deployment was performed.
