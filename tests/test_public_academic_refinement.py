import json
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "web/app.js").read_text()


def function(name):
    start = APP.index(f"function {name}(")
    boundaries = [APP.find(prefix, start + 1) for prefix in ("\nfunction ", "\nasync function ")]
    return APP[start:min(end for end in boundaries if end >= 0)]


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.targets = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag in ("a", "link", "script"):
            self.targets.append(attrs.get("href", attrs.get("src", "")))


class PublicAcademicRefinementTests(unittest.TestCase):
    def run_js(self, body):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Use the established Node runtime on PATH")
        result = subprocess.run([node, "-e", body], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_brand_scope_legend_and_current_view(self):
        html = (ROOT / "web/index.html").read_text()
        self.assertIn('<title>Synthetic Image Forensics Research Map</title>', html)
        heading = re.search(r'<h1 class="header-title">(.*?)</h1>', html, re.S)
        self.assertIsNotNone(heading)
        self.assertEqual(re.sub(r'<[^>]+>', '', heading.group(1)).strip(),
                         'Synthetic Image Forensics Research Map')
        scope = " ".join(html.split('<h3>Scope</h3>')[1].split('</section>')[0].split())
        for text in ("fully generated images", "clearly tied to synthetic-image forensics",
                     "not automatically in scope", "watermarking", "active provenance", "fingerprint embedding"):
            self.assertIn(text, scope)
        legend = html.split('aria-label="Map legend"')[1].split('id="map-status"')[0]
        for text in ("Detection", "Source Attribution", "Localization", "Mixed / multiple tasks",
                     "shared color", "Unknown", "more unique papers in the current filtered view"):
            self.assertIn(text, legend)
        self.assertIn('>Current view</p>', html)
        self.assertIn('Top Mapped Institutions', html)
        self.assertIn('not a quality or impact ranking', html)
        self.assertIn('background: var(--map-unknown-fill)', (ROOT / 'web/style.css').read_text())

    def test_exact_identifier_variants_and_existing_search_fields(self):
        source = "\n".join(function(name) for name in (
            "normalizedSearchText", "recordTitle", "recordAuthors", "getRecordYear",
            "publicationYear", "isBookRecord", "recordSearchText", "searchTextMatchesTerms"))
        result = self.run_js("""
const PaperSearchHelpers = require('./web/paper_search_helpers.js');
const TitleMarkup = require('./web/title_markup.js');
const getTasks=r=>r.tasks||[], getImageScopes=r=>r.image_scopes||[], getPaperCategories=r=>r.research_types||[];
const formatPublicTask=t=>t, getEntryTypeLabel=t=>t, IMAGE_SCOPE_LABELS={fully_generated:'Fully Generated'};
""" + source + """
const record={title:'Synthetic Image Analysis', authors:['Alice Example'], venue:'CVPR', year:2026,
  abstract:'Unusual spectral evidence', doi:'10.1234/Example', arxiv_id:'2607.12052', tasks:['detection']};
const search=recordSearchText(record);
const queries=['10.1234/example','DOI:10.1234/Example','https://doi.org/10.1234%2FExample',
 '2607.12052','arXiv:2607.12052','https://arxiv.org/abs/2607.12052',
 'https://arxiv.org/pdf/2607.12052v2.pdf','spectral','Alice Example','Synthetic Image','CVPR','2026','Detection'];
console.log(JSON.stringify({matches:queries.map(q=>searchTextMatchesTerms(search,PaperSearchHelpers.queryTerms(q,normalizedSearchText))),
 falseDoi:searchTextMatchesTerms(recordSearchText({...record,doi:'10.1234/example2'}),PaperSearchHelpers.queryTerms('10.1234/example',normalizedSearchText)),
 falseArxiv:searchTextMatchesTerms(search,PaperSearchHelpers.queryTerms('2607.12053',normalizedSearchText))}));
""")
        self.assertEqual(result['matches'], [True] * 13)
        self.assertFalse(result['falseDoi'])
        self.assertFalse(result['falseArxiv'])

    def test_relevance_weights_and_deterministic_ties(self):
        result = self.run_js("""
const helpers=require('./web/paper_search_helpers.js');
const normalize=s=>String(s||'').toLowerCase().trim().replace(/[^a-z0-9]+/g,' ');
const base={title:'',identifiers:[],authors:'',institutions:'',venue:'',taxonomy:'',abstract:'',year:''};
const score=(fields,q='image forensics')=>helpers.relevanceScore({...base,...fields},q,normalize);
const values=[score({title:'image forensics'}),score({title:'image forensics methods'}),
 score({title:'an image forensics study'}),score({authors:'image forensics'}),
 score({institutions:'image forensics'}),score({venue:'image forensics'}),
 score({taxonomy:'image forensics'}),score({abstract:'image forensics'})];
function recordRelevance(r){return r.score}
function recordTitle(r){return r.title}
function paperIdentity(r){return r.id}
function recordSearchCacheId(r){return r.id}
""" + function('getRecordYear') + function('compareTextValues') + function('compareRecordsForSort') + """
const records=[{id:'z',title:'B',year:2025,score:16},{id:'b',title:'A',year:2025,score:16},
 {id:'a',title:'A',year:2025,score:16},{id:'new',title:'Z',year:2026,score:16},
 {id:'exact',title:'Z',year:2020,score:10000}];
const sorted=rows=>rows.sort((a,b)=>compareRecordsForSort(a,b,'relevance')).map(r=>r.id);
console.log(JSON.stringify({values,identifier:score({identifiers:['doi:10.1234/test']},'https://doi.org/10.1234/test'),
 moreTerms:score({title:'an image forensics study'})>score({title:'image',abstract:'forensics'}),
 sorted:sorted([...records]),reverse:sorted([...records].reverse())}));
""")
        self.assertEqual(result['values'], sorted(result['values'], reverse=True))
        self.assertEqual(result['identifier'], 9000)
        self.assertTrue(result['moreTerms'])
        self.assertEqual(result['sorted'], ['exact', 'new', 'a', 'b', 'z'])
        self.assertEqual(result['sorted'], result['reverse'])

    def test_auto_sort_and_explicit_url_states(self):
        order = APP[APP.index('const URL_STATE_PARAMETER_ORDER'):APP.index('const TILE_BOUNDS')]
        result = self.run_js(order + function('serializeViewState') + function('parseViewState') + function('syncAutomaticSort') + """
let explicitSortSelection=false;
const sortControl={value:'year-desc'}, keywordFilter={value:''};
function syncFilterDropdownForSelect(){}
const steps=[];
syncAutomaticSort();steps.push(sortControl.value);
keywordFilter.value='image';syncAutomaticSort();steps.push(sortControl.value);
keywordFilter.value='';syncAutomaticSort();steps.push(sortControl.value);
explicitSortSelection=true;sortControl.value='year-asc';keywordFilter.value='image';syncAutomaticSort();steps.push(sortControl.value);
keywordFilter.value='';syncAutomaticSort();steps.push(sortControl.value);
const defaults=parseViewState('');
const auto=parseViewState('?keyword=image');
const explicit=parseViewState('?keyword=image&sort=year-desc&view=institutions');
console.log(JSON.stringify({steps,defaults,auto,explicit,papers:parseViewState('?view=papers'),
 explicitQuery:serializeViewState(explicit),autoQuery:serializeViewState(auto)}));
""")
        self.assertEqual(result['steps'], ['year-desc', 'relevance', 'year-desc', 'year-asc', 'year-asc'])
        self.assertEqual(result['defaults']['view'], 'papers')
        self.assertEqual(result['papers']['view'], 'papers')
        self.assertEqual(result['explicit']['view'], 'institutions')
        self.assertEqual(result['auto']['sort'], 'relevance')
        self.assertNotIn('sort=', result['autoQuery'])
        self.assertIn('sort=year-desc', result['explicitQuery'])

    def test_citation_omits_unknowns_and_uses_available_metadata(self):
        result = self.run_js("""
const {citationText}=require('./web/paper_details_helpers.js');
console.log(JSON.stringify([
 citationText({authors:['Alice','Bob'],title:'Example',venue:'CVPR',year:2026,url:'https://doi.org/10.1234/test'}),
 citationText({title:'Only a title',venue:'Unknown publication venue',year:null}),
 citationText({title:'A preprint',year:2025,url:'https://arxiv.org/abs/2501.12345'}),citationText()]));
""")
        self.assertEqual(result, ['Alice, Bob. "Example." CVPR, 2026. https://doi.org/10.1234/test',
                                  '"Only a title."', '"A preprint." 2025. https://arxiv.org/abs/2501.12345', ''])

    def test_methodology_headings_links_and_conservative_citation(self):
        path = ROOT / 'web/methodology.html'
        html = path.read_text()
        for heading in ('Scope', 'Taxonomy', 'Paper collection and curation', 'Paper identity and deduplication',
                        'Affiliation and institution mapping', 'Map coverage limitations', 'Metadata verification',
                        'Updates and corrections', 'Data access', 'How to cite'):
            self.assertIn(f'>{heading}</h2>', html)
        for page in (path, ROOT / 'web/index.html'):
            for link in Links(page.read_text()).targets:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                target = (page.parent / url.path).resolve() if url.path else page
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.exists(), link)
                if url.fragment and target.suffix == '.html':
                    self.assertIn(url.fragment, Links(target.read_text()).ids, link)
        cff = (ROOT / 'CITATION.cff').read_text()
        self.assertIn('cff-version: 1.2.0', cff)
        self.assertIn('family-names: Li', cff)
        for unsupported in ('doi:', 'orcid:', 'license:', 'date-released:', '\nversion:'):
            self.assertNotIn(unsupported, cff)
        self.assertIn('no project code license or data redistribution license', html)


if __name__ == '__main__':
    unittest.main()
