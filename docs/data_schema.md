# Data Schema

## Canonical institution entities

`data/curated/institutions.csv` owns institution identity. Each row has a stable
`institution_id`, `canonical_name`, `institution_type`, `institution_status`, an
optional `parent_institution_id`, and a `public_display` preference. Ignored,
deprecated, and merged entities remain traceable but are omitted from public
outputs.

`institution_type` has exactly four canonical values, in public display order:
`university`, `research_unit`, `company`, and `other`. The shared resolver in
`scripts/institution_types.py` owns this enum and applies types after
canonical/merged-ID resolution; curated and public validators import its
canonical set. Existing canonical values are preserved; unsupported legacy
research values can be resolved for backward-compatible reads, but new or
unverified entities default to `other` for manual review. Names and aliases are
context, not sufficient classification evidence: in particular, the word
“Institute” does not imply `research_unit`.
Parent and child entities are typed independently. Legacy `unknown`,
`laboratory`, `department`, and `institute` values are invalid in curated and
public data. `data/processed/institution_type_migration_report.csv` preserves
the migration's previous type, rule, evidence, aliases considered, and affected
unique-paper count.

Public and Admin surfaces use `web/institution_type_labels.js` to display
`research_unit` as **Research Institute**. Public JSON and downloaded CSV retain
the raw `research_unit` machine value for reproducibility and backward
compatibility; the display label is not a serialized enum migration.

`institution_locations.csv` owns location only and references `institution_id`.
Coordinate edits cannot change that ID. A child without a location may inherit
the nearest confirmed parent location; its own row overrides inheritance.

`institution_aliases.csv` maps a reviewed alias to one canonical ID.
`author_institution_mappings.csv` stores the stable ID plus raw affiliation
evidence. Its existing `provenance_source` is normalized by the audit into
`manually_confirmed`, `admin_accepted`, `curated_import`, `automatic_import`,
or `unresolved`; legacy values remain valid and no data migration is required.
Reassignment is an explicit mapping or confirmed merge action.
`institution_audit_log.csv` records ignore and global merge impact and
confirmation. A trusted mapping's institution-ID replacement also appends a
`confirmed_mapping_changed` event with previous/new IDs, source, timestamp,
and user/action metadata. Location-only changes never create this event.
Admin resolution appends either `mapping_change_confirmed` or
`mapping_reverted`, including the queue ID, source audit ID, mapping ID, exact
old/new (and reverted) IDs and names, actor, note, evidence source/URL, and UTC
timestamp. The source audit ID makes suppression transition-specific: resolving
one change does not suppress a later change to the same mapping.
Parent and alias cycles are invalid.

`data/manual/institution_consistency_audit.csv` is a generated, reporting-only
second-layer audit. It compares explicit mappings with raw affiliation
evidence, aliases, parents, merge history, and public exports. Findings use
`confirmed_mapping_changed`, `author_institution_conflict`,
`suspicious_replacement`, `duplicate_institution`, `alias_missing`, or
`parent_child_inconsistency`, with low/medium/high severity. Findings include a
stable paper-author `review_group_id`, normalized provenance, classification,
blocking flag, and a human-readable explanation. Alias and confirmed
parent-child compatibility lower risk; strong evidence for an unrelated
organization can remain high even for a trusted mapping.

`data/curated/institution_review_queue.csv` is the persistent Admin queue. It
copies each finding's evidence and stable `audit_id`/`mapping_id`, then records
`finding_status`, resolution action/note, current-state flag, reviewer, and
timestamps. `finding_status` is a lifecycle field with exactly three values:
`open`, `resolved`, and `archived`; the specific outcome remains in
`resolution_action`. Re-auditing upserts evidence without overwriting human
outcomes; open findings that disappear, or whose mappings are excluded or
replaced, become `archived` while retaining their audit evidence. Mapping
corrections use the existing mapping service and are committed atomically with
queue resolution. The generated report is never edited to record an outcome.
The Admin API groups these immutable rows by paper and author at read time.
Resolving or ignoring a case applies the decision to every open child finding.
Legal resolution actions are `accept_suggestion`, `replace_mapping`, `ignore`,
`manually_resolved`, `keep_multiple_affiliations`, `mapping_change_confirmed`,
`mapping_reverted`, and the lifecycle/migration actions
`legacy_review_decision`, `resolved_by_reaudit`, `mapping_excluded`, and
`mapping_replaced`.
Only open findings are returned in the actionable Admin list. Resolved and
archived findings remain available in the read-only history section.
Only high `confirmed_mapping_changed` and `suspicious_replacement` findings are
publish blockers; naming variations and possible multiple affiliations are not.

## Overview

The project uses four core related CSV tables to represent papers, authors, institutions, and the affiliations connecting them, plus auxiliary manual correction tables. The schema is intentionally small and compatible with metadata commonly available from OpenAlex, Semantic Scholar, Crossref, arXiv, and manual research.

Files in `data/manual/` are human-maintained source-of-truth corrections and must not be overwritten by automated processing. Future collection scripts should preserve original API responses in `data/raw/`, write normalized output to `data/processed/`, and apply manual data as explicit overrides.

Use UTF-8 CSV files. Store booleans as `true` or `false`; leave a value empty when it is unknown. Stable project IDs should be used for relationships rather than names, because names can change or collide.

## `correction_backlog.csv`

