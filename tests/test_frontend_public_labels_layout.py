import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendPublicLabelsLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")

    def test_renamed_public_filter_labels_and_title_case(self):
        for expected in (
            "Paper Type",
            "Publication Type",
            "Publication Venue",
            "Record Version",
            "Institution Type",
            "Publication Year",
            "Filtered Records",
            "Institution Records",
            "Unique Papers",
            "Map Records",
            "Paper Coverage",
            "Unique Institutions",
        ):
            self.assertIn(expected, self.html)
        for removed in (
            "Entry type",
            "Venue Type",
            "Version Status",
            "Institution type",
            "Publication year",
        ):
            self.assertNotIn(removed, self.html)
        self.assertNotIn("<h2 id=\"results-heading\">Filtered records</h2>", self.html)
        self.assertNotIn(">Institution records</button>", self.html)
        self.assertNotIn(">Unique papers</button>", self.html)
        self.assertNotRegex(self.html, r">All (?:Tasks|Paper Types|Publication Types|Venues|Countries|Institution Types|Records)<")
        self.assertEqual(self.html.count('<option value="all">All</option>'), 7)

    def test_record_version_is_independent_of_publication_type(self):
        self.assertIn('value="has-arxiv"', self.html)
        self.assertIn('value="no-arxiv"', self.html)
        self.assertNotIn('value="preprint-only"', self.html)
        self.assertNotIn('value="published"', self.html)
        matching = self.app[
            self.app.index("const selectedVersion = preprintFilter.value"):
            self.app.index("const year = publicationYear(record)")
        ]
        self.assertIn("hasArxivVersion(record)", matching)
        self.assertNotIn("isPreprintOnlyRecord(record)", matching)
        self.assertNotIn("hasPublishedVenue(record)", matching)

    def test_filter_order_places_publication_type_immediately_before_venue(self):
        filter_grid = self.html[
            self.html.index('<div class="filter-grid">'):
            self.html.index('<div id="active-institution-filter"')
        ]
        ordered_ids = re.findall(r'id="([^"]+)"', filter_grid)
        self.assertLess(
            ordered_ids.index("entry-type-filter"),
            ordered_ids.index("venue-type-filter"),
        )
        self.assertEqual(
            ordered_ids.index("venue-type-filter") + 1,
            ordered_ids.index("venue-filter"),
        )
        expected = [
            "keyword-filter", "task-filter", "entry-type-filter", "venue-type-filter",
            "venue-filter", "country-filter", "institution-type-filter", "preprint-filter",
            "min-year-filter", "max-year-filter",
        ]
        positions = [ordered_ids.index(identifier) for identifier in expected]
        self.assertEqual(positions, sorted(positions))

    def test_all_nine_filter_groups_remain_present(self):
        filter_grid = self.html[
            self.html.index('<div class="filter-grid">'):
            self.html.index('<div id="active-institution-filter"')
        ]
        groups = (
            "keyword-filter", "task-filter", "entry-type-filter",
            "venue-type-filter", "venue-filter", "country-combobox",
            "institution-type-filter", "preprint-filter", "year-range",
        )
        for group in groups:
            marker = f'id="{group}"' if group != "year-range" else 'class="year-range"'
            self.assertIn(marker, filter_grid)

    def test_filtered_overview_has_only_four_non_task_metrics(self):
        overview = self.html[
            self.html.index('<section class="panel dataset-overview"'):
            self.html.index('<section class="map-panel"')
        ]
        labels = re.findall(r"<dt>([^<]+)</dt>", overview)
        self.assertEqual(labels, [
            "Map Records", "Paper Coverage", "Unique Institutions", "Countries",
        ])
        for removed_id in (
            "dataset-detection-count", "dataset-attribution-count",
            "dataset-combined-count",
        ):
            self.assertNotIn(removed_id, overview)
            self.assertNotIn(removed_id, self.app)
        task_chart = self.app[
            self.app.index("function renderTaskChart"):
            self.app.index("function renderInstitutionChart")
        ]
        for task in (
            '"detection"', '"source_attribution"',
            '"detection_and_source_attribution"',
        ):
            self.assertIn(task, task_chart)

    def test_compact_filter_geometry_and_overview_responsive_grid(self):
        self.assertIn(".sidebar .panel {\n  padding: 12px 14px 13px;", self.css)
        self.assertIn(".filter-grid {\n  display: grid;\n  gap: 9px;", self.css)
        self.assertIn(".filter-grid label {\n  gap: 3px;", self.css)
        self.assertIn('.filter-grid input:not([type="range"])', self.css)
        self.assertIn(".country-combobox-button {\n  display: flex;", self.css)
        self.assertIn("height: 35px", self.css)
        self.assertIn(".year-range-slider {\n  position: relative;\n  height: 24px;", self.css)
        self.assertIn(
            "grid-template-columns: auto minmax(0, 1fr) minmax(190px, 280px)",
            self.css,
        )
        self.assertIn(".dataset-overview > p {\n  align-self: center;", self.css)
        self.assertIn("@media (max-width: 1100px)", self.css)
        self.assertIn("@media (max-width: 820px)", self.css)
        self.assertNotIn("dataset-overview-heading", self.css)

    def test_sort_is_in_filtered_records_header_not_filter_panel(self):
        filter_grid = self.html[
            self.html.index('<div class="filter-grid">'):
            self.html.index('<div id="active-institution-filter"')
        ]
        results_header = self.html[
            self.html.index('<div class="results-heading-row">'):
            self.html.index('<ol id="results-list"')
        ]
        self.assertNotIn('id="sort-control"', filter_grid)
        self.assertIn('id="sort-control"', results_header)
        self.assertIn("Sort By", results_header)
        self.assertLess(results_header.index("results-heading"), results_header.index("results-view-toggle"))
        self.assertLess(results_header.index("results-view-toggle"), results_header.index("results-count"))
        self.assertLess(results_header.index("results-count"), results_header.index("sort-control"))
        self.assertLess(results_header.index("sort-control"), results_header.index("export-csv"))

    def test_sort_option_capitalization_and_behavior_scope(self):
        for expected in (
            "Year: Newest First",
            "Year: Oldest First",
            "Title: A–Z",
            "Title: Z–A",
        ):
            self.assertIn(expected, self.html)
        matching = self.app[
            self.app.index("function recordMatchesActiveFilters"):
            self.app.index("\nfunction dimensionPaperCounts")
        ]
        render = self.app[
            self.app.index("function renderRecords()"):
            self.app.index("\nfunction configureYearRange")
        ]
        self.assertNotIn("sortControl", matching)
        self.assertIn("compareRecordsForSort(first, second, sortControl.value)", render)
        self.assertIn('sortMode === "title-desc"', self.app)

    def test_results_header_wraps_without_horizontal_overflow(self):
        self.assertIn("grid-template-columns: minmax(0, 1fr) auto minmax(0, auto)", self.css)
        self.assertIn("flex-wrap: wrap", self.css)
        self.assertIn("@media (max-width: 820px)", self.css)
        self.assertIn(".results-heading-row {\n    grid-template-columns: 1fr;", self.css)
        self.assertIn(".sort-control-label {\n    flex: 1 1 190px;", self.css)


if __name__ == "__main__":
    unittest.main()
