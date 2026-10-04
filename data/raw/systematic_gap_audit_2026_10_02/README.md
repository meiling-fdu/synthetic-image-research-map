# October 2–3 literature gap audit evidence

This directory is isolated audit material, not an import/export input. No curated or manual data is written by the audit helper.

- `search/`: original web search response strings and queries (42 calls, 84 query strings).
- `evidence/p*.json`: original primary-source web-reader responses, including failed retrievals. Tool citation tokens are preserved as raw source data, never as report citations.
- `sources/*.gz`: original HTTP response bytes, gzip-compressed deterministically; `source_manifest.json` has URL/time/status/content type/SHA-256. HTTP success does not establish usable content.
- `evidence/*_pdf_text.json`: text extracted from the two locally cached primary PDFs, with page boundaries and source links.
- `icml2026_screening.json`, `primary_metadata.json`, `priority_identity_checks.json`, `fetch_jobs.json`, `fetch_extra_jobs.json`: interrupted-session screen, extracts, partial checks and retrieval plans, preserved without replacement.
- `candidates.json`: final work-level adjudications, seven-layer identity evidence, proposed taxonomy, exact decisions and metadata before/after values. `actionable_sets` defines exactly A and B. Quarantined evidence holds are in neither set. `manual_review` remains true on proposals. Empty fields mean unverified/unavailable.
- `discovery_records.json`: every parsed search occurrence; links to final work IDs where promoted. Unpromoted discovery records have an explicit screening disposition and are not counted as unique reviewed works.
- `source_coverage.json`: venue/source families, saved query references, outcomes and limits.
- `baseline.json`, `saved_105_checksums.json`: unchanged interrupted baseline and protected corpus checksum inventory.
- `external_changes.json`: separate committed homepage-branding changes since that baseline, never an exception for corpus data.
- `validation.json`, `final_git_audit.json`: completed integrity and Git evidence.

Revalidate from any directory using the absolute script path, or from the repository root:

```sh
python3 scripts/audit_gap_2026_10_02.py validate
python3 -m unittest tests.test_audit_gap_2026_10_02
```

Counts distinguish raw query occurrences (duplicates retained), automatic index enumeration, gated title inspection, work-level status decisions, and the frozen reference. The report does not claim exhaustive coverage or full-text review of every screened title.

## Approved successor migration, October 3

The above validation receipt describes the completed pre-migration audit. The maintainer subsequently approved 17 additions and 12 metadata updates; those are now applied. `candidates.json` retains the original statuses and discovery evidence, with separate `maintainer_decision` and `migration_outcome` fields. Its original full contents are preserved in `../systematic_gap_migration_2026_10_03/discovery_snapshot.json`.

Do not interpret the old audit's “105 unchanged” result as a current-state assertion or rerun discovery. Validate the intentional successor with `python3 scripts/migrate_systematic_gap_2026_10_03.py validate`. The [migration report](../../../docs/systematic_literature_gap_migration_2026_10_03.md) records additions, non-add decisions, unresolved affiliations, tests and integrity. Frozen NeurIPS evidence remains unchanged: **7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA**.

## Commit packaging

The complete local evidence inventory above is broader than the approved commit. The [migration report’s explicit commit allowlist](../../../docs/systematic_literature_gap_migration_2026_10_03.md#commit-preparation--explicit-allowlist) classifies every path. Search response bodies, web-reader tool responses, redundant full-source captures, transient interstitial/error bodies and verbose/debugging receipts remain local and unstaged. No capture is deleted or normalized. Original manifest/candidate capture paths and checksums remain historical retrieval references; omitted bodies are not repository dependencies for current migration or historical corpus guard tests.

Structured primary metadata, reviewed affiliation evidence, decision ledgers, compact final validation receipts and required predecessor snapshots are committed. Four raw captures are retained because reconstruction reads them: the official PMLR volume index and three institution-specific Wikidata coordinate records.
