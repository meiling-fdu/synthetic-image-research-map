import json
import shutil
import subprocess
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]


class FrontendYearRangeSliderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (REPOSITORY / "web" / "app.js").read_text(encoding="utf-8")
        cls.html = (REPOSITORY / "web" / "index.html").read_text(encoding="utf-8")
        cls.css = (REPOSITORY / "web" / "style.css").read_text(encoding="utf-8")
        cls.node = shutil.which("node")

    def run_node(self, script):
        if self.node is None:
            self.skipTest("Node.js is not on PATH")
        result = subprocess.run(
            [self.node, "-e", script], check=True, capture_output=True, text=True,
        )
        return json.loads(result.stdout)

    def year_helper_source(self):
        start = self.app.index("function deriveYearBounds")
        end = self.app.index("\nfunction currentYearSelection", start)
        return self.app[start:end]

    def test_accessible_dual_range_markup_and_distinguishable_handles(self):
        self.assertEqual(self.html.count('type="range"'), 2)
        self.assertNotIn('id="min-year-filter" type="number"', self.html)
        self.assertIn('aria-label="Start publication year"', self.html)
        self.assertIn('aria-label="End publication year"', self.html)
        self.assertIn('id="year-range-value"', self.html)
        self.assertIn('id="year-range-min"', self.html)
        self.assertIn('id="year-range-max"', self.html)
        self.assertIn(".year-range-input-end::-webkit-slider-thumb", self.css)
        self.assertIn("border-radius: 3px", self.css)
        self.assertIn(".year-range-input:focus-visible", self.css)

    def test_dynamic_bounds_default_full_range_and_refresh_preservation(self):
        payload = self.run_node(f"""
function publicationYear(record) {{
  return Number.isInteger(record.year) ? record.year : null;
}}
{self.year_helper_source()}
const firstBounds = deriveYearBounds([
  {{year: 2026}}, {{year: null}}, {{year: 2017}}, {{year: 2021}},
]);
const defaultSelection = resolveYearSelection(firstBounds);
const preserved = resolveYearSelection(
  deriveYearBounds([{{year: 2015}}, {{year: 2028}}]),
  {{start: 2019, end: 2024}},
);
const clamped = resolveYearSelection(
  deriveYearBounds([{{year: 2020}}, {{year: 2025}}]),
  {{start: 2017, end: 2026}},
);
process.stdout.write(JSON.stringify({{firstBounds, defaultSelection, preserved, clamped}}));
""")
        self.assertEqual(payload["firstBounds"], {"minimum": 2017, "maximum": 2026})
        self.assertEqual(payload["defaultSelection"], {"start": 2017, "end": 2026})
        self.assertEqual(payload["preserved"], {"start": 2019, "end": 2024})
        self.assertEqual(payload["clamped"], {"start": 2020, "end": 2025})
        self.assertIn("const previousSelection = yearRangeBounds ? currentYearSelection() : null", self.app)

    def test_start_end_constraints_and_visible_range_sync(self):
        sync_start = self.app.index("function syncYearRange")
        sync_end = self.app.index("\nfunction configureYearRange", sync_start)
        sync_source = self.app[sync_start:sync_end]
        payload = self.run_node(f"""
function clampYear(value, minimum, maximum) {{
  return Math.min(maximum, Math.max(minimum, value));
}}
function input(value) {{
  return {{value: String(value), attributes: {{}}, setAttribute(name, next) {{ this.attributes[name] = next; }}}};
}}
const minYearFilter = input(2025);
const maxYearFilter = input(2023);
const yearRangeValue = {{value: '', textContent: ''}};
const sliderStyle = {{values: {{}}, setProperty(name, value) {{ this.values[name] = value; }}}};
const yearRangeSlider = {{style: sliderStyle}};
const yearRangeBounds = {{minimum: 2017, maximum: 2026}};
{sync_source}
syncYearRange('start');
const afterStart = {{start: minYearFilter.value, end: maxYearFilter.value, label: yearRangeValue.textContent}};
minYearFilter.value = '2024';
maxYearFilter.value = '2020';
syncYearRange('end');
const afterEnd = {{start: minYearFilter.value, end: maxYearFilter.value, label: yearRangeValue.textContent}};
process.stdout.write(JSON.stringify({{afterStart, afterEnd}}));
""")
        self.assertEqual(payload["afterStart"], {"start": "2025", "end": "2025", "label": "2025–2025"})
        self.assertEqual(payload["afterEnd"], {"start": "2020", "end": "2020", "label": "2020–2020"})

    def test_keyboard_arrows_home_end_and_page_keys_respect_constraints(self):
        payload = self.run_node(f"""
function publicationYear(record) {{ return record.year; }}
{self.year_helper_source()}
const keys = ['ArrowLeft', 'ArrowDown', 'ArrowRight', 'ArrowUp', 'Home', 'End', 'PageDown', 'PageUp'];
const values = Object.fromEntries(keys.map(key => [
  key, keyboardYearValue(key, 2020, 2017, 2024, 2),
]));
const constrainedStartEnd = keyboardYearValue('End', 2020, 2017, 2022, 2);
const constrainedEndHome = keyboardYearValue('Home', 2024, 2022, 2026, 2);
process.stdout.write(JSON.stringify({{values, constrainedStartEnd, constrainedEndHome}}));
""")
        self.assertEqual(payload["values"], {
            "ArrowLeft": 2019,
            "ArrowDown": 2019,
            "ArrowRight": 2021,
            "ArrowUp": 2021,
            "Home": 2017,
            "End": 2024,
            "PageDown": 2018,
            "PageUp": 2022,
        })
        self.assertEqual(payload["constrainedStartEnd"], 2022)
        self.assertEqual(payload["constrainedEndHome"], 2022)
        self.assertIn('minYearFilter.addEventListener("keydown"', self.app)
        self.assertIn('maxYearFilter.addEventListener("keydown"', self.app)

    def test_year_combines_with_venue_venue_type_country_and_institution_type(self):
        start = self.app.index("function recordMatchesActiveFilters")
        end = self.app.index("\nfunction dimensionPaperCounts", start)
        matching_source = self.app[start:end]
        payload = self.run_node(f"""
const taskFilter = {{value: 'all'}};
const entryTypeFilter = {{value: 'all'}};
const venueFilter = {{value: 'venue:wifs'}};
const venueTypeFilter = {{value: 'conference'}};
const preprintFilter = {{value: 'all'}};
const countryFilter = {{value: 'Italy'}};
const institutionTypeFilter = {{value: 'university'}};
const minYearFilter = {{value: '2020'}};
const maxYearFilter = {{value: '2024'}};
const activeInstitutionFilter = null;
let yearRangeBounds = null;
function yearFilterValue(input) {{ return Number(input.value); }}
function publicationYear(record) {{ return record.year; }}
function venueFilterValue(record) {{ return record.venue; }}
function recordVenueType(record) {{ return record.venueType; }}
function getEntryType(record) {{ return record.entryType; }}
function recordSearchText() {{ return ''; }}
function searchTextMatchesTerms() {{ return true; }}
function recordMatchesInstitutionIdentities() {{ return true; }}
function recordMatchesInstitutionDimensions(record, country, type) {{
  return (country === 'all' || record.country === country)
    && (type === 'all' || record.institutionType === type);
}}
function isPreprintOnlyRecord() {{ return false; }}
function hasPublishedVenue() {{ return true; }}
function hasArxivVersion() {{ return false; }}
{matching_source}
const records = [
  {{id: 'match', year: 2022, venue: 'venue:wifs', venueType: 'conference', country: 'Italy', institutionType: 'university'}},
  {{id: 'year', year: 2019, venue: 'venue:wifs', venueType: 'conference', country: 'Italy', institutionType: 'university'}},
  {{id: 'venue', year: 2022, venue: 'venue:cvpr', venueType: 'conference', country: 'Italy', institutionType: 'university'}},
  {{id: 'country', year: 2022, venue: 'venue:wifs', venueType: 'conference', country: 'France', institutionType: 'university'}},
  {{id: 'type', year: 2022, venue: 'venue:wifs', venueType: 'conference', country: 'Italy', institutionType: 'company'}},
];
const matches = records.filter(record => recordMatchesActiveFilters(record, [])).map(record => record.id);
yearRangeBounds = {{minimum: 2020, maximum: 2024}};
const unknownYear = {{year: null, venue: 'venue:wifs', venueType: 'conference', country: 'Italy', institutionType: 'university'}};
const unknownAtFullRange = recordMatchesActiveFilters(unknownYear, []);
maxYearFilter.value = '2023';
const unknownAtRestrictedRange = recordMatchesActiveFilters(unknownYear, []);
process.stdout.write(JSON.stringify({{matches, unknownAtFullRange, unknownAtRestrictedRange}}));
""")
        self.assertEqual(payload["matches"], ["match"])
        self.assertTrue(payload["unknownAtFullRange"])
        self.assertFalse(payload["unknownAtRestrictedRange"])

    def test_paper_deduplicated_counts_and_export_use_same_filtered_papers(self):
        derive_start = self.app.index("function deriveFilteredRecordSets")
        derive_end = self.app.index("\nfunction normalizedSetSize", derive_start)
        derive_source = self.app[derive_start:derive_end]
        csv_start = self.app.index("function escapeCsvValue")
        csv_end = self.app.index("\nfunction exportFilename", csv_start)
        csv_source = self.app[csv_start:csv_end]
        payload = self.run_node(f"""
{derive_source}
{csv_source}
const mapRecords = [
  {{paper: 'a', institution: 'one', year: 2022}},
  {{paper: 'a', institution: 'two', year: 2022}},
  {{paper: 'b', institution: 'three', year: 2018}},
];
const papers = [{{paper: 'a', title: 'A', year: 2022}}, {{paper: 'b', title: 'B', year: 2018}}];
const identity = record => record.paper;
const aggregate = records => [...new Map(records.map(record => [record.paper, record])).values()];
const matches = record => record.year >= 2020;
const filtered = deriveFilteredRecordSets(mapRecords, papers, matches, matches, identity, aggregate);
const exportText = buildCsv(filtered.filteredPapers, [['paper', record => record.paper]]);
process.stdout.write(JSON.stringify({{
  mapCount: filtered.filteredRecords.length,
  paperCount: filtered.filteredPapers.length,
  exportedRows: exportText.split('\\r\\n').length - 1,
}}));
""")
        self.assertEqual(payload, {"mapCount": 2, "paperCount": 1, "exportedRows": 1})
        self.assertIn("buildCsv(currentDisplayedResults, columns)", self.app)
        self.assertIn("updateDatasetStatistics(visibleRecords, visiblePaperRecords)", self.app)
        self.assertIn("renderHeaderStatistics(visibleRecords, visiblePaperRecords)", self.app)
        self.assertIn("renderResults(visibleRecords, visiblePaperRecords)", self.app)


if __name__ == "__main__":
    unittest.main()
