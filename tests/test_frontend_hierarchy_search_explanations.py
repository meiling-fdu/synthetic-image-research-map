import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendHierarchySearchExplanationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
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

    def hierarchy_helpers(self):
        start = self.app.index("function institutionIdentityWithDescendants")
        end = self.app.index("\nfunction hierarchyInstitutionLabel", start)
        return self.app[start:end]

    def test_direct_descendant_multiple_multilevel_and_unrelated_matches(self):
        helpers = self.hierarchy_helpers()
        result = self.run_node(rf'''
const canonicalInstitutionSearchIndex = {{
  parent: {{canonical_name: 'Parent University'}},
  child: {{canonical_name: 'Child Laboratory'}},
  second: {{canonical_name: 'Second Laboratory'}},
  grandchild: {{canonical_name: 'Grandchild Center'}},
  unrelated: {{canonical_name: 'Unrelated Institute'}},
}};
const institutionHierarchy = [];
function institutionIdentity(record) {{
  return record.institution_id ? `id:${{record.institution_id.toLowerCase()}}` : '';
}}
function recordInstitution(record) {{ return record.institution || ''; }}
function recordInstitutionIdentities(record) {{
  return new Set((record.actual || [record.institution_id]).filter(Boolean).map(
    institution_id => institutionIdentity({{institution_id}}),
  ));
}}
function hierarchyInstitutionLabel() {{ return ''; }}
function searchTextMatchesTerms(text, terms) {{ return terms.every(term => text.includes(term)); }}
function cachedRecordSearchText(record) {{ return record.searchText || ''; }}
{helpers}
const index = new Map([
  ['id:parent', new Set(['id:child', 'id:second'])],
  ['id:child', new Set(['id:grandchild'])],
]);
const roots = new Set(['id:parent']);
function context(record) {{
  return buildInstitutionMatchContext(
    record, [record], ['parent'], roots, '', index,
  );
}}
const direct = context({{actual: ['parent'], searchText: ''}});
const descendant = context({{actual: ['child'], searchText: ''}});
const both = context({{actual: ['parent', 'child'], searchText: ''}});
const multiple = context({{actual: ['child', 'second'], searchText: ''}});
const multilevel = context({{actual: ['grandchild'], searchText: ''}});
const unrelatedKeyword = context({{actual: ['unrelated'], searchText: 'parent'}});
process.stdout.write(JSON.stringify({{
  direct,
  descendant,
  both,
  multiple,
  multilevel,
  unrelatedKeyword,
}}));
''')
        self.assertEqual(result["direct"]["type"], "direct")
        self.assertEqual(result["descendant"]["type"], "descendant")
        self.assertEqual(
            [item["name"] for item in result["descendant"]["descendants"]],
            ["Child Laboratory"],
        )
        self.assertEqual(result["both"]["type"], "direct")
        self.assertEqual(result["both"]["descendants"], [])
        self.assertEqual(
            {item["name"] for item in result["multiple"]["descendants"]},
            {"Child Laboratory", "Second Laboratory"},
        )
        self.assertEqual(
            [item["name"] for item in result["multilevel"]["descendants"]],
            ["Grandchild Center"],
        )
        self.assertIsNone(result["unrelatedKeyword"])

    def test_active_parent_filter_marks_descendant_even_with_unrelated_keyword_text(self):
        helpers = self.hierarchy_helpers()
        result = self.run_node(rf'''
const canonicalInstitutionSearchIndex = {{
  parent: {{canonical_name: 'Parent'}}, child: {{canonical_name: 'Child'}},
}};
const institutionHierarchy = [];
function institutionIdentity(record) {{ return record.institution_id ? `id:${{record.institution_id}}` : ''; }}
function recordInstitution() {{ return ''; }}
function recordInstitutionIdentities(record) {{ return new Set(record.actual.map(id => `id:${{id}}`)); }}
function hierarchyInstitutionLabel() {{ return ''; }}
function searchTextMatchesTerms() {{ return true; }}
function cachedRecordSearchText() {{ return 'unrelated'; }}
{helpers}
const index = new Map([['id:parent', new Set(['id:child'])]]);
const record = {{actual: ['child']}};
const match = buildInstitutionMatchContext(
  record, [record], ['unrelated'], new Set(), 'id:parent', index,
);
process.stdout.write(JSON.stringify(match));
''')
        self.assertEqual(result["type"], "descendant")

    def test_paper_deduplication_and_csv_keep_actual_child_relationship(self):
        derive_start = self.app.index("function deriveFilteredRecordSets")
        derive_end = self.app.index("\nfunction normalizedSetSize", derive_start)
        derive = self.app[derive_start:derive_end]
        columns_start = self.app.index("const INSTITUTION_CSV_COLUMNS")
        columns_end = self.app.index("\nconst PAPER_CSV_COLUMNS", columns_start)
        columns = self.app[columns_start:columns_end]
        csv_start = self.app.index("function escapeCsvValue")
        csv_end = self.app.index("\nfunction exportFilename", csv_start)
        csv_helpers = self.app[csv_start:csv_end]
        result = self.run_node(rf'''
function paperIdentity(record) {{ return record.paper_id; }}
function aggregateUniquePapers(rows) {{ return [rows[0]]; }}
{derive}
const mapRows = [
  {{paper_id: 'paper-1', institution_id: 'child', institution: 'Child Laboratory'}},
  {{paper_id: 'paper-1', institution_id: 'second', institution: 'Second Laboratory'}},
];
const papers = [{{paper_id: 'paper-1'}}];
const filtered = deriveFilteredRecordSets(mapRows, papers, () => true, () => true);
let institutionMatchContextByRecord = new WeakMap();
institutionMatchContextByRecord.set(mapRows[0], {{
  type: 'descendant',
  parents: [{{name: 'Parent University'}}],
  descendants: [{{name: 'Child Laboratory'}}],
}});
function recordTitle() {{ return ''; }}
function recordAuthors() {{ return []; }}
function recordInstitutionAuthors() {{ return []; }}
function publicationYear() {{ return null; }}
function venueDisplayLabel() {{ return ''; }}
function isBookRecord() {{ return false; }}
function getRecordVenue() {{ return ''; }}
function recordVenueType() {{ return ''; }}
function canonicalVenueTrack() {{ return ''; }}
function getPaperCategories() {{ return []; }}
function recordInstitution(record) {{ return record.institution; }}
function normalizeInstitutionType() {{ return ''; }}
function normalizedDoi() {{ return ''; }}
function recordArxivId() {{ return ''; }}
function recordArxivUrl() {{ return ''; }}
function recordPaperUrl() {{ return ''; }}
{columns}
{csv_helpers}
const selectedColumns = INSTITUTION_CSV_COLUMNS.filter(([name]) => [
  'institution_name', 'institution_id', 'match_type',
  'matched_parent_institution', 'matched_descendant_institutions',
].includes(name));
process.stdout.write(JSON.stringify({{
  paperCount: filtered.filteredPapers.length,
  csv: buildCsv([mapRows[0]], selectedColumns),
}}));
''')
        self.assertEqual(result["paperCount"], 1)
        self.assertEqual(
            result["csv"].splitlines(),
            [
                "institution_name,institution_id,match_type,matched_parent_institution,matched_descendant_institutions",
                "Child Laboratory,child,descendant,Parent University,Child Laboratory",
            ],
        )
        self.assertNotIn("Parent University,parent", result["csv"])

    def test_explanation_is_descendant_only_and_url_state_remains_authoritative(self):
        helper_start = self.app.index("function institutionMatchExplanationHtml")
        helper_end = self.app.index("\nfunction institutionResultContent", helper_start)
        helper = self.app[helper_start:helper_end]
        result = self.run_node(rf'''
let institutionMatchContextByRecord = new WeakMap();
function escapeHtml(value) {{ return String(value); }}
{helper}
const direct = {{}};
const descendant = {{}};
institutionMatchContextByRecord.set(direct, {{
  type: 'direct', parents: [{{name: 'Parent'}}], descendants: [],
}});
institutionMatchContextByRecord.set(descendant, {{
  type: 'descendant', parents: [{{name: 'Parent'}}], descendants: [{{name: 'Child'}}],
}});
process.stdout.write(JSON.stringify({{
  direct: institutionMatchExplanationHtml(direct),
  descendant: institutionMatchExplanationHtml(descendant),
}}));
''')
        self.assertEqual(result["direct"], "")
        self.assertIn("Matched via", result["descendant"])
        self.assertIn("Child", result["descendant"])
        self.assertIn("Parent", result["descendant"])
        self.assertIn("result-institution-match-context", self.css)
        self.assertIn("institution: state.institution", self.app)
        self.assertIn('if (value) params.set(key, value)', self.app)
        self.assertIn("activeInstitutionFilter?.identity", self.app)


if __name__ == "__main__":
    unittest.main()
