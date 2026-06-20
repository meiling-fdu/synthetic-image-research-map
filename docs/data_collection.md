# Data Collection

## OpenAlex Candidate Search

`scripts/search_openalex.py` is an early collection tool for discovering possible papers through the OpenAlex Works API. It uses only the Python standard library and searches precise AI-generated/synthetic image detection and source-attribution queries, or custom queries supplied in a text file. Broad generative-model or generic-attribution queries are intentionally omitted.

### Default Query Groups

The default search list is organized into two focused groups. The exact query string used for each request is retained in the raw-data manifest.

**Detection queries**

- `AI-generated image detection`
- `synthetic image detection`
- `generated image detection`
- `GAN-generated image detection`
- `diffusion-generated image detection`
- `detecting AI-generated images`
- `detecting synthetic images`
- `fake image detection generative AI`
- `deepfake image detection`
- `forensic detection of generated images`

**Source attribution queries**

- `AI-generated image source attribution`
- `synthetic image source attribution`
- `generated image source attribution`
- `source attribution of AI-generated images`
- `source attribution of synthetic images`
- `forensic attribution of generated images`
- `generated image provenance`
- `source identification of generated images`
- `source verification of generated images`
- `which model generated this image`

Broad queries such as `model attribution`, `generative model attribution`, generic `generator attribution`, and `attribution methods` are deliberately excluded. They commonly retrieve work on feature or saliency attribution, authorship attribution, camera or sensor attribution, and other adjacent topics. Queries about synthetic-data augmentation, synthetic training data, or object detection with synthetic data are also excluded because generating training inputs is not the research target.

OpenAlex results are raw candidate records, not final curated project data. Broad search terms can retrieve irrelevant, duplicate, out-of-scope, or incorrectly described papers. Retrieval does not establish that a paper belongs in the map and does not confirm its task label, authors, institutions, or affiliations.

Every candidate must be reviewed manually before any corresponding record is added to `data/manual/`. Automated collection writes only to `data/raw/openalex/` by default. It never writes to the manual CSV files.

## Dry Run

Always inspect the planned queries first from the repository root:

```bash
python3 scripts/search_openalex.py --dry-run
```

Dry-run mode prints the encoded OpenAlex URLs but makes no network requests and writes no files. A custom UTF-8 query file can contain one query per line; blank lines and lines beginning with `#` are ignored:

```bash
python3 scripts/search_openalex.py \
  --dry-run \
  --queries-file docs/example_queries.txt \
  --max-results 100
```

`--max-results` is the maximum number of candidates requested for each query. `--output-dir` controls the non-dry-run raw output location and defaults to `data/raw/openalex/`.

## API Key

The script reads an optional OpenAlex API key from the `OPENALEX_API_KEY` environment variable. Never place a key in source code, query files, documentation, or committed data.

For the current shell session on macOS or Linux:

```bash
export OPENALEX_API_KEY="your-key-here"
python3 scripts/search_openalex.py --dry-run
```

The key is redacted when dry-run URLs are printed and when request URLs are stored in raw archives. In non-dry-run mode it is sent only with the OpenAlex request.

## Raw Output

A non-dry run creates timestamped files under `data/raw/openalex/` by default. Each query receives one JSON archive containing the unprocessed OpenAlex response page or pages. A timestamped manifest records the query text, collection timestamp, output filename, retrieval status, and result count when available.

These files preserve automatic retrieval as candidate data. They must pass through a separate review and preprocessing workflow before any paper is promoted into the curated manual tables.

## Full Candidate Pipeline

`scripts/run_pipeline.py` orchestrates the existing scripts as subprocesses without duplicating their logic. The full order is:

1. Search OpenAlex and archive raw candidate responses.
2. Extract complete audit CSVs and separate in-scope paper and affiliation CSVs.
3. Resolve institutions only for in-scope affiliations by default.
4. Optionally geocode only unresolved in-scope affiliations.
5. Export map-ready JSON from the latest in-scope resolved/geocoded file.
6. Build the institution review queue from in-scope affiliation files.

Inspect every command without running it:

```bash
python3 scripts/run_pipeline.py --dry-run
```

Run a deliberately small batch:

```bash
python3 scripts/run_pipeline.py \
  --max-results 10 \
  --limit 5 \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)"
```

