import csv
import unittest
from pathlib import Path

from scripts.curated_export import build_curated_map_records
from scripts.validate_curated_database import validate_confirmed_locations


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"
INSTITUTION_ID = "institution:d1012c88e7ee61fd"
DOI = "10.1145/3690624.3709392"


def rows(filename):
    with (CURATED / filename).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class XiaohongshuMultiLocationTests(unittest.TestCase):
    def test_one_canonical_institution_retains_both_confirmed_locations(self):
        institutions = [
            row for row in rows("institutions.csv")
            if row["institution_id"] == INSTITUTION_ID
        ]
        self.assertEqual(len(institutions), 1)
        self.assertEqual(institutions[0]["canonical_name"], "Xiaohongshu Inc.")

        locations = [
            row for row in rows("institution_locations.csv")
            if row["institution_id"] == INSTITUTION_ID
        ]
        self.assertEqual(
            {(row["city"], row["region"], row["country"]) for row in locations},
            {("Shanghai", "Shanghai", "China"), ("Beijing", "Beijing", "China")},
        )
        self.assertEqual(len({row["location_id"] for row in locations}), 2)

    def test_paper_specific_mappings_select_beijing_and_preserve_shanghai(self):
        mappings = [
            row for row in rows("author_institution_mappings.csv")
            if row["institution_id"] == INSTITUTION_ID
        ]
        beijing = next(row for row in mappings if row["doi"] == DOI)
        self.assertEqual(
            beijing["institution_authors"],
            "Jiayin Cai; Xiaolong Jiang; Yao Hu",
        )
        self.assertEqual(
            (beijing["institution_city"], beijing["institution_country"]),
            ("Beijing", "China"),
        )
        shanghai = next(
            row for row in mappings
            if row["doi"] == "10.48550/arxiv.2406.19435"
        )
        self.assertEqual(
            (shanghai["institution_city"], shanghai["institution_country"]),
            ("Shanghai", "China"),
        )
        self.assertTrue(all(row["institution"] == "Xiaohongshu Inc." for row in mappings))

    def test_previous_capitalization_is_a_confirmed_alias(self):
        aliases = [
            row for row in rows("institution_aliases.csv")
            if row["institution_id"] == INSTITUTION_ID
        ]
        self.assertTrue(any(
            row["alias_name"] == "xiaohongshu Inc."
            and row["canonical_institution_name"] == "Xiaohongshu Inc."
            and row["review_status"] == "confirmed"
            for row in aliases
        ))

    def test_exporter_uses_mapping_specific_city_for_one_canonical_id(self):
        paper = {
            "paper_id": "paper:one", "title": "Paper", "year": "2026",
            "publication_year": "2026", "task": "detection", "in_scope": True,
            "authors": "Shanghai Author; Beijing Author",
        }
        mappings = [
            {
                "mapping_id": "mapping:shanghai", "paper_id": "paper:one",
                "institution": "Xiaohongshu Inc.", "institution_id": INSTITUTION_ID,
                "institution_authors": "Shanghai Author", "institution_city": "Shanghai",
                "institution_country": "China", "mapping_status": "active",
            },
            {
                "mapping_id": "mapping:beijing", "paper_id": "paper:one",
                "institution": "Xiaohongshu Inc.", "institution_id": INSTITUTION_ID,
                "institution_authors": "Beijing Author", "institution_city": "Beijing",
                "institution_country": "China", "mapping_status": "active",
            },
        ]
        locations = [
            {
                "location_id": "location:shanghai", "institution_id": INSTITUTION_ID,
                "institution": "Xiaohongshu Inc.", "city": "Shanghai", "region": "Shanghai",
                "country": "China", "country_code": "CN", "lat": "31.2199", "lon": "121.4747",
            },
            {
                "location_id": "location:beijing", "institution_id": INSTITUTION_ID,
                "institution": "Xiaohongshu Inc.", "city": "Beijing", "region": "Beijing",
                "country": "China", "country_code": "CN", "lat": "39.978168", "lon": "116.406507",
            },
        ]
        markers, _report = build_curated_map_records(
            [paper], mappings, [], confirmed_location_records=locations,
        )
        self.assertEqual(
            {(marker["mapping_id"], marker["city"]) for marker in markers},
            {("mapping:shanghai", "Shanghai"), ("mapping:beijing", "Beijing")},
        )

    def test_multiple_locations_for_one_id_are_not_a_duplicate_institution_warning(self):
        locations = [
            row for row in rows("institution_locations.csv")
            if row["institution_id"] == INSTITUTION_ID
        ]
        issues = []
        validate_confirmed_locations(locations, issues)
        self.assertFalse(any(
            "duplicate normalized institution name" in issue.message
            for issue in issues
        ))


if __name__ == "__main__":
    unittest.main()
