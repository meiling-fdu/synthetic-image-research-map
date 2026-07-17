#!/usr/bin/env python3
"""Generate a readable quality report for the public preview map dataset.

This script is read-only with respect to candidate data. It calls no APIs and never
writes to data/manual/.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from .country_normalization import normalize_country_region
except ImportError:  # Direct execution from the scripts directory.
    from country_normalization import normalize_country_region


DEFAULT_INPUT = Path("web/data/public_preview_map_data.json")
DEFAULT_OUTPUT = Path("docs/public_preview_report.md")
MANUAL_DATA_DIR = Path("data/manual")
TOP_LIMIT = 10
KNOWN_TASKS = {
    "detection",
    "source_attribution",
    "detection_and_source_attribution",
}
MISSING_INSTITUTION_VALUES = {"", "none", "null", "unknown", "n/a", "na"}


class ReportError(RuntimeError):
    """An expected input, schema, or output error shown without a traceback."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown quality report for the public preview dataset."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Public preview JSON (default: {DEFAULT_INPUT}).",
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


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return clean_text(value).casefold() in {"1", "true", "yes", "y"}


def path_is_in_manual_data(path: Path) -> bool:
    try:
        path.resolve().relative_to(MANUAL_DATA_DIR.resolve())
        return True
    except ValueError:
        return False


def read_dataset(path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as error:
        raise ReportError(f"Could not read {path}: {error}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ReportError(f"Invalid JSON in {path}: {error}") from error

    if isinstance(payload, list):
        metadata: Dict[str, Any] = {}
        records = payload
    elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
        raw_metadata = payload.get("metadata")
        metadata = raw_metadata if isinstance(raw_metadata, dict) else {}
        records = payload["records"]
    else:
        raise ReportError(
            f"{path} must contain an array of records or an object with a records array."
        )

    if not all(isinstance(record, dict) for record in records):
        raise ReportError(f"{path} contains a map record that is not a JSON object.")
    return metadata, records


def first_text(record: Dict[str, Any], *fields: str) -> str:
    for field in fields:
        value = clean_text(record.get(field))
        if value:
            return value
    return ""


def normalized_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean_text(value),
        flags=re.IGNORECASE,
    ).casefold()


def paper_identity(record: Dict[str, Any]) -> Tuple[str, ...]:
    openalex_url = clean_text(record.get("openalex_url")).casefold().rstrip("/")
    if openalex_url:
        return "openalex", openalex_url
    doi = normalized_doi(record.get("doi"))
    if doi:
        return "doi", doi
    arxiv_id = clean_text(record.get("arxiv_id")).casefold()
    if arxiv_id:
        return "arxiv", arxiv_id
    title = re.sub(
        r"[^a-z0-9]+", " ", first_text(record, "title", "paper_title").casefold()
    ).strip()
    year = first_text(record, "publication_year", "year")
    if title:
        return "title_year", title, year
    return "record", clean_text(record.get("id")).casefold()


def institution_name(record: Dict[str, Any]) -> str:
    value = first_text(record, "institution", "institution_name")
    return "" if value.casefold() in MISSING_INSTITUTION_VALUES else value


def institution_identity(record: Dict[str, Any]) -> str:
    return institution_name(record).casefold()


def normalized_country(record: Dict[str, Any]) -> str:
    return normalize_country_region(
        record.get("country"),
        record.get("country_code"),
        record.get("region"),
        record.get("region_code"),
        record.get("raw_country") if "raw_country" in record else None,
        record.get("raw_country_code") if "raw_country_code" in record else None,
    )["country"]


def has_usable_coordinates(record: Dict[str, Any]) -> bool:
    try:
        latitude = float(record.get("latitude"))
        longitude = float(record.get("longitude"))
    except (TypeError, ValueError):
        return False
    return (
        math.isfinite(latitude)
        and math.isfinite(longitude)
        and -90 <= latitude <= 90
        and -180 <= longitude <= 180
    )


def paper_url(record: Dict[str, Any]) -> str:
    return first_text(
        record,
        "primary_url",
        "landing_page_url",
        "url",
        "openalex_url",
        "arxiv_url",
    )


def is_arxiv_record(record: Dict[str, Any]) -> bool:
    doi = normalized_doi(record.get("doi"))
    return bool(
        parse_bool(record.get("is_arxiv_preprint"))
        or clean_text(record.get("arxiv_id"))
        or clean_text(record.get("arxiv_url"))
        or doi.startswith("10.48550/arxiv.")
    )


def resolution_confidence(record: Dict[str, Any]) -> str:
    value = clean_text(record.get("resolution_confidence")).casefold()
    return value if value in {"high", "medium", "low", "unresolved"} else "unresolved"


def count_values(
    records: Iterable[Dict[str, Any]],
    getter: Callable[[Dict[str, Any]], str],
    unknown: str = "Unknown",
) -> Counter:
    counts: Counter = Counter()
    for record in records:
        value = clean_text(getter(record)) or unknown
        counts[value] += 1
    return counts


def count_present_values(
    records: Iterable[Dict[str, Any]],
    getter: Callable[[Dict[str, Any]], str],
) -> Counter:
    counts: Counter = Counter()
    for record in records:
        value = clean_text(getter(record))
        if value:
            counts[value] += 1
    return counts


def markdown_text(value: Any) -> str:
    return clean_text(value).replace("|", "\\|")


def metadata_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return clean_text(value)


def counter_table(
    counts: Counter,
    label: str,
    limit: Optional[int] = None,
    year_order: bool = False,
) -> List[str]:
    lines = [f"| {label} | Records |", "| --- | ---: |"]
    if year_order:
        items = sorted(
            counts.items(),
            key=lambda item: (
                item[0] == "Unknown",
                -int(item[0]) if item[0].isdigit() else 0,
                item[0].casefold(),
            ),
        )
    else:
        items = sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold()))
    if limit is not None:
        items = items[:limit]
    if not items:
        lines.append("| None | 0 |")
    else:
        lines.extend(
            f"| {markdown_text(value)} | {count} |" for value, count in items
        )
    return lines


