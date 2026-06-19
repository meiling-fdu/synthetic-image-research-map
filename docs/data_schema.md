# Data Schema

## Overview

The project uses four core related CSV tables to represent papers, authors, institutions, and the affiliations connecting them, plus auxiliary manual correction tables. The schema is intentionally small and compatible with metadata commonly available from OpenAlex, Semantic Scholar, Crossref, arXiv, and manual research.

Files in `data/manual/` are human-maintained source-of-truth corrections and must not be overwritten by automated processing. Future collection scripts should preserve original API responses in `data/raw/`, write normalized output to `data/processed/`, and apply manual data as explicit overrides.

Use UTF-8 CSV files. Store booleans as `true` or `false`; leave a value empty when it is unknown. Stable project IDs should be used for relationships rather than names, because names can change or collide.

## `papers.csv`

One row represents one paper. This table stores bibliographic metadata, scope labels, and provenance for how the paper entered the dataset.

| Column | Definition |
| --- | --- |
| `paper_id` | Stable, project-assigned identifier for the paper; primary key. |
| `title` | Paper title as reported by the preferred source or confirmed manually. |
| `year` | Four-digit publication year. Leave empty if unresolved. |
| `venue` | Journal, conference, workshop, or repository venue. |
| `doi` | Canonical DOI without a resolver URL when available. |
| `url` | Preferred public landing-page URL for the paper. |
| `arxiv_id` | arXiv identifier, including version only when the version matters. |
| `task` | Primary project task label: `detection`, `source_attribution`, `detection_and_source_attribution`, or `uncertain`. |
| `subtask` | Controlled reviewable label: `synthetic_image_detection`, `ai_generated_image_detection`, `deepfake_image_detection`, `generated_image_source_attribution`, `source_identification`, `source_verification`, `detection_and_source_attribution`, or `unknown`. |
| `is_survey` | `true` when the paper is a survey, review, systematic review, or taxonomy rather than a primary research contribution. |
| `is_deepfake_related` | `true` when the work specifically concerns deepfakes or face manipulation. This flag keeps that related area distinguishable from general synthetic-image research. |
| `is_image_editing_related` | `true` when an audit candidate concerns image editing or manipulation. Image-editing-only work is outside the scoped map dataset. |
| `source_query` | Query, search phrase, import batch, or other discovery context that produced the record. |
| `source_database` | Originating metadata source, such as `openalex`, `semantic_scholar`, `crossref`, `arxiv`, or `manual`. |
| `manual_review` | `true` when a human must verify the record, classification, deduplication, or metadata; otherwise `false`. |
| `notes` | Free-text comments for decisions, uncertainty, corrections, or follow-up work. |

### Processed OpenAlex Publication Metadata

`data/processed/openalex_candidate_papers.csv` retains the core fields above and adds source-level publication metadata for review and map display. The legacy `year`, `venue`, and `url` columns remain aliases for `publication_year`, `venue_name`, and `primary_url` so older local exports remain compatible.

| Column | Definition |
| --- | --- |
| `authors_ordered` | JSON-encoded list of paper-level author display names in the original OpenAlex `authorships` order. This is the display-author source for every institution-level map record. |
| `publication_year` | OpenAlex `publication_year`; no year is inferred from a title or URL. |
| `publication_date` | Source publication date when OpenAlex provides one. |
| `venue_name` | Source or repository display name, preferring `primary_location.source.display_name`; empty when unavailable. |
| `venue_type` | OpenAlex source type, such as journal, conference, or repository, when available. |
| `publisher` | Publisher or source host-organization name reported by OpenAlex. |
| `publication_type` | OpenAlex work `type`, falling back to `type_crossref` when needed. |
| `doi` | Canonical DOI without a resolver URL when available. |
| `arxiv_id` | arXiv identifier detected from source identifiers, a `10.48550/arXiv.*` DOI, or an arXiv location URL. |
| `arxiv_url` | Canonical `https://arxiv.org/abs/...` URL when an arXiv identifier can be extracted. |
| `primary_url` | Preferred source landing URL, with DOI and OpenAlex URLs used only as later fallbacks. |
| `landing_page_url` | Landing page from the primary or best available OpenAlex location. |
| `openalex_url` | OpenAlex work URL/identifier retained for source provenance. |
| `is_arxiv_preprint` | `true` when an arXiv identifier, arXiv URL, or explicit arXiv source is detected. |

These values remain candidate metadata. A missing venue is left empty and flagged for manual review; venue or conference names must never be guessed from a paper title.

