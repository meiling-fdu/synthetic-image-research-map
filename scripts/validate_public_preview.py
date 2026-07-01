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
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    from .canonical_authorship import (
        CanonicalAuthorshipError,
        guard_no_legacy_runtime_references,
        normalize_arxiv,
        normalize_doi,
    )
    from .country_normalization import (
        CHINA_REGION_BY_CODE,
        normalize_country_region,
    )
except ImportError:  # Direct execution from the scripts directory.
    from canonical_authorship import (
        CanonicalAuthorshipError,
        guard_no_legacy_runtime_references,
        normalize_arxiv,
        normalize_doi,
    )
    from country_normalization import (
        CHINA_REGION_BY_CODE,
        normalize_country_region,
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


FORBIDDEN_INSTITUTION_NAMES = {"Federico II University Hospital"}


def validate_forbidden_institution_names(
    index: int,
    record: Dict[str, Any],
    issues: List[Issue],
) -> None:
    title = record_title(record)
    values = [record]
    for field in ("author_institution_affiliations", "curated_mappings"):
        nested = record.get(field)
        if isinstance(nested, list):
            values.extend(value for value in nested if isinstance(value, dict))
    aggregated = record.get("aggregated_institutions")
    names = [
        institution_name(value)
        for value in values
        if institution_name(value)
    ]
    if isinstance(aggregated, list):
        names.extend(clean_text(value) for value in aggregated)
    for name in names:
        if name in FORBIDDEN_INSTITUTION_NAMES:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"forbidden non-canonical institution name: {name}",
            )


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


def normalized_author_name(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value)).casefold()
    if "," in text:
        family, given = text.split(",", 1)
        text = f"{given} {family}"
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def public_paper_identity_keys(record: Dict[str, Any]) -> set[str]:
    keys = set()
    openalex_url = normalized_text(record.get("openalex_url")).rstrip("/")
    doi = normalized_doi(record.get("doi"))
    title = normalized_title(record.get("title"))
    year = clean_text(record.get("publication_year") or record.get("year"))
    if openalex_url:
        keys.add(f"openalex:{openalex_url}")
    if doi:
        keys.add(f"doi:{doi}")
    if title and year:
        keys.add(f"title_year:{title}|{year}")
    return keys


def _people(value: Any) -> List[str]:
    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]
    return [
        clean_text(item)
        for item in re.split(r"\s*;\s*", clean_text(value))
        if clean_text(item)
    ]


def _author_comparison_entries(record: Dict[str, Any]) -> List[Tuple[str, set[str]]]:
    authors = _people(record.get("institution_authors"))
    raw_author_ids = record.get("institution_author_ids")
    if isinstance(raw_author_ids, list):
        author_ids = [normalized_text(value) for value in raw_author_ids]
    else:
        author_ids = [
            normalized_text(value)
            for value in clean_text(raw_author_ids).split(";")
        ]
    entries = []
    for index, author in enumerate(authors):
        keys = {f"name:{normalized_author_name(author)}"}
        if index < len(author_ids) and normalized_text(author_ids[index]):
            keys.add(
                f"id:{normalized_text(author_ids[index]).rstrip('/')}"
            )
        entries.append((author, keys))
    return entries


def validate_curated_affiliation_supersession(
    map_records: Sequence[Any],
    paper_records: Sequence[Any],
    issues: List[Issue],
) -> None:
    curated_contexts = []
    for paper in paper_records:
        if not isinstance(paper, dict):
            continue
        mappings = [
            mapping
            for mapping in paper.get("curated_mappings") or []
            if isinstance(mapping, dict)
            and normalized_text(mapping.get("mapping_status")) == "active"
        ]
        if not mappings:
            continue
        author_institutions: Dict[str, set[str]] = {}
        for mapping in mappings:
            institution = normalized_title(mapping.get("institution"))
            for _author, author_keys in _author_comparison_entries(mapping):
                for author_key in author_keys:
                    author_institutions.setdefault(author_key, set()).add(
                        institution
                    )
        curated_contexts.append(
            (
                public_paper_identity_keys(paper),
                author_institutions,
            )
        )

    for index, record in enumerate(map_records):
        if not isinstance(record, dict):
            continue
        matching_context = next(
            (
                context
                for context in curated_contexts
                if context[0] & public_paper_identity_keys(record)
            ),
            None,
        )
        if matching_context is None:
            continue
        if normalized_text(record.get("source_database")) == "curated" or clean_text(
            record.get("mapping_id")
        ):
            continue
        if (
            normalized_text(record.get("public_evidence_mode")) == "add"
            and normalized_text(record.get("public_evidence_approval"))
            == "explicit_admin_supplement"
        ):
            continue
        add_issue(
            issues,
            "ERROR",
            index,
            record_title(record),
            "non-curated institution evidence remains after active curated "
            "author–institution mappings superseded public evidence",
        )
        stale_institution = normalized_title(
            record.get("institution_name") or record.get("institution")
        )
        author_institutions = matching_context[1]
        for author, author_keys in _author_comparison_entries(record):
            curated_institutions = {
                institution
                for author_key in author_keys
                for institution in author_institutions.get(author_key, set())
            }
            if curated_institutions and stale_institution not in curated_institutions:
                add_issue(
                    issues,
                    "ERROR",
                    index,
                    record_title(record),
                    f"normalized author {author!r} is assigned to stale public "
                    "and curated institutions",
                )


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


