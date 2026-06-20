#!/usr/bin/env python3
"""Export OpenAlex-linked key papers missing from automatic candidate queries.

This supplement list is for manual audit only. It does not modify candidate
data, public preview data, or the source key-paper checklist.
"""

from __future__ import annotations

import argparse
import csv
import re
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KEY_PAPERS = ROOT / "data" / "manual" / "key_papers_enriched.csv"
DEFAULT_GAP_ANALYSIS = ROOT / "data" / "manual" / "key_paper_gap_analysis.csv"
DEFAULT_CANDIDATE_PAPERS = ROOT / "data" / "processed" / "openalex_candidate_papers.csv"
DEFAULT_OUTPUT = ROOT / "data" / "manual" / "key_paper_supplement_candidates.csv"
DEFAULT_REPORT = ROOT / "docs" / "key_paper_supplement_candidates.md"
SUPPLEMENT_REASON = "linked_openalex_but_missing_from_candidate_queries"
OUTPUT_COLUMNS = (
    "title",
    "year",
    "expected_task",
    "authors",
    "doi",
    "arxiv_id",
    "openalex_url",
    "paper_url",
    "source_doc",
    "section",
    "notes",
    "supplement_reason",
    "manual_review",
)


class SupplementExportError(RuntimeError):
    """An expected input/output error."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export OpenAlex-linked key papers that are missing from automatic "
            "candidate queries as manual supplement candidates."
        )
    )
    parser.add_argument("--key-papers", type=Path, default=DEFAULT_KEY_PAPERS)
    parser.add_argument("--gap-analysis", type=Path, default=DEFAULT_GAP_ANALYSIS)
    parser.add_argument("--candidate-papers", type=Path, default=DEFAULT_CANDIDATE_PAPERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
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


def first_text(row: Dict[str, Any], *fields: str) -> str:
    for field in fields:
        value = clean_text(row.get(field))
        if value:
            return value
    return ""


def read_csv_rows(path: Path, required_columns: Iterable[str]) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = sorted(set(required_columns) - columns)
            if missing:
                raise SupplementExportError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise SupplementExportError(f"Could not read {path}: {error}") from error


def title_year_key(row: Dict[str, Any]) -> Tuple[str, str]:
    return normalize_title(row.get("title")), normalize_year(row.get("year"))


def supplement_gap_keys(rows: Sequence[Dict[str, str]]) -> set[Tuple[str, str]]:
    keys: set[Tuple[str, str]] = set()
    for row in rows:
        if clean_text(row.get("likely_gap_reason")) != SUPPLEMENT_REASON:
            continue
        if clean_text(row.get("openalex_link_status")) != "linked_to_openalex":
            continue
        key = title_year_key(row)
        if all(key):
            keys.add(key)
    return keys


def candidate_identities(rows: Sequence[Dict[str, str]]) -> set[Tuple[str, str]]:
    identities: set[Tuple[str, str]] = set()
    for row in rows:
        openalex = normalize_openalex(first_text(row, "openalex_url", "openalex_id"))
        doi = normalize_doi(row.get("doi"))
        title_key = title_year_key(row)
        if openalex:
            identities.add(("openalex", openalex))
        if doi:
            identities.add(("doi", doi))
        if all(title_key):
            identities.add(("title_year", "|".join(title_key)))
    return identities


def accepted_openalex_url(row: Dict[str, str]) -> str:
    return first_text(row, "openalex_url", "enriched_openalex_url")


def accepted_doi(row: Dict[str, str]) -> str:
    return first_text(row, "doi", "enriched_doi")


def accepted_paper_url(row: Dict[str, str]) -> str:
    return first_text(row, "paper_url", "enriched_paper_url")


def row_identities(row: Dict[str, str]) -> List[Tuple[str, str]]:
    identities: List[Tuple[str, str]] = []
    openalex = normalize_openalex(accepted_openalex_url(row))
    doi = normalize_doi(accepted_doi(row))
    title_key = title_year_key(row)
    if openalex:
        identities.append(("openalex", openalex))
    if doi:
        identities.append(("doi", doi))
    if all(title_key):
        identities.append(("title_year", "|".join(title_key)))
    return identities


def dedupe_key(row: Dict[str, str]) -> Tuple[str, str]:
    openalex = normalize_openalex(accepted_openalex_url(row))
    if openalex:
        return "openalex", openalex
    doi = normalize_doi(accepted_doi(row))
    if doi:
        return "doi", doi
    title_key = title_year_key(row)
    return "title_year", "|".join(title_key)


def output_row(row: Dict[str, str]) -> Dict[str, str]:
    return {
        "title": clean_text(row.get("title")),
        "year": normalize_year(row.get("year")),
        "expected_task": clean_text(row.get("expected_task")),
        "authors": clean_text(row.get("authors")),
        "doi": accepted_doi(row),
        "arxiv_id": clean_text(row.get("arxiv_id")),
        "openalex_url": accepted_openalex_url(row),
        "paper_url": accepted_paper_url(row),
        "source_doc": clean_text(row.get("source_doc")),
        "section": clean_text(row.get("section")),
        "notes": clean_text(row.get("notes")),
        "supplement_reason": SUPPLEMENT_REASON,
        "manual_review": "true",
    }


def export_supplement_candidates(
    key_rows: Sequence[Dict[str, str]],
    gap_rows: Sequence[Dict[str, str]],
    candidate_rows: Sequence[Dict[str, str]],
) -> List[Dict[str, str]]:
    gap_keys = supplement_gap_keys(gap_rows)
    existing_candidate_ids = candidate_identities(candidate_rows)
    exported: List[Dict[str, str]] = []
    seen: set[Tuple[str, str]] = set()

    for row in key_rows:
        if clean_text(row.get("openalex_link_status")) != "linked_to_openalex":
            continue
        key = title_year_key(row)
        if key not in gap_keys:
            continue
        if any(identity in existing_candidate_ids for identity in row_identities(row)):
            continue
        identity = dedupe_key(row)
        if identity in seen:
            continue
        seen.add(identity)
        exported.append(output_row(row))
    return exported


def write_csv(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def markdown_text(value: Any) -> str:
    return clean_text(value).replace("|", "\\|") or "-"


def counter_table(counter: Counter[str]) -> List[str]:
    if not counter:
        return ["None."]
    lines = ["| Value | Count |", "| --- | ---: |"]
    for value, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {markdown_text(value)} | {count} |")
    return lines


def build_report(rows: Sequence[Dict[str, str]]) -> str:
    expected_task_counts = Counter(row.get("expected_task", "") for row in rows)
    source_doc_counts = Counter(row.get("source_doc", "") for row in rows)
    lines = [
        "# Key Paper Supplement Candidates",
        "",
        "This report lists manually curated key papers that are linked to OpenAlex "
        "but are missing from the current automatic OpenAlex candidate queries.",
        "",
        "The supplement CSV is for audit only. It is not used by the public preview "
        "exporter automatically, and every row remains `manual_review=true`.",
        "",
        "## Summary",
        "",
        f"- Total supplement candidates: {len(rows)}",
        "",
        "## Counts by Expected Task",
        "",
        *counter_table(expected_task_counts),
        "",
        "## Counts by Source Document",
        "",
        *counter_table(source_doc_counts),
        "",
        "## Example Titles",
        "",
    ]
    if rows:
        for row in rows[:30]:
            year = f" ({row['year']})" if row.get("year") else ""
            lines.append(f"- {markdown_text(row.get('title'))}{year}")
    else:
        lines.append("None.")
    return "\n".join(lines).rstrip() + "\n"


def write_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(report)
        temporary = Path(handle.name)
    temporary.replace(path)


def print_summary(rows: Sequence[Dict[str, str]], output: Path, report: Path) -> None:
    print("Key paper supplement candidate export complete")
    print(f"  Total supplement candidates: {len(rows)}")
    print("  Counts by expected_task:")
    for task, count in sorted(Counter(row.get("expected_task", "") for row in rows).items()):
        print(f"    {task or '(blank)'}: {count}")
    print(f"  CSV: {output}")
    print(f"  Report: {report}")


def run(args: argparse.Namespace) -> int:
    key_path = project_path(args.key_papers)
    gap_path = project_path(args.gap_analysis)
    candidate_path = project_path(args.candidate_papers)
    output_path = project_path(args.output)
    report_path = project_path(args.report)
    try:
        key_rows = read_csv_rows(key_path, ("title", "openalex_link_status"))
        gap_rows = read_csv_rows(
            gap_path,
            ("title", "year", "openalex_link_status", "likely_gap_reason"),
        )
        candidate_rows = read_csv_rows(candidate_path, ("title",))
        rows = export_supplement_candidates(key_rows, gap_rows, candidate_rows)
        write_csv(output_path, rows)
        write_report(report_path, build_report(rows))
    except SupplementExportError as error:
        print(f"Error: {error}")
        return 1
    except OSError as error:
        print(f"Error writing supplement output: {error}")
        return 1
    print_summary(rows, output_path, report_path)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
