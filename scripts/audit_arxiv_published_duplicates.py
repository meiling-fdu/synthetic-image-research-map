#!/usr/bin/env python3
"""Audit likely arXiv/published duplicate papers using local metadata only."""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPERS = REPOSITORY_ROOT / "data" / "curated" / "papers.csv"
DEFAULT_ARXIV_LINKS = REPOSITORY_ROOT / "data" / "manual" / "paper_arxiv_links.csv"
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT / "data" / "manual" / "arxiv_published_duplicate_review.csv"
)
OUTPUT_COLUMNS = (
    "canonical_title",
    "published_title",
    "arxiv_title",
    "published_openalex_id",
    "arxiv_openalex_id",
    "published_doi",
    "arxiv_doi",
    "arxiv_id",
    "published_source",
    "arxiv_source",
    "recommended_action",
    "confidence",
    "notes",
)
ARXIV_DOI_RE = re.compile(r"^10\.48550/arxiv\.(.+)$", re.IGNORECASE)
ARXIV_ID_RE = re.compile(r"(?:arxiv:|arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5})(?:v\d+)?", re.I)


def clean(value: Any) -> str:
    return " ".join(str(value if value is not None else "").split())


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalize_doi(value: Any) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", clean(value), flags=re.I).casefold()


def normalize_arxiv_id(*values: Any) -> str:
    for value in values:
        text = clean(value)
        doi_match = ARXIV_DOI_RE.match(normalize_doi(text))
        if doi_match:
            text = doi_match.group(1)
        match = ARXIV_ID_RE.search(text)
        if match:
            return match.group(1)
    return ""


def openalex_id(record: Mapping[str, Any]) -> str:
    value = clean(record.get("openalex_url") or record.get("openalex_id")).rstrip("/")
    return value.rsplit("/", 1)[-1] if value else ""


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def record_key(record: Mapping[str, Any]) -> str:
    if openalex_id(record):
        return f"openalex:{openalex_id(record).casefold()}"
    doi = normalize_doi(record.get("doi"))
    if doi:
        return f"doi:{doi}"
    arxiv_id = normalize_arxiv_id(
        record.get("arxiv_id"), record.get("arxiv_url"), record.get("doi")
    )
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    return f"title:{normalize_title(record.get('title'))}|{clean(record.get('year'))}"


def merge_records(*sources: Iterable[Mapping[str, Any]]) -> List[Dict[str, str]]:
    merged: Dict[str, Dict[str, str]] = {}
    for rows in sources:
        for raw in rows:
            record = {key: clean(value) for key, value in raw.items()}
            key = record_key(record)
            existing = merged.setdefault(key, {})
            # Earlier inputs have priority; curated metadata is supplied first.
            for field, value in record.items():
                if value and not existing.get(field):
                    existing[field] = value
    return list(merged.values())


def audit_input_records(
    curated_rows: Sequence[Mapping[str, Any]],
    arxiv_link_rows: Sequence[Mapping[str, Any]],
) -> List[Dict[str, str]]:
    """Keep link observations only for titles present in the curated dataset."""
    curated_titles = {
        normalize_title(row.get("title")) for row in curated_rows
        if normalize_title(row.get("title"))
    }
    relevant_links = [
        row for row in arxiv_link_rows
        if normalize_title(row.get("title")) in curated_titles
    ]
    return merge_records(curated_rows, relevant_links)


def is_arxiv_record(record: Mapping[str, Any]) -> bool:
    doi = normalize_doi(record.get("doi"))
    venue = clean(record.get("venue")).casefold()
    source = clean(record.get("source_database") or record.get("source")).casefold()
    return bool(ARXIV_DOI_RE.match(doi) or "arxiv" in venue or source == "arxiv")


def is_published_record(record: Mapping[str, Any]) -> bool:
    doi = normalize_doi(record.get("doi"))
    venue = clean(record.get("venue"))
    publication_type = clean(record.get("publication_type")).casefold()
    formal_doi = bool(doi and not ARXIV_DOI_RE.match(doi))
    formal_venue = bool(venue and "arxiv" not in venue.casefold())
    return formal_doi or formal_venue or publication_type in {"article", "conference", "proceedings"}


