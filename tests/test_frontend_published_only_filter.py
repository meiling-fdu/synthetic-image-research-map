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

    def test_control_is_compact_accessible_off_by_default_and_in_requested_order(self):
        record_version = self.html.index(">Record Version</span>")
        published_only = self.html.index('id="published-only-filter"')
        publication_year = self.html.index(">Publication Year</legend>")
        self.assertLess(record_version, published_only)
        self.assertLess(published_only, publication_year)
        self.assertIn(
            '<label class="published-only-filter" for="published-only-filter">', self.html
        )
        self.assertIn('id="published-only-filter" type="checkbox" disabled', self.html)
        self.assertNotIn('id="published-only-filter" type="checkbox" checked', self.html)
        self.assertIn(".published-only-filter {", self.css)
        self.assertIn("min-height: 24px", self.css)

    def test_canonical_dataset_has_only_resolved_publication_types(self):
        counts = {}
        for paper in self.public_papers:
            publication_type = paper.get("publication_type", "")
            counts[publication_type] = counts.get(publication_type, 0) + 1
        self.assertEqual(
            counts,
            # Canonical paper records by controlled publication type after the
            # eight main-track conference additions.
            {"conference": 358, "journal": 161, "preprint": 62, "book": 1},
        )
        self.assertEqual(counts["preprint"], 62)
        published_only_count = sum(
            counts[key] for key in ("conference", "journal", "book")
        )
        self.assertEqual(published_only_count, 520)

    def test_predicate_semantics_and_filter_composition(self):
        helper = self.app[
            self.app.index("function isFormallyPublished"):
            self.app.index("\nfunction isBookRecord")
        ]
        predicate = self.app[
            self.app.index("function recordMatchesActiveFilters"):
            self.app.index("\nfunction dimensionPaperCounts")
        ]
        result = self.run_node(f"""
{helper}
{predicate}
const taskFilter = {{value: 'all'}};
const entryTypeFilter = {{selectedOptions: [{{value: 'all'}}]}};
const venueTypeFilter = {{value: 'all'}};
const venueFilter = {{value: 'all'}};
const preprintFilter = {{value: 'all'}};
const publishedOnlyFilter = {{checked: false}};
const minYearFilter = {{value: '2023'}};
const maxYearFilter = {{value: '2025'}};
const countryFilter = {{value: 'all'}};
const institutionTypeFilter = {{value: 'all'}};
const yearRangeBounds = {{minimum: 2023, maximum: 2025}};
const activeInstitutionFilter = null;
function recordMatchesInstitutionIdentities() {{ return true; }}
function searchTextMatchesTerms() {{ return true; }}
function cachedRecordSearchText() {{ return ''; }}
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
publishedOnlyFilter.checked = true;
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

    def test_state_reset_and_url_round_trip_are_integrated(self):
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
        self.assertIn("publishedOnlyFilter.checked = false", reset)
        self.assertIn('[publishedOnlyFilter, "published-only"]', self.app)

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
