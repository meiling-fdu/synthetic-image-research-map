import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendStickyPublicLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")

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

    def test_desktop_panels_are_sticky_with_opaque_backgrounds(self):
        desktop = self.css.split("@media (max-width: 820px)", 1)[0]
        filters = desktop[desktop.index(".sidebar .filters-panel {"):]
        summary = desktop[desktop.index(".map-summary {"):]
        for rule in (filters, summary):
            self.assertIn("position: sticky", rule)
            self.assertIn("top: 0", rule)
            self.assertIn("background: var(--paper)", rule)
            self.assertIn("z-index:", rule)

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

    def test_narrow_layout_disables_in_page_sticky_summary(self):
        mobile = self.css.split("@media (max-width: 820px)", 1)[1]
        self.assertIn(".map-summary {\n    position: static;", mobile)
        self.assertIn(".sidebar .filters-panel {\n    position: fixed;", mobile)


if __name__ == "__main__":
    unittest.main()
