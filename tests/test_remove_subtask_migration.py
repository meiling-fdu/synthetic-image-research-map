import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_papers import CuratedPaperError, normalize_paper_draft
from scripts.migrate_remove_subtask import migrate_csv


class RemoveSubtaskMigrationTests(unittest.TestCase):
    def test_migration_is_idempotent_and_preserves_other_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.csv"
            path.write_text(
                'paper_id,title,task,subtask,authors\n'
                'paper:1,"Title, exact",detection,synthetic_image_detection,"A; B"\n',
                encoding="utf-8",
            )
            removed, audit = migrate_csv(path)
            self.assertEqual(removed, 1)
            self.assertEqual(audit[0]["assessment"], "consistent")
            first_bytes = path.read_bytes()
            removed_again, audit_again = migrate_csv(path)
            self.assertEqual((removed_again, audit_again), (0, []))
            self.assertEqual(path.read_bytes(), first_bytes)
            rows = list(csv.DictReader(path.open(encoding="utf-8")))
            self.assertEqual(
                rows,
                [{
                    "paper_id": "paper:1",
                    "title": "Title, exact",
                    "task": "detection",
                    "authors": "A; B",
                }],
            )

    def test_current_canonical_input_rejects_removed_field(self):
        with self.assertRaises(CuratedPaperError) as error:
            normalize_paper_draft({"subtask": "synthetic_image_detection"})
        self.assertEqual(error.exception.error_code, "removed_field")


if __name__ == "__main__":
    unittest.main()
