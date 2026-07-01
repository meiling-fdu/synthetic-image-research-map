#!/usr/bin/env python3
"""Read-only OpenAlex-first paper search for the local admin workflow."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Mapping, Sequence, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from .openalex_utils import (
        OPENALEX_API,
        OpenAlexFetchError,
        abstract_from_inverted_index,
        fetch_json_with_retry,
        fetch_openalex_work,
        normalize_openalex_id,
        normalize_title,
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
        normalize_title,
        title_similarity,
    )


ARXIV_ID_RE = re.compile(
    r"(?:arxiv[:/\s])?(\d{4}\.\d{4,5}(?:v\d+)?)",
    re.IGNORECASE,
)
DOI_URL_RE = re.compile(r"^https?://(?:dx\.)?doi\.org/", re.IGNORECASE)
ARXIV_API = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"
USER_AGENT = "synthetic-image-research-map/0.1 (local admin paper search)"
INTERNAL_FETCH_LIMIT = 50
STRONG_SIMILARITY = 0.85


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


def _institution_geo(institution: Mapping[str, Any]) -> Dict[str, Any]:
    geo = institution.get("geo")
    geo = geo if isinstance(geo, dict) else {}
    return {
        "city": clean(geo.get("city")),
        "country": clean(geo.get("country") or institution.get("country_code")),
        "latitude": geo.get("latitude") if geo.get("latitude") is not None else "",
        "longitude": geo.get("longitude") if geo.get("longitude") is not None else "",
    }


def _work_mapping_candidates(work: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Group OpenAlex authorship evidence by institution without dropping gaps."""
    grouped: Dict[str, Dict[str, Any]] = {}
    for index, authorship in enumerate(work.get("authorships") or [], start=1):
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author")
        author_name = (
            clean(author.get("display_name")) if isinstance(author, dict) else ""
        )
        raw_affiliations = [
            clean(value)
            for value in authorship.get("raw_affiliation_strings") or []
            if clean(value)
        ]
        institutions = [
            value
            for value in authorship.get("institutions") or []
            if isinstance(value, dict)
        ]
        if not institutions:
            for raw_affiliation in raw_affiliations:
                key = f"raw:{raw_affiliation.casefold()}"
                candidate = grouped.setdefault(
                    key,
                    {
                        "institution": raw_affiliation,
                        "openalex_institution_id": "",
                        "institution_authors": [],
                        "author_order": [],
                        "raw_affiliations": [],
                        "city": "",
                        "country": "",
                        "latitude": "",
                        "longitude": "",
                        "provenance_source": (
                            "OpenAlex raw affiliation strings"
                        ),
                    },
                )
                if author_name not in candidate["institution_authors"]:
                    candidate["institution_authors"].append(author_name)
                    candidate["author_order"].append(
                        clean(authorship.get("author_position")) or str(index)
                    )
                if raw_affiliation not in candidate["raw_affiliations"]:
                    candidate["raw_affiliations"].append(raw_affiliation)
        for institution in institutions:
            institution_name = clean(institution.get("display_name"))
            institution_id = clean(institution.get("id"))
            if not institution_name:
                continue
            key = institution_id or institution_name.casefold()
            candidate = grouped.setdefault(
                key,
                {
                    "institution": institution_name,
                    "openalex_institution_id": institution_id,
                    "institution_authors": [],
                    "author_order": [],
                    "raw_affiliations": [],
                    **_institution_geo(institution),
                    "provenance_source": "OpenAlex authorships",
                },
            )
            if author_name and author_name not in candidate["institution_authors"]:
                candidate["institution_authors"].append(author_name)
                candidate["author_order"].append(
                    clean(authorship.get("author_position")) or str(index)
                )
            for raw_affiliation in raw_affiliations:
                if raw_affiliation not in candidate["raw_affiliations"]:
                    candidate["raw_affiliations"].append(raw_affiliation)
    return list(grouped.values())


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
    ids = work.get("ids")
    if isinstance(ids, dict):
        arxiv_id = normalize_arxiv_id(ids.get("arxiv"))
        if arxiv_id:
            return arxiv_id
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
        "mapping_candidates": _work_mapping_candidates(work),
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