`data/manual/correction_backlog.csv` is the auditable queue for known and suspected metadata corrections, regression cases, and scope decisions. It preserves local or cited evidence without applying changes to exports. A backlog row must be promoted deliberately into the appropriate manual override table only after its evidence, full paper coverage, and any required map location have been verified.

| Column | Definition |
| --- | --- |
| `item_id` | Stable backlog identifier. |
| `category` | Work group such as `confirmed_institution_correction`, `suspected_institution_correction`, or `scope_review`. |
| `title` | Paper title associated with the issue. |
| `year` | Publication year used to disambiguate the paper. |
| `problem_type` | Concise machine-readable issue type. |
| `current_problem` | Description of the currently observed error or uncertainty. |
| `expected_correction` | Expected outcome or specific question to resolve. |
| `evidence` | Local, publisher, paper, or other evidence already available for review. |
| `priority` | Review priority: `high`, `medium`, or `low`. |
| `status` | Workflow state such as `pending_override`, `needs_review`, `needs_full_paper_check`, or `implemented_regression_check`. |
| `notes` | Guardrails and additional review context. |

## `papers.csv`

One row represents one paper. This table stores bibliographic metadata, scope labels, and provenance for how the paper entered the dataset.

| Column | Definition |
| --- | --- |
| `paper_id` | Stable, project-assigned identifier for the paper; primary key. |
| `title` | Paper title as reported by the preferred source or confirmed manually. |
| `year` | Four-digit publication year. Leave empty if unresolved. |
| `venue` | Compatibility alias of the canonical `venue_name`; never includes year, edition, proceedings volume, acronym, or display formatting. |
| `venue_id` | Stable canonical venue-and-track identifier used for aggregation. |
| `venue_name` | Canonical full venue name without a duplicated acronym. |
| `venue_acronym` | Confirmed familiar acronym when one exists; otherwise empty. |
| `venue_type` | Controlled venue type: `conference`, `journal`, `preprint`, or `book`. Workshop venues use `conference`; workshop identity is encoded by `venue_track=workshops`. |
| `venue_track` | `main`, `workshops`, `findings`, `industry`, `demo`, `doctoral_consortium`, or explicit `other`. |
| `raw_venue` | Original unmodified source value retained through migration and later exports. |
| `doi` | Canonical DOI without a resolver URL when available. |
| `url` | Preferred public landing-page URL for the paper. |
| `arxiv_id` | arXiv identifier, including version only when the version matters. |
| `task` | Primary project task label: `detection`, `source_attribution`, `detection_and_source_attribution`, or `uncertain`. |
| `subtask` | Controlled reviewable label: `synthetic_image_detection`, `ai_generated_image_detection`, `deepfake_image_detection`, `generated_image_source_attribution`, `source_identification`, `source_verification`, `detection_and_source_attribution`, or `unknown`. |
| `entry_type` | Automatic, reviewable project-specific map-entry category: `method`, `dataset`, `benchmark`, `survey`, or `analysis`. It describes the entry's primary contribution, defaults to `method`, and is independent of `task`, `subtask`, and the formal OpenAlex `publication_type`. |
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
| `publication_type` | Controlled lowercase bibliographic type: `conference`, `journal`, `preprint`, or `book`. Legacy OpenAlex/Crossref values such as `article`, `journal-article`, and `proceedings-article` are normalized during ingestion and export; conference or proceedings evidence takes precedence over a generic legacy `article` source type. |

### Book metadata invariant

`scripts/publication_types.py` owns the authoritative `BOOK_INCOMPATIBLE_FIELDS`
list and the shared normalization policy. When `publication_type=book`, venue
identity/taxonomy fields (`venue`, `venue_id`, `venue_name`, `venue_acronym`,
`venue_type`, `venue_track`, `raw_venue`, aliases/labels and legacy venue
variants) and the paper category (`entry_type`, including legacy
`paper_type`/`category`) must be empty or absent. `publisher` remains a distinct,
compatible bibliographic field and must never be placed in `venue`.

The Admin UI confirms destructive clearing. Persistence defensively normalizes
invalid book payloads in the same atomic update, curated validation reports
historical violations, and curated/public export normalizes again after metadata
merges. This is deliberately a normalization policy, not payload rejection.
| `doi` | Canonical DOI without a resolver URL when available. |
| `arxiv_id` | arXiv identifier detected from source identifiers, a `10.48550/arXiv.*` DOI, or an arXiv location URL. |
| `arxiv_url` | Canonical `https://arxiv.org/abs/...` URL when an arXiv identifier can be extracted. |
| `has_arxiv_version` | `true` when a distinct arXiv identifier is detected, even if the paper also has a formal DOI and published venue. |
| `primary_url` | Preferred source landing URL, with DOI and OpenAlex URLs used only as later fallbacks. |
| `landing_page_url` | Landing page from the primary or best available OpenAlex location. |
| `openalex_url` | OpenAlex work URL/identifier retained for source provenance. |
| `is_arxiv_preprint` | `true` when an arXiv identifier, arXiv URL, or explicit arXiv source is detected. |

Published metadata and arXiv-version metadata are kept separate: a paper may have a formal DOI and venue while also exposing `arxiv_id`, `arxiv_url`, and `has_arxiv_version=true`. The publication year remains the OpenAlex publication year, not an inferred arXiv submission year. These values remain candidate metadata. A missing venue is left empty and flagged for manual review; venue or conference names must never be guessed from a paper title.

