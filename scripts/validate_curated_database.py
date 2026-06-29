#!/usr/bin/env python3
"""Validate the maintainer-confirmed curated CSV database layer."""

from __future__ import annotations

import csv
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Mapping, Sequence, Tuple

try:
    from .curated_schema import (
        ALLOWED_COORDINATE_STATUSES,
        ALLOWED_CURATION_STATUSES,
        ALLOWED_EXCLUSION_REASONS,
        ALLOWED_REVIEW_STATUSES,
        ALLOWED_TASKS,
        CURATED_DATA_DIR,
        EXPECTED_COLUMNS,
    )
except ImportError:  # Support direct execution from the repository root.
    from curated_schema import (
        ALLOWED_COORDINATE_STATUSES,
        ALLOWED_CURATION_STATUSES,
        ALLOWED_EXCLUSION_REASONS,
        ALLOWED_REVIEW_STATUSES,
        ALLOWED_TASKS,
        CURATED_DATA_DIR,
        EXPECTED_COLUMNS,
    )


BOOLEAN_LIKE_VALUES = {"true", "false", "1", "0", "yes", "no", "y", "n"}
YEAR_PATTERN = re.compile(r"[+-]?\d+")


@dataclass(frozen=True)
class Issue:
    level: str
    filename: str
    row_number: int | None
    message: str


@dataclass(frozen=True)
class DuplicateCandidate:
    filename: str
    field: str
    value: str
    row_numbers: Tuple[int, ...]


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: object) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalize_doi(value: object) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean(value),
        flags=re.IGNORECASE,
    ).casefold()


def normalize_openalex_url(value: object) -> str:
    return clean(value).casefold().rstrip("/")


def add_issue(
    issues: List[Issue],
    level: str,
    filename: str,
    message: str,
    row_number: int | None = None,
) -> None:
    issues.append(Issue(level, filename, row_number, message))


def read_curated_files(
    issues: List[Issue],
) -> Tuple[Dict[str, List[Dict[str, str]]], Dict[str, int]]:
    datasets: Dict[str, List[Dict[str, str]]] = {}
    row_counts: Dict[str, int] = {}

    if not CURATED_DATA_DIR.is_dir():
        add_issue(issues, "ERROR", str(CURATED_DATA_DIR), "directory does not exist")
        return datasets, row_counts

    unexpected = sorted(
        path.name
        for path in CURATED_DATA_DIR.glob("*.csv")
        if path.name not in EXPECTED_COLUMNS
    )
    for filename in unexpected:
        add_issue(
            issues,
            "WARNING",
            filename,
            "CSV is not part of the curated schema and was not validated",
        )

    for filename, expected_header in EXPECTED_COLUMNS.items():
        path = CURATED_DATA_DIR / filename
        if not path.is_file():
            add_issue(issues, "ERROR", filename, "required file does not exist")
            continue
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                actual_header = tuple(reader.fieldnames or ())
                if actual_header != expected_header:
                    add_issue(
                        issues,
                        "ERROR",
                        filename,
                        "header does not exactly match the expected columns/order",
                    )
                    datasets[filename] = []
                    row_counts[filename] = 0
                    continue
                rows = [dict(row) for row in reader]
        except (OSError, UnicodeError, csv.Error) as error:
            add_issue(issues, "ERROR", filename, f"could not read CSV: {error}")
            continue

        datasets[filename] = rows
        row_counts[filename] = len(rows)

    return datasets, row_counts


def validate_years(
    datasets: Mapping[str, Sequence[Mapping[str, str]]],
    issues: List[Issue],
) -> None:
    for filename, rows in datasets.items():
        for row_number, row in enumerate(rows, start=2):
            year = clean(row.get("year"))
            if year and not YEAR_PATTERN.fullmatch(year):
                add_issue(
                    issues,
                    "ERROR",
                    filename,
                    f"year must be an integer when present: {year!r}",
                    row_number,
                )


def validate_allowed_value(
    rows: Sequence[Mapping[str, str]],
    filename: str,
    field: str,
    allowed: Iterable[str],
    issues: List[Issue],
) -> None:
    allowed_values = set(allowed)
    for row_number, row in enumerate(rows, start=2):
        value = clean(row.get(field))
        if value and value not in allowed_values:
            add_issue(
                issues,
                "ERROR",
                filename,
                f"{field} has unsupported value {value!r}",
                row_number,
            )


