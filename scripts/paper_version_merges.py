#!/usr/bin/env python3
"""Apply maintainer-confirmed paper-version merges to public preview records."""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping, Sequence, Tuple

try:
    from .curated_schema import PAPER_VERSION_MERGE_COLUMNS, CURATED_DATA_DIR
except ImportError:
    from curated_schema import PAPER_VERSION_MERGE_COLUMNS, CURATED_DATA_DIR


DEFAULT_PAPER_VERSION_MERGES_PATH = (
    CURATED_DATA_DIR / "paper_version_merges.csv"
)


class PaperVersionMergeError(RuntimeError):
    """An invalid paper-version merge input."""


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalize_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean(value),
        flags=re.IGNORECASE,
    ).casefold()


def normalize_url(value: Any) -> str:
    return clean(value).casefold().rstrip("/")


def normalize_arxiv_id(value: Any) -> str:
    value = re.sub(
        r"^https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/",
        "",
        clean(value),
        flags=re.IGNORECASE,
    )
    return re.sub(r"(?:\.pdf)?v\d+$", "", value, flags=re.IGNORECASE).casefold()


def read_paper_version_merges(
    path: Path = DEFAULT_PAPER_VERSION_MERGES_PATH,
) -> list[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != PAPER_VERSION_MERGE_COLUMNS:
                raise PaperVersionMergeError(
                    f"{path} does not have the exact paper-version merge header"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise PaperVersionMergeError(f"could not read {path}: {error}") from error
    except (UnicodeError, csv.Error) as error:
        raise PaperVersionMergeError(f"invalid CSV in {path}: {error}") from error


def active_confirmed_merges(
    rows: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if clean(row.get("status")).casefold() == "confirmed_duplicate"
        and clean(row.get("is_active")).casefold() in {"true", "1", "yes", "y"}
    ]


def _side_matches(
    record: Mapping[str, Any],
    row: Mapping[str, Any],
    prefix: str,
) -> bool:
    """Match a side by its strongest populated identifier."""
    selectors = (
        (
            normalize_url(record.get("openalex_url")),
            normalize_url(row.get(f"{prefix}_openalex_url")),
        ),
        (
            normalize_doi(record.get("doi")),
            normalize_doi(row.get(f"{prefix}_doi")),
        ),
        (
            normalize_arxiv_id(
                record.get("arxiv_id") or record.get("arxiv_url")
            ),
            normalize_arxiv_id(row.get(f"{prefix}_arxiv_id")),
        ),
    )
    for actual, expected in selectors:
        if expected:
            return actual == expected
    expected_title = normalize_title(row.get(f"{prefix}_title"))
    expected_year = clean(row.get(f"{prefix}_year"))
    actual_year = clean(record.get("publication_year") or record.get("year"))
    return bool(
        expected_title
        and normalize_title(record.get("title")) == expected_title
        and (not expected_year or actual_year == expected_year)
    )


def record_matches_merge_side(
    record: Mapping[str, Any],
    row: Mapping[str, Any],
    prefix: str,
) -> bool:
    if prefix not in {"canonical", "duplicate"}:
        raise ValueError("prefix must be 'canonical' or 'duplicate'")
    return _side_matches(record, row, prefix)


def _copy_missing(
    target: MutableMapping[str, Any],
    source: Mapping[str, Any],
    field: str,
) -> None:
    if target.get(field) in (None, "", []) and source.get(field) not in (
        None,
        "",
        [],
    ):
        target[field] = source[field]


def _merge_arxiv_metadata(
    canonical: MutableMapping[str, Any],
    duplicate: Mapping[str, Any],
    row: Mapping[str, Any],
) -> None:
    arxiv_id = clean(
        canonical.get("arxiv_id")
        or duplicate.get("arxiv_id")
        or row.get("duplicate_arxiv_id")
    )
    arxiv_url = clean(
        canonical.get("arxiv_url")
        or duplicate.get("arxiv_url")
        or row.get("duplicate_arxiv_url")
    )
    if arxiv_id and not arxiv_url:
        arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
    if arxiv_id:
        canonical["arxiv_id"] = arxiv_id
    if arxiv_url:
        canonical["arxiv_url"] = arxiv_url
    canonical["has_arxiv_version"] = bool(arxiv_id or arxiv_url)
    if not canonical.get("arxiv_year"):
        canonical["arxiv_year"] = duplicate.get(
            "arxiv_year"
        ) or row.get("duplicate_year")
    for field in ("abstract", "abstract_source"):
        _copy_missing(canonical, duplicate, field)
    merged_version = {
        "title": clean(
            row.get("duplicate_title") or duplicate.get("title")
        ),
        "year": clean(row.get("duplicate_year") or duplicate.get("year")),
        "doi": clean(row.get("duplicate_doi") or duplicate.get("doi")),
        "arxiv_id": clean(
            row.get("duplicate_arxiv_id") or duplicate.get("arxiv_id")
        ),
        "arxiv_url": clean(
            row.get("duplicate_arxiv_url") or duplicate.get("arxiv_url")
        ),
        "openalex_url": clean(
            row.get("duplicate_openalex_url")
            or duplicate.get("openalex_url")
        ),
    }
    versions = canonical.setdefault("merged_versions", [])
    if not isinstance(versions, list):
        versions = []
        canonical["merged_versions"] = versions
    identity = (
        normalize_url(merged_version["openalex_url"]),
        normalize_doi(merged_version["doi"]),
        normalize_arxiv_id(merged_version["arxiv_id"]),
    )
    if any(identity) and not any(
        (
            normalize_url(version.get("openalex_url")),
            normalize_doi(version.get("doi")),
            normalize_arxiv_id(version.get("arxiv_id")),
        )
        == identity
        for version in versions
        if isinstance(version, dict)
    ):
        versions.append(merged_version)


def _institution_identity(record: Mapping[str, Any]) -> str:
    institution_id = clean(
        record.get("institution_id")
        or record.get("canonical_institution_id")
    )
    if institution_id:
        return f"id:{institution_id.casefold()}"
    institution = clean(
        record.get("canonical_institution_name")
        or record.get("institution_name")
        or record.get("institution")
    )
    return f"name:{normalize_title(institution)}"


def _merge_marker_metadata(
    target: MutableMapping[str, Any],
    source: Mapping[str, Any],
) -> None:
    for field in (
        "institution_authors",
        "institution_author_ids",
        "raw_affiliation",
        "affiliations",
    ):
        if not isinstance(source.get(field), list):
            _copy_missing(target, source, field)
            continue
        existing = target.get(field)
        if not isinstance(existing, list):
            existing = []
            target[field] = existing
        seen = {repr(value) for value in existing}
        for value in source[field]:
            if repr(value) not in seen:
                existing.append(value)
                seen.add(repr(value))
    for field in (
        "evidence_url",
        "affiliation_evidence_url",
        "raw_affiliation_text",
    ):
        _copy_missing(target, source, field)


def apply_confirmed_version_merges(
    paper_records: Sequence[Mapping[str, Any]],
    map_records: Sequence[Mapping[str, Any]],
    merge_rows: Sequence[Mapping[str, Any]],
) -> Tuple[list[Dict[str, Any]], list[Dict[str, Any]], Dict[str, int]]:
    """Merge duplicate versions into canonical records without changing author order."""
    papers = [dict(record) for record in paper_records]
    maps = [dict(record) for record in map_records]
    applied = 0
    papers_removed = 0
    markers_removed = 0

    for row in active_confirmed_merges(merge_rows):
        canonical_papers = [
            record for record in papers if _side_matches(record, row, "canonical")
        ]
        duplicate_papers = [
            record for record in papers if _side_matches(record, row, "duplicate")
        ]
        if len(canonical_papers) != 1 or not duplicate_papers:
            continue
        canonical = canonical_papers[0]
        for duplicate in duplicate_papers:
            _merge_arxiv_metadata(canonical, duplicate, row)
            papers.remove(duplicate)
            papers_removed += 1

        canonical_maps = [
            record for record in maps if _side_matches(record, row, "canonical")
        ]
        duplicate_maps = [
            record for record in maps if _side_matches(record, row, "duplicate")
        ]
        for marker in duplicate_maps:
            _merge_arxiv_metadata(marker, marker, row)
            marker.update(
                {
                    field: canonical.get(field)
                    for field in (
                        "paper_id",
                        "title",
                        "year",
                        "publication_year",
                        "venue",
                        "venue_name",
                        "doi",
                        "openalex_url",
                        "paper_url",
                        "primary_url",
                        "publication_type",
                        "task",
                        "subtask",
                        "authors",
                    )
                    if canonical.get(field) not in (None, "", [])
                }
            )
            _merge_arxiv_metadata(marker, canonical, row)

        by_institution: Dict[str, Dict[str, Any]] = {}
        unrelated = [
            record
            for record in maps
            if record not in canonical_maps and record not in duplicate_maps
        ]
        for marker in [*canonical_maps, *duplicate_maps]:
            _merge_arxiv_metadata(marker, canonical, row)
            key = _institution_identity(marker)
            if key not in by_institution:
                by_institution[key] = marker
            else:
                _merge_marker_metadata(by_institution[key], marker)
                markers_removed += 1
        maps = [*unrelated, *by_institution.values()]
        applied += 1

    return papers, maps, {
        "confirmed_version_merges_loaded": len(
            active_confirmed_merges(merge_rows)
        ),
        "confirmed_version_merges_applied": applied,
        "duplicate_papers_removed": papers_removed,
        "duplicate_markers_removed": markers_removed,
    }
