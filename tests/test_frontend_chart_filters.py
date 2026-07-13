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
        self.assertIn("recordMatchesInstitutionIdentities(", matching)
        self.assertIn("activeInstitutionIdentities", matching)
        self.assertNotIn("keywordFilter.value =", self.app[
            self.app.index("function applyInstitutionFilter"):
            self.app.index("function clearInstitutionFilter")
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
        self.assertIn('style.css?v=20260713-public-overview', self.html)
        self.assertIn('app.js?v=20260714-paper-version-links', self.html)

    def test_public_overview_omits_non_map_metric_and_explanation(self):
        self.assertNotIn("Papers without map location", self.html)
        self.assertNotIn("dataset-paper-without-location-count", self.html)
        self.assertNotIn("datasetPaperWithoutLocationCount", self.app)
        self.assertNotIn(
            "Paper coverage includes records without map markers; map records require institution coordinates.",
            self.app,
        )

    def test_overview_metrics_redistribute_without_responsive_wrapping(self):
        statistics = self.css[
            self.css.index(".dataset-statistics {"):
            self.css.index(".dataset-statistics dt")
        ]
        self.assertIn("display: flex", statistics)
        self.assertIn("flex-wrap: nowrap", statistics)
        self.assertIn("flex: 1 1 0", statistics)
        self.assertIn("overflow-x: auto", statistics)

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

    def test_alias_resolution_and_exact_filter_match_canonical_identity(self):
        render = self.app[
            self.app.index("function renderRecords()"):
            self.app.index("function configureYearRange()")
        ]
        predicate = self.app[
            self.app.index("function recordMatchesActiveFilters"):
            self.app.index("function deriveFilteredRecordSets")
        ]
        self.assertIn("buildInstitutionSearchIndex(", render)
        self.assertIn("resolveInstitutionSearch(", render)
        self.assertIn("resolvedInstitutionIdentities", render)
        self.assertIn("activeInstitutionIdentities", render)
        self.assertIn("recordMatchesInstitutionIdentities(", predicate)
        self.assertIn("const visibleRecords = filteredSets.filteredRecords", render)
        self.assertIn("MarkerSizeHelpers.groupInstitutionRecords(\n    visibleRecords", render)

    def test_confirmed_hierarchy_automatically_expands_top_level_parent(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        start = self.app.index("function buildInstitutionHierarchyIndex")
        end = self.app.index("\nfunction yearFilterValue", start)
        source = self.app[start:end]
        script = r'''
function institutionIdentity(record) {
  return record.institution_id ? `id:${record.institution_id.toLowerCase()}` : "";
}
function recordInstitutionIdentities(record) {
  return new Set(record.institution_ids || [institutionIdentity(record)]);
}
''' + source + r'''
const parent = 'id:institution:parent';
const child = 'id:institution:child';
const grandchild = 'id:institution:grandchild';
const sibling = 'id:institution:sibling';
const unrelatedParent = 'id:institution:unrelated-parent';
const unrelatedChild = 'id:institution:unrelated-child';
const relationships = [
  {parent_institution_id: 'institution:parent', child_institution_id: 'institution:child', review_status: 'confirmed'},
  {parent_institution_id: 'institution:child', child_institution_id: 'institution:grandchild', review_status: 'confirmed'},
  {parent_institution_id: 'institution:parent', child_institution_id: 'institution:sibling', review_status: 'pending_review'},
  {parent_institution_id: 'institution:unrelated-parent', child_institution_id: 'institution:unrelated-child', review_status: 'confirmed'},
];
const index = buildInstitutionHierarchyIndex(relationships);
const expanded = institutionIdentityWithDescendants(parent, index);
const childOnly = institutionIdentityWithDescendants(child, index);
process.stdout.write(JSON.stringify({
  expanded: [...expanded].sort(),
  childOnly: [...childOnly].sort(),
  parentMatchesChildExpanded: recordMatchesInstitutionIdentities(
    {institution_id: 'institution:child'}, expanded, true,
  ),
  rejectedIncluded: expanded.has(sibling),
  childIncludesParent: childOnly.has(parent),
  unrelatedIncluded: expanded.has(unrelatedParent) || expanded.has(unrelatedChild),
}));
'''
        completed = subprocess.run(
            [node, "-e", script], check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["expanded"], [
            "id:institution:child",
            "id:institution:grandchild",
            "id:institution:parent",
        ])
        self.assertEqual(result["childOnly"], ["id:institution:child"])
        self.assertTrue(result["parentMatchesChildExpanded"])
        self.assertFalse(result["rejectedIncluded"])
        self.assertFalse(result["childIncludesParent"])
        self.assertFalse(result["unrelatedIncluded"])

    def test_no_hierarchy_checkbox_or_related_state_is_rendered(self):
        combined = "\n".join((self.app, self.css, self.html))
        for removed in (
            "Include affiliated institutes",
            "data-include-affiliated-institutes",
            "includeAffiliatedInstitutes",
            "hierarchyExpansionIdentity",
            "hierarchy-expansion-control",
        ):
            self.assertNotIn(removed, combined)

    def test_automatic_hierarchy_expansion_shared_outputs_use_one_filtered_set(self):
        self.assertIn("institution_hierarchy", self.app)
        render = self.app[
            self.app.index("function renderRecords()"):
            self.app.index("function configureYearRange()")
        ]
        for consumer in (
            "updateDatasetStatistics(visibleRecords, visiblePaperRecords)",
            "renderHeaderStatistics(visibleRecords, visiblePaperRecords)",
            "renderResults(visibleRecords, visiblePaperRecords)",
            "MarkerSizeHelpers.groupInstitutionRecords(\n    visibleRecords",
        ):
            self.assertIn(consumer, render)

        csv_source = self.app[
            self.app.index("function downloadFilteredCsv"):
            self.app.index("function renderResults")
        ]
        self.assertIn("currentDisplayedResults", csv_source)
        results_source = self.app[
            self.app.index("function renderResults"):
            self.app.index("function selectResultsView")
        ]
        self.assertIn("currentDisplayedResults", results_source)

    def test_default_institution_counts_and_top_chart_keep_ids_separate(self):
        chart = self.app[
            self.app.index("function renderInstitutionChart"):
            self.app.index("function renderYearChart")
        ]
        statistics = self.app[
            self.app.index("function updateDatasetStatistics"):
            self.app.index("function renderChartEmpty")
        ]
        self.assertIn("const key = institutionIdentity(record)", chart)
        self.assertIn("datasetRecords.map(institutionIdentity)", statistics)
        self.assertNotIn("institutionIdentityWithDescendants", chart)
        self.assertNotIn("institutionIdentityWithDescendants", statistics)

    def test_hierarchy_is_not_used_by_affiliation_canonicalization(self):
        resolver = self.app[
            self.app.index("function buildCanonicalInstitutionResolver"):
            self.app.index("function recordSearchText")
        ]
        self.assertNotIn("institutionHierarchy", resolver)
        self.assertNotIn("hierarchy.forEach", resolver)
        self.assertIn("buildCanonicalInstitutionResolver(aliases)", resolver)

    def test_institution_alias_search_normalization_and_exact_resolution(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        functions = []
        for start_name, end_name in (
            ("function normalizedTitle", "function paperIdentity"),
            ("function recordInstitution(", "function recordCountry"),
            ("function institutionIdentity", "function affiliationIdentity"),
            ("function normalizedSearchText", "function recordSearchText"),
        ):
            start = self.app.index(start_name)
            end = self.app.index(end_name, start)
            functions.append(self.app[start:end])
        script = "\n".join(functions) + r'''
const maps = [
  {id: 'p1', institution: 'Université de Montréal', institution_id: 'institution:um'},
  {id: 'p1', institution: 'Université de Montréal', institution_id: 'institution:um'},
  {id: 'p2', institution: 'Université de Montréal Hospital', institution_id: 'institution:hospital'},
];
const papers = [
  {id: 'p1', author_institution_affiliations: [{institution: 'Université de Montréal', institution_id: 'institution:um'}]},
  {id: 'p3', author_institution_affiliations: [{institution: 'Université de Montréal', institution_id: 'institution:um'}]},
];
const aliases = [
  {alias_name: 'UdeM', canonical_institution_name: 'Université de Montréal', canonical_institution_id: 'institution:um'},
  {alias_name: 'University of Montreal', canonical_institution_name: 'Université de Montréal', canonical_institution_id: 'institution:um'},
  {alias_name: 'Université de Montréal (former)', canonical_institution_name: 'Université de Montréal', canonical_institution_id: 'institution:um'},
];
const index = buildInstitutionSearchIndex(maps, papers, aliases);
const resolved = ['UNIVERSITE-DE-MONTREAL', 'udem', 'University of Montreal', 'Université de Montréal (former)']
  .map(value => resolveInstitutionSearch(value, index));
process.stdout.write(JSON.stringify({
  normalized: normalizedSearchText('  École—Supérieure...  '),
  resolved,
  unrelated: resolveInstitutionSearch('Université de Montréal Hosp', index),
  paperMatches: papers.filter(paper => recordInstitutionIdentities(paper).has(resolved[0])).map(paper => paper.id),
}));
'''
        completed = subprocess.run(
            [node, "-e", script], check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["normalized"], "ecole superieure")
        self.assertEqual(result["resolved"], ["id:institution:um"] * 4)
        self.assertEqual(result["unrelated"], "")
        self.assertEqual(result["paperMatches"], ["p1", "p3"])

    def test_public_payload_preserves_alias_metadata(self):
        self.assertIn("payload.institution_aliases", self.app)
        self.assertIn("canonical_institution_id", self.app)
        self.assertIn("institutionAliases = normalizedData.institutionAliases", self.app)

    def test_frontend_defensively_consolidates_astar_records_and_papers(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        slices = []
        for start_name, end_name in (
            ("function institutionIdentity", "function affiliationIdentity"),
            ("function normalizedIdentityValue", "function recordCountry"),
            ("function normalizedSearchText", "function recordSearchText"),
        ):
            start = self.app.index(start_name)
            end = self.app.index(end_name, start)
            slices.append(self.app[start:end])
        script = r'''
function normalizedDoi(value) { return String(value || ''); }
function recordPaperUrl(record) { return record.paper_url || ''; }
function recordTitle(record) { return record.title || ''; }
function recordInstitutionAuthors(record) { return record.institution_authors || []; }
''' + "\n".join(slices) + r'''
const canonicalName = 'Agency for Science, Technology and Research (A*STAR)';
const canonicalId = 'institution:e81a0314e783d8a4';
const aliases = [
  {alias_name: 'A*STAR', canonical_institution_name: canonicalName, canonical_institution_id: canonicalId},
  {alias_name: 'Agency for Science, Technology and Research', canonical_institution_name: canonicalName, canonical_institution_id: canonicalId},
];
const maps = [
  {title: 'Alias paper', year: 2024, doi: '10.1/alias', institution: 'A*STAR', institution_id: 'institution:old', institution_authors: ['Alias Author']},
  {title: 'Alias paper', year: 2024, doi: '10.1/alias', institution: 'Agency for Science, Technology and Research', institution_id: 'institution:expanded', institution_authors: ['Expanded Author']},
  {title: 'Other paper', year: 2025, doi: '10.1/other', institution: 'A*STAR', institution_id: 'institution:old', institution_authors: ['Other Author']},
  {title: 'Multi paper', year: 2025, doi: '10.1/multi', institution: 'Other University', institution_id: 'institution:other', institution_authors: ['Multi Author']},
];
const papers = [
  {title: 'Alias paper', year: 2024, doi: '10.1/alias', map_record_count: 2, aggregated_institutions: ['A*STAR', 'Agency for Science, Technology and Research'], author_institution_affiliations: [
    {institution: 'A*STAR', institution_id: 'institution:old'},
    {institution: 'Agency for Science, Technology and Research', institution_id: 'institution:expanded'},
  ]},
  {title: 'Other paper', year: 2025, doi: '10.1/other', map_record_count: 1, author_institution_affiliations: [{institution: 'A*STAR', institution_id: 'institution:old'}]},
];
const canonicalized = canonicalizePublicDataset(maps, papers, aliases);
const index = buildInstitutionSearchIndex(canonicalized.mapRecords, canonicalized.paperRecords, aliases);
const aliasIdentity = resolveInstitutionSearch('A*STAR', index);
const canonicalIdentity = resolveInstitutionSearch(canonicalName, index);
const matchingPapers = canonicalized.paperRecords
  .filter(paper => recordInstitutionIdentities(paper).has(aliasIdentity))
  .map(paperIdentity).sort();
process.stdout.write(JSON.stringify({
  mapCount: canonicalized.mapRecords.length,
  astarMapCount: canonicalized.mapRecords.filter(record => institutionIdentity(record) === aliasIdentity).length,
  astarNames: [...new Set(canonicalized.mapRecords.filter(record => institutionIdentity(record) === aliasIdentity).map(recordInstitution))],
  authors: canonicalized.mapRecords.find(record => record.doi === '10.1/alias').institution_authors.sort(),
  paperInstitutions: canonicalized.paperRecords[0].aggregated_institutions,
  paperMapCount: canonicalized.paperRecords[0].map_record_count,
  aliasIdentity,
  canonicalIdentity,
  matchingPapers,
  partial: resolveInstitutionSearch('Agency for Science', index),
}));
'''
        completed = subprocess.run(
            [node, "-e", script], check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["mapCount"], 3)
        self.assertEqual(result["astarMapCount"], 2)
        self.assertEqual(result["astarNames"], ["Agency for Science, Technology and Research (A*STAR)"])
        self.assertEqual(result["authors"], ["Alias Author", "Expanded Author"])
        self.assertEqual(result["paperInstitutions"], ["Agency for Science, Technology and Research (A*STAR)"])
        self.assertEqual(result["paperMapCount"], 1)
        self.assertEqual(result["aliasIdentity"], result["canonicalIdentity"])
        self.assertEqual(result["matchingPapers"], ["doi:10.1/alias", "doi:10.1/other"])
        self.assertEqual(result["partial"], "")

    def test_counts_markers_and_csv_use_canonical_identity(self):
        statistics = self.app[
            self.app.index("function updateDatasetStatistics"):
            self.app.index("function renderChartEmpty")
        ]
        chart = self.app[
            self.app.index("function renderInstitutionChart"):
            self.app.index("function renderYearChart")
        ]
        self.assertIn("datasetRecords.map(institutionIdentity)", statistics)
        self.assertIn("const key = institutionIdentity(record)", chart)
        self.assertIn('["institution_id", (record)', self.app)
        self.assertIn('["institution_ids", (record)', self.app)
        self.assertIn("MarkerSizeHelpers.groupInstitutionRecords(\n    visibleRecords,\n    institutionIdentity", self.app)

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

    def test_paper_coverage_results_and_csv_keep_matching_non_map_papers(self):
        statistics_start = self.app.index("function updateDatasetStatistics(")
        statistics = self.app[
            statistics_start:
            self.app.index("function renderTaskChart", statistics_start)
        ]
        render = self.app[
            self.app.index("function renderRecords()"):
            self.app.index("function configureYearRange()")
        ]
        self.assertIn("datasetPaperCount.textContent = paperCoverageRecords.length", statistics)
        self.assertIn("const matchesPublicPaper", render)
        self.assertIn("currentFilteredPaperRecords = visiblePaperRecords", render)
        self.assertIn("renderResults(visibleRecords, visiblePaperRecords)", render)
        self.assertIn('resultsView === "papers"\n    ? PAPER_CSV_COLUMNS', self.app)

        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        derive_start = self.app.index("function deriveFilteredRecordSets")
        derive_end = self.app.index("\nfunction normalizedSetSize", derive_start)
        csv_start = self.app.index("function escapeCsvValue")
        csv_end = self.app.index("\nfunction exportFilename", csv_start)
        script = f"""
{self.app[derive_start:derive_end]}
{self.app[csv_start:csv_end]}
const maps = [{{id: 'mapped', title: 'Mapped detection'}}];
const papers = [
  {{id: 'mapped', title: 'Mapped detection', has_map_location: true}},
  {{id: 'non-map', title: 'Needle attribution study', has_map_location: false}},
];
const matchesKeyword = record => record.title.toLowerCase().includes('needle');
const result = deriveFilteredRecordSets(
  maps, papers, matchesKeyword, matchesKeyword, record => record.id, records => records,
);
const csv = buildCsv(result.filteredPapers, [
  ['title', record => record.title],
  ['has_map_location', record => String(record.has_map_location)],
]);
process.stdout.write(JSON.stringify({{
  mapRecords: result.filteredRecords.length,
  papers: result.filteredPapers.map(record => record.id),
  csv,
}}));
"""
        completed = subprocess.run(
            [node, "-e", script], check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["mapRecords"], 0)
        self.assertEqual(result["papers"], ["non-map"])
        self.assertIn("Needle attribution study,false", result["csv"])

    def test_map_records_and_markers_remain_institution_record_based(self):
        statistics_start = self.app.index("function updateDatasetStatistics(")
        statistics = self.app[
            statistics_start:
            self.app.index("function renderTaskChart", statistics_start)
        ]
        render = self.app[
            self.app.index("function renderRecords()"):
            self.app.index("function configureYearRange()")
        ]
        self.assertIn("datasetRecordCount.textContent = datasetRecords.length", statistics)
        self.assertIn("groupInstitutionRecords(\n    visibleRecords", render)
        self.assertIn("visibleMarkerEntries.push", render)


if __name__ == "__main__":
    unittest.main()
