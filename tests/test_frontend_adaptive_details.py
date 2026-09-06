import json
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class AdaptiveDetailsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / 'web/app.js').read_text()
        cls.css = (ROOT / 'web/style.css').read_text()
        cls.html = (ROOT / 'web/index.html').read_text()

    def function(self, name, next_name):
        return self.app[self.app.index('function ' + name):
                        self.app.index('\nfunction ' + next_name)]

    def test_selection_hydration_collapse_reopen_and_pins(self):
        source = self.function('setPaperDetailsExpanded', 'resetPaperDetails')
        source += self.function('selectPaper', 'setPersistentSelection')
        source += self.function('restoreLinkedPaperSelection', 'reconcilePersistentSelectionAfterFilter')
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Run with Node on PATH')
        script = '''
let collapsed = true, expandedAttribute, focused, resizes = 0;
const mapWorkspace = {classList: {toggle(name, value) { collapsed = value; }}};
const openPaperDetailsButton = {
  setAttribute(name, value) { expandedAttribute = value; },
  focus() { focused = 'handle'; },
};
const closePaperDetailsButton = {focus() { focused = 'close'; }};
const stackedDetailsMedia = {matches:false};
const paperDetails = {contains:()=>false};
const document = {activeElement:null};
const interactionState = {detailMode: 'empty', transientHover: null};
let requestedPaperIdentity = '';
const markerHoverIntent = {cancel() {}};
function scheduleMapResize() { resizes++; }
function closeActiveInstitutionTooltip() {}
function institutionIdentity(record) { return record.id; }
function renderActiveSelection() { syncPaperDetailsLayout(); }
function requestUrlStateSync() {}
function syncUrlFromState() {}
const canonicalPaperRecordsByIdentity = new Map([['paper:a', {}]]);
''' + source + '''
syncPaperDetailsLayout();
const initial = collapsed;
selectPaper('paper:a');
const paperOpen = !collapsed;
selectMapMarker({record: {id:'institution:a'}, institutionKey:'marker:a'});
const institutionOpen = !collapsed;
const before = JSON.stringify(interactionState);
setPaperDetailsExpanded(false, {focus:true});
const closed = collapsed && focused === 'handle';
setPaperDetailsExpanded(true, {focus:true});
const reopened = !collapsed && focused === 'close';
const pinnedPreserved = before === JSON.stringify(interactionState);
requestedPaperIdentity = 'paper:a';
setPaperDetailsExpanded(false);
const hydration = restoreLinkedPaperSelection(new Set(['paper:a']));
syncPaperDetailsLayout();
console.log(JSON.stringify({initial, paperOpen, institutionOpen, closed, reopened,
  pinnedPreserved, hydration, hydratedOpen: !collapsed, expandedAttribute, resizes}));
'''
        result = json.loads(subprocess.run([node, '-e', script], check=True,
                                          capture_output=True, text=True).stdout)
        for key in ('initial', 'paperOpen', 'institutionOpen', 'closed', 'reopened',
                    'pinnedPreserved', 'hydratedOpen'):
            self.assertTrue(result[key], key)
        self.assertEqual(result['hydration'], 'open')
        self.assertEqual(result['expandedAttribute'], 'true')
        self.assertGreater(result['resizes'], 0)

    def test_shared_render_and_desktop_only_close(self):
        pipeline = self.function('renderRecordsForGeneration', 'activeFilterCategoryCount')
        self.assertIn('syncPaperDetailsLayout();', pipeline)
        render = self.function('renderActiveSelection', 'clearHoveredSelection')
        self.assertIn('syncPaperDetailsLayout();', render)
        close = self.app.split('closePaperDetailsButton.addEventListener("click", () => {', 1)[1].split('\n});', 1)[0]
        desktop, mobile = close.split('const selectionOrigin', 1)
        self.assertIn('if (!stackedDetailsMedia.matches)', desktop)
        self.assertIn('setPaperDetailsExpanded(false, { focus: true });', desktop)
        self.assertNotIn('clearPersistentSelection', desktop)
        self.assertIn('clearPersistentSelection()', mobile)

    def test_desktop_recovers_width_and_mobile_keeps_existing_stack(self):
        self.assertIn('class="map-workspace details-collapsed"', self.html)
        self.assertIn('aria-controls="paper-details" aria-expanded="false"', self.html)
        desktop = self.css.split('@media (min-width: 1251px)', 1)[1].split('@media', 1)[0]
        self.assertIn('grid-template-columns: minmax(0, 1fr) 32px', desktop)
        self.assertIn('.details-collapsed > #paper-details', desktop)
        self.assertIn('display: none', desktop)
        mobile = self.css.split('@media (max-width: 1250px)', 1)[1].split('@media', 1)[0]
        self.assertIn('grid-template-columns: 1fr', mobile)
        self.assertNotIn('details-collapsed', mobile)
        self.assertIn('map.invalidateSize({ animate: false, pan: false })', self.app)
