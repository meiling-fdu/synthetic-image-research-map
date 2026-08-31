import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_institutions import CuratedInstitutionError, stable_institution_id
from scripts.curated_locations import location_review_payload, queue_row_id
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_AUDIT_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_AUDIT_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)
from scripts.serve_admin import confirm_location_review_or_canonical


def blank(columns, **values):
    return {column: values.get(column, "") for column in columns}


def write_csv(path, columns, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class LocationConfirmationStateModelTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.name = "Canonical Test University"
        self.institution_id = stable_institution_id(self.name)
        self.paths = {
            "institutions_path": self.root / "institutions.csv",
            "institution_locations_path": self.root / "locations.csv",
            "location_review_path": self.root / "reviews.csv",
            "mappings_path": self.root / "mappings.csv",
            "institution_aliases_path": self.root / "aliases.csv",
            "institution_audit_path": self.root / "institution_audit.csv",
            "institution_location_audit_path": self.root / "location_audit.csv",
        }
        write_csv(self.paths["institutions_path"], INSTITUTION_COLUMNS, [blank(
            INSTITUTION_COLUMNS,
            institution_id=self.institution_id,
            canonical_name=self.name,
            institution_type="university",
            institution_status="active",
            public_display="self",
        )])
        write_csv(self.paths["institution_locations_path"], INSTITUTION_LOCATION_COLUMNS)
        write_csv(self.paths["location_review_path"], INSTITUTION_LOCATION_REVIEW_COLUMNS)
        write_csv(self.paths["mappings_path"], AUTHOR_INSTITUTION_MAPPING_COLUMNS, [blank(
            AUTHOR_INSTITUTION_MAPPING_COLUMNS,
            mapping_id="mapping:test",
            paper_id="paper:test",
            title="Synthetic Image Detection",
            year="2026",
            institution_id=self.institution_id,
            institution=self.name,
            institution_authors="Test Author",
            raw_affiliation=f"Lab, {self.name}",
            mapping_status="active",
        )])
        write_csv(self.paths["institution_aliases_path"], INSTITUTION_ALIAS_COLUMNS, [blank(
            INSTITUTION_ALIAS_COLUMNS,
            alias_id="alias:test",
            alias_name="CTU",
            institution_id=self.institution_id,
            canonical_institution_name=self.name,
            review_status="confirmed",
        )])
        write_csv(self.paths["institution_audit_path"], INSTITUTION_AUDIT_COLUMNS)
        write_csv(
            self.paths["institution_location_audit_path"],
            INSTITUTION_LOCATION_AUDIT_COLUMNS,
        )

    def tearDown(self):
        self.temporary.cleanup()

    def draft(self, queue_id="derived:missing"):
        return {
            "queue_id": queue_id,
            "institution_id": self.institution_id,
            "confirmed_institution": self.name,
            "confirmed_city": "Baltimore",
            "confirmed_region": "Maryland",
            "confirmed_country": "United States",
            "confirmed_country_code": "US",
            "confirmed_lat": "39.29038",
            "confirmed_lon": "-76.61219",
        }

    def confirm(self, payload=None):
        return confirm_location_review_or_canonical(payload or self.draft(), **self.paths)

    def test_confirmation_without_review_row_is_canonical_and_preserves_relationships(self):
        protected = {
            key: self.paths[key].read_bytes()
            for key in (
                "institutions_path", "mappings_path",
                "institution_aliases_path", "institution_audit_path",
            )
        }
        result = self.confirm()
        self.assertTrue(result["canonical_confirmation"])
        location = read_csv(self.paths["institution_locations_path"])[0]
        self.assertEqual(location["institution_id"], self.institution_id)
        self.assertEqual(location["city"], "Baltimore")
        self.assertEqual(location["region"], "Maryland")
        self.assertEqual(location["country"], "United States")
        self.assertEqual(location["coordinate_status"], "known")
        self.assertEqual(read_csv(self.paths["location_review_path"]), [])
        for key, content in protected.items():
            self.assertEqual(self.paths[key].read_bytes(), content)
        mapping = read_csv(self.paths["mappings_path"])[0]
        self.assertEqual(mapping["paper_id"], "paper:test")
        self.assertEqual(mapping["institution_id"], self.institution_id)

    def test_confirmation_with_existing_review_row_keeps_legacy_workflow(self):
        review = blank(
            INSTITUTION_LOCATION_REVIEW_COLUMNS,
            institution=self.name,
            canonical_institution_name=self.name,
            institution_id=self.institution_id,
            related_paper_id="paper:test",
            title="Synthetic Image Detection",
            year="2026",
            review_status="pending_review",
            location_status="missing",
            coordinate_status="missing",
        )
        write_csv(
            self.paths["location_review_path"],
            INSTITUTION_LOCATION_REVIEW_COLUMNS,
            [review],
        )
        result = self.confirm(self.draft(queue_row_id(review)))
        self.assertFalse(result.get("canonical_confirmation", False))
        self.assertEqual(result["queue_row"]["review_status"], "confirmed")
        saved_review = read_csv(self.paths["location_review_path"])[0]
        self.assertEqual(saved_review["location_status"], "known")
        self.assertEqual(saved_review["coordinate_status"], "known")
        first = {
            key: self.paths[key].read_bytes()
            for key in ("institution_locations_path", "location_review_path")
        }
        self.confirm(self.draft(queue_row_id(review)))
        for key, content in first.items():
            self.assertEqual(self.paths[key].read_bytes(), content)

    def test_repeated_canonical_confirmation_is_idempotent(self):
        self.confirm()
        first = {
            key: self.paths[key].read_bytes()
            for key in (
                "institution_locations_path", "institution_location_audit_path",
                "mappings_path", "institution_aliases_path",
            )
        }
        self.confirm()
        self.assertEqual(len(read_csv(self.paths["institution_locations_path"])), 1)
        self.assertEqual(len(read_csv(self.paths["institution_location_audit_path"])), 1)
        for key, content in first.items():
            self.assertEqual(self.paths[key].read_bytes(), content)

    def test_missing_invalid_and_country_inconsistent_coordinates_do_not_write(self):
        cases = [
            ({"confirmed_lat": ""}, "lat is required"),
            ({"confirmed_lon": "181"}, "lon must be between"),
            (
                {"confirmed_country": "Germany", "confirmed_country_code": "US"},
                "same country",
            ),
        ]
        before = self.paths["institution_locations_path"].read_bytes()
        for changes, message in cases:
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(CuratedInstitutionError, message):
                    self.confirm({**self.draft(), **changes})
                self.assertEqual(
                    self.paths["institution_locations_path"].read_bytes(), before
                )

    def test_review_payload_identifies_derived_and_persisted_rows(self):
        mappings = read_csv(self.paths["mappings_path"])
        derived = location_review_payload(
            review_path=self.paths["location_review_path"],
            locations_path=self.paths["institution_locations_path"],
            aliases_path=self.paths["institution_aliases_path"],
            mappings=mappings,
            institutions_path=self.paths["institutions_path"],
        )["records"]
        self.assertEqual(len(derived), 1)
        self.assertFalse(derived[0]["review_row_persisted"])

        persisted = blank(
            INSTITUTION_LOCATION_REVIEW_COLUMNS,
            institution=self.name,
            canonical_institution_name=self.name,
            institution_id=self.institution_id,
            related_paper_id="paper:test",
            title="Synthetic Image Detection",
            year="2026",
            review_status="pending_review",
            location_status="missing",
            coordinate_status="missing",
        )
        write_csv(
            self.paths["location_review_path"],
            INSTITUTION_LOCATION_REVIEW_COLUMNS,
            [persisted],
        )
        records = location_review_payload(
            review_path=self.paths["location_review_path"],
            locations_path=self.paths["institution_locations_path"],
            aliases_path=self.paths["institution_aliases_path"],
            mappings=mappings,
            institutions_path=self.paths["institutions_path"],
        )["records"]
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0]["review_row_persisted"])


if __name__ == "__main__":
    unittest.main()
