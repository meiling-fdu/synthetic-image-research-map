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
    RELEASE_CANONICAL_INSTITUTION_STATUS_TOTALS,
    RELEASE_PUBLICATION_TYPE_TOTALS,
    RELEASE_TASK_TOTALS,
    PUBLIC_PAPERS_WITHOUT_MAP,
    TASK_TOTALS,
    RELEASE_REPOSITORY_BASELINE,
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
        self.assert_current("public_unique_papers", len(self.public_papers))
        self.assert_current("canonical_institution_rows", len(self.institutions))
        self.assert_current("active_canonical_institutions", len(active))
        self.assert_current(
            "inactive_or_merged_institutions",
            len(self.institutions) - len(active),
        )
        self.assert_current("institution_hierarchy_edges", len(self.hierarchy))

    def test_curated_paper_count_is_defined_by_unique_authoritative_rows(self):
        paper_ids = [row["paper_id"].strip() for row in self.curated_papers]
        self.assertTrue(paper_ids, "authoritative papers.csv must not be empty")
        self.assertTrue(all(paper_ids), "every curated paper requires a paper_id")
        self.assertEqual(
            len(self.curated_papers),
            len(set(paper_ids)),
            "authoritative papers.csv must contain one row per stable paper_id",
        )

    def test_release_checkpoint_artifact_matches_reviewed_repository_baseline(self):
        artifact = json.loads(
            (ROOT / "data/processed/current_repository_baseline.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(artifact["checkpoint"], "2026-08-24-stable-release")
        counts = artifact["dataset_counts"]
        for name, expected in RELEASE_REPOSITORY_BASELINE.items():
            with self.subTest(name=name):
                self.assertEqual(counts[name], expected)
        self.assertEqual(
            artifact["distribution_counts"]["institution_status"],
            RELEASE_CANONICAL_INSTITUTION_STATUS_TOTALS,
        )
        self.assertEqual(
            artifact["distribution_counts"]["publication_type"],
            RELEASE_PUBLICATION_TYPE_TOTALS,
        )
        self.assertEqual(
            artifact["distribution_counts"]["task"], RELEASE_TASK_TOTALS
        )

    def test_historical_public_export_baseline_is_an_explicit_reviewed_snapshot(self):
        baseline = json.loads(
            (CURATED / "public_export_baseline.json").read_text(encoding="utf-8")
        )
        self.assertEqual(baseline, {
            "paper_records": 488,
            "map_records": 950,
            "approval_note": (
                "Last reviewed complete public export before the venue taxonomy "
                "migration. Decreases require an explicitly reviewed replacement "
                "baseline."
            ),
        })

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

    def test_curated_bowie_affiliation_awaits_a_canonical_location(self):
        """Keep reviewed affiliations without publishing unconfirmed geography.

        The reviewed 1303-marker state contained two preliminary OpenAlex rows
        for this paper. Manual curation retained both affiliations, but only
        University of Baltimore currently has a confirmed canonical location.
        Bowie State therefore remains in paper detail and off the map until its
        derived pending location review is explicitly confirmed.
        """
        doi = "10.1109/snpd-winter57765.2023.10223798"
        mapping_ids = [row["mapping_id"] for row in self.mappings]
        self.assertEqual(len(mapping_ids), len(set(mapping_ids)))
        source_mappings = {
            (
                row["mapping_id"],
                row["institution_id"],
                row["location_id"],
                row["institution_authors"],
                row["mapping_status"],
                row["provenance_source"],
            )
            for row in self.mappings if row.get("doi") == doi
        }
        self.assertEqual(source_mappings, {
            (
                "mapping:03dbf1409de8df957bd3",
                "institution:86acee6f855e6b06",
                "",
                "Galamo Monkam; Jie Yan",
                "active",
                "manually_confirmed",
            ),
            (
                "mapping:5f304d4786427a2bbe5d",
                "institution:85dd03b724084b02",
                "",
                "Weifeng Xu",
                "active",
                "manually_confirmed",
            ),
        })
        paper = next(row for row in self.public_papers if row.get("doi") == doi)
        affiliations = {
            (
                row["institution_id"],
                tuple(row.get("authors") or ()),
            )
            for row in paper["author_institution_affiliations"]
        }
        self.assertEqual(affiliations, {
            (
                "institution:86acee6f855e6b06",
                ("Galamo Monkam", "Jie Yan"),
            ),
            (
                "institution:85dd03b724084b02",
                ("Weifeng Xu",),
            ),
        })

        relationships = [row for row in self.map_records if row.get("doi") == doi]
        self.assertEqual(len(relationships), 1)
        relationship = relationships[0]
        self.assertEqual(
            (
                relationship["mapping_id"],
                relationship["institution_id"],
                relationship["location_id"],
                tuple(relationship["institution_authors"]),
            ),
            (
                "mapping:5f304d4786427a2bbe5d",
                "institution:85dd03b724084b02",
                "location:87e3eb1151a82d258822",
                ("Weifeng Xu",),
            ),
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