Use `--skip-search` after raw OpenAlex archives already exist locally. This avoids repeating the external search while still rebuilding extraction, resolution, optional geocoding, export, and review outputs. Other skip flags can disable resolution, geocoding, or review-queue generation; when generic geocoding runs after resolution, it reads the resolved affiliation CSV and skips rows whose working coordinates were already populated authoritatively.

The default handoff excludes out-of-scope papers before any institution API or geocoding request. `--include-out-of-scope` is an explicit debugging mode that sends the complete audit files through downstream steps. It should not be used for normal visualization exports.

The pipeline stops immediately when a subprocess fails and never commits or pushes changes. Its generated raw, processed, cache, map, and review files are ignored local artifacts for exploratory candidate analysis, not curated final data. Nothing in the pipeline writes to `data/manual/`.

## Raw-to-Processed Candidate Extraction

`scripts/extract_openalex_candidates.py` converts raw OpenAlex archives into four review-oriented CSV files:

- `data/processed/openalex_candidate_papers.csv` retains every deduplicated paper for audit.
- `data/processed/openalex_candidate_affiliations.csv` retains every author-institution row for audit.
- `data/processed/openalex_candidate_papers_in_scope.csv` contains only papers marked `in_scope=true`.
- `data/processed/openalex_candidate_affiliations_in_scope.csv` contains only affiliations whose `openalex_id` belongs to an in-scope paper.

Each paper receives an automatic, reviewable `material_type` from deterministic title-and-abstract rules. The allowed values are `research_paper`, `dataset`, `benchmark`, `survey`, `challenge`, `anti_forensics`, `auxiliary`, and `uncertain`. An explicit auxiliary source note is authoritative. Otherwise, strong survey/review terms take precedence; explicit challenges or competitions take precedence over benchmarks; anti-forensics/evasion terms take precedence over ordinary research; benchmarks take precedence over datasets; dataset/corpus/database terms identify dataset records; and narrow tool/resource phrases identify auxiliary records. A normal method or application paper defaults to `research_paper`. When duplicate source records produce incompatible special-purpose labels that the precedence rules cannot resolve, the merged result is `uncertain` rather than silently choosing one.

Material type does not replace or alter `preliminary_task` and `preliminary_subtask`, and no candidate is excluded merely for being a dataset, benchmark, survey, challenge, anti-forensics/evasion paper, or auxiliary record. The full and in-scope candidate paper CSVs both include the field. The map exporter carries it into every institution-level record, and public-preview export preserves it without changing the existing preview filters.

Preview extraction from the repository root without writing files:

```bash
python3 scripts/extract_openalex_candidates.py --dry-run
```

Write the processed candidates after inspecting the dry-run counts:

```bash
python3 scripts/extract_openalex_candidates.py
```

Custom locations can be supplied with `--input-dir` and `--output-dir`. The defaults are `data/raw/openalex/` and `data/processed/`.

The extractor deduplicates by OpenAlex ID and falls back to a normalized title when an ID is missing. It reconstructs available abstracts to apply preliminary task labels and a separate rule-based relevance filter. These automatic decisions can be wrong, especially for broad search results, so every paper and affiliation row remains `manual_review=true`.

### Publication Metadata Extraction

The candidate paper CSV preserves OpenAlex `publication_year` and `publication_date`, work type, DOI, source type, publisher/host organization, and several source URLs. `venue_name` prefers `primary_location.source.display_name`, then other explicit OpenAlex source or location fields. Missing venues stay empty, add a review note, and are never inferred from the paper title. The legacy `year`, `venue`, and `url` fields remain compatible aliases.

arXiv status is detected from OpenAlex arXiv identifiers, `10.48550/arXiv.*` DOI values, arXiv landing/PDF URLs, or an explicit arXiv source. When an identifier is available, the extractor stores both `arxiv_id` and a canonical `arxiv_url`, and sets `is_arxiv_preprint=true`. These signals are automatic source metadata and remain subject to review.

### Offline arXiv-version enrichment

Run `python3 scripts/enrich_papers_arxiv.py` to create the separate manual-review table `data/manual/paper_arxiv_links.csv`. The script does not call OpenAlex. It first reuses valid arXiv identifiers already present in candidate metadata or `key_papers_enriched.csv`; only papers without a known identifier are searched through the arXiv Atom API by normalized title.

