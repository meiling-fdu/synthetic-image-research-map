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

Each paper receives an automatic, reviewable `entry_type` from conservative, deterministic title rules. This project-specific map-entry category is separate from the formal OpenAlex `publication_type` and from the paper's research topic. The allowed values are `method`, `dataset`, `benchmark`, `survey`, and `analysis`; ordinary technical papers default to `method`. Classification priority is survey, benchmark, dataset, analysis, then method. Benchmark wording, `*Bench` names, evaluation protocols, leaderboards, standardized evaluation, and frameworks explicitly for reliable assessment identify benchmark resources. Analysis requires an empirical or diagnostic framing such as bias, human ability, robustness, failure, limitation, performance, or comparative evaluation; the word `analysis` alone is not enough. Abstract mentions of datasets, evaluation, challenges, robustness, comparisons, or related work do not determine `entry_type`.

Entry type does not replace or alter `preliminary_task` and `preliminary_subtask`, and no candidate is excluded because of its entry type. Anti-forensics, evasion, adversarial attacks, anti-detection, counter-forensics, and robustness are topics, while challenges, competitions, shared tasks, and challenge tracks are contexts; neither group supplies entry-type values. Such papers normally remain `method` unless the title clearly identifies a dataset, benchmark, survey, or analysis contribution. Future `topic_tags` or `contribution_tags` may represent these secondary details, but they are not part of `entry_type` now. The full and in-scope candidate paper CSVs include `entry_type`; the map and public-preview exporters preserve it while accepting legacy `material_type` inputs during regeneration.

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

Run `python3 scripts/enrich_papers_arxiv.py` to create the separate manual-review table `data/manual/paper_arxiv_links.csv` and its audit report `data/manual/arxiv_link_enrichment_report.csv`. The script does not call OpenAlex. It first reuses valid arXiv identifiers already present in candidate metadata or `key_papers_enriched.csv`, then matches formal and preprint rows already present in the local candidate database. A local match is filled only when the normalized titles are equal, author overlap is at least `0.80`, and the best arXiv ID is unique. Lower-overlap and ambiguous candidates are report-only. Only papers without a known identifier are searched through the arXiv Atom API; exact DOI matches or normalized-title matches with high author overlap may be linked automatically, while title-only matches require review.

This CSV is a partial, resumable enrichment table: `not_searched` rows have not yet been queried, while `not_found_in_arxiv` records only that the current query returned no result. Neither status proves absence. "Without known arXiv version" means only that no arXiv ID or URL is currently known in project data.

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

`data/manual/key_papers.csv` is a manually curated, in-scope checklist of papers whose coverage should be monitored. Checklist membership is the project's scope decision for this audit. OpenAlex is only a metadata source: absence from its candidate pool does not make a key paper out of scope. The checklist does not itself add a paper to candidate data, the map, or the public preview.

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

Run the local comparison from the repository root:

```bash
python3 scripts/audit_key_paper_coverage.py
```

The script compares the checklist with `data/processed/openalex_candidate_papers.csv`, `web/data/openalex_candidate_map_data.json`, `web/data/public_preview_map_data.json`, and the paper-level `web/data/public_preview_papers.json`, then writes `data/manual/key_paper_coverage_report.csv`. It uses normalized titles for current coverage matching and distinguishes `covered_as_map_marker`, `covered_in_public_preview_paper_list`, `missing_affiliation`, `missing_coordinates`, `missing_from_candidate_pool`, and `possible_title_match_failure`.

These statuses measure coverage and pipeline location, not scope. A missing key paper is a coverage gap that should be reviewed for import or metadata enrichment. A key paper present in the OpenAlex candidate pool but absent from exports should be diagnosed for affiliation, coordinate, or export-rule issues. OpenAlex candidate membership is not coverage ground truth, and the audit never publishes, excludes, or changes the scope of a checklist entry. Recommended actions are deliberately limited to coverage, title-review, import/enrichment, and export diagnostics.

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

## Manual OpenAlex Imports

Manually reviewed `*_import_ready.csv` files in `data/manual/` can be imported
reproducibly with `scripts/import_manual_openalex_papers.py` and
`scripts/import_manual_openalex_affiliations.py`. Only rows with
`import_status=ready` are eligible. Rows labeled
`generated_video_detection` are excluded from both workflows.

Dry runs validate the manual inputs and processed CSV schemas, report local
duplicates, and make no network requests or file changes:

```bash
python3 scripts/import_manual_openalex_papers.py --dry-run
python3 scripts/import_manual_openalex_affiliations.py --dry-run
```

Run the imports, then rebuild and validate the preview:

```bash
python3 scripts/import_manual_openalex_papers.py
python3 scripts/import_manual_openalex_affiliations.py
python3 scripts/export_candidate_map_data.py
python3 scripts/export_public_preview.py --preserve-existing
python3 scripts/validate_public_preview.py
python3 scripts/audit_key_paper_coverage.py
```

