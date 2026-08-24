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
        cls.marker_helpers = (
            ROOT / "web" / "marker_size_helpers.js"
        ).read_text(encoding="utf-8")

    def test_renamed_public_filter_labels_and_title_case(self):
        for expected in (
            "Research Type",
            "Publication Type",
            "Publication Venue",
            "Record Version",
            "Institution Type",
            "Publication Year",
            "Filtered Records",
            "Institution Records",
            "Unique Papers",
            "Institution Records",
            "Unique Institutions",
        ):
            self.assertIn(expected, self.html)
        for removed in (
            "Entry type",
            "Paper Type",
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
            self.html.index('id="active-filter-bar"')
        ]
        ordered_ids = re.findall(r'<(?:input|select)[^>]+id="([^"]+)"', filter_grid)
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
            self.html.index('id="active-filter-bar"')
        ]
        groups = (
            "keyword-filter", "task-filter", "entry-type-filter",
            "venue-type-filter", "venue-filter", "country-filter",
            "institution-type-filter", "preprint-filter", "year-range",
        )
        for group in groups:
            marker = f'id="{group}"' if group != "year-range" else 'class="year-range"'
            self.assertIn(marker, filter_grid)

    def test_all_select_filters_use_one_custom_dropdown_controller(self):
        dropdown_ids = (
            "task-filter", "entry-type-filter", "venue-type-filter",
            "venue-filter", "country-filter", "institution-type-filter",
            "preprint-filter",
        )
        self.assertEqual(self.html.count("data-filter-dropdown"), len(dropdown_ids))
        initialization = self.app[
            self.app.index("filterDropdowns = ["):
            self.app.index("const chartTooltip")
        ]
        for dropdown_id in dropdown_ids:
            variable = {
                "task-filter": "taskFilter",
                "entry-type-filter": "entryTypeFilter",
                "venue-type-filter": "venueTypeFilter",
                "venue-filter": "venueFilter",
                "country-filter": "countryFilter",
                "institution-type-filter": "institutionTypeFilter",
                "preprint-filter": "preprintFilter",
            }[dropdown_id]
            self.assertIn(variable, initialization)
        self.assertIn("].map(createFilterDropdown)", initialization)
        self.assertIn('select.setAttribute("aria-hidden", "true")', self.app)
        self.assertIn("select.tabIndex = -1", self.app)

    def test_filtered_overview_distinguishes_all_four_data_units(self):
        overview = self.html[
            self.html.index('<div class="dataset-overview"'):
            self.html.index('<div class="map-status-row"')
        ]
        self.assertIn('aria-label="Filtered data overview"', overview)
        self.assertNotIn("Filtered Overview", overview)
        self.assertNotIn("<h2", overview)
        labels = re.findall(r"<dt>([^<]+)</dt>", overview)
        self.assertEqual(labels, [
            "Institution Records", "Unique Papers", "Unique Institutions", "Countries",
        ])
        self.assertIn('id="dataset-paper-count"', overview)
        self.assertIn("datasetPaperCount", self.app)
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
        self.assertIn(".sidebar .panel {\n  padding: 12px;", self.css)
        self.assertIn(".filter-grid {\n  display: grid;\n  gap: 8px;", self.css)
        self.assertIn(".filter-grid label {\n  gap: 4px;", self.css)
        self.assertIn('.filter-grid input:not([type="range"])', self.css)
        self.assertIn(".filter-dropdown-button {\n  display: flex;", self.css)
        self.assertIn("height: 35px", self.css)
        self.assertIn(".year-range-slider {\n  position: relative;\n  height: 24px;", self.css)
        self.assertIn("justify-content: space-between", self.css)
        self.assertIn(".dataset-overview > p {\n  margin: 0;", self.css)
        self.assertIn("flex: 0 1 280px", self.css)
        self.assertIn("@media (max-width: 1250px)", self.css)
        self.assertIn("@media (max-width: 820px)", self.css)
        self.assertNotIn("dataset-overview-heading", self.css)

    def test_header_uses_structural_logo_desktop_and_constrained_modes(self):
        header = self.css[
            self.css.index(".site-header {"):
            self.css.index(".header-repository-link {")
        ]
        self.assertIn('grid-template-areas: "hero statistics repository"', header)
        self.assertIn(".header-brand", header)
        self.assertIn(".header-logo", header)
        self.assertIn("grid-area: repository", header)
        statistics = self.css[
            self.css.index(".header-statistics {"):
            self.css.index(".header-chart {")
        ]
        self.assertIn("grid-area: statistics", statistics)
        self.assertIn(
            "grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr) minmax(0, 1fr)",
            statistics,
        )
        desktop = self.css.split("@media (min-width: 1200px)", 1)[1].split(
            "@media (max-width: 1250px)", 1
        )[0]
        self.assertIn('grid-template-areas: "hero statistics repository"', desktop)
        self.assertIn(
            "grid-template-columns: 406px minmax(0, 1fr) auto",
            desktop,
        )
        self.assertIn("height: 96px", header)
        self.assertIn("height: 100%", header)
        self.assertIn("object-fit: contain", header)
        self.assertIn("height: 112px", desktop)
        self.assertIn(
            "grid-template-columns: minmax(0, 0.9fr) "
            "minmax(0, 1.25fr) minmax(0, 1fr)",
            desktop,
        )
        self.assertNotIn("position: absolute", header)

    def test_public_controls_and_cards_use_consistent_spacing_rhythm(self):
        filter_grid = self.css[
            self.css.index(".filter-grid {"):self.css.index(".visually-hidden {")
        ]
        self.assertIn("gap: 8px", filter_grid)

        results_heading = self.css[
            self.css.index(".results-heading-row {"):
            self.css.index(".results-heading-group {")
        ]
        self.assertIn("gap: 8px 12px", results_heading)
        self.assertIn("margin-bottom: 8px", results_heading)

        result_card = self.css[
            self.css.index(".result-card {"):self.css.index(".result-title {")
        ]
        self.assertIn("padding: 12px", result_card)

        legend = self.css[
            self.css.index(".map-encoding-legend {"):
            self.css.index(".marker-size-examples {")
        ]
        self.assertIn("gap: 4px 16px", legend)
        self.assertIn("white-space: nowrap", legend)

    def test_logo_replaces_visible_title_and_duplicate_task_legend(self):
        project_name = "Synthetic Image Detection &amp; Attribution Landscape"
        logo = (
            ROOT / "web" / "assets"
            / "synthetic-image-detection-attribution-landscape-logo.png"
        )
        self.assertTrue(logo.is_file())
        self.assertIn(f'<h1 class="visually-hidden">{project_name}</h1>', self.html)
        self.assertIn(f'alt="{project_name}"', self.html)
        self.assertIn('class="header-logo"', self.html)
        self.assertIn('width="1149"', self.html)
        self.assertIn('height="393"', self.html)
        self.assertNotIn('class="task-legend"', self.html)
        self.assertNotIn(".task-legend", self.css)
        self.assertNotIn(".legend-dot", self.css)
        self.assertIn('class="map-encoding-legend"', self.html)

    def test_sort_is_in_filtered_records_header_not_filter_panel(self):
        filter_grid = self.html[
            self.html.index('<div class="filter-grid">'):
            self.html.index('id="active-filter-bar"')
        ]
        results_header = self.html[
            self.html.index('<div class="results-heading-row">'):
            self.html.index('<ol id="results-list"')
        ]
        self.assertNotIn('id="sort-control"', filter_grid)
        self.assertIn('id="sort-control"', results_header)
        self.assertIn("Sort By", results_header)
        self.assertLess(results_header.index("results-heading"), results_header.index("results-count"))
        self.assertLess(results_header.index("results-count"), results_header.index("results-view-toggle"))
        self.assertLess(results_header.index("results-count"), results_header.index("sort-control"))
        self.assertLess(results_header.index("sort-control"), results_header.index("export-csv"))

    def test_polished_controls_and_details_close_are_accessible(self):
        self.assertIn('aria-label="Close paper details"', self.html)
        self.assertIn('id="close-paper-details"', self.html)
        self.assertIn(">&times;</button>", self.html)
        self.assertIn(".paper-details-close {\n  display: grid;", self.css)
        self.assertIn("#reset-filters::before", self.css)
        self.assertIn('content: "↶"', self.css)

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

    def test_public_copy_uses_production_research_map_wording(self):
        for removed in (
            "static prototype",
            "Loading Public Preview Data",
            "Public Preview JSON",
            "Public Preview Papers JSON",
            "Data Notice and Credits",
        ):
            self.assertNotIn(removed, self.html)
        for removed in (
            "Unable to load public preview data.",
            "OpenAlex candidate",
            "Previewing ${visibleCount}",
            "preview paper details",
            "Unknown venue/source",
        ):
            self.assertNotIn(removed, self.app)
        self.assertIn("curated from source metadata and manual review", self.html)
        self.assertIn("Preliminary affiliations", self.app)

    def test_task_and_publication_labels_are_canonical(self):
        task_filter = self.html[
            self.html.index('<select id="task-filter"'):
            self.html.index("</select>", self.html.index('<select id="task-filter"'))
        ]
        for label in (
            "Detection",
            "Source Attribution",
            "Detection + Source Attribution",
        ):
            self.assertIn(label, task_filter)
            self.assertIn(f'"{label}"', self.app)
            self.assertIn(f'"{label}"', self.marker_helpers)
        self.assertNotIn("Detection and Source Attribution", task_filter)
        self.assertNotIn("Detection + attribution", self.app)
        self.assertIn("Publication Venue", self.html)
        self.assertIn("Publication Venue: A–Z", self.html)
        self.assertNotIn("Venue/Source: A–Z", self.html)
        self.assertIn("Unknown publication venue", self.app)
        self.assertIn('aria-label="Paper categories"', self.app)

    def test_map_and_result_count_labels_use_record_scope_consistently(self):
        self.assertIn("Filtered institution records represent paper–institution links", self.html)
        self.assertIn('resultsView === "papers" ? "unique paper" : "institution record"', self.app)
        self.assertEqual(self.app.count('recordLabel: "institution record"'), 2)
        self.assertIn("No records match the current filters.", self.app)
        self.assertIn('aria-label="Research Map"', self.html)

    def test_bottom_information_is_one_compact_production_panel(self):
        self.assertEqual(self.html.count('class="panel site-information"'), 1)
        self.assertIn("About, Methodology, and Scope", self.html)
        self.assertIn("Records and Mapping", self.html)
        self.assertIn("Explore and Report", self.html)
        self.assertNotIn("Data Notice and Credits", self.html)
        self.assertNotIn("methodology-panel", self.html)
        self.assertNotIn("project-links-content", self.html)
        self.assertNotIn("dataset-status-note", self.html)
        self.assertNotIn("dataset-switcher", self.html)

        for label, href in (
            ("Map Data JSON", "data/public_preview_map_data.json"),
            ("Paper Data JSON", "data/public_preview_papers.json"),
            ("Quality Report", "../docs/public_preview_report.md"),
            ("Data Methodology", "../docs/data_collection.md"),
        ):
            self.assertIn(f'href="{href}">{label}</a>', self.html)

    def test_obsolete_sample_and_preview_status_paths_are_removed(self):
        self.assertFalse((ROOT / "web" / "data" / "sample_map_data.json").exists())
        for removed in (
            "sample_map_data.json",
            "Fictional Sample",
            "fictional sample",
            "Uncurated Public Preview",
            "uncurated public preview record",
            "loadSampleFallback",
            "renderDatasetSwitcher",
        ):
            self.assertNotIn(removed, self.html)
            self.assertNotIn(removed, self.app)
        self.assertIn('requestedName === "openalex"', self.app)

    def test_footer_credits_link_all_named_sources_consistently(self):
        footer = self.html.split('<footer aria-label="Site credits">', 1)[1].split(
            "</footer>", 1
        )[0]
        links = re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', footer)
        self.assertEqual(
            links,
            [
                ("https://openalex.org/", "OpenAlex"),
                ("https://leafletjs.com/", "Leaflet"),
                (
                    "https://www.openstreetmap.org/copyright",
                    "© OpenStreetMap contributors",
                ),
                ("https://developers.openai.com/codex/", "Codex"),
                ("https://learn.chatgpt.com/", "ChatGPT"),
            ],
        )
        footer_css = self.css[
            self.css.index("footer {"):self.css.index("/* Core Leaflet layout")
        ]
        self.assertIn("flex-wrap: wrap", footer_css)
        self.assertIn("text-decoration: underline", footer_css)
        self.assertIn("overflow-wrap: anywhere", footer_css)


if __name__ == "__main__":
    unittest.main()
