#!/usr/bin/env python3
"""Local confirmed institution-location curation operations."""

from __future__ import annotations

import csv
import difflib
import hashlib
import math
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence

try:
    from .curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        INSTITUTION_AUDIT_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        ALLOWED_INSTITUTION_REVIEW_STATUSES,
    )
    from .curated_institutions import DEFAULT_INSTITUTIONS_PATH, load_institutions
    from .country_normalization import (
        canonical_english_location_fields,
        country_code_for_name,
    )
    from .paper_exclusions import (
        all_identity_keys, build_active_exclusion_index, record_is_excluded,
    )
except ImportError:
    from curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        INSTITUTION_AUDIT_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        ALLOWED_INSTITUTION_REVIEW_STATUSES,
    )
    from curated_institutions import DEFAULT_INSTITUTIONS_PATH, load_institutions
    from country_normalization import (
        canonical_english_location_fields,
        country_code_for_name,
    )
    from paper_exclusions import (
        all_identity_keys, build_active_exclusion_index, record_is_excluded,
    )


DEFAULT_LOCATION_REVIEW_PATH = CURATED_DATA_DIR / "institution_location_review.csv"
DEFAULT_INSTITUTION_LOCATIONS_PATH = CURATED_DATA_DIR / "institution_locations.csv"
DEFAULT_INSTITUTION_ALIASES_PATH = CURATED_DATA_DIR / "institution_aliases.csv"
DEFAULT_AUTHOR_INSTITUTION_MAPPINGS_PATH = (
    CURATED_DATA_DIR / "author_institution_mappings.csv"
)
DEFAULT_INSTITUTION_AUDIT_PATH = CURATED_DATA_DIR / "institution_audit_log.csv"
COUNTRY_CODE_PATTERN = re.compile(r"[A-Z]{2}")


