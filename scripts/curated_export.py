#!/usr/bin/env python3
"""Integrate maintainer-confirmed papers and mappings into public previews."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

try:
    from .curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        PAPERS_COLUMNS,
    )
    from .country_normalization import normalize_country_region, public_location_display
    from .publication_types import normalize_publication_type
    from .export_candidate_map_data import normalize_export_task_labels
    from .paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PAPER_EXCLUSION_COLUMNS,
        active_exclusions,
        all_identity_keys,
        clean,
        record_is_excluded,
        build_active_exclusion_index,
    )
    from .name_matching import canonical_name_key, names_match
    from .curated_papers import normalize_author_names
except ImportError:
    from curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        PAPERS_COLUMNS,
    )
    from country_normalization import normalize_country_region, public_location_display
    from publication_types import normalize_publication_type
    from export_candidate_map_data import normalize_export_task_labels
    from paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PAPER_EXCLUSION_COLUMNS,
        active_exclusions,
        all_identity_keys,
        clean,
        record_is_excluded,
        build_active_exclusion_index,
    )
    from name_matching import canonical_name_key, names_match
    from curated_papers import normalize_author_names


DEFAULT_CURATED_PAPERS_PATH = CURATED_DATA_DIR / "papers.csv"
DEFAULT_CURATED_MAPPINGS_PATH = (
    CURATED_DATA_DIR / "author_institution_mappings.csv"
)
DEFAULT_LOCATION_REVIEW_PATH = (
    CURATED_DATA_DIR / "institution_location_review.csv"
)
DEFAULT_INSTITUTION_ALIASES_PATH = CURATED_DATA_DIR / "institution_aliases.csv"
DEFAULT_INSTITUTION_RESOLUTION_CACHE_PATH = Path(
    "data/processed/institution_resolution_cache.json"
)
DEFAULT_CURATED_EXCLUSIONS_PATH = DEFAULT_EXCLUSIONS_PATH
ACTIVE_MAPPING_STATUS = "active"
AFFILIATION_REVIEW_STATES = {"unreviewed", "curated", "reviewed_empty"}
PUBLIC_PAPER_TASKS = {
    "detection",
    "source_attribution",
    "detection_and_source_attribution",
    "uncertain",
}
PUBLIC_MAP_TASKS = PUBLIC_PAPER_TASKS - {"uncertain"}
CONFIRMED_CURATION_STATUSES = {
    "manually_confirmed",
    "corrected_by_admin",
}
CURATED_OVERRIDE_FIELDS = (
    "paper_id",
    "title",
    "year",
    "publication_year",
    "authors",
    "venue",
    "venue_name",
    "doi",
    "arxiv_id",
    "arxiv_url",
    "paper_url",
    "primary_url",
    "openalex_url",
    "publication_type",
    "abstract",
    "task",
    "subtask",
    "entry_type",
    "source_database",
    "metadata_source",
    "curation_status",
    "review_status",
    "review_note",
)


class CuratedExportError(RuntimeError):
    """An expected curated export input or write error."""


@dataclass(frozen=True)
class CoordinateMatch:
    status: str
    record: Dict[str, Any] | None


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _read_csv(path: Path, columns: Sequence[str]) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != tuple(columns):
                raise CuratedExportError(
                    f"{path} does not have the exact curated CSV header"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise CuratedExportError(f"could not read {path}: {error}") from error
    except (UnicodeError, csv.Error) as error:
        raise CuratedExportError(f"invalid CSV in {path}: {error}") from error


def load_curated_papers(
    path: Path = DEFAULT_CURATED_PAPERS_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, PAPERS_COLUMNS)


def load_curated_mappings(
    path: Path = DEFAULT_CURATED_MAPPINGS_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)


def load_active_exclusions(
    path: Path = DEFAULT_CURATED_EXCLUSIONS_PATH,
) -> List[Dict[str, str]]:
    return list(active_exclusions(_read_csv(path, PAPER_EXCLUSION_COLUMNS)))


def load_location_review_queue(
    path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, INSTITUTION_LOCATION_REVIEW_COLUMNS)


def load_institution_aliases(
    path: Path = DEFAULT_INSTITUTION_ALIASES_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, INSTITUTION_ALIAS_COLUMNS)


def load_institution_resolution_cache(
    path: Path = DEFAULT_INSTITUTION_RESOLUTION_CACHE_PATH,
) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as error:
        raise CuratedExportError(f"could not read {path}: {error}") from error
    except (UnicodeError, json.JSONDecodeError) as error:
        raise CuratedExportError(f"invalid JSON in {path}: {error}") from error
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, dict):
        raise CuratedExportError(
            f"{path} does not have the expected resolution-cache format"
        )
    return [
        dict(record)
        for record in records.values()
        if isinstance(record, dict)
    ]


def save_location_review_queue(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> None:
    for row in rows:
        if not clean(row.get("institution_id")):
            raise CuratedExportError(
                "location review rows require a canonical institution_id"
            )
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=INSTITUTION_LOCATION_REVIEW_COLUMNS,
                lineterminator="\n",
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        raise CuratedExportError(f"could not write {path}: {error}") from error


def normalize_paper_identity_keys(record: Mapping[str, Any]) -> List[str]:
    keys = list(all_identity_keys(record))
    paper_id = clean(
        record.get("paper_id")
        or record.get("related_paper_id")
        or record.get("display_id")
    ).casefold()
    if paper_id:
        keys.append(f"paper_id:{paper_id}")
    merged_versions = record.get("merged_versions")
    if isinstance(merged_versions, list):
        for version in merged_versions:
            if isinstance(version, Mapping):
                keys.extend(all_identity_keys(version))
    return list(dict.fromkeys(keys))


def normalize_institution(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalize_regional_location(
    record: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return a copy with canonical public country/region fields."""
    normalized = dict(record)
    normalized.update(
        normalize_country_region(
            record.get("country"),
            record.get("country_code"),
            record.get("region"),
            record.get("region_code"),
            (
                record.get("raw_country")
                if "raw_country" in record
                else None
            ),
            (
                record.get("raw_country_code")
                if "raw_country_code" in record
                else None
            ),
        )
    )
    normalized["location_display"] = public_location_display(
        normalized.get("region"),
        normalized.get("country"),
        normalized.get("country_code"),
    )
    return normalized


