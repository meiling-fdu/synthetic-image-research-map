# Data Collection

## OpenAlex Candidate Search

`scripts/search_openalex.py` is an early collection tool for discovering possible papers through the OpenAlex Works API. It uses only the Python standard library and searches the project's default synthetic image detection and attribution queries, or custom queries supplied in a text file.

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

## Raw-to-Processed Candidate Extraction

`scripts/extract_openalex_candidates.py` converts raw OpenAlex archives into two review-oriented CSV files:

- `data/processed/openalex_candidate_papers.csv` contains deduplicated paper metadata and preliminary rule-based labels.
- `data/processed/openalex_candidate_affiliations.csv` contains separate author-institution rows, preserving multiple authors and multiple institutions per paper.

Preview extraction from the repository root without writing files:

```bash
python3 scripts/extract_openalex_candidates.py --dry-run
```

Write the processed candidates after inspecting the dry-run counts:

```bash
python3 scripts/extract_openalex_candidates.py
```

Custom locations can be supplied with `--input-dir` and `--output-dir`. The defaults are `data/raw/openalex/` and `data/processed/`.

The extractor deduplicates by OpenAlex ID and falls back to a normalized title when an ID is missing. It reconstructs available abstracts only to apply simple detection, attribution, survey, deepfake, and image-editing keyword rules. These labels are preliminary and can be wrong, especially for broad search results. Uncertain records are retained with `preliminary_task=uncertain`, and every paper and affiliation row is written with `manual_review=true`.

Processed candidate CSVs are not final curated data. A reviewer must verify relevance, labels, author identities, institutions, affiliations, and locations before manually adding any record to `data/manual/`. The extractor never writes to or updates the manual CSV templates.

## Automatic institution resolution

`scripts/resolve_candidate_institutions.py` should run before generic geocoding. It resolves candidate institutions from authoritative identifiers without fuzzy matching or generic location search. ROR IDs are tried first using the [ROR single-record API](https://ror.readme.io/docs/api-single), optional OpenAlex institution IDs are tried second using the [OpenAlex institution API](https://docs.openalex.org/api-entities/institutions/get-a-single-institution), and rows without identifiers may use only an exact normalized institution-name and country match already present in the local resolution cache.

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

`scripts/geocode_candidate_affiliations.py` can add preliminary coordinates to candidate affiliation rows before the map export. It reads `data/processed/openalex_candidate_affiliations.csv`, writes `data/processed/openalex_candidate_affiliations_geocoded.csv`, and stores reusable query results in `data/processed/geocoding_cache.json` by default. Both generated files are ignored by Git.

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

`scripts/build_institution_review_queue.py` compares the original candidate affiliations with the geocoded output and generates `data/processed/institution_review_queue.csv`. The queue includes institutions with missing or invalid coordinates, failure notes, unexpected name changes, or suspiciously generic names. Entries are deduplicated by the same normalized institution name plus city and country.

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

`scripts/export_candidate_map_data.py` joins the processed paper and affiliation CSVs by `openalex_id` and generates `web/data/openalex_candidate_map_data.json` for local map exploration. It groups authors at each paper-institution location and preserves separate map records when a paper has multiple institutions.

The exporter includes only affiliation rows that already contain valid latitude and longitude values. It does not geocode missing institutions, call external APIs, or infer locations. Rows with missing or invalid coordinates remain in the processed CSV and are reported in the export summary rather than silently assigned a location.

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

The input and output paths can be changed with `--papers-csv`, `--affiliations-csv`, and `--output`. Use `--max-records` to limit the number of grouped map records exported during local exploration.

Serve the repository and open [http://localhost:8000/web/?dataset=openalex](http://localhost:8000/web/?dataset=openalex) to select the generated dataset. The JSON file is ignored by Git and should not be committed.

This map export is for exploratory visualization only. It is assembled from automatically extracted candidates, retains `manual_review`, and is not a curated or publication-ready research dataset. Nothing in this step writes to `data/manual/`.