### Canonical venue resolution

`scripts/venues.py` is the single canonical venue resolver used by curated writes, migration, validation, admin metadata, and public export. It delegates the effective bibliographic type to `scripts/publication_types.py`: an intentional reviewed override wins when explicitly supplied, otherwise a confirmed canonical Conference, Journal, or Book venue wins over repository or arXiv signals; a repository type is used only when no confirmed formal venue exists. Public export resolves the canonical venue before its final paper/marker type synchronization, and validation rejects a confirmed venue/type conflict. `data/curated/venue_aliases.csv` is the explicit confirmed alias map, not a parallel paper or venue database. Matching is exact after deterministic Unicode, HTML-entity, whitespace, punctuation, year, proceedings-prefix, yearly-edition, and known proceedings-volume cleanup; fuzzy similarity never merges venues. Tracks remain part of the stable identity. Unknown aliases receive a conservative deterministic identity and `unmapped` audit status, while conflicting confirmed targets are reported as `ambiguous` and are not merged.

`scripts/migrate_venues.py` writes `docs/venue_migration_report.json` before an optional atomic `--apply`. It preserves `raw_venue`, writes the canonical fields into the existing curated paper rows, counts canonical paper identities, and is idempotent. Main and non-main tracks retain distinct `venue_id` values. Public JSON also carries `venue_aliases` for search, `venue_label` for the human-readable format `Canonical Full Name (ACRONYM) · Track`, and metadata containing the shared publication-type order `conference`, `journal`, `preprint`, `book`; none of these display fields replaces canonical identity.

`entry_type` is deliberately narrow. Anti-forensics, evasion, adversarial attacks, and robustness describe research topics; challenges, competitions, shared tasks, and challenge tracks describe evaluation or publication contexts. They are not entry types and normally remain `method` unless the title strongly identifies a dataset, benchmark, survey, or analysis contribution. Future secondary fields such as `topic_tags` or `contribution_tags` may represent those details, but they are not part of `entry_type` now.

## `paper_arxiv_links.csv`

`data/manual/paper_arxiv_links.csv` is a separate, partial and resumable manual-review table produced by `scripts/enrich_papers_arxiv.py`. It records known or conservatively suggested arXiv versions without rewriting candidate metadata or proving that an unlinked paper has no arXiv version. The file may contain only the portion of the candidate collection processed so far.

| Column | Definition |
| --- | --- |
| `title` | Candidate paper title used for review and title matching. |
| `year` | Formal publication year; never replaced with the arXiv submission year. |
| `doi` | Formal publication DOI when available. |
| `openalex_url` | OpenAlex provenance URL for the candidate paper. |
| `venue` | Formal publication venue when available. |
| `authors` | Published author list used as optional match evidence. |
| `arxiv_id` | Reused or conservatively matched valid arXiv identifier. |
| `arxiv_url` | Canonical arXiv abstract URL. |
| `arxiv_year` | Year encoded in the arXiv identifier, retained only as diagnostic metadata. |
| `match_status` | `linked_to_arxiv`, `possible_arxiv_match`, `not_searched`, or `not_found_in_arxiv`. |
| `title_similarity` | Normalized-title similarity between the paper and the best arXiv candidate. |
| `author_overlap` | Jaccard overlap of normalized author surname/initial keys when both sources provide authors. |
| `match_reason` | Human-readable evidence or uncertainty for the status. |
| `source` | Identifier origin: candidate metadata, key-paper enrichment, arXiv API, or not queried. |
| `manual_review` | Always `true`; all links and suggestions remain reviewable. |

`not_searched` means that partial enrichment has not queried the row yet. `not_found_in_arxiv` means only that the current query returned no result. Neither status is proof that no arXiv version exists. In exports, "without known arXiv version" therefore means only that the project does not currently hold an arXiv ID or URL for the paper.

Candidate-map and public-preview exports apply only `linked_to_arxiv` rows that contain an arXiv ID or URL. They match by OpenAlex URL when the enrichment row provides one, otherwise by DOI, otherwise by normalized title plus publication year. The resulting `arxiv_id`, `arxiv_url`, and `arxiv_year` fields describe a known arXiv version and do not replace formal publication year, DOI, venue, OpenAlex URL, or `publication_type`. `has_arxiv_version` means an ID or URL is known regardless of formal publication. "Preprint-only" instead describes a record whose publication itself is a preprint without a known formal venue; it is never inferred merely from the existence of an arXiv version.

## `arxiv_link_enrichment_report.csv`

`data/manual/arxiv_link_enrichment_report.csv` is the reviewable audit output
from `scripts/enrich_papers_arxiv.py`. Before making network queries, the script
compares formally published rows without direct arXiv metadata against local
rows that contain valid arXiv identifiers. Automatic linking requires an exact
normalized title, author-key Jaccard overlap of at least `0.80`, and one unique
best arXiv identifier. Exact DOI matches returned by arXiv are also sufficient.
Title-only, low-author-overlap, or ambiguous candidates use
`action=needs_review` and do not populate an empty link.
Previously cached `possible_arxiv_match` API suggestions are also carried into
this report so unresolved candidates remain visible across resumable runs.