Matches are conservative: near-identical titles can be linked directly, while less exact title matches require supporting author overlap. Plausible unsupported matches remain `possible_arxiv_match`. The formal publication year, DOI, and venue are preserved; `arxiv_year` is diagnostic and may be earlier than, equal to, or later than the publication year. Every row remains `manual_review=true`.

The output CSV is also a resume cache. Completed rows are reused by DOI, OpenAlex URL, or normalized title plus publication year unless `--force` is supplied. The script writes incremental atomic snapshots and saves partial results when interrupted or when arXiv returns an error. Use `--max-new-queries N` to cap new arXiv requests in a run; reused completed rows do not count toward that cap. With `--stop-on-rate-limit`, an arXiv HTTP 429 or equivalent throttling response saves the partial batch and exits successfully so the same command can resume later. Other useful review options include `--limit`, `--sleep-seconds`, and `--title-contains`.

“Without known arXiv version” means only that no version is currently recorded or found by this enrichment step; it is not proof that no arXiv version exists.

### Paper-Author-Institution Extraction

OpenAlex authorships are preserved in source order. The extractor writes that paper-level sequence to `authors_ordered` as a JSON list, using each author display name with the raw author name as fallback. It also writes one candidate affiliation row for every author-institution pair, including stable OpenAlex author and institution IDs, the one-based authorship-array order, source position, location metadata, ROR ID, and institution-specific raw affiliation text when available. Multiple authors at one institution remain separate rows, and authors with multiple institutions receive one row per institution.

Raw affiliation strings are retained even when OpenAlex supplies no structured institution. If an authorship has neither structured nor raw affiliation information, the author is still retained with empty institution fields, `manual_review=true`, and an explanatory note. This prevents first-author or first-institution shortcuts and preserves collaborators whose affiliations need later resolution.

### Rule-Based Relevance Filter

A candidate is marked `in_scope=true` only when its title or reconstructed abstract contains both an explicit generated-image term and a scoped task term, with no strong exclusion. Generated-image terms cover AI-generated, synthetic, generated, fake/deepfake, GAN-generated, diffusion-generated, text-to-image, and generative images. Standalone mentions of a GAN, diffusion model, generative model, or synthetic data are not sufficient.

Scoped task terms cover detection/detectors and generated-image source attribution, source identification, source verification, provenance, and forensic attribution. Generic `attribution`, model attribution, and generator attribution are not standalone inclusion rules. A generator-attribution phrase can contribute only when an explicit generated-image term is present in the same title or abstract.

Strong exclusions cover model, feature, saliency, explainable-AI, authorship, camera-model, and sensor attribution; object/change/anomaly/target detection; medical imaging or diagnosis; remote sensing and hyperspectral work; traffic-sign recognition; person re-identification; disease identification; data augmentation; synthetic training data; educational integrity; and AI-generated text detection. Range-image segmentation/classification is also excluded. Generic image segmentation, classification, or recognition is excluded unless an explicit generated-image term occurs close to a detection or generated-image source-attribution task, preventing incidental mentions of synthetic test images from admitting unrelated computer-vision papers. These records remain in the complete audit CSVs with an `exclusion_reason`, but do not enter scoped downstream processing.

The candidate paper CSV retains every record and adds `in_scope`, `relevance_score`, `relevance_reason`, and `exclusion_reason`. Scores are `2` when both required term groups match without an exclusion, `1` when only one required group matches, and `0` when neither group matches or an exclusion applies. Preliminary main labels are limited to `detection`, `source_attribution`, `detection_and_source_attribution`, and `uncertain`; automatic labels remain traceable suggestions rather than curated decisions.

Out-of-scope records are never deleted: they remain in the two complete candidate CSVs with their scores and reasons. Resolution, geocoding, review-queue generation, map export, and public-preview export use the scoped stream by default. Extraction summaries report total and in-scope paper and affiliation counts.

Processed candidate CSVs are not final curated data. A reviewer must verify relevance, labels, author identities, institutions, affiliations, and locations before manually adding any record to `data/manual/`. The extractor never writes to or updates the manual CSV templates.

## Key Paper Coverage Audit

`data/manual/key_papers.csv` is a lightweight, manually curated checklist of papers whose coverage should be monitored. It complements the OpenAlex query workflow; it is not an ingestion queue or a replacement for systematic retrieval. Checklist membership is independent of OpenAlex linkage and does not add that paper to candidate data, the map, or the public preview.

