# Approved October 3 gap migration evidence

This is the successor to the completed October 2 literature audit. Discovery was not restarted. The 17 approved additions and 12 identity-preserving metadata updates are already applied; do not run `apply` again.

- `baseline.json`: saved HEAD, 105 protected checksums, 49 frozen checksums, all original curated rows, public counts and frozen MIRROR record.
- `approved_candidates.json`, `maintainer_decisions.json`, `plan.json`: approved works, 27 explicit decisions, and exact schema-shaped additions/updates. `live_deduplication.json` contains the seven-layer checks immediately before insertion. `insertion.json` records 17 additions and 12 existing identities updated, with no conversions.
- `sources/*.gz`, `source_manifest.json`: original public HTTP response bytes and URL/time/status/content-type/checksum provenance. These are deliberate evidence archives, not temporary downloads. A successful HTTP status does not prove usable PDF content.
- `affiliation_review.json`, `affiliation_pdf_text.json`, `prior_source_references.json`: reviewed paper-time affiliation groups, extracted source text, and references to unchanged earlier captures. MICCAI's inaccessible PDF and unresolved ten-author affiliations remain explicit.
- `institution_identity_checks.json`, `location_evidence.json`: institution identity and coordinate evidence. Missing coordinates remain review cases; no centroid fallback or alias merge is made.
- `preexport_repairs.json`, `title_normalization_repairs.json`: validation-driven repairs limited to this migration. Unsupported location placeholders were removed from the confirmed-location registry; three metadata titles were canonicalized with the repository normalizer. The final plan matches the applied rows.
- `discovery_snapshot.json`: full original candidate ledger before adding maintainer decisions/outcomes. Original discovery statuses and evidence remain intact in the successor ledger.
- `predecessor_623/`, `predecessor_623_manifest.json`: deterministic gzip archives of original inputs, each checked against the saved baseline SHA-256 before historical use. These isolate completed historical reports from later curation. They are not the current authoritative corpus.
- `preexisting_branding_snapshot.json`: separately verified branding changes committed before this migration, explaining why the older UI snapshot was already stale. The original UI fixture is not overwritten.
- `validation.json`, `relationship_verification.json`: recomputed counts, exact approved-delta checks, deduplication, affiliations, relationship evidence and protected/frozen integrity. One unchanged historical UCSB author-set overlap is documented separately from new relationships.
- `curated_validation_before.txt`, `curated_validation_after.txt`: baseline/current warning comparison. Four identifier-less exclusion reviews and the unresolved MICCAI mapping explain the five new warnings.
- `full_suite_initial.xml`, `initial_full_suite_triage.json`: superseded first full-suite results and explicit failure classifications. `full_suite.xml` is the final run; `test_results.json` records the requested smaller groups and final result.
- `git_audit.json`: complete tracked/untracked path inventory, scope classification, staged state and HEAD comparison.

Current read-only validation:

```sh
python3 scripts/migrate_systematic_gap_2026_10_03.py validate
python3 scripts/validate_curated_database.py
python3 scripts/validate_public_preview.py
python3 -m pytest -q tests/test_systematic_gap_migration_2026_10_03.py tests/test_audit_gap_2026_10_02.py
```

The full suite requires pytest and Node on PATH. This run used Python 3.14, pytest 9.1.1 in an external temporary dependency directory, and bundled Node 24.19.0. No repository dependencies were installed. Normal public validation permits documented unresolved-affiliation warnings; strict warning-free validation is not claimed.

See [the migration report](../../../docs/systematic_literature_gap_migration_2026_10_03.md) for all 17 mapping classifications, all 12 metadata updates, final test results and limitations. No manual data, frozen NeurIPS artifacts or frontend implementation was edited. No commit or push is part of this task.

## Commit packaging

The complete local evidence inventory above is broader than the approved commit. The [migration report’s explicit commit allowlist](../../../docs/systematic_literature_gap_migration_2026_10_03.md#commit-preparation--explicit-allowlist) classifies every path. Search response bodies, web-reader tool responses, redundant full-source captures, transient interstitial/error bodies and verbose/debugging receipts remain local and unstaged. No capture is deleted or normalized. Original manifest/candidate capture paths and checksums remain historical retrieval references; omitted bodies are not repository dependencies for current migration or historical corpus guard tests.

Structured primary metadata, reviewed affiliation evidence, decision ledgers, compact final validation receipts and required predecessor snapshots are committed. Four raw captures are retained because reconstruction reads them: the official PMLR volume index and three institution-specific Wikidata coordinate records.
