# AGENTS.md

## Project Goal

Build an interactive academic world map of papers, researchers, and institutions working on synthetic image detection and synthetic image attribution.

## Project Boundaries

- Keep this repository an independent website and data-visualization project.
- Prefer a lightweight static site.
- Do not create a backend server unless explicitly requested.
- Use Python scripts for data collection, cleaning, normalization, and preprocessing.
- Use Leaflet.js for the interactive world map.
- Do not use paid APIs.
- Never hardcode API keys or other credentials.
- Cache all geocoding results locally.
- Do not store private research code, model weights, private datasets, or experiment results in this repository.
- Before making major changes, explain which files will be created or modified and why.

## Research Scope

- Include synthetic image detection and synthetic image attribution.
- Focus on generated images, not audio or video.
- Mark deepfake and face-manipulation papers as a separate category when they are included.
- Mark image-editing attribution papers as a separate category when they are included.
- Survey and review papers may be included, but must be labeled as surveys or reviews.

## Data Integrity

- Preserve the source metadata for every paper, including enough information to trace each record back to its source.
- Keep raw data, processed data, and manual corrections separate.
- Never overwrite manually edited data files.
- Make automatically assigned task labels reviewable.
- Keep uncertain classifications and set a `manual_review` flag rather than silently forcing a category.
- Do not merge institution or author names without manual confirmation.
- Preserve every affiliation when a paper has multiple affiliations.
- Do not treat the first author's location as the location of the entire paper.
- Keep locally cached geocoding results reproducible and separate from manual corrections.

## Repository Layout

- `data/raw/`: Unmodified API responses and other source data.
- `data/processed/`: Cleaned, normalized, and derived datasets.
- `data/manual/`: Human-reviewed corrections, mappings, and overrides.
- `scripts/`: Python data collection and preprocessing scripts.
- `web/`: Static website assets and Leaflet.js application code.
- `docs/`: Project notes, methodology, schemas, and other documentation.

## Implementation Guidelines

- Keep Python scripts readable, focused, and modular.
- Add concise comments for non-trivial processing or classification logic.
- Avoid unnecessary dependencies; prefer the standard library when it remains clear and maintainable.
- Prefer CSV and JSON for intermediate data files.
- Make every script runnable from the repository root.
- Use paths relative to the repository root rather than relying on the caller's current subdirectory.
- Keep collection, normalization, classification, geocoding, and export steps separable where practical.
- Do not modify files in `data/manual/` from automated scripts.
- When combining automatic output with manual corrections, read manual files as overrides and write the result to `data/processed/`.

## Change Discipline

- Keep changes scoped to the requested task.
- Document new data sources, schemas, classification rules, and geocoding behavior.
- Preserve provenance fields through all processing stages.
- Treat ambiguous matches and classifications explicitly instead of hiding uncertainty.
- Verify that the static site can run without a custom backend.
