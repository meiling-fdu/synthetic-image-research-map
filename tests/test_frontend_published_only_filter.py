import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendPublishedOnlyFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        payload = json.loads(
            (ROOT / "web" / "data" / "public_preview_papers.json").read_text(
                encoding="utf-8"
            )
        )
        cls.public_papers = payload["records"]
        cls.node = shutil.which("node")

    def run_node(self, source):
        if self.node is None:
            self.skipTest("Node.js is not on PATH")
        completed = subprocess.run(
            [self.node, "-e", source], check=True, capture_output=True, text=True
        )
        return json.loads(completed.stdout)

    def test_control_is_a_standard_publication_status_dropdown_in_requested_order(self):
        record_version = self.html.index(">Record Version</span>")
        published_only = self.html.index('id="published-only-filter"')
        publication_year = self.html.index(">Publication Year</legend>")
        self.assertLess(publication_year, record_version)
        self.assertLess(published_only, publication_year)
        self.assertIn(
            '<span id="published-only-filter-label" class="filter-label">Publication Status</span>',
            self.html,
        )
        self.assertIn(
            '<select id="published-only-filter" aria-labelledby="published-only-filter-label" disabled>',
            self.html,
        )
        self.assertIn('<option value="all">All</option>', self.html)
        self.assertIn('<option value="published-only">Published only</option>', self.html)
        self.assertNotIn('id="published-only-filter" type="checkbox"', self.html)
        self.assertNotIn(".published-only-filter {", self.css)
        self.assertIn(".filter-dropdown-field {", self.css)
        self.assertIn(".filter-grid select,", self.css)

    def test_canonical_dataset_has_only_resolved_publication_types(self):
        counts = {}
        for paper in self.public_papers:
            publication_type = paper.get("publication_type", "")
            counts[publication_type] = counts.get(publication_type, 0) + 1
        self.assertEqual(
            counts,
            # The NORMAL evidence successor adds nine conferences.
            {"conference": 389, "journal": 165, "preprint": 111, "book": 1},
        )
        self.assertEqual(counts["preprint"], 111)
        published_only_count = sum(
            counts[key] for key in ("conference", "journal", "book")
        )
        self.assertEqual(published_only_count, 555)

    def test_predicate_semantics_and_filter_composition(self):
        helper = self.app[
            self.app.index("function isFormallyPublished"):
            self.app.index("\nfunction isBookRecord")
        ]
        predicate = self.app[
            self.app.index("function recordMatchesActiveFilters"):
            self.app.index("\nfunction dimensionPaperCounts")
        ]
        publication_status = self.app[
            self.app.index("function isPublishedOnlySelected"):
            self.app.index("\nconst resetButton")
        ]
        result = self.run_node(f"""
{helper}
{publication_status}
{predicate}
const taskFilter = {{value: 'all'}};
const imageScopeFilter = {{selectedOptions: [{{value: 'all'}}]}};
const entryTypeFilter = {{selectedOptions: [{{value: 'all'}}]}};
const venueTypeFilter = {{value: 'all'}};
const venueFilter = {{value: 'all'}};
const preprintFilter = {{value: 'all'}};
const publishedOnlyFilter = {{value: 'all'}};
const minYearFilter = {{value: '2023'}};
const maxYearFilter = {{value: '2025'}};
const countryFilter = {{value: 'all'}};
const institutionTypeFilter = {{value: 'all'}};
const yearRangeBounds = {{minimum: 2023, maximum: 2025}};
const activeInstitutionFilter = null;
function recordMatchesInstitutionIdentities() {{ return true; }}
function searchTextMatchesTerms() {{ return true; }}
function cachedRecordSearchText() {{ return ''; }}
function selectedFilterValues() {{ return []; }}
function getTasks() {{ return []; }}
function getImageScopes() {{ return []; }}
function getPaperCategories(record) {{ return record.paper_categories; }}
function venueFilterValue(record) {{ return record.venue; }}
function recordVenueType(record) {{ return record.publication_type; }}
function hasArxivVersion(record) {{ return record.has_arxiv_version; }}
function publicationYear(record) {{ return record.year; }}
function yearFilterValue(input) {{ return Number(input.value); }}
function recordMatchesInstitutionDimensions() {{ return true; }}
const records = [
  {{id:'preprint', publication_type:'preprint', venue:'arXiv', year:2024,
    has_arxiv_version:true, paper_categories:['method']}},
  {{id:'conference', publication_type:'conference', venue:'CVPR', year:2024,
    has_arxiv_version:false, paper_categories:['method']}},
  {{id:'journal', publication_type:'journal', venue:'TIFS', year:2023,
    has_arxiv_version:false, paper_categories:['survey']}},
  {{id:'dual', publication_type:'conference', venue:'ECCV', year:2025,
    has_arxiv_version:true, paper_categories:['method']}},
];
const ids = () => records.filter(record => recordMatchesActiveFilters(record, [])).map(r => r.id);
const off = ids();
publishedOnlyFilter.value = 'published-only';
const on = ids();
venueTypeFilter.value = 'conference';
const conference = ids();
venueTypeFilter.value = 'all'; venueFilter.value = 'ECCV';
const venue = ids();
venueFilter.value = 'all'; preprintFilter.value = 'has-arxiv';
const version = ids();
preprintFilter.value = 'all'; minYearFilter.value = '2024'; maxYearFilter.value = '2024';
const year = ids();
process.stdout.write(JSON.stringify({{
  off, on, conference, venue, version, year,
  formal: records.map(record => isFormallyPublished(record)),
}}));
""")
        self.assertEqual(result["off"], ["preprint", "conference", "journal", "dual"])
        self.assertEqual(result["on"], ["conference", "journal", "dual"])
        self.assertEqual(result["conference"], ["conference", "dual"])
        self.assertEqual(result["venue"], ["dual"])
        self.assertEqual(result["version"], ["dual"])
        self.assertEqual(result["year"], ["conference"])
        self.assertEqual(result["formal"], [False, True, True, True])

    def test_load_switch_reset_and_url_round_trip_are_integrated(self):
        order = self.app[
            self.app.index("const URL_STATE_PARAMETER_ORDER"):
            self.app.index("\nconst PAPER_ISSUE_URL")
        ]
        helpers = self.app[
            self.app.index("function serializeViewState"):
            self.app.index("\nfunction canonicalViewUrl")
        ]
        result = self.run_node(f"""
{order}
{helpers}
const state = {{keyword:'', task:'all', paperType:'all', publicationType:'all',
  venue:'all', country:'all', institutionType:'all', version:'all', publishedOnly:true,
  yearStart:2020, yearEnd:2025, yearMinimum:2020, yearMaximum:2025,
  institution:'', institutionLabel:'', marker:'', paper:'', view:'institutions', sort:'year-desc'}};
const query = serializeViewState(state);
process.stdout.write(JSON.stringify({{query, restored:parseViewState(query)}}));
""")
        self.assertEqual(result["query"], "published_only=1")
        self.assertTrue(result["restored"]["publishedOnly"])
        self.assertFalse(self.run_node(f"""
{order}
{helpers}
process.stdout.write(JSON.stringify(parseViewState('').publishedOnly));
"""))
        reset = self.app[
            self.app.index("function resetFilterValues"):
            self.app.index("\nfunction clearActiveFilter")
        ]
        self.assertIn('publishedOnlyFilter.value = "all"', reset)
        self.assertIn('[publishedOnlyFilter, "published-only"]', self.app)
        clear = self.app.split('} else if (key === "published-only") {', 1)[1].split('} else', 1)[0]
        self.assertIn('syncFilterDropdownForSelect(publishedOnlyFilter)', clear)
        restore = self.app[
            self.app.index("function restoreViewState"):
            self.app.index("\nfunction restoreViewStateFromLocation")
        ]
        self.assertIn(
            'publishedOnlyFilter.value = state.publishedOnly === true ? "published-only" : "all";',
            restore,
        )

    def test_responsive_filter_drawer_uses_the_same_control_system(self):
        self.assertIn(
            '<div class="filter-dropdown-field" data-filter-dropdown>\n'
            '              <span id="published-only-filter-label"',
            self.html,
        )
        mobile = self.css.split("@media (max-width: 820px)", 1)[1]
        self.assertIn(".filters-panel-content {", mobile)
        self.assertIn(".filters-panel-actions {", mobile)

    def test_every_paper_dependent_view_consumes_the_shared_filtered_sets(self):
        render = self.app[
            self.app.index("function renderRecordsForGeneration"):
            self.app.index("\n// A category is active")
        ]
        self.assertEqual(render.count("const filteredSets = deriveFilteredRecordSets("), 1)
        self.assertIn("const visibleRecords = filteredSets.filteredRecords", render)
        self.assertIn("const visiblePaperRecords = filteredSets.filteredPapers", render)
        self.assertIn("groupInstitutionRecords(\n    visibleRecords", render)
        self.assertIn("updateDatasetStatistics(visibleRecords, visiblePaperRecords)", render)
        self.assertIn("renderHeaderStatistics(visibleRecords, visiblePaperRecords)", render)
        self.assertIn("renderResults(visibleRecords, visiblePaperRecords, activeGeneration)", render)
        self.assertIn("filteredSets.matchingPaperIdentities", render)


if __name__ == "__main__":
    unittest.main()
