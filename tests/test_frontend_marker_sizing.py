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

    def test_tooltip_lifecycle_and_marker_stroke_are_explicit(self):
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
        self.assertIn('color: "#1f5964"', base_style)
        self.assertNotIn("#ffffff", base_style)
        self.assertIn("border: 1.75px solid #1f5964", style_source)
        self.assertIn("background: var(--detection)", style_source)

    def test_public_preview_record_counts_are_unchanged(self):
        map_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_map_data.json").read_text()
        )
        paper_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )

        self.assertEqual(len(map_payload["records"]), 788)
        self.assertEqual(len(paper_payload["records"]), 395)


if __name__ == "__main__":
    unittest.main()
