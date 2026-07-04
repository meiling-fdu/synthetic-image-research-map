#!/usr/bin/env python3
"""Validate the maintainer-confirmed curated CSV database layer."""

from __future__ import annotations

import csv
import math
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
        ALLOWED_ENTRY_TYPES,
        ALLOWED_EXCLUSION_REASONS,
        ALLOWED_LOCATION_STATUSES,
        ALLOWED_INSTITUTION_REVIEW_STATUSES,
        ALLOWED_MAPPING_STATUSES,
        ALLOWED_REVIEW_STATUSES,
        ALLOWED_REVIEW_ACTIONS,
        ALLOWED_REVIEW_QUEUES,
        ALLOWED_SCOPE_STATUSES,
        ALLOWED_SUBTASKS,
        ALLOWED_TASKS,
        CURATED_DATA_DIR,
        EXPECTED_COLUMNS,
    )
except ImportError:  # Support direct execution from the repository root.
    from curated_schema import (
        ALLOWED_COORDINATE_STATUSES,
        ALLOWED_CURATION_STATUSES,
        ALLOWED_ENTRY_TYPES,
        ALLOWED_EXCLUSION_REASONS,
        ALLOWED_LOCATION_STATUSES,
        ALLOWED_INSTITUTION_REVIEW_STATUSES,
        ALLOWED_MAPPING_STATUSES,
        ALLOWED_REVIEW_STATUSES,
        ALLOWED_REVIEW_ACTIONS,
        ALLOWED_REVIEW_QUEUES,
        ALLOWED_SCOPE_STATUSES,
        ALLOWED_SUBTASKS,
        ALLOWED_TASKS,
        CURATED_DATA_DIR,
        EXPECTED_COLUMNS,
    )


BOOLEAN_LIKE_VALUES = {"true", "false", "1", "0", "yes", "no", "y", "n"}
YEAR_PATTERN = re.compile(r"[+-]?\d+")
COUNTRY_CODE_PATTERN = re.compile(r"[A-Z]{2}")


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


def normalize_institution(value: object) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


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
            alternative_identity = (
                clean(row.get("doi"))
                or clean(row.get("openalex_url"))
                or (clean(row.get("title")) and clean(row.get("year")))
            )
            if paper_id in paper_ids or alternative_identity:
                continue
            reference_description = (
                f"{field} does not exist in papers.csv: {paper_id!r}"
                if paper_id
                else f"{field} is blank"
            )
            if not alternative_identity:
                add_issue(
                    issues,
                    "ERROR",
                    filename,
                    (
                        f"{reference_description}, and no DOI, OpenAlex URL, "
                        "or title + year is provided"
                    ),
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
    issues: List[Issue],
) -> None:
    active_statuses = {"active", "needs_review"}
    active_rows: List[Tuple[int, Mapping[str, str]]] = []
    for row_number, row in enumerate(mappings, start=2):
        mapping_status = clean(row.get("mapping_status")).casefold()
        if mapping_status not in active_statuses:
            continue
        active_rows.append((row_number, row))
        for field in ("institution", "institution_authors", "review_note"):
            if not clean(row.get(field)):
                add_issue(
                    issues,
                    "ERROR",
                    "author_institution_mappings.csv",
                    f"{field} is required for an active mapping",
                    row_number,
                )
        if not any(
            clean(row.get(field))
            for field in ("raw_affiliation", "evidence_source", "evidence_url")
        ):
            add_issue(
                issues,
                "ERROR",
                "author_institution_mappings.csv",
                (
                    "active mapping requires raw_affiliation, evidence_source, "
                    "or evidence_url"
                ),
                row_number,
            )

    for position, (left_number, left) in enumerate(active_rows):
        left_keys = {
            value
            for value in (
                f"paper_id:{clean(left.get('paper_id')).casefold()}"
                if clean(left.get("paper_id"))
                else "",
                f"doi:{normalize_doi(left.get('doi'))}"
                if normalize_doi(left.get("doi"))
                else "",
                f"openalex:{normalize_openalex_url(left.get('openalex_url'))}"
                if normalize_openalex_url(left.get("openalex_url"))
                else "",
                (
                    f"title_year:{normalize_title(left.get('title'))}|"
                    f"{clean(left.get('year'))}"
                )
                if normalize_title(left.get("title")) and clean(left.get("year"))
                else "",
            )
            if value
        }
        left_institution = normalize_title(left.get("institution"))
        left_authors = normalize_title(left.get("institution_authors"))
        for right_number, right in active_rows[position + 1 :]:
            right_keys = {
                value
                for value in (
                    f"paper_id:{clean(right.get('paper_id')).casefold()}"
                    if clean(right.get("paper_id"))
                    else "",
                    f"doi:{normalize_doi(right.get('doi'))}"
                    if normalize_doi(right.get("doi"))
                    else "",
                    (
                        f"openalex:{normalize_openalex_url(right.get('openalex_url'))}"
                    )
                    if normalize_openalex_url(right.get("openalex_url"))
                    else "",
                    (
                        f"title_year:{normalize_title(right.get('title'))}|"
                        f"{clean(right.get('year'))}"
                    )
                    if normalize_title(right.get("title"))
                    and clean(right.get("year"))
                    else "",
                )
                if value
            }
            if (
                left_keys & right_keys
                and left_institution == normalize_title(right.get("institution"))
                and left_authors == normalize_title(
                    right.get("institution_authors")
                )
            ):
                add_issue(
                    issues,
                    "ERROR",
                    "author_institution_mappings.csv",
                    (
                        "duplicate active paper/institution/authors mapping "
                        f"across rows {left_number} and {right_number}"
                    ),
                )


