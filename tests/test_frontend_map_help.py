import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class MapHelpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'web/index.html').read_text()
        cls.app = (ROOT / 'web/app.js').read_text()
        cls.css = (ROOT / 'web/style.css').read_text()

    def test_closed_native_disclosure_content_and_documentation(self):
        self.assertIn('<details id="map-help" class="map-help">', self.html)
        self.assertIn('aria-controls="map-help-content" aria-expanded="false"', self.html)
        help_text = self.html.split('<details id="map-help"', 1)[1].split('</details>', 1)[0]
        for label in ('Detection', 'Source Attribution', 'Localization', 'Image Scope', 'Research Type',
                      'Institution Records', 'Unique Papers', 'without mapped institutions', 'Copy link', 'Export CSV'):
            self.assertIn(label, help_text)
        self.assertIn('href="../docs/data_collection.md">Data Methodology', help_text)
        self.assertIn('href="#site-information-heading"', help_text)
        self.assertNotIn('role="dialog"', help_text)

    def test_escape_toggle_aria_and_outside_close_without_state_mutation(self):
        source = self.app.split('const mapHelp = document.querySelector', 1)[1].split('updateDatasetLabels();', 1)[0]
        script = '''
const handlers={}, docHandlers={};
let focused=false, expanded='false', prevented=false, stopped=false;
const summary={setAttribute(k,v){expanded=v},focus(){focused=true}};
const help={open:false,querySelector:()=>summary,addEventListener(k,f){handlers[k]=f},contains:()=>false};
const document={querySelector:()=>help,addEventListener(k,f){docHandlers[k]=f}};
''' + 'const mapHelp = document.querySelector' + source + '''
help.open=true; handlers.toggle();
if(expanded!=='true') throw Error('expanded');
handlers.keydown({key:'Escape',preventDefault(){prevented=true},stopPropagation(){stopped=true}});
handlers.toggle();
if(help.open || expanded!=='false' || !focused || !prevented || !stopped) throw Error('escape');
help.open=true; docHandlers.pointerdown({target:{}});
if(help.open) throw Error('outside');
'''
        subprocess.run([shutil.which('node'), '-e', script], check=True)
        for forbidden in ('renderRecords(', 'syncUrl', 'selectPaper(', 'resetFilterValues(', 'requestUrlStateSync('):
            self.assertNotIn(forbidden, source)

    def test_responsive_overlay_focus_and_no_animation(self):
        rule = self.css.split('.map-help-content {', 1)[1].split('}', 1)[0]
        self.assertIn('position: absolute', rule)
        self.assertIn('width: min(420px, calc(100% - 24px))', rule)
        self.assertIn('overflow-y: auto', rule)
        self.assertIn('.map-help summary:focus-visible', self.css)
        self.assertNotIn('animation', rule)
