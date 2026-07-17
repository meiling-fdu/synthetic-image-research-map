#!/usr/bin/env python3
"""Validate and atomically create records in the curated paper database."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

try:
    from .curated_schema import (
        ALLOWED_CURATION_STATUSES,
        ALLOWED_ENTRY_TYPES,
        ALLOWED_REVIEW_STATUSES,
        ALLOWED_SCOPE_STATUSES,
        ALLOWED_SUBTASKS,
        ALLOWED_TASKS,
        CURATED_DATA_DIR,
        PAPERS_COLUMNS,
    )
    from .paper_exclusions import (
        all_identity_keys,
        clean,
        normalized_title_year_key,
    )
    from .publication_types import ALLOWED_PUBLICATION_TYPES, normalize_publication_type
    from .venues import (
        VenueRegistryError,
        canonicalize_record,
        display_venue,
        publication_type_for_venue_type,
        read_venue_aliases,
        resolve_venue,
        validate_canonical_venue_fields,
    )
except ImportError:
    from curated_schema import (
        ALLOWED_CURATION_STATUSES,
        ALLOWED_ENTRY_TYPES,
        ALLOWED_REVIEW_STATUSES,
        ALLOWED_SCOPE_STATUSES,
        ALLOWED_SUBTASKS,
        ALLOWED_TASKS,
        CURATED_DATA_DIR,
        PAPERS_COLUMNS,
    )
    from paper_exclusions import all_identity_keys, clean, normalized_title_year_key
    from publication_types import ALLOWED_PUBLICATION_TYPES, normalize_publication_type
    from venues import (
        VenueRegistryError,
        canonicalize_record,
        display_venue,
        publication_type_for_venue_type,
        read_venue_aliases,
        resolve_venue,
        validate_canonical_venue_fields,
    )


DEFAULT_CURATED_PAPERS_PATH = CURATED_DATA_DIR / "papers.csv"
YEAR_RE = re.compile(r"\d{4}")


class CuratedPaperError(RuntimeError):
    """A curated paper validation or write error."""


class DuplicatePaperError(CuratedPaperError):
    """A duplicate create request with structured matching records."""

    def __init__(self, matches: Sequence[Mapping[str, Any]]):
        self.matches = list(matches)
        super().__init__("paper matches an existing preview, curated, or exclusion record")


def read_curated_papers(
    path: Path = DEFAULT_CURATED_PAPERS_PATH,
) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != PAPERS_COLUMNS:
                raise CuratedPaperError(
                    f"{path} does not have the exact curated paper header"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise CuratedPaperError(f"could not read {path}: {error}") from error
    except (UnicodeError, csv.Error) as error:
        raise CuratedPaperError(f"invalid CSV in {path}: {error}") from error


def write_curated_papers(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_CURATED_PAPERS_PATH,
) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=PAPERS_COLUMNS,
                lineterminator="\n",
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        raise CuratedPaperError(f"could not write {path}: {error}") from error


def normalize_author_names(value: Any) -> List[str]:
    """Return author names from supported API, CSV, and JSON value shapes."""
    if value is None:
        return []
    if isinstance(value, Mapping):
        name = clean(
            value.get("name") or value.get("display_name") or value.get("author")
        )
        return [name] if name and name.casefold() != "[object object]" else []
    if isinstance(value, (list, tuple)):
        return [
            name
            for item in value
            for name in normalize_author_names(item)
            if name
        ]
    text = clean(value)
    if not text:
        return []
    if text.startswith(("[", "{")):
        try:
            parsed = json.loads(text)
        except (TypeError, json.JSONDecodeError):
            parsed = None
        if isinstance(parsed, (list, dict)):
            return normalize_author_names(parsed)
    separator = ";" if ";" in text else "|" if "|" in text else None
    names = (
        [clean(item) for item in text.split(separator) if clean(item)]
        if separator
        else [text]
    )
    return [name for name in names if name.casefold() != "[object object]"]


def _authors_text(value: Any) -> str:
    return "; ".join(normalize_author_names(value))


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def apply_canonical_venue_selection(
    draft: Mapping[str, Any],
    *,
    existing: Mapping[str, Any] | None = None,
    venue_aliases_path: Path | None = None,
) -> Dict[str, Any]:
    """Validate a structured selection and preserve historical raw provenance."""
    aliases = read_venue_aliases(venue_aliases_path) if venue_aliases_path else read_venue_aliases()
    venue_id = clean(draft.get("venue_id"))
    supplied_venue = clean(draft.get("venue_name") or draft.get("venue"))
    if venue_id:
        try:
            canonical = validate_canonical_venue_fields(draft, aliases)
        except VenueRegistryError as error:
            raise CuratedPaperError(str(error)) from error
        for field in ("venue_name", "venue_acronym", "venue_type", "venue_track"):
            if clean(draft.get(field)) != canonical[field]:
                raise CuratedPaperError(
                    f"{field} must match canonical venue_id {canonical['venue_id']!r}"
                )
    elif supplied_venue:
        resolved = resolve_venue(
            draft.get("raw_venue") or supplied_venue,
            publication_type=draft.get("publication_type"),
            venue_type=draft.get("venue_type"),
            aliases=aliases,
        )
        if resolved.ambiguity_status == "ambiguous":
            raise CuratedPaperError(
                "venue is ambiguous; leave the canonical venue unchanged and flag it for review"
            )
        if resolved.ambiguity_status != "resolved":
            raise CuratedPaperError(
                "venue is not in the canonical registry; create it through the reviewed venue workflow"
            )
        canonical = validate_canonical_venue_fields(resolved.as_record(), aliases)
    else:
        return {
            "venue": "", "venue_id": "", "venue_name": "", "venue_acronym": "",
            "venue_type": "", "venue_track": "main", "raw_venue": clean((existing or {}).get("raw_venue")),
            "venue_aliases": [], "venue_label": "",
        }
    expected_publication_type = publication_type_for_venue_type(canonical["venue_type"])
    requested_publication_type = normalize_publication_type(draft.get("publication_type"))
    if (
        requested_publication_type
        and requested_publication_type != expected_publication_type
        and draft.get("publication_type_override") is not True
    ):
        raise CuratedPaperError(
            "publication_type conflicts with canonical venue_type; explicit override is required"
        )
    replace_provenance = draft.get("replace_raw_venue") is True
    historical_raw = clean((existing or {}).get("raw_venue"))
    if not historical_raw:
        historical_raw = clean((existing or {}).get("venue"))
    raw_venue = (
        clean(draft.get("raw_venue") or supplied_venue)
        if replace_provenance
        else historical_raw or clean(draft.get("raw_venue") or supplied_venue)
    )
    result = {
        **canonical,
        "venue": canonical["venue_name"],
        "raw_venue": raw_venue,
        "venue_aliases": list(canonical.get("aliases", [])),
    }
    result["venue_label"] = display_venue(result)
    result["publication_type"] = requested_publication_type or expected_publication_type
    return result


def normalize_paper_draft(draft: Mapping[str, Any]) -> Dict[str, str]:
    title = clean(draft.get("title"))
    year = clean(draft.get("year"))
    task = clean(draft.get("task"))
    entry_type = clean(draft.get("entry_type")).casefold() or "method"
    subtask = clean(draft.get("subtask"))
    scope_status = clean(draft.get("scope_status")) or "in_scope"
    publication_type = normalize_publication_type(
        draft.get("publication_type"), venue=draft.get("venue")
    ) or ("preprint" if clean(draft.get("source_database")).casefold() == "arxiv" else "")
    if not title:
        raise CuratedPaperError("title is required")
    if not YEAR_RE.fullmatch(year):
        raise CuratedPaperError("year must be a four-digit integer")
    if not publication_type:
        raise CuratedPaperError(
            "publication_type must be one of " + ", ".join(ALLOWED_PUBLICATION_TYPES)
        )
    if task not in ALLOWED_TASKS:
        raise CuratedPaperError(
            "task must be one of " + ", ".join(sorted(ALLOWED_TASKS))
        )
    if entry_type not in ALLOWED_ENTRY_TYPES:
        raise CuratedPaperError(
            "entry_type must be one of "
            + ", ".join(sorted(ALLOWED_ENTRY_TYPES))
        )
    if subtask and subtask not in ALLOWED_SUBTASKS:
        raise CuratedPaperError(
            "subtask must be blank or one of "
            + ", ".join(sorted(ALLOWED_SUBTASKS))
        )
    if scope_status not in ALLOWED_SCOPE_STATUSES:
        raise CuratedPaperError(
            "scope_status must be one of "
            + ", ".join(sorted(ALLOWED_SCOPE_STATUSES))
        )

    source_database = clean(draft.get("source_database")).casefold()
    if source_database not in {"openalex", "arxiv", "manual"}:
        raise CuratedPaperError(
            "source_database must be openalex, arxiv, or manual"
        )
    metadata_source = source_database
    curation_status = (
        "manually_confirmed"
        if source_database in {"openalex", "arxiv"}
        else "manually_added"
    )
    if curation_status not in ALLOWED_CURATION_STATUSES:
        raise CuratedPaperError("unsupported curation status")
    review_status = clean(draft.get("review_status")) or "pending"
    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise CuratedPaperError(
            "review_status must be one of "
            + ", ".join(sorted(ALLOWED_REVIEW_STATUSES))
        )

    normalized = {
        "title": title,
        "year": year,
        "authors": _authors_text(draft.get("authors")),
        "venue": clean(draft.get("venue")),
        "doi": clean(draft.get("doi")),
        "arxiv_id": clean(draft.get("arxiv_id")),
        "openalex_url": clean(draft.get("openalex_url")),
        "paper_url": clean(draft.get("paper_url")),
        "publication_type": publication_type,
        "abstract": clean(draft.get("abstract")),
        "task": task,
        "entry_type": entry_type,
        "subtask": subtask,
        "scope_status": scope_status,
        "source_database": source_database,
        "metadata_source": metadata_source,
        "curation_status": curation_status,
        "review_status": review_status,
        "review_note": clean(draft.get("review_note")),
    }
    normalized = canonicalize_record(normalized)
    if not all_identity_keys(normalized):
        raise CuratedPaperError(
            "paper requires a DOI, OpenAlex URL, or title + year identity"
        )
    return normalized


def duplicate_matches(
    paper: Mapping[str, Any],
    datasets: Iterable[tuple[str, Sequence[Mapping[str, Any]]]],
) -> List[Dict[str, Any]]:
    paper_keys = set(all_identity_keys(paper))
    matches = []
    seen = set()
    for source, records in datasets:
        for record in records:
            shared_keys = sorted(paper_keys & set(all_identity_keys(record)))
            if not shared_keys:
                continue
            marker = (
                source,
                clean(record.get("paper_id")),
                clean(record.get("openalex_url")),
                clean(record.get("doi")),
                clean(record.get("title")),
                clean(record.get("year") or record.get("publication_year")),
            )
            if marker in seen:
                continue
            seen.add(marker)
            matches.append(
                {
                    "source": source,
                    "paper_id": marker[1],
                    "openalex_url": marker[2],
                    "doi": marker[3],
                    "title": marker[4],
                    "year": marker[5],
                    "matched_keys": shared_keys,
                }
            )
    return matches


def create_curated_paper(
    draft: Mapping[str, Any],
    *,
    preview_records: Sequence[Mapping[str, Any]],
    exclusion_records: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_CURATED_PAPERS_PATH,
) -> Dict[str, str]:
    normalized = normalize_paper_draft(draft)
    curated_rows = read_curated_papers(path)
    matches = duplicate_matches(
        normalized,
        (
            ("public_preview", preview_records),
            ("curated_papers", curated_rows),
            ("paper_exclusions", exclusion_records),
        ),
    )
    if matches:
        raise DuplicatePaperError(matches)

    title_year = normalized_title_year_key(normalized)
    digest = hashlib.sha256(title_year.encode("utf-8")).hexdigest()[:20]
    now = _timestamp()
    row = {
        "paper_id": f"curated:{digest}",
        **normalized,
        "created_at": now,
        "updated_at": now,
    }
    curated_rows.append(row)
    write_curated_papers(curated_rows, path)
    return row


def update_curated_paper(
    current_paper: Mapping[str, Any],
    draft: Mapping[str, Any],
    *,
    preview_records: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_CURATED_PAPERS_PATH,
    venue_aliases_path: Path | None = None,
) -> Dict[str, str]:
    """Create or update a curated metadata override for one effective paper."""
    title = clean(draft.get("title"))
    year = clean(draft.get("year"))
    task = clean(draft.get("task"))
    entry_type = clean(draft.get("entry_type")).casefold()
    subtask = clean(draft.get("subtask"))
    scope_status = clean(draft.get("scope_status")) or "in_scope"
    publication_type = normalize_publication_type(
        draft.get("publication_type"), venue=draft.get("venue")
    )
    curation_status = (
        clean(draft.get("curation_status")) or "corrected_by_admin"
    )
    review_status = clean(draft.get("review_status")) or "reviewed"
    if not title:
        raise CuratedPaperError("title is required")
    if not YEAR_RE.fullmatch(year):
        raise CuratedPaperError("year must be a four-digit integer")
    if not publication_type:
        raise CuratedPaperError(
            "publication_type must be one of " + ", ".join(ALLOWED_PUBLICATION_TYPES)
        )
    if task not in ALLOWED_TASKS:
        raise CuratedPaperError(
            "task must be one of " + ", ".join(sorted(ALLOWED_TASKS))
        )
    if not entry_type:
        raise CuratedPaperError("entry_type is required")
    if entry_type not in ALLOWED_ENTRY_TYPES:
        raise CuratedPaperError(
            "entry_type must be one of "
            + ", ".join(sorted(ALLOWED_ENTRY_TYPES))
        )
    if subtask and subtask not in ALLOWED_SUBTASKS:
        raise CuratedPaperError(
            "subtask must be blank or one of "
            + ", ".join(sorted(ALLOWED_SUBTASKS))
        )
    if scope_status not in ALLOWED_SCOPE_STATUSES:
        raise CuratedPaperError(
            "scope_status must be one of "
            + ", ".join(sorted(ALLOWED_SCOPE_STATUSES))
        )
    if curation_status not in ALLOWED_CURATION_STATUSES:
        raise CuratedPaperError(
            "curation_status must be one of "
            + ", ".join(sorted(ALLOWED_CURATION_STATUSES))
        )
    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise CuratedPaperError(
            "review_status must be one of "
            + ", ".join(sorted(ALLOWED_REVIEW_STATUSES))
        )

    existing_rows = read_curated_papers(path)
    current_keys = set(all_identity_keys(current_paper))
    existing = next(
        (
            row
            for row in existing_rows
            if clean(current_paper.get("paper_id"))
            and clean(row.get("paper_id")) == clean(current_paper.get("paper_id"))
        ),
        None,
    )
    if existing is None:
        existing = next(
            (
                row
                for row in existing_rows
                if current_keys & set(all_identity_keys(row))
            ),
            None,
        )

    source_database = clean(
        draft.get("source_database")
        or (existing or {}).get("source_database")
        or current_paper.get("source_database")
        or "manual"
    ).casefold()
    if source_database not in {"openalex", "arxiv", "manual"}:
        source_database = "manual"
    normalized = {
        "title": title,
        "year": year,
        "authors": _authors_text(draft.get("authors")),
        "venue": clean(draft.get("venue")),
        "doi": clean(draft.get("doi")),
        "arxiv_id": clean(draft.get("arxiv_id")),
        "openalex_url": clean(draft.get("openalex_url")),
        "paper_url": clean(draft.get("paper_url")),
        "publication_type": publication_type,
        "abstract": clean(draft.get("abstract")),
        "task": task,
        "entry_type": entry_type,
        "subtask": subtask,
        "scope_status": scope_status,
        "source_database": source_database,
        "metadata_source": clean(
            draft.get("metadata_source")
            or (existing or {}).get("metadata_source")
            or current_paper.get("metadata_source")
            or source_database
        ),
        "curation_status": curation_status,
        "review_status": review_status,
        "review_note": clean(draft.get("review_note")),
        "venue_id": clean(draft.get("venue_id")),
        "venue_name": clean(draft.get("venue_name")),
        "venue_acronym": clean(draft.get("venue_acronym")),
        "venue_type": clean(draft.get("venue_type")),
        "venue_track": clean(draft.get("venue_track")),
        "raw_venue": clean(draft.get("raw_venue")),
        "publication_type_override": draft.get("publication_type_override") is True,
        "replace_raw_venue": draft.get("replace_raw_venue") is True,
    }
    venue_fields = apply_canonical_venue_selection(
        normalized,
        existing=existing or current_paper,
        venue_aliases_path=venue_aliases_path,
    )
    normalized.update(venue_fields)
    normalized.pop("publication_type_override", None)
    normalized.pop("replace_raw_venue", None)
    if not all_identity_keys(normalized):
        raise CuratedPaperError(
            "paper requires a DOI, OpenAlex URL, or title + year identity"
        )

    other_curated = [row for row in existing_rows if row is not existing]
    collisions = duplicate_matches(
        normalized,
        (("public_preview", preview_records), ("curated_papers", other_curated)),
    )
    allowed_keys = current_keys | set(all_identity_keys(existing or {}))
    collisions = [
        match
        for match in collisions
        if not (set(match["matched_keys"]) & allowed_keys)
    ]
    if collisions:
        raise DuplicatePaperError(collisions)

    now = _timestamp()
    if existing:
        row = {
            "paper_id": clean(existing.get("paper_id")),
            **normalized,
            "created_at": clean(existing.get("created_at")) or now,
            "updated_at": now,
        }
        existing_rows[existing_rows.index(existing)] = row
    else:
        identity = normalized_title_year_key(normalized)
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
        row = {
            "paper_id": f"curated:{digest}",
            **normalized,
            "created_at": now,
            "updated_at": now,
        }
        existing_rows.append(row)
    write_curated_papers(existing_rows, path)
    return row
