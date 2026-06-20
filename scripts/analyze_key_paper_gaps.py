#!/usr/bin/env python3
"""Analyze why manual key papers are not covered by the current pipeline.

This script is local and read-only with respect to the enriched checklist,
candidate papers, and public preview data. It calls no external APIs.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import tempfile
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KEY_PAPERS = ROOT / "data" / "manual" / "key_papers_enriched.csv"
DEFAULT_CANDIDATE_PAPERS = ROOT / "data" / "processed" / "openalex_candidate_papers.csv"
DEFAULT_PUBLIC_PREVIEW = ROOT / "web" / "data" / "public_preview_map_data.json"
DEFAULT_REPORT = ROOT / "docs" / "key_paper_gap_analysis.md"
DEFAULT_CSV = ROOT / "data" / "manual" / "key_paper_gap_analysis.csv"
OUTPUT_COLUMNS = (
    "title",
    "year",
    "expected_task",
    "openalex_link_status",
    "coverage_status",
    "in_public_preview",
    "in_candidate_papers",
    "likely_gap_reason",
)
COVERAGE_STATUSES = (
    "covered_in_public_preview",
    "covered_in_candidates_only",
    "possible_pipeline_match",
    "not_covered_by_pipeline",
)
LINK_STATUSES = (
    "linked_to_openalex",
    "possible_openalex_match",
    "not_found_in_openalex",
    "skipped",
    "",
)
GAP_REASONS = (
    "already_in_public_preview",
    "in_candidates_but_filtered_from_public_preview",
    "openalex_not_found",
    "possible_openalex_match_needs_review",
    "linked_openalex_but_missing_from_candidate_queries",
    "title_may_need_cleaning",
    "auxiliary_material",
    "unknown_gap",
)
FUZZY_TITLE_THRESHOLD = 0.92
MAX_EXAMPLES_PER_REASON = 8
TITLE_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
    "with",
}


class GapAnalysisError(RuntimeError):
    """An expected input/output error."""


@dataclass(frozen=True)
class PaperRecord:
    source: str
    row: Dict[str, Any]
    title: str
    year: str
    openalex_id: str
    doi: str
    arxiv_id: str
    normalized_title: str


@dataclass(frozen=True)
class GapResult:
    key_paper: PaperRecord
    openalex_link_status: str
    coverage_status: str
    in_public_preview: bool
    in_candidate_papers: bool
    likely_gap_reason: str


class PaperIndex:
    def __init__(self, records: Sequence[PaperRecord]) -> None:
        self.records = list(records)
        self.by_openalex = index_records(records, "openalex_id")
        self.by_doi = index_records(records, "doi")
        self.by_arxiv = index_records(records, "arxiv_id")
        self.by_title_year: Dict[Tuple[str, str], List[PaperRecord]] = defaultdict(list)
        self.by_title_token: Dict[str, List[PaperRecord]] = defaultdict(list)
        for record in records:
            if record.normalized_title and record.year:
                self.by_title_year[(record.normalized_title, record.year)].append(record)
            token = title_blocking_token(record.normalized_title)
            if token:
                self.by_title_token[token].append(record)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze coverage gaps for manually curated key papers."
    )
    parser.add_argument("--key-papers", type=Path, default=DEFAULT_KEY_PAPERS)
    parser.add_argument("--candidate-papers", type=Path, default=DEFAULT_CANDIDATE_PAPERS)
    parser.add_argument("--public-preview", type=Path, default=DEFAULT_PUBLIC_PREVIEW)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_CSV)
    return parser.parse_args(argv)


def project_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value)).casefold()
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).replace("_", " ")
    return " ".join(text.split())


def title_blocking_token(normalized_title: str) -> str:
    for token in normalized_title.split():
        if token not in TITLE_STOPWORDS and len(token) > 2:
            return token
    return ""


def normalize_year(value: Any) -> str:
    text = clean_text(value)
    return text if re.fullmatch(r"(?:19|20)\d{2}", text) else ""


def normalize_openalex(value: Any) -> str:
    text = clean_text(value).casefold().rstrip("/")
    match = re.search(r"(?:^|/)(w\d+)$", text, flags=re.IGNORECASE)
    return match.group(1).casefold() if match else text


def normalize_doi(value: Any) -> str:
    text = clean_text(value)
    text = re.sub(r"^doi:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    return text.rstrip(" /.").casefold()


def normalize_arxiv(value: Any) -> str:
    text = clean_text(value)
    url_match = re.search(r"arxiv\.org/(?:abs|pdf)/([^?#]+)", text, re.IGNORECASE)
    if url_match:
        text = url_match.group(1)
    text = re.sub(r"^arxiv:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\.pdf$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"v\d+$", "", text, flags=re.IGNORECASE)
    return text.strip(" /").casefold()


def first_text(row: Dict[str, Any], *fields: str) -> str:
    for field in fields:
        value = clean_text(row.get(field))
        if value:
            return value
    return ""


def effective_openalex(row: Dict[str, Any]) -> str:
    if clean_text(row.get("openalex_link_status")) == "linked_to_openalex":
        return first_text(row, "enriched_openalex_url", "openalex_url")
    return first_text(row, "openalex_url")


def effective_doi(row: Dict[str, Any]) -> str:
    if clean_text(row.get("openalex_link_status")) == "linked_to_openalex":
        return first_text(row, "enriched_doi", "doi")
    return first_text(row, "doi")


def make_record(source: str, row: Dict[str, Any], enriched_key_paper: bool = False) -> PaperRecord:
    title = first_text(row, "title", "paper_title")
    openalex_value = effective_openalex(row) if enriched_key_paper else first_text(row, "openalex_url", "openalex_id", "id")
    doi_value = effective_doi(row) if enriched_key_paper else first_text(row, "doi")
    return PaperRecord(
        source=source,
        row=row,
        title=title,
        year=normalize_year(first_text(row, "publication_year", "year")),
        openalex_id=normalize_openalex(openalex_value),
        doi=normalize_doi(doi_value),
        arxiv_id=normalize_arxiv(first_text(row, "arxiv_id", "arxiv_url")),
        normalized_title=normalize_title(title),
    )


def index_records(records: Sequence[PaperRecord], field: str) -> Dict[str, List[PaperRecord]]:
    index: Dict[str, List[PaperRecord]] = defaultdict(list)
    for record in records:
        value = getattr(record, field)
        if value:
            index[value].append(record)
    return dict(index)


def read_csv_rows(path: Path, required_columns: Iterable[str]) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = sorted(set(required_columns) - columns)
            if missing:
                raise GapAnalysisError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise GapAnalysisError(f"Could not read {path}: {error}") from error


def read_key_papers(path: Path) -> List[PaperRecord]:
    rows = read_csv_rows(path, ("title", "openalex_link_status"))
    rows = [row for row in rows if any(clean_text(value) for value in row.values())]
    return [make_record("key_papers_enriched", row, enriched_key_paper=True) for row in rows]


def read_candidate_papers(path: Path) -> List[PaperRecord]:
    rows = read_csv_rows(path, ("title",))
    return [make_record("candidate_papers", row) for row in rows]


def read_public_preview(path: Path) -> List[PaperRecord]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as error:
        raise GapAnalysisError(f"Could not read {path}: {error}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise GapAnalysisError(f"Invalid JSON in {path}: {error}") from error

    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
        rows = payload["records"]
    else:
        raise GapAnalysisError(
            f"{path} must contain an array or an object with a records array."
        )
    if not all(isinstance(row, dict) for row in rows):
        raise GapAnalysisError(f"{path} contains a non-object preview record.")
    return [make_record("public_preview", row) for row in rows]


def has_confirmed_match(key_paper: PaperRecord, index: PaperIndex) -> bool:
    checks = (
        (key_paper.openalex_id, index.by_openalex),
        (key_paper.doi, index.by_doi),
        (key_paper.arxiv_id, index.by_arxiv),
    )
    for value, lookup in checks:
        if value and value in lookup:
            return True
    if key_paper.normalized_title and key_paper.year:
        return (key_paper.normalized_title, key_paper.year) in index.by_title_year
    return False


def has_possible_title_match(key_paper: PaperRecord, indexes: Sequence[PaperIndex]) -> bool:
    if not key_paper.normalized_title:
        return False
    blocking_token = title_blocking_token(key_paper.normalized_title)
    if not blocking_token:
        return False
    for index in indexes:
        candidates = index.by_title_token.get(blocking_token, [])
        for record in candidates:
            if not record.normalized_title:
                continue
            length_ratio = min(
                len(key_paper.normalized_title),
                len(record.normalized_title),
            ) / max(len(key_paper.normalized_title), len(record.normalized_title))
            if length_ratio < 0.75:
                continue
            similarity = difflib.SequenceMatcher(
                None, key_paper.normalized_title, record.normalized_title
            ).ratio()
            if similarity >= FUZZY_TITLE_THRESHOLD:
                return True
    return False


def title_may_need_cleaning(title: str) -> bool:
    text = clean_text(title)
    if not text:
        return False
    suffix_patterns = (
        r"\.\s*[A-Z][A-Za-z0-9&./ -]{1,35},\s*(?:19|20)\d{2}$",
        r"\s+(?:SPW|APSIPA\s+ASC|ACM\s+Multimedia|IJACSA|CVPR|ICCV|ECCV|WACV|BMVC|ICIP|ICASSP|TIFS|TPAMI),?\s*(?:19|20)\d{2}$",
        r"\.\s*(?:19|20)\d{6}$",
        r"\s+(?:arXiv|IEEE|ACM)\s*(?:19|20)\d{2}$",
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in suffix_patterns)


def is_auxiliary_material(row: Dict[str, Any]) -> bool:
    section = clean_text(row.get("section")).casefold()
    notes = clean_text(row.get("notes")).casefold()
    return any(
        marker in f"{section} {notes}"
        for marker in (
            "auxiliary",
            "dataset",
            "benchmark",
            "survey",
            "anti-forensics",
            "anti forensic",
            "to supplement",
        )
    )


def coverage_status(
    in_preview: bool,
    in_candidates: bool,
    possible_match: bool,
) -> str:
    if in_preview:
        return "covered_in_public_preview"
    if in_candidates:
        return "covered_in_candidates_only"
    if possible_match:
        return "possible_pipeline_match"
    return "not_covered_by_pipeline"


def likely_gap_reason(
    key_paper: PaperRecord,
    status: str,
    in_preview: bool,
    in_candidates: bool,
) -> str:
    link_status = clean_text(key_paper.row.get("openalex_link_status"))
    if in_preview:
        return "already_in_public_preview"
    if in_candidates:
        return "in_candidates_but_filtered_from_public_preview"
    if title_may_need_cleaning(key_paper.title):
        return "title_may_need_cleaning"
    if is_auxiliary_material(key_paper.row):
        return "auxiliary_material"
    if link_status == "not_found_in_openalex":
        return "openalex_not_found"
    if link_status == "possible_openalex_match":
        return "possible_openalex_match_needs_review"
    if link_status == "linked_to_openalex":
        return "linked_openalex_but_missing_from_candidate_queries"
    if status == "possible_pipeline_match":
        return "unknown_gap"
    return "unknown_gap"


def analyze_gaps(
    key_papers: Sequence[PaperRecord],
    candidates: Sequence[PaperRecord],
    preview: Sequence[PaperRecord],
) -> List[GapResult]:
    candidate_index = PaperIndex(candidates)
    preview_index = PaperIndex(preview)
    results: List[GapResult] = []
    for key_paper in key_papers:
        in_candidates = has_confirmed_match(key_paper, candidate_index)
        in_preview = has_confirmed_match(key_paper, preview_index)
        possible_match = False
        if not in_candidates and not in_preview:
            possible_match = has_possible_title_match(
                key_paper, (candidate_index, preview_index)
            )
        status = coverage_status(in_preview, in_candidates, possible_match)
        results.append(
            GapResult(
                key_paper=key_paper,
                openalex_link_status=clean_text(key_paper.row.get("openalex_link_status")),
                coverage_status=status,
                in_public_preview=in_preview,
                in_candidate_papers=in_candidates,
                likely_gap_reason=likely_gap_reason(
                    key_paper, status, in_preview, in_candidates
                ),
            )
        )
    return results


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def result_row(result: GapResult) -> Dict[str, str]:
    key = result.key_paper
    return {
        "title": key.title,
        "year": key.year,
        "expected_task": clean_text(key.row.get("expected_task")),
        "openalex_link_status": result.openalex_link_status,
        "coverage_status": result.coverage_status,
        "in_public_preview": bool_text(result.in_public_preview),
        "in_candidate_papers": bool_text(result.in_candidate_papers),
        "likely_gap_reason": result.likely_gap_reason,
    }


def write_csv(path: Path, results: Sequence[GapResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for result in results:
            writer.writerow(result_row(result))
        temporary = Path(handle.name)
    temporary.replace(path)


def markdown_text(value: Any) -> str:
    return clean_text(value).replace("|", "\\|") or "-"


def counter_table(counter: Counter[str], labels: Sequence[str]) -> List[str]:
    lines = ["| Value | Count |", "| --- | ---: |"]
    seen = set()
    for label in labels:
        lines.append(f"| `{label or '(blank)'}` | {counter[label]} |")
        seen.add(label)
    for label, count in sorted(counter.items()):
        if label not in seen:
            lines.append(f"| `{label or '(blank)'}` | {count} |")
    return lines


def examples_by_reason(results: Sequence[GapResult]) -> List[str]:
    lines: List[str] = []
    grouped: Dict[str, List[GapResult]] = defaultdict(list)
    for result in results:
        grouped[result.likely_gap_reason].append(result)
    for reason in GAP_REASONS:
        examples = grouped.get(reason, [])[:MAX_EXAMPLES_PER_REASON]
        lines.extend([f"### `{reason}`", ""])
        if examples:
            for result in examples:
                year = f" ({result.key_paper.year})" if result.key_paper.year else ""
                lines.append(
                    f"- {markdown_text(result.key_paper.title)}{year} "
                    f"- `{result.coverage_status}`, "
                    f"OpenAlex link `{result.openalex_link_status or '(blank)'}`"
                )
        else:
            lines.append("None.")
        lines.append("")
    return lines


def build_report(results: Sequence[GapResult]) -> str:
    coverage_counts = Counter(result.coverage_status for result in results)
    link_counts = Counter(result.openalex_link_status for result in results)
    reason_counts = Counter(result.likely_gap_reason for result in results)
    lines = [
        "# Key Paper Gap Analysis",
        "",
        "This local analysis compares the manually curated enriched key-paper "
        "checklist with current OpenAlex candidate papers and the public preview. "
        "It does not call external APIs and does not modify source datasets.",
        "",
        "`not_covered_by_pipeline` means only that the current automatic pipeline "
        "did not cover a checklist paper; it does not mean the paper is invalid "
        "or irrelevant.",
        "",
        "## Summary",
        "",
        f"- Total key papers: {len(results)}",
        "",
        "### Coverage Status",
        "",
        *counter_table(coverage_counts, COVERAGE_STATUSES),
        "",
        "### OpenAlex Link Status",
        "",
        *counter_table(link_counts, LINK_STATUSES),
        "",
        "### Likely Gap Reason",
        "",
        *counter_table(reason_counts, GAP_REASONS),
        "",
        "## Top Examples by Likely Gap Reason",
        "",
        *examples_by_reason(results),
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(report)
        temporary = Path(handle.name)
    temporary.replace(path)


def print_summary(results: Sequence[GapResult], report: Path, output_csv: Path) -> None:
    print("Key paper gap analysis complete")
    print(f"  Total key papers: {len(results)}")
    print("  Coverage status:")
    for status, count in Counter(result.coverage_status for result in results).items():
        print(f"    {status}: {count}")
    print("  Likely gap reason:")
    for reason, count in Counter(result.likely_gap_reason for result in results).items():
        print(f"    {reason}: {count}")
    print(f"  Report: {report}")
    print(f"  CSV: {output_csv}")


def run(args: argparse.Namespace) -> int:
    key_path = project_path(args.key_papers)
    candidate_path = project_path(args.candidate_papers)
    preview_path = project_path(args.public_preview)
    report_path = project_path(args.report)
    csv_path = project_path(args.output_csv)
    try:
        key_papers = read_key_papers(key_path)
        candidates = read_candidate_papers(candidate_path)
        preview = read_public_preview(preview_path)
        results = analyze_gaps(key_papers, candidates, preview)
        write_csv(csv_path, results)
        write_report(report_path, build_report(results))
    except GapAnalysisError as error:
        print(f"Error: {error}")
        return 1
    except OSError as error:
        print(f"Error writing gap analysis output: {error}")
        return 1
    print_summary(results, report_path, csv_path)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
