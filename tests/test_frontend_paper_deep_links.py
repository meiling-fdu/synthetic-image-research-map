import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendPaperDeepLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.node = shutil.which("node")

    def run_node(self, source):
        if self.node is None:
            self.skipTest("Node.js is not on PATH")
        completed = subprocess.run(
            [self.node, "-e", source],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def function_source(self, name, next_name):
        start = self.app.index(f"function {name}")
        end = self.app.index(f"\nfunction {next_name}", start)
        return self.app[start:end]

    def test_restoration_opens_visible_and_filtered_out_papers_without_changing_filters(self):
        restore = self.function_source(
            "restoreLinkedPaperSelection", "reconcilePersistentSelectionAfterFilter"
        )
        result = self.run_node(f"""
const paper = {{title: 'Stable paper'}};
const origin = {{record: paper, marker: {{id: 1}}, institutionKey: 'institution:a'}};
let requestedPaperIdentity = 'doi:10.1000/stable';
const canonicalPaperRecordsByIdentity = new Map([[requestedPaperIdentity, paper]]);
const visiblePaperSelectionByIdentity = new Map([[requestedPaperIdentity, origin]]);
const interactionState = {{selectedPaperId: null, detailMode: 'empty', selectionSource: null}};
const filters = {{task: 'detection'}};
{restore}
const visible = restoreLinkedPaperSelection(new Set([requestedPaperIdentity]));
const visibleSelection = {{
  state: visible,
  identity: interactionState.selectedPaperId,
  mode: interactionState.detailMode,
  source: interactionState.selectionSource,
}};
visiblePaperSelectionByIdentity.clear();
// Bibliographic coverage remains selectable even without a map marker.
const markerless = restoreLinkedPaperSelection(new Set([requestedPaperIdentity]));
const filtered = restoreLinkedPaperSelection(new Set());
console.log(JSON.stringify({{
  visibleSelection,
  markerless,
  filtered,
  identity: interactionState.selectedPaperId,
  mode: interactionState.detailMode,
  recordTitle: canonicalPaperRecordsByIdentity.get(interactionState.selectedPaperId).title,
  filters,
}}));
""")
        self.assertEqual(result["visibleSelection"], {
            "state": "open",
            "identity": "doi:10.1000/stable",
            "mode": "paper",
            "source": "deep-link",
        })
        self.assertEqual(result["filtered"], "filtered-out")
        self.assertEqual(result["markerless"], "open")
        self.assertEqual(result["identity"], "doi:10.1000/stable")
        self.assertEqual(result["mode"], "paper")
        self.assertEqual(result["recordTitle"], "Stable paper")
        self.assertEqual(result["filters"], {"task": "detection"})

    def test_stale_identifier_has_a_closable_non_destructive_state(self):
        restore = self.function_source(
            "restoreLinkedPaperSelection", "reconcilePersistentSelectionAfterFilter"
        )
        result = self.run_node(f"""
let requestedPaperIdentity = 'doi:10.9999/stale';
const canonicalPaperRecordsByIdentity = new Map();
const visiblePaperSelectionByIdentity = new Map();
const interactionState = {{selectedPaperId: 'old', detailMode: 'paper'}};
{restore}
console.log(JSON.stringify({{
  state: restoreLinkedPaperSelection(new Set()),
  selected: interactionState.selectedPaperId,
  mode: interactionState.detailMode,
  requested: requestedPaperIdentity,
}}));
""")
        self.assertEqual(result, {
            "state": "unavailable", "selected": None, "mode": "empty",
            "requested": "doi:10.9999/stale",
        })
        self.assertIn("Linked paper unavailable", self.app)
        self.assertIn("Your filters were not changed", self.app)
        self.assertIn("Close linked paper details", self.app)
        active = self.app[
            self.app.index("function renderActiveSelection"):
            self.app.index("\nfunction clearHoveredSelection")
        ]
        self.assertIn("!canonicalPaperRecordsByIdentity.has(requestedPaperIdentity)", active)
        self.assertIn("showLinkedPaperUnavailable()", active)

    def test_explicit_selection_and_close_push_only_the_paper_url_state(self):
        start = self.app.index("function setPersistentSelection")
        end = self.app.index("\nfunction restoreLinkedPaperSelection", start)
        # Include the shared selector used by the current compatibility wrapper.
        helpers = self.function_source("selectPaper", "selectMapMarker") + self.app[start:end]
        result = self.run_node(f"""
const interactionState = {{transientHover: {{old: true}}, detailMode: 'empty'}};
const markerHoverIntent = {{cancel() {{}}}};
let requestedPaperIdentity = '';
let pendingResultReveal = {{old: true}};
const calls = [];
function renderActiveSelection() {{ calls.push('render-selection'); }}
function requestUrlStateSync(mode) {{ calls.push(`history:${{mode}}`); }}
function syncUrlFromState() {{ calls.push(`url:${{requestedPaperIdentity}}`); }}
function scheduleMapResize() {{ calls.push('resize'); }}
{helpers}
setPersistentSelection({{identity: 'openalex:W123', contextualInstitutionId: 'institution:a'}});
const opened = requestedPaperIdentity;
const openedState = {{...interactionState}};
clearPersistentSelection();
console.log(JSON.stringify({{
  opened, openedState, closedState: interactionState,
  closed: requestedPaperIdentity,
  pendingResultReveal,
  calls,
}}));
""")
        self.assertEqual(result["opened"], "openalex:W123")
        self.assertEqual(result["openedState"]["selectedPaperId"], "openalex:W123")
        self.assertEqual(result["openedState"]["contextualInstitutionId"], "institution:a")
        self.assertEqual(result["openedState"]["detailMode"], "paper")
        self.assertIsNone(result["closedState"]["selectedPaperId"])
        self.assertEqual(result["closedState"]["detailMode"], "empty")
        self.assertEqual(result["closed"], "")
        self.assertIsNone(result["pendingResultReveal"])
        self.assertEqual(result["calls"].count("history:push"), 2)
        self.assertIn("url:openalex:W123", result["calls"])
        self.assertIn("url:", result["calls"])
        self.assertNotIn("renderRecords", helpers)

    def test_copy_paper_link_uses_canonical_filters_and_accessible_feedback(self):
        copy = self.app[
            self.app.index("async function copySelectedPaperUrl"):
            self.app.index("\nfunction formatResolutionValue")
        ]
        result = self.run_node(f"""
let requestedPaperIdentity = 'doi:10.1000/copied';
let copied = '';
function currentViewState() {{ return {{task: 'detection', paper: ''}}; }}
function canonicalViewUrl(state) {{
  return `https://example.test/map?task=${{state.task}}&paper=${{encodeURIComponent(state.paper)}}`;
}}
async function writeViewUrlToClipboard(url) {{ copied = url; }}
function showCopyPaperLinkFeedback() {{}}
{copy}
copySelectedPaperUrl().then(url => console.log(JSON.stringify({{url, copied}})));
""")
        expected = (
            "https://example.test/map?task=detection&"
            "paper=doi%3A10.1000%2Fcopied"
        )
        self.assertEqual(result["url"], expected)
        self.assertEqual(result["copied"], expected)
        self.assertIn('button.type = "button"', self.app)
        self.assertIn('button.textContent = "Copy paper link"', self.app)
        self.assertIn('status.setAttribute("aria-live", "polite")', self.app)
        self.assertIn("min-height: 44px", self.css)

    def test_popstate_restores_or_closes_and_hover_is_not_serialized(self):
        popstate = self.app[
            self.app.index('window.addEventListener("popstate"'):
            self.app.index('window.addEventListener("resize"', self.app.index('window.addEventListener("popstate"'))
        ]
        restore_location = self.app[
            self.app.index("function restoreViewStateFromLocation"):
            self.app.index("\nfunction renderActiveFilterChips")
        ]
        hover = self.app[
            self.app.index("function activateHoverPreview"):
            self.app.index("\nfunction clearHoverPreview")
        ]
        self.assertIn("restoreViewStateFromLocation()", popstate)
        self.assertIn("parseViewState(window.location.search)", restore_location)
        self.assertEqual(restore_location.count("renderRecords();"), 1)
        self.assertNotIn("requestedPaperIdentity", hover)
        self.assertNotIn("syncUrlFromState", hover)
        self.assertIn("markerHoverIntent.schedule", hover)

    def test_render_reuses_existing_identity_indexes_and_filter_match_set(self):
        pipeline = self.app[
            self.app.index("function renderRecordsForGeneration"):
            self.app.index("\n// A category is active")
        ]
        restore = self.function_source(
            "restoreLinkedPaperSelection", "reconcilePersistentSelectionAfterFilter"
        )
        self.assertIn("visiblePaperSelectionByIdentity.set", pipeline)
        self.assertIn("filteredSets.matchingPaperIdentities", pipeline)
        self.assertIn("canonicalPaperRecordsByIdentity.get", restore)
        self.assertNotIn(".filter(", restore)
        self.assertNotIn("records.forEach", restore)

    def test_deep_linked_details_use_the_same_metadata_status_block(self):
        details = self.app[
            self.app.index("function paperDetailsHtml"):
            self.app.index("\nfunction resultBadges")
        ]
        show = self.app[
            self.app.index("function showPaperDetails"):
            self.app.index("\nfunction showLinkedPaperUnavailable")
        ]
        self.assertIn("paperMetadataStatusHtml(record)", details)
        self.assertIn("paperDetailsHtml(", show)


if __name__ == "__main__":
    unittest.main()