def duplicate_groups(
    rows: Sequence[Mapping[str, str]],
    field: str,
    normalizer,
) -> List[Tuple[str, Tuple[int, ...]]]:
    positions: DefaultDict[str, List[int]] = defaultdict(list)
    display_values: Dict[str, str] = {}
    for row_number, row in enumerate(rows, start=2):
        raw_value = clean(row.get(field))
        value = normalizer(raw_value)
        if not value:
            continue
        positions[value].append(row_number)
        display_values.setdefault(value, raw_value)
    return [
        (display_values[value], tuple(row_numbers))
        for value, row_numbers in positions.items()
        if len(row_numbers) > 1
    ]


def validate_paper_duplicates(
    papers: Sequence[Mapping[str, str]],
    issues: List[Issue],
) -> List[DuplicateCandidate]:
    candidates: List[DuplicateCandidate] = []
    checks = (
        ("paper_id", lambda value: clean(value).casefold()),
        ("doi", normalize_doi),
        ("openalex_url", normalize_openalex_url),
    )
    for field, normalizer in checks:
        for value, row_numbers in duplicate_groups(papers, field, normalizer):
            candidates.append(
                DuplicateCandidate("papers.csv", field, value, row_numbers)
            )
            add_issue(
                issues,
                "ERROR",
                "papers.csv",
                f"duplicate {field} across rows {', '.join(map(str, row_numbers))}: {value!r}",
            )

    title_year_positions: DefaultDict[Tuple[str, str], List[int]] = defaultdict(list)
    title_year_display: Dict[Tuple[str, str], str] = {}
    for row_number, row in enumerate(papers, start=2):
        title = normalize_title(row.get("title"))
        year = clean(row.get("year"))
        if not title or not year:
            continue
        key = (title, year)
        title_year_positions[key].append(row_number)
        title_year_display.setdefault(key, clean(row.get("title")))
    for key, row_numbers in title_year_positions.items():
        if len(row_numbers) < 2:
            continue
        value = f"{title_year_display[key]} ({key[1]})"
        candidates.append(
            DuplicateCandidate(
                "papers.csv",
                "normalized_title+year",
                value,
                tuple(row_numbers),
            )
        )
        add_issue(
            issues,
            "ERROR",
            "papers.csv",
            "duplicate normalized title + year across rows "
            f"{', '.join(map(str, row_numbers))}: {value!r}",
        )
    return candidates


def validate_references(
    datasets: Mapping[str, Sequence[Mapping[str, str]]],
    issues: List[Issue],
) -> None:
    papers = datasets.get("papers.csv", [])
    paper_ids = {clean(row.get("paper_id")) for row in papers if clean(row.get("paper_id"))}

    reference_files = (
        ("author_institution_mappings.csv", "paper_id"),
        ("institution_location_review.csv", "related_paper_id"),
    )
    for filename, field in reference_files:
        for row_number, row in enumerate(datasets.get(filename, []), start=2):
            paper_id = clean(row.get(field))
            if paper_id and paper_id not in paper_ids:
                add_issue(
                    issues,
                    "ERROR",
                    filename,
                    f"{field} does not exist in papers.csv: {paper_id!r}",
                    row_number,
                )

    for row_number, row in enumerate(
        datasets.get("paper_exclusions.csv", []), start=2
    ):
        paper_id = clean(row.get("paper_id"))
        if paper_id and paper_id in paper_ids:
            continue
        alternative_identity = (
            clean(row.get("doi"))
            or clean(row.get("openalex_url"))
            or (clean(row.get("title")) and clean(row.get("year")))
        )
        reference_description = (
            f"paper_id is not in papers.csv: {paper_id!r}"
            if paper_id
            else "paper_id is blank"
        )
        if alternative_identity:
            add_issue(
                issues,
                "WARNING",
                "paper_exclusions.csv",
                f"{reference_description}; exclusion will rely on alternate identity",
                row_number,
            )
        else:
            add_issue(
                issues,
                "ERROR",
                "paper_exclusions.csv",
                f"{reference_description}, and no DOI, OpenAlex URL, or title + year is provided",
                row_number,
            )


