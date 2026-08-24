import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendUrlStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
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

    def serialization_helpers(self):
        order_start = self.app.index("const URL_STATE_PARAMETER_ORDER")
        order_end = self.app.index("\nconst TILE_BOUNDS", order_start)
        helper_start = self.app.index("function serializeViewState")
        helper_end = self.app.index("\nfunction canonicalViewUrl", helper_start)
        return self.app[order_start:order_end] + "\n" + self.app[helper_start:helper_end]

    def test_serialization_round_trip_covers_complete_meaningful_state(self):
        helpers = self.serialization_helpers()
        result = self.run_node(f"""
{helpers}
const state = {{
  keyword: 'synthetic image', task: 'detection', paperType: 'survey',
  publicationType: 'conference', venue: 'CVPR', country: 'Italy',
  institutionType: 'university', version: 'has-arxiv',
  yearStart: 2020, yearEnd: 2024, yearMinimum: 2017, yearMaximum: 2026,
  institution: 'id:https://example.org/i/1', institutionLabel: 'Example University',
  paper: 'doi:10.1000/example',
  view: 'papers', sort: 'title-asc',
}};
const query = serializeViewState(state, 'preview');
console.log(JSON.stringify({{query, parsed: parseViewState(query)}}));
""")
        params = dict(
            pair.split("=", 1) for pair in result["query"].split("&")
        )
        self.assertEqual(params["dataset"], "preview")
        self.assertEqual(
            list(params),
            [
                "dataset", "keyword", "task", "paper_type", "publication_type",
                "venue", "country", "institution_type", "version", "year_start",
                "year_end", "institution", "institution_label", "paper", "view", "sort",
            ],
        )
        parsed = result["parsed"]
        self.assertEqual(parsed["keyword"], "synthetic image")
        self.assertEqual(parsed["paperType"], "survey")
        self.assertEqual(parsed["publicationType"], "conference")
        self.assertEqual((parsed["yearStart"], parsed["yearEnd"]), (2020, 2024))
        self.assertEqual(parsed["institutionLabel"], "Example University")
        self.assertEqual(parsed["paper"], "doi:10.1000/example")
        self.assertEqual((parsed["view"], parsed["sort"]), ("papers", "title-asc"))

    def test_defaults_are_omitted_but_explicit_dataset_is_preserved(self):
        helpers = self.serialization_helpers()
        result = self.run_node(f"""
{helpers}
const defaults = {{
  keyword: '', task: 'all', paperType: 'all', publicationType: 'all', venue: 'all',
  country: 'all', institutionType: 'all', version: 'all',
  yearStart: 2017, yearEnd: 2026, yearMinimum: 2017, yearMaximum: 2026,
  institution: '', institutionLabel: '', paper: '', view: 'institutions', sort: 'year-desc',
}};
console.log(JSON.stringify({{
  preserved: serializeViewState(defaults, 'preview'),
  absent: serializeViewState(defaults, ''),
  invalidYears: parseViewState('?year_start=soon&year_end=20240'),
}}));
""")
        self.assertEqual(result["preserved"], "dataset=preview")
        self.assertEqual(result["absent"], "")
        self.assertIsNone(result["invalidYears"]["yearStart"])
        self.assertIsNone(result["invalidYears"]["yearEnd"])

    def test_restoration_sets_dynamic_controls_years_institution_view_and_sort(self):
        start = self.app.index("function selectContainsValue")
        end = self.app.index("\nfunction requestUrlStateSync", start)
        restoration = self.app[start:end]
        result = self.run_node(f"""
function option(value) {{ return {{value, textContent: value}}; }}
function select(values, value = 'all') {{
  return {{
    value, options: values.map(option),
    append(item) {{ this.options.push(item); }},
  }};
}}
const document = {{createElement: () => option('')}};
const keywordFilter = {{value: ''}};
const taskFilter = select(['all', 'detection']);
const entryTypeFilter = select(['all', 'survey']);
const venueTypeFilter = select(['all']);
const venueFilter = select(['all']);
const countryFilter = select(['all']);
const institutionTypeFilter = select(['all']);
const preprintFilter = select(['all', 'has-arxiv']);
const sortControl = select(['year-desc', 'title-asc'], 'year-desc');
const minYearFilter = {{value: '2017'}};
const maxYearFilter = {{value: '2026'}};
const yearRangeBounds = {{minimum: 2017, maximum: 2026}};
const institutionHierarchy = [];
const resultsViewButtons = [
  {{dataset: {{resultsView: 'institutions'}}, setAttribute(name, value) {{ this.pressed = value; }}}},
  {{dataset: {{resultsView: 'papers'}}, setAttribute(name, value) {{ this.pressed = value; }}}},
];
let resultsView = 'institutions';
let activeInstitutionFilter = null;
let requestedPaperIdentity = '';
let syncYears = 0;
let dropdownSyncs = 0;
const filterDropdowns = [1, 2];
function resetFilterValues() {{}}
function resolveYearSelection(bounds, selection) {{ return selection; }}
function syncYearRange() {{ syncYears += 1; }}
function hierarchyInstitutionLabel() {{ return ''; }}
function syncFilterDropdown() {{ dropdownSyncs += 1; }}
{restoration}
restoreViewState({{
  keyword: 'needle', task: 'detection', paperType: 'survey',
  publicationType: 'conference', venue: 'CVPR', country: 'Italy',
  institutionType: 'university', version: 'has-arxiv',
  yearStart: 2020, yearEnd: 2024, institution: 'id:test',
  institutionLabel: 'Example University', paper: 'doi:10.1000/example',
  view: 'papers', sort: 'title-asc',
}});
console.log(JSON.stringify({{
  keyword: keywordFilter.value, task: taskFilter.value, paperType: entryTypeFilter.value,
  publicationType: venueTypeFilter.value, venue: venueFilter.value,
  country: countryFilter.value, institutionType: institutionTypeFilter.value,
  version: preprintFilter.value, years: [minYearFilter.value, maxYearFilter.value],
  institution: activeInstitutionFilter, resultsView, sort: sortControl.value,
  paper: requestedPaperIdentity,
  pressed: resultsViewButtons.map(button => button.pressed), syncYears, dropdownSyncs,
}}));
""")
        self.assertEqual(result["keyword"], "needle")
        self.assertEqual(result["publicationType"], "conference")
        self.assertEqual(result["venue"], "CVPR")
        self.assertEqual(result["country"], "Italy")
        self.assertEqual(result["institutionType"], "university")
        self.assertEqual(result["years"], ["2020", "2024"])
        self.assertEqual(result["institution"]["label"], "Example University")
        self.assertEqual(result["paper"], "doi:10.1000/example")
        self.assertEqual((result["resultsView"], result["sort"]), ("papers", "title-asc"))
        self.assertEqual(result["pressed"], ["false", "true"])
        self.assertEqual((result["syncYears"], result["dropdownSyncs"]), (1, 2))

    def test_history_sync_is_guarded_and_popstate_restores_once(self):
        start = self.app.index("function requestUrlStateSync")
        end = self.app.index("\nfunction restoreViewStateFromLocation", start)
        sync = self.app[start:end]
        result = self.run_node(f"""
let urlStateReady = true;
let restoringUrlState = false;
let pendingUrlHistoryMode = 'replace';
let lastCanonicalViewUrl = '';
let nextUrl = 'https://example.test/map?task=detection';
const calls = [];
const window = {{
  location: {{href: 'https://example.test/map', search: ''}},
  history: {{
    pushState(state, title, url) {{ calls.push(['push', url]); window.location.href = url; }},
    replaceState(state, title, url) {{ calls.push(['replace', url]); window.location.href = url; }},
  }},
}};
function canonicalViewUrl() {{ return nextUrl; }}
{sync}
requestUrlStateSync('push');
syncUrlFromState();
syncUrlFromState();
restoringUrlState = true;
nextUrl = 'https://example.test/map?task=survey';
syncUrlFromState();
console.log(JSON.stringify({{calls, pendingUrlHistoryMode}}));
""")
        self.assertEqual(result["calls"], [["push", "https://example.test/map?task=detection"]])
        self.assertEqual(result["pendingUrlHistoryMode"], "replace")

        popstate = self.app[
            self.app.index('window.addEventListener("popstate"'):
            self.app.index('window.addEventListener("resize"', self.app.index('window.addEventListener("popstate"'))
        ]
        self.assertIn("restoreViewStateFromLocation()", popstate)
        restoration = self.app[
            self.app.index("function restoreViewStateFromLocation"):
            self.app.index("\nfunction renderActiveFilterChips")
        ]
        self.assertEqual(restoration.count("renderRecords();"), 1)
        self.assertIn("restoringUrlState = true", restoration)
        self.assertIn("restoringUrlState = false", restoration)

    def test_copy_link_uses_the_current_canonical_url_and_reports_accessibly(self):
        self.assertIn('id="copy-view-link"', self.html)
        self.assertIn('id="copy-view-link-status"', self.html)
        self.assertIn('role="status" aria-live="polite"', self.html)
        self.assertIn(".copy-link-button.is-copied", self.css)
        start = self.app.index("async function writeViewUrlToClipboard")
        end = self.app.index("\nfunction showCopyLinkFeedback", start)
        writer = self.app[start:end]
        result = self.run_node(f"""
{writer}
let copied = '';
writeViewUrlToClipboard(
  'https://example.test/map?dataset=preview&task=detection',
  async value => {{ copied = value; }},
).then(() => console.log(JSON.stringify({{copied}})));
""")
        self.assertEqual(
            result["copied"],
            "https://example.test/map?dataset=preview&task=detection",
        )
        copy = self.app[
            self.app.index("async function copyCanonicalViewUrl"):
            self.app.index("\nfunction formatResolutionValue")
        ]
        self.assertIn("const url = canonicalViewUrl();", copy)
        self.assertIn("await writeViewUrlToClipboard(url)", copy)

    def test_startup_restores_before_the_first_render_and_pipeline_syncs_once(self):
        display = self.app[
            self.app.index("function displayDataset"):
            self.app.index("\nasync function loadData")
        ]
        self.assertLess(display.index("configureYearRange()"), display.index("restoreViewState("))
        self.assertLess(display.index("restoreViewState("), display.index("renderRecords();"))
        self.assertEqual(display.count("renderRecords();"), 1)
        pipeline = self.app[
            self.app.index("function renderRecordsForGeneration"):
            self.app.index("\n// A category is active")
        ]
        self.assertEqual(pipeline.count("syncUrlFromState();"), 1)


if __name__ == "__main__":
    unittest.main()
