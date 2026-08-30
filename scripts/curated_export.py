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
        OBSOLETE_AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        PAPERS_COLUMNS,
        normalize_curation_status,
    )
    from .country_normalization import normalize_country_region, public_location_display
    from .publication_types import normalize_book_record, normalize_publication_type
    from .paper_categories import categories_from_record
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
    from .paper_links import resolve_public_links
    from .public_relationships import (
        ReviewedRelationshipResolver, canonical_author_names, normalized_author_set,
    )
except ImportError:
    from curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        OBSOLETE_AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        PAPERS_COLUMNS,
        normalize_curation_status,
    )
    from country_normalization import normalize_country_region, public_location_display
    from publication_types import normalize_book_record, normalize_publication_type
    from paper_categories import categories_from_record
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
    from paper_links import resolve_public_links
    from public_relationships import (
        ReviewedRelationshipResolver, canonical_author_names, normalized_author_set,
    )


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
CONFIRMED_CURATION_STATUSES = {"confirmed"}
CURATED_OVERRIDE_FIELDS = (
    "paper_id",
    "title",
    "year",
    "publication_year",
    "authors",
    "venue",
    "venue_name",
    "venue_id",
    "venue_acronym",
    "venue_type",
    "venue_track",
    "raw_venue",
    "venue_aliases",
    "venue_label",
    "doi",
    "arxiv_id",
    "arxiv_url",
    "paper_url",
    "primary_url",
    "openalex_url",
    "publication_type",
    "abstract",
    "task",
    "paper_categories",
    "source_database",
    "metadata_source",
    "curation_status",
    "review_status",
)
CURATED_AUTHORITATIVE_PUBLIC_FIELDS = {
    "doi",
    "arxiv_id",
    "arxiv_url",
    "paper_url",
    "primary_url",
    "openalex_url",
    "venue",
    "venue_name",
    "venue_id",
    "venue_acronym",
    "venue_type",
    "venue_track",
    "venue_aliases",
    "venue_label",
    "publication_type",
    "paper_categories",
}


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
            actual_columns = tuple(reader.fieldnames or ())
            projected_columns = tuple(
                column for column in actual_columns
                if column not in OBSOLETE_AUTHOR_INSTITUTION_MAPPING_COLUMNS
            )
            missing_affiliation_order = (
                tuple(columns) == tuple(AUTHOR_INSTITUTION_MAPPING_COLUMNS)
                and "affiliation_order" not in actual_columns
                and tuple(
                    column for column in columns
                    if column != "affiliation_order"
                ) == projected_columns
            )
            legacy_mapping_header = (
                tuple(columns) == tuple(AUTHOR_INSTITUTION_MAPPING_COLUMNS)
                and (
                    projected_columns == tuple(columns)
                    or missing_affiliation_order
                )
                and set(actual_columns) - set(columns)
                <= OBSOLETE_AUTHOR_INSTITUTION_MAPPING_COLUMNS
            )
            if actual_columns != tuple(columns) and not legacy_mapping_header:
                raise CuratedExportError(
                    f"{path} does not have the exact curated CSV header"
                )
            return [
                {column: clean(row.get(column)) for column in columns}
                for row in reader
            ]
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
        if paper_id.startswith("openalex:"):
            work_id = paper_id.split(":", 1)[1]
            if work_id:
                keys.append(f"openalex:https://openalex.org/{work_id}")
        elif paper_id.startswith("https://openalex.org/"):
            keys.append(f"openalex:{paper_id.rstrip('/')}")
    merged_versions = record.get("merged_versions")
    if isinstance(merged_versions, list):
        for version in merged_versions:
            if isinstance(version, Mapping):
                keys.extend(all_identity_keys(version))
    return list(dict.fromkeys(keys))


class PaperIdentityCache:
    """Transaction-local normalized identities keyed by live record identity."""

    def __init__(self) -> None:
        self._keys: Dict[int, Tuple[Mapping[str, Any], Tuple[str, ...]]] = {}

    def keys(self, record: Mapping[str, Any]) -> Tuple[str, ...]:
        marker = id(record)
        cached = self._keys.get(marker)
        if cached is None or cached[0] is not record:
            keys = tuple(normalize_paper_identity_keys(record))
            self._keys[marker] = (record, keys)
            return keys
        return cached[1]


