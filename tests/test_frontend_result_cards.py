import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


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

    def test_titles_are_accessibly_named_and_use_a_two_line_preview(self):
        self.assertIn('aria-labelledby="${cardId}"', self.app)
        self.assertIn('id="${cardId}"', self.app)
        self.assertIn("result-card-title-${resultsView}-${index}", self.app)
        result_title = self.css.split(".result-title {", 1)[1].split("}", 1)[0]
        self.assertIn("overflow-wrap: anywhere", result_title)
        self.assertIn("-webkit-line-clamp: 2", result_title)
        self.assertIn("overflow: hidden", result_title)

    def test_author_order_object_safety_and_accessible_expansion(self):
        authors = self.function("resultAuthors", "institutionResultContent")
        self.assertIn("PaperDetailsHelpers.renderPaperAuthorItems", authors)
        self.assertIn("visibleAuthors", authors)
        self.assertIn("overflowAuthors", authors)
        self.assertIn("visibleLimit", authors)
        self.assertIn("Authors at this institution", self.app)
        self.assertIn("Paper authors", self.app)
        self.assertIn('closest(".paper-authors-toggle")', self.app)
        self.assertIn('setAttribute("aria-expanded"', self.app)
        self.assertIn('aria-controls="${regionId}"', authors)
        self.assertNotIn("[object Object]", authors)

    def test_unique_paper_cards_reuse_author_affiliation_numbers(self):
        paper = self.function("paperResultContent", "renderResults")
        authors = self.function("resultAuthors", "institutionResultContent")
        self.assertIn("resultAuthors(normalizedRecord.authors", paper)
        self.assertIn("renderPaperAuthorItems", authors)
        self.assertIn("author-affiliation-numbers", (
            ROOT / "web" / "paper_details_helpers.js"
        ).read_text(encoding="utf-8"))

    def test_current_public_preview_record_matches_details_and_card_markers(self):
        preview = json.loads((
            ROOT / "web" / "data" / "public_preview_papers.json"
        ).read_text(encoding="utf-8"))
        title = (
            '"That\'s another doom I haven\'t thought about": A User Study on '
            "AI Labels as a Safeguard Against Image-Based Misinformation"
        )
        record = next(
            item for item in preview["records"] if item["title"] == title
        )
        helper = ROOT / "web" / "paper_details_helpers.js"
        script = r"""
const helpers = require(process.argv[1]);
const record = JSON.parse(process.argv[2]);
const escapeHtml = (value) => String(value);
process.stdout.write(JSON.stringify({
  cardItems: helpers.renderPaperAuthorItems(record, escapeHtml),
  detailsHtml: helpers.renderPaperAuthors(record, escapeHtml),
}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper), json.dumps(record)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)

        self.assertEqual(
            [affiliation["index"] for affiliation in record["affiliations"]],
            [1, 2, 3, 4, 5],
        )
        expected = {
            author["name"]: ",".join(map(str, author["affiliation_indices"]))
            for author in record["authors"]
        }
        for author_name, numbers in expected.items():
            marker = f'>{numbers}</sup>'
            self.assertTrue(
                any(author_name in item and marker in item for item in rendered["cardItems"])
            )
            self.assertIn(author_name, rendered["detailsHtml"])
            self.assertIn(marker, rendered["detailsHtml"])

    def test_mapping_assets_share_a_current_cache_key(self):
        versions = {
            asset: self.html.split(f'{asset}?v=', 1)[1].split('"', 1)[0]
            for asset in ("style.css", "paper_details_helpers.js", "app.js")
        }
        self.assertEqual(len(set(versions.values())), 1)

    def test_shared_author_items_preserve_mappings_across_visibility_slices(self):
        helper = ROOT / "web" / "paper_details_helpers.js"
        script = r"""
