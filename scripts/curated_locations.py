#!/usr/bin/env python3
"""Local confirmed institution-location curation operations."""

from __future__ import annotations

import csv
import hashlib
import math
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

try:
    from .curated_schema import (
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        ALLOWED_INSTITUTION_REVIEW_STATUSES,
    )
except ImportError:
    from curated_schema import (
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        ALLOWED_INSTITUTION_REVIEW_STATUSES,
    )


DEFAULT_LOCATION_REVIEW_PATH = CURATED_DATA_DIR / "institution_location_review.csv"
DEFAULT_INSTITUTION_LOCATIONS_PATH = CURATED_DATA_DIR / "institution_locations.csv"
DEFAULT_INSTITUTION_ALIASES_PATH = CURATED_DATA_DIR / "institution_aliases.csv"
COUNTRY_CODE_PATTERN = re.compile(r"[A-Z]{2}")


class CuratedLocationError(RuntimeError):
    """An expected location validation or storage error."""


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_institution_name(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _read_csv(path: Path, columns: Sequence[str]) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != tuple(columns):
                raise CuratedLocationError(
                    f"{path} does not have the exact curated CSV header"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise CuratedLocationError(f"could not read {path}: {error}") from error
    except (UnicodeError, csv.Error) as error:
        raise CuratedLocationError(f"invalid CSV in {path}: {error}") from error


def _write_csv_atomic(
    rows: Sequence[Mapping[str, Any]],
    path: Path,
    columns: Sequence[str],
) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=columns,
                lineterminator="\n",
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise CuratedLocationError(f"could not write {path}: {error}") from error


def load_location_review_queue(
    path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, INSTITUTION_LOCATION_REVIEW_COLUMNS)


def load_confirmed_locations(
    path: Path = DEFAULT_INSTITUTION_LOCATIONS_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, INSTITUTION_LOCATION_COLUMNS)


def load_institution_aliases(
    path: Path = DEFAULT_INSTITUTION_ALIASES_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, INSTITUTION_ALIAS_COLUMNS)


def save_institution_aliases(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_INSTITUTION_ALIASES_PATH,
) -> None:
    _write_csv_atomic(rows, path, INSTITUTION_ALIAS_COLUMNS)


def save_confirmed_locations(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_INSTITUTION_LOCATIONS_PATH,
) -> None:
    _write_csv_atomic(rows, path, INSTITUTION_LOCATION_COLUMNS)


def save_location_review_queue(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> None:
    _write_csv_atomic(rows, path, INSTITUTION_LOCATION_REVIEW_COLUMNS)


def validate_coordinates(latitude: Any, longitude: Any) -> tuple[str, str]:
    latitude_text = clean(latitude)
    longitude_text = clean(longitude)
    try:
        latitude_value = float(latitude_text)
        longitude_value = float(longitude_text)
    except ValueError as error:
        raise CuratedLocationError("latitude and longitude must be numbers") from error
    if not math.isfinite(latitude_value) or not -90 <= latitude_value <= 90:
        raise CuratedLocationError("latitude must be between -90 and 90")
    if not math.isfinite(longitude_value) or not -180 <= longitude_value <= 180:
        raise CuratedLocationError("longitude must be between -180 and 180")
    return format(latitude_value, ".10g"), format(longitude_value, ".10g")


def validate_country_code(value: Any) -> str:
    country_code = clean(value)
    if not COUNTRY_CODE_PATTERN.fullmatch(country_code):
        raise CuratedLocationError(
            "country_code must be two uppercase ISO alpha-2 style letters"
        )
    return country_code


def location_id_for(institution: Any) -> str:
    normalized = normalize_institution_name(institution)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:20]
    return f"location:{digest}"


def queue_row_id(row: Mapping[str, Any]) -> str:
    identity = "|".join(
        (
            normalize_institution_name(row.get("institution")),
            clean(row.get("related_paper_id")).casefold(),
            clean(row.get("doi")).casefold(),
            clean(row.get("openalex_url")).casefold().rstrip("/"),
            clean(row.get("title")).casefold(),
            clean(row.get("year")),
        )
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
    return f"location-review:{digest}"


def _find_queue_row(
    rows: Sequence[Mapping[str, Any]], requested_id: Any
) -> int:
    identifier = clean(requested_id)
    if not identifier:
        raise CuratedLocationError("queue_id is required")
    for index, row in enumerate(rows):
        if queue_row_id(row) == identifier:
            return index
    raise CuratedLocationError("location review row was not found")


def _append_note(existing: Any, note: Any) -> str:
    old = clean(existing)
    new = clean(note)
    if not old:
        return new
    if not new or new in old.split(" | "):
        return old
    return f"{old} | {new}"


def _confirmed_location_fields(
    draft: Mapping[str, Any],
    *,
    created_by: str,
    normalized_institution: str,
) -> Dict[str, str]:
    institution = clean(
        draft.get("confirmed_institution") or draft.get("institution")
    )
    if not institution:
        raise CuratedLocationError("confirmed_institution is required")
    normalized = normalize_institution_name(normalized_institution)
    if not normalized:
        raise CuratedLocationError("confirmed_institution is invalid")
    country_code = validate_country_code(
        draft.get("confirmed_country_code") or draft.get("country_code")
    )
    latitude, longitude = validate_coordinates(
        draft.get("confirmed_lat") if "confirmed_lat" in draft else draft.get("lat"),
        draft.get("confirmed_lon") if "confirmed_lon" in draft else draft.get("lon"),
    )
    coordinate_source = clean(draft.get("coordinate_source"))
    coordinate_source_url = clean(draft.get("coordinate_source_url"))
    review_note = clean(
        draft.get("coordinate_review_note") or draft.get("review_note")
    )
    if not coordinate_source and not coordinate_source_url:
        raise CuratedLocationError(
            "coordinate_source or coordinate_source_url is required"
        )
    if not review_note:
        raise CuratedLocationError("coordinate_review_note is required")
    city = clean(draft.get("confirmed_city") or draft.get("city"))
    country = clean(draft.get("confirmed_country") or draft.get("country"))
    if not city or not country:
        raise CuratedLocationError(
            "confirmed city and country are required"
        )
    return {
        "location_id": location_id_for(normalized),
        "institution": institution,
        "normalized_institution": normalized,
        "city": city,
        "region": clean(draft.get("confirmed_region") or draft.get("region")),
        "country": country,
        "country_code": country_code,
        "lat": latitude,
        "lon": longitude,
        "coordinate_source": coordinate_source,
        "coordinate_source_url": coordinate_source_url,
        "coordinate_status": "known",
        "review_note": review_note,
        "created_by": clean(created_by) or "local-admin",
    }


def create_or_update_confirmed_location(
    queue_id: Any,
    draft: Mapping[str, Any],
    *,
    locations_path: Path = DEFAULT_INSTITUTION_LOCATIONS_PATH,
    review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
    created_by: str = "local-admin",
) -> Dict[str, Any]:
    review_rows = load_location_review_queue(review_path)
    review_index = _find_queue_row(review_rows, queue_id)
    queue_row = review_rows[review_index]
    queue_normalized = normalize_institution_name(
        draft.get("confirmed_institution") or queue_row.get("institution")
    )
    values = _confirmed_location_fields(
        draft,
        created_by=created_by,
        normalized_institution=queue_normalized,
    )

    locations = load_confirmed_locations(locations_path)
    matches = [
        index
        for index, row in enumerate(locations)
        if normalize_institution_name(
            row.get("normalized_institution") or row.get("institution")
        )
        == values["normalized_institution"]
    ]
    if len(matches) > 1:
        raise CuratedLocationError(
            "multiple confirmed locations already exist for this institution"
        )
    now = _timestamp()
    action = "updated" if matches else "created"
    if matches:
        existing = locations[matches[0]]
        values["location_id"] = clean(existing.get("location_id")) or values[
            "location_id"
        ]
        values["created_at"] = clean(existing.get("created_at")) or now
        values["created_by"] = clean(existing.get("created_by")) or values[
            "created_by"
        ]
        values["updated_at"] = now
        locations[matches[0]] = values
    else:
        values["created_at"] = now
        values["updated_at"] = now
        locations.append(values)

    queue_row["canonical_institution_name"] = values["institution"]
    queue_row["review_status"] = "confirmed"
    queue_row["location_status"] = "known"
    queue_row["coordinate_status"] = "known"
    queue_row["review_note"] = _append_note(
        queue_row.get("review_note"), values["review_note"]
    )
    queue_row["updated_at"] = now
    save_confirmed_locations(locations, locations_path)
    try:
        save_location_review_queue(review_rows, review_path)
    except CuratedLocationError:
        # Restore the confirmed-location file if the paired queue update fails.
        if matches:
            locations[matches[0]] = existing
        else:
            locations.pop()
        save_confirmed_locations(locations, locations_path)
        raise
    return {
        "action": action,
        "location": values,
        "queue_row": {**queue_row, "queue_id": queue_row_id(queue_row)},
    }


def mark_queue_row(
    queue_id: Any,
    status: str,
    note: Any,
    *,
    review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> Dict[str, Any]:
    review_note = clean(note)
    if not review_note:
        raise CuratedLocationError("review_note is required")
    status_values = {
        "pending_review": ("missing", "missing"),
        "needs_coordinates": ("needs_coordinate_review", "missing"),
        "ambiguous": ("ambiguous", "needs_coordinate_review"),
        "alias_candidate": ("ambiguous", "missing"),
        "ignore": ("missing", "missing"),
        "excluded": ("missing", "missing"),
    }
    if status not in status_values:
        raise CuratedLocationError("unsupported institution review status")
    rows = load_location_review_queue(review_path)
    index = _find_queue_row(rows, queue_id)
    row = rows[index]
    row["review_status"] = status
    row["location_status"], row["coordinate_status"] = status_values[status]
    row["review_note"] = _append_note(row.get("review_note"), review_note)
    row["updated_at"] = _timestamp()
    save_location_review_queue(rows, review_path)
    return {**row, "queue_id": queue_row_id(row)}


def save_queue_metadata(
    queue_id: Any,
    draft: Mapping[str, Any],
    *,
    review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> Dict[str, Any]:
    rows = load_location_review_queue(review_path)
    index = _find_queue_row(rows, queue_id)
    row = rows[index]
    editable = (
        "canonical_institution_name",
        "detected_language",
        "suggested_city",
        "suggested_country",
        "matched_institution",
        "suggested_canonical_institution",
        "match_method",
        "similarity_score",
        "confidence",
        "openalex_institution_id",
        "ror_id",
        "wikidata_id",
        "review_note",
    )
    for field in editable:
        if field in draft:
            row[field] = clean(draft.get(field))
    requested_status = clean(draft.get("review_status"))
    if requested_status:
        if requested_status not in ALLOWED_INSTITUTION_REVIEW_STATUSES:
            raise CuratedLocationError("unsupported institution review status")
        if (
            requested_status in {"confirmed", "alias_of_confirmed"}
            and requested_status != clean(row.get("review_status"))
        ):
            raise CuratedLocationError(
                "use Confirm location or Confirm as alias for this status"
            )
        row["review_status"] = requested_status
    row["updated_at"] = _timestamp()
    save_location_review_queue(rows, review_path)
    return {**row, "queue_id": queue_row_id(row)}


def confirm_alias(
    queue_id: Any,
    canonical_institution_name: Any,
    *,
    alias_language: Any = "",
    alias_source: Any = "",
    note: Any = "",
    review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
    locations_path: Path = DEFAULT_INSTITUTION_LOCATIONS_PATH,
    aliases_path: Path = DEFAULT_INSTITUTION_ALIASES_PATH,
) -> Dict[str, Any]:
    canonical = clean(canonical_institution_name)
    if not canonical:
        raise CuratedLocationError("a canonical institution is required")
    confirmed = load_confirmed_locations(locations_path)
    target = next(
        (
            row for row in confirmed
            if normalize_institution_name(row.get("institution")) ==
            normalize_institution_name(canonical)
        ),
        None,
    )
    if target is None:
        raise CuratedLocationError(
            "alias target must be an existing confirmed institution"
        )
    rows = load_location_review_queue(review_path)
    index = _find_queue_row(rows, queue_id)
    queue_row = rows[index]
    alias_name = clean(queue_row.get("institution"))
    aliases = load_institution_aliases(aliases_path)
    original_aliases = [dict(row) for row in aliases]
    normalized_alias = normalize_institution_name(alias_name)
    conflicts = {
        normalize_institution_name(row.get("canonical_institution_name"))
        for row in aliases
        if normalize_institution_name(row.get("alias_name")) == normalized_alias
        and clean(row.get("review_status")) == "confirmed"
    }
    if conflicts and normalize_institution_name(canonical) not in conflicts:
        queue_row["review_status"] = "ambiguous"
        queue_row["updated_at"] = _timestamp()
        save_location_review_queue(rows, review_path)
        raise CuratedLocationError(
            "this alias already maps to a different canonical institution"
        )
    alias_row = {
        "alias_name": alias_name,
        "canonical_institution_name": clean(target.get("institution")),
        "alias_language": clean(alias_language),
        "alias_source": clean(alias_source) or "local-admin",
        "review_status": "confirmed",
        "notes": clean(note),
    }
    existing = next(
        (
            row for row in aliases
            if normalize_institution_name(row.get("alias_name")) == normalized_alias
            and normalize_institution_name(row.get("canonical_institution_name"))
            == normalize_institution_name(canonical)
        ),
        None,
    )
    if existing:
        existing.update(alias_row)
    else:
        aliases.append(alias_row)
    queue_row["canonical_institution_name"] = clean(target.get("institution"))
    queue_row["matched_institution"] = clean(target.get("institution"))
    queue_row["review_status"] = "alias_of_confirmed"
    queue_row["review_note"] = _append_note(queue_row.get("review_note"), note)
    queue_row["updated_at"] = _timestamp()
    save_institution_aliases(aliases, aliases_path)
    try:
        save_location_review_queue(rows, review_path)
    except CuratedLocationError:
        save_institution_aliases(original_aliases, aliases_path)
        raise
    return {
        "alias": alias_row,
        "queue_row": {**queue_row, "queue_id": queue_row_id(queue_row)},
    }


def location_review_report(
    review_rows: Iterable[Mapping[str, Any]],
    locations: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    reviews = list(review_rows)
    confirmed = list(locations)
    location_counts = Counter(
        normalize_institution_name(
            row.get("normalized_institution") or row.get("institution")
        )
        for row in confirmed
    )
    location_counts.pop("", None)
    statuses = Counter(clean(row.get("review_status")) for row in reviews)
    coordinate_statuses = Counter(
        clean(row.get("coordinate_status")) for row in reviews
    )
    candidates: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in confirmed:
        normalized = normalize_institution_name(
            row.get("normalized_institution") or row.get("institution")
        )
        if normalized:
            candidates[normalized].append(dict(row))
    return {
        "total_queue_rows": len(reviews),
        **{
            status: statuses[status]
            for status in sorted(ALLOWED_INSTITUTION_REVIEW_STATUSES)
        },
        "ambiguous": statuses["ambiguous"],
        "needs_coordinate_review": coordinate_statuses[
            "needs_coordinate_review"
        ],
        "confirmed_locations_count": len(confirmed),
        "institutions_with_multiple_location_candidates": sorted(
            institution
            for institution, count in location_counts.items()
            if count > 1
        ),
        "multiple_location_candidate_count": sum(
            count > 1 for count in location_counts.values()
        ),
    }


def location_review_payload(
    *,
    review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
    locations_path: Path = DEFAULT_INSTITUTION_LOCATIONS_PATH,
    aliases_path: Path = DEFAULT_INSTITUTION_ALIASES_PATH,
) -> Dict[str, Any]:
    reviews = load_location_review_queue(review_path)
    locations = load_confirmed_locations(locations_path)
    aliases = load_institution_aliases(aliases_path)
    aliases_by_canonical: Dict[str, List[str]] = defaultdict(list)
    confirmed_alias_targets: Dict[str, str] = {}
    for alias in aliases:
        if clean(alias.get("review_status")) != "confirmed":
            continue
        canonical = clean(alias.get("canonical_institution_name"))
        aliases_by_canonical[normalize_institution_name(canonical)].append(
            clean(alias.get("alias_name"))
        )
        confirmed_alias_targets[
            normalize_institution_name(alias.get("alias_name"))
        ] = canonical
    by_institution: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for location in locations:
        by_institution[
            normalize_institution_name(
                location.get("normalized_institution")
                or location.get("institution")
            )
        ].append(location)
    records = []
    for row in reviews:
        raw_key = normalize_institution_name(row.get("institution"))
        alias_target = confirmed_alias_targets.get(raw_key)
        canonical_key = normalize_institution_name(
            row.get("canonical_institution_name") or alias_target
            or row.get("institution")
        )
        matches = by_institution.get(canonical_key, [])
        effective_status = clean(row.get("review_status"))
        if alias_target and effective_status not in {"ignore", "excluded"}:
            effective_status = "alias_of_confirmed"
        records.append(
            {
                **row,
                "review_status": effective_status or "pending_review",
                "canonical_institution_name": clean(
                    row.get("canonical_institution_name") or alias_target
                ),
                "queue_id": queue_row_id(row),
                "confirmed_location": matches[0] if len(matches) == 1 else None,
                "confirmed_location_count": len(matches),
                "existing_aliases": aliases_by_canonical.get(canonical_key, []),
            }
        )
    return {
        "records": records,
        "confirmed_locations": locations,
        "institution_aliases": aliases,
        "summary": location_review_report(reviews, locations),
    }