| Column | Definition |
| --- | --- |
| `paper_id` | OpenAlex work ID of the formal publication when available. |
| `title` | Formal publication title. |
| `existing_doi` | DOI retained on the formal publication. |
| `matched_arxiv_id` / `arxiv_url` | Candidate arXiv version. |
| `match_basis` | `doi`, `exact_title_author`, or `normalized_title_author`. |
| `confidence` | `high`, `medium`, or `low`. |
| `action` | `filled`, `needs_review`, or `skipped` when the confirmed link already existed. |
| `note` | Evidence summary, including author overlap or ambiguity. |

## `paper_abstracts.csv`

`data/manual/paper_abstracts.csv` is an optional manual/cache layer for original paper abstracts. It is never populated by an AI summary and automated exports treat it as read-only. Rows match in priority order by DOI, arXiv ID, OpenAlex URL, then normalized title plus publication year. Manual rows take precedence over abstract text already present in processed candidate metadata and locally cached raw OpenAlex abstracts.

| Column | Definition |
| --- | --- |
| `title` | Paper title used only for the final title/year matching fallback. |
| `year` | Publication year required when title matching is used. |
| `doi` | DOI, with or without a resolver URL. Strongest match key. |
| `arxiv_id` | arXiv identifier or arXiv URL. Version suffixes are ignored for matching. |
| `openalex_url` | OpenAlex work URL. |
| `abstract` | Original abstract text copied from the identified metadata or official paper source. Never generated to fill a gap. |
| `abstract_source` | Provenance such as OpenAlex, Crossref, arXiv, publisher, or a named manual source. |
| `notes` | Review and provenance notes. |

Map records expose `abstract` and `abstract_source`. When no original abstract is available, `abstract` remains empty and the frontend displays it as unavailable. `ai_summary` is a separate optional generated-content field. It must be clearly labeled as AI-generated, must retain its own provenance in any future schema extension, and must never be substituted for or represented as the original abstract.

### Map-Ready Author Fields

| Field | Definition |
| --- | --- |
| `authors` | Full paper-level author list copied from `authors_ordered` and kept in the original OpenAlex authorship order for every institution record. It is never rebuilt or reordered by institution. |
| `institution_authors` | Authors affiliated with the institution represented by the current map record. Names use the paper-level display form and follow the same original paper order. The field is an empty list when the relationship cannot be determined conservatively. |

Institution-specific authors are derived from the paper-author-institution rows. Matching prefers an exact OpenAlex institution identifier, then an exact ROR identifier, and finally an exact normalized full institution name. Substring and fuzzy name matching are not used. An author with multiple affiliations appears in `institution_authors` for every corresponding institution record, while the full `authors` list stays identical across those records.

## `institution_author_overrides.csv`

`data/manual/institution_author_overrides.csv` records human-verified corrections to institution-specific author attribution when source authorship-to-institution links are incomplete. The map exporter applies this manual layer while generating institution records; it does not alter raw OpenAlex data, processed CSVs, or the paper-level `authors` field.

| Column | Definition |
| --- | --- |
| `title` | Paper title used for exact normalized-title matching. Required. |
| `year` | Publication year to match when provided. May be empty. |
| `institution` | Institution display name used for exact normalized-name matching. Required. |
| `authors` | Semicolon-separated institution author names. The exporter preserves this order and replaces the generated `institution_authors` list. |
| `notes` | Human-readable correction rationale or provenance. |

Title and institution normalization lowercases text, replaces punctuation with spaces, and collapses whitespace. Matching is exact after normalization; no substring or fuzzy matching is used. Export summaries report loaded, applied, and unmatched overrides so stale or misspelled corrections remain reviewable. Scripts must treat this file as read-only manual input.

## `institution_record_overrides.csv`

`data/manual/institution_record_overrides.csv` corrects generated institution markers for a matched paper when its paper-level affiliations or geocoded institutions are wrong. This is an auditable manual export layer: it does not modify raw OpenAlex responses, processed affiliation rows, caches, or other manual tables. OpenAlex-resolved institutions are fallback metadata, not final ground truth; confirmed paper or publisher evidence belongs in this explicit correction layer.

| Column | Definition |
| --- | --- |
| `title` | Paper title used for exact normalized-title matching. Required. |
| `year` | Pre-override publication year used with the title to identify the paper. Required. |
| `mode` | `replace` removes all matched paper records and creates exactly the grouped override rows; `add` retains existing records and adds this institution when absent; `remove` deletes exact normalized matches for this institution. |
| `institution` | Canonical institution name only. Required. Do not include a department, school, laboratory, street address, city, or raw affiliation string. |
| `city` | Correct city, when known. |
| `region` | Correct region or administrative area, when needed. |
| `country` | Correct country display name. |
| `country_code` | Correct country code. |
| `latitude` | Verified institution latitude. May be blank only when no reliable local coordinate source exists. |
| `longitude` | Verified institution longitude. Must be supplied together with latitude or left blank with it. |
| `institution_authors` | Semicolon-separated authors affiliated with this institution. |
| `address` | Optional official street or campus address, kept separate from the canonical institution name. |
| `evidence` | Optional raw affiliation, paper, publisher, or local metadata evidence supporting the correction. |
| `notes` | Human-readable provenance and reason for replacement. |

Implementations also accept optional `doi` and `openalex_url` columns as stronger paper identity evidence when a manual table includes them; they are not required by the base schema above.