Before writing either public JSON file, the exporter compares the prior and
proposed paper identities and canonical paper–institution relationships. Active
durable exclusions, confirmed paper-version merges, reviewed mapping changes,
and canonical institution redirects explain intentional removals; anything else
is reported and blocked. With `--preserve-existing`, unexplained gaps from a
partial local candidate snapshot are retained, while records covered by those
explicit current decisions are filtered before unioning. Restored/inactive
exclusions never authorize removal.

`data/curated/public_export_baseline.json` is retained as a bootstrap/disaster
reference when prior public outputs are unavailable, not as an unconditional
minimum for ordinary Admin maintenance. It is never lowered automatically. An
exceptional reviewed reduction that cannot be inferred from durable evidence
may still use an explicitly supplied `--approved-baseline` file.

Use repeatable or comma-separated `--input` values to select different manual
CSVs, and `--limit N` for a bounded online run. The importers preserve the
existing processed CSV headers exactly, skip duplicate OpenAlex IDs and
normalized titles or affiliation keys, skip retracted works, and replace each
processed CSV atomically after a successful batch. A failed OpenAlex request is
reported for that work or institution without aborting unrelated rows.

Institution metadata and coordinates returned by OpenAlex remain automatic
fallback data. Coordinate-bearing institution responses receive medium
resolution confidence; institutions without a complete coordinate pair remain
marked `needs_review=true`. The scripts never write back to the manual input
files.

## Candidate CSV-to-Map Export

`scripts/export_candidate_map_data.py` joins the processed paper and affiliation CSVs by `openalex_id` and generates `web/data/openalex_candidate_map_data.json` for local map exploration. It preserves separate map records when a paper has multiple institutions.

By default, the exporter reads the in-scope paper CSV and the latest geocoded affiliation CSV, then rechecks paper IDs before grouping. `--include-out-of-scope` is available only for deliberate debugging. This prevents a broader custom affiliation file from silently reintroducing unrelated papers.

Grouping prefers `institution_openalex_id`, then `ror_id`, and only falls back to an exact normalized full institution name. It never uses substring or fuzzy name matching. The extractor stores `authors_ordered` once per paper as a JSON list in the original OpenAlex `authorships` array order; `author_position` and the one-based `author_order` remain on every affiliation row. Each marker for that paper reuses the same ordered paper-level `authors` list, regardless of institution. For older paper CSVs without `authors_ordered`, the exporter reconstructs the list once across all of the paper's affiliation rows using `author_order`, never separately per institution.

Each marker also receives `institution_authors`, derived from the author-institution rows assigned to that exact institution group. Names are mapped back to the canonical paper-level display list and sorted by original `author_order`, so institution grouping cannot reorder them. A multiply affiliated author appears in every matching institution record. If the institution identity or canonical author position cannot be determined conservatively, the field remains an empty list rather than guessing.

OpenAlex authorship-to-institution links can be incomplete even when the paper-level author list is correct. Human-reviewed corrections belong in `data/manual/institution_author_overrides.csv`, never in raw or processed OpenAlex files. During map export, a correction matches by normalized title, by year when the manual row provides one, and by normalized institution name. A match replaces only the institution record's `institution_authors` list, preserving the semicolon-delimited author order from the manual CSV; it never changes the paper-level `authors` list.

The candidate map exporter reports how many institution-author overrides were loaded and applied and lists unmatched rows for review. This correction layer is offline and read-only: export does not call an external API or write back to the manual override file.

Paper-level institution corrections belong in `data/manual/institution_record_overrides.csv`. Rows match by exact normalized title plus publication year or optional DOI/OpenAlex identifiers. `mode=replace` removes the complete matched paper record set and inserts exactly the grouped manual rows; `mode=remove` deletes an exact normalized institution-name match; and `mode=add` keeps existing records and appends the manual institution only when it is not already present. The modes run in that order so the result is deterministic and public-preview reapplication cannot duplicate additions. Replacement and addition retain the paper's bibliographic metadata, ordered full author list, task and entry-type labels, paper/OpenAlex/arXiv provenance, confidence, and review fields. The exporter reports each mode, automatic records removed by replacement, replacement records created, unmatched rows, and coordinate-missing override records.

The `institution` value is always the canonical institution name alone. Departments, schools, laboratories, official affiliation strings, and raw evidence belong in `evidence` or `notes`; street and campus addresses belong in `address`; and city, region, and country use their dedicated columns. OpenAlex institution resolution is useful fallback metadata, not final ground truth. Confirmed paper or publisher evidence may override it without modifying raw or processed OpenAlex data.

Coordinates must come from reliable local metadata or prior verified manual evidence and must never be guessed. A `replace` or `add` row may leave both coordinate fields blank when the institution correction is confirmed but its location is still pending. Candidate export retains and counts that record; the normal public-preview location filter excludes it until coordinates are verified.