def validate_paper_mapping_coverage(
    papers: Sequence[Mapping[str, str]],
    mappings: Sequence[Mapping[str, str]],
    issues: List[Issue],
) -> None:
    eligible_statuses = {"active", "needs_review"}
    mapping_paper_ids = {
        clean(row.get("paper_id"))
        for row in mappings
        if clean(row.get("mapping_status")) in eligible_statuses
        and clean(row.get("paper_id"))
    }
    for row_number, paper in enumerate(papers, start=2):
        if clean(paper.get("scope_status")) == "out_of_scope":
            continue
        paper_id = clean(paper.get("paper_id"))
        if paper_id and paper_id not in mapping_paper_ids:
            add_issue(
                issues,
                "WARNING",
                "papers.csv",
                "in-scope paper has no active or needs_review "
                "author–institution mapping",
                row_number,
            )


def validate_confirmed_locations(
    rows: Sequence[Mapping[str, str]],
    issues: List[Issue],
) -> None:
    normalized_positions: DefaultDict[str, List[int]] = defaultdict(list)
    location_id_positions: DefaultDict[str, List[int]] = defaultdict(list)
    required = (
        "location_id",
        "institution",
        "normalized_institution",
        "country_code",
        "lat",
        "lon",
        "coordinate_status",
        "review_note",
        "created_at",
        "updated_at",
        "created_by",
    )
    for row_number, row in enumerate(rows, start=2):
        for field in required:
            if not clean(row.get(field)):
                add_issue(
                    issues,
                    "ERROR",
                    "institution_locations.csv",
                    f"{field} is required",
                    row_number,
                )
        if not (
            clean(row.get("coordinate_source"))
            or clean(row.get("coordinate_source_url"))
        ):
            add_issue(
                issues,
                "ERROR",
                "institution_locations.csv",
                "coordinate_source or coordinate_source_url is required",
                row_number,
            )
        country_code = clean(row.get("country_code"))
        if country_code and not COUNTRY_CODE_PATTERN.fullmatch(country_code):
            add_issue(
                issues,
                "ERROR",
                "institution_locations.csv",
                "country_code must be two uppercase letters",
                row_number,
            )
        try:
            latitude = float(clean(row.get("lat")))
            longitude = float(clean(row.get("lon")))
        except ValueError:
            latitude = longitude = math.nan
            add_issue(
                issues,
                "ERROR",
                "institution_locations.csv",
                "lat and lon must be numeric",
                row_number,
            )
        if not math.isnan(latitude) and (
            not math.isfinite(latitude) or not -90 <= latitude <= 90
        ):
            add_issue(
                issues,
                "ERROR",
                "institution_locations.csv",
                "lat must be between -90 and 90",
                row_number,
            )
        if not math.isnan(longitude) and (
            not math.isfinite(longitude) or not -180 <= longitude <= 180
        ):
            add_issue(
                issues,
                "ERROR",
                "institution_locations.csv",
                "lon must be between -180 and 180",
                row_number,
            )
        normalized = normalize_institution(row.get("normalized_institution"))
        stored_normalized = clean(row.get("normalized_institution"))
        if stored_normalized and stored_normalized != normalized:
            add_issue(
                issues,
                "ERROR",
                "institution_locations.csv",
                "normalized_institution is not in normalized form",
                row_number,
            )
        if normalized:
            normalized_positions[normalized].append(row_number)
        location_id = clean(row.get("location_id")).casefold()
        if location_id:
            location_id_positions[location_id].append(row_number)

    for label, positions in (
        ("normalized institution", normalized_positions),
        ("location_id", location_id_positions),
    ):
        for value, row_numbers in positions.items():
            if len(row_numbers) > 1:
                add_issue(
                    issues,
                    "ERROR",
                    "institution_locations.csv",
                    f"duplicate {label} across rows "
                    f"{', '.join(map(str, row_numbers))}: {value!r}",
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


def validate_institution_aliases(
    aliases: Sequence[Mapping[str, str]],
    confirmed_locations: Sequence[Mapping[str, str]],
    issues: List[Issue],
) -> None:
    confirmed_by_name = {}
    for row in confirmed_locations:
        confirmed_by_name[normalize_institution(row.get("institution"))] = row
        confirmed_by_name[normalize_institution(
            row.get("normalized_institution")
        )] = row
    alias_targets: DefaultDict[str, set[str]] = defaultdict(set)
    alias_rows: DefaultDict[Tuple[str, str], List[int]] = defaultdict(list)
    for row_number, row in enumerate(aliases, start=2):
        alias = normalize_institution(row.get("alias_name"))
        canonical = normalize_institution(row.get("canonical_institution_name"))
        if not alias or not canonical:
            add_issue(
                issues, "ERROR", "institution_aliases.csv",
                "alias_name and canonical_institution_name are required", row_number
            )
            continue
        if clean(row.get("review_status")) != "confirmed":
            add_issue(
                issues, "ERROR", "institution_aliases.csv",
                "curated aliases must have review_status=confirmed", row_number
            )
        if canonical not in confirmed_by_name:
            add_issue(
                issues, "ERROR", "institution_aliases.csv",
                "canonical target is not a confirmed institution", row_number
            )
        alias_targets[alias].add(canonical)
        alias_rows[(alias, canonical)].append(row_number)
    for (alias, canonical), row_numbers in alias_rows.items():
        if len(row_numbers) > 1:
            add_issue(
                issues, "ERROR", "institution_aliases.csv",
                f"duplicate alias mapping on rows {row_numbers}: {alias} -> {canonical}"
            )
    for alias, targets in alias_targets.items():
        if len(targets) > 1:
            add_issue(
                issues, "ERROR", "institution_aliases.csv",
                f"ambiguous alias maps to multiple canonical institutions: {alias}"
            )


def main() -> int:
    issues: List[Issue] = []
    datasets, row_counts = read_curated_files(issues)
    validate_years(datasets, issues)

    papers = datasets.get("papers.csv", [])
    mappings = datasets.get("author_institution_mappings.csv", [])
    exclusions = datasets.get("paper_exclusions.csv", [])
    locations = datasets.get("institution_location_review.csv", [])
    confirmed_locations = datasets.get("institution_locations.csv", [])
    aliases = datasets.get("institution_aliases.csv", [])
    review_decisions = datasets.get("review_decisions.csv", [])
    version_merges = datasets.get("paper_version_merges.csv", [])

    validate_allowed_value(papers, "papers.csv", "task", ALLOWED_TASKS, issues)
    validate_allowed_value(
        papers, "papers.csv", "entry_type", ALLOWED_ENTRY_TYPES, issues
    )
    for row_number, paper in enumerate(papers, start=2):
        if not clean(paper.get("entry_type")):
            add_issue(
                issues,
                "ERROR",
                "papers.csv",
                "entry_type is required",
                row_number,
            )
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
        papers, "papers.csv", "scope_status", ALLOWED_SCOPE_STATUSES, issues
    )
    validate_allowed_value(
        papers, "papers.csv", "subtask", ALLOWED_SUBTASKS, issues
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
        "review_status",
        ALLOWED_INSTITUTION_REVIEW_STATUSES,
        issues,
    )
    validate_allowed_value(
        locations,
        "institution_location_review.csv",
        "location_status",
        ALLOWED_LOCATION_STATUSES,
        issues,
    )
    validate_allowed_value(
        confirmed_locations,
        "institution_locations.csv",
        "coordinate_status",
        {"known"},
        issues,
    )
    validate_allowed_value(
        mappings,
        "author_institution_mappings.csv",
        "mapping_status",
        ALLOWED_MAPPING_STATUSES,
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
    validate_boolean_fields(version_merges, "paper_version_merges.csv", issues)
    validate_allowed_value(
        version_merges,
        "paper_version_merges.csv",
        "status",
        {"confirmed_duplicate", "needs_review", "distinct"},
        issues,
    )
    merge_ids = set()
    duplicate_identities = set()
    for row_number, row in enumerate(version_merges, start=2):
        merge_id = clean(row.get("merge_id"))
        if not merge_id:
            add_issue(
                issues,
                "ERROR",
                "paper_version_merges.csv",
                "merge_id is required",
                row_number,
            )
        elif merge_id in merge_ids:
            add_issue(
                issues,
                "ERROR",
                "paper_version_merges.csv",
                f"duplicate merge_id {merge_id!r}",
                row_number,
            )
        merge_ids.add(merge_id)
        for prefix in ("canonical", "duplicate"):
            if not clean(row.get(f"{prefix}_title")):
                add_issue(
                    issues,
                    "ERROR",
                    "paper_version_merges.csv",
                    f"{prefix}_title is required",
                    row_number,
                )
        duplicate_identity = (
            normalize_openalex_url(row.get("duplicate_openalex_url"))
            or normalize_doi(row.get("duplicate_doi"))
            or (
                normalize_title(row.get("duplicate_title")),
                clean(row.get("duplicate_year")),
            )
        )
        if duplicate_identity in duplicate_identities:
            add_issue(
                issues,
                "ERROR",
                "paper_version_merges.csv",
                "duplicate paper is assigned to more than one canonical paper",
                row_number,
            )
        duplicate_identities.add(duplicate_identity)
    validate_allowed_value(
        review_decisions,
        "review_decisions.csv",
        "review_queue",
        ALLOWED_REVIEW_QUEUES,
        issues,
    )
    validate_allowed_value(
        review_decisions,
        "review_decisions.csv",
        "action",
        ALLOWED_REVIEW_ACTIONS,
        issues,
    )
    for row_number, row in enumerate(review_decisions, start=2):
        for field in (
            "decision_id",
            "review_queue",
            "target_type",
            "action",
            "review_note",
            "created_at",
            "updated_at",
            "created_by",
        ):
            if not clean(row.get(field)):
                add_issue(
                    issues,
                    "ERROR",
                    "review_decisions.csv",
                    f"{field} is required",
                    row_number,
                )
        if not any(
            clean(row.get(field))
            for field in ("title", "doi", "openalex_url", "institution")
        ):
            add_issue(
                issues,
                "ERROR",
                "review_decisions.csv",
                "paper or institution identity is required",
                row_number,
            )
    validate_references(datasets, issues)
    validate_mapping_evidence(mappings, issues)
    validate_paper_mapping_coverage(papers, mappings, issues)
    validate_confirmed_locations(confirmed_locations, issues)
    confirmed_by_name = {}
    for row in confirmed_locations:
        confirmed_by_name[normalize_institution(row.get("institution"))] = row
        confirmed_by_name[normalize_institution(
            row.get("normalized_institution")
        )] = row
    validate_institution_aliases(aliases, confirmed_locations, issues)
    for row_number, row in enumerate(locations, start=2):
        status = clean(row.get("review_status"))
        canonical = normalize_institution(row.get("canonical_institution_name"))
        if status == "confirmed" and canonical not in confirmed_by_name:
            add_issue(
                issues, "ERROR", "institution_location_review.csv",
                "confirmed status requires a canonical confirmed location", row_number
            )
        if status == "alias_of_confirmed" and canonical not in confirmed_by_name:
            add_issue(
                issues, "ERROR", "institution_location_review.csv",
                "alias_of_confirmed requires a confirmed canonical target", row_number
            )
    duplicates = validate_paper_duplicates(papers, issues)
    print_summary(row_counts, issues, duplicates)
    return 1 if any(issue.level == "ERROR" for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
