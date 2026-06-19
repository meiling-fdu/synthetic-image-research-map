#!/usr/bin/env python3
"""Geocode uncurated candidate affiliations with a local Nominatim cache.

Coordinates produced here are preliminary candidates. They require manual review and
must never be treated as curated institution locations without confirmation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_INPUT = Path(
    "data/processed/openalex_candidate_affiliations_resolved.csv"
)
DEFAULT_OUTPUT = Path(
    "data/processed/openalex_candidate_affiliations_geocoded.csv"
)
DEFAULT_CACHE = Path("data/processed/geocoding_cache.json")
DEFAULT_CORRECTIONS = Path("data/manual/institution_corrections.csv")
DEFAULT_SLEEP_SECONDS = 1.2
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
MANUAL_DATA_DIR = Path("data/manual")

REQUIRED_COLUMNS = {
    "institution_name",
    "city",
    "country",
    "latitude",
    "longitude",
    "manual_review",
    "notes",
}
CORRECTION_COLUMNS = {
    "match_key",
    "corrected_institution_name",
    "corrected_city",
    "corrected_country",
    "corrected_latitude",
    "corrected_longitude",
    "correction_source",
    "confidence",
    "notes",
}


class GeocodingError(RuntimeError):
    """An expected file, response, or service error shown without a traceback."""


class GeocodingServiceError(GeocodingError):
    """A service error that must stop further online requests."""


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def polite_delay(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 1.0:
        raise argparse.ArgumentTypeError(
            "must be at least 1.0 second for the public Nominatim service"
        )
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Enrich candidate affiliation rows with preliminary Nominatim coordinates. "
            "Use --dry-run to inspect queries without network requests or file writes."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Candidate affiliation CSV (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Geocoded candidate CSV (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=DEFAULT_CACHE,
        help=f"Local geocoding cache (default: {DEFAULT_CACHE}).",
    )
    parser.add_argument(
        "--corrections",
        type=Path,
        default=DEFAULT_CORRECTIONS,
        help=f"Manual institution correction table (default: {DEFAULT_CORRECTIONS}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned unique queries without requests or writes.",
    )
    parser.add_argument(
        "--include-out-of-scope",
        action="store_true",
        help=(
            "Process rows marked in_scope=false when supplied for debugging; "
            "default pipeline inputs contain only in-scope affiliations."
        ),
    )
    parser.add_argument(
        "--limit",
        type=positive_int,
        help="Maximum number of uncached online queries for this run.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=polite_delay,
        default=DEFAULT_SLEEP_SECONDS,
        help=(
            "Delay between online requests; minimum 1.0 "
            f"(default: {DEFAULT_SLEEP_SECONDS})."
        ),
    )
    parser.add_argument(
        "--user-agent",
        default="",
        help="Required custom identifying User-Agent for non-dry online runs.",
    )
    return parser.parse_args(argv)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def unique_strings(values: Iterable[Any]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        cleaned = clean_text(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def append_note(row: Dict[str, str], message: str) -> None:
    existing = clean_text(row.get("notes"))
    notes = unique_strings(
        [*(existing.split(" | ") if existing else []), clean_text(message)]
    )
    row["notes"] = " | ".join(notes)


def parse_bool(value: Any) -> bool:
    return clean_text(value).casefold() in {"1", "true", "yes", "y"}


def select_scope_rows(
    rows: Sequence[Dict[str, str]], include_out_of_scope: bool
) -> List[Dict[str, str]]:
    if include_out_of_scope or not any("in_scope" in row for row in rows):
        return list(rows)
    return [row for row in rows if parse_bool(row.get("in_scope"))]


def valid_coordinate(value: Any, minimum: float, maximum: float) -> bool:
    cleaned = clean_text(value)
    if not cleaned:
        return False
    try:
        coordinate = float(cleaned)
    except ValueError:
        return False
    return math.isfinite(coordinate) and minimum <= coordinate <= maximum


def row_has_valid_coordinates(row: Dict[str, str]) -> bool:
    return valid_coordinate(row.get("latitude"), -90.0, 90.0) and valid_coordinate(
        row.get("longitude"), -180.0, 180.0
    )


def normalize_institution_name(value: Any) -> str:
    """Normalize punctuation and whitespace for exact, non-fuzzy matching."""
    lowered = clean_text(value).casefold()
    without_punctuation = re.sub(r"[_\W]+", " ", lowered)
    return " ".join(without_punctuation.split())


def build_query(row: Dict[str, str]) -> str:
    """Use only institution and known location fields; never infer from author text."""
    institution = clean_text(row.get("institution_name"))
    city = clean_text(row.get("city"))
    country = clean_text(row.get("country"))
    if institution:
        return ", ".join(unique_strings([institution, city, country]))
    return ", ".join(unique_strings([city, country]))


def cache_key(query: str) -> str:
    return clean_text(query).casefold()


def path_is_in_manual_data(path: Path) -> bool:
    try:
        path.resolve().relative_to(MANUAL_DATA_DIR.resolve())
        return True
    except ValueError:
        return False


def read_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            missing = sorted(REQUIRED_COLUMNS - set(fieldnames))
            if missing:
                raise GeocodingError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return fieldnames, [dict(row) for row in reader]
    except OSError as error:
        raise GeocodingError(f"Could not read {path}: {error}") from error


def read_corrections(path: Path) -> Dict[str, Dict[str, str]]:
    """Read manual overrides without ever modifying their source file."""
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(CORRECTION_COLUMNS - set(reader.fieldnames or []))
            if missing:
                raise GeocodingError(
                    f"{path} is missing correction columns: {', '.join(missing)}"
                )

            corrections = {}
            for line_number, row in enumerate(reader, start=2):
                if not any(clean_text(value) for value in row.values()):
                    continue
                normalized_key = normalize_institution_name(row.get("match_key"))
                if not normalized_key:
                    raise GeocodingError(
                        f"{path}:{line_number} has no usable match_key."
                    )
                if normalized_key in corrections:
                    raise GeocodingError(
                        f"{path}:{line_number} duplicates normalized match_key "
                        f"'{normalized_key}'."
                    )
                if not valid_coordinate(
                    row.get("corrected_latitude"), -90.0, 90.0
                ) or not valid_coordinate(
                    row.get("corrected_longitude"), -180.0, 180.0
                ):
                    raise GeocodingError(
                        f"{path}:{line_number} must provide valid corrected latitude "
                        "and longitude values."
                    )
                confidence = clean_text(row.get("confidence")).casefold()
                if confidence and confidence not in {"high", "medium", "low"}:
                    raise GeocodingError(
                        f"{path}:{line_number} confidence must be high, medium, low, "
                        "or empty."
                    )
                corrections[normalized_key] = dict(row)
            return corrections
    except OSError as error:
        raise GeocodingError(f"Could not read corrections {path}: {error}") from error


def correction_note(correction: Dict[str, str]) -> str:
    details = [
        f"Manual institution correction applied for match_key '{clean_text(correction.get('match_key'))}'."
    ]
    source = clean_text(correction.get("correction_source"))
    confidence = clean_text(correction.get("confidence"))
    correction_notes = clean_text(correction.get("notes"))
    if source:
        details.append(f"Source: {source}.")
    if confidence:
        details.append(f"Confidence: {confidence}.")
    if correction_notes:
        details.append(f"Correction note: {correction_notes}")
    details.append("Manual provenance retained; verify before curation.")
    return " ".join(details)


def apply_manual_corrections(
    rows: Sequence[Dict[str, str]],
    corrections: Dict[str, Dict[str, str]],
) -> int:
    """Apply exact normalized-name overrides before cache or online geocoding."""
    corrected_rows = 0
    for row in rows:
        normalized_name = normalize_institution_name(row.get("institution_name"))
        correction = corrections.get(normalized_name)
        if correction is None:
            continue

        row["latitude"] = clean_text(correction.get("corrected_latitude"))
        row["longitude"] = clean_text(correction.get("corrected_longitude"))
        for target, source in (
            ("institution_name", "corrected_institution_name"),
            ("city", "corrected_city"),
            ("country", "corrected_country"),
        ):
            corrected_value = clean_text(correction.get(source))
            if corrected_value:
                row[target] = corrected_value
        row["manual_review"] = "true"
        append_note(row, correction_note(correction))
        corrected_rows += 1
    return corrected_rows


def empty_cache() -> Dict[str, Any]:
    return {
        "cache_version": 1,
        "provider": "OpenStreetMap Nominatim",
        "updated_at": None,
        "results": {},
    }


def load_cache(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return empty_cache()
    try:
        with path.open("r", encoding="utf-8") as handle:
            cache = json.load(handle)
    except OSError as error:
        raise GeocodingError(f"Could not read cache {path}: {error}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise GeocodingError(f"Invalid JSON in cache {path}: {error}") from error

    if not isinstance(cache, dict) or not isinstance(cache.get("results"), dict):
        raise GeocodingError(f"Cache {path} does not have the expected format.")
    return cache


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def write_cache(path: Path, cache: Dict[str, Any]) -> None:
    cache["updated_at"] = utc_timestamp()
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(cache, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary_path.replace(path)
    except OSError as error:
        raise GeocodingError(f"Could not write cache {path}: {error}") from error


def write_rows(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        raise GeocodingError(f"Could not write output {path}: {error}") from error


def parse_nominatim_result(payload: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(payload, list):
        raise GeocodingServiceError("Nominatim returned an unexpected JSON response.")
    if not payload:
        return None
    first = payload[0]
    if not isinstance(first, dict):
        raise GeocodingServiceError("Nominatim returned an unexpected result record.")

    latitude = clean_text(first.get("lat"))
    longitude = clean_text(first.get("lon"))
    if not valid_coordinate(latitude, -90.0, 90.0) or not valid_coordinate(
        longitude, -180.0, 180.0
    ):
        raise GeocodingServiceError(
            "Nominatim returned a result without valid coordinates."
        )
    return {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "display_name": clean_text(first.get("display_name")),
        "osm_type": clean_text(first.get("osm_type")),
        "osm_id": clean_text(first.get("osm_id")),
    }


def geocode_query(query: str, user_agent: str) -> Optional[Dict[str, Any]]:
    params = urlencode(
        {
            "q": query,
            "format": "jsonv2",
            "limit": 1,
            "addressdetails": 1,
        }
    )
    request = Request(
        f"{NOMINATIM_SEARCH_URL}?{params}",
        headers={
            "Accept": "application/json",
            "User-Agent": user_agent,
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        if error.code == 429:
            raise GeocodingServiceError(
                "Nominatim rate limit reached (HTTP 429). Stop and retry later."
            ) from error
        if error.code in (401, 403):
            raise GeocodingServiceError(
                f"Nominatim rejected the request (HTTP {error.code}). Check the "
                "custom User-Agent and usage policy before retrying."
            ) from error
        raise GeocodingServiceError(
            f"Nominatim returned HTTP {error.code}; online geocoding stopped."
        ) from error
    except URLError as error:
        raise GeocodingServiceError(
            f"Could not reach Nominatim; online geocoding stopped: {error.reason}"
        ) from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise GeocodingServiceError(
            "Nominatim returned a response that was not valid JSON."
        ) from error
    return parse_nominatim_result(payload)


def collect_queries(
    rows: Sequence[Dict[str, str]],
) -> Tuple[int, List[str], int]:
    rows_with_coordinates = 0
    queries = []
    rows_without_query = 0
    seen = set()

    for row in rows:
        if row_has_valid_coordinates(row):
            rows_with_coordinates += 1
            continue
        query = build_query(row)
        if not query:
            rows_without_query += 1
            continue
        key = cache_key(query)
        if key not in seen:
            seen.add(key)
            queries.append(query)
    return rows_with_coordinates, queries, rows_without_query


def resolved_cache_entry(query: str, result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "query": query,
        "status": "resolved",
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "display_name": result.get("display_name", ""),
        "osm_type": result.get("osm_type", ""),
        "osm_id": result.get("osm_id", ""),
        "cached_at": utc_timestamp(),
    }


def not_found_cache_entry(query: str) -> Dict[str, Any]:
    return {
        "query": query,
        "status": "not_found",
        "cached_at": utc_timestamp(),
    }


def cached_coordinates(entry: Any) -> Optional[Tuple[float, float]]:
    if not isinstance(entry, dict) or entry.get("status") != "resolved":
        return None
    latitude = entry.get("latitude")
    longitude = entry.get("longitude")
    if not valid_coordinate(latitude, -90.0, 90.0) or not valid_coordinate(
        longitude, -180.0, 180.0
    ):
        return None
    return float(latitude), float(longitude)


def cache_entry_is_usable(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    if entry.get("status") == "not_found":
        return True
    return cached_coordinates(entry) is not None


def run_dry_run(
    rows: Sequence[Dict[str, str]],
    cache: Dict[str, Any],
    corrected_rows: int,
    limit: Optional[int],
    input_count: Optional[int] = None,
) -> int:
    rows_with_coordinates, queries, rows_without_query = collect_queries(rows)
    rows_with_existing_coordinates = rows_with_coordinates - corrected_rows
    cached_results = cache["results"]
    uncached_queries = [
        query
        for query in queries
        if not cache_entry_is_usable(cached_results.get(cache_key(query)))
    ]
    attempted_queries = uncached_queries[:limit] if limit is not None else uncached_queries
    rows_needing_online_geocoding = 0
    unmatched_examples = []
    seen_examples = set()
    for row in rows:
        if row_has_valid_coordinates(row):
            continue
        query = build_query(row)
        if not query or cache_entry_is_usable(cached_results.get(cache_key(query))):
            continue
        rows_needing_online_geocoding += 1
        example = clean_text(row.get("institution_name")) or f"(no institution) {query}"
        normalized_example = normalize_institution_name(example)
        if normalized_example not in seen_examples:
            seen_examples.add(normalized_example)
            unmatched_examples.append(example)

    print("DRY RUN: no network requests were made and no files were written.")
    print(f"Input affiliation rows: {input_count if input_count is not None else len(rows)}")
    print(f"Downstream rows processed: {len(rows)}")
    print(f"Rows that would use manual corrections: {corrected_rows}")
    print(f"Rows already containing valid coordinates: {rows_with_existing_coordinates}")
    print(f"Rows needing online geocoding: {rows_needing_online_geocoding}")
    print(f"Rows lacking institution, city, and country: {rows_without_query}")
    print(f"Unique queries represented in the local cache: {len(queries) - len(uncached_queries)}")
    print(f"Unique uncached queries that would be attempted: {len(attempted_queries)}")
    for query in attempted_queries:
        print(f"  {query}")
    if limit is not None and len(uncached_queries) > limit:
        print(f"{len(uncached_queries) - limit} additional uncached queries excluded by --limit.")
    print("Examples of institutions without a manual correction:")
    if unmatched_examples:
        for example in unmatched_examples[:5]:
            print(f"  {example}")
    else:
        print("  None")
    return 0


def online_results(
    queries: Sequence[str],
    cache: Dict[str, Any],
    limit: Optional[int],
    sleep_seconds: float,
    user_agent: str,
) -> Tuple[Dict[str, str], int, bool]:
    """Resolve uncached queries serially and stop immediately on service errors."""
    failures: Dict[str, str] = {}
    requests_made = 0
    stopped = False

    for query in queries:
        key = cache_key(query)
        if cache_entry_is_usable(cache["results"].get(key)):
            continue
        if limit is not None and requests_made >= limit:
            continue
        if requests_made:
            time.sleep(sleep_seconds)
        requests_made += 1

        try:
            result = geocode_query(query, user_agent)
        except GeocodingServiceError as error:
            failures[key] = str(error)
            print(f"Error: {error}", file=sys.stderr)
            stopped = True
            break

        if result is None:
            cache["results"][key] = not_found_cache_entry(query)
            print(f"No result: {query}")
        else:
            cache["results"][key] = resolved_cache_entry(query, result)
            print(f"Resolved: {query}")

    return failures, requests_made, stopped


def enrich_rows(
    rows: Sequence[Dict[str, str]],
    cache: Dict[str, Any],
    failures: Dict[str, str],
    attempted_query_keys: set,
    limit_reached: bool,
) -> Tuple[int, int, int]:
    resolved_rows = 0
    unresolved_rows = 0
    unqueryable_rows = 0

    for row in rows:
        if row_has_valid_coordinates(row):
            continue
        row["manual_review"] = "true"
        query = build_query(row)
        if not query:
            append_note(
                row,
                "Geocoding not attempted: institution, city, and country are missing; manual review required.",
            )
            unresolved_rows += 1
            unqueryable_rows += 1
            continue

        key = cache_key(query)
        entry = cache["results"].get(key)
        coordinates = cached_coordinates(entry)
        if coordinates is not None:
            row["latitude"] = str(coordinates[0])
            row["longitude"] = str(coordinates[1])
            append_note(
                row,
                f"Preliminary Nominatim geocode for '{query}'; verify coordinates manually.",
            )
            resolved_rows += 1
        elif isinstance(entry, dict) and entry.get("status") == "not_found":
            append_note(
                row,
                f"Nominatim found no result for '{query}'; manual review required.",
            )
            unresolved_rows += 1
        elif key in failures:
            append_note(
                row,
                f"Geocoding failed for '{query}': {failures[key]}",
            )
            unresolved_rows += 1
        else:
            reason = (
                "Geocoding not attempted because --limit was reached."
                if limit_reached and key not in attempted_query_keys
                else "Geocoding was not completed in this run."
            )
            append_note(row, f"{reason} Manual review required for '{query}'.")
            unresolved_rows += 1

    return resolved_rows, unresolved_rows, unqueryable_rows


def run(args: argparse.Namespace) -> int:
    if path_is_in_manual_data(args.output) or path_is_in_manual_data(args.cache):
        print("Error: output and cache paths must not be inside data/manual/.", file=sys.stderr)
        return 1

    try:
        fieldnames, rows = read_rows(args.input)
        cache = load_cache(args.cache)
        corrections = read_corrections(args.corrections)
    except GeocodingError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    input_count = len(rows)
    rows = select_scope_rows(rows, args.include_out_of_scope)
    try:
        corrected_rows = apply_manual_corrections(rows, corrections)
    except GeocodingError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.dry_run:
        return run_dry_run(rows, cache, corrected_rows, args.limit, input_count)

    user_agent = clean_text(args.user_agent)
    if not user_agent:
        print(
            "Error: non-dry-run mode requires a non-empty custom --user-agent value.",
            file=sys.stderr,
        )
        return 1

    _, queries, _ = collect_queries(rows)
    uncached_queries = [
        query
        for query in queries
        if not cache_entry_is_usable(cache["results"].get(cache_key(query)))
    ]
    planned_queries = (
        uncached_queries[: args.limit] if args.limit is not None else uncached_queries
    )
    attempted_keys = {cache_key(query) for query in planned_queries}

    failures, requests_made, stopped = online_results(
        queries,
        cache,
        args.limit,
        args.sleep_seconds,
        user_agent,
    )
    limit_reached = args.limit is not None and len(uncached_queries) > args.limit
    resolved_rows, unresolved_rows, unqueryable_rows = enrich_rows(
        rows,
        cache,
        failures,
        attempted_keys,
        limit_reached,
    )

    try:
        write_cache(args.cache, cache)
        write_rows(args.output, fieldnames, rows)
    except GeocodingError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Wrote preliminary geocoded candidates: {args.output}")
    print(f"Updated local cache: {args.cache}")
    print("Geocoding summary:")
    print(f"  Input affiliation rows: {input_count}")
    print(f"  Downstream rows processed: {len(rows)}")
    print(f"  Rows using manual corrections: {corrected_rows}")
    print(f"  Online requests made: {requests_made}")
    print(f"  Rows resolved from cache or this run: {resolved_rows}")
    print(f"  Rows still unresolved: {unresolved_rows}")
    print(f"  Rows without enough fields for a query: {unqueryable_rows}")
    print("All geocoded coordinates are preliminary and require manual review.")
    return 1 if stopped else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
