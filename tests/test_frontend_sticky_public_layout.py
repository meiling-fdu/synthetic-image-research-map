import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendStickyPublicLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")

    def test_complete_header_summary_uses_one_sticky_container(self):
        self.assertEqual(self.html.count('<header class="site-header">'), 1)
        self.assertEqual(self.html.count('<div class="site-header-inner">'), 1)
        header = self.html[
            self.html.index('<header class="site-header">'):
            self.html.index('</header>')
        ]
        for content in (
            'class="header-brand"',
            "Unique Papers by Task",
            "Top Institutions by Unique Papers",
            "Unique Papers by Year",
            "GitHub Repository",
            'id="data-updated"',
        ):
            self.assertIn(content, header)

        sticky_rule = self.css.split(".site-header {", 1)[1].split("}", 1)[0]
        self.assertIn("position: sticky", sticky_rule)
        self.assertIn("top: 0", sticky_rule)
        self.assertIn("z-index: 1100", sticky_rule)
        self.assertIn("width: 100%", sticky_rule)
        self.assertIn("background: var(--header-surface)", sticky_rule)

        inner_rule = self.css.split(".site-header-inner {", 1)[1].split("}", 1)[0]
        self.assertIn("display: grid", inner_rule)
        self.assertIn('grid-template-areas: "hero statistics repository"', inner_rule)
        self.assertIn("background: transparent", inner_rule)

    def test_header_summary_keeps_existing_filter_render_pipeline(self):
        self.assertEqual(self.html.count('id="task-chart-content"'), 1)
        self.assertEqual(self.html.count('id="institution-chart-content"'), 1)
        self.assertEqual(self.html.count('id="year-chart-content"'), 1)
        apply_filters = self.app[
            self.app.index("function renderRecords"):
            self.app.index("function activeFilterCategoryCount")
        ]
        self.assertIn(
            "renderHeaderStatistics(visibleRecords, visiblePaperRecords)",
            apply_filters,
        )

    def test_scroll_offset_tracks_sticky_summary_height(self):
        html_rule = self.css.split("html {", 1)[1].split("}", 1)[0]
        self.assertIn(
            "scroll-padding-top: calc(var(--sticky-summary-offset) + 12px)",
            html_rule,
        )
        self.assertIn(
            "scroll-margin-top: calc(var(--sticky-summary-offset) + 12px)",
            self.css,
        )

    def test_complete_map_summary_is_wrapped_before_workspace(self):
        summary = self.html[
            self.html.index('<div class="map-summary">'):
            self.html.index('<div class="map-workspace">')
        ]
        self.assertIn('class="dataset-overview"', summary)
        self.assertIn('class="map-status-row"', summary)
        self.assertIn("Institution Records", summary)
        self.assertIn("Unique Papers", summary)
        self.assertIn("Unique Institutions", summary)
        self.assertIn("Countries", summary)
        self.assertIn("Circle Size = Unique Papers in Current View", summary)
        self.assertIn("Circle Color = Dominant Task", summary)
        self.assertIn('id="map-status"', summary)

    def test_desktop_filter_clears_header_and_map_summary_does_not_stack(self):
        desktop = self.css.split("@media (max-width: 820px)", 1)[0]
        sticky_desktop = desktop.split(
            "@media (min-width: 821px)", 1
        )[1].split("}", 1)[0]
        summary = desktop[
            desktop.index(".map-summary {"):desktop.index(".map-workspace {")
        ]
        self.assertIn("position: sticky", sticky_desktop)
        self.assertIn("top: var(--sticky-summary-offset)", sticky_desktop)
        self.assertIn(
            "max-height: calc(100dvh - var(--sticky-summary-offset) - 12px)",
            sticky_desktop,
        )
        self.assertIn("overflow-y: auto", sticky_desktop)
        self.assertIn("overscroll-behavior: contain", sticky_desktop)
        self.assertIn("scrollbar-gutter: stable", sticky_desktop)
        base_filter = desktop[
            desktop.index(".sidebar .filters-panel {"):
            desktop.index("@media (min-width: 821px)")
        ]
        self.assertNotIn("position: sticky", base_filter)
        self.assertNotIn("position: sticky", summary)
        self.assertIn("background: transparent", summary)

    def test_map_and_results_are_adjacent_and_results_use_page_scroll(self):
        map_column = self.css[
            self.css.index(".map-column {"):
            self.css.index(".results-panel {")
        ]
        self.assertIn("gap: 0", map_column)
        results_list = self.css[
            self.css.index(".results-list {"):
            self.css.index(".result-item {")
        ]
        self.assertNotIn("max-height", results_list)
        self.assertNotIn("overflow-y", results_list)

    def test_map_and_results_flow_without_a_full_height_outer_frame(self):
        map_column = self.css[
            self.css.index(".map-column {"):self.css.index(".results-heading-row {")
        ]
        wrapper = map_column.split(".results-panel {", 1)[0]
        self.assertIn("border: 0", wrapper)
        self.assertIn("border-radius: 0", wrapper)
        self.assertIn("background: transparent", wrapper)
        self.assertIn("box-shadow: none", wrapper)
        self.assertIn(".results-panel::before", map_column)
        self.assertEqual(map_column.count(".results-panel::before"), 1)
        self.assertIn("right: 12px", map_column)
        self.assertIn("left: 12px", map_column)
        self.assertIn("border-top: 1px solid var(--separator-line)", map_column)
        self.assertIn(".map-column > .map-panel", map_column)
        self.assertIn("border: 0", map_column)
        self.assertIn("box-shadow: none", map_column)

    def test_page_level_layout_and_sticky_header_do_not_add_seam_borders(self):
        header = self.css.split(".site-header {", 1)[1].split("}", 1)[0]
        page_shell = self.css.split(".page-shell {", 1)[1].split("}", 1)[0]
        self.assertIn("border-bottom: 0", header)
        self.assertNotIn("border:", page_shell)
        self.assertNotIn("border-left", page_shell)
        self.assertNotIn("border-right", page_shell)

    def test_header_workspace_and_footer_share_near_full_desktop_width(self):
        shared = self.css.split(
            ".site-header-inner,\n.page-shell,\nfooter {", 1
        )[1].split("}", 1)[0]
        self.assertIn("width: calc(100% - 24px)", shared)
        self.assertIn("max-width: 1920px", shared)
        self.assertIn("margin-inline: auto", shared)
        self.assertNotIn("max-width: 1440px", shared)
        self.assertNotIn("calc(100% - 40px)", shared)

    def test_desktop_sidebar_is_compact_and_main_column_gets_remaining_width(self):
        page_shell = self.css.split(".page-shell {", 1)[1].split("}", 1)[0]
        self.assertIn(
            "grid-template-columns: clamp(244px, 13vw, 248px) minmax(0, 1fr)",
            page_shell,
        )
        self.assertIn("gap: 11px", page_shell)
        self.assertNotIn("grid-template-columns: 250px", page_shell)

    def test_desktop_filters_and_workspace_use_compact_coherent_gutters(self):
        page_shell = self.css.split(".page-shell {", 1)[1].split("}", 1)[0]
        workspace = self.css.split(".map-workspace {", 1)[1].split("}", 1)[0]
        results = self.css.split(".results-panel {", 1)[1].split("}", 1)[0]
        self.assertIn("gap: 11px", page_shell)
        self.assertIn("gap: 12px", workspace)
        self.assertIn("padding: 12px 12px 16px", results)

    def test_secondary_surfaces_and_controls_are_deliberately_normalized(self):
        root = self.css.split(":root {", 1)[1].split("}", 1)[0]
        body = self.css.split("\nbody {\n  background", 1)[1].split("}", 1)[0]
        filters = self.css.split(".sidebar .filters-panel {", 1)[1].split("}", 1)[0]
        details = self.css.split(".paper-details {", 1)[1].split("}", 1)[0]
        controls = self.css.split("select,\ninput,\nbutton {", 1)[1].split("}", 1)[0]
        for token in (
            "--page-surface: #fbfcfc",
            "--header-surface: #f9fbfb",
            "--secondary-surface: #f6f8f8",
            "--institution-surface: #f3f7f7",
            "--metric-surface: #f5f8f8",
            "--overview-surface:",
        ):
            self.assertIn(token, root)
        self.assertIn(": var(--page-surface)", body)
        self.assertIn("background: var(--secondary-surface)", filters)
        self.assertIn("box-shadow: none", filters)
        self.assertIn("background: var(--secondary-surface)", details)
        self.assertIn("-webkit-appearance: none", controls)
        self.assertIn("appearance: none", controls)
        self.assertIn("box-shadow: none", controls)
        self.assertIn(':where(select, input:not([type="range"]), button):focus-visible', self.css)

    def test_bright_surfaces_keep_header_continuous_and_metrics_subtle(self):
        header = self.css.split(".site-header {", 1)[1].split("}", 1)[0]
        overview = self.css.split(".header-statistics {", 1)[1].split("}", 1)[0]
        metrics = self.css.split(".dataset-statistics div {", 1)[1].split("}", 1)[0]
        details_heading = self.css.split(".paper-details-heading {", 1)[1].split("}", 1)[0]
        self.assertIn("background: var(--header-surface)", header)
        self.assertIn("background: var(--overview-surface)", overview)
        self.assertIn("background: var(--metric-surface)", metrics)
        self.assertIn("background: var(--secondary-surface)", details_heading)
        self.assertNotIn("rgb(234 240 242", self.css)

    def test_desktop_map_dominates_narrower_details_column(self):
        workspace = self.css.split(".map-workspace {", 1)[1].split("}", 1)[0]
        details = self.css.split(".paper-details {", 1)[1].split("}", 1)[0]
        self.assertIn(
            "grid-template-columns: minmax(0, 1fr) minmax(260px, 276px)",
            workspace,
        )
        self.assertIn("background: var(--secondary-surface)", details)
        self.assertIn("max-width: 220px", self.css)

    def test_header_uses_one_full_width_surface_and_one_overview_strip(self):
        header = self.css.split(".site-header {", 1)[1].split("}", 1)[0]
        statistics = self.css.split(".header-statistics {", 1)[1].split("}", 1)[0]
        chart = self.css.split(".header-chart {", 1)[1].split("}", 1)[0]
        self.assertIn("background: var(--header-surface)", header)
        self.assertIn("width: 100%", header)
        self.assertIn("background: var(--overview-surface)", statistics)
        self.assertIn("gap: 0", statistics)
        self.assertIn("background: transparent", chart)
        self.assertIn("border: 0", chart)
        self.assertIn(".header-chart + .header-chart", self.css)

    def test_narrow_layout_uses_filter_drawer_above_sticky_header(self):
        mobile = self.css.split("@media (max-width: 820px)", 1)[1]
        self.assertIn(".sidebar .filters-panel {\n    position: fixed;", mobile)
        self.assertIn("z-index: 2000", mobile)

    def test_narrow_header_stays_sticky_with_tablet_grid_and_mobile_rail(self):
        tablet = self.css.split("@media (max-width: 820px) {", 1)[1].split(
            "@media (max-width: 820px) and", 1
        )[0]
        mobile = self.css.split("@media (max-width: 540px) {", 1)[1]
        self.assertIn(
            "grid-template-columns: repeat(3, minmax(0, 1fr))",
            tablet,
        )
        self.assertIn("display: flex", mobile)
        self.assertIn("overflow-x: auto", mobile)
        self.assertIn("scroll-snap-type: inline proximity", mobile)
        for responsive_rules in (tablet, mobile):
            self.assertNotIn(".site-header {\n    position: static", responsive_rules)
        self.assertIn("--sticky-summary-offset: 195px", mobile)


if __name__ == "__main__":
    unittest.main()
