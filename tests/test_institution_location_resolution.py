import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_locations import (
    CuratedLocationError,
    consolidate_exact_confirmed_locations,
    create_or_update_confirmed_location,
    location_id_redirects,
    location_review_payload,
    queue_row_id,
    resolve_location_id,
)
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_AUDIT_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data/curated"
PENG_ID = "institution:aee00ab2f1fd8132"
PENG_CURRENT_LOCATION = "location:aee00ab2f1fd813231e8"


def row(columns, **values):
    return {column: values.get(column, "") for column in columns}


def write_rows(path, columns, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class ExactLocationConsolidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.locations = root / "locations.csv"
        self.mappings = root / "mappings.csv"
        self.audits = root / "audits.csv"
        write_rows(self.audits, INSTITUTION_AUDIT_COLUMNS)

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_duplicate_reassigns_references_and_retains_distinct_office(self):
        write_rows(self.locations, INSTITUTION_LOCATION_COLUMNS, [
            row(INSTITUTION_LOCATION_COLUMNS, location_id="location:unused", institution_id="institution:one", institution="Example Lab", city="Rome", region="Lazio", country="Italy", country_code="IT", lat="41.9", lon="12.5", coordinate_status="known", created_at="2025-01-01T00:00:00Z"),
            row(INSTITUTION_LOCATION_COLUMNS, location_id="location:used", institution_id="institution:one", institution="Example Lab", city=" Rome ", region="LAZIO", country="Italia", country_code="IT", lat="41.900000000", lon="12.5000000", coordinate_status="known", created_at="2026-01-01T00:00:00Z"),
            row(INSTITUTION_LOCATION_COLUMNS, location_id="location:milan", institution_id="institution:one", institution="Example Lab", city="Milan", region="Lombardy", country="Italy", country_code="IT", lat="45.46", lon="9.19", coordinate_status="known"),
        ])
        write_rows(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            row(AUTHOR_INSTITUTION_MAPPING_COLUMNS, mapping_id="mapping:one", paper_id="paper:one", institution="Example Lab", institution_id="institution:one", location_id="location:used", mapping_status="active"),
        ])

        result = consolidate_exact_confirmed_locations(
            locations_path=self.locations, mappings_path=self.mappings,
            institution_audit_path=self.audits, write=True,
        )

        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual({item["location_id"] for item in read_rows(self.locations)}, {"location:used", "location:milan"})
        self.assertEqual(read_rows(self.mappings)[0]["location_id"], "location:used")
        redirects = location_id_redirects(self.audits)
        self.assertEqual(resolve_location_id("location:unused", redirects), "location:used")
        self.assertEqual(read_rows(self.audits)[0]["action"], "location_merge")

        before = {path: path.read_bytes() for path in (self.locations, self.mappings, self.audits)}
        consolidate_exact_confirmed_locations(
            locations_path=self.locations, mappings_path=self.mappings,
            institution_audit_path=self.audits, write=True,
        )
        self.assertEqual(before, {path: path.read_bytes() for path in before})


class LocationConfirmationAmbiguityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.paths = {name: root / f"{name}.csv" for name in ("locations", "mappings", "audits", "reviews", "institutions", "aliases")}
        write_rows(self.paths["locations"], INSTITUTION_LOCATION_COLUMNS, [
            row(INSTITUTION_LOCATION_COLUMNS, location_id="location:north", institution_id="institution:lab", institution="Example Lab", city="Shenzhen", region="Guangdong", country="China", country_code="CN", lat="22.62", lon="113.92", coordinate_status="known"),
            row(INSTITUTION_LOCATION_COLUMNS, location_id="location:south", institution_id="institution:lab", institution="Example Lab", city="Shenzhen", region="Guangdong", country="China", country_code="CN", lat="22.57", lon="113.96", coordinate_status="known"),
        ])
        write_rows(self.paths["mappings"], AUTHOR_INSTITUTION_MAPPING_COLUMNS)
        write_rows(self.paths["audits"], INSTITUTION_AUDIT_COLUMNS)
        write_rows(self.paths["institutions"], INSTITUTION_COLUMNS, [
            row(INSTITUTION_COLUMNS, institution_id="institution:lab", canonical_name="Example Lab", institution_status="active"),
        ])
        write_rows(self.paths["aliases"], INSTITUTION_ALIAS_COLUMNS)
        self.review = row(INSTITUTION_LOCATION_REVIEW_COLUMNS, institution="Example Lab", canonical_institution_name="Example Lab", institution_id="institution:lab", related_paper_id="paper:one", review_status="pending_review", location_status="needs_coordinate_review", coordinate_status="missing")
        write_rows(self.paths["reviews"], INSTITUTION_LOCATION_REVIEW_COLUMNS, [self.review])

    def tearDown(self):
        self.temp.cleanup()

    def confirm(self, draft):
        return create_or_update_confirmed_location(
            queue_row_id(self.review), draft,
            locations_path=self.paths["locations"], review_path=self.paths["reviews"],
            institutions_path=self.paths["institutions"], mappings_path=self.paths["mappings"],
            aliases_path=self.paths["aliases"], institution_audit_path=self.paths["audits"],
        )

    def test_true_multilocation_requires_selection_and_candidates_are_distinguishable(self):
        payload = location_review_payload(
            review_path=self.paths["reviews"], locations_path=self.paths["locations"],
            aliases_path=self.paths["aliases"], institutions_path=self.paths["institutions"],
        )
        candidate = payload["records"][0]
        self.assertEqual(len(candidate["confirmed_locations"]), 2)
        self.assertEqual({item["city"] for item in candidate["confirmed_locations"]}, {"Shenzhen"})
        self.assertEqual(len({(item["lat"], item["lon"]) for item in candidate["confirmed_locations"]}), 2)
        with self.assertRaisesRegex(CuratedLocationError, "select a location candidate"):
            self.confirm({"institution_id": "institution:lab", "confirmed_city": "Shenzhen", "confirmed_region": "Guangdong", "confirmed_country": "China", "confirmed_country_code": "CN", "confirmed_lat": "22.60", "confirmed_lon": "113.94"})

        result = self.confirm({"institution_id": "institution:lab", "location_id": "location:north", "confirmed_city": "Shenzhen", "confirmed_region": "Guangdong", "confirmed_country": "China", "confirmed_country_code": "CN", "confirmed_lat": "22.62", "confirmed_lon": "113.92"})
        self.assertEqual(result["location"]["location_id"], "location:north")
        self.assertEqual(read_rows(self.paths["reviews"])[0]["review_status"], "confirmed")


class PengChengRepositoryRegressionTests(unittest.TestCase):
    def test_reviews_reuse_current_confirmed_location_without_new_records(self):
        locations = [item for item in read_rows(CURATED / "institution_locations.csv") if item["institution_id"] == PENG_ID]
        mappings = [item for item in read_rows(CURATED / "author_institution_mappings.csv") if item["institution_id"] == PENG_ID]
        reviews = [item for item in read_rows(CURATED / "institution_location_review.csv") if item["institution_id"] == PENG_ID and item["related_paper_id"] in {"curated:7693a9c0107feaf90e10", "curated:64635535d7b7b6a12a32"}]
        self.assertEqual(len(locations), 3)
        self.assertEqual(len({item["location_id"] for item in locations}), 3)
        self.assertTrue(all(item["review_status"] == "confirmed" and item["location_status"] == "known" for item in reviews))
        by_paper = {item["paper_id"]: item for item in mappings}
        for paper_id in ("curated:7693a9c0107feaf90e10", "curated:64635535d7b7b6a12a32"):
            self.assertEqual(by_paper[paper_id]["location_id"], PENG_CURRENT_LOCATION)


if __name__ == "__main__":
    unittest.main()
