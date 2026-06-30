# Synthetic Image Research Map

An interactive academic world map for exploring papers, researchers, and institutions working on AI-generated/synthetic image detection and generated-image source attribution. The project is a lightweight static website backed by transparent, reviewable datasets and Python preprocessing.

**Online demo:** [Synthetic Image Research Map on GitHub Pages](https://meiling-fdu.github.io/synthetic-image-research-map/)

## Project Goals

- Map the global research landscape for AI-generated/synthetic image detection and source attribution.
- Connect papers with their authors, institutions, affiliations, and locations without reducing a paper to a single author location.
- Preserve source metadata and data provenance throughout the collection and processing workflow.
- Make automatic classifications and uncertain records easy to review and correct manually.
- Exclude adjacent attribution fields and synthetic-data applications that do not detect or source-attribute generated images.

## Roadmap

1. Improve literature search coverage for synthetic image detection and source attribution.
2. Add bibliographic sources such as Semantic Scholar and Crossref.
3. Improve institution resolution and confidence scoring.
4. Establish a manual validation workflow for relevance, labels, affiliations, and coordinates.
5. Add a year-based timeline visualization.
6. Add country- and institution-level statistics.
7. Add citation and data-export support.

## Repository Structure

```text
.
|-- AGENTS.md          # Project guidance for contributors and coding agents
|-- README.md          # Project overview and workflow
|-- data/
|   |-- raw/           # Unmodified source and API data
|   |-- processed/     # Cleaned, normalized, and derived datasets
|   |-- manual/        # Human-reviewed corrections and overrides
|   `-- curated/       # Maintainer-confirmed paper and mapping database
|-- scripts/           # Python collection and preprocessing scripts
|-- web/               # Static Leaflet.js prototype
|   |-- index.html     # Prototype page and controls
|   |-- style.css      # Responsive interface styles
|   |-- app.js         # Map rendering, filters, and summary counts
|   `-- data/          # Static datasets exported for the website
|-- docs/              # Methodology, schemas, and project notes
`-- notebooks/         # Exploratory analysis notebooks
```

Empty directories contain `.gitkeep` placeholders until project files are added.

## Data Workflow

1. Collect source records into `data/raw/` without altering the original metadata.
2. Clean, normalize, classify, and geocode records with Python scripts in `scripts/`.
3. Store reusable automatic outputs in `data/processed/`, including provenance and `manual_review` flags where needed.
4. Maintain confirmed corrections and overrides separately in `data/manual/`; automated scripts must not overwrite these files.
5. Apply manual overrides during processing and export website-ready static data to `web/data/`.
6. Load the exported data in the static Leaflet.js website from `web/`.

Maintainers can use the local `data/curated/` database layer for confirmed paper records, author–institution mappings, durable exclusions, location-review queues, and evidence-backed institution coordinates. OpenAlex remains a candidate metadata source, while public preview JSON remains generated output. The deployed public site is read-only; maintainer editing is local only.

The local admin browser is an **Interactive Curation Console** with a dashboard, paper metadata overrides, scope review, author–institution mappings, institution location confirmation, high-risk marker review, marker blocker review, key-paper coverage review, manual/OpenAlex import review, fixed refresh workflows, validation status, and Git status. Start it with `python3 scripts/serve_admin.py`, then open the tokenized localhost URL printed in the terminal. See the [local admin workflow](docs/admin_workflow.md) for the complete maintainer runbook. The console never commits or pushes and adds no admin behavior to GitHub Pages.

Durable maintainer decisions live in `data/curated/*.csv`. Files in `data/manual/*.csv` are generated review inputs, `web/data/*.json` is generated public-preview output, and `data/processed/*.csv` remains an unedited source layer. The intended cycle is: review queue → curated decision → full refresh → validation → manual diff/commit/push.

Maintainers can also use the local browser's **Delete / Scope Review** workflow to record durable exclusions for out-of-scope papers. Decisions are stored in `data/curated/paper_exclusions.csv`; the public-preview exporter applies active exclusions without modifying OpenAlex-derived processed CSV files. The deployed public site remains read-only.

The public-preview exporter merges eligible curated papers into the searchable paper list and turns active curated mappings into markers only when an exact institution match has one unique valid location. Confirmed records in `data/curated/institution_locations.csv` have location priority; when none exists, trusted active entries in `data/processed/institution_resolution_cache.json` may supply a clearly noted fallback without modifying the curated CSV. Missing or ambiguous locations remain marker-free and enter the curated location-review queue. Header-only curated files leave preview output unchanged.

## Data collection prototype

The standard-library OpenAlex search script can preview its default candidate-paper queries without making API requests or writing files. The defaults are grouped into detection and source attribution, with explicit generated-image wording in every query:

```bash
python3 scripts/search_openalex.py --dry-run
```

Broad model/generator attribution, feature attribution, authorship attribution, camera or sensor attribution, and synthetic-data training or augmentation queries are intentionally excluded. OpenAlex output is raw candidate data and requires manual review before anything is added to `data/manual/`. See [docs/data_collection.md](docs/data_collection.md) for the grouped default query list, query-file options, result limits, API-key handling, and raw-output details. Each manifest entry records the exact query string used.

After raw OpenAlex archives are available, preview the candidate extraction step:

```bash
python3 scripts/extract_openalex_candidates.py --dry-run
```

Then write the complete audit CSVs and their scoped downstream counterparts:

```bash
python3 scripts/extract_openalex_candidates.py
```

The complete `openalex_candidate_papers.csv` and `openalex_candidate_affiliations.csv` files retain every candidate for audit. The additional `*_in_scope.csv` files contain only papers marked `in_scope=true` and their matching affiliations. All remain automatically extracted review material with `manual_review=true`.

Affiliations are represented at paper-author-institution level. Every OpenAlex authorship is preserved, authors with multiple institutions produce multiple relationship rows, and raw-only or missing affiliations remain reviewable rather than being dropped. Map records retain the full paper author list in publication order and separately identify the authors affiliated with each mapped institution; first-author-only mapping is intentionally avoided.

Public map records count Hong Kong, Macau/Macao, and Taiwan under China while retaining those names and their `HK`, `MO`, and `TW` codes as regional metadata. Original source country values remain available in raw-country fields; raw, cached, processed, and manual source data are not rewritten by this display normalization.

Candidate papers receive a conservative rule-based relevance assessment. `in_scope=true` requires explicit AI-generated/synthetic image context plus detection or generated-image source-attribution context. Broad model, feature, saliency, explainable-AI, authorship, camera-model, sensor, and generic attribution are excluded, as are synthetic-data applications such as augmentation, medical diagnosis, downstream recognition, and remote sensing. All candidates remain auditable, but only scoped records proceed downstream.

The extractor also preserves OpenAlex publication year/date, venue and source type, publisher, publication type, DOI, arXiv identifiers and links, and source URLs. Missing venues remain unknown rather than being inferred, and detected arXiv records are explicitly marked as preprints for review. Manually confirmed alternate versions, such as an arXiv version of a published OpenAlex record, can be recorded in `data/manual/paper_version_overrides.csv`; exporters attach those arXiv links without changing published DOI, venue, year, or paper URL metadata.

Search for additional arXiv versions and write a separate manual-review table:

```bash
python3 scripts/enrich_papers_arxiv.py --limit 50
```

The script reuses existing valid arXiv identifiers and strong local formal/preprint pairs before querying arXiv, resumes from `data/manual/paper_arxiv_links.csv`, and writes match evidence and review-only candidates to `data/manual/arxiv_link_enrichment_report.csv`. It never changes candidate data. A `not_found_in_arxiv` result means only that this step did not record or find a version, not that none exists.

### Key paper coverage audit

Import the lightweight coverage checklist from local Word documents in `data/manual/source_docs/`:

```bash
python3 scripts/import_key_papers_from_docx.py
```

The importer updates only `data/manual/key_papers.csv`; checklist membership does not publish a paper. This file is the manually curated in-scope coverage checklist: missing entries in downstream data are coverage gaps, not scope-filter candidates. OpenAlex is a metadata source rather than coverage ground truth. Then compare the checklist with the full candidate paper CSV and public preview:

Enrich missing DOI, OpenAlex, and paper links with conservative title matching:

```bash
export OPENALEX_API_KEY="your-local-openalex-key"
python3 scripts/enrich_key_papers_openalex.py \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)" \
  --only-missing
```

This writes `data/manual/key_papers_enriched.csv` and `docs/key_paper_enrichment_report.md` without overwriting the manually curated checklist. The script reads `OPENALEX_API_KEY` from the environment, or `--api-key` if supplied; never commit or share the key. Request URLs printed by debug/error output redact the key. The script requests 25 relevance-sorted results by default and tries general search, Web-like title/title-and-abstract parameters, then title/title-and-abstract filters. It stops at the first strong link; `--per-page` changes the result count. Statuses describe OpenAlex linkage: strong title/year candidates are `linked_to_openalex`, while `possible_openalex_match` candidates remain unfilled for review. Linkage does not validate or publish a paper.

If `data/manual/key_papers_enriched.csv` already exists, enrichment resumes from it by default. Rows with `linked_to_openalex`, `possible_openalex_match`, or `not_found_in_openalex` are reused by normalized title plus year without spending OpenAlex budget. Use `--force` to re-query selected rows, or `--no-resume-from-output` to ignore the existing output cache. If OpenAlex returns a fatal error such as HTTP 429, the script writes a partial CSV/report that can be resumed later.

Retry only records not found during an earlier enrichment run:

```bash
python3 scripts/enrich_key_papers_openalex.py \
  --input data/manual/key_papers_enriched.csv \
  --output data/manual/key_papers_enriched.csv \
  --only-status not_found_in_openalex \
  --force \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)"
```

Existing completed rows are preserved unless `--force` is used. Updating the enriched CSV in place is supported; overwriting `data/manual/key_papers.csv` is refused.

Diagnose one unresolved title with `--title-contains` and full per-strategy output:

```bash
python3 scripts/enrich_key_papers_openalex.py \
  --input data/manual/key_papers_enriched.csv \
  --output data/manual/key_papers_enriched.csv \
  --only-status not_found_in_openalex \
  --force \
  --title-contains "Forensic Invariant Learning" \
  --debug
```

The console and enrichment report show selection, preservation, and actual-search counts so an unchanged status total can be diagnosed directly.

Then run the coverage comparison:

```bash
python3 scripts/audit_key_paper_coverage.py
```

The report writes `data/manual/key_paper_coverage_report.csv` and uses `covered_in_public_preview`, `in_candidate_map_but_not_public_preview`, `in_openalex_candidate_pool_but_not_exported`, `missing_from_openalex_candidate_pool`, and `possible_title_match_failure`. Missing papers should be reviewed for import or enrichment. Papers present in OpenAlex but absent from exports should be diagnosed for affiliation, coordinate, or export-rule issues. The audit measures coverage gaps and never makes scope decisions or publishes a checklist row.

### Automatic institution resolution

Run authoritative institution resolution before generic geocoding. Start with a network-free preview:

```bash
python3 scripts/resolve_candidate_institutions.py --dry-run
```

For a small online batch, provide an identifying user agent and request limit:

```bash
python3 scripts/resolve_candidate_institutions.py \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)" \
  --limit 10
```

The resolver uses ROR IDs first, optional OpenAlex institution IDs second, and exact normalized name-and-country matches from its cache only when no identifier is available. High-confidence authoritative coordinates can support exploratory visualization, but the generated files remain candidate metadata rather than curated institution data. Pass `data/processed/openalex_candidate_affiliations_resolved.csv` to later geocoding or export steps.

### Manual institution corrections

Institution geocoding overrides belong in `data/manual/institution_corrections.csv`. The geocoder applies exact normalized-name matches from this table before using its cache or Nominatim; it does not use fuzzy matching. Corrected coordinates and optional institution, city, and country values retain their provenance in `notes` and remain marked for manual review.

Documentation-only fictional correction example:

```csv
fictional institute,Fictional Institute of Visual Studies,Example City,Example Country,12.3456,78.9012,https://example.invalid/institution,high,Fictional format example only
```

### Candidate affiliation geocoding

Preview the unique affiliation queries without making network requests or writing files:

```bash
python3 scripts/geocode_candidate_affiliations.py --dry-run
```

For a small, deliberate online run, provide a custom identifying user agent and consider using `--limit` first:

```bash
python3 scripts/geocode_candidate_affiliations.py \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)" \
  --limit 10
```

The script uses a local cache and waits 1.2 seconds between requests by default. Review the [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/) before online use; the public service requires an identifying user agent, caching, single-threaded requests, and no more than one request per second.

Build a deduplicated institution review queue from the original and geocoded candidate affiliations:

```bash
python3 scripts/build_institution_review_queue.py
```

Use `--dry-run` to preview queue counts and examples without writing `data/processed/institution_review_queue.csv`.

Preview the candidate CSV-to-map export without writing JSON:

```bash
python3 scripts/export_candidate_map_data.py --dry-run
```

Generate the local candidate map dataset:

```bash
python3 scripts/export_candidate_map_data.py
```

To export the map from the preliminary geocoded affiliations instead:

```bash
python3 scripts/export_candidate_map_data.py \
  --affiliations-csv data/processed/openalex_candidate_affiliations_geocoded.csv
```

To prefer authoritative resolved institution metadata and cap the exploratory export:

```bash
python3 scripts/export_candidate_map_data.py --affiliations-csv data/processed/openalex_candidate_affiliations_resolved.csv --max-records 200
```

With the local HTTP server running, open [http://localhost:8000/web/?dataset=openalex](http://localhost:8000/web/?dataset=openalex) to explore the candidate map. `web/data/openalex_candidate_map_data.json` is generated locally, ignored by Git, and intended only for exploratory visualization of uncurated candidates.

Candidate OpenAlex map records may include institution resolution method, confidence, review status, and resolution notes. Popups also display compact publication metadata: year, venue, publication type, DOI, arXiv/preprint status, and available paper links. A high-confidence institution resolution still remains candidate metadata unless the paper and affiliation are manually reviewed and curated.

### Public preview export

The website supports three dataset modes. Opening `/web/` without a dataset parameter tries the public preview first and clearly falls back to the fictional sample if the preview file is unavailable:

- The **public preview dataset** is the public default, generated as strict map markers at `web/data/public_preview_map_data.json` plus a broader searchable paper list at `web/data/public_preview_papers.json`, and can be opened explicitly with `?dataset=preview`.
- The **fictional sample dataset** is committed toy data for demonstrating the interface and can be opened with `?dataset=sample`.
- The **local OpenAlex candidate dataset** is generated at `web/data/openalex_candidate_map_data.json`, opened with `?dataset=openalex`, and ignored by Git. This mode is intended only for local generated data.

Preview the default filtering without writing a file:

```bash
python3 scripts/export_public_preview.py --dry-run
```

Export all eligible medium-or-higher-confidence map records while excluding records marked as needing review:

```bash
python3 scripts/export_public_preview.py
```

For a capped high-confidence-only preview:

```bash
python3 scripts/export_public_preview.py --max-map-records 50 --min-confidence high
```

The public preview contains provenance-labeled OpenAlex candidate metadata plus any eligible maintainer-confirmed curated records; it is not a uniformly curated final bibliography. The map marker export includes all eligible `detection`, `source_attribution`, and `detection_and_source_attribution` records with usable institution coordinates by default; uncertain, out-of-scope, low-confidence, review-flagged, missing-institution, and missing-coordinate marker records are excluded. Use `--max-map-records` (or the legacy `--max-records` alias) for limited test or performance-fallback exports. The paper-level preview list can include in-scope/key/candidate/curated papers that still need affiliation or coordinate review, and marks them with coverage flags rather than inventing locations. Use `--include-missing-location` only for local debugging of otherwise unmappable automatic marker records.

Generate a Markdown quality summary for the currently published preview:

```bash
python3 scripts/report_public_preview.py
```

The report is written to `docs/public_preview_report.md` and summarizes coverage, publication metadata, institution resolution confidence, and records requiring further inspection.

Validate the refreshed preview before committing it. Strict mode also treats
warnings as publication blockers:

```bash
python3 scripts/validate_public_preview.py --strict
```

### Refresh public preview

Run the scoped pipeline, rebuild the public preview and quality report, and
validate the result with one command:

```bash
python3 scripts/refresh_public_preview.py \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)"
```

Add `--skip-search` to reuse existing raw OpenAlex responses or `--strict` to
treat validation warnings as failures. Inspect the refreshed JSON and report,
and ensure validation passes before committing them; the script never commits
or pushes files.

## One-command pipeline

Preview the complete workflow without executing subprocesses or writing files:

```bash
python3 scripts/run_pipeline.py --dry-run
```

Run a small end-to-end candidate batch:

```bash
python3 scripts/run_pipeline.py \
  --max-results 10 \
  --limit 5 \
  --user-agent "SyntheticImageResearchMap/0.1 (contact: you@example.org)"
```

The pipeline searches and extracts all candidates for audit, then sends only in-scope papers and affiliations through resolution, optional geocoding, map export, and the institution review queue. Use `--skip-search` to reuse existing raw responses. `--include-out-of-scope` enables a deliberate debugging run; normal visualization should use the scoped default. Generated outputs remain local candidate data and are never promoted into `data/manual/` automatically.

## Local Preview

The prototype loads its JSON data with `fetch`, so preview it through a local HTTP server rather than opening `web/index.html` directly:

```bash
python3 -m http.server 8000
```

Then open [http://localhost:8000/web/](http://localhost:8000/web/) for the preview-first default, or [http://localhost:8000/web/?dataset=sample](http://localhost:8000/web/?dataset=sample) for the fictional sample.

The public preview remains primarily automatically generated candidate metadata, with provenance-labeled curated records included when available; it is not a uniformly manually curated bibliography. Leaflet and OpenStreetMap map resources are loaded from public CDNs, so the map tiles require an internet connection during preview.

## GitHub Pages Deployment

1. Go to the repository **Settings**.
2. Open **Pages**.
3. Set **Source** to **Deploy from a branch**.
4. Select the `main` branch and the `/root` folder.
5. Save the settings.
6. Open the generated GitHub Pages URL.

The GitHub Pages URL redirects to `/web/?dataset=preview`, so visitors see the committed public preview by default. The public site only shows committed files; locally generated candidate data is not published unless it is explicitly committed.

Open `/web/?dataset=sample` to view the fictional sample manually. The `?dataset=openalex` mode is reserved for local generated data and normally will not be available on GitHub Pages.

## Current Limitations

The online preview is an automatically generated candidate view based on OpenAlex metadata, not a manually curated bibliography. Paper relevance, task labels, institution names, and coordinates may contain errors, so the map should be used for exploratory visualization rather than authoritative bibliographic analysis. Future versions will add more manual validation and broader bibliographic sources.

## Current Status

**Early prototype.** A minimal static Leaflet.js map demonstrates markers, paper popups, filters, and visible-record summaries using an uncurated public candidate preview and a separate fictional sample dataset.
