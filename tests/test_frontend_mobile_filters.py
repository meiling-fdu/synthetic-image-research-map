import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendMobileFiltersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")

    def test_single_filter_panel_is_reused_by_mobile_drawer(self):
        self.assertEqual(self.html.count('id="filters-panel"'), 1)
        self.assertEqual(self.html.count('class="filter-grid"'), 1)
        self.assertIn('aria-controls="filters-panel"', self.html)
        self.assertIn('aria-expanded="false"', self.html)
        self.assertIn('aria-label="Close filters"', self.html)
        self.assertIn('id="done-filters"', self.html)
        self.assertIn('id="filters-backdrop"', self.html)
        self.assertIn('role="region"', self.html)
        self.assertIn('aria-labelledby="filters-heading"', self.html)
        self.assertNotIn('role="dialog"', self.html)
        self.assertNotIn('aria-modal="true"', self.html)

    def test_existing_breakpoint_preserves_desktop_and_enables_mobile_drawer(self):
        mobile = self.css.split("@media (max-width: 820px)", 1)[1]
        self.assertIn(".mobile-filters-trigger", mobile)
        self.assertIn("position: fixed", mobile)
        self.assertIn("height: 100dvh", mobile)
        self.assertIn("overflow-y: auto", mobile)
        self.assertIn("z-index: 2000", mobile)
        desktop = self.css.split("@media (max-width: 820px)", 1)[0]
        self.assertIn(".mobile-filters-trigger,\n.filters-backdrop,", desktop)
        self.assertIn("display: none", desktop)

    def test_active_count_uses_authoritative_categories_and_omits_zero(self):
        descriptor = self.app[
            self.app.index("function activeFilterChipDescriptors"):
            self.app.index("\nfunction renderActiveFilterChips")
        ]
        for filter_name in (
            "keywordFilter", "taskFilter", "entryTypeFilter", "venueTypeFilter",
            "venueFilter", "countryFilter", "institutionTypeFilter",
            "preprintFilter", "activeInstitutionFilter",
        ):
            self.assertIn(filter_name, descriptor)
        self.assertIn("selection.start !== yearRangeBounds.minimum", descriptor)
        self.assertIn("selection.end !== yearRangeBounds.maximum", descriptor)
        self.assertIn("return activeFilterChipDescriptors().length", self.app)
        self.assertIn('count ? `Filters (${count})` : "Filters"', self.app)
        self.assertNotIn("Filters (0)", self.app)

    def test_open_close_focus_trap_scroll_lock_and_resize_cleanup(self):
        self.assertIn('document.body.classList.add("filters-drawer-open")', self.app)
        self.assertIn('document.body.classList.remove("filters-drawer-open")', self.app)
        self.assertIn('filtersHeading.focus()', self.app)
        self.assertIn('mobileFiltersTrigger.focus()', self.app)
        self.assertIn('event.key === "Escape"', self.app)
        self.assertIn('event.key !== "Tab"', self.app)
        self.assertIn('!mobileFiltersMedia.matches || !filtersDrawerOpen', self.app)
        self.assertIn('filtersPanel.contains(document.activeElement)', self.app)
        self.assertIn('filtersPanel.toggleAttribute("inert"', self.app)
        self.assertIn('filtersPanel.setAttribute("aria-modal", "true")', self.app)
        self.assertIn('filtersPanel.removeAttribute("aria-modal")', self.app)
        self.assertIn('isOpenMobileDialog ? "dialog" : "region"', self.app)
        self.assertIn('filtersBackdrop.addEventListener("pointerdown"', self.app)
        self.assertIn('doneFiltersButton.addEventListener("click"', self.app)
        self.assertIn('mobileFiltersMedia.addEventListener("change"', self.app)
        self.assertIn('closeFiltersDrawer({ restoreFocus: false })', self.app)

    def test_reset_remains_single_authoritative_implementation(self):
        self.assertEqual(
            self.app.count('resetButton.addEventListener("click"'),
            1,
        )
        reset_values = self.app[
            self.app.index("function resetFilterValues"):
            self.app.index("\nfunction clearActiveFilter")
        ]
        reset = self.app[self.app.index('resetButton.addEventListener("click"'):]
        self.assertIn('keywordFilter.value = ""', reset_values)
        self.assertIn('countryFilter.value = "all"', reset_values)
        self.assertIn("activeInstitutionFilter = null", reset_values)
        self.assertIn("resetFilterValues({ resetSort: true })", reset)
        self.assertIn("renderRecords()", reset)
        self.assertNotIn("closeFiltersDrawer", reset)

    def test_reduced_motion_and_safe_area_are_supported(self):
        self.assertIn("prefers-reduced-motion: reduce", self.css)
        self.assertIn("env(safe-area-inset-top)", self.css)
        self.assertIn("env(safe-area-inset-bottom)", self.css)


if __name__ == "__main__":
    unittest.main()
