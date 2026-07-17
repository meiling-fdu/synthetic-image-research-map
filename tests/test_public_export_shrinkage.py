import json
import tempfile
import unittest
from pathlib import Path

from scripts.export_public_preview import PreviewExportError, enforce_export_baseline


class PublicExportShrinkageTests(unittest.TestCase):
    def write_baseline(self, directory: str, papers: int, maps: int) -> Path:
        path = Path(directory) / "baseline.json"
        path.write_text(json.dumps({
            "paper_records": papers,
            "map_records": maps,
        }), encoding="utf-8")
        return path

    def test_counts_at_or_above_baseline_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.write_baseline(directory, 488, 950)
            enforce_export_baseline(488, 950, baseline)
            enforce_export_baseline(500, 1000, baseline)

    def test_unapproved_shrinkage_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.write_baseline(directory, 488, 950)
            with self.assertRaisesRegex(PreviewExportError, "shrinkage guard"):
                enforce_export_baseline(395, 703, baseline)

    def test_explicit_approved_baseline_allows_reviewed_reduction(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.write_baseline(directory, 488, 950)
            approved = Path(directory) / "approved.json"
            approved.write_text(json.dumps({
                "paper_records": 395,
                "map_records": 703,
            }), encoding="utf-8")
            enforce_export_baseline(395, 703, baseline, approved)


if __name__ == "__main__":
    unittest.main()
