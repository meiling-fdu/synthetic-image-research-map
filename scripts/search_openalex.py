#!/usr/bin/env python3
"""Collect raw OpenAlex candidate records for later manual review."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


OPENALEX_WORKS_URL = "https://api.openalex.org/works"
DEFAULT_OUTPUT_DIR = Path("data/raw/openalex")
DEFAULT_MAX_RESULTS = 100
OPENALEX_PAGE_SIZE = 200
DEFAULT_QUERIES = (
    "synthetic image detection",
    "AI-generated image detection",
    "generated image detection",
    "diffusion image detection",
    "GAN image detection",
    "synthetic image attribution",
    "AI-generated image attribution",
    "generative model attribution",
    "source attribution generated images",
    "generated image source attribution",
)


class CollectionError(RuntimeError):
    """An expected error that should be shown without a traceback."""


def positive_int(value: str) -> int:
    """Parse a strictly positive command-line integer."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search OpenAlex for raw candidate papers. Use --dry-run to inspect "
            "request URLs without making network requests or writing output files."
        )
    )
    parser.add_argument(
        "--queries-file",
        type=Path,
        help="UTF-8 text file with one query per line; blank lines and # comments are ignored.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Raw output directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--max-results",
        type=positive_int,
        default=DEFAULT_MAX_RESULTS,
        help=f"Maximum candidate records to retrieve per query (default: {DEFAULT_MAX_RESULTS}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned OpenAlex URLs without making requests or writing files.",
    )
    return parser.parse_args(argv)


def unique_nonempty(values: Iterable[str]) -> List[str]:
    """Remove duplicate and empty queries while preserving their order."""
    seen = set()
    result = []
    for value in values:
        query = value.strip()
        if query and query not in seen:
            seen.add(query)
            result.append(query)
    return result


def load_queries(queries_file: Optional[Path]) -> List[str]:
    if queries_file is None:
        return list(DEFAULT_QUERIES)

    try:
        lines = queries_file.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise CollectionError(f"Could not read queries file {queries_file}: {error}") from error

    queries = unique_nonempty(
        line for line in lines if not line.lstrip().startswith("#")
    )
    if not queries:
        raise CollectionError(f"Queries file {queries_file} contains no usable queries.")
    return queries


def build_query_url(
    query: str,
    per_page: int,
    cursor: str,
    api_key: Optional[str],
) -> str:
    params = {
        "search": query,
        "per-page": per_page,
        "cursor": cursor,
    }
    if api_key:
        params["api_key"] = api_key
    return f"{OPENALEX_WORKS_URL}?{urlencode(params)}"


