import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InstitutionManagementPaginationFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        cls.source = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web/admin.css").read_text(encoding="utf-8")
        start = cls.source.index("function filteredInstitutionRecords")
        end = cls.source.index("async function postInstitutionAction", start)
        cls.pagination = cls.source[start:end]

    def test_controls_are_rendered_above_and_below_with_supported_sizes(self):
        self.assertEqual(self.html.count('class="institution-pagination"'), 2)
        self.assertEqual(self.html.count('data-institution-page-action="first"'), 2)
        self.assertEqual(self.html.count('data-institution-page-action="previous"'), 2)
        self.assertEqual(self.html.count('data-institution-page-action="next"'), 2)
        self.assertEqual(self.html.count('data-institution-page-action="last"'), 2)
        for size in (25, 50, 100):
            self.assertEqual(self.html.count(f'<option value="{size}"'), 2)
        self.assertIn('institutionManagement: { query: "", page: 1, pageSize: 50 }', self.source)

    def test_filtering_happens_before_page_slicing(self):
        filtering = self.pagination.index("const records = filteredInstitutionRecords()")
        slicing = self.pagination.index("records.slice(pageStart, pageStart + pageSize)")
        rendering = self.pagination.index("pageRecords.forEach")
        self.assertLess(filtering, slicing)
        self.assertLess(slicing, rendering)
        self.assertNotIn("records.forEach((institution)", self.pagination)

    def test_search_and_page_size_changes_reset_to_first_page(self):
        search_listener = self.source[
            self.source.index('elements["institution-management-search"].addEventListener'):
            self.source.index('elements["institution-merge-search"].addEventListener')
        ]
        self.assertIn("state.institutionManagement.page = 1", search_listener)
        page_size = self.pagination[
            self.pagination.index("function changeInstitutionPageSize"):
            self.pagination.index("function updateInstitutionPagination")
        ]
        self.assertIn("state.institutionManagement.pageSize = Number(event.currentTarget.value)", page_size)
        self.assertIn("state.institutionManagement.page = 1", page_size)

    def test_navigation_scrolls_the_list_and_reports_page_state(self):
        change_page = self.pagination[
            self.pagination.index("function changeInstitutionPage"):
            self.pagination.index("function changeInstitutionPageSize")
        ]
        self.assertIn("scrollInstitutionManagementToTop()", change_page)
        self.assertIn("list.scrollTop = 0", self.pagination)
        self.assertIn("`Page ${recordCount ? page : 0} of ${totalPages}", self.pagination)

    def test_refresh_and_actions_preserve_pagination_state(self):
        refresh = self.source[
            self.source.index("async function refreshInstitutions"):
            self.source.index("function institutionActionButton")
        ]
        self.assertIn("renderInstitutionManagement()", refresh)
        self.assertNotIn("institutionManagement.page =", refresh)
        self.assertNotIn("institutionManagement.query =", refresh)
        self.assertNotIn("institutionManagement.pageSize =", refresh)
        self.assertIn("await Promise.all([refreshInstitutions(), loadLocationReviews()])", self.source)

    def test_empty_and_out_of_range_states_are_visible(self):
        self.assertIn("No institutions match the current search.", self.pagination)
        self.assertIn("No institutions are available.", self.pagination)
        self.assertIn("is out of range. Choose First, Previous, or Last.", self.pagination)
        self.assertIn('id="institution-management-empty" role="status"', self.html)

    def test_search_and_headers_are_sticky_in_scrollable_list(self):
        self.assertIn(".institution-management-search {", self.css)
        self.assertIn("position: sticky", self.css[self.css.index(".institution-management-search {"):])
        table_css = self.css[self.css.index(".institution-management-table-wrap {"):]
        self.assertIn("overflow: auto", table_css)
        self.assertIn(".institution-management-table-wrap thead th", table_css)
        self.assertIn("position: sticky", table_css)


if __name__ == "__main__":
    unittest.main()
