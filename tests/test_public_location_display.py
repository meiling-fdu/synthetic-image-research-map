import json
import unittest
from pathlib import Path

from scripts.country_normalization import public_location_display
from scripts.curated_export import normalize_regional_location
from scripts.export_public_preview import build_preview


ROOT = Path(__file__).resolve().parent.parent


class PublicLocationDisplayTests(unittest.TestCase):
    def test_region_plus_country(self):
        self.assertEqual(
            public_location_display("California", "US", "US"),
            "California, United States",
        )

    def test_missing_region_and_country_code_normalization(self):
        for code, expected in {
            "CN": "China",
            "US": "United States",
            "GB": "United Kingdom",
            "KR": "South Korea",
        }.items():
            with self.subTest(code=code):
                self.assertEqual(public_location_display("", code, code), expected)

    def test_empty_and_duplicate_fields_are_clean(self):
        self.assertEqual(public_location_display("", "", ""), "")
        self.assertEqual(
            public_location_display("Singapore", "Singapore", "SG"),
            "Singapore",
        )

    def test_curated_records_normalize_country_and_preserve_raw_source(self):
        record = normalize_regional_location({
            "city": "London",
            "region": "England",
            "country": "GB",
            "country_code": "GB",
        })
        self.assertEqual(record["location_display"], "England, United Kingdom")
        self.assertEqual(record["city"], "London")
        self.assertEqual(record["country"], "United Kingdom")
        self.assertEqual(record["country_code"], "GB")
        self.assertEqual(record["raw_country"], "GB")
        self.assertEqual(record["raw_country_code"], "GB")

    def test_new_imports_automatically_use_shared_display_rule(self):
        payload, _summary = build_preview(
            [{
                "id": "new-import",
                "title": "Newly imported paper",
                "task": "detection",
                "institution": "Example Institute",
                "country": "KR",
                "country_code": "KR",
                "region": "Seoul",
                "city": "Seoul",
                "latitude": 37.5,
                "longitude": 127.0,
                "resolution_confidence": "high",
                "needs_review": False,
                "in_scope": True,
            }],
            max_records=None,
            min_confidence="medium",
            include_needs_review=False,
            paper_version_overrides=(),
        )
        record = payload["records"][0]
        self.assertEqual(record["location_display"], "Seoul, South Korea")
        self.assertEqual(record["city"], "Seoul")

    def test_existing_visible_records_have_no_raw_code_display(self):
        payload = json.loads(
            (ROOT / "web/data/public_preview_map_data.json").read_text()
        )
        self.assertTrue(payload["records"])
        for record in payload["records"]:
            display = record.get("location_display", "")
            self.assertEqual(
                display,
                public_location_display(
                    record.get("region"),
                    record.get("country"),
                    record.get("country_code"),
                ),
            )
            self.assertNotRegex(display, r"(?:^|,\s*)[A-Z]{2}$")

        papers = json.loads(
            (ROOT / "web/data/public_preview_papers.json").read_text()
        )["records"]
        visible_affiliations = [
            affiliation
            for paper in papers
            for affiliation in paper.get("affiliations", [])
            if affiliation.get("country") or affiliation.get("region")
        ]
        self.assertTrue(visible_affiliations)
        for affiliation in visible_affiliations:
            self.assertEqual(
                affiliation.get("location_display"),
                public_location_display(
                    affiliation.get("region"),
                    affiliation.get("country"),
                    affiliation.get("country_code"),
                ),
            )

    def test_frontend_defensive_formatter_does_not_use_city(self):
        source = (ROOT / "web/app.js").read_text()
        body = source[
            source.index("function recordLocation(record)"):
            source.index("function recordPaperUrl(record)")
        ]
        self.assertNotIn("record.city", body)
        self.assertIn("record.location_display", body)


if __name__ == "__main__":
    unittest.main()
