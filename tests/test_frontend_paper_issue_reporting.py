import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendPaperIssueReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.node = shutil.which("node")

    def run_node(self, source):
        if self.node is None:
            self.skipTest("Node.js is not on PATH")
        completed = subprocess.run(
            [self.node, "-e", source],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def report_url_helpers(self):
        start = self.app.index("function publicIssueText")
        end = self.app.index("\nfunction paperIssueContext", start)
        return (
            'const PAPER_ISSUE_URL = '
            '"https://github.com/meiling-fdu/synthetic-image-research-map/issues/new";\n'
            + self.app[start:end]
        )

    def test_generated_url_contains_encoded_stable_context_and_problem_choices(self):
        helpers = self.report_url_helpers()
        result = self.run_node(f"""
{helpers}
const report = paperIssueReportUrl({{
  paperId: 'doi:10.1000/a paper&part=2',
  title: 'Detection & attribution: "A/B"',
  deepLink: 'https://example.test/map?dataset=preview&paper=doi%3A10.1000%2Fa',
  publicationType: 'Conference', venue: 'CVPR & Workshops', year: 2025,
  researchTypes: ['Method', 'Dataset'], task: 'Detection',
  institutions: ['Example University', 'Research & Development Lab'],
  locations: ['Rome, Italy'],
}});
const parsed = new URL(report);
console.log(JSON.stringify({{
  report,
  originPath: parsed.origin + parsed.pathname,
  title: parsed.searchParams.get('title'),
  body: parsed.searchParams.get('body'),
}}));
""")
        self.assertEqual(
            result["originPath"],
            "https://github.com/meiling-fdu/synthetic-image-research-map/issues/new",
        )
        self.assertEqual(
            result["title"],
            'Paper metadata issue: Detection & attribution: "A/B"',
        )
        body = result["body"]
        self.assertIn("Stable ID: `doi:10.1000/a paper&part=2`", body)
        self.assertIn("Paper deep link: https://example.test/map?dataset=preview", body)
        self.assertIn("Publication venue: CVPR & Workshops", body)
        for choice in (
            "Incorrect affiliation", "Incorrect location",
            "Incorrect publication metadata", "Duplicate record",
            "Missing information",
        ):
            self.assertIn(f"- [ ] {choice}", body)
        self.assertIn("%26", result["report"])
        self.assertIn("%2F", result["report"])

    def test_missing_metadata_is_human_readable_and_never_serializes_undefined(self):
        helpers = self.report_url_helpers()
        result = self.run_node(f"""
{helpers}
const parsed = new URL(paperIssueReportUrl({{paperId: 'openalex:W1'}}));
console.log(JSON.stringify({{
  title: parsed.searchParams.get('title'),
  body: parsed.searchParams.get('body'),
}}));
""")
        self.assertEqual(result["title"], "Paper metadata issue: Unknown title")
        self.assertNotIn("undefined", result["body"])
        self.assertNotIn("null", result["body"])
        self.assertGreaterEqual(result["body"].count("Not available"), 8)

    def test_context_uses_only_public_display_metadata(self):
        start = self.app.index("function paperIssueContext")
        end = self.app.index("\nfunction appendCopyPaperLinkAction", start)
        context_helper = self.app[start:end]
        result = self.run_node(f"""
function paperDetailsPublication(record) {{
  return {{typeLabel: record.publication_type, venue: record.venue}};
}}
function recordInstitution(record) {{ return record.institution || ''; }}
function recordLocation(record) {{ return record.location_display || ''; }}
function recordTitle(record) {{ return record.title; }}
function publicationYear(record) {{ return record.publication_year ?? null; }}
function getPaperCategories(record) {{ return record.paper_categories || []; }}
function getEntryTypeLabel(value) {{ return value === 'method' ? 'Method' : value; }}
function formatPublicTask() {{ return 'Detection'; }}
{context_helper}
const context = paperIssueContext({{
  title: 'Public title', publication_type: 'Journal', venue: 'Public Venue',
  publication_year: 2024, paper_categories: ['method'],
  aggregated_institutions: ['Public University'],
  aggregated_locations: [{{location_display: 'Paris, France'}}],
  manual_review: true, provenance_sources: ['internal-source'],
  admin_notes: 'do not expose', mapping_fallback: true,
}}, [{{record: {{institution: 'Public Lab', location_display: 'Rome, Italy'}}}}],
  'doi:10.1000/public', 'https://example.test/?paper=public');
console.log(JSON.stringify(context));
""")
        self.assertEqual(result["title"], "Public title")
        self.assertEqual(result["publicationType"], "Journal")
        self.assertEqual(result["researchTypes"], ["Method"])
        self.assertEqual(
            result["institutions"], ["Public University", "Public Lab"]
        )
        self.assertEqual(result["locations"], ["Paris, France", "Rome, Italy"])
        serialized = json.dumps(result)
        for internal_value in ("manual_review", "internal-source", "admin_notes", "mapping_fallback"):
            self.assertNotIn(internal_value, serialized)

    def test_report_action_is_an_accessible_external_link_in_compact_action_group(self):
        action = self.app[
            self.app.index("function appendCopyPaperLinkAction"):
            self.app.index("\nfunction showCopyPaperLinkFeedback")
        ]
        self.assertIn('document.createElement("a")', action)
        self.assertIn('reportLink.textContent = "Report issue"', action)
        self.assertIn('reportLink.target = "_blank"', action)
        self.assertIn('reportLink.rel = "noopener noreferrer"', action)
        self.assertIn("opens in a new tab", action)
        self.assertIn("paperIssueReportUrl(paperIssueContext(", action)
        self.assertIn("requestedPaperIdentity\n    || (record ? paperIdentity(record)", action)
        self.assertIn("if (requestedPaperIdentity) container.append", action)
        self.assertIn(".paper-details-share-actions", self.css)
        self.assertIn(".report-paper-issue-link", self.css)
        self.assertIn("min-height: 38px", self.css)
        self.assertIn("flex-wrap: wrap", self.css)

    def test_generic_github_issues_link_remains_available(self):
        self.assertIn(
            'href="https://github.com/meiling-fdu/synthetic-image-research-map/issues"',
            self.html,
        )
        self.assertIn(">GitHub Issues</a>", self.html)


if __name__ == "__main__":
    unittest.main()
