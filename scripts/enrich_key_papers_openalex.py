#!/usr/bin/env python3
"""Enrich the manual key-paper coverage checklist with OpenAlex identifiers.

This is a manual coverage-auditing utility. It writes a separate enriched CSV
and never adds records to candidate data or the public map.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import os
import re
import tempfile
import time
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "manual" / "key_papers.csv"
DEFAULT_OUTPUT = ROOT / "data" / "manual" / "key_papers_enriched.csv"
DEFAULT_REPORT = ROOT / "docs" / "key_paper_enrichment_report.md"
DEFAULT_USER_AGENT = (
    "synthetic-image-research-map/0.1 "
    "(https://github.com/meiling-fdu/synthetic-image-research-map)"
)
DEFAULT_SLEEP_SECONDS = 0.5
OPENALEX_WORKS_URL = "https://api.openalex.org/works"
DEFAULT_PER_PAGE = 25
MAX_PER_PAGE = 200
OPENALEX_LINK_STATUSES = (
    "linked_to_openalex",
    "possible_openalex_match",
    "not_found_in_openalex",
    "skipped",
)
SEARCH_STRATEGIES = (
    "search",
    "search.title",
    "search.title_and_abstract",
    "title.search",
    "title_and_abstract.search",
)
AUTO_SIMILARITY = 0.96
POSSIBLE_SIMILARITY = 0.85
POSSIBLE_TOKEN_OVERLAP = 0.65
SOURCE_IDENTIFIER_FIELDS = ("doi", "openalex_url", "paper_url")
OPENALEX_LINK_FIELDS = (
    "openalex_link_status",
    "openalex_link_reason",
    "search_strategy_used",
    "candidate_source_query",
    "title_similarity",
    "candidate_title",
    "candidate_year",
    "candidate_openalex_url",
    "candidate_doi",
    "candidate_paper_url",
    "enriched_openalex_url",
    "enriched_doi",
    "enriched_paper_url",
)
LEGACY_RESULT_FIELDS = ("enrichment_status", "enrichment_reason")


class EnrichmentError(RuntimeError):
    """An expected error that should be shown without a traceback."""


class OpenAlexRequestError(EnrichmentError):
    """An OpenAlex HTTP response with diagnostics for strategy-level handling."""

    def __init__(self, status_code: int, request_url: str, response_body: str) -> None:
        self.status_code = status_code
        self.request_url = request_url
        self.response_body = response_body
        super().__init__(
            "OpenAlex request failed.\n"
            f"  status code: {status_code}\n"
            f"  request URL: {request_url}\n"
            f"  response body: {response_body}"
        )


@dataclass(frozen=True)
class OpenAlexCandidate:
    title: str
    normalized_title: str
    year: Optional[int]
    doi: str
    openalex_url: str
    paper_url: str
    cited_by_count: int = 0
    result_index: int = 0
    search_strategy: str = ""
    source_query: str = ""
    similarity: float = 0.0
    token_overlap: float = 0.0


@dataclass(frozen=True)
class EnrichmentResult:
    row_number: int
    input_title: str
    input_year: str
    status: str
    reason: str
    candidate: Optional[OpenAlexCandidate]


@dataclass
class RetryAccounting:
    rows_read: int = 0
    rows_selected: int = 0
    title_mismatch_skips: int = 0
    status_mismatch_skips: int = 0
    preserved_linked: int = 0
    rows_searched: int = 0
    requests_made: int = 0


def nonnegative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def per_page_int(value: str) -> int:
    parsed = positive_int(value)
    if parsed > MAX_PER_PAGE:
        raise argparse.ArgumentTypeError(f"must not exceed {MAX_PER_PAGE}")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search OpenAlex by title and write a separate enriched key-paper "
            "coverage checklist."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="Identifying User-Agent sent to OpenAlex.",
    )
    parser.add_argument(
        "--api-key",
        help=(
            "OpenAlex API key. Overrides OPENALEX_API_KEY when both are set. "
            "The key is never written to output files or debug logs."
        ),
    )
    parser.add_argument(
        "--sleep-seconds",
        type=nonnegative_float,
        default=DEFAULT_SLEEP_SECONDS,
        help=f"Minimum delay between requests (default: {DEFAULT_SLEEP_SECONDS}).",
    )
    parser.add_argument(
        "--limit",
        type=positive_int,
        help="Maximum number of checklist rows to query; remaining rows are skipped.",
    )
    parser.add_argument(
        "--per-page",
        type=per_page_int,
        default=DEFAULT_PER_PAGE,
        help=f"OpenAlex results requested per strategy (default: {DEFAULT_PER_PAGE}).",
    )
    parser.add_argument(
        "--only-missing",
        dest="only_missing",
        action="store_true",
        default=True,
        help="Search only rows missing DOI or OpenAlex URL (default).",
    )
    parser.add_argument(
        "--refresh-existing",
        dest="only_missing",
        action="store_false",
        help="Also search rows that already contain both DOI and OpenAlex URL.",
    )
    parser.add_argument(
        "--only-status",
        choices=OPENALEX_LINK_STATUSES,
        help="Retry only rows with this existing openalex_link_status.",
    )
    parser.add_argument(
        "--title-contains",
        help="Process only rows whose title contains this text, case-insensitively.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-query selected rows even when they are already linked or identified.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print each strategy URL, HTTP result, and top five scored candidates.",
    )
    return parser.parse_args(argv)


def project_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value)).casefold()
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).replace("_", " ")
    return " ".join(text.split())


def sanitize_search_query(title: str) -> str:
    """Return title words without OpenAlex wildcard/search punctuation."""
    query = unicodedata.normalize("NFKC", title)
    query = re.sub(r"[?*]", " ", query)
    # Preserve word characters, apostrophes, and hyphens; other punctuation is
    # only syntax/noise for this title lookup and becomes a word separator.
    query = re.sub(r"[^\w\s'’-]", " ", query, flags=re.UNICODE)
    query = query.replace("_", " ")
    return " ".join(query.split())


def title_similarity(first: str, second: str) -> Tuple[float, float]:
    if not first or not second:
        return 0.0, 0.0
    similarity = difflib.SequenceMatcher(None, first, second).ratio()
    first_tokens = set(first.split())
    second_tokens = set(second.split())
    union = first_tokens | second_tokens
    overlap = len(first_tokens & second_tokens) / len(union) if union else 0.0
    return similarity, overlap


def parse_year(value: Any) -> Optional[int]:
    text = clean_text(value)
    if re.fullmatch(r"(?:19|20)\d{2}", text):
        return int(text)
    return None


def year_is_consistent(key_year: Optional[int], candidate_year: Optional[int]) -> bool:
    if key_year is None:
        return True
    return candidate_year is not None and abs(key_year - candidate_year) <= 1


def normalize_doi(value: Any) -> str:
    text = clean_text(value)
    text = re.sub(r"^doi:\s*", "", text, flags=re.IGNORECASE)
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/", "", text, flags=re.IGNORECASE
    ).rstrip(" /.")


def first_text(mapping: Dict[str, Any], *fields: str) -> str:
    for field in fields:
        value = clean_text(mapping.get(field))
        if value:
            return value
    return ""


def location_url(candidate: Dict[str, Any]) -> str:
    for field in ("primary_location", "best_oa_location"):
        location = candidate.get(field)
        if isinstance(location, dict):
            url = first_text(location, "landing_page_url", "pdf_url")
            if url:
                return url
    open_access = candidate.get("open_access")
    if isinstance(open_access, dict):
        return first_text(open_access, "oa_url")
    return ""


def parse_candidate(
    value: Any,
    result_index: int = 0,
    search_strategy: str = "",
    source_query: str = "",
) -> Optional[OpenAlexCandidate]:
    if not isinstance(value, dict):
        return None
    title = first_text(value, "display_name", "title")
    normalized = normalize_title(title)
    openalex_url = clean_text(value.get("id"))
    if not title or not normalized or not openalex_url:
        return None
    return OpenAlexCandidate(
        title=title,
        normalized_title=normalized,
        year=parse_year(value.get("publication_year")),
        doi=normalize_doi(value.get("doi")),
        openalex_url=openalex_url,
        paper_url=location_url(value),
        cited_by_count=(
            value.get("cited_by_count")
            if isinstance(value.get("cited_by_count"), int)
            and value.get("cited_by_count") >= 0
            else 0
        ),
        result_index=result_index,
        search_strategy=search_strategy,
        source_query=source_query,
    )


def strategy_parameter(search_strategy: str, sanitized_query: str) -> Tuple[str, str]:
    if search_strategy in {
        "search",
        "search.title",
        "search.title_and_abstract",
    }:
        return search_strategy, sanitized_query
    if search_strategy in {"title.search", "title_and_abstract.search"}:
        return "filter", f"{search_strategy}:{sanitized_query}"
    raise ValueError(f"Unsupported OpenAlex search strategy: {search_strategy}")


def query_url(
    search_query: str,
    api_key: str,
    search_strategy: str = "search",
    per_page: int = DEFAULT_PER_PAGE,
) -> str:
    parameter, value = strategy_parameter(search_strategy, search_query)
    params = [
        (parameter, value),
        ("sort", "relevance_score:desc"),
        ("per-page", str(per_page)),
    ]
    if api_key:
        params.append(("api_key", api_key))
    return f"{OPENALEX_WORKS_URL}?{urlencode(params)}"


def redact_request_url(url: str) -> str:
    parts = urlsplit(url)
    query = urlencode(
        [
            (key, "REDACTED" if key == "api_key" else value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def redact_secret_text(text: str, api_key: str) -> str:
    """Remove API keys from diagnostics before they can reach logs or reports."""
    redacted = re.sub(
        r"([?&]api_key=)[^&\s]+",
        r"\1REDACTED",
        text,
        flags=re.IGNORECASE,
    )
    if api_key:
        redacted = redacted.replace(api_key, "REDACTED")
    return redacted


def http_error_body(error: HTTPError) -> str:
    try:
        body = error.read()
    except OSError:
        return "(unavailable)"
    if not body:
        return "(empty)"
    return body.decode("utf-8", errors="replace")


def request_candidates(
    title: str,
    user_agent: str,
    api_key: str,
    debug: bool = False,
    search_strategy: str = "search",
    per_page: int = DEFAULT_PER_PAGE,
    result_offset: int = 0,
) -> Tuple[List[OpenAlexCandidate], int, int]:
    search_query = sanitize_search_query(title)
    if not search_query:
        return [], 0, 0
    _, source_query = strategy_parameter(search_strategy, search_query)
    url = query_url(search_query, api_key, search_strategy, per_page)
    safe_url = redact_request_url(url)
    if debug:
        print(f"DEBUG original title: {title}")
        print(f"DEBUG sanitized search query: {search_query}")
        print(f"DEBUG search strategy: {search_strategy}")
        print(f"DEBUG request URL: {safe_url}")
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": user_agent},
    )
    try:
        with urlopen(request, timeout=30) as response:
            http_status = getattr(response, "status", None)
            if http_status is None and hasattr(response, "getcode"):
                http_status = response.getcode()
            payload = json.load(response)
    except HTTPError as error:
        body = redact_secret_text(http_error_body(error), api_key)
        if error.code in (401, 403):
            body = f"{body}\n  hint: Check OPENALEX_API_KEY if it is set."
        elif error.code == 429:
            body = f"{body}\n  hint: Retry later with a longer --sleep-seconds delay."
        raise OpenAlexRequestError(error.code, safe_url, body) from error
    except URLError as error:
        raise EnrichmentError(f"Could not reach OpenAlex: {error.reason}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise EnrichmentError("OpenAlex returned invalid JSON.") from error

    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list):
        raise EnrichmentError("OpenAlex response is missing the expected results list.")
    parsed = [
        parse_candidate(
            candidate,
            result_offset + result_index,
            search_strategy,
            source_query,
        )
        for result_index, candidate in enumerate(results)
    ]
    return (
        [candidate for candidate in parsed if candidate is not None],
        int(http_status or 200),
        len(results),
    )


def score_candidates(
    key_title: str,
    key_year: Optional[int],
    candidates: Sequence[OpenAlexCandidate],
) -> List[OpenAlexCandidate]:
    normalized_key = normalize_title(key_title)
    scored = []
    for candidate in candidates:
        similarity, overlap = title_similarity(normalized_key, candidate.normalized_title)
        scored.append(
            OpenAlexCandidate(
                title=candidate.title,
                normalized_title=candidate.normalized_title,
                year=candidate.year,
                doi=candidate.doi,
                openalex_url=candidate.openalex_url,
                paper_url=candidate.paper_url,
                cited_by_count=candidate.cited_by_count,
                result_index=candidate.result_index,
                search_strategy=candidate.search_strategy,
                source_query=candidate.source_query,
                similarity=similarity,
                token_overlap=overlap,
            )
        )
    return sorted(
        scored,
        key=lambda item: (
            -item.similarity,
            (
                abs(key_year - item.year)
                if key_year is not None and item.year is not None
                else (0 if key_year is None else 10**9)
            ),
            -int(bool(item.doi)),
            -int(bool(item.paper_url)),
            -item.cited_by_count,
            item.result_index,
        ),
    )


def classify_openalex_link(
    key_title: str,
    key_year: Optional[int],
    candidates: Sequence[OpenAlexCandidate],
) -> Tuple[str, str, Optional[OpenAlexCandidate]]:
    scored = score_candidates(key_title, key_year, candidates)
    if not scored:
        return (
            "not_found_in_openalex",
            "OpenAlex returned no usable title candidates.",
            None,
        )

    strong = [
        candidate
        for candidate in scored
        if candidate.similarity >= AUTO_SIMILARITY
        and year_is_consistent(key_year, candidate.year)
    ]

    if strong:
        candidate = strong[0]
        match_kind = (
            "exact normalized title"
            if candidate.similarity == 1.0
            else "strong normalized-title similarity"
        )
        year_note = (
            "year not supplied in checklist"
            if key_year is None
            else f"year difference {abs(key_year - int(candidate.year))}"
        )
        ambiguity_note = ""
        if len(strong) > 1:
            ambiguity_note = (
                f" {len(strong)} strong candidates were found; selected the best "
                "by title similarity, year distance, DOI, paper URL, citation "
                "count, then OpenAlex result order."
            )
        return (
            "linked_to_openalex",
            f"{match_kind}; similarity {candidate.similarity:.3f}; {year_note}."
            f"{ambiguity_note}",
            candidate,
        )

    best = scored[0]
    plausible = (
        best.similarity >= POSSIBLE_SIMILARITY
        and best.token_overlap >= POSSIBLE_TOKEN_OVERLAP
    )
    if plausible:
        year_detail = "year unavailable"
        if key_year is not None and best.year is not None:
            year_detail = f"year difference {abs(key_year - best.year)}"
        return (
            "possible_openalex_match",
            f"Best candidate is plausible but below automatic acceptance rules; similarity {best.similarity:.3f}; {year_detail}.",
            best,
        )
    return (
        "not_found_in_openalex",
        f"No plausible title match; best similarity was {best.similarity:.3f}.",
        best,
    )


def deduplicate_candidates(
    candidates: Sequence[OpenAlexCandidate],
) -> List[OpenAlexCandidate]:
    """Keep the first occurrence of each OpenAlex work across strategies."""
    unique: List[OpenAlexCandidate] = []
    seen = set()
    for candidate in candidates:
        identity = candidate.openalex_url.casefold().rstrip("/")
        if identity in seen:
            continue
        seen.add(identity)
        unique.append(candidate)
    return unique


def debug_strategy_outcome(
    key_title: str,
    key_year: Optional[int],
    candidates: Sequence[OpenAlexCandidate],
    http_status: int,
    link_status: str,
    result_count: int,
) -> None:
    scored = score_candidates(key_title, key_year, candidates)
    print(f"DEBUG HTTP status: {http_status}")
    print(f"DEBUG results returned: {result_count}")
    print("DEBUG top candidates:")
    if not scored:
        print("  (none)")
    for index, candidate in enumerate(scored[:5], start=1):
        year = candidate.year if candidate.year is not None else "unknown"
        print(
            f"  {index}. {candidate.title} ({year}) "
            f"similarity={candidate.similarity:.3f}"
        )
    print(f"DEBUG link status: {link_status}")


def debug_strategy_failure(error: OpenAlexRequestError) -> None:
    print(f"DEBUG HTTP status: {error.status_code}")
    print("DEBUG results returned: 0")
    print("DEBUG top candidates:")
    print("  (none; strategy_failed)")
    print("DEBUG link status: strategy_failed")


def search_openalex_with_fallbacks(
    title: str,
    key_year: Optional[int],
    user_agent: str,
    api_key: str,
    per_page: int,
    sleep_seconds: float,
    previous_request_at: Optional[float],
    debug: bool,
) -> Tuple[
    str,
    str,
    Optional[OpenAlexCandidate],
    Optional[float],
    int,
]:
    if not sanitize_search_query(title):
        status, reason, candidate = classify_openalex_link(title, key_year, [])
        return status, reason, candidate, previous_request_at, 0

    all_candidates: List[OpenAlexCandidate] = []
    request_count = 0
    status = "not_found_in_openalex"
    reason = "OpenAlex returned no usable title candidates."
    best: Optional[OpenAlexCandidate] = None
    strategy_failures: List[str] = []

    for strategy_index, search_strategy in enumerate(SEARCH_STRATEGIES):
        if previous_request_at is not None:
            elapsed = time.monotonic() - previous_request_at
            if elapsed < sleep_seconds:
                time.sleep(sleep_seconds - elapsed)

        try:
            candidates, http_status, result_count = request_candidates(
                title,
                user_agent,
                api_key,
                debug=debug,
                search_strategy=search_strategy,
                per_page=per_page,
                result_offset=strategy_index * per_page,
            )
        except OpenAlexRequestError as error:
            previous_request_at = time.monotonic()
            request_count += 1
            if error.status_code != 400:
                raise
            strategy_failures.append(
                f"{search_strategy} strategy_failed with HTTP 400: "
                f"{error.response_body}"
            )
            if debug:
                debug_strategy_failure(error)
            continue

        previous_request_at = time.monotonic()
        request_count += 1
        all_candidates = deduplicate_candidates([*all_candidates, *candidates])
        status, reason, best = classify_openalex_link(
            title, key_year, all_candidates
        )
        if debug:
            debug_strategy_outcome(
                title,
                key_year,
                candidates,
                http_status,
                status,
                result_count,
            )
        if status == "linked_to_openalex":
            break

    if strategy_failures:
        reason = f"{reason} Strategy failures: {'; '.join(strategy_failures)}"
    return status, reason, best, previous_request_at, request_count


def read_input(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            if "title" not in fieldnames:
                raise EnrichmentError(f"{path} is missing required column: title")
            rows = [dict(row) for row in reader]
    except OSError as error:
        raise EnrichmentError(f"Could not read {path}: {error}") from error

    for field in SOURCE_IDENTIFIER_FIELDS:
        if field not in fieldnames:
            fieldnames.append(field)

    base_fields = [
        field
        for field in fieldnames
        if field not in OPENALEX_LINK_FIELDS and field not in LEGACY_RESULT_FIELDS
    ]
    insertion_index = (
        base_fields.index("notes") + 1 if "notes" in base_fields else len(base_fields)
    )
    output_fields = (
        base_fields[:insertion_index]
        + list(OPENALEX_LINK_FIELDS)
        + base_fields[insertion_index:]
    )
    return output_fields, rows


def write_csv(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def markdown_text(value: Any) -> str:
    return clean_text(value).replace("|", "\\|") or "-"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def report_table(results: Sequence[EnrichmentResult]) -> List[str]:
    if not results:
        return ["None.", ""]
    lines = [
        "| Row | Checklist title | Year | OpenAlex link status | Search strategy used | Candidate title | Candidate year | Similarity | Candidate DOI | OpenAlex | Reason |",
        "| ---: | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for result in results:
        candidate = result.candidate
        openalex_link = (
            f"[record]({candidate.openalex_url})" if candidate else "-"
        )
        lines.append(
            "| {row} | {title} | {year} | `{status}` | `{strategy}` | {candidate_title} | {candidate_year} | {similarity} | {doi} | {openalex} | {reason} |".format(
                row=result.row_number,
                title=markdown_text(result.input_title),
                year=markdown_text(result.input_year),
                status=result.status,
                strategy=(candidate.search_strategy if candidate else "-"),
                candidate_title=markdown_text(candidate.title if candidate else ""),
                candidate_year=candidate.year if candidate and candidate.year else "-",
                similarity=f"{candidate.similarity:.3f}" if candidate else "-",
                doi=markdown_text(candidate.doi if candidate else ""),
                openalex=openalex_link,
                reason=markdown_text(result.reason),
            )
        )
    lines.append("")
    return lines


def write_report(
    path: Path,
    input_path: Path,
    output_path: Path,
    results: Sequence[EnrichmentResult],
    accounting: RetryAccounting,
) -> None:
    counts = Counter(result.status for result in results)
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# Key Paper OpenAlex Enrichment Report",
        "",
        f"Generated: `{generated}`  ",
        f"Input: `{display_path(input_path)}`  ",
        f"Enriched output: `{display_path(output_path)}`",
        "",
        "This report links manually curated checklist papers to possible OpenAlex metadata for coverage auditing. OpenAlex link status does not determine whether a checklist paper is valid, and linked papers are not automatically published to the map.",
        "",
        "## Summary",
        "",
        f"- Rows read: {accounting.rows_read}",
        f"- Rows selected for processing: {accounting.rows_selected}",
        f"- Rows skipped because title did not match `--title-contains`: {accounting.title_mismatch_skips}",
        f"- Rows skipped because status did not match `--only-status`: {accounting.status_mismatch_skips}",
        f"- Rows preserved because already `linked_to_openalex`: {accounting.preserved_linked}",
        f"- Rows actually searched: {accounting.rows_searched}",
        f"- OpenAlex requests made: {accounting.requests_made}",
        f"- Linked to OpenAlex: {counts['linked_to_openalex']}",
        f"- Possible OpenAlex matches requiring review: {counts['possible_openalex_match']}",
        f"- Not found in OpenAlex: {counts['not_found_in_openalex']}",
        f"- Skipped: {counts['skipped']}",
        "",
    ]
    for status, heading in (
        ("linked_to_openalex", "Linked to OpenAlex"),
        ("possible_openalex_match", "Possible OpenAlex Matches"),
        ("not_found_in_openalex", "Not Found in OpenAlex"),
        ("skipped", "Skipped"),
    ):
        lines.extend([f"## {heading}", ""])
        lines.extend(report_table([result for result in results if result.status == status]))

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write("\n".join(lines).rstrip() + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def candidate_from_existing_row(row: Dict[str, str]) -> Optional[OpenAlexCandidate]:
    candidate_title = clean_text(row.get("candidate_title"))
    openalex_url = first_text(
        row,
        "candidate_openalex_url",
        "enriched_openalex_url",
        "openalex_url",
    )
    if not candidate_title and not openalex_url:
        return None
    if not candidate_title:
        candidate_title = clean_text(row.get("title"))
    try:
        similarity = float(clean_text(row.get("title_similarity")))
    except ValueError:
        similarity = title_similarity(
            normalize_title(row.get("title")),
            normalize_title(candidate_title),
        )[0]
    return OpenAlexCandidate(
        title=candidate_title,
        normalized_title=normalize_title(candidate_title),
        year=parse_year(first_text(row, "candidate_year", "year")),
        doi=first_text(row, "candidate_doi", "enriched_doi", "doi"),
        openalex_url=openalex_url,
        paper_url=first_text(
            row,
            "candidate_paper_url",
            "enriched_paper_url",
            "paper_url",
        ),
        search_strategy=clean_text(row.get("search_strategy_used")),
        source_query=clean_text(row.get("candidate_source_query")),
        similarity=similarity,
    )


def enrich_rows(
    rows: Sequence[Dict[str, str]],
    user_agent: str,
    sleep_seconds: float,
    limit: Optional[int],
    only_missing: bool,
    api_key: str,
    debug: bool,
    per_page: int,
    only_status: Optional[str],
    title_contains: Optional[str],
    force: bool,
) -> Tuple[List[Dict[str, str]], List[EnrichmentResult], RetryAccounting]:
    output_rows: List[Dict[str, str]] = []
    results: List[EnrichmentResult] = []
    accounting = RetryAccounting(rows_read=len(rows))
    previous_request_at: Optional[float] = None
    title_filter = clean_text(title_contains).casefold()

    for row_number, original in enumerate(rows, start=2):
        row = dict(original)
        for field in LEGACY_RESULT_FIELDS:
            row.pop(field, None)
        for field in OPENALEX_LINK_FIELDS:
            row.setdefault(field, "")
        title = row.get("title", "")
        year_text = row.get("year", "")
        existing_status = clean_text(row.get("openalex_link_status"))
        existing_reason = clean_text(row.get("openalex_link_reason"))
        candidate = candidate_from_existing_row(row)
        recomputed = False

        if title_filter and title_filter not in clean_text(title).casefold():
            accounting.title_mismatch_skips += 1
            status = existing_status or "skipped"
            reason = existing_reason or (
                f"Title did not contain --title-contains value {title_contains!r}."
            )
        elif only_status is not None and existing_status != only_status:
            accounting.status_mismatch_skips += 1
            status = existing_status or "skipped"
            reason = existing_reason or f"Not selected by --only-status {only_status}."
        else:
            accounting.rows_selected += 1
            if existing_status == "linked_to_openalex" and not force:
                accounting.preserved_linked += 1
                status = existing_status
                reason = existing_reason or "Existing OpenAlex link preserved."
            elif (
                not force
                and only_missing
                and row.get("doi", "").strip()
                and row.get("openalex_url", "").strip()
            ):
                status = existing_status or "skipped"
                reason = existing_reason or "DOI and OpenAlex URL are already present."
            elif not clean_text(title):
                status = existing_status or "skipped"
                reason = existing_reason or "Title is empty."
            elif limit is not None and accounting.rows_searched >= limit:
                status = existing_status or "skipped"
                reason = existing_reason or f"Search limit of {limit} reached."
            else:
                for field in OPENALEX_LINK_FIELDS:
                    row[field] = ""
                candidate = None
                (
                    status,
                    reason,
                    candidate,
                    previous_request_at,
                    requests_made,
                ) = search_openalex_with_fallbacks(
                    title=clean_text(title),
                    key_year=parse_year(year_text),
                    user_agent=user_agent,
                    api_key=api_key,
                    per_page=per_page,
                    sleep_seconds=sleep_seconds,
                    previous_request_at=previous_request_at,
                    debug=debug,
                )
                if requests_made:
                    accounting.rows_searched += 1
                accounting.requests_made += requests_made
                recomputed = True
        if recomputed and candidate is not None:
            row["search_strategy_used"] = candidate.search_strategy
            row["candidate_source_query"] = candidate.source_query
            row["title_similarity"] = f"{candidate.similarity:.3f}"
            row["candidate_title"] = candidate.title
            row["candidate_year"] = str(candidate.year or "")
            row["candidate_openalex_url"] = candidate.openalex_url
            row["candidate_doi"] = candidate.doi
            row["candidate_paper_url"] = candidate.paper_url
        if recomputed and candidate is not None and status == "linked_to_openalex":
            row["enriched_openalex_url"] = candidate.openalex_url
            row["enriched_doi"] = candidate.doi
            row["enriched_paper_url"] = candidate.paper_url

        if recomputed or not existing_status:
            row["openalex_link_status"] = status
            row["openalex_link_reason"] = reason
        output_rows.append(row)
        results.append(
            EnrichmentResult(
                row_number=row_number,
                input_title=title,
                input_year=year_text,
                status=status,
                reason=reason,
                candidate=candidate,
            )
        )
    return output_rows, results, accounting


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    input_path = project_path(args.input).resolve()
    output_path = project_path(args.output).resolve()
    report_path = project_path(args.report).resolve()

    if output_path == DEFAULT_INPUT.resolve():
        print("Error: refusing to overwrite data/manual/key_papers.csv.")
        return 2
    if not clean_text(args.user_agent):
        print("Error: --user-agent must be non-empty.")
        return 2
    api_key = clean_text(args.api_key) or os.environ.get("OPENALEX_API_KEY", "").strip()

    try:
        fieldnames, rows = read_input(input_path)
        if args.only_status and not any(
            "openalex_link_status" in row for row in rows
        ):
            raise EnrichmentError(
                "--only-status requires an enriched input containing "
                "openalex_link_status."
            )
        enriched_rows, results, accounting = enrich_rows(
            rows=rows,
            user_agent=args.user_agent.strip(),
            sleep_seconds=args.sleep_seconds,
            limit=args.limit,
            only_missing=args.only_missing,
            api_key=api_key,
            debug=args.debug,
            per_page=args.per_page,
            only_status=args.only_status,
            title_contains=args.title_contains,
            force=args.force,
        )
        write_csv(output_path, fieldnames, enriched_rows)
        write_report(report_path, input_path, output_path, results, accounting)
    except EnrichmentError as error:
        print(f"Error: {error}")
        return 1
    except OSError as error:
        print(f"Error writing enrichment output: {error}")
        return 1

    counts = Counter(result.status for result in results)
    print("Key paper OpenAlex enrichment complete")
    print(f"  Rows read: {accounting.rows_read}")
    print(f"  Rows selected for processing: {accounting.rows_selected}")
    print(
        "  Rows skipped because title did not match --title-contains: "
        f"{accounting.title_mismatch_skips}"
    )
    print(
        "  Rows skipped because status did not match --only-status: "
        f"{accounting.status_mismatch_skips}"
    )
    print(
        "  Rows preserved because already linked_to_openalex: "
        f"{accounting.preserved_linked}"
    )
    print(f"  Rows actually searched: {accounting.rows_searched}")
    print(f"  OpenAlex requests made: {accounting.requests_made}")
    print("  OpenAlex link status:")
    for status in (
        "linked_to_openalex",
        "possible_openalex_match",
        "not_found_in_openalex",
        "skipped",
    ):
        print(f"    {status}: {counts[status]}")
    print(f"  Output: {output_path}")
    print(f"  Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
