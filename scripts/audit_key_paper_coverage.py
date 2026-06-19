#!/usr/bin/env python3
"""Audit manual key-paper coverage in candidate and public-preview data.

The key-paper CSV is a human-maintained checklist. This script is read-only
with respect to manual, candidate, and preview data and calls no external APIs.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DEFAULT_KEY_PAPERS = Path("data/manual/key_papers.csv")
DEFAULT_CANDIDATE_PAPERS = Path(
    "data/processed/openalex_candidate_papers.csv"
)
DEFAULT_PUBLIC_PREVIEW = Path("web/data/public_preview_map_data.json")
DEFAULT_OUTPUT = Path("docs/key_paper_coverage_report.md")
MANUAL_DATA_DIR = Path("data/manual")
KEY_PAPER_COLUMNS = (
    "title",
    "year",
    "doi",
    "arxiv_id",
    "openalex_url",
    "paper_url",
    "expected_task",
    "notes",
)
FUZZY_TITLE_THRESHOLD = 0.92
MAX_POSSIBLE_MATCHES = 3


class AuditError(RuntimeError):
    """An expected input or output error shown without a traceback."""


@dataclass(frozen=True)
class PaperRecord:
    source: str
    source_index: int
    row: Dict[str, Any]
    title: str
    year: str
    openalex_id: str
    doi: str
    arxiv_id: str
    normalized_title: str


@dataclass(frozen=True)
class ConfirmedMatch:
    record: PaperRecord
    method: str


@dataclass(frozen=True)
class PossibleMatch:
    record: PaperRecord
    method: str
    similarity: float


@dataclass
class AuditResult:
    key_paper: PaperRecord
    candidate_match: Optional[ConfirmedMatch]
    preview_match: Optional[ConfirmedMatch]
    possible_matches: List[PossibleMatch]
    status: str


class PaperIndex:
    def __init__(self, records: Sequence[PaperRecord]) -> None:
        self.records = list(records)
        self.by_openalex = index_records(records, "openalex_id")
        self.by_doi = index_records(records, "doi")
        self.by_arxiv = index_records(records, "arxiv_id")
        self.by_title_year: Dict[Tuple[str, str], List[PaperRecord]] = {}
        self.by_title: Dict[str, List[PaperRecord]] = {}
        for record in records:
            if record.normalized_title:
                self.by_title.setdefault(record.normalized_title, []).append(record)
                if record.year:
                    self.by_title_year.setdefault(
                        (record.normalized_title, record.year), []
                    ).append(record)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit manual key-paper coverage in full OpenAlex candidates and "
            "the public preview."
        )
    )
    parser.add_argument(
        "--key-papers",
        type=Path,
        default=DEFAULT_KEY_PAPERS,
        help=f"Manual key-paper checklist (default: {DEFAULT_KEY_PAPERS}).",
    )
    parser.add_argument(
        "--candidate-papers",
        type=Path,
        default=DEFAULT_CANDIDATE_PAPERS,
        help=f"Full candidate paper CSV (default: {DEFAULT_CANDIDATE_PAPERS}).",
    )
    parser.add_argument(
        "--public-preview",
        type=Path,
        default=DEFAULT_PUBLIC_PREVIEW,
        help=f"Public preview JSON (default: {DEFAULT_PUBLIC_PREVIEW}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Markdown report path (default: {DEFAULT_OUTPUT}).",
    )
    return parser.parse_args(argv)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalize_openalex(value: Any) -> str:
    text = clean_text(value).casefold().rstrip("/")
    match = re.search(r"(?:^|/)(w\d+)$", text, flags=re.IGNORECASE)
    return match.group(1).casefold() if match else text


def normalize_doi(value: Any) -> str:
    text = clean_text(value)
    text = re.sub(r"^doi:\s*", "", text, flags=re.IGNORECASE)
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        text,
        flags=re.IGNORECASE,
    ).casefold()


def normalize_arxiv(value: Any) -> str:
    text = clean_text(value)
    url_match = re.search(
        r"arxiv\.org/(?:abs|pdf)/([^?#]+)",
        text,
        flags=re.IGNORECASE,
    )
    if url_match:
        text = url_match.group(1)
    text = re.sub(r"^arxiv:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\.pdf$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"v\d+$", "", text, flags=re.IGNORECASE)
    return text.strip(" /").casefold()


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value)).casefold()
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).replace("_", " ")
    return " ".join(text.split())


def normalize_year(value: Any) -> str:
    text = clean_text(value)
    return text if re.fullmatch(r"\d{4}", text) else ""


def first_text(row: Dict[str, Any], *fields: str) -> str:
    for field in fields:
        value = clean_text(row.get(field))
        if value:
            return value
    return ""


def paper_record(source: str, source_index: int, row: Dict[str, Any]) -> PaperRecord:
    title = first_text(row, "title", "paper_title")
    return PaperRecord(
        source=source,
        source_index=source_index,
        row=row,
        title=title,
        year=normalize_year(first_text(row, "publication_year", "year")),
        openalex_id=normalize_openalex(
            first_text(row, "openalex_url", "openalex_id")
        ),
        doi=normalize_doi(row.get("doi")),
        arxiv_id=normalize_arxiv(row.get("arxiv_id")),
        normalized_title=normalize_title(title),
    )


def index_records(
    records: Sequence[PaperRecord],
    field: str,
) -> Dict[str, List[PaperRecord]]:
    index: Dict[str, List[PaperRecord]] = {}
    for record in records:
        value = getattr(record, field)
        if value:
            index.setdefault(value, []).append(record)
    return index


def read_csv_rows(
    path: Path,
    required_columns: Iterable[str],
) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = sorted(set(required_columns) - columns)
            if missing:
                raise AuditError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise AuditError(f"Could not read {path}: {error}") from error


def read_key_papers(path: Path) -> List[PaperRecord]:
    rows = read_csv_rows(path, KEY_PAPER_COLUMNS)
    populated = [row for row in rows if any(clean_text(value) for value in row.values())]
    return [paper_record("key_papers", index, row) for index, row in enumerate(populated)]


def read_candidate_papers(path: Path) -> List[PaperRecord]:
    rows = read_csv_rows(path, ("title",))
    return [paper_record("candidates", index, row) for index, row in enumerate(rows)]


def read_preview(path: Path) -> List[PaperRecord]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as error:
        raise AuditError(f"Could not read {path}: {error}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise AuditError(f"Invalid JSON in {path}: {error}") from error

    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
        rows = payload["records"]
    else:
        raise AuditError(
            f"{path} must contain a record array or an object with a records array."
        )
    if not all(isinstance(row, dict) for row in rows):
        raise AuditError(f"{path} contains a preview record that is not an object.")
    return [paper_record("public_preview", index, row) for index, row in enumerate(rows)]


def confirmed_match(key_paper: PaperRecord, index: PaperIndex) -> Optional[ConfirmedMatch]:
    checks = (
        ("openalex_url", key_paper.openalex_id, index.by_openalex),
        ("doi", key_paper.doi, index.by_doi),
        ("arxiv_id", key_paper.arxiv_id, index.by_arxiv),
    )
    for method, value, lookup in checks:
        if value and lookup.get(value):
            return ConfirmedMatch(lookup[value][0], method)
    title_year = (key_paper.normalized_title, key_paper.year)
    if all(title_year) and index.by_title_year.get(title_year):
        return ConfirmedMatch(index.by_title_year[title_year][0], "title+year")
    return None


def possible_title_matches(
    key_paper: PaperRecord,
    indexes: Sequence[PaperIndex],
) -> List[PossibleMatch]:
    if not key_paper.normalized_title:
        return []

    matches: List[PossibleMatch] = []
    seen = set()
    for index in indexes:
        exact_title_records = index.by_title.get(key_paper.normalized_title, [])
        for record in exact_title_records:
            identity = (record.source, record.openalex_id, record.doi, record.arxiv_id)
            if identity not in seen:
                seen.add(identity)
                matches.append(PossibleMatch(record, "normalized title", 1.0))

        for record in index.records:
            if not record.normalized_title or record in exact_title_records:
                continue
            similarity = difflib.SequenceMatcher(
                None,
                key_paper.normalized_title,
                record.normalized_title,
            ).ratio()
            if similarity < FUZZY_TITLE_THRESHOLD:
                continue
            identity = (record.source, record.openalex_id, record.doi, record.arxiv_id)
            if identity in seen:
                continue
            seen.add(identity)
            matches.append(PossibleMatch(record, "fuzzy title", similarity))

    return sorted(
        matches,
        key=lambda match: (-match.similarity, match.record.source, match.record.title),
    )[:MAX_POSSIBLE_MATCHES]


def audit_coverage(
    key_papers: Sequence[PaperRecord],
    candidate_records: Sequence[PaperRecord],
    preview_records: Sequence[PaperRecord],
) -> List[AuditResult]:
    candidate_index = PaperIndex(candidate_records)
    preview_index = PaperIndex(preview_records)
    results = []
    for key_paper in key_papers:
        candidate = confirmed_match(key_paper, candidate_index)
        preview = confirmed_match(key_paper, preview_index)
        possible = []
        if candidate is None and preview is None:
            possible = possible_title_matches(
                key_paper,
                (candidate_index, preview_index),
            )
        if preview is not None:
            status = "in_public_preview"
        elif candidate is not None:
            status = "in_candidates_only"
        elif possible:
            status = "possible_match"
        else:
            status = "missing"
        results.append(AuditResult(key_paper, candidate, preview, possible, status))
    return results


def markdown_text(value: Any) -> str:
    return clean_text(value).replace("|", "\\|").replace("\n", " ")


def key_label(key_paper: PaperRecord) -> str:
    if key_paper.title:
        return key_paper.title
    return first_text(
        key_paper.row,
        "doi",
        "arxiv_id",
        "openalex_url",
        "paper_url",
    ) or "Untitled key-paper entry"


def match_description(match: Optional[ConfirmedMatch]) -> str:
    if match is None:
        return "No"
    return f"Yes (`{match.method}`)"


def result_list(results: Sequence[AuditResult]) -> List[str]:
    if not results:
        return ["None."]
    return [
        f"- {markdown_text(key_label(result.key_paper))}"
        + (f" ({result.key_paper.year})" if result.key_paper.year else "")
        for result in results
    ]


def build_report(
    key_path: Path,
    candidate_path: Path,
    preview_path: Path,
    results: Sequence[AuditResult],
) -> str:
    matched_candidates = [result for result in results if result.candidate_match]
    matched_preview = [result for result in results if result.preview_match]
    missing_candidates = [result for result in results if not result.candidate_match]
    candidates_only = [
        result
        for result in results
        if result.candidate_match and not result.preview_match
    ]
    possible = [result for result in results if result.possible_matches]

    lines = [
        "# Key Paper Coverage Report",
        "",
        "This audit compares a manual coverage checklist with automatic candidate "
        "and public-preview data. Checklist membership does not publish a paper.",
        "",
        "## Inputs",
        "",
        f"- Key papers: `{key_path.as_posix()}`",
        f"- Candidate papers: `{candidate_path.as_posix()}`",
        f"- Public preview: `{preview_path.as_posix()}`",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Total key papers | {len(results)} |",
        f"| Matched in candidate papers | {len(matched_candidates)} |",
        f"| Matched in public preview | {len(matched_preview)} |",
        f"| Missing from candidates | {len(missing_candidates)} |",
        f"| Present in candidates but missing from public preview | {len(candidates_only)} |",
        f"| Possible title-only matches | {len(possible)} |",
        "",
        "## Per-Paper Status",
        "",
        "| # | Key paper | Year | Expected task | Status | Candidate | Public preview | Notes |",
        "| ---: | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    if results:
        for index, result in enumerate(results, start=1):
            key = result.key_paper
            lines.append(
                f"| {index} | {markdown_text(key_label(key))} | "
                f"{markdown_text(key.year)} | "
                f"{markdown_text(key.row.get('expected_task'))} | "
                f"`{result.status}` | "
                f"{match_description(result.candidate_match)} | "
                f"{match_description(result.preview_match)} | "
                f"{markdown_text(key.row.get('notes'))} |"
            )
    else:
        lines.append("| - | No key papers listed | | | | | | |")

    lines.extend(
        [
            "",
            "## Missing From Candidates",
            "",
            *result_list(missing_candidates),
            "",
            "## Present in Candidates but Missing From Public Preview",
            "",
            *result_list(candidates_only),
            "",
            "## Possible Title-Only Matches",
            "",
        ]
    )
    possible_rows = [
        (result, match)
        for result in possible
        for match in result.possible_matches
    ]
    if possible_rows:
        lines.extend(
            [
                "| Key paper | Source | Possible record | Year | Basis | Similarity |",
                "| --- | --- | --- | ---: | --- | ---: |",
            ]
        )
        for result, match in possible_rows:
            lines.append(
                f"| {markdown_text(key_label(result.key_paper))} | "
                f"{markdown_text(match.record.source)} | "
                f"{markdown_text(match.record.title)} | "
                f"{markdown_text(match.record.year)} | "
                f"{markdown_text(match.method)} | {match.similarity:.3f} |"
            )
    else:
        lines.append("None.")
    lines.extend(
        [
            "",
            "Possible matches require manual confirmation and are not counted as "
            "covered by either dataset.",
            "",
        ]
    )
    return "\n".join(lines)


def path_is_in_manual_data(path: Path) -> bool:
    try:
        path.resolve().relative_to(MANUAL_DATA_DIR.resolve())
        return True
    except ValueError:
        return False


def write_report(path: Path, report: str) -> None:
    if path_is_in_manual_data(path):
        raise AuditError("Refusing to write an audit report into data/manual/.")
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path.write_text(report, encoding="utf-8")
        temporary_path.replace(path)
    except OSError as error:
        raise AuditError(f"Could not write {path}: {error}") from error


def print_summary(results: Sequence[AuditResult], output: Path) -> None:
    print("Key paper coverage audit:")
    print(f"  Total key papers: {len(results)}")
    print(
        "  Matched in candidate papers: "
        f"{sum(result.candidate_match is not None for result in results)}"
    )
    print(
        "  Matched in public preview: "
        f"{sum(result.preview_match is not None for result in results)}"
    )
    print(
        "  Missing from candidates: "
        f"{sum(result.candidate_match is None for result in results)}"
    )
    print(
        "  Candidates missing from public preview: "
        f"{sum(result.candidate_match is not None and result.preview_match is None for result in results)}"
    )
    print(
        "  Possible title-only matches: "
        f"{sum(bool(result.possible_matches) for result in results)}"
    )
    print(f"  Report: {output}")


def run(args: argparse.Namespace) -> int:
    try:
        key_papers = read_key_papers(args.key_papers)
        candidates = read_candidate_papers(args.candidate_papers)
        preview = read_preview(args.public_preview)
        results = audit_coverage(key_papers, candidates, preview)
        report = build_report(
            args.key_papers,
            args.candidate_papers,
            args.public_preview,
            results,
        )
        write_report(args.output, report)
    except AuditError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print_summary(results, args.output)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
