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

## Local Preview

The prototype loads its JSON data with `fetch`, so preview it through a local HTTP server rather than opening `web/index.html` directly:

```bash
python3 -m http.server 8000
```

Then open [http://localhost:8000/web/](http://localhost:8000/web/).

The current map uses only clearly fictional toy records from `web/data/sample_map_data.json`. Leaflet and OpenStreetMap map resources are loaded from public CDNs, so the map tiles require an internet connection during preview.

## Current Status

**Early prototype.** A minimal static Leaflet.js map demonstrates markers, paper popups, task and year filters, and visible-record summaries using fictional toy data. Real literature collection and ingestion have not yet been implemented.