class CuratedLocationError(RuntimeError):
    """An expected location validation or storage error."""

    def __init__(
        self,
        message: str,
        *,
        field: str = "",
        error_code: str = "invalid_location",
        submitted_institution_id: str = "",
        current_institution_id: str = "",
    ):
        self.field = field
        self.error_code = error_code
        self.submitted_institution_id = submitted_institution_id
        self.current_institution_id = current_institution_id
        super().__init__(message)


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_institution_name(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalize_candidate_name(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).casefold()
    text = "".join(
        character for character in text if not unicodedata.combining(character)
    )
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


INSTITUTION_ACRONYM_STOPWORDS = {
    "and", "at", "de", "del", "der", "di", "for", "of", "the", "und", "universite",
}
INSTITUTION_SUBUNIT_TERMS = {
    "center", "centre", "clinic", "department", "faculty", "hospital", "institute",
    "laboratory", "lab", "school",
}


def institution_acronym(value: Any) -> str:
    words = normalize_candidate_name(value).split()
    return "".join(
        word[0] for word in words
        if word and word not in INSTITUTION_ACRONYM_STOPWORDS
    )


def institution_candidate_evidence(
    candidate_name: Any,
    canonical_name: Any,
) -> tuple[float, str]:
    """Return conservative review evidence; never a merge decision."""
    candidate = normalize_candidate_name(candidate_name)
    canonical = normalize_candidate_name(canonical_name)
    if not candidate or not canonical or candidate == canonical:
        return 0.0, ""
    candidate_acronym = institution_acronym(candidate_name)
    canonical_acronym = institution_acronym(canonical_name)
    if (
        len(candidate.replace(" ", "")) <= 12
        and candidate.replace(" ", "") == canonical_acronym
    ) or (
        len(canonical.replace(" ", "")) <= 12
        and canonical.replace(" ", "") == candidate_acronym
    ):
        return 1.0, "abbreviation_full_name"
    candidate_words = set(candidate.split())
    canonical_words = set(canonical.split())
    if (candidate in canonical or canonical in candidate) and (
        (candidate_words | canonical_words) & INSTITUTION_SUBUNIT_TERMS
    ):
        return 0.9, "parent_subunit_variant"
    overlap = len(candidate_words & canonical_words) / max(
        len(candidate_words | canonical_words), 1
    )
    similarity = difflib.SequenceMatcher(None, candidate, canonical).ratio()
    if overlap >= 0.6 and similarity >= 0.72:
        return round(max(overlap, similarity), 3), "near_duplicate_name"
    return 0.0, ""


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


def is_confirmed_location(row: Mapping[str, Any]) -> bool:
    """Candidate coordinates remain stored but are not confirmed choices."""
    if clean(row.get("coordinate_status")) not in {"known", "confirmed"}:
        return False
    try:
        validate_coordinates(row.get("lat"), row.get("lon"))
    except CuratedLocationError:
        return False
    return True


def load_institution_aliases(
    path: Path = DEFAULT_INSTITUTION_ALIASES_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, INSTITUTION_ALIAS_COLUMNS)


def normalized_location_key(row: Mapping[str, Any]) -> tuple[str, ...]:
    """Return the conservative exact-equivalence key for one confirmed location."""
    try:
        latitude = format(float(clean(row.get("lat"))), ".10g")
        longitude = format(float(clean(row.get("lon"))), ".10g")
    except ValueError:
        latitude = clean(row.get("lat"))
        longitude = clean(row.get("lon"))
    country = clean(row.get("country_code")).upper() or normalize_candidate_name(
        row.get("country")
    )
    return (
        clean(row.get("institution_id")),
        normalize_candidate_name(row.get("city")),
        normalize_candidate_name(row.get("region")),
        country,
        latitude,
        longitude,
    )


def location_id_redirects(
    audit_path: Path = DEFAULT_INSTITUTION_AUDIT_PATH,
) -> Dict[str, str]:
    redirects = {}
    for row in _read_csv(audit_path, INSTITUTION_AUDIT_COLUMNS):
        if clean(row.get("action")) != "location_merge":
            continue
        source = clean(row.get("previous_location_id"))
        target = clean(row.get("location_id"))
        if source and target and source != target:
            redirects[source] = target
    return redirects


def resolve_location_id(value: Any, redirects: Mapping[str, str]) -> str:
    identifier = clean(value)
    seen = set()
    while identifier in redirects and identifier not in seen:
        seen.add(identifier)
        identifier = clean(redirects[identifier])
    return identifier


def consolidate_exact_confirmed_locations(
    *,
    locations_path: Path = DEFAULT_INSTITUTION_LOCATIONS_PATH,
    mappings_path: Path = DEFAULT_AUTHOR_INSTITUTION_MAPPINGS_PATH,
    institution_audit_path: Path = DEFAULT_INSTITUTION_AUDIT_PATH,
    write: bool = False,
    institution_id: Any = "",
) -> Dict[str, Any]:
    """Consolidate only byte-normalized physical-location equivalents atomically."""
    locations = load_confirmed_locations(locations_path)
    mappings = _read_csv(mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
    audits = _read_csv(institution_audit_path, INSTITUTION_AUDIT_COLUMNS)
    scope = clean(institution_id)
    usage = Counter(clean(row.get("location_id")) for row in mappings)
    groups: Dict[tuple[str, ...], List[Dict[str, str]]] = defaultdict(list)
    for row in locations:
        if scope and clean(row.get("institution_id")) != scope:
            continue
        if clean(row.get("coordinate_status")) != "known":
            continue
        key = normalized_location_key(row)
        if key[0] and key[1] and key[3] and key[4] and key[5]:
            groups[key].append(row)

    existing_redirects = location_id_redirects(institution_audit_path)
    redirects: Dict[str, str] = {}
    findings = []
    for key, equivalent in sorted(groups.items()):
        if len(equivalent) < 2:
            continue
        survivor = min(
            equivalent,
            key=lambda row: (
                -usage[clean(row.get("location_id"))],
                clean(row.get("created_at")) or "9999",
                clean(row.get("location_id")),
            ),
        )
        target_id = clean(survivor.get("location_id"))
        for duplicate in equivalent:
            source_id = clean(duplicate.get("location_id"))
            if source_id == target_id:
                continue
            redirects[source_id] = target_id
            findings.append({
                "action": "location_merged",
                "institution_id": key[0],
                "institution": clean(survivor.get("institution")),
                "source_location_id": source_id,
                "target_location_id": target_id,
                "city": clean(survivor.get("city")),
                "region": clean(survivor.get("region")),
                "country": clean(survivor.get("country")),
                "lat": clean(survivor.get("lat")),
                "lon": clean(survivor.get("lon")),
                "status": "merged" if write else "would_merge",
            })

    if not write or not redirects:
        return {"findings": findings, "redirects": {**existing_redirects, **redirects}}

    now = _timestamp()
    survivors = {target for target in redirects.values()}
    location_by_id = {
        clean(row.get("location_id")): row for row in locations
        if clean(row.get("location_id")) in survivors
    }
    for mapping in mappings:
        source_id = clean(mapping.get("location_id"))
        if source_id not in redirects:
            continue
        target_id = redirects[source_id]
        target = location_by_id[target_id]
        mapping.update({
            "location_id": target_id,
            "institution_city": clean(target.get("city")),
            "institution_country": clean(target.get("country")),
            "institution_latitude": clean(target.get("lat")),
            "institution_longitude": clean(target.get("lon")),
            "updated_at": now,
        })
    for audit in audits:
        current_id = clean(audit.get("location_id"))
        if current_id in redirects:
            audit["location_id"] = redirects[current_id]
    known_audits = {
        (clean(row.get("previous_location_id")), clean(row.get("location_id")))
        for row in audits if clean(row.get("action")) == "location_merge"
    }
    for source_id, target_id in redirects.items():
        if (source_id, target_id) in known_audits:
            continue
        target = location_by_id[target_id]
        digest = hashlib.sha256(f"{source_id}|{target_id}".encode()).hexdigest()[:20]
        affected = usage[source_id]
        audits.append({
            "audit_id": f"institution-audit:{digest}",
            "action": "location_merge",
            "institution_id": clean(target.get("institution_id")),
            "previous_location_id": source_id,
            "location_id": target_id,
            "affected_papers": str(affected),
            "affected_mappings": str(affected),
            "affected_markers": str(affected),
            "confirmation_text": "Exact normalized city, region, country, latitude, and longitude equivalence.",
            "review_note": "Automatic exact-equivalent confirmed-location consolidation.",
            "created_at": now,
            "created_by": "institution-location-audit",
        })
    locations = [
        row for row in locations
        if clean(row.get("location_id")) not in redirects
    ]
    snapshots = {
        path: path.read_bytes() if path.exists() else None
        for path in (locations_path, mappings_path, institution_audit_path)
    }
    try:
        save_confirmed_locations(locations, locations_path)
        _write_csv_atomic(mappings, mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
        _write_csv_atomic(audits, institution_audit_path, INSTITUTION_AUDIT_COLUMNS)
    except Exception:
        for path, content in snapshots.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise
    return {"findings": findings, "redirects": {**existing_redirects, **redirects}}


def save_institution_aliases(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_INSTITUTION_ALIASES_PATH,
) -> None:
    _write_csv_atomic(rows, path, INSTITUTION_ALIAS_COLUMNS)


def save_confirmed_locations(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_INSTITUTION_LOCATIONS_PATH,
) -> None:
    normalized_rows = []
    for row in rows:
        normalized_rows.append({
            **row,
            **canonical_english_location_fields({
                field: row.get(field)
                for field in ("city", "region", "country", "country_code")
            }),
        })
    _write_csv_atomic(normalized_rows, path, INSTITUTION_LOCATION_COLUMNS)


def save_location_review_queue(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> None:
    for row in rows:
        if not clean(row.get("institution_id")):
            raise CuratedLocationError(
                "location review rows require a canonical institution_id"
            )
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


def location_id_for(
    institution: Any,
    *,
    institution_id: Any = "",
    city: Any = "",
    region: Any = "",
    country: Any = "",
) -> str:
    """Return a stable ID for one institution-location relationship."""
    identity = "|".join((
        clean(institution_id).casefold()
        or normalize_institution_name(institution),
        clean(city).casefold(),
        clean(region).casefold(),
        clean(country).casefold(),
    ))
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
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


def _confirmed_location_fields(
    draft: Mapping[str, Any],
    *,
    created_by: str,
    normalized_institution: str,
) -> Dict[str, str]:
    obsolete = {
        "coordinate_source", "coordinate_source_url",
        "coordinate_review_note", "review_note",
    } & set(draft)
    if obsolete:
        raise CuratedLocationError(
            f"unsupported location field: {sorted(obsolete)[0]}"
        )
    institution = clean(
        draft.get("confirmed_institution") or draft.get("institution")
    )
    if not institution:
        raise CuratedLocationError("confirmed_institution is required")
    normalized = normalize_institution_name(normalized_institution)
    if not normalized:
        raise CuratedLocationError("confirmed_institution is invalid")
    geographic = canonical_english_location_fields({
        "city": draft.get("confirmed_city") or draft.get("city"),
        "region": draft.get("confirmed_region") or draft.get("region"),
        "country": draft.get("confirmed_country") or draft.get("country"),
        "country_code": draft.get("confirmed_country_code") or draft.get("country_code"),
    })
    country = geographic["country"]
    country_code = validate_country_code(
        geographic.get("country_code")
        or country_code_for_name(country)
    )
    latitude, longitude = validate_coordinates(
        draft.get("confirmed_lat") if "confirmed_lat" in draft else draft.get("lat"),
        draft.get("confirmed_lon") if "confirmed_lon" in draft else draft.get("lon"),
    )
    city = geographic["city"]
    if not city or not country:
        raise CuratedLocationError(
            "confirmed city and country are required"
        )
    return {
        "location_id": location_id_for(
            institution,
            institution_id=draft.get("institution_id"),
            city=city,
            region=geographic["region"],
            country=country,
        ),
        "institution_id": clean(draft.get("institution_id")),
        "institution": institution,
        "normalized_institution": normalized,
        "city": city,
        "region": geographic["region"],
        "country": country,
        "country_code": country_code,
        "lat": latitude,
        "lon": longitude,
        "coordinate_status": "known",
        "created_by": clean(created_by) or "local-admin",
    }


def create_or_update_confirmed_location(
    queue_id: Any,
    draft: Mapping[str, Any],
    *,
    locations_path: Path = DEFAULT_INSTITUTION_LOCATIONS_PATH,
    review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    mappings_path: Path = DEFAULT_AUTHOR_INSTITUTION_MAPPINGS_PATH,
    aliases_path: Path = DEFAULT_INSTITUTION_ALIASES_PATH,
    institution_audit_path: Path = DEFAULT_INSTITUTION_AUDIT_PATH,
    created_by: str = "local-admin",
) -> Dict[str, Any]:
    review_rows = load_location_review_queue(review_path)
    review_index = _find_queue_row(review_rows, queue_id)
    queue_row = review_rows[review_index]
    bound_institution_id = clean(queue_row.get("institution_id"))
    if not bound_institution_id:
        raise CuratedLocationError("location review row is not bound to an institution_id")
    institutions = load_institutions(institutions_path)
    aliases = load_institution_aliases(aliases_path)
    audits = _read_csv(institution_audit_path, INSTITUTION_AUDIT_COLUMNS)

    redirects = {
        clean(row.get("previous_institution_id")): clean(row.get("institution_id"))
        for row in audits
        if clean(row.get("action")) == "merge"
        and clean(row.get("previous_institution_id"))
        and clean(row.get("institution_id"))
    }
    alias_ids = {
        clean(row.get("alias_id")): clean(row.get("institution_id"))
        for row in aliases
        if clean(row.get("review_status")) == "confirmed"
        and clean(row.get("alias_id"))
        and clean(row.get("institution_id"))
    }

    def canonical_id(value: Any) -> str:
        identifier = alias_ids.get(clean(value), clean(value))
        seen = set()
        while identifier in redirects and identifier not in seen:
            seen.add(identifier)
            identifier = redirects[identifier]
        return identifier

    # Older review rows can retain the pre-normalization institution ID while
    # their active paper mapping already points at the current canonical
    # identity. Resolve that relationship before comparing submitted IDs.
    mapping_rows = _read_csv(mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
    paper_id = clean(queue_row.get("related_paper_id"))
    mapping_ids = {
        clean(row.get("institution_id"))
        for row in mapping_rows
        if clean(row.get("paper_id")) == paper_id
        and clean(row.get("mapping_status")) in {"active", "needs_review"}
        and normalize_institution_name(row.get("institution"))
        == normalize_institution_name(queue_row.get("institution"))
        and clean(row.get("institution_id"))
    }
    current_institution_id = canonical_id(
        next(iter(mapping_ids)) if len(mapping_ids) == 1 else bound_institution_id
    )
    entity = next(
        (
            row for row in institutions
            if clean(row.get("institution_id")) == current_institution_id
        ),
        None,
    )
    if entity is None:
        raise CuratedLocationError("location review institution_id is unknown")
    requested_id = clean(draft.get("institution_id"))
    submitted_canonical_id = canonical_id(requested_id)
    if requested_id and submitted_canonical_id != current_institution_id:
        raise CuratedLocationError(
            "location confirmation cannot change institution identity; use the identity-change workflow",
            field="institution_id",
            error_code="institution_identity_change_not_allowed",
            submitted_institution_id=requested_id,
            current_institution_id=current_institution_id,
        )
    canonical_name = clean(entity.get("canonical_name"))
    location_draft = {
        **draft,
        "institution_id": current_institution_id,
        "confirmed_institution": canonical_name,
    }
    queue_normalized = normalize_institution_name(canonical_name)
    values = _confirmed_location_fields(
        location_draft,
        created_by=created_by,
        normalized_institution=queue_normalized,
    )

    # Repair exact duplicate rows before matching the user's selection.  A
    # legacy selected ID remains usable through the durable location redirect.
    consolidate_exact_confirmed_locations(
        locations_path=locations_path,
        mappings_path=mappings_path,
        institution_audit_path=institution_audit_path,
        write=True,
        institution_id=current_institution_id,
    )
    locations = load_confirmed_locations(locations_path)
    selected_location_id = resolve_location_id(
        draft.get("location_id"), location_id_redirects(institution_audit_path)
    )
    if selected_location_id:
        matches = [
            index for index, row in enumerate(locations)
            if clean(row.get("institution_id")) == current_institution_id
            and clean(row.get("location_id")) == selected_location_id
        ]
        if not matches:
            raise CuratedLocationError(
                "selected confirmed location does not belong to this institution",
                field="location_id",
                error_code="invalid_location_id",
            )
    else:
        values_key = normalized_location_key(values)
        matches = [
            index for index, row in enumerate(locations)
            if normalized_location_key(row) == values_key
        ]
        same_locality = [
            row for row in locations
            if clean(row.get("institution_id")) == current_institution_id
            and normalize_candidate_name(row.get("city")) == normalize_candidate_name(values["city"])
            and normalize_candidate_name(row.get("region")) == normalize_candidate_name(values["region"])
            and (clean(row.get("country_code")).upper() or normalize_candidate_name(row.get("country")))
            == (values["country_code"] or normalize_candidate_name(values["country"]))
        ]
        if not matches and len(same_locality) > 1:
            raise CuratedLocationError(
                "multiple distinct confirmed locations match this locality; select a location candidate",
                field="location_id",
                error_code="ambiguous_location",
            )
    if len(matches) > 1:
        raise CuratedLocationError("duplicate confirmed location rows exist")
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

    # A location action updates location state only. Identity remains owned by
    # institutions.csv and mapping reassignment remains an explicit action.
    queue_row["review_status"] = "confirmed"
    queue_row["location_status"] = "known"
    queue_row["coordinate_status"] = "known"
    queue_row["updated_at"] = now
    # Historical refreshes may have produced duplicate review rows for the
    # same paper/raw institution under an obsolete ID. They represent the same
    # location decision when the active mapping resolves them to this target.
    for peer in review_rows:
        if peer is queue_row:
            continue
        if (
            clean(peer.get("related_paper_id")) == paper_id
            and normalize_institution_name(peer.get("institution"))
            == normalize_institution_name(queue_row.get("institution"))
        ):
            peer["review_status"] = "confirmed"
            peer["location_status"] = "known"
            peer["coordinate_status"] = "known"
            peer["updated_at"] = now
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
    status_values = {
        "pending_review": ("missing", "missing"),
        "ambiguous": ("ambiguous", "needs_coordinate_review"),
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
    target_institution_id = clean(target.get("institution_id")) or (
        "institution:" + hashlib.sha256(
            normalize_institution_name(target.get("institution")).encode("utf-8")
        ).hexdigest()[:16]
    )
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
        "alias_id": "alias:" + hashlib.sha256(
            normalized_alias.encode("utf-8")
        ).hexdigest()[:16],
        "alias_name": alias_name,
        "institution_id": target_institution_id,
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
    queue_row["institution_id"] = target_institution_id
    queue_row["matched_institution"] = clean(target.get("institution"))
    queue_row["review_status"] = "alias_of_confirmed"
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
    confirmed = [row for row in locations if is_confirmed_location(row)]
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
    confirmed_ids = {clean(row.get("institution_id")) for row in confirmed}
    needs_coordinates = sum(
        clean(row.get("review_status")) == "pending_review"
        and clean(row.get("institution_id")) not in confirmed_ids
        for row in reviews
    )
    return {
        "total_queue_rows": len(reviews),
        **{
            status: statuses[status]
            for status in sorted(ALLOWED_INSTITUTION_REVIEW_STATUSES)
        },
        "ambiguous": statuses["ambiguous"],
        "needs_coordinates": needs_coordinates,
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
    mappings: Sequence[Mapping[str, Any]] = (),
    exclusions: Sequence[Mapping[str, Any]] = (),
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    paper_is_suppressed: Callable[[Mapping[str, Any]], str] | None = None,
) -> Dict[str, Any]:
    reviews = load_location_review_queue(review_path)
    locations = load_confirmed_locations(locations_path)
    aliases = load_institution_aliases(aliases_path)
    institutions = load_institutions(institutions_path)
    institution_by_id = {
        clean(row.get("institution_id")): row for row in institutions
        if clean(row.get("institution_id"))
    }
    inactive_ids = {
        clean(row.get("institution_id"))
        for row in institutions
        if clean(row.get("institution_status")) != "active"
    }
    active_exclusion_index = build_active_exclusion_index(exclusions)
    aliases_by_canonical: Dict[str, List[str]] = defaultdict(list)
    aliases_by_id: Dict[str, List[str]] = defaultdict(list)
    confirmed_alias_targets: Dict[str, str] = {}
    for alias in aliases:
        if clean(alias.get("review_status")) != "confirmed":
            continue
        canonical = clean(alias.get("canonical_institution_name"))
        aliases_by_canonical[normalize_institution_name(canonical)].append(
            clean(alias.get("alias_name"))
        )
        aliases_by_id[clean(alias.get("institution_id"))].append(
            clean(alias.get("alias_name"))
        )
        confirmed_alias_targets[
            normalize_institution_name(alias.get("alias_name"))
        ] = canonical
    by_institution: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    by_institution_id: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for location in locations:
        if not is_confirmed_location(location):
            continue
        by_institution[
            normalize_institution_name(
                location.get("normalized_institution")
                or location.get("institution")
            )
        ].append(location)
        if clean(location.get("institution_id")):
            by_institution_id[clean(location.get("institution_id"))].append(location)
    records = []
    suppression_reasons: Counter[str] = Counter()
    mappings_by_institution: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    eligible_mappings: List[Mapping[str, Any]] = []
    for mapping in mappings:
        if clean(mapping.get("mapping_status")) not in {"active", "needs_review"}:
            continue
        if record_is_excluded(mapping, active_exclusion_index):
            continue
        if paper_is_suppressed and paper_is_suppressed(mapping):
            continue
        eligible_mappings.append(mapping)
        mappings_by_institution[
            normalize_institution_name(mapping.get("institution"))
        ].append(mapping)
    reviewed_mapping_keys = {
        (clean(row.get("institution_id")), identity_key)
        for row in reviews
        for identity_key in all_identity_keys({
            **row,
            "paper_id": clean(row.get("related_paper_id")),
        })
    }
    for mapping in eligible_mappings:
        institution_id = clean(mapping.get("institution_id"))
        entity = institution_by_id.get(institution_id, {})
        if clean(entity.get("institution_status")) != "active":
            continue
        mapping_identity_keys = {
            (institution_id, identity_key)
            for identity_key in all_identity_keys(mapping)
        }
        if mapping_identity_keys & reviewed_mapping_keys:
            continue
        known = by_institution_id.get(institution_id, [])
        if any(clean(row.get("lat")) and clean(row.get("lon")) for row in known):
            continue
        reviews.append({
            "institution": clean(mapping.get("institution")),
            "canonical_institution_name": clean(entity.get("canonical_name")),
            "institution_id": institution_id,
            "related_paper_id": clean(mapping.get("paper_id")),
            "title": clean(mapping.get("title")),
            "year": clean(mapping.get("year")),
            "doi": clean(mapping.get("doi")),
            "openalex_url": clean(mapping.get("openalex_url")),
            "institution_authors": clean(mapping.get("institution_authors")),
            "raw_affiliation": clean(mapping.get("raw_affiliation")),
            "review_status": "pending_review",
            "location_status": "needs_location_review",
            "coordinate_status": "missing",
            "derived_from_active_mapping": "true",
        })
        reviewed_mapping_keys.update(mapping_identity_keys)
    for row in reviews:
        institution_id = clean(row.get("institution_id"))
        entity = institution_by_id.get(institution_id, {})
        raw_key = normalize_institution_name(row.get("institution"))
        alias_target = confirmed_alias_targets.get(raw_key)
        canonical_key = normalize_institution_name(
            row.get("canonical_institution_name") or alias_target
            or row.get("institution")
        )
        matches = by_institution_id.get(institution_id) or by_institution.get(canonical_key, [])
        affected_mappings = mappings_by_institution.get(raw_key, [])
        affected_papers = {}
        for mapping in affected_mappings:
            paper_id = clean(mapping.get("paper_id"))
            paper_key = paper_id or "|".join((
                clean(mapping.get("title")), clean(mapping.get("year"))
            ))
            affected_papers[paper_key] = {
                "paper_id": paper_id,
                "title": clean(mapping.get("title")),
                "year": clean(mapping.get("year")),
            }
        effective_status = clean(row.get("review_status")) or "pending_review"
        row_paper_identity = {
            **row,
            "paper_id": clean(row.get("related_paper_id")),
        }
        row_only_references_excluded_paper = (
            (record_is_excluded(row_paper_identity, active_exclusion_index)
             or bool(paper_is_suppressed and paper_is_suppressed(row_paper_identity)))
            and not affected_mappings
        )
        if institution_id in inactive_ids:
            effective_status = "ignore"
        elif row_only_references_excluded_paper:
            effective_status = "excluded"
        elif alias_target and effective_status not in {"ignore", "excluded"}:
            effective_status = "alias_of_confirmed"
        elif effective_status in {"pending_review", "ambiguous"} and any(
            clean(location.get("lat")) and clean(location.get("lon")) for location in matches
        ):
            effective_status = "confirmed"
        candidate_suggestions = []
        suggested_key = normalize_institution_name(
            row.get("suggested_canonical_institution")
            or row.get("matched_institution")
        )
        needs_candidate_review = (
            effective_status in {"pending_review", "ambiguous"}
            and (not matches or effective_status == "ambiguous")
        )
        for location in locations if needs_candidate_review else ():
            canonical_name = clean(location.get("institution"))
            location_key = normalize_institution_name(canonical_name)
            score, reason = institution_candidate_evidence(
                row.get("institution"), canonical_name
            )
            if suggested_key and suggested_key == location_key:
                score = max(score, 1.0)
                reason = "source_suggested_canonical_match"
            if not reason:
                continue
            row_country = clean(row.get("suggested_country")).casefold()
            canonical_country = clean(location.get("country")).casefold()
            conflicts = []
            if row_country and canonical_country and row_country != canonical_country:
                conflicts.append("country")
            candidate_suggestions.append({
                "canonical_institution_name": canonical_name,
                "canonical_record": dict(location),
                "aliases": aliases_by_canonical.get(location_key, []),
                "reason": reason,
                "evidence": (
                    f"{reason.replace('_', ' ')}; normalized-name score={score:.3f}"
                ),
                "score": score,
                "location_conflicts": conflicts,
            })
        candidate_suggestions.sort(
            key=lambda candidate: (-candidate["score"], candidate["canonical_institution_name"])
        )
        if len(candidate_suggestions) > 1:
            conflict_fields = {
                "country": "country_between_candidates",
                "region": "region_between_candidates",
                "coordinates": "coordinates_between_candidates",
            }
            candidate_values = {
                "country": {
                    clean(candidate["canonical_record"].get("country")).casefold()
                    for candidate in candidate_suggestions
                    if clean(candidate["canonical_record"].get("country"))
                },
                "region": {
                    clean(candidate["canonical_record"].get("region")).casefold()
                    for candidate in candidate_suggestions
                    if clean(candidate["canonical_record"].get("region"))
                },
                "coordinates": {
                    (
                        clean(candidate["canonical_record"].get("lat")),
                        clean(candidate["canonical_record"].get("lon")),
                    )
                    for candidate in candidate_suggestions
                    if clean(candidate["canonical_record"].get("lat"))
                    and clean(candidate["canonical_record"].get("lon"))
                },
            }
            for field, values in candidate_values.items():
                if len(values) > 1:
                    for candidate in candidate_suggestions:
                        candidate["location_conflicts"].append(
                            conflict_fields[field]
                        )
        record = {
                **row,
                "review_status": effective_status,
                "effective_review_status": effective_status,
                "actionable": effective_status in {"pending_review", "ambiguous"},
                "canonical_institution_name": clean(
                    entity.get("canonical_name") or row.get("canonical_institution_name") or alias_target
                ),
                "abbreviation": clean(entity.get("abbreviation")),
                "aliases": (
                    aliases_by_id.get(institution_id, [])
                    if institution_id else aliases_by_canonical.get(canonical_key, [])
                ),
                "queue_id": queue_row_id(row),
                "confirmed_location": matches[0] if len(matches) == 1 else None,
                "confirmed_locations": [dict(location) for location in matches],
                "confirmed_location_count": len(matches),
                "has_usable_confirmed_location": any(
                    clean(location.get("lat")) and clean(location.get("lon"))
                    for location in matches
                ),
                "existing_aliases": aliases_by_canonical.get(canonical_key, []),
                "candidate_suggestions": candidate_suggestions,
                "affected_mappings": [
                    {
                        field: clean(mapping.get(field))
                        for field in (
                            "mapping_id", "paper_id", "title", "year", "institution",
                            "institution_authors", "raw_affiliation", "mapping_status",
                        )
                    }
                    for mapping in affected_mappings
                ],
                "affected_papers": list(affected_papers.values()),
            }
        if institution_id in inactive_ids:
            suppression_reasons["resolved_by_ignored_institution"] += 1
        elif row_only_references_excluded_paper:
            suppression_reasons["resolved_by_durable_exclusion"] += 1
        elif effective_status in {"ignore", "excluded"}:
            suppression_reasons["resolved_by_durable_exclusion"] += 1
        elif alias_target or effective_status == "alias_of_confirmed":
            suppression_reasons["resolved_by_curated_correction"] += 1
        elif matches or effective_status == "confirmed" or clean(row.get("coordinate_status")) == "known":
            suppression_reasons["resolved_by_active_institution_override"] += 1
        if not any(existing["queue_id"] == record["queue_id"] for existing in records):
            records.append(record)
    summary = location_review_report(reviews, locations)
    effective_counts = Counter(record["review_status"] for record in records)
    summary.update({
        "total_queue_rows": len(records),
        "pending_review": effective_counts["pending_review"],
        "needs_coordinates": sum(
            record["actionable"]
            and not record.get("has_usable_confirmed_location")
            for record in records
        ),
        "ambiguous": effective_counts["ambiguous"],
        "confirmed": effective_counts["confirmed"],
        "alias_of_confirmed": effective_counts["alias_of_confirmed"],
        "ignore": effective_counts["ignore"],
        "excluded": effective_counts["excluded"],
    })
    return {
        "records": records,
        "total_unresolved": sum(
            record["review_status"] in {"pending_review", "ambiguous"}
            for record in records
        ),
        "hidden_resolved": sum(suppression_reasons.values()),
        "suppression_reasons": dict(sorted(suppression_reasons.items())),
        "confirmed_locations": [row for row in locations if is_confirmed_location(row)],
        "candidate_locations": [row for row in locations if not is_confirmed_location(row)],
        "institution_aliases": aliases,
        "summary": summary,
    }
