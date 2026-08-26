import json
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node") or str(
    Path.home()
    / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
)


class InstitutionDisplayFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not Path(NODE).exists():
            raise unittest.SkipTest("node is not available")

    def run_helper(self, expression):
        script = (
            "const helper = require('./web/institution_display.js');"
            f"console.log(JSON.stringify({expression}));"
        )
        result = subprocess.run(
            [NODE, "-e", script], cwd=ROOT, check=True,
            text=True, capture_output=True,
        )
        return json.loads(result.stdout)

    def test_full_name_without_abbreviation(self):
        self.assertEqual(
            self.run_helper("helper.format('Technical University of Madrid', '')"),
            "Technical University of Madrid",
        )

    def test_full_name_precedes_abbreviation(self):
        self.assertEqual(
            self.run_helper("helper.format('Technical University of Madrid', 'UPM')"),
            "Technical University of Madrid (UPM)",
        )

    def test_preformatted_legacy_value_is_not_duplicated(self):
        self.assertEqual(
            self.run_helper("helper.format('Technical University of Madrid (UPM)', 'UPM')"),
            "Technical University of Madrid (UPM)",
        )

    def test_both_frontends_load_the_shared_helper(self):
        self.assertIn("institution_display.js", (ROOT / "web/index.html").read_text())
        self.assertIn("institution_display.js", (ROOT / "web/admin.html").read_text())
        self.assertIn(
            "return InstitutionDisplay.formatRecord(record);",
            (ROOT / "web/app.js").read_text(),
        )
        self.assertIn(
            "const institution = InstitutionDisplay.formatRecord(raw);",
            (ROOT / "web/app.js").read_text(),
        )
        self.assertIn(
            "return InstitutionDisplay.formatRecord(institution);",
            (ROOT / "web/admin.js").read_text(),
        )


if __name__ == "__main__":
    unittest.main()
