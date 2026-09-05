# Public metadata-status global/local audit

Generated from `web/data/public_preview_papers.json` and authoritative mapping statuses in `data/curated/author_institution_mappings.csv`.

## Finding

The previous implementation allowed localized field status to set the paper-wide status and treated the derived `needs_review` aggregate as global. It also allowed curated affiliation state to upgrade a source-only paper. The corrected rule derives `overall` only from paper-level `review_status` and `curation_status`; venue, task/category, affiliation, mapping, and affiliation-provenance review signals remain field-local.

## Counts

| Metric | Before | After |
|---|---:|---:|
| Overall Verified | 343 | 397 |
| Overall Curated | 47 | 0 |
| Overall Needs review | 223 | 18 |
| Overall Source metadata | 0 | 198 |
| Papers with at least one Needs-review field | 223 | 223 |
| Needs-review venue fields | 218 | 57 |
| Authoritative `venue_review_required=true` | 39 | 39 |
| Localized venue issues | 39 | 39 |
| Needs-review affiliation fields | 173 | 193 |
| Localized affiliation issues | 173 | 193 |
| Genuinely globally unresolved papers | 18 | 18 |

- Previous Needs-review papers audited: **223**
- Previous Needs-review papers corrected to a non-global status: **205**
- All papers whose overall label changed, including source-only affiliation upgrades: **252**
- Full per-paper audit: [`public_metadata_status_audit.csv`](public_metadata_status_audit.csv)

## Exact scope rule

1. Normalize paper-level `review_status` and `curation_status` with precedence **Needs review → Verified → Curated → Source metadata**. This is `overall` and `default_field_status`.
2. Apply `venue_review_required` only to Venue, task uncertainty only to Task / category, and affiliation/mapping/provenance review signals only to Institution affiliations.
3. Treat public `needs_review` as a derived aggregate, never as a standalone global decision. When not already explained by a global, venue, or task state, it localizes to affiliation/mapping review because those are the remaining inputs to the export's recomputation.
4. Missing optional metadata creates no field and no downgrade. Unknown internal values provide no confidence and normalize to Source metadata unless a recognized higher-precedence paper-level value is also present.
5. `field_overrides` contains only status/source deviations from `default_field_status`; local fields never change `overall`.