def year_distance(left: Mapping[str, Any], right: Mapping[str, Any]) -> Optional[int]:
    try:
        return abs(int(clean(left.get("year"))) - int(clean(right.get("year"))))
    except ValueError:
        return None


def source_label(record: Mapping[str, Any]) -> str:
    return clean(
        record.get("venue")
        or record.get("source_database")
        or record.get("source")
        or record.get("metadata_source")
    )


def audit_duplicates(records: Sequence[Mapping[str, Any]]) -> List[Dict[str, str]]:
    groups: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        title_key = normalize_title(record.get("title"))
        if title_key:
            groups[title_key].append(record)

    results = []
    seen_pairs = set()
    for group in groups.values():
        published = [record for record in group if is_published_record(record)]
        preprints = [record for record in group if is_arxiv_record(record)]
        for published_record in published:
            for arxiv_record in preprints:
                pair_key = (record_key(published_record), record_key(arxiv_record))
                if pair_key[0] == pair_key[1] or pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                distance = year_distance(published_record, arxiv_record)
                published_arxiv = normalize_arxiv_id(
                    published_record.get("arxiv_id"), published_record.get("arxiv_url"),
                    published_record.get("doi"), published_record.get("paper_url"),
                )
                preprint_arxiv = normalize_arxiv_id(
                    arxiv_record.get("arxiv_id"), arxiv_record.get("arxiv_url"),
                    arxiv_record.get("doi"), arxiv_record.get("paper_url"),
                )
                shared_arxiv = published_arxiv and published_arxiv == preprint_arxiv
                distinct_openalex = bool(
                    openalex_id(published_record)
                    and openalex_id(arxiv_record)
                    and openalex_id(published_record) != openalex_id(arxiv_record)
                )
                close_year = distance is None or distance <= 2
                high_confidence = bool(shared_arxiv and distinct_openalex and close_year)
                plausible = close_year and (shared_arxiv or distinct_openalex)
                action = (
                    "keep_published_attach_arxiv"
                    if high_confidence
                    else "needs_manual_review"
                    if plausible
                    else "not_duplicate"
                )
                confidence = "high" if high_confidence else "medium" if plausible else "low"
                evidence = ["exact normalized title"]
                if shared_arxiv:
                    evidence.append(f"shared arXiv ID {published_arxiv}")
                if distinct_openalex:
                    evidence.append("distinct OpenAlex IDs")
                if distance is not None:
                    evidence.append(f"year distance {distance}")
                results.append({
                    "canonical_title": clean(published_record.get("title")),
                    "published_title": clean(published_record.get("title")),
                    "arxiv_title": clean(arxiv_record.get("title")),
                    "published_openalex_id": openalex_id(published_record),
                    "arxiv_openalex_id": openalex_id(arxiv_record),
                    "published_doi": clean(published_record.get("doi")),
                    "arxiv_doi": clean(arxiv_record.get("doi")),
                    "arxiv_id": published_arxiv or preprint_arxiv,
                    "published_source": source_label(published_record),
                    "arxiv_source": source_label(arxiv_record),
                    "recommended_action": action,
                    "confidence": confidence,
                    "notes": "; ".join(evidence) + ". Diagnostic only; no records changed.",
                })
    return sorted(results, key=lambda row: (row["canonical_title"].casefold(), row["arxiv_openalex_id"]))


def write_review(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--arxiv-links", type=Path, default=DEFAULT_ARXIV_LINKS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    records = audit_input_records(
        read_rows(args.papers), read_rows(args.arxiv_links)
    )
    rows = audit_duplicates(records)
    write_review(rows, args.output)
    high = sum(row["confidence"] == "high" for row in rows)
    manual = sum(row["recommended_action"] == "needs_manual_review" for row in rows)
    print(f"Candidate duplicate groups: {len(rows)}")
    print(f"High-confidence: {high}")
    print(f"Needs manual review: {manual}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
