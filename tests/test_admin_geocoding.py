import json
import csv
import tempfile
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
    rank_candidates,
)
from scripts.serve_admin import make_handler
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
    INSTITUTION_REVIEW_QUEUE_COLUMNS,
)


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
    def test_palermo_location_evidence_outranks_and_blocks_wrong_country(self):
        candidates = rank_candidates([
            {
                "display_name": "University of Palermo, Greifswald, Deutschland",
                "institution_name": "University of Palermo",
                "city": "Greifswald", "region": "Mecklenburg-Vorpommern",
                "country": "Germany", "country_code": "DE",
                "latitude": 54.0, "longitude": 13.4,
            },
            {
                "display_name": "Università degli Studi di Palermo, Palermo, Italia",
                "institution_name": "Università degli Studi di Palermo",
                "city": "Palermo", "region": "Sicilia",
                "country": "Italy", "country_code": "IT",
                "latitude": 38.1, "longitude": 13.3,
            },
        ], {
            "names": ["University of Palermo", "Università degli Studi di Palermo"],
            "city": "Palermo", "region": "Sicily", "country": "Italy",
            "country_code": "IT",
        })
        self.assertEqual(candidates[0]["country_code"], "IT")
        self.assertTrue(candidates[0]["selectable"])
        self.assertFalse(candidates[1]["selectable"])
        self.assertIn("country code conflicts", " ".join(candidates[1]["conflicts"]))

    def test_valid_name_and_address_return_normalized_candidate(self):
        requests = []
        provider = NominatimProvider(
            user_agent="test-agent",
            opener=lambda request, **_kwargs: (requests.append(request.full_url) or Response([{
                "place_id": 42,
                "name": "Example University",
                "display_name": "Example University, Rome, Italy",
                "lat": "41.9",
                "lon": "12.5",
                "importance": 0.82,
                "address": {
                    "university": "Example University",
                    "municipality": "Rome",
                    "province": "Lazio",
                    "country": "Italy",
                    "country_code": "it",
                },
            }])),
        )
        result = CachedGeocoder(provider, minimum_interval=0).search(
            "Example University", "Rome, Italy", context={"country_code": "IT"}
        )
        candidate = result["candidates"][0]
        self.assertEqual(result["query"], "Example University, Rome, Italy")
        self.assertEqual(candidate["institution_name"], "Example University")
        self.assertEqual((candidate["latitude"], candidate["longitude"]), (41.9, 12.5))
        self.assertEqual(candidate["provider"], "OpenStreetMap Nominatim")
        self.assertEqual(candidate["city"], "Rome")
        self.assertEqual(candidate["region"], "Lazio")
        self.assertEqual(candidate["country"], "Italy")
        self.assertEqual(candidate["country_code"], "IT")
        self.assertIn("countrycodes=it", requests[0])
        self.assertNotIn("test-agent", json.dumps(result))

    def test_macau_country_code_is_normalized_without_stale_fallback(self):
        candidate = normalize_nominatim_candidate({
            "name": "University of Macau",
            "display_name": "University of Macau, Avenida da Universidade, Taipa, Macau",
            "lat": "22.1295",
            "lon": "113.5453",
            "address": {
                "university": "University of Macau",
                "city": "Macau",
                "country": "Macau",
                "country_code": "mo",
            },
        })
        self.assertEqual(candidate["country_code"], "MO")
        self.assertEqual(candidate["region"], "")

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

    def search(self, institution_name, address, *, context=None):
        self.calls.append((institution_name, address, context))
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
    institution_id = "institution:a407f4c649ba4c6a"

    @staticmethod
    def write_csv(path, columns, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def row(columns, **values):
        return {column: values.get(column, "") for column in columns}

    def request_with_handler(self, handler, method, path, payload=None):
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            headers = {"X-Admin-Token": "token"}
            body = None
            if payload is not None:
                headers["Content-Type"] = "application/json"
                body = json.dumps(payload)
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def geocode_payload(self):
        return {
            "institution_id": self.institution_id,
            "loaded_institution_id": self.institution_id,
            "city": "Palermo", "region": "Sicily", "country": "Italy",
            "country_code": "IT",
        }

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
        status, payload = self.request(geocoder, self.geocode_payload())
        after = {path: (path.stat().st_mtime_ns, path.stat().st_size) for path in protected if path.exists()}
        self.assertEqual(status, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["provider"], "fake")
        self.assertEqual(geocoder.calls[0][0], "University of Palermo")
        self.assertEqual(geocoder.calls[0][1], "Palermo, Sicily, Italy")
        self.assertEqual(geocoder.calls[0][2]["country_code"], "IT")
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
                status, payload = self.request(EndpointGeocoder(error), self.geocode_payload())
                self.assertEqual(status, expected)
                self.assertFalse(payload["success"])
                self.assertTrue(payload["errors"])

    def test_missing_unknown_and_mismatched_institution_ids_are_rejected(self):
        cases = [
            ({}, "institution_id is required"),
            ({"institution_id": "institution:missing", "loaded_institution_id": "institution:missing"}, "unknown"),
            ({"institution_id": self.institution_id, "loaded_institution_id": "institution:other"}, "differs"),
        ]
        for body, message in cases:
            with self.subTest(body=body):
                status, payload = self.request(EndpointGeocoder(), body)
                self.assertEqual(status, 400)
                self.assertIn(message, " ".join(payload["errors"]))

    def test_palermo_detail_and_first_review_do_not_require_queue_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = {
                "institutions_path": root / "institutions.csv",
                "institution_locations_path": root / "locations.csv",
                "institution_aliases_path": root / "aliases.csv",
                "location_review_path": root / "location_reviews.csv",
                "institution_review_queue_path": root / "review_queue.csv",
                "mappings_path": root / "mappings.csv",
            }
            self.write_csv(paths["institutions_path"], INSTITUTION_COLUMNS, [self.row(
                INSTITUTION_COLUMNS, institution_id=self.institution_id,
                canonical_name="University of Palermo", institution_type="university",
                institution_status="active", public_display="self",
            )])
            self.write_csv(paths["institution_locations_path"], INSTITUTION_LOCATION_COLUMNS, [self.row(
                INSTITUTION_LOCATION_COLUMNS, location_id="location:a407f4c649ba4c6a",
                institution_id=self.institution_id, institution="University of Palermo",
                normalized_institution="university of palermo", city="Palermo",
                region="Sicily", country="Italy", country_code="IT",
                lat="38.1157", lon="13.3615",
                coordinate_source="Fixture source",
                coordinate_status="known",
                review_note="Fixture confirmation.",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
                created_by="test",
            )])
            self.write_csv(paths["institution_aliases_path"], INSTITUTION_ALIAS_COLUMNS, [])
            self.write_csv(paths["location_review_path"], INSTITUTION_LOCATION_REVIEW_COLUMNS, [])
            self.write_csv(paths["institution_review_queue_path"], INSTITUTION_REVIEW_QUEUE_COLUMNS, [])
            self.write_csv(paths["mappings_path"], AUTHOR_INSTITUTION_MAPPING_COLUMNS, [self.row(
                AUTHOR_INSTITUTION_MAPPING_COLUMNS, mapping_id="mapping:palermo",
                institution_id=self.institution_id, institution="University of Palermo",
                raw_affiliation="Department of Engineering, University of Palermo",
                mapping_status="active",
            )])
            handler = make_handler("token", **paths)
            status, payload = self.request_with_handler(
                handler, "GET", f"/api/institution?institution_id={self.institution_id}"
            )
            self.assertEqual(status, 200)
            detail = payload["data"]
            self.assertEqual(detail["institution"]["institution_id"], self.institution_id)
            self.assertEqual(detail["editable_institution_id"], self.institution_id)
            self.assertEqual(detail["current_location"]["city"], "Palermo")
            self.assertEqual(detail["aliases"], [])
            self.assertEqual(detail["location_reviews"], [])
            self.assertEqual(detail["review_queue"], [])
            self.assertEqual(len(detail["affiliation_evidence"]), 1)

            status, _payload = self.request_with_handler(handler, "POST", "/api/institution/location", {
                "institution_id": self.institution_id,
                "loaded_institution_id": self.institution_id,
                "city": "Palermo", "region": "Sicily", "country": "Italy",
                "country_code": "IT", "lat": "38.1157", "lon": "13.3615",
                "coordinate_source": "Fixture source",
                "coordinate_source_url": "https://example.test/palermo",
                "coordinate_status": "known", "review_note": "Fixture review.",
            })
            self.assertEqual(status, 200)
            with paths["location_review_path"].open(encoding="utf-8", newline="") as handle:
                reviews = list(csv.DictReader(handle))
            self.assertEqual(reviews, [])


if __name__ == "__main__":
    unittest.main()
