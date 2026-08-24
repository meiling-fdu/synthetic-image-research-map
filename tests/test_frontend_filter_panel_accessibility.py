import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendFilterPanelAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.node = shutil.which("node")

    def run_node(self, source):
        if self.node is None:
            self.skipTest("Node.js is not on PATH")
        completed = subprocess.run(
            [self.node, "-e", source], check=True, capture_output=True, text=True,
        )
        return json.loads(completed.stdout)

    def test_default_markup_is_a_labelled_non_modal_region(self):
        sidebar = self.html[
            self.html.index('<aside class="sidebar"'):
            self.html.index('<div class="map-column">')
        ]
        panel = sidebar[
            sidebar.index('id="filters-panel"'):
            sidebar.index('<div class="filters-panel-heading">')
        ]
        self.assertIn('aria-labelledby="filters-heading"', sidebar)
        self.assertIn('role="region"', panel)
        self.assertIn('aria-labelledby="filters-heading"', panel)
        self.assertNotIn('role="dialog"', panel)
        self.assertNotIn("aria-modal", panel)

    def test_responsive_dialog_state_focus_trap_and_restoration(self):
        start = self.app.index("function drawerFocusableElements")
        end = self.app.index("\nfunction deriveYearBounds", start)
        helpers = self.app[start:end]
        result = self.run_node(f"""
function classes() {{
  const values = new Set();
  return {{
    add: value => values.add(value), remove: value => values.delete(value),
    has: value => values.has(value),
  }};
}}
const document = {{activeElement: null, body: {{classList: classes()}}}};
const attributes = new Map([['role', 'region'], ['aria-labelledby', 'filters-heading']]);
const filtersPanel = {{
  classList: classes(),
  setAttribute(name, value) {{ attributes.set(name, String(value)); }},
  removeAttribute(name) {{ attributes.delete(name); }},
  toggleAttribute(name, force) {{
    if (force) attributes.set(name, ''); else attributes.delete(name);
  }},
  hasAttribute(name) {{ return attributes.has(name); }},
  querySelectorAll() {{ return focusableCandidates; }},
  contains(element) {{ return element === filtersHeading || focusableCandidates.includes(element); }},
}};
function element(id, tabIndex) {{
  return {{
    id, tabIndex, hidden: false,
    getClientRects: () => [{{}}],
    closest: selector => selector === '[inert]' && filtersPanel.hasAttribute('inert')
      ? filtersPanel : null,
    focus() {{ document.activeElement = this; }},
    setAttribute(name, value) {{ this[name] = String(value); }},
  }};
}}
const closeButton = element('close', 0);
const hiddenNativeSelect = element('native-select', -1);
const doneButton = element('done', 0);
const outsideButton = element('outside', 0);
const focusableCandidates = [closeButton, hiddenNativeSelect, doneButton];
const filtersHeading = element('heading', -1);
const mobileFiltersTrigger = element('trigger', 0);
const filtersBackdrop = {{hidden: true}};
const mobileFiltersMedia = {{matches: false}};
let filtersDrawerOpen = false;
let dropdownCloses = 0;
const closeAllFilterDropdowns = () => {{ dropdownCloses += 1; }};
const getComputedStyle = () => ({{visibility: 'visible'}});
{helpers}
const snapshot = () => ({{
  role: attributes.get('role'), modal: attributes.has('aria-modal'),
  inert: attributes.has('inert'), open: filtersDrawerOpen,
  expanded: mobileFiltersTrigger['aria-expanded'],
  focused: document.activeElement?.id || null,
  backdropHidden: filtersBackdrop.hidden,
}});
syncFiltersPanelAccessibility();
const desktop = snapshot();
mobileFiltersMedia.matches = true;
handleMobileFiltersMediaChange({{matches: true}});
const mobileClosed = snapshot();
openFiltersDrawer();
const mobileOpen = snapshot();
const focusableIds = drawerFocusableElements().map(item => item.id);
let prevented = 0;
document.activeElement = doneButton;
handleFiltersDrawerKeydown({{key: 'Tab', shiftKey: false, preventDefault() {{ prevented += 1; }}}});
const wrappedForward = document.activeElement.id;
document.activeElement = closeButton;
handleFiltersDrawerKeydown({{key: 'Tab', shiftKey: true, preventDefault() {{ prevented += 1; }}}});
const wrappedBackward = document.activeElement.id;
document.activeElement = outsideButton;
handleFiltersDrawerKeydown({{key: 'Tab', shiftKey: false, preventDefault() {{ prevented += 1; }}}});
const recaptured = document.activeElement.id;
handleFiltersDrawerKeydown({{key: 'Escape', shiftKey: false, preventDefault() {{ prevented += 1; }}}});
const escaped = snapshot();
openFiltersDrawer();
mobileFiltersMedia.matches = false;
handleMobileFiltersMediaChange({{matches: false}});
const desktopTransition = snapshot();
process.stdout.write(JSON.stringify({{
  desktop, mobileClosed, mobileOpen, focusableIds, wrappedForward,
  wrappedBackward, recaptured, escaped, desktopTransition, prevented,
  dropdownCloses,
}}));
""")
        self.assertEqual(result["desktop"], {
            "role": "region", "modal": False, "inert": False, "open": False,
            "focused": None, "backdropHidden": True,
        })
        self.assertTrue(result["mobileClosed"]["inert"])
        self.assertFalse(result["mobileClosed"]["modal"])
        self.assertEqual(result["mobileOpen"]["role"], "dialog")
        self.assertTrue(result["mobileOpen"]["modal"])
        self.assertFalse(result["mobileOpen"]["inert"])
        self.assertEqual(result["mobileOpen"]["focused"], "heading")
        self.assertEqual(result["focusableIds"], ["close", "done"])
        self.assertEqual(result["wrappedForward"], "close")
        self.assertEqual(result["wrappedBackward"], "done")
        self.assertEqual(result["recaptured"], "close")
        self.assertEqual(result["escaped"]["role"], "region")
        self.assertFalse(result["escaped"]["modal"])
        self.assertTrue(result["escaped"]["inert"])
        self.assertEqual(result["escaped"]["focused"], "trigger")
        self.assertEqual(result["escaped"]["expanded"], "false")
        self.assertTrue(result["escaped"]["backdropHidden"])
        self.assertEqual(result["desktopTransition"]["role"], "region")
        self.assertFalse(result["desktopTransition"]["modal"])
        self.assertFalse(result["desktopTransition"]["inert"])
        self.assertEqual(result["desktopTransition"]["focused"], "heading")
        self.assertEqual(result["dropdownCloses"], 2)

    def test_escape_outside_click_and_responsive_handlers_remain_scoped(self):
        trap = self.app[
            self.app.index("function handleFiltersDrawerKeydown"):
            self.app.index("\nfunction deriveYearBounds")
        ]
        self.assertIn("if (!mobileFiltersMedia.matches || !filtersDrawerOpen) return", trap)
        self.assertIn('event.key === "Escape"', trap)
        self.assertIn("closeFiltersDrawer()", trap)
        self.assertIn("closeFiltersDrawer({ restoreFocus: false })", trap)

        listeners = self.app[self.app.index('mobileFiltersTrigger.addEventListener("click"'):]
        self.assertIn('filtersBackdrop.addEventListener("pointerdown"', listeners)
        self.assertIn("event.preventDefault()", listeners)
        self.assertIn("closeFiltersDrawer()", listeners)
        self.assertIn(
            'mobileFiltersMedia.addEventListener("change", handleMobileFiltersMediaChange)',
            listeners,
        )


if __name__ == "__main__":
    unittest.main()
