import json
import shutil
import subprocess
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]


class FrontendCountryInstitutionTypeFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (REPOSITORY / "web" / "app.js").read_text()
        cls.html = (REPOSITORY / "web" / "index.html").read_text()
        cls.css = (REPOSITORY / "web" / "style.css").read_text()

    def run_filter_helpers(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        constants = self.app[
            self.app.index("const INSTITUTION_TYPE_LABELS"):
            self.app.index("\nfunction noWrapMinZoomForWidth")
        ]
        helpers = self.app[
            self.app.index("function normalizedLocationName"):
            self.app.index("\nfunction recordLocation")
        ]
        counts = self.app[
            self.app.index("function dimensionPaperCounts"):
            self.app.index("\nfunction deriveFilteredRecordSets")
        ]
        script = f"""
{constants}
function normalizedTitle(value) {{ return String(value || '').toLowerCase(); }}
function recordInstitution(record) {{ return String(record.institution || record.institution_name || '').trim(); }}
function institutionIdentity(record) {{
  const id = String(record.institution_id || record.canonical_institution_id || '').trim();
  return id ? `id:${{id.toLowerCase()}}` : `name:${{normalizedTitle(recordInstitution(record))}}`;
}}
function uniqueTextValues(values) {{
  const seen = new Set();
  return values.filter(value => {{
    const key = String(value || '').trim().toLowerCase();
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  }});
}}
function compareTextValues(first, second) {{
  return String(first || '').localeCompare(String(second || ''), undefined, {{sensitivity: 'base'}});
}}
{helpers}
{counts}
const papers = [
  {{id: 'alias-paper', affiliations: [
    {{name: 'Example U', institution_id: 'institution:u', country: 'CN', institution_type: 'Education', authors: ['A']}},
    {{name: 'Example University', institution_id: 'institution:u', country: 'China', institution_type: 'university', authors: ['A', 'A']}},
  ]}},
  {{id: 'company-paper', affiliations: [
    {{name: 'Example Co', institution_id: 'institution:co', country: 'US', institution_type: 'corporate'}},
  ]}},
  {{id: 'multi-paper', affiliations: [
    {{name: 'Korea Lab', institution_id: 'institution:kr', country: 'KR', institution_type: 'research-unit'}},
    {{name: 'US Company', institution_id: 'institution:us', country: 'United States', country_code: 'US', institution_type: 'company'}},
  ]}},
  {{id: 'unknown-paper', affiliations: [
    {{name: 'Mystery', institution_id: 'institution:mystery', country: 'CN'}},
    {{name: 'Mystery Alias', institution_id: 'institution:mystery', country: 'China', institution_type: 'other'}},
  ]}},
  {{id: 'hierarchy-paper', affiliations: [
    {{name: 'Parent University', institution_id: 'institution:parent', country: 'US', institution_type: 'university'}},
    {{name: 'Child Lab', institution_id: 'institution:child', country: 'US', institution_type: 'research_unit'}},
  ]}},
];
const countryCounts = sortedDimensionCounts(dimensionPaperCounts(papers, paper => countriesForRecord(paper)));
const typeCounts = sortedDimensionCounts(
  dimensionPaperCounts(papers, paper => institutionTypesForRecord(paper)), institutionTypeLabel,
);
const combined = papers.filter(paper => recordMatchesInstitutionDimensions(
  paper, 'China', 'university', false,
));
const combinedOther = papers.filter(paper => recordMatchesInstitutionDimensions(
  paper, 'China', 'other', false,
));
const tieCounts = sortedDimensionCounts(new Map([['China', 2], ['Canada', 2], ['Italy', 3]]));
process.stdout.write(JSON.stringify({{
  normalization: ['CN', 'US', 'KR'].map(code => canonicalCountryName(code)),
  aliasAffiliations: dimensionAffiliations(papers[0]).length,
  multiCountries: countriesForRecord(papers[2]),
  normalizedTypes: ['Education', 'research-unit', 'corporate'].map(normalizeInstitutionType),
  missingTypes: institutionTypesForRecord(papers[3]),
  hierarchyAffiliations: dimensionAffiliations(papers[4]).map(value => value.institution_id),
  countryCounts,
  typeCounts,
  orderedTypeCounts: sortedInstitutionTypeCounts(new Map([
    ['company', 4], ['other', 1], ['university', 2], ['research_unit', 3],
  ])),
  combined: combined.map(paper => paper.id),
  combinedOther: combinedOther.map(paper => paper.id),
  crossAffiliationMismatch: recordMatchesInstitutionDimensions(
    papers[2], 'South Korea', 'company', false,
  ),
  hierarchyEntityMismatch: recordMatchesInstitutionDimensions(
    papers[4], 'United States', 'research_unit', false,
    new Set(['id:institution:parent']),
  ),
  markerMatch: recordMatchesInstitutionDimensions(
    {{institution: 'US Company', country: 'US', institution_type: 'company'}},
    'United States', 'company', true,
  ),
  markerMismatch: recordMatchesInstitutionDimensions(
    {{institution: 'Korea Lab', country: 'KR', institution_type: 'research_unit'}},
    'United States', 'research_unit', true,
  ),
  tieCounts,
}}));
"""
        result = subprocess.run(
            [node, "-e", script], check=True, capture_output=True, text=True,
        )
        return json.loads(result.stdout)

    def test_dropdowns_are_compact_defaults_near_institution_filters(self):
        self.assertIn('id="country-filter"', self.html)
        self.assertIn('id="country-filter"', self.html)
        self.assertIn('id="country-combobox-button"', self.html)
        self.assertIn('role="combobox"', self.html)
        self.assertIn('role="listbox"', self.html)
        self.assertNotIn('id="country-combobox-search"', self.html)
        self.assertNotIn('role="searchbox"', self.html)
        self.assertIn('id="institution-type-filter"', self.html)
        self.assertNotIn("All Countries", self.html)
        self.assertNotIn("All Institution Types", self.html)
        self.assertLess(
            self.html.index('id="country-filter"'),
            self.html.index('id="institution-type-filter"'),
        )

    def test_country_type_normalization_counts_and_combination(self):
        result = self.run_filter_helpers()
        self.assertEqual(
            result["normalization"], ["China", "United States", "South Korea"],
        )
        self.assertEqual(result["aliasAffiliations"], 1)
        self.assertEqual(result["multiCountries"], ["South Korea", "United States"])
        self.assertEqual(
            result["normalizedTypes"], ["university", "research_unit", "company"],
        )
        self.assertEqual(result["missingTypes"], ["other"])
        self.assertEqual(
            result["hierarchyAffiliations"],
            ["institution:parent", "institution:child"],
        )
        self.assertEqual(result["countryCounts"], [
            ["United States", 3], ["China", 2], ["South Korea", 1],
        ])
        self.assertEqual(result["typeCounts"], [
            ["company", 2], ["research_unit", 2], ["university", 2], ["other", 1],
        ])
        self.assertEqual(result["orderedTypeCounts"], [
            ["university", 2], ["research_unit", 3], ["company", 4], ["other", 1],
        ])
        self.assertEqual(result["combined"], ["alias-paper"])
        self.assertEqual(result["combinedOther"], ["unknown-paper"])
        self.assertFalse(result["crossAffiliationMismatch"])
        self.assertFalse(result["hierarchyEntityMismatch"])
        self.assertTrue(result["markerMatch"])
        self.assertFalse(result["markerMismatch"])
        self.assertEqual(
            result["tieCounts"], [["Italy", 3], ["Canada", 2], ["China", 2]],
        )

    def test_filters_share_all_visible_output_pipelines(self):
        matching = self.app[
            self.app.index("function recordMatchesActiveFilters"):
            self.app.index("function deriveFilteredRecordSets")
        ]
        for existing_filter in (
            "matchesTask", "matchesEntryType", "matchesVenue", "matchesVersion",
            "matchesMinimumYear", "matchesMaximumYear", "matchesInstitution",
        ):
            self.assertIn(existing_filter, matching)
        self.assertIn("recordMatchesInstitutionDimensions(", matching)

        render = self.app[
            self.app.index("function renderRecords()"):
            self.app.index("function configureYearRange()")
        ]
        self.assertIn("MarkerSizeHelpers.groupInstitutionRecords(\n    visibleRecords", render)
        self.assertIn("updateDatasetStatistics(visibleRecords, visiblePaperRecords)", render)
        self.assertIn("renderHeaderStatistics(visibleRecords, visiblePaperRecords)", render)
        self.assertIn("renderResults(visibleRecords, visiblePaperRecords)", render)
        self.assertIn("updateInstitutionDimensionFilters(", render)
        self.assertIn("currentFilteredRecords = visibleRecords", render)
        self.assertIn("currentFilteredPaperRecords = visiblePaperRecords", render)
        self.assertIn("currentDisplayedResults", self.app)
        self.assertIn("buildCsv(currentDisplayedResults, columns)", self.app)
        self.assertIn("renderInstitutionChart(datasetRecords)", self.app)

    def test_rendering_and_csv_include_readable_types_deterministically(self):
        self.assertIn('research_unit: "Research unit"', self.app)
        self.assertIn('other: "Other"', self.app)
        self.assertIn(
            'const INSTITUTION_TYPE_ORDER = ["university", "research_unit", "company", "other"]',
            self.app,
        )
        self.assertNotIn('unknown: "Unknown"', self.app)
        self.assertIn('["institution_type",', self.app)
        self.assertIn('["institution_types",', self.app)
        self.assertIn('class="affiliation-type"', self.app)
        self.assertIn("sortedInstitutionTypeCounts(typeCounts)", self.app)
        self.assertIn("compareTextValues(labelForValue(first[0])", self.app)
        self.assertIn('countryFilter.addEventListener("change", renderRecords)', self.app)
        self.assertIn(
            'institutionTypeFilter.addEventListener("change", renderRecords)', self.app,
        )

    def test_country_panel_height_and_internal_scrolling(self):
        panel = self.css[
            self.css.index(".country-combobox-panel {"):
            self.css.index(".country-combobox-panel[hidden]")
        ]
        options = self.css[
            self.css.index(".country-combobox-options {"):
            self.css.index(".country-combobox-option {")
        ]
        self.assertIn("max-height: min(420px, 60vh)", panel)
        self.assertIn("overflow: hidden", panel)
        self.assertIn("overflow-y: auto", options)
        self.assertIn("overscroll-behavior: contain", options)

    def test_keyboard_and_upward_placement_helpers(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        source = self.app[
            self.app.index("function nextCountryOptionIndex"):
            self.app.index("\nfunction countryOptionElements")
        ]
        script = f"""
{source}
process.stdout.write(JSON.stringify({{
  arrowDown: nextCountryOptionIndex([0, 1, 2], 1, 1),
  arrowUpWrap: nextCountryOptionIndex([0, 1, 2], 0, -1),
  upward: countryComboboxPlacement(
    {{left: 300, top: 730, bottom: 770, width: 220}}, 400, 800, 800,
  ),
  narrow: countryComboboxPlacement(
    {{left: 280, top: 100, bottom: 140, width: 220}}, 300, 320, 700,
  ),
}}));
"""
        completed = subprocess.run(
            [node, "-e", script], check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["arrowDown"], 2)
        self.assertEqual(result["arrowUpWrap"], 2)
        self.assertEqual(result["upward"]["placement"], "up")
        self.assertLess(result["upward"]["top"], 730)
        self.assertGreaterEqual(result["narrow"]["left"], 8)
        self.assertLessEqual(
            result["narrow"]["left"] + result["narrow"]["width"], 312,
        )

    def test_selection_escape_and_outside_click_use_shared_filter_state(self):
        selection = self.app[
            self.app.index("function selectCountryComboboxValue"):
            self.app.index("\nfunction updateInstitutionDimensionFilters")
        ]
        events = self.app[self.app.index('countryFilter.addEventListener("change"'):]
        self.assertIn("countryFilter.value = value", selection)
        self.assertIn('dispatchEvent(new Event("change", { bubbles: true }))', selection)
        self.assertIn("closeCountryCombobox(true)", selection)
        self.assertIn('event.key === "Escape"', events)
        self.assertIn("closeCountryCombobox(true)", events)
        self.assertIn('document.addEventListener("pointerdown"', events)
        self.assertIn("!countryCombobox.contains(event.target)", events)
        self.assertIn("setActiveCountryOption(selectedIndex, true)", self.app)
        self.assertNotIn("filterCountryComboboxOptions", self.app)
        self.assertIn(
            'replaceCountedFilterOptions(\n    countryFilter,\n    "All",',
            self.app,
        )
        self.assertIn(
            'sortedDimensionCounts(countryCounts),\n    (value) => value,\n    false,',
            self.app,
        )

    def test_country_trigger_matches_native_filter_control_geometry_and_states(self):
        select = self.css[self.css.index("select {"):self.css.index("\ninput {", self.css.index("select {"))]
        button = self.css[
            self.css.index(".country-combobox-button {"):
            self.css.index(".country-combobox-button > span:first-child")
        ]
        for declaration in (
            "height: 35px", "border-radius: 5px", "font-size: 0.8rem",
            "font-weight: 400",
        ):
            self.assertIn(declaration, select)
            self.assertIn(declaration, button)
        self.assertIn("background-size: 4px 5px, 4px 5px", select)
        self.assertIn("border-right: 4px solid transparent", self.css)
        self.assertIn("button:hover:not(:disabled)", self.css)
        self.assertIn("button:focus-visible", self.css)
        self.assertIn("button:disabled,\nselect:disabled", self.css)
        self.assertIn('.country-combobox-option[aria-selected="true"]', self.css)


if __name__ == "__main__":
    unittest.main()
