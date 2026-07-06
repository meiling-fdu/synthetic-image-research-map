import json
import subprocess
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


class FrontendMarkerSizingTests(unittest.TestCase):
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
        self.assertEqual(values["singular"], "1 paper in current view")
        self.assertEqual(values["plural"], "3 papers in current view")
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
        self.assertIn('map.on("mousemove"', app_source)
        self.assertIn(
            'mapElement.addEventListener("mouseleave"', app_source
        )
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
        self.assertIn("let pinnedInstitutionKey", app_source)
        self.assertIn("const previousPin =", app_source)
        self.assertIn("if (pinnedPaperRecord)", app_source)
        self.assertIn(
            "closePaperDetailsButton.addEventListener",
            app_source,
        )

    def test_public_preview_record_counts_are_unchanged(self):
        map_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_map_data.json").read_text()
        )
        paper_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )

        self.assertEqual(len(map_payload["records"]), 827)
        self.assertEqual(len(paper_payload["records"]), 402)


if __name__ == "__main__":
    unittest.main()
