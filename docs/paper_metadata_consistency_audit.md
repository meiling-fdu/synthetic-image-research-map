# Paper Metadata Consistency Audit

This deterministic audit traces 18 canonical metadata fields across all 639 public papers (11502 paper-field rows).

## Result

- TRUE_INCONSISTENCY: 0
- LEGACY_FALLBACK_RISK: 0
- INTENTIONAL_TRANSFORMATION: 10
- DISPLAY_ONLY: 7453
- MISSING_OPTIONAL: 2289
- Authoritative affiliation mismatches: 0
- Retired institution affiliation leaks: 0

## Stable corpus invariants

- Public papers: 639
- Published-only papers: 531
- Unique public paper–institution relationships: 1419
- Map markers: 1419 (one valid relationship has two confirmed locations)

## Findings by field

| Field | True inconsistency | Legacy risk | Intentional | Display only | Missing optional |
|---|---:|---:|---:|---:|---:|
| affiliations | 0 | 0 | 0 | 0 | 0 |
| arxiv_id | 0 | 0 | 0 | 325 | 314 |
| author_institution_attribution | 0 | 0 | 0 | 638 | 1 |
| authors | 0 | 0 | 6 | 633 | 0 |
| curation_status | 0 | 0 | 0 | 472 | 167 |
| doi | 0 | 0 | 0 | 508 | 131 |
| location_ids | 0 | 0 | 0 | 481 | 158 |
| metadata_source | 0 | 0 | 0 | 472 | 167 |
| paper_categories | 0 | 0 | 0 | 0 | 639 |
| paper_id | 0 | 0 | 0 | 0 | 167 |
| publication_date | 0 | 0 | 4 | 258 | 377 |
| publication_type | 0 | 0 | 0 | 0 | 0 |
| publication_year | 0 | 0 | 0 | 639 | 0 |
| review_status | 0 | 0 | 0 | 472 | 167 |
| source_database | 0 | 0 | 0 | 639 | 0 |
| task | 0 | 0 | 0 | 639 | 0 |
| title | 0 | 0 | 0 | 639 | 0 |
| venue | 0 | 0 | 0 | 638 | 1 |

## Frontend and CSV contracts

- PASS — canonical paper source precedes marker fallback
- PASS — paper CSV uses canonical DOI normalizer
- PASS — paper CSV uses canonical arXiv extractor
- PASS — Paper Details uses exported venue before legacy venue fallbacks
- PASS — deep links restore canonical paper identity
- PASS — hierarchy match context is stored separately

Paper Details, Institution Records, Unique Papers, CSV export, and deep links consume the canonical paper record first. Display punctuation, label expansion, DOI/arXiv link construction, author joining, and venue acronym/track labels are presentation-only. Institution hierarchy match context remains in a separate search explanation structure and is never added to affiliation evidence.
