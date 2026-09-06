import json
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class CrossHighlightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / 'web/app.js').read_text()

    def run_js(self, source):
        return json.loads(subprocess.check_output([shutil.which('node'), '-e', source], text=True))

    def test_paper_all_markers_exact_institution_clear_and_pinned_precedence(self):
        source = self.app.split('const cardMapHighlightElements = new Set();', 1)[1].split('resultsList.addEventListener("pointerover"', 1)[0]
        result = self.run_js('''
const cardMapHighlightElements=new Set();
const interactionState={detailMode:'empty'};
let requestedPaperIdentity='';
const resultsRenderGeneration=3;
function element(){const classes=new Set();return {classes,classList:{add:c=>classes.add(c),remove:c=>classes.delete(c)}}}
const a=element(),b=element();
const visibleMarkerEntryByInstitutionKey=new Map([['a',{marker:{getElement:()=>a}}],['b',{marker:{getElement:()=>b}}]]);
const resultsPipeline={relatedEntriesByIdentity:new Map([['p',[{record:{key:'a'}},{record:{key:'b'}},{record:{key:'hidden'}}]]])};
function markerInstitutionIdentity(record){return record.key}
''' + source + '''
const card={dataset:{resultGeneration:'3',paperIdentity:'p'}};
highlightCardMarkers(card); const paper=[a.classes.size,b.classes.size];
card.dataset.markerIdentity='b'; highlightCardMarkers(card); const exact=[a.classes.size,b.classes.size];
clearCardMapHighlights(); const clear=[a.classes.size,b.classes.size];
interactionState.detailMode='paper'; highlightCardMarkers(card); const pinned=[a.classes.size,b.classes.size];
console.log(JSON.stringify({paper,exact,clear,pinned}));
''')
        self.assertEqual(result, dict(paper=[1, 1], exact=[0, 1], clear=[0, 0], pinned=[0, 0]))

    def test_marker_only_highlights_rendered_exact_relationships(self):
        source = self.app[self.app.index('function syncResultHighlights()'):self.app.index('\nfunction resolveShowInResultsTarget')]
        result = self.run_js('''
const interactionState={detailMode:'empty',transientHover:{institutionKey:'a'}};
const resultsPipeline={resultIndexesByInstitutionKey:new Map([['a',new Set([0,99])]])};
const resultsRenderGeneration=1, resultsView='institutions';
const items=[0,1].map(i=>({dataset:{resultIndex:String(i)},classes:{},classList:{toggle(k,v){items[i].classes[k]=v}},removeAttribute(){}}));
const resultsList={querySelectorAll:()=>items};
function persistentResultSelection(){return null}
function interactionResultIndexes(){return new Set()}
''' + source + '''
syncResultHighlights(); const hovered=items.map(i=>i.classes['is-interaction-hovered']);
interactionState.detailMode='paper'; syncResultHighlights();
console.log(JSON.stringify({hovered,pinned:items.map(i=>i.classes['is-interaction-hovered'])}));
''')
        self.assertEqual(result, dict(hovered=[True, False], pinned=[False, False]))

    def test_no_navigation_mutation_keyboard_touch_and_cleanup(self):
        source = self.app.split('const cardMapHighlightElements = new Set();', 1)[1].split('activeFilterChips.addEventListener', 1)[0]
        for forbidden in ('selectPaper(', 'renderRecords(', 'requestUrlStateSync(', 'panTo(', 'fitBounds(', 'appendResultChunk('):
            self.assertNotIn(forbidden, source)
        self.assertIn('event.pointerType === "touch"', source)
        self.assertIn('"focusin"', source)
        self.assertIn('"focusout"', source)
        self.assertIn('item.contains(event.relatedTarget)', source)
        marker = (ROOT / 'web/marker_interaction_helpers.js').read_text()
        self.assertIn('addEventListener("focus", handlers.hover)', marker)
        self.assertIn('addEventListener("blur", handlers.leave)', marker)
