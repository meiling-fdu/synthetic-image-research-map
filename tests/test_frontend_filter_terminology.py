import json
import pathlib
import re
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendFilterTerminologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.docs = (ROOT / "docs" / "data_schema.md").read_text(encoding="utf-8")
        cls.node = shutil.which("node")

    def run_node(self, source):
        if self.node is None:
            self.skipTest("Node.js is not on PATH")
        completed = subprocess.run(
            [self.node, "-e", source], check=True, capture_output=True, text=True,
        )
        return json.loads(completed.stdout)

    def test_public_labels_and_descriptions_distinguish_the_two_dimensions(self):
        filter_grid = self.html[
            self.html.index('<div class="filter-grid">'):
            self.html.index('id="active-filter-bar"')
        ]
        self.assertIn('>Research Type</span>', filter_grid)
        self.assertIn('>Publication Type</span>', filter_grid)
        self.assertNotIn('>Paper Type</span>', filter_grid)
        self.assertIn(
            "Research contribution type: Methods, Datasets, Benchmarks, Surveys,",
            filter_grid,
        )
        self.assertIn(
            "Publication format: Conference, Journal, Preprint, Book Chapter,",
            filter_grid,
        )
        self.assertIn(
            'aria-describedby="research-type-filter-description"', filter_grid,
        )
        self.assertIn(
            'aria-describedby="venue-type-filter-description"', filter_grid,
        )
        self.assertIn(
            'button.setAttribute("aria-describedby", descriptionIds)', self.app,
        )
        self.assertIn("Keyword, Task, Research Type, Publication Type", self.docs)

    def test_control_ids_values_and_multi_select_change_pipeline(self):
        research_select = re.search(
            r'<select id="research-type-filter"[^>]*>(.*?)</select>',
            self.html,
            re.DOTALL,
        ).group(1)
        self.assertEqual(
            re.findall(r'<option value="([^"]+)">', research_select),
            ["all", "method", "dataset", "benchmark", "survey", "analysis_study"],
        )
        self.assertIn(
            'const entryTypeFilter = document.querySelector("#research-type-filter")',
            self.app,
        )
        self.assertIn(
            'entryTypeFilter.addEventListener("change", handleFilterControlChange)',
            self.app,
        )
        matching = self.app[
            self.app.index("function recordMatchesActiveFilters"):
            self.app.index("function dimensionPaperCounts")
        ]
        self.assertIn("const selectedTasks = selectedFilterValues(taskFilter)", matching)
        self.assertIn("const selectedImageScopes = selectedFilterValues(imageScopeFilter)", matching)
        self.assertIn("const selectedEntryTypes = selectedFilterValues(entryTypeFilter)", matching)
        self.assertIn("selectedTasks.some((value) => getTasks(record).includes(value))", matching)
        self.assertIn(
            "selectedImageScopes.some((value) => getImageScopes(record).includes(value))",
            matching,
        )
        self.assertIn(
            "selectedEntryTypes.some((value) => getPaperCategories(record).includes(value))",
            matching,
        )

    def test_existing_research_types_urls_round_trip_without_migration(self):
        order_start = self.app.index("const URL_STATE_PARAMETER_ORDER")
        order_end = self.app.index("\nconst TILE_BOUNDS", order_start)
        helpers_start = self.app.index("function serializeViewState")
        helpers_end = self.app.index("\nfunction canonicalViewUrl", helpers_start)
        helpers = (
            self.app[order_start:order_end]
            + "\n"
            + self.app[helpers_start:helpers_end]
        )
        result = self.run_node(f"""
{helpers}
const restored = parseViewState('?dataset=preview&research_types=survey&publication_type=journal');
const state = {{
  keyword: '', tasks: 'all', imageScopes: 'all', researchTypes: restored.researchTypes,
  publicationType: restored.publicationType, venue: 'all', country: 'all',
  institutionType: 'all', version: 'all', yearStart: 2018, yearEnd: 2026,
  yearMinimum: 2018, yearMaximum: 2026, institution: '', institutionLabel: '',
  view: 'institutions', sort: 'year-desc',
}};
process.stdout.write(JSON.stringify({{
  restored,
  serialized: serializeViewState(state, 'preview'),
}}));
""")
        self.assertEqual(result["restored"]["researchTypes"], "survey")
        self.assertEqual(result["restored"]["publicationType"], "journal")
        self.assertEqual(
            result["serialized"],
            "dataset=preview&research_types=survey&publication_type=journal",
        )

    def test_active_chip_renames_only_the_user_facing_category(self):
        descriptors = self.app[
            self.app.index("function activeFilterChipDescriptors"):
            self.app.index("\nfunction currentViewState")
        ]
        self.assertIn(
            'key: "research-types", category: "Research Type"', descriptors,
        )
        self.assertIn(
            'key: "venue-type", category: "Publication Type"', descriptors,
        )
        self.assertNotIn('category: "Paper Type"', descriptors)
        self.assertIn(
            'researchTypes: serializedFilterValues(entryTypeFilter)', self.app,
        )
        self.assertIn('research_types: state.researchTypes !== "all"', self.app)
        self.assertIn('researchTypes: params.get("research_types") || "all"', self.app)


if __name__ == "__main__":
    unittest.main()
