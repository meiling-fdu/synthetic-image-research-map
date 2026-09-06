import json
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class MoreFiltersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / 'web/app.js').read_text()
        cls.html = (ROOT / 'web/index.html').read_text()
        cls.css = (ROOT / 'web/style.css').read_text()

    def test_manual_disclosure_count_hydration_reset_and_chip_clear(self):
        source = self.app[self.app.index('function setMoreFiltersExpanded'):
                          self.app.index('function renderActiveFilterChips')]
        source += self.app[self.app.index('function parseViewState'):
                           self.app.index('function canonicalViewUrl')]
        node = shutil.which('node')
        self.assertIsNotNone(node)
        script = '''
const venueTypeFilter={value:'all'}, venueFilter={value:'all'}, countryFilter={value:'all'},
  institutionTypeFilter={value:'all'}, preprintFilter={value:'all'};
const moreFiltersContent={hidden:true, contains:()=>false};
const moreFiltersToggle={dataset:{},setAttribute(k,v){this[k]=v}};
const document={activeElement:null};
function closeAllFilterDropdowns(){}
''' + source + '''
const states=[];
const snapshot=()=>states.push([moreFiltersContent.hidden,moreFiltersToggle.textContent,moreFiltersToggle['aria-expanded']]);
syncMoreFilters(); snapshot();
setMoreFiltersExpanded(true); syncMoreFilters(); snapshot();
setMoreFiltersExpanded(false); snapshot();
const hydrated=parseViewState('?country=Italy&version=has-arxiv&published_only=1');
countryFilter.value=hydrated.country; preprintFilter.value=hydrated.version;
syncMoreFilters(); snapshot();
setMoreFiltersExpanded(false); syncMoreFilters(); snapshot();
countryFilter.value='all'; syncMoreFilters(); snapshot();
preprintFilter.value='all'; syncMoreFilters(); snapshot();
setMoreFiltersExpanded(true); syncMoreFilters({reset:true}); snapshot();
console.log(JSON.stringify(states));
'''
        result = json.loads(subprocess.check_output([node, '-e', script], text=True))
        self.assertEqual(result, [
            [True, 'More filters', 'false'], [False, 'More filters', 'true'],
            [True, 'More filters', 'false'], [False, 'More filters · 2', 'true'],
            [True, 'More filters · 2', 'false'], [False, 'More filters · 1', 'true'],
            [True, 'More filters', 'false'], [True, 'More filters', 'false'],
        ])

    def test_grouping_accessibility_and_responsive_structure(self):
        group = self.html.split('<div class="more-filters">', 1)[1].split('</fieldset>', 1)[0]
        for control in ('venue-type-filter', 'venue-filter', 'country-filter', 'institution-type-filter', 'preprint-filter'):
            self.assertIn(f'id="{control}"', group)
            self.assertEqual(self.html.count(f'id="{control}"'), 1)
        before = self.html.split('<div class="more-filters">')[0]
        for control in ('keyword-filter', 'task-filter', 'image-scope-filter', 'research-type-filter', 'published-only-filter', 'min-year-filter'):
            self.assertIn(f'id="{control}"', before)
        self.assertIn('aria-expanded="false" aria-controls="more-filters-content"', self.html)
        self.assertIn('class="more-filters-content" hidden', self.html)
        self.assertIn('.more-filters-toggle:focus-visible', self.css)
        self.assertIn('.more-filters-content[hidden] { display: none; }', self.css)
        self.assertLess(self.html.index('id="more-filters-toggle"'), self.html.index('id="done-filters"'))

    def test_shared_pipeline_and_reset_remain_authoritative(self):
        render = self.app.split('function renderRecordsForGeneration', 1)[1].split('// A category is active', 1)[0]
        self.assertIn('syncMoreFilters();', render)
        reset = self.app.split('function resetFilterValues', 1)[1].split('function clearActiveFilter', 1)[0]
        self.assertIn('syncMoreFilters({ reset: true });', reset)
        restore = self.app.split('function restoreViewStateFromLocation', 1)[1].split('function setMoreFiltersExpanded', 1)[0]
        self.assertIn('renderRecords();', restore)
        focus = self.app.split('function focusFilterControl', 1)[1].split('const keywordSuggestions', 1)[0]
        self.assertIn('setMoreFiltersExpanded(true)', focus)