def validate_boolean_fields(
    rows: Sequence[Mapping[str, str]],
    filename: str,
    issues: List[Issue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        for field in (
            "is_active",
            "excluded_from_public_preview",
            "excluded_from_map",
        ):
            value = clean(row.get(field))
            if value and value.casefold() not in BOOLEAN_LIKE_VALUES:
                add_issue(
                    issues,
                    "ERROR",
                    filename,
                    f"{field} must be boolean-like when present: {value!r}",
                    row_number,
                )


def validate_mapping_evidence(
    mappings: Sequence[Mapping[str, str]],
    papers: Sequence[Mapping[str, str]],
    issues: List[Issue],
) -> None:
    paper_status = {
        clean(row.get("paper_id")): clean(row.get("curation_status"))
        for row in papers
        if clean(row.get("paper_id"))
    }
    manual_mapping_statuses = {"manually_added", "manual", "added_by_admin"}
    for row_number, row in enumerate(mappings, start=2):
        paper_id = clean(row.get("paper_id"))
        mapping_status = clean(row.get("mapping_status")).casefold()
        is_manual = (
            mapping_status in manual_mapping_statuses
            or paper_status.get(paper_id) == "manually_added"
        )
        if (
            is_manual
            and not clean(row.get("evidence_source"))
            and not clean(row.get("evidence_url"))
        ):
            add_issue(
                issues,
                "WARNING",
                "author_institution_mappings.csv",
                "manually added mapping has no evidence_source or evidence_url",
                row_number,
            )


def print_summary(
    row_counts: Mapping[str, int],
    issues: Sequence[Issue],
    duplicates: Sequence[DuplicateCandidate],
) -> None:
    errors = [issue for issue in issues if issue.level == "ERROR"]
    warnings = [issue for issue in issues if issue.level == "WARNING"]

    print("Curated database validation")
    print(f"Files checked: {len(row_counts)}/{len(EXPECTED_COLUMNS)}")
    print("Rows per file:")
    for filename in EXPECTED_COLUMNS:
        count = row_counts.get(filename)
        print(f"  {filename}: {count if count is not None else 'not checked'}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Duplicate candidates: {len(duplicates)}")

    for issue in issues:
        location = issue.filename
        if issue.row_number is not None:
            location += f":{issue.row_number}"
        print(f"{issue.level}: {location}: {issue.message}")
    for duplicate in duplicates:
        rows = ", ".join(map(str, duplicate.row_numbers))
        print(
            f"DUPLICATE: {duplicate.filename} {duplicate.field} "
            f"rows {rows}: {duplicate.value}"
        )


def main() -> int:
    issues: List[Issue] = []
    datasets, row_counts = read_curated_files(issues)
    validate_years(datasets, issues)

    papers = datasets.get("papers.csv", [])
    mappings = datasets.get("author_institution_mappings.csv", [])
    exclusions = datasets.get("paper_exclusions.csv", [])
    locations = datasets.get("institution_location_review.csv", [])

    validate_allowed_value(papers, "papers.csv", "task", ALLOWED_TASKS, issues)
    validate_allowed_value(
        papers,
        "papers.csv",
        "curation_status",
        ALLOWED_CURATION_STATUSES,
        issues,
    )
    validate_allowed_value(
        papers, "papers.csv", "review_status", ALLOWED_REVIEW_STATUSES, issues
    )
    validate_allowed_value(
        exclusions,
        "paper_exclusions.csv",
        "reason",
        ALLOWED_EXCLUSION_REASONS,
        issues,
    )
    validate_allowed_value(
        locations,
        "institution_location_review.csv",
        "coordinate_status",
        ALLOWED_COORDINATE_STATUSES,
        issues,
    )
    validate_boolean_fields(exclusions, "paper_exclusions.csv", issues)
    validate_references(datasets, issues)
    validate_mapping_evidence(mappings, papers, issues)
    duplicates = validate_paper_duplicates(papers, issues)
    print_summary(row_counts, issues, duplicates)
    return 1 if any(issue.level == "ERROR" for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
