import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_schema import (
    INSTITUTION_LOCATION_AUDIT_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)
from scripts.curated_schema_migrations import migrate_obsolete_location_schema


ROOT = Path(__file__).resolve().parents[1]
OBSOLETE = (
    "coordinate_source",
    "coordinate_source_url",
    "coordinate_review_note",
    "review_note",
)


def write_legacy(path, columns, row):
    fields = [*columns, *OBSOLETE]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({**{field: "" for field in fields}, **row})


class AdminInstitutionWorkflowCleanupTests(unittest.TestCase):
    def test_institution_authors_spans_full_mapping_form_width(self):
        html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        self.assertIn('<label class="full-width">Institution authors', html)
        self.assertIn('<label class="full-width">Raw affiliation', html)

    def test_removed_location_fields_are_absent_from_ui_and_schema(self):
        source = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in ("web/admin.html", "web/admin.js")
        )
        for field in ("coordinate-source", "coordinate-source-url", "coordinate-review-note"):
            self.assertNotIn(field, source)
        for columns in (
            INSTITUTION_LOCATION_COLUMNS,
            INSTITUTION_LOCATION_REVIEW_COLUMNS,
            INSTITUTION_LOCATION_AUDIT_COLUMNS,
        ):
            self.assertTrue(set(columns).isdisjoint(OBSOLETE))

    def test_legacy_location_rows_migrate_without_ids_changing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_legacy(root / "institution_locations.csv", INSTITUTION_LOCATION_COLUMNS, {
                "location_id": "location:stable", "institution_id": "institution:stable",
                "coordinate_source": "old", "coordinate_source_url": "https://old.test",
                "coordinate_review_note": "old coordinate note", "review_note": "old note",
            })
            write_legacy(root / "institution_location_review.csv", INSTITUTION_LOCATION_REVIEW_COLUMNS, {
                "institution_id": "institution:stable", "review_status": "needs_coordinates",
                "review_note": "old note",
            })
            write_legacy(root / "institution_location_audit_log.csv", INSTITUTION_LOCATION_AUDIT_COLUMNS, {
                "audit_id": "audit:stable", "institution_id": "institution:stable",
                "coordinate_source": "old", "review_note": "old note",
            })
            result = migrate_obsolete_location_schema(root)
            self.assertEqual(result["files_migrated"], 3)
            with (root / "institution_locations.csv").open(newline="") as handle:
                location = next(csv.DictReader(handle))
                self.assertEqual(location["location_id"], "location:stable")
                self.assertTrue(set(location).isdisjoint(OBSOLETE))
            with (root / "institution_location_review.csv").open(newline="") as handle:
                review = next(csv.DictReader(handle))
                self.assertEqual(review["review_status"], "pending_review")

    def test_only_primary_and_exception_actions_remain(self):
        html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        self.assertIn('id="location-confirm"', html)
        self.assertIn('id="location-confirm-alias"', html)
        for action in ("location-mark-ambiguous", "location-ignore", "location-exclude"):
            self.assertIn(f'id="{action}"', html)
        for removed in ("location-save-metadata", "location-needs-coordinates", "location-create-new"):
            self.assertNotIn(removed, html)


if __name__ == "__main__":
    unittest.main()
