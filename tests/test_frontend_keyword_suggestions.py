import json
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class KeywordSuggestionTests(unittest.TestCase):
    def run_js(self, source):
        node = shutil.which('node')
        self.assertIsNotNone(node)
        return json.loads(subprocess.check_output([node, '-e', source], cwd=ROOT, text=True))

    def test_index_groups_ranking_duplicates_and_limits(self):
        result = self.run_js('''
const {build,find} = require('./web/keyword_suggestions.js');
const index = build([
 ...Array.from({length:8}, (_,i) => ({type:'Papers',id:String(i),label:'Image '+i})),
 {type:'Papers',id:'0',label:'Image 0'},
 {type:'Authors',label:'Image Author'}, {type:'Authors',label:'image author'},
 {type:'Institutions',id:'i',label:'Image Lab'}, {type:'Institutions',id:'i',label:'Image Lab'},
]);
console.log(JSON.stringify({short:find(index,'i'),matches:find(index,'image')}));
''')
        self.assertEqual(result['short'], [])
        self.assertEqual([e['type'] for e in result['matches']],
                         ['Papers'] * 3 + ['Authors', 'Institutions'])

    def test_keyboard_free_text_escape_clear_and_selection(self):
        result = self.run_js('''
const {mount} = require('./web/keyword_suggestions.js');
function node() {
 return {children:[], attrs:{}, handlers:{}, dataset:{}, hidden:true, value:'',
  append(...items){this.children.push(...items)}, replaceChildren(){this.children=[]},
  setAttribute(k,v){this.attrs[k]=v}, removeAttribute(k){delete this.attrs[k]},
  addEventListener(k,v){this.handlers[k]=v}, scrollIntoView(){},
  querySelectorAll(){return this.children.flatMap(g=>g.children).filter(e=>e.attrs?.role==='option')},
  contains(){return false}};
}
global.document = {createElement:node, addEventListener(){}};
const input=node(), list=node(), chosen=[];
const controller=mount(input,list,e=>chosen.push(e.id));
controller.setEntries([{type:'Papers',id:'a',label:'Image A'},{type:'Papers',id:'b',label:'Image B'}]);
input.value='image'; input.handlers.input({});
let prevented=0;
const key=k=>input.handlers.keydown({key:k,preventDefault(){prevented++},stopPropagation(){}});
key('Enter'); const freeText=prevented===0 && chosen.length===0;
key('ArrowDown'); key('Enter'); const selected=chosen[0];
key('ArrowUp'); const last=input.attrs['aria-activedescendant'];
key('Escape'); const escaped=list.hidden && !input.attrs['aria-activedescendant'];
input.value=''; input.handlers.input({}); const cleared=list.hidden;
console.log(JSON.stringify({freeText,selected,last,escaped,cleared}));
''')
        self.assertEqual(result, dict(freeText=True, selected='a', last='keyword-suggestion-1', escaped=True, cleared=True))

    def test_routes_reuse_selection_and_keyword_pipeline(self):
        app = (ROOT / 'web/app.js').read_text()
        source = app[app.index('function selectKeywordSuggestion'):app.index('\nkeywordFilter.addEventListener("compositionstart"')]
        result = self.run_js('''
const calls=[];
const keywordFilter={value:'',dispatchEvent(e){calls.push(['input',this.value,e.type])}};
const keywordSuggestions={close(){calls.push(['close'])}};
const paperDetailsHeading={focus(){}};
function closeFiltersDrawer(){}
function selectPaper(...args){calls.push(['paper',...args])}
function selectMapMarker(marker){calls.push(['marker',marker])}
const visibleMarkerEntryByInstitutionKey=new Map([['i','marker-i']]);
''' + source + '''
selectKeywordSuggestion({type:'Papers',id:'p'});
selectKeywordSuggestion({type:'Institutions',id:'i'});
selectKeywordSuggestion({type:'Authors',label:'A Name'});
console.log(JSON.stringify(calls));
''')
        self.assertEqual(result, [['paper', 'p'], ['marker', 'marker-i'], ['input', 'A Name', 'input'], ['close']])

    def test_reset_url_and_responsive_contract(self):
        app = (ROOT / 'web/app.js').read_text()
        reset = app.split('function resetFilterValues', 1)[1].split('function clearActiveFilter', 1)[0]
        self.assertIn('keywordSuggestions.close()', reset)
        self.assertIn('keywordFilter.value = ""', reset)
        restore = app.split('function restoreViewState(state)', 1)[1].split('function requestUrlStateSync', 1)[0]
        self.assertIn('resetFilterValues(', restore)
        self.assertIn('keyword: state.keyword', app)
        css = (ROOT / 'web/style.css').read_text()
        popup = css.split('.keyword-suggestions {', 1)[1].split('}', 1)[0]
        self.assertIn('inset-inline: 0', popup)
        self.assertIn('overflow-y: auto', popup)
        html = (ROOT / 'web/index.html').read_text()
        self.assertIn('role="combobox"', html)
        self.assertIn('aria-controls="keyword-suggestions"', html)
