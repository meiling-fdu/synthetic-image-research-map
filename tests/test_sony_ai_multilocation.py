import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_export import build_curated_map_records
from scripts.curated_mappings import (
    CuratedMappingError,
    create_mapping,
    load_mappings,
    update_mapping,
)
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)
from scripts.validate_curated_database import validate_confirmed_locations


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"
SONY_AI_ID = "institution:cf2639c8e56f6453"
TOKYO_ID = "location:cf2639c8e56f6453f311"
CALIFORNIA_ID = "location:d99adc768886c63d2401"


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path, columns, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def schema_row(columns, **values):
    return {column: values.get(column, "") for column in columns}


class SonyAiRepositoryRegressionTests(unittest.TestCase):
    def test_one_canonical_sony_ai_has_two_confirmed_locations(self):
        institutions = [
            row for row in read_rows(CURATED / "institutions.csv")
            if row["institution_id"] == SONY_AI_ID
        ]
        locations = [
            row for row in read_rows(CURATED / "institution_locations.csv")
            if row["institution_id"] == SONY_AI_ID
        ]
        self.assertEqual(len(institutions), 1)
        self.assertEqual(institutions[0]["canonical_name"], "Sony AI")
        self.assertEqual(
            {row["location_id"] for row in locations},
            {TOKYO_ID, CALIFORNIA_ID},
        )

    def test_sony_ai_papers_share_identity_and_select_mapping_locations(self):
        mappings = [
            row for row in read_rows(CURATED / "author_institution_mappings.csv")
            if row["institution_id"] == SONY_AI_ID
            and row["mapping_status"] == "active"
        ]
        by_title = {row["title"]: row for row in mappings}
        self.assertEqual(
            by_title["CO-SPY: Combining Semantic and Pixel Features to Detect Synthetic Images by AI"]["location_id"],
            CALIFORNIA_ID,
        )
        self.assertEqual(
            by_title["How to Trace Latent Generative Model Generated Images without Artificial Watermark?"]["location_id"],
            CALIFORNIA_ID,
        )
        self.assertEqual(
            by_title["Where Did I Come From? Origin Attribution of AI-Generated Images"]["location_id"],
            CALIFORNIA_ID,
        )
        self.assertEqual({row["institution_id"] for row in mappings}, {SONY_AI_ID})

    def test_legitimate_sony_locations_do_not_warn_as_duplicate_institutions(self):
        locations = [
            row for row in read_rows(CURATED / "institution_locations.csv")
            if row["institution_id"] == SONY_AI_ID
        ]
        issues = []
        validate_confirmed_locations(locations, issues)
        self.assertFalse(any(
            "duplicate normalized institution name" in issue.message
            for issue in issues
        ))


class MappingLocationLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.mappings = root / "mappings.csv"
        self.reviews = root / "reviews.csv"
        self.institutions = root / "institutions.csv"
        self.aliases = root / "aliases.csv"
        self.locations = root / "locations.csv"
        write_rows(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
        write_rows(self.reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS)
        write_rows(self.aliases, INSTITUTION_ALIAS_COLUMNS)
        write_rows(self.institutions, INSTITUTION_COLUMNS, [schema_row(
            INSTITUTION_COLUMNS,
            institution_id=SONY_AI_ID,
            canonical_name="Sony AI",
            institution_status="active",
        ), schema_row(
            INSTITUTION_COLUMNS,
            institution_id="institution:other",
            canonical_name="Other Lab",
            institution_status="active",
        )])
        write_rows(self.locations, INSTITUTION_LOCATION_COLUMNS, [
            schema_row(
                INSTITUTION_LOCATION_COLUMNS,
                location_id=TOKYO_ID,
                institution_id=SONY_AI_ID,
                institution="Sony AI",
                city="Tokyo",
                region="Tokyo",
                country="Japan",
                country_code="JP",
                lat="35.6302",
                lon="139.7408",
                coordinate_status="known",
            ),
            schema_row(
                INSTITUTION_LOCATION_COLUMNS,
                location_id=CALIFORNIA_ID,
                institution_id=SONY_AI_ID,
                institution="Sony AI",
                city="San Mateo",
                region="California",
                country="United States",
                country_code="US",
                lat="37.5595",
                lon="-122.2847",
                coordinate_status="known",
            ),
            schema_row(
                INSTITUTION_LOCATION_COLUMNS,
                location_id="location:other",
                institution_id="institution:other",
                institution="Other Lab",
                city="Paris",
                country="France",
                country_code="FR",
                lat="48.8566",
                lon="2.3522",
                coordinate_status="known",
            ),
        ])
        self.paper = {"paper_id": "paper:one", "title": "Paper One", "year": "2026"}
        self.draft = {
            "institution": "Sony AI",
            "institution_id": SONY_AI_ID,
            "location_id": TOKYO_ID,
            "institution_authors": "Ada Example",
            "raw_affiliation": "Sony AI",
            "evidence_source": "Publisher PDF",
            "mapping_status": "active",
        }

    def tearDown(self):
        self.temp.cleanup()

    def create(self, draft=None):
        return create_mapping(
            self.paper,
            draft or self.draft,
            map_records=[],
            mappings_path=self.mappings,
            location_review_path=self.reviews,
            institutions_path=self.institutions,
            institution_aliases_path=self.aliases,
            institution_locations_path=self.locations,
        )

    def test_location_only_edit_preserves_institution_mapping_and_lineage(self):
        original = self.create()["mapping"]
        updated = update_mapping(
            self.paper,
            original["mapping_id"],
            {**self.draft, "location_id": CALIFORNIA_ID},
            map_records=[],
            mappings_path=self.mappings,
            location_review_path=self.reviews,
            institutions_path=self.institutions,
            institution_aliases_path=self.aliases,
            institution_locations_path=self.locations,
        )["mapping"]
        self.assertEqual(updated["mapping_id"], original["mapping_id"])
        self.assertEqual(updated["institution_id"], SONY_AI_ID)
        self.assertEqual(updated["location_id"], CALIFORNIA_ID)
        self.assertEqual(updated["institution_city"], "San Mateo")
        self.assertEqual(updated["institution_country"], "United States")
        self.assertEqual(load_mappings(self.mappings)[0]["location_id"], CALIFORNIA_ID)

    def test_invalid_cross_institution_location_is_rejected_without_write(self):
        with self.assertRaisesRegex(
            CuratedMappingError, "belongs to a different institution"
        ):
            self.create({**self.draft, "location_id": "location:other"})
        self.assertEqual(load_mappings(self.mappings), [])

    def test_admin_form_round_trips_location_and_avoids_arbitrary_choice(self):
        html = (ROOT / "web" / "admin.html").read_text(encoding="utf-8")
        javascript = (ROOT / "web" / "admin.js").read_text(encoding="utf-8")
        self.assertIn('id="mapping-location-id"', html)
        self.assertIn("renderMappingLocationOptions(text(mapping.location_id))", javascript)
        self.assertIn('location_id: elements["mapping-location-id"].value', javascript)
        self.assertIn("else if (locations.length === 1)", javascript)
        self.assertIn("Multiple confirmed locations exist", javascript)


class MappingLocationExportTests(unittest.TestCase):
    def setUp(self):
        self.paper = {
            "paper_id": "paper:one",
            "title": "Paper",
            "year": "2026",
            "publication_year": "2026",
            "task": "detection",
            "in_scope": True,
            "authors": "Ada Example",
        }
        self.locations = [
            {"location_id": TOKYO_ID, "institution_id": SONY_AI_ID, "institution": "Sony AI", "city": "Tokyo", "country": "Japan", "country_code": "JP", "lat": "35.6302", "lon": "139.7408"},
            {"location_id": CALIFORNIA_ID, "institution_id": SONY_AI_ID, "institution": "Sony AI", "city": "San Mateo", "country": "United States", "country_code": "US", "lat": "37.5595", "lon": "-122.2847"},
        ]
        self.mapping = {
            "mapping_id": "mapping:one",
            "paper_id": "paper:one",
            "institution": "Sony AI",
            "institution_id": SONY_AI_ID,
            "institution_authors": "Ada Example",
            "mapping_status": "active",
        }

    def test_public_export_uses_mapping_specific_location(self):
        markers, _ = build_curated_map_records(
            [self.paper],
            [{**self.mapping, "location_id": CALIFORNIA_ID}],
            [],
            confirmed_location_records=self.locations,
        )
        self.assertEqual(len(markers), 1)
        self.assertEqual(markers[0]["location_id"], CALIFORNIA_ID)
        self.assertEqual(markers[0]["city"], "San Mateo")

    def test_explicit_unknown_location_does_not_fall_back_to_another_office(self):
        markers, report = build_curated_map_records(
            [self.paper],
            [{**self.mapping, "location_id": "location:missing"}],
            [],
            confirmed_location_records=self.locations,
        )
        self.assertEqual(markers, [])
        self.assertEqual(report["curated_mappings_missing_coordinates"], 1)

    def test_no_location_is_ambiguous_when_multiple_offices_exist(self):
        markers, report = build_curated_map_records(
            [self.paper],
            [self.mapping],
            [],
            confirmed_location_records=self.locations,
        )
        self.assertEqual(markers, [])
        self.assertEqual(report["curated_mappings_ambiguous_coordinates"], 1)


if __name__ == "__main__":
    unittest.main()
