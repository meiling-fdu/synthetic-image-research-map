#!/usr/bin/env python3
"""Shared durable paper-exclusion reading, matching, and writing helpers."""

from __future__ import annotations

import csv
import json
import re
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

try:
    from .curated_schema import (
        ALLOWED_EXCLUSION_REASONS,
        CURATED_DATA_DIR,
        PAPER_EXCLUSION_COLUMNS,
    )
except ImportError:
    from curated_schema import (
        ALLOWED_EXCLUSION_REASONS,
        CURATED_DATA_DIR,
        PAPER_EXCLUSION_COLUMNS,
    )


DEFAULT_EXCLUSIONS_PATH = CURATED_DATA_DIR / "paper_exclusions.csv"
TRUE_VALUES = {"1", "true", "yes", "y"}


class PaperExclusionError(RuntimeError):
    """An exclusion input or write error suitable for concise reporting."""


def clean(value: Any) -> str:
    return " ".join(str(value if value is not None else "").split())


def parse_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    return clean(value).casefold() in TRUE_VALUES


def normalize_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean(value),
        flags=re.IGNORECASE,
    ).casefold()


def normalize_openalex_url(value: Any) -> str:
    return clean(value).casefold().rstrip("/")


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def record_year(record: Mapping[str, Any]) -> str:
    return clean(record.get("year") or record.get("publication_year"))


def normalized_title_year_key(record: Mapping[str, Any]) -> str:
    title = normalize_title(record.get("title"))
    year = record_year(record)
    return f"{title}|{year}" if title and year else ""


def all_identity_keys(record: Mapping[str, Any]) -> List[str]:
    keys: List[str] = []
    doi = normalize_doi(record.get("doi"))
    openalex_url = normalize_openalex_url(record.get("openalex_url"))
    title_year = normalized_title_year_key(record)
    if doi:
        keys.append(f"doi:{doi}")
    if openalex_url:
        keys.append(f"openalex:{openalex_url}")
    if title_year:
        keys.append(f"title_year:{title_year}")
    return keys


def primary_identity_key(record: Mapping[str, Any]) -> str:
    """Return the required DOI → OpenAlex → title/year match key."""
    keys = all_identity_keys(record)
    return keys[0] if keys else ""


def read_exclusion_rows(
    path: Path = DEFAULT_EXCLUSIONS_PATH,
) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != PAPER_EXCLUSION_COLUMNS:
                raise PaperExclusionError(
                    f"{path} does not have the exact paper-exclusion header"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise PaperExclusionError(f"could not read {path}: {error}") from error
    except (UnicodeError, csv.Error) as error:
        raise PaperExclusionError(f"invalid CSV in {path}: {error}") from error


def write_exclusion_rows(
    rows: Sequence[Mapping[str, Any]],
    path: Path = DEFAULT_EXCLUSIONS_PATH,
) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=PAPER_EXCLUSION_COLUMNS,
                lineterminator="\n",
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        raise PaperExclusionError(f"could not write {path}: {error}") from error


def active_exclusions(
    rows: Iterable[Mapping[str, Any]],
) -> List[Mapping[str, Any]]:
    return [row for row in rows if parse_boolean(row.get("is_active"))]


def build_active_exclusion_index(
    rows: Iterable[Mapping[str, Any]],
) -> Dict[str, List[Mapping[str, Any]]]:
    index: Dict[str, List[Mapping[str, Any]]] = {}
    for row in active_exclusions(rows):
        key = primary_identity_key(row)
        if key:
            index.setdefault(key, []).append(row)
    return index


def record_is_excluded(
    record: Mapping[str, Any],
    active_index: Mapping[str, Sequence[Mapping[str, Any]]],
) -> bool:
    return any(key in active_index for key in all_identity_keys(record))


def records_share_any_identity(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> bool:
    return bool(set(all_identity_keys(left)) & set(all_identity_keys(right)))


def matching_exclusion_rows(
    record: Mapping[str, Any],
    rows: Iterable[Mapping[str, Any]],
    *,
    active_only: bool = False,
) -> List[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if (not active_only or parse_boolean(row.get("is_active")))
        and records_share_any_identity(record, row)
    ]


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def exclusion_row_from_paper(
    paper: Mapping[str, Any],
    reason: str,
    review_note: str,
) -> Dict[str, str]:
    if reason not in ALLOWED_EXCLUSION_REASONS:
        raise PaperExclusionError(f"unsupported exclusion reason: {reason!r}")
    if not clean(review_note):
        raise PaperExclusionError("review_note is required")
    if not primary_identity_key(paper):
        raise PaperExclusionError(
            "paper requires a DOI, OpenAlex URL, or title + year identity"
        )
    return {
        "exclusion_id": f"exclusion-{uuid.uuid4().hex}",
        "paper_id": clean(paper.get("paper_id")),
        "title": clean(paper.get("title")),
        "year": record_year(paper),
        "doi": clean(paper.get("doi")),
        "openalex_url": clean(paper.get("openalex_url")),
        "reason": reason,
        "review_note": clean(review_note),
        "excluded_from_public_preview": "true",
        "excluded_from_map": "true",
        "is_active": "true",
        "created_at": utc_timestamp(),
        "created_by": "local_admin",
        "restored_at": "",
        "restore_note": "",
        "source_database": clean(paper.get("source_database")),
        "metadata_source": clean(paper.get("metadata_source")),
    }


def upsert_active_exclusion(
    paper: Mapping[str, Any],
    reason: str,
    review_note: str,
    path: Path = DEFAULT_EXCLUSIONS_PATH,
) -> Dict[str, Any]:
    rows = read_exclusion_rows(path)
    matches = matching_exclusion_rows(paper, rows, active_only=True)
    if matches:
        existing = matches[0]
        existing_note = clean(existing.get("review_note"))
        requested_note = clean(review_note)
        if requested_note and requested_note != existing_note:
            existing["review_note"] = requested_note
            write_exclusion_rows(rows, path)
            return {
                "status": "updated",
                "already_excluded": True,
                "exclusion_id": clean(existing.get("exclusion_id")),
            }
        return {
            "status": "already_excluded",
            "already_excluded": True,
            "exclusion_id": clean(existing.get("exclusion_id")),
        }

    row = exclusion_row_from_paper(paper, reason, review_note)
    rows.append(row)
    write_exclusion_rows(rows, path)
    return {
        "status": "created",
        "already_excluded": False,
        "exclusion_id": row["exclusion_id"],
    }


def restore_active_exclusions(
    paper: Mapping[str, Any],
    restore_note: str,
    path: Path = DEFAULT_EXCLUSIONS_PATH,
) -> Dict[str, Any]:
    note = clean(restore_note)
    if not note:
        raise PaperExclusionError("restore_note is required")
    rows = read_exclusion_rows(path)
    matches = matching_exclusion_rows(paper, rows, active_only=True)
    if not matches:
        return {"status": "already_restored", "restored": 0}
    restored_at = utc_timestamp()
    for row in matches:
        row["is_active"] = "false"
        row["restored_at"] = restored_at
        row["restore_note"] = note
    write_exclusion_rows(rows, path)
    return {"status": "restored", "restored": len(matches)}


def read_json_records(path: Path) -> List[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PaperExclusionError(f"could not read {path}: {error}") from error
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise PaperExclusionError(f"{path} does not contain a records array")
    return [dict(record) for record in records if isinstance(record, dict)]
