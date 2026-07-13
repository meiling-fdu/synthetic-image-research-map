#!/usr/bin/env python3
"""Stable institution identities and protected administrative operations."""

from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

try:
    from .curated_schema import (
        ALLOWED_INSTITUTION_STATUSES,
        ALLOWED_INSTITUTION_TYPES,
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_AUDIT_COLUMNS,
        INSTITUTION_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
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
        INSTITUTION_LOCATION_COLUMNS,
    )


DEFAULT_INSTITUTIONS_PATH = CURATED_DATA_DIR / "institutions.csv"
DEFAULT_ALIASES_PATH = CURATED_DATA_DIR / "institution_aliases.csv"
DEFAULT_LOCATIONS_PATH = CURATED_DATA_DIR / "institution_locations.csv"
DEFAULT_MAPPINGS_PATH = CURATED_DATA_DIR / "author_institution_mappings.csv"
DEFAULT_AUDIT_PATH = CURATED_DATA_DIR / "institution_audit_log.csv"


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
    created_by: Any, audit_path: Path,
) -> dict[str, str]:
    rows = _read(audit_path, INSTITUTION_AUDIT_COLUMNS)
    now = _timestamp()
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
) -> dict[str, str]:
    """Update location fields only; the stable institution ID cannot be changed."""
    entities = load_institutions(institutions_path)
    entity = _entity(entities, institution_id)
    identifier = clean(entity.get("institution_id"))
    requested = clean(draft.get("institution_id"))
    if requested and requested != identifier:
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
    _write(locations_path, INSTITUTION_LOCATION_COLUMNS, rows)
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
) -> dict[str, str]:
    rows = load_institutions(institutions_path)
    child = _entity(rows, institution_id)
    parent_id = clean(parent_institution_id)
    if parent_id:
        _entity(rows, parent_id)
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
    save_institutions(rows, institutions_path)
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
    for mapping in mappings:
        if clean(mapping.get("institution_id")) == clean(source_institution_id):
            mapping["institution_id"] = clean(target_institution_id)
            mapping["institution"] = clean(target.get("canonical_name"))
            mapping["updated_at"] = _timestamp()
    aliases = _read(aliases_path, INSTITUTION_ALIAS_COLUMNS)
    if not any(normalize_institution(row.get("alias_name")) == normalize_institution(source.get("canonical_name")) for row in aliases):
        aliases.append({"alias_id": alias_id_for(source.get("canonical_name")), "alias_name": clean(source.get("canonical_name")), "institution_id": clean(target_institution_id), "canonical_institution_name": clean(target.get("canonical_name")), "alias_language": "", "alias_source": "institution-merge", "review_status": "confirmed", "notes": clean(review_note)})
    source["institution_status"] = "merged"
    source["updated_at"] = _timestamp()
    _write(mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS, mappings)
    _write(aliases_path, INSTITUTION_ALIAS_COLUMNS, aliases)
    save_institutions(entities, institutions_path)
    audit = _append_audit(action="merge", institution_id=clean(target_institution_id), previous_institution_id=clean(source_institution_id), impact=impact, confirmation=phrase, review_note=review_note, created_by="local-admin", audit_path=audit_path)
    return {"source": dict(source), "target": dict(target), "impact": impact, "audit": audit}
