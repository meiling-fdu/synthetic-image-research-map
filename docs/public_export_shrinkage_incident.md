# Public export shrinkage incident

## Impact

A direct export reduced `public_preview_papers.json` from 488 to 395 records
and `public_preview_map_data.json` from 950 to 703 records. The complete
identity-level incident lists are:

- `docs/public_export_missing_papers.csv` — 93 canonical paper identities.
- `docs/public_export_missing_map_records.csv` — 247 stable map-record IDs.

## Root cause

The local OpenAlex candidate files are a partial snapshot. The 93 missing
papers were not present in the current in-scope candidate CSV, the all-candidate
CSV, the map-input JSON, or curated papers. They were valid historical records
retained by the published public JSON baseline. Running
`scripts/export_public_preview.py` directly without `--preserve-existing`
discarded that baseline union.

Venue normalization did not exclude the records. The missing papers covered
37 journals, 34 preprints, 19 conferences, and 3 books. Sixteen had an unknown
venue and two carried the legacy workshop type, but none were retracted,
durably excluded, or removed by paper-version resolution. All 93 were in scope
and map-ready. Their paper summaries referenced 228 of the missing markers; the
remaining 19 markers belonged to nine paper identities still represented in
the smaller paper export. All 247 missing markers were in scope, had usable
coordinates, and consisted of 167 automatic-fallback and 80 curated markers.

## Resolution

The committed outputs were used as the preservation baseline, then regenerated
with `--preserve-existing`. The venue resolver reapplied the new taxonomy to
the complete baseline. The result contains 488 papers and 950 markers, with no
missing baseline paper identities or marker IDs and no remaining public
`venue_type=workshop` values.

The exporter now checks the reviewed counts in
`data/curated/public_export_baseline.json` before writing. An unexpected
decrease fails the export; an intentional reduction requires an explicitly
supplied reviewed baseline.
