"""Normalize bibliographic publication types to the project's vocabulary."""

from __future__ import annotations

from typing import Any


ALLOWED_PUBLICATION_TYPES = ("conference", "journal", "preprint", "book")

_ALIASES = {
    "conference": "conference",
    "conference-paper": "conference",
    "conference paper": "conference",
    "proceedings": "conference",
    "proceedings-article": "conference",
    "proceedings article": "conference",
    "inproceedings": "conference",
    "article": "journal",
    "article-journal": "journal",
    "journal-article": "journal",
    "journal article": "journal",
    "journal": "journal",
    "review": "journal",
    "editorial": "journal",
    "letter": "journal",
    "preprint": "preprint",
    "posted-content": "preprint",
    "posted content": "preprint",
    "book": "book",
    "book-chapter": "book",
    "book chapter": "book",
    "chapter": "book",
}

_LEGACY_ARTICLE_ALIASES = {
    "article", "article-journal", "journal-article", "journal article"
}


def normalize_publication_type(
    value: Any,
    *,
    venue: Any = "",
    venue_type: Any = "",
    arxiv_id: Any = "",
    arxiv_url: Any = "",
    doi: Any = "",
) -> str:
    """Return a controlled value, giving conference venue evidence priority.

    An arXiv identifier is sufficient only for an otherwise venue-less,
    formal-DOI-less record. Unknown values deliberately remain unresolved.
    """
    raw = str(value or "").strip().casefold().replace("_", "-")
    venue_text = f"{venue or ''} {venue_type or ''}".casefold()
    if (
        raw
        in {
            "conference",
            "conference-paper",
            "conference paper",
            "proceedings",
            "proceedings-article",
            "proceedings article",
            "inproceedings",
        }
        or "conference" in venue_text
        or "proceeding" in venue_text
    ):
        return "conference"
    if raw in {"journal", "preprint", "book"}:
        return raw
    if raw in _LEGACY_ARTICLE_ALIASES:
        return "journal"
    if raw in {"book-chapter", "book chapter", "chapter"}:
        return "book"
    if raw in {"posted-content", "posted content"}:
        return "preprint"
    if "engproc" in str(doi or "").casefold():
        return "conference"
    if "journal" in venue_text:
        return "journal"
    if "book series" in venue_text or "book-series" in venue_text:
        return "book"
    if "arxiv" in venue_text:
        return "preprint"
    normalized = _ALIASES.get(raw, "")
    if normalized:
        return normalized
    has_arxiv = bool(str(arxiv_id or "").strip() or str(arxiv_url or "").strip())
    repository_only = "repository" in str(venue_type or "").casefold()
    repository_doi = "zenodo" in str(doi or "").casefold()
    has_formal_evidence = bool(
        (str(venue or "").strip() and not repository_only)
        or (str(doi or "").strip() and not repository_doi)
    )
    return "preprint" if has_arxiv and not has_formal_evidence else ""
