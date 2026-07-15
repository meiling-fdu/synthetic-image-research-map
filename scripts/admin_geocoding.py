#!/usr/bin/env python3
"""Server-side assisted geocoding for the local admin interface."""

from __future__ import annotations

import json
import difflib
import math
import os
import re
import threading
import time
import unicodedata
from collections import OrderedDict
from typing import Any, Callable, Dict, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"
MAX_QUERY_LENGTH = 300
MAX_FIELD_LENGTH = 200


class GeocodingError(RuntimeError):
    """A safe error suitable for returning through the admin API."""


class GeocodingInputError(GeocodingError):
    pass


class GeocodingProviderError(GeocodingError):
    pass


class GeocodingRateLimitError(GeocodingProviderError):
    pass


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalized_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).casefold()
    text = "".join(character for character in text if not unicodedata.combining(character))
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def text_similarity(left: Any, right: Any) -> float:
    first = normalized_text(left)
    second = normalized_text(right)
    if not first or not second:
        return 0.0
    if first == second or first in second or second in first:
        return 1.0
    return difflib.SequenceMatcher(None, first, second).ratio()


def normalized_query(institution_name: Any, address: Any) -> str:
    if not isinstance(institution_name, (str, type(None))) or not isinstance(
        address, (str, type(None))
    ):
        raise GeocodingInputError("institution_name and address must be strings")
    name = clean(institution_name)
    location = clean(address)
    if not name and not location:
        raise GeocodingInputError("institution_name or address is required")
    if len(name) > MAX_FIELD_LENGTH or len(location) > MAX_FIELD_LENGTH:
        raise GeocodingInputError(
            f"institution_name and address must each be at most {MAX_FIELD_LENGTH} characters"
        )
    query = ", ".join(part for part in (name, location) if part)
    if len(query) > MAX_QUERY_LENGTH:
        raise GeocodingInputError(f"geocoding query must be at most {MAX_QUERY_LENGTH} characters")
    return query


def _coordinate(value: Any, minimum: float, maximum: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError("invalid coordinate") from error
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise ValueError("coordinate outside valid range")
    return number


def normalize_nominatim_candidate(row: Mapping[str, Any]) -> Dict[str, Any] | None:
    try:
        latitude = _coordinate(row.get("lat"), -90, 90)
        longitude = _coordinate(row.get("lon"), -180, 180)
    except ValueError:
        return None
    display_name = clean(row.get("display_name"))
    if not display_name:
        return None
    address_data = row.get("address") if isinstance(row.get("address"), Mapping) else {}
    city = clean(
        address_data.get("city")
        or address_data.get("town")
        or address_data.get("village")
        or address_data.get("municipality")
    )
    region = clean(
        address_data.get("state")
        or address_data.get("region")
        or address_data.get("province")
    )
    country = clean(address_data.get("country"))
    raw_country_code = clean(address_data.get("country_code"))
    country_code = (
        raw_country_code.upper()
        if len(raw_country_code) == 2 and raw_country_code.isalpha()
        else ""
    )
    institution = clean(
        address_data.get("university")
        or address_data.get("college")
        or address_data.get("research_institute")
        or address_data.get("organisation")
        or row.get("name")
        or display_name.split(",", 1)[0]
    )
    try:
        confidence = float(row.get("importance"))
    except (TypeError, ValueError):
        confidence = None
    if confidence is not None and not math.isfinite(confidence):
        confidence = None
    provider_id = clean(row.get("place_id"))
    return {
        "display_name": display_name,
        "institution_name": institution,
        "address": display_name,
        "city": city,
        "region": region,
        "country": country,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "confidence": confidence,
        "provider": "OpenStreetMap Nominatim",
        "provider_id": provider_id,
        "category": clean(row.get("category") or row.get("class")),
        "entity_type": clean(row.get("type")),
        "map_url": (
            f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}"
            f"#map=16/{latitude}/{longitude}"
        ),
    }


