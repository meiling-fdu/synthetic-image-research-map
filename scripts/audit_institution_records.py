#!/usr/bin/env python3
"""Audit local candidate affiliations for likely institution false matches."""

from __future__ import annotations

import argparse
import csv
import re
import tempfile
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPERS = ROOT / "data/processed/openalex_candidate_papers_in_scope.csv"
DEFAULT_AFFILIATIONS = (
    ROOT / "data/processed/openalex_candidate_affiliations_geocoded.csv"
)
DEFAULT_OVERRIDES = ROOT / "data/manual/institution_record_overrides.csv"
DEFAULT_OUTPUT = ROOT / "data/manual/institution_record_review_queue.csv"
OUTPUT_COLUMNS = (
    "title",
    "year",
    "author",
    "institution",
    "current_country",
    "current_country_code",
    "raw_affiliation",
    "reason",
    "suggested_action",
    "suggested_institution",
    "confidence",
    "notes",
)
GENERIC_TOKENS = {
    "and", "college", "department", "engineering", "for", "institute",
    "of", "research", "school", "science", "sciences", "technology", "the",
    "university",
}
COUNTRY_ALIASES = {
    "AU": {"australia"},
    "CA": {"canada"},
    "CN": {"china"},
    "DE": {"germany"},
    "ES": {"spain"},
    "FR": {"france"},
    "GB": {"united kingdom", "uk"},
    "IN": {"india"},
    "IT": {"italy"},
    "JP": {"japan"},
    "KR": {"south korea", "korea"},
    "NO": {"norway"},
    "RU": {"russia", "russian federation"},
    "SG": {"singapore"},
    "US": {"united states", "usa"},
}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--affiliations", type=Path, default=DEFAULT_AFFILIATIONS)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).casefold()
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", text))


def tokens(value: object) -> Set[str]:
    return {
        token for token in normalize(value).split()
        if len(token) > 2 and token not in GENERIC_TOKENS
    }


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def paper_key(title: object, year: object) -> Tuple[str, str]:
    return normalize(title), clean(year)


def paper_index(rows: Iterable[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    return {
        clean(row.get("openalex_id") or row.get("openalex_url")).casefold().rstrip("/"): row
        for row in rows
        if clean(row.get("openalex_id") or row.get("openalex_url"))
    }


def explicit_country_mismatch(raw: str, current_code: str) -> Optional[str]:
    normalized_raw = normalize(raw)
    for code, aliases in COUNTRY_ALIASES.items():
        if code != current_code and any(
            re.search(rf"\b{re.escape(alias)}\b", normalized_raw)
            for alias in aliases
        ):
            return code
    return None


def classify(row: Dict[str, str]) -> Optional[Tuple[str, str, str, str]]:
    institution = clean(
        row.get("resolved_institution_name") or row.get("institution_name")
    )
    raw = clean(row.get("raw_affiliation_text"))
    normalized_institution = normalize(institution)
    normalized_raw = normalize(raw)
    if not institution or not raw:
        return None

    if normalized_institution == "mit university" and "rmit university" in normalized_raw:
        return (
            "acronym_confusion_rmit_mit",
            "replace paper institution records",
            "RMIT University",
            "high",
        )
    if normalized_institution in {
        "institute of engineering science",
        "indian institute of technology indore",
    } and "indian institute of engineering science and technology" in normalized_raw:
        return (
            "institution_name_confusion_iiest",
            "replace paper institution records",
            "Indian Institute of Engineering Science and Technology Shibpur",
            "high",
        )
    if normalized_institution.startswith("unge aksjon"):
        suggested = "University of Oslo" if "university of oslo" in normalized_raw else ""
        return (
            "known_unrelated_organization",
            "replace paper institution records" if suggested else "manual review",
            suggested,
            "high" if suggested else "medium",
        )

    current_code = clean(
        row.get("resolved_country") or row.get("country_code") or row.get("country")
    ).upper()
    suggested_code = explicit_country_mismatch(raw, current_code)
    if suggested_code:
        return (
            f"country_mismatch_raw_text_suggests_{suggested_code}",
            "manual review",
            "",
            "medium",
        )

    institution_tokens = tokens(institution)
    raw_tokens = tokens(raw)
    if institution_tokens and not institution_tokens.intersection(raw_tokens):
        return (
            "low_institution_name_overlap",
            "manual review",
            "",
            "low",
        )
    return None


def write_atomic(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    papers = paper_index(read_csv(args.papers))
    affiliations = read_csv(args.affiliations)
    override_keys = {
        paper_key(row.get("title"), row.get("year"))
        for row in read_csv(args.overrides)
        if clean(row.get("mode")).casefold() == "replace"
    }
    queue = []
    covered_findings = 0
    seen = set()
    for affiliation in affiliations:
        paper_id = clean(affiliation.get("openalex_id")).casefold().rstrip("/")
        paper = papers.get(paper_id)
        if not paper:
            continue
        finding = classify(affiliation)
        if not finding:
            continue
        reason, action, suggested, confidence = finding
        key = paper_key(
            paper.get("title"), paper.get("publication_year") or paper.get("year")
        )
        if key in override_keys:
            covered_findings += 1
            continue
        output = {
            "title": clean(paper.get("title")),
            "year": clean(paper.get("publication_year") or paper.get("year")),
            "author": clean(affiliation.get("author_name")),
            "institution": clean(
                affiliation.get("resolved_institution_name")
                or affiliation.get("institution_name")
            ),
            "current_country": clean(
                affiliation.get("resolved_country") or affiliation.get("country")
            ),
            "current_country_code": clean(affiliation.get("country_code")),
            "raw_affiliation": clean(affiliation.get("raw_affiliation_text")),
            "reason": reason,
            "suggested_action": action,
            "suggested_institution": suggested,
            "confidence": confidence,
            "notes": "Automatic local audit finding; verify before adding an override.",
        }
        dedupe_key = tuple(output[column] for column in OUTPUT_COLUMNS[:-1])
        if dedupe_key not in seen:
            seen.add(dedupe_key)
            queue.append(output)

    queue.sort(key=lambda row: (row["title"].casefold(), row["author"].casefold()))
    if not args.dry_run:
        write_atomic(args.output, queue)
    print(f"Affiliation rows audited: {len(affiliations)}")
    print(f"Suspicious findings covered by confirmed overrides: {covered_findings}")
    print(f"Additional review queue rows: {len(queue)}")
    print(f"Output: {args.output}{' (dry run)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