const helpers = require(process.argv[1]);
const escapeHtml = (value) => String(value);
const authors = [
  {name: "One", affiliation_indices: [1]},
  {name: "Shared", affiliation_indices: [1, 2, 2]},
  {name: "Unmapped", affiliation_indices: []},
  {name: "Overflow", affiliation_indices: [10]},
];
const items = helpers.renderPaperAuthorItems({authors}, escapeHtml);
process.stdout.write(JSON.stringify({items, collapsed: items.slice(0, 2), expanded: items}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)
        self.assertEqual(rendered["collapsed"], rendered["expanded"][:2])
        self.assertIn(">1,2</sup>", rendered["items"][1])
        self.assertNotIn("<sup", rendered["items"][2])
        self.assertIn(">10</sup>", rendered["items"][3])

    def test_institution_record_renderer_does_not_add_numbering(self):
        institution = self.function(
            "institutionResultContent", "uniquePaperInstitutions"
        )
        self.assertNotIn("result-institution-number", institution)

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
        self.assertIn('`${cardId}-authors`, 4', institution)

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
        self.assertIn('aria-label="Paper institutions"', institutions)
        self.assertIn("affiliation.number", institutions)
        self.assertIn('aria-label="Institution ${escapeHtml(affiliation.number)}"', institutions)
        paper = self.function("paperResultContent", "renderResults")
        self.assertIn('`${cardId}-authors`, 4', paper)
        self.assertIn('`${cardId}-institutions`, 3', paper)

    def test_grid_uses_content_sized_rows_without_stretching_shorter_cards(self):
        results_list = self.css.split(".results-list {", 1)[1].split("}", 1)[0]
        self.assertIn("align-items: start", results_list)
        self.assertNotIn("align-items: stretch", results_list)
        self.assertNotIn("grid-auto-rows", results_list)
        item = self.css.split(".result-item {", 1)[1].split("}", 1)[0]
        self.assertIn("align-self: start", item)
        self.assertNotIn("align-self: stretch", item)
        self.assertNotIn("height:", item)
        card = self.css.split(".result-card {", 1)[1].split("}", 1)[0]
        self.assertNotIn("height:", card)
        self.assertNotIn("overflow: hidden", card)
        self.assertNotIn("--result-card-height", self.css)

    def test_adaptive_content_and_metadata_follow_natural_flow(self):
        adaptive = self.css.split(".result-card-adaptive {", 1)[1].split("}", 1)[0]
        self.assertIn("min-width: 0", adaptive)
        self.assertNotIn("flex:", adaptive)
        self.assertNotIn("overflow:", adaptive)
        secondary = self.css.split(".result-secondary {", 1)[1].split("}", 1)[0]
        self.assertNotIn("margin-top: auto", secondary)
        self.assertNotIn("flex:", secondary)
        self.assertNotIn("max-height: 78px", self.css)
        self.assertNotIn(".result-authors.is-expanded", self.css)
        self.assertNotIn(".result-paper-institutions.is-expanded", self.css)

    def test_mobile_keeps_natural_cards_in_a_single_column(self):
        mobile = self.css.split("@media (max-width: 540px) {", 1)[1]
        self.assertIn(
            ".results-list {\n    grid-template-columns: 1fr;\n  }",
            mobile,
        )
        self.assertNotIn("grid-auto-rows", mobile)
        self.assertNotIn("result-card-height", mobile)

    def test_render_does_not_apply_stale_fixed_height_view_classes(self):
        render = self.function("renderResults", "selectResultsView")
        self.assertNotIn("results-list-institutions", render)
        self.assertNotIn("results-list-papers", render)
        self.assertNotIn("result-card-height", self.app)

    def test_expansion_uses_natural_growth_and_accessible_controls(self):
        self.assertIn("overflow.hidden = isExpanded", self.app)
        self.assertIn('aria-controls="${regionId}"', self.app)
        self.assertNotIn("style.height", self.app)
        self.assertNotIn('toggleAttribute("tabindex"', self.app)

    def test_collapsed_overflow_content_is_not_forced_visible_by_card_css(self):
        hidden_overflow = self.css.split(
            ".result-institutions-overflow[hidden],", 1
        )[1].split("}", 1)[0]
        self.assertIn(".paper-authors-overflow[hidden]", hidden_overflow)
        self.assertIn("display: none", hidden_overflow)

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
        self.assertIn("text-overflow: ellipsis", card_css)
        self.assertIn("white-space: nowrap", card_css)


if __name__ == "__main__":
    unittest.main()
