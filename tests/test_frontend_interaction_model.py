import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


class FrontendInteractionModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web/style.css").read_text(encoding="utf-8")
        cls.html = (ROOT / "web/index.html").read_text(encoding="utf-8")

    def source(self, start, end):
        return self.app[self.app.index(start):self.app.index(end, self.app.index(start))]

    def test_state_names_the_three_entities_and_navigation_context(self):
        state = self.source("const interactionState = {", "\nconst markerHoverIntent")
        for field in (
            "selectedPaperId", "contextualInstitutionId", "pinnedMapMarkerId",
            "mapParentMarkerId", "detailMode", "selectionSource", "transientHover",
        ):
            self.assertIn(field, state)
        for mode in ("empty", "institution-papers", "paper"):
            self.assertIn(f'"{mode}"', self.app)
        for source in (
            "unique-paper", "institution-record", "map-institution", "map-paper",
            "deep-link",
        ):
            self.assertIn(f'"{source}"', self.app)

    def test_marker_click_selects_marker_without_selecting_a_paper_or_toggling(self):
        select_marker = self.source("function selectMapMarker", "\nfunction setPersistentSelection")
        self.assertIn("selectedPaperId = null", select_marker)
        self.assertIn('detailMode = "institution-papers"', select_marker)
        self.assertIn('selectionSource = "map-institution"', select_marker)
        self.assertNotIn("paperIdentity(", select_marker)
        self.assertNotIn("clearPersistentSelection", select_marker)
        binding = self.source("institutionGroups.forEach", "\n  const linkedPaperState")
        self.assertIn("click: () => selectMapMarker(markerEntry)", binding)

    def test_hover_is_delayed_transient_and_cannot_override_persistent_state(self):
        hover = self.source("function activateHoverPreview", "\nfunction clearHoverPreview")
        self.assertIn('if (interactionState.detailMode !== "empty") return', hover)
        self.assertIn("markerHoverIntent.schedule", hover)
        self.assertNotIn("selectedPaperId =", hover)
        self.assertNotIn("requestedPaperIdentity", hover)
        self.assertNotIn("syncUrlFromState", hover)
        self.assertIn("delay: 125", self.app)

    def test_institution_papers_use_one_deduplicated_current_view_set(self):
        helper = ROOT / "web/marker_size_helpers.js"
        script = r"""
const helpers = require(process.argv[1]);
const records = [
  {site: 'A', paper: 'P', task: 'detection'},
  {site: 'A', paper: 'P', task: 'detection'},
  {site: 'A', paper: 'Q', task: 'source_attribution'},
  {site: 'B', paper: 'R', task: 'detection'},
];
const group = helpers.groupInstitutionRecords(records, r => r.site, r => r.paper)[0];
const counts = helpers.getInstitutionTaskCounts(group.records, r => r.paper);
process.stdout.write(JSON.stringify({
  groupCount: group.paperCount,
  list: [...new Set(group.records.map(r => r.paper))],
  counts,
  dominant: helpers.getDominantInstitutionTask(counts),
}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper)], check=True,
            capture_output=True, text=True,
        )
        value = json.loads(result.stdout)
        self.assertEqual(value["groupCount"], 2)
        self.assertEqual(value["list"], ["P", "Q"])
        self.assertEqual(value["counts"]["detection"], 1)
        self.assertEqual(value["counts"]["source_attribution"], 1)
        self.assertEqual(value["dominant"], "mixed")
        self.assertIn("markerPapersInCurrentView(markerEntry)", self.app)

    def test_map_paper_back_and_cross_entry_clear_stale_parent(self):
        map_paper = self.source(
            "function selectPaperFromInstitutionList", "\nfunction returnToInstitution"
        )
        self.assertIn("mapParentMarkerId: markerEntry.institutionKey", map_paper)
        self.assertIn('source: "map-paper"', map_paper)
        details = self.source("function showPaperDetails", "\nfunction showLinkedPaperUnavailable")
        self.assertIn("back.dataset.backToInstitution", details)
        direct = self.source("function selectResultItem", "\nfunction selectPaperFromInstitutionList")
        self.assertEqual(direct.count("mapParentMarkerId: null"), 2)
        self.assertIn('source: "unique-paper"', direct)
        self.assertIn('source: "institution-record"', direct)

    def test_selected_paper_connections_use_a_visible_coordinate_origin(self):
        descriptor = self.source(
            "function selectedPaperDescriptor", "\nfunction renderPaperSelection"
        )
        self.assertIn(
            "const record = visibleOrigin?.record || canonicalPaperRecordsByIdentity.get(identity)",
            descriptor,
        )
        self.assertNotIn(
            "const record = canonicalPaperRecordsByIdentity.get(identity) || visibleOrigin?.record",
            descriptor,
        )

    def test_result_primary_and_related_semantics_survive_lazy_rendering(self):
        sync = self.source("function syncResultHighlights", "\nfunction resolveShowInResultsTarget")
        self.assertIn("is-selection-primary", sync)
        self.assertIn("is-selection-related", sync)
        self.assertIn("contextualInstitutionId", sync)
        self.assertIn("aria-current", sync)
        append = self.source("function appendResultChunk", "\nfunction observeResultSentinel")
        prepare = self.source("function prepareFirstResultViewport", "\nfunction scheduleResultsMasonryLayout")
        self.assertIn("syncResultHighlights()", append)
        self.assertIn("syncResultHighlights()", prepare)
        self.assertIn(".result-item.is-selection-primary", self.css)
        self.assertIn(".result-item.is-selection-related", self.css)

    def test_filter_reconciliation_distinguishes_map_children_and_direct_papers(self):
        reconcile = self.source(
            "function reconcilePersistentSelectionAfterFilter", "\nfunction activateHoverPreview"
        )
        self.assertIn("mapParentMarkerId", reconcile)
        self.assertIn('detailMode = "institution-papers"', reconcile)
        self.assertIn("resetPersistentState()", reconcile)
        self.assertIn("return restoreLinkedPaperSelection", reconcile)
        direct = self.source("function restoreLinkedPaperSelection", "\nfunction reconcilePersistentSelectionAfterFilter")
        self.assertIn('return matchingPaperIdentities.has(requestedPaperIdentity) ? "open" : "filtered-out"', direct)

    def test_copy_url_and_accessible_copy_match_entity_semantics(self):
        self.assertIn('"marker", "paper", "view"', self.app)
        self.assertIn('marker: params.get("marker") || ""', self.app)
        self.assertIn("Open institution papers.", self.app)
        self.assertIn("Select a paper or explore an institution marker", self.html)
        self.assertIn("Hover over an institution for a preview", self.app)
        self.assertIn('data-marker-paper=', self.app)
        self.assertIn('back.className = "back-to-institution-button"', self.app)


if __name__ == "__main__":
    unittest.main()