def add_issue(
    issues: List[Issue],
    level: str,
    index: int,
    title: str,
    message: str,
) -> None:
    issues.append(Issue(level=level, index=index, title=title, message=message))


def validate_record(index: int, record: Any, issues: List[Issue]) -> None:
    if not isinstance(record, dict):
        add_issue(issues, "ERROR", index, "<non-object>", "record is not a JSON object")
        return
    validate_canonical_authorship(index, record, issues)
    validate_forbidden_institution_names(index, record, issues)

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
    validate_forbidden_institution_names(index, record, issues)
    validate_canonical_authorship(index, record, issues)

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


def validate_canonical_authorship(
    index: int,
    record: Dict[str, Any],
    issues: List[Issue],
) -> None:
    """Hard-check the sole public author–institution representation."""
    title = record_title(record)
    canonical = record.get("canonical_authorship")
    if not isinstance(canonical, dict):
        add_issue(
            issues, "ERROR", index, title, "canonical_authorship is missing"
        )
        return
    authors = canonical.get("authors")
    institutions = canonical.get("institutions")
    if not isinstance(authors, list) or not isinstance(institutions, list):
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "canonical_authorship authors/institutions must be arrays",
        )
        return
    indices = [
        institution.get("index")
        for institution in institutions
        if isinstance(institution, dict)
    ]
    expected = list(range(1, len(institutions) + 1))
    if indices != expected:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "canonical institution indices must be unique, consecutive, and ordered",
        )
    institution_ids = {
        clean_text(institution.get("institution_id"))
        for institution in institutions
        if isinstance(institution, dict)
    }
    if "" in institution_ids or len(institution_ids) != len(institutions):
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "canonical institution IDs must be non-empty and unique",
        )
    referenced_ids: set[str] = set()
    for author in authors:
        if not isinstance(author, dict) or not clean_text(author.get("name")):
            add_issue(
                issues, "ERROR", index, title, "canonical author name is missing"
            )
            continue
        memberships = author.get("institutions")
        if not isinstance(memberships, list):
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"author has invalid institution membership: {author.get('name')}",
            )
            continue
        unknown = {
            clean_text(stable_id)
            for stable_id in memberships
        } - institution_ids
        if unknown:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"author references unknown institution IDs: {sorted(unknown)}",
            )
        if institutions and not memberships:
            add_issue(
                issues,
                "ERROR",
                index,
                title,
                f"author has no institution index: {author.get('name')}",
            )
        referenced_ids.update(clean_text(value) for value in memberships)
    orphaned = institution_ids - referenced_ids
    if orphaned:
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            f"orphan canonical institution IDs: {sorted(orphaned)}",
        )
    if "institution:unresolved" in institution_ids:
        add_issue(
            issues,
            "WARNING",
            index,
            title,
            "canonical authorship contains unresolved institution membership",
        )
    if contains_raw_affiliation_field(record):
        add_issue(
            issues,
            "ERROR",
            index,
            title,
            "raw OpenAlex affiliation field appears in frontend dataset",
        )


def contains_raw_affiliation_field(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            key in {"raw_affiliation", "raw_affiliation_text", "raw_affiliations"}
            or contains_raw_affiliation_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(contains_raw_affiliation_field(item) for item in value)
    return False


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


def validate_canonical_paper_uniqueness(
    records: Sequence[Dict[str, Any]], issues: List[Issue]
) -> None:
    for label, getter in (
        ("canonical paper", lambda row: clean_text(row.get("paper_id"))),
        ("DOI", lambda row: normalize_doi(row.get("doi"))),
        ("arXiv ID", lambda row: normalize_arxiv(row.get("arxiv_id"))),
    ):
        seen = set()
        for index, record in enumerate(records):
            value = getter(record)
            if not value:
                continue
            if value in seen:
                add_issue(
                    issues, "ERROR", index, record_title(record),
                    f"duplicate {label}: {value}",
                )
            seen.add(value)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        guard_no_legacy_runtime_references()
        _metadata, records = read_dataset(args.input)
        _paper_metadata, paper_records = read_dataset(args.paper_input)
    except (ValidationInputError, CanonicalAuthorshipError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    issues: List[Issue] = []
    for index, record in enumerate(records):
        validate_record(index, record, issues)
    validate_preprint_version_duplicates(records, issues)
    paper_issues: List[Issue] = []
    for index, record in enumerate(paper_records):
        validate_paper_record(index, record, paper_issues)
    validate_canonical_paper_uniqueness(paper_records, paper_issues)
    validate_preprint_version_duplicates(paper_records, paper_issues)
    validate_curated_affiliation_supersession(
        records, paper_records, issues
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