Both exporters run institution-record corrections before the narrower `institution_author_overrides.csv` layer, so an exact author-only correction can still refine a corrected institution later. Corrections also run before public-preview filtering, making preview export robust when its candidate-map JSON predates a manual correction.

The candidate exporter tags grouped institution records as automatic and replacement records as manual overrides. For every replaced paper it performs a final identity check across normalized title/year, DOI, and OpenAlex URL; export fails if any automatic record for that paper survives.

Run `python3 scripts/audit_institution_records.py` to audit the current local geocoded affiliations without calling an API. The audit detects confirmed acronym/name-confusion patterns, explicit country conflicts in raw affiliation text, unrelated organization matches, and very low institution-name overlap. Findings for papers already covered by confirmed replacement overrides are counted but omitted from the queue. Additional ambiguous findings are written to `data/manual/institution_record_review_queue.csv` for manual inspection and never become overrides automatically. Use `--dry-run` to print counts without rewriting the queue.

Run `python3 scripts/triage_institution_review_queue.py` to classify that queue using deterministic local rules for aliases/translations, parent/subunit names, country words in place names, explicit institution conflicts, author-assignment conflicts, and incomplete paper-level evidence. It writes `data/manual/institution_record_review_triage.csv` and a separate `data/manual/institution_record_override_candidates.csv`; it never edits the confirmed override table. A replacement candidate is emitted only when all paper authors are covered by high-confidence wrong-institution findings and every proposed institution has an exact coordinate-bearing match in the local geocoded affiliation data. Otherwise the paper remains in triage for full-paper or manual review.

Run `python3 scripts/build_institution_risk_report.py` to turn the local paper, geocoded affiliation, review-queue, correction-backlog, and override files into `data/manual/institution_paper_risk_report.csv`. The script calls no API and produces one row per normalized paper title and year. It uses the maximum row risk plus only a small capped bonus for multiple distinct high-risk reason types; repeated author rows do not accumulate into an artificial paper-level risk. Scores of 60 or more are `high`, 25–59 are `medium`, and lower scores are `low`.

The score is an explainable review priority heuristic, not an absolute probability that an affiliation is wrong. High-risk papers require human verification with the publisher page, paper PDF, Crossref, ROR, or other official evidence. Online services are review sources for a person or a separate approved workflow; this report builder itself uses local data only. Confirmed corrections should eventually move into the appropriate manual override file, while verified overrides remain low-priority regression cases. OpenAlex-resolved institutions are fallback metadata rather than final ground truth, and this report never edits `institution_record_overrides.csv`.

## Paper Abstract Display Data

Candidate-map export loads `data/manual/paper_abstracts.csv` when present and also checks processed paper rows for existing `abstract`, `abstract_text`, or `reconstructed_abstract` fields. If those are empty, it reconstructs abstracts already stored as `abstract_inverted_index` values in local `data/raw/openalex/` archives. This fallback is read-only and makes no OpenAlex, Crossref, arXiv, publisher, or other network request.

Abstract matching uses DOI first, then arXiv ID, OpenAlex URL, and normalized title plus publication year. Manual/cache rows take precedence, followed by processed candidate metadata and then local raw OpenAlex cache data. Every non-empty abstract carries `abstract_source`; missing abstracts remain empty and are displayed as `No abstract available.` They must not be inferred or generated.

The Paper details panel keeps `abstract` separate from the optional `ai_summary` field. `abstract` is original metadata from OpenAlex, Crossref, arXiv, a publisher, or the manual cache. `ai_summary` is generated content and must always be labeled `AI-generated summary`; it is not original paper metadata. The current workflow does not call an AI service or generate summaries and displays an informational unavailable state instead.

The processed affiliation CSV remains the complete relationship-level source: map aggregation never replaces or removes its author-institution rows. Institution and country aggregation affects only those location fields, including in the unique-paper web view; it never changes author order. Automatic affiliations without valid coordinates remain available for review but cannot produce map markers. A confirmed coordinate-pending manual override may remain in candidate export data, but it likewise cannot produce a marker or enter the normal public preview until coordinates are verified.

The exporter includes only affiliation rows with a complete valid resolved or original latitude/longitude pair. It does not geocode missing institutions, call external APIs, or infer locations. Rows with missing or invalid coordinates remain in the processed CSV and are reported in the export summary rather than silently assigned a location.

Map-ready export normalizes Hong Kong, Macau/Macao, and Taiwan into public `country=China` and `country_code=CN` values while retaining `region`/`region_code` as `Hong Kong/HK`, `Macau/MO`, or `Taiwan/TW`. The pre-normalization resolved/source values are preserved in `raw_country` and `raw_country_code`. The same normalization is applied again by public-preview export for compatibility with older local map JSON. It does not alter raw OpenAlex files, processed affiliations, geocoding caches, or manual corrections.