### Importing the checklist from Word documents

Place source `.docx` files under `data/manual/source_docs/`, then run:

```bash
python3 scripts/import_key_papers_from_docx.py
```

The standard-library importer reads Word ZIP/XML content without calling an API. Word list items and lines beginning with `·` are treated as paper entries; nearby year headings and immediately following author lines are retained when available. Detection documents default to `detection`, while Identification and Verification sections in attribution documents use `source_attribution`; titles that explicitly combine detection and attribution use `detection_and_source_attribution`. Benchmark, dataset, survey, and anti-forensics/evasion entries are retained with auxiliary notes.

The importer regenerates `data/manual/key_papers.csv` from the source documents by default, deduplicates by cleaned normalized title plus year, and records the source filename and section. Use `--preserve-existing` only when you intentionally want to merge existing checklist rows back into the generated output.

Title parsing removes trailing venue/year suffixes such as `QPAIN, 2026`, `CVPR, 2025`, `ICCV Workshop, 2023`, or `arXiv 20250404` while keeping meaningful punctuation inside the title, including colons and question marks. Removed suffixes are retained in `notes` as `source_suffix=...`; trailing aliases after a venue/year suffix, such as `(ZED)`, are retained as `source_alias=...`. Identifiers and URLs remain empty unless explicitly present in a source document. This is a manual coverage-checklist update only: it does not change candidate data, the public preview, or map publication status.

### Enriching checklist identifiers with OpenAlex

Imported checklist entries often contain only a title, year, and author line. To search OpenAlex by title and write a separate enriched checklist, run:

```bash
export OPENALEX_API_KEY="your-local-openalex-key"
python3 scripts/enrich_key_papers_openalex.py \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)" \
  --only-missing
```

By default, the script searches only rows missing a DOI or OpenAlex URL, requests 25 results per strategy, sorts by OpenAlex relevance score, waits at least 0.5 seconds between every request, and writes `data/manual/key_papers_enriched.csv` plus `docs/key_paper_enrichment_report.md`. It reads a local OpenAlex key from `OPENALEX_API_KEY`; `--api-key` can be used for one run and takes priority over the environment variable. Never commit or share the key. Debug and error request URLs redact `api_key`, and the key is not written to CSV or report output. Use `--limit` for a small review batch, `--per-page` to change the result count, and `--sleep-seconds` for a longer delay. The original `data/manual/key_papers.csv` is never overwritten.

If the output CSV already exists, enrichment resumes from it by default before any OpenAlex request is made. Existing output rows with `linked_to_openalex`, `possible_openalex_match`, or `not_found_in_openalex` are matched by normalized title plus year and reused without spending API budget. Use `--no-resume-from-output` to ignore the output cache, or `--force` to re-query selected rows. If OpenAlex stops the run with a fatal error such as HTTP 429, the script writes all processed, reused, and unprocessed rows to the output CSV, writes a partial report, and exits non-zero so the same command can be resumed later.

Lookup begins with the simple Works `search` parameter. If it yields no strong link, the script tries the OpenAlex-Web-like `search.title` and `search.title_and_abstract` query parameters, then the API filter forms `title.search` and `title_and_abstract.search`. Every strategy uses `sort=relevance_score:desc`, and retries stop as soon as a `linked_to_openalex` candidate is found. All parameter values pass through `urllib.parse.urlencode`, and wildcard/punctuation sanitization applies to every strategy. If no strategy produces a strong link, candidates from all attempts are deduplicated and ranked together. An HTTP 400 from one strategy is recorded as `strategy_failed` in `openalex_link_reason` and does not prevent the next strategy from running. `search_strategy_used` and `candidate_source_query` preserve how the reported candidate was retrieved.

The input may be either the original checklist or a previously enriched CSV. Retry only records that were not found in the previous run with:

```bash
python3 scripts/enrich_key_papers_openalex.py \
  --input data/manual/key_papers_enriched.csv \
  --output data/manual/key_papers_enriched.csv \
  --only-status not_found_in_openalex \
  --force \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)"
```

In-place updates to the enriched CSV are atomic. Field values for rows with completed statuses are preserved, and existing `linked_to_openalex`, `possible_openalex_match`, and `not_found_in_openalex` rows are not queried again unless `--force` is supplied. The script refuses any output path that would overwrite `data/manual/key_papers.csv`.

