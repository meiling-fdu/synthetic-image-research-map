# Primary-source evidence — ten-paper curation

This cache is limited to the ten additions specified by the user. `manifest.json`
records download URLs, byte lengths and SHA-256 hashes. PDFs were extracted with
pypdf and page 1 was rendered and visually inspected for author numbering;
full-text sections on objectives, datasets and contributions were also reviewed.
The dynamic-ensemble PDF was copied from the preceding reconciliation cache.
Version identifiers printed in the arXiv PDFs are recorded in the manual ledger.

OpenAlex exact DOI/arXiv lookups support identifiers only. No OpenAlex author
affiliation inference was used. Cached web responses retain the original source
URLs; they are discovery/evidence traces, not instructions or a literature search.
Additional official arXiv/proceedings metadata already inspected during
reconciliation remains in `../key_paper_reconciliation_2026_09_08/`.

OpenReview direct PDF requests returned HTTP 403/browser challenges. The Prefill
workshop identity is instead supported by the official NeurIPS event and slides,
alongside the inspected arXiv PDF. The different DINOHash workshop record was not
merged into Provenance; its version relationship and affiliation superscript 1
remain unresolved.

Geocoder responses are unmodified, locally cached Nominatim/OpenStreetMap data
(ODbL; https://www.openstreetmap.org/copyright). Only reviewed institution/campus
or exact street-address matches were accepted. Empty results were retained.
Newcastle's returned multi-site geometry/postcode mismatch was not accepted.
Lab campus-point reuse and Aptima's representative headquarters location are
explicitly documented in the manual ledger; no personal work-site inference or
city-center fallback was made.

Decisions: `data/manual/primary_paper_curation_2026_09_08.json`.
Current reproducible audit: `scripts/report_primary_paper_curation.py`.
