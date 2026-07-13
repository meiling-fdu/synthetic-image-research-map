import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class AdminInstitutionQueueLifecycleFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "web/admin.js").read_text(encoding="utf-8")

    def test_cleanup_list_defensively_renders_only_open_records(self):
        renderer = self.javascript[
            self.javascript.index("function renderInstitutionAudit()"):
            self.javascript.index("function selectedInstitutionCases()")
        ]
        self.assertIn('if (row.status !== "open") return false', renderer)
        self.assertIn("No actionable open institution findings", renderer)
        self.assertNotIn('institution-audit-status', self.html)

    def test_archived_findings_are_collapsed_and_read_only(self):
        self.assertIn(
            '<details class="archived-findings" id="institution-archived-findings" hidden>',
            self.html,
        )
        self.assertIn("Archived findings", self.html)
        self.assertIn("read-only and never actionable", self.html)
        self.assertIn('audit.archived_records || []', self.javascript)
        self.assertIn('elements["institution-archived-findings"].open = false', self.javascript)
        self.assertIn('if (item.status !== "open")', self.javascript)
        self.assertIn("no cleanup actions available", self.javascript)


if __name__ == "__main__":
    unittest.main()
