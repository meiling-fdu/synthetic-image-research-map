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
