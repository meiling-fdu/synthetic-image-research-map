import tempfile
import unittest
from pathlib import Path

from scripts.migrate_publication_types import migrate_csv


class PublicationTypeMigrationTests(unittest.TestCase):
    def test_changes_only_publication_type_field_and_uses_conference_evidence(self):
        original = (
            "title,venue,publication_type,notes\n"
            '"Article in title","Journal of Tests",Article,"article remains prose"\n'
            '"Conference paper","Proceedings of Tests",article,"unchanged note"\n'
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.csv"
            path.write_text(original, encoding="utf-8")

            summary = migrate_csv(path, write=True)

            self.assertEqual(
                path.read_text(encoding="utf-8"),
                original.replace(
                    '"Journal of Tests",Article,',
                    '"Journal of Tests",journal,',
                ).replace(
                    '"Proceedings of Tests",article,',
                    '"Proceedings of Tests",conference,',
                ),
            )
            self.assertEqual(
                summary["changes"],
                {"Article -> journal": 1, "article -> conference": 1},
            )

    def test_dry_run_does_not_write(self):
        original = "title,publication_type\nExample,article\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.csv"
            path.write_text(original, encoding="utf-8")
            summary = migrate_csv(path, write=False)
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertEqual(summary["changes"], {"article -> journal": 1})

    def test_publication_venue_reclassifies_legacy_journal_as_conference(self):
        original = "title,publication_venue,publication_type\nExample,Proceedings of CVPR,journal\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.csv"
            path.write_text(original, encoding="utf-8")
            summary = migrate_csv(path, write=True)
            self.assertIn(",conference\n", path.read_text(encoding="utf-8"))
            self.assertEqual(summary["changes"], {"journal -> conference": 1})


if __name__ == "__main__":
    unittest.main()
