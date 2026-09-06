import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class StickyResultsToolbarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / 'web/style.css').read_text()
        cls.html = (ROOT / 'web/index.html').read_text()
        cls.app = (ROOT / 'web/app.js').read_text()

    def test_single_existing_toolbar_keeps_all_controls(self):
        toolbar = self.html.split('<div class="results-heading-row">', 1)[1].split('<div class="results-records-area">', 1)[0]
        for attribute in ('id="results-heading"', 'id="results-count"',
                          'data-results-view="papers"', 'data-results-view="institutions"',
                          'id="sort-control"', 'id="copy-view-link"', 'id="export-csv"'):
            self.assertIn(attribute, toolbar)
            self.assertEqual(self.html.count(attribute), 1)

    def test_sticky_flow_layering_and_scroll_clearance(self):
        toolbar = self.css.split('.results-heading-row {', 1)[1].split('}', 1)[0]
        self.assertIn('position: sticky', toolbar)
        self.assertIn('top: var(--results-header-height, var(--sticky-summary-offset))', toolbar)
        self.assertIn('z-index: 30', toolbar)
        self.assertIn('background: var(--page-surface)', toolbar)
        self.assertNotIn('position: fixed', toolbar)
        self.assertIn('var(--results-toolbar-height, 100px) + 12px', self.css)
        for selector in ('.results-panel {', '.results-list {'):
            rule = self.css.split(selector, 1)[1].split('}', 1)[0]
            self.assertNotIn('overflow', rule)
            self.assertNotIn('max-height', rule)

    def test_wrapping_and_layout_measurement_do_not_mutate_state(self):
        narrow = self.css.split('@media (max-width: 820px) {', 1)[1]
        self.assertIn('.results-heading-row {\n    grid-template-columns: 1fr;', narrow)
        for selector in ('.results-actions {', '.results-view-toggle {'):
            rule = self.css.split(selector, 1)[1].split('}', 1)[0]
            self.assertIn('flex-wrap: wrap', rule)
        measure = self.app.split('function observeResultsToolbarLayout()', 1)[1].split('observeResultsToolbarLayout();', 1)[0]
        self.assertIn('observer.observe(header)', measure)
        self.assertIn('observer.observe(toolbar)', measure)
        for mutation in ('renderRecords(', 'syncUrl', 'selectPaper(', 'sortControl.value', 'keywordFilter.value'):
            self.assertNotIn(mutation, measure)