When the affiliation CSV contains automatic resolution fields, the exporter prefers complete valid `resolved_latitude` and `resolved_longitude` pairs over the original coordinates. It also prefers non-empty resolved institution names, cities, and countries. If resolved coordinates are absent or invalid, the exporter falls back to a complete valid original coordinate pair; it never combines coordinates from different sources.

Before writing map records, the exporter reads `data/manual/paper_version_overrides.csv` when it exists. This manual table attaches confirmed alternate-version metadata, such as an arXiv version of a published paper that OpenAlex stores as a separate Work. Overrides match by published OpenAlex URL first, then DOI, then normalized title. They add `arxiv_id`, `arxiv_url`, and `has_arxiv_version=true`, append an override note, and preserve the published DOI, venue, publication year, and primary paper URL.

The exporter also reads `data/manual/paper_arxiv_links.csv` when present. It applies only `linked_to_arxiv` rows with a non-empty arXiv ID or URL, matching by the enrichment row's OpenAlex URL when available, otherwise its DOI, otherwise normalized title plus publication year. It fills or preserves `arxiv_id`, `arxiv_url`, and `arxiv_year` without replacing conflicting existing arXiv metadata or changing formal publication year, DOI, venue, OpenAlex URL, `publication_type`, or primary URL. The summary reports enrichment rows loaded, usable linked rows, links applied, and unmatched linked rows. A missing enrichment file is treated as an empty partial table.

Finally, the exporter reads `data/manual/publication_overrides.csv` when it exists. This auditable manual layer corrects cases where OpenAlex primarily exposes an arXiv/preprint Work even though the paper has a known formal publication. It matches an exact normalized title and, when provided, the pre-override `match_year`; no API or fuzzy matching is used. A match replaces the displayed publication year, venue, DOI, formal paper URL, and publication type across their map aliases. It does not change the OpenAlex URL or known arXiv ID, URL, or year. Because the corrected record has a formal venue, public preprint-only logic becomes false while `has_arxiv_version` can remain true. The exporter reports overrides loaded, applied, and unmatched.

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

Map records carry the extracted entry type, publication year/date, venue name/type, publisher, publication type, DOI, arXiv metadata, and source URLs when available. Institution-level grouping is unchanged.

