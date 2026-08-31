import csv
import json
import unittest
from pathlib import Path

from tests.baseline_expectations import INFORMATION_ENGINEERING_PUBLIC_RECORD_IDS

from scripts.export_public_preview import (
    add_public_detail_fields,
    add_paper_institution_search_ids,
    canonicalize_public_institutions,
    PreviewExportError,
    public_institution_aliases,
    public_canonical_institution_search_index,
    public_institution_hierarchy,
    public_institution_search_relationships,
)
from scripts.curated_export import stable_institution_id
from scripts.validate_curated_database import (
    validate_institution_hierarchy,
    validate_institution_search_relationships,
)


REPOSITORY = Path(__file__).resolve().parents[1]
PARENT_NAME = "Chinese Academy of Sciences"
PARENT_ID = "institution:3afb6cc453e0a8d9"
CHILD_NAME = "Institute of Information Engineering, Chinese Academy of Sciences"
CHILD_ID = "institution:cee70184073782c7"
CHILD_ALIAS = "Institute of Information Engineering"
LEGACY_ALIAS_ID = "institution:9aae8d70d2d6eed8"


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

    def test_confirmed_short_alias_targets_existing_child_id(self):
        aliases = self.read_csv("data/curated/institution_aliases.csv")
        matches = [row for row in aliases if row["alias_name"] == CHILD_ALIAS]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["institution_id"], CHILD_ID)
        self.assertEqual(matches[0]["canonical_institution_name"], CHILD_NAME)
        self.assertEqual(matches[0]["review_status"], "confirmed")
        institutions = self.read_csv("data/curated/institutions.csv")
        self.assertFalse(any(
            row["canonical_name"] == CHILD_ALIAS for row in institutions
        ))

    def test_short_and_full_same_paper_affiliations_dedupe_by_canonical_id(self):
        aliases = public_institution_aliases(
            self.read_csv("data/curated/institution_aliases.csv")
        )
        institutions = self.read_csv("data/curated/institutions.csv")
        paper = {
            "title": "Alias duplicate evidence",
            "doi": "10.1/iie-alias",
            "preliminary_affiliations": True,
            "authors": [
                {"name": "Short Author", "affiliation_indices": [1]},
                {"name": "Full Author", "affiliation_indices": [2]},
            ],
            "affiliations": [{
                "index": 1,
                "name": CHILD_ALIAS,
                "institution_id": LEGACY_ALIAS_ID,
                "raw_affiliation_evidence": ["Short raw evidence"],
                "provenance_sources": ["OpenAlex"],
                "preliminary": True,
            }, {
                "index": 2,
                "name": CHILD_NAME,
                "institution_id": CHILD_ID,
                "raw_affiliation_evidence": ["Full raw evidence"],
                "provenance_sources": ["paper PDF"],
            }],
            "author_institution_affiliations": [{
                "index": 1,
                "institution": CHILD_ALIAS,
                "institution_id": LEGACY_ALIAS_ID,
                "authors": ["Short Author"],
                "mapping_fallback": True,
            }, {
                "index": 2,
                "institution": CHILD_NAME,
                "institution_id": CHILD_ID,
                "authors": ["Full Author"],
            }],
        }
        maps = [{
            "title": paper["title"], "doi": paper["doi"],
            "institution": CHILD_ALIAS, "institution_id": LEGACY_ALIAS_ID,
            "institution_authors": ["Short Author"],
        }, {
            "title": paper["title"], "doi": paper["doi"],
            "institution": CHILD_NAME, "institution_id": CHILD_ID,
            "institution_authors": ["Full Author"],
        }]

        canonical_maps = canonicalize_public_institutions(
            [paper], maps, aliases, institutions=institutions,
        )
        add_public_detail_fields([paper], canonical_maps)

        self.assertEqual(len(canonical_maps), 1)
        self.assertEqual(canonical_maps[0]["institution_id"], CHILD_ID)
        self.assertEqual(canonical_maps[0]["institution"], CHILD_NAME)
        self.assertEqual(
            canonical_maps[0]["institution_authors"],
            ["Short Author", "Full Author"],
        )
        self.assertEqual(len(paper["affiliations"]), 1)
        affiliation = paper["affiliations"][0]
        self.assertEqual(affiliation["name"], CHILD_NAME)
        self.assertEqual(affiliation["institution_id"], CHILD_ID)
        self.assertEqual(
            affiliation["raw_affiliation_evidence"],
            ["Short raw evidence", "Full raw evidence"],
        )
        self.assertEqual(
            affiliation["provenance_sources"], ["OpenAlex", "paper PDF"]
        )
        self.assertTrue(affiliation["preliminary"])
        self.assertEqual(
            [author["affiliation_indices"] for author in paper["authors"]],
            [[1], [1]],
        )

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

    def test_active_registry_hierarchy_exports_without_synthesizing_locations(self):
        institutions = [
            {"institution_id": "institution:bits", "canonical_name": "BITS Pilani", "institution_status": "active", "parent_institution_id": ""},
            {"institution_id": "institution:goa", "canonical_name": "BITS Pilani, Goa", "institution_status": "active", "parent_institution_id": "institution:bits"},
            {"institution_id": "institution:hyderabad", "canonical_name": "BITS Pilani, Hyderabad", "institution_status": "active", "parent_institution_id": "institution:bits"},
            {"institution_id": "institution:old", "canonical_name": "Old campus", "institution_status": "merged", "parent_institution_id": "institution:bits"},
        ]
        first = public_institution_hierarchy([], [], institutions)
        second = public_institution_hierarchy([], [], list(reversed(institutions)))
        self.assertEqual(first, second)
        self.assertEqual(
            [(row["parent_institution_name"], row["child_institution_name"]) for row in first],
            [
                ("BITS Pilani", "BITS Pilani, Goa"),
                ("BITS Pilani", "BITS Pilani, Hyderabad"),
            ],
        )

    def test_every_active_public_institution_exports_direct_parent_metadata(self):
        institutions = [
            {"institution_id": "institution:root", "canonical_name": "Root", "institution_type": "university", "institution_status": "active", "parent_institution_id": ""},
            {"institution_id": "institution:child", "canonical_name": "Child", "institution_type": "research_unit", "institution_status": "active", "parent_institution_id": "institution:root"},
            {"institution_id": "institution:leaf", "canonical_name": "Leaf", "institution_type": "research_unit", "institution_status": "active", "parent_institution_id": "institution:child"},
        ]
        hierarchy = public_institution_hierarchy([], [], institutions)
        index = public_canonical_institution_search_index(
            institutions, [], hierarchy
        )

        self.assertEqual(set(index), {row["institution_id"] for row in institutions})
        self.assertEqual(index["institution:root"]["parent_institution_id"], "")
        self.assertEqual(
            index["institution:child"],
            {
                "canonical_name": "Child",
                "institution_type": "research_unit",
                "parent_institution_id": "institution:root",
                "parent_institution_name": "Root",
                "parent_institution_type": "university",
                "names": ["Child"],
                "normalized_names": ["child"],
            },
        )
        self.assertEqual(
            index["institution:leaf"]["parent_institution_id"],
            "institution:child",
        )

    def test_public_hierarchy_export_rejects_structural_invalidity(self):
        active = lambda institution_id, parent="": {
            "institution_id": institution_id,
            "canonical_name": institution_id.split(":", 1)[1],
            "institution_type": "research_unit",
            "institution_status": "active",
            "parent_institution_id": parent,
        }
        cases = {
            "self-parent": [active("institution:self", "institution:self")],
            "orphan": [active("institution:child", "institution:missing")],
            "cycle": [
                active("institution:a", "institution:b"),
                active("institution:b", "institution:a"),
            ],
        }
        for label, institutions in cases.items():
            with self.subTest(label=label), self.assertRaises(PreviewExportError):
                public_institution_hierarchy([], [], institutions)

        institutions = [
            active("institution:parent"),
            {**active("institution:retired"), "institution_status": "merged"},
        ]
        relationship = [{
            "parent_institution_id": "institution:parent",
            "child_institution_id": "institution:retired",
            "relationship_type": "affiliated_institute",
            "review_status": "confirmed",
        }]
        with self.assertRaises(PreviewExportError):
            public_institution_hierarchy(relationship, [], institutions)

    def test_validator_uses_active_registry_and_rejects_store_disagreement(self):
        institutions = [
            {"institution_id": "institution:certh", "institution_status": "active", "parent_institution_id": ""},
            {"institution_id": "institution:iti", "institution_status": "active", "parent_institution_id": "institution:certh"},
        ]
        relationship = {
            "parent_institution_id": "institution:certh",
            "child_institution_id": "institution:iti",
            "relationship_type": "affiliated_institute",
            "review_status": "confirmed",
        }
        issues = []
        validate_institution_hierarchy([relationship], institutions, issues)
        self.assertEqual(issues, [])
        institutions[1]["parent_institution_id"] = ""
        validate_institution_hierarchy([relationship], institutions, issues)
        self.assertTrue(any("disagrees with institutions.csv" in issue.message for issue in issues))

    def test_validator_rejects_cycle_orphan_inactive_and_alias_nodes(self):
        alias_name = "Alias Only Node"
        alias_id = stable_institution_id(alias_name)
        institutions = [
            {"institution_id": "institution:a", "institution_status": "active", "parent_institution_id": "institution:b"},
            {"institution_id": "institution:b", "institution_status": "active", "parent_institution_id": "institution:a"},
            {"institution_id": "institution:retired", "institution_status": "merged", "parent_institution_id": ""},
        ]
        relationships = [
            {"parent_institution_id": "institution:a", "child_institution_id": "institution:b", "relationship_type": "affiliated_institute", "review_status": "confirmed"},
            {"parent_institution_id": "institution:missing", "child_institution_id": "institution:a", "relationship_type": "affiliated_institute", "review_status": "confirmed"},
            {"parent_institution_id": "institution:a", "child_institution_id": "institution:retired", "relationship_type": "affiliated_institute", "review_status": "confirmed"},
            {"parent_institution_id": "institution:a", "child_institution_id": alias_id, "relationship_type": "affiliated_institute", "review_status": "confirmed"},
        ]
        issues = []
        validate_institution_hierarchy(
            relationships,
            institutions,
            issues,
            [{"alias_name": alias_name, "institution_id": "institution:a"}],
        )
        messages = [issue.message for issue in issues]
        self.assertTrue(any("cycle" in message for message in messages))
        self.assertTrue(any("orphan parent" in message for message in messages))
        self.assertTrue(any("retired/inactive" in message for message in messages))
        self.assertTrue(any("aliases cannot be hierarchy nodes" in message for message in messages))

    def test_search_relationships_export_separately_from_hierarchy(self):
        institutions = [
            {"institution_id": "institution:root", "canonical_name": "Root University", "institution_status": "active"},
            {"institution_id": "institution:related", "canonical_name": "Related University", "institution_status": "active"},
        ]
        relationships = [{
            "root_institution_id": "institution:root",
            "related_institution_id": "institution:related",
            "relationship_type": "search_family",
            "review_status": "confirmed",
            "evidence_source": "manual review",
        }]
        before = [dict(row) for row in relationships]

        exported = public_institution_search_relationships(
            relationships, institutions
        )
        issues = []
        validate_institution_search_relationships(
            relationships, institutions, issues
        )

        self.assertEqual(issues, [])
        self.assertEqual(relationships, before)
        self.assertEqual(exported, [{
            "root_institution_id": "institution:root",
            "root_institution_name": "Root University",
            "related_institution_id": "institution:related",
            "related_institution_name": "Related University",
            "relationship_type": "search_family",
            "review_status": "confirmed",
            "evidence_source": "manual review",
            "evidence_url": "",
        }])
        self.assertEqual(public_institution_hierarchy([], [], institutions), [])

    def test_paper_search_ids_include_reviewable_mappings_without_mutating_them(self):
        papers = [{"paper_id": "paper:one", "title": "One", "year": 2026}]
        mappings = [{
            "paper_id": "paper:one",
            "institution_id": "institution:active",
            "mapping_status": "active",
        }, {
            "paper_id": "paper:one",
            "institution_id": "institution:reviewable",
            "mapping_status": "needs_review",
        }, {
            "paper_id": "paper:one",
            "institution_id": "institution:excluded",
            "mapping_status": "excluded",
        }]
        before = [dict(row) for row in mappings]

        count = add_paper_institution_search_ids(papers, mappings)

        self.assertEqual(count, 1)
        self.assertEqual(mappings, before)
        self.assertEqual(
            papers[0]["search_institution_ids"],
            ["institution:active", "institution:reviewable"],
        )

    def test_hkust_search_family_keeps_registry_mappings_and_locations_separate(self):
        root_id = "institution:fa80d3c071c298e1"
        guangzhou_id = "institution:942667142da716c5"
        institutions = self.read_csv("data/curated/institutions.csv")
        relationships = self.read_csv(
            "data/curated/institution_search_relationships.csv"
        )
        hierarchy = self.read_csv("data/curated/institution_hierarchy.csv")
        mappings = self.read_csv("data/curated/author_institution_mappings.csv")
        locations = self.read_csv("data/curated/institution_locations.csv")
        by_id = {row["institution_id"]: row for row in institutions}

        self.assertEqual(by_id[root_id]["institution_status"], "active")
        self.assertEqual(by_id[guangzhou_id]["institution_status"], "active")
        self.assertEqual(by_id[guangzhou_id]["parent_institution_id"], "")
        self.assertTrue(any(
            row["root_institution_id"] == root_id
            and row["related_institution_id"] == guangzhou_id
            for row in relationships
        ))
        self.assertFalse(any(
            row["parent_institution_id"] == root_id
            and row["child_institution_id"] == guangzhou_id
            for row in hierarchy
        ))
        self.assertTrue(any(row["institution_id"] == root_id for row in mappings))
        self.assertTrue(any(row["institution_id"] == guangzhou_id for row in mappings))
        self.assertTrue(any(row["institution_id"] == root_id for row in locations))
        guangzhou_locations = [
            row for row in locations if row["institution_id"] == guangzhou_id
        ]
        self.assertTrue(guangzhou_locations)
        for location in guangzhou_locations:
            self.assertEqual(location["institution"], by_id[guangzhou_id]["canonical_name"])
            self.assertEqual(location["coordinate_status"], "known")
            self.assertTrue(-90 <= float(location["lat"]) <= 90)
            self.assertTrue(-180 <= float(location["lon"]) <= 180)

    def test_public_hkust_search_metadata_covers_root_alias_and_specific_branch(self):
        import json

        root_id = "institution:fa80d3c071c298e1"
        guangzhou_id = "institution:942667142da716c5"
        payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )
        self.assertTrue(any(
            row["root_institution_id"] == root_id
            and row["related_institution_id"] == guangzhou_id
            for row in payload["institution_search_relationships"]
        ))
        self.assertIn(
            "Hong Kong University of Science and Technology",
            payload["canonical_institution_search_index"][root_id]["names"],
        )
        self.assertIn(
            "HKUST Guangzhou",
            payload["canonical_institution_search_index"][guangzhou_id]["names"],
        )
        self.assertIn(
            "HKUST(GZ)",
            payload["canonical_institution_search_index"][guangzhou_id]["names"],
        )
        guangzhou_papers = [
            row for row in payload["records"]
            if guangzhou_id in row.get("search_institution_ids", [])
        ]
        self.assertEqual(
            [row["title"] for row in guangzhou_papers],
            [
                "RealNet: Efficient and Unsupervised Detection of "
                "AI-Generated Images via Real-Only Representation Learning",
                "SynerDetect: Hierarchical Synergistic Learning for "
                "Generalizable AI-Generated Image Detection",
            ],
        )

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
                "source_institution_id": PARENT_ID,
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

    def test_public_preview_uses_parent_for_search_without_duplicate_marker(self):
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
            self.assertEqual(
                payload["canonical_institution_search_index"][PARENT_ID][
                    "canonical_name"
                ],
                PARENT_NAME,
            )
            self.assertEqual(
                payload["canonical_institution_search_index"][CHILD_ID][
                    "canonical_name"
                ],
                CHILD_NAME,
            )

        parent_records = [
            row for row in map_payload["records"]
            if row.get("institution_id") == PARENT_ID
        ]
        child_records = [
            row for row in map_payload["records"]
            if row.get("institution_id") == CHILD_ID
        ]
        self.assertGreater(len(child_records), 0)
        self.assertEqual(
            {row["institution"] for row in child_records}, {CHILD_NAME}
        )
        child_papers = {
            row.get("doi") or row.get("title") for row in child_records
        }
        parent_papers = {
            row.get("doi") or row.get("title") for row in parent_records
        }
        self.assertTrue(child_papers.isdisjoint(parent_papers))

    def test_information_engineering_public_payload_has_exact_child_papers(self):
        map_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_map_data.json").read_text()
        )
        paper_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )
        aliases = [
            row for row in map_payload["institution_aliases"]
            if row["alias_name"] == CHILD_ALIAS
        ]
        self.assertEqual(len(aliases), 1)
        self.assertEqual(aliases[0]["canonical_institution_id"], CHILD_ID)
        self.assertEqual(
            map_payload["institution_id_redirects"][LEGACY_ALIAS_ID], CHILD_ID
        )
        child_records = [
            row for row in map_payload["records"]
            if row.get("institution_id") == CHILD_ID
        ]
        self.assertEqual(
            {row["id"] for row in child_records},
            INFORMATION_ENGINEERING_PUBLIC_RECORD_IDS,
        )
        self.assertEqual(
            len({row["title"] for row in child_records}),
            len(INFORMATION_ENGINEERING_PUBLIC_RECORD_IDS),
        )
        self.assertFalse(any(
            row.get("institution_id") == LEGACY_ALIAS_ID
            for row in map_payload["records"]
        ))
        for paper in paper_payload["records"]:
            matching = [
                row for row in paper.get("affiliations") or []
                if row.get("institution_id") == CHILD_ID
            ]
            self.assertLessEqual(len(matching), 1)
            self.assertFalse(any(
                row.get("institution_id") == LEGACY_ALIAS_ID
                for row in paper.get("affiliations") or []
            ))

    def test_public_affiliations_keep_full_cas_institute_without_parent_split(self):
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
        payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )
        for paper in payload["records"]:
            affiliations = paper.get("author_institution_affiliations") or []
            names = {row.get("institution") for row in affiliations}
            if CHILD_NAME in names:
                self.assertNotIn(PARENT_NAME, names)

    def test_committed_public_exports_share_hierarchy_and_direct_parent_metadata(self):
        map_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_map_data.json").read_text()
        )
        paper_payload = json.loads(
            (REPOSITORY / "web/data/public_preview_papers.json").read_text()
        )
        self.assertEqual(
            map_payload["institution_hierarchy"],
            paper_payload["institution_hierarchy"],
        )
        self.assertEqual(
            map_payload["canonical_institution_search_index"],
            paper_payload["canonical_institution_search_index"],
        )
        index = map_payload["canonical_institution_search_index"]
        for relationship in map_payload["institution_hierarchy"]:
            child = index[relationship["child_institution_id"]]
            self.assertEqual(
                child["parent_institution_id"],
                relationship["parent_institution_id"],
            )
            self.assertEqual(
                child["parent_institution_name"],
                relationship["parent_institution_name"],
            )
            self.assertEqual(
                child["parent_institution_type"],
                relationship["parent_institution_type"],
            )

    def test_hierarchy_export_does_not_mutate_identity_location_or_curation(self):
        institutions = self.read_csv("data/curated/institutions.csv")
        relationships = self.read_csv("data/curated/institution_hierarchy.csv")
        locations = self.read_csv("data/curated/institution_locations.csv")
        before = json.dumps(
            {"institutions": institutions, "relationships": relationships, "locations": locations},
            sort_keys=True,
        )
        exported = public_institution_hierarchy(
            relationships, locations, institutions
        )
        public_canonical_institution_search_index(institutions, [], exported)
        after = json.dumps(
            {"institutions": institutions, "relationships": relationships, "locations": locations},
            sort_keys=True,
        )
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
