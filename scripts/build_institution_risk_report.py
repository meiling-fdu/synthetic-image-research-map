#!/usr/bin/env python3
"""Build an explainable paper-level institution review priority report.

This script uses local candidate, review, backlog, and override files only. Its
scores are review heuristics, not probabilities or automatic corrections.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple


DEFAULT_PAPERS = Path("data/processed/openalex_candidate_papers_in_scope.csv")
DEFAULT_AFFILIATIONS = Path(
    "data/processed/openalex_candidate_affiliations_geocoded.csv"
)
DEFAULT_REVIEW_QUEUE = Path("data/manual/institution_record_review_queue.csv")
DEFAULT_BACKLOG = Path("data/manual/correction_backlog.csv")
DEFAULT_RECORD_OVERRIDES = Path("data/manual/institution_record_overrides.csv")
DEFAULT_AUTHOR_OVERRIDES = Path("data/manual/institution_author_overrides.csv")
DEFAULT_OUTPUT = Path("data/manual/institution_paper_risk_report.csv")

OUTPUT_COLUMNS = [
    "title",
    "year",
    "risk_score",
    "risk_level",
    "main_reasons",
    "current_institutions",
    "current_countries",
    "current_institution_authors",
    "raw_affiliation_evidence",
    "review_action",
    "notes",
]

PAPER_COLUMNS = {"openalex_id", "title", "year"}
AFFILIATION_COLUMNS = {
    "openalex_id",
    "author_name",
    "institution_name",
    "country",
    "country_code",
    "raw_affiliation_text",
}
REVIEW_COLUMNS = {
    "title",
    "year",
    "author",
    "institution",
    "current_country_code",
    "raw_affiliation",
    "reason",
}
BACKLOG_COLUMNS = {
    "item_id",
    "category",
    "title",
    "year",
    "problem_type",
    "current_problem",
    "expected_correction",
    "evidence",
    "priority",
    "status",
}
RECORD_OVERRIDE_COLUMNS = {"title", "year", "mode", "institution"}
AUTHOR_OVERRIDE_COLUMNS = {"title", "year", "institution", "authors"}

ORGANIZATION_WORDS = {
    "academy",
    "college",
    "company",
    "corporation",
    "group",
    "institute",
    "institution",
    "laboratory",
    "research",
    "school",
    "university",
}
INSTITUTION_STOPWORDS = ORGANIZATION_WORDS | {
    "and",
    "center",
    "centre",
    "for",
    "national",
    "of",
    "science",
    "sciences",
    "technology",
    "the",
}
COUNTRY_TERMS = {
    "CN": {"china"},
    "FR": {"france"},
    "GB": {"great britain", "united kingdom", "uk"},
    "GR": {"greece"},
    "IN": {"india"},
    "IT": {"italy"},
    "MO": {"macao", "macau"},
    "NO": {"norway"},
    "SG": {"singapore"},
    "TR": {"turkey", "turkiye"},
    "US": {"united states", "usa"},
}

# Conservative local aliases seen in the review queue. These lower priority;
# they never rewrite an institution name.
ALIAS_EVIDENCE = {
    "altinbas university": {"altinbas university"},
    "centre for research and technology hellas": {"certh"},
    "consorzio nazionale interuniversitario per le telecomunicazioni": {
        "cnit",
        "national inter university consortium for telecommunications",
    },
    "information technologies institute": {"certh iti", "iti"},
    "hindustan institute of technology and science": {
        "hindusthan institute of technology"
    },
    "institut d electronique de microelectronique et de nanotechnologie": {
        "iemn"
    },
    "institut national de recherche en sciences et technologies du numerique": {
        "inria"
    },
    "istituto di scienza e tecnologie dell informazione alessandro faedo": {
        "isti cnr"
    },
    "meta united states": {"facebook ai"},
    "national research council": {"consiglio nazionale delle ricerche"},
    "university of padua": {"university of padova"},
}
GENERIC_INSTITUTION_NAMES = {"global university"}
SUBUNIT_WORDS = {"center", "centre", "college", "department", "laboratory", "school"}
NAMED_ORGANIZATION_WORDS = {
    "academy",
    "company",
    "corporation",
    "group",
    "institute",
    "institution",
    "university",
}


class RiskReportError(RuntimeError):
    """An expected input or output error."""


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalized_text(value: Any) -> str:
    text = html.unescape(clean_text(value)).replace("ı", "i")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.casefold()).split())


def parse_year(value: Any) -> Optional[int]:
    try:
        year = int(clean_text(value))
    except ValueError:
        return None
    return year if 0 < year < 10000 else None


def paper_key(title: Any, year: Any) -> Optional[Tuple[str, int]]:
    normalized_title = normalized_text(title)
    parsed_year = parse_year(year)
    if not normalized_title or parsed_year is None:
        return None
    return normalized_title, parsed_year


def read_csv(path: Path, required: Set[str], optional: bool = False) -> List[Dict[str, str]]:
    if not path.exists():
        if optional:
            return []
        raise RiskReportError(f"Required input does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required - set(reader.fieldnames or []))
            if missing:
                raise RiskReportError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise RiskReportError(f"Could not read {path}: {error}") from error


def ordered_unique(values: Iterable[Any]) -> List[str]:
    output: List[str] = []
    seen = set()
    for value in values:
        text = clean_text(value)
        key = normalized_text(text)
        if text and key not in seen:
            seen.add(key)
            output.append(text)
    return output


def parse_authors(value: Any) -> List[str]:
    text = clean_text(value)
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        parsed = None
    if isinstance(parsed, list):
        return ordered_unique(parsed)
    return ordered_unique(re.split(r"\s*;\s*", text))


def preferred_institution(row: Dict[str, str]) -> str:
    return clean_text(row.get("resolved_institution_name")) or clean_text(
        row.get("institution_name")
    )


def preferred_country(row: Dict[str, str]) -> str:
    return (
        clean_text(row.get("resolved_country"))
        or clean_text(row.get("country"))
        or clean_text(row.get("country_code"))
    )


def is_alias_or_parent(institution: Any, raw_affiliation: Any) -> bool:
    institution_key = normalized_text(institution)
    raw_key = normalized_text(raw_affiliation)
    if not institution_key or not raw_key:
        return False
    if institution_key in GENERIC_INSTITUTION_NAMES:
        return False
    if f" {institution_key} " in f" {raw_key} ":
        return True
    aliases = ALIAS_EVIDENCE.get(institution_key, set())
    if any(alias in raw_key for alias in aliases):
        return True
    raw_tokens = set(raw_key.split())
    return bool(raw_tokens & SUBUNIT_WORDS) and not bool(
        raw_tokens & NAMED_ORGANIZATION_WORDS
    )


def explicitly_names_different_institution(
    institution: Any, raw_affiliation: Any
) -> bool:
    institution_key = normalized_text(institution)
    raw_key = normalized_text(raw_affiliation)
    if not institution_key or not raw_key or is_alias_or_parent(institution, raw_affiliation):
        return False
    if institution_key in GENERIC_INSTITUTION_NAMES:
        return True
    if not ORGANIZATION_WORDS.intersection(raw_key.split()):
        return False
    institution_tokens = {
        token
        for token in institution_key.split()
        if token not in INSTITUTION_STOPWORDS and len(token) > 2
    }
    if not institution_tokens:
        return False
    overlap = institution_tokens.intersection(raw_key.split())
    return len(overlap) / len(institution_tokens) <= 0.25


def raw_supports_current_country(raw: Any, country_code: Any) -> bool:
    raw_key = normalized_text(raw)
    code = clean_text(country_code).upper()
    return any(term in raw_key for term in COUNTRY_TERMS.get(code, set()))


def author_alignment_conflict(
    listed_author: Any,
    raw_affiliation: Any,
    paper_authors: Sequence[str],
) -> bool:
    raw_key = normalized_text(raw_affiliation)
    listed_key = normalized_text(listed_author)
    if not raw_key or not listed_key or listed_key in raw_key:
        return False
    return any(
        author_key and author_key != listed_key and author_key in raw_key
        for author_key in (normalized_text(author) for author in paper_authors)
    )


def add_signal(
    signals: Dict[Tuple[str, int], Dict[str, Tuple[int, str]]],
    key: Tuple[str, int],
    code: str,
    score: int,
    reason: str,
) -> None:
    existing = signals[key].get(code)
    if existing is None or score > existing[0]:
        signals[key][code] = (score, reason)


def risk_level(score: int) -> str:
    if score >= 60:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def build_report(
    papers: Sequence[Dict[str, str]],
    affiliations: Sequence[Dict[str, str]],
    review_rows: Sequence[Dict[str, str]],
    backlog_rows: Sequence[Dict[str, str]],
    record_overrides: Sequence[Dict[str, str]],
    author_overrides: Sequence[Dict[str, str]],
) -> Tuple[List[Dict[str, Any]], int]:
    papers_by_key: Dict[Tuple[str, int], Dict[str, Any]] = {}
    paper_key_by_openalex: Dict[str, Tuple[str, int]] = {}
    for row in papers:
        year = row.get("publication_year") or row.get("year")
        key = paper_key(row.get("title"), year)
        if key is None:
            continue
        paper = papers_by_key.setdefault(
            key,
            {
                "title": clean_text(row.get("title")),
                "year": key[1],
                "authors": parse_authors(row.get("authors_ordered")),
            },
        )
        if not paper["authors"]:
            paper["authors"] = parse_authors(row.get("authors"))
        openalex_id = clean_text(row.get("openalex_id"))
        if openalex_id:
            paper_key_by_openalex[openalex_id] = key

    institutions: Dict[Tuple[str, int], List[str]] = defaultdict(list)
    countries: Dict[Tuple[str, int], List[str]] = defaultdict(list)
    institution_authors: Dict[Tuple[str, int], Dict[str, List[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    raw_evidence: Dict[Tuple[str, int], List[str]] = defaultdict(list)
    signals: Dict[Tuple[str, int], Dict[str, Tuple[int, str]]] = defaultdict(dict)

    for row in affiliations:
        key = paper_key_by_openalex.get(clean_text(row.get("openalex_id")))
        if key is None:
            continue
        institution = preferred_institution(row)
        country = preferred_country(row)
        author = clean_text(row.get("author_name"))
        raw = clean_text(row.get("raw_affiliation_text"))
        if institution:
            institutions[key].append(institution)
            if author:
                institution_authors[key][institution].append(author)
        if country:
            countries[key].append(country)
        if raw:
            raw_evidence[key].append(f"{author}: {raw}" if author else raw)
        confidence = clean_text(row.get("resolution_confidence")).casefold()
        needs_review = clean_text(row.get("needs_review")).casefold() in {
            "1",
            "true",
            "yes",
            "y",
        }
        if raw and not institution and ORGANIZATION_WORDS.intersection(
            normalized_text(raw).split()
        ):
            add_signal(
                signals,
                key,
                "unresolved_raw_institution",
                35,
                "Raw affiliation names an organization, but no institution is resolved",
            )
        elif confidence == "low" or needs_review:
            add_signal(
                signals,
                key,
                "low_resolution_confidence",
                25,
                "At least one affiliation has low-confidence or review-required resolution",
            )

    for row in review_rows:
        key = paper_key(row.get("title"), row.get("year"))
        if key not in papers_by_key:
            continue
        institution = clean_text(row.get("institution"))
        raw = clean_text(row.get("raw_affiliation"))
        author = clean_text(row.get("author"))
        reason = clean_text(row.get("reason"))
        if raw:
            raw_evidence[key].append(f"Review row, {author}: {raw}")

        if author_alignment_conflict(
            author, raw, papers_by_key[key].get("authors", [])
        ):
            add_signal(
                signals,
                key,
                "author_institution_alignment",
                70,
                "Raw affiliation contains another paper author's name rather than the listed author",
            )

        alias = is_alias_or_parent(institution, raw)
        if alias:
            add_signal(
                signals,
                key,
                "known_alias_or_parent",
                5,
                "Raw affiliation is consistent with a known alias, translation, or parent/subunit relation",
            )
        elif explicitly_names_different_institution(institution, raw):
            add_signal(
                signals,
                key,
                "different_institution_in_raw",
                60,
                "Raw affiliation appears to name a different institution than the resolved institution",
            )

        if reason.startswith("country_mismatch"):
            if raw_supports_current_country(raw, row.get("current_country_code")):
                add_signal(
                    signals,
                    key,
                    "country_match_or_place_name",
                    5,
                    "Raw text also supports the current country; mismatch may be a place name or multiple affiliation",
                )
            else:
                add_signal(
                    signals,
                    key,
                    "country_mismatch",
                    55,
                    "Raw affiliation country conflicts with the resolved institution country",
                )
                if len(ordered_unique(countries.get(key, []))) > 1:
                    add_signal(
                        signals,
                        key,
                        "suspicious_geographic_outlier",
                        60,
                        "A resolved country is an outlier within the paper and conflicts with raw affiliation evidence",
                    )
        elif reason == "low_institution_name_overlap" and not alias:
            add_signal(
                signals,
                key,
                "low_institution_name_overlap",
                25,
                "Raw and resolved institution names have low overlap",
            )

    override_keys = {
        key
        for row in record_overrides
        if (key := paper_key(row.get("title"), row.get("year"))) is not None
    }
    author_override_keys = {
        key
        for row in author_overrides
        if (key := paper_key(row.get("title"), row.get("year"))) is not None
    }
    verified_keys = override_keys | author_override_keys

    backlog_by_key: Dict[Tuple[str, int], List[Dict[str, str]]] = defaultdict(list)
    included_backlog_cases = 0
    for row in backlog_rows:
        key = paper_key(row.get("title"), row.get("year"))
        if key not in papers_by_key:
            continue
        backlog_by_key[key].append(row)
        included_backlog_cases += 1
        category = clean_text(row.get("category")).casefold()
        status = clean_text(row.get("status")).casefold()
        problem_type = clean_text(row.get("problem_type")).replace("_", " ")
        if category == "suspected_institution_correction":
            add_signal(
                signals,
                key,
                f"backlog_{clean_text(row.get('item_id'))}",
                75,
                f"Known suspicious correction backlog case: {problem_type}",
            )
        elif category == "confirmed_institution_correction" and status not in {
            "implemented_regression_check",
            "verified",
            "complete",
        }:
            add_signal(
                signals,
                key,
                f"backlog_{clean_text(row.get('item_id'))}",
                70,
                f"Confirmed correction still requires follow-through: {problem_type}",
            )
        evidence = clean_text(row.get("evidence"))
        if evidence:
            raw_evidence[key].append(
                f"Backlog {clean_text(row.get('item_id'))}: {evidence}"
            )

    report: List[Dict[str, Any]] = []
    for key, paper in papers_by_key.items():
        paper_signals = signals.get(key, {})
        signal_values = list(paper_signals.values())
        row_max = max((score for score, _ in signal_values), default=0)
        distinct_high_reasons = sum(score >= 50 for score, _ in signal_values)
        score = min(100, row_max + min(15, max(0, distinct_high_reasons - 1) * 5))

        backlog = backlog_by_key.get(key, [])
        has_actionable_backlog = any(
            clean_text(row.get("category")).casefold()
            in {"suspected_institution_correction", "confirmed_institution_correction"}
            and clean_text(row.get("status")).casefold()
            not in {"implemented_regression_check", "verified", "complete"}
            for row in backlog
        )
        verified = key in verified_keys
        if verified and not has_actionable_backlog:
            score = max(5, min(score, 15))
            paper_signals["verified_manual_override"] = (
                5,
                "A manually verified institution or institution-author override exists",
            )

        reasons = [
            reason
            for _, reason in sorted(
                paper_signals.values(), key=lambda item: (-item[0], item[1])
            )
        ]
        if not reasons:
            reasons = ["No specific local institution risk signal detected"]

        if has_actionable_backlog:
            action = (
                "Verify the full author-institution mapping and complete the known "
                "backlog correction using publisher, PDF, or official evidence."
            )
        elif verified:
            action = "Regression-check the confirmed manual override during export."
        elif score >= 60:
            action = (
                "Verify the full author-institution mapping against the publisher "
                "page or PDF before editing manual overrides."
            )
        elif score >= 25:
            action = (
                "Review raw affiliations and an authoritative source; promote only "
                "a confirmed correction."
            )
        else:
            action = "No immediate action; retain OpenAlex resolution as fallback metadata."

        author_groups = []
        for institution in ordered_unique(institutions.get(key, [])):
            authors = ordered_unique(institution_authors[key].get(institution, []))
            if authors:
                author_groups.append(f"{institution}: {', '.join(authors)}")

        notes = []
        if backlog:
            notes.append(
                "Backlog: "
                + ", ".join(
                    f"{clean_text(row.get('item_id'))} ({clean_text(row.get('status'))})"
                    for row in backlog
                )
            )
        if verified:
            notes.append("Confirmed manual override exists")
        notes.append("Heuristic review priority; not a probability or correction")

        report.append(
            {
                "title": paper["title"],
                "year": paper["year"],
                "risk_score": score,
                "risk_level": risk_level(score),
                "main_reasons": " | ".join(ordered_unique(reasons)),
                "current_institutions": " | ".join(
                    ordered_unique(institutions.get(key, []))
                ),
                "current_countries": " | ".join(
                    ordered_unique(countries.get(key, []))
                ),
                "current_institution_authors": " | ".join(author_groups),
                "raw_affiliation_evidence": " | ".join(
                    ordered_unique(raw_evidence.get(key, []))
                ),
                "review_action": action,
                "notes": " | ".join(notes),
            }
        )

    report.sort(
        key=lambda row: (
            -int(row["risk_score"]),
            normalized_text(row["title"]),
            int(row["year"]),
        )
    )
    return report, included_backlog_cases


def write_report(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        raise RiskReportError(f"Could not write {path}: {error}") from error


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a local paper-level institution review risk report."
    )
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--affiliations", type=Path, default=DEFAULT_AFFILIATIONS)
    parser.add_argument("--review-queue", type=Path, default=DEFAULT_REVIEW_QUEUE)
    parser.add_argument("--correction-backlog", type=Path, default=DEFAULT_BACKLOG)
    parser.add_argument("--record-overrides", type=Path, default=DEFAULT_RECORD_OVERRIDES)
    parser.add_argument("--author-overrides", type=Path, default=DEFAULT_AUTHOR_OVERRIDES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        papers = read_csv(args.papers, PAPER_COLUMNS)
        affiliations = read_csv(args.affiliations, AFFILIATION_COLUMNS)
        review_rows = read_csv(args.review_queue, REVIEW_COLUMNS, optional=True)
        backlog_rows = read_csv(args.correction_backlog, BACKLOG_COLUMNS, optional=True)
        record_overrides = read_csv(
            args.record_overrides, RECORD_OVERRIDE_COLUMNS, optional=True
        )
        author_overrides = read_csv(
            args.author_overrides, AUTHOR_OVERRIDE_COLUMNS, optional=True
        )
        report, backlog_cases = build_report(
            papers,
            affiliations,
            review_rows,
            backlog_rows,
            record_overrides,
            author_overrides,
        )
        expected_papers = len(
            {
                key
                for row in papers
                if (
                    key := paper_key(
                        row.get("title"),
                        row.get("publication_year") or row.get("year"),
                    )
                )
                is not None
            }
        )
        if len(report) != expected_papers:
            raise RiskReportError(
                "Paper-level row-count guard failed: "
                f"expected {expected_papers}, built {len(report)}"
            )
        write_report(args.output, report)
    except RiskReportError as error:
        print(f"Error: {error}")
        return 1

    level_counts = {level: 0 for level in ("high", "medium", "low")}
    for row in report:
        level_counts[row["risk_level"]] += 1
    print("Institution paper risk report summary:")
    print(f"  Total papers analyzed: {len(report)}")
    print(f"  High-risk papers: {level_counts['high']}")
    print(f"  Medium-risk papers: {level_counts['medium']}")
    print(f"  Low-risk papers: {level_counts['low']}")
    print(f"  Known backlog cases included: {backlog_cases}")
    print(f"  Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
