#!/usr/bin/env python3
"""Normalize paper identifiers and resolve public version links consistently."""

from __future__ import annotations

import re
from typing import Any, Dict, Mapping
from urllib.parse import unquote, urlsplit, urlunsplit


DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
ARXIV_DOI_PREFIX = "10.48550/arxiv."
ARXIV_ID_RE = re.compile(
    r"^(?:[a-z-]+(?:\.[a-z]{2})?/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?$",
    re.IGNORECASE,
)


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_doi(value: Any) -> str:
    doi = re.sub(
        r"^(?:doi:\s*|https?://(?:dx\.)?doi\.org/)",
        "",
        clean(value),
        flags=re.IGNORECASE,
    ).strip().rstrip("/")
    return doi.casefold() if DOI_RE.fullmatch(doi) else ""


def is_arxiv_doi(value: Any) -> bool:
    return normalize_doi(value).startswith(ARXIV_DOI_PREFIX)


def normalize_arxiv_id(*values: Any) -> str:
    for value in values:
        text = clean(value)
        doi = normalize_doi(text)
        if doi.startswith(ARXIV_DOI_PREFIX):
            text = doi[len(ARXIV_DOI_PREFIX):]
        text = re.sub(
            r"^https?://(?:www\.|export\.)?arxiv\.org/(?:abs|pdf)/",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\.pdf$", "", text, flags=re.IGNORECASE)
        if ARXIV_ID_RE.fullmatch(text):
            return re.sub(r"v\d+$", "", text, flags=re.IGNORECASE).casefold()
    return ""


def safe_http_url(value: Any) -> str:
    text = clean(value)
    try:
        parts = urlsplit(text)
    except ValueError:
        return ""
    if parts.scheme.casefold() not in {"http", "https"} or not parts.hostname:
        return ""
    return urlunsplit(parts)


def canonical_url(value: Any) -> str:
    url = safe_http_url(value)
    if not url:
        return ""
    parts = urlsplit(url)
    host = (parts.hostname or "").casefold().removeprefix("www.")
    path = unquote(parts.path).rstrip("/")
    if host in {"doi.org", "dx.doi.org"}:
        doi = normalize_doi(path.lstrip("/"))
        return f"doi:{doi}" if doi else ""
    arxiv_id = normalize_arxiv_id(url)
    if host in {"arxiv.org", "export.arxiv.org"} and arxiv_id:
        return f"arxiv:{arxiv_id}"
    if host == "openalex.org" and re.fullmatch(r"/W\d+", path, re.IGNORECASE):
        return f"openalex:{path[1:].casefold()}"
    port = parts.port
    if port in {80, 443}:
        port = None
    authority = host + (f":{port}" if port else "")
    return f"{authority}{path or '/'}?{parts.query}".casefold().rstrip("?")


def _formal_url(record: Mapping[str, Any], formal_doi: str) -> str:
    if formal_doi:
        return f"https://doi.org/{formal_doi}"
    for field in (
        "publisher_url",
        "published_url",
        "official_publication_url",
        "paper_url",
        "venue_url",
        "proceedings_url",
        "landing_page_url",
        "primary_url",
        "url",
    ):
        url = safe_http_url(record.get(field))
        target = canonical_url(url)
        if url and not target.startswith(
            ("arxiv:", "openalex:", f"doi:{ARXIV_DOI_PREFIX}")
        ):
            return url
    return ""


def resolve_public_links(record: Mapping[str, Any]) -> Dict[str, str]:
    """Return normalized formal, metadata-fallback, and arXiv version links."""
    source_doi = normalize_doi(record.get("doi") or record.get("doi_url"))
    formal_doi = "" if source_doi.startswith(ARXIV_DOI_PREFIX) else source_doi
    arxiv_id = normalize_arxiv_id(
        record.get("arxiv_id"),
        record.get("arxiv_url"),
        source_doi,
    )
    formal_url = _formal_url(record, formal_doi)
    formal_url_doi = normalize_doi(formal_url)
    if not formal_doi and formal_url_doi and not is_arxiv_doi(formal_url_doi):
        formal_doi = formal_url_doi
        formal_url = f"https://doi.org/{formal_doi}"
    openalex_url = safe_http_url(record.get("openalex_url"))
    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
    primary_url = formal_url or openalex_url or arxiv_url
    return {
        "formal_doi": formal_doi,
        "formal_url": formal_url,
        "openalex_url": openalex_url,
        "arxiv_id": arxiv_id,
        "arxiv_url": arxiv_url,
        "primary_url": primary_url,
    }
