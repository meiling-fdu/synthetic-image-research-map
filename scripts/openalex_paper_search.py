#!/usr/bin/env python3
"""Read-only OpenAlex-first paper search for the local admin workflow."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Sequence, Tuple
from urllib.parse import urlencode

try:
    from .openalex_utils import (
        OPENALEX_API,
        OpenAlexFetchError,
        abstract_from_inverted_index,
        fetch_json_with_retry,
        fetch_openalex_work,
        normalize_openalex_id,
        title_similarity,
    )
except ImportError:
    from openalex_utils import (
        OPENALEX_API,
        OpenAlexFetchError,
        abstract_from_inverted_index,
        fetch_json_with_retry,
        fetch_openalex_work,
        normalize_openalex_id,
        title_similarity,
    )


ARXIV_ID_RE = re.compile(
    r"(?:arxiv[:/\s])?(\d{4}\.\d{4,5}(?:v\d+)?)",
    re.IGNORECASE,
)
DOI_URL_RE = re.compile(r"^https?://(?:dx\.)?doi\.org/", re.IGNORECASE)


class OpenAlexSearchInputError(ValueError):
    """A malformed or empty admin search request."""


def clean(value: Any) -> str:
    return " ".join(str(value if value is not None else "").split())


def normalize_doi(value: Any) -> str:
    return DOI_URL_RE.sub("", clean(value)).casefold()


def normalize_arxiv_id(value: Any) -> str:
    text = clean(value)
    match = ARXIV_ID_RE.search(text)
    return match.group(1) if match else ""


def paper_url_identifiers(value: Any) -> Tuple[str, str, str]:
    url = clean(value)
    url_casefolded = url.casefold()
    return (
        normalize_openalex_id(url),
        normalize_doi(url) if "doi.org/" in url_casefolded else "",
        normalize_arxiv_id(url) if "arxiv" in url_casefolded else "",
    )


def _work_authors(work: Mapping[str, Any]) -> List[str]:
    authors = []
    for authorship in work.get("authorships") or []:
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author")
        name = clean(author.get("display_name")) if isinstance(author, dict) else ""
        if name:
            authors.append(name)
    return authors


def _work_venue(work: Mapping[str, Any]) -> str:
    locations = [
        work.get("primary_location"),
        work.get("best_oa_location"),
        *(work.get("locations") or []),
    ]
    for location in locations:
        if not isinstance(location, dict):
            continue
        source = location.get("source")
        if isinstance(source, dict) and clean(source.get("display_name")):
            return clean(source.get("display_name"))
    host_venue = work.get("host_venue")
    return clean(host_venue.get("display_name")) if isinstance(host_venue, dict) else ""


def _primary_url(work: Mapping[str, Any]) -> str:
    primary_location = work.get("primary_location")
    if isinstance(primary_location, dict):
        landing_page = clean(primary_location.get("landing_page_url"))
        if landing_page:
            return landing_page
    doi = normalize_doi(work.get("doi"))
    return f"https://doi.org/{doi}" if doi else clean(work.get("id"))


def _work_arxiv_id(work: Mapping[str, Any]) -> str:
    doi = normalize_doi(work.get("doi"))
    if doi.startswith("10.48550/arxiv."):
        return doi.split("arxiv.", 1)[1]
    for location in work.get("locations") or []:
        if not isinstance(location, dict):
            continue
        landing_page_url = clean(location.get("landing_page_url"))
        if "arxiv" not in landing_page_url.casefold():
            continue
        arxiv_id = normalize_arxiv_id(landing_page_url)
        if arxiv_id:
            return arxiv_id
    return ""


def shape_work(work: Mapping[str, Any], query_title: str = "") -> Dict[str, Any]:
    title = clean(work.get("display_name") or work.get("title"))
    doi = normalize_doi(work.get("doi"))
    openalex_url = clean(work.get("id"))
    primary_url = _primary_url(work)
    similarity = title_similarity(query_title, title) if query_title else None
    return {
        "title": title,
        "year": work.get("publication_year") or "",
        "authors": _work_authors(work),
        "venue": _work_venue(work),
        "doi": doi,
        "arxiv_id": _work_arxiv_id(work),
        "openalex_url": openalex_url,
        "primary_url": primary_url,
        "paper_url": primary_url,
        "publication_type": clean(work.get("type")),
        "similarity_score": round(similarity, 4) if similarity is not None else None,
        "abstract": abstract_from_inverted_index(
            work.get("abstract_inverted_index")
        ),
    }


def _search_works(params: Mapping[str, str]) -> List[Dict[str, Any]]:
    url = f"{OPENALEX_API}/works?{urlencode(params)}"
    payload = fetch_json_with_retry(
        url,
        max_retries=1,
        base_sleep_seconds=1,
    )
    results = payload.get("results")
    if not isinstance(results, list):
        raise OpenAlexFetchError("OpenAlex search returned no results array")
    return [work for work in results if isinstance(work, dict)]


def search_openalex_papers(
    query: Mapping[str, Any],
    *,
    max_results: int = 10,
) -> Dict[str, Any]:
    title = clean(query.get("title"))
    doi = normalize_doi(query.get("doi"))
    arxiv_id = normalize_arxiv_id(query.get("arxiv_id"))
    paper_url = clean(query.get("paper_url"))
    url_openalex, url_doi, url_arxiv = paper_url_identifiers(paper_url)
    openalex_id = normalize_openalex_id(query.get("openalex_url")) or url_openalex
    doi = doi or url_doi
    arxiv_id = arxiv_id or url_arxiv

    if not any((title, doi, arxiv_id, paper_url, openalex_id)):
        raise OpenAlexSearchInputError(
            "provide at least one of title, DOI, arXiv ID, or paper URL"
        )
    max_results = max(1, min(int(max_results), 25))

    search_kind = ""
    works: Sequence[Mapping[str, Any]]
    if openalex_id:
        search_kind = "openalex_id"
        works = [fetch_openalex_work(openalex_id)]
    else:
        strategies: List[Tuple[str, Dict[str, str]]] = []
        if doi:
            strategies.append(
                (
                    "doi",
                    {
                        "filter": f"doi:https://doi.org/{doi}",
                        "per-page": str(max_results),
                    },
                )
            )
        elif arxiv_id:
            strategies.append(
                (
                    "arxiv_id",
                    {
                        "filter": (
                            "doi:https://doi.org/"
                            f"10.48550/arxiv.{arxiv_id.casefold()}"
                        ),
                        "per-page": str(max_results),
                    },
                )
            )
        if title:
            strategies.append(
                (
                    "title",
                    {
                        "search": title,
                        "per-page": str(max_results),
                        "sort": "relevance_score:desc",
                    },
                )
            )
        elif paper_url and not strategies:
            strategies.append(
                (
                    "paper_url",
                    {
                        "search": paper_url,
                        "per-page": str(max_results),
                        "sort": "relevance_score:desc",
                    },
                )
            )

        works = []
        for strategy_name, params in strategies:
            works = _search_works(params)
            search_kind = strategy_name
            if works:
                break

    seen = set()
    results = []
    for work in works:
        candidate = shape_work(work, title)
        identity = candidate["openalex_url"] or candidate["doi"]
        if not identity or identity in seen:
            continue
        seen.add(identity)
        results.append(candidate)
    if title:
        results.sort(
            key=lambda candidate: (
                -(candidate.get("similarity_score") or 0),
                clean(candidate.get("title")).casefold(),
            )
        )
    return {
        "query_type": search_kind,
        "count": len(results),
        "results": results[:max_results],
        "manual_fallback_available": True,
    }
