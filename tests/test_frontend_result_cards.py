import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontendResultCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

    def function(self, name, next_name):
        return self.app.split(f"function {name}", 1)[1].split(
            f"\nfunction {next_name}", 1
        )[0]

    def test_views_use_distinct_entity_specific_card_renderers(self):
        institution = self.function(
            "institutionResultContent", "uniquePaperInstitutions"
        )
        paper = self.function("paperResultContent", "renderResults")
        render = self.function("renderResults", "selectResultsView")
        self.assertIn("result-card-institution", institution)
        self.assertIn("Institution record", institution)
        self.assertIn("result-card-paper", paper)
        self.assertIn("Unique paper", paper)
        self.assertIn("institutionResultContent(record, relatedEntries, cardId)", render)
        self.assertIn("paperResultContent(record, relatedEntries, cardId)", render)
        self.assertIn(": visibleRecords", render)
        self.assertIn("paperListRecordsForDisplay(visiblePaperRecords)", render)

    def test_titles_wrap_fully_and_cards_have_accessible_names(self):
        self.assertIn('aria-labelledby="${cardId}"', self.app)
        self.assertIn('id="${cardId}"', self.app)
        self.assertIn("result-card-title-${resultsView}-${index}", self.app)
        result_title = self.css.split(".result-title {", 1)[1].split("}", 1)[0]
        self.assertIn("overflow-wrap: anywhere", result_title)
        self.assertNotIn("text-overflow", result_title)
        self.assertNotIn("white-space: nowrap", result_title)

    def test_author_order_object_safety_and_accessible_expansion(self):
        authors = self.function("resultAuthors", "institutionResultContent")
        self.assertIn("authors.map((name) => ({ name }))", authors)
        self.assertIn("PaperDetailsHelpers.renderPaperAuthors", authors)
        self.assertIn("visibleLimit", authors)
        self.assertIn("Authors at this institution", self.app)
        self.assertIn("Paper authors", self.app)
        self.assertIn('closest(".paper-authors-toggle")', self.app)
        self.assertIn('setAttribute("aria-expanded"', self.app)
        self.assertNotIn("[object Object]", authors)

    def test_institution_cards_preserve_scoped_mappings(self):
        institution = self.function(
            "institutionResultContent", "uniquePaperInstitutions"
        )
        self.assertIn("institution?.authors?.length", institution)
        self.assertIn("recordInstitutionAuthors(record)", institution)
        self.assertIn("recordAuthors(normalizedRecord)", institution)
        self.assertIn("institutionFilterButtonHtml", institution)
        self.assertIn("recordLocation(record)", institution)
        self.assertIn("institutionTypeLabel(institutionType)", institution)

    def test_unique_papers_group_all_canonical_institutions(self):
        institutions = self.function("resultInstitutions", "paperResultContent")
        unique = self.function("uniquePaperInstitutions", "resultInstitutions")
        self.assertIn("uniquePaperInstitutions(affiliations)", institutions)
        self.assertIn("institutionIdentity", unique)
        self.assertIn("uniqueAffiliations.length", institutions)
        self.assertIn("result-institutions-overflow", institutions)
        self.assertIn('aria-expanded="false"', institutions)
        self.assertIn("Show all institutions", institutions)
        self.assertIn("Show fewer institutions", self.app)

    def test_publication_row_badges_and_links_are_nonduplicative(self):
        venue = self.function("resultVenueYear", "resultLinks")
        badges = self.function("resultBadges", "resultVenueYear")
        links = self.function("resultLinks", "resultAuthors")
        self.assertIn("paperDetailsPublication(record)", venue)
        self.assertIn("publicationYear(record)", venue)
        self.assertIn('join(" ")', venue)
        self.assertIn("/^unknown venue\\/source$/i", venue)
        self.assertIn('year !== null', venue)
        self.assertNotIn("venueDisplayHtml(record)", venue)
        self.assertNotIn("venue-type-badge", venue)
        self.assertIn("popup-badges result-badges", badges)
        self.assertIn("popup-badge popup-task task-", badges)
        self.assertIn("entry-type-badge", badges)
        self.assertNotIn("publication-type-badge", badges)
        self.assertNotIn("institution-type-badge", badges)
        self.assertNotIn("arXiv version", badges)
        self.assertNotIn("Preliminary affiliations", badges)
        self.assertNotIn("resolutionConfidence", badges)
        self.assertNotIn("reviewStatus", badges)
        self.assertIn("paperExternalLinks(record)", links)
        self.assertIn("paper-details-links result-links", links)

    def test_institution_type_is_only_in_the_scoped_institution_block(self):
        institution = self.function(
            "institutionResultContent", "uniquePaperInstitutions"
        )
        self.assertEqual(institution.count("institutionTypeLabel(institutionType)"), 1)
        self.assertIn("${resultBadges(record)}", institution)
        self.assertNotIn("resultBadges(record, true)", institution)

    def test_sort_control_uses_compact_sizing_without_changing_options(self):
        self.assertIn(
            '<select id="sort-control" class="sort-control-compact" disabled>',
            self.html,
        )
        select_css = self.css.split(".sort-control-label select {", 1)[1].split(
            "}", 1
        )[0]
        self.assertIn("height: 32px", select_css)
        self.assertIn("min-height: 32px", select_css)
        self.assertIn("padding: 3px 28px 3px 8px", select_css)
        sort_options = self.html.split(
            '<select id="sort-control" class="sort-control-compact" disabled>', 1
        )[1].split("</select>", 1)[0]
        self.assertEqual(sort_options.count('<option value="'), 5)

    def test_counts_states_list_semantics_and_nested_controls(self):
        render = self.function("renderResults", "selectResultsView")
        self.assertIn('resultNoun = resultsView === "papers" ? "paper" : "record"', render)
        self.assertIn("displayedResults.length", render)
        self.assertIn("No matching ${resultNoun}s", render)
        self.assertIn('<ol id="results-list"', self.html)
        self.assertIn("Data unavailable", self.app)
        self.assertIn("Loading…", self.html)
        self.assertNotIn('tabindex="0"', render)
        self.assertIn(":is(a, button):focus-visible", self.css)

    def test_result_content_has_no_horizontal_overflow_patterns(self):
        card_css = self.css.split(".result-item {", 1)[1].split(
            ".results-empty", 1
        )[0]
        self.assertIn("min-width: 0", card_css)
        self.assertIn("overflow-wrap: anywhere", card_css)
        self.assertIn("flex-wrap: wrap", card_css)
        self.assertNotIn("text-overflow: ellipsis", card_css)


if __name__ == "__main__":
    unittest.main()
