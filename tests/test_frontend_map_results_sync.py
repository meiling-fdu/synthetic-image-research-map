import json
import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendMapResultsSyncTests(unittest.TestCase):
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

    def test_result_institution_controls_select_a_visible_marker_without_filtering(self):
        institution = self.app[
            self.app.index("function institutionResultContent"):
            self.app.index("\nfunction uniquePaperInstitutions")
        ]
        papers = self.app[
            self.app.index("function resultInstitutions"):
            self.app.index("\nfunction paperResultContent")
        ]
        self.assertIn("institutionFocusButtonHtml", institution)
        self.assertIn("institutionFocusButtonHtml", papers)
        self.assertNotIn("institutionFilterButtonHtml", institution + papers)
        selection = self.app[
            self.app.index("function resultInstitutionSelection"):
            self.app.index("\nfunction renderRecords")
        ]
        self.assertIn("visibleMarkerEntryByInstitutionKey.get", selection)
        self.assertIn("setPersistentSelection(selection)", selection)
        self.assertNotIn("activeInstitutionFilter", selection)
        self.assertNotIn("renderRecords", selection)
        self.assertNotIn("applyInstitutionFilter", selection)
        helper = selection[
            selection.index("function resultInstitutionSelection"):
            selection.index("\nfunction previewInstitutionFromResult")
        ]
        result = self.run_node(f"""
const item = {{dataset: {{resultIndex: '0', resultGeneration: '7'}}}};
const button = {{
  dataset: {{focusInstitution: 'institution:x'}},
  closest() {{ return item; }},
}};
const marker = {{id: 'marker:x'}};
const resultsRenderGeneration = 7;
const resultsPipeline = {{displayedResults: [{{paper: 'paper:one'}}]}};
const visibleMarkerEntryByInstitutionKey = new Map([[
  'institution:x', {{records: [{{paper: 'paper:one'}}], record: {{paper: 'paper:one'}}, marker}},
]]);
function paperIdentity(record) {{ return record.paper; }}
{helper}
const selected = resultInstitutionSelection(button);
console.log(JSON.stringify({{
  identity: selected.identity,
  institutionKey: selected.institutionKey,
  marker: selected.marker.id,
  scope: selected.resultScope,
}}));
""")
        self.assertEqual(result, {
            "identity": "paper:one",
            "institutionKey": "institution:x",
            "marker": "marker:x",
            "scope": "paper",
        })

    def test_marker_selection_maps_to_all_corresponding_result_indexes(self):
        start = self.app.index("function interactionResultIndexes")
        end = self.app.index("\nfunction renderedResultItem", start)
        helper = self.app[start:end]
        result = self.run_node(f"""
{helper}
const pipeline = {{
  resultIndexesByPaperIdentity: new Map([
    ['paper:a', new Set([0, 3])],
    ['paper:b', new Set([1])],
  ]),
  resultIndexesByInstitutionKey: new Map([
    ['institution:x', new Set([0, 1, 4])],
  ]),
}};
const markerSelection = {{
  identity: 'paper:a', resultPaperIdentities: ['paper:a', 'paper:b'],
  resultScope: 'institution', institutionKey: 'institution:x',
}};
const paperSelection = {{
  identity: 'paper:a', resultPaperIdentities: ['paper:a'],
  resultScope: 'paper', institutionKey: 'institution:x',
}};
console.log(JSON.stringify({{
  marker: [...interactionResultIndexes(markerSelection, pipeline)].sort(),
  paper: [...interactionResultIndexes(paperSelection, pipeline)].sort(),
}}));
""")
        self.assertEqual(result["marker"], [0, 1, 3, 4])
        self.assertEqual(result["paper"], [0, 3])

    def test_open_details_resolves_every_visible_institution_for_the_paper(self):
        start = self.app.index("function relatedMarkerEntries")
        end = self.app.index("\nfunction renderConnectionSelection", start)
        helper = self.app[start:end]
        result = self.run_node(f"""
function paperIdentity(record) {{ return record.paper; }}
const visibleMarkerEntries = [
  {{institutionKey: 'a', records: [{{paper: 'paper:one'}}, {{paper: 'paper:two'}}]}},
  {{institutionKey: 'b', records: [{{paper: 'paper:one'}}]}},
  {{institutionKey: 'c', records: [{{paper: 'paper:three'}}]}},
];
{helper}
console.log(JSON.stringify(
  relatedMarkerEntries({{identity: 'paper:one'}}).map(entry => entry.institutionKey)
));
""")
        self.assertEqual(result, ["a", "b"])
        connection = self.app[
            self.app.index("function renderConnectionSelection"):
            self.app.index("\nfunction setMarkerSelectionState")
        ]
        self.assertIn('isCurrent ? "current" : isRelated ? "related" : "dimmed"', connection)
        self.assertIn("entry.institutionKey === selection.institutionKey", connection)
        marker_state = self.app[
            self.app.index("function setMarkerSelectionState"):
            self.app.index("\nfunction renderPaperSelection")
        ]
        self.assertIn("is-paper-pinned", marker_state)
        self.assertIn("is-paper-selection-origin", marker_state)

    def test_temporary_hover_and_persistent_selection_are_distinct(self):
        state = self.app[
            self.app.index("const interactionState = {"):
            self.app.index("\nlet activeInstitutionTooltipMarker")
        ]
        self.assertIn("hovered: null", state)
        self.assertIn("selected: null", state)
        active = self.app[
            self.app.index("function renderActiveSelection"):
            self.app.index("\nfunction setHoveredSelection")
        ]
        self.assertIn("interactionState.selected || interactionState.hovered", active)
        self.assertIn("interactionState.hovered || interactionState.selected", active)
        self.assertIn("syncResultHighlights()", active)
        self.assertIn(".result-item.is-interaction-hovered", self.css)
        self.assertIn(".result-item.is-interaction-selected", self.css)

    def test_incremental_results_reapply_highlights_and_offer_explicit_reveal(self):
        append = self.app[
            self.app.index("function appendResultChunk"):
            self.app.index("\nfunction observeResultSentinel")
        ]
        prepare = self.app[
            self.app.index("function prepareFirstResultViewport"):
            self.app.index("\nfunction scheduleResultsMasonryLayout")
        ]
        for source in (append, prepare):
            self.assertIn("syncResultHighlights()", source)
            self.assertIn("continuePendingResultReveal()", source)
        reveal = self.app[
            self.app.index("function selectionNeedsResultsReveal"):
            self.app.index("\nfunction createResultItem")
        ]
        self.assertIn("data-show-selection-in-results", reveal)
        self.assertIn("appendResultChunk(", reveal)
        self.assertEqual(reveal.count("scrollIntoView("), 1)
        self.assertIn('item.scrollIntoView({ block: "nearest", behavior: "auto" })', reveal)
        self.assertIn("pendingResultReveal.generation !== resultsRenderGeneration", reveal)

    def test_filter_view_pagination_and_dataset_changes_restore_linked_state(self):
        render = self.app[
            self.app.index("function renderRecordsForGeneration"):
            self.app.index("\n// A category is active")
        ]
        self.assertIn("restoreLinkedPaperSelection(", render)
        self.assertIn("filteredSets.matchingPaperIdentities", render)
        self.assertIn('linkedPaperState === "unavailable"', render)
        view = self.app[
            self.app.index("function selectResultsView"):
            self.app.index("\nfunction baseMapStatusText")
        ]
        self.assertIn("interactionState.hovered = null", view)
        self.assertNotIn("clearPaperInteraction", view)
        results = self.app[
            self.app.index("function renderResults"):
            self.app.index("\nfunction selectResultsView")
        ]
        self.assertIn("pendingResultReveal = null", results)
        dataset = self.app[
            self.app.index("function displayDataset"):
            self.app.index("\nasync function loadData")
        ]
        self.assertIn("clearPaperInteraction(false)", dataset)

    def test_highlight_sync_uses_visible_indexes_and_never_triggers_a_filter_render(self):
        sync = self.app[
            self.app.index("function addResultIndex"):
            self.app.index("\nfunction createResultItem")
        ]
        self.assertIn("resultIndexesByPaperIdentity", sync)
        self.assertIn("resultIndexesByInstitutionKey", sync)
        self.assertIn("resultsList.querySelectorAll", sync)
        self.assertNotIn("records.filter", sync)
        self.assertNotIn("paperRecords", sync)
        self.assertNotIn("renderRecords()", sync)


if __name__ == "__main__":
    unittest.main()
