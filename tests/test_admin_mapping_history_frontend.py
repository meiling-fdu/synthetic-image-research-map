import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class AdminMappingHistoryFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "web/admin.js").read_text(encoding="utf-8")

    def test_historical_mappings_have_a_separate_collapsed_section(self):
        self.assertIn('<details class="historical-mappings" id="historical-mappings" hidden>', self.html)
        self.assertNotIn('<details class="historical-mappings" id="historical-mappings" open', self.html)
        self.assertIn('id="historical-mapping-table-body"', self.html)
        self.assertIn('elements["historical-mappings"].open = false', self.javascript)

    def test_only_current_statuses_render_in_current_mapping_table(self):
        renderer = self.javascript[
            self.javascript.index("function renderMappings(payload)"):
            self.javascript.index("function openMappingDialog")
        ]
        self.assertIn('new Set(["active", "needs_review"])', renderer)
        self.assertIn("currentMappings.forEach", renderer)
        self.assertIn("historicalMappings.forEach", renderer)
        self.assertNotIn("mappings.forEach", renderer)

    def test_audit_rows_are_unambiguously_non_current(self):
        for label in (
            "Excluded",
            "Replaced",
            "Retained for audit history",
            "Audit record — not a current affiliation",
        ):
            self.assertIn(label, self.javascript)
        self.assertIn("They are not current affiliations.", self.html)


if __name__ == "__main__":
    unittest.main()
