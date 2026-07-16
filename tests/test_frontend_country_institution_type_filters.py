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
  combined: combined.map(paper => paper.id),
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
        self.assertIn('>All countries</option>', self.html)
        self.assertIn('id="institution-type-filter"', self.html)
        self.assertIn('>All institution types</option>', self.html)
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
        self.assertEqual(result["missingTypes"], ["unknown"])
        self.assertEqual(
            result["hierarchyAffiliations"],
            ["institution:parent", "institution:child"],
        )
        self.assertEqual(result["countryCounts"], [
            ["United States", 3], ["China", 2], ["South Korea", 1],
        ])
        self.assertEqual(result["typeCounts"], [
            ["company", 2], ["research_unit", 2], ["university", 2], ["unknown", 1],
        ])
        self.assertEqual(result["combined"], ["alias-paper"])
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
        self.assertIn('["institution_type",', self.app)
        self.assertIn('["institution_types",', self.app)
        self.assertIn('class="affiliation-type"', self.app)
        self.assertIn("second[1] - first[1]", self.app)
        self.assertIn("compareTextValues(labelForValue(first[0])", self.app)
        self.assertIn('countryFilter.addEventListener("change", renderRecords)', self.app)
        self.assertIn(
            'institutionTypeFilter.addEventListener("change", renderRecords)', self.app,
        )


if __name__ == "__main__":
    unittest.main()