Rows with the same normalized title and year form one paper replacement. Matching begins with normalized title plus year or an optional DOI/OpenAlex URL, then expands to every generated record sharing the matched DOI or OpenAlex URL. Modes run deterministically as `replace`, then `remove`, then `add`. In `replace` mode, both map and public-preview exporters remove the complete matched record set before creating one record per manual row. `remove` uses exact normalized institution-name matching within the matched paper. `add` is idempotent: it does not duplicate an institution already present for that paper. Replacement and addition records retain paper-level title, authors, DOI, venue, publication type, paper and OpenAlex URLs, arXiv metadata, task labels, entry type, confidence, and review fields. Only institution identity, institution authors, location, coordinates, marker ID, and institution-resolution method are changed.

Coordinate-pending `replace` or `add` rows remain part of candidate export data with null coordinates and are counted explicitly. The normal public-preview location filter excludes them until verified coordinates are supplied; `--include-missing-location` remains available for deliberate review exports. Departments and complete official affiliations belong in `evidence`, street addresses in `address`, and city/region/country in their dedicated fields. They must never be folded into `institution`.

## `institution_record_review_queue.csv`

`data/manual/institution_record_review_queue.csv` is generated by the local-only `scripts/audit_institution_records.py` audit. Each row is a review candidate, not an accepted correction. It records the paper, author, resolved institution/country, raw affiliation text, controlled reason, suggested action, optional suggested institution, confidence, and notes. Low-overlap and country-conflict findings must be verified manually before any corresponding row is added to `institution_record_overrides.csv`.

## `institution_paper_risk_report.csv`

`data/manual/institution_paper_risk_report.csv` is the paper-level human-review priority report produced by `scripts/build_institution_risk_report.py`. It aggregates local candidate affiliations, row-level review signals, the correction backlog, and confirmed overrides. `risk_score` is a bounded heuristic priority score, not a probability, correctness judgment, or automatic correction.

| Column | Definition |
| --- | --- |
| `title` | Candidate paper title. |
| `year` | Candidate publication year used with the normalized title as the paper key. |
| `risk_score` | Explainable review-priority score from 0 to 100. |
| `risk_level` | `high` for scores 60 or above, `medium` for 25–59, and `low` below 25. |
| `main_reasons` | Distinct local signals that produced or reduced the priority. |
| `current_institutions` | Unique currently resolved institutions across the paper's affiliation rows. |
| `current_countries` | Unique currently resolved countries or country codes. |
| `current_institution_authors` | Current institution-to-author grouping assembled from local affiliation rows. |
| `raw_affiliation_evidence` | Deduplicated raw affiliation and correction-backlog evidence for review. |
| `review_action` | Recommended human review step; never an automatic correction. |
| `notes` | Backlog/override status and the heuristic-score disclaimer. |

Paper scoring uses the maximum row-level risk rather than summing author rows. A small capped bonus applies only when multiple distinct high-risk reason types occur, so repeated low-risk author rows cannot make a paper high risk. Confirmed manual overrides lower non-actionable cases to regression-check priority. Confirmed but incomplete corrections and suspected backlog cases remain high priority until their evidence and full author mapping are resolved.

### Map-Ready Location Fields

| Field | Definition |
| --- | --- |
| `country` | Public country display name. Hong Kong, Macau/Macao, and Taiwan records use `China`. |
| `country_code` | Public country code. The three normalized regions use `CN`. |
| `region` | Canonical regional display name: `Hong Kong`, `Macau`, or `Taiwan` when applicable; otherwise empty unless another source region is explicitly retained. |
| `region_code` | Regional code `HK`, `MO`, or `TW` when applicable. |
| `raw_country` | Country value received from resolved or source affiliation metadata before public normalization. |
| `raw_country_code` | Country code received from source affiliation metadata before public normalization. |

Country/region normalization happens only in map-ready and public-preview exports. Raw OpenAlex responses, processed affiliation CSVs, geocoding caches, and manual data are not rewritten.

## `key_papers.csv`

`data/manual/key_papers.csv` is a human-maintained, in-scope coverage checklist. One row identifies a paper that should be checked against automatic candidate retrieval and public-preview publication; checklist membership does not automatically add or publish the paper. OpenAlex candidate data is a metadata source rather than coverage ground truth, so an absent key paper is an import/enrichment gap, not an out-of-scope decision.

| Column | Definition |
| --- | --- |
| `title` | Clean paper title extracted from a source document or entered manually, without trailing venue/year annotations. |
| `year` | Four-digit publication year taken from the entry or its nearby year heading when available. |
| `authors` | Author line in the order written in the source document. The importer does not reorder authors. |
| `doi` | DOI, preferably in canonical form without a resolver URL. |
| `arxiv_id` | arXiv identifier; version suffixes are optional for coverage matching. |
| `openalex_url` | OpenAlex work URL when known. |
| `paper_url` | Preferred public paper or landing-page URL for human review. |
| `expected_task` | Expected scoped task: `detection`, `source_attribution`, or `detection_and_source_attribution`. |
| `source_doc` | Filename of the Word document from which the entry was imported. Multiple filenames may be retained for duplicate entries. |
| `section` | Nearest document section, such as `Identification`, `Verification`, `Benchmark`, `Dataset`, `Survey`, or `Anti-forensics`. |
| `notes` | Free-text coverage context, uncertainty, follow-up notes, and extracted source hints such as `source_suffix=QPAIN, 2026` or `source_alias=(ZED)`. |

