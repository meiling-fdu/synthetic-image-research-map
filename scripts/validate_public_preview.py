#!/usr/bin/env python3
"""Validate public preview map data before publication.

The validator is read-only, uses no external services, and accepts either the
legacy top-level record array or the metadata-plus-records object format.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    from .country_normalization import (
        CHINA_REGION_BY_CODE,
        normalize_country_region,
    )
except ImportError:  # Direct execution from the scripts directory.
    from country_normalization import (
        CHINA_REGION_BY_CODE,
        normalize_country_region,
    )

try:
    from .paper_version_merges import (
        DEFAULT_PAPER_VERSION_MERGES_PATH,
        PaperVersionMergeError,
        active_confirmed_merges,
        read_paper_version_merges,
        record_matches_merge_side,
    )
except ImportError:
    from paper_version_merges import (
        DEFAULT_PAPER_VERSION_MERGES_PATH,
        PaperVersionMergeError,
        active_confirmed_merges,
        read_paper_version_merges,
        record_matches_merge_side,
    )


DEFAULT_INPUT = Path("web/data/public_preview_map_data.json")
DEFAULT_PAPER_INPUT = Path("web/data/public_preview_papers.json")
ALLOWED_TASKS = {
    "detection",
    "source_attribution",
    "detection_and_source_attribution",
}
ALLOWED_SUBTASKS = {
    "synthetic_image_detection",
    "ai_generated_image_detection",
    "deepfake_image_detection",
    "generated_image_source_attribution",
    "source_identification",
    "source_verification",
    "detection_and_source_attribution",
    "unknown",
}
FORBIDDEN_LABELS = {
    "generator_attribution",
    "model_attribution",
    "generic_attribution",
    "uncertain",
}
MISSING_VALUE_STRINGS = {"", "none", "nan", "null"}
PAPER_LINK_FIELDS = ("paper_url", "openalex_url", "doi", "arxiv_url", "paper_id")


class ValidationInputError(RuntimeError):
    """An input error that should be shown without a traceback."""


@dataclass(frozen=True)
class Issue:
    level: str
    index: int
    title: str
    message: str


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate public preview JSON before committing it."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Public preview JSON (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--paper-version-merges",
        type=Path,
        default=DEFAULT_PAPER_VERSION_MERGES_PATH,
        help=(
            "Confirmed paper-version merge CSV "
            f"(default: {DEFAULT_PAPER_VERSION_MERGES_PATH})."
        ),
    )
    parser.add_argument(
        "--paper-input",
        type=Path,
        default=DEFAULT_PAPER_INPUT,
        help=f"Paper-level public preview JSON (default: {DEFAULT_PAPER_INPUT}).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero exit status when warnings are present.",
    )
    return parser.parse_args(argv)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalized_text(value: Any) -> str:
    return clean_text(value).casefold()


def author_name(value: Any) -> str:
    if isinstance(value, dict):
        return clean_text(value.get("name") or value.get("author"))
    return clean_text(value)


def normalized_author_name(value: Any) -> str:
    name = author_name(value)
    if name.count(",") == 1:
        family, given = (part.strip() for part in name.split(",", 1))
        name = f"{given} {family}"
    return " ".join(re.findall(r"\w+", name.casefold(), flags=re.UNICODE))


def is_bad_author_candidate(record: Any) -> bool:
    """Flag a mapped paper whose author list is still one unsplit long line."""
    if not isinstance(record, dict):
        return False
    authors = record.get("authors")
    affiliations = record.get("affiliations")
    if (
        not isinstance(authors, list)
        or len(authors) != 1
        or not isinstance(authors[0], dict)
        or not isinstance(affiliations, list)
        or len(affiliations) < 2
    ):
        return False
    author = authors[0]
    name = author_name(author)
    return (
        name.count(",") >= 2
        and author.get("affiliation_indices") == []
    )


def is_missing_value(value: Any) -> bool:
    return normalized_text(value) in MISSING_VALUE_STRINGS


def read_dataset(path: Path) -> Tuple[Dict[str, Any], List[Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as error:
        raise ValidationInputError(f"Could not read {path}: {error}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValidationInputError(f"Invalid JSON in {path}: {error}") from error

    if isinstance(payload, list):
        return {}, payload
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        metadata = payload.get("metadata")
        return metadata if isinstance(metadata, dict) else {}, payload["records"]
    raise ValidationInputError(
        f"{path} must contain an array of records or an object with a records array."
    )


def parse_integer(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if math.isfinite(value) and value.is_integer() else None
    text = clean_text(value)
    if not re.fullmatch(r"[+-]?\d+", text):
        return None
    return int(text)


def parse_boolean(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    text = normalized_text(value)
    if text in {"1", "true", "yes", "y"}:
        return True
    if text in {"0", "false", "no", "n"}:
        return False
    return None


def record_title(record: Dict[str, Any]) -> str:
    title = clean_text(record.get("title"))
    return title if title and not is_missing_value(title) else "<untitled>"


def institution_name(record: Dict[str, Any]) -> str:
    # Current map exports use `institution`; accept `institution_name` too so
    # the validator remains compatible with both public record schemas.
    for field in ("institution_name", "institution"):
        value = clean_text(record.get(field))
        if value and not is_missing_value(value):
            return value
    return ""


def normalized_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean_text(value),
        flags=re.IGNORECASE,
    ).casefold()


def normalized_title(value: Any) -> str:
    normalized = re.sub(r"[^\w]+", " ", normalized_text(value))
    return " ".join(normalized.replace("_", " ").split())


def has_formal_publication_evidence(record: Dict[str, Any]) -> bool:
    venue = normalized_text(record.get("venue") or record.get("venue_name"))
    doi = normalized_doi(record.get("doi"))
    return bool(
        (doi and not doi.startswith("10.48550/arxiv."))
        or (
            venue
            and not re.search(r"\b(?:arxiv|pre[\s-]?print)\b", venue)
        )
    )


def is_preprint_only_record(record: Dict[str, Any]) -> bool:
    venue = normalized_text(record.get("venue") or record.get("venue_name"))
    publication_type = normalized_text(record.get("publication_type"))
    doi = normalized_doi(record.get("doi"))
    return not has_formal_publication_evidence(record) and bool(
        parse_boolean(record.get("is_arxiv_preprint")) is True
        or publication_type in {"preprint", "posted-content"}
        or re.search(r"\b(?:arxiv|pre[\s-]?print)\b", venue)
        or doi.startswith("10.48550/arxiv.")
    )


def is_formal_publication(record: Dict[str, Any]) -> bool:
    return has_formal_publication_evidence(record)


def paper_identity(record: Dict[str, Any]) -> Tuple[str, ...]:
    openalex_url = normalized_text(record.get("openalex_url")).rstrip("/")
    if openalex_url and not is_missing_value(openalex_url):
        return "openalex", openalex_url
    doi = normalized_doi(record.get("doi"))
    if doi and not is_missing_value(doi):
        return "doi", doi
    arxiv_id = normalized_text(record.get("arxiv_id"))
    if arxiv_id and not is_missing_value(arxiv_id):
        return "arxiv", arxiv_id
    paper_url = normalized_text(record.get("paper_url")).rstrip("/")
    if paper_url and not is_missing_value(paper_url):
        return "url", paper_url
    title = re.sub(
        r"[^a-z0-9]+", " ", normalized_text(record.get("title"))
    ).strip()
    year = clean_text(record.get("publication_year") or record.get("year"))
    return "title_year", title, year


def validate_preprint_version_duplicates(
    records: Sequence[Any],
    issues: List[Issue],
) -> None:
    """Reject preprint/formal pairs that would render as duplicate papers."""
    by_title: Dict[str, List[Tuple[int, Dict[str, Any]]]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        title_key = normalized_title(record.get("title"))
        if title_key:
            by_title.setdefault(title_key, []).append((index, record))

    for title_records in by_title.values():
        if not any(is_formal_publication(record) for _, record in title_records):
            continue
        for index, record in title_records:
            if is_preprint_only_record(record):
                add_issue(
                    issues,
                    "ERROR",
                    index,
                    record_title(record),
                    "preprint version duplicates a formal publication with the "
                    "same normalized title",
                )


def validate_confirmed_version_merges(
    records: Sequence[Any],
    merge_rows: Sequence[Dict[str, str]],
    issues: List[Issue],
    *,
    paper_level: bool,
) -> None:
    """Reject confirmed duplicate leakage and missing canonical arXiv metadata."""
    for merge in active_confirmed_merges(merge_rows):
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            if record_matches_merge_side(record, merge, "duplicate"):
                add_issue(
                    issues,
                    "ERROR",
                    index,
                    record_title(record),
                    "confirmed duplicate paper version leaked into public preview",
                )
        if not paper_level:
            continue
        canonical = [
            (index, record)
            for index, record in enumerate(records)
            if isinstance(record, dict)
            and record_matches_merge_side(record, merge, "canonical")
        ]
        if len(canonical) != 1:
            add_issue(
                issues,
                "ERROR",
                canonical[0][0] if canonical else -1,
                clean_text(merge.get("canonical_title")) or "<missing canonical>",
                "confirmed version merge must resolve to exactly one canonical paper",
            )
            continue
        index, record = canonical[0]
        expected_arxiv = normalized_text(merge.get("duplicate_arxiv_id"))
        if expected_arxiv and normalized_text(record.get("arxiv_id")) != expected_arxiv:
            add_issue(
                issues,
                "ERROR",
                index,
                record_title(record),
                "canonical paper is missing the confirmed duplicate arXiv ID",
            )


def validate_curated_affiliation_supersession(
    map_records: Sequence[Any],
    paper_records: Sequence[Any],
    issues: List[Issue],
) -> None:
    """Report automatic institutions superseded by confirmed author mappings."""
    paper_by_doi = {
        normalized_doi(record.get("doi")): record
        for record in paper_records
        if isinstance(record, dict) and normalized_doi(record.get("doi"))
    }
    for index, record in enumerate(map_records):
        if (
            not isinstance(record, dict)
            or normalized_text(record.get("source_database")) != "openalex"
        ):
            continue
        paper = paper_by_doi.get(normalized_doi(record.get("doi")))
        if not paper:
            continue
        mappings = [
            mapping
            for mapping in paper.get("curated_mappings") or []
            if isinstance(mapping, dict)
            and normalized_text(mapping.get("mapping_status")) == "active"
        ]
        curated_institutions = {
            normalized_text(mapping.get("institution"))
            for mapping in mappings
            if clean_text(mapping.get("institution"))
        }
        if normalized_text(institution_name(record)) in curated_institutions:
            continue
        record_author_ids = {
            normalized_text(value)
            for value in record.get("institution_author_ids") or []
            if clean_text(value)
        }
        record_authors = {
            normalized_author_name(value)
            for value in record.get("institution_authors") or []
            if author_name(value)
        }
        overlaps_confirmed_author = any(
            bool(
                record_author_ids
                & {
                    normalized_text(value)
                    for value in mapping.get("institution_author_ids") or []
                    if clean_text(value)
                }
            )
            or bool(
                record_authors
                & {
                    normalized_author_name(value)
                    for value in mapping.get("institution_authors") or []
                    if author_name(value)
                }
            )
            for mapping in mappings
        )
        if overlaps_confirmed_author:
            add_issue(
                issues,
                "WARNING",
                index,
                record_title(record),
                "stale public and curated institutions overlap for a confirmed author",
            )


def add_issue(
    issues: List[Issue],
    level: str,
    index: int,
    title: str,
    message: str,
) -> None:
    issues.append(Issue(level=level, index=index, title=title, message=message))


def validate_paper_detail_schema(
    index: int,
    record: Dict[str, Any],
    issues: List[Issue],
    *,
    marker_record: bool,
) -> None:
    title = record_title(record)
    affiliations = record.get("affiliations")
    if not isinstance(affiliations, list):
        add_issue(issues, "ERROR", index, title, "affiliations must be an array")
        affiliations = []
    valid_indices = set()
    for expected_index, affiliation in enumerate(affiliations, start=1):
        if not isinstance(affiliation, dict):
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                "affiliation entries must be objects",
            )
            continue
        affiliation_index = parse_integer(affiliation.get("index"))
        if affiliation_index != expected_index:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                "affiliation indices must be consecutive and start at 1",
            )
        else:
            valid_indices.add(affiliation_index)
        if not clean_text(
            affiliation.get("name") or affiliation.get("canonical_name")
        ):
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"affiliation {expected_index} has no name",
            )
        for field in ("institution_id", "country", "region"):
            if field not in affiliation:
                add_issue(
                    issues,
                    "ERROR",
                    index,
                    title,
                    f"affiliation {expected_index} is missing {field}",
                )

    authors = record.get("authors")
    if not isinstance(authors, list):
        add_issue(issues, "ERROR", index, title, "authors must be an array")
        return
    authors_text = record.get("authors_text")
    if authors_text is not None and not clean_text(authors_text):
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "authors_text must be a non-empty legacy display string",
        )
    if is_bad_author_candidate(record):
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "mapped multi-affiliation record has an unsplit author line",
        )
    for author in authors:
        if not isinstance(author, dict):
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                "author entries must be objects",
            )
            continue
        name = author_name(author)
        if not name:
            add_issue(issues, "ERROR", index, title, "author name is missing")
        indices = author.get("affiliation_indices")
        if not isinstance(indices, list):
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"author affiliation_indices must be an array: {name}",
            )
            continue
        invalid_indices = [
            value
            for value in indices
            if parse_integer(value) not in valid_indices
        ]
        if invalid_indices:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"author references unknown affiliation index: {name}",
            )
        if not isinstance(author.get("is_current_marker_author"), bool):
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"author is_current_marker_author must be boolean: {name}",
            )
        if not marker_record and author.get("is_current_marker_author") is True:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                "paper-level authors cannot be current marker authors",
            )

    current_institution = record.get("current_institution")
    if marker_record:
        if not isinstance(current_institution, dict):
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                "marker current_institution must be an object",
            )
        elif parse_integer(current_institution.get("index")) not in valid_indices:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                "marker current_institution references an unknown affiliation",
            )
    elif current_institution is not None:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "paper-level current_institution must be null",
        )


def validate_record(index: int, record: Any, issues: List[Issue]) -> None:
    if not isinstance(record, dict):
        add_issue(issues, "ERROR", index, "<non-object>", "record is not a JSON object")
        return
    validate_paper_detail_schema(index, record, issues, marker_record=True)

    title = record_title(record)
    raw_title = clean_text(record.get("title"))
    if not raw_title:
        add_issue(issues, "ERROR", index, title, "title is missing or empty")
    elif is_missing_value(raw_title):
        add_issue(issues, "ERROR", index, title, "title contains a missing-value placeholder")

    task = clean_text(record.get("task"))
    if task.casefold() in FORBIDDEN_LABELS:
        add_issue(issues, "ERROR", index, title, f"forbidden task label: {task}")
    elif task not in ALLOWED_TASKS:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            f"task must be one of {', '.join(sorted(ALLOWED_TASKS))}",
        )

    subtask = clean_text(record.get("subtask"))
    if not subtask:
        add_issue(issues, "WARNING", index, title, "subtask is missing")
    elif subtask.casefold() in FORBIDDEN_LABELS:
        add_issue(issues, "ERROR", index, title, f"forbidden subtask label: {subtask}")
    elif subtask not in ALLOWED_SUBTASKS:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            f"unsupported subtask label: {subtask}",
        )

    for field in ("preliminary_task", "preliminary_subtask"):
        value = normalized_text(record.get(field))
        if value in FORBIDDEN_LABELS:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"{field} contains forbidden legacy label: {value}",
            )

    institution = institution_name(record)
    if not institution:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "institution_name/institution is missing or contains a missing-value placeholder",
        )
    for field in ("institution_name", "institution"):
        if (
            field in record
            and clean_text(record.get(field))
            and is_missing_value(record[field])
        ):
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"{field} contains a missing-value placeholder",
            )

    normalized_location = normalize_country_region(
        record.get("country"),
        record.get("country_code"),
        record.get("region"),
        record.get("region_code"),
        record.get("raw_country") if "raw_country" in record else None,
        record.get("raw_country_code") if "raw_country_code" in record else None,
    )
    normalized_region_code = normalized_location["region_code"]
    if normalized_region_code in CHINA_REGION_BY_CODE:
        expected = {
            "country": "China",
            "country_code": "CN",
            "region": CHINA_REGION_BY_CODE[normalized_region_code],
            "region_code": normalized_region_code,
        }
        actual = {
            "country": clean_text(record.get("country")),
            "country_code": clean_text(record.get("country_code")).upper(),
            "region": clean_text(record.get("region")),
            "region_code": clean_text(record.get("region_code")).upper(),
        }
        if actual != expected:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                "regional location must use "
                f"country=China, country_code=CN, "
                f"region={expected['region']}, "
                f"region_code={expected['region_code']}",
            )

    for field, minimum, maximum in (
        ("latitude", -90.0, 90.0),
        ("longitude", -180.0, 180.0),
    ):
        value = record.get(field)
        try:
            coordinate = float(value)
        except (TypeError, ValueError):
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"{field} is missing or not numeric",
            )
            continue
        if not math.isfinite(coordinate) or not minimum <= coordinate <= maximum:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"{field} must be between {minimum:g} and {maximum:g}",
            )

    year_value = record.get("publication_year")
    if is_missing_value(year_value):
        year_value = record.get("year")
    if is_missing_value(year_value):
        add_issue(issues, "ERROR", index, title, "publication_year/year is missing")
    elif parse_integer(year_value) is None:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "publication_year/year is not parseable as an integer",
        )

    has_paper_link = any(
        not is_missing_value(record.get(field)) for field in PAPER_LINK_FIELDS
    )
    if not has_paper_link:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            f"no paper link identifier in {', '.join(PAPER_LINK_FIELDS)}",
        )

    if "needs_review" in record:
        needs_review = parse_boolean(record.get("needs_review"))
        if needs_review is True:
            add_issue(issues, "ERROR", index, title, "needs_review is true")
        elif needs_review is None:
            add_issue(
                issues,
                "WARNING",
                index,
                title,
                "needs_review is not a recognized boolean value",
            )

    if "resolution_confidence" in record and not is_missing_value(
        record.get("resolution_confidence")
    ):
        confidence = normalized_text(record.get("resolution_confidence"))
        if confidence in {"low", "unresolved"}:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"resolution_confidence is {confidence}",
            )
        elif confidence not in {"medium", "high"}:
            add_issue(
                issues,
                "WARNING",
                index,
                title,
                f"unrecognized resolution_confidence: {confidence}",
            )


def validate_paper_record(index: int, record: Any, issues: List[Issue]) -> None:
    if not isinstance(record, dict):
        add_issue(issues, "ERROR", index, "<non-object>", "record is not a JSON object")
        return
    validate_paper_detail_schema(index, record, issues, marker_record=False)

    title = record_title(record)
    raw_title = clean_text(record.get("title"))
    if not raw_title or is_missing_value(raw_title):
        add_issue(issues, "ERROR", index, title, "title is missing or empty")

    task = clean_text(record.get("task"))
    allowed_paper_tasks = {*ALLOWED_TASKS, "uncertain"}
    if task.casefold() in FORBIDDEN_LABELS - {"uncertain"}:
        add_issue(issues, "ERROR", index, title, f"forbidden task label: {task}")
    elif task not in allowed_paper_tasks:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            f"task must be one of {', '.join(sorted(allowed_paper_tasks))}",
        )

    year_value = record.get("publication_year")
    if is_missing_value(year_value):
        year_value = record.get("year")
    if is_missing_value(year_value) or parse_integer(year_value) is None:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "publication_year/year is missing or not parseable as an integer",
        )

    has_paper_link = any(
        not is_missing_value(record.get(field)) for field in PAPER_LINK_FIELDS
    )
    if not has_paper_link:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            f"no paper link identifier in {', '.join(PAPER_LINK_FIELDS)}",
        )

    for field in (
        "has_map_location",
        "missing_affiliation",
        "missing_coordinates",
        "needs_review",
    ):
        if parse_boolean(record.get(field)) is None:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"{field} is missing or not a recognized boolean value",
            )

    map_record_count = parse_integer(record.get("map_record_count"))
    if map_record_count is None or map_record_count < 0:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "map_record_count is missing or not a non-negative integer",
        )
    else:
        has_map_location = parse_boolean(record.get("has_map_location"))
        if has_map_location is True and map_record_count < 1:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                "has_map_location=true requires map_record_count >= 1",
            )
        if has_map_location is False and map_record_count != 0:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                "has_map_location=false requires map_record_count=0",
            )

    coverage_status = normalized_text(record.get("coverage_status"))
    allowed_statuses = {
        "map_ready",
        "missing_affiliation",
        "missing_coordinates",
        "paper_only_review",
    }
    if coverage_status not in allowed_statuses:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            f"coverage_status must be one of {', '.join(sorted(allowed_statuses))}",
        )
    if parse_boolean(record.get("missing_affiliation")) is True:
        add_issue(
            issues,
            "WARNING",
            index,
            title,
            "public paper has no eligible author–institution mapping; markers "
            "and author affiliation numbers are unavailable",
        )
    mapped_author_keys = {
        normalized_author_name(author)
        for author in record.get("authors") or []
        if isinstance(author, dict) and author.get("affiliation_indices")
    }
    for author in record.get("authors") or []:
        if (
            mapped_author_keys
            and normalized_author_name(author) not in mapped_author_keys
        ):
            add_issue(
                issues,
                "WARNING",
                index,
                title,
                f"author has no institution index: {author_name(author)}",
            )


def print_summary(
    path: Path,
    records: Sequence[Any],
    issues: Sequence[Issue],
    *,
    paper_level: bool = False,
) -> None:
    object_records = [record for record in records if isinstance(record, dict)]
    unique_papers = {paper_identity(record) for record in object_records}
    unique_institutions = {
        institution_name(record).casefold()
        for record in object_records
        if institution_name(record)
    }
    errors = sum(issue.level == "ERROR" for issue in issues)
    warnings = sum(issue.level == "WARNING" for issue in issues)

    print(f"Public preview validation: {path}")
    print(f"Total records: {len(records)}")
    print(f"Unique papers: {len(unique_papers)}")
    if paper_level:
        with_locations = sum(
            parse_boolean(record.get("has_map_location")) is True
            for record in object_records
        )
        missing_affiliations = sum(
            parse_boolean(record.get("missing_affiliation")) is True
            for record in object_records
        )
        missing_coordinates = sum(
            parse_boolean(record.get("missing_coordinates")) is True
            for record in object_records
        )
        print(f"Papers with map locations: {with_locations}")
        print(f"Papers missing affiliations: {missing_affiliations}")
        print(f"Papers missing coordinates: {missing_coordinates}")
    else:
        print(f"Unique institutions: {len(unique_institutions)}")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")

    if issues:
        print("\nIssues:")
        for issue in issues:
            print(
                f"{issue.level} record[{issue.index}] "
                f"{issue.title!r}: {issue.message}"
            )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        _metadata, records = read_dataset(args.input)
        _paper_metadata, paper_records = read_dataset(args.paper_input)
        merge_rows = read_paper_version_merges(args.paper_version_merges)
    except (ValidationInputError, PaperVersionMergeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    issues: List[Issue] = []
    for index, record in enumerate(records):
        validate_record(index, record, issues)
    validate_preprint_version_duplicates(records, issues)
    validate_confirmed_version_merges(
        records, merge_rows, issues, paper_level=False
    )
    paper_issues: List[Issue] = []
    for index, record in enumerate(paper_records):
        validate_paper_record(index, record, paper_issues)
    validate_preprint_version_duplicates(paper_records, paper_issues)
    validate_confirmed_version_merges(
        paper_records, merge_rows, paper_issues, paper_level=True
    )

    print_summary(args.input, records, issues)
    print()
    print_summary(args.paper_input, paper_records, paper_issues, paper_level=True)
    errors = sum(issue.level == "ERROR" for issue in issues)
    warnings = sum(issue.level == "WARNING" for issue in issues)
    paper_errors = sum(issue.level == "ERROR" for issue in paper_issues)
    paper_warnings = sum(issue.level == "WARNING" for issue in paper_issues)
    failed = (
        errors > 0
        or paper_errors > 0
        or (args.strict and (warnings > 0 or paper_warnings > 0))
    )
    if failed:
        reason = "errors or warnings" if args.strict else "errors"
        print(f"\nValidation failed: publication data contains {reason}.")
        return 1

    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