def normalize_task_subtask(
    record: Mapping[str, Any],
) -> Tuple[str, str] | None:
    labels = normalize_export_task_labels(dict(record))
    if labels is None:
        return None
    task, subtask = labels
    if task not in PUBLIC_PAPER_TASKS:
        return None
    return task, subtask


def _parse_year(value: Any) -> int | None:
    try:
        year = int(clean(value))
    except ValueError:
        return None
    return year if 0 < year < 10000 else None


def _parse_people(value: Any) -> List[str]:
    if isinstance(value, list):
        return [
            clean(item.get("name") or item.get("author"))
            if isinstance(item, dict)
            else clean(item)
            for item in value
            if (
                clean(item.get("name") or item.get("author"))
                if isinstance(item, dict)
                else clean(item)
            )
        ]
    text = clean(value)
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [clean(item) for item in parsed if clean(item)]
    separator = ";" if ";" in text else "|" if "|" in text else None
    if separator:
        return [clean(item) for item in text.split(separator) if clean(item)]
    return [text]


def _parse_curated_authors(value: Any) -> List[str]:
    """Parse the curated papers.csv author column using its documented format."""
    people = normalize_author_names(value)
    if len(people) != 1 or "," not in people[0]:
        return people
    return [clean(author) for author in people[0].split(",") if clean(author)]


def _ordered_mapping_authors(
    paper_authors: Sequence[str],
    mapping_authors: Sequence[str],
) -> List[str]:
    """Keep paper order; use mappings only when they are the sole usable source."""
    if not paper_authors:
        ordered_mapping_authors = []
        seen_mapping_keys = set()
        for author in mapping_authors:
            key = _normalized_person(author)
            if key and key not in seen_mapping_keys:
                ordered_mapping_authors.append(author)
                seen_mapping_keys.add(key)
        return ordered_mapping_authors

    ordered = []
    seen = set()
    ambiguous_author_line = (
        len(paper_authors) == 1 and paper_authors[0].count(",") >= 2
    )
    if not ambiguous_author_line:
        for author in paper_authors:
            key = _normalized_person(author)
            if key and key not in seen:
                ordered.append(author)
                seen.add(key)
        if ordered:
            return ordered

    # A legacy comma-separated line cannot be split blindly because it may
    # contain "Family, Given" names. Mapping names may identify boundaries,
    # but their positions in the paper line still determine the order.
    author_line = clean(paper_authors[0]).casefold()
    positioned = []
    mapping_keys = set()
    for author in mapping_authors:
        key = _normalized_person(author)
        if not key or key in mapping_keys:
            continue
        mapping_keys.add(key)
        position = author_line.find(clean(author).casefold())
        if position >= 0:
            positioned.append((position, author))
    if mapping_keys and len(positioned) == len(mapping_keys):
        return [author for _position, author in sorted(positioned)]

    if paper_authors:
        return list(paper_authors)
    return [
        author
        for author in mapping_authors
        if _normalized_person(author)
    ]


def _normalized_person(value: Any) -> str:
    return canonical_name_key(value)


def _is_explicit_admin_supplement(record: Mapping[str, Any]) -> bool:
    return (
        clean(record.get("public_evidence_mode")) == "add"
        and clean(record.get("public_evidence_approval"))
        == "explicit_admin_supplement"
    )


def _valid_coordinates(record: Mapping[str, Any]) -> bool:
    latitude = record.get("latitude")
    longitude = record.get("longitude")
    if latitude in (None, ""):
        latitude = record.get("lat")
    if longitude in (None, ""):
        longitude = record.get("lon")
    try:
        latitude_value = float(latitude)
        longitude_value = float(longitude)
    except (TypeError, ValueError):
        return False
    return (
        math.isfinite(latitude_value)
        and math.isfinite(longitude_value)
        and -90 <= latitude_value <= 90
        and -180 <= longitude_value <= 180
    )


def _coordinate_signature(record: Mapping[str, Any]) -> Tuple[Any, ...]:
    latitude = record.get("latitude")
    longitude = record.get("longitude")
    if latitude in (None, ""):
        latitude = record.get("lat")
    if longitude in (None, ""):
        longitude = record.get("lon")
    return (
        round(float(latitude), 7),
        round(float(longitude), 7),
        clean(record.get("city")).casefold(),
        clean(record.get("country_code")).upper(),
        clean(record.get("region_code")).upper(),
    )


def _candidate_location_is_safe(record: Mapping[str, Any]) -> bool:
    confidence = clean(record.get("resolution_confidence")).casefold()
    needs_review = clean(record.get("needs_review")).casefold()
    return (
        _valid_coordinates(record)
        and confidence in {"medium", "high"}
        and needs_review not in {"1", "true", "yes", "y"}
    )


def _location_groups(
    records: Iterable[Mapping[str, Any]],
    *,
    require_safe_candidate: bool,
) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        institution = normalize_institution(
            record.get("normalized_institution")
            or record.get("institution")
        )
        if not institution or not _valid_coordinates(record):
            continue
        if require_safe_candidate and not _candidate_location_is_safe(record):
            continue
        grouped.setdefault(institution, []).append(dict(record))
    return grouped


def _unique_location(
    records: Sequence[Mapping[str, Any]],
) -> CoordinateMatch:
    by_signature: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    for record in records:
        by_signature.setdefault(_coordinate_signature(record), dict(record))
    if len(by_signature) == 1:
        return CoordinateMatch("known", next(iter(by_signature.values())))
    return CoordinateMatch("ambiguous", None)


