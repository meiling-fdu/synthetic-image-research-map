import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]


class FrontendChartAndInstitutionFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (REPOSITORY / "web" / "app.js").read_text()
        cls.css = (REPOSITORY / "web" / "style.css").read_text()
        cls.html = (REPOSITORY / "web" / "index.html").read_text()

    def test_all_summary_charts_are_static(self):
        chart_source = self.app[
            self.app.index("function renderTaskChart"):
            self.app.index("function renderHeaderStatistics")
        ]
        for interactive_text in (
            "<button", "aria-pressed", "data-chart-task",
            "data-chart-institution", "data-chart-year",
            "activateChartFilter",
        ):
            self.assertNotIn(interactive_text, chart_source)
        self.assertIn('<span class="task-chart-segment"', chart_source)
        self.assertIn('<div class="institution-chart-row"', chart_source)
        self.assertIn('<div class="year-chart-item"', chart_source)

    def test_top_institutions_retains_compact_static_bar_structure(self):
        self.assertIn(
            '<div class="institution-chart-label"><span class="institution-chart-fill"',
            self.app,
        )
        self.assertIn('<span class="institution-chart-count">', self.app)
        self.assertIn("grid-template-rows: repeat(5, 1fr)", self.css)
        self.assertIn("grid-auto-flow: column", self.css)
        self.assertNotIn(".institution-chart-row.is-selected", self.css)

    def test_exact_institution_filter_is_separate_from_keyword_filter(self):
        matching = self.app[
            self.app.index("function recordMatchesActiveFilters"):
            self.app.index("function normalizedSetSize")
        ]
        self.assertIn("recordInstitutionIdentities(record).has(activeInstitutionFilter.identity)", matching)
        self.assertNotIn("keywordFilter.value =", self.app[
            self.app.index("function applyInstitutionFilter"):
            self.app.index("function renderHeaderStatistics")
        ])
        self.assertIn("data-institution-filter", self.app)
        self.assertIn("institution_id: affiliation.institutionId", self.app)

    def test_affiliation_links_chip_and_reset_are_accessible(self):
        self.assertIn('aria-label="Filter by institution', self.app)
        self.assertIn("active-institution-filter", self.html)
        self.assertIn("data-clear-institution-filter", self.app)
        self.assertIn("activeInstitutionFilter = null", self.app)
        self.assertIn(".active-filter-chip", self.css)
        self.assertIn("button.institution-filter-link", self.css)

    def test_filter_uses_shared_record_and_paper_pipeline(self):
        self.assertIn(".filter((record) => recordMatchesActiveFilters(record, keywordTerms))", self.app)
        self.assertIn("updateDatasetStatistics(visibleRecords, visiblePaperRecords)", self.app)
        self.assertIn("renderHeaderStatistics(visibleRecords, visiblePaperRecords)", self.app)
        self.assertIn("renderResults(visibleRecords, visiblePaperRecords)", self.app)

    def test_responsive_dimensions_and_asset_versions_are_preserved(self):
        self.assertIn("height: 76px", self.css)
        self.assertIn("min-width: 0", self.css)
        self.assertIn('style.css?v=20260713-exact-institution-filter', self.html)
        self.assertIn('app.js?v=20260713-exact-institution-filter', self.html)


if __name__ == "__main__":
    unittest.main()
