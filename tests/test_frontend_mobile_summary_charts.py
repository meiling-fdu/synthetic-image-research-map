import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontendMobileSummaryChartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.mobile = cls.css.split("@media (max-width: 540px) {", 1)[1]

    def test_mobile_uses_a_bounded_horizontal_card_rail(self):
        statistics = self.mobile.split(".header-statistics {", 1)[1].split("}", 1)[0]
        chart = self.mobile.split(".header-chart {", 1)[1].split("}", 1)[0]
        self.assertIn("display: flex", statistics)
        self.assertIn("overflow-x: auto", statistics)
        self.assertIn("overflow-y: hidden", statistics)
        self.assertIn("scroll-snap-type: inline proximity", statistics)
        self.assertIn("flex: 0 0 min(82vw, 300px)", chart)
        self.assertIn("height: 126px", chart)
        self.assertIn("scroll-snap-align: start", chart)

        # The card basis remains narrower than both representative mobile
        # viewports, leaving scrolling inside the rail instead of on the page.
        for viewport in (390, 320):
            with self.subTest(viewport=viewport):
                self.assertLessEqual(min(viewport * 0.82, 300), viewport - 24)

    def test_mobile_labels_and_touch_targets_are_not_compressed(self):
        self.assertIn("font-size: 0.68rem", self.mobile)
        self.assertIn("font-size: 0.7rem", self.mobile)
        self.assertIn("min-height: 44px", self.mobile)
        self.assertIn("min-height: 64px", self.mobile)
        self.assertIn("grid-template-columns: repeat(3, minmax(78px, 1fr))", self.mobile)
        self.assertIn("grid-template-columns: 7px minmax(0, 1fr)", self.mobile)
        self.assertIn("text-overflow: clip", self.mobile)
        self.assertIn("grid-template-rows: repeat(2, 44px)", self.mobile)
        self.assertIn("grid-auto-columns: minmax(132px, 1fr)", self.mobile)
        self.assertIn("flex: 0 0 48px", self.mobile)
        self.assertNotIn("font-size: 0.48rem", self.mobile)

    def test_desktop_and_tablet_chart_grid_remain_unchanged(self):
        desktop = self.css.split("@media (max-width: 540px) {", 1)[0]
        self.assertIn(
            "grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr) minmax(0, 1fr)",
            desktop,
        )
        tablet = desktop.split("@media (max-width: 820px) {", 1)[1]
        self.assertIn("grid-template-columns: repeat(3, minmax(0, 1fr))", tablet)

    def test_layout_reuses_existing_accessible_chart_controls_and_pipeline(self):
        chart_renderers = self.app[
            self.app.index("function renderTaskChart"):
            self.app.index("function renderHeaderStatistics")
        ]
        self.assertEqual(chart_renderers.count('<button type="button"'), 3)
        self.assertEqual(chart_renderers.count('aria-pressed="'), 3)
        self.assertIn("refreshedControl?.focus({ preventScroll: true })", self.app)
        activation = self.app[
            self.app.index("function activateChartFilter"):
            self.app.index("function renderTaskChart")
        ]
        self.assertEqual(activation.count('requestUrlStateSync("push")'), 1)
        self.assertEqual(activation.count("renderRecords();"), 1)


if __name__ == "__main__":
    unittest.main()
