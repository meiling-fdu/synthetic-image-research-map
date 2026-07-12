import unittest
import json
import shutil
import subprocess
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]


class FrontendChartAndInstitutionFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (REPOSITORY / "web" / "app.js").read_text()
        cls.css = (REPOSITORY / "web" / "style.css").read_text()
        cls.html = (REPOSITORY / "web" / "index.html").read_text()

    def test_all_summary_charts_are_static(self):
        chart_source = self.app[
            self.app.index("function renderTaskChart"):
            self.app.index("function renderHeaderStatistics")
        ]
        for interactive_text in (
            "<button", "aria-pressed", "data-chart-task",
            "data-chart-institution", "data-chart-year",
            "activateChartFilter",
        ):
            self.assertNotIn(interactive_text, chart_source)
        self.assertIn('<span class="task-chart-segment"', chart_source)
        self.assertIn('<div class="institution-chart-row"', chart_source)
        self.assertIn('<div class="year-chart-item"', chart_source)

    def test_top_institutions_retains_compact_static_bar_structure(self):
        self.assertIn(
            '<div class="institution-chart-label"><span class="institution-chart-fill"',
            self.app,
        )
        self.assertIn('<span class="institution-chart-count">', self.app)
        self.assertIn("grid-template-rows: repeat(5, 1fr)", self.css)
        self.assertIn("grid-auto-flow: column", self.css)
        self.assertNotIn(".institution-chart-row.is-selected", self.css)

    def test_exact_institution_filter_is_separate_from_keyword_filter(self):
        matching = self.app[
            self.app.index("function recordMatchesActiveFilters"):
            self.app.index("function normalizedSetSize")
        ]
        self.assertIn("recordInstitutionIdentities(record).has(activeInstitutionFilter.identity)", matching)
        self.assertNotIn("keywordFilter.value =", self.app[
            self.app.index("function applyInstitutionFilter"):
            self.app.index("function renderHeaderStatistics")
        ])
        self.assertIn("data-institution-filter", self.app)
        self.assertIn("institution_id: affiliation.institutionId", self.app)

    def test_affiliation_links_chip_and_reset_are_accessible(self):
        self.assertIn('aria-label="Filter by institution', self.app)
        self.assertIn("active-institution-filter", self.html)
        self.assertIn("data-clear-institution-filter", self.app)
        self.assertIn("activeInstitutionFilter = null", self.app)
        self.assertIn(".active-filter-chip", self.css)
        self.assertIn("button.institution-filter-link", self.css)

    def test_filter_uses_shared_record_and_paper_pipeline(self):
        self.assertIn("matchesInstitutionRecord,\n    matchesPublicPaper", self.app)
        self.assertIn("updateDatasetStatistics(visibleRecords, visiblePaperRecords)", self.app)
        self.assertIn("renderHeaderStatistics(visibleRecords, visiblePaperRecords)", self.app)
        self.assertIn("renderResults(visibleRecords, visiblePaperRecords)", self.app)

    def test_responsive_dimensions_and_asset_versions_are_preserved(self):
        self.assertIn("height: 76px", self.css)
        self.assertIn("min-width: 0", self.css)
        self.assertIn('style.css?v=20260713-exact-institution-filter', self.html)
        self.assertIn('app.js?v=20260713-institution-record-semantics', self.html)

    def test_keyword_search_text_includes_supported_record_fields(self):
        search = self.app[
            self.app.index("function recordSearchText"):
            self.app.index("function yearFilterValue")
        ]
        for field in (
            "recordTitle(record)", "...authors", "record.institution_name",
            "record.institution", "record.venue_name", "record.venue",
            "record.task", "record.subtask", "getEntryTypeLabel",
            "publicationYear(record)",
        ):
            self.assertIn(field, search)

    def test_unified_sets_deduplicate_map_matches_and_keep_standalone_matches(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        start = self.app.index("function deriveFilteredRecordSets")
        end = self.app.index("\nfunction normalizedSetSize", start)
        function_source = self.app[start:end]
        script = f"""
{function_source}
const mapRecords = [
  {{id: 'mapped', institution: 'University of Siena'}},
  {{id: 'mapped', institution: 'University of Siena'}},
  {{id: 'venue-only', institution: 'Elsewhere'}},
];
const papers = [
  {{id: 'mapped', venue: 'Journal'}},
  {{id: 'venue-only', venue: 'University of Siena Press'}},
  {{id: 'standalone', venue: 'University of Siena Proceedings'}},
  {{id: 'duplicate-version', canonical: 'mapped', venue: 'Journal'}},
];
const matches = record => [record.institution, record.venue]
  .filter(Boolean).join(' ').toLowerCase().includes('university of siena');
const identity = record => record.canonical || record.id;
const aggregate = records => [...new Map(records.map(record => [identity(record), record])).values()];
const institutionMatches = record => (record.institution || '').toLowerCase()
  .includes('university of siena');
const result = deriveFilteredRecordSets(
  mapRecords, papers, institutionMatches, matches, identity, aggregate,
);
process.stdout.write(JSON.stringify({{
  recordIds: result.filteredRecords.map(record => record.id),
  paperIds: result.filteredPapers.map(identity),
}}));
"""
        completed = subprocess.run(
            [node, "-e", script], check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["recordIds"], ["mapped", "mapped"])
        self.assertEqual(set(result["paperIds"]), {"mapped", "venue-only", "standalone"})
        self.assertEqual(result["paperIds"].count("mapped"), 1)

    def test_institution_keyword_and_exact_filter_match_only_the_current_row(self):
        render = self.app[
            self.app.index("function renderRecords()"):
            self.app.index("function configureYearRange()")
        ]
        predicate = self.app[
            self.app.index("function recordMatchesActiveFilters"):
            self.app.index("function deriveFilteredRecordSets")
        ]
        self.assertIn("recordInstitutionSearchText(record)", render)
        self.assertIn("{ institutionRecord: true, institutionKeyword }", render)
        self.assertIn("institutionIdentity(record) === activeInstitutionFilter.identity", predicate)
        self.assertIn("recordInstitutionIdentities(record).has(activeInstitutionFilter.identity)", predicate)
        self.assertIn("const visibleRecords = filteredSets.filteredRecords", render)
        self.assertIn("MarkerSizeHelpers.groupInstitutionRecords(\n    visibleRecords", render)

    def test_toggle_and_csv_reuse_the_same_current_filtered_sets(self):
        toggle = self.app[
            self.app.index("function selectResultsView"):
            self.app.index("function baseMapStatusText")
        ]
        export = self.app[
            self.app.index("function downloadFilteredCsv"):
            self.app.index("function formatResolutionValue")
        ]
        self.assertIn("renderResults(currentFilteredRecords, currentFilteredPaperRecords)", toggle)
        self.assertIn("buildCsv(currentDisplayedResults, columns)", export)
        self.assertNotIn("recordMatchesActiveFilters", toggle)


if __name__ == "__main__":
    unittest.main()
