import json
import subprocess
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


class FrontendPaperDetailsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (REPOSITORY / "web/app.js").read_text()
        cls.css = (REPOSITORY / "web/style.css").read_text()
        cls.html = (REPOSITORY / "web/index.html").read_text()

    def test_author_names_order_and_disclosure_markup(self):
        helper = REPOSITORY / "web/paper_details_helpers.js"
        script = r"""
const helpers = require(process.argv[1]);
const escapeHtml = (value) => String(value)
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
const authors = [
  {name: "First Author"},
  {display_name: "Second Author"},
  "Third Author",
  {author: "Fourth Author"},
];
const html = helpers.renderPaperAuthors({authors}, escapeHtml, null, 2);
process.stdout.write(JSON.stringify({html}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)["html"]
        self.assertNotIn("[object Object]", rendered)
        self.assertLess(rendered.index("First Author"), rendered.index("Second Author"))
        self.assertLess(rendered.index("Second Author"), rendered.index("Third Author"))
        self.assertIn('class="paper-authors-overflow" hidden', rendered)
        self.assertIn('aria-expanded="false"', rendered)
        self.assertIn("Show all authors", rendered)

    def test_title_affiliations_badges_and_links_are_wrap_safe(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultContent", 1)[0]
        self.assertLess(
            details.index("paper-details-title"),
            details.index('class="popup-badges"'),
        )
        self.assertIn("publication-type-badge", details)
        self.assertIn("task-${escapeHtml(MarkerSizeHelpers.normalizeTaskLabel", details)
        self.assertIn("paper-details-affiliations", details)
        self.assertIn("affiliation.authors.map(escapeHtml).join", details)
        self.assertIn("overflow-wrap: anywhere", self.css)
        self.assertIn("white-space: normal", self.css)
        self.assertNotIn("text-overflow: ellipsis", self.css.split(
            ".paper-details-affiliations", 1
        )[1].split(".result-author-affiliations", 1)[0])

    def test_external_links_require_valid_urls_and_have_safe_labels(self):
        links = self.app.split(
            "function paperExternalLinks(record) {", 1
        )[1].split("\nfunction escapeCsvValue", 1)[0]
        external = self.app.split(
            "function externalLink(url, label) {", 1
        )[1].split("\nfunction normalizedDoi", 1)[0]
        self.assertIn("deduplicatePaperLinks", links)
        for label in ("Project", "Code", "Dataset"):
            self.assertIn(f'label: "{label}"', links)
        self.assertIn("safeHttpUrl(url)", external)
        self.assertIn("opens in a new tab", external)
        self.assertIn('rel="noopener noreferrer"', external)

    def test_accessible_region_close_and_author_toggle_behavior(self):
        self.assertIn('role="region"', self.html)
        self.assertIn('aria-label="Close paper details"', self.html)
        self.assertIn('"aria-label",\n    "Close paper details"', self.app)
        self.assertIn('closest(".paper-authors-toggle")', self.app)
        self.assertIn('setAttribute("aria-expanded", String(!isExpanded))', self.app)
        self.assertIn('"Show fewer authors"', self.app)

    def test_existing_pin_hover_and_filtered_selection_guards_remain(self):
        self.assertIn(
            "const detailSelection = interactionState.pinned || interactionState.hovered",
            self.app,
        )
        clear_hover = self.app.split(
            "function clearHoverPreview(marker, event = null) {", 1
        )[1].split("\nfunction pinPaper", 1)[0]
        self.assertNotIn("interactionState.pinned = null", clear_hover)
        render = self.app.split("function renderRecords() {", 1)[1].split(
            "\nfunction configureYearRange()", 1
        )[0]
        self.assertIn("interactionState.pinned = null", render)
        self.assertIn("interactionState.pinnedMarkerId = null", render)
        self.assertIn("clearPinnedSelection()", self.app)


if __name__ == "__main__":
    unittest.main()
