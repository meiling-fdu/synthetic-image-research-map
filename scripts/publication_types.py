"""Normalize bibliographic publication types to the project's vocabulary."""

from __future__ import annotations

from typing import Any


ALLOWED_PUBLICATION_TYPES = ("conference", "article", "preprint", "book")

_ALIASES = {
    "conference": "conference",
    "conference-paper": "conference",
    "conference paper": "conference",
    "proceedings": "conference",
    "proceedings-article": "conference",
    "proceedings article": "conference",
    "article": "article",
    "journal-article": "article",
    "journal article": "article",
    "preprint": "preprint",
    "posted-content": "preprint",
    "posted content": "preprint",
    "book": "book",
    "book-chapter": "book",
    "book chapter": "book",
}


def normalize_publication_type(
    value: Any, *, venue: Any = "", venue_type: Any = ""
) -> str:
    """Return a controlled value, giving conference venue evidence priority."""
    raw = str(value or "").strip().casefold().replace("_", "-")
    venue_text = f"{venue or ''} {venue_type or ''}".casefold()
    if (
        raw in {"conference", "conference-paper", "proceedings", "proceedings-article"}
        or "conference" in venue_text
        or "proceeding" in venue_text
    ):
        return "conference"
    return _ALIASES.get(raw, "")
