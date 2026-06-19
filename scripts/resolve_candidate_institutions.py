#!/usr/bin/env python3
"""Resolve candidate institutions from authoritative IDs before geocoding.

All results remain candidate metadata. The script uses ROR and OpenAlex institution
records, never fuzzy-matches names, never performs generic geocoding, and never writes
to data/manual/.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

try:
    from geocode_candidate_affiliations import normalize_institution_name
except ModuleNotFoundError:
    from scripts.geocode_candidate_affiliations import normalize_institution_name


DEFAULT_INPUT = Path(
    "data/processed/openalex_candidate_affiliations_in_scope.csv"
)
DEFAULT_OUTPUT = Path(
    "data/processed/openalex_candidate_affiliations_resolved.csv"
)
DEFAULT_REPORT = Path("data/processed/institution_resolution_report.csv")
DEFAULT_CACHE = Path("data/processed/institution_resolution_cache.json")
DEFAULT_SLEEP_SECONDS = 1.0
MANUAL_DATA_DIR = Path("data/manual")
ROR_API_BASE = "https://api.ror.org/v2/organizations"
OPENALEX_API_BASE = "https://api.openalex.org/institutions"

RESOLUTION_COLUMNS = (
    "resolved_institution_name",
    "resolved_city",
    "resolved_country",
    "resolved_latitude",
    "resolved_longitude",
    "resolution_method",
    "resolution_confidence",
    "resolution_notes",
    "needs_review",
)

REPORT_COLUMNS = (
    "institution_name",
    "city",
    "country",
    "ror_id",
    "resolution_method",
    "resolution_confidence",
    "needs_review",
    "reason",
    "example_openalex_id",
    "example_author_name",
)

REQUIRED_COLUMNS = {
    "openalex_id",
    "author_name",
    "institution_name",
    "city",
    "country",
    "ror_id",
    "latitude",
    "longitude",
}

OPENALEX_INSTITUTION_COLUMNS = (
    "openalex_institution_id",
    "institution_openalex_id",
    "institution_id",
    "institution_url",
)

SUSPICIOUS_GENERIC_NAMES = (
    "Microsoft",
    "Meta",
    "Google",
    "Adobe",
    "OpenAI",
    "National Institute",
    "Institute of Art",
    "Cambridge School",
)


class ResolutionError(RuntimeError):
    """An expected file or metadata error shown without a traceback."""


class ResolutionServiceError(ResolutionError):
    """An API error that must stop further external requests."""


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def nonnegative_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative finite number")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve candidate institution metadata from ROR and OpenAlex IDs, "
            "then use exact name-country cache matches for rows without IDs."
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
        help=f"Resolved candidate CSV (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"Resolution report CSV (default: {DEFAULT_REPORT}).",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=DEFAULT_CACHE,
        help=f"Institution metadata cache (default: {DEFAULT_CACHE}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Summarize identifiers and planned requests without network or writes.",
    )
    parser.add_argument(
        "--include-out-of-scope",
        action="store_true",
        help=(
            "Process rows marked in_scope=false when a broader input CSV is supplied; "
            "the default scoped input excludes them."
        ),
    )
    parser.add_argument(
        "--limit",
        type=positive_int,
        help="Maximum number of uncached authoritative API requests.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=nonnegative_float,
        default=DEFAULT_SLEEP_SECONDS,
        help=f"Delay between API requests (default: {DEFAULT_SLEEP_SECONDS}).",
    )
    parser.add_argument(
        "--user-agent",
        default="",
        help="Identifying User-Agent required when external requests are needed.",
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


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def parse_bool(value: Any) -> bool:
    return clean_text(value).casefold() in {"1", "true", "yes", "y"}


def select_scope_rows(
    rows: Sequence[Dict[str, str]], include_out_of_scope: bool
) -> List[Dict[str, str]]:
    if include_out_of_scope or not any("in_scope" in row for row in rows):
        return list(rows)
    return [row for row in rows if parse_bool(row.get("in_scope"))]


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def valid_coordinate(value: Any, minimum: float, maximum: float) -> bool:
    cleaned = clean_text(value)
    if not cleaned:
        return False
    try:
        coordinate = float(cleaned)
    except ValueError:
        return False
    return math.isfinite(coordinate) and minimum <= coordinate <= maximum


def entry_coordinates(entry: Any) -> Optional[Tuple[float, float]]:
    if not isinstance(entry, dict) or entry.get("status") != "resolved":
        return None
    latitude = entry.get("resolved_latitude")
    longitude = entry.get("resolved_longitude")
    if not valid_coordinate(latitude, -90.0, 90.0) or not valid_coordinate(
        longitude, -180.0, 180.0
    ):
        return None
    return float(latitude), float(longitude)


def normalize_ror_id(value: Any) -> str:
    text = clean_text(value).lower().rstrip("/")
    if not text:
        return ""
    candidate = text.rsplit("/", 1)[-1]
    return candidate if re.fullmatch(r"0[a-hj-km-np-tv-z0-9]{6}[0-9]{2}", candidate) else ""


def normalize_openalex_institution_id(value: Any) -> str:
    text = clean_text(value)
    match = re.search(r"(?:https?://openalex\.org/)?(I[0-9]+)(?:/)?$", text, re.IGNORECASE)
    return match.group(1).upper() if match else ""


def openalex_institution_id(row: Dict[str, str]) -> str:
    for column in OPENALEX_INSTITUTION_COLUMNS:
        identifier = normalize_openalex_institution_id(row.get(column))
        if identifier:
            return identifier
    for column, value in row.items():
        lowered = column.casefold()
        if "institution" in lowered and ("id" in lowered or "url" in lowered):
            identifier = normalize_openalex_institution_id(value)
            if identifier:
                return identifier
    return ""


def is_generic_name(value: Any) -> bool:
    normalized = normalize_institution_name(value)
    padded = f" {normalized} "
    return any(
        f" {normalize_institution_name(name)} " in padded
        for name in SUSPICIOUS_GENERIC_NAMES
    )


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
                raise ResolutionError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return fieldnames, [dict(row) for row in reader]
    except OSError as error:
        raise ResolutionError(f"Could not read {path}: {error}") from error


def empty_cache() -> Dict[str, Any]:
    return {
        "cache_version": 1,
        "updated_at": None,
        "records": {},
    }


def load_cache(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return empty_cache()
    try:
        with path.open("r", encoding="utf-8") as handle:
            cache = json.load(handle)
    except OSError as error:
        raise ResolutionError(f"Could not read cache {path}: {error}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ResolutionError(f"Invalid JSON in cache {path}: {error}") from error
    if not isinstance(cache, dict) or not isinstance(cache.get("records"), dict):
        raise ResolutionError(f"Cache {path} does not have the expected format.")
    return cache


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary_path.replace(path)
    except OSError as error:
        raise ResolutionError(f"Could not write {path}: {error}") from error


def write_csv(
    path: Path,
    fieldnames: Sequence[str],
    rows: Sequence[Dict[str, str]],
) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        raise ResolutionError(f"Could not write {path}: {error}") from error


def cache_key(provider: str, identifier: str) -> str:
    return f"{provider}:{identifier.casefold()}"


def cached_identifier(cache: Dict[str, Any], provider: str, identifier: str) -> Any:
    return cache["records"].get(cache_key(provider, identifier))


def request_json(
    url: str,
    user_agent: str,
    provider: str,
) -> Optional[Dict[str, Any]]:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": user_agent},
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return None
        if error.code == 429:
            raise ResolutionServiceError(
                f"{provider} rate limit reached (HTTP 429); resolution stopped."
            ) from error
        if error.code in (401, 403):
            raise ResolutionServiceError(
                f"{provider} rejected the request (HTTP {error.code}); check access credentials."
            ) from error
        raise ResolutionServiceError(
            f"{provider} returned HTTP {error.code}; resolution stopped."
        ) from error
    except URLError as error:
        raise ResolutionServiceError(
            f"Could not reach {provider}; resolution stopped: {error.reason}"
        ) from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ResolutionServiceError(
            f"{provider} returned a response that was not valid JSON."
        ) from error
    if not isinstance(payload, dict):
        raise ResolutionServiceError(f"{provider} returned an unexpected JSON response.")
    return payload


def ror_display_name(payload: Dict[str, Any]) -> str:
    names = payload.get("names") if isinstance(payload.get("names"), list) else []
    for preferred_type in ("ror_display", "label"):
        for name in names:
            if not isinstance(name, dict):
                continue
            types = name.get("types") if isinstance(name.get("types"), list) else []
            if preferred_type in types and clean_text(name.get("value")):
                return clean_text(name.get("value"))
    for name in names:
        if isinstance(name, dict) and clean_text(name.get("value")):
            return clean_text(name.get("value"))
    return ""


def parse_ror_record(identifier: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    names = payload.get("names") if isinstance(payload.get("names"), list) else []
    name_values = [
        clean_text(name.get("value"))
        for name in names
        if isinstance(name, dict) and clean_text(name.get("value"))
    ]
    locations = (
        payload.get("locations") if isinstance(payload.get("locations"), list) else []
    )
    details: Dict[str, Any] = {}
    for location in locations:
        if not isinstance(location, dict):
            continue
        candidate = location.get("geonames_details")
        if isinstance(candidate, dict) and entry_coordinates(
            {
                "status": "resolved",
                "resolved_latitude": candidate.get("lat"),
                "resolved_longitude": candidate.get("lng"),
            }
        ):
            details = candidate
            break
    display_name = ror_display_name(payload)
    country_code = clean_text(details.get("country_code"))
    country_name = clean_text(details.get("country_name"))
    return {
        "status": "resolved",
        "provider": "ROR",
        "identifier": identifier,
        "canonical_id": clean_text(payload.get("id")) or f"https://ror.org/{identifier}",
        "resolved_institution_name": display_name,
        "resolved_city": clean_text(details.get("name")),
        "resolved_country": country_code or country_name,
        "resolved_latitude": details.get("lat", ""),
        "resolved_longitude": details.get("lng", ""),
        "match_names": unique_strings([display_name, *name_values]),
        "country_variants": unique_strings([country_code, country_name]),
        "record_status": clean_text(payload.get("status")),
        "source_url": f"{ROR_API_BASE}/{identifier}",
        "cached_at": utc_timestamp(),
    }


def parse_openalex_record(identifier: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    geo = payload.get("geo") if isinstance(payload.get("geo"), dict) else {}
    alternatives = (
        payload.get("display_name_alternatives")
        if isinstance(payload.get("display_name_alternatives"), list)
        else []
    )
    acronyms = (
        payload.get("display_name_acronyms")
        if isinstance(payload.get("display_name_acronyms"), list)
        else []
    )
    display_name = clean_text(payload.get("display_name"))
    country_code = clean_text(geo.get("country_code") or payload.get("country_code"))
    country_name = clean_text(geo.get("country"))
    return {
        "status": "resolved",
        "provider": "OpenAlex",
        "identifier": identifier,
        "canonical_id": clean_text(payload.get("id")) or f"https://openalex.org/{identifier}",
        "resolved_institution_name": display_name,
        "resolved_city": clean_text(geo.get("city")),
        "resolved_country": country_code or country_name,
        "resolved_latitude": geo.get("latitude", ""),
        "resolved_longitude": geo.get("longitude", ""),
        "match_names": unique_strings([display_name, *alternatives, *acronyms]),
        "country_variants": unique_strings([country_code, country_name]),
        "record_status": "active",
        "source_url": f"{OPENALEX_API_BASE}/{identifier}",
        "cached_at": utc_timestamp(),
    }


def not_found_entry(provider: str, identifier: str) -> Dict[str, Any]:
    return {
        "status": "not_found",
        "provider": provider,
        "identifier": identifier,
        "cached_at": utc_timestamp(),
    }


def request_identifier(
    provider: str,
    identifier: str,
    user_agent: str,
    openalex_api_key: str,
) -> Dict[str, Any]:
    if provider == "ror":
        url = f"{ROR_API_BASE}/{quote(identifier, safe='')}"
        payload = request_json(url, user_agent, "ROR")
        return parse_ror_record(identifier, payload) if payload else not_found_entry("ROR", identifier)

    params = {"api_key": openalex_api_key} if openalex_api_key else {}
    suffix = f"?{urlencode(params)}" if params else ""
    url = f"{OPENALEX_API_BASE}/{quote(identifier, safe='')}{suffix}"
    payload = request_json(url, user_agent, "OpenAlex")
    return (
        parse_openalex_record(identifier, payload)
        if payload
        else not_found_entry("OpenAlex", identifier)
    )


def planned_identifier_tasks(
    rows: Sequence[Dict[str, str]],
    cache: Dict[str, Any],
) -> List[Tuple[str, str]]:
    tasks = []
    seen = set()
    for row in rows:
        ror_id = normalize_ror_id(row.get("ror_id"))
        openalex_id = openalex_institution_id(row)
        task: Optional[Tuple[str, str]] = None
        if ror_id:
            ror_entry = cached_identifier(cache, "ror", ror_id)
            if ror_entry is None:
                task = ("ror", ror_id)
            elif entry_coordinates(ror_entry) is None and openalex_id:
                if cached_identifier(cache, "openalex", openalex_id) is None:
                    task = ("openalex", openalex_id)
        elif openalex_id and cached_identifier(cache, "openalex", openalex_id) is None:
            task = ("openalex", openalex_id)
        if task and task not in seen:
            seen.add(task)
            tasks.append(task)
    return tasks


def exact_cache_match(
    row: Dict[str, str],
    cache: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], bool]:
    name = normalize_institution_name(row.get("institution_name"))
    country = normalize_institution_name(row.get("country"))
    if not name or not country:
        return None, False

    matches: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for entry in cache["records"].values():
        coordinates = entry_coordinates(entry)
        if coordinates is None:
            continue
        names = {
            normalize_institution_name(value) for value in entry.get("match_names", [])
        }
        countries = {
            normalize_institution_name(value)
            for value in entry.get("country_variants", [])
        }
        if name not in names or country not in countries:
            continue
        signature = (
            normalize_institution_name(entry.get("resolved_institution_name")),
            str(coordinates[0]),
            str(coordinates[1]),
        )
        matches[signature] = entry
    if len(matches) == 1:
        return next(iter(matches.values())), False
    return None, len(matches) > 1


def country_conflicts(original_country: Any, entry: Dict[str, Any]) -> bool:
    original = normalize_institution_name(original_country)
    if not original:
        return False
    variants = {
        normalize_institution_name(value)
        for value in entry.get("country_variants", [])
        if clean_text(value)
    }
    return bool(variants) and original not in variants


def blank_resolution_fields(row: Dict[str, str]) -> None:
    for column in RESOLUTION_COLUMNS:
        row[column] = ""


def resolve_row(
    source_row: Dict[str, str],
    cache: Dict[str, Any],
) -> Tuple[Dict[str, str], List[str]]:
    row = dict(source_row)
    blank_resolution_fields(row)
    reasons = []
    method = "unresolved"
    confidence = "low"
    entry: Optional[Dict[str, Any]] = None

    ror_id = normalize_ror_id(row.get("ror_id"))
    openalex_id = openalex_institution_id(row)
    if ror_id:
        candidate = cached_identifier(cache, "ror", ror_id)
        if entry_coordinates(candidate) is not None:
            entry = candidate
            method = "ror_id"
            confidence = "high"
        elif openalex_id:
            candidate = cached_identifier(cache, "openalex", openalex_id)
            if entry_coordinates(candidate) is not None:
                entry = candidate
                method = "openalex_institution_id"
                confidence = "high"
        if entry is None:
            entry = candidate if isinstance(candidate, dict) and candidate.get("status") == "resolved" else None
            method = "ror_id"
            reasons.append("ror_identifier_unresolved")
    elif openalex_id:
        candidate = cached_identifier(cache, "openalex", openalex_id)
        if entry_coordinates(candidate) is not None:
            entry = candidate
            method = "openalex_institution_id"
            confidence = "high"
        else:
            entry = candidate if isinstance(candidate, dict) and candidate.get("status") == "resolved" else None
            method = "openalex_institution_id"
            reasons.append("openalex_identifier_unresolved")
    else:
        entry, ambiguous = exact_cache_match(row, cache)
        if entry is not None:
            method = "exact_name_country_cache_match"
            confidence = "medium"
        elif ambiguous:
            reasons.append("ambiguous_exact_name_country_cache_match")
        else:
            reasons.append("no_authoritative_identifier_or_exact_cache_match")

    coordinates = entry_coordinates(entry)
    if entry is not None:
        row["resolved_institution_name"] = clean_text(
            entry.get("resolved_institution_name")
        )
        row["resolved_city"] = clean_text(entry.get("resolved_city"))
        row["resolved_country"] = clean_text(entry.get("resolved_country"))
        if coordinates is not None:
            row["resolved_latitude"] = str(coordinates[0])
            row["resolved_longitude"] = str(coordinates[1])
            if not valid_coordinate(row.get("latitude"), -90.0, 90.0):
                row["latitude"] = str(coordinates[0])
            if not valid_coordinate(row.get("longitude"), -180.0, 180.0):
                row["longitude"] = str(coordinates[1])

    if coordinates is None:
        reasons.append("resolved_coordinates_missing")
        confidence = "low"
    if entry is not None and country_conflicts(row.get("country"), entry):
        reasons.append(
            "resolved_country_conflicts_with_source "
            f"(source={clean_text(row.get('country'))}, "
            f"resolved={clean_text(entry.get('resolved_country'))})"
        )
    if entry is not None and clean_text(entry.get("record_status")).casefold() not in {
        "",
        "active",
    }:
        reasons.append("authoritative_record_not_active")
    if is_generic_name(row.get("institution_name")) and method not in {
        "ror_id",
        "openalex_institution_id",
    }:
        reasons.append("generic_name_without_strong_identifier")

    reasons = unique_strings(reasons)
    needs_review = bool(reasons) or confidence == "low"
    row["resolution_method"] = method
    row["resolution_confidence"] = confidence
    row["needs_review"] = bool_text(needs_review)
    row["resolution_notes"] = (
        "; ".join(reasons)
        if reasons
        else "Resolved from authoritative candidate institution metadata."
    )
    return row, reasons or ["resolved"]


def build_report(
    source_rows: Sequence[Dict[str, str]],
    resolved_rows: Sequence[Dict[str, str]],
    row_reasons: Sequence[Sequence[str]],
) -> List[Dict[str, str]]:
    grouped: Dict[Tuple[str, ...], Dict[str, Any]] = {}
    for source, resolved, reasons in zip(source_rows, resolved_rows, row_reasons):
        key = (
            normalize_institution_name(source.get("institution_name")),
            normalize_institution_name(source.get("city")),
            normalize_institution_name(source.get("country")),
            normalize_ror_id(source.get("ror_id")),
            resolved["resolution_method"],
            resolved["resolution_confidence"],
            resolved["needs_review"],
        )
        group = grouped.get(key)
        if group is None:
            group = {
                "institution_name": clean_text(source.get("institution_name")),
                "city": clean_text(source.get("city")),
                "country": clean_text(source.get("country")),
                "ror_id": clean_text(source.get("ror_id")),
                "resolution_method": resolved["resolution_method"],
                "resolution_confidence": resolved["resolution_confidence"],
                "needs_review": resolved["needs_review"],
                "reasons": [],
                "example_openalex_id": clean_text(source.get("openalex_id")),
                "example_author_name": clean_text(source.get("author_name")),
            }
            grouped[key] = group
        group["reasons"].extend(reasons)

    report = []
    for group in grouped.values():
        report.append(
            {
                "institution_name": group["institution_name"],
                "city": group["city"],
                "country": group["country"],
                "ror_id": group["ror_id"],
                "resolution_method": group["resolution_method"],
                "resolution_confidence": group["resolution_confidence"],
                "needs_review": group["needs_review"],
                "reason": ";".join(unique_strings(group["reasons"])),
                "example_openalex_id": group["example_openalex_id"],
                "example_author_name": group["example_author_name"],
            }
        )
    return report


def dry_run(
    rows: Sequence[Dict[str, str]],
    cache: Dict[str, Any],
    limit: Optional[int],
    input_count: Optional[int] = None,
) -> int:
    rows_with_ror = sum(bool(normalize_ror_id(row.get("ror_id"))) for row in rows)
    rows_with_openalex = sum(bool(openalex_institution_id(row)) for row in rows)
    rows_without_ids = sum(
        not normalize_ror_id(row.get("ror_id")) and not openalex_institution_id(row)
        for row in rows
    )
    tasks = planned_identifier_tasks(rows, cache)
    selected = tasks[:limit] if limit is not None else tasks
    exact_matches = sum(
        exact_cache_match(row, cache)[0] is not None
        for row in rows
        if not normalize_ror_id(row.get("ror_id")) and not openalex_institution_id(row)
    )

    print("DRY RUN: no network requests were made and no files were written.")
    print(f"Input affiliation rows: {input_count if input_count is not None else len(rows)}")
    print(f"Downstream rows processed: {len(rows)}")
    print(f"Candidate affiliation rows: {len(rows)}")
    print(f"Rows with ROR IDs: {rows_with_ror}")
    print(f"Rows with OpenAlex institution IDs: {rows_with_openalex}")
    print(f"Rows without authoritative institution IDs: {rows_without_ids}")
    print(f"Rows eligible for exact name-country cache matches: {exact_matches}")
    print(f"Unique uncached authoritative requests that would be attempted: {len(selected)}")
    for provider, identifier in selected:
        print(f"  {provider}: {identifier}")
    if limit is not None and len(tasks) > limit:
        print(f"{len(tasks) - limit} additional requests excluded by --limit.")
    return 0


def populate_cache(
    rows: Sequence[Dict[str, str]],
    cache: Dict[str, Any],
    limit: Optional[int],
    sleep_seconds: float,
    user_agent: str,
    openalex_api_key: str,
) -> Tuple[int, bool]:
    requests_made = 0
    stopped = False
    while True:
        tasks = planned_identifier_tasks(rows, cache)
        if not tasks or (limit is not None and requests_made >= limit):
            break
        made_progress = False
        for provider, identifier in tasks:
            if limit is not None and requests_made >= limit:
                break
            if requests_made:
                time.sleep(sleep_seconds)
            requests_made += 1
            try:
                entry = request_identifier(
                    provider, identifier, user_agent, openalex_api_key
                )
            except ResolutionServiceError as error:
                print(f"Error: {error}", file=sys.stderr)
                stopped = True
                break
            cache["records"][cache_key(provider, identifier)] = entry
            status = entry.get("status", "unknown")
            print(f"Cached {provider} {identifier}: {status}")
            made_progress = True
        if stopped or not made_progress:
            break
    return requests_made, stopped


def print_summary(
    rows: Sequence[Dict[str, str]],
    report: Sequence[Dict[str, str]],
    requests_made: int,
    input_count: Optional[int] = None,
) -> None:
    confidence_counts = defaultdict(int)
    review_count = 0
    for row in rows:
        confidence_counts[row["resolution_confidence"]] += 1
        review_count += row["needs_review"] == "true"
    print("Institution resolution summary:")
    print(f"  Input affiliation rows: {input_count if input_count is not None else len(rows)}")
    print(f"  Downstream rows processed: {len(rows)}")
    print(f"  Affiliation rows: {len(rows)}")
    print(f"  API requests made: {requests_made}")
    print(f"  High confidence rows: {confidence_counts['high']}")
    print(f"  Medium confidence rows: {confidence_counts['medium']}")
    print(f"  Low confidence rows: {confidence_counts['low']}")
    print(f"  Rows needing review: {review_count}")
    print(f"  Deduplicated report rows: {len(report)}")


def run(args: argparse.Namespace) -> int:
    if any(
        path_is_in_manual_data(path)
        for path in (args.output, args.report, args.cache)
    ):
        print("Error: output, report, and cache must not be inside data/manual/.", file=sys.stderr)
        return 1
    try:
        fieldnames, source_rows = read_rows(args.input)
        cache = load_cache(args.cache)
    except ResolutionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    input_count = len(source_rows)
    source_rows = select_scope_rows(source_rows, args.include_out_of_scope)

    if args.dry_run:
        return dry_run(source_rows, cache, args.limit, input_count)

    planned_tasks = planned_identifier_tasks(source_rows, cache)
    user_agent = clean_text(args.user_agent)
    if planned_tasks and not user_agent:
        print(
            "Error: uncached authoritative lookups require a non-empty --user-agent.",
            file=sys.stderr,
        )
        return 1

    requests_made, stopped = populate_cache(
        source_rows,
        cache,
        args.limit,
        args.sleep_seconds,
        user_agent,
        os.environ.get("OPENALEX_API_KEY", ""),
    )
    resolved_rows = []
    reasons = []
    for source_row in source_rows:
        resolved, row_reasons = resolve_row(source_row, cache)
        resolved_rows.append(resolved)
        reasons.append(row_reasons)
    report = build_report(source_rows, resolved_rows, reasons)
    output_fields = [*fieldnames]
    for column in RESOLUTION_COLUMNS:
        if column not in output_fields:
            output_fields.append(column)
    cache["updated_at"] = utc_timestamp()

    try:
        write_json(args.cache, cache)
        write_csv(args.output, output_fields, resolved_rows)
        write_csv(args.report, REPORT_COLUMNS, report)
    except ResolutionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Wrote resolved candidate affiliations: {args.output}")
    print(f"Wrote institution resolution report: {args.report}")
    print(f"Updated institution resolution cache: {args.cache}")
    print_summary(resolved_rows, report, requests_made, input_count)
    print("All resolution outputs remain candidate metadata and are not curated data.")
    return 1 if stopped else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
