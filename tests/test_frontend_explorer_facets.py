import json
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "web/app.js").read_text()


def function(name):
    signature = "function " + name + "("
    return signature + APP.split(signature, 1)[1].split("\nfunction ", 1)[0]


class FrontendExplorerFacetTests(unittest.TestCase):
    def run_js(self, source):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is not on PATH")
        result = subprocess.run([node, "-e", source], check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def test_disjunctive_counts_ignore_only_their_own_dimension(self):
        # Two mapped affiliations for one paper must not inflate any facet.
        source = r'''
const paperIdentity = record => record.id;
const select = values => ({multiple:true, options:values.map(value => ({value,selected:true}))});
const taskFilter = select(['detection', 'source_attribution']);
const imageScopeFilter = select(['fully_generated']);
const entryTypeFilter = select(['benchmark']);
const venueFilter = {value:'cvpr'}, venueTypeFilter = {value:'conference'};
const countryFilter = {value:'Italy'}, institutionTypeFilter = {value:'university'};
const preprintFilter = {value:'has-arxiv'}, publishedOnlyFilter = {value:'published-only'};
const minYearFilter = {value:'2024'}, maxYearFilter = {value:'2026'};
const yearRangeBounds = {minimum:2020, maximum:2026}, activeInstitutionFilter = null;
const getTasks = r => r.tasks, getImageScopes = r => r.scopes, getPaperCategories = r => r.types;
const venueFilterValue = r => r.venue, recordVenueType = r => r.venueType;
const hasArxivVersion = r => r.arxiv, isFormallyPublished = r => r.published;
const isPublishedOnlySelected = () => publishedOnlyFilter.value === 'published-only';
const publicationYear = r => r.year;
const cachedRecordSearchText = r => r.title || '';
const searchTextMatchesTerms = (text, terms) => terms.every(term => text.includes(term));
const recordMatchesInstitutionDimensions = (r, country, type) =>
  (country === 'all' || r.country === country) && (type === 'all' || r.institutionType === type);
const aggregateUniquePapers = rows => rows;
const base = {id:'base',tasks:['detection','source_attribution'],scopes:['fully_generated'],
  types:['benchmark','method'],venue:'cvpr',venueType:'conference',arxiv:true,published:true,
  year:2025,country:'Italy',institutionType:'university'};
const variants = [
  ['Task', {tasks:['localization']}], ['ImageScope', {scopes:['deepfake']}],
  ['EntryType', {types:['dataset']}], ['Venue', {venue:'eccv'}],
  ['VenueType', {venueType:'journal'}], ['Version', {arxiv:false}],
  ['PublicationStatus', {published:false}], ['Country', {country:'China'}],
  ['InstitutionType', {institutionType:'company'}],
];
const papers = [base, ...variants.map(([id, fields]) => ({...base, ...fields, id})),
  {...base,id:'old',year:2020}];
const records = papers.flatMap(p => [{...p}, {...p}]);
const counts = Object.fromEntries(variants.map(([name]) => {
  const sets = deriveFilteredRecordSets(records,papers,
    r => recordMatchesActiveFilters(r,[],{institutionRecord:true,['ignore'+name]:true}),
    r => recordMatchesActiveFilters(r,[],{['ignore'+name]:true}));
  return [name,sets.filteredPapers.map(paperIdentity)];
}));
const sets = deriveFilteredRecordSets(records,papers,r => recordMatchesActiveFilters(r,[]));
process.stdout.write(JSON.stringify({counts, ordinary:sets.filteredPapers.map(paperIdentity),
  tasks:[...dimensionPaperCounts(sets.filteredPapers,getTasks)],
  keyword:papers.filter(r => recordMatchesActiveFilters(r,['missing'],{ignoreTask:true})).length}));
'''
        helpers = "\n".join(function(name) for name in (
            "selectedFilterValues", "yearFilterValue", "recordMatchesActiveFilters",
            "deriveFilteredRecordSets", "dimensionPaperCounts",
        ))
        result = self.run_js(helpers + source)
        self.assertEqual(result["ordinary"], ["base"])
        for dimension, identities in result["counts"].items():
            self.assertEqual(identities, ["base", dimension])
        self.assertEqual(result["tasks"], [["detection", 1], ["source_attribution", 1]])
        self.assertEqual(result["keyword"], 0)

    def test_zero_options_and_multiselections_survive_count_refresh(self):
        helpers = "\n".join(function(name) for name in (
            "dimensionPaperCounts", "includeZeroCountOptions", "updateStaticFacetCounts",
            "replaceCountedFilterOptions",
        ))
        result = self.run_js(helpers + r'''
const document = {createElement:() => ({})};
const syncFilterDropdownForSelect = () => {};
const select = {value:'retained',options:[],replaceChildren(...options){this.options=options}};
const counts = includeZeroCountOptions(new Map([['available',2]]),
  [{values:['retained','unselected']}],r=>r.values);
replaceCountedFilterOptions(select,'All',[...counts],v=>v);
const multi = {options:[{value:'a',textContent:'A (8)',selected:true},
  {value:'b',textContent:'B (9)',selected:true},{value:'c',textContent:'C',selected:false}]};
updateStaticFacetCounts(multi,new Map([['a',1]]));
process.stdout.write(JSON.stringify({value:select.value,options:select.options,multi:multi.options}));
''')
        self.assertEqual(result["value"], "retained")
        self.assertEqual([o["textContent"] for o in result["options"]],
                         ["All", "available (2)", "retained (0)", "unselected (0)"])
        self.assertEqual([o["textContent"] for o in result["multi"]], ["A (1)", "B (0)", "C (0)"])
        self.assertEqual([o["selected"] for o in result["multi"]], [True, True, False])

    def test_mapped_and_standalone_values_count_each_paper_once(self):
        result = self.run_js(function("dimensionPaperCounts") + r'''
const sources = [
  {id:'one',values:['university']},
  {id:'one',values:['other']},
  {id:'one',values:['other','other']},
  {id:'standalone',values:['other']},
];
process.stdout.write(JSON.stringify([...dimensionPaperCounts(sources,r=>r.values,r=>r.id)]));
''')
        self.assertEqual(result, [["university", 1], ["other", 2]])

    def test_workspace_context_is_compact_and_derived_from_filter_chips(self):
        result = self.run_js(function("workspaceFilterSummary") + r'''
const descriptors = [{key:'keyword',value:'image'}, {key:'tasks',value:'Detection, Localization'},
 {key:'research-types',value:'Benchmarks'}, {key:'year',value:'2024–2026'}, {key:'country',value:'Italy'}];
process.stdout.write(JSON.stringify([
 workspaceFilterSummary([]),workspaceFilterSummary(descriptors),
 workspaceFilterSummary(descriptors.slice(1,4))]));
''')
        self.assertEqual(result, ["", "Detection +1 · Benchmarks · +3 filters",
                                  "Detection +1 · Benchmarks · 2024–2026"])
        self.assertIn("activeFilterChipDescriptors()", function("renderWorkspaceFilterContext"))

    def test_explicit_map_navigation_does_not_mutate_filters(self):
        source = function("fitMapResults") + function("resetMapWorld")
        result = self.run_js(source + r'''
const calls = [], DISPLAY_BOUNDS = 'world';
const minimums = [];
const noWrapMinZoomForWidth = () => 2;
const updateNoWrapMinZoom = () => map.setMinZoom(2);
let fittedZoom = 8;
const map = {fitBounds:(...args)=>calls.push(args), getSize:()=>({x:1440}),
  setMinZoom:zoom=>minimums.push(zoom), getBoundsZoom:()=>fittedZoom};
const L = {latLngBounds:points=>points, point:(x,y)=>({x,y})};
let visibleMarkerEntries = [];
fitMapResults();
const zero = calls.length;
visibleMarkerEntries = [{marker:{getLatLng:()=>[40,10]}}];
fitMapResults();
fittedZoom = 1.5;
fitMapResults(); resetMapWorld();
process.stdout.write(JSON.stringify({zero,calls,minimums}));
''')
        self.assertEqual(result["zero"], 0)
        self.assertEqual(result["calls"][0], [[[40, 10]],
                         {"padding": [36, 36], "maxZoom": 8, "animate": False}])
        self.assertEqual(result["calls"][2][0], "world")
        self.assertEqual(result["minimums"], [0, 2, 0, 1.5, 2])
        render = function("renderRecordsForGeneration")
        self.assertNotIn("fitMapResults()", render)
        self.assertNotIn("fitBounds", render)


if __name__ == "__main__":
    unittest.main()
