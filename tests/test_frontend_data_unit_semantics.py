import json
import pathlib
import re
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendDataUnitSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")

    def function_block(self, start, end):
        start_index = self.app.index(f"function {start}")
        return self.app[start_index:self.app.index(f"function {end}", start_index)]

    def test_summary_and_chart_copy_names_the_aggregation_unit(self):
        overview = self.html[
            self.html.index('<div class="dataset-overview"'):
            self.html.index('<div class="map-status-row"')
        ]
        self.assertEqual(
            re.findall(r"<dt>([^<]+)</dt>", overview),
            ["Institution Records", "Unique Papers", "Unique Institutions", "Countries"],
        )
        for heading in (
            "Unique Papers by Forensic Task",
            "Top Institutions by Unique Papers",
            "Unique Papers by Year",
        ):
            self.assertIn(heading, self.html)

        chart_source = self.app[
            self.app.index("function renderTaskChart"):
            self.app.index("function hasResolutionMetadata")
        ]
        self.assertIn("unique paper", chart_source)
        self.assertNotRegex(chart_source, r'data-chart-tooltip="[^\n]*?\\bpaper\\$')
        self.assertNotRegex(chart_source, r'aria-label="[^\n]*?\\bpaper\\$')

    def test_filtered_counts_and_charts_update_from_the_same_record_sets(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")

        statistics = self.function_block("updateDatasetStatistics", "renderChartEmpty")
        charts = self.app[
            self.app.index("function renderChartEmpty"):
            self.app.index("function hasResolutionMetadata")
        ]
        script = f"""
const datasetRecordCount = {{textContent: ''}};
const datasetPaperCount = {{textContent: ''}};
const datasetInstitutionCount = {{textContent: ''}};
const datasetCountryCount = {{textContent: ''}};
const taskChartContent = {{innerHTML: ''}};
const institutionChartContent = {{innerHTML: ''}};
const yearChartContent = {{innerHTML: ''}};
const taskFilter = {{value: 'all'}};
let activeInstitutionFilter = null;
const currentYearSelection = () => ({{start: 2018, end: 2026}});
const TASK_COLORS = {{
  detection: '#1', source_attribution: '#2',
  detection_and_source_attribution: '#3',
}};
const escapeHtml = value => String(value);
const recordInstitution = record => record.institution;
const institutionIdentity = record => record.institution;
const paperIdentity = record => record.paper;
const recordCountry = record => record.country;
const publicationYear = record => record.year;
const compareTextValues = (first, second) => first.localeCompare(second);
const normalizedSetSize = values => new Set(values.filter(Boolean)).size;
const paperListRecordsForDisplay = records => [
  ...new Map(records.map(record => [paperIdentity(record), record])).values(),
];
{statistics}
{charts}
const records = [
  {{paper: 'p1', institution: 'Alpha', country: 'US', task: 'detection', year: 2022}},
  {{paper: 'p1', institution: 'Beta', country: 'GB', task: 'detection', year: 2022}},
  {{paper: 'p2', institution: 'Alpha', country: 'US', task: 'source_attribution', year: 2023}},
];
// This mirrors deriveFilteredRecordSets: one entry per paper identity.
const papers = [records[0], records[2]];
const snapshot = () => ({{
  records: datasetRecordCount.textContent,
  papers: datasetPaperCount.textContent,
  institutions: datasetInstitutionCount.textContent,
  countries: datasetCountryCount.textContent,
  task: taskChartContent.innerHTML,
  institution: institutionChartContent.innerHTML,
  year: yearChartContent.innerHTML,
}});
updateDatasetStatistics(records, papers);
renderHeaderStatistics(records, papers);
const all = snapshot();
updateDatasetStatistics(records.slice(0, 2), papers.slice(0, 1));
renderHeaderStatistics(records.slice(0, 2), papers.slice(0, 1));
process.stdout.write(JSON.stringify({{all, filtered: snapshot()}}));
"""
        result = json.loads(subprocess.run(
            [node, "-e", script], check=True, capture_output=True, text=True,
        ).stdout)

        self.assertEqual(
            {key: result["all"][key] for key in ("records", "papers", "institutions", "countries")},
            {"records": 3, "papers": 2, "institutions": 2, "countries": 2},
        )
        self.assertEqual(
            {key: result["filtered"][key] for key in ("records", "papers", "institutions", "countries")},
            {"records": 2, "papers": 1, "institutions": 2, "countries": 2},
        )
        self.assertIn("Alpha — 2 unique papers", result["all"]["institution"])
        self.assertIn("Alpha — 1 unique paper", result["filtered"]["institution"])
        self.assertIn("2 filtered unique papers", result["all"]["task"])
        self.assertIn("1 filtered unique paper", result["filtered"]["task"])
        self.assertIn("2023 — 1 unique paper", result["all"]["year"])
        self.assertNotIn("2023", result["filtered"]["year"])

    def test_results_view_uses_the_matching_collection_and_unit_label(self):
        render = self.function_block("renderResults", "selectResultsView")
        self.assertIn(
            'const displayedResults = resultsView === "papers"\n'
            "    ? paperListRecordsForDisplay(visiblePaperRecords)\n"
            "    : visibleRecords;",
            render,
        )
        self.assertIn(
            'const resultNoun = resultsView === "papers" ? "unique paper" : "institution record";',
            render,
        )
        self.assertIn("const count = displayedResults.length", render)

        filtered_pipeline = self.app[
            self.app.index("function renderRecords()"):
            self.app.index("function configureYearRange()")
        ]
        for call in (
            "updateDatasetStatistics(visibleRecords, visiblePaperRecords)",
            "renderHeaderStatistics(visibleRecords, visiblePaperRecords)",
            "renderResults(visibleRecords, visiblePaperRecords, activeGeneration)",
        ):
            self.assertIn(call, filtered_pipeline)


if __name__ == "__main__":
    unittest.main()
