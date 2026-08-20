import csv
import json
import unittest
from collections import Counter
from pathlib import Path

from scripts.export_public_preview import identity_key
from scripts.paper_exclusions import records_share_any_identity
from scripts.public_relationships import public_relationship_key
from tests.baseline_expectations import (
    ACTIVE_CANONICAL_INSTITUTION_TYPE_TOTALS,
    CANONICAL_INSTITUTION_STATUS_TOTALS,
    CANONICAL_INSTITUTION_TYPE_TOTALS,
    CURRENT_REPOSITORY_BASELINE,
    INFORMATION_ENGINEERING_PUBLIC_RECORD_IDS,
    PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS,
    PUBLICATION_TYPE_TOTALS,
    PUBLIC_PAPERS_WITHOUT_MAP,
    TASK_TOTALS,
)


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"
PUBLIC = ROOT / "web" / "data"
INFORMATION_ENGINEERING_ID = "institution:cee70184073782c7"


def read_csv(name):
    with (CURATED / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_public(name):
    with (PUBLIC / name).open(encoding="utf-8") as handle:
        return json.load(handle)


class CurrentRepositoryBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curated_papers = read_csv("papers.csv")
        cls.institutions = read_csv("institutions.csv")
        cls.mappings = read_csv("author_institution_mappings.csv")
        cls.hierarchy = read_csv("institution_hierarchy.csv")
        cls.paper_payload = read_public("public_preview_papers.json")
        cls.map_payload = read_public("public_preview_map_data.json")
        cls.public_papers = cls.paper_payload["records"]
        cls.map_records = cls.map_payload["records"]

    def assert_current(self, name, computed):
        expected = CURRENT_REPOSITORY_BASELINE[name]
        self.assertEqual(
            computed,
            expected,
            (
                f"Current repository baseline is stale for {name}: "
                f"expected {expected}, computed {computed}. Review curated changes "
                "and update tests/baseline_expectations.py."
            ),
        )

    def test_current_repository_counts_recompute_from_authoritative_files(self):
        active = [
            row for row in self.institutions
            if row["institution_status"] == "active"
        ]
        self.assert_current("curated_papers", len(self.curated_papers))
        self.assert_current("public_unique_papers", len(self.public_papers))
        self.assert_current("public_map_relationships", len(self.map_records))
        self.assert_current("canonical_institution_rows", len(self.institutions))
        self.assert_current("active_canonical_institutions", len(active))
        self.assert_current(
            "inactive_or_merged_institutions",
            len(self.institutions) - len(active),
        )
        self.assert_current("author_institution_mappings", len(self.mappings))
        self.assert_current("institution_hierarchy_edges", len(self.hierarchy))

    def test_public_paper_and_map_relationship_identities_are_unique(self):
        paper_identities = [identity_key(row) for row in self.public_papers]
        self.assertEqual(len(paper_identities), len(set(paper_identities)))
        map_relationships = [public_relationship_key(row) for row in self.map_records]
        self.assertEqual(len(map_relationships), len(set(map_relationships)))
        self.assertTrue(
            all(
                any(
                    records_share_any_identity(map_record, paper)
                    for paper in self.public_papers
                )
                for map_record in self.map_records
            )
        )

    def test_public_paper_map_coverage_matches_reviewed_blockers(self):
        map_source_papers = {identity_key(row) for row in self.map_records}
        papers_with_map = [
            paper for paper in self.public_papers
            if any(
                records_share_any_identity(paper, marker)
                for marker in self.map_records
            )
        ]
        papers_without_map = [
            paper for paper in self.public_papers
            if paper not in papers_with_map
        ]
        self.assert_current("public_map_source_papers", len(map_source_papers))
        self.assert_current("public_papers_with_map", len(papers_with_map))
        self.assert_current("public_papers_without_map", len(papers_without_map))
        self.assertEqual(
            {paper["title"] for paper in papers_without_map},
            set(PUBLIC_PAPERS_WITHOUT_MAP),
        )
        with (ROOT / "data/manual/paper_marker_blocker_report.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            blockers = {
                row["title"]: row["blocker_type"]
                for row in csv.DictReader(handle)
                if row["title"] in PUBLIC_PAPERS_WITHOUT_MAP
            }
        self.assertEqual(blockers, PUBLIC_PAPERS_WITHOUT_MAP)

    def test_public_institutions_are_exactly_active_canonicals(self):
        institution_ids = [row["institution_id"] for row in self.institutions]
        self.assertEqual(len(institution_ids), len(set(institution_ids)))
        active_ids = {
            row["institution_id"] for row in self.institutions
            if row["institution_status"] == "active"
        }
        merged_ids = {
            row["institution_id"] for row in self.institutions
            if row["institution_status"] == "merged"
        }
        for payload in (self.paper_payload, self.map_payload):
            self.assertEqual(
                set(payload["canonical_institution_search_index"]),
                active_ids,
            )
            self.assertTrue(
                merged_ids.issubset(payload["institution_id_redirects"])
            )
            self.assertTrue(
                set(payload["institution_id_redirects"].values()).issubset(active_ids)
            )
        for row in self.map_records:
            if row["institution_id"] in active_ids:
                continue
            self.assertEqual(row.get("affiliation_review_state"), "unreviewed")
            self.assertTrue(row.get("preliminary_affiliations"))
            self.assertEqual(row.get("institution_source"), "automatic_fallback")

    def test_status_and_type_totals_reconcile_their_declared_populations(self):
        statuses = Counter(row["institution_status"] for row in self.institutions)
        self.assertEqual(statuses, CANONICAL_INSTITUTION_STATUS_TOTALS)
        self.assertEqual(
            Counter(row["institution_type"] for row in self.institutions),
            CANONICAL_INSTITUTION_TYPE_TOTALS,
        )
        active = [
            row for row in self.institutions
            if row["institution_status"] == "active"
        ]
        self.assertEqual(
            Counter(row["institution_type"] for row in active),
            ACTIVE_CANONICAL_INSTITUTION_TYPE_TOTALS,
        )
        paper_type_counts = Counter()
        for paper in self.public_papers:
            paper_type_counts.update(
                set(paper.get("aggregated_institution_types") or ())
            )
        self.assertEqual(
            paper_type_counts,
            PUBLIC_PAPER_INSTITUTION_TYPE_TOTALS,
        )

    def test_publication_and_task_totals_use_single_label_paper_semantics(self):
        publication_types = Counter(
            row.get("publication_type") for row in self.public_papers
        )
        tasks = Counter(row.get("task") for row in self.public_papers)
        self.assertEqual(publication_types, PUBLICATION_TYPE_TOTALS)
        self.assertEqual(tasks, TASK_TOTALS)
        self.assertEqual(sum(publication_types.values()), len(self.public_papers))
        self.assertEqual(sum(tasks.values()), len(self.public_papers))

    def test_hierarchy_edges_reference_active_ids_and_are_acyclic(self):
        active_ids = {
            row["institution_id"] for row in self.institutions
            if row["institution_status"] == "active"
        }
        edges = [
            (row["parent_institution_id"], row["child_institution_id"])
            for row in self.hierarchy
        ]
        self.assertEqual(len(edges), len(set(edges)))
        self.assertTrue({item for edge in edges for item in edge} <= active_ids)
        children = {}
        for parent, child in edges:
            children.setdefault(parent, set()).add(child)
        for start in active_ids:
            pending = list(children.get(start, ()))
            visited = set()
            while pending:
                node = pending.pop()
                self.assertNotEqual(node, start, f"hierarchy cycle from {start}")
                if node not in visited:
                    visited.add(node)
                    pending.extend(children.get(node, ()))

    def test_information_engineering_record_identity_set_is_exact(self):
        actual = {
            row["id"] for row in self.map_records
            if row.get("institution_id") == INFORMATION_ENGINEERING_ID
        }
        self.assertEqual(actual, INFORMATION_ENGINEERING_PUBLIC_RECORD_IDS)
