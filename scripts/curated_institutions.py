#!/usr/bin/env python3
"""Stable institution identities and protected administrative operations."""

from __future__ import annotations

import csv
import hashlib
import math
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

try:
    from .curated_schema import (
        ALLOWED_INSTITUTION_STATUSES,
        ALLOWED_INSTITUTION_TYPES,
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_AUDIT_COLUMNS,
        INSTITUTION_COLUMNS,
        INSTITUTION_HIERARCHY_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        INSTITUTION_REVIEW_QUEUE_COLUMNS,
    )
except ImportError:
    from curated_schema import (
        ALLOWED_INSTITUTION_STATUSES,
        ALLOWED_INSTITUTION_TYPES,
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_AUDIT_COLUMNS,
        INSTITUTION_COLUMNS,
        INSTITUTION_HIERARCHY_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        INSTITUTION_REVIEW_QUEUE_COLUMNS,
    )


DEFAULT_INSTITUTIONS_PATH = CURATED_DATA_DIR / "institutions.csv"
DEFAULT_ALIASES_PATH = CURATED_DATA_DIR / "institution_aliases.csv"
DEFAULT_LOCATIONS_PATH = CURATED_DATA_DIR / "institution_locations.csv"
DEFAULT_MAPPINGS_PATH = CURATED_DATA_DIR / "author_institution_mappings.csv"
DEFAULT_AUDIT_PATH = CURATED_DATA_DIR / "institution_audit_log.csv"
DEFAULT_LOCATION_REVIEWS_PATH = CURATED_DATA_DIR / "institution_location_review.csv"
DEFAULT_HIERARCHY_PATH = CURATED_DATA_DIR / "institution_hierarchy.csv"
DEFAULT_REVIEW_QUEUE_PATH = CURATED_DATA_DIR / "institution_review_queue.csv"


