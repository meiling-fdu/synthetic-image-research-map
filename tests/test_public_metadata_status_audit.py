import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicMetadataStatusAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "docs/public_metadata_status_audit.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_full_public_dataset_has_an_explained_classification(self):
        self.assertEqual(len(self.rows), 574)
        self.assertTrue(all(row["paper_id"] and row["title"] for row in self.rows))
        self.assertTrue(all(row["global_reason"] for row in self.rows))
        self.assertEqual(
            {row["corrected_overall"] for row in self.rows},
            {"Verified", "Needs review", "Source metadata"},
        )

    def test_every_previous_needs_review_paper_has_scoped_triggers(self):
        previous = [
            row for row in self.rows if row["previous_overall"] == "Needs review"
        ]
        self.assertEqual(len(previous), 212)
        for row in previous:
            self.assertIn(row["trigger_scope"], {"global", "local"})
            self.assertTrue(row["global_reason"])
            if row["corrected_overall"] != "Needs review":
                self.assertEqual(row["trigger_scope"], "local")
                self.assertTrue(row["local_reasons"])

    def test_audit_exposes_required_normalized_inputs_without_notes(self):
        required = {
            "curation_status", "review_status", "needs_review",
            "venue_review_required", "affiliation_review_state",
            "mapping_statuses", "field_specific_overrides",
        }
        self.assertTrue(required.issubset(self.rows[0]))
        self.assertNotIn("notes", self.rows[0])
        self.assertNotIn("review_id", self.rows[0])


if __name__ == "__main__":
    unittest.main()
