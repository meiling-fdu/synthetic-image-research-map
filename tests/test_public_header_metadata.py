import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import refresh_public_preview
from scripts.public_export_metadata import TIMESTAMP_FIELD


ROOT = Path(__file__).resolve().parent.parent


class PublicHeaderMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web/style.css").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "web/app.js").read_text(encoding="utf-8")
        cls.metadata_javascript = (ROOT / "web/public_metadata.js").read_text(encoding="utf-8")

    def test_visible_title_and_maintainer_copy(self):
        self.assertIn("<h1>Synthetic Image Detection &amp; Attribution Map</h1>", self.html)
        self.assertIn("Maintained by Meiling Li", self.html)

    def test_date_is_formatted_from_generated_metadata(self):
        self.assertIn("metadata.public_preview_generated_at", self.javascript)
        self.assertIn('month: "long"', self.metadata_javascript)
        self.assertIn('timeZone: "UTC"', self.metadata_javascript)
        self.assertIn("`Last updated: ${formattedDate}`", self.javascript)
        self.assertNotIn("13 July 2026", self.html)
        self.assertNotIn("13 July 2026", self.javascript)

    def test_missing_or_invalid_timestamp_hides_date(self):
        self.assertIn("element.hidden = !formattedDate", self.javascript)
        self.assertIn('element.textContent = formattedDate ? `Last updated: ${formattedDate}` : ""', self.javascript)
        self.assertIn('if (!match) return ""', self.metadata_javascript)

    def test_responsive_repository_block_keeps_valid_grid_placement(self):
        self.assertIn(".header-repository-block {", self.css)
        mobile = self.css.split("@media (max-width: 540px)", 1)[1]
        self.assertIn(".header-repository-block", mobile)
        self.assertIn("grid-row: 2", mobile)
        self.assertIn(".header-statistics", mobile)
        self.assertIn("grid-row: 3", mobile)

    def test_date_rendering_is_deterministic_across_timezones(self):
        node = Path(
            "/Users/meilinger/.cache/codex-runtimes/"
            "codex-primary-runtime/dependencies/node/bin/node"
        )
        if not node.exists():
            self.skipTest("Bundled Node.js is unavailable")
        script = (
            "const m=require('./web/public_metadata.js');"
            "process.stdout.write(m.formatPublicPreviewDate("
            "'2026-07-18T00:05:00Z'));"
        )
        values = []
        for timezone in ("UTC", "Pacific/Honolulu", "Pacific/Kiritimati"):
            environment = {**os.environ, "TZ": timezone}
            values.append(subprocess.run(
                (node, "-e", script),
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            ).stdout)
        self.assertEqual(values, ["18 July 2026"] * 3)

    def test_missing_or_invalid_timestamp_returns_empty_fallback(self):
        node = Path(
            "/Users/meilinger/.cache/codex-runtimes/"
            "codex-primary-runtime/dependencies/node/bin/node"
        )
        if not node.exists():
            self.skipTest("Bundled Node.js is unavailable")
        script = (
            "const m=require('./web/public_metadata.js');"
            "process.stdout.write(JSON.stringify(["
            "m.formatPublicPreviewDate(),"
            "m.formatPublicPreviewDate('not-a-date'),"
            "m.formatPublicPreviewDate('2026-02-30T10:00:00Z')"
            "]));"
        )
        result = subprocess.run(
            (node, "-e", script),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(json.loads(result.stdout), ["", "", ""])

    def test_failed_refresh_restores_export_outputs_and_does_not_stamp(self):
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