The DOCX importer reads local files from `data/manual/source_docs/`, removes trailing venue/year suffixes from paper titles, records removed suffixes in `notes`, and deduplicates imported entries by cleaned normalized title plus year. Auxiliary benchmark, dataset, survey, and anti-forensics/evasion entries remain in the checklist with explicit notes. DOI, arXiv, OpenAlex, and paper URL fields stay empty unless the source document explicitly supplies them.

The coverage audit reports where each key paper is present in the OpenAlex candidate pool, candidate map, and public preview. Its statuses describe coverage/export gaps only and never use `out_of_scope`. Missing papers require import or metadata-enrichment review; non-exported papers require affiliation, coordinate, public-preview-filter, or export-rule diagnosis. The checklist is manually curated, so OpenAlex linkage or pipeline coverage does not determine scope or validity. Importing or manually adding a checklist row never publishes it to the map.

With the broad-coverage preview, the audit distinguishes paper-level visibility from map-marker visibility. `covered_in_public_preview_paper_list` means the paper appears in the public preview's searchable paper list, while `covered_as_map_marker` means at least one institution record has usable coordinates and appears on the map. `missing_affiliation` and `missing_coordinates` are review states, not scope decisions.

## `web/data/public_preview_papers.json`

`web/data/public_preview_papers.json` is the paper-level public preview export. It is generated by `scripts/export_public_preview.py` from local candidate metadata, the key-paper checklist, and local manual/cache enrichment files. It is designed to broaden website coverage while keeping the map marker export strict.

Both public-preview JSON outputs include the same `metadata.public_preview_generated_at` value. `scripts/export_public_preview.py` computes this authoritative successful-export instant once in second-precision UTC ISO 8601 form (`YYYY-MM-DDTHH:MM:SSZ`), adds it to both proposed payloads only after the identity-level shrinkage guard passes, validates the pair in memory, and transactionally replaces both JSON files. If either replacement fails, the exporter restores every already-replaced output. A dry run, validation failure, or shrinkage-guard failure does not change either checked-in timestamp. The public header formats the stored UTC calendar date deterministically as `Last updated: D Month YYYY`; it never uses browser time, page-load time, Git history, or filesystem metadata. Legacy files without the field remain readable and the header omits the label gracefully, while the validator rejects one-sided, malformed, or inconsistent timestamps.

Each record is one paper and may include:

| Column | Meaning |
| --- | --- |
| `title`, `year`, `publication_year`, `authors`, `venue`, `doi`, `paper_url`, `openalex_url` | Paper-level bibliographic metadata from local candidate sources and manual override layers. |
| `arxiv_id`, `arxiv_url`, `arxiv_year`, `has_arxiv_version` | Known arXiv-version metadata when present locally. |
| `abstract`, `abstract_source` | Original abstract metadata from local/manual caches; empty when unavailable. |
| `task`, `subtask`, `entry_type`, `publication_type` | Candidate classification and publication metadata. |
| `has_map_location` | `true` when at least one public preview map marker exists for the paper. |
| `map_record_count` | Count of public preview marker records tied to the paper. |
| `aggregated_locations` | Ordered canonical institution/location objects. Each object keeps `institution_name`, `institution_id`, normalized `country`/`country_code`, `region`/`region_code`, and the explicit `location_display` pair together. |
| `aggregated_institutions`, `aggregated_country_names`, `aggregated_country_codes`, `aggregated_regions`, `aggregated_region_codes` | First-occurrence-deduplicated summaries derived from `aggregated_locations`; these lists are never independently sorted. Blank regions are omitted without changing institution or country order. |
| `missing_affiliation` | `true` when the paper lacks usable local affiliation records for map export. |
| `missing_coordinates` | `true` when affiliation evidence exists but usable coordinates are still missing. |
| `needs_review` | `true` when candidate metadata, affiliation, or coordinates still require review. |
| `coverage_status` | One of `map_ready`, `missing_affiliation`, `missing_coordinates`, or `paper_only_review`. |

Paper-level preview records without coordinates must not be converted into markers or assigned locations unless affiliation and coordinate evidence is added through the normal auditable workflow.

## `key_papers_enriched.csv`

`data/manual/key_papers_enriched.csv` is a separate OpenAlex-linkage output. It preserves every checklist field, including the original title and author text, then adds the following columns immediately after `notes`:

| Column | Definition |
| --- | --- |
| `openalex_link_status` | `linked_to_openalex`, `possible_openalex_match`, `not_found_in_openalex`, or `skipped`. These values describe metadata linkage, not paper validity. |
| `openalex_link_reason` | Title/year evidence, ranking explanation, or skip reason for the linkage status. |
| `search_strategy_used` | OpenAlex strategy that returned the reported candidate: `search`, `search.title`, `search.title_and_abstract`, `title.search`, or `title_and_abstract.search`. |
| `candidate_source_query` | Sanitized query value used by the candidate's source strategy, including the field prefix for filter searches. |
| `title_similarity` | Normalized-title similarity for the reported OpenAlex candidate. |
| `candidate_title` | Best candidate title returned by OpenAlex. |
| `candidate_year` | Best candidate publication year returned by OpenAlex. |
| `candidate_openalex_url` | Best candidate OpenAlex work URL. |
| `candidate_doi` | Best candidate DOI when OpenAlex provides one. |
| `candidate_paper_url` | Best candidate landing page or PDF URL when available. |
| `enriched_openalex_url` | Automatically accepted OpenAlex URL; populated only for `linked_to_openalex`. |
| `enriched_doi` | Automatically accepted DOI; populated only for `linked_to_openalex`. |
| `enriched_paper_url` | Automatically accepted paper URL; populated only for `linked_to_openalex`. |

