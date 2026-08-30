import json
import subprocess
import unittest
from pathlib import Path

from scripts.export_public_preview import build_preview, identity_key
from scripts.paper_exclusions import read_exclusion_rows


REPOSITORY = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


class FrontendMarkerSizingTests(unittest.TestCase):
    def test_marker_grouping_preserves_distinct_sites_for_one_institution(self):
        helper = REPOSITORY / "web" / "marker_size_helpers.js"
        app = (REPOSITORY / "web/app.js").read_text()
        start = app.index("function markerInstitutionIdentity(")
        end = app.index("\nfunction canonicalInstitutionIds", start)
        marker_identity = app[start:end]
        script = f"""
const helpers = require(process.argv[1]);
const institutionIdentity = (record) => `id:${{record.institution_id}}`;
{marker_identity}
const base = {{paper: 'paper:1', institution_id: 'institution:deakin'}};
const records = [
  {{...base, location_id: 'location:burwood', latitude: -37.8475136, longitude: 145.1149474}},
  {{...base, location_id: 'location:burwood', latitude: -37.8475136, longitude: 145.1149474}},
  {{...base, location_id: 'location:waurn-ponds', latitude: -38.1989397, longitude: 144.2969971}},
];
const groups = helpers.groupInstitutionRecords(records, markerInstitutionIdentity, (record) => record.paper);
const coordinateGroups = helpers.groupInstitutionRecords(
  records.map(({{location_id, ...record}}) => record), markerInstitutionIdentity, (record) => record.paper,
);
process.stdout.write(JSON.stringify({{
  keys: groups.map((group) => group.key),
  sizes: groups.map((group) => group.records.length),
  coordinateGroupCount: coordinateGroups.length,
}}));
"""
        completed = subprocess.run(
            [str(NODE), "-e", script, str(helper)], check=True,
            capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(len(result["keys"]), 2)
        self.assertEqual(result["sizes"], [2, 1])
        self.assertEqual(result["coordinateGroupCount"], 2)

    def test_marker_sizing_and_filtered_unique_counts(self):
        helper = REPOSITORY / "web" / "marker_size_helpers.js"
        script = """
const helpers = require(process.argv[1]);
const records = [
  {institution: "one", paper: "a"},
  {institution: "one", paper: "a"},
  {institution: "one", paper: "b"},
  {institution: "two", paper: "c"},
];
const group = (items) => helpers.groupInstitutionRecords(
  items,
  (record) => record.institution,
  (record) => record.paper,
);
process.stdout.write(JSON.stringify({
  minimum: helpers.getMarkerRadius(1),
  larger: helpers.getMarkerRadius(4),
  capped: helpers.getMarkerRadius(10000),
  maximum: helpers.MAX_MARKER_RADIUS,
  allCount: group(records)[0].paperCount,
  filteredCount: group(records.filter((record) => record.paper === "a"))[0].paperCount,
  singular: helpers.formatInstitutionPaperCount(1),
  plural: helpers.formatInstitutionPaperCount(3),
  detectionTask: helpers.normalizeTaskLabel("Detection"),
  attributionTask: helpers.normalizeTaskLabel("source attribution"),
  combinedTask: helpers.normalizeTaskLabel("Detection + source attribution"),
  unknownTask: helpers.normalizeTaskLabel(""),
}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        values = json.loads(result.stdout)

        self.assertEqual(values["minimum"], 6)
        self.assertGreater(values["larger"], values["minimum"])
        self.assertEqual(values["capped"], values["maximum"])
        self.assertEqual(values["allCount"], 2)
        self.assertEqual(values["filteredCount"], 1)
        self.assertEqual(values["singular"], "1 unique paper in current view")
        self.assertEqual(values["plural"], "3 unique papers in current view")
        self.assertEqual(values["detectionTask"], "detection")
        self.assertEqual(values["attributionTask"], "source_attribution")
        self.assertEqual(
            values["combinedTask"], "detection_and_source_attribution"
        )
        self.assertEqual(values["unknownTask"], "unknown")

    def test_marker_task_composition_uses_unique_visible_papers(self):
        helper = REPOSITORY / "web" / "marker_size_helpers.js"
        script = """
const helpers = require(process.argv[1]);
const identity = (record) => record.paper;
const counts = (records) => helpers.getInstitutionTaskCounts(records, identity);
const dominant = (records) => helpers.getDominantInstitutionTask(counts(records));
const duplicateRecords = [
  {paper: "a", task: "detection"},
  {paper: "a", task: "detection"},
  {paper: "b", task: "source_attribution"},
];
process.stdout.write(JSON.stringify({
  detection: dominant([{paper: "a", task: "detection"}]),
  attribution: dominant([{paper: "a", task: "source_attribution"}]),
  combined: dominant([
    {paper: "a", task: "detection_and_source_attribution"},
  ]),
  dominantDetection: dominant([
    ...duplicateRecords,
    {paper: "c", task: "detection"},
  ]),
  tied: dominant(duplicateRecords),
  unknown: dominant([{paper: "a"}]),
  duplicateCounts: counts(duplicateRecords),
  breakdown: helpers.formatTaskBreakdown(counts(duplicateRecords)),
}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        values = json.loads(result.stdout)

        self.assertEqual(values["detection"], "detection")
        self.assertEqual(values["attribution"], "source_attribution")
        self.assertEqual(
            values["combined"], "detection_and_source_attribution"
        )
        self.assertEqual(values["dominantDetection"], "detection")
        self.assertEqual(values["tied"], "mixed")
        self.assertEqual(values["unknown"], "unknown")
        self.assertEqual(values["duplicateCounts"]["detection"], 1)
        self.assertEqual(values["duplicateCounts"]["source_attribution"], 1)
        self.assertIn("Detection: 1", values["breakdown"])

    def test_tooltip_lifecycle_and_marker_palette_are_explicit(self):
        app_source = (REPOSITORY / "web/app.js").read_text()
        style_source = (REPOSITORY / "web/style.css").read_text()
        base_style = app_source.split(
            "const BASE_MARKER_STYLE = {", 1
        )[1].split("};", 1)[0]

        self.assertIn("permanent: false", app_source)
        self.assertIn("sticky: false", app_source)
        self.assertIn("function closeActiveInstitutionTooltip(", app_source)
        self.assertIn("function openInstitutionTooltip(", app_source)
        self.assertNotIn('map.on("mousemove"', app_source)
        self.assertIn(
            'mapElement.addEventListener("mouseleave"', app_source
        )
        self.assertIn("paperDetails.contains(event.relatedTarget)", app_source)
        self.assertNotIn('paperDetails.addEventListener("mouseleave"', app_source)
        self.assertNotIn(".bindTooltip(", app_source)
        self.assertIn("fillOpacity: 0.5", base_style)
        self.assertIn("opacity: 0.68", base_style)
        self.assertNotIn("#ffffff", base_style)
        self.assertIn("--map-detection-fill: #5a9da6", style_source)
        self.assertIn("--map-detection-stroke: #376f78", style_source)
        self.assertIn("--map-attribution-fill: #c58a55", style_source)
        self.assertIn("--map-mixed-fill: #8b6fa8", style_source)
        self.assertIn("--map-unknown-fill: #8a98a3", style_source)
        self.assertIn(
            "border: 1.5px solid rgb(55 111 120 / 68%)", style_source
        )
        self.assertIn(
            "background: rgb(90 157 166 / 50%)", style_source
        )
        self.assertIn("const interactionState = {", app_source)
        self.assertIn("transientHover: null", app_source)
        self.assertIn("selectedPaperId: null", app_source)
        self.assertIn('detailMode: "empty"', app_source)
        self.assertIn("if (interactionState.detailMode !== \"empty\") return", app_source)
        self.assertIn(
            "closePaperDetailsButton.addEventListener",
            app_source,
        )

    def test_selection_status_omits_long_paper_titles(self):
        app_source = (REPOSITORY / "web/app.js").read_text()
        style_source = (REPOSITORY / "web/style.css").read_text()
        interaction_body = app_source.split(
            "function showPaperInteraction(selection, { preserveScroll = false } = {}) {", 1
        )[1].split("\nfunction institutionLocationText", 1)[0]

        self.assertIn(
            "`Showing ${visibleCount} visible institution record",
            interaction_body,
        )
        self.assertIn('lineCount ? " · Connections shown." : "."', interaction_body)
        self.assertNotIn("recordTitle(record)", interaction_body)
        self.assertNotIn("paperTitle", interaction_body)
        self.assertNotIn(" for “", interaction_body)
        self.assertIn("white-space: nowrap", style_source)
        self.assertIn("overflow: hidden", style_source)
        self.assertIn("text-overflow: ellipsis", style_source)

    def test_pinned_details_survive_hover_cleanup_and_close_explicitly(self):
        app_source = (REPOSITORY / "web/app.js").read_text()
        restore_body = app_source.split(
            "function renderActiveSelection({ preserveScroll = false } = {}) {", 1
        )[1].split("\nfunction activateHoverPreview", 1)[0]
        hover_body = app_source.split(
            "function activateHoverPreview(", 1
        )[1].split("\nfunction clearHoverPreview", 1)[0]

        self.assertIn('interactionState.detailMode === "paper"', restore_body)
        self.assertIn('interactionState.detailMode === "institution-papers"', restore_body)
        self.assertIn('if (interactionState.detailMode !== "empty") return', hover_body)
        self.assertIn('closePaperDetailsButton.addEventListener("click", () => {', app_source)

        clear_body = app_source.split(
            "function clearHoverPreview(marker, event = null) {", 1
        )[1].split("\nfunction resultInstitutionSelection", 1)[0]
        self.assertIn("clearHoveredSelection(marker)", clear_body)
        self.assertNotIn("selectedPaperId = null", clear_body)
        self.assertIn("selectMapMarker(markerEntry)", app_source)
        self.assertNotIn('paperDetails.addEventListener("mouseleave"', app_source)
        self.assertIn("MarkerInteractionHelpers.bindMarkerHandlers", app_source)

    def test_persistent_paper_lines_take_precedence_over_hover(self):
        app_source = (REPOSITORY / "web/app.js").read_text()
        active_body = app_source.split(
            "function renderActiveSelection({ preserveScroll = false } = {}) {", 1
        )[1].split("\nfunction clearHoveredSelection", 1)[0]
        interaction_body = app_source.split(
            "function showPaperInteraction(selection, { preserveScroll = false } = {}) {", 1
        )[1].split("\nfunction renderActiveSelection", 1)[0]
        connection_body = app_source.split(
            "function renderConnectionSelection(selection, mode) {", 1
        )[1].split("\nfunction renderPaperSelection", 1)[0]
        draw_body = app_source.split(
            "function drawConnectionLines(relatedEntries, currentRecord, targetLayer) {", 1
        )[1].split("\nfunction relatedMarkerEntries", 1)[0]

        self.assertIn('interactionState.detailMode === "paper"', active_body)
        self.assertIn('if (interactionState.detailMode !== "empty") return', app_source)
        self.assertIn("renderPaperSelection(selection", interaction_body)
        self.assertIn(
            "renderConnectionSelection(", interaction_body
        )
        self.assertIn("hoverConnectionLayer.clearLayers()", connection_body)
        self.assertIn("selectedConnectionLayer.clearLayers()", connection_body)
        self.assertIn("drawConnectionLines(", connection_body)
        self.assertIn('const targetLayer = isHover ? hoverConnectionLayer : selectedConnectionLayer', connection_body)
        self.assertIn("if (locations.length < 2)", draw_body)
        self.assertIn("return 0", draw_body)

    def test_rerender_restores_pinned_paper_from_shared_identity_state(self):
        app_source = (REPOSITORY / "web/app.js").read_text()
        render_body = app_source.split(
            "function renderRecords() {", 1
        )[1].split("\nfunction configureYearRange()", 1)[0]

        self.assertIn("visiblePaperSelectionByIdentity = new Map()", render_body)
        self.assertIn("visiblePaperSelectionByIdentity.set", render_body)
        self.assertIn("reconcilePersistentSelectionAfterFilter(", render_body)
        self.assertIn("filteredSets.matchingPaperIdentities", render_body)

    def test_marker_handlers_are_rebuilt_once_and_ai_summary_is_absent(self):
        app_source = (REPOSITORY / "web/app.js").read_text()
        style_source = (REPOSITORY / "web/style.css").read_text()
        render_body = app_source.split(
            "function renderRecords() {", 1
        )[1].split("\nfunction configureYearRange()", 1)[0]
        details_body = app_source.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultContent", 1)[0]

        self.assertEqual(render_body.count('markerLayer.clearLayers();'), 1)
        self.assertEqual(
            render_body.count("MarkerInteractionHelpers.bindMarkerHandlers"), 1
        )
        self.assertNotIn("AI-generated summary", details_body)
        self.assertNotIn("ai_summary", details_body)
        self.assertNotIn("paper-ai-summary", style_source)

        for metadata in ("Authors", "Year", "Affiliations", "Abstract"):
            self.assertIn(metadata, details_body)
        for internal_metadata in ("Resolution", "Needs review", "Current institution"):
            self.assertNotIn(internal_metadata, details_body)
        self.assertIn("paperExternalLinks(record)", details_body)

    def test_connection_lines_use_visible_slate_style(self):
        app_source = (REPOSITORY / "web/app.js").read_text()
        style_source = (REPOSITORY / "web/style.css").read_text()
        connection_style = app_source.split(
            "const CONNECTION_LINE_STYLE = {", 1
        )[1].split("};", 1)[0]

        self.assertIn("--map-connection-line: #2f4554", style_source)
        self.assertIn('getPropertyValue("--map-connection-line")', connection_style)
        self.assertIn('|| "#2f4554"', connection_style)
        self.assertIn("weight: 2.4", connection_style)
        self.assertIn("opacity: 0.68", connection_style)

    def test_public_preview_counts_match_current_pipeline_eligibility(self):
        map_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_map_data.json").read_text()
        )
        paper_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )

        rebuilt_map, summary = build_preview(
            map_payload["records"],
            None,
            "medium",
            False,
            (),
            exclusion_rows=read_exclusion_rows(),
        )
        self.assertEqual(
            len(map_payload["records"]), len(rebuilt_map["records"])
        )
        self.assertEqual(
            len(map_payload["records"]), summary["records_exported"]
        )
        self.assertEqual(
            len(paper_payload["records"]),
            len({identity_key(record) for record in paper_payload["records"]}),
        )


if __name__ == "__main__":
    unittest.main()
