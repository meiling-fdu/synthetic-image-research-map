#!/usr/bin/env python3
"""Paper-level curated author–institution mapping operations."""

from __future__ import annotations

import csv
import hashlib
import math
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

try:
    from .curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
    )
    from .paper_exclusions import (
        all_identity_keys,
        clean,
        normalized_title_year_key,
    )
except ImportError:
    from curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
    )
    from paper_exclusions import all_identity_keys, clean, normalized_title_year_key


DEFAULT_MAPPINGS_PATH = CURATED_DATA_DIR / "author_institution_mappings.csv"
DEFAULT_LOCATION_REVIEW_PATH = CURATED_DATA_DIR / "institution_location_review.csv"
ACTIVE_MAPPING_STATUSES = {"active", "needs_review"}
ALLOWED_MAPPING_STATUSES = ACTIVE_MAPPING_STATUSES | {"excluded"}


class CuratedMappingError(RuntimeError):
    """An expected mapping validation or write error."""


class DuplicateMappingError(CuratedMappingError):
    """An active mapping already uses the same paper, institution, and authors."""

    def __init__(self, mapping: Mapping[str, Any]):
        self.mapping = dict(mapping)
        super().__init__(
            "an active mapping already exists for this paper, institution, and authors"
        )


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _normalized_text(value: Any) -> str:
    return " ".join(
        unicodedata.normalize("NFKC", clean(value)).casefold().split()
    )


def paper_identity_keys(record: Mapping[str, Any]) -> List[str]:
    keys = list(all_identity_keys(record))
    paper_id = clean(
        record.get("paper_id")
        or record.get("related_paper_id")
        or record.get("display_id")
    ).casefold()
    if paper_id:
        keys.insert(0, f"paper_id:{paper_id}")
    return keys


