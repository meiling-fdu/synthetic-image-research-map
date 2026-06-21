#!/usr/bin/env python3
"""Triage local institution review findings without external lookups."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / "data/manual/institution_record_review_queue.csv"
DEFAULT_TRIAGE = ROOT / "data/manual/institution_record_review_triage.csv"
DEFAULT_CANDIDATES = ROOT / "data/manual/institution_record_override_candidates.csv"
DEFAULT_AFFILIATIONS = ROOT / "data/processed/openalex_candidate_affiliations_geocoded.csv"
DEFAULT_PAPERS = ROOT / "data/processed/openalex_candidate_papers_in_scope.csv"
TRIAGE_COLUMNS = (
    "title", "year", "author", "current_institution", "current_country",
    "current_country_code", "raw_affiliation", "reason", "triage_label",
    "triage_confidence", "suggested_institution", "suggested_country",
    "suggested_action", "notes",
)
CANDIDATE_COLUMNS = (
    "title", "year", "mode", "institution", "city", "region", "country",
    "country_code", "latitude", "longitude", "institution_authors", "notes",
    "triage_source",
)
ALIASES = (
    (("altinbas university",), ("altinbas university",)),
    (("national research council",), ("consiglio nazionale delle ricerche",)),
    (("consorzio nazionale interuniversitario per le telecomunicazioni",), ("cnit", "national inter university consortium for telecommunications")),
    (("meta",), ("facebook ai",)),
    (("centre for research and technology hellas",), ("certh",)),
    (("information technologies institute",), ("iti", "certh iti")),
    (("institut d electronique de microelectronique et de nanotechnologie",), ("iemn",)),
    (("university of padua",), ("university of padova",)),
    (("institut national de recherche en sciences et technologies du numerique",), ("inria",)),
    (("hindustan institute of technology and science",), ("hindusthan institute of technology",)),
    (("istituto di scienza e tecnologie dell informazione alessandro faedo",), ("isti cnr",)),
)
EXPLICIT_WRONG = {
    "srm institute of science and technology": "Dhanekula Institute of Engineering and Technology",
    "karnatak university": "University of Chakwal",
    "brandman university": "Reichman University",
    "graphic era university": "Graphic Era Hill University",
    "institute of art": "Institute of Artificial Intelligence",
    "global university": "C. V. Raman Global University",
}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--triage-output", type=Path, default=DEFAULT_TRIAGE)
    parser.add_argument("--candidates-output", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--affiliations", type=Path, default=DEFAULT_AFFILIATIONS)
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    return parser.parse_args(argv)


def clean(value: object) -> str:
    return " ".join(html.unescape(str(value or "")).split())


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).casefold()
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("ı", "i").replace("ß", "ss")
    return " ".join(re.findall(r"[a-z0-9]+", text))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_atomic(path: Path, columns: Iterable[str], rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def alias_match(current: str, raw: str) -> bool:
    for current_aliases, raw_aliases in ALIASES:
        if any(alias in current for alias in current_aliases) and any(
            alias in raw for alias in raw_aliases
        ):
            return True
    return False


def starts_with_other_author(author: str, raw: str) -> bool:
    prefix = clean(raw).split(";", 1)[0]
    if ";" not in raw or len(normalize(prefix).split()) not in {2, 3, 4}:
        return False
    return normalize(prefix) not in normalize(author) and normalize(author) not in normalize(prefix)


def triage_row(row: Dict[str, str]) -> Dict[str, str]:
    current = normalize(row.get("institution"))
    raw = normalize(row.get("raw_affiliation"))
    reason = clean(row.get("reason"))
    label = "needs_manual_check"
    confidence = "low"
    suggested = ""
    suggested_country = ""
    action = "Review raw affiliation and full paper before correcting."
    notes = "Ambiguous local-only audit finding."

    if starts_with_other_author(row.get("author", ""), row.get("raw_affiliation", "")):
        label = "likely_wrong_author_institution_assignment"
        confidence = "high"
        action = "Check the paper author-affiliation mapping; do not create a paper-wide override from this row alone."
        notes = "Raw affiliation begins with a different person's name."
    elif "china lake" in raw:
        label = "false_positive_country_word_in_city"
        confidence = "high"
        action = "No institution correction needed for the country-word finding."
        notes = "China Lake is a place name in California, USA, not evidence for country China."
    elif alias_match(current, raw):
        label = "false_positive_alias_or_translation"
        confidence = "high"
        action = "No institution correction needed."
        notes = "Current institution and raw affiliation use a known alias or translation."
    elif (
        reason == "country_mismatch_raw_text_suggests_CN"
        and any(term in raw for term in ("macau", "macao", "fujitsu"))
    ):
        label = "false_positive_alias_or_translation"
        confidence = "high"
        action = "No institution correction needed."
        notes = "The country term is compatible with the current regional or corporate affiliation."
    elif current in EXPLICIT_WRONG and normalize(EXPLICIT_WRONG[current]) in raw:
        label = "likely_wrong_institution"
        confidence = "high"
        suggested = EXPLICIT_WRONG[current]
        action = "Verify all paper affiliations before promoting a mode=replace candidate."
        notes = "Raw affiliation explicitly names a different institution."
    elif current in EXPLICIT_WRONG:
        label = "likely_wrong_institution"
        confidence = "medium"
        suggested = EXPLICIT_WRONG[current]
        action = "Check the full paper before correcting."
        notes = "Known current-name confusion, but the raw text is not sufficient for automatic replacement."
    elif current in raw and current:
        label = "false_positive_subunit_or_parent_institution"
        confidence = "high"
        action = "No institution correction needed."
        notes = "Raw text names the current institution within a department, lab, or multi-affiliation string."
    elif " & " in clean(row.get("raw_affiliation")) or " | " in clean(row.get("raw_affiliation")):
        label = "needs_full_paper_check"
        confidence = "medium"
        action = "Reconstruct every paper affiliation before proposing mode=replace."
        notes = "Raw text contains multiple affiliations."
    elif reason.startswith("country_mismatch") or reason == "low_institution_name_overlap":
        label = "needs_full_paper_check"
        confidence = "medium"
        action = "Check all authors and affiliations in the full paper."
        notes = "A single queue row cannot establish a complete paper-level replacement."

    return {
        "title": clean(row.get("title")),
        "year": clean(row.get("year")),
        "author": clean(row.get("author")),
        "current_institution": clean(row.get("institution")),
        "current_country": clean(row.get("current_country")),
        "current_country_code": clean(row.get("current_country_code")),
        "raw_affiliation": clean(row.get("raw_affiliation")),
        "reason": reason,
        "triage_label": label,
        "triage_confidence": confidence,
        "suggested_institution": suggested,
        "suggested_country": suggested_country,
        "suggested_action": action,
        "notes": notes,
    }


def author_names(value: object) -> List[str]:
    text = clean(value)
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [clean(author) for author in parsed if clean(author)]
    except json.JSONDecodeError:
        pass
    return [part.strip() for part in text.split(";") if part.strip()]


def local_institution_index(rows: Iterable[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    index = {}
    for row in rows:
        institution = clean(row.get("resolved_institution_name") or row.get("institution_name"))
        latitude = clean(row.get("resolved_latitude") or row.get("latitude"))
        longitude = clean(row.get("resolved_longitude") or row.get("longitude"))
        if institution and latitude and longitude:
            index.setdefault(normalize(institution), row)
    return index


def generate_candidates(
    triage: List[Dict[str, str]],
    papers: List[Dict[str, str]],
    affiliations: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    paper_authors = {
        (normalize(row.get("title")), clean(row.get("publication_year") or row.get("year"))): {
            normalize(author) for author in author_names(row.get("authors_ordered"))
        }
        for row in papers
    }
    local_institutions = local_institution_index(affiliations)
    grouped = defaultdict(list)
    for row in triage:
        grouped[(normalize(row["title"]), row["year"])].append(row)

    candidates = []
    for key, rows in grouped.items():
        expected_authors = paper_authors.get(key, set())
        covered_authors = {normalize(row["author"]) for row in rows}
        if not expected_authors or not expected_authors.issubset(covered_authors):
            continue
        if any(
            row["triage_label"] != "likely_wrong_institution"
            or row["triage_confidence"] != "high"
            or not row["suggested_institution"]
            for row in rows
        ):
            continue
        by_institution = defaultdict(list)
        for row in rows:
            by_institution[row["suggested_institution"]].append(row["author"])
        if any(normalize(name) not in local_institutions for name in by_institution):
            continue
        for institution, authors in by_institution.items():
            local = local_institutions[normalize(institution)]
            candidates.append({
                "title": rows[0]["title"],
                "year": rows[0]["year"],
                "mode": "replace",
                "institution": institution,
                "city": clean(local.get("resolved_city") or local.get("city")),
                "region": "",
                "country": clean(local.get("resolved_country") or local.get("country")),
                "country_code": clean(local.get("country_code")),
                "latitude": clean(local.get("resolved_latitude") or local.get("latitude")),
                "longitude": clean(local.get("resolved_longitude") or local.get("longitude")),
                "institution_authors": "; ".join(dict.fromkeys(authors)),
                "notes": "High-confidence local triage candidate; verify before promotion.",
                "triage_source": str(DEFAULT_TRIAGE.relative_to(ROOT)),
            })
    return candidates


def print_examples(label: str, rows: List[Dict[str, str]], limit: int = 5) -> None:
    print(f"Top {label} examples:")
    examples = [row for row in rows if row["triage_label"] == label][:limit]
    if not examples:
        print("  none")
    for row in examples:
        print(f"  {row['title']} / {row['author']} -> {row['current_institution']}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    triage = [triage_row(row) for row in read_csv(args.queue)]
    candidates = generate_candidates(
        triage,
        read_csv(args.papers),
        read_csv(args.affiliations),
    )
    write_atomic(args.triage_output, TRIAGE_COLUMNS, triage)
    write_atomic(args.candidates_output, CANDIDATE_COLUMNS, candidates)
    labels = Counter(row["triage_label"] for row in triage)
    confidences = Counter(row["triage_confidence"] for row in triage)
    print(f"Total rows: {len(triage)}")
    print("Count by triage_label:")
    for label, count in sorted(labels.items()):
        print(f"  {label}: {count}")
    print("Count by triage_confidence:")
    for confidence, count in sorted(confidences.items()):
        print(f"  {confidence}: {count}")
    print(f"Override candidates generated: {len(candidates)}")
    print_examples("likely_wrong_institution", triage)
    print_examples("needs_full_paper_check", triage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
