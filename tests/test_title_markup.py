import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


class TitleMarkupTests(unittest.TestCase):
    def run_helper(self, titles):
        script = r"""
const helper = require(process.argv[1]);
const titles = JSON.parse(process.argv[2]);
process.stdout.write(JSON.stringify(titles.map((title) => ({
  html: helper.toHtml(title),
  plain: helper.plainText(title),
  search: helper.searchText(title),
  segments: helper.segments(title),
}))));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(ROOT / "web/title_markup.js"), json.dumps(titles)],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_supported_superscripts_and_plain_titles(self):
        normal, squared, cubed = self.run_helper([
            "A normal paper title",
            "M<sup>2</sup>EA: Detection",
            "D <sup>3</sup> QE: Detection",
        ])
        self.assertEqual(normal["html"], "A normal paper title")
        self.assertEqual(normal["plain"], "A normal paper title")
        self.assertEqual(squared["html"], "M<sup>2</sup>EA: Detection")
        self.assertEqual(squared["plain"], "M2EA: Detection")
        self.assertEqual(cubed["html"], "D <sup>3</sup> QE: Detection")
        self.assertEqual(cubed["plain"], "D 3 QE: Detection")

    def test_unknown_and_malformed_markup_remains_safe_text(self):
        unknown, malformed, nested = self.run_helper([
            'Paper <img src=x onerror="alert(1)"> title',
            "Broken <sup>2 title",
            "Safe <sup><script>alert(1)</script></sup>",
        ])
        self.assertIn("&lt;img", unknown["html"])
        self.assertNotIn("<img", unknown["html"])
        self.assertEqual(malformed["html"], "Broken &lt;sup&gt;2 title")
        self.assertEqual(
            nested["html"],
            "Safe <sup>&lt;script&gt;alert(1)&lt;/script&gt;</sup>",
        )

    def test_plain_search_forms_match_superscript_titles(self):
        squared, cubed = self.run_helper([
            "M<sup>2</sup>EA: Detection",
            "D <sup>3</sup> QE: Detection",
        ])
        self.assertIn("m2ea", squared["search"].lower())
        self.assertIn("d3qe", cubed["search"].lower())

    def test_public_and_admin_use_shared_safe_renderer(self):
        public = (ROOT / "web/app.js").read_text(encoding="utf-8")
        admin = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        self.assertIn("TitleMarkup.toHtml", public)
        self.assertIn("TitleMarkup.searchText", public)
        self.assertIn("TitleMarkup.render", admin)
        self.assertIn("paperTitleSearchText", admin)
        self.assertNotIn("${escapeHtml(recordTitle(record))}</h3>", public)


if __name__ == "__main__":
    unittest.main()
