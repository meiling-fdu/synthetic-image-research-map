"""Normalize publication types and enforce their cross-layer invariants."""

from __future__ import annotations

from typing import Any, Mapping


ALLOWED_PUBLICATION_TYPES = ("conference", "journal", "preprint", "book")

# This is the authoritative cross-layer list.  Books may retain publisher and
# other ordinary bibliographic fields, but never venue taxonomy or the
# project-specific paper category that is defined for paper-like records.
BOOK_INCOMPATIBLE_FIELDS = (
    "venue",
    "venue_id",
    "venue_name",
    "venue_acronym",
    "venue_type",
    "venue_track",
    "raw_venue",
    "venue_aliases",
    "venue_label",
    "publication_venue",
    "host_venue",
    "host_venue_name",
    "entry_type",
    "paper_type",
    "category",
)

_LIST_FIELDS = {"venue_aliases"}

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


def is_book_publication(value: Any) -> bool:
    """Return whether *value* itself denotes a book, ignoring stale venues."""
    raw = str(value or "").strip().casefold().replace("_", "-")
    return _ALIASES.get(raw) == "book"


def book_incompatibilities(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return populated fields that violate the book metadata invariant."""
    if not is_book_publication(record.get("publication_type")):
        return {}
    return {
        field: record[field]
        for field in BOOK_INCOMPATIBLE_FIELDS
        if field in record
        and (
            bool(record[field])
            if not isinstance(record[field], str)
            else bool(record[field].strip())
        )
    }


def normalize_book_record(
    record: Mapping[str, Any], *, remove: bool = False
) -> dict[str, Any]:
    """Copy *record* and deterministically clear incompatible book metadata.

    Curated CSV callers use empty values so their fixed schema is preserved.
    Public JSON callers may request field removal instead.
    """
    normalized = dict(record)
    if not is_book_publication(normalized.get("publication_type")):
        return normalized
    normalized["publication_type"] = "book"
    for field in BOOK_INCOMPATIBLE_FIELDS:
        if remove:
            normalized.pop(field, None)
        elif field in normalized:
            normalized[field] = [] if field in _LIST_FIELDS else ""
    return normalized


def normalize_publication_type(
    value: Any,
    *,
    venue: Any = "",
    venue_type: Any = "",
    arxiv_id: Any = "",
    arxiv_url: Any = "",
    doi: Any = "",
) -> str:
    """Return a controlled value using shared publication-type precedence.

    An arXiv identifier is sufficient only for an otherwise venue-less,
    formal-DOI-less record. Unknown values deliberately remain unresolved.
    """
    resolved, _rule = resolve_publication_type(
        value,
        venue=venue,
        venue_type=venue_type,
        arxiv_id=arxiv_id,
        arxiv_url=arxiv_url,
        doi=doi,
    )
    return resolved


def resolve_publication_type(
    value: Any,
    *,
    venue: Any = "",
    venue_type: Any = "",
    arxiv_id: Any = "",
    arxiv_url: Any = "",
    doi: Any = "",
    explicit_override: bool = False,
) -> tuple[str, str]:
    """Resolve effective publication type and the rule that produced it."""
    raw = str(value or "").strip().casefold().replace("_", "-")
    normalized = _ALIASES.get(raw, "")
    venue_type_text = str(venue_type or "").strip().casefold().replace("_", "-")
    canonical_venue_type = _ALIASES.get(venue_type_text, "")
    if venue_type_text == "book-series":
        canonical_venue_type = "book"
    if canonical_venue_type in {"conference", "journal", "book"} and not explicit_override:
        return canonical_venue_type, "canonical_venue_type"
    if normalized and explicit_override:
        return normalized, "curated_override"
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
        return "conference", "bibliographic_venue"
    if raw in {"journal", "preprint", "book"}:
        return raw, "existing_value"
    if raw in _LEGACY_ARTICLE_ALIASES:
        return "journal", "legacy_article_alias"
    if raw in {"book-chapter", "book chapter", "chapter"}:
        return "book", "book_alias"
    if raw in {"posted-content", "posted content"}:
        return "preprint", "repository_source"
    if "engproc" in str(doi or "").casefold():
        return "conference", "doi_proceedings"
    if "journal" in venue_text:
        return "journal", "bibliographic_venue"
    if "book series" in venue_text or "book-series" in venue_text:
        return "book", "bibliographic_venue"
    if "arxiv" in venue_text:
        return "preprint", "repository_source"
    if normalized:
        return normalized, "existing_value"
    has_arxiv = bool(str(arxiv_id or "").strip() or str(arxiv_url or "").strip())
    repository_only = "repository" in str(venue_type or "").casefold()
    repository_doi = "zenodo" in str(doi or "").casefold()
    has_formal_evidence = bool(
        (str(venue or "").strip() and not repository_only)
        or (str(doi or "").strip() and not repository_doi)
    )
    if has_arxiv and not has_formal_evidence:
        return "preprint", "repository_source"
    return "", "unresolved"
