import unittest
import json

from scripts.curated_export import build_curated_map_records, integrate_curated_records


class CuratedLocationResolutionTests(unittest.TestCase):
    def test_curated_alias_canonicalizes_automatic_export_without_mappings(self):
        stale = {
            "title": "Automatic candidate",
            "institution": "Federico II University Hospital",
            "institution_id": "institution:stale",
            "raw_affiliation": "University Federico II of Naples",
        }
        locations = [
            {
                "institution": "University of Naples Federico II",
                "normalized_institution": "university of naples federico ii",
            }
        ]
        aliases = [
            {
                "alias_name": "Federico II University Hospital",
                "canonical_institution_name": "University of Naples Federico II",
                "review_status": "confirmed",
            }
        ]

        papers, maps, _reviews, _summary = integrate_curated_records(
            [], [stale], [], [],
            confirmed_location_records=locations,
            institution_aliases=aliases,
        )

        self.assertEqual(papers, [])
        self.assertEqual(
            maps[0]["institution"], "University of Naples Federico II"
        )
        self.assertNotEqual(maps[0]["institution_id"], "institution:stale")

    def test_explicit_admin_supplement_survives_curated_supersession(self):
        paper = {
            "title": "Supplement test",
            "year": 2026,
            "task": "detection",
            "doi": "10.1000/supplement",
            "authors": ["Ada Researcher"],
        }
        supplement = {
            **paper,
            "institution": "Approved Lab",
            "institution_authors": ["Ada Researcher"],
            "public_evidence_mode": "add",
            "public_evidence_approval": "explicit_admin_supplement",
            "latitude": 40.0,
            "longitude": 10.0,
        }
        mapping = {
            "mapping_id": "mapping:primary",
            "title": paper["title"],
            "year": "2026",
            "doi": paper["doi"],
            "institution": "Primary University",
            "institution_authors": "Ada Researcher",
            "mapping_status": "active",
        }

        papers, maps, _reviews, _summary = integrate_curated_records(
            [paper], [supplement], [], [mapping]
        )

        self.assertEqual(
            [record["institution"] for record in maps], ["Approved Lab"]
        )
        self.assertEqual(
            [
                affiliation["institution"]
                for affiliation in papers[0][
                    "author_institution_affiliations"
                ]
            ],
            ["Primary University", "Approved Lab"],
        )

    def test_active_curated_mappings_replace_stale_openalex_affiliations(self):
        paper = {
            "title": (
                "Incremental learning for the detection and classification "
                "of GAN-generated images"
            ),
            "year": 2019,
            "publication_year": 2019,
            "task": "detection",
            "doi": "10.1109/wifs47025.2019.9035099",
            "openalex_url": "https://openalex.org/W3010699567",
            "authors": [
                "Francesco Marra",
                "Luisa Verdoliva",
                "Cristiano Saltori",
                "Giulia Boato",
            ],
        }
        stale_markers = [
            {
                **paper,
                "id": "stale-primary",
                "institution": "Federico II University Hospital",
                "institution_authors": [
                    "Marra, Francesco",
                    "Luisa Verdoliva",
                ],
                "source_database": "OpenAlex",
                "latitude": 40.85,
                "longitude": 14.26,
            },
            {
                **paper,
                "id": "stale-version",
                "openalex_url": "https://openalex.org/W2978778164",
                "institution": "Federico II University Hospital",
                "institution_authors": [
                    "Francesco Marra",
                    "Luisa Verdoliva",
                ],
                "source_database": "OpenAlex",
                "latitude": 40.85,
                "longitude": 14.26,
            },
        ]
        mappings = [
            {
                "mapping_id": "mapping:naples",
                "title": paper["title"],
                "year": "2019",
                "doi": paper["doi"],
                "openalex_url": paper["openalex_url"],
                "institution": "University of Naples Federico II",
                "institution_authors": "Francesco Marra; Luisa Verdoliva",
                "mapping_status": "active",
            },
            {
                "mapping_id": "mapping:trento",
                "title": paper["title"],
                "year": "2019",
                "doi": paper["doi"],
                "openalex_url": paper["openalex_url"],
                "institution": "University of Trento",
                "institution_authors": "Cristiano Saltori; Giulia Boato",
                "mapping_status": "active",
            },
        ]
        locations = [
            {
                "institution": "University of Naples Federico II",
                "normalized_institution": "university of naples federico ii",
                "city": "Naples",
                "country": "Italy",
                "country_code": "IT",
                "lat": 40.8463,
                "lon": 14.2572,
            },
            {
                "institution": "University of Trento",
                "normalized_institution": "university of trento",
                "city": "Trento",
                "country": "Italy",
                "country_code": "IT",
                "lat": 46.0668,
                "lon": 11.1232,
            },
        ]

        papers, maps, _reviews, summary = integrate_curated_records(
            [paper],
            stale_markers,
            [],
            mappings,
            confirmed_location_records=locations,
        )

        self.assertEqual(
            {record["institution"] for record in maps},
            {"University of Naples Federico II", "University of Trento"},
        )
        self.assertEqual(summary["stale_public_markers_suppressed"], 2)
        self.assertNotIn("Federico II University Hospital", json.dumps(maps))
        self.assertNotIn(
            "Federico II University Hospital", json.dumps(papers)
        )
        self.assertEqual(
            papers[0]["author_institution_affiliations"],
            [
                {
                    "index": 1,
                    "institution_id": papers[0][
                        "author_institution_affiliations"
                    ][0]["institution_id"],
                    "institution": "University of Naples Federico II",
                    "authors": ["Francesco Marra", "Luisa Verdoliva"],
                },
                {
                    "index": 2,
                    "institution_id": papers[0][
                        "author_institution_affiliations"
                    ][1]["institution_id"],
                    "institution": "University of Trento",
                    "authors": ["Cristiano Saltori", "Giulia Boato"],
                },
            ],
        )

    def test_exported_paper_has_author_institution_indices(self):
        curated_paper = {
            "paper_id": "curated:indices",
            "title": "Author index test",
            "year": "2026",
            "authors": "Ada Researcher; Ben Researcher",
            "task": "detection",
            "scope_status": "in_scope",
            "review_status": "reviewed",
        }
        mapping = {
            "mapping_id": "mapping:indices",
            "paper_id": "curated:indices",
            "institution": "Example University",
            "institution_authors": "Ada Researcher",
            "mapping_status": "needs_review",
        }

        papers, _maps, _reviews, _summary = integrate_curated_records(
            [], [], [curated_paper], [mapping]
        )

        self.assertEqual(
            papers[0]["author_institution_affiliations"][0]["index"], 1
        )
        self.assertEqual(
            papers[0]["author_institution_indices"][0]["institution_indices"],
            [1],
        )
        self.assertEqual(
            papers[0]["author_institution_indices"][0]["author"],
            "Ada Researcher",
        )

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
