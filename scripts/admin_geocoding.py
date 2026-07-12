#!/usr/bin/env python3
"""Server-side assisted geocoding for the local admin interface."""

from __future__ import annotations

import json
import math
import os
import threading
import time
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
        "latitude": latitude,
        "longitude": longitude,
        "confidence": confidence,
        "provider": "OpenStreetMap Nominatim",
        "provider_id": provider_id,
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

    def search(self, query: str) -> Sequence[Dict[str, Any]]:
        parameters = {"q": query, "format": "jsonv2", "addressdetails": "1", "limit": "5"}
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

    def search(self, institution_name: Any, address: Any) -> Dict[str, Any]:
        query = normalized_query(institution_name, address)
        cache_key = query.casefold()
        with self.lock:
            now = self.clock()
            cached = self.cache.get(cache_key)
            if cached and now - cached[0] <= self.ttl_seconds:
                self.cache.move_to_end(cache_key)
                return {"query": query, "provider": self.provider.name, "candidates": list(cached[1])}
            delay = self.minimum_interval - (now - self.last_request)
            if delay > 0:
                self.sleeper(delay)
            self.last_request = self.clock()
            candidates = list(self.provider.search(query))
            self.cache[cache_key] = (self.clock(), candidates)
            self.cache.move_to_end(cache_key)
            while len(self.cache) > self.max_entries:
                self.cache.popitem(last=False)
        return {"query": query, "provider": self.provider.name, "candidates": candidates}


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