For a single-paper diagnostic retry, combine status and case-insensitive title filters:

```bash
python3 scripts/enrich_key_papers_openalex.py \
  --input data/manual/key_papers_enriched.csv \
  --output data/manual/key_papers_enriched.csv \
  --only-status not_found_in_openalex \
  --force \
  --title-contains "Forensic Invariant Learning" \
  --debug \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)"
```

Console output and `docs/key_paper_enrichment_report.md` report rows read, rows reused from existing output, rows selected, status-filter skips, rows queried from OpenAlex, newly linked/possible/not-found rows, and total HTTP requests. A separate title-filter skip count reconciles diagnostics that use `--title-contains`. Debug mode prints each strategy URL and HTTP status plus up to five candidate titles, years, and normalized-title similarities.

The script sanitizes a separate OpenAlex search query while preserving the checklist title and author text exactly. A candidate is `linked_to_openalex` when normalized-title similarity is at least 0.96 and its year differs by at most one when a checklist year is available. Multiple strong candidates are ranked by title similarity, year distance, DOI availability, paper-link availability, citation count, then API order; ambiguity is recorded in `openalex_link_reason`. Weaker candidates are `possible_openalex_match` and expose `candidate_*` fields without filling `enriched_*` identifiers. Other statuses are `not_found_in_openalex` and `skipped`.

OpenAlex enrichment links a manual checklist paper to external metadata; it does not validate the paper, change its curated status, or publish it. Accepted identifiers are written only to the separate `enriched_*` columns in `key_papers_enriched.csv`.

Run the read-only comparison from the repository root:

```bash
python3 scripts/audit_key_paper_coverage.py
```

To use accepted OpenAlex identifiers from enrichment, pass the separate enriched checklist:

```bash
python3 scripts/audit_key_paper_coverage.py \
  --key-papers data/manual/key_papers_enriched.csv
```

The script compares the checklist with `data/processed/openalex_candidate_papers.csv` and `web/data/public_preview_map_data.json`, then writes `docs/key_paper_coverage_report.md`. Confirmed matching uses accepted OpenAlex URL, DOI, arXiv ID, then normalized title and year. Exact title-only and high-similarity suggestions that need confirmation use `possible_pipeline_match`. The other statuses are `covered_in_public_preview`, `covered_in_candidates_only`, and `not_covered_by_pipeline`.

`not_covered_by_pipeline` means only that the current automatic candidate/public-preview workflow did not cover the manually curated checklist paper. It does not mean the paper is invalid or out of scope. The audit never publishes a checklist entry.

Use `--key-papers`, `--candidate-papers`, `--public-preview`, and `--output` to audit alternate local files. The audit never modifies its three inputs and never calls external APIs.

## Automatic institution resolution

