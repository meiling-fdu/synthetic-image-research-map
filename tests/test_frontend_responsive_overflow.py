import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendResponsiveOverflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.admin_css = (ROOT / "web" / "admin.css").read_text(encoding="utf-8")

    def test_site_information_can_shrink_inside_the_page_shell(self):
        site_information = self.css[
            self.css.index(".site-information {"):
            self.css.index(".site-information h2,")
        ]
        self.assertIn("min-width: 0", site_information)
        self.assertIn("minmax(0, 1fr)", site_information)

    def test_information_grid_and_links_do_not_force_intrinsic_width(self):
        self.assertIn(".site-information-grid section {\n  min-width: 0;", self.css)
        links = self.css[
            self.css.index(".project-link-list {"):
            self.css.index(".dataset-overview {")
        ]
        self.assertIn("flex-wrap: wrap", links)
        self.assertIn("overflow-wrap: anywhere", links)

    def test_mobile_layout_keeps_information_in_one_container_track(self):
        mobile = self.css.split("@media (max-width: 540px)", 1)[1]
        self.assertIn(
            ".site-information-header,\n  .site-information-grid {\n"
            "    grid-template-columns: 1fr;",
            mobile,
        )

    def test_fix_does_not_mask_document_overflow(self):
        normalized = " ".join(self.css.split())
        self.assertNotIn("html, body { overflow-x: hidden", normalized)

    def test_admin_title_can_wrap_at_the_smallest_supported_width(self):
        mobile = self.admin_css.split("@media (max-width: 620px)", 1)[1]
        self.assertIn("h1 {\n    white-space: normal;", mobile)

    def test_admin_mobile_menus_position_against_the_full_navigation_bar(self):
        mobile = self.admin_css.split("@media (max-width: 620px)", 1)[1]
        self.assertIn(".console-nav { position: relative; }", mobile)
        self.assertIn(".nav-menu { position: static; }", mobile)


if __name__ == "__main__":
    unittest.main()
