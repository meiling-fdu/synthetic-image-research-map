#!/usr/bin/env python3
"""Build local-only coordinate diagnostics for key papers missing map coordinates."""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


EXPORT_DIAGNOSTICS = Path("data/manual/key_paper_export_diagnostics.csv")
AFFILIATION_ENRICHMENT = Path("data/manual/key_paper_affiliation_enrichment.csv")
OPENALEX_AFFILIATIONS = Path("data/processed/openalex_candidate_affiliations.csv")
GEOCODED_AFFILIATIONS = Path(
    "data/processed/openalex_candidate_affiliations_geocoded.csv"
)
INSTITUTION_RECORD_OVERRIDES = Path("data/manual/institution_record_overrides.csv")
INSTITUTIONS = Path("data/manual/institutions.csv")
INSTITUTION_CORRECTIONS = Path("data/manual/institution_corrections.csv")
INSTITUTION_RESOLUTION_CACHE = Path("data/processed/institution_resolution_cache.json")
GEOCODING_CACHE = Path("data/processed/geocoding_cache.json")
OUTPUT = Path("data/manual/key_paper_coordinate_diagnostics.csv")

TARGET_SKIP_REASON = "missing_valid_coordinates"
SEDID_TITLE = "Exposing the Fake: Effective Diffusion-Generated Images Detection"

OUTPUT_COLUMNS = [
    "title",
    "year",
    "normalized_title",
    "openalex_url",
    "doi",
    "author",
    "author_position",
    "institution",
    "city",
    "region",
    "country",
    "country_code",
    "latitude",
    "longitude",
    "coordinate_status",
    "coordinate_source",
    "recommended_action",
    "notes",
]

EXPORT_DIAGNOSTIC_COLUMNS = {
    "title",
    "year",
    "normalized_title",
    "openalex_url",
    "doi",
    "skip_reason",
}
AFFILIATION_ENRICHMENT_COLUMNS = {
    "title",
    "year",
    "normalized_title",
    "openalex_url",
    "doi",
    "author",
    "author_position",
    "raw_affiliation",
    "institution",
    "city",
    "region",
    "country",
    "country_code",
    "latitude",
    "longitude",
    "institution_source",
    "notes",
}
OPENALEX_AFFILIATION_COLUMNS = {
    "openalex_id",
    "author_name",
    "author_position",
    "author_order",
    "institution_name",
    "city",
    "country",
    "country_code",
    "latitude",
    "longitude",
    "raw_affiliation_text",
    "notes",
}

ALLOWED_COORDINATE_STATUSES = {
    "has_valid_coordinates",
    "missing_coordinates_but_has_city_country",
    "missing_city_country",
    "missing_affiliation_records",
    "ambiguous_institution_location",
    "needs_manual_coordinate_review",
}
ALLOWED_ACTIONS = {
    "no_action",
    "lookup_existing_local_coordinates",
    "manual_coordinate_review",
    "fill_city_country_first",
    "add_affiliation_evidence_first",
    "defer_until_institution_pipeline",
}


class CoordinateDiagnosisError(RuntimeError):
    """An expected local input, validation, or output error."""


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: Any) -> str:
    title = clean_text(value).casefold()
    title = title.replace("‐", "-").replace("–", "-").replace("—", "-")
    title = title.replace("real-world", "real world")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", title).split())


def normalize_identifier_url(value: Any) -> str:
    return clean_text(value).casefold().rstrip("/")


def normalize_doi(value: Any) -> str:
    doi = clean_text(value)
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    return doi.casefold()


def normalize_institution_name(value: Any) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", clean_text(value).casefold()).split())


def parse_year(value: Any) -> str:
    text = clean_text(value)
    return text if re.fullmatch(r"\d{1,4}", text) else ""


def parse_coordinate(value: Any, minimum: float, maximum: float) -> Optional[float]:
    text = clean_text(value)
    if not text:
        return None
    try:
        coordinate = float(text)
    except ValueError:
        return None
    if math.isfinite(coordinate) and minimum <= coordinate <= maximum:
        return coordinate
    return None


