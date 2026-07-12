import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]


class FrontendChartFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (REPOSITORY / "web" / "app.js").read_text()
        cls.css = (REPOSITORY / "web" / "style.css").read_text()

    def test_chart_buttons_reuse_existing_filter_controls_and_render_pipeline(self):
        for value in (
            "data-chart-task",
            "data-chart-institution",
            "data-chart-year",
            'taskFilter.value = taskFilter.value === button.dataset.chartTask',
            'keywordFilter.value = keywordFilter.value === button.dataset.chartInstitution',
            "minYearFilter.value = year",
            "maxYearFilter.value = year",
            "renderRecords();",
        ):
            self.assertIn(value, self.app)

    def test_selected_state_and_native_keyboard_activation_are_accessible(self):
        self.assertIn('aria-pressed="${String(isSelected)}"', self.app)
        self.assertIn('type="button"', self.app)
        self.assertIn(".task-chart-segment.is-selected", self.css)
        self.assertIn(".institution-chart-row.is-selected", self.css)
        self.assertIn(".year-chart-item.is-selected", self.css)

    def test_responsive_dimensions_and_asset_version_are_preserved(self):
        html = (REPOSITORY / "web" / "index.html").read_text()
        self.assertIn("height: 76px", self.css)
        self.assertIn("min-width: 0", self.css)
        self.assertIn('style.css?v=20260713-chart-filters', html)
        self.assertIn('app.js?v=20260713-chart-filters', html)

    def test_year_toggle_restores_range_and_reset_clears_snapshot(self):
        self.assertIn("yearRangeBeforeChartSelection = {", self.app)
        self.assertIn('yearRangeBeforeChartSelection?.minimum || ""', self.app)
        self.assertIn('yearRangeBeforeChartSelection?.maximum || ""', self.app)
        self.assertGreaterEqual(self.app.count("yearRangeBeforeChartSelection = null;"), 2)
        self.assertIn("[minYearFilter, maxYearFilter].forEach", self.app)

    def test_chart_aggregation_and_public_data_files_are_not_changed_by_feature(self):
        self.assertIn("renderHeaderStatistics(visibleRecords, visiblePaperRecords)", self.app)
        handler = self.app[
            self.app.index("function activateChartFilter"):
            self.app.index("function renderHeaderStatistics")
        ]
        self.assertNotIn("fetch(", handler)


if __name__ == "__main__":
    unittest.main()