class NominatimProvider:
    name = "nominatim"

    def __init__(
        self,
        *,
        user_agent: str,
        email: str = "",
        timeout: float = 8.0,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        if not clean(user_agent):
            raise GeocodingInputError("a geocoding User-Agent is required")
        self.user_agent = clean(user_agent)
        self.email = clean(email)
        self.timeout = timeout
        self.opener = opener

    def search(self, query: str, *, country_codes: str = "") -> Sequence[Dict[str, Any]]:
        parameters = {"q": query, "format": "jsonv2", "addressdetails": "1", "limit": "5"}
        if clean(country_codes):
            parameters["countrycodes"] = clean(country_codes).casefold()
        if self.email:
            parameters["email"] = self.email
        request = Request(
            f"{NOMINATIM_ENDPOINT}?{urlencode(parameters)}",
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code == 429:
                raise GeocodingRateLimitError("geocoding provider rate limit reached") from error
            raise GeocodingProviderError("geocoding provider request failed") from error
        except (TimeoutError, URLError, OSError, UnicodeError, json.JSONDecodeError) as error:
            raise GeocodingProviderError("geocoding provider is temporarily unavailable") from error
        if not isinstance(payload, list):
            raise GeocodingProviderError("geocoding provider returned an invalid response")
        return [
            candidate
            for row in payload
            if isinstance(row, Mapping)
            for candidate in [normalize_nominatim_candidate(row)]
            if candidate is not None
        ]


class CachedGeocoder:
    """Small in-memory cache and serialized throttle for a provider."""

    def __init__(
        self,
        provider: Any,
        *,
        ttl_seconds: float = 3600,
        max_entries: int = 128,
        minimum_interval: float = 1.0,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.provider = provider
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.minimum_interval = minimum_interval
        self.clock = clock
        self.sleeper = sleeper
        self.cache: OrderedDict[str, tuple[float, Sequence[Dict[str, Any]]]] = OrderedDict()
        self.last_request = float("-inf")
        self.lock = threading.Lock()

    def search(
        self,
        institution_name: Any,
        address: Any,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        query = normalized_query(institution_name, address)
        evidence = dict(context or {})
        country_code = clean(evidence.get("country_code")).upper()
        country_codes = country_code if len(country_code) == 2 else ""
        cache_key = "|".join((query.casefold(), country_codes.casefold()))
        with self.lock:
            now = self.clock()
            cached = self.cache.get(cache_key)
            if cached and now - cached[0] <= self.ttl_seconds:
                self.cache.move_to_end(cache_key)
                candidates = rank_candidates(cached[1], evidence)
                return geocoding_result(query, self.provider.name, candidates, evidence)
            delay = self.minimum_interval - (now - self.last_request)
            if delay > 0:
                self.sleeper(delay)
            self.last_request = self.clock()
            try:
                candidates = list(self.provider.search(query, country_codes=country_codes))
            except TypeError:
                # Small test/local providers may implement the original one-argument contract.
                candidates = list(self.provider.search(query))
            self.cache[cache_key] = (self.clock(), candidates)
            self.cache.move_to_end(cache_key)
            while len(self.cache) > self.max_entries:
                self.cache.popitem(last=False)
        ranked = rank_candidates(candidates, evidence)
        return geocoding_result(query, self.provider.name, ranked, evidence)


def _context_values(context: Mapping[str, Any], key: str) -> list[str]:
    value = context.get(key)
    if isinstance(value, (list, tuple, set)):
        return [clean(item) for item in value if clean(item)]
    return [clean(value)] if clean(value) else []


def rank_candidates(
    candidates: Sequence[Mapping[str, Any]], context: Mapping[str, Any] | None = None
) -> list[Dict[str, Any]]:
    """Rank provider results by explicit identity and location consistency."""
    evidence = dict(context or {})
    names = _context_values(evidence, "names") or _context_values(evidence, "institution_name")
    cities = _context_values(evidence, "cities") or _context_values(evidence, "city")
    regions = _context_values(evidence, "regions") or _context_values(evidence, "region")
    countries = _context_values(evidence, "countries") or _context_values(evidence, "country")
    codes = [value.upper() for value in (
        _context_values(evidence, "country_codes") or _context_values(evidence, "country_code")
    )]
    affiliations = _context_values(evidence, "affiliation_evidence")
    unrelated_types = {"house", "road", "residential", "postcode", "neighbourhood"}
    ranked = []
    for raw in candidates:
        candidate = dict(raw)
        score = 0.0
        conflicts = []
        factors = []
        candidate_code = clean(candidate.get("country_code")).upper()
        candidate_country = clean(candidate.get("country"))
        code_matches = bool(codes and candidate_code and candidate_code in codes)
        country_match = (
            max(text_similarity(candidate_country, value) for value in countries)
            if countries and candidate_country else 0.0
        )
        if codes and candidate_code:
            if code_matches:
                score += 120
                factors.append("country-code match")
            else:
                score -= 300
                conflicts.append("country code conflicts with confirmed evidence")
        if countries and candidate_country:
            if country_match >= 0.9:
                score += 90
                factors.append("country match")
            elif not (codes and candidate_code in codes):
                score -= 220
                conflicts.append("country conflicts with confirmed evidence")
        if cities and clean(candidate.get("city")):
            similarity = max(text_similarity(candidate.get("city"), value) for value in cities)
            if similarity >= 0.85:
                score += 55
                factors.append("city match")
            else:
                score -= 15
        if regions and clean(candidate.get("region")):
            similarity = max(text_similarity(candidate.get("region"), value) for value in regions)
            if similarity >= 0.68:
                score += 40
                factors.append("region match")
            else:
                score -= 12
                conflicts.append("region differs from known evidence")
        candidate_name = candidate.get("institution_name") or candidate.get("display_name")
        if names:
            similarity = max(text_similarity(candidate_name, value) for value in names)
            score += similarity * 45
            if similarity >= 0.75:
                factors.append("institution-name match")
        address_evidence = ", ".join((*cities, *regions, *countries))
        score += text_similarity(candidate.get("address"), address_evidence) * 15
        if affiliations:
            affiliation_similarity = max(
                text_similarity(candidate.get("address"), value) for value in affiliations
            )
            score += affiliation_similarity * 20
            if affiliation_similarity >= 0.65:
                factors.append("affiliation-address match")
        entity_type = normalized_text(candidate.get("entity_type") or candidate.get("category"))
        if entity_type in unrelated_types:
            score -= 80
            conflicts.append("provider entity type is unrelated to an institution")
        country_consistent = not any(item.startswith("country") for item in conflicts)
        if codes or countries:
            country_consistent = country_consistent and (
                code_matches or country_match >= 0.9
            )
            if not candidate_code and not candidate_country:
                conflicts.append("country is unavailable despite confirmed country evidence")
        candidate.update({
            "score": round(score, 3),
            "ranking_factors": factors,
            "conflicts": conflicts,
            "country_consistent": country_consistent,
            "selectable": country_consistent,
        })
        ranked.append(candidate)
    ranked.sort(key=lambda item: (-float(item.get("score", 0)), clean(item.get("display_name"))))
    return ranked


def geocoding_result(
    query: str,
    provider: str,
    candidates: Sequence[Mapping[str, Any]],
    context: Mapping[str, Any],
) -> Dict[str, Any]:
    values = [dict(candidate) for candidate in candidates]
    safe_count = sum(candidate.get("selectable") is not False for candidate in values)
    return {
        "query": query,
        "provider": provider,
        "candidates": values,
        "safe_candidate_count": safe_count,
        "no_safe_match": bool(values) and safe_count == 0,
        "context": {
            key: context.get(key)
            for key in ("city", "region", "country", "country_code")
            if clean(context.get(key))
        },
    }


def configured_geocoder() -> CachedGeocoder:
    provider_name = clean(os.environ.get("ADMIN_GEOCODING_PROVIDER", "nominatim")).casefold()
    if provider_name != "nominatim":
        raise GeocodingInputError(f"unsupported ADMIN_GEOCODING_PROVIDER: {provider_name}")
    provider = NominatimProvider(
        user_agent=os.environ.get(
            "ADMIN_GEOCODING_USER_AGENT",
            "synthetic-image-research-map-admin/1.0",
        ),
        email=os.environ.get("ADMIN_GEOCODING_EMAIL", ""),
    )
    return CachedGeocoder(provider)
