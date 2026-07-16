import unittest
import json

from scripts.curated_export import (
    CuratedExportError,
    _recalculate_paper_details,
    _remove_overridden_markers,
    _upsert_location_review,
    build_curated_map_records,
    integrate_curated_records,
)
from scripts.export_public_preview import add_public_detail_fields


class CuratedLocationResolutionTests(unittest.TestCase):
    def test_export_location_review_sync_preserves_canonical_identity(self):
        reviews = []
        mapping = {
            "paper_id": "openalex:W2903907439",
            "title": "Cascade learning from adversarial synthetic images",
            "institution": "Rensselaer Polytechnic Institute",
            "institution_id": "institution:50c86a6fc102a2c1",
            "institution_authors": "Qiang Ji",
        }

        result = _upsert_location_review(
            reviews, mapping, coordinate_status="missing"
        )

        self.assertEqual(result, "created")
        self.assertEqual(
            reviews[0]["institution_id"], "institution:50c86a6fc102a2c1"
        )
        self.assertEqual(
            reviews[0]["canonical_institution_name"],
            "Rensselaer Polytechnic Institute",
        )

    def test_export_location_review_sync_rejects_blank_canonical_id(self):
        with self.assertRaisesRegex(
            CuratedExportError, "requires a canonical institution_id"
        ):
            _upsert_location_review(
                [],
                {"paper_id": "paper:fixture", "institution": "Example Lab"},
                coordinate_status="missing",
            )

    def test_recalculation_discards_stale_derived_affiliations(self):
        paper = {
            "title": "Corrected derived details",
            "year": 2022,
            "doi": "10.1000/derived",
            "authors": ["Ada Researcher"],
            "affiliations": [{"index": 1, "name": "Old University"}],
            "current_institution": {"index": 1, "name": "Old University"},
        }
        mapping = {
            **paper,
            "mapping_id": "mapping:corrected",
            "institution": "Correct University",
            "institution_authors": "Ada Researcher",
            "mapping_status": "active",
        }

        _recalculate_paper_details(
            paper, [], [mapping], {"mapping:corrected"}
        )

        self.assertNotIn("affiliations", paper)
        self.assertNotIn("current_institution", paper)
        self.assertEqual(
            paper["author_institution_affiliations"][0]["institution"],
            "Correct University",
        )

    def test_curated_marker_id_replaces_stale_institution_spelling(self):
        paper = {
            "title": "Corrected institution",
            "year": 2022,
            "doi": "10.1000/corrected",
        }
        stale = {
            **paper,
            "id": "curated-map:stable",
            "institution": "Univresity of Example",
            "institution_authors": ["Ada Researcher"],
            "source_database": "curated",
        }
        replacement = {
            **paper,
            "id": "curated-map:stable",
            "institution": "University of Example",
            "institution_authors": ["Ada Researcher"],
            "source_database": "curated",
        }
        records = [stale]

        removed = _remove_overridden_markers(records, paper, replacement)

        self.assertEqual(removed, 1)
        self.assertEqual(records, [])

    def test_curated_mapping_suppresses_explicit_marker_supplements(self):
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
            "institution_id": "institution:primary",
            "institution_authors": "Ada Researcher",
            "mapping_status": "active",
        }

        papers, maps, _reviews, _summary = integrate_curated_records(
            [paper], [supplement], [], [mapping]
        )

        self.assertEqual(maps, [])
        self.assertEqual(
            [
                affiliation["institution"]
                for affiliation in papers[0][
                    "author_institution_affiliations"
                ]
            ],
            ["Primary University"],
        )

    def test_unreviewed_paper_uses_preliminary_automatic_fallback(self):
        paper = {
            "title": "Unreviewed fallback",
            "year": 2025,
            "doi": "10.1000/unreviewed",
            "authors": ["Ada Researcher"],
        }
        automatic = {
            **paper,
            "institution": "Automatic University",
            "institution_authors": ["Ada Researcher"],
            "source_database": "OpenAlex",
            "latitude": 1.0,
            "longitude": 2.0,
        }

        papers, maps, _reviews, _summary = integrate_curated_records(
            [paper], [automatic], [], []
        )

        self.assertEqual(papers[0]["affiliation_review_state"], "unreviewed")
        self.assertTrue(papers[0]["preliminary_affiliations"])
        self.assertEqual(maps[0]["institution"], "Automatic University")
        self.assertEqual(maps[0]["institution_source"], "automatic_fallback")
        self.assertTrue(maps[0]["preliminary_affiliations"])

    def test_reviewed_empty_suppresses_markers_and_superscripts(self):
        paper = {
            "title": "Reviewed empty",
            "year": 2025,
            "doi": "10.1000/reviewed-empty",
            "authors": ["Ada Researcher"],
        }
        automatic = {
            **paper,
            "institution": "Automatic University",
            "institution_authors": ["Ada Researcher"],
            "source_database": "OpenAlex",
            "latitude": 1.0,
            "longitude": 2.0,
        }
        excluded = {
            **paper,
            "mapping_id": "mapping:excluded",
            "institution": "Rejected University",
            "institution_authors": "Ada Researcher",
            "mapping_status": "excluded",
        }

        papers, maps, _reviews, _summary = integrate_curated_records(
            [paper], [automatic], [], [excluded]
        )
        add_public_detail_fields(papers, maps)

        self.assertEqual(maps, [])
        self.assertEqual(papers[0]["affiliation_review_state"], "reviewed_empty")
        self.assertEqual(papers[0]["affiliations"], [])
        self.assertEqual(papers[0]["authors"][0]["affiliation_indices"], [])

    def test_noise_informed_four_curated_mappings_replace_automatic_records(self):
        paper = {
            "title": "Noise-Informed Diffusion-Generated Image Detection With Anomaly Attention",
            "year": 2025,
            "publication_year": 2025,
            "task": "detection",
            "doi": "10.1109/tifs.2025.3573161",
            "openalex_url": "https://openalex.org/W4410853187",
            "authors": [
                "Weinan Guan", "Wei Wang", "Bo Peng", "Ziwen He",
                "Jing Dong", "Haonan Cheng",
            ],
        }
        institutions = [
            ("University of Chinese Academy of Sciences", "Weinan Guan"),
            (
                "Institute of Automation, Chinese Academy of Sciences",
                "Weinan Guan; Wei Wang; Bo Peng; Jing Dong",
            ),
            (
                "Nanjing University of Information Science and Technology",
                "Ziwen He",
            ),
            ("Communication University of China", "Haonan Cheng"),
        ]
        mappings = [
            {
                **paper,
                "mapping_id": f"mapping:noise-{index}",
                "institution": institution,
                "institution_authors": authors,
                "mapping_status": "active",
            }
            for index, (institution, authors) in enumerate(institutions, start=1)
        ]
        locations = [
            {
                "location_id": f"location:noise-{index}",
                "institution": institution,
                "normalized_institution": institution.casefold(),
                "city": f"City {index}",
                "country": "China",
                "country_code": "CN",
                "lat": 30.0 + index,
                "lon": 110.0 + index,
            }
            for index, (institution, _authors) in enumerate(institutions, start=1)
        ]
        automatic = [
            {
                **paper,
                "id": "automatic-stale",
                "institution": "Chinese Academy of Sciences",
                "institution_authors": ["Weinan Guan"],
                "source_database": "OpenAlex",
                "latitude": 39.0,
                "longitude": 116.0,
            },
            {
                **paper,
                "id": "automatic-overlap",
                "institution": "Communication University of China",
                "institution_authors": ["Haonan Cheng"],
                "source_database": "OpenAlex",
                "latitude": 39.9,
                "longitude": 116.4,
            },
        ]

        first = integrate_curated_records(
            [paper], automatic, [], mappings,
            confirmed_location_records=locations,
        )
        second = integrate_curated_records(
            [paper], automatic, [], mappings,
            confirmed_location_records=locations,
        )
        self.assertEqual(first, second)
        exported_papers, exported_maps, _reviews, summary = first
        add_public_detail_fields(exported_papers, exported_maps)

        self.assertEqual(summary["stale_public_markers_suppressed"], 2)
        self.assertEqual(len(exported_maps), 4)
        self.assertEqual(
            [record["institution"] for record in exported_maps],
            [institution for institution, _authors in institutions],
        )
        self.assertEqual(
            {record["source_database"] for record in exported_maps}, {"curated"}
        )
        self.assertEqual(
            [row["name"] for row in exported_papers[0]["affiliations"]],
            [institution for institution, _authors in institutions],
        )

    def test_merged_identity_uses_curated_precedence(self):
        canonical = {
            "title": "Published title",
            "year": 2025,
            "doi": "10.1000/published",
            "task": "detection",
            "authors": ["Ada Researcher"],
            "merged_versions": [
                {
                    "title": "Preprint title",
                    "year": 2024,
                    "openalex_url": "https://openalex.org/W123",
                }
            ],
        }
        automatic = {
            **canonical,
            "institution": "Automatic University",
            "source_database": "OpenAlex",
            "latitude": 1.0,
            "longitude": 2.0,
        }
        mapping = {
            "title": "Preprint title",
            "year": "2024",
            "openalex_url": "https://openalex.org/W123",
            "mapping_id": "mapping:merged",
            "institution": "Curated University",
            "institution_id": "institution:curated",
            "institution_authors": "Ada Researcher",
            "mapping_status": "active",
        }

        papers, maps, _reviews, _summary = integrate_curated_records(
            [canonical], [automatic], [], [mapping]
        )

        self.assertEqual(maps, [])
        self.assertEqual(papers[0]["affiliation_review_state"], "curated")
        self.assertEqual(
            papers[0]["author_institution_affiliations"][0]["institution"],
            "Curated University",
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
                    "mapping_source": "curated_admin",
                    "mapping_fallback": False,
                },
                {
                    "index": 2,
                    "institution_id": papers[0][
                        "author_institution_affiliations"
                    ][1]["institution_id"],
                    "institution": "University of Trento",
                    "authors": ["Cristiano Saltori", "Giulia Boato"],
                    "mapping_source": "curated_admin",
                    "mapping_fallback": False,
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
            "source_database": "manual",
            "curation_status": "manually_added",
            "review_status": "reviewed",
        }
        mapping = {
            "mapping_id": "mapping:indices",
            "paper_id": "curated:indices",
            "institution": "Example University",
            "institution_id": "institution:example",
            "institution_authors": "Ada Researcher",
            "mapping_status": "active",
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
        add_public_detail_fields(papers, [])
        self.assertEqual(
            papers[0]["authors"],
            [
                {
                    "name": "Ada Researcher",
                    "affiliation_indices": [1],
                    "is_current_marker_author": False,
                    "affiliation_source": "curated_admin",
                    "affiliation_fallback": False,
                },
                {
                    "name": "Ben Researcher",
                    "affiliation_indices": [],
                    "is_current_marker_author": False,
                    "affiliation_source": "unmapped",
                    "affiliation_fallback": False,
                },
            ],
        )
        self.assertEqual(
            papers[0]["affiliations"][0]["name"], "Example University"
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
            "institution_id": "institution:fudan",
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