def _distinctive_subtitle(title: str) -> str:
    parts = re.split(r"\s*:\s*", title, maxsplit=1)
    if len(parts) == 2 and len(parts[1].split()) >= 4:
        return parts[1]
    words = title.split()
    return " ".join(words[-min(12, len(words)):])


def _title_strategies(title: str, fetch_limit: int) -> List[Tuple[str, Dict[str, str]]]:
    common = {
        "per-page": str(fetch_limit),
        "sort": "relevance_score:desc",
    }
    variants: List[Tuple[str, Dict[str, str]]] = [
        ("exact_title_phrase", {**common, "search": f'"{title}"'}),
        ("full_title", {**common, "search": title}),
    ]
    subtitle = _distinctive_subtitle(title)
    if normalize_title(subtitle) != normalize_title(title):
        variants.append(("distinctive_subtitle", {**common, "search": subtitle}))
    variants.append(
        (
            "title_search",
            {
                "filter": f"title.search:{title}",
                "per-page": str(fetch_limit),
            },
        )
    )
    return variants


def _fetch_arxiv_metadata(arxiv_id: str) -> Dict[str, Any]:
    """Return a candidate from arXiv's public Atom API for an exact identifier."""
    url = f"{ARXIV_API}?{urlencode({'id_list': arxiv_id, 'max_results': 1})}"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=45) as response:
        document = ET.fromstring(response.read())
    entry = document.find(f"{ATOM}entry")
    if entry is None:
        return {}
    entry_id = normalize_arxiv_id(entry.findtext(f"{ATOM}id"))
    if entry_id.casefold() != arxiv_id.casefold():
        return {}
    published = clean(entry.findtext(f"{ATOM}published"))
    doi = normalize_doi(entry.findtext(f"{ARXIV}doi"))
    return {
        "title": clean(entry.findtext(f"{ATOM}title")),
        "year": published[:4] if published else "",
        "authors": [
            clean(author.findtext(f"{ATOM}name"))
            for author in entry.findall(f"{ATOM}author")
            if clean(author.findtext(f"{ATOM}name"))
        ],
        "venue": "arXiv",
        "doi": doi,
        "arxiv_id": entry_id,
        "openalex_url": "",
        "primary_url": f"https://arxiv.org/abs/{entry_id}",
        "paper_url": f"https://arxiv.org/abs/{entry_id}",
        "publication_type": "preprint",
        "abstract": clean(entry.findtext(f"{ATOM}summary")),
        "candidate_source": "arxiv",
    }