Possible candidates remain review suggestions and do not populate `enriched_*` identifiers. The coverage audit can use accepted `enriched_openalex_url` and `enriched_doi` values when this enriched CSV is supplied as its checklist input.

Coverage audit statuses are `covered_in_public_preview`, `covered_in_candidates_only`, `possible_pipeline_match`, and `not_covered_by_pipeline`. The last status means only that current automatic retrieval and visualization did not cover the checklist paper; it is not a rejection of the manually curated entry.

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

### Curated institution review and aliases

`data/curated/institution_location_review.csv` keeps raw institution evidence and an authoritative `review_status`: `confirmed`, `pending_review`, `needs_coordinates`, `ambiguous`, `alias_candidate`, `alias_of_confirmed`, `ignore`, or `excluded`. Legacy location/coordinate diagnostics remain secondary fields.

`data/curated/institution_aliases.csv` has `alias_name`, `canonical_institution_name`, `alias_language`, `alias_source`, `review_status`, and `notes`. Alias targets must exist in `institution_locations.csv`. Duplicate mappings are invalid, and one normalized alias pointing to multiple canonical institutions is ambiguous. Confirmed aliases resolve to the canonical public name and coordinates; no alias is exported as a separate node.

Public-preview JSON includes an additive top-level `institution_aliases` array containing confirmed alias display text, canonical display text, the stable `canonical_institution_id`, language, and provenance source. For backward compatibility, an active canonical name ending in a unique trailing acronym also exports its exact pre-acronym form with `alias_source=legacy-canonical-name`; this rule does not infer similar names or parent/child relationships. It also includes `canonical_institution_search_index`, an object keyed by active canonical institution ID. Each entry contains `canonical_name`, the reviewed display `names` used for search, and their `normalized_names`; merged, ignored, and deprecated institutions are not keys. A confirmed merge-source name remains searchable only as an alias of its active canonical target.

Public search normalizes only lookup text (Unicode normalization and accent folding, case folding, punctuation, hyphens, and repeated whitespace); displayed names are unchanged. The institution branch matches the normalized full query as an exact name or phrase substring against the canonical index and converts every match to canonical institution IDs. It does not split institution names into loose OR tokens. Title, author, publication venue, task, year, and known arXiv-version metadata remain a separate branch, and all downstream map records, paper coverage, statistics, result views, markers, and CSV export derive from the same filtered canonical record sets.

The public filters are ordered Keyword, Task, Paper Type, Publication Type, Publication Venue, Country, Institution Type, Record Version, and Publication Year. Every unfiltered select displays `All`. Publication Venue depends on Publication Type and uses canonical venue identities. Record Version is independent of Publication Type: it filters only whether a known arXiv alternate version exists, and deliberately has no Preprint/Published options.

The public alias array combines confirmed rows from `institution_aliases.csv` with review rows that have an explicit `canonical_institution_name` and `review_status=confirmed` or `alias_of_confirmed`. Ambiguous, pending, rejected, and merely similar names are excluded. The additive `institution_id_redirects` object maps merged legacy IDs from `institution_audit_log.csv` to their final active canonical IDs. Before writing public JSON, every map record, paper affiliation, current-institution object, and paper institution aggregate is resolved by active or redirected ID first and by the public alias map only as a fallback. Duplicate records are removed by canonical paper–institution pair. Additive `source_institution`, `source_institution_id`, and `source_institution_names` fields retain the pre-canonical public source values; curated and raw source rows are not rewritten.

`data/curated/institution_hierarchy.csv` stores reviewed parent/child relationships separately from aliases. Each row uses stable `parent_institution_id` and `child_institution_id`, `relationship_type=affiliated_institute`, `review_status=confirmed`, and evidence fields. Both IDs must refer to confirmed canonical locations; self-links, duplicates, cycles, and unconfirmed rows are invalid. Public-preview JSON exposes the confirmed subset as additive `institution_hierarchy` metadata with canonical display names. Exact selection of a top-level confirmed parent automatically expands filtering to all confirmed descendants, while selection of a specific child remains exact. Hierarchy affects only the filter set: it never changes canonical identities, affiliation content or numbering, or default institution aggregations.

The local admin institution queue computes conservative alias/duplicate suggestions from queued evidence and confirmed canonical rows. It shows candidate location/coordinates, existing aliases, affected mappings and papers, name-match evidence, and country conflicts. Suggestions are read-only until the reviewer confirms an alias. Rejecting/ignoring a suggestion changes no alias or canonical row, and the queue never merges canonical institutions or reassigns mappings automatically.

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

## `paper_version_overrides.csv`

`data/manual/paper_version_overrides.csv` records manually confirmed alternate paper versions, such as an arXiv version of a formally published paper when OpenAlex represents the two versions as separate Works. Export scripts read this table as an override layer; they do not overwrite processed candidate CSVs.

