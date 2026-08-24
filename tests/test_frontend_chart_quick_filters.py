import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendChartQuickFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.node = shutil.which("node")

    def run_node(self, source):
        if self.node is None:
            self.skipTest("Node.js is not on PATH")
        completed = subprocess.run(
            [self.node, "-e", source], check=True, capture_output=True, text=True,
        )
        return json.loads(completed.stdout)

    def function(self, start, end):
        start_index = self.app.index(f"function {start}")
        return self.app[start_index:self.app.index(f"function {end}", start_index)]

    def test_activation_toggles_each_filter_with_one_render_and_url_update(self):
        activation = self.function("activateChartFilter", "renderTaskChart")
        result = self.run_node(f"""
const taskFilter = {{
  value: 'all', options: [{{value: 'all'}}, {{value: 'detection'}}],
}};
const minYearFilter = {{value: '2018'}};
const maxYearFilter = {{value: '2026'}};
const yearRangeBounds = {{minimum: 2018, maximum: 2026}};
let activeInstitutionFilter = null;
let displayedInstitutionFilter = null;
let yearHistoryStarted = true;
let renders = 0;
let urlUpdates = [];
let dropdownSyncs = 0;
let rangeSyncs = 0;
let focusRestores = 0;
const headerStatistics = {{
  querySelectorAll: () => [
    ['task', 'detection'],
    ['institution', 'institution:alpha'],
    ['year', '2024'],
  ].map(([chartFilter, chartValue]) => ({{
    dataset: {{chartFilter, chartValue}},
    focus: options => {{ if (options.preventScroll) focusRestores += 1; }},
  }})),
}};
const selectContainsValue = (select, value) => select.options.some(option => option.value === value);
const syncFilterDropdownForSelect = () => {{ dropdownSyncs += 1; }};
const currentYearSelection = () => ({{
  start: Number(minYearFilter.value), end: Number(maxYearFilter.value),
}});
const syncYearRange = () => {{ rangeSyncs += 1; }};
const hideChartTooltip = () => {{}};
const rememberFilterChange = () => {{}};
const requestUrlStateSync = mode => urlUpdates.push(mode);
const renderRecords = () => {{ renders += 1; }};
{activation}
const snapshot = name => ({{
  name, task: taskFilter.value,
  institution: activeInstitutionFilter,
  years: [minYearFilter.value, maxYearFilter.value],
  renders, urlUpdates: [...urlUpdates], dropdownSyncs, rangeSyncs, focusRestores,
}});
const states = [];
activateChartFilter('task', 'detection'); states.push(snapshot('task-on'));
activateChartFilter('task', 'detection'); states.push(snapshot('task-off'));
activateChartFilter('institution', 'institution:alpha', 'Alpha'); states.push(snapshot('institution-on'));
activateChartFilter('institution', 'institution:alpha', 'Alpha'); states.push(snapshot('institution-off'));
activateChartFilter('year', '2024'); states.push(snapshot('year-on'));
activateChartFilter('year', '2024'); states.push(snapshot('year-off'));
process.stdout.write(JSON.stringify(states));
""")
        self.assertEqual(result[0]["task"], "detection")
        self.assertEqual(result[1]["task"], "all")
        self.assertEqual(result[2]["institution"], {
            "identity": "institution:alpha", "label": "Alpha",
        })
        self.assertIsNone(result[3]["institution"])
        self.assertEqual(result[4]["years"], ["2024", "2024"])
        self.assertEqual(result[5]["years"], ["2018", "2026"])
        for index, state in enumerate(result, 1):
            self.assertEqual(state["renders"], index)
            self.assertEqual(state["urlUpdates"], ["push"] * index)
            self.assertEqual(state["focusRestores"], index)
        self.assertEqual(result[-1]["dropdownSyncs"], 2)
        self.assertEqual(result[-1]["rangeSyncs"], 2)

    def test_rendered_pressed_state_tracks_external_filter_state(self):
        charts = self.app[
            self.app.index("function renderTaskChart"):
            self.app.index("function renderHeaderStatistics")
        ]
        result = self.run_node(f"""
const taskChartContent = {{innerHTML: ''}};
const institutionChartContent = {{innerHTML: ''}};
const yearChartContent = {{innerHTML: ''}};
const TASK_COLORS = {{
  detection: '#1', source_attribution: '#2', detection_and_source_attribution: '#3',
}};
const escapeHtml = value => String(value);
const recordInstitution = record => record.institution;
const institutionIdentity = record => record.institutionKey;
const paperIdentity = record => record.paper;
const publicationYear = record => record.year;
const compareTextValues = (first, second) => first.localeCompare(second);
const renderChartEmpty = container => {{ container.innerHTML = 'empty'; }};
const taskFilter = {{value: 'detection'}};
let activeInstitutionFilter = {{identity: 'institution:alpha', label: 'Alpha'}};
const minYearFilter = {{value: '2024'}};
const maxYearFilter = {{value: '2024'}};
const currentYearSelection = () => ({{
  start: Number(minYearFilter.value), end: Number(maxYearFilter.value),
}});
{charts}
const records = [
  {{paper: 'p1', institution: 'Alpha', institutionKey: 'institution:alpha', task: 'detection', year: 2024}},
  {{paper: 'p2', institution: 'Beta', institutionKey: 'institution:beta', task: 'source_attribution', year: 2023}},
];
renderTaskChart(records);
renderInstitutionChart(records);
renderYearChart(records);
const selected = {{
  task: taskChartContent.innerHTML,
  institution: institutionChartContent.innerHTML,
  year: yearChartContent.innerHTML,
}};
taskFilter.value = 'all';
activeInstitutionFilter = null;
minYearFilter.value = '2018';
maxYearFilter.value = '2026';
renderTaskChart(records);
renderInstitutionChart(records);
renderYearChart(records);
process.stdout.write(JSON.stringify({{
  selected,
  cleared: {{
    task: taskChartContent.innerHTML,
    institution: institutionChartContent.innerHTML,
    year: yearChartContent.innerHTML,
  }},
}}));
""")
        self.assertIn('data-chart-value="detection"', result["selected"]["task"])
        self.assertIn('data-chart-value="detection"', result["selected"]["task"].split('aria-pressed="true"')[0])
        self.assertIn('data-chart-value="institution:alpha"', result["selected"]["institution"].split('aria-pressed="true"')[0])
        self.assertIn('data-chart-value="2024"', result["selected"]["year"].split('aria-pressed="true"')[0])
        for html in result["cleared"].values():
            self.assertNotIn('aria-pressed="true"', html)

    def test_native_buttons_supply_keyboard_semantics_and_mobile_hit_areas(self):
        charts = self.app[
            self.app.index("function renderTaskChart"):
            self.app.index("function renderHeaderStatistics")
        ]
        self.assertEqual(charts.count('<button type="button"'), 3)
        self.assertEqual(charts.count('aria-pressed="'), 3)
        self.assertNotIn('tabindex="0"', charts)
        self.assertNotIn('role="button"', charts)
        self.assertIn('headerStatistics.addEventListener("click"', self.app)
        self.assertIn("event.target.closest(\"button[data-chart-filter]\")", self.app)
        self.assertIn("refreshedControl?.focus({ preventScroll: true })", self.app)
        self.assertIn("touch-action: manipulation", self.css)
        self.assertIn("min-height: 100%", self.css)
        mobile = self.css.split("@media (max-width: 540px) {", 1)[1]
        self.assertIn("min-height: 44px", mobile)
        self.assertIn("grid-template-rows: repeat(2, 44px)", mobile)
        self.assertIn("flex: 0 0 48px", mobile)

    def test_chart_actions_use_existing_url_and_render_pipeline(self):
        activation = self.function("activateChartFilter", "renderTaskChart")
        self.assertEqual(activation.count('requestUrlStateSync("push")'), 1)
        self.assertEqual(activation.count("renderRecords();"), 1)
        self.assertNotIn("recordMatchesActiveFilters", activation)
        self.assertNotIn("deriveFilteredRecordSets", activation)
        self.assertNotIn("dispatchEvent", activation)


if __name__ == "__main__":
    unittest.main()
