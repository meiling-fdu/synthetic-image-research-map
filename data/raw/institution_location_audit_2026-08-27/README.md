# Location evidence cache — 27 August 2026

Read-only source responses retained for the scoped institution-location audit.
These are evidence, not automatic overrides of manual decisions.

- `named-features.json`: Nominatim search responses grouped by query, with endpoint,
  query and retrieval date. Result objects preserve the returned feature identity,
  coordinates, address, names, bounding box and licence. Candidate selection required
  separate paper/site evidence; nearby results and city centroids were not accepted.
- `padriciano.osm`: OpenStreetMap API 0.6 map response for bounding box
  `13.8265,45.6555,13.8315,45.6600`, retrieved 2026-08-27 from
  `https://api.openstreetmap.org/api/0.6/map`. Building way `62251650` supports the
  independently identified Amped Software tenant location in Padriciano Building A.
- `ucr-boundary.json`: Nominatim lookup of OSM relation `R1634776`, with
  `format=jsonv2&polygon_geojson=1`, retrieved 2026-08-27. The returned campus boundary
  was used to check the existing University of California, Riverside point, not
  replace it with a new centroid.

Geodata attribution: © OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright).
Returned copyright and feature metadata remain in the caches. Query results may
change upstream; this snapshot preserves what was examined. No API keys were used.

Decisions, paper affiliations, source URLs, rejected alternatives and curated IDs
are recorded in `docs/manual_institution_location_audit_2026-08-27.json`,
`docs/remaining_institution_location_audit_2026-08-27.json` and the curated audit logs.
Downloaded paper PDFs and browser screenshots are not stored in this repository.