| Column | Definition |
| --- | --- |
| `published_openalex_url` | OpenAlex URL for the published record to annotate. This is the strongest match key. |
| `published_doi` | DOI for the published record, without changing or replacing the published DOI in exports. |
| `title` | Published paper title used as a conservative fallback match key. |
| `arxiv_id` | Manually confirmed arXiv identifier for an alternate version. |
| `arxiv_url` | Manually confirmed arXiv abstract URL. |
| `notes` | Provenance or explanation for the override. |

When an override matches by OpenAlex URL, DOI, or normalized title, map and public-preview exports attach `arxiv_id`, `arxiv_url`, and `has_arxiv_version=true`. The published venue, publication year, DOI, and primary paper URL are preserved. An arXiv override does not by itself make a published venue record a preprint-only record.

## `publication_overrides.csv`

`data/manual/publication_overrides.csv` is an auditable correction layer for papers whose candidate metadata describes an arXiv or preprint record even though a formal publication is known. Exporters read this file without changing raw OpenAlex responses, processed candidate CSVs, or arXiv enrichment data.

| Column | Definition |
| --- | --- |
| `title` | Paper title used for exact normalized-title matching. Required. |
| `match_year` | Optional pre-override candidate year. When present, the title match is accepted only when the record currently has this year. |
| `formal_year` | Correct formal publication year written to `year` and `publication_year`. Required. |
| `formal_venue` | Correct formal venue written to `venue` and `venue_name`. |
| `formal_doi` | Correct formal publication DOI. |
| `formal_paper_url` | Preferred formal publication landing page, written to the map/public URL aliases including `paper_url` and `primary_url`. |
| `publication_type` | Correct formal publication type, using the canonical values `conference`, `journal`, `preprint`, or `book`; legacy provider values such as `Article` are accepted only as migration input and normalize to `journal`. |
| `notes` | Human-readable provenance and reason for the correction. |

Matching uses normalized title and, when supplied, `match_year` against the record before the override. A match replaces only formal display/publication metadata. It preserves the OpenAlex URL and all `arxiv_id`, `arxiv_url`, `arxiv_year`, and `has_arxiv_version` values. A formal venue means the record is no longer preprint-only even though its arXiv version remains known.

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

Affiliation is a property of an author's relationship to a particular paper, not a permanent property of either the author or paper. Researchers move between institutions, papers can have many authors, and one author can list several affiliations on the same paper. Paper-level or first-author-only locations would discard this information and misrepresent collaboration geography. Relationship-level records preserve every reported affiliation, author order, corresponding-author status, and original affiliation text while supporting accurate institution and map views. Map exports create a marker for every affiliated institution with usable coordinates, but every marker reuses the same paper-level `authors_ordered` list and separately derives `institution_authors`. Both fields follow original paper order. Institution grouping never sorts, groups, or truncates the full display author list, and it does not replace or collapse the underlying relationship rows.

## Curated author–institution mapping evidence

`data/curated/author_institution_mappings.csv` keeps the reviewable paper-level grouping used by the admin and exporter. In addition to the canonical `institution` and `institution_authors`, imported candidates preserve `author_order`, `raw_affiliation`, `openalex_institution_id`, source city/country/latitude/longitude, and `provenance_source`. Missing coordinates never remove a candidate. Unmatched institutions use `mapping_status=needs_review`; confirmed canonical or alias matches may use `active`.

Public paper and marker records expose one stable author mapping field,
`author_affiliation_indices`. Each entry contains the display `author`, one-based
`indices` into the record's `affiliations` list, corresponding
`institution_ids`, a `source`, and a boolean `fallback`. Source priority is
`curated_admin`, `canonical_author_mapping`, `raw_affiliation`, then
`paper_institution_fallback`; an unresolved author is retained with
`source=unmapped` and an empty index list. A fallback is never labeled as a
confirmed curated mapping. The legacy `author_institution_affiliations` and
`author_institution_indices` fields remain temporarily for older consumers.
Public marker records also expose `institution_id`; the frontend falls back to
a normalized canonical institution name only for legacy records.

## Confirmed paper-version merges

`data/curated/paper_version_merges.csv` records reviewed duplicate-version decisions without deleting source data. Each row identifies a canonical formal publication and a duplicate version independently by OpenAlex URL, DOI, arXiv ID, or normalized title plus year. `status=confirmed_duplicate` and `is_active=true` are required before the exporter acts.

During export, the formal publication keeps its title, year, venue, DOI, OpenAlex URL, paper URL, and author order. The duplicate contributes arXiv ID/URL, an abstract when the canonical abstract is missing, and usable affiliation evidence. Its title, year, DOI, arXiv ID/URL, and OpenAlex URL remain traceable in the canonical record's `merged_versions` array. Duplicate markers are rewritten to the canonical paper identity and deduplicated by institution. `needs_review` and `distinct` rows are audit outcomes only and never trigger a merge.

`docs/arxiv_published_duplicate_audit.csv` is a review report generated by `scripts/audit_arxiv_published_duplicates.py`. Candidate scoring combines normalized-title similarity, author overlap, year distance, venue/version type, shared identifiers, abstract similarity, and task labels. Similarity alone never creates a curated merge.

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
