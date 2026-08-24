import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.audit_institution_identities import audit_and_consolidate
from scripts.curated_institutions import institution_match_key
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_AUDIT_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_HIERARCHY_COLUMNS,
    INSTITUTION_LOCATION_AUDIT_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
    INSTITUTION_REVIEW_QUEUE_COLUMNS,
    INSTITUTION_SEARCH_RELATIONSHIP_COLUMNS,
)


def record(columns, **values):
    return {column: values.get(column, "") for column in columns}


def write_csv(path, columns, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class InstitutionIdentityResolutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.paths = {name: root / f"{name}.csv" for name in (
            "institutions", "mappings", "aliases", "locations", "location_reviews",
            "location_audits", "hierarchy", "search_relationships", "review_queue", "audit",
        )}
        schemas = {
            "institutions": INSTITUTION_COLUMNS, "mappings": AUTHOR_INSTITUTION_MAPPING_COLUMNS,
            "aliases": INSTITUTION_ALIAS_COLUMNS, "locations": INSTITUTION_LOCATION_COLUMNS,
            "location_reviews": INSTITUTION_LOCATION_REVIEW_COLUMNS,
            "location_audits": INSTITUTION_LOCATION_AUDIT_COLUMNS,
            "hierarchy": INSTITUTION_HIERARCHY_COLUMNS,
            "search_relationships": INSTITUTION_SEARCH_RELATIONSHIP_COLUMNS,
            "review_queue": INSTITUTION_REVIEW_QUEUE_COLUMNS, "audit": INSTITUTION_AUDIT_COLUMNS,
        }
        for name, columns in schemas.items():
            write_csv(self.paths[name], columns)
        self.report = root / "report.csv"
        self.doc = root / "report.md"

    def tearDown(self):
        self.temp.cleanup()

    def run_audit(self):
        return audit_and_consolidate(
            write=True, paths=self.paths, report_path=self.report, doc_path=self.doc
        )

    def test_common_abbreviation_punctuation_and_spacing_normalize_exactly(self):
        self.assertEqual(institution_match_key(" A*STAR "), institution_match_key("a star"))
        self.assertEqual(institution_match_key("A.STAR"), institution_match_key("ASTAR"))

    def test_astar_duplicates_mappings_locations_aliases_and_pending_review_consolidate(self):
        short_id, duplicate_id, survivor_id = "institution:short", "institution:duplicate", "institution:survivor"
        full = "Agency for Science, Technology and Research"
        write_csv(self.paths["institutions"], INSTITUTION_COLUMNS, [
            record(INSTITUTION_COLUMNS, institution_id=short_id, canonical_name="A*STAR", institution_type="research_unit", institution_status="active"),
            record(INSTITUTION_COLUMNS, institution_id=duplicate_id, canonical_name=full, institution_type="research_unit", institution_status="active"),
            record(INSTITUTION_COLUMNS, institution_id=survivor_id, canonical_name=full, abbreviation="A*STAR", institution_type="research_unit", institution_status="active", public_display="self"),
        ])
        write_csv(self.paths["mappings"], AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            record(AUTHOR_INSTITUTION_MAPPING_COLUMNS, mapping_id="mapping:1", paper_id="paper:1", institution="A*STAR", institution_id=short_id, institution_authors="Ada", mapping_status="active"),
            record(AUTHOR_INSTITUTION_MAPPING_COLUMNS, mapping_id="mapping:2", paper_id="paper:2", institution=full, institution_id=duplicate_id, institution_authors="Grace", mapping_status="active"),
        ])
        write_csv(self.paths["locations"], INSTITUTION_LOCATION_COLUMNS, [
            record(INSTITUTION_LOCATION_COLUMNS, location_id="location:one", institution_id=survivor_id, institution=full, normalized_institution="agency for science technology and research", city="Singapore", region="Singapore", country="Singapore", country_code="SG", lat="1.2996", lon="103.7886", coordinate_status="known"),
            record(INSTITUTION_LOCATION_COLUMNS, location_id="location:duplicate", institution_id=survivor_id, institution=f"{full} (A*STAR)", normalized_institution="agency for science technology and research a star", city="Singapore", region="Singapore", country="Singapore", country_code="SG", lat="1.2996", lon="103.7886", coordinate_status="known"),
        ])
        write_csv(self.paths["aliases"], INSTITUTION_ALIAS_COLUMNS, [
            record(INSTITUTION_ALIAS_COLUMNS, alias_id="alias:full", alias_name=full, institution_id=survivor_id, canonical_institution_name=full, review_status="confirmed"),
            record(INSTITUTION_ALIAS_COLUMNS, alias_id="alias:display", alias_name=f"{full} (A*STAR)", institution_id=survivor_id, canonical_institution_name=full, review_status="confirmed"),
        ])
        write_csv(self.paths["location_reviews"], INSTITUTION_LOCATION_REVIEW_COLUMNS, [
            record(INSTITUTION_LOCATION_REVIEW_COLUMNS, institution="A*STAR", canonical_institution_name="A*STAR", institution_id=short_id, related_paper_id="paper:1", review_status="pending_review", location_status="known", coordinate_status="known"),
        ])
        write_csv(self.paths["hierarchy"], INSTITUTION_HIERARCHY_COLUMNS, [
            record(INSTITUTION_HIERARCHY_COLUMNS, parent_institution_id=short_id, child_institution_id="institution:child", relationship_type="affiliated_institute", review_status="confirmed"),
        ])
        write_csv(self.paths["search_relationships"], INSTITUTION_SEARCH_RELATIONSHIP_COLUMNS, [
            record(INSTITUTION_SEARCH_RELATIONSHIP_COLUMNS, root_institution_id=duplicate_id, related_institution_id="institution:related", relationship_type="search_result", review_status="confirmed"),
        ])
        write_csv(self.paths["review_queue"], INSTITUTION_REVIEW_QUEUE_COLUMNS, [
            record(INSTITUTION_REVIEW_QUEUE_COLUMNS, issue_type="duplicate_institution", current_institution_id=duplicate_id, suggested_institution_id=survivor_id, finding_status="open", is_current="true"),
        ])

        result = self.run_audit()

        institutions = read_csv(self.paths["institutions"])
        active = [row for row in institutions if row["institution_status"] == "active"]
        self.assertEqual([(row["institution_id"], row["canonical_name"], row["abbreviation"]) for row in active], [(survivor_id, full, "A*STAR")])
        self.assertEqual({row["institution_id"] for row in read_csv(self.paths["mappings"])}, {survivor_id})
        self.assertEqual({row["institution"] for row in read_csv(self.paths["mappings"])}, {full})
        self.assertEqual(len(read_csv(self.paths["locations"])), 1)
        review = read_csv(self.paths["location_reviews"])[0]
        self.assertEqual((review["institution_id"], review["review_status"], review["match_method"]), (survivor_id, "confirmed", "exact_abbreviation"))
        aliases = read_csv(self.paths["aliases"])
        self.assertIn("A*STAR", {row["alias_name"] for row in aliases})
        self.assertNotIn(full, {row["alias_name"] for row in aliases})
        self.assertEqual(read_csv(self.paths["hierarchy"])[0]["parent_institution_id"], survivor_id)
        self.assertEqual(read_csv(self.paths["search_relationships"])[0]["root_institution_id"], survivor_id)
        self.assertEqual(read_csv(self.paths["review_queue"])[0]["finding_status"], "archived")
        self.assertEqual(sum(row["action"] == "duplicate_merged" for row in result["rows"]), 2)
        self.assertEqual(sum(row["action"] == "pending_review_resolved" for row in result["rows"]), 1)

    def test_ambiguous_exact_alias_match_is_marked_ambiguous_without_merge(self):
        write_csv(self.paths["institutions"], INSTITUTION_COLUMNS, [
            record(INSTITUTION_COLUMNS, institution_id="institution:one", canonical_name="One Research Agency", abbreviation="ORA", institution_status="active"),
            record(INSTITUTION_COLUMNS, institution_id="institution:two", canonical_name="Other Research Agency", abbreviation="ORA", institution_status="active"),
        ])
        write_csv(self.paths["location_reviews"], INSTITUTION_LOCATION_REVIEW_COLUMNS, [
            record(INSTITUTION_LOCATION_REVIEW_COLUMNS, institution="O.R.A.", institution_id="institution:stale", review_status="pending_review", location_status="missing", coordinate_status="missing"),
        ])

        result = self.run_audit()

        self.assertEqual(len([row for row in read_csv(self.paths["institutions"]) if row["institution_status"] == "active"]), 2)
        review = read_csv(self.paths["location_reviews"])[0]
        self.assertEqual(review["review_status"], "ambiguous")
        self.assertEqual(review["institution_id"], "institution:stale")
        self.assertTrue(any(row["action"] == "ambiguous_pending_review" for row in result["rows"]))

    def test_exact_duplicate_names_in_different_countries_are_left_ambiguous(self):
        write_csv(self.paths["institutions"], INSTITUTION_COLUMNS, [
            record(INSTITUTION_COLUMNS, institution_id="institution:us", canonical_name="Northeastern University", institution_status="active"),
            record(INSTITUTION_COLUMNS, institution_id="institution:cn", canonical_name="Northeastern University", institution_status="active"),
        ])
        write_csv(self.paths["locations"], INSTITUTION_LOCATION_COLUMNS, [
            record(INSTITUTION_LOCATION_COLUMNS, location_id="location:us", institution_id="institution:us", institution="Northeastern University", country="United States", country_code="US", lat="42.3", lon="-71.0", coordinate_status="known"),
            record(INSTITUTION_LOCATION_COLUMNS, location_id="location:cn", institution_id="institution:cn", institution="Northeastern University", country="China", country_code="CN", lat="41.7", lon="123.4", coordinate_status="known"),
        ])

        result = self.run_audit()

        self.assertEqual({row["institution_status"] for row in read_csv(self.paths["institutions"])}, {"active"})
        finding = next(row for row in result["rows"] if row["action"] == "ambiguous_exact_match")
        self.assertIn("different countries", finding["details"])

    def test_peng_cheng_exact_identity_with_multiple_locations_needs_coordinates_idempotently(self):
        identifier = "institution:peng-cheng"
        write_csv(self.paths["institutions"], INSTITUTION_COLUMNS, [
            record(INSTITUTION_COLUMNS, institution_id=identifier, canonical_name="Peng Cheng Laboratory", institution_status="active"),
        ])
        write_csv(self.paths["locations"], INSTITUTION_LOCATION_COLUMNS, [
            record(INSTITUTION_LOCATION_COLUMNS, location_id="location:one", institution_id=identifier, institution="Peng Cheng Laboratory", country="China", country_code="CN", lat="22.62", lon="113.92", coordinate_status="known"),
            record(INSTITUTION_LOCATION_COLUMNS, location_id="location:two", institution_id=identifier, institution="Peng Cheng Laboratory", country="China", country_code="CN", lat="22.58", lon="113.96", coordinate_status="known"),
        ])
        write_csv(self.paths["mappings"], AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            record(AUTHOR_INSTITUTION_MAPPING_COLUMNS, mapping_id="mapping:peng", paper_id="paper:peng", institution="Peng Cheng Laboratory", institution_id=identifier, institution_authors="Ada", mapping_status="active"),
        ])
        write_csv(self.paths["location_reviews"], INSTITUTION_LOCATION_REVIEW_COLUMNS, [
            record(INSTITUTION_LOCATION_REVIEW_COLUMNS, institution="Pengcheng Laboratory", canonical_institution_name="Peng Cheng Laboratory", institution_id=identifier, related_paper_id="paper:peng", review_status="ambiguous", location_status="needs_coordinate_review", coordinate_status="ambiguous"),
        ])

        result = self.run_audit()
        review = read_csv(self.paths["location_reviews"])[0]
        self.assertEqual(review["institution_id"], identifier)
        self.assertEqual(review["review_status"], "pending_review")
        self.assertEqual(review["location_status"], "needs_coordinate_review")
        self.assertEqual(review["coordinate_status"], "missing")
        self.assertEqual(read_csv(self.paths["mappings"])[0]["location_id"], "")
        self.assertTrue(any(row["action"] == "identity_resolved_needs_coordinates" for row in result["rows"]))

        first = {path: path.read_bytes() for path in (*self.paths.values(), self.report, self.doc)}
        self.run_audit()
        self.assertEqual(
            {path: path.read_bytes() for path in first}, first,
        )

    def test_exact_identity_reuses_one_confirmed_canonical_location(self):
        identifier = "institution:known"
        write_csv(self.paths["institutions"], INSTITUTION_COLUMNS, [
            record(INSTITUTION_COLUMNS, institution_id=identifier, canonical_name="Known Laboratory", institution_status="active"),
        ])
        write_csv(self.paths["locations"], INSTITUTION_LOCATION_COLUMNS, [
            record(INSTITUTION_LOCATION_COLUMNS, location_id="location:known", institution_id=identifier, institution="Known Laboratory", country="Italy", country_code="IT", lat="41.9", lon="12.5", coordinate_status="known"),
        ])
        write_csv(self.paths["location_reviews"], INSTITUTION_LOCATION_REVIEW_COLUMNS, [
            record(INSTITUTION_LOCATION_REVIEW_COLUMNS, institution="Known Laboratory", institution_id=identifier, review_status="ambiguous", location_status="ambiguous", coordinate_status="ambiguous"),
        ])

        self.run_audit()

        review = read_csv(self.paths["location_reviews"])[0]
        self.assertEqual(review["review_status"], "confirmed")
        self.assertEqual(review["location_status"], "known")
        self.assertEqual(review["coordinate_status"], "known")

    def test_batch_failure_restores_every_curated_file(self):
        write_csv(self.paths["institutions"], INSTITUTION_COLUMNS, [
            record(INSTITUTION_COLUMNS, institution_id="institution:one", canonical_name="Same Institute", institution_status="active"),
            record(INSTITUTION_COLUMNS, institution_id="institution:two", canonical_name="Same Institute", institution_status="active"),
        ])
        before = {path: path.read_bytes() for path in self.paths.values()}
        with patch("scripts.audit_institution_identities.merge_institutions", side_effect=RuntimeError("write failed")):
            with self.assertRaisesRegex(RuntimeError, "write failed"):
                self.run_audit()
        self.assertEqual({path: path.read_bytes() for path in self.paths.values()}, before)


if __name__ == "__main__":
    unittest.main()
