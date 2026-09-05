import json
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node") or str(
    Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
)
EXPECTED = {
    "paper-tasks": ["detection", "source_attribution", "localization"],
    "paper-image-scopes": ["fully_generated", "generative_editing", "deepfake", "traditional_manipulation"],
    "paper-research-types": ["method", "dataset", "benchmark", "survey", "analysis_study"],
    "metadata-tasks": ["detection", "source_attribution", "localization"],
    "metadata-image-scopes": ["fully_generated", "generative_editing", "deepfake", "traditional_manipulation"],
    "metadata-research-types": ["method", "dataset", "benchmark", "survey", "analysis_study"],
}
SINGLE_SELECTS = {
    "paper-publication-type",
    "paper-scope-status",
    "paper-review-status",
    "metadata-venue-track",
    "metadata-publication-type",
    "metadata-scope-status",
    "metadata-curation-status",
    "metadata-review-status",
}


class TaxonomyMarkupParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_group = None
        self.groups = {}
        self.selects = {}
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if tag == "fieldset" and element_id in EXPECTED:
            self.current_group = element_id
            self.groups[element_id] = {"attrs": attributes, "inputs": []}
        elif tag == "label" and self.current_group:
            self.labels.append(attributes.get("for"))
        elif tag == "input" and self.current_group:
            self.groups[self.current_group]["inputs"].append(attributes)
        elif tag == "select" and element_id:
            self.selects[element_id] = attributes

    def handle_endtag(self, tag):
        if tag == "fieldset":
            self.current_group = None


def function_source(source, name, next_name):
    return f"function {name}" + source.split(f"function {name}", 1)[1].split(
        f"\nfunction {next_name}", 1
    )[0]


class AdminPaperTaxonomyFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web/admin.css").read_text(encoding="utf-8")
        cls.parser = TaxonomyMarkupParser()
        cls.parser.feed(cls.html)

    def test_add_and_edit_forms_expose_exact_accessible_checkbox_groups(self):
        self.assertEqual(set(self.parser.groups), set(EXPECTED))
        all_input_ids = []
        for group_id, values in EXPECTED.items():
            with self.subTest(group_id=group_id):
                group = self.parser.groups[group_id]
                inputs = group["inputs"]
                self.assertEqual(group["attrs"].get("aria-required"), "true")
                self.assertEqual([item.get("value") for item in inputs], values)
                self.assertTrue(all(item.get("type") == "checkbox" for item in inputs))
                self.assertTrue(all("paper-category-input" in item.get("class", "") for item in inputs))
                input_ids = [item.get("id") for item in inputs]
                self.assertTrue(all(input_ids))
                self.assertTrue(all(item in self.parser.labels for item in input_ids))
                all_input_ids.extend(input_ids)
        self.assertEqual(len(all_input_ids), len(set(all_input_ids)))
        self.assertNotRegex(
            self.html,
            r'<select[^>]+id="(?:paper|metadata)-(?:tasks|image-scopes|research-types)"',
        )

    @unittest.skipUnless(Path(NODE).is_file(), "Node.js is required for the checkbox behavior test")
    def test_loading_toggling_and_reload_preserve_multiple_values(self):
        helpers = "\n".join([
            function_source(self.javascript, "selectedCheckboxValues", "setCheckedValues"),
            function_source(self.javascript, "setCheckedValues", "validateTaxonomyGroups"),
        ])
        script = f"""
const elements = {{}};
function group(values) {{
  const inputs = values.map((value) => ({{ value, checked: false }}));
  return {{ inputs, querySelectorAll: () => inputs }};
}}
elements["metadata-tasks"] = group(["detection", "source_attribution", "localization"]);
{helpers}
setCheckedValues("metadata-tasks", ["detection", "localization"]);
const loaded = selectedCheckboxValues("metadata-tasks");
elements["metadata-tasks"].inputs[1].checked = true;
elements["metadata-tasks"].inputs[0].checked = false;
const saved = selectedCheckboxValues("metadata-tasks");
elements["metadata-tasks"].inputs.forEach((input) => {{ input.checked = false; }});
setCheckedValues("metadata-tasks", saved);
const reloaded = selectedCheckboxValues("metadata-tasks");
process.stdout.write(JSON.stringify({{ loaded, saved, reloaded }}));
"""
        result = subprocess.run(
            [NODE, "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        values = json.loads(result.stdout)
        self.assertEqual(values["loaded"], ["detection", "localization"])
        self.assertEqual(values["saved"], ["source_attribution", "localization"])
        self.assertEqual(values["reloaded"], values["saved"])

    def test_payload_snapshot_hydration_and_validation_use_checkbox_values(self):
        add_identifiers = {
            "tasks": "paper-tasks",
            "image_scopes": "paper-image-scopes",
            "research_types": "paper-research-types",
        }
        edit_identifiers = {
            "tasks": "metadata-tasks",
            "image_scopes": "metadata-image-scopes",
            "research_types": "metadata-research-types",
        }
        for field, identifier in add_identifiers.items():
            self.assertIn(f'{field}: selectedCheckboxValues("{identifier}")', self.javascript)
        for field, identifier in edit_identifiers.items():
            self.assertIn(f'values.{field} = selectedCheckboxValues("{identifier}")', self.javascript)
            self.assertIn(f'setCheckedValues("{identifier}", record?.{field})', self.javascript)
            self.assertIn(f'draft.{field} = selectedCheckboxValues("{identifier}")', self.javascript)
        self.assertIn('validateTaxonomyGroups("paper", { focus: true })', self.javascript)
        self.assertIn('validateTaxonomyGroups("metadata", { focus: true })', self.javascript)
        self.assertIn("Select at least one value in every taxonomy dimension.", self.javascript)

    def test_checkbox_group_layout_is_two_column_then_one_column(self):
        grid = self.css.split(".paper-category-options {", 1)[1].split("}", 1)[0]
        option = self.css.split(".paper-draft-form .paper-category-option {", 1)[1].split("}", 1)[0]
        narrow = self.css.split("@media (max-width: 620px) {", 1)[1]
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", grid)
        self.assertRegex(
            narrow,
            r"\.paper-category-options\s*\{\s*grid-template-columns:\s*1fr;",
        )
        self.assertIn("min-height: 2.25rem", option)
        self.assertNotRegex(grid + option, r"(?:overflow|max-height):")

    def test_single_selects_and_venue_verification_checkbox_are_unchanged(self):
        for select_id in SINGLE_SELECTS:
            with self.subTest(select_id=select_id):
                self.assertIn(select_id, self.parser.selects)
                self.assertNotIn("multiple", self.parser.selects[select_id])
        self.assertIn('id="metadata-venue-review-confirmed" type="checkbox"', self.html)
        self.assertIn('elements["metadata-venue-review-confirmed"].checked', self.javascript)
        self.assertIn('draft.venue_review_confirmed = true', self.javascript)

    def test_admin_assets_share_a_fresh_cache_key(self):
        css_version = re.search(r'/admin\.css\?v=([^"\s]+)', self.html).group(1)
        js_version = re.search(r'/admin\.js\?v=([^"\s]+)', self.html).group(1)
        self.assertEqual(css_version, js_version)
        self.assertEqual(css_version, "20260905-taxonomy-checkboxes")


if __name__ == "__main__":
    unittest.main()
