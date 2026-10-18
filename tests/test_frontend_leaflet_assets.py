"""Pin the CDN stylesheet to Leaflet's independently verified 1.9.4 digest."""
from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StylesheetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.leaflet_stylesheets = []

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if (tag == "link" and attributes.get("rel") == "stylesheet"
                and "leaflet" in attributes.get("href", "")):
            self.leaflet_stylesheets.append(attributes)


class LeafletAssetTests(unittest.TestCase):
    def test_leaflet_stylesheet_uses_verified_sri(self):
        parser = StylesheetParser()
        parser.feed((ROOT / "web/index.html").read_text(encoding="utf-8"))
        self.assertEqual(len(parser.leaflet_stylesheets), 1)
        stylesheet = parser.leaflet_stylesheets[0]
        # Verified from CDN bytes and https://leafletjs.com/download.html.
        self.assertEqual(stylesheet["href"],
                         "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css")
        self.assertEqual(stylesheet["integrity"],
                         "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=")
        self.assertEqual(stylesheet["crossorigin"], "")


if __name__ == "__main__":
    unittest.main()