def valid_coordinate_pair(row: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    pairs = (
        (row.get("resolved_latitude"), row.get("resolved_longitude")),
        (row.get("latitude"), row.get("longitude")),
        (row.get("corrected_latitude"), row.get("corrected_longitude")),
    )
    for raw_latitude, raw_longitude in pairs:
        latitude = parse_coordinate(raw_latitude, -90.0, 90.0)
        longitude = parse_coordinate(raw_longitude, -180.0, 180.0)
        if latitude is not None and longitude is not None:
            return latitude, longitude
    return None


def read_csv(
    path: Path,
    required_columns: Iterable[str],
    optional: bool = False,
) -> List[Dict[str, str]]:
    if not path.exists():
        if optional:
            return []
        raise CoordinateDiagnosisError(f"Required local input does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(set(required_columns) - set(reader.fieldnames or []))
            if missing:
                raise CoordinateDiagnosisError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise CoordinateDiagnosisError(f"Could not read {path}: {error}") from error


def read_json(path: Path, optional: bool = True) -> Dict[str, Any]:
    if not path.exists():
        if optional:
            return {}
        raise CoordinateDiagnosisError(f"Required local input does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise CoordinateDiagnosisError(f"Could not read {path}: {error}") from error
    return payload if isinstance(payload, dict) else {}


def paper_identity_keys(row: Dict[str, Any]) -> List[Tuple[str, Any]]:
    keys: List[Tuple[str, Any]] = []
    openalex = normalize_identifier_url(row.get("openalex_url") or row.get("openalex_id"))
    if openalex:
        keys.append(("openalex", openalex))
    doi = normalize_doi(row.get("doi"))
    if doi:
        keys.append(("doi", doi))
    title = normalize_title(row.get("title") or row.get("normalized_title"))
    year = parse_year(row.get("year") or row.get("publication_year"))
    if title and year:
        keys.append(("title_year", (title, year)))
    if title:
        keys.append(("title", title))
    return keys


def index_rows_by_paper_identity(
    rows: Sequence[Dict[str, str]],
) -> Dict[Tuple[str, Any], List[Dict[str, str]]]:
    index: Dict[Tuple[str, Any], List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        for key in paper_identity_keys(row):
            index[key].append(row)
    return index


def matching_rows(
    target: Dict[str, Any],
    index: Dict[Tuple[str, Any], List[Dict[str, str]]],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    seen = set()
    for key in paper_identity_keys(target):
        for row in index.get(key, []):
            identity = tuple((column, row.get(column, "")) for column in sorted(row))
            if identity in seen:
                continue
            seen.add(identity)
            rows.append(row)
    return rows


def title_sort_key(row: Dict[str, Any]) -> Tuple[str, int, str]:
    author_position = clean_text(row.get("author_position") or row.get("author_order"))
    try:
        position = int(author_position)
    except ValueError:
        position = 999999
    return clean_text(row.get("title")).casefold(), position, clean_text(row.get("author"))


def coordinate_source_entry(
    latitude: float,
    longitude: float,
    source: str,
    city: Any = "",
    country: Any = "",
) -> Dict[str, str]:
    return {
        "latitude": f"{latitude:.8g}",
        "longitude": f"{longitude:.8g}",
        "source": clean_text(source),
        "city": clean_text(city),
        "country": clean_text(country),
    }


def add_coordinate_match(
    index: Dict[str, List[Dict[str, str]]],
    institution: Any,
    entry: Dict[str, str],
) -> None:
    key = normalize_institution_name(institution)
    if key:
        index[key].append(entry)


def build_local_coordinate_index() -> Dict[str, List[Dict[str, str]]]:
    index: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    for row in read_csv(
        INSTITUTION_RECORD_OVERRIDES,
        {"institution", "city", "country", "latitude", "longitude"},
        optional=True,
    ):
        pair = valid_coordinate_pair(row)
        if pair is None:
            continue
        add_coordinate_match(
            index,
            row.get("institution"),
            coordinate_source_entry(
                pair[0],
                pair[1],
                "data/manual/institution_record_overrides.csv",
                row.get("city"),
                row.get("country"),
            ),
        )

    for row in read_csv(
        INSTITUTIONS,
        {"name", "city", "country", "latitude", "longitude"},
        optional=True,
    ):
        pair = valid_coordinate_pair(row)
        if pair is None:
            continue
        add_coordinate_match(
            index,
            row.get("name"),
            coordinate_source_entry(
                pair[0],
                pair[1],
                "data/manual/institutions.csv",
                row.get("city"),
                row.get("country"),
            ),
        )

    for row in read_csv(
        INSTITUTION_CORRECTIONS,
        {
            "corrected_institution_name",
            "corrected_country",
            "corrected_latitude",
            "corrected_longitude",
        },
        optional=True,
    ):
        pair = valid_coordinate_pair(row)
        if pair is None:
            continue
        add_coordinate_match(
            index,
            row.get("corrected_institution_name"),
            coordinate_source_entry(
                pair[0],
                pair[1],
                "data/manual/institution_corrections.csv",
                "",
                row.get("corrected_country"),
            ),
        )

    for row in read_csv(
        GEOCODED_AFFILIATIONS,
        {
            "institution_name",
            "resolved_institution_name",
            "resolved_city",
            "resolved_country",
            "resolved_latitude",
            "resolved_longitude",
            "latitude",
            "longitude",
        },
        optional=True,
    ):
        pair = valid_coordinate_pair(row)
        if pair is None:
            continue
        city = clean_text(row.get("resolved_city")) or clean_text(row.get("city"))
        country = clean_text(row.get("resolved_country")) or clean_text(row.get("country"))
        source = "data/processed/openalex_candidate_affiliations_geocoded.csv"
        entry = coordinate_source_entry(pair[0], pair[1], source, city, country)
        add_coordinate_match(index, row.get("resolved_institution_name"), entry)
        add_coordinate_match(index, row.get("institution_name"), entry)

    resolution_cache = read_json(INSTITUTION_RESOLUTION_CACHE)
    records = resolution_cache.get("records", {})
    if isinstance(records, dict):
        for record in records.values():
            if not isinstance(record, dict) or record.get("status") != "resolved":
                continue
            pair = valid_coordinate_pair(record)
            if pair is None:
                continue
            source = "data/processed/institution_resolution_cache.json"
            entry = coordinate_source_entry(
                pair[0],
                pair[1],
                f"{source}:{clean_text(record.get('provider')) or 'local cache'}",
                record.get("resolved_city"),
                record.get("resolved_country"),
            )
            add_coordinate_match(index, record.get("resolved_institution_name"), entry)
            for name in record.get("match_names", []):
                add_coordinate_match(index, name, entry)

    geocoding_cache = read_json(GEOCODING_CACHE)
    results = geocoding_cache.get("results", {})
    if isinstance(results, dict):
        provider = clean_text(geocoding_cache.get("provider")) or "local geocoding cache"
        for result in results.values():
            if not isinstance(result, dict) or result.get("status") != "resolved":
                continue
            pair = valid_coordinate_pair(result)
            if pair is None:
                continue
            query = clean_text(result.get("query"))
            institution = query.split(",", 1)[0].strip()
            add_coordinate_match(
                index,
                institution,
                coordinate_source_entry(
                    pair[0],
                    pair[1],
                    f"data/processed/geocoding_cache.json:{provider}",
                    "",
                    "",
                ),
            )

    deduped: Dict[str, List[Dict[str, str]]] = {}
    for key, entries in index.items():
        seen = set()
        unique = []
        for entry in entries:
            identity = (
                entry["latitude"],
                entry["longitude"],
                entry["source"],
                entry["city"],
                entry["country"],
            )
            if identity in seen:
                continue
            seen.add(identity)
            unique.append(entry)
        deduped[key] = unique
    return deduped


def best_local_coordinate_match(
    institution: str,
    city: str,
    country: str,
    coordinate_index: Dict[str, List[Dict[str, str]]],
) -> Tuple[Optional[Dict[str, str]], bool]:
    matches = coordinate_index.get(normalize_institution_name(institution), [])
    if not matches:
        return None, False
    if len(matches) == 1:
        return matches[0], False
    city_key = city.casefold()
    country_key = country.casefold()
    location_matches = [
        match
        for match in matches
        if (
            not city_key
            or clean_text(match.get("city")).casefold() == city_key
        )
        and (
            not country_key
            or clean_text(match.get("country")).casefold() in {country_key, country_key[:2]}
        )
    ]
    if len(location_matches) == 1:
        return location_matches[0], False
    return None, True


def enrichment_output_row(
    target: Dict[str, str],
    row: Dict[str, str],
    coordinate_index: Dict[str, List[Dict[str, str]]],
) -> Dict[str, str]:
    institution = clean_text(row.get("institution"))
    city = clean_text(row.get("city"))
    country = clean_text(row.get("country"))
    latitude = clean_text(row.get("latitude"))
    longitude = clean_text(row.get("longitude"))
    source = ""
    notes = [clean_text(row.get("notes"))]
    pair = valid_coordinate_pair(row)
    ambiguous = False
    local_match = None
    if pair is None and institution:
        local_match, ambiguous = best_local_coordinate_match(
            institution,
            city,
            country or clean_text(row.get("country_code")),
            coordinate_index,
        )
    if pair is not None:
        status = "has_valid_coordinates"
        action = "no_action"
        source = clean_text(row.get("institution_source"))
    elif local_match is not None:
        status = "has_valid_coordinates"
        action = "manual_coordinate_review"
        latitude = local_match["latitude"]
        longitude = local_match["longitude"]
        source = local_match["source"]
        notes.append("Possible exact local institution coordinate match; verify before copying into enrichment CSV.")
    elif ambiguous:
        status = "ambiguous_institution_location"
        action = "manual_coordinate_review"
        notes.append("Multiple exact local coordinate matches exist for this institution name.")
    elif institution and city and country:
        status = "missing_coordinates_but_has_city_country"
        action = "lookup_existing_local_coordinates"
    elif institution:
        status = "missing_city_country"
        action = "fill_city_country_first"
    else:
        status = "missing_affiliation_records"
        action = "add_affiliation_evidence_first"
    return {
        "title": clean_text(target.get("title") or row.get("title")),
        "year": clean_text(target.get("year") or row.get("year")),
        "normalized_title": clean_text(
            target.get("normalized_title") or row.get("normalized_title")
        ),
        "openalex_url": clean_text(target.get("openalex_url") or row.get("openalex_url")),
        "doi": clean_text(target.get("doi") or row.get("doi")),
        "author": clean_text(row.get("author")),
        "author_position": clean_text(row.get("author_position")),
        "institution": institution,
        "city": city,
        "region": clean_text(row.get("region")),
        "country": country,
        "country_code": clean_text(row.get("country_code")),
        "latitude": latitude,
        "longitude": longitude,
        "coordinate_status": status,
        "coordinate_source": source,
        "recommended_action": action,
        "notes": " | ".join(part for part in notes if part),
    }


def openalex_output_row(
    target: Dict[str, str],
    row: Dict[str, str],
    coordinate_index: Dict[str, List[Dict[str, str]]],
) -> Dict[str, str]:
    institution = clean_text(row.get("resolved_institution_name") or row.get("institution_name"))
    city = clean_text(row.get("resolved_city") or row.get("city"))
    country = clean_text(row.get("resolved_country") or row.get("country"))
    latitude = clean_text(row.get("resolved_latitude") or row.get("latitude"))
    longitude = clean_text(row.get("resolved_longitude") or row.get("longitude"))
    source = ""
    notes = [clean_text(row.get("resolution_notes")), clean_text(row.get("notes"))]
    pair = valid_coordinate_pair(row)
    ambiguous = False
    local_match = None
    if pair is None and institution:
        local_match, ambiguous = best_local_coordinate_match(
            institution,
            city,
            country or clean_text(row.get("country_code")),
            coordinate_index,
        )
    if pair is not None:
        status = "has_valid_coordinates"
        action = "no_action"
        source = clean_text(row.get("resolution_method"))
    elif local_match is not None:
        status = "has_valid_coordinates"
        action = "manual_coordinate_review"
        latitude = local_match["latitude"]
        longitude = local_match["longitude"]
        source = local_match["source"]
        notes.append("Possible exact local institution coordinate match; verify before copying into enrichment CSV.")
    elif ambiguous:
        status = "ambiguous_institution_location"
        action = "manual_coordinate_review"
        notes.append("Multiple exact local coordinate matches exist for this institution name.")
    elif institution and city and country:
        status = "missing_coordinates_but_has_city_country"
        action = "lookup_existing_local_coordinates"
    elif institution:
        status = "missing_city_country"
        action = "fill_city_country_first"
    else:
        status = "missing_affiliation_records"
        action = "add_affiliation_evidence_first"
    return {
        "title": clean_text(target.get("title")),
        "year": clean_text(target.get("year")),
        "normalized_title": clean_text(target.get("normalized_title")),
        "openalex_url": clean_text(target.get("openalex_url")),
        "doi": clean_text(target.get("doi")),
        "author": clean_text(row.get("author_name")),
        "author_position": clean_text(row.get("author_order") or row.get("author_position")),
        "institution": institution,
        "city": city,
        "region": "",
        "country": country,
        "country_code": clean_text(row.get("country_code")),
        "latitude": latitude,
        "longitude": longitude,
        "coordinate_status": status,
        "coordinate_source": source,
        "recommended_action": action,
        "notes": " | ".join(part for part in notes if part),
    }


def placeholder_output_row(target: Dict[str, str]) -> Dict[str, str]:
    return {
        "title": clean_text(target.get("title")),
        "year": clean_text(target.get("year")),
        "normalized_title": clean_text(target.get("normalized_title")),
        "openalex_url": clean_text(target.get("openalex_url")),
        "doi": clean_text(target.get("doi")),
        "author": "",
        "author_position": "",
        "institution": "",
        "city": "",
        "region": "",
        "country": "",
        "country_code": "",
        "latitude": "",
        "longitude": "",
        "coordinate_status": "missing_affiliation_records",
        "coordinate_source": "",
        "recommended_action": "add_affiliation_evidence_first",
        "notes": "No affiliation row found in key-paper enrichment or local OpenAlex affiliation tables.",
    }


def build_diagnostics() -> Tuple[List[Dict[str, str]], int]:
    export_rows = read_csv(EXPORT_DIAGNOSTICS, EXPORT_DIAGNOSTIC_COLUMNS)
    targets = [
        row for row in export_rows if clean_text(row.get("skip_reason")) == TARGET_SKIP_REASON
    ]
    enrichment_rows = read_csv(AFFILIATION_ENRICHMENT, AFFILIATION_ENRICHMENT_COLUMNS)
    openalex_rows = read_csv(OPENALEX_AFFILIATIONS, OPENALEX_AFFILIATION_COLUMNS)
    geocoded_rows = read_csv(GEOCODED_AFFILIATIONS, OPENALEX_AFFILIATION_COLUMNS, optional=True)
    coordinate_index = build_local_coordinate_index()

    enrichment_index = index_rows_by_paper_identity(enrichment_rows)
    openalex_index = index_rows_by_paper_identity([*geocoded_rows, *openalex_rows])

    output_rows: List[Dict[str, str]] = []
    for target in targets:
        enriched = matching_rows(target, enrichment_index)
        if enriched:
            output_rows.extend(
                enrichment_output_row(target, row, coordinate_index)
                for row in enriched
            )
            continue
        openalex_affiliations = [
            row
            for row in matching_rows(target, openalex_index)
            if clean_text(row.get("institution_name"))
            or clean_text(row.get("raw_affiliation_text"))
        ]
        if openalex_affiliations:
            output_rows.extend(
                openalex_output_row(target, row, coordinate_index)
                for row in openalex_affiliations
            )
        else:
            output_rows.append(placeholder_output_row(target))

    output_rows.sort(key=title_sort_key)
    validate(output_rows, targets)
    local_matches = sum(
        bool(clean_text(row.get("latitude")) and clean_text(row.get("coordinate_source")))
        and "data/" in row.get("coordinate_source", "")
        for row in output_rows
    )
    return output_rows, local_matches


def validate(rows: Sequence[Dict[str, str]], targets: Sequence[Dict[str, str]]) -> None:
    target_titles = {clean_text(row.get("normalized_title")) for row in targets}
    output_titles = {clean_text(row.get("normalized_title")) for row in rows}
    missing = sorted(target_titles - output_titles)
    if missing:
        raise CoordinateDiagnosisError(
            f"Coordinate diagnostics missing target papers: {missing}"
        )
    if normalize_title(SEDID_TITLE) not in output_titles:
        raise CoordinateDiagnosisError("SeDID is missing from coordinate diagnostics")
    invalid_statuses = sorted(
        {row["coordinate_status"] for row in rows} - ALLOWED_COORDINATE_STATUSES
    )
    invalid_actions = sorted(
        {row["recommended_action"] for row in rows} - ALLOWED_ACTIONS
    )
    if invalid_statuses or invalid_actions:
        raise CoordinateDiagnosisError(
            f"Unsupported statuses/actions: {invalid_statuses=} {invalid_actions=}"
        )
    for row in rows:
        has_lat = bool(clean_text(row.get("latitude")))
        has_lon = bool(clean_text(row.get("longitude")))
        if has_lat != has_lon:
            raise CoordinateDiagnosisError(
                f"Partial coordinate pair for {row['title']} / {row['institution']}"
            )
        if has_lat and valid_coordinate_pair(row) is None:
            raise CoordinateDiagnosisError(
                f"Invalid coordinate pair for {row['title']} / {row['institution']}"
            )


def write_csv(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=OUTPUT_COLUMNS,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise CoordinateDiagnosisError(f"Could not write {path}: {error}") from error


def main() -> int:
    try:
        rows, local_matches = build_diagnostics()
        write_csv(OUTPUT, rows)
    except CoordinateDiagnosisError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    paper_count = len({row["normalized_title"] for row in rows})
    print(f"Wrote: {OUTPUT}")
    print(f"Missing-coordinate papers found: {paper_count}")
    print(f"Coordinate diagnostic rows: {len(rows)}")
    print("By coordinate_status:")
    for key, count in Counter(row["coordinate_status"] for row in rows).most_common():
        print(f"  {key}: {count}")
    print("By recommended_action:")
    for key, count in Counter(row["recommended_action"] for row in rows).most_common():
        print(f"  {key}: {count}")
    print(
        "SeDID included: "
        f"{any(normalize_title(row['title']) == normalize_title(SEDID_TITLE) for row in rows)}"
    )
    print(f"Existing local coordinate matches found: {local_matches}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
