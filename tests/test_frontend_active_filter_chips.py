import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendActiveFilterChipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.node = shutil.which("node")

    def run_node(self, source):
        if self.node is None:
            self.skipTest("Node.js is not on PATH")
        completed = subprocess.run(
            [self.node, "-e", source],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def test_bar_has_accessible_list_status_and_clear_all(self):
        self.assertEqual(self.html.count('id="active-filter-bar"'), 1)
        self.assertIn('aria-label="Active filters"', self.html)
        self.assertIn('id="active-filter-chips"', self.html)
        self.assertIn('id="clear-active-filters"', self.html)
        self.assertIn('role="status" aria-live="polite"', self.html)
        self.assertIn(".active-filter-chip button:focus-visible", self.css)

    def test_descriptors_cover_every_supported_filter_and_active_values(self):
        start = self.app.index("function selectedFilterOptionLabel")
        end = self.app.index("\nfunction renderActiveFilterChips", start)
        helpers = self.app[start:end]
        result = self.run_node(f"""
function control(value, label = value) {{
  return {{value, selectedOptions: [{{textContent: label}}]}};
}}
const keywordFilter = control(' diffusion ');
const taskFilter = control('detection');
const entryTypeFilter = control('survey');
const venueTypeFilter = control('conference', 'Conference (1,234)');
const venueFilter = control('cvpr', 'CVPR (42)');
const countryFilter = control('Italy', 'Italy (8)');
const institutionTypeFilter = control('university');
const preprintFilter = control('has-arxiv', 'Records With arXiv Version');
const publishedOnlyFilter = {{checked: false}};
const minYearFilter = control('2021');
const maxYearFilter = control('2024');
const yearRangeBounds = {{minimum: 2017, maximum: 2026}};
const activeInstitutionFilter = {{identity: 'id:test', label: 'Example University'}};
function formatPublicTask() {{ return 'Detection'; }}
function getEntryTypeLabel() {{ return 'Survey'; }}
function institutionTypeLabel() {{ return 'University'; }}
function currentYearSelection() {{
  return {{start: Number(minYearFilter.value), end: Number(maxYearFilter.value)}};
}}
{helpers}
console.log(JSON.stringify(activeFilterChipDescriptors()));
""")
        self.assertEqual(
            [descriptor["key"] for descriptor in result],
            [
                "keyword", "task", "entry-type", "venue-type", "venue",
                "country", "institution-type", "version", "year", "institution",
            ],
        )
        self.assertEqual(result[3]["value"], "Conference")
        self.assertEqual(result[2]["category"], "Research Type")
        self.assertEqual(result[4]["value"], "CVPR")
        self.assertEqual(result[8]["value"], "2021–2024")

    def test_rendering_builds_removal_buttons_and_clear_all_threshold(self):
        start = self.app.index("function renderActiveFilterChips")
        end = self.app.index("\nfunction applyInstitutionFilter", start)
        render = self.app[start:end]
        result = self.run_node(f"""
function element(tag) {{
  return {{
    tag, children: [], dataset: {{}}, attributes: {{}}, hidden: false, textContent: '',
    append(...children) {{ this.children.push(...children); }},
    setAttribute(name, value) {{ this.attributes[name] = value; }},
  }};
}}
const document = {{
  createDocumentFragment: () => element('fragment'),
  createElement: element,
}};
const activeFilterChips = element('ul');
activeFilterChips.replaceChildren = function (fragment) {{ this.children = fragment.children; }};
const activeFilterBar = element('div');
const clearActiveFiltersButton = element('button');
const activeFilterStatus = element('span');
let activeFilterChipsSignature = '';
let descriptors = [
  {{key: 'task', category: 'Task', value: 'Detection'}},
  {{key: 'country', category: 'Country', value: 'Italy'}},
];
function activeFilterChipDescriptors() {{ return descriptors; }}
{render}
renderActiveFilterChips();
const first = {{
  labels: activeFilterChips.children.map(item => item.children[0].textContent),
  removeKeys: activeFilterChips.children.map(item => item.children[1].dataset.removeFilter),
  removeLabel: activeFilterChips.children[0].children[1].attributes['aria-label'],
  barHidden: activeFilterBar.hidden,
  clearHidden: clearActiveFiltersButton.hidden,
  status: activeFilterStatus.textContent,
}};
descriptors = [descriptors[0]];
renderActiveFilterChips();
console.log(JSON.stringify({{first, oneClearHidden: clearActiveFiltersButton.hidden}}));
""")
        self.assertEqual(result["first"]["labels"], ["Task: Detection", "Country: Italy"])
        self.assertEqual(result["first"]["removeKeys"], ["task", "country"])
        self.assertEqual(result["first"]["removeLabel"], "Remove Task filter: Detection")
        self.assertFalse(result["first"]["barHidden"])
        self.assertFalse(result["first"]["clearHidden"])
        self.assertEqual(result["first"]["status"], "2 active filters")
        self.assertTrue(result["oneClearHidden"])

    def test_individual_removal_and_clear_all_use_one_existing_render(self):
        clear_start = self.app.index("function clearActiveFilter")
        clear_end = self.app.index("\nfunction focusFilterControl", clear_start)
        clear_helper = self.app[clear_start:clear_end]
        result = self.run_node(f"""
function control(value) {{ return {{value}}; }}
const keywordFilter = control('query');
const taskFilter = control('detection');
const entryTypeFilter = control('survey');
const venueTypeFilter = control('conference');
const venueFilter = control('cvpr');
const countryFilter = control('Italy');
const institutionTypeFilter = control('university');
const preprintFilter = control('has-arxiv');
const publishedOnlyFilter = {{checked: false}};
const minYearFilter = control('2021');
const maxYearFilter = control('2024');
const yearRangeBounds = {{minimum: 2017, maximum: 2026}};
let activeInstitutionFilter = {{identity: 'id:test', label: 'Example University'}};
let displayedInstitutionFilter = activeInstitutionFilter;
let syncSelects = 0;
let syncYears = 0;
let renders = 0;
function syncFilterDropdownForSelect() {{ syncSelects += 1; }}
function syncYearRange() {{ syncYears += 1; }}
function requestUrlStateSync() {{}}
function rememberFilterChange() {{}}
function renderRecords() {{ renders += 1; }}
{clear_helper}
clearActiveFilter('task');
clearActiveFilter('year');
clearActiveFilter('institution');
console.log(JSON.stringify({{
  task: taskFilter.value, minYear: minYearFilter.value, maxYear: maxYearFilter.value,
  activeInstitutionFilter, displayedInstitutionFilter, syncSelects, syncYears, renders,
}}));
""")
        self.assertEqual(result["task"], "all")
        self.assertEqual((result["minYear"], result["maxYear"]), ("2017", "2026"))
        self.assertIsNone(result["activeInstitutionFilter"])
        self.assertIsNone(result["displayedInstitutionFilter"])
        self.assertEqual(result["syncSelects"], 1)
        self.assertEqual(result["syncYears"], 1)
        self.assertEqual(result["renders"], 3)

        reset_start = self.app.index("function resetFilterValues")
        reset_end = self.app.index("\nfunction clearActiveFilter", reset_start)
        reset = self.app[reset_start:reset_end]
        self.assertIn(
            'resetFilterValues();\n  rememberFilterChange("all");\n  requestUrlStateSync("push");\n  renderRecords();',
            self.app,
        )
        self.assertIn("resetFilterValues({ resetSort: true });", self.app)
        self.assertIn("if (resetSort) sortControl.value", reset)

    def test_sync_runs_in_shared_pipeline_without_another_dataset_scan(self):
        render_start = self.app.index("function renderRecordsForGeneration")
        render_end = self.app.index("\n// A category is active", render_start)
        pipeline = self.app[render_start:render_end]
        self.assertEqual(pipeline.count("renderActiveFilterChips();"), 1)
        self.assertLess(
            pipeline.index("updateVenueDimensionFilters("),
            pipeline.index("renderActiveFilterChips();"),
        )
        chip_render = self.app[
            self.app.index("function renderActiveFilterChips"):
            self.app.index("\nfunction applyInstitutionFilter")
        ]
        self.assertNotIn("records", chip_render)
        self.assertIn("signature === activeFilterChipsSignature", chip_render)


if __name__ == "__main__":
    unittest.main()
