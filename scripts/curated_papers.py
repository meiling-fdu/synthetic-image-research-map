#!/usr/bin/env python3
"""Validate and atomically create records in the curated paper database."""

from __future__ import annotations

import csv
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

try:
    from .curated_schema import (
        ALLOWED_CURATION_STATUSES,
        ALLOWED_REVIEW_STATUSES,
        ALLOWED_TASKS,
        CURATED_DATA_DIR,
        PAPERS_COLUMNS,
    )
    from .paper_exclusions import (
        all_identity_keys,
        clean,
        normalized_title_year_key,
    )
except ImportError:
    from curated_schema import (
        ALLOWED_CURATION_STATUSES,
        ALLOWED_REVIEW_STATUSES,
        ALLOWED_TASKS,
        CURATED_DATA_DIR,
        PAPERS_COLUMNS,
    )
    from paper_exclusions import all_identity_keys, clean, normalized_title_year_key


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


def _authors_text(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(clean(author) for author in value if clean(author))
    return clean(value)


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def normalize_paper_draft(draft: Mapping[str, Any]) -> Dict[str, str]:
    title = clean(draft.get("title"))
    year = clean(draft.get("year"))
    task = clean(draft.get("task"))
    if not title:
        raise CuratedPaperError("title is required")
    if not YEAR_RE.fullmatch(year):
        raise CuratedPaperError("year must be a four-digit integer")
    if task not in ALLOWED_TASKS:
        raise CuratedPaperError(
            "task must be one of " + ", ".join(sorted(ALLOWED_TASKS))
        )

    source_database = clean(draft.get("source_database")).casefold()
    if source_database not in {"openalex", "manual"}:
        raise CuratedPaperError("source_database must be openalex or manual")
    metadata_source = (
        "openalex" if source_database == "openalex" else "manual"
    )
    curation_status = (
        "manually_confirmed"
        if source_database == "openalex"
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
        "publication_type": clean(draft.get("publication_type")),
        "abstract": clean(draft.get("abstract")),
        "task": task,
        "subtask": clean(draft.get("subtask")),
        "scope_status": clean(draft.get("scope_status")) or "in_scope",
        "source_database": source_database,
        "metadata_source": metadata_source,
        "curation_status": curation_status,
        "review_status": review_status,
        "review_note": clean(draft.get("review_note")),
    }
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
