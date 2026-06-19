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


DEFAULT_INPUT = Path("web/data/public_preview_map_data.json")
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
PAPER_LINK_FIELDS = ("paper_url", "openalex_url", "doi", "arxiv_url")


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


def normalized_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean_text(value),
        flags=re.IGNORECASE,
    ).casefold()


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


def print_summary(path: Path, records: Sequence[Any], issues: Sequence[Issue]) -> None:
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
    except ValidationInputError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    issues: List[Issue] = []
    for index, record in enumerate(records):
        validate_record(index, record, issues)

    print_summary(args.input, records, issues)
    errors = sum(issue.level == "ERROR" for issue in issues)
    warnings = sum(issue.level == "WARNING" for issue in issues)
    failed = errors > 0 or (args.strict and warnings > 0)
    if failed:
        reason = "errors or warnings" if args.strict else "errors"
        print(f"\nValidation failed: publication data contains {reason}.")
        return 1

    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
