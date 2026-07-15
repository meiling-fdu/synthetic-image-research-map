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
from scripts.curated_institutions import stable_institution_id
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)
from scripts.validate_curated_database import validate_mapping_evidence


def write_empty_csv(path, columns):
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=columns).writeheader()


class OptionalMappingReviewNoteTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        directory = Path(self.temporary_directory.name)
        self.mappings_path = directory / "mappings.csv"
        self.locations_path = directory / "locations.csv"
        self.institutions_path = directory / "institutions.csv"
        write_empty_csv(self.mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
        write_empty_csv(self.locations_path, INSTITUTION_LOCATION_REVIEW_COLUMNS)
        write_empty_csv(self.institutions_path, INSTITUTION_COLUMNS)
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
        institution = draft.get("institution")
        if institution:
            with self.institutions_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            institution_id = stable_institution_id(institution)
            if not any(row["institution_id"] == institution_id for row in rows):
                rows.append({
                    **{column: "" for column in INSTITUTION_COLUMNS},
                    "institution_id": institution_id,
                    "canonical_name": institution,
                    "institution_type": "university",
                    "institution_status": "active",
                    "public_display": "self",
                })
                with self.institutions_path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=INSTITUTION_COLUMNS)
                    writer.writeheader()
                    writer.writerows(rows)
        return create_mapping(
            self.paper,
            draft,
            map_records=[],
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
            institutions_path=self.institutions_path,
        )["mapping"]

    def update(self, mapping_id, draft):
        return update_mapping(
            self.paper,
            mapping_id,
            draft,
            map_records=[],
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
            institutions_path=self.institutions_path,
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

    def test_create_rejects_unknown_canonical_institution_without_writing(self):
        before = self.mappings_path.read_bytes()
        with self.assertRaisesRegex(CuratedMappingError, "canonical registry"):
            create_mapping(
                self.paper,
                {
                    **self.draft,
                    "institution": "Unregistered University",
                },
                map_records=[],
                mappings_path=self.mappings_path,
                location_review_path=self.locations_path,
                institutions_path=self.institutions_path,
            )
        self.assertEqual(self.mappings_path.read_bytes(), before)

    def test_active_mapping_with_empty_review_note_passes_database_validation(self):
        issues = []

        validate_mapping_evidence(
            [{**self.draft, "mapping_status": "active", "review_note": ""}],
            issues,
        )

        self.assertEqual(issues, [])

    def test_active_mapping_with_review_note_passes_database_validation(self):
        issues = []

        validate_mapping_evidence(
            [
                {
                    **self.draft,
                    "mapping_status": "active",
                    "review_note": "Confirmed in publisher PDF",
                }
            ],
            issues,
        )

        self.assertEqual(issues, [])

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
