import unittest

from scripts.curated_export import build_curated_map_records
from scripts.curated_locations import location_review_report
from scripts.validate_curated_database import validate_institution_aliases


class InstitutionReviewWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.paper = {
            "paper_id": "curated:test",
            "title": "Institution review test",
            "year": 2026,
            "task": "detection",
            "authors": ["Researcher"],
        }
        self.location = {
            "institution": "Complutense University of Madrid",
            "normalized_institution": "complutense university of madrid",
            "city": "Madrid",
            "country": "Spain",
            "country_code": "ES",
            "lat": 40.449167,
            "lon": -3.728056,
        }

    def mapping(self, institution):
        return {
            "mapping_id": f"mapping:{institution}",
            "paper_id": self.paper["paper_id"],
            "title": self.paper["title"],
            "year": "2026",
            "institution": institution,
            "mapping_status": "active",
        }

    def review(self, institution, status):
        return {
            "institution": institution,
            "related_paper_id": self.paper["paper_id"],
            "title": self.paper["title"],
            "year": "2026",
            "review_status": status,
        }

    def markers_for(self, institution, status, aliases=()):
        return build_curated_map_records(
            [self.paper],
            [self.mapping(institution)],
            [],
            location_review_rows=[self.review(institution, status)],
            confirmed_location_records=[self.location],
            institution_aliases=aliases,
        )[0]

    def test_confirmed_institution_is_exported(self):
        self.assertEqual(
            len(self.markers_for(
                "Complutense University of Madrid", "confirmed"
            )),
            1,
        )

    def test_non_exportable_statuses_are_not_exported(self):
        for status in (
            "pending_review",
            "needs_coordinates",
            "ambiguous",
            "alias_candidate",
            "ignore",
            "excluded",
        ):
            with self.subTest(status=status):
                self.assertEqual(
                    self.markers_for(
                        "Complutense University of Madrid", status
                    ),
                    [],
                )

    def test_spanish_and_chinese_aliases_resolve_to_canonical(self):
        aliases = [
            {
                "alias_name": alias,
                "canonical_institution_name":
                    "Complutense University of Madrid",
                "review_status": "confirmed",
            }
            for alias in ("Universidad Complutense de Madrid", "马德里康普顿斯大学")
        ]
        for alias in ("Universidad Complutense de Madrid", "马德里康普顿斯大学"):
            with self.subTest(alias=alias):
                markers = self.markers_for(
                    alias, "alias_of_confirmed", aliases
                )
                self.assertEqual(len(markers), 1)
                self.assertEqual(
                    markers[0]["institution"],
                    "Complutense University of Madrid",
                )

    def test_alias_does_not_create_duplicate_map_node(self):
        alias = {
            "alias_name": "Universidad Complutense de Madrid",
            "canonical_institution_name": "Complutense University of Madrid",
            "review_status": "confirmed",
        }
        mappings = [
            self.mapping("Complutense University of Madrid"),
            self.mapping("Universidad Complutense de Madrid"),
        ]
        reviews = [
            self.review("Complutense University of Madrid", "confirmed"),
            self.review(
                "Universidad Complutense de Madrid", "alias_of_confirmed"
            ),
        ]
        markers, _ = build_curated_map_records(
            [self.paper],
            mappings,
            [],
            location_review_rows=reviews,
            confirmed_location_records=[self.location],
            institution_aliases=[alias],
        )
        self.assertEqual(len(markers), 1)

    def test_status_counts_match_rows(self):
        rows = [
            {"review_status": "confirmed"},
            {"review_status": "pending_review"},
            {"review_status": "pending_review"},
            {"review_status": "alias_candidate"},
        ]
        summary = location_review_report(rows, [])
        self.assertEqual(summary["confirmed"], 1)
        self.assertEqual(summary["pending_review"], 2)
        self.assertEqual(summary["alias_candidate"], 1)

    def test_duplicate_and_conflicting_aliases_are_detected(self):
        aliases = [
            {
                "alias_name": "Universidad Ejemplo",
                "canonical_institution_name": canonical,
                "review_status": "confirmed",
            }
            for canonical in (
                "Example University",
                "Example University",
                "Other University",
            )
        ]
        confirmed = [
            {"institution": "Example University"},
            {"institution": "Other University"},
        ]
        issues = []
        validate_institution_aliases(aliases, confirmed, issues)
        messages = [issue.message for issue in issues]
        self.assertTrue(any("duplicate alias mapping" in item for item in messages))
        self.assertTrue(any("multiple canonical" in item for item in messages))


if __name__ == "__main__":
    unittest.main()