Serve the repository and open [http://localhost:8000/web/?dataset=openalex](http://localhost:8000/web/?dataset=openalex) to select the generated dataset. The JSON file is ignored by Git and should not be committed.

This map export is for exploratory visualization only. It is assembled from automatically extracted candidates, retains `manual_review`, and is not a curated or publication-ready research dataset. Nothing in this step writes to `data/manual/`.

## Curated database layer

OpenAlex is a candidate metadata source, not the final source of truth. Maintainer-confirmed paper records and decisions live in the CSV files under `data/curated/`; raw OpenAlex responses, processed candidate datasets, and manual correction files remain separate. The public preview JSON files under `web/data/` are generated output and must be changed through export scripts rather than edited directly.

Paper-level editing is the main local curation workflow. Author–institution mappings are core curation objects and are confirmed manually, preserving all supported affiliations rather than assigning a paper to its first author's location. Coordinates are not edited during paper-level curation. Institutions with missing or uncertain locations are recorded in `data/curated/institution_location_review.csv` for the separate location-review workflow.

Removing a paper from maintained outputs is a durable exclusion decision in `data/curated/paper_exclusions.csv`; it does not delete or alter the processed OpenAlex source files. The curated layer is intended for local maintainer tools. The GitHub Pages site remains a read-only static site.

Validate and summarize the curated layer from the repository root:

```bash
python3 scripts/validate_curated_database.py
python3 scripts/report_curated_database.py
```

Header-only curated files are valid and leave public-preview output byte-for-byte unchanged. When curated rows exist, the public-preview exporter merges them through the integration described below.

### Local admin browser

Maintainers can inspect the current public-preview papers, their map-marker institution records, and any additional curated papers in a local read-only browser:

```bash
python3 scripts/serve_admin.py
```

For the concise start-to-finish maintainer procedure, including paper addition, scope exclusion, author–institution mapping, institution location review, and the full refresh pipeline, see [Local Admin Workflow](admin_workflow.md).

The server binds to `127.0.0.1:8765` by default and prints a newly generated admin token. Open `http://localhost:8765/admin/?token=<TOKEN>`, replacing `<TOKEN>` with that terminal value. The page stores the token for the current browser tab, removes it from the address bar, and sends it to API requests in the `X-Admin-Token` header. Direct API clients may use that header or the `token` query parameter.

The server refuses non-loopback binding unless `--unsafe-bind-all` is explicitly supplied. The public GitHub Pages site remains a separate read-only static site and does not use these admin APIs.

### OpenAlex-first paper addition

The local admin browser's **Add Paper** workflow searches OpenAlex by title, DOI, arXiv ID, or paper URL. DOI and arXiv identifiers are tried as exact lookups before title retrieval. Title retrieval combines exact-phrase, full-title, distinctive-subtitle, and `title.search` queries, requests up to 50 candidates per query, deduplicates them, and reranks them by normalized title similarity. Exact DOI, exact arXiv ID, and exact normalized-title matches rank ahead of candidates with title similarity of at least `0.85`; lower-scoring results remain collapsed under **Weak matches**. The search diagnostics show the query variants, raw candidate count, best title similarity, and exact-lookup attempts.

Review the returned candidates, choose **Use this OpenAlex record**, correct or complete the prefilled metadata, assign the task and optional subtask, and save the confirmed record to `data/curated/papers.csv`. OpenAlex supplies candidate metadata; the saved curated row represents the maintainer's confirmation and uses `source_database=openalex`, `metadata_source=openalex`, and `curation_status=manually_confirmed`. When an exact arXiv ID is not found in OpenAlex, the workflow may retrieve public Atom metadata directly from arXiv; a confirmed fallback row instead records `source_database=arxiv` and `metadata_source=arxiv`.

For an existing paper, the admin **Paper Metadata** editor writes `task` and the controlled `entry_type` contribution category (`method`, `dataset`, `benchmark`, `survey`, or `analysis`) to the same curated paper row. `entry_type` is independent of the bibliographic `publication_type`. Both Add Paper and Paper Metadata expose `publication_type` as a required dropdown with `conference`, `journal`, `preprint`, and `book`; legacy `article` values normalize to `journal`, while proceedings and conference-venue evidence continues to normalize to `conference`. These values flow through the normal refresh/export/publish process; generated `web/data/` files are never the source of truth.

If no candidate is correct—or OpenAlex is unavailable—choose **Add manually instead**. The same form opens without metadata and saves the record with manual provenance and `curation_status=manually_added`. OpenAlex failures do not write any files and do not disable this manual fallback.

Before saving, the server compares DOI, OpenAlex URL, and normalized title plus year against the current public-preview papers, curated papers, and paper-exclusion history. A match is shown as a duplicate warning and creation is blocked; Step 4 does not merge or override records.

Paper addition stores paper metadata only; author–institution mappings are edited separately after selecting the saved paper, and institution coordinates remain a separate review workflow. A successful paper save does not edit `data/processed/` or generated public-preview JSON; the normal exporter reads curated records later. Run the curated validator after any curation session:

```bash
python3 scripts/validate_curated_database.py
```

### Paper-level author–institution mapping editor

Select a paper in the local admin browser and use **Author–Institution Mappings** to add, edit, exclude, or replace its curated affiliation records. Each row records the canonical institution, the authors associated with that institution, raw affiliation or supporting evidence, mapping status, and a required review note. The records are saved to `data/curated/author_institution_mappings.csv`.

Mappings are paper-level curation objects; map markers are derived outputs. The editor therefore does not request latitude or longitude. Current exported/public marker records appear in a separate evidence table for comparison and are never edited by this workflow.

An active mapping whose canonical institution has no exact institution match with valid coordinates in the existing public map data is added to `data/curated/institution_location_review.csv` with `location_status=missing` and `coordinate_status=missing`. The queue preserves the paper, author, affiliation, and evidence context without inventing coordinates or treating the institution name as an address. Institutions already represented by valid public marker coordinates are not queued.

Duplicate active mappings are blocked when the paper identity, institution, and institution-author correspondence match. **Replace all mappings** requires explicit confirmation, marks prior active rows as `excluded`, appends the replacement review note for auditability, and creates the replacement row rather than deleting history. These local actions do not edit `data/processed/` or public-preview JSON directly.

### Curated public-preview integration

`python3 scripts/export_public_preview.py` now reads curated papers, active author–institution mappings, durable exclusions, and the institution location-review queue after building the existing automatic preview. Curated papers are merged by DOI, OpenAlex URL, then normalized title plus year. A matching `manually_confirmed` or `corrected_by_admin` row may override selected bibliographic and classification fields; otherwise curated values fill missing metadata. A non-duplicate, in-scope curated paper is appended to the paper-level preview.

The exporter also reads `data/curated/paper_version_merges.csv`. Active `confirmed_duplicate` rows merge reviewed arXiv/repository versions into the canonical formal publication after curated-paper integration. Canonical bibliographic fields and author order win; arXiv identifiers, missing abstracts, and affiliation/marker evidence are migrated before duplicate paper and institution records are removed. Run `python3 scripts/audit_arxiv_published_duplicates.py` to regenerate the candidate review report. Candidates without a confirmed curated row remain visible and are never auto-merged.

Paper-level publication does not require coordinates. A curated paper with no mappings receives `missing_affiliation`; a paper with mappings but no coordinate-bearing institution receives `missing_coordinates`. Its mapping evidence remains attached to the paper record, while no marker is fabricated.

Active curated mappings produce markers only after an exact normalized institution-name match resolves to one unique valid location. The shared resolver first uses maintainer-confirmed records in `data/curated/institution_locations.csv`, then trusted active authoritative entries in `data/processed/institution_resolution_cache.json`, then the current public map's validated locations, and finally medium/high-confidence, non-review candidate-map locations. Ambiguous exact-name matches are deliberately unresolved. A marker using a confirmed curated location carries `resolution_method=curated_confirmed_location`; a processed-cache fallback carries `resolution_method=processed_institution_resolution_cache_fallback` plus an explicit marker note, and is not promoted into the curated CSV. Other exact known matches use `curated_mapping_existing_location`. Each marker preserves the confirmed institution-author correspondence and evidence provenance and replaces only an automatic marker for the same paper and institution.

Active mappings without a unique valid location are added or updated in `data/curated/institution_location_review.csv`. Missing matches use `location_status=missing` and `coordinate_status=missing`; ambiguous matches use `needs_coordinate_review` and `ambiguous`. Existing review notes and creation timestamps are preserved, and repeated mappings for the same paper and institution do not create duplicate queue items. When a previously queued institution gains an exact known location, its queue status is updated to `known`.

Active paper exclusions remain authoritative for both paper and marker outputs. Header-only curated files are a strict no-op, so the existing candidate preview and its hashes remain unchanged until maintainers add curated records.

### Institution Location Review

Open the tokenized local admin browser and choose **Institution Location Review** to inspect rows from `data/curated/institution_location_review.csv`. Each queue row keeps the related paper, institution authors, raw affiliation, mapping evidence, suggested location, current statuses, and review note visible. Coordinate review is intentionally separate from confirming the paper-level author–institution relationship.

Select a queue row and enter the confirmed institution, optional city/region/country labels, uppercase two-letter country code, latitude, longitude, coordinate source or source URL, and a required coordinate review note. Latitude must be between -90 and 90 and longitude between -180 and 180. The server never geocodes, guesses, or invents a coordinate: the maintainer must copy it from a reliable source and document that evidence.

Confirmation atomically creates or updates the matching normalized institution in `data/curated/institution_locations.csv`, marks the queue row `location_status=known` and `coordinate_status=known`, and preserves the queue's paper and evidence context. Duplicate confirmed rows for the same normalized institution are rejected. **Mark ambiguous** instead records `location_status=ambiguous` and `coordinate_status=needs_coordinate_review`; **Mark unresolved** records both statuses as missing. Both status decisions require a review note and create no coordinates.

After confirmation the browser reports **Location saved. Run full refresh pipeline to update markers.** The next export gives a unique confirmed location priority over existing public and safe candidate locations. An active curated mapping can then produce a marker; multiple confirmed candidates remain ambiguous and marker-free. The save endpoints write only curated CSV files, and the full refresh is still required to update generated `web/data/` JSON. GitHub Pages changes only after the separate, confirmed **Publish Changes** workflow commits and pushes eligible files.

Summarize the queue and confirmed location table with:

```bash
python3 scripts/report_location_review.py
```

### Local real-time export and validation

The local admin browser includes a **Refresh local preview** panel with separate controls for curated validation, public-preview export, public-preview validation, reloading browser data, and the complete refresh pipeline. Each command is a fixed server-side argv list; the browser cannot supply a shell command or command arguments. Requests require the admin token and command execution is additionally restricted to loopback clients.

**Run full refresh pipeline** executes these local scripts in order and stops at the first failure:

```text
python3 scripts/validate_curated_database.py
python3 scripts/validate_paper_exclusions.py
python3 scripts/export_public_preview.py
python3 scripts/validate_public_preview.py
python3 scripts/audit_key_paper_coverage.py
python3 scripts/diagnose_paper_marker_blockers.py
```

The server captures bounded stdout/stderr tails, exit status, duration, and any Git-status paths changed by the workflow. Only one maintenance workflow may run at a time, and each subprocess has a timeout. A failed validation is shown in the collapsible command log; later full-refresh steps are not run, and the UI does not describe the preview as validated.

Export and full refresh update the local generated files under `web/data/`
through `scripts/export_public_preview.py --preserve-existing`, then reload the
paper list and selected-paper details from the refreshed JSON. This preserves
unexplained gaps from a partial local candidate cache while filtering durable
explicit removals. The confirmed **Publish Changes** workflow relies on the
exporter's identity-level paper and paper–institution audit before Git staging;
raw size changes remain visible diagnostics rather than an unconditional
percentage cap or count floor. **Reload preview data** only rereads the current
local JSON and does not run an export. The optional Git-status view runs only
`git status --short`.

These actions never stage, commit, push, or publish anything. After a successful export the UI explicitly reports: **Local preview updated. Commit and push manually to update GitHub Pages.** The deployed GitHub Pages site changes only after the maintainer reviews the diff and manually commits and pushes it.

### Visual paper deletion / scope exclusion

The local admin browser can record a durable decision to remove an out-of-scope paper from future public preview and map exports. Start the localhost server with `python3 scripts/serve_admin.py`, open the tokenized URL printed in the terminal, find the paper, and choose **Delete / Exclude from site**. The confirmation dialog requires both a reason and review note.

Deletion in this workflow means adding an active audit row to `data/curated/paper_exclusions.csv`. It does not delete or modify OpenAlex-derived files under `data/processed/`, and the browser does not directly edit generated public-preview JSON. Duplicate active decisions are not appended: an existing matching exclusion is retained and its review note may be updated. Restoring a paper marks the audit row inactive and records `restored_at` plus a restore note rather than deleting history.

Allowed reason values are:

- `out_of_scope`
- `downstream_synthetic_data_only`
- `medical_or_agriculture_or_industrial_only`
- `remote_sensing_only`
- `deepfake_only_not_core`
- `policy_or_perception_only`
- `duplicate`
- `retracted`
- `wrong_metadata`
- `other`

The exporter reads active exclusions and matches DOI first, OpenAlex URL second, and normalized title plus year otherwise. It removes matches from both public-preview JSON files. Excluded checklist papers are also omitted from the normal key-paper coverage audit; the marker-blocker report reads the already-filtered paper preview and therefore excludes them naturally.

Retractions are also excluded defensively even without a matching curated
exclusion row. The final export removes them from both public-preview files
after candidate, preserved-preview, and curated records have been combined.
Recognized signals are a `retraction`/`retracted` publication type, an explicit
`is_retracted`/`retracted` flag, a title beginning with `[Retracted]` or
`Retracted:`, or retraction text in exclusion metadata.

After making or restoring a decision, refresh generated outputs and checks from the repository root:

```bash
python3 scripts/validate_curated_database.py
python3 scripts/validate_paper_exclusions.py
python3 scripts/report_excluded_papers.py
python3 scripts/export_public_preview.py
python3 scripts/validate_public_preview.py
python3 scripts/audit_key_paper_coverage.py
python3 scripts/diagnose_paper_marker_blockers.py
```

The admin browser refreshes its local list immediately but deliberately does not run the exporter. GitHub Pages remains read-only and has no access to the local write API.

## Public Preview Export

`scripts/export_public_preview.py` filters the local map-ready candidate JSON into `web/data/public_preview_map_data.json` for optional publication through GitHub Pages, then merges eligible maintainer-confirmed curated records. It also writes `web/data/public_preview_papers.json`, a paper-level public preview list that includes in-scope candidate/key/curated papers even when affiliation or coordinate data is incomplete. The map JSON remains strict: only records with usable institution coordinates can become markers. The paper JSON carries transparent coverage fields such as `has_map_location`, `map_record_count`, `missing_affiliation`, `missing_coordinates`, `needs_review`, and `coverage_status` so incomplete papers can be searched and reviewed without fabricating locations. Provenance fields distinguish automatic candidate metadata from curated records.

During export, titles are normalized case-insensitively with punctuation and
hyphen differences collapsed. When records with the same normalized title
include both an arXiv/preprint-only version and a record with a non-arXiv DOI
or non-preprint venue, the formal publication is retained and the preprint-only
record is omitted from both the paper list and map output. The formal record's
DOI, authorship, affiliations, countries, and marker data are not replaced by
the preprint metadata. Standalone preprints remain eligible when no formal
publication record is present.

By default, the exporter publishes all eligible records, requires `in_scope=true`, requires a main task of `detection`, `source_attribution`, or `detection_and_source_attribution`, requires `resolution_confidence` of `medium` or `high`, and excludes every record marked `needs_review=true`. It also requires a non-placeholder institution name and a finite latitude/longitude pair within geographic bounds, because every public record must represent a mapped institution. `--include-uncertain` and `--include-missing-location` can relax task or location checks for local debugging; unsupported legacy or generic-attribution labels remain excluded. The exporter keeps only fields needed by the public map and never copies raw responses or caches.

The public-preview exporter also reads `data/manual/paper_version_overrides.csv`, the partial `data/manual/paper_arxiv_links.csv`, and `data/manual/publication_overrides.csv` before filtering and field limiting. This keeps known arXiv-version links and formal-publication corrections available when the local map-ready JSON predates those manual inputs. Public-preview `arxiv_id`, `arxiv_url`, `arxiv_year`, and `has_arxiv_version` are "known arXiv version" metadata. Publication overrides change only the formal display fields and leave those arXiv fields plus the OpenAlex URL intact. An arXiv version does not by itself make a formally published record preprint-only.

After integration, public export resolves every record through the canonical venue registry and the shared effective publication-type resolver before paper/marker synchronization. Confirmed Conference and Journal identities therefore override stale Preprint source labels while preserving repository links; confirmed Book series remain Book. Run `python3 scripts/migrate_publication_types.py` without `--apply` for the machine-readable deterministic curated audit at `data/processed/publication_type_migration_audit.csv` and the complete final-public Preprint/Book audit at `data/processed/public_preprint_book_audit.csv`; use `--apply` only for deterministic curated changes, then rerun the dry run to verify idempotence.

Inspect the filtering summary without writing output:

```bash
python3 scripts/export_public_preview.py --dry-run
```

Write the default public preview:

```bash
python3 scripts/export_public_preview.py
```

The confidence threshold can be tightened with `--min-confidence high`, and `--max-map-records` can produce a limited test or performance-fallback preview. The legacy `--max-records` name remains an alias. Without either maximum option, all eligible map records are exported. `--include-needs-review` and `--include-missing-location` are explicit debugging opt-ins; review-flagged or unmappable records should normally remain local.

Confirmed institution parent/child relationships are curated independently in `data/curated/institution_hierarchy.csv`. The exporter publishes only confirmed ID-based links and never uses hierarchy to rewrite source affiliations, infer a child institute from a parent name, or create an alias. The static frontend automatically expands an exact top-level parent selection to confirmed descendants; exact child selections remain child-only.

Only the filtered public preview JSON files should be considered for publication. Raw OpenAlex responses, processed candidate archives, institution-resolution and geocoding caches, the full local candidate map JSON, low-confidence marker records, and records needing review remain local and ignored by Git. Paper-level preview records may still need affiliation or coordinate review; they are included to make coverage gaps visible, not to claim complete institution metadata. The preview is a provenance-labeled mixture of automatic candidates and any maintainer-confirmed curated rows, not a uniformly curated final bibliography.

### Public Preview Quality Report

Run `python3 scripts/report_public_preview.py` after every public-preview refresh. It regenerates `docs/public_preview_report.md` from the committed preview JSON so coverage counts, missing metadata, confidence levels, and potential quality issues remain synchronized with the dataset shown by the online map. The report explicitly counts and lists records missing institutions or usable coordinates; a default export should report zero for both.

### Public Preview Validation

Validation is the final recommended step after exporting the public preview and regenerating its quality report:

```bash
python3 scripts/export_public_preview.py
python3 scripts/report_public_preview.py
python3 scripts/validate_public_preview.py --strict
```

`scripts/validate_public_preview.py` accepts either a top-level record array or the metadata-plus-records object format. It checks the strict map preview for publication-safe task and subtask labels, required paper and institution metadata, coordinate bounds, publication year, link availability, review status, and institution-resolution confidence. It also validates the paper-level preview for paper metadata, coverage flags, and consistency between `has_map_location` and `map_record_count` without requiring institution coordinates. Errors always return a non-zero status; `--strict` also fails on warnings. The validator only reads the preview JSON files and does not modify generated or manual data.

The exporter owns `metadata.public_preview_generated_at`. It computes one UTC `YYYY-MM-DDTHH:MM:SSZ` value after shrinkage checks, validates both proposed outputs with that same value, and commits the JSON pair transactionally. `--dry-run`, failed validation, failed shrinkage checks, and failed publish workflows preserve the previously successful timestamp. Maintainers must not derive or edit this field from local time, file modification times, or Git commit dates; refresh and publish workflows do not run a separate timestamping step.

Validation also enforces the public regional convention: records identified as Hong Kong, Macau/Macao, or Taiwan must use `country=China`, `country_code=CN`, and the matching `region` and `region_code`. The quality report applies the same normalization when counting countries, so these records contribute to China in the Top Countries table even when reporting on an older preview file.

### Interactive Curation Console data boundaries

The localhost console treats `data/curated/*.csv` as the only durable human-decision layer. Paper metadata overrides, exclusions, mappings, location confirmations, location-review queue entries, and review outcomes are stored there. Generated `data/manual/*.csv` reports are read-only diagnostic queues; `data/processed/*.csv` remains the OpenAlex/processed source layer; and `web/data/public_preview_*.json` is produced only by the exporter or full refresh.

`scripts/report_high_risk_markers.py` deterministically combines available public markers, candidate markers, marker blockers, and key-paper coverage diagnostics into `data/manual/high_risk_marker_review.csv`. Missing optional inputs are tolerated. Reviewing this report never changes it: actions are routed to the relevant curated CSV or to `data/curated/review_decisions.csv`. The public exporter applies `exclude_wrong_mapping` decisions as institution-and-paper-specific marker suppressions.

### Recommended Refresh Workflow

`scripts/refresh_public_preview.py` is the recommended pre-commit workflow. It calls the existing scoped pipeline, public-preview exporter, quality-report generator, and validator in that order. Each step is a subprocess, and the refresh stops immediately if any command fails. It does not duplicate pipeline logic, modify manual data, commit, or push.

Refresh always preserves the current complete preview while merging newly
derived records. It has no default processing limit or public-record cap:
`--limit` and `--max-records` are applied only when the maintainer passes them
explicitly.

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