`scripts/resolve_candidate_institutions.py` should run before generic geocoding. Its default input is `data/processed/openalex_candidate_affiliations_in_scope.csv`, so unrelated affiliations do not trigger authoritative API requests. It resolves candidate institutions from authoritative identifiers without fuzzy matching or generic location search. ROR IDs are tried first using the [ROR single-record API](https://ror.readme.io/docs/api-single), optional OpenAlex institution IDs are tried second using the [OpenAlex institution API](https://docs.openalex.org/api-entities/institutions/get-a-single-institution), and rows without identifiers may use only an exact normalized institution-name and country match already present in the local resolution cache.

Preview available identifiers and planned uncached requests without network access or file writes:

```bash
python3 scripts/resolve_candidate_institutions.py --dry-run
```

Run a small online batch with an identifying user agent:

```bash
python3 scripts/resolve_candidate_institutions.py \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)" \
  --limit 10
```

The script writes `data/processed/openalex_candidate_affiliations_resolved.csv`, `data/processed/institution_resolution_report.csv`, and `data/processed/institution_resolution_cache.json`. These generated files are ignored by Git. Blank working coordinate fields are filled from accepted authoritative results so the resolved affiliation CSV can be passed to the generic geocoder or exploratory map exporter, while the added `resolved_*` fields preserve explicit resolution provenance.

Resolution confidence has three levels:

- `high`: resolved through a ROR or OpenAlex institution identifier.
- `medium`: resolved through one unambiguous exact normalized name and country match in the authoritative cache.
- `low`: unresolved, missing coordinates, ambiguous, or otherwise weakly resolved.

Generic organization names remain reviewable unless a strong identifier resolves them. Country conflicts and missing coordinates also set `needs_review=true` and are explained in `resolution_notes`. Low-confidence records should enter the institution review queue. High-confidence results may be used for exploratory visualization, but every output remains candidate metadata and must not be treated as curated final data.

## Candidate Affiliation Geocoding

`scripts/geocode_candidate_affiliations.py` can add preliminary coordinates before map export. It reads the automatically resolved, in-scope `data/processed/openalex_candidate_affiliations_resolved.csv` by default, writes `data/processed/openalex_candidate_affiliations_geocoded.csv`, and stores reusable query results in `data/processed/geocoding_cache.json`. Out-of-scope rows do not produce Nominatim queries unless debugging is explicitly enabled.

Before consulting the cache or Nominatim, the script reads `data/manual/institution_corrections.csv`. A correction matches the candidate `institution_name` exactly after lowercasing, removing simple punctuation, and trimming and collapsing whitespace. No fuzzy matching is used, because automatically merging similar institution names could assign papers to the wrong organization or campus.

When a correction matches, its verified latitude and longitude replace automatic coordinates. Corrected institution, city, and country values are applied only when their fields are non-empty, so other source fields remain intact. The row is annotated with the correction source and confidence and remains `manual_review=true` for transparent provenance. Corrected rows never trigger an online geocoding request.

Documentation-only fictional correction example:

```csv
fictional institute,Fictional Institute of Visual Studies,Example City,Example Country,12.3456,78.9012,https://example.invalid/institution,high,Fictional format example only
```

Start with a dry run, which makes no network requests and writes no files:

```bash
python3 scripts/geocode_candidate_affiliations.py --dry-run
```

The dry run reports rows that would use manual corrections, rows with existing coordinates, rows needing online geocoding, unique uncached queries, and examples of institutions with no manual match. Queries use only the institution name, city, and country when available. Rows without enough location information are retained unchanged and flagged for manual review.

Online geocoding uses the public OpenStreetMap Nominatim search endpoint. Before running it, read the [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/). Public-service use must remain small, single-threaded, cached, identified with a custom user agent, and limited to at most one request per second. The script defaults to a 1.2-second delay and rejects delays below one second.

Use a clearly identifying user agent and begin with a small limit:

```bash
python3 scripts/geocode_candidate_affiliations.py \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)" \
  --limit 10
```

Cached successes and “not found” results are reused on later runs. Service and rate-limit errors stop further requests while preserving successfully cached progress. Unresolved rows are never discarded.

Geocoding is approximate: the first Nominatim result may refer to the wrong campus, similarly named institution, or administrative location. Every enriched row remains `manual_review=true`, and coordinates must be confirmed before they become curated data in `data/manual/`.

## Institution Review Queue

`scripts/build_institution_review_queue.py` compares the original in-scope affiliations with the geocoded in-scope output and generates `data/processed/institution_review_queue.csv`. The queue includes institutions with missing or invalid coordinates, failure notes, unexpected name changes, or suspiciously generic names. Entries are deduplicated by the same normalized institution name plus city and country.

Preview the queue without writing it:

```bash
python3 scripts/build_institution_review_queue.py --dry-run
```

Write the generated queue:

```bash
python3 scripts/build_institution_review_queue.py
```

`--max-examples` can cap the number of deduplicated review entries written or previewed. Each entry includes one example affiliation, author, and OpenAlex work identifier, a suggested exact normalized `match_key`, controlled review reasons, and a proposed manual action.

The review queue is generated from automatic candidate data and is not curated final institution metadata. Reviewers should investigate each entry and copy only manually verified corrections into `data/manual/institution_corrections.csv`; the queue builder never writes to that manual file. The generated queue itself is ignored by Git.

## Candidate CSV-to-Map Export

`scripts/export_candidate_map_data.py` joins the processed paper and affiliation CSVs by `openalex_id` and generates `web/data/openalex_candidate_map_data.json` for local map exploration. It preserves separate map records when a paper has multiple institutions.

By default, the exporter reads the in-scope paper CSV and the latest geocoded affiliation CSV, then rechecks paper IDs before grouping. `--include-out-of-scope` is available only for deliberate debugging. This prevents a broader custom affiliation file from silently reintroducing unrelated papers.

Grouping prefers `institution_openalex_id`, then `ror_id`, and only falls back to an exact normalized full institution name. It never uses substring or fuzzy name matching. The extractor stores `authors_ordered` once per paper as a JSON list in the original OpenAlex `authorships` array order; `author_position` and the one-based `author_order` remain on every affiliation row. Each marker for that paper reuses the same ordered paper-level `authors` list, regardless of institution. For older paper CSVs without `authors_ordered`, the exporter reconstructs the list once across all of the paper's affiliation rows using `author_order`, never separately per institution.

Each marker also receives `institution_authors`, derived from the author-institution rows assigned to that exact institution group. Names are mapped back to the canonical paper-level display list and sorted by original `author_order`, so institution grouping cannot reorder them. A multiply affiliated author appears in every matching institution record. If the institution identity or canonical author position cannot be determined conservatively, the field remains an empty list rather than guessing.

The processed affiliation CSV remains the complete relationship-level source: map aggregation never replaces or removes its author-institution rows. Institution and country aggregation affects only those location fields, including in the unique-paper web view; it never changes author order. Affiliations without valid coordinates remain available for review but cannot produce map markers.

The exporter includes only affiliation rows with a complete valid resolved or original latitude/longitude pair. It does not geocode missing institutions, call external APIs, or infer locations. Rows with missing or invalid coordinates remain in the processed CSV and are reported in the export summary rather than silently assigned a location.

Map-ready export normalizes Hong Kong, Macau/Macao, and Taiwan into public `country=China` and `country_code=CN` values while retaining `region`/`region_code` as `Hong Kong/HK`, `Macau/MO`, or `Taiwan/TW`. The pre-normalization resolved/source values are preserved in `raw_country` and `raw_country_code`. The same normalization is applied again by public-preview export for compatibility with older local map JSON. It does not alter raw OpenAlex files, processed affiliations, geocoding caches, or manual corrections.

When the affiliation CSV contains automatic resolution fields, the exporter prefers complete valid `resolved_latitude` and `resolved_longitude` pairs over the original coordinates. It also prefers non-empty resolved institution names, cities, and countries. If resolved coordinates are absent or invalid, the exporter falls back to a complete valid original coordinate pair; it never combines coordinates from different sources.

Before writing map records, the exporter reads `data/manual/paper_version_overrides.csv` when it exists. This manual table attaches confirmed alternate-version metadata, such as an arXiv version of a published paper that OpenAlex stores as a separate Work. Overrides match by published OpenAlex URL first, then DOI, then normalized title. They add `arxiv_id`, `arxiv_url`, and `has_arxiv_version=true`, append an override note, and preserve the published DOI, venue, publication year, and primary paper URL.

Resolution method, confidence, review status, and notes are included in each map record when those columns are available. Records with `needs_review=true` may still be visualized for exploration, but they remain preliminary and should not be presented as verified institution metadata. The export summary separates records using resolved versus original coordinates and reports skipped and reviewable records.

Inspect the join and summary without writing the JSON file:

```bash
python3 scripts/export_candidate_map_data.py --dry-run
```

Generate the local map dataset:

```bash
python3 scripts/export_candidate_map_data.py
```

After geocoding, point the exporter at the generated affiliation CSV:

```bash
python3 scripts/export_candidate_map_data.py \
  --affiliations-csv data/processed/openalex_candidate_affiliations_geocoded.csv
```

To export the automatically resolved affiliation data:

```bash
python3 scripts/export_candidate_map_data.py --affiliations-csv data/processed/openalex_candidate_affiliations_resolved.csv --max-records 200
```

The input and output paths can be changed with `--papers-csv`, `--affiliations-csv`, and `--output`. Use `--max-records` to limit the number of grouped map records exported during local exploration.

Map records carry the extracted material type, publication year/date, venue name/type, publisher, publication type, DOI, arXiv metadata, and source URLs when available. Institution-level grouping is unchanged.

Serve the repository and open [http://localhost:8000/web/?dataset=openalex](http://localhost:8000/web/?dataset=openalex) to select the generated dataset. The JSON file is ignored by Git and should not be committed.

This map export is for exploratory visualization only. It is assembled from automatically extracted candidates, retains `manual_review`, and is not a curated or publication-ready research dataset. Nothing in this step writes to `data/manual/`.

## Public Preview Export

`scripts/export_public_preview.py` filters the local map-ready candidate JSON into `web/data/public_preview_map_data.json` for optional publication through GitHub Pages. The output is explicitly labeled as an uncurated public preview, not a manually curated bibliography.

By default, the exporter publishes at most 200 records, requires `in_scope=true`, requires a main task of `detection`, `source_attribution`, or `detection_and_source_attribution`, requires `resolution_confidence` of `medium` or `high`, and excludes every record marked `needs_review=true`. It also requires a non-placeholder institution name and a finite latitude/longitude pair within geographic bounds, because every public record must represent a mapped institution. `--include-uncertain` and `--include-missing-location` can relax task or location checks for local debugging; unsupported legacy or generic-attribution labels remain excluded. The exporter keeps only fields needed by the public map and never copies raw responses or caches.

The public-preview exporter also reads `data/manual/paper_version_overrides.csv` before filtering and field limiting. This keeps manually confirmed arXiv-version links available in the public preview even when the local map-ready JSON was produced before the override existed. An override does not change the record's published venue/year/DOI metadata and does not by itself make a venue record preprint-only.

Inspect the filtering summary without writing output:

```bash
python3 scripts/export_public_preview.py --dry-run
```

Write the default public preview:

```bash
python3 scripts/export_public_preview.py
```

The confidence threshold can be tightened with `--min-confidence high`, and `--max-records` can produce a smaller preview. `--include-needs-review` and `--include-missing-location` are explicit debugging opt-ins; review-flagged or unmappable records should normally remain local.

Only the filtered public preview JSON should be considered for publication. Raw OpenAlex responses, processed candidate archives, institution-resolution and geocoding caches, the full local candidate map JSON, low-confidence records, and records needing review remain local and ignored by Git. Public-preview records are still automatically generated candidates and must not be described as curated final data.

### Public Preview Quality Report

Run `python3 scripts/report_public_preview.py` after every public-preview refresh. It regenerates `docs/public_preview_report.md` from the committed preview JSON so coverage counts, missing metadata, confidence levels, and potential quality issues remain synchronized with the dataset shown by the online map. The report explicitly counts and lists records missing institutions or usable coordinates; a default export should report zero for both.

### Public Preview Validation

Validation is the final recommended step after exporting the public preview and regenerating its quality report:

```bash
python3 scripts/export_public_preview.py
python3 scripts/report_public_preview.py
python3 scripts/validate_public_preview.py --strict
```

`scripts/validate_public_preview.py` accepts either a top-level record array or the metadata-plus-records object format. It checks publication-safe task and subtask labels, required paper and institution metadata, coordinate bounds, publication year, link availability, review status, and institution-resolution confidence. Errors always return a non-zero status; `--strict` also fails on warnings. The validator only reads the preview JSON and does not modify generated or manual data.

Validation also enforces the public regional convention: records identified as Hong Kong, Macau/Macao, or Taiwan must use `country=China`, `country_code=CN`, and the matching `region` and `region_code`. The quality report applies the same normalization when counting countries, so these records contribute to China in the Top Countries table even when reporting on an older preview file.

### Recommended Refresh Workflow

`scripts/refresh_public_preview.py` is the recommended pre-commit workflow. It calls the existing scoped pipeline, public-preview exporter, quality-report generator, and validator in that order. Each step is a subprocess, and the refresh stops immediately if any command fails. It does not duplicate pipeline logic, modify manual data, commit, or push.

Run a full refresh including a new OpenAlex search:

```bash
python3 scripts/refresh_public_preview.py \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)"
```

Reuse existing raw OpenAlex responses:

```bash
python3 scripts/refresh_public_preview.py \
  --skip-search \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)"
```

Treat validation warnings as failures:

```bash
python3 scripts/refresh_public_preview.py \
  --strict \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)"
```

The safe defaults are 100 results per search query, an 800-request resolution/geocoding limit, at most 500 public records, and medium-or-higher institution confidence. Replace the example User-Agent contact information with an appropriate project contact. Validation must pass before `web/data/public_preview_map_data.json` and `docs/public_preview_report.md` are committed.
