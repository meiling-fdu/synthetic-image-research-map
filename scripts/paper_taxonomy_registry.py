#!/usr/bin/env python3
"""Read and join the curated paper-taxonomy registry at the public boundary."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

try:
    from .curated_export import PaperIdentityCache, PaperIdentityIndex
    from .curated_schema import PAPER_TAXONOMY_COLUMNS
    from .paper_taxonomy import taxonomy_from_record
except ImportError:
    from curated_export import PaperIdentityCache, PaperIdentityIndex
    from curated_schema import PAPER_TAXONOMY_COLUMNS
    from paper_taxonomy import taxonomy_from_record


DEFAULT_PAPER_TAXONOMY_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "curated" / "paper_taxonomy.csv"
)
DIMENSIONS = ("tasks", "image_scopes", "research_types")
REVIEW_STATUSES = frozenset({"reviewed", "needs_review"})


class PaperTaxonomyRegistryError(RuntimeError):
    """Raised when registry membership, identity, or schema is invalid."""


def read_paper_taxonomy_registry(
    path: Path = DEFAULT_PAPER_TAXONOMY_PATH,
) -> list[Dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != PAPER_TAXONOMY_COLUMNS:
                raise PaperTaxonomyRegistryError(
                    f"{path} does not have the exact paper-taxonomy header"
                )
            rows = [dict(row) for row in reader]
    except OSError as error:
        raise PaperTaxonomyRegistryError(f"could not read {path}: {error}") from error
    except (UnicodeError, csv.Error) as error:
        raise PaperTaxonomyRegistryError(f"invalid CSV in {path}: {error}") from error

    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        taxonomy_id = str(row.get("taxonomy_id") or "").strip()
        if not taxonomy_id:
            raise PaperTaxonomyRegistryError(
                f"{path}:{row_number}: taxonomy_id is required"
            )
        if taxonomy_id in seen_ids:
            raise PaperTaxonomyRegistryError(
                f"{path}:{row_number}: duplicate taxonomy_id {taxonomy_id!r}"
            )
        seen_ids.add(taxonomy_id)
        taxonomy = taxonomy_from_record(row)
        statuses = []
        for dimension in DIMENSIONS:
            status = str(row.get(f"{dimension}_status") or "").strip()
            if status not in REVIEW_STATUSES:
                raise PaperTaxonomyRegistryError(
                    f"{path}:{row_number}: invalid {dimension}_status {status!r}"
                )
            statuses.append(status)
            reason = str(row.get(f"{dimension}_review_reason") or "").strip()
            if status == "needs_review" and not reason:
                raise PaperTaxonomyRegistryError(
                    f"{path}:{row_number}: {dimension}_review_reason is required"
                )
        expected = "needs_review" if "needs_review" in statuses else "reviewed"
        if row.get("taxonomy_status") != expected:
            raise PaperTaxonomyRegistryError(
                f"{path}:{row_number}: taxonomy_status must be {expected!r}"
            )
    return rows


def public_taxonomy_fields(row: Mapping[str, Any]) -> Dict[str, Any]:
    taxonomy = taxonomy_from_record(dict(row))
    review = {
        dimension: {
            "status": row[f"{dimension}_status"],
            **(
                {"reason": row[f"{dimension}_review_reason"]}
                if row[f"{dimension}_review_reason"]
                else {}
            ),
        }
        for dimension in DIMENSIONS
    }
    return {
        **taxonomy,
        "taxonomy_status": row["taxonomy_status"],
        "taxonomy_review": review,
    }


def apply_paper_taxonomy_registry(
    papers: Sequence[Dict[str, Any]],
    map_records: Sequence[Dict[str, Any]],
    registry_rows: Sequence[Mapping[str, Any]],
) -> Dict[str, int]:
    """Join taxonomy after public paper identity reconciliation, with exact coverage."""
    if len(registry_rows) != len(papers):
        raise PaperTaxonomyRegistryError(
            "paper-taxonomy registry/public membership mismatch: "
            f"{len(registry_rows)} registry rows for {len(papers)} public papers"
        )
    cache = PaperIdentityCache()
    registry_index = PaperIdentityIndex(registry_rows, cache)
    matched_registry: set[int] = set()
    for paper in papers:
        matches = registry_index.matches(paper)
        if len(matches) != 1:
            raise PaperTaxonomyRegistryError(
                "paper-taxonomy identity match must be exactly one for "
                f"{paper.get('title')!r}; found {len(matches)}"
            )
        row = matches[0]
        matched_registry.add(id(row))
        paper.update(public_taxonomy_fields(row))
    if len(matched_registry) != len(registry_rows):
        raise PaperTaxonomyRegistryError(
            "paper-taxonomy registry contains identities outside the public corpus"
        )

    paper_index = PaperIdentityIndex(papers, cache)
    for marker in map_records:
        matches = paper_index.matches(marker)
        if len(matches) != 1:
            raise PaperTaxonomyRegistryError(
                "map record must resolve to exactly one taxonomy-bearing public paper for "
                f"{marker.get('title')!r}; found {len(matches)}"
            )
        marker.update(
            {
                key: value
                for key, value in matches[0].items()
                if key in (*DIMENSIONS, "taxonomy_status", "taxonomy_review")
            }
        )
    return {
        "registry_rows": len(registry_rows),
        "public_papers_matched": len(matched_registry),
        "map_records_matched": len(map_records),
    }
