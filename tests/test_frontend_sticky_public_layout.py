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
        header = self.html[
            self.html.index('<header class="site-header">'):
            self.html.index('</header>')
        ]
        for content in (
            'class="header-brand"',
            "Task Distribution",
            "Top Institutions",
            "Year Distribution",
            "GitHub Repository",
            'id="data-updated"',
        ):
            self.assertIn(content, header)

        sticky_rule = self.css.split(".site-header {", 1)[1].split("}", 1)[0]
        self.assertIn("position: sticky", sticky_rule)
        self.assertIn("top: 0", sticky_rule)
        self.assertIn("z-index: 1100", sticky_rule)
        self.assertIn("background: var(--canvas)", sticky_rule)

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
        self.assertIn("Map Records", summary)
        self.assertIn("Unique Institutions", summary)
        self.assertIn("Countries", summary)
        self.assertIn("Circle Size = Papers in Current View", summary)
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
        self.assertIn("background: var(--paper)", summary)

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

    def test_map_and_results_share_one_surface_with_single_inset_divider(self):
        map_column = self.css[
            self.css.index(".map-column {"):self.css.index(".results-heading-row {")
        ]
        self.assertIn("border: 1px solid var(--line)", map_column)
        self.assertIn("border-radius: 8px", map_column)
        self.assertIn("box-shadow: var(--shadow)", map_column)
        self.assertIn(".results-panel::before", map_column)
        self.assertIn("right: 12px", map_column)
        self.assertIn("left: 12px", map_column)
        self.assertIn("border-top: 1px solid var(--line)", map_column)
        self.assertIn(".map-column > .map-panel", map_column)
        self.assertIn("border: 0", map_column)
        self.assertIn("box-shadow: none", map_column)

    def test_narrow_layout_uses_filter_drawer_above_sticky_header(self):
        mobile = self.css.split("@media (max-width: 820px)", 1)[1]
        self.assertIn(".sidebar .filters-panel {\n    position: fixed;", mobile)
        self.assertIn("z-index: 2000", mobile)

    def test_narrow_header_stays_sticky_and_compacts_to_three_panels(self):
        tablet = self.css.split("@media (max-width: 820px) {", 1)[1].split(
            "@media (max-width: 820px) and", 1
        )[0]
        mobile = self.css.split("@media (max-width: 540px) {", 1)[1]
        for responsive_rules in (tablet, mobile):
            self.assertIn(
                "grid-template-columns: repeat(3, minmax(0, 1fr))",
                responsive_rules,
            )
            self.assertNotIn(".site-header {\n    position: static", responsive_rules)
        self.assertIn("--sticky-summary-offset: 141px", mobile)


if __name__ == "__main__":
    unittest.main()
