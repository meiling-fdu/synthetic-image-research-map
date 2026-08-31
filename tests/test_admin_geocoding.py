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
    city_resolution_result,
    GeocodingInputError,
    GeocodingProviderError,
    GeocodingRateLimitError,
    NominatimProvider,
    normalize_nominatim_candidate,
    normalized_query,
    rank_candidates,
    resolve_candidate_locality,
)
from scripts.serve_admin import make_handler
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_AUDIT_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_AUDIT_COLUMNS,
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
    def test_nominatim_locality_precedence_and_supported_fallbacks(self):
        base = {
            "display_name": "Example University, Example Place",
            "lat": "40", "lon": "-75",
        }
        cases = [
            ({"city": "City", "town": "Town"}, "City", "nominatim:city"),
            ({"town": "Town", "municipality": "Municipality"}, "Town", "nominatim:town"),
            ({"municipality": "Municipality", "village": "Village"}, "Municipality", "nominatim:municipality"),
            ({"village": "Village", "borough": "Borough"}, "Village", "nominatim:village"),
            ({"borough": "Borough"}, "Borough", "nominatim:borough"),
        ]
        for address, expected, source in cases:
            with self.subTest(address=address):
                candidate = normalize_nominatim_candidate({**base, "address": address})
                self.assertEqual(candidate["city"], expected)
                self.assertEqual(candidate["locality_source"], source)

    def test_county_is_never_promoted_to_city(self):
        candidate = normalize_nominatim_candidate({
            "display_name": "Example University, Example County",
            "lat": "40", "lon": "-75",
            "address": {
                "municipality": "Example County", "county": "Example County",
                "country": "United States", "country_code": "us",
            },
        })
        self.assertEqual(candidate["city"], "")
        self.assertNotIn("county", candidate["locality_fields"])

    def test_raw_affiliation_resolves_missing_city_for_matching_candidate(self):
        candidate = normalize_nominatim_candidate({
            "name": "Bowie State University",
            "display_name": "Bowie State University, Patuxent Riding, Maryland, United States",
            "lat": "39.0183881", "lon": "-76.7609512",
            "address": {
                "university": "Bowie State University",
                "suburb": "Patuxent Riding",
                "state": "Maryland", "country": "United States", "country_code": "us",
            },
        })
        ranked = rank_candidates([candidate], {
            "names": ["Bowie State University"],
            "region": "Maryland", "country": "United States", "country_code": "US",
            "affiliation_evidence": [
                "Department of Computer Science, Bowie State University, Bowie, USA"
            ],
        })
        self.assertEqual(ranked[0]["city"], "Bowie")
        self.assertEqual(ranked[0]["locality_source"], "raw_affiliation:city")
        self.assertNotEqual(ranked[0]["city"], "Patuxent Riding")
        self.assertTrue(ranked[0]["selectable"])

    def test_conflicting_locality_evidence_remains_manual(self):
        candidate = normalize_nominatim_candidate({
            "name": "Example University",
            "display_name": "Example University, Alpha, Maryland, United States",
            "lat": "39", "lon": "-76",
            "address": {
                "university": "Example University", "city": "Alpha",
                "state": "Maryland", "country": "United States", "country_code": "us",
            },
        })
        resolved = resolve_candidate_locality(candidate, {
            "names": ["Example University"],
            "affiliation_evidence": ["Example University, Beta, USA"],
        })
        self.assertEqual(resolved["locality_resolution_status"], "conflict")
        self.assertIn("conflicts", resolved["locality_conflicts"][0])

    def test_unique_milan_city_resolution_populates_normalized_geography_only(self):
        result = city_resolution_result({"candidates": [{
            "display_name": "Milano, Lombardia, Italia",
            "city": "Milan", "region": "Lombardy", "country": "Italia",
            "country_code": "IT", "latitude": 45.46, "longitude": 9.19,
            "confidence": 0.72, "score": 60, "selectable": True,
        }, {
            "display_name": "Milan, Tennessee, United States",
            "city": "Milan", "region": "Tennessee", "country": "United States",
            "country_code": "US", "latitude": 35.9, "longitude": -88.8,
            "confidence": 0.2, "score": 25, "selectable": True,
        }]}, "Milan")
        self.assertEqual(result["resolution_status"], "resolved")
        self.assertEqual(result["resolved_location"]["region"], "Lombardy")
        self.assertEqual(result["resolved_location"]["country"], "Italy")
        self.assertFalse(result["coordinates_authoritative"])

    def test_cambridge_country_context_prefers_massachusetts(self):
        ranked = rank_candidates([{
            "display_name": "Cambridge, Massachusetts, United States",
            "city": "Cambridge", "region": "Massachusetts",
            "country": "United States", "country_code": "US",
            "latitude": 42.37, "longitude": -71.11, "confidence": 0.6,
        }, {
            "display_name": "Cambridge, Cambridgeshire, United Kingdom",
            "city": "Cambridge", "region": "Cambridgeshire",
            "country": "United Kingdom", "country_code": "GB",
            "latitude": 52.2, "longitude": 0.12, "confidence": 0.7,
        }], {"city": "Cambridge", "country": "United States", "country_code": "US"})
        result = city_resolution_result({"candidates": ranked}, "Cambridge")
        self.assertEqual(result["resolution_status"], "resolved")
        self.assertEqual(result["resolved_location"]["region"], "Massachusetts")

    def test_ambiguous_city_without_context_is_not_silently_resolved(self):
        result = city_resolution_result({"candidates": [{
            "display_name": "Springfield, Illinois", "city": "Springfield",
            "region": "Illinois", "country": "United States", "country_code": "US",
            "confidence": 0.55, "score": 50, "selectable": True,
        }, {
            "display_name": "Springfield, Missouri", "city": "Springfield",
            "region": "Missouri", "country": "United States", "country_code": "US",
            "confidence": 0.51, "score": 49, "selectable": True,
        }]}, "Springfield")
        self.assertEqual(result["resolution_status"], "ambiguous")
        self.assertIsNone(result["resolved_location"])

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
        self.assertIn("accept-language=en", requests[0])
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

    def request(self, geocoder, payload, path="/api/institution/geocode"):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler("token", geocoder=geocoder))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                path,
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

    def test_city_endpoint_reuses_geocoder_without_persisting(self):
        geocoder = EndpointGeocoder()
        status, payload = self.request(
            geocoder,
            self.geocode_payload(),
            "/api/institution/resolve-city",
        )
        self.assertEqual(status, 200)
        self.assertEqual(geocoder.calls[0][0], "")
        self.assertEqual(geocoder.calls[0][1], "Palermo")
        self.assertEqual(payload["data"]["resolution_kind"], "city")
        self.assertEqual(payload["data"]["resolution_status"], "resolved")
        self.assertFalse(payload["data"]["coordinates_authoritative"])

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
                "institution_audit_path": root / "audit.csv",
                "institution_location_audit_path": root / "location_audit.csv",
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
            self.write_csv(paths["institution_audit_path"], INSTITUTION_AUDIT_COLUMNS, [])
            self.write_csv(
                paths["institution_location_audit_path"],
                INSTITUTION_LOCATION_AUDIT_COLUMNS,
                [],
            )
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
            self.assertEqual(
                [row["city"] for row in detail["locations"]], ["Palermo"]
            )
            self.assertEqual(detail["aliases"], [])
            self.assertEqual(detail["location_reviews"], [])
            self.assertEqual(detail["review_queue"], [])
            self.assertEqual(len(detail["affiliation_evidence"]), 1)

            status, payload = self.request_with_handler(
                handler,
                "POST",
                (
                    "/api/admin/institutions/"
                    f"{self.institution_id}/confirm-location"
                ),
                {
                    "city": "Palermo", "region": "Sicily", "country": "Italy",
                    "country_code": "IT", "lat": "38.1157", "lon": "13.3615",
                    "coordinate_status": "known",
                },
            )
            self.assertEqual(status, 200)
            self.assertEqual(
                payload["data"]["institution_id"], self.institution_id
            )
            with paths["institution_location_audit_path"].open(
                encoding="utf-8", newline=""
            ) as handle:
                evidence = list(csv.DictReader(handle))
            self.assertEqual(len(evidence), 1)
            self.assertEqual(evidence[0]["action"], "location_confirmed")
            self.assertEqual(evidence[0]["institution_id"], self.institution_id)

            status, payload = self.request_with_handler(
                handler,
                "POST",
                (
                    "/api/admin/institutions/"
                    f"{self.institution_id}/confirm-location"
                ),
                {"institution_id": "institution:other"},
            )
            self.assertEqual(status, 400)
            self.assertIn("exactly match", payload["error"])

    def test_alias_and_merged_ids_resolve_to_the_active_canonical_institution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            active_id = self.institution_id
            merged_id = "institution:1111111111111111"
            alias_id = "alias:2222222222222222"
            paths = {
                "institutions_path": root / "institutions.csv",
                "institution_locations_path": root / "locations.csv",
                "institution_aliases_path": root / "aliases.csv",
                "institution_audit_path": root / "audit.csv",
                "location_review_path": root / "location_reviews.csv",
                "institution_review_queue_path": root / "review_queue.csv",
                "mappings_path": root / "mappings.csv",
            }
            self.write_csv(paths["institutions_path"], INSTITUTION_COLUMNS, [
                self.row(
                    INSTITUTION_COLUMNS, institution_id=active_id,
                    canonical_name="University of Palermo", institution_type="university",
                    institution_status="active",
                ),
                self.row(
                    INSTITUTION_COLUMNS, institution_id=merged_id,
                    canonical_name="Università di Palermo", institution_type="university",
                    institution_status="merged",
                ),
            ])
            self.write_csv(paths["institution_locations_path"], INSTITUTION_LOCATION_COLUMNS, [
                self.row(
                    INSTITUTION_LOCATION_COLUMNS, institution_id=active_id,
                    institution="University of Palermo", city="Palermo", country="Italy",
                    country_code="IT", lat="38.1173970", lon="13.3700045",
                )
            ])
            self.write_csv(paths["institution_aliases_path"], INSTITUTION_ALIAS_COLUMNS, [
                self.row(
                    INSTITUTION_ALIAS_COLUMNS, alias_id=alias_id,
                    alias_name="Università degli Studi di Palermo", institution_id=active_id,
                    canonical_institution_name="University of Palermo", review_status="confirmed",
                )
            ])
            self.write_csv(paths["institution_audit_path"], INSTITUTION_AUDIT_COLUMNS, [
                self.row(
                    INSTITUTION_AUDIT_COLUMNS, action="merge", institution_id=active_id,
                    previous_institution_id=merged_id,
                )
            ])
            for key, columns in (
                ("location_review_path", INSTITUTION_LOCATION_REVIEW_COLUMNS),
                ("institution_review_queue_path", INSTITUTION_REVIEW_QUEUE_COLUMNS),
                ("mappings_path", AUTHOR_INSTITUTION_MAPPING_COLUMNS),
            ):
                self.write_csv(paths[key], columns, [])
            handler = make_handler("token", **paths)

            for requested_id in (alias_id, merged_id):
                with self.subTest(requested_id=requested_id):
                    status, payload = self.request_with_handler(
                        handler, "GET", f"/api/institution?institution_id={requested_id}"
                    )
                    self.assertEqual(status, 200)
                    detail = payload["data"]
                    self.assertEqual(detail["requested_institution_id"], requested_id)
                    self.assertEqual(detail["editable_institution_id"], active_id)
                    self.assertEqual(detail["institution"]["institution_id"], active_id)
                    self.assertEqual(detail["current_location"]["city"], "Palermo")

            status, payload = self.request_with_handler(
                handler,
                "POST",
                f"/api/admin/institutions/{merged_id}/confirm-location",
                {},
            )
            self.assertEqual(status, 409)
            self.assertEqual(payload["error_code"], "inactive_institution")
            self.assertEqual(payload["active_institution_id"], active_id)


if __name__ == "__main__":
    unittest.main()
