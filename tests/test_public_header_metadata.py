import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import refresh_public_preview
from scripts.stamp_public_preview import TIMESTAMP_FIELD, stamp_previews


ROOT = Path(__file__).resolve().parent.parent


class PublicHeaderMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web/style.css").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "web/app.js").read_text(encoding="utf-8")

    def test_visible_title_and_maintainer_copy(self):
        self.assertIn("<h1>Synthetic Image Detection &amp; Attribution Map</h1>", self.html)
        self.assertIn("Maintained by Meiling Li", self.html)

    def test_date_is_formatted_from_generated_metadata(self):
        self.assertIn("metadata.public_preview_generated_at", self.javascript)
        self.assertIn('month: "long"', self.javascript)
        self.assertIn('timeZone: "UTC"', self.javascript)
        self.assertIn("`Data updated: ${formattedDate}`", self.javascript)
        self.assertNotIn("13 July 2026", self.html)
        self.assertNotIn("13 July 2026", self.javascript)

    def test_missing_or_invalid_timestamp_hides_date(self):
        self.assertIn("element.hidden = !formattedDate", self.javascript)
        self.assertIn('element.textContent = formattedDate ? `Data updated: ${formattedDate}` : ""', self.javascript)
        self.assertIn('Number.isNaN(date.getTime())', self.javascript)

    def test_responsive_repository_block_keeps_valid_grid_placement(self):
        self.assertIn(".header-repository-block {", self.css)
        mobile = self.css.split("@media (max-width: 540px)", 1)[1]
        self.assertIn(".header-repository-block", mobile)
        self.assertIn("grid-row: 2", mobile)
        self.assertIn(".header-statistics", mobile)
        self.assertIn("grid-row: 3", mobile)

    def test_stamp_is_additive_and_uses_same_success_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("map.json", "papers.json")]
            for index, path in enumerate(paths):
                path.write_text(json.dumps({"metadata": {"kind": index}, "records": [{"id": index}]}))
            stamp_previews(paths, "2026-07-13T10:00:00Z")
            payloads = [json.loads(path.read_text()) for path in paths]
            self.assertTrue(all(payload["metadata"][TIMESTAMP_FIELD] == "2026-07-13T10:00:00Z" for payload in payloads))
            self.assertEqual(payloads[0]["records"], [{"id": 0}])

    def test_failed_refresh_does_not_run_success_stamp(self):
        steps = [refresh_public_preview.RefreshStep(1, "Validate public preview", ["validate"])]
        with mock.patch.object(
            refresh_public_preview.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(["validate"], 1),
        ) as run:
            self.assertEqual(refresh_public_preview.execute_steps(steps), 1)
        self.assertEqual(run.call_count, 1)
        self.assertNotIn("stamp_public_preview.py", " ".join(run.call_args.args[0]))


if __name__ == "__main__":
    unittest.main()
