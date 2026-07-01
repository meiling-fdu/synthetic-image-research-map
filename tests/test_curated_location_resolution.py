import unittest

from scripts.curated_export import build_curated_map_records


class CuratedLocationResolutionTests(unittest.TestCase):
    def test_processed_cache_fallback_is_not_publicly_exportable(self):
        paper = {
            "paper_id": "curated:test",
            "title": "Cache fallback test",
            "year": 2026,
            "publication_year": 2026,
            "task": "detection",
            "subtask": "general",
            "doi": "10.1234/cache-test",
            "authors": ["Researcher"],
        }
        mapping = {
            "mapping_id": "mapping:test",
            "paper_id": "curated:test",
            "title": paper["title"],
            "year": "2026",
            "doi": paper["doi"],
            "institution": "Fudan University",
            "institution_authors": "Researcher",
            "mapping_status": "active",
        }
        cache_record = {
            "status": "resolved",
            "provider": "ROR",
            "record_status": "active",
            "resolved_institution_name": "Fudan University",
            "resolved_city": "Shanghai",
            "resolved_country": "CN",
            "resolved_latitude": 31.22222,
            "resolved_longitude": 121.45806,
            "match_names": ["Fudan University", "复旦大学"],
            "country_variants": ["CN", "China"],
            "source_url": "https://ror.org/013q1eq08",
        }

        markers, summary = build_curated_map_records(
            [paper],
            [mapping],
            [],
            confirmed_location_records=[],
            processed_cache_records=[cache_record],
        )

        self.assertEqual(summary["curated_markers_created"], 0)
        self.assertEqual(markers, [])
        self.assertEqual(summary["curated_mappings_missing_coordinates"], 1)

    def test_confirmed_curated_location_has_priority_over_cache(self):
        paper = {
            "paper_id": "curated:test",
            "title": "Curated priority test",
            "year": 2026,
            "task": "detection",
        }
        mapping = {
            "mapping_id": "mapping:test",
            "paper_id": "curated:test",
            "institution": "Example University",
            "mapping_status": "active",
        }
        confirmed = {
            "location_id": "location:test",
            "institution": "Example University",
            "normalized_institution": "example university",
            "city": "Curated City",
            "country": "Italy",
            "country_code": "IT",
            "lat": 41.0,
            "lon": 12.0,
        }
        cache_record = {
            "status": "resolved",
            "provider": "ROR",
            "record_status": "active",
            "resolved_institution_name": "Example University",
            "resolved_city": "Cache City",
            "resolved_country": "US",
            "resolved_latitude": 40.0,
            "resolved_longitude": -75.0,
            "match_names": ["Example University"],
            "country_variants": ["US", "United States"],
        }

        markers, _summary = build_curated_map_records(
            [paper],
            [mapping],
            [],
            confirmed_location_records=[confirmed],
            processed_cache_records=[cache_record],
        )

        self.assertEqual(markers[0]["latitude"], 41.0)
        self.assertEqual(markers[0]["longitude"], 12.0)
        self.assertEqual(
            markers[0]["resolution_method"], "curated_confirmed_location"
        )
        self.assertNotIn("fallback", markers[0]["notes"])


if __name__ == "__main__":
    unittest.main()
