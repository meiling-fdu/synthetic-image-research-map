#!/usr/bin/env python3
"""Fill missing curated arXiv IDs using unique normalized title matches."""

from __future__ import annotations

import html
import csv
import json
import logging
import re
import socket
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Sequence

try:
    from .curated_papers import (
        DEFAULT_CURATED_PAPERS_PATH,
        read_curated_papers,
        write_curated_papers,
    )
    from .curated_schema import CURATED_ARXIV_LINK_COLUMNS
except ImportError:
    from curated_papers import (
        DEFAULT_CURATED_PAPERS_PATH,
        read_curated_papers,
        write_curated_papers,
    )
    from curated_schema import CURATED_ARXIV_LINK_COLUMNS

try:
    from .export_public_preview import build_preview, identity_key
    from .export_candidate_map_data import (
        apply_paper_arxiv_links,
        paper_identity_keys,
    )
    from .paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        read_exclusion_rows,
    )
except ImportError:
    from export_public_preview import build_preview, identity_key
    from export_candidate_map_data import (
        apply_paper_arxiv_links,
        paper_identity_keys,
    )
    from paper_exclusions import DEFAULT_EXCLUSIONS_PATH, read_exclusion_rows


ARXIV_API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "SyntheticImageResearchMap-ArxivAutofill/1.0 (academic metadata curation)"
ARXIV_ID_RE = re.compile(
    r"(?:abs/)?([a-z-]+(?:\.[a-z]{2})?/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?$",
    re.IGNORECASE,
)
RETRY_DELAYS_SECONDS = (3.0, 8.0)
NORMAL_REQUEST_DELAY_SECONDS = 3.0
CONNECT_TIMEOUT_SECONDS = 10.0
READ_TIMEOUT_SECONDS = 20.0
TRANSIENT_HTTP_STATUSES = {429, 500, 502, 503, 504}
LOGGER = logging.getLogger(__name__)
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PUBLIC_MAP_PATH = REPOSITORY_ROOT / "web/data/public_preview_map_data.json"
DEFAULT_CURATED_ARXIV_LINKS_PATH = (
    REPOSITORY_ROOT / "data/curated/paper_arxiv_links.csv"
)


class ArxivLookupError(RuntimeError):
    """An arXiv request or response could not be processed."""

    def __init__(
        self,
        reason: str,
        *,
        kind: str,
        http_status: int | None = None,
        attempts: int = 1,
    ):
        super().__init__(reason)
        self.reason = reason
        self.kind = kind
        self.http_status = http_status
        self.attempts = attempts

    def as_dict(self, title: str) -> Dict[str, Any]:
        return {
            "title": title,
            "reason": self.reason,
            "failure_type": self.kind,
            "http_status": self.http_status,
            "attempts": self.attempts,
        }


def normalize_exact_title(value: Any) -> str:
    """Normalize presentation differences while retaining every title word."""
    text = html.unescape(str(value or ""))
    text = unicodedata.normalize("NFKC", text).casefold()
    text = text.translate(str.maketrans({
        "‘": "'", "’": "'", "‚": "'", "‛": "'",
        "“": '"', "”": '"', "„": '"', "‟": '"',
        "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "―": "-",
    }))
    # Punctuation is ignored, but Unicode letters and numbers are retained.
    text = "".join(
        character
        if character.isspace() or character.isalnum()
        else "" if unicodedata.category(character).startswith(("P", "S"))
        else " "
        for character in text
    )
    return " ".join(text.split())


def base_arxiv_id(value: Any) -> str:
    text = html.unescape(str(value or "")).strip().rstrip("/")
    match = ARXIV_ID_RE.search(text)
    return match.group(1) if match else ""


def _retry_after_seconds(value: Any, *, now: Callable[[], datetime]) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return max(0.0, float(text))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(text)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0.0, (retry_at - now()).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


