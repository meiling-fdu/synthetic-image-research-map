import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError

from scripts.admin_geocoding import (
    CachedGeocoder,
    GeocodingInputError,
    GeocodingProviderError,
    GeocodingRateLimitError,
    NominatimProvider,
    normalize_nominatim_candidate,
    normalized_query,
)
from scripts.serve_admin import make_handler


ROOT = Path(__file__).resolve().parent.parent


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class FakeProvider:
    name = "fake"

    def __init__(self):
        self.calls = []

    def search(self, query):
        self.calls.append(query)
        return [{"display_name": query, "latitude": 1.0, "longitude": 2.0}]


class AdminGeocodingTests(unittest.TestCase):
    def test_valid_name_and_address_return_normalized_candidate(self):
        provider = NominatimProvider(
            user_agent="test-agent",
            opener=lambda *_args, **_kwargs: Response([{
                "place_id": 42,
                "name": "Example University",
                "display_name": "Example University, Rome, Italy",
                "lat": "41.9",
                "lon": "12.5",
                "importance": 0.82,
                "address": {"university": "Example University"},
            }]),
        )
        result = CachedGeocoder(provider, minimum_interval=0).search(
            "Example University", "Rome, Italy"
        )
        candidate = result["candidates"][0]
        self.assertEqual(result["query"], "Example University, Rome, Italy")
        self.assertEqual(candidate["institution_name"], "Example University")
        self.assertEqual((candidate["latitude"], candidate["longitude"]), (41.9, 12.5))
        self.assertEqual(candidate["provider"], "OpenStreetMap Nominatim")
        self.assertNotIn("test-agent", json.dumps(result))

    def test_empty_overlong_and_malformed_queries_are_rejected(self):
        with self.assertRaises(GeocodingInputError):
            normalized_query("", "")
        with self.assertRaises(GeocodingInputError):
            normalized_query("x" * 201, "")
        with self.assertRaises(GeocodingInputError):
            normalized_query({"bad": "value"}, "Rome")

    def test_timeout_and_network_failure_are_safe_provider_errors(self):
        for failure in (TimeoutError(), URLError("offline")):
            with self.subTest(failure=failure):
                provider = NominatimProvider(
                    user_agent="test-agent",
                    opener=lambda *_args, failure=failure, **_kwargs: (_ for _ in ()).throw(failure),
                )
                with self.assertRaisesRegex(GeocodingProviderError, "temporarily unavailable"):
                    provider.search("Example")

    def test_provider_rate_limit_is_distinct_and_safe(self):
        error = HTTPError("https://example.invalid", 429, "limited", {}, None)
        provider = NominatimProvider(
            user_agent="test-agent",
            opener=lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
        )
        with self.assertRaises(GeocodingRateLimitError):
            provider.search("Example")

    def test_malformed_candidates_and_invalid_coordinates_are_ignored(self):
        self.assertIsNone(normalize_nominatim_candidate({"display_name": "Missing"}))
        self.assertIsNone(normalize_nominatim_candidate({
            "display_name": "Bad latitude", "lat": "91", "lon": "10"
        }))
        self.assertIsNone(normalize_nominatim_candidate({
            "display_name": "Bad longitude", "lat": "10", "lon": "181"
        }))
        provider = NominatimProvider(
            user_agent="test-agent",
            opener=lambda *_args, **_kwargs: Response([{"unexpected": True}]),
        )
        self.assertEqual(provider.search("Example"), [])

    def test_cache_normalizes_query_and_prevents_duplicate_calls(self):
        provider = FakeProvider()
        geocoder = CachedGeocoder(provider, minimum_interval=0)
        first = geocoder.search(" Example   University ", " Rome ")
        second = geocoder.search("example university", "rome")
        self.assertEqual(len(provider.calls), 1)
        self.assertEqual(first["candidates"], second["candidates"])


class EndpointGeocoder:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    def search(self, institution_name, address):
        self.calls.append((institution_name, address))
        if self.error:
            raise self.error
        return {
            "query": f"{institution_name}, {address}",
            "provider": "fake",
            "candidates": [{
                "display_name": "Example University, Rome",
                "institution_name": "Example University",
                "address": "Rome, Italy",
                "latitude": 41.9,
                "longitude": 12.5,
                "confidence": 0.8,
                "provider": "Fake Provider",
                "provider_id": "42",
                "map_url": "https://www.openstreetmap.org/",
            }],
        }


class AdminGeocodingEndpointTests(unittest.TestCase):
    def request(self, geocoder, payload):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler("token", geocoder=geocoder))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/institution/geocode",
                body=json.dumps(payload),
                headers={"X-Admin-Token": "token", "Content-Type": "application/json"},
            )
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_endpoint_returns_contract_without_writing_research_files(self):
        protected = [
            ROOT / "data/curated/institution_locations.csv",
            ROOT / "data/manual/institution_location_review.csv",
        ]
        before = {path: (path.stat().st_mtime_ns, path.stat().st_size) for path in protected if path.exists()}
        geocoder = EndpointGeocoder()
        status, payload = self.request(geocoder, {
            "institution_name": "Example University", "address": "Rome, Italy"
        })
        after = {path: (path.stat().st_mtime_ns, path.stat().st_size) for path in protected if path.exists()}
        self.assertEqual(status, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["provider"], "fake")
        self.assertEqual(geocoder.calls, [("Example University", "Rome, Italy")])
        self.assertEqual(before, after)
        self.assertNotIn("credential", json.dumps(payload).casefold())

    def test_endpoint_maps_provider_and_rate_limit_errors(self):
        cases = [
            (GeocodingProviderError("provider unavailable"), 502),
            (GeocodingRateLimitError("provider limited"), 429),
            (GeocodingInputError("bad query"), 400),
        ]
        for error, expected in cases:
            with self.subTest(error=error):
                status, payload = self.request(EndpointGeocoder(error), {
                    "institution_name": "Example", "address": "Rome"
                })
                self.assertEqual(status, expected)
                self.assertFalse(payload["success"])
                self.assertTrue(payload["errors"])


if __name__ == "__main__":
    unittest.main()