## `authors.csv`

One row represents one author identity. The table keeps source identifiers and profile links without assuming that authors sharing a name are the same person.

| Column | Definition |
| --- | --- |
| `author_id` | Stable, project-assigned identifier for the author; primary key. |
| `name` | Author's display name, preserving the best available spelling. |
| `orcid` | ORCID identifier when confirmed. |
| `homepage` | Confirmed personal or institutional homepage URL. |
| `google_scholar` | Google Scholar profile identifier or URL when confirmed. |
| `semantic_scholar` | Semantic Scholar author identifier or profile URL when available. |
| `notes` | Free-text comments about identity, name variants, or unresolved ambiguity. |

Do not merge two author records solely because their names match. Identity resolution requires supporting identifiers or manual confirmation.

## `institutions.csv`

One row represents one institution or organizational unit used for affiliation and map placement. Original names remain available while a reviewed normalized form supports display and grouping.

| Column | Definition |
| --- | --- |
| `institution_id` | Stable, project-assigned identifier for the institution; primary key. |
| `name` | Institution name as reported by a source or affiliation string. |
| `normalized_name` | Manually confirmed canonical display name used for grouping variants. Do not populate by blindly merging similar names. |
| `city` | City associated with the institution location. |
| `country` | Country associated with the institution location; use one consistent naming convention. |
| `latitude` | Decimal latitude for the reviewed map location. |
| `longitude` | Decimal longitude for the reviewed map location. |
| `geocoding_source` | Source of the coordinates, such as a named geocoder, source database, institutional page, or `manual`. |
| `manual_review` | `true` when identity, normalization, location, or coordinates require human verification; otherwise `false`. |
| `notes` | Free-text comments about aliases, campuses, location uncertainty, or corrections. |

Geocoding results must be cached locally. Automated geocoding should not replace confirmed manual coordinates or normalization decisions.

## `institution_corrections.csv`

One row represents a manually verified override for an institution name found in automatic candidate affiliations. The table is applied before cached or online geocoding, so a correction can replace an incorrect automatic match. It is a human-maintained source file and must never be overwritten by scripts.

| Column | Definition |
| --- | --- |
| `match_key` | Raw or normalized institution name to match against `institution_name`. Matching uses lowercase text with simple punctuation removed and whitespace trimmed and collapsed. |
| `corrected_institution_name` | Manually verified institution name. Leave empty to preserve the candidate value. |
| `corrected_city` | Manually verified city. Leave empty to preserve the candidate value. |
| `corrected_country` | Manually verified country. Leave empty to preserve the candidate value. |
| `corrected_latitude` | Manually verified decimal latitude required for an active correction row. |
| `corrected_longitude` | Manually verified decimal longitude required for an active correction row. |
| `correction_source` | URL or explanatory note documenting the evidence for the correction. |
| `confidence` | Human-assigned confidence: `high`, `medium`, or `low`. |
| `notes` | Free text describing ambiguity, campus choice, or other correction context. |

Matching is exact after normalization; there is no fuzzy matching. This avoids merging similarly named institutions without explicit human intent. Duplicate normalized `match_key` values are rejected as ambiguous.

Documentation-only fictional example (do not add this row to the template):

```csv
fictional institute,Fictional Institute of Visual Studies,Example City,Example Country,12.3456,78.9012,https://example.invalid/institution,high,Fictional format example only
```

## `openalex_candidate_affiliations.csv`

This processed candidate table uses one row per paper-author-institution relationship reported by OpenAlex. Multiple authors at one institution remain separate rows, and one author with multiple institutions produces multiple rows. An author with only raw affiliation text, or no affiliation information, still receives one row with empty structured institution fields and `manual_review=true`.

| Column | Definition |
| --- | --- |
| `openalex_id` | OpenAlex work identifier. |
| `author_openalex_id` | OpenAlex author identifier when available. |
| `author_name` | Source author display name. |
| `author_position` | OpenAlex positional label, such as `first`, `middle`, or `last`. |
| `author_order` | One-based order of the authorship in the source work. |
| `institution_openalex_id` | OpenAlex institution identifier when structured metadata is available. |
| `institution_name` | Source institution display name. |
| `city` | Institution city when available. |
| `country` | Institution country name when available. |
| `country_code` | Source country code, kept separately from the country name. |
| `ror_id` | ROR identifier without the resolver URL. |
| `latitude` | Source institution latitude when available. |
| `longitude` | Source institution longitude when available. |
| `raw_affiliation_text` | Original affiliation text associated with this author and institution when available. |
| `manual_review` | Always `true` for automatic candidate rows until the relationship is verified. |
| `notes` | Missing-identity, raw-only, or missing-affiliation review context. |