class CuratedInstitutionError(RuntimeError):
    """An expected institution validation or protected-operation error."""


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_institution(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def stable_institution_id(value: Any) -> str:
    normalized = normalize_institution(value)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"institution:{digest}" if normalized else ""


def alias_id_for(value: Any) -> str:
    normalized = normalize_institution(value)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"alias:{digest}" if normalized else ""


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _read(path: Path, columns: Sequence[str]) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != tuple(columns):
                raise CuratedInstitutionError(f"{path} has an unexpected CSV header")
            return [dict(row) for row in reader]
    except OSError as error:
        raise CuratedInstitutionError(f"could not read {path}: {error}") from error


def _write(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise CuratedInstitutionError(f"could not write {path}: {error}") from error


def load_institutions(path: Path = DEFAULT_INSTITUTIONS_PATH) -> list[dict[str, str]]:
    return _read(path, INSTITUTION_COLUMNS)


def save_institutions(rows: Sequence[Mapping[str, Any]], path: Path = DEFAULT_INSTITUTIONS_PATH) -> None:
    _write(path, INSTITUTION_COLUMNS, rows)


def _entity(rows: Sequence[Mapping[str, Any]], institution_id: Any) -> dict[str, Any]:
    identifier = clean(institution_id)
    matches = [row for row in rows if clean(row.get("institution_id")) == identifier]
    if len(matches) != 1:
        raise CuratedInstitutionError("institution_id must identify exactly one institution")
    return matches[0]  # type: ignore[return-value]


def _active_entity(
    rows: Sequence[Mapping[str, Any]], institution_id: Any
) -> dict[str, Any]:
    entity = _entity(rows, institution_id)
    if clean(entity.get("institution_status")) != "active":
        raise CuratedInstitutionError(
            "institution_id must identify an active canonical institution"
        )
    return entity


def institution_impact(
    institution_id: Any,
    mappings: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    identifier = clean(institution_id)
    affected = [
        row for row in mappings
        if clean(row.get("institution_id")) == identifier
        and clean(row.get("mapping_status")) in {"active", "needs_review"}
    ]
    papers = {clean(row.get("paper_id")) or clean(row.get("title")) for row in affected}
    authors = sorted({
        author.strip()
        for row in affected
        for author in clean(row.get("institution_authors")).split(";")
        if author.strip()
    })
    return {
        "papers": len(papers),
        "author_mappings": len(affected),
        "markers": len(affected),
        "authors": authors,
    }


def _append_audit(
    *, action: str, institution_id: str, previous_institution_id: str = "",
    impact: Mapping[str, Any], confirmation: Any = "", review_note: Any,
    created_by: Any, audit_path: Path, created_at: Any = "",
) -> dict[str, str]:
    rows = _read(audit_path, INSTITUTION_AUDIT_COLUMNS)
    now = clean(created_at) or _timestamp()
    seed = "|".join((action, institution_id, previous_institution_id, now, clean(created_by)))
    row = {
        "audit_id": f"institution-audit:{hashlib.sha256(seed.encode()).hexdigest()[:20]}",
        "action": action,
        "institution_id": institution_id,
        "previous_institution_id": previous_institution_id,
        "affected_papers": str(impact.get("papers", 0)),
        "affected_mappings": str(impact.get("author_mappings", 0)),
        "affected_markers": str(impact.get("markers", 0)),
        "affected_authors": "; ".join(impact.get("authors", [])),
        "confirmation_text": clean(confirmation),
        "review_note": clean(review_note),
        "created_at": now,
        "created_by": clean(created_by) or "local-admin",
    }
    rows.append(row)
    _write(audit_path, INSTITUTION_AUDIT_COLUMNS, rows)
    return row


def append_mapping_change_resolution_audit(
    *, action: str, review_queue_id: Any, source_audit_id: Any,
    mapping_id: Any, previous_institution_id: Any,
    previous_institution_name: Any, new_institution_id: Any,
    new_institution_name: Any, reverted_institution_id: Any = "",
    reverted_institution_name: Any = "", evidence_source: Any = "",
    evidence_url: Any = "", review_note: Any, created_by: Any,
    created_at: Any = "", audit_path: Path = DEFAULT_AUDIT_PATH,
) -> dict[str, str]:
    """Append a structured Admin resolution for one exact mapping transition."""
    if action not in {"mapping_change_confirmed", "mapping_reverted"}:
        raise CuratedInstitutionError("unsupported mapping change resolution action")
    old_id = clean(previous_institution_id)
    new_id = clean(new_institution_id)
    reverted_id = clean(reverted_institution_id)
    if not clean(review_queue_id) or not clean(source_audit_id) or not clean(mapping_id):
        raise CuratedInstitutionError("mapping change resolution requires queue, audit, and mapping IDs")
    if not old_id or not new_id or old_id == new_id:
        raise CuratedInstitutionError("mapping change resolution requires an exact old-to-new transition")
    if action == "mapping_reverted" and reverted_id != old_id:
        raise CuratedInstitutionError("reverted institution must match the previous trusted institution")
    metadata = "; ".join((
        f"review_queue_id={clean(review_queue_id)}",
        f"source_audit_id={clean(source_audit_id)}",
        f"mapping_id={clean(mapping_id)}",
        f"previous_institution={clean(previous_institution_name)}",
        f"new_institution={clean(new_institution_name)}",
        f"reverted_institution={clean(reverted_institution_name)}",
        f"evidence_source={clean(evidence_source)}",
        f"evidence_url={clean(evidence_url)}",
    ))
    target_id = reverted_id if action == "mapping_reverted" else new_id
    return _append_audit(
        action=action,
        institution_id=target_id,
        previous_institution_id=new_id if action == "mapping_reverted" else old_id,
        impact={"papers": 1, "author_mappings": 1, "markers": 1, "authors": []},
        confirmation=metadata,
        review_note=review_note,
        created_by=created_by,
        created_at=created_at,
        audit_path=audit_path,
    )


def append_confirmed_mapping_change_audit(
    previous: Mapping[str, Any], updated: Mapping[str, Any], *,
    change_source: Any, created_by: Any, review_note: Any,
    audit_path: Path = DEFAULT_AUDIT_PATH,
) -> dict[str, str]:
    """Record an institution-ID replacement on a trusted mapping."""
    previous_id = clean(previous.get("institution_id"))
    updated_id = clean(updated.get("institution_id"))
    if not previous_id or not updated_id or previous_id == updated_id:
        raise CuratedInstitutionError("mapping change audit requires two distinct institution IDs")
    metadata = "; ".join((
        f"mapping_id={clean(updated.get('mapping_id'))}",
        f"paper_id={clean(updated.get('paper_id'))}",
        f"paper_title={clean(updated.get('title'))}",
        f"previous_institution={clean(previous.get('institution'))}",
        f"new_institution={clean(updated.get('institution'))}",
        f"change_source={clean(change_source) or 'unknown'}",
    ))
    authors = [
        author.strip() for author in clean(updated.get("institution_authors")).split(";")
        if author.strip()
    ]
    return _append_audit(
        action="confirmed_mapping_changed",
        institution_id=updated_id,
        previous_institution_id=previous_id,
        impact={"papers": 1, "author_mappings": 1, "markers": 1, "authors": authors},
        confirmation=metadata,
        review_note=review_note,
        created_by=created_by,
        audit_path=audit_path,
    )


def update_institution_identity(
    institution_id: Any, draft: Mapping[str, Any], *,
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
) -> dict[str, str]:
    """Edit one identity record; mappings are deliberately never rewritten here."""
    rows = load_institutions(institutions_path)
    row = _entity(rows, institution_id)
    canonical = clean(draft.get("canonical_name") or row.get("canonical_name"))
    institution_type = clean(draft.get("institution_type") or row.get("institution_type"))
    status = clean(draft.get("institution_status") or row.get("institution_status"))
    if not canonical:
        raise CuratedInstitutionError("canonical_name is required")
    if institution_type not in ALLOWED_INSTITUTION_TYPES:
        raise CuratedInstitutionError("unsupported institution_type")
    if status not in ALLOWED_INSTITUTION_STATUSES:
        raise CuratedInstitutionError("unsupported institution_status")
    if status != clean(row.get("institution_status")):
        raise CuratedInstitutionError(
            "institution status changes require their dedicated action"
        )
    duplicate = next((other for other in rows if other is not row and normalize_institution(other.get("canonical_name")) == normalize_institution(canonical)), None)
    if duplicate:
        raise CuratedInstitutionError("canonical_name belongs to another institution; use the explicit merge action")
    row.update({"canonical_name": canonical, "institution_type": institution_type, "institution_status": status, "public_display": clean(draft.get("public_display") or row.get("public_display")) or "self", "updated_at": _timestamp()})
    save_institutions(rows, institutions_path)
    return dict(row)


def update_institution_location(
    institution_id: Any, draft: Mapping[str, Any], *,
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    locations_path: Path = DEFAULT_LOCATIONS_PATH,
    location_reviews_path: Optional[Path] = None,
) -> dict[str, str]:
    """Update location fields without manufacturing provenance-free review rows."""
    entities = load_institutions(institutions_path)
    entity = _entity(entities, institution_id)
    identifier = clean(entity.get("institution_id"))
    requested = clean(draft.get("institution_id"))
    loaded = clean(draft.get("loaded_institution_id"))
    if not requested:
        raise CuratedInstitutionError("institution_id is required for location edits")
    if loaded and loaded != requested:
        raise CuratedInstitutionError("institution_id differs from the institution loaded by the editor")
    if requested != identifier:
        raise CuratedInstitutionError("location edits cannot change institution_id")
    rows = _read(locations_path, INSTITUTION_LOCATION_COLUMNS)
    matches = [row for row in rows if clean(row.get("institution_id")) == identifier]
    if len(matches) > 1:
        raise CuratedInstitutionError("institution has multiple location rows")
    row = matches[0] if matches else {column: "" for column in INSTITUTION_LOCATION_COLUMNS}
    now = _timestamp()
    if not matches:
        rows.append(row)
        row["location_id"] = f"location:{identifier.removeprefix('institution:')}"
        row["created_at"] = now
        row["created_by"] = clean(draft.get("created_by")) or "local-admin"
    row["institution_id"] = identifier
    row["institution"] = clean(entity.get("canonical_name"))
    row["normalized_institution"] = normalize_institution(entity.get("canonical_name"))
    for field in ("city", "region", "country", "country_code", "lat", "lon", "coordinate_source", "coordinate_source_url", "coordinate_status", "review_note"):
        if field in draft:
            row[field] = clean(draft.get(field))
    row["updated_at"] = now
    required_location_fields = (
        "location_id",
        "institution_id",
        "institution",
        "normalized_institution",
        "country_code",
        "lat",
        "lon",
        "coordinate_status",
        "review_note",
        "created_at",
        "updated_at",
        "created_by",
    )
    for field in required_location_fields:
        if not clean(row.get(field)):
            raise CuratedInstitutionError(f"{field} is required for location edits")
    if not (
        clean(row.get("coordinate_source"))
        or clean(row.get("coordinate_source_url"))
    ):
        raise CuratedInstitutionError(
            "coordinate_source or coordinate_source_url is required for location edits"
        )
    if not re.fullmatch(r"[A-Z]{2}", clean(row.get("country_code"))):
        raise CuratedInstitutionError(
            "country_code must be two uppercase letters"
        )
    try:
        latitude = float(clean(row.get("lat")))
        longitude = float(clean(row.get("lon")))
    except ValueError as error:
        raise CuratedInstitutionError("lat and lon must be numeric") from error
    if not math.isfinite(latitude) or not -90 <= latitude <= 90:
        raise CuratedInstitutionError("lat must be between -90 and 90")
    if not math.isfinite(longitude) or not -180 <= longitude <= 180:
        raise CuratedInstitutionError("lon must be between -180 and 180")
    reviews = None
    review_matches = []
    if location_reviews_path is not None:
        reviews = _read(location_reviews_path, INSTITUTION_LOCATION_REVIEW_COLUMNS)
        review_matches = [
            review for review in reviews
            if clean(review.get("institution_id")) == identifier
        ]
        # A direct editor save has no paper/affiliation provenance of its own.
        # Only synchronize review rows that were created by an evidence-bearing
        # mapping or review action; the confirmed location row is sufficient
        # when no such review exists.
        for review in review_matches:
            if not (
                clean(review.get("related_paper_id"))
                or clean(review.get("doi"))
                or clean(review.get("openalex_url"))
                or (clean(review.get("title")) and clean(review.get("year")))
            ):
                raise CuratedInstitutionError(
                    "existing location review row lacks paper provenance"
                )
        for review in review_matches:
            previous_note = clean(review.get("review_note"))
            location_note = clean(row.get("review_note"))
            combined_note = previous_note
            if location_note and location_note not in previous_note:
                combined_note = " | ".join(item for item in (previous_note, location_note) if item)
            review.update({
                "institution_id": identifier,
                "canonical_institution_name": clean(entity.get("canonical_name")),
                "suggested_city": clean(row.get("city")),
                "suggested_country": clean(row.get("country")),
                "review_status": "confirmed",
                "location_status": "known",
                "coordinate_status": "known",
                "review_note": combined_note,
                "updated_at": now,
            })
    touched_paths = [locations_path]
    if location_reviews_path is not None and review_matches:
        touched_paths.append(location_reviews_path)
    snapshots = {
        path: path.read_bytes() if path.exists() else None
        for path in touched_paths
    }
    try:
        _write(locations_path, INSTITUTION_LOCATION_COLUMNS, rows)
        if location_reviews_path is not None and review_matches and reviews is not None:
            _write(
                location_reviews_path,
                INSTITUTION_LOCATION_REVIEW_COLUMNS,
                reviews,
            )
    except Exception:
        for path, content in snapshots.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise
    return dict(row)


def add_institution_alias(
    institution_id: Any, alias_name: Any, *, note: Any = "", source: Any = "local-admin",
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    aliases_path: Path = DEFAULT_ALIASES_PATH,
) -> dict[str, str]:
    entities = load_institutions(institutions_path)
    entity = _entity(entities, institution_id)
    alias = clean(alias_name)
    if not alias:
        raise CuratedInstitutionError("alias_name is required")
    if normalize_institution(alias) == normalize_institution(entity.get("canonical_name")):
        raise CuratedInstitutionError("an alias must differ from the canonical name")
    canonical_owner = next(
        (
            row for row in entities
            if normalize_institution(row.get("canonical_name")) == normalize_institution(alias)
            and clean(row.get("institution_id")) != clean(institution_id)
        ),
        None,
    )
    if canonical_owner:
        raise CuratedInstitutionError(
            "alias name belongs to another canonical institution; use the explicit merge action"
        )
    rows = _read(aliases_path, INSTITUTION_ALIAS_COLUMNS)
    conflict = next((row for row in rows if normalize_institution(row.get("alias_name")) == normalize_institution(alias) and clean(row.get("institution_id")) != clean(institution_id)), None)
    if conflict:
        raise CuratedInstitutionError("alias already resolves to another institution")
    existing = next((row for row in rows if normalize_institution(row.get("alias_name")) == normalize_institution(alias)), None)
    values = {
        "alias_id": alias_id_for(alias), "alias_name": alias,
        "institution_id": clean(institution_id),
        "canonical_institution_name": clean(entity.get("canonical_name")),
        "alias_language": "", "alias_source": clean(source) or "local-admin",
        "review_status": "confirmed", "notes": clean(note),
    }
    if existing:
        existing.update(values)
    else:
        rows.append(values)
    _write(aliases_path, INSTITUTION_ALIAS_COLUMNS, rows)
    return values


def set_parent_institution(
    institution_id: Any, parent_institution_id: Any, *,
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    hierarchy_path: Path = DEFAULT_HIERARCHY_PATH,
) -> dict[str, str]:
    rows = load_institutions(institutions_path)
    child = _active_entity(rows, institution_id)
    parent_id = clean(parent_institution_id)
    if parent_id:
        _active_entity(rows, parent_id)
    if parent_id == clean(institution_id):
        raise CuratedInstitutionError("an institution cannot be its own parent")
    parents = {clean(row.get("institution_id")): clean(row.get("parent_institution_id")) for row in rows}
    cursor = parent_id
    while cursor:
        if cursor == clean(institution_id):
            raise CuratedInstitutionError("parent institution cycle is forbidden")
        cursor = parents.get(cursor, "")
    child["parent_institution_id"] = parent_id
    child["updated_at"] = _timestamp()
    hierarchy = _read(hierarchy_path, INSTITUTION_HIERARCHY_COLUMNS)
    hierarchy = [
        relation for relation in hierarchy
        if not (
            clean(relation.get("child_institution_id")) == clean(institution_id)
            and clean(relation.get("relationship_type")) == "affiliated_institute"
        )
    ]
    if parent_id:
        hierarchy.append({
            "parent_institution_id": parent_id,
            "child_institution_id": clean(institution_id),
            "relationship_type": "affiliated_institute",
            "review_status": "confirmed",
            "evidence_source": "Institution Management",
            "evidence_url": "",
            "notes": "Confirmed through the local admin institution manager.",
        })

    files = (institutions_path, hierarchy_path)
    snapshots = {
        path: path.read_bytes() if path.exists() else None for path in files
    }
    try:
        save_institutions(rows, institutions_path)
        _write(hierarchy_path, INSTITUTION_HIERARCHY_COLUMNS, hierarchy)
    except Exception:
        for path, content in snapshots.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise
    return dict(child)


def effective_location(
    institution_id: Any, institutions: Sequence[Mapping[str, Any]], locations: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    """Return the nearest own/ancestor location and record inheritance."""
    entities = {clean(row.get("institution_id")): row for row in institutions}
    by_id = {clean(row.get("institution_id")): row for row in locations}
    original = clean(institution_id)
    cursor = original
    visited: set[str] = set()
    while cursor and cursor not in visited:
        visited.add(cursor)
        if cursor in by_id:
            return {**by_id[cursor], "inherited_from_institution_id": "" if cursor == original else cursor}
        cursor = clean(entities.get(cursor, {}).get("parent_institution_id"))
    return None


def ignore_institution(
    institution_id: Any, *, confirmation: bool, review_note: Any,
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    mappings_path: Path = DEFAULT_MAPPINGS_PATH,
    audit_path: Path = DEFAULT_AUDIT_PATH,
) -> Dict[str, Any]:
    if confirmation is not True:
        raise CuratedInstitutionError("ignore requires explicit confirmation")
    if not clean(review_note):
        raise CuratedInstitutionError("review_note is required")
    rows = load_institutions(institutions_path)
    entity = _entity(rows, institution_id)
    mappings = _read(mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
    impact = institution_impact(institution_id, mappings)
    entity["institution_status"] = "ignored"
    entity["updated_at"] = _timestamp()
    save_institutions(rows, institutions_path)
    audit = _append_audit(action="ignore", institution_id=clean(institution_id), impact=impact, confirmation="This hides this institution from public outputs without deleting data.", review_note=review_note, created_by="local-admin", audit_path=audit_path)
    return {"institution": dict(entity), "impact": impact, "audit": audit}


def merge_institutions(
    source_institution_id: Any, target_institution_id: Any, *, confirmation: Any,
    review_note: Any, institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    mappings_path: Path = DEFAULT_MAPPINGS_PATH, aliases_path: Path = DEFAULT_ALIASES_PATH,
    locations_path: Path = DEFAULT_LOCATIONS_PATH,
    location_reviews_path: Path = DEFAULT_LOCATION_REVIEWS_PATH,
    hierarchy_path: Path = DEFAULT_HIERARCHY_PATH,
    review_queue_path: Path = DEFAULT_REVIEW_QUEUE_PATH,
    audit_path: Path = DEFAULT_AUDIT_PATH,
) -> Dict[str, Any]:
    entities = load_institutions(institutions_path)
    source = _entity(entities, source_institution_id)
    target = _entity(entities, target_institution_id)
    if source is target:
        raise CuratedInstitutionError("source and target institutions must differ")
    phrase = f"REPLACE {clean(source.get('canonical_name'))} WITH {clean(target.get('canonical_name'))} GLOBALLY"
    if clean(confirmation) != phrase:
        raise CuratedInstitutionError(f"global replacement requires exact confirmation: {phrase}")
    if not clean(review_note):
        raise CuratedInstitutionError("review_note is required")
    mappings = _read(mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
    impact = institution_impact(source_institution_id, mappings)
    source_id = clean(source_institution_id)
    target_id = clean(target_institution_id)
    target_name = clean(target.get("canonical_name"))
    source_parent = clean(source.get("parent_institution_id"))
    target_parent = clean(target.get("parent_institution_id"))
    if (
        source_parent
        and target_parent
        and source_parent != target_parent
        and source_parent != target_id
        and target_parent != source_id
    ):
        raise CuratedInstitutionError(
            "merge requires manual parent resolution when both institutions have different parents"
        )
    now = _timestamp()
    for mapping in mappings:
        if clean(mapping.get("institution_id")) == source_id:
            mapping["institution_id"] = target_id
            mapping["institution"] = target_name
            mapping["updated_at"] = now

    locations = _read(locations_path, INSTITUTION_LOCATION_COLUMNS)
    source_locations = [
        row for row in locations if clean(row.get("institution_id")) == source_id
    ]
    target_locations = [
        row for row in locations if clean(row.get("institution_id")) == target_id
    ]
    if source_locations and target_locations:
        raise CuratedInstitutionError(
            "merge requires manual location resolution when both institutions have confirmed locations"
        )
    for location in source_locations:
        location["institution_id"] = target_id
        location["institution"] = target_name
        location["normalized_institution"] = normalize_institution(target_name)
        location["location_id"] = f"location:{target_id.removeprefix('institution:')}"
        location["updated_at"] = now

    location_reviews = _read(
        location_reviews_path, INSTITUTION_LOCATION_REVIEW_COLUMNS
    )
    for review in location_reviews:
        if clean(review.get("institution_id")) == source_id:
            review["institution_id"] = target_id
            review["canonical_institution_name"] = target_name
            review["updated_at"] = now

    aliases = _read(aliases_path, INSTITUTION_ALIAS_COLUMNS)
    for alias in aliases:
        if clean(alias.get("institution_id")) == source_id:
            alias["institution_id"] = target_id
            alias["canonical_institution_name"] = target_name
    if not any(normalize_institution(row.get("alias_name")) == normalize_institution(source.get("canonical_name")) for row in aliases):
        aliases.append({"alias_id": alias_id_for(source.get("canonical_name")), "alias_name": clean(source.get("canonical_name")), "institution_id": target_id, "canonical_institution_name": target_name, "alias_language": "", "alias_source": "institution-merge", "review_status": "confirmed", "notes": clean(review_note)})

    hierarchy = _read(hierarchy_path, INSTITUTION_HIERARCHY_COLUMNS)
    migrated_hierarchy = []
    hierarchy_keys = set()
    for relation in hierarchy:
        if clean(relation.get("parent_institution_id")) == source_id:
            relation["parent_institution_id"] = target_id
        if clean(relation.get("child_institution_id")) == source_id:
            relation["child_institution_id"] = target_id
        parent = clean(relation.get("parent_institution_id"))
        child = clean(relation.get("child_institution_id"))
        key = (parent, child, clean(relation.get("relationship_type")))
        if parent == child or key in hierarchy_keys:
            continue
        hierarchy_keys.add(key)
        migrated_hierarchy.append(relation)

    review_queue = _read(review_queue_path, INSTITUTION_REVIEW_QUEUE_COLUMNS)
    for finding in review_queue:
        if clean(finding.get("current_institution_id")) == source_id:
            finding["current_institution_id"] = target_id
            finding["current_institution"] = target_name
            finding["updated_at"] = now
        if clean(finding.get("suggested_institution_id")) == source_id:
            finding["suggested_institution_id"] = target_id
            finding["suggested_canonical_institution"] = target_name
            finding["updated_at"] = now

    for entity in entities:
        if entity is target:
            if target_parent == source_id:
                entity["parent_institution_id"] = source_parent
            elif not target_parent and source_parent != target_id:
                entity["parent_institution_id"] = source_parent
        elif entity is not source and clean(entity.get("parent_institution_id")) == source_id:
            entity["parent_institution_id"] = target_id
    source["institution_status"] = "merged"
    if clean(source.get("parent_institution_id")) == target_id:
        source["parent_institution_id"] = ""
    source["updated_at"] = now

    files = (
        institutions_path, mappings_path, aliases_path, locations_path,
        location_reviews_path, hierarchy_path, review_queue_path, audit_path,
    )
    snapshots = {
        path: path.read_bytes() if path.exists() else None for path in files
    }
    try:
        _write(mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS, mappings)
        _write(aliases_path, INSTITUTION_ALIAS_COLUMNS, aliases)
        _write(locations_path, INSTITUTION_LOCATION_COLUMNS, locations)
        _write(
            location_reviews_path,
            INSTITUTION_LOCATION_REVIEW_COLUMNS,
            location_reviews,
        )
        _write(hierarchy_path, INSTITUTION_HIERARCHY_COLUMNS, migrated_hierarchy)
        _write(review_queue_path, INSTITUTION_REVIEW_QUEUE_COLUMNS, review_queue)
        save_institutions(entities, institutions_path)
        audit = _append_audit(action="merge", institution_id=target_id, previous_institution_id=source_id, impact=impact, confirmation=phrase, review_note=review_note, created_by="local-admin", audit_path=audit_path)
    except Exception:
        for path, content in snapshots.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise
    return {"source": dict(source), "target": dict(target), "impact": impact, "audit": audit}
