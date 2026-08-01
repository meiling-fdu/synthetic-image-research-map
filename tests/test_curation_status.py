import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_papers import CuratedPaperError, read_curated_papers
from scripts.curated_schema import PAPERS_COLUMNS, normalize_curation_status
from scripts.migrate_curation_status import migrate


class CurationStatusTests(unittest.TestCase):
    def test_legacy_and_canonical_normalization(self):
        expected = {
            "corrected_by_admin": "confirmed",
            "manually_confirmed": "confirmed",
            "manually_added": "confirmed",
            "auto_imported": "needs_review",
            "needs_review": "needs_review",
            "confirmed": "confirmed",
            "": "needs_review",
            None: "needs_review",
        }
        for value, canonical in expected.items():
            with self.subTest(value=value):
                self.assertEqual(normalize_curation_status(value), canonical)

    def test_unknown_status_fails_in_strict_mode_and_is_never_confirmed(self):
        with self.assertRaisesRegex(ValueError, "unsupported curation_status"):
            normalize_curation_status("mystery")
        self.assertEqual(
            normalize_curation_status("mystery", reject_unknown=False),
            "needs_review",
        )

    def test_read_boundary_normalizes_every_legacy_value(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.csv"
            self._write_rows(path, [self._row(status) for status in (
                "corrected_by_admin", "manually_confirmed", "manually_added",
                "auto_imported", "needs_review", "confirmed",
            )])
            self.assertEqual(
                [row["curation_status"] for row in read_curated_papers(path)],
                ["confirmed", "confirmed", "confirmed", "needs_review", "needs_review", "confirmed"],
            )

    def test_unknown_persisted_value_is_reported_with_row_context(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.csv"
            self._write_rows(path, [self._row("mystery")])
            with self.assertRaisesRegex(CuratedPaperError, "papers.csv:2"):
                read_curated_papers(path)

    def test_migration_is_idempotent_and_preserves_unrelated_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.csv"
            rows = [self._row("manually_added"), self._row("auto_imported")]
            rows[0]["title"] = "Keep, punctuation and formatting"
            self._write_rows(path, rows)
            self.assertEqual(migrate(path), 2)
            first = path.read_bytes()
            self.assertEqual(migrate(path), 0)
            self.assertEqual(path.read_bytes(), first)
            with path.open(encoding="utf-8", newline="") as handle:
                migrated = list(csv.DictReader(handle))
            self.assertEqual(migrated[0]["title"], rows[0]["title"])
            self.assertEqual(
                [row["curation_status"] for row in migrated],
                ["confirmed", "needs_review"],
            )

    def test_admin_dropdown_has_only_human_labels_and_canonical_values(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "web/admin.html").read_text(encoding="utf-8")
        block = html.split('id="metadata-curation-status"', 1)[1].split("</select>", 1)[0]
        self.assertEqual(block.count("<option"), 2)
        self.assertIn('<option value="confirmed">Confirmed</option>', block)
        self.assertIn('<option value="needs_review">Needs review</option>', block)
        for legacy in ("corrected_by_admin", "manually_confirmed", "manually_added", "auto_imported"):
            self.assertNotIn(legacy, block)

    @staticmethod
    def _row(status):
        row = {column: "" for column in PAPERS_COLUMNS}
        row.update({"paper_id": f"paper:{status}", "title": "Title", "year": "2026", "curation_status": status})
        return row

    @staticmethod
    def _write_rows(path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=PAPERS_COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
