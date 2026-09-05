# Paper Metadata Consistency Audit

This deterministic audit traces 18 canonical metadata fields across all 613 public papers (11034 paper-field rows).

## Result

- TRUE_INCONSISTENCY: 0
- LEGACY_FALLBACK_RISK: 0
- INTENTIONAL_TRANSFORMATION: 10
- DISPLAY_ONLY: 7085
- MISSING_OPTIONAL: 2298
- Authoritative affiliation mismatches: 0
- Retired institution affiliation leaks: 0

## Stable corpus invariants

- Public papers: 613
- Published-only papers: 517
- Unique public paper–institution relationships: 1402
- Map markers: 1403 (one valid relationship has two confirmed locations)

## Findings by field

| Field | True inconsistency | Legacy risk | Intentional | Display only | Missing optional |
|---|---:|---:|---:|---:|---:|
| affiliations | 0 | 0 | 0 | 0 | 0 |
| arxiv_id | 0 | 0 | 0 | 290 | 323 |
| author_institution_attribution | 0 | 0 | 0 | 613 | 0 |
| authors | 0 | 0 | 6 | 607 | 0 |
| curation_status | 0 | 0 | 0 | 415 | 198 |
| doi | 0 | 0 | 0 | 524 | 89 |
| location_ids | 0 | 0 | 0 | 445 | 168 |
| metadata_source | 0 | 0 | 0 | 415 | 198 |
| paper_categories | 0 | 0 | 0 | 0 | 613 |
| paper_id | 0 | 0 | 0 | 0 | 198 |
| publication_date | 0 | 0 | 4 | 297 | 312 |
| publication_type | 0 | 0 | 0 | 0 | 0 |
| publication_year | 0 | 0 | 0 | 613 | 0 |
| review_status | 0 | 0 | 0 | 415 | 198 |
| source_database | 0 | 0 | 0 | 613 | 0 |
| task | 0 | 0 | 0 | 613 | 0 |
| title | 0 | 0 | 0 | 613 | 0 |
| venue | 0 | 0 | 0 | 612 | 1 |

## Frontend and CSV contracts

- PASS — canonical paper source precedes marker fallback
- PASS — paper CSV uses canonical DOI normalizer
- PASS — paper CSV uses canonical arXiv extractor
- PASS — Paper Details uses exported venue before legacy venue fallbacks
- PASS — deep links restore canonical paper identity
- PASS — hierarchy match context is stored separately

Paper Details, Institution Records, Unique Papers, CSV export, and deep links consume the canonical paper record first. Display punctuation, label expansion, DOI/arXiv link construction, author joining, and venue acronym/track labels are presentation-only. Institution hierarchy match context remains in a separate search explanation structure and is never added to affiliation evidence.