def _request_failure(error: BaseException, attempts: int) -> tuple[ArxivLookupError, bool, float | None]:
    if isinstance(error, urllib.error.HTTPError):
        status = int(error.code)
        retry_after = _retry_after_seconds(
            error.headers.get("Retry-After") if error.headers else None,
            now=lambda: datetime.now(timezone.utc),
        )
        failure = ArxivLookupError(
            f"HTTP {status}: {error.reason}",
            kind="http_error",
            http_status=status,
            attempts=attempts,
        )
        return failure, status in TRANSIENT_HTTP_STATUSES, retry_after
    underlying = error.reason if isinstance(error, urllib.error.URLError) else error
    if isinstance(underlying, (TimeoutError, socket.timeout)):
        return (
            ArxivLookupError(
                f"timeout: {underlying}", kind="timeout", attempts=attempts
            ),
            True,
            None,
        )
    return (
        ArxivLookupError(
            f"network error: {underlying}",
            kind="network_error",
            attempts=attempts,
        ),
        True,
        None,
    )


def lookup_arxiv_by_title(
    title: str,
    *,
    timeout: float = CONNECT_TIMEOUT_SECONDS,
    read_timeout: float = READ_TIMEOUT_SECONDS,
    urlopen: Callable[..., Any] = urllib.request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
) -> List[Dict[str, str]]:
    query = urllib.parse.urlencode({
        "search_query": f'ti:"{title}"',
        "start": 0,
        "max_results": 50,
    })
    request = urllib.request.Request(
        f"{ARXIV_API_URL}?{query}", headers={"User-Agent": USER_AGENT}
    )
    payload = b""
    for attempt in range(1, len(RETRY_DELAYS_SECONDS) + 2):
        try:
            with urlopen(request, timeout=timeout) as response:
                # urllib's timeout covers connection establishment. Explicitly
                # apply a separate socket read timeout when the response exposes
                # its underlying socket (real HTTP responses do; test doubles may not).
                socket_object = getattr(
                    getattr(getattr(response, "fp", None), "raw", None),
                    "_sock",
                    None,
                )
                if socket_object is not None:
                    socket_object.settimeout(read_timeout)
                payload = response.read()
            break
        except (OSError, urllib.error.HTTPError, urllib.error.URLError) as error:
            failure, transient, retry_after = _request_failure(error, attempt)
            LOGGER.warning(
                "arXiv request attempt %d/3 for %r failed: %s",
                attempt,
                title,
                failure.reason,
            )
            if not transient or attempt > len(RETRY_DELAYS_SECONDS):
                raise failure from error
            delay = (
                retry_after
                if retry_after is not None
                else RETRY_DELAYS_SECONDS[attempt - 1]
            )
            sleep(delay)
    try:
        root = ET.fromstring(payload)
    except (ET.ParseError, UnicodeError) as error:
        raise ArxivLookupError(
            f"XML parsing error: {error}", kind="xml_parsing_error"
        ) from error
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    results = []
    for entry in root.findall("atom:entry", namespace):
        arxiv_id = base_arxiv_id(entry.findtext("atom:id", "", namespace))
        candidate_title = entry.findtext("atom:title", "", namespace)
        if arxiv_id and candidate_title:
            results.append({"arxiv_id": arxiv_id, "title": candidate_title})
    return results