def _processed_cache_location_groups(
    records: Iterable[Mapping[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        if (
            clean(record.get("status")).casefold() != "resolved"
            or clean(record.get("record_status")).casefold()
            not in {"", "active"}
            or clean(record.get("provider")).casefold()
            not in {"ror", "openalex"}
        ):
            continue
        location = {
            "institution": clean(record.get("resolved_institution_name")),
            "city": clean(record.get("resolved_city")),
            "country": next(
                (
                    clean(value)
                    for value in record.get("country_variants", [])
                    if len(clean(value)) != 2
                ),
                clean(record.get("resolved_country")),
            ),
            "country_code": next(
                (
                    clean(value).upper()
                    for value in record.get("country_variants", [])
                    if len(clean(value)) == 2
                ),
                clean(record.get("resolved_country")).upper(),
            ),
            "latitude": record.get("resolved_latitude"),
            "longitude": record.get("resolved_longitude"),
            "coordinate_source": (
                "data/processed/institution_resolution_cache.json"
            ),
            "coordinate_source_url": clean(record.get("source_url")),
            "_location_resolution_source": "processed_cache_fallback",
        }
        if not _valid_coordinates(location):
            continue
        names = [
            record.get("resolved_institution_name"),
            *(
                record.get("match_names")
                if isinstance(record.get("match_names"), list)
                else []
            ),
        ]
        for name in names:
            institution = normalize_institution(name)
            if institution:
                grouped.setdefault(institution, []).append(location)
    return grouped


def match_institutions_to_known_coordinates(
    public_map_records: Sequence[Mapping[str, Any]],
    candidate_map_records: Sequence[Mapping[str, Any]] = (),
    confirmed_location_records: Sequence[Mapping[str, Any]] = (),
    processed_cache_records: Sequence[Mapping[str, Any]] = (),
) -> Dict[str, CoordinateMatch]:
    confirmed_groups = _location_groups(
        confirmed_location_records, require_safe_candidate=False
    )
    processed_cache_groups = _processed_cache_location_groups(
        processed_cache_records
    )
    public_groups = _location_groups(
        public_map_records, require_safe_candidate=False
    )
    candidate_groups = _location_groups(
        candidate_map_records, require_safe_candidate=True
    )
    matches: Dict[str, CoordinateMatch] = {}
    for institution in (
        set(confirmed_groups)
        | set(processed_cache_groups)
        | set(public_groups)
        | set(candidate_groups)
    ):
        if institution in confirmed_groups:
            matches[institution] = _unique_location(
                confirmed_groups[institution]
            )
        elif institution in processed_cache_groups:
            matches[institution] = _unique_location(
                processed_cache_groups[institution]
            )
        elif institution in public_groups:
            matches[institution] = _unique_location(public_groups[institution])
        else:
            matches[institution] = _unique_location(candidate_groups[institution])
    return matches


def _paper_index(
    records: Sequence[MutableMapping[str, Any]],
) -> Dict[str, List[MutableMapping[str, Any]]]:
    index: Dict[str, List[MutableMapping[str, Any]]] = {}
    for record in records:
        for key in normalize_paper_identity_keys(record):
            index.setdefault(key, []).append(record)
    return index


def _matching_papers(
    record: Mapping[str, Any],
    index: Mapping[str, Sequence[MutableMapping[str, Any]]],
) -> List[MutableMapping[str, Any]]:
    seen = set()
    for key in normalize_paper_identity_keys(record):
        matches = index.get(key, ())
        if not matches:
            continue
        result = []
        for match in matches:
            marker = id(match)
            if marker not in seen:
                seen.add(marker)
                result.append(match)
        return result
    return []


def _curated_paper_record(
    row: Mapping[str, Any], task: str, subtask: str
) -> Dict[str, Any]:
    year = _parse_year(row.get("year"))
    arxiv_id = clean(row.get("arxiv_id"))
    paper_url = clean(row.get("paper_url"))
    openalex_url = clean(row.get("openalex_url"))
    doi = clean(row.get("doi"))
    if not paper_url:
        if doi:
            paper_url = (
                doi
                if doi.casefold().startswith(("http://", "https://"))
                else f"https://doi.org/{doi}"
            )
        elif arxiv_id:
            paper_url = f"https://arxiv.org/abs/{arxiv_id}"
        else:
            paper_url = openalex_url
    review_status = clean(row.get("review_status"))
    note = clean(row.get("review_note"))
    publication_type = normalize_publication_type(
        row.get("publication_type"), venue=row.get("venue"), venue_type=row.get("venue_type")
    )
    normalized_type = publication_type.casefold()
    entry_type = clean(row.get("entry_type")).casefold() or (
        "survey"
        if normalized_type in {"survey", "review", "systematic review"}
        else "dataset"
        if normalized_type == "dataset"
        else "benchmark"
        if normalized_type == "benchmark"
        else "method"
    )
    return {
        "paper_id": clean(row.get("paper_id")),
        "title": clean(row.get("title")),
        "in_scope": True,
        "year": year,
        "publication_year": year,
        "publication_date": "",
        "task": task,
        "subtask": subtask,
        "entry_type": entry_type,
        "venue": clean(row.get("venue")),
        "venue_name": clean(row.get("venue")),
        "venue_type": "",
        "publisher": "",
        "publication_type": publication_type,
        "abstract": clean(row.get("abstract")),
        "abstract_source": clean(row.get("metadata_source")),
        "ai_summary": "",
        "doi": doi,
        "arxiv_id": arxiv_id,
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
        "arxiv_year": None,
        "has_arxiv_version": bool(arxiv_id),
        "paper_url": paper_url,
        "primary_url": paper_url,
        "landing_page_url": "",
        "openalex_url": openalex_url,
        "is_arxiv_preprint": bool(arxiv_id and not doi),
        "url": paper_url,
        "authors": _parse_curated_authors(row.get("authors")),
        "source_database": clean(row.get("source_database")) or "curated",
        "metadata_source": clean(row.get("metadata_source")),
        "curation_status": clean(row.get("curation_status")),
        "review_status": review_status,
        "review_note": note,
        "needs_review": review_status != "reviewed",
        "notes": note,
        "has_map_location": False,
        "map_record_count": 0,
        "missing_affiliation": True,
        "missing_coordinates": False,
        "coverage_status": "missing_affiliation",
        "aggregated_institutions": [],
        "aggregated_country_names": [],
        "aggregated_country_codes": [],
        "aggregated_regions": [],
        "aggregated_region_codes": [],
    }


def build_curated_paper_preview_records(
    curated_papers: Sequence[Mapping[str, Any]],
    exclusion_rows: Sequence[Mapping[str, Any]] = (),
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    exclusion_index = build_active_exclusion_index(exclusion_rows)
    records = []
    skipped_scope = 0
    skipped_task = 0
    skipped_exclusion = 0
    for row in curated_papers:
        if clean(row.get("scope_status")).casefold() == "out_of_scope":
            skipped_scope += 1
            continue
        labels = normalize_task_subtask(row)
        if labels is None:
            skipped_task += 1
            continue
        record = _curated_paper_record(row, *labels)
        if record_is_excluded(record, exclusion_index):
            skipped_exclusion += 1
            continue
        records.append(record)
    return records, {
        "curated_papers_loaded": len(curated_papers),
        "curated_papers_eligible": len(records),
        "curated_papers_skipped_scope": skipped_scope,
        "curated_papers_skipped_task": skipped_task,
        "curated_papers_skipped_exclusion": skipped_exclusion,
    }


def _merge_curated_paper(
    existing: MutableMapping[str, Any],
    curated: Mapping[str, Any],
) -> None:
    confirmed = clean(curated.get("curation_status")) in (
        CONFIRMED_CURATION_STATUSES
    )
    for field in CURATED_OVERRIDE_FIELDS:
        value = curated.get(field)
        if value in (None, "", []):
            continue
        if confirmed or existing.get(field) in (None, "", []):
            existing[field] = value
    curated_note = clean(curated.get("notes"))
    existing_note = clean(existing.get("notes"))
    if curated_note and curated_note not in existing_note.split(" | "):
        existing["notes"] = (
            f"{existing_note} | {curated_note}"
            if existing_note
            else curated_note
        )


def _mapping_public_fields(mapping: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "mapping_id": clean(mapping.get("mapping_id")),
        "institution_id": clean(mapping.get("institution_id"))
        or stable_institution_id(mapping.get("institution")),
        "institution": clean(mapping.get("institution")),
        "institution_authors": _parse_people(
            mapping.get("institution_authors")
        ),
        "raw_affiliation": clean(mapping.get("raw_affiliation")),
        "evidence_source": clean(mapping.get("evidence_source")),
        "evidence_url": clean(mapping.get("evidence_url")),
        "affiliation_note": clean(mapping.get("affiliation_note")),
        "mapping_status": clean(mapping.get("mapping_status")),
        "review_note": clean(mapping.get("review_note")),
    }


def stable_institution_id(value: Any) -> str:
    normalized = normalize_institution(value)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"institution:{digest}" if normalized else ""


def _marker_id(
    paper: Mapping[str, Any], mapping: Mapping[str, Any]
) -> str:
    mapping_id = clean(mapping.get("mapping_id"))
    identity = mapping_id or "|".join(
        normalize_paper_identity_keys(paper)
        + [
            normalize_institution(mapping.get("institution")),
            normalize_institution(mapping.get("institution_authors")),
        ]
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
    return f"curated-map:{digest}"


def _mapping_note(mapping: Mapping[str, Any]) -> str:
    values = []
    for label, field in (
        ("Raw affiliation", "raw_affiliation"),
        ("Evidence source", "evidence_source"),
        ("Evidence URL", "evidence_url"),
        ("Affiliation note", "affiliation_note"),
        ("Review note", "review_note"),
    ):
        value = clean(mapping.get(field))
        if value:
            values.append(f"{label}: {value}")
    return " | ".join(values)


def _curated_marker(
    paper: Mapping[str, Any],
    mapping: Mapping[str, Any],
    location: Mapping[str, Any],
) -> Dict[str, Any]:
    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if latitude in (None, ""):
        latitude = location.get("lat")
    if longitude in (None, ""):
        longitude = location.get("lon")
    paper_url = clean(
        paper.get("paper_url")
        or paper.get("primary_url")
        or paper.get("openalex_url")
    )
    cache_fallback = (
        clean(location.get("_location_resolution_source"))
        == "processed_cache_fallback"
    )
    notes = _mapping_note(mapping)
    if cache_fallback:
        fallback_note = (
            "Coordinates applied from processed "
            "institution_resolution_cache fallback"
        )
        notes = f"{notes} | {fallback_note}" if notes else fallback_note
    return normalize_regional_location({
        "id": _marker_id(paper, mapping),
        "paper_id": clean(paper.get("paper_id")),
        "title": clean(paper.get("title")),
        "in_scope": True,
        "year": _parse_year(
            paper.get("publication_year") or paper.get("year")
        ),
        "publication_year": _parse_year(
            paper.get("publication_year") or paper.get("year")
        ),
        "publication_date": clean(paper.get("publication_date")),
        "task": clean(paper.get("task")),
        "subtask": clean(paper.get("subtask")),
        "entry_type": clean(paper.get("entry_type")) or "method",
        "venue": clean(paper.get("venue") or paper.get("venue_name")),
        "venue_name": clean(paper.get("venue_name") or paper.get("venue")),
        "publication_type": normalize_publication_type(
            paper.get("publication_type"),
            venue=paper.get("venue") or paper.get("venue_name"),
            venue_type=paper.get("venue_type"),
        ),
        "abstract": clean(paper.get("abstract")),
        "abstract_source": clean(paper.get("abstract_source")),
        "doi": clean(paper.get("doi")),
        "arxiv_id": clean(paper.get("arxiv_id")),
        "arxiv_url": clean(paper.get("arxiv_url")),
        "has_arxiv_version": bool(
            clean(paper.get("arxiv_id")) or clean(paper.get("arxiv_url"))
        ),
        "paper_url": paper_url,
        "primary_url": paper_url,
        "openalex_url": clean(paper.get("openalex_url")),
        "url": paper_url,
        "authors": _parse_people(paper.get("authors")),
        "institution": clean(mapping.get("institution")),
        "institution_id": stable_institution_id(mapping.get("institution")),
        "institution_authors": _parse_people(
            mapping.get("institution_authors")
        ),
        "country": clean(location.get("country")),
        "country_code": clean(location.get("country_code")),
        "region": clean(location.get("region")),
        "region_code": clean(location.get("region_code")),
        "raw_country": clean(location.get("raw_country")),
        "raw_country_code": clean(location.get("raw_country_code")),
        "city": clean(location.get("city")),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "lat": float(latitude),
        "lon": float(longitude),
        "source_database": "curated",
        "metadata_source": clean(paper.get("metadata_source")),
        "curation_status": clean(paper.get("curation_status")),
        "mapping_id": clean(mapping.get("mapping_id")),
        "raw_affiliation": clean(mapping.get("raw_affiliation")),
        "evidence_source": clean(mapping.get("evidence_source")),
        "evidence_url": clean(mapping.get("evidence_url")),
        "coordinate_source": clean(location.get("coordinate_source")),
        "coordinate_source_url": clean(
            location.get("coordinate_source_url")
        ),
        "resolution_method": (
            "curated_confirmed_location"
            if clean(location.get("location_id"))
            else "processed_institution_resolution_cache_fallback"
            if cache_fallback
            else "curated_mapping_existing_location"
        ),
        "resolution_confidence": "high",
        "needs_review": False,
        "notes": notes,
    })


def _mapping_matches_paper(
    mapping: Mapping[str, Any], paper: Mapping[str, Any]
) -> bool:
    return bool(
        set(normalize_paper_identity_keys(mapping))
        & set(normalize_paper_identity_keys(paper))
    )


def affiliation_review_state(
    paper: Mapping[str, Any],
    mappings: Sequence[Mapping[str, Any]],
    curated_papers: Sequence[Mapping[str, Any]] = (),
) -> str:
    """Return the paper-level source decision for affiliation evidence.

    Active mappings are accepted curation. Needs-review mappings are still
    candidates, so automatic evidence remains available until one is accepted.
    Excluded mapping history or an explicit paper state is durable evidence
    that an empty affiliation result was reviewed. General paper-metadata
    review is deliberately not treated as affiliation review.
    """
    matching_mappings = [
        mapping for mapping in mappings if _mapping_matches_paper(mapping, paper)
    ]
    statuses = {
        clean(mapping.get("mapping_status")) for mapping in matching_mappings
    }
    if ACTIVE_MAPPING_STATUS in statuses:
        return "curated"
    if "needs_review" in statuses:
        return "unreviewed"
    if matching_mappings:
        return "reviewed_empty"
    explicit_state = clean(paper.get("affiliation_review_state"))
    if explicit_state in AFFILIATION_REVIEW_STATES:
        return explicit_state
    return "unreviewed"


def _mark_preliminary_automatic_evidence(
    record: MutableMapping[str, Any],
) -> None:
    record["affiliation_review_state"] = "unreviewed"
    record["institution_source"] = "automatic_fallback"
    record["preliminary_affiliations"] = True
    note = "Preliminary automatic affiliation evidence; not manually reviewed."
    existing_note = clean(record.get("resolution_notes"))
    if note not in existing_note:
        record["resolution_notes"] = (
            f"{existing_note} | {note}" if existing_note else note
        )
    for field in ("affiliations", "author_institution_affiliations"):
        values = record.get(field)
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, MutableMapping):
                value["mapping_fallback"] = True


def enforce_affiliation_source_precedence(
    paper_records: Sequence[MutableMapping[str, Any]],
    map_records: List[Dict[str, Any]],
    mappings: Sequence[Mapping[str, Any]],
    curated_papers: Sequence[Mapping[str, Any]] = (),
) -> int:
    """Apply paper-level manual-first selection and return removed markers."""
    removed = 0
    resolved_mapping_ids = {
        clean(record.get("mapping_id"))
        for record in map_records
        if clean(record.get("source_database")).casefold() == "curated"
        and clean(record.get("mapping_id"))
    }
    for paper in paper_records:
        state = affiliation_review_state(paper, mappings, curated_papers)
        paper["affiliation_review_state"] = state
        active_mapping_ids = {
            clean(mapping.get("mapping_id"))
            for mapping in mappings
            if _mapping_matches_paper(mapping, paper)
            and clean(mapping.get("mapping_status")) == ACTIVE_MAPPING_STATUS
            and clean(mapping.get("mapping_id"))
        }
        matching_marker_ids = {
            id(marker)
            for marker in map_records
            if _mapping_matches_paper(marker, paper)
        }
        if state == "unreviewed":
            _mark_preliminary_automatic_evidence(paper)
            for marker in map_records:
                if id(marker) in matching_marker_ids:
                    _mark_preliminary_automatic_evidence(marker)
            continue

        kept = []
        for marker in map_records:
            if id(marker) not in matching_marker_ids:
                kept.append(marker)
                continue
            if (
                state == "curated"
                and clean(marker.get("source_database")).casefold() == "curated"
                and clean(marker.get("mapping_id")) in active_mapping_ids
            ):
                marker["affiliation_review_state"] = "curated"
                marker["institution_source"] = "curated"
                marker["preliminary_affiliations"] = False
                kept.append(marker)
            else:
                removed += 1
        map_records[:] = kept
        _recalculate_paper_details(
            paper, map_records, mappings, resolved_mapping_ids
        )
        paper["affiliation_review_state"] = state
        paper["institution_source"] = (
            "curated" if state == "curated" else "reviewed_empty"
        )
        paper["preliminary_affiliations"] = False
    return removed


def _queue_key(record: Mapping[str, Any]) -> Tuple[str, str]:
    paper_id = clean(
        record.get("paper_id")
        or record.get("related_paper_id")
        or record.get("display_id")
    ).casefold()
    identity = (
        f"paper_id:{paper_id}"
        if paper_id
        else next(iter(normalize_paper_identity_keys(record)), "")
    )
    return identity, normalize_institution(record.get("institution"))


def _merged_people(left: Any, right: Any) -> str:
    people = []
    seen = set()
    for value in _parse_people(left) + _parse_people(right):
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            people.append(value)
    return "; ".join(people)


def _upsert_location_review(
    rows: List[Dict[str, str]],
    mapping: Mapping[str, Any],
    *,
    coordinate_status: str,
) -> str:
    institution_id = clean(mapping.get("institution_id"))
    if not institution_id:
        raise CuratedExportError(
            "location review creation requires a canonical institution_id"
        )
    now = _timestamp()
    location_status = (
        "needs_coordinate_review"
        if coordinate_status == "ambiguous"
        else "missing"
    )
    key = _queue_key(mapping)
    values = {
        "institution": clean(mapping.get("institution")),
        "canonical_institution_name": clean(mapping.get("institution")),
        "institution_id": institution_id,
        "related_paper_id": clean(mapping.get("paper_id")),
        "title": clean(mapping.get("title")),
        "year": clean(mapping.get("year")),
        "doi": clean(mapping.get("doi")),
        "openalex_url": clean(mapping.get("openalex_url")),
        "institution_authors": clean(mapping.get("institution_authors")),
        "raw_affiliation": clean(mapping.get("raw_affiliation")),
        "evidence_source": clean(mapping.get("evidence_source")),
        "evidence_url": clean(mapping.get("evidence_url")),
        "suggested_city": "",
        "suggested_country": "",
        "review_status": (
            "ambiguous"
            if coordinate_status == "ambiguous"
            else "needs_coordinates"
        ),
        "location_status": location_status,
        "coordinate_status": coordinate_status,
        "review_note": clean(mapping.get("review_note")),
        "updated_at": now,
    }
    for row in rows:
        if _queue_key(row) != key:
            continue
        row["institution_authors"] = _merged_people(
            row.get("institution_authors"), values["institution_authors"]
        )
        for field, value in values.items():
            if field in {"institution_authors", "review_note"}:
                continue
            if value:
                row[field] = value
        if not clean(row.get("review_note")):
            row["review_note"] = values["review_note"]
        row["created_at"] = clean(row.get("created_at")) or now
        row["updated_at"] = now
        return "updated"
    rows.append({**values, "created_at": now})
    return "created"


def _mark_location_known(
    rows: List[Dict[str, str]], mapping: Mapping[str, Any]
) -> bool:
    key = _queue_key(mapping)
    for row in rows:
        if _queue_key(row) == key:
            if (
                clean(row.get("location_status")) == "known"
                and clean(row.get("coordinate_status")) == "known"
            ):
                return False
            row["location_status"] = "known"
            row["coordinate_status"] = "known"
            row["updated_at"] = _timestamp()
            return True
    return False


def build_curated_map_records(
    paper_records: Sequence[MutableMapping[str, Any]],
    mappings: Sequence[Mapping[str, Any]],
    public_map_records: Sequence[Mapping[str, Any]],
    candidate_map_records: Sequence[Mapping[str, Any]] = (),
    exclusion_rows: Sequence[Mapping[str, Any]] = (),
    location_review_rows: List[Dict[str, str]] | None = None,
    confirmed_location_records: Sequence[Mapping[str, Any]] = (),
    processed_cache_records: Sequence[Mapping[str, Any]] = (),
    institution_aliases: Sequence[Mapping[str, Any]] = (),
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    paper_index = _paper_index(paper_records)
    exclusion_index = build_active_exclusion_index(exclusion_rows)
    locations = match_institutions_to_known_coordinates(
        public_map_records,
        candidate_map_records,
        confirmed_location_records,
        processed_cache_records,
    )
    review_rows = location_review_rows if location_review_rows is not None else []
    markers = []
    missing = 0
    ambiguous = 0
    queue_created = 0
    queue_updated = 0
    queue_known = 0
    skipped_status = 0
    skipped_paper = 0
    skipped_task = 0
    resolved_mapping_ids = set()
    matched_paper_mappings = 0
    emitted_marker_keys = set()
    confirmed_aliases = {
        normalize_institution(row.get("alias_name")):
        clean(row.get("canonical_institution_name"))
        for row in institution_aliases
        if clean(row.get("review_status")) == "confirmed"
        and clean(row.get("alias_name"))
        and clean(row.get("canonical_institution_name"))
    }
    confirmed_location_keys = {
        normalize_institution(
            row.get("normalized_institution") or row.get("institution")
        )
        for row in confirmed_location_records
        if _valid_coordinates(row)
    }
    review_status_by_key = {
        _queue_key(row): clean(row.get("review_status")) or "pending_review"
        for row in review_rows
    }
    non_exportable_statuses = {
        "pending_review",
        "needs_coordinates",
        "ambiguous",
        "alias_candidate",
        "ignore",
        "excluded",
    }

    for mapping in mappings:
        if clean(mapping.get("mapping_status")) != ACTIVE_MAPPING_STATUS:
            skipped_status += 1
            continue
        papers = _matching_papers(mapping, paper_index)
        if not papers:
            skipped_paper += 1
            continue
        paper = papers[0]
        if record_is_excluded(paper, exclusion_index):
            skipped_paper += 1
            continue
        matched_paper_mappings += 1
        raw_institution_key = normalize_institution(mapping.get("institution"))
        canonical_institution = confirmed_aliases.get(raw_institution_key)
        institution_key = normalize_institution(
            canonical_institution or mapping.get("institution")
        )
        queue_status = (
            "alias_of_confirmed"
            if canonical_institution
            else review_status_by_key.get(_queue_key(mapping))
        )
        if queue_status in non_exportable_statuses:
            skipped_status += 1
            continue
        match = (
            locations.get(institution_key, CoordinateMatch("missing", None))
            if institution_key in confirmed_location_keys
            else CoordinateMatch("missing", None)
        )
        if match.status != "known" or match.record is None:
            coordinate_status = (
                "ambiguous" if match.status == "ambiguous" else "missing"
            )
            result = _upsert_location_review(
                review_rows, mapping, coordinate_status=coordinate_status
            )
            queue_created += int(result == "created")
            queue_updated += int(result == "updated")
            missing += int(coordinate_status == "missing")
            ambiguous += int(coordinate_status == "ambiguous")
            continue
        queue_known += int(_mark_location_known(review_rows, mapping))
        resolved_mapping_ids.add(clean(mapping.get("mapping_id")))
        if clean(paper.get("task")) not in PUBLIC_MAP_TASKS:
            skipped_task += 1
            continue
        export_mapping = dict(mapping)
        if canonical_institution:
            export_mapping["institution"] = canonical_institution
        marker_key = (
            next(iter(normalize_paper_identity_keys(paper)), ""),
            normalize_institution(export_mapping.get("institution")),
        )
        if marker_key in emitted_marker_keys:
            continue
        emitted_marker_keys.add(marker_key)
        markers.append(_curated_marker(paper, export_mapping, match.record))

    return markers, {
        "curated_mappings_loaded": len(mappings),
        "curated_markers_created": len(markers),
        "curated_mappings_missing_coordinates": missing,
        "curated_mappings_ambiguous_coordinates": ambiguous,
        "curated_mappings_skipped_status": skipped_status,
        "curated_mappings_skipped_paper": skipped_paper,
        "curated_mappings_skipped_task": skipped_task,
        "curated_mappings_matched_papers": matched_paper_mappings,
        "location_review_rows_created": queue_created,
        "location_review_rows_updated": queue_updated,
        "location_review_rows_marked_known": queue_known,
        "resolved_mapping_ids": resolved_mapping_ids,
    }


def _remove_overridden_markers(
    map_records: List[Dict[str, Any]],
    paper: Mapping[str, Any],
    replacement_marker: Mapping[str, Any],
) -> int:
    paper_keys = set(normalize_paper_identity_keys(paper))
    institution_key = normalize_institution(replacement_marker.get("institution"))
    replacement_authors = {
        _normalized_person(author)
        for author in _parse_people(
            replacement_marker.get("institution_authors")
        )
    }
    kept = []
    removed = 0
    for marker in map_records:
        same_paper = bool(
            paper_keys & set(normalize_paper_identity_keys(marker))
        )
        same_marker_id = bool(
            clean(replacement_marker.get("id"))
            and clean(marker.get("id")) == clean(replacement_marker.get("id"))
        )
        same_institution = (
            normalize_institution(marker.get("institution")) == institution_key
        )
        marker_authors = {
            _normalized_person(author)
            for author in _parse_people(marker.get("institution_authors"))
        }
        superseded_automatic_mapping = bool(
            replacement_authors & marker_authors
        ) and clean(marker.get("source_database")).casefold() != "curated"
        if (
            same_paper
            and not _is_explicit_admin_supplement(marker)
            and (
                same_marker_id
                or same_institution
                or superseded_automatic_mapping
            )
        ):
            removed += 1
        else:
            kept.append(marker)
    map_records[:] = kept
    return removed


def _recalculate_paper_details(
    paper: MutableMapping[str, Any],
    map_records: Sequence[Mapping[str, Any]],
    mappings: Sequence[Mapping[str, Any]],
    resolved_mapping_ids: set[str],
) -> None:
    markers = [
        marker
        for marker in map_records
        if _mapping_matches_paper(marker, paper)
    ]
    visible_mappings = [
        mapping
        for mapping in mappings
        if clean(mapping.get("mapping_status")) == ACTIVE_MAPPING_STATUS
        and _mapping_matches_paper(mapping, paper)
    ]
    has_map_location = bool(markers)
    missing_affiliation = not has_map_location and not visible_mappings
    active_mappings = [
        mapping
        for mapping in visible_mappings
        if clean(mapping.get("mapping_status")) == ACTIVE_MAPPING_STATUS
    ]
    missing_coordinates = (
        not has_map_location
        and any(
            clean(mapping.get("mapping_id")) not in resolved_mapping_ids
            for mapping in active_mappings
        )
    )
    if has_map_location:
        coverage_status = "map_ready"
    elif missing_affiliation:
        coverage_status = "missing_affiliation"
    elif missing_coordinates:
        coverage_status = "missing_coordinates"
    else:
        coverage_status = "paper_only_review"

    unresolved_active = any(
        clean(mapping.get("mapping_id")) not in resolved_mapping_ids
        for mapping in active_mappings
    )
    needs_review_mapping = any(
        clean(mapping.get("mapping_status")) == "needs_review"
        for mapping in visible_mappings
    )
    paper["has_map_location"] = has_map_location
    paper["map_record_count"] = len(markers)
    paper["missing_affiliation"] = missing_affiliation
    paper["missing_coordinates"] = missing_coordinates
    paper["coverage_status"] = coverage_status
    paper["needs_review"] = bool(
        missing_affiliation
        or missing_coordinates
        or unresolved_active
        or needs_review_mapping
        or clean(paper.get("task")) == "uncertain"
        or (
            clean(paper.get("review_status"))
            and clean(paper.get("review_status")) != "reviewed"
        )
    )
    paper["curated_mappings"] = [
        _mapping_public_fields(mapping) for mapping in visible_mappings
    ]
    current_authors = _parse_people(paper.get("authors"))
    affiliation_records = list(visible_mappings)
    known_affiliation_keys = {
        normalize_institution(mapping.get("institution"))
        for mapping in affiliation_records
    }
    for marker in markers:
        marker_key = normalize_institution(marker.get("institution"))
        if (
            _is_explicit_admin_supplement(marker)
            and marker_key
            and marker_key not in known_affiliation_keys
        ):
            affiliation_records.append(marker)
            known_affiliation_keys.add(marker_key)

    mapping_authors = []
    for mapping in affiliation_records:
        for author in _parse_people(mapping.get("institution_authors")):
            if normalize_institution(author) not in {
                normalize_institution(value) for value in mapping_authors
            }:
                mapping_authors.append(author)
    if mapping_authors:
        paper["authors"] = _ordered_mapping_authors(
            current_authors, mapping_authors
        )
    affiliations = []
    author_affiliations: Dict[str, Dict[str, Any]] = {}
    paper_authors = _parse_people(paper.get("authors"))
    for index, mapping in enumerate(affiliation_records, start=1):
        institution = clean(mapping.get("institution"))
        institution_id = stable_institution_id(institution)
        mapping_authors = _parse_people(mapping.get("institution_authors"))
        mapping_source = (
            "curated_admin"
            if clean(mapping.get("mapping_status")) == ACTIVE_MAPPING_STATUS
            else "raw_affiliation"
        )
        affiliations.append(
            {
                "index": index,
                "institution_id": institution_id,
                "institution": institution,
                "authors": mapping_authors,
                "mapping_source": mapping_source,
                "mapping_fallback": False,
            }
        )
        for author in mapping_authors:
            matched_paper_authors = [
                paper_author
                for paper_author in paper_authors
                if names_match(paper_author, author)
            ]
            author_name = (
                matched_paper_authors[0]
                if len(matched_paper_authors) == 1
                else author
            )
            author_key = canonical_name_key(author_name)
            values = author_affiliations.setdefault(
                author_key,
                {
                    "author": author_name,
                    "institution_indices": [],
                    "institution_ids": [],
                    "source": mapping_source,
                    "fallback": False,
                },
            )
            values["institution_indices"].append(index)
            values["institution_ids"].append(institution_id)
    paper["author_institution_affiliations"] = affiliations
    paper["author_institution_indices"] = list(author_affiliations.values())
    # The final public-detail pass rebuilds these fields from the current
    # curated mappings. Do not let a preserved preview's stale derived schema
    # outrank corrected institution names or author mappings.
    paper.pop("affiliations", None)
    paper.pop("current_institution", None)
    for marker in markers:
        marker["authors"] = list(paper.get("authors") or [])
        marker["author_institution_affiliations"] = affiliations
        marker["author_institution_indices"] = list(
            author_affiliations.values()
        )
        marker.pop("affiliations", None)
        marker.pop("current_institution", None)
    paper["aggregated_institutions"] = sorted(
        {
            clean(record.get("institution"))
            for record in [*markers, *visible_mappings]
            if clean(record.get("institution"))
        },
        key=str.casefold,
    )
    paper["aggregated_country_names"] = sorted(
        {
            clean(marker.get("country"))
            for marker in markers
            if clean(marker.get("country"))
        },
        key=str.casefold,
    )
    paper["aggregated_country_codes"] = sorted(
        {
            clean(marker.get("country_code"))
            for marker in markers
            if clean(marker.get("country_code"))
        }
    )
    paper["aggregated_regions"] = sorted(
        {
            clean(marker.get("region"))
            for marker in markers
            if clean(marker.get("region"))
        },
        key=str.casefold,
    )
    paper["aggregated_region_codes"] = sorted(
        {
            clean(marker.get("region_code"))
            for marker in markers
            if clean(marker.get("region_code"))
        }
    )


def integrate_curated_records(
    paper_records: Sequence[Mapping[str, Any]],
    map_records: Sequence[Mapping[str, Any]],
    curated_papers: Sequence[Mapping[str, Any]],
    mappings: Sequence[Mapping[str, Any]],
    exclusion_rows: Sequence[Mapping[str, Any]] = (),
    candidate_map_records: Sequence[Mapping[str, Any]] = (),
    location_review_rows: Sequence[Mapping[str, Any]] = (),
    confirmed_location_records: Sequence[Mapping[str, Any]] = (),
    processed_cache_records: Sequence[Mapping[str, Any]] = (),
    institution_aliases: Sequence[Mapping[str, Any]] = (),
) -> Tuple[
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, str]],
    Dict[str, Any],
]:
    papers = [dict(record) for record in paper_records]
    maps = [dict(record) for record in map_records]
    reviews = [dict(row) for row in location_review_rows]
    curated_records, paper_summary = build_curated_paper_preview_records(
        curated_papers, exclusion_rows
    )
    paper_index = _paper_index(papers)
    map_index = _paper_index(maps)
    added = 0
    merged = 0
    for curated in curated_records:
        matches = _matching_papers(curated, paper_index)
        if matches:
            target = matches[0]
            _merge_curated_paper(target, curated)
            merged += 1
        else:
            target = curated
            papers.append(target)
            for key in normalize_paper_identity_keys(target):
                paper_index.setdefault(key, []).append(target)
            added += 1
        for map_record in _matching_papers(curated, map_index):
            _merge_curated_paper(map_record, curated)

    # Source selection is paper-wide. Remove every automatic marker before
    # creating replacements so a different institution or missing coordinate
    # cannot leave stale automatic evidence behind.
    replaced_markers = enforce_affiliation_source_precedence(
        papers, maps, mappings, curated_papers
    )

    marker_records, mapping_summary = build_curated_map_records(
        papers,
        mappings,
        maps,
        candidate_map_records,
        exclusion_rows,
        reviews,
        confirmed_location_records,
        processed_cache_records,
        institution_aliases,
    )
    for marker in marker_records:
        matching = _matching_papers(marker, paper_index)
        if not matching:
            continue
        maps.append(marker)

    # Rebuild every affected paper from the selected source. Running this a
    # second time is intentional: curated markers now exist and must be the
    # only marker inputs used for detail affiliations and superscripts.
    replaced_markers += enforce_affiliation_source_precedence(
        papers, maps, mappings, curated_papers
    )

    papers.sort(
        key=lambda record: (
            -(_parse_year(record.get("publication_year") or record.get("year")) or 0),
            clean(record.get("title")).casefold(),
        )
    )
    mapping_summary = dict(mapping_summary)
    mapping_summary.pop("resolved_mapping_ids", None)
    return papers, maps, reviews, {
        **paper_summary,
        **mapping_summary,
        "curated_papers_added": added,
        "curated_papers_merged": merged,
        "curated_markers_replaced": replaced_markers,
        "stale_public_markers_suppressed": replaced_markers,
    }
