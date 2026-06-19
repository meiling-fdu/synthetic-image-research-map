# Synthetic Image Research Map

An interactive academic world map for exploring papers, researchers, and institutions working on synthetic image detection and synthetic image attribution. The project is planned as a lightweight static website backed by transparent, reviewable datasets and Python-based preprocessing.

**Online demo:** [Synthetic Image Research Map on GitHub Pages](https://meiling-fdu.github.io/synthetic-image-research-map/)

## Project Goals

- Map the global research landscape for synthetic image detection and attribution.
- Connect papers with their authors, institutions, affiliations, and locations without reducing a paper to a single author location.
- Preserve source metadata and data provenance throughout the collection and processing workflow.
- Make automatic classifications and uncertain records easy to review and correct manually.
- Distinguish core synthetic image research from related areas such as deepfake detection, face manipulation, image-editing attribution, and survey papers.

## Roadmap

1. Improve literature search coverage for synthetic image detection and attribution.
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
|   `-- manual/        # Human-reviewed corrections and overrides
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

## Data collection prototype

The standard-library OpenAlex search script can preview its default candidate-paper queries without making API requests or writing files:

```bash
python3 scripts/search_openalex.py --dry-run
```

OpenAlex output is raw candidate data and requires manual review before anything is added to `data/manual/`. See [docs/data_collection.md](docs/data_collection.md) for query-file, result-limit, API-key, and raw-output details.

After raw OpenAlex archives are available, preview the candidate extraction step:

```bash
python3 scripts/extract_openalex_candidates.py --dry-run
```

Then write the complete audit CSVs and their scoped downstream counterparts:

```bash
python3 scripts/extract_openalex_candidates.py
```

The complete `openalex_candidate_papers.csv` and `openalex_candidate_affiliations.csv` files retain every candidate for audit. The additional `*_in_scope.csv` files contain only papers marked `in_scope=true` and their matching affiliations. All remain automatically extracted review material with `manual_review=true`.

Affiliations are represented at paper-author-institution level. Every OpenAlex authorship is preserved, authors with multiple institutions produce multiple relationship rows, and raw-only or missing affiliations remain reviewable rather than being dropped. Map exports include every affiliated institution with usable coordinates and aggregate all associated collaborators for that paper-institution marker; first-author-only mapping is intentionally avoided.

Candidate papers receive a conservative rule-based relevance assessment. `in_scope=true` requires both an AI-generated/synthetic-image term and a detection/attribution task term, while explicit unrelated-domain terms override inclusion. All records are retained with scores and matched reasons, but only the scoped files proceed to institution resolution, geocoding, review queues, maps, and public previews by default.

The extractor also preserves OpenAlex publication year/date, venue and source type, publisher, publication type, DOI, arXiv identifiers and links, and source URLs. Missing venues remain unknown rather than being inferred, and detected arXiv records are explicitly marked as preprints for review.

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

- The **public preview dataset** is the public default, generated at `web/data/public_preview_map_data.json`, and can be opened explicitly with `?dataset=preview`.
- The **fictional sample dataset** is committed toy data for demonstrating the interface and can be opened with `?dataset=sample`.
- The **local OpenAlex candidate dataset** is generated at `web/data/openalex_candidate_map_data.json`, opened with `?dataset=openalex`, and ignored by Git. This mode is intended only for local generated data.

Preview the default filtering without writing a file:

```bash
python3 scripts/export_public_preview.py --dry-run
```

Export up to 200 medium-or-higher-confidence records while excluding records marked as needing review:

```bash
python3 scripts/export_public_preview.py
```

For a smaller high-confidence-only preview:

```bash
python3 scripts/export_public_preview.py --max-records 50 --min-confidence high
```

The public preview contains automatically generated OpenAlex candidate metadata, not a curated final bibliography. It excludes out-of-scope, low-confidence, and review-flagged records by default, while raw responses and caches remain local.

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

The public preview remains automatically generated candidate metadata, not a manually curated bibliography. Leaflet and OpenStreetMap map resources are loaded from public CDNs, so the map tiles require an internet connection during preview.

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