def redact_api_key(url: str) -> str:
    """Return a URL safe for logs and manifests."""
    parts = urlsplit(url)
    redacted_query = urlencode(
        [
            (key, "REDACTED" if key == "api_key" else value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, redacted_query, parts.fragment))


def initial_query_url(
    query: str,
    max_results: int,
    api_key: Optional[str],
) -> str:
    return build_query_url(
        query,
        min(OPENALEX_PAGE_SIZE, max_results),
        "*",
        api_key,
    )


def request_json(url: str) -> Dict[str, Any]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "synthetic-image-research-map/early-prototype",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        if error.code in (401, 403):
            raise CollectionError(
                "OpenAlex rejected authentication. Check OPENALEX_API_KEY and try again."
            ) from error
        if error.code == 429:
            raise CollectionError(
                "OpenAlex rate limit reached. Stop and retry later; no further requests were made."
            ) from error
        raise CollectionError(f"OpenAlex returned HTTP {error.code}; collection stopped.") from error
    except URLError as error:
        raise CollectionError(f"Could not reach OpenAlex; collection stopped: {error.reason}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise CollectionError("OpenAlex returned a response that was not valid JSON.") from error

    if not isinstance(payload, dict):
        raise CollectionError("OpenAlex returned an unexpected JSON response.")
    return payload


def collect_query(
    query: str,
    max_results: int,
    api_key: Optional[str],
) -> Tuple[List[Dict[str, Any]], List[str], int]:
    pages = []
    requested_urls = []
    result_count = 0
    cursor = "*"

    while result_count < max_results:
        per_page = min(OPENALEX_PAGE_SIZE, max_results - result_count)
        url = build_query_url(query, per_page, cursor, api_key)
        payload = request_json(url)
        results = payload.get("results")
        if not isinstance(results, list):
            raise CollectionError("OpenAlex response is missing the expected results list.")

        pages.append(payload)
        requested_urls.append(redact_api_key(url))
        result_count += len(results)

        meta = payload.get("meta")
        next_cursor = meta.get("next_cursor") if isinstance(meta, dict) else None

        # A short page or missing cursor means there are no further records.
        if len(results) < per_page or not next_cursor or result_count >= max_results:
            break
        cursor = str(next_cursor)

    return pages, requested_urls, min(result_count, max_results)


def slugify(query: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")
    return slug or "query"


def write_json(path: Path, payload: Any) -> None:
    """Write JSON atomically so interrupted runs do not leave partial files."""
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary_path.replace(path)


def utc_timestamp() -> Tuple[str, str]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return now.isoformat().replace("+00:00", "Z"), now.strftime("%Y%m%dT%H%M%SZ")


def run_dry_run(
    queries: Sequence[str],
    max_results: int,
    api_key: Optional[str],
) -> int:
    print("DRY RUN: no network requests will be made and no files will be written.")
    if api_key:
        print("OPENALEX_API_KEY is set; its value is redacted below.")
    for query in queries:
        print(f"\nQuery: {query}")
        url = initial_query_url(query, max_results, api_key)
        print(f"  {redact_api_key(url)}")
        if max_results > OPENALEX_PAGE_SIZE:
            print("  Additional page URLs depend on cursor tokens returned by OpenAlex.")
    return 0


def run_collection(
    queries: Sequence[str],
    output_dir: Path,
    max_results: int,
    api_key: Optional[str],
) -> int:
    timestamp, filename_timestamp = utc_timestamp()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_entries = []
    exit_code = 0

    for index, query in enumerate(queries, start=1):
        output_filename = (
            f"{filename_timestamp}_{index:03d}_{slugify(query)}.json"
        )
        entry: Dict[str, Any] = {
            "query": query,
            "timestamp": timestamp,
            "output_filename": output_filename,
            "result_count": None,
            "status": "pending",
        }

        print(f"Collecting query {index}/{len(queries)}: {query}")
        try:
            pages, requested_urls, result_count = collect_query(
                query, max_results, api_key
            )
            archive = {
                "archive_type": "openalex_raw_candidate_pages",
                "query": query,
                "retrieved_at": timestamp,
                "requested_urls": requested_urls,
                "pages": pages,
            }
            write_json(output_dir / output_filename, archive)
            entry.update(
                {
                    "result_count": result_count,
                    "status": "complete",
                }
            )
            print(f"  Saved {result_count} candidate records to {output_filename}")
        except CollectionError as error:
            entry.update({"status": "failed", "error": str(error)})
            print(f"Error: {error}", file=sys.stderr)
            exit_code = 1
            manifest_entries.append(entry)
            break

        manifest_entries.append(entry)

    manifest = {
        "source_database": "OpenAlex Works API",
        "created_at": timestamp,
        "max_results_per_query": max_results,
        "entries": manifest_entries,
    }
    manifest_path = output_dir / f"manifest_{filename_timestamp}.json"
    write_json(manifest_path, manifest)
    print(f"Manifest written to {manifest_path}")
    return exit_code


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        queries = load_queries(args.queries_file)
    except CollectionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    api_key = os.environ.get("OPENALEX_API_KEY") or None
    if args.dry_run:
        return run_dry_run(queries, args.max_results, api_key)
    return run_collection(queries, args.output_dir, args.max_results, api_key)


if __name__ == "__main__":
    sys.exit(main())
