import csv
import tempfile
import unittest
from pathlib import Path

from scripts.migrate_paper_categories import migrate
from scripts.curated_schema import PAPERS_COLUMNS
from scripts.paper_categories import (
    PaperCategoriesError,
    normalize_paper_categories,
    serialize_paper_categories,
)


class PaperCategoriesTests(unittest.TestCase):
    def test_legacy_scalar_and_multi_value_normalization(self):
        self.assertEqual(normalize_paper_categories("method", compatibility=True), ["method"])
        self.assertEqual(
            normalize_paper_categories(["survey", "dataset", "method", "dataset"]),
            ["method", "dataset", "survey"],
        )
        self.assertEqual(serialize_paper_categories(["benchmark", "dataset"]), "dataset;benchmark")

    def test_strict_mode_rejects_scalars_and_unknown_values(self):
        with self.assertRaises(PaperCategoriesError):
            normalize_paper_categories("method")
        with self.assertRaises(PaperCategoriesError):
            normalize_paper_categories(["tutorial"])
        with self.assertRaises(PaperCategoriesError):
            normalize_paper_categories(["method", ""])

    def test_missing_is_empty(self):
        self.assertEqual(normalize_paper_categories(None), [])
        self.assertEqual(normalize_paper_categories("", compatibility=True), [])

    def test_migration_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.csv"
            columns = ["entry_type" if column == "paper_categories" else column for column in PAPERS_COLUMNS]
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
                writer.writerow({"paper_id": "one", "entry_type": "dataset"})
            self.assertEqual(migrate(path), 1)
            self.assertEqual(migrate(path), 0)
            with path.open(newline="", encoding="utf-8") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["paper_categories"], "dataset")

    def test_admin_and_public_frontend_multi_value_contract(self):
        root = Path(__file__).parents[1]
        html = (root / "web" / "admin.html").read_text(encoding="utf-8")
        admin = (root / "web" / "admin.js").read_text(encoding="utf-8")
        public = (root / "web" / "app.js").read_text(encoding="utf-8")
        for category in ("method", "dataset", "benchmark", "survey", "analysis"):
            self.assertIn(f'name="paper_categories" value="{category}"', html)
        self.assertIn('draft.paper_categories = paperCategories', admin)
        self.assertIn('selectedEntryTypes.some((value) => getPaperCategories(record).includes(value))', public)
        self.assertIn('getPaperCategories(record).join(";")', public)

    def test_generated_json_uses_arrays_and_real_multi_category_paper(self):
        import json
        root = Path(__file__).parents[1]
        title = "Contrasting Deepfakes Diffusion via Contrastive Learning and Global-Local Similarities"
        for filename in ("public_preview_papers.json", "public_preview_map_data.json"):
            records = json.loads((root / "web" / "data" / filename).read_text(encoding="utf-8"))["records"]
            self.assertTrue(all(isinstance(record.get("paper_categories"), list) for record in records))
            self.assertFalse(any("entry_type" in record for record in records))
            matches = [record for record in records if record.get("title") == title]
            self.assertTrue(matches)
            self.assertTrue(all(record["paper_categories"] == ["method", "dataset"] for record in matches))


if __name__ == "__main__":
    unittest.main()
