import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.review_decisions import upsert_review_decision


class ReviewDecisionIdempotenceTests(unittest.TestCase):
    def test_identical_resolution_does_not_rewrite_timestamp_or_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review_decisions.csv"
            draft = {
                "review_queue": "marker_blocker",
                "target_type": "paper",
                "title": "Paper",
                "year": "2024",
                "doi": "10.1000/paper",
                "institution": "One",
                "action": "exclude_wrong_mapping",
                "review_note": "Checked source evidence.",
            }
            with patch("scripts.review_decisions._now", return_value="2026-01-01T00:00:00Z"):
                first = upsert_review_decision(draft, path)
            before = path.read_bytes()
            with patch("scripts.review_decisions._now", return_value="2026-01-02T00:00:00Z"):
                second = upsert_review_decision(draft, path)
            self.assertEqual(first, second)
            self.assertEqual(path.read_bytes(), before)
            with path.open(encoding="utf-8", newline="") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 1)


if __name__ == "__main__":
    unittest.main()