def autofill_missing_arxiv_ids(
    *,
    path: Path = DEFAULT_CURATED_PAPERS_PATH,
    lookup: Callable[[str], Sequence[Mapping[str, Any]]] = lookup_arxiv_by_title,
    export: Callable[[], Mapping[str, Any]] | None = None,
    request_delay_seconds: float | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Dict[str, Any]:
    rows = read_curated_papers(path)
    stats: Dict[str, Any] = {
        "total_records": len(rows),
        "already_containing_arxiv_ids": 0,
        "exact_matches_added": 0,
        "no_match_count": 0,
        "ambiguous_match_count": 0,
        "failed_lookup_count": 0,
        "failed_lookups": [],
        "updated_papers": [],
        "export_ran": False,
    }
    production_lookup = lookup is lookup_arxiv_by_title
    delay = (
        NORMAL_REQUEST_DELAY_SECONDS
        if request_delay_seconds is None and production_lookup
        else float(request_delay_seconds or 0)
    )
    lookup_count = 0
    for row in rows:
        if str(row.get("arxiv_id") or "").strip():
            stats["already_containing_arxiv_ids"] += 1
            continue
        title = str(row.get("title") or "").strip()
        normalized = normalize_exact_title(title)
        try:
            if lookup_count and delay:
                sleep(delay)
            lookup_count += 1
            candidates = lookup(title)
        except Exception as error:  # One failed paper must not stop the batch.
            stats["failed_lookup_count"] += 1
            if isinstance(error, ArxivLookupError):
                failure = error.as_dict(title)
            else:
                failure = {
                    "title": title,
                    "reason": str(error) or error.__class__.__name__,
                    "failure_type": "unexpected_error",
                    "http_status": None,
                    "attempts": 1,
                }
            stats["failed_lookups"].append(failure)
            LOGGER.warning(
                "arXiv lookup failed for %r: %s", title, failure["reason"]
            )
            continue
        matches = [
            candidate for candidate in candidates
            if normalize_exact_title(candidate.get("title")) == normalized
            and base_arxiv_id(candidate.get("arxiv_id"))
        ]
        if not matches:
            stats["no_match_count"] += 1
            continue
        if len(matches) != 1:
            stats["ambiguous_match_count"] += 1
            continue
        arxiv_id = base_arxiv_id(matches[0].get("arxiv_id"))
        row["arxiv_id"] = arxiv_id
        if not str(row.get("paper_url") or "").strip():
            row["paper_url"] = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        stats["exact_matches_added"] += 1
        stats["updated_papers"].append({"title": title, "arxiv_id": arxiv_id})

    if stats["exact_matches_added"]:
        write_curated_papers(rows, path)
        if export is not None:
            export_result = dict(export())
            stats["export_ran"] = True
            stats["export_success"] = bool(export_result.get("success"))
            stats["export_result"] = export_result
    return stats


def _read_public_map_records(path: Path) -> List[Dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ArxivLookupError(
            f"could not read public map dataset: {error}",
            kind="input_error",
        ) from error
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list) or not all(
        isinstance(record, dict) for record in records
    ):
        raise ArxivLookupError(
            "public map dataset does not contain a records list",
            kind="input_error",
        )
    return [dict(record) for record in records]


def eligible_public_map_papers(
    records: Sequence[Mapping[str, Any]],
    exclusion_rows: Sequence[Mapping[str, Any]] = (),
) -> List[Dict[str, Any]]:
    """Apply public-map export eligibility and return one record per map paper."""
    payload, _summary = build_preview(
        [dict(record) for record in records],
        None,
        "medium",
        False,
        (),
        exclusion_rows=[dict(row) for row in exclusion_rows],
    )
    unique: Dict[Any, Dict[str, Any]] = {}
    for record in payload["records"]:
        unique.setdefault(identity_key(record), record)
    return list(unique.values())


def read_curated_arxiv_links(
    path: Path = DEFAULT_CURATED_ARXIV_LINKS_PATH,
) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != CURATED_ARXIV_LINK_COLUMNS:
                raise ArxivLookupError(
                    f"{path} does not have the curated arXiv-link header",
                    kind="input_error",
                )
            return [dict(row) for row in reader]
    except (OSError, UnicodeError, csv.Error) as error:
        raise ArxivLookupError(str(error), kind="input_error") from error


def write_curated_arxiv_links(
    rows: Sequence[Mapping[str, Any]], path: Path
) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=CURATED_ARXIV_LINK_COLUMNS,
                lineterminator="\n",
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        raise ArxivLookupError(str(error), kind="write_error") from error


def apply_curated_arxiv_metadata(
    record: Mapping[str, Any],
    path: Path = DEFAULT_CURATED_ARXIV_LINKS_PATH,
) -> Dict[str, Any]:
    """Return admin metadata with the same arXiv enrichment used by export."""
    effective = dict(record)
    effective_records = [effective]
    apply_paper_arxiv_links(effective_records, read_curated_arxiv_links(path))
    return effective_records[0]


def curated_arxiv_override_for_record(
    record: Mapping[str, Any],
    path: Path = DEFAULT_CURATED_ARXIV_LINKS_PATH,
) -> Dict[str, str] | None:
    target_keys = set(paper_identity_keys(dict(record)))
    return next(
        (
            row for row in read_curated_arxiv_links(path)
            if target_keys & set(paper_identity_keys(row))
        ),
        None,
    )


def set_curated_arxiv_override(
    paper: Mapping[str, Any],
    arxiv_id: Any,
    path: Path = DEFAULT_CURATED_ARXIV_LINKS_PATH,
    *,
    match_record: Mapping[str, Any] | None = None,
) -> List[Dict[str, str]]:
    """Upsert or remove one paper's curated arXiv override atomically."""
    target_key = identity_key(dict(match_record or paper))
    rows = read_curated_arxiv_links(path)
    matching_indexes = [
        index for index, row in enumerate(rows)
        if identity_key(row) == target_key
    ]
    normalized_id = base_arxiv_id(arxiv_id)
    replacement = None
    if normalized_id:
        replacement = {
            "title": str(paper.get("title") or "").strip(),
            "year": str(
                paper.get("year") or paper.get("publication_year") or ""
            ).strip(),
            "doi": str(paper.get("doi") or "").strip(),
            "openalex_url": str(paper.get("openalex_url") or "").strip(),
            "arxiv_id": normalized_id,
            "match_status": "linked_to_arxiv",
            "source": "admin_metadata_edit",
        }
    updated: List[Dict[str, str]] = []
    replacement_written = False
    for index, row in enumerate(rows):
        if index not in matching_indexes:
            updated.append(row)
            continue
        if replacement is not None and not replacement_written:
            updated.append(replacement)
            replacement_written = True
    if replacement is not None and not replacement_written:
        updated.append(replacement)
    if updated != rows:
        write_curated_arxiv_links(updated, path)
    return updated


def autofill_public_map_arxiv_ids(
    *,
    map_path: Path = DEFAULT_PUBLIC_MAP_PATH,
    links_path: Path = DEFAULT_CURATED_ARXIV_LINKS_PATH,
    exclusions_path: Path = DEFAULT_EXCLUSIONS_PATH,
    lookup: Callable[[str], Sequence[Mapping[str, Any]]] = lookup_arxiv_by_title,
    export: Callable[[], Mapping[str, Any]] | None = None,
    request_delay_seconds: float | None = None,
    sleep: Callable[[float], None] = time.sleep,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> Dict[str, Any]:
    exclusion_rows = read_exclusion_rows(exclusions_path)
    papers = eligible_public_map_papers(
        _read_public_map_records(map_path), exclusion_rows
    )
    stats: Dict[str, Any] = {
        "total_records": len(papers),
        "eligible_public_map_papers": len(papers),
        "already_containing_arxiv_ids": 0,
        "papers_requiring_lookup": 0,
        "processed_lookups": 0,
        "exact_matches_added": 0,
        "no_match_count": 0,
        "ambiguous_match_count": 0,
        "failed_lookup_count": 0,
        "failed_lookups": [],
        "updated_papers": [],
        "export_ran": False,
    }
    production_lookup = lookup is lookup_arxiv_by_title
    delay = (
        NORMAL_REQUEST_DELAY_SECONDS
        if request_delay_seconds is None and production_lookup
        else float(request_delay_seconds or 0)
    )
    additions: List[Dict[str, str]] = []
    stats["papers_requiring_lookup"] = sum(
        not str(paper.get("arxiv_id") or "").strip() for paper in papers
    )
    stats["already_containing_arxiv_ids"] = (
        len(papers) - stats["papers_requiring_lookup"]
    )
    looked_up = 0
    for paper in papers:
        if str(paper.get("arxiv_id") or "").strip():
            continue
        title = str(paper.get("title") or "").strip()
        outcome = "failure"
        try:
            if looked_up and delay:
                sleep(delay)
            if progress is not None:
                progress({
                    **stats,
                    "processed_lookups": looked_up,
                    "current_paper_title": title,
                })
            looked_up += 1
            candidates = lookup(title)
        except Exception as error:
            stats["failed_lookup_count"] += 1
            failure = (
                error.as_dict(title)
                if isinstance(error, ArxivLookupError)
                else {
                    "title": title,
                    "reason": str(error) or error.__class__.__name__,
                    "failure_type": "unexpected_error",
                    "http_status": None,
                    "attempts": 1,
                }
            )
            stats["failed_lookups"].append(failure)
            LOGGER.warning("arXiv lookup failed for %r: %s", title, failure["reason"])
        else:
            normalized = normalize_exact_title(title)
            matches = [
                candidate
                for candidate in candidates
                if normalize_exact_title(candidate.get("title")) == normalized
                and base_arxiv_id(candidate.get("arxiv_id"))
            ]
            if not matches:
                stats["no_match_count"] += 1
                outcome = "no match"
            elif len(matches) != 1:
                stats["ambiguous_match_count"] += 1
                outcome = "ambiguous"
            else:
                arxiv_id = base_arxiv_id(matches[0].get("arxiv_id"))
                additions.append({
                    "title": title,
                    "year": str(paper.get("year") or paper.get("publication_year") or ""),
                    "doi": str(paper.get("doi") or ""),
                    "openalex_url": str(paper.get("openalex_url") or ""),
                    "arxiv_id": arxiv_id,
                    "match_status": "linked_to_arxiv",
                    "source": "admin_exact_title_autofill",
                })
                stats["exact_matches_added"] += 1
                stats["updated_papers"].append(
                    {"title": title, "arxiv_id": arxiv_id}
                )
                outcome = "success"
        LOGGER.info(
            "arXiv autofill %d/%d %r: %s",
            looked_up,
            stats["papers_requiring_lookup"],
            title,
            outcome,
        )
        stats["processed_lookups"] = looked_up
        if progress is not None:
            progress({
                **stats,
                "processed_lookups": looked_up,
                "current_paper_title": title,
            })

    if additions:
        existing = read_curated_arxiv_links(links_path)
        existing_keys = {identity_key(row) for row in existing}
        existing.extend(
            row for row in additions if identity_key(row) not in existing_keys
        )
        write_curated_arxiv_links(existing, links_path)
        if export is not None:
            export_result = dict(export())
            stats["export_ran"] = True
            stats["export_success"] = bool(export_result.get("success"))
            stats["export_result"] = export_result
    return stats


def missing_public_map_arxiv_papers(
    *,
    map_path: Path = DEFAULT_PUBLIC_MAP_PATH,
    links_path: Path = DEFAULT_CURATED_ARXIV_LINKS_PATH,
    exclusions_path: Path = DEFAULT_EXCLUSIONS_PATH,
) -> List[Dict[str, Any]]:
    """List eligible papers with no effective arXiv ID, without writing files."""
    papers = eligible_public_map_papers(
        _read_public_map_records(map_path), read_exclusion_rows(exclusions_path)
    )
    linked_keys = {
        identity_key(row) for row in read_curated_arxiv_links(links_path)
    }
    return [
        {
            "paper_id": str(paper.get("id") or ""),
            "title": str(paper.get("title") or "").strip(),
            "year": str(paper.get("year") or paper.get("publication_year") or ""),
            "doi": str(paper.get("doi") or ""),
            "openalex_url": str(paper.get("openalex_url") or ""),
            "candidates": [],
        }
        for paper in papers
        if not str(paper.get("arxiv_id") or "").strip()
        and identity_key(paper) not in linked_keys
    ]


def discover_public_map_arxiv_candidates(
    *,
    map_path: Path = DEFAULT_PUBLIC_MAP_PATH,
    links_path: Path = DEFAULT_CURATED_ARXIV_LINKS_PATH,
    exclusions_path: Path = DEFAULT_EXCLUSIONS_PATH,
    lookup: Callable[[str], Sequence[Mapping[str, Any]]] = lookup_arxiv_by_title,
    export: Callable[[], Mapping[str, Any]] | None = None,
    request_delay_seconds: float | None = None,
    sleep: Callable[[float], None] = time.sleep,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> Dict[str, Any]:
    """Find review candidates without changing curated or generated files."""
    del export  # Compatibility only: discovery intentionally never exports.
    missing = missing_public_map_arxiv_papers(
        map_path=map_path,
        links_path=links_path,
        exclusions_path=exclusions_path,
    )
    stats: Dict[str, Any] = {
        "total_records": len(missing),
        "eligible_public_map_papers": len(missing),
        "papers_requiring_lookup": len(missing),
        "processed_lookups": 0,
        "candidate_papers": [],
        "candidate_count": 0,
        "no_match_count": 0,
        "ambiguous_match_count": 0,
        "failed_lookup_count": 0,
        "failed_lookups": [],
        "writes_performed": False,
    }
    production_lookup = lookup is lookup_arxiv_by_title
    delay = (
        NORMAL_REQUEST_DELAY_SECONDS
        if request_delay_seconds is None and production_lookup
        else float(request_delay_seconds or 0)
    )
    for index, paper in enumerate(missing):
        title = str(paper.get("title") or "").strip()
        if index and delay:
            sleep(delay)
        if progress is not None:
            progress({**stats, "current_paper_title": title})
        try:
            results = lookup(title)
        except Exception as error:
            failure = (
                error.as_dict(title)
                if isinstance(error, ArxivLookupError)
                else {
                    "title": title,
                    "reason": str(error) or error.__class__.__name__,
                    "failure_type": "unexpected_error",
                    "http_status": None,
                    "attempts": 1,
                }
            )
            stats["failed_lookup_count"] += 1
            stats["failed_lookups"].append(failure)
        else:
            normalized = normalize_exact_title(title)
            exact = [
                candidate for candidate in results
                if normalize_exact_title(candidate.get("title")) == normalized
                and base_arxiv_id(candidate.get("arxiv_id"))
            ]
            if not exact:
                stats["no_match_count"] += 1
            else:
                ambiguous = len(exact) > 1
                if ambiguous:
                    stats["ambiguous_match_count"] += 1
                candidates = [{
                    "arxiv_id": base_arxiv_id(candidate.get("arxiv_id")),
                    "arxiv_url": (
                        "https://arxiv.org/abs/"
                        + base_arxiv_id(candidate.get("arxiv_id"))
                    ),
                    "candidate_title": str(candidate.get("title") or "").strip(),
                    "source": "arXiv Atom API title search",
                    "confidence": "medium" if ambiguous else "high",
                    "evidence": (
                        "Exact normalized title match; multiple arXiv records "
                        "require reviewer disambiguation."
                        if ambiguous else
                        "Unique exact normalized title match."
                    ),
                } for candidate in exact]
                stats["candidate_papers"].append({
                    "paper_id": str(
                        paper.get("paper_id") or paper.get("id") or ""
                    ),
                    "title": title,
                    "year": str(
                        paper.get("year") or paper.get("publication_year") or ""
                    ),
                    "doi": str(paper.get("doi") or ""),
                    "openalex_url": str(paper.get("openalex_url") or ""),
                    "candidates": candidates,
                })
                stats["candidate_count"] += len(candidates)
        stats["processed_lookups"] = index + 1
        if progress is not None:
            progress({**stats, "current_paper_title": title})
    return stats