def record_label(record: Dict[str, Any]) -> str:
    title = first_text(record, "title", "paper_title") or "Untitled record"
    year = first_text(record, "publication_year", "year") or "unknown year"
    institution = institution_name(record) or "unknown institution"
    identifier = clean_text(record.get("id"))
    suffix = f"; `{markdown_text(identifier)}`" if identifier else ""
    return (
        f"{markdown_text(title)} ({markdown_text(year)}) - "
        f"{markdown_text(institution)}{suffix}"
    )


def issue_section(title: str, records: Sequence[Dict[str, Any]]) -> List[str]:
    lines = [f"### {title}", "", f"Count: **{len(records)}**", ""]
    if records:
        lines.extend(f"- {record_label(record)}" for record in records)
    else:
        lines.append("None.")
    lines.append("")
    return lines


def build_report(
    input_path: Path,
    metadata: Dict[str, Any],
    records: Sequence[Dict[str, Any]],
) -> str:
    papers_by_identity: Dict[Tuple[str, ...], Dict[str, Any]] = {}
    for record in records:
        papers_by_identity.setdefault(paper_identity(record), record)
    paper_records = list(papers_by_identity.values())
    tasks = count_values(paper_records, lambda record: first_text(record, "task"))
    subtasks = count_values(paper_records, lambda record: first_text(record, "subtask"))
    years = count_values(
        paper_records, lambda record: first_text(record, "publication_year", "year")
    )
    venues = count_present_values(
        paper_records, lambda record: first_text(record, "venue_label", "venue_name", "venue")
    )
    countries = count_present_values(records, normalized_country)
    institutions = count_present_values(
        records, institution_name
    )
    confidences = count_values(records, resolution_confidence)

    missing_venue = [
        record for record in records if not first_text(record, "venue_name", "venue")
    ]
    missing_url = [record for record in records if not paper_url(record)]
    missing_institution = [record for record in records if not institution_name(record)]
    missing_coordinates = [
        record for record in records if not has_usable_coordinates(record)
    ]
    unknown_task = [
        record
        for record in records
        if clean_text(record.get("task")).casefold() not in KNOWN_TASKS
    ]
    weak_confidence = [
        record
        for record in records
        if resolution_confidence(record) in {"low", "unresolved"}
    ]

    unique_papers = {paper_identity(record) for record in records}
    unique_institutions = {
        institution_identity(record)
        for record in records
        if institution_identity(record)
    }
    unique_countries = {
        normalized_country(record).casefold()
        for record in records
        if normalized_country(record)
    }

    lines = [
        "# Public Preview Quality Report",
        "",
        f"Source: `{input_path.as_posix()}`",
        "",
        "This report describes map records, not a manually curated bibliography. "
        "One paper may produce multiple records when collaborators have multiple institutions.",
        "Unique papers are identified by OpenAlex URL, then DOI, arXiv ID, or "
        "normalized title and year when stronger identifiers are unavailable.",
        "",
        "## Dataset Metadata",
        "",
    ]
    if metadata:
        lines.extend(["| Field | Value |", "| --- | --- |"])
        lines.extend(
            f"| {markdown_text(key)} | {markdown_text(metadata_value(value))} |"
            for key, value in sorted(metadata.items())
        )
    else:
        lines.append("No dataset-level metadata was provided.")

    lines.extend(
        [
            "",
            "## Overview",
            "",
            "| Metric | Count |",
            "| --- | ---: |",
            f"| Map records | {len(records)} |",
            f"| Unique papers | {len(unique_papers)} |",
            f"| Unique institutions | {len(unique_institutions)} |",
            f"| Countries | {len(unique_countries)} |",
            f"| arXiv/preprint records | {sum(is_arxiv_record(record) for record in records)} |",
            f"| Records with DOI | {sum(bool(normalized_doi(record.get('doi'))) for record in records)} |",
            f"| Records with venue | {len(records) - len(missing_venue)} |",
            f"| Records missing venue | {len(missing_venue)} |",
            f"| Records missing paper URL | {len(missing_url)} |",
            f"| Records missing institution | {len(missing_institution)} |",
            f"| Records missing coordinates | {len(missing_coordinates)} |",
            f"| Records with `needs_review=true` | {sum(parse_bool(record.get('needs_review')) for record in records)} |",
            "",
            "## Records by Task",
            "",
            *counter_table(tasks, "Task"),
            "",
            "## Records by Subtask",
            "",
            *counter_table(subtasks, "Subtask"),
            "",
            "## Records by Year",
            "",
            *counter_table(years, "Year", year_order=True),
            "",
            "## Top Venues",
            "",
            *counter_table(venues, "Venue", limit=TOP_LIMIT),
            "",
            "## Top Countries",
            "",
            *counter_table(countries, "Country", limit=TOP_LIMIT),
            "",
            "## Top Institutions",
            "",
            *counter_table(institutions, "Institution", limit=TOP_LIMIT),
            "",
            "## Records by Resolution Confidence",
            "",
            *counter_table(confidences, "Confidence"),
            "",
            "## Potential quality issues",
            "",
            *issue_section("Records missing venue", missing_venue),
            *issue_section("Records missing URL", missing_url),
            *issue_section("Records missing institution", missing_institution),
            *issue_section("Records missing coordinates", missing_coordinates),
            *issue_section("Records with unknown task", unknown_task),
            *issue_section(
                "Records with low or unresolved confidence", weak_confidence
            ),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_report(path: Path, report: str) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8") as handle:
            handle.write(report)
        temporary_path.replace(path)
    except OSError as error:
        raise ReportError(f"Could not write {path}: {error}") from error


def run(args: argparse.Namespace) -> int:
    if path_is_in_manual_data(args.output):
        print("Error: report output must not be inside data/manual/.", file=sys.stderr)
        return 1
    try:
        metadata, records = read_dataset(args.input)
        report = build_report(args.input, metadata, records)
        write_report(args.output, report)
    except ReportError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Wrote public preview quality report: {args.output}")
    print(f"Map records summarized: {len(records)}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
