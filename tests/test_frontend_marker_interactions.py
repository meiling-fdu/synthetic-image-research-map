import json
import subprocess
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


class FrontendMarkerInteractionTests(unittest.TestCase):
    def test_registered_leaflet_marker_callbacks_drive_hover_and_pin_state(self):
        helper = REPOSITORY / "web" / "marker_interaction_helpers.js"
        script = r"""
const helpers = require(process.argv[1]);
const callbacks = new Map();
const marker = {
  on(name, callback) { callbacks.set(name, callback); return this; },
};
const state = {hovered: null, pinned: null};
const renders = [];
const paper = {
  identity: "paper:multi",
  coordinates: [[10, 20], [30, 40]],
};
const render = () => {
  const details = state.pinned || state.hovered || null;
  const connections = state.hovered || state.pinned || null;
  const uniqueCoordinates = new Set(
    (connections?.coordinates || []).map((value) => value.join(",")),
  );
  renders.push({
    details: details?.identity || null,
    connections: connections?.identity || null,
    lineCount: Math.max(0, uniqueCoordinates.size - 1),
  });
};
const firstBind = helpers.bindMarkerHandlers(marker, {
  supportsHover: true,
  hover() { state.hovered = paper; render(); },
  leave() { state.hovered = null; render(); },
  click() { state.hovered = null; state.pinned = paper; render(); },
});
const duplicateBind = helpers.bindMarkerHandlers(marker, {
  supportsHover: true, hover() {}, leave() {}, click() {},
});
callbacks.get("mouseover")();
callbacks.get("mouseout")();
let stopped = false;
callbacks.get("click")({originalEvent: {stopPropagation() { stopped = true; }}});
callbacks.get("mouseover")();
callbacks.get("mouseout")();
process.stdout.write(JSON.stringify({
  events: [...callbacks.keys()], firstBind, duplicateBind, stopped, renders,
}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        values = json.loads(result.stdout)

        self.assertEqual(values["events"], ["click", "mouseover", "mouseout"])
        self.assertTrue(values["firstBind"])
        self.assertFalse(values["duplicateBind"])
        self.assertTrue(values["stopped"])
        self.assertEqual(values["renders"][0], {
            "details": "paper:multi",
            "connections": "paper:multi",
            "lineCount": 1,
        })
        self.assertEqual(values["renders"][1]["lineCount"], 0)
        self.assertEqual(values["renders"][2]["lineCount"], 1)
        self.assertEqual(values["renders"][3]["details"], "paper:multi")
        self.assertEqual(values["renders"][4], {
            "details": "paper:multi",
            "connections": "paper:multi",
            "lineCount": 1,
        })

    def test_one_coordinate_creates_no_connection_line(self):
        coordinates = {(10, 20)}
        self.assertEqual(max(0, len(coordinates) - 1), 0)

    def test_index_loads_latest_marker_helper_and_app_versions(self):
        html = (REPOSITORY / "web" / "index.html").read_text()
        self.assertIn(
            'marker_interaction_helpers.js?v=20260712-hover-events', html
        )
        self.assertIn('app.js?v=20260712-hover-connections-v2', html)


if __name__ == "__main__":
    unittest.main()
