import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_mappings import (
    CuratedMappingError,
    create_mapping,
    load_mappings,
    update_mapping,
)
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)


def write_empty_csv(path, columns):
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=columns).writeheader()


class OptionalMappingReviewNoteTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        directory = Path(self.temporary_directory.name)
        self.mappings_path = directory / "mappings.csv"
        self.locations_path = directory / "locations.csv"
        write_empty_csv(self.mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
        write_empty_csv(self.locations_path, INSTITUTION_LOCATION_REVIEW_COLUMNS)
        self.paper = {
            "paper_id": "curated:test",
            "title": "Test paper",
            "year": "2026",
        }
        self.draft = {
            "institution": "Example University",
            "institution_authors": "Researcher One",
            "evidence_source": "Publisher PDF",
        }

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create(self, draft):
        return create_mapping(
            self.paper,
            draft,
            map_records=[],
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
        )["mapping"]

    def update(self, mapping_id, draft):
        return update_mapping(
            self.paper,
            mapping_id,
            draft,
            map_records=[],
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
        )["mapping"]

    def test_create_accepts_empty_missing_and_null_review_note(self):
        for index, note in enumerate(("", None, "missing")):
            draft = {
                **self.draft,
                "institution": f"Example University {index}",
            }
            if note != "missing":
                draft["review_note"] = note
            self.assertEqual(self.create(draft)["review_note"], "")

    def test_update_can_clear_review_note(self):
        mapping = self.create({**self.draft, "review_note": "Confirmed in PDF"})
        updated = self.update(mapping["mapping_id"], {**self.draft, "review_note": ""})
        self.assertEqual(updated["review_note"], "")

    def test_update_preserves_note_when_field_is_omitted(self):
        mapping = self.create({**self.draft, "review_note": "Confirmed in PDF"})
        updated = self.update(
            mapping["mapping_id"],
            {**self.draft, "evidence_source": "Author page"},
        )
        self.assertEqual(updated["review_note"], "Confirmed in PDF")
        self.assertEqual(load_mappings(self.mappings_path)[0]["review_note"], "Confirmed in PDF")

    def test_other_required_fields_remain_required(self):
        for field in ("institution", "institution_authors"):
            with self.subTest(field=field), self.assertRaises(CuratedMappingError):
                self.create({**self.draft, field: "", "review_note": ""})

    def test_frontend_marks_only_review_note_optional(self):
        html = (
            Path(__file__).resolve().parents[1] / "web" / "admin.html"
        ).read_text()
        self.assertIn("Review note (optional)", html)
        self.assertIn('id="mapping-review-note" rows="3"></textarea>', html)
        self.assertIn('id="mapping-institution" type="text" required', html)
        self.assertIn(
            'id="mapping-authors" type="text" placeholder="Separate authors with semicolons" required',
            html,
        )


if __name__ == "__main__":
    unittest.main()