def _candidate_priority(
    candidate: Dict[str, Any],
    *,
    query_title: str,
    query_doi: str,
    query_arxiv_id: str,
) -> Tuple[int, float, str]:
    candidate_doi = normalize_doi(candidate.get("doi"))
    candidate_arxiv = normalize_arxiv_id(candidate.get("arxiv_id"))
    normalized_exact = bool(
        query_title
        and normalize_title(candidate.get("title")) == normalize_title(query_title)
    )
    similarity = float(candidate.get("similarity_score") or 0)
    if query_doi and candidate_doi == query_doi:
        rank = 0
        basis = "exact_doi"
    elif query_arxiv_id and candidate_arxiv.casefold() == query_arxiv_id.casefold():
        rank = 1
        basis = "exact_arxiv"
    elif normalized_exact:
        rank = 2
        basis = "exact_normalized_title"
    elif query_title and similarity >= STRONG_SIMILARITY:
        rank = 3
        basis = "high_title_similarity"
    else:
        rank = 4
        basis = "weak_title_similarity" if query_title else "other"
    candidate["match_basis"] = basis
    candidate["match_strength"] = "weak" if rank == 4 else "strong"
    candidate["match_warning"] = (
        f"Weak title match ({similarity:.3f}); verify carefully."
        if rank == 4 and query_title
        else ""
    )
    return rank, -similarity, clean(candidate.get("title")).casefold()


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
    fetch_limit = max(INTERNAL_FETCH_LIMIT, max_results)

    search_kind = ""
    works: Sequence[Mapping[str, Any]]
    query_variants: List[Dict[str, str]] = []
    raw_candidate_count = 0
    doi_lookup_attempted = False
    arxiv_lookup_attempted = False
    arxiv_fallback_used = False
    arxiv_fallback_error = ""
    strategy_errors: List[str] = []
    if openalex_id:
        search_kind = "openalex_id"
        works = [fetch_openalex_work(openalex_id)]
        raw_candidate_count = len(works)
        query_variants.append(
            {"name": "openalex_id", "parameters": f"works/{openalex_id}"}
        )
    else:
        strategies: List[Tuple[str, Dict[str, str]]] = []
        if doi:
            doi_lookup_attempted = True
            strategies.append(
                (
                    "exact_doi",
                    {
                        "filter": f"doi:{doi}",
                        "per-page": str(fetch_limit),
                    },
                )
            )
        if arxiv_id:
            arxiv_lookup_attempted = True
            strategies.append(
                (
                    "exact_arxiv_doi",
                    {
                        "filter": f"doi:10.48550/arxiv.{arxiv_id.casefold()}",
                        "per-page": str(fetch_limit),
                    },
                )
            )
        if title:
            strategies.extend(_title_strategies(title, fetch_limit))
        elif paper_url and not strategies:
            strategies.append(
                (
                    "paper_url",
                    {
                        "search": paper_url,
                        "per-page": str(fetch_limit),
                        "sort": "relevance_score:desc",
                    },
                )
            )

        works = []
        for strategy_name, params in strategies:
            variant = {
                "name": strategy_name,
                "parameters": urlencode(params),
            }
            query_variants.append(variant)
            try:
                fetched = _search_works(params)
            except OpenAlexFetchError as error:
                variant["error"] = str(error)
                strategy_errors.append(f"{strategy_name}: {error}")
                continue
            raw_candidate_count += len(fetched)
            works.extend(fetched)
        if strategy_errors and len(strategy_errors) == len(strategies):
            raise OpenAlexFetchError("; ".join(strategy_errors))
        search_kind = "combined" if len(strategies) > 1 else strategies[0][0]

    seen = set()
    results = []
    for work in works:
        candidate = shape_work(work, title)
        identity = candidate["openalex_url"] or candidate["doi"]
        if not identity or identity in seen:
            continue
        seen.add(identity)
        candidate["candidate_source"] = "openalex"
        results.append(candidate)

    if arxiv_id and not any(
        normalize_arxiv_id(candidate.get("arxiv_id")).casefold()
        == arxiv_id.casefold()
        for candidate in results
    ):
        try:
            fallback = _fetch_arxiv_metadata(arxiv_id)
        except (OSError, TimeoutError, ET.ParseError) as error:
            fallback = {}
            arxiv_fallback_error = clean(error)
        if fallback:
            fallback["similarity_score"] = (
                round(title_similarity(title, fallback.get("title")), 4)
                if title
                else None
            )
            results.append(fallback)
            arxiv_fallback_used = True

    results.sort(
        key=lambda candidate: _candidate_priority(
            candidate,
            query_title=title,
            query_doi=doi,
            query_arxiv_id=arxiv_id,
        )
    )
    best_similarity = max(
        (
            float(candidate.get("similarity_score"))
            for candidate in results
            if candidate.get("similarity_score") is not None
        ),
        default=0.0,
    )
    visible_results = results[:max_results]
    return {
        "query_type": search_kind,
        "count": len(visible_results),
        "results": visible_results,
        "debug": {
            "query_variants": query_variants,
            "raw_candidates_fetched": raw_candidate_count,
            "unique_candidates_ranked": len(results),
            "best_normalized_title_similarity": round(best_similarity, 4),
            "doi_exact_lookup_attempted": doi_lookup_attempted,
            "arxiv_exact_lookup_attempted": arxiv_lookup_attempted,
            "arxiv_fallback_used": arxiv_fallback_used,
            "arxiv_fallback_error": arxiv_fallback_error,
            "query_errors": strategy_errors,
        },
        "manual_fallback_available": True,
    }
