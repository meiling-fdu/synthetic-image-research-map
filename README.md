# Synthetic Image Research Map

An interactive academic world map for exploring papers, researchers, and institutions working on synthetic image detection and synthetic image attribution. The project is planned as a lightweight static website backed by transparent, reviewable datasets and Python-based preprocessing.

## Project Goals

- Map the global research landscape for synthetic image detection and attribution.
- Connect papers with their authors, institutions, affiliations, and locations without reducing a paper to a single author location.
- Preserve source metadata and data provenance throughout the collection and processing workflow.
- Make automatic classifications and uncertain records easy to review and correct manually.
- Distinguish core synthetic image research from related areas such as deepfake detection, face manipulation, image-editing attribution, and survey papers.

## Planned Features

- An interactive Leaflet.js world map of research institutions and affiliations.
- Browsing and filtering by paper, researcher, institution, country, task, and publication year.
- Separate labels for detection, attribution, deepfake or face manipulation, image-editing attribution, and survey or review work.
- Paper detail views with source metadata, authors, and all known affiliations.
- Reviewable task classifications and explicit flags for uncertain records.
- Locally cached geocoding with support for manually reviewed corrections.
- Static, portable web assets that do not require a backend server.

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

Then write the two processed candidate CSVs:

```bash
python3 scripts/extract_openalex_candidates.py
```

The processed paper and affiliation CSVs are automatically extracted review material, not manually curated final data. Every row keeps `manual_review=true` until a researcher reviews and deliberately promotes information into `data/manual/`.

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

With the local HTTP server running, open [http://localhost:8000/web/?dataset=openalex](http://localhost:8000/web/?dataset=openalex) to explore the candidate map. `web/data/openalex_candidate_map_data.json` is generated locally, ignored by Git, and intended only for exploratory visualization of uncurated candidates.

## Local Preview

The prototype loads its JSON data with `fetch`, so preview it through a local HTTP server rather than opening `web/index.html` directly:

```bash
python3 -m http.server 8000
```

Then open [http://localhost:8000/web/](http://localhost:8000/web/).

The current map uses only clearly fictional toy records from `web/data/sample_map_data.json`. Leaflet and OpenStreetMap map resources are loaded from public CDNs, so the map tiles require an internet connection during preview.

## Current Status

**Early prototype.** A minimal static Leaflet.js map demonstrates markers, paper popups, task and year filters, and visible-record summaries using fictional toy data. Real literature collection and ingestion have not yet been implemented.