## `paper_author_affiliations.csv`

One row represents a specific author-institution affiliation on a specific paper. Together, `paper_id`, `author_id`, and `institution_id` identify the relationship; multiple rows are allowed when an author reports multiple affiliations.

| Column | Definition |
| --- | --- |
| `paper_id` | Foreign key to `papers.paper_id`. |
| `author_id` | Foreign key to `authors.author_id`. |
| `institution_id` | Foreign key to `institutions.institution_id`. Leave empty only when the source affiliation cannot yet be resolved to an institution. |
| `author_order` | One-based position of the author in the paper's author list. |
| `is_corresponding` | `true` when the source identifies this author as corresponding, `false` when explicitly not corresponding, or empty when unknown. |
| `affiliation_text` | Original affiliation text associated with this author and paper, preserved for provenance and later review. |
| `manual_review` | `true` when the author, institution, or relationship match is uncertain and needs human verification; otherwise `false`. |
| `notes` | Free-text comments about the relationship, unresolved mappings, or source conflicts. |

### Why This Relationship Table Is Necessary

Affiliation is a property of an author's relationship to a particular paper, not a permanent property of either the author or paper. Researchers move between institutions, papers can have many authors, and one author can list several affiliations on the same paper. Paper-level or first-author-only locations would discard this information and misrepresent collaboration geography. Relationship-level records preserve every reported affiliation, author order, corresponding-author status, and original affiliation text while supporting accurate institution and map views. Map exports create a marker for every affiliated institution with usable coordinates, but every marker reuses the same paper-level `authors_ordered` list. Institution grouping never sorts, groups, or truncates the display author list, and it does not replace or collapse the underlying relationship rows.

## Paper Labeling

Labels describe scope without collapsing related categories into one field:

- Set `task=detection` only when the paper primarily detects AI-generated or synthetic images.
- Set `task=source_attribution` only when the paper attributes an AI-generated or synthetic image to its generation source, identifies that source, verifies it, or studies generated-image provenance/forensic attribution.
- Set `task=detection_and_source_attribution` when both scoped tasks are substantive, and `task=uncertain` when the automatic rules cannot assign one safely.
- Use only the documented `subtask` vocabulary from the `papers.csv` table. `model_attribution`, `generator_attribution`, and generic `attribution` are not task or subtask labels.
- Set `is_survey=true` for survey, review, systematic review, or taxonomy papers. A survey should still receive the `task` value that best describes its topical coverage.
- Set `is_deepfake_related=true` for deepfake or face-manipulation research. This flag does not replace `task`.
- Set `is_image_editing_related=true` for audit candidates centered on edited or manipulated images; this flag does not make them in scope.
- A paper may have more than one boolean flag. For example, a survey of deepfake detection can use `task=detection`, `is_survey=true`, and `is_deepfake_related=true`.
- Audio-only and video-only work is outside the project scope. Multimodal work should be included only when generated-image research is a meaningful component, with the scope explained in `notes`.

### Scope Boundary

In-scope work must combine explicit AI-generated/synthetic image context with detection or generated-image source-attribution context. Broad model attribution, feature or saliency attribution, explainable-AI attribution, authorship attribution, camera-model attribution, sensor attribution, and generic attribution are intentionally excluded. Papers that merely use GANs, synthetic data, or generated images for data augmentation, training, medical diagnosis, object recognition, traffic-sign recognition, person re-identification, remote sensing, or other downstream tasks are also outside scope.

`generator attribution` may support a preliminary source-attribution classification only when the same title or abstract explicitly identifies AI-generated, synthetic, generated, fake/deepfake, GAN-generated, diffusion-generated, text-to-image, or generative images. It is never sufficient by itself.

## Manual Review and Automatic Labels

Automatic labels are preliminary suggestions, not final classifications. They must remain visible, traceable, and editable so that a reviewer can understand and correct them. Future processing should preserve the rule, model, query, or source that produced an automatic decision rather than silently replacing it.

Set `manual_review=true` whenever a value is uncertain or conflicting, including ambiguous paper scope, author identity, institution normalization, affiliation mapping, deduplication, or geocoding. Describe the question in `notes`. After a human resolves the issue, update the reviewed manual record, set `manual_review=false`, and retain enough provenance or notes to explain the decision. An empty value means unknown; it should not be treated as reviewed or inferred automatically.
