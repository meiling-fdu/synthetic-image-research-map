import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class AccessibilityHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / 'web/app.js').read_text()
        cls.css = (ROOT / 'web/style.css').read_text()
        cls.html = (ROOT / 'web/index.html').read_text()

    def test_handled_escape_does_not_reach_drawer(self):
        handler = self.app.split('function handleFiltersDrawerKeydown', 1)[1].split('\nfunction handleMobileFiltersMediaChange', 1)[0]
        subprocess.run([shutil.which('node'), '-e', 'function handleFiltersDrawerKeydown' + handler + '''
handleFiltersDrawerKeydown({key:'Escape',defaultPrevented:true});
'''], check=True)
        controller = self.app.split('function createFilterDropdown', 1)[1].split('function syncFilterDropdownForSelect', 1)[0]
        self.assertIn('event.key === "Escape" && !panel.hidden', controller)
        self.assertIn('event.stopPropagation()', controller)

    def test_publication_status_uses_shared_keyboard_controller(self):
        registry = self.app.split('filterDropdowns = [', 1)[1].split('].map(createFilterDropdown)', 1)[0]
        self.assertIn('publishedOnlyFilter,', registry)

    def test_live_region_reduced_motion_and_touch_targets(self):
        self.assertIn('id="results-empty-heading" role="status" aria-live="polite" aria-atomic="true"', self.html)
        reduced = self.css.split('@media (prefers-reduced-motion: reduce)', 1)[1].split('@keyframes', 1)[0]
        self.assertIn('.results-list { transition: none; }', reduced)
        self.assertIn('@media (pointer: coarse)', self.css)
        self.assertIn('.paper-details-close { min-width: 44px; }', self.css)
