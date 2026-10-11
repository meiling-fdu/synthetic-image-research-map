"""Desktop-only semantics, year drafts, empty states, and asset regressions."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'web/app.js').read_text()


def function(name):
    signature = 'function ' + name + '('
    return signature + APP.split(signature, 1)[1].split('\nfunction ', 1)[0]


class DesktopAuditTests(unittest.TestCase):
    def js(self, source):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Run with Node on PATH')
        result = subprocess.run([node, '-e', source], check=True, text=True, capture_output=True)
        return json.loads(result.stdout)

    def test_map_status_distinguishes_unmapped_papers_from_empty_filters(self):
        result = self.js(function('baseMapStatusText') + '''
let visibleMarkerEntries = [], currentFilteredPaperRecords = [];
const empty = baseMapStatusText([]);
currentFilteredPaperRecords = [{id:'unmapped'}];
const unmapped = baseMapStatusText([]);
visibleMarkerEntries = [{id:'location'}];
console.log(JSON.stringify([empty,unmapped,baseMapStatusText([{}])]));
''')
        self.assertEqual(result, ['No unique papers match the current filters.',
            '1 matching unique paper, but no mapped institution locations. View Unique Papers.',
            '1 institution/location marker'])

    def test_desktop_list_items_keep_native_details_and_mobile_behavior(self):
        result = self.js(function('syncResultItemAccessibility') + '''
const attributes = {}, mobileFiltersMedia = {matches:false};
const item = {dataset:{detailsLabel:'Open Paper Details for Example'},
 setAttribute:(k,v)=>attributes[k]=v,removeAttribute:k=>delete attributes[k]};
syncResultItemAccessibility(item);
const desktop = {tabIndex:item.tabIndex,attributes:{...attributes}};
mobileFiltersMedia.matches=true;syncResultItemAccessibility(item);
const mobile = {tabIndex:item.tabIndex,attributes:{...attributes}};
mobileFiltersMedia.matches=false;syncResultItemAccessibility(item);
console.log(JSON.stringify({desktop,mobile,back:{tabIndex:item.tabIndex,attributes}}));
''')
        self.assertEqual(result['desktop'], {'tabIndex': -1, 'attributes': {}})
        self.assertEqual(result['back'], result['desktop'])
        self.assertEqual(result['mobile']['tabIndex'], 0)
        self.assertEqual(result['mobile']['attributes']['role'], 'button')
        create = function('createResultItem')
        self.assertIn('details.type = "button"', create)
        self.assertIn('details.textContent = "Details"', create)
        self.assertIn('details.setAttribute("aria-controls", "paper-details")', create)
        self.assertIn('resultFocusTarget(item).focus', APP)
        self.assertIn('resultFocusTarget(replacement)', APP)

    def test_year_drafts_invalid_values_escape_and_crossing(self):
        source = '\n'.join(function(n) for n in (
            'clampYear', 'syncYearRange', 'syncYearInputs', 'commitYearInput'))
        result = self.js(source + '''
function input(value){return {value:String(value),attributes:{},
 setAttribute(k,v){this.attributes[k]=v}, removeAttribute(k){delete this.attributes[k]}}}
const minYearFilter=input(2018), maxYearFilter=input(2027);
const yearStartInput=input(2018), yearEndInput=input(2027), yearInputStatus={};
const yearRangeSlider={style:{setProperty(){}}},yearRangeBounds={minimum:2018,maximum:2027};
let yearHistoryStarted=false,commits=0;
function handleYearRangeInput(handle){commits++;syncYearRange(handle)}
const invalid=[];
for(const value of ['', '20', 'abcd', '2017', '2028', '2020.5']){
 yearStartInput.value=value;commitYearInput('start');
 invalid.push([minYearFilter.value,commits,yearStartInput.attributes['aria-invalid']]);
}
syncYearInputs();
const restored=[yearStartInput.value,yearInputStatus.hidden];
yearStartInput.value='2025';commitYearInput('start');
yearEndInput.value='2023';commitYearInput('end');
const crossed=[minYearFilter.value,maxYearFilter.value,yearStartInput.value,yearEndInput.value,commits];
commitYearInput('end');
console.log(JSON.stringify({invalid,restored,crossed,commits}));
''')
        self.assertEqual(result['invalid'], [['2018', 0, 'true']] * 6)
        self.assertEqual(result['restored'], ['2018', True])
        self.assertEqual(result['crossed'], ['2023', '2023', '2023', '2023', 2])
        self.assertEqual(result['commits'], 2)
        listeners = APP.split('[[yearStartInput, "start"]', 1)[1].split('[resultsList, paperDetails]', 1)[0]
        self.assertNotIn('addEventListener("input"', listeners)
        self.assertIn('event.key === "Escape"', listeners)

    def test_details_reorders_existing_sections_only_on_desktop(self):
        result = self.js(function('orderDesktopPaperDetails') + '''
let mobileFiltersMedia={matches:false}, moved=[];
const paperDetailsContent={querySelector:s=>({selector:s}),append:n=>moved.push(n.selector)};
orderDesktopPaperDetails();const desktop=moved;
moved=[];mobileFiltersMedia.matches=true;orderDesktopPaperDetails();
console.log(JSON.stringify({desktop,mobile:moved}));
''')
        self.assertEqual(result['desktop'], ['.paper-details-title', '.paper-details-venue-row',
            '.paper-details-links', '.paper-taxonomy-rows', '.paper-details-authors',
            '.paper-details-affiliation-section', '.paper-abstract-section',
            '.paper-details-metadata-status', '.paper-taxonomy-review'])
        self.assertEqual(result['mobile'], [])

    def test_loader_overlaps_requests_and_keeps_validation_and_errors(self):
        source = 'async ' + function('readDataset')
        result = self.js(source + r'''
const DATASET_CONFIG={preview:{url:'map',paperUrl:'papers'},openalex:{url:'map'}};
const normalizeDatasetPayload=p=>({metadata:p.metadata,records:p.records});
const normalizeCountryRegionRecord=r=>r;
const validateRecord=r=>r.valid, validatePaperRecord=r=>r.valid;
let calls=[], releases={}, failure='';
const fetch=(url,options)=>{calls.push([url,options.cache]);return new Promise(resolve=>{
 releases[url]=()=>resolve({ok:failure!==url,status:503,text:async()=>JSON.stringify({metadata:{source:url},records:[{valid:true,id:url}]})});
});};
(async()=>{
 const pending=readDataset('preview');const concurrent=calls.slice();
 releases.papers();releases.map();const data=await pending;
 failure='papers';const failed=readDataset('preview');releases.map();releases.papers();
 let error;try{await failed}catch(e){error=e.message}
 failure='';calls=[];const one=readDataset('openalex');releases.map();const single=await one;
 console.log(JSON.stringify({concurrent,data,error,single,calls}));
})().catch(e=>{console.error(e);process.exit(1)});
''')
        self.assertEqual(result['concurrent'], [['map', 'no-cache'], ['papers', 'no-cache']])
        self.assertEqual(result['data']['records'], [{'valid': True, 'id': 'map'}])
        self.assertEqual(result['data']['paperRecords'][0]['id'], 'papers')
        self.assertEqual(result['data']['paperMetadata'], {'source': 'papers'})
        self.assertEqual(result['error'], 'preview paper data request failed with status 503')
        self.assertEqual(result['calls'], [['map', 'no-cache']])
        self.assertNotIn('paperRecords', result['single'])

    def test_map_validation_precedes_parallel_paper_failure(self):
        source = 'async ' + function('readDataset')
        result = self.js(source + r'''
const DATASET_CONFIG={preview:{url:'map',paperUrl:'papers'}};
const normalizeDatasetPayload=p=>({metadata:{},records:p});
const normalizeCountryRegionRecord=r=>r;
const validateRecord=r=>r.valid, validatePaperRecord=r=>r.valid;
let mapText='', paperFailure='network';
const fetch=async url=>{
 if(url==='papers' && paperFailure==='network') throw new Error('paper network failure');
 return {ok:true,text:async()=>{
  if(url==='papers' && paperFailure==='body') throw new Error('paper body failure');
  return url==='map' ? mapText : '[]';
 }};
};
(async()=>{
 const outcomes=[];
 for(const failure of ['network','body']){
  paperFailure=failure;
  for(const text of ['', '[{"valid":false}]', '[{"valid":true}]']){
   mapText=text;
   try{outcomes.push(await readDataset('preview'))}catch(e){outcomes.push(e.message)}
  }
 }
 console.log(JSON.stringify(outcomes));
})().catch(e=>{console.error(e);process.exit(1)});
''')
        self.assertEqual(result, [
            {'metadata': {}, 'records': []},
            'preview data does not match the expected format',
            'paper network failure',
            {'metadata': {}, 'records': []},
            'preview data does not match the expected format',
            'paper body failure',
        ])

    def test_public_asset_versions_and_skip_landmarks(self):
        index = (ROOT / 'web/index.html').read_text()
        methodology = (ROOT / 'web/methodology.html').read_text()
        refs = re.findall(r'(?:src|href)="([^"?:]+\.(?:css|js))\?v=([^" ]+)"', index + methodology)
        self.assertGreater(len(refs), 10)
        self.assertEqual({version for _, version in refs}, {'20261009-desktop-1'})
        for target in ('research-map', 'paper-results'):
            self.assertIn(f'href="#{target}"', index)
            self.assertRegex(index, rf'<section id="{target}"[^>]*tabindex="-1"')
        self.assertIn('target.focus({ preventScroll: true })', APP)
        self.assertIn('style.removeProperty("--sticky-summary-offset")', APP)


if __name__ == '__main__':
    unittest.main()
