import csv
import unittest
from pathlib import Path

from scripts.export_public_preview import (
    canonicalize_public_institutions,
    public_institution_aliases,
    public_institution_hierarchy,
)


REPOSITORY = Path(__file__).resolve().parents[1]
PARENT_NAME = "Chinese Academy of Sciences"
PARENT_ID = "institution:3afb6cc453e0a8d9"
CHILD_NAME = "Institute of Information Engineering, Chinese Academy of Sciences"
CHILD_ID = "institution:cee70184073782c7"


class InstitutionHierarchyTests(unittest.TestCase):
    def read_csv(self, relative_path):
        with (REPOSITORY / relative_path).open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def test_cas_parent_is_not_an_alias_of_information_engineering(self):
        aliases = self.read_csv("data/curated/institution_aliases.csv")
        self.assertFalse(any(
            row["alias_name"] == PARENT_NAME
            and row["canonical_institution_name"] == CHILD_NAME
            for row in aliases
        ))
        exported = public_institution_aliases(aliases)
        self.assertFalse(any(row["alias_name"] == PARENT_NAME for row in exported))

    def test_explicit_institute_review_stays_with_the_child(self):
        reviews = self.read_csv("data/curated/institution_location_review.csv")
        row = next(
            row for row in reviews
            if row["doi"] == "10.1109/iccvw69036.2025.00165"
            and CHILD_NAME in row["raw_affiliation"]
        )
        self.assertEqual(row["institution"], CHILD_NAME)
        self.assertEqual(row["canonical_institution_name"], CHILD_NAME)
        self.assertIn(CHILD_NAME, row["raw_affiliation"])

    def test_only_confirmed_hierarchy_rows_are_exported(self):
        locations = [
            {"institution": PARENT_NAME},
            {"institution": CHILD_NAME},
        ]
        relationships = [
            {
                "parent_institution_id": PARENT_ID,
                "child_institution_id": CHILD_ID,
                "relationship_type": "affiliated_institute",
                "review_status": "confirmed",
            },
            {
                "parent_institution_id": CHILD_ID,
                "child_institution_id": PARENT_ID,
                "relationship_type": "affiliated_institute",
                "review_status": "pending_review",
            },
        ]
        exported = public_institution_hierarchy(relationships, locations)
        self.assertEqual(len(exported), 1)
        self.assertEqual(exported[0]["parent_institution_id"], PARENT_ID)
        self.assertEqual(exported[0]["child_institution_id"], CHILD_ID)
        self.assertEqual(exported[0]["parent_institution_name"], PARENT_NAME)
        self.assertEqual(exported[0]["child_institution_name"], CHILD_NAME)

    def test_old_public_consolidation_is_reversed_from_provenance(self):
        maps = [{
            "title": "Parent paper",
            "doi": "10.1/parent",
            "institution": CHILD_NAME,
            "institution_id": CHILD_ID,
            "source_institution": PARENT_NAME,
            "source_institution_id": PARENT_ID,
        }, {
            "title": "Child paper",
            "doi": "10.1/child",
            "institution": CHILD_NAME,
            "institution_id": CHILD_ID,
        }]
        papers = [{
            "title": "Parent paper",
            "doi": "10.1/parent",
            "author_institution_affiliations": [{
                "institution": CHILD_NAME,
                "institution_id": CHILD_ID,
                "source_institution": PARENT_NAME,
            }],
        }]
        locations = [
            {"institution": PARENT_NAME},
            {"institution": CHILD_NAME},
        ]
        canonicalized = canonicalize_public_institutions(
            papers, maps, [], locations,
        )
        self.assertEqual(len(canonicalized), 2)
        self.assertEqual(canonicalized[0]["institution"], PARENT_NAME)
        self.assertEqual(canonicalized[0]["institution_id"], PARENT_ID)
        self.assertEqual(canonicalized[1]["institution"], CHILD_NAME)
        self.assertEqual(canonicalized[1]["institution_id"], CHILD_ID)
        affiliation = papers[0]["author_institution_affiliations"][0]
        self.assertEqual(affiliation["institution"], PARENT_NAME)
        self.assertEqual(affiliation["source_institution"], PARENT_NAME)

    def test_stale_alias_shadow_collapses_to_one_full_affiliation(self):
        paper = {
            "title": "One full affiliation",
            "doi": "10.1/full",
            "affiliations": [{
                "index": 1,
                "name": PARENT_NAME,
                "institution_id": PARENT_ID,
                "source_institution_names": [PARENT_NAME, CHILD_NAME],
            }, {
                "index": 2,
                "name": CHILD_NAME,
                "institution_id": CHILD_ID,
            }],
            "author_institution_affiliations": [{
                "index": 1,
                "institution": PARENT_NAME,
                "institution_id": PARENT_ID,
                "authors": ["Example Author"],
                "source_institution_names": [PARENT_NAME, CHILD_NAME],
            }, {
                "index": 2,
                "institution": CHILD_NAME,
                "institution_id": CHILD_ID,
                "authors": ["Example Author"],
            }],
            "authors": [{
                "name": "Example Author",
                "affiliation_indices": [1],
            }],
        }
        canonicalize_public_institutions(
            [paper], [], [], [
                {"institution": PARENT_NAME},
                {"institution": CHILD_NAME},
            ],
        )
        self.assertEqual(len(paper["affiliations"]), 1)
        self.assertEqual(paper["affiliations"][0]["name"], CHILD_NAME)
        self.assertEqual(paper["affiliations"][0]["index"], 1)
        self.assertEqual(len(paper["author_institution_affiliations"]), 1)
        self.assertEqual(
            paper["author_institution_affiliations"][0]["institution"],
            CHILD_NAME,
        )
        self.assertEqual(
            paper["authors"][0]["affiliation_indices"], [1]
        )
        self.assertIn(
            PARENT_NAME,
            paper["affiliations"][0]["source_institution_names"],
        )

    def test_curated_hierarchy_keeps_parent_and_child_ids_distinct(self):
        relationships = self.read_csv("data/curated/institution_hierarchy.csv")
        cas_children = {
            row["child_institution_id"]
            for row in relationships
            if row["parent_institution_id"] == PARENT_ID
            and row["review_status"] == "confirmed"
        }
        self.assertIn(CHILD_ID, cas_children)
        self.assertNotIn(PARENT_ID, cas_children)

    def test_public_preview_keeps_parent_and_child_records_separate(self):
        import json

        map_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_map_data.json").read_text()
        )
        paper_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )
        for payload in (map_payload, paper_payload):
            self.assertTrue(any(
                row["parent_institution_id"] == PARENT_ID
                and row["child_institution_id"] == CHILD_ID
                for row in payload["institution_hierarchy"]
            ))
            self.assertFalse(any(
                row["alias_name"] == PARENT_NAME
                and row["canonical_institution_id"] == CHILD_ID
                for row in payload["institution_aliases"]
            ))

        parent_records = [
            row for row in map_payload["records"]
            if row.get("institution_id") == PARENT_ID
        ]
        child_records = [
            row for row in map_payload["records"]
            if row.get("institution_id") == CHILD_ID
        ]
        self.assertGreater(len(parent_records), 0)
        self.assertGreater(len(child_records), 0)
        self.assertEqual(
            {row["institution"] for row in parent_records}, {PARENT_NAME}
        )
        self.assertEqual(
            {row["institution"] for row in child_records}, {CHILD_NAME}
        )
        parent_pairs = {
            (row.get("doi") or row.get("title"), row["institution_id"])
            for row in parent_records
        }
        child_pairs = {
            (row.get("doi") or row.get("title"), row["institution_id"])
            for row in child_records
        }
        self.assertEqual(len(parent_pairs), len(parent_records))
        self.assertEqual(len(child_pairs), len(child_records))

    def test_public_affiliations_keep_full_cas_institute_without_parent_split(self):
        import json

        payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )
        full_name = (
            "Institute of Computing Technology, Chinese Academy of Sciences"
        )
        matching_papers = []
        for paper in payload["records"]:
            affiliations = paper.get("author_institution_affiliations") or []
            if any(row.get("institution") == full_name for row in affiliations):
                matching_papers.append(paper)
                self.assertFalse(any(
                    row.get("institution") == PARENT_NAME
                    for row in affiliations
                ))
                self.assertEqual(
                    sum(row.get("institution") == full_name for row in affiliations),
                    1,
                )
                indices = [row.get("index") for row in affiliations]
                self.assertEqual(indices, list(range(1, len(affiliations) + 1)))
                for author in paper.get("authors") or []:
                    self.assertTrue(all(
                        1 <= index <= len(affiliations)
                        for index in author.get("affiliation_indices") or []
                    ))
        self.assertGreater(len(matching_papers), 0)

    def test_restored_child_affiliations_do_not_retain_empty_parent_shadow(self):
        import json

        payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )
        for paper in payload["records"]:
            affiliations = paper.get("author_institution_affiliations") or []
            names = {row.get("institution") for row in affiliations}
            if CHILD_NAME in names:
                self.assertNotIn(PARENT_NAME, names)


if __name__ == "__main__":
    unittest.main()
