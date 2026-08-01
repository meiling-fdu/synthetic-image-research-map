import json
import re
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
        self.assertIn("${publicationMetadataBlock}", details)
        self.assertIn("paper-details-publication-type", self.app)
        self.assertIn("task-${escapeHtml(MarkerSizeHelpers.normalizeTaskLabel", details)
        self.assertIn("paper-details-affiliations", details)
        self.assertIn("affiliation.authors.map(escapeHtml).join", details)
        self.assertIn("overflow-wrap: anywhere", self.css)
        self.assertIn("white-space: normal", self.css)
        self.assertNotIn("text-overflow: ellipsis", self.css.split(
            ".paper-details-affiliations", 1
        )[1].split(".result-author-affiliations", 1)[0])

    def test_publication_metadata_and_content_follow_reading_order(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultBadges", 1)[0]
        title = details.index("paper-details-title")
        badges = details.index('class="popup-badges"')
        venue = details.index("${publicationMetadataBlock}")
        authors = details.index("paper-details-authors")
        affiliations = details.index("${affiliationsBlock}")
        links = details.index("${linksBlock}")
        self.assertLess(title, badges)
        self.assertLess(badges, venue)
        self.assertLess(venue, authors)
        self.assertLess(authors, affiliations)
        self.assertLess(affiliations, links)
        self.assertNotIn("venueDisplayHtml(record)", details)
        self.assertNotIn("venue-type-badge", details)
        self.assertIn("Publication type:", self.app)

    def test_only_primary_badges_remain_in_paper_details(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultBadges", 1)[0]
        self.assertIn("popup-task", details)
        self.assertNotIn("${publicationTypeBadge}", details)
        self.assertIn("${entryTypeBadge}", details)
        self.assertNotIn("arXiv version", details)
        self.assertNotIn("confidenceBadge", details)
        self.assertNotIn("affiliationBadge", details)
        self.assertNotIn("Preprint-only", details)

    def test_public_details_exclude_duplicate_and_curation_fields(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultBadges", 1)[0]
        for label in (
            "Location</dt>",
            "Current institution</dt>",
            "Resolution</dt>",
            "Resolution notes</dt>",
            "Needs review</dt>",
        ):
            self.assertNotIn(label, details)
        self.assertNotIn("<dt>Subtask</dt>", details)
        self.assertNotIn("moreDetails", details)

    def test_section_typography_and_removed_more_details(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultBadges", 1)[0]
        self.assertEqual(details.count('class="paper-details-section-heading"'), 3)
        title_css = self.css.split(".paper-details-title {", 1)[1].split("}", 1)[0]
        self.assertIn("text-align: justify", title_css)
        self.assertIn("text-align-last: left", title_css)
        self.assertNotIn("white-space: nowrap", title_css)
        self.assertNotIn("text-overflow", title_css)
        self.assertNotIn('class="paper-details-more-toggle"', details)
        self.assertNotIn('aria-controls="paper-details-more-content"', details)
        self.assertNotIn("if (moreDetailsToggle)", self.app)

    def test_publication_row_uses_public_label_before_venue_and_deduplicates(self):
        helper_source = (
            REPOSITORY / "web" / "paper_details_helpers.js"
        ).read_text(encoding="utf-8")
        for label in (
            "Conference", "Journal", "Workshop", "Preprint", "Book",
            "Book Chapter", "Thesis", "Report", "Position Paper",
            "Dataset Paper",
        ):
            self.assertIn(f'"{label}"', helper_source)
        self.assertIn("duplicatePrefix", helper_source)
        renderer = self.app.split("function paperDetailsPublicationHtml(record) {", 1)[1].split(
            "\nfunction paperDetailsHtml", 1
        )[0]
        self.assertLess(renderer.index("metadata.typeLabel"), renderer.index("metadata.venue"))
        self.assertLess(renderer.index("metadata.venue"), renderer.index("metadata.year"))

    def test_publication_metadata_all_missing_value_combinations(self):
        helper = REPOSITORY / "web" / "paper_details_helpers.js"
        app_path = REPOSITORY / "web" / "app.js"
        script = r"""
const fs = require("fs");
global.PaperDetailsHelpers = require(process.argv[1]);
global.venueDisplayLabel = (record) => record.venue || "";
global.escapeHtml = (value) => String(value)
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
const app = fs.readFileSync(process.argv[2], "utf8");
const start = app.indexOf("function paperDetailsPublication(record) {");
const end = app.indexOf("\nfunction paperDetailsHtml", start);
eval(app.slice(start, end));
const cases = [
  {key: "journal", record: {publication_type: "journal", venue: "Journal of Image and Graphics", year: 2026}},
  {key: "conference", record: {publication_type: "conference_paper", venue: "IEEE/CVF Conference on Computer Vision and Pattern Recognition", year: 2025}},
  {key: "bookChapter", record: {publication_type: "book_chapter", venue: "Artificial Intelligence and Society", year: 2024}},
  {key: "typeVenue", record: {publication_type: "journal", venue: "Venue"}},
  {key: "typeYear", record: {publication_type: "journal", year: 2026}},
  {key: "venueYear", record: {venue: "Venue", year: 2026}},
  {key: "typeOnly", record: {publication_type: "journal"}},
  {key: "venueOnly", record: {venue: "Venue"}},
  {key: "yearOnly", record: {year: 2026}},
  {key: "none", record: {}},
];
process.stdout.write(JSON.stringify(Object.fromEntries(
  cases.map(({key, record}) => [key, paperDetailsPublicationHtml(record)]),
)));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper), str(app_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)

        def visible_text(markup):
            without_hidden = re.sub(
                r'<span class="visually-hidden">.*?</span>', "", markup
            )
            return " ".join(re.sub(r"<[^>]+>", "", without_hidden).split())

        expected = {
            "journal": "Journal | Journal of Image and Graphics · 2026",
            "conference": "Conference | IEEE/CVF Conference on Computer Vision and Pattern Recognition · 2025",
            "bookChapter": "Book Chapter | Artificial Intelligence and Society · 2024",
            "typeVenue": "Journal | Venue",
            "typeYear": "Journal · 2026",
            "venueYear": "Venue · 2026",
            "typeOnly": "Journal",
            "venueOnly": "Venue",
            "yearOnly": "2026",
            "none": "",
        }
        self.assertEqual(
            {key: visible_text(value) for key, value in rendered.items()},
            expected,
        )
        for markup in rendered.values():
            self.assertNotIn("| |", visible_text(markup))
            self.assertNotIn("· ·", visible_text(markup))

    def test_narrow_panel_content_can_wrap_without_horizontal_overflow(self):
        content_css = self.css.split(".paper-details-content {", 1)[1].split("}", 1)[0]
        affiliations_css = self.css.split(
            ".paper-details-affiliations li {", 1
        )[1].split("}", 1)[0]
        self.assertIn("min-width: 0", content_css)
        self.assertIn("overflow-wrap: anywhere", content_css)
        self.assertIn("min-width: 0", affiliations_css)
        self.assertIn("overflow-wrap: anywhere", affiliations_css)
        self.assertIn("flex-wrap: wrap", self.css.split(
            ".paper-details-links {", 1
        )[1].split("}", 1)[0])

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