def records_share_paper_identity(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> bool:
    return bool(set(paper_identity_keys(left)) & set(paper_identity_keys(right)))


def _read_csv(
    path: Path, expected_columns: Sequence[str]
) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != tuple(expected_columns):
                raise CuratedMappingError(
                    f"{path} does not have the exact curated CSV header"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise CuratedMappingError(f"could not read {path}: {error}") from error
    except (UnicodeError, csv.Error) as error:
        raise CuratedMappingError(f"invalid CSV in {path}: {error}") from error


def _write_csv(
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
        raise CuratedMappingError(f"could not write {path}: {error}") from error


def load_mappings(
    path: Path = DEFAULT_MAPPINGS_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)


def save_mappings(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_MAPPINGS_PATH,
) -> None:
    _write_csv(rows, path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)


def load_location_reviews(
    path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> List[Dict[str, str]]:
    return _read_csv(path, INSTITUTION_LOCATION_REVIEW_COLUMNS)


def save_location_reviews(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> None:
    _write_csv(rows, path, INSTITUTION_LOCATION_REVIEW_COLUMNS)


def mappings_for_paper(
    paper: Mapping[str, Any],
    rows: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows if records_share_paper_identity(paper, row)]


def location_reviews_for_paper(
    paper: Mapping[str, Any],
    rows: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows if records_share_paper_identity(paper, row)]


def _paper_fields(paper: Mapping[str, Any]) -> Dict[str, str]:
    paper_id = clean(paper.get("paper_id") or paper.get("display_id"))
    fields = {
        "paper_id": paper_id,
        "title": clean(paper.get("title")),
        "year": clean(paper.get("year") or paper.get("publication_year")),
        "doi": clean(paper.get("doi")),
        "openalex_url": clean(paper.get("openalex_url")),
    }
    if not paper_identity_keys(fields):
        raise CuratedMappingError(
            "paper requires a stable ID, DOI, OpenAlex URL, or title + year"
        )
    return fields


def _mapping_fields(
    paper: Mapping[str, Any],
    draft: Mapping[str, Any],
) -> Dict[str, str]:
    institution = clean(draft.get("institution"))
    institution_id = clean(draft.get("institution_id"))
    institution_authors = clean(draft.get("institution_authors"))
    raw_affiliation = clean(draft.get("raw_affiliation"))
    evidence_source = clean(draft.get("evidence_source"))
    evidence_url = clean(draft.get("evidence_url"))
    review_note = clean(draft.get("review_note"))
    mapping_status = clean(draft.get("mapping_status")) or "active"
    if not institution:
        raise CuratedMappingError("institution is required")
    if not institution_id:
        normalized = _normalized_text(institution)
        institution_id = (
            f"institution:{hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]}"
            if normalized else ""
        )
    if not institution_authors:
        raise CuratedMappingError("institution authors are required")
    if not any((raw_affiliation, evidence_source, evidence_url)):
        raise CuratedMappingError(
            "raw affiliation or evidence source/evidence URL is required"
        )
    if mapping_status not in ACTIVE_MAPPING_STATUSES:
        raise CuratedMappingError(
            "mapping_status must be active or needs_review"
        )
    return {
        **_paper_fields(paper),
        "institution": institution,
        "institution_id": institution_id,
        "institution_authors": institution_authors,
        "author_order": clean(draft.get("author_order")),
        "raw_affiliation": raw_affiliation,
        "openalex_institution_id": clean(
            draft.get("openalex_institution_id")
        ),
        "institution_city": clean(draft.get("institution_city")),
        "institution_country": clean(draft.get("institution_country")),
        "institution_latitude": clean(draft.get("institution_latitude")),
        "institution_longitude": clean(draft.get("institution_longitude")),
        "provenance_source": clean(draft.get("provenance_source")),
        "evidence_source": evidence_source,
        "evidence_url": evidence_url,
        "affiliation_note": clean(draft.get("affiliation_note")),
        "mapping_status": mapping_status,
        "review_note": review_note,
    }


def _duplicate_mapping(
    candidate: Mapping[str, Any],
    rows: Iterable[Mapping[str, Any]],
    *,
    ignore_mapping_id: str = "",
) -> Dict[str, Any] | None:
    institution = clean(candidate.get("institution_id")) or _normalized_text(
        candidate.get("institution")
    )
    authors = _normalized_text(candidate.get("institution_authors"))
    for row in rows:
        if clean(row.get("mapping_id")) == ignore_mapping_id:
            continue
        if clean(row.get("mapping_status")) not in ACTIVE_MAPPING_STATUSES:
            continue
        if not records_share_paper_identity(candidate, row):
            continue
        if (
            (clean(row.get("institution_id")) or _normalized_text(row.get("institution"))) == institution
            and _normalized_text(row.get("institution_authors")) == authors
        ):
            return dict(row)
    return None


def _mapping_id(mapping: Mapping[str, Any], timestamp: str) -> str:
    identity = "|".join(
        (
            normalized_title_year_key(mapping),
            clean(mapping.get("doi")).casefold(),
            clean(mapping.get("openalex_url")).casefold(),
            _normalized_text(mapping.get("institution")),
            _normalized_text(mapping.get("institution_authors")),
            timestamp,
        )
    )
    return f"mapping:{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:20]}"


def _unique_mapping_id(
    mapping: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    seed: str,
) -> str:
    existing_ids = {clean(row.get("mapping_id")) for row in rows}
    counter = 0
    while True:
        candidate = _mapping_id(mapping, f"{seed}|{counter}")
        if candidate not in existing_ids:
            return candidate
        counter += 1


def _valid_coordinate(value: Any, *, latitude: bool) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    limit = 90 if latitude else 180
    return math.isfinite(number) and -limit <= number <= limit


def known_location_institutions(
    map_records: Iterable[Mapping[str, Any]],
) -> set[str]:
    known = set()
    for record in map_records:
        latitude = record.get("latitude")
        longitude = record.get("longitude")
        if latitude in (None, ""):
            latitude = record.get("lat")
        if longitude in (None, ""):
            longitude = record.get("lon")
        institution = _normalized_text(record.get("institution"))
        if (
            institution
            and _valid_coordinate(latitude, latitude=True)
            and _valid_coordinate(longitude, latitude=False)
        ):
            known.add(institution)
    return known


def mapping_location_state(
    mapping: Mapping[str, Any],
    *,
    map_records: Sequence[Mapping[str, Any]],
    location_rows: Sequence[Mapping[str, Any]],
) -> str:
    if _normalized_text(mapping.get("institution")) in known_location_institutions(
        map_records
    ):
        return "known"
    key = _queue_key(mapping)
    for row in location_rows:
        if _queue_key(row) == key:
            return clean(row.get("coordinate_status")) or "missing"
    return "not_queued"


def _queue_key(record: Mapping[str, Any]) -> tuple[str, str, str]:
    paper_key = next(iter(paper_identity_keys(record)), "")
    return (
        paper_key,
        _normalized_text(record.get("institution")),
        _normalized_text(record.get("institution_authors")),
    )


def _sync_location_review(
    mapping: Mapping[str, Any],
    *,
    map_records: Sequence[Mapping[str, Any]],
    location_rows: List[Dict[str, str]],
) -> str:
    if clean(mapping.get("mapping_status")) != "active":
        return "not_required"
    if _normalized_text(mapping.get("institution")) in known_location_institutions(
        map_records
    ):
        return "known"

    now = _timestamp()
    values = {
        "institution": clean(mapping.get("institution")),
        "canonical_institution_name": clean(mapping.get("institution")),
        "institution_id": clean(mapping.get("institution_id")),
        "related_paper_id": clean(mapping.get("paper_id")),
        "title": clean(mapping.get("title")),
        "year": clean(mapping.get("year")),
        "doi": clean(mapping.get("doi")),
        "openalex_url": clean(mapping.get("openalex_url")),
        "institution_authors": clean(mapping.get("institution_authors")),
        "raw_affiliation": clean(mapping.get("raw_affiliation")),
        "evidence_source": clean(mapping.get("evidence_source")),
        "evidence_url": clean(mapping.get("evidence_url")),
        "suggested_city": clean(mapping.get("institution_city")),
        "suggested_country": clean(mapping.get("institution_country")),
        "openalex_institution_id": clean(
            mapping.get("openalex_institution_id")
        ),
        "review_status": "needs_coordinates",
        "location_status": "missing",
        "coordinate_status": "missing",
        "review_note": clean(mapping.get("review_note")),
        "updated_at": now,
    }
    key = _queue_key(mapping)
    for row in location_rows:
        if _queue_key(row) == key:
            created_at = clean(row.get("created_at")) or now
            row.update(values)
            row["created_at"] = created_at
            return "updated"
    location_rows.append({**values, "created_at": now})
    return "created"


def create_mapping(
    paper: Mapping[str, Any],
    draft: Mapping[str, Any],
    *,
    map_records: Sequence[Mapping[str, Any]],
    mappings_path: Path = DEFAULT_MAPPINGS_PATH,
    location_review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> Dict[str, Any]:
    rows = load_mappings(mappings_path)
    candidate = _mapping_fields(paper, draft)
    duplicate = _duplicate_mapping(candidate, rows)
    if duplicate:
        raise DuplicateMappingError(duplicate)
    now = _timestamp()
    row = {
        "mapping_id": _unique_mapping_id(candidate, rows, now),
        **candidate,
        "created_at": now,
        "updated_at": now,
    }
    location_rows = load_location_reviews(location_review_path)
    location_status = _sync_location_review(
        row, map_records=map_records, location_rows=location_rows
    )
    rows.append(row)
    save_mappings(rows, mappings_path)
    if location_status in {"created", "updated"}:
        save_location_reviews(location_rows, location_review_path)
    return {"mapping": row, "location_review": location_status}


def create_mapping_candidates(
    paper: Mapping[str, Any],
    drafts: Sequence[Mapping[str, Any]],
    *,
    map_records: Sequence[Mapping[str, Any]],
    mappings_path: Path = DEFAULT_MAPPINGS_PATH,
    location_review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> Dict[str, Any]:
    """Atomically append all non-duplicate candidates for a newly added paper."""
    rows = load_mappings(mappings_path)
    location_rows = load_location_reviews(location_review_path)
    created: List[Dict[str, str]] = []
    location_results: List[str] = []
    for index, draft in enumerate(drafts):
        candidate = _mapping_fields(paper, draft)
        duplicate = _duplicate_mapping(candidate, [*rows, *created])
        if duplicate:
            continue
        now = _timestamp()
        row = {
            "mapping_id": _unique_mapping_id(
                candidate, [*rows, *created], f"{now}|candidate|{index}"
            ),
            **candidate,
            "created_at": now,
            "updated_at": now,
        }
        created.append(row)
        location_results.append(
            _sync_location_review(
                row, map_records=map_records, location_rows=location_rows
            )
        )
    if created:
        save_mappings([*rows, *created], mappings_path)
    if any(status in {"created", "updated"} for status in location_results):
        save_location_reviews(location_rows, location_review_path)
    return {
        "mappings": created,
        "location_reviews": location_results,
    }


def update_mapping(
    paper: Mapping[str, Any],
    mapping_id: str,
    draft: Mapping[str, Any],
    *,
    map_records: Sequence[Mapping[str, Any]],
    mappings_path: Path = DEFAULT_MAPPINGS_PATH,
    location_review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> Dict[str, Any]:
    rows = load_mappings(mappings_path)
    row = next(
        (row for row in rows if clean(row.get("mapping_id")) == clean(mapping_id)),
        None,
    )
    if row is None or not records_share_paper_identity(paper, row):
        raise CuratedMappingError("mapping not found for selected paper")
    candidate_draft = dict(draft)
    if "review_note" not in candidate_draft:
        candidate_draft["review_note"] = row.get("review_note")
    candidate = _mapping_fields(paper, candidate_draft)
    duplicate = _duplicate_mapping(
        candidate, rows, ignore_mapping_id=clean(mapping_id)
    )
    if duplicate:
        raise DuplicateMappingError(duplicate)
    created_at = clean(row.get("created_at")) or _timestamp()
    row.update(candidate)
    row["created_at"] = created_at
    row["updated_at"] = _timestamp()
    location_rows = load_location_reviews(location_review_path)
    location_status = _sync_location_review(
        row, map_records=map_records, location_rows=location_rows
    )
    save_mappings(rows, mappings_path)
    if location_status in {"created", "updated"}:
        save_location_reviews(location_rows, location_review_path)
    return {"mapping": dict(row), "location_review": location_status}


def _append_audit_note(existing: Any, action: str, note: str) -> str:
    prior = clean(existing)
    entry = f"[{_timestamp()}] {action}: {clean(note)}"
    return f"{prior} | {entry}" if prior else entry


def exclude_mapping(
    paper: Mapping[str, Any],
    mapping_id: str,
    review_note: str,
    *,
    mappings_path: Path = DEFAULT_MAPPINGS_PATH,
) -> Dict[str, str]:
    if not clean(review_note):
        raise CuratedMappingError("review note is required")
    rows = load_mappings(mappings_path)
    row = next(
        (row for row in rows if clean(row.get("mapping_id")) == clean(mapping_id)),
        None,
    )
    if row is None or not records_share_paper_identity(paper, row):
        raise CuratedMappingError("mapping not found for selected paper")
    if clean(row.get("mapping_status")) == "excluded":
        raise CuratedMappingError("mapping is already excluded")
    row["mapping_status"] = "excluded"
    row["review_note"] = _append_audit_note(
        row.get("review_note"), "Excluded", review_note
    )
    row["updated_at"] = _timestamp()
    save_mappings(rows, mappings_path)
    return dict(row)


def replace_all_mappings(
    paper: Mapping[str, Any],
    drafts: Sequence[Mapping[str, Any]],
    review_note: str,
    *,
    confirm_replace_all: bool,
    map_records: Sequence[Mapping[str, Any]],
    mappings_path: Path = DEFAULT_MAPPINGS_PATH,
    location_review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
) -> Dict[str, Any]:
    if confirm_replace_all is not True:
        raise CuratedMappingError("confirm_replace_all=true is required")
    if not clean(review_note):
        raise CuratedMappingError("review note is required")
    if not isinstance(drafts, list) or not drafts:
        raise CuratedMappingError("at least one replacement mapping is required")

    rows = load_mappings(mappings_path)
    replaced = []
    for row in rows:
        if (
            records_share_paper_identity(paper, row)
            and clean(row.get("mapping_status")) in ACTIVE_MAPPING_STATUSES
        ):
            row["mapping_status"] = "excluded"
            row["review_note"] = _append_audit_note(
                row.get("review_note"), "Replaced", review_note
            )
            row["updated_at"] = _timestamp()
            replaced.append(clean(row.get("mapping_id")))

    created = []
    location_rows = load_location_reviews(location_review_path)
    location_results = []
    for draft in drafts:
        candidate_draft = dict(draft)
        candidate_draft.setdefault("review_note", review_note)
        candidate = _mapping_fields(paper, candidate_draft)
        duplicate = _duplicate_mapping(candidate, rows)
        if duplicate:
            raise DuplicateMappingError(duplicate)
        now = _timestamp()
        row = {
            "mapping_id": _unique_mapping_id(
                candidate, rows, f"{now}|{len(created)}"
            ),
            **candidate,
            "created_at": now,
            "updated_at": now,
        }
        rows.append(row)
        created.append(row)
        location_results.append(
            _sync_location_review(
                row, map_records=map_records, location_rows=location_rows
            )
        )

    save_mappings(rows, mappings_path)
    if any(status in {"created", "updated"} for status in location_results):
        save_location_reviews(location_rows, location_review_path)
    return {
        "replaced_mapping_ids": replaced,
        "mappings": created,
        "location_reviews": location_results,
    }
