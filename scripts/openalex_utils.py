#!/usr/bin/env python3
"""Small shared helpers for reproducible OpenAlex imports."""

from __future__ import annotations

import json
import re
import time
import unicodedata
from difflib import SequenceMatcher
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OPENALEX_API = "https://api.openalex.org"
USER_AGENT = "synthetic-image-research-map/0.1 (manual OpenAlex import)"
OPENALEX_ID_RE = re.compile(r"\b([WIASPFC]\d+)\b", re.IGNORECASE)


class OpenAlexFetchError(RuntimeError):
    """A request failure that callers can report without stopping a batch."""


def normalize_openalex_id(value: Any) -> str:
    """Return the canonical short OpenAlex identifier, such as W123."""
    match = OPENALEX_ID_RE.search(str(value or "").strip())
    return match.group(1).upper() if match else ""


def fetch_json_with_retry(
    url: str,
    max_retries: int = 5,
    base_sleep_seconds: float = 20,
) -> Dict[str, Any]:
    """Fetch JSON, retrying rate limits and transient failures."""
    last_error = ""
    for attempt in range(max_retries + 1):
        request = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )
        try:
            with urlopen(request, timeout=45) as response:
                payload = json.load(response)
            if not isinstance(payload, dict):
                raise OpenAlexFetchError(f"OpenAlex returned non-object JSON for {url}")
            return payload
        except HTTPError as error:
            last_error = f"HTTP {error.code}"
            retryable = error.code == 429 or 500 <= error.code < 600
            if not retryable or attempt >= max_retries:
                break
            retry_after = error.headers.get("Retry-After")
            try:
                delay = float(retry_after) if retry_after else 0
            except (TypeError, ValueError):
                delay = 0
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = str(getattr(error, "reason", error))
            if attempt >= max_retries:
                break
            delay = 0

        time.sleep(max(delay, base_sleep_seconds * (2**attempt)))

    raise OpenAlexFetchError(f"Could not fetch {url}: {last_error or 'unknown error'}")


def _fetch_entity(entity: str, value: Any) -> Dict[str, Any]:
    openalex_id = normalize_openalex_id(value)
    if not openalex_id:
        raise OpenAlexFetchError(f"Invalid OpenAlex identifier: {value!r}")
    return fetch_json_with_retry(f"{OPENALEX_API}/{entity}/{openalex_id}")


def fetch_openalex_work(openalex_id_or_url: Any) -> Dict[str, Any]:
    return _fetch_entity("works", openalex_id_or_url)


def fetch_openalex_institution(institution_id_or_url: Any) -> Dict[str, Any]:
    return _fetch_entity("institutions", institution_id_or_url)


def abstract_from_inverted_index(inverted_index: Any) -> str:
    """Reconstruct an abstract from OpenAlex's word-to-position mapping."""
    if not isinstance(inverted_index, dict):
        return ""
    positioned = []
    for word, positions in inverted_index.items():
        if not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int):
                positioned.append((position, str(word)))
    return " ".join(word for _, word in sorted(positioned))


def normalize_title(value: Any) -> str:
    """Normalize harmless typography differences before comparing titles."""
    normalized = unicodedata.normalize("NFKC", str(value or "")).casefold()
    normalized = normalized.translate(
        str.maketrans(
            {
                "\u2010": "-",
                "\u2011": "-",
                "\u2012": "-",
                "\u2013": "-",
                "\u2014": "-",
                "\u2212": "-",
                "\u2018": "'",
                "\u2019": "'",
                "\u201c": '"',
                "\u201d": '"',
            }
        )
    )
    # Treat hyphenated compounds (notably "real-world") like spaced words.
    normalized = re.sub(r"[-_]+", " ", normalized)
    normalized = re.sub(r"[^\w]+", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split()).rstrip(" .,:;!?")


def title_similarity(left: Any, right: Any) -> float:
    return SequenceMatcher(None, normalize_title(left), normalize_title(right)).ratio()
