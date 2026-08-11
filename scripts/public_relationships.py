#!/usr/bin/env python3
"""Canonical public paper/institution/location/author relationship identity."""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Mapping, Sequence


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalized_text(value: Any) -> str:
    value = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", value, flags=re.UNICODE))


def normalized_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/", "", clean(value), flags=re.I
    ).casefold()


def paper_relationship_identity(record: Mapping[str, Any]) -> tuple[str, ...]:
    """Return the strongest stable paper identity available on a public row."""
    doi = normalized_doi(record.get("doi"))
    if doi:
        return ("doi", doi)
    paper_id = clean(record.get("paper_id")).casefold()
    if paper_id:
        return ("paper", paper_id)
    arxiv = clean(record.get("arxiv_id")).casefold()
    if arxiv:
        return ("arxiv", arxiv)
    openalex = clean(record.get("openalex_url") or record.get("openalex_id")).casefold().rstrip("/")
    if openalex:
        return ("openalex", openalex)
    return (
        "title_year",
        normalized_text(record.get("title")),
        clean(record.get("publication_year") or record.get("year")),
    )


def normalized_author_set(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        values: Sequence[Any] = value.split(";")
    elif isinstance(value, Sequence):
        values = value
    else:
        values = ()
    names = set()
    for author in values:
        if isinstance(author, Mapping):
            author = author.get("display_name") or author.get("name")
        author_text = clean(author)
        if "," in author_text:
            family, given = author_text.split(",", 1)
            author_text = f"{given} {family}"
        normalized = normalized_text(author_text)
        if normalized:
            names.add(normalized)
    return tuple(sorted(names))


def public_relationship_key(record: Mapping[str, Any]) -> tuple[Any, ...]:
    """Identity invariant shared by materialization and final validation."""
    institution = clean(
        record.get("institution_id")
        or record.get("canonical_institution_id")
        or record.get("canonical_institution_name")
        or record.get("institution_name")
        or record.get("institution")
    ).casefold()
    location = clean(record.get("location_id")).casefold()
    return (
        paper_relationship_identity(record),
        institution,
        location,
        normalized_author_set(record.get("institution_authors")),
    )
