import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendResponsiveOverflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")

    def test_project_links_grid_can_shrink_inside_the_page_shell(self):
        project_links = self.css[
            self.css.index(".project-links {"):
            self.css.index(".project-links h2,")
        ]
        self.assertIn("grid-template-columns: auto minmax(0, 1fr)", project_links)
        self.assertIn("min-width: 0", project_links)

    def test_project_links_content_and_links_do_not_force_intrinsic_width(self):
        content = self.css[
            self.css.index(".project-links-content {"):
            self.css.index(".project-link-list a,")
        ]
        self.assertIn(".project-links-content {", content)
        self.assertIn("min-width: 0", content)
        self.assertIn(".project-link-list {", content)
        self.assertIn("flex-wrap: wrap", content)

    def test_mobile_layout_keeps_project_links_in_one_container_track(self):
        mobile = self.css.split("@media (max-width: 540px)", 1)[1]
        project_links = mobile[
            mobile.index(".project-links {"):
            mobile.index(".project-links h2 {")
        ]
        self.assertIn("grid-template-columns: 1fr", project_links)

    def test_fix_does_not_mask_document_overflow(self):
        normalized = " ".join(self.css.split())
        self.assertNotIn("html, body { overflow-x: hidden", normalized)


if __name__ == "__main__":
    unittest.main()
