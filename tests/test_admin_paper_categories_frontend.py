import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("method", "dataset", "benchmark", "survey", "analysis")


class CategoryMarkupParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_fieldset = False
        self.in_grid = False
        self.fieldset_attrs = {}
        self.legend_count = 0
        self.inputs = []
        self.labels = []
        self.error_inside_grid = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "fieldset" and attributes.get("id") == "metadata-entry-type-field":
            self.in_fieldset = True
            self.fieldset_attrs = attributes
        if not self.in_fieldset:
            return
        if tag == "legend":
            self.legend_count += 1
        elif tag == "div" and attributes.get("id") == "metadata-paper-categories":
            self.in_grid = True
        elif tag == "label" and "paper-category-option" in attributes.get("class", "").split():
            self.labels.append(attributes)
        elif tag == "input" and attributes.get("type") == "checkbox":
            self.inputs.append(attributes)
        elif tag == "p" and attributes.get("id") == "metadata-paper-categories-error":
            self.error_inside_grid = self.in_grid

    def handle_endtag(self, tag):
        if tag == "div" and self.in_grid:
            self.in_grid = False
        elif tag == "fieldset" and self.in_fieldset:
            self.in_fieldset = False


def function_body(source, name, next_name):
    return source.split(f"function {name}", 1)[1].split(f"\nfunction {next_name}", 1)[0]


class AdminPaperCategoriesFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "admin.html").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "web" / "admin.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "admin.css").read_text(encoding="utf-8")
        cls.parser = CategoryMarkupParser()
        cls.parser.feed(cls.html)

    def test_markup_has_exact_canonical_accessible_checkbox_set(self):
        self.assertEqual(self.parser.legend_count, 1)
        self.assertEqual(len(self.parser.inputs), 5)
        self.assertEqual(len(self.parser.labels), 5)
        self.assertEqual(
            self.parser.fieldset_attrs.get("aria-describedby"),
            "metadata-paper-categories-error",
        )
        ids = [attributes.get("id") for attributes in self.parser.inputs]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn(None, ids)
        self.assertEqual(
            [attributes.get("value") for attributes in self.parser.inputs],
            list(CATEGORIES),
        )
        self.assertTrue(
            all(attributes.get("name") == "paper_categories" for attributes in self.parser.inputs)
        )
        self.assertEqual(
            [attributes.get("for") for attributes in self.parser.labels],
            ids,
        )
        self.assertFalse(self.parser.error_inside_grid)
        self.assertNotRegex(
            self.html,
            r'type="checkbox"[^>]*(?:value=""|value(?!\s*=))',
        )

    def test_one_authoritative_live_selection_reader_is_reused(self):
        reader = function_body(
            self.javascript, "getSelectedPaperCategories() {", "setPaperCategoriesError"
        )
        self.assertIn("paperCategoryCheckboxes().filter((input) => input.checked)", reader)
        self.assertIn(".map((input) => input.value)", reader)
        self.assertIn("normalizePaperCategories(", reader)
        self.assertIn(
            'input.paper-category-input[type="checkbox"][name="paper_categories"]',
            self.javascript,
        )
        snapshot = function_body(
            self.javascript, "metadataFormSnapshot() {", "metadataFormIsDirty"
        )
        validation = function_body(
            self.javascript, "validatePaperCategories({ focus = false } = {}) {", "hydratePaperCategories"
        )
        self.assertIn("getSelectedPaperCategories()", snapshot)
        self.assertIn("getSelectedPaperCategories()", validation)
        self.assertNotIn("selectedPaperCategories", self.javascript)

    def test_clear_preserves_checkbox_values_and_hydration_clears_previous_record(self):
        clear = function_body(self.javascript, "clearPaperMetadata(message, isError = false) {", "renderMetadataComparison")
        self.assertIn('["checkbox", "radio"].includes(control.type)', clear)
        self.assertIn("control.checked = false", clear)
        self.assertIn("control.value = \"\"", clear)
        hydrate = function_body(self.javascript, "hydratePaperCategories(value) {", "metadataFormSnapshot")
        self.assertLess(
            hydrate.index("input.checked = false"),
            hydrate.index("normalizePaperCategories(value)"),
        )
        self.assertIn("input.checked = categories.includes(input.value)", hydrate)
        populate = function_body(self.javascript, "populateMetadataForm() {", "closeMetadataEditor")
        self.assertIn("record?.paper_categories ?? record?.entry_type", populate)
        self.assertLess(
            populate.index("hydratePaperCategories("),
            populate.index("state.metadataSave.baseline = metadataFormSnapshot()"),
        )

    def test_validation_error_state_and_book_policy_are_preserved(self):
        validation = function_body(
            self.javascript, "validatePaperCategories({ focus = false } = {}) {", "hydratePaperCategories"
        )
        self.assertIn('value !== "book" && selected.length === 0', validation)
        self.assertIn('setPaperCategoriesError("Select at least one paper category.")', validation)
        self.assertIn("setPaperCategoriesError();", validation)
        error_state = function_body(
            self.javascript, "setPaperCategoriesError(message = \"\") {", "validatePaperCategories"
        )
        self.assertIn('fieldset.setAttribute("aria-invalid", "true")', error_state)
        self.assertIn('fieldset.removeAttribute("aria-invalid")', error_state)
        change = function_body(self.javascript, "handleMetadataFormChange(event) {", "populateMetadataForm")
        self.assertIn('matches?.(".paper-category-input")', change)
        self.assertIn("validatePaperCategories();", change)

    def test_dirty_snapshot_and_payload_use_canonical_selection(self):
        snapshot = function_body(
            self.javascript, "metadataFormSnapshot() {", "metadataFormIsDirty"
        )
        dirty = function_body(self.javascript, "metadataFormIsDirty() {", "normalizeCurationStatus")
        save = self.javascript.split("async function saveMetadata(event) {", 1)[1].split(
            "\nfunction renderPaperDetail", 1
        )[0]
        self.assertIn("values.paper_categories = getSelectedPaperCategories()", snapshot)
        self.assertIn("metadataFormSnapshot() !== state.metadataSave.baseline", dirty)
        self.assertIn("const paperCategories = validatePaperCategories({ focus: true })", save)
        self.assertIn("draft.paper_categories = paperCategories", save)
        self.assertNotIn("draft.entry_type", save)
        self.assertIn("paper_categories: isBook ? [] :", save)

    def test_layout_is_scoped_two_column_and_responsive(self):
        grid = self.css.split(".paper-category-options {", 1)[1].split("}", 1)[0]
        option = self.css.split(".paper-draft-form .paper-category-option {", 1)[1].split("}", 1)[0]
        self.assertIn("display: grid", grid)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", grid)
        self.assertIn("display: flex", option)
        self.assertIn("align-items: center", option)
        self.assertIn("gap:", option)
        narrow = self.css.split("@media (max-width: 620px) {", 1)[1]
        self.assertRegex(
            narrow,
            r"\.paper-category-options\s*\{\s*grid-template-columns:\s*1fr;",
        )
        self.assertNotIn("position: absolute", grid + option)
        self.assertNotIn("height:", grid + option)

    def test_admin_js_and_css_share_a_fresh_cache_key(self):
        css_version = re.search(r'/admin\.css\?v=([^"\s]+)', self.html).group(1)
        js_version = re.search(r'/admin\.js\?v=([^"\s]+)', self.html).group(1)
        self.assertEqual(css_version, js_version)
        self.assertEqual(css_version, "20260801-paper-categories")
        self.assertIn("20260718-research-institute", self.html)


if __name__ == "__main__":
    unittest.main()
