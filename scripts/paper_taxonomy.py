#!/usr/bin/env python3
"""Canonical multi-label taxonomy normalization for curated papers."""

from __future__ import annotations

from typing import Any, Iterable, List, Sequence


TAXONOMY_DELIMITER = ";"
TASK_ORDER = ("detection", "source_attribution", "localization")
IMAGE_SCOPE_ORDER = (
    "fully_generated",
    "generative_editing",
    "deepfake",
    "traditional_manipulation",
)
RESEARCH_TYPE_ORDER = (
    "method",
    "dataset",
    "benchmark",
    "survey",
    "analysis_study",
)


class PaperTaxonomyError(ValueError):
    """Raised when a paper taxonomy dimension is malformed or unsupported."""


def normalize_taxonomy_values(
    value: Any,
    *,
    field: str,
    order: Sequence[str],
    compatibility: bool = False,
) -> List[str]:
    """Return unique values in canonical order for one taxonomy dimension."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        if not compatibility:
            raise PaperTaxonomyError(f"{field} must be an array")
        values: Iterable[Any] = value.split(TAXONOMY_DELIMITER)
    elif isinstance(value, (list, tuple)):
        values = value
    else:
        raise PaperTaxonomyError(f"{field} must be an array")

    allowed = frozenset(order)
    normalized = set()
    for raw in values:
        if not isinstance(raw, str):
            raise PaperTaxonomyError(f"every {field} item must be a string")
        item = raw.strip().casefold()
        if not item:
            raise PaperTaxonomyError(f"{field} must not contain empty strings")
        if item not in allowed:
            raise PaperTaxonomyError(
                f"unknown {field} value {raw!r}; expected one of " + ", ".join(order)
            )
        normalized.add(item)
    return [item for item in order if item in normalized]


def normalize_tasks(value: Any, *, compatibility: bool = False) -> List[str]:
    return normalize_taxonomy_values(
        value, field="tasks", order=TASK_ORDER, compatibility=compatibility
    )


def normalize_image_scopes(value: Any, *, compatibility: bool = False) -> List[str]:
    return normalize_taxonomy_values(
        value,
        field="image_scopes",
        order=IMAGE_SCOPE_ORDER,
        compatibility=compatibility,
    )


def normalize_research_types(value: Any, *, compatibility: bool = False) -> List[str]:
    return normalize_taxonomy_values(
        value,
        field="research_types",
        order=RESEARCH_TYPE_ORDER,
        compatibility=compatibility,
    )


def serialize_taxonomy_values(value: Any, *, field: str, order: Sequence[str]) -> str:
    return TAXONOMY_DELIMITER.join(
        normalize_taxonomy_values(value, field=field, order=order, compatibility=True)
    )


def serialize_tasks(value: Any) -> str:
    return serialize_taxonomy_values(value, field="tasks", order=TASK_ORDER)


def serialize_image_scopes(value: Any) -> str:
    return serialize_taxonomy_values(
        value, field="image_scopes", order=IMAGE_SCOPE_ORDER
    )


def serialize_research_types(value: Any) -> str:
    return serialize_taxonomy_values(
        value, field="research_types", order=RESEARCH_TYPE_ORDER
    )


def taxonomy_from_record(record: dict[str, Any]) -> dict[str, List[str]]:
    """Read the canonical taxonomy from a CSV or JSON record."""
    return {
        "tasks": normalize_tasks(record.get("tasks"), compatibility=True),
        "image_scopes": normalize_image_scopes(
            record.get("image_scopes"), compatibility=True
        ),
        "research_types": normalize_research_types(
            record.get("research_types"), compatibility=True
        ),
    }
