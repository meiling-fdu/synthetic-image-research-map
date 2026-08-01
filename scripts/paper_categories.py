#!/usr/bin/env python3
"""Canonical paper-contribution category normalization."""

from __future__ import annotations

from typing import Any, Iterable, List


PAPER_CATEGORY_ORDER = ("method", "dataset", "benchmark", "survey", "analysis")
PAPER_CATEGORY_SET = frozenset(PAPER_CATEGORY_ORDER)
PAPER_CATEGORIES_DELIMITER = ";"


class PaperCategoriesError(ValueError):
    """Raised when paper categories are malformed or unsupported."""


def normalize_paper_categories(value: Any, *, compatibility: bool = False) -> List[str]:
    """Return validated, unique categories in canonical order.

    Compatibility mode accepts legacy scalar strings and semicolon-delimited CSV
    cells. Strict mode accepts arrays only, which is the normal JSON/API contract.
    """
    if value is None or value == "":
        return []
    if isinstance(value, str):
        if not compatibility:
            raise PaperCategoriesError("paper_categories must be an array")
        values: Iterable[Any] = value.split(PAPER_CATEGORIES_DELIMITER)
    elif isinstance(value, (list, tuple)):
        values = value
    else:
        raise PaperCategoriesError("paper_categories must be an array")

    normalized = set()
    for raw in values:
        if not isinstance(raw, str):
            raise PaperCategoriesError("every paper_categories item must be a string")
        category = raw.strip().casefold()
        if not category:
            raise PaperCategoriesError("paper_categories must not contain empty strings")
        if category not in PAPER_CATEGORY_SET:
            raise PaperCategoriesError(
                f"unknown paper category {raw!r}; expected one of "
                + ", ".join(PAPER_CATEGORY_ORDER)
            )
        normalized.add(category)
    return [category for category in PAPER_CATEGORY_ORDER if category in normalized]


def categories_from_record(record: dict[str, Any]) -> List[str]:
    """Read canonical or legacy record data at an explicit compatibility boundary."""
    if "paper_categories" in record:
        return normalize_paper_categories(record.get("paper_categories"), compatibility=True)
    return normalize_paper_categories(record.get("entry_type"), compatibility=True)


def serialize_paper_categories(value: Any) -> str:
    return PAPER_CATEGORIES_DELIMITER.join(
        normalize_paper_categories(value, compatibility=True)
    )
