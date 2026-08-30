import json
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLED_NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


class FrontendNoResultsRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")

    def node(self, script):
        executable = str(BUNDLED_NODE) if BUNDLED_NODE.exists() else shutil.which("node")
        if not executable:
            self.skipTest("Node.js is unavailable")
        result = subprocess.run(
            [executable, "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def function(self, name, next_name):
        start = self.app.index(f"function {name}")
        end = self.app.index(f"\nfunction {next_name}", start)
        return self.app[start:end]

    def test_empty_state_has_contextual_accessible_recovery_controls(self):
        empty = self.html[
            self.html.index('id="results-empty"'):
            self.html.index("</section>", self.html.index('id="results-empty"'))
        ]
        self.assertIn('aria-labelledby="results-empty-heading"', empty)
        self.assertIn('id="results-empty-summary"', empty)
        self.assertIn('id="undo-last-filter" type="button" hidden', empty)
        self.assertIn('id="clear-empty-filters" type="button" hidden', empty)
        self.assertIn('aria-label="Remove individual filters"', empty)
        self.assertNotIn("No matching records.", self.html)
        self.assertIn('id="results-count" role="status" aria-live="polite" tabindex="-1"', self.html)

    def test_empty_state_reuses_active_filter_descriptors_for_count_and_removal(self):
        source = self.function("renderNoResultsState", "renderResults")
        script = f"""
function element() {{
  return {{
    children: [], dataset: {{}}, hidden: false, textContent: '', attributes: {{}},
    append(...items) {{ this.children.push(...items); }},
    replaceChildren(fragment) {{ this.children = fragment.children; }},
    setAttribute(name, value) {{ this.attributes[name] = value; }},
  }};
}}
const document = {{
  createDocumentFragment: element,
  createElement: element,
}};
const resultsEmptyHeading = element();
const resultsEmptySummary = element();
const resultsEmptyFilterActions = element();
const undoLastFilterButton = element();
const clearEmptyFiltersButton = element();
let lastFilterChange = {{key: 'task'}};
function activeFilterChipDescriptors() {{
  return [
    {{key: 'keyword', category: 'Keyword', value: 'impossible phrase'}},
    {{key: 'year', category: 'Publication Year', value: '2024'}},
  ];
}}
{source}
renderNoResultsState('unique paper');
process.stdout.write(JSON.stringify({{
  heading: resultsEmptyHeading.textContent,
  summary: resultsEmptySummary.textContent,
  undoHidden: undoLastFilterButton.hidden,
  clearHidden: clearEmptyFiltersButton.hidden,
  actions: resultsEmptyFilterActions.children.map(item => ({{
    key: item.children[0].dataset.emptyRemoveFilter,
    text: item.children[0].textContent,
    label: item.children[0].attributes['aria-label'],
  }})),
}}));
"""
        result = self.node(script)
        self.assertEqual(result["heading"], "No matching unique papers")
        self.assertIn("2 active filter/search constraints", result["summary"])
        self.assertFalse(result["undoHidden"])
        self.assertFalse(result["clearHidden"])
        self.assertEqual([action["key"] for action in result["actions"]], ["keyword", "year"])
        self.assertEqual(result["actions"][0]["text"], "Remove Keyword: impossible phrase")
        self.assertIn("Remove Publication Year filter", result["actions"][1]["label"])

    def test_undo_coalesces_search_edits_and_preserves_view_and_sort(self):
        state_source = self.app[
            self.app.index("function currentViewState"):
            self.app.index("\nfunction serializeViewState")
        ]
        undo_source = self.function("undoLastFilterChange", "focusFilterControl")
        script = f"""
const keywordFilter = {{value: ''}};
const taskFilter = {{value: 'all'}};
const entryTypeFilter = {{value: 'all'}};
const venueTypeFilter = {{value: 'all'}};
const venueFilter = {{value: 'all'}};
const countryFilter = {{value: 'all'}};
const institutionTypeFilter = {{value: 'all'}};
const preprintFilter = {{value: 'all'}};
const minYearFilter = {{value: '2018'}};
const maxYearFilter = {{value: '2026'}};
const yearRangeBounds = {{minimum: 2018, maximum: 2026}};
let activeInstitutionFilter = null;
let requestedPaperIdentity = 'paper:kept';
const interactionState = {{detailMode: 'empty', pinnedMapMarkerId: null}};
let resultsView = 'papers';
const sortControl = {{value: 'title-asc'}};
let lastKnownFilterState = null;
let lastFilterChange = null;
let restoringUrlState = false;
let urlUpdates = 0;
let renders = 0;
let focuses = 0;
function currentYearSelection() {{
  return {{start: Number(minYearFilter.value), end: Number(maxYearFilter.value)}};
}}
function restoreViewState(state) {{
  keywordFilter.value = state.keyword;
  taskFilter.value = state.task;
  entryTypeFilter.value = state.paperType;
  venueTypeFilter.value = state.publicationType;
  venueFilter.value = state.venue;
  countryFilter.value = state.country;
  institutionTypeFilter.value = state.institutionType;
  preprintFilter.value = state.version;
  minYearFilter.value = String(state.yearStart);
  maxYearFilter.value = String(state.yearEnd);
  activeInstitutionFilter = state.institution
    ? {{identity: state.institution, label: state.institutionLabel}} : null;
  requestedPaperIdentity = state.paper;
  resultsView = state.view;
  sortControl.value = state.sort;
}}
function requestUrlStateSync(mode) {{ if (mode === 'push') urlUpdates += 1; }}
function renderRecords() {{ renders += 1; }}
function focusResultsRecoveryDestination() {{ focuses += 1; }}
{state_source}
{undo_source}
lastKnownFilterState = currentFilterConstraintState();
keywordFilter.value = 'nothing';
rememberFilterChange('keyword');
keywordFilter.value = 'nothing matches';
rememberFilterChange('keyword', {{coalesce: true}});
const remembered = lastFilterChange;
undoLastFilterChange();
process.stdout.write(JSON.stringify({{
  rememberedBefore: remembered.before.keyword,
  rememberedAfter: remembered.after.keyword,
  keyword: keywordFilter.value,
  view: resultsView,
  sort: sortControl.value,
  paper: requestedPaperIdentity,
  urlUpdates,
  renders,
  focuses,
  undoAvailable: Boolean(lastFilterChange),
}}));
"""
        result = self.node(script)
        self.assertEqual(result["rememberedBefore"], "")
        self.assertEqual(result["rememberedAfter"], "nothing matches")
        self.assertEqual(result["keyword"], "")
        self.assertEqual(result["view"], "papers")
        self.assertEqual(result["sort"], "title-asc")
        self.assertEqual(result["paper"], "paper:kept")
        self.assertEqual((result["urlUpdates"], result["renders"], result["focuses"]), (1, 1, 1))
        self.assertFalse(result["undoAvailable"])

    def test_individual_and_clear_all_actions_use_one_existing_pipeline_pass(self):
        clear_one = self.function("clearActiveFilter", "clearAllActiveFilters")
        clear_all = self.function("clearAllActiveFilters", "focusResultsRecoveryDestination")
        for source in (clear_one, clear_all):
            with self.subTest(action=source.split("(", 1)[0]):
                self.assertEqual(source.count('requestUrlStateSync("push")'), 1)
                self.assertEqual(source.count("renderRecords();"), 1)
                self.assertNotIn("deriveFilteredRecordSets", source)
                self.assertNotIn("recordMatchesActiveFilters", source)
        events = self.app[
            self.app.index('resultsEmpty.addEventListener("click"'):
            self.app.index('copyViewLinkButton.addEventListener', self.app.index('resultsEmpty.addEventListener("click"'))
        ]
        self.assertIn("clearActiveFilter(remove.dataset.emptyRemoveFilter)", events)
        self.assertIn("clearAllActiveFilters();", events)
        self.assertIn("undoLastFilterChange();", events)
        self.assertIn("focusResultsRecoveryDestination();", events)

    def test_recovery_back_to_results_hides_the_empty_panel(self):
        render = self.function("renderResults", "selectResultsView")
        self.assertIn("resultsEmpty.hidden = count !== 0", render)
        self.assertIn("renderNoResultsState(resultNoun);", render)
        self.assertLess(
            render.index("resultsEmpty.hidden = count !== 0"),
            render.index("if (!count)"),
        )
        self.assertIn("resultsList.hidden = false", self.app)

    def test_url_navigation_clears_stale_undo_and_recovery_is_focusable(self):
        restore = self.function("restoreViewStateFromLocation", "renderActiveFilterChips")
        self.assertIn("lastFilterChange = null", restore)
        self.assertIn("requestUrlStateSync(\"push\")", self.function(
            "undoLastFilterChange", "focusFilterControl",
        ))
        self.assertIn("button:not([hidden])", self.function(
            "focusResultsRecoveryDestination", "undoLastFilterChange",
        ))
        self.assertIn("focus({ preventScroll: true })", self.function(
            "focusResultsRecoveryDestination", "undoLastFilterChange",
        ))

    def test_empty_render_does_not_scan_the_dataset_again(self):
        source = self.function("renderNoResultsState", "renderResults")
        self.assertIn("activeFilterChipDescriptors()", source)
        self.assertNotIn("records", source)
        self.assertNotIn("paperRecords", source)
        self.assertNotIn(".filter(", source)
        self.assertNotIn("renderRecords", source)
        self.assertIn(".results-empty-primary-actions", self.css)
        self.assertIn(".results-empty-filter-actions", self.css)
        self.assertIn("min-height: 44px", self.css)


if __name__ == "__main__":
    unittest.main()