class PaperIdentityIndex:
    """Match any canonical identity while preserving source-record order."""

    def __init__(
        self,
        records: Sequence[Mapping[str, Any]],
        cache: PaperIdentityCache,
    ) -> None:
        self.records = records
        self.cache = cache
        self.positions = {id(record): index for index, record in enumerate(records)}
        self.by_key: Dict[str, List[Mapping[str, Any]]] = {}
        for record in records:
            for key in cache.keys(record):
                self.by_key.setdefault(key, []).append(record)

    def matches(self, record: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        candidates: Dict[int, Mapping[str, Any]] = {}
        for key in self.cache.keys(record):
            for candidate in self.by_key.get(key, ()):
                candidates.setdefault(id(candidate), candidate)
        return sorted(
            candidates.values(), key=lambda candidate: self.positions[id(candidate)]
        )


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


def normalize_task(record: Mapping[str, Any]) -> str | None:
    task = normalize_export_task_labels(dict(record))
    if task is None:
        return None
    if task not in PUBLIC_PAPER_TASKS:
        return None
    return task


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

    # Curated legacy rows sometimes mix comma-delimited rosters with
    # ``Family, Given`` names, or retain two mapped authors in one comma-joined
    # field. Reconstruct a boundary only when the active mapping author set
    # proves one unique interpretation; otherwise preserve the source text.
    reconciled_authors = []
    index = 0
    while index < len(paper_authors):
        author = paper_authors[index]
        whole_matches = [
            candidate for candidate in mapping_authors
            if names_match(author, candidate)
        ]
        if len(whole_matches) == 1:
            reconciled_authors.append(author)
            index += 1
            continue

        comma_parts = [clean(part) for part in author.split(",") if clean(part)]
        part_matches = [
            [
                candidate for candidate in mapping_authors
                if names_match(part, candidate)
            ]
            for part in comma_parts
        ]
        if (
            len(comma_parts) > 1
            and all(len(matches) == 1 for matches in part_matches)
            and len({matches[0] for matches in part_matches}) == len(part_matches)
        ):
            reconciled_authors.extend(matches[0] for matches in part_matches)
            index += 1
            continue

        if (
            index + 1 < len(paper_authors)
            and len(canonical_name_key(author).split()) == 1
            and len(canonical_name_key(paper_authors[index + 1]).split()) == 1
        ):
            combined = f"{author} {paper_authors[index + 1]}"
            combined_matches = [
                candidate for candidate in mapping_authors
                if names_match(combined, candidate)
            ]
            if len(combined_matches) == 1:
                reconciled_authors.append(combined_matches[0])
                index += 2
                continue

        reconciled_authors.append(author)
        index += 1

    paper_authors = reconciled_authors
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


def _confirmed_location_is_usable(record: Mapping[str, Any]) -> bool:
    # Blank status remains compatible with legacy caller-supplied fixtures.
    # Explicit review/missing states must never be revived by numeric values.
    return clean(record.get("coordinate_status")).casefold() in {
        "", "known", "confirmed",
    } and _valid_coordinates(record)


def _confirmed_institution_ids(
    records: Sequence[Mapping[str, Any]],
) -> set[str]:
    """Return canonical identities that are resolved and publicly usable."""
    return {
        clean(record.get("institution_id"))
        for record in records
        if clean(record.get("institution_status")).casefold() == "active"
        and clean(record.get("institution_id"))
    }


def _supported_preliminary_mapping(
    mapping: Mapping[str, Any], paper: Mapping[str, Any]
) -> bool:
    """Whether paper metadata supports a still-preliminary affiliation link."""
    return (
        clean(mapping.get("mapping_status")) == "needs_review"
        and clean(paper.get("curation_status")) == "needs_review"
        and bool(clean(mapping.get("raw_affiliation")))
        and bool(clean(mapping.get("provenance_source")))
    )


def _candidate_location_is_safe(record: Mapping[str, Any]) -> bool:
    confidence = clean(record.get("resolution_confidence")).casefold()
    needs_review = clean(record.get("needs_review")).casefold()
    return (
        _valid_coordinates(record)
        and confidence in {"medium", "high"}
        and needs_review not in {"1", "true", "yes", "y"}
    )


def _institution_location_keys(record: Mapping[str, Any]) -> List[str]:
    keys: List[str] = []
    location_id = clean(record.get("location_id"))
    if location_id:
        keys.append(f"location_id:{location_id.casefold()}")
    institution_id = clean(record.get("institution_id"))
    city = clean(
        record.get("city")
        or record.get("institution_city")
        or record.get("suggested_city")
    ).casefold()
    country = clean(
        record.get("country")
        or record.get("institution_country")
        or record.get("suggested_country")
        or record.get("country_code")
    ).casefold()
    if institution_id:
        if city and country:
            keys.append(
                f"id:{institution_id.casefold()}|city:{city}|country:{country}"
            )
        keys.append(f"id:{institution_id.casefold()}")
    institution = normalize_institution(
        record.get("normalized_institution")
        or record.get("institution")
        or record.get("canonical_institution_name")
    )
    if institution:
        if city and country:
            keys.append(f"name:{institution}|city:{city}|country:{country}")
        keys.append(f"name:{institution}")
    return keys


def _preferred_institution_location_key(record: Mapping[str, Any]) -> str:
    keys = _institution_location_keys(record)
    return keys[0] if keys else ""


def _mapping_location_lookup_keys(record: Mapping[str, Any]) -> List[str]:
    """Honor an explicit mapping location without trying another office."""
    location_id = clean(record.get("location_id"))
    if location_id:
        return [f"location_id:{location_id.casefold()}"]
    return _institution_location_keys(record)


def _coordinate_match_for_keys(
    keys: Sequence[str],
    locations: Mapping[str, CoordinateMatch],
    confirmed_location_keys: set[str],
) -> CoordinateMatch:
    saw_ambiguous = False
    for key in keys:
        if key not in confirmed_location_keys:
            continue
        match = locations.get(key, CoordinateMatch("missing", None))
        if match.status == "known" and match.record is not None:
            return match
        saw_ambiguous = saw_ambiguous or match.status == "ambiguous"
    if saw_ambiguous:
        return CoordinateMatch("ambiguous", None)
    return CoordinateMatch("missing", None)


def _location_groups(
    records: Iterable[Mapping[str, Any]],
    *,
    require_safe_candidate: bool,
) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        if not _institution_location_keys(record) or not _valid_coordinates(record):
            continue
        if require_safe_candidate and not _candidate_location_is_safe(record):
            continue
        for key in _institution_location_keys(record):
            grouped.setdefault(key, []).append(dict(record))
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
                grouped.setdefault(f"name:{institution}", []).append(location)
    return grouped


def match_institutions_to_known_coordinates(
    public_map_records: Sequence[Mapping[str, Any]],
    candidate_map_records: Sequence[Mapping[str, Any]] = (),
    confirmed_location_records: Sequence[Mapping[str, Any]] = (),
    processed_cache_records: Sequence[Mapping[str, Any]] = (),
) -> Dict[str, CoordinateMatch]:
    confirmed_groups = _location_groups(
        (row for row in confirmed_location_records if _confirmed_location_is_usable(row)),
        require_safe_candidate=False,
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
    identity_cache: PaperIdentityCache | None = None,
) -> Dict[str, List[MutableMapping[str, Any]]]:
    index: Dict[str, List[MutableMapping[str, Any]]] = {}
    cache = identity_cache or PaperIdentityCache()
    for record in records:
        for key in cache.keys(record):
            index.setdefault(key, []).append(record)
    return index


def _matching_papers(
    record: Mapping[str, Any],
    index: Mapping[str, Sequence[MutableMapping[str, Any]]],
    identity_cache: PaperIdentityCache | None = None,
) -> List[MutableMapping[str, Any]]:
    seen = set()
    keys = (
        identity_cache.keys(record)
        if identity_cache is not None
        else normalize_paper_identity_keys(record)
    )
    for key in keys:
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


def _curated_paper_record(row: Mapping[str, Any], task: str) -> Dict[str, Any]:
    try:
        from .venue_audit import VenueAudit
        from .venues import read_venue_aliases
    except ImportError:
        from venue_audit import VenueAudit
        from venues import read_venue_aliases
    row = VenueAudit(read_venue_aliases()).effective(row)
    year = _parse_year(row.get("year"))
    doi = clean(row.get("doi"))
    links = resolve_public_links(row)
    arxiv_id = links["arxiv_id"]
    paper_url = links["formal_url"]
    openalex_url = links["openalex_url"]
    review_status = clean(row.get("review_status"))
    publication_type = row.get("publication_type") or normalize_publication_type(
        row.get("publication_type"), venue=row.get("venue"), venue_type=row.get("venue_type")
    )
    normalized_type = publication_type.casefold()
    paper_categories = categories_from_record(dict(row)) or ([
        "survey"
        if normalized_type in {"survey", "review", "systematic review"}
        else "dataset"
        if normalized_type == "dataset"
        else "benchmark"
        if normalized_type == "benchmark"
        else "method"
    ] if normalized_type != "book" else [])
    return {
        "paper_id": clean(row.get("paper_id")),
        "title": clean(row.get("title")),
        "in_scope": True,
        "year": year,
        "publication_year": year,
        "publication_date": "",
        "task": task,
        "paper_categories": paper_categories,
        "venue": clean(row.get("venue") or row.get("venue_name")),
        "venue_name": clean(row.get("venue_name") or row.get("venue")),
        "venue_id": clean(row.get("venue_id")),
        "venue_acronym": clean(row.get("venue_acronym")),
        "venue_type": clean(row.get("venue_type")),
        "venue_track": clean(row.get("venue_track")),
        "raw_venue": clean(row.get("raw_venue")),
        "publisher": "",
        "publication_type": publication_type,
        "venue_review_required": row.get("venue_review_required", False),
        "venue_review_reason": row.get("venue_review_reason", ""),
        "abstract": clean(row.get("abstract")),
        "abstract_source": clean(row.get("metadata_source")),
        "ai_summary": "",
        "doi": doi,
        "arxiv_id": arxiv_id,
        "arxiv_url": links["arxiv_url"],
        "arxiv_year": None,
        "has_arxiv_version": bool(arxiv_id),
        "paper_url": paper_url,
        "formal_url": paper_url,
        "primary_url": links["primary_url"],
        "landing_page_url": "",
        "openalex_url": openalex_url,
        "is_arxiv_preprint": bool(arxiv_id and not doi),
        "url": links["primary_url"],
        "authors": _parse_curated_authors(row.get("authors")),
        "source_database": clean(row.get("source_database")) or "curated",
        "metadata_source": clean(row.get("metadata_source")),
        "curation_status": normalize_curation_status(row.get("curation_status")),
        "review_status": review_status,
        "needs_review": review_status != "reviewed",
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
        task = normalize_task(row)
        if task is None:
            skipped_task += 1
            continue
        record = _curated_paper_record(row, task)
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
    curation_status = normalize_curation_status(curated.get("curation_status"))
    confirmed = curation_status in CONFIRMED_CURATION_STATUSES
    for field in CURATED_OVERRIDE_FIELDS:
        if field not in curated:
            continue
        value = curated.get(field)
        if confirmed and field in CURATED_AUTHORITATIVE_PUBLIC_FIELDS:
            existing[field] = value
        elif value not in (None, "", []) and (
            confirmed or existing.get(field) in (None, "", [])
        ):
            existing[field] = value
    normalized = normalize_book_record(existing)
    existing.clear()
    existing.update(normalized)
    links = resolve_public_links(existing)
    existing["arxiv_id"] = links["arxiv_id"]
    existing["arxiv_url"] = links["arxiv_url"]
    existing["has_arxiv_version"] = bool(links["arxiv_id"])
    existing["paper_url"] = links["formal_url"]
    existing["formal_url"] = links["formal_url"]
    existing["primary_url"] = links["primary_url"]
    existing["url"] = links["primary_url"]


def _mapping_public_fields(mapping: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "mapping_id": clean(mapping.get("mapping_id")),
        "institution_id": clean(mapping.get("institution_id"))
        or stable_institution_id(mapping.get("institution")),
        "location_id": clean(mapping.get("location_id")),
        "institution": clean(mapping.get("institution")),
        "institution_authors": _parse_people(
            mapping.get("institution_authors")
        ),
        "raw_affiliation": clean(mapping.get("raw_affiliation")),
        "mapping_status": clean(mapping.get("mapping_status")),
        "affiliation_order": _affiliation_order(mapping),
    }


def _affiliation_order(mapping: Mapping[str, Any]) -> int | None:
    value = clean(mapping.get("affiliation_order"))
    return int(value) if value.isdigit() and int(value) > 0 else None


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
    raw_affiliation = clean(mapping.get("raw_affiliation"))
    return f"Raw affiliation: {raw_affiliation}" if raw_affiliation else ""


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
    links = resolve_public_links(paper)
    paper_url = links["formal_url"]
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
        "paper_categories": categories_from_record(dict(paper)) or ["method"],
        "venue": clean(paper.get("venue") or paper.get("venue_name")),
        "venue_name": clean(paper.get("venue_name") or paper.get("venue")),
        "venue_id": clean(paper.get("venue_id")),
        "venue_acronym": clean(paper.get("venue_acronym")),
        "venue_type": clean(paper.get("venue_type")),
        "venue_track": clean(paper.get("venue_track")),
        "raw_venue": clean(paper.get("raw_venue")),
        "publication_type": normalize_publication_type(
            paper.get("publication_type"),
            venue=paper.get("venue") or paper.get("venue_name"),
            venue_type=paper.get("venue_type"),
        ),
        "abstract": clean(paper.get("abstract")),
        "abstract_source": clean(paper.get("abstract_source")),
        "doi": clean(paper.get("doi")),
        "arxiv_id": links["arxiv_id"],
        "arxiv_url": links["arxiv_url"],
        "has_arxiv_version": bool(
            clean(paper.get("arxiv_id")) or clean(paper.get("arxiv_url"))
        ),
        "paper_url": paper_url,
        "formal_url": paper_url,
        "primary_url": links["primary_url"],
        "openalex_url": links["openalex_url"],
        "url": links["primary_url"],
        "authors": _parse_people(paper.get("authors")),
        "institution": clean(mapping.get("institution")),
        "institution_id": clean(mapping.get("institution_id"))
        or stable_institution_id(mapping.get("institution")),
        "location_id": clean(location.get("location_id")),
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
        "curation_status": normalize_curation_status(paper.get("curation_status")),
        "mapping_id": clean(mapping.get("mapping_id")),
        "affiliation_order": _affiliation_order(mapping),
        "raw_affiliation": clean(mapping.get("raw_affiliation")),
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
    *,
    matching_mappings: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    """Return the paper-level source decision for affiliation evidence.

    Active mappings are accepted curation. Needs-review mappings are still
    candidates, so automatic evidence remains available until one is accepted.
    Excluded mapping history or an explicit paper state is durable evidence
    that an empty affiliation result was reviewed. General paper-metadata
    review is deliberately not treated as affiliation review.
    """
    if matching_mappings is None:
        matching_mappings = [
            mapping
            for mapping in mappings
            if _mapping_matches_paper(mapping, paper)
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
    *,
    source_backed: bool = False,
) -> None:
    record["affiliation_review_state"] = "unreviewed"
    record["institution_source"] = (
        "source_backed_preliminary" if source_backed else "automatic_fallback"
    )
    record["preliminary_affiliations"] = True
    note = (
        "Preliminary source-backed affiliation evidence; paper review pending."
        if source_backed
        else "Preliminary automatic affiliation evidence; not manually reviewed."
    )
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


def curated_affiliation_removal_reason(
    marker: Mapping[str, Any],
    matching_mappings: Sequence[Mapping[str, Any]],
) -> str:
    """Explain why a marker is outside the paper's effective curated state.

    This is paper-wide selection, not author-set supersession: a historical
    subset of an author group is not an additional legitimate affiliation.
    Candidate-only curation deliberately retains automatic fallback evidence.
    """
    if not matching_mappings:
        return ""
    state = affiliation_review_state(
        marker, (), matching_mappings=matching_mappings
    )
    if state == "unreviewed":
        return ""
    if state == "reviewed_empty":
        return "reviewed empty affiliations; no active curated mappings"
    eligible = [
        row for row in matching_mappings
        if clean(row.get("mapping_status")) == ACTIVE_MAPPING_STATUS
        or _supported_preliminary_mapping(row, marker)
    ]
    for mapping in eligible:
        institution_id = clean(mapping.get("institution_id")) or stable_institution_id(
            mapping.get("institution")
        )
        if (
            clean(marker.get("mapping_id")) == clean(mapping.get("mapping_id"))
            and clean(marker.get("institution_id")) == institution_id
            and normalized_author_set(marker.get("institution_authors"))
            == normalized_author_set(mapping.get("institution_authors"))
            and (not clean(mapping.get("location_id"))
                 or clean(marker.get("location_id")) == clean(mapping.get("location_id")))
        ):
            return ""
    # Public detail enrichment intentionally coalesces authors from separate
    # affiliation rows when they resolve to the same institution and site.
    # Accept that aggregate marker when its authors are exactly the union of
    # the active rows represented at that institution/location.
    marker_institution_id = clean(marker.get("institution_id"))
    marker_location_id = clean(marker.get("location_id"))
    coalesced = [
        mapping for mapping in eligible
        if (clean(mapping.get("institution_id")) or stable_institution_id(
            mapping.get("institution")
        )) == marker_institution_id
        and (not clean(mapping.get("location_id"))
             or clean(mapping.get("location_id")) == marker_location_id)
    ]
    coalesced_authors = normalized_author_set([
        author
        for mapping in coalesced
        for author in canonical_author_names(mapping.get("institution_authors"))
    ])
    if (
        coalesced
        and clean(marker.get("mapping_id")) in {
            clean(mapping.get("mapping_id")) for mapping in coalesced
        }
        and normalized_author_set(marker.get("institution_authors")) == coalesced_authors
    ):
        return ""
    return "outside effective active curated mappings: " + ", ".join(
        clean(row.get("mapping_id")) for row in eligible
    )


def enforce_affiliation_source_precedence(
    paper_records: Sequence[MutableMapping[str, Any]],
    map_records: List[Dict[str, Any]],
    mappings: Sequence[Mapping[str, Any]],
    curated_papers: Sequence[Mapping[str, Any]] = (),
    *,
    identity_cache: PaperIdentityCache | None = None,
) -> int:
    """Apply paper-level manual-first selection and return removed markers."""
    cache = identity_cache or PaperIdentityCache()
    mapping_index = PaperIdentityIndex(mappings, cache)
    marker_index = PaperIdentityIndex(map_records, cache)
    active_marker_ids = {id(marker) for marker in map_records}
    removed_marker_ids: set[int] = set()
    resolved_mapping_ids = {
        clean(record.get("mapping_id"))
        for record in map_records
        if clean(record.get("source_database")).casefold() == "curated"
        and clean(record.get("mapping_id"))
    }
    for paper in paper_records:
        matching_mappings = mapping_index.matches(paper)
        state = affiliation_review_state(
            paper,
            mappings,
            curated_papers,
            matching_mappings=matching_mappings,
        )
        paper["affiliation_review_state"] = state
        active_mapping_ids = {
            clean(mapping.get("mapping_id"))
            for mapping in matching_mappings
            if clean(mapping.get("mapping_status")) == ACTIVE_MAPPING_STATUS
            and clean(mapping.get("mapping_id"))
        }
        supported_preliminary_mapping_ids = {
            clean(mapping.get("mapping_id"))
            for mapping in matching_mappings
            if _supported_preliminary_mapping(mapping, paper)
            and clean(mapping.get("mapping_id"))
        }
        eligible_curated_marker_ids = (
            active_mapping_ids | supported_preliminary_mapping_ids
        )
        matching_markers = [
            marker
            for marker in marker_index.matches(paper)
            if id(marker) in active_marker_ids
        ]
        if state == "unreviewed":
            # New unreviewed papers may have explicit PDF affiliation evidence
            # while locations remain pending. Those sourced links control which
            # institutions may contribute geography, independently of paper
            # review: only curated markers with confirmed identities and
            # confirmed locations survive.
            supported_preliminary = [
                mapping for mapping in matching_mappings
                if _supported_preliminary_mapping(mapping, paper)
            ]
            if supported_preliminary:
                supported_mapping_ids = {
                    clean(mapping.get("mapping_id"))
                    for mapping in supported_preliminary
                }
                for marker in matching_markers:
                    if not (
                        clean(marker.get("source_database")).casefold() == "curated"
                        and clean(marker.get("mapping_id")) in supported_mapping_ids
                    ):
                        marker_id = id(marker)
                        active_marker_ids.discard(marker_id)
                        removed_marker_ids.add(marker_id)
                matching_markers = [
                    marker for marker in matching_markers
                    if id(marker) in active_marker_ids
                ]
            if (clean(paper.get("curation_status")) == "needs_review"
                    and matching_mappings):
                _recalculate_paper_details(
                    paper, map_records, mappings, resolved_mapping_ids,
                    matching_markers=matching_markers,
                    matching_mappings=_visible_affiliation_mappings(paper, matching_mappings),
                )
            _mark_preliminary_automatic_evidence(
                paper, source_backed=bool(supported_preliminary)
            )
            for marker in matching_markers:
                _mark_preliminary_automatic_evidence(
                    marker,
                    source_backed=(
                        clean(marker.get("source_database")).casefold()
                        == "curated"
                    ),
                )
            continue

        for marker in matching_markers:
            if (
                state == "curated"
                and clean(marker.get("source_database")).casefold() == "curated"
                and clean(marker.get("mapping_id")) in eligible_curated_marker_ids
                and not curated_affiliation_removal_reason(marker, matching_mappings)
            ):
                if clean(marker.get("mapping_id")) in supported_preliminary_mapping_ids:
                    _mark_preliminary_automatic_evidence(
                        marker, source_backed=True
                    )
                else:
                    marker["affiliation_review_state"] = "curated"
                    marker["institution_source"] = "curated"
                    marker["preliminary_affiliations"] = False
            else:
                marker_id = id(marker)
                active_marker_ids.discard(marker_id)
                removed_marker_ids.add(marker_id)
        remaining_markers = [
            marker
            for marker in marker_index.matches(paper)
            if id(marker) in active_marker_ids
        ]
        visible_mappings = _visible_affiliation_mappings(paper, matching_mappings)
        _recalculate_paper_details(
            paper,
            map_records,
            mappings,
            resolved_mapping_ids,
            matching_markers=remaining_markers,
            matching_mappings=visible_mappings,
        )
        paper["affiliation_review_state"] = state
        paper["institution_source"] = (
            "curated" if state == "curated" else "reviewed_empty"
        )
        paper["preliminary_affiliations"] = False
    removed = sum(
        id(marker) in removed_marker_ids for marker in map_records
    )
    map_records[:] = [
        marker for marker in map_records if id(marker) in active_marker_ids
    ]
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
    return identity, _preferred_institution_location_key(record)


def _queue_keys(record: Mapping[str, Any]) -> List[Tuple[str, str]]:
    """Return specific and fallback keys shared by mapping and review schemas."""
    identity, _ = _queue_key(record)
    location_keys = _institution_location_keys(record)
    return [(identity, key) for key in location_keys] or [(identity, "")]


def _indexed_review_row(
    row_index: Mapping[Tuple[str, str], Dict[str, str]],
    record: Mapping[str, Any],
) -> Dict[str, str] | None:
    return next(
        (row_index[key] for key in _queue_keys(record) if key in row_index),
        None,
    )


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
    row_index: Dict[Tuple[str, str], Dict[str, str]] | None = None,
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
        "evidence_source": "",
        "evidence_url": "",
        "suggested_city": "",
        "suggested_country": "",
        "review_status": (
            "ambiguous"
            if coordinate_status == "ambiguous"
            else "pending_review"
        ),
        "location_status": location_status,
        "coordinate_status": coordinate_status,
        "updated_at": now,
    }
    indexed_row = (
        _indexed_review_row(row_index, mapping)
        if row_index is not None
        else None
    )
    matching_rows = (
        [indexed_row]
        if indexed_row is not None
        else ([] if row_index is not None else rows)
    )
    for row in matching_rows:
        if row_index is None and not (
            set(_queue_keys(row)) & set(_queue_keys(mapping))
        ):
            continue
        row["institution_authors"] = _merged_people(
            row.get("institution_authors"), values["institution_authors"]
        )
        for field, value in values.items():
            if field == "institution_authors":
                continue
            if value:
                row[field] = value
        row["created_at"] = clean(row.get("created_at")) or now
        row["updated_at"] = now
        return "updated"
    row = {**values, "created_at": now}
    rows.append(row)
    if row_index is not None:
        for row_key in _queue_keys(row):
            row_index.setdefault(row_key, row)
    return "created"


def _mark_location_known(
    rows: List[Dict[str, str]],
    mapping: Mapping[str, Any],
    *,
    row_index: Dict[Tuple[str, str], Dict[str, str]] | None = None,
) -> bool:
    key = _queue_key(mapping)
    indexed_row = (
        _indexed_review_row(row_index, mapping)
        if row_index is not None
        else None
    )
    matching_rows = (
        [indexed_row]
        if indexed_row is not None
        else ([] if row_index is not None else rows)
    )
    for row in matching_rows:
        if row_index is not None or (
            set(_queue_keys(row)) & set(_queue_keys(mapping))
        ):
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
    institution_records: Sequence[Mapping[str, Any]] = (),
    *,
    identity_cache: PaperIdentityCache | None = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    cache = identity_cache or PaperIdentityCache()
    paper_index = _paper_index(paper_records, cache)
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
    skipped_unresolved_identity = 0
    skipped_unresolved_location = 0
    preliminary_markers_created = 0
    map_eligible_preliminary_institution_ids: set[str] = set()
    resolved_mapping_ids = set()
    matched_paper_mappings = 0
    emitted_marker_keys = set()
    active_mapping_marker_diagnostics: List[Dict[str, Any]] = []
    confirmed_aliases = {
        normalize_institution(row.get("alias_name")): {
            "institution": clean(row.get("canonical_institution_name")),
            "institution_id": clean(row.get("institution_id")),
        }
        for row in institution_aliases
        if clean(row.get("review_status")) == "confirmed"
        and clean(row.get("alias_name"))
        and clean(row.get("canonical_institution_name"))
    }
    confirmed_location_keys = {
        key
        for row in confirmed_location_records
        for key in _institution_location_keys(row)
        if _confirmed_location_is_usable(row)
    }
    explicitly_confirmed_location_keys = {
        key
        for row in confirmed_location_records
        if clean(row.get("coordinate_status")).casefold()
        in {"known", "confirmed"}
        and _valid_coordinates(row)
        for key in _institution_location_keys(row)
    }
    confirmed_institution_ids = _confirmed_institution_ids(institution_records)
    review_status_by_key = {
        key: clean(row.get("review_status")) or "pending_review"
        for row in review_rows
        for key in _queue_keys(row)
    }
    review_row_by_key: Dict[Tuple[str, str], Dict[str, str]] = {}
    for row in review_rows:
        for key in _queue_keys(row):
            review_row_by_key.setdefault(key, row)
    non_exportable_statuses = {
        "pending_review",
        "ambiguous",
        "ignore",
        "excluded",
    }

    for mapping in mappings:
        mapping_status = clean(mapping.get("mapping_status"))
        if mapping_status not in {ACTIVE_MAPPING_STATUS, "needs_review"}:
            skipped_status += 1
            continue
        papers = _matching_papers(mapping, paper_index, cache)
        if not papers:
            skipped_paper += 1
            active_mapping_marker_diagnostics.append({
                "paper_id": clean(mapping.get("paper_id")),
                "canonical_paper_identity": "; ".join(cache.keys(mapping)),
                "title": clean(mapping.get("title")),
                "mapping_id": clean(mapping.get("mapping_id")),
                "source_institution_id": clean(mapping.get("institution_id")),
                "canonical_institution_id": clean(mapping.get("institution_id")),
                "author_ids": clean(mapping.get("author_order")),
                "author_names": clean(mapping.get("institution_authors")),
                "location_status": "unknown",
                "coordinates": "",
                "final_drop_reason": "paper_not_found",
            })
            continue
        paper = papers[0]
        preliminary = _supported_preliminary_mapping(mapping, paper)
        if mapping_status == "needs_review" and not preliminary:
            skipped_status += 1
            continue
        if record_is_excluded(paper, exclusion_index):
            skipped_paper += 1
            active_mapping_marker_diagnostics.append({
                "paper_id": clean(mapping.get("paper_id")),
                "canonical_paper_identity": "; ".join(cache.keys(paper)),
                "title": clean(mapping.get("title") or paper.get("title")),
                "mapping_id": clean(mapping.get("mapping_id")),
                "source_institution_id": clean(mapping.get("institution_id")),
                "canonical_institution_id": clean(mapping.get("institution_id")),
                "author_ids": clean(mapping.get("author_order")),
                "author_names": clean(mapping.get("institution_authors")),
                "location_status": "unknown",
                "coordinates": "",
                "final_drop_reason": "paper_excluded",
            })
            continue
        matched_paper_mappings += 1
        institution_id = clean(mapping.get("institution_id"))
        if institution_records and institution_id not in confirmed_institution_ids:
            skipped_unresolved_identity += 1
            active_mapping_marker_diagnostics.append({
                "paper_id": clean(mapping.get("paper_id")),
                "canonical_paper_identity": "; ".join(cache.keys(paper)),
                "title": clean(mapping.get("title") or paper.get("title")),
                "mapping_id": clean(mapping.get("mapping_id")),
                "source_institution_id": institution_id,
                "canonical_institution_id": institution_id,
                "author_ids": clean(mapping.get("author_order")),
                "author_names": clean(mapping.get("institution_authors")),
                "location_status": "unknown",
                "coordinates": "",
                "final_drop_reason": "institution_identity_unresolved",
            })
            continue
        if preliminary and not institution_records:
            # A populated ID is not itself proof that the canonical registry
            # record is resolved.
            skipped_unresolved_identity += 1
            continue
        raw_institution_key = normalize_institution(mapping.get("institution"))
        canonical_alias = confirmed_aliases.get(raw_institution_key) or {}
        if clean(mapping.get("institution_id")):
            # An explicit active mapping is already an identity decision.
            # Name aliases and coordinate evidence must not replace that ID.
            canonical_alias = {}
        canonical_institution = clean(canonical_alias.get("institution"))
        canonical_institution_id = clean(canonical_alias.get("institution_id"))
        lookup_mapping = dict(mapping)
        if canonical_institution:
            lookup_mapping["institution"] = canonical_institution
        if canonical_institution_id:
            lookup_mapping["institution_id"] = canonical_institution_id
        institution_keys = _mapping_location_lookup_keys(lookup_mapping)
        institution_key = institution_keys[0] if institution_keys else ""
        queue_status = (
            "alias_of_confirmed"
            if canonical_institution
            else next(
                (
                    review_status_by_key[key]
                    for key in _queue_keys(mapping)
                    if key in review_status_by_key
                ),
                None,
            )
        )
        if queue_status in {"excluded", "ignore"}:
            skipped_status += 1
            active_mapping_marker_diagnostics.append({
                "paper_id": clean(mapping.get("paper_id")),
                "canonical_paper_identity": "; ".join(cache.keys(paper)),
                "title": clean(mapping.get("title") or paper.get("title")),
                "mapping_id": clean(mapping.get("mapping_id")),
                "source_institution_id": clean(mapping.get("institution_id")),
                "canonical_institution_id": canonical_institution_id or clean(mapping.get("institution_id")),
                "author_ids": clean(mapping.get("author_order")),
                "author_names": clean(mapping.get("institution_authors")),
                "location_status": queue_status,
                "coordinates": "",
                "final_drop_reason": "location_review_excluded",
            })
            continue
        match = _coordinate_match_for_keys(
            institution_keys,
            locations,
            (
                explicitly_confirmed_location_keys
                if preliminary
                else confirmed_location_keys
            ),
        )
        if queue_status in non_exportable_statuses and match.status != "known":
            skipped_status += 1
            skipped_unresolved_location += int(preliminary)
            active_mapping_marker_diagnostics.append({
                "paper_id": clean(mapping.get("paper_id")),
                "canonical_paper_identity": "; ".join(cache.keys(paper)),
                "title": clean(mapping.get("title") or paper.get("title")),
                "mapping_id": clean(mapping.get("mapping_id")),
                "source_institution_id": clean(mapping.get("institution_id")),
                "canonical_institution_id": canonical_institution_id or clean(mapping.get("institution_id")),
                "author_ids": clean(mapping.get("author_order")),
                "author_names": clean(mapping.get("institution_authors")),
                "location_status": queue_status,
                "coordinates": "",
                "final_drop_reason": "location_review_not_exportable",
            })
            continue
        if match.status != "known" or match.record is None:
            coordinate_status = (
                "ambiguous" if match.status == "ambiguous" else "missing"
            )
            result = (
                "unchanged"
                if preliminary
                else _upsert_location_review(
                    review_rows,
                    mapping,
                    coordinate_status=coordinate_status,
                    row_index=review_row_by_key,
                )
            )
            queue_created += int(result == "created")
            queue_updated += int(result == "updated")
            missing += int(coordinate_status == "missing")
            ambiguous += int(coordinate_status == "ambiguous")
            skipped_unresolved_location += int(preliminary)
            active_mapping_marker_diagnostics.append({
                "paper_id": clean(mapping.get("paper_id")),
                "canonical_paper_identity": "; ".join(cache.keys(paper)),
                "title": clean(mapping.get("title") or paper.get("title")),
                "mapping_id": clean(mapping.get("mapping_id")),
                "source_institution_id": clean(mapping.get("institution_id")),
                "canonical_institution_id": canonical_institution_id or clean(mapping.get("institution_id")),
                "author_ids": clean(mapping.get("author_order")),
                "author_names": clean(mapping.get("institution_authors")),
                "location_status": coordinate_status,
                "coordinates": "",
                "final_drop_reason": f"{coordinate_status}_coordinates",
            })
            continue
        if not preliminary:
            queue_known += int(
                _mark_location_known(
                    review_rows, mapping, row_index=review_row_by_key
                )
            )
        resolved_mapping_ids.add(clean(mapping.get("mapping_id")))
        if clean(paper.get("task")) not in PUBLIC_MAP_TASKS:
            skipped_task += 1
            active_mapping_marker_diagnostics.append({
                "paper_id": clean(mapping.get("paper_id")),
                "canonical_paper_identity": "; ".join(cache.keys(paper)),
                "title": clean(mapping.get("title") or paper.get("title")),
                "mapping_id": clean(mapping.get("mapping_id")),
                "source_institution_id": clean(mapping.get("institution_id")),
                "canonical_institution_id": canonical_institution_id or clean(mapping.get("institution_id")) or clean(match.record.get("institution_id")),
                "author_ids": clean(mapping.get("author_order")),
                "author_names": clean(mapping.get("institution_authors")),
                "location_status": "known",
                "coordinates": f"{clean(match.record.get('lat') or match.record.get('latitude'))},{clean(match.record.get('lon') or match.record.get('longitude'))}",
                "final_drop_reason": f"non_public_task:{clean(paper.get('task'))}",
            })
            continue
        export_mapping = dict(mapping)
        if canonical_institution:
            export_mapping["institution"] = canonical_institution
        if canonical_institution_id:
            export_mapping["institution_id"] = canonical_institution_id
        elif not clean(mapping.get("institution_id")) and clean(match.record.get("institution_id")):
            export_mapping["institution_id"] = clean(match.record.get("institution_id"))
        if not clean(mapping.get("institution_id")) and not canonical_institution and clean(match.record.get("institution")):
            export_mapping["institution"] = clean(match.record.get("institution"))
        marker_key = (
            next(iter(cache.keys(paper)), ""),
            _preferred_institution_location_key(export_mapping),
        )
        if marker_key in emitted_marker_keys:
            active_mapping_marker_diagnostics.append({
                "paper_id": clean(mapping.get("paper_id")),
                "canonical_paper_identity": "; ".join(cache.keys(paper)),
                "title": clean(mapping.get("title") or paper.get("title")),
                "mapping_id": clean(mapping.get("mapping_id")),
                "source_institution_id": clean(mapping.get("institution_id")),
                "canonical_institution_id": clean(export_mapping.get("institution_id")),
                "author_ids": clean(mapping.get("author_order")),
                "author_names": clean(mapping.get("institution_authors")),
                "location_status": "known",
                "coordinates": f"{clean(match.record.get('lat') or match.record.get('latitude'))},{clean(match.record.get('lon') or match.record.get('longitude'))}",
                "final_drop_reason": "duplicate_paper_institution_marker",
            })
            continue
        emitted_marker_keys.add(marker_key)
        markers.append(_curated_marker(paper, export_mapping, match.record))
        if preliminary:
            markers[-1]["mapping_status"] = "needs_review"
            markers[-1]["institution_identity_status"] = "confirmed"
            markers[-1]["institution_location_status"] = "confirmed"
            markers[-1]["preliminary_affiliations"] = True
            preliminary_markers_created += 1
            map_eligible_preliminary_institution_ids.add(
                clean(export_mapping.get("institution_id"))
            )

    return markers, {
        "curated_mappings_loaded": len(mappings),
        "curated_markers_created": len(markers),
        "curated_mappings_missing_coordinates": missing,
        "curated_mappings_ambiguous_coordinates": ambiguous,
        "curated_mappings_skipped_status": skipped_status,
        "curated_mappings_skipped_paper": skipped_paper,
        "curated_mappings_skipped_task": skipped_task,
        "curated_mappings_unresolved_identity_excluded": skipped_unresolved_identity,
        "curated_mappings_unresolved_location_excluded": skipped_unresolved_location,
        "preliminary_markers_created": preliminary_markers_created,
        "confirmed_institution_records_newly_map_eligible": len(
            map_eligible_preliminary_institution_ids
        ),
        "curated_mappings_matched_papers": matched_paper_mappings,
        "location_review_rows_created": queue_created,
        "location_review_rows_updated": queue_updated,
        "location_review_rows_marked_known": queue_known,
        "resolved_mapping_ids": resolved_mapping_ids,
        "active_mapping_marker_diagnostics": active_mapping_marker_diagnostics,
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


def _visible_affiliation_mappings(paper, mappings):
    """Keep sourced pending affiliations reviewable only on unreviewed papers."""
    unreviewed = clean(paper.get("curation_status")) == "needs_review"
    return [mapping for mapping in mappings
            if clean(mapping.get("mapping_status")) == ACTIVE_MAPPING_STATUS
            or (unreviewed and clean(mapping.get("mapping_status")) == "needs_review"
                and clean(mapping.get("raw_affiliation"))
                and clean(mapping.get("provenance_source")))]


def _recalculate_paper_details(
    paper: MutableMapping[str, Any],
    map_records: Sequence[Mapping[str, Any]],
    mappings: Sequence[Mapping[str, Any]],
    resolved_mapping_ids: set[str],
    *,
    matching_markers: Sequence[Mapping[str, Any]] | None = None,
    matching_mappings: Sequence[Mapping[str, Any]] | None = None,
) -> None:
    markers = list(matching_markers) if matching_markers is not None else [
        marker for marker in map_records if _mapping_matches_paper(marker, paper)
    ]
    visible_mappings = (
        list(matching_mappings)
        if matching_mappings is not None
        else [
            mapping
            for mapping in mappings
            if clean(mapping.get("mapping_status")) == ACTIVE_MAPPING_STATUS
            and _mapping_matches_paper(mapping, paper)
        ]
    )
    visible_mappings = [
        mapping for _index, mapping in sorted(
            enumerate(visible_mappings),
            key=lambda item: (
                _affiliation_order(item[1]) is None,
                _affiliation_order(item[1]) or item[0] + 1,
                item[0],
            ),
        )
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
        institution_id = clean(mapping.get("institution_id")) or stable_institution_id(institution)
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
                "mapping_fallback": clean(mapping.get("mapping_status")) == "needs_review",
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
                    "fallback": clean(mapping.get("mapping_status")) == "needs_review",
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
    paper["aggregated_institutions"] = []
    aggregated_keys: set[str] = set()
    for record in [*affiliation_records, *markers]:
        institution = clean(record.get("institution"))
        key = normalize_institution(institution)
        if institution and key not in aggregated_keys:
            aggregated_keys.add(key)
            paper["aggregated_institutions"].append(institution)
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
    institution_records: Sequence[Mapping[str, Any]] = (),
) -> Tuple[
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, str]],
    Dict[str, Any],
]:
    papers = [dict(record) for record in paper_records]
    location_policy = ReviewedRelationshipResolver([], locations=confirmed_location_records)
    maps = [dict(record) for record in map_records
            if not location_policy.location_is_rejected(record)]
    candidate_map_records = [record for record in candidate_map_records
                             if not location_policy.location_is_rejected(record)]
    reviews = [dict(row) for row in location_review_rows]
    curated_records, paper_summary = build_curated_paper_preview_records(
        curated_papers, exclusion_rows
    )
    paper_index = _paper_index(papers)
    map_index = _paper_index(maps)
    curated_source_index = _paper_index(list(curated_papers))
    added = 0
    merged = 0
    for curated in curated_records:
        curated = normalize_book_record(curated)
        matches = _matching_papers(curated, paper_index)
        if matches:
            target = matches[0]
            original = next(iter(_matching_papers(curated, curated_source_index)), {})
            if not original.get("venue_track") and target.get("venue_id") == curated.get("venue_id") and target.get("venue_track"):
                curated = {**curated, "venue_track": target["venue_track"]}
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

    identity_cache = PaperIdentityCache()

    # Source selection is paper-wide. Remove every automatic marker before
    # creating replacements so a different institution or missing coordinate
    # cannot leave stale automatic evidence behind.
    replaced_markers = enforce_affiliation_source_precedence(
        papers,
        maps,
        mappings,
        curated_papers,
        identity_cache=identity_cache,
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
        institution_records,
        identity_cache=identity_cache,
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
        papers,
        maps,
        mappings,
        curated_papers,
        identity_cache=identity_cache,
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
