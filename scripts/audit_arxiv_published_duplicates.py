#!/usr/bin/env python3
"""Audit likely arXiv/formal-publication duplicate paper pairs."""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

try:
    from .paper_version_merges import (
        DEFAULT_PAPER_VERSION_MERGES_PATH,
        active_confirmed_merges,
        read_paper_version_merges,
    )
except ImportError:
    from paper_version_merges import (
        DEFAULT_PAPER_VERSION_MERGES_PATH,
        active_confirmed_merges,
        read_paper_version_merges,
    )


DEFAULT_PAPERS = Path("web/data/public_preview_papers.json")
DEFAULT_OUTPUT = Path("docs/arxiv_published_duplicate_audit.csv")
REPORT_COLUMNS = (
    "canonical_candidate_title",
    "duplicate_candidate_title",
    "canonical_year",
    "duplicate_year",
    "canonical_venue",
    "duplicate_venue",
    "canonical_doi",
    "duplicate_doi",
    "arxiv_id",
    "arxiv_url",
    "canonical_openalex_id",
    "duplicate_openalex_id",
    "title_similarity_score",
    "author_overlap_score",
    "abstract_similarity_score",
    "task_similarity",
    "recommended_action",
    "reason",
)


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalized(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    text = re.sub(r"<[^>]+>|\$|\^|\\", " ", text)
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalized_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean(value),
        flags=re.IGNORECASE,
    ).casefold()


def year(record: Mapping[str, Any]) -> int:
    try:
        return int(record.get("publication_year") or record.get("year") or 0)
    except (TypeError, ValueError):
        return 0


def author_names(record: Mapping[str, Any]) -> set[str]:
    result = set()
    for value in record.get("authors") or []:
        name = clean(
            value.get("name") or value.get("author")
            if isinstance(value, dict)
            else value
        )
        if name.count(",") == 1:
            family, given = (part.strip() for part in name.split(",", 1))
            name = f"{given} {family}"
        name = normalized(name)
        if name:
            result.add(name)
    return result


def similarity(left: Any, right: Any) -> float:
    return difflib.SequenceMatcher(None, normalized(left), normalized(right)).ratio()


def is_preprint(record: Mapping[str, Any]) -> bool:
    venue = normalized(record.get("venue") or record.get("venue_name"))
    publication_type = normalized(record.get("publication_type"))
    doi = normalized_doi(record.get("doi"))
    return bool(
        "arxiv" in venue
        or publication_type in {"preprint", "posted content"}
        or doi.startswith("10.48550/arxiv.")
    )


def author_overlap(left: Mapping[str, Any], right: Mapping[str, Any]) -> float:
    left_names = author_names(left)
    right_names = author_names(right)
    if not left_names or not right_names:
        return 0.0
    return len(left_names & right_names) / min(len(left_names), len(right_names))


def pair_is_candidate(
    preprint: Mapping[str, Any],
    published: Mapping[str, Any],
) -> bool:
    difference = year(published) - year(preprint)
    if difference < 0 or difference > 2:
        return False
    same_non_arxiv_doi = (
        normalized_doi(preprint.get("doi"))
        == normalized_doi(published.get("doi"))
        and not normalized_doi(preprint.get("doi")).startswith("10.48550/arxiv.")
    )
    title_score = similarity(preprint.get("title"), published.get("title"))
    overlap = author_overlap(preprint, published)
    return same_non_arxiv_doi or (
        title_score >= 0.60 and overlap > 0
    )


def _confirmed_lookup(
    merge_rows: Sequence[Mapping[str, Any]],
) -> set[tuple[str, str]]:
    return {
        (
            normalized(row.get("canonical_title")),
            normalized(row.get("duplicate_title")),
        )
        for row in active_confirmed_merges(merge_rows)
    }


def classify_pair(
    preprint: Mapping[str, Any],
    published: Mapping[str, Any],
    confirmed_lookup: set[tuple[str, str]],
) -> tuple[str, str]:
    key = (
        normalized(published.get("title")),
        normalized(preprint.get("title")),
    )
    if key in confirmed_lookup:
        return (
            "confirmed_duplicate",
            "Maintainer-confirmed merge; identifiers and version metadata are "
            "migrated to the formal publication.",
        )
    return (
        "needs_review",
        "Candidate met the title/year/author screening threshold, but no "
        "maintainer-confirmed merge exists.",
    )


def audit_pairs(
    records: Sequence[Mapping[str, Any]],
    merge_rows: Sequence[Mapping[str, Any]],
) -> list[Dict[str, str]]:
    preprints = [record for record in records if is_preprint(record)]
    published = [record for record in records if not is_preprint(record)]
    confirmed_lookup = _confirmed_lookup(merge_rows)
    rows = []
    for preprint in preprints:
        for formal in published:
            if not pair_is_candidate(preprint, formal):
                continue
            action, reason = classify_pair(preprint, formal, confirmed_lookup)
            left_abstract = clean(preprint.get("abstract"))
            right_abstract = clean(formal.get("abstract"))
            abstract_score = (
                similarity(left_abstract, right_abstract)
                if left_abstract and right_abstract
                else 0.0
            )
            same_task = bool(
                clean(preprint.get("task"))
                and clean(preprint.get("task")) == clean(formal.get("task"))
                and clean(preprint.get("subtask"))
                == clean(formal.get("subtask"))
            )
            rows.append(
                {
                    "canonical_candidate_title": clean(formal.get("title")),
                    "duplicate_candidate_title": clean(preprint.get("title")),
                    "canonical_year": str(year(formal)),
                    "duplicate_year": str(year(preprint)),
                    "canonical_venue": clean(
                        formal.get("venue") or formal.get("venue_name")
                    ),
                    "duplicate_venue": clean(
                        preprint.get("venue") or preprint.get("venue_name")
                    ),
                    "canonical_doi": clean(formal.get("doi")),
                    "duplicate_doi": clean(preprint.get("doi")),
                    "arxiv_id": clean(preprint.get("arxiv_id")),
                    "arxiv_url": clean(preprint.get("arxiv_url")),
                    "canonical_openalex_id": clean(formal.get("openalex_url")),
                    "duplicate_openalex_id": clean(preprint.get("openalex_url")),
                    "title_similarity_score": f"{similarity(preprint.get('title'), formal.get('title')):.3f}",
                    "author_overlap_score": f"{author_overlap(preprint, formal):.3f}",
                    "abstract_similarity_score": f"{abstract_score:.3f}",
                    "task_similarity": "same" if same_task else "different_or_missing",
                    "recommended_action": action,
                    "reason": reason,
                }
            )
    return sorted(
        rows,
        key=lambda row: (
            row["recommended_action"] != "confirmed_duplicate",
            -float(row["title_similarity_score"]),
            row["canonical_candidate_title"].casefold(),
        ),
    )


def read_records(path: Path) -> list[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list) or not all(
        isinstance(record, dict) for record in records
    ):
        raise ValueError(f"{path} does not contain a record list")
    return records


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument(
        "--merges", type=Path, default=DEFAULT_PAPER_VERSION_MERGES_PATH
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    rows = audit_pairs(
        read_records(args.papers),
        read_paper_version_merges(args.merges),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=REPORT_COLUMNS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    counts = {
        action: sum(row["recommended_action"] == action for row in rows)
        for action in ("confirmed_duplicate", "needs_review", "distinct")
    }
    print(
        f"Wrote {len(rows)} candidate pairs to {args.output}: "
        f"{counts['confirmed_duplicate']} confirmed, "
        f"{counts['needs_review']} needs review, {counts['distinct']} distinct."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
