import csv
import tempfile
import unittest
from pathlib import Path

from scripts.country_normalization import canonical_english_location_fields
from scripts.curated_schema import INSTITUTION_LOCATION_COLUMNS
from scripts.migrate_institution_location_english import migrate


def write_locations(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INSTITUTION_LOCATION_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


class InstitutionLocationEnglishNormalizationTests(unittest.TestCase):
    def test_known_localized_forms_normalize_before_future_persistence(self):
        self.assertEqual(
            canonical_english_location_fields({
                "city": "Montréal", "region": "Québec",
                "country": "Türkiye", "country_code": "TR",
            }),
            {
                "city": "Montreal", "region": "Quebec",
                "country": "Turkey", "country_code": "TR",
            },
        )
        self.assertEqual(
            canonical_english_location_fields({"country": "中国", "country_code": "CN"})["country"],
            "China",
        )

    def test_migration_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "locations.csv"
            audit = Path(directory) / "audit.csv"
            row = {column: "" for column in INSTITUTION_LOCATION_COLUMNS}
            row.update({
                "location_id": "location:1", "institution_id": "institution:1",
                "institution": "Fixture University", "city": "Montréal",
                "region": "Québec", "country": "Türkiye", "country_code": "TR",
            })
            write_locations(path, [row])
            self.assertEqual(migrate(path, audit_path=audit), 3)
            first = path.read_bytes()
            self.assertEqual(migrate(path, audit_path=audit), 0)
            self.assertEqual(path.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
