import unittest
import csv
import tempfile
from pathlib import Path

from scripts.curated_export import build_curated_map_records
from scripts.export_public_preview import public_institution_aliases
from scripts.curated_locations import (
    CuratedLocationError,
    confirm_alias,
    institution_candidate_evidence,
    load_institution_aliases,
    load_location_review_queue,
    location_review_payload,
    location_review_report,
    mark_queue_row,
    save_location_review_queue,
)
from scripts.curated_schema import (
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)
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

    def test_location_review_writer_rejects_blank_canonical_id(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reviews.csv"
            with self.assertRaisesRegex(
                CuratedLocationError, "require a canonical institution_id"
            ):
                save_location_review_queue(
                    [{"institution": "Unregistered Lab"}], path
                )

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

    def markers_without_known_coordinates(self, institution, status):
        return build_curated_map_records(
            [self.paper],
            [self.mapping(institution)],
            [],
            location_review_rows=[self.review(institution, status)],
            confirmed_location_records=[],
        )[0]

    def test_confirmed_institution_is_exported(self):
        self.assertEqual(
            len(self.markers_for(
                "Complutense University of Madrid", "confirmed"
            )),
            1,
        )

    def test_non_exportable_statuses_without_known_coordinates_are_not_exported(self):
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
                    self.markers_without_known_coordinates(
                        "Complutense University of Madrid", status
                    ),
                    [],
                )

    def test_known_coordinates_override_stale_review_statuses(self):
        for status in (
            "pending_review",
            "needs_coordinates",
            "ambiguous",
            "alias_candidate",
        ):
            with self.subTest(status=status):
                self.assertEqual(
                    len(self.markers_for("Complutense University of Madrid", status)),
                    1,
                )
        for status in ("ignore", "excluded"):
            with self.subTest(status=status):
                self.assertEqual(
                    self.markers_for("Complutense University of Madrid", status),
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

    def test_public_alias_export_is_confirmed_additive_and_provenanced(self):
        exported = public_institution_aliases([
            {
                "alias_name": "UdeM",
                "canonical_institution_name": "Université de Montréal",
                "alias_language": "fr",
                "alias_source": "maintainer-confirmed",
                "review_status": "confirmed",
            },
            {
                "alias_name": "Pending name",
                "canonical_institution_name": "Université de Montréal",
                "review_status": "pending_review",
            },
        ])
        self.assertEqual(len(exported), 1)
        self.assertEqual(exported[0]["alias_name"], "UdeM")
        self.assertEqual(exported[0]["alias_language"], "fr")
        self.assertEqual(exported[0]["alias_source"], "maintainer-confirmed")
        self.assertTrue(exported[0]["canonical_institution_id"].startswith("institution:"))

    def test_candidate_reasons_cover_abbreviations_subunits_and_near_duplicates(self):
        self.assertEqual(
            institution_candidate_evidence("MIT", "Massachusetts Institute of Technology")[1],
            "abbreviation_full_name",
        )
        self.assertEqual(
            institution_candidate_evidence("Example University Hospital", "Example University")[1],
            "parent_subunit_variant",
        )
        self.assertEqual(
            institution_candidate_evidence("Universite de Montreal", "Université de Montréal")[0],
            0.0,
        )

    @staticmethod
    def write_csv(path, columns, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def test_admin_alias_confirmation_persists_and_rejection_does_not_touch_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reviews = root / "reviews.csv"
            locations = root / "locations.csv"
            aliases = root / "aliases.csv"
            review_row = {column: "" for column in INSTITUTION_LOCATION_REVIEW_COLUMNS}
            review_row.update({
                "institution": "MIT",
                "institution_id": "institution:mit-alias",
                "related_paper_id": "curated:test",
                "title": "Institution review test",
                "year": "2026",
                "review_status": "alias_candidate",
            })
            location_row = {column: "" for column in INSTITUTION_LOCATION_COLUMNS}
            location_row.update({
                "location_id": "location:mit",
                "institution_id": "institution:mit",
                "institution": "Massachusetts Institute of Technology",
                "normalized_institution": "massachusetts institute of technology",
                "country": "United States",
                "country_code": "US",
                "lat": "42.3601",
                "lon": "-71.0942",
            })
            self.write_csv(reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [review_row])
            self.write_csv(locations, INSTITUTION_LOCATION_COLUMNS, [location_row])
            self.write_csv(aliases, INSTITUTION_ALIAS_COLUMNS, [])

            payload = location_review_payload(
                review_path=reviews,
                locations_path=locations,
                aliases_path=aliases,
                mappings=[self.mapping("MIT")],
            )
            candidate = payload["records"][0]
            self.assertEqual(candidate["candidate_suggestions"][0]["reason"], "abbreviation_full_name")
            self.assertEqual(len(candidate["affected_mappings"]), 1)
            self.assertEqual(len(candidate["affected_papers"]), 1)

            queue_id = candidate["queue_id"]
            mark_queue_row(queue_id, "ignore", "rejected candidate", review_path=reviews)
            self.assertEqual(load_institution_aliases(aliases), [])

            self.write_csv(reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [review_row])
            confirm_alias(
                queue_id,
                "Massachusetts Institute of Technology",
                review_path=reviews,
                locations_path=locations,
                aliases_path=aliases,
            )
            persisted = load_institution_aliases(aliases)
            self.assertEqual(len(persisted), 1)
            self.assertEqual(persisted[0]["alias_name"], "MIT")
            self.assertEqual(persisted[0]["institution_id"], "institution:mit")
            self.assertEqual(persisted[0]["review_status"], "confirmed")
            self.assertEqual(
                load_location_review_queue(reviews)[0]["institution_id"],
                "institution:mit",
            )
            saved_review = location_review_payload(
                review_path=reviews,
                locations_path=locations,
                aliases_path=aliases,
            )
            self.assertEqual(saved_review["total_unresolved"], 0)
            self.assertEqual(location_row["institution"], "Massachusetts Institute of Technology")


if __name__ == "__main__":
    unittest.main()
