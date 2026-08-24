import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendSortDropdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.node = shutil.which("node")

    def run_node(self, source):
        if self.node is None:
            self.skipTest("Node.js is not on PATH")
        completed = subprocess.run(
            [self.node, "-e", source], check=True, capture_output=True, text=True,
        )
        return json.loads(completed.stdout)

    def test_sort_uses_the_existing_custom_dropdown_registry_and_hidden_native_state(self):
        sort_markup = self.html[
            self.html.index('<div class="sort-control-label'):
            self.html.index('<button id="copy-view-link"')
        ]
        self.assertIn("filter-dropdown-field", sort_markup)
        self.assertIn("data-filter-dropdown", sort_markup)
        self.assertIn('id="sort-control-label" class="filter-label"', sort_markup)
        self.assertIn('id="sort-control" class="sort-control-compact"', sort_markup)
        self.assertEqual(sort_markup.count('<option value="'), 5)

        initialization = self.app[
            self.app.index("filterDropdowns = ["):
            self.app.index("const chartTooltip")
        ]
        self.assertIn("sortControl,", initialization)
        self.assertIn("].map(createFilterDropdown)", initialization)
        controller = self.app[
            self.app.index("function createFilterDropdown"):
            self.app.index("\nfunction syncFilterDropdownForSelect")
        ]
        self.assertIn('select.setAttribute("aria-hidden", "true")', controller)
        self.assertIn("select.tabIndex = -1", controller)
        self.assertIn('button.setAttribute("role", "combobox")', controller)
        self.assertIn('options.setAttribute("role", "listbox")', controller)

    def test_opening_uses_shared_expanded_state_and_selected_option(self):
        opening = self.app[
            self.app.index("function openFilterDropdown"):
            self.app.index("\nfunction selectFilterDropdownValue")
        ]
        controller = self.app[
            self.app.index("function createFilterDropdown"):
            self.app.index("\nfunction syncFilterDropdownForSelect")
        ]
        self.assertIn("closeAllFilterDropdowns(dropdown)", opening)
        self.assertIn("dropdown.panel.hidden = false", opening)
        self.assertIn('dropdown.button.setAttribute("aria-expanded", "true")', opening)
        self.assertIn("setActiveFilterDropdownOption(dropdown, selectedIndex, true)", opening)
        self.assertIn('button.addEventListener("click"', controller)
        self.assertIn("if (panel.hidden) openFilterDropdown(dropdown)", controller)

    def test_selection_updates_native_sort_and_existing_url_render_pipeline(self):
        selection = self.app[
            self.app.index("function selectFilterDropdownValue"):
            self.app.index("\nfunction createFilterDropdown")
        ]
        self.assertIn("dropdown.select.value = value", selection)
        self.assertIn("closeFilterDropdown(dropdown, true)", selection)
        self.assertIn(
            'dispatchEvent(new Event("change", { bubbles: true }))', selection
        )
        events = self.app[
            self.app.index("function handleFilterControlChange"):
            self.app.index('document.addEventListener("pointerdown"')
        ]
        self.assertIn(
            'sortControl.addEventListener("change", handleFilterControlChange)', events
        )
        self.assertIn('requestUrlStateSync("push")', events)
        self.assertIn("renderRecords()", events)
        self.assertIn(
            "compareRecordsForSort(first, second, sortControl.value)", self.app
        )

    def test_keyboard_navigation_wraps_and_uses_shared_enter_space_escape_behavior(self):
        start = self.app.index("function nextFilterOptionIndex")
        end = self.app.index("\nfunction filterDropdownPlacement", start)
        helper = self.app[start:end]
        result = self.run_node(f"""
{helper}
console.log(JSON.stringify({{
  down: nextFilterOptionIndex([0, 1, 2, 3, 4], 0, 1),
  up: nextFilterOptionIndex([0, 1, 2, 3, 4], 0, -1),
  fromMissing: nextFilterOptionIndex([0, 1, 2], -1, 1),
}}));
""")
        self.assertEqual(result, {"down": 1, "up": 4, "fromMissing": 0})

        controller = self.app[
            self.app.index("function createFilterDropdown"):
            self.app.index("\nfunction syncFilterDropdownForSelect")
        ]
        self.assertIn('["ArrowDown", "ArrowUp"]', controller)
        self.assertIn('["Enter", " "]', controller)
        self.assertIn('event.key === "Escape"', controller)
        self.assertIn("moveActiveFilterDropdownOption", controller)
        self.assertIn("selectFilterDropdownValue(dropdown, option.value)", controller)
        self.assertIn("closeFilterDropdown(dropdown, true)", controller)

    def test_url_restoration_and_native_changes_refresh_the_visible_value(self):
        restoration = self.app[
            self.app.index("function restoreViewState"):
            self.app.index("\nfunction requestUrlStateSync")
        ]
        self.assertIn(
            "if (selectContainsValue(sortControl, state.sort)) sortControl.value = state.sort",
            restoration,
        )
        self.assertLess(
            restoration.index("sortControl.value = state.sort"),
            restoration.index("filterDropdowns.forEach(syncFilterDropdown)"),
        )
        synchronization = self.app[
            self.app.index("function syncFilterDropdown"):
            self.app.index("\nfunction positionFilterDropdownPanel")
        ]
        self.assertIn("dropdown.value.textContent = selectedOption?.label", synchronization)
        self.assertIn(
            'element.setAttribute("aria-selected", String(option.value === dropdown.select.value))',
            synchronization,
        )
        controller = self.app[
            self.app.index("function createFilterDropdown"):
            self.app.index("\nfunction syncFilterDropdownForSelect")
        ]
        self.assertIn(
            'select.addEventListener("change", () => syncFilterDropdown(dropdown))',
            controller,
        )

    def test_compact_visual_state_reuses_shared_menu_and_has_no_native_outline(self):
        self.assertIn(".sort-control-label .filter-dropdown-button {", self.css)
        self.assertIn("height: 32px", self.css)
        self.assertIn("min-height: 32px", self.css)
        self.assertIn(".filter-dropdown-chevron {", self.css)
        self.assertIn(".filter-dropdown-panel {", self.css)
        self.assertIn(".filter-dropdown-option.is-active", self.css)
        self.assertIn('.filter-dropdown-option[aria-selected="true"]', self.css)
        self.assertIn("button:focus-visible", self.css)
        self.assertIn(".filter-dropdown-field.is-enhanced > select", self.css)
        self.assertNotIn(".sort-control-label select {", self.css)
        self.assertIn(".sort-control-label .filter-dropdown-panel {", self.css)


if __name__ == "__main__":
    unittest.main()
