import csv
import json
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from scripts.curated_export import _recalculate_paper_details
from scripts.curated_mappings import (
    CuratedMappingError,
    create_mapping,
    exclude_mapping,
    load_mappings,
    mappings_for_paper,
    reorder_mappings,
    replace_all_mappings,
)
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
    INSTITUTION_REVIEW_QUEUE_COLUMNS,
    PAPER_EXCLUSION_COLUMNS,
)
from scripts.export_public_preview import (
    add_public_detail_fields,
    apply_ordered_paper_location_summaries,
    canonicalize_public_institutions,
)
from scripts.migrate_affiliation_order import affiliation_order_issues, migrate
from scripts.validate_curated_database import validate_mapping_evidence
from scripts.serve_admin import make_handler


ROOT = Path(__file__).resolve().parents[1]
CURATED_PAPER_COLUMNS = (
    "paper_id", "title", "year", "authors", "venue", "venue_id",
    "venue_name", "venue_acronym", "venue_type", "venue_track", "raw_venue",
    "doi", "arxiv_id", "openalex_url", "paper_url", "publication_type",
    "abstract", "task", "scope_status", "source_database", "metadata_source",
    "curation_status", "review_status", "created_at", "updated_at",
    "paper_categories",
)


def blank(columns, **values):
    return {column: str(values.get(column, "")) for column in columns}


def write_csv(path, columns, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class AffiliationOrderTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(self.temporary_directory.name)
        self.mappings = root / "mappings.csv"
        self.reviews = root / "reviews.csv"
        self.institutions = root / "institutions.csv"
        self.aliases = root / "aliases.csv"
        self.locations = root / "locations.csv"
        self.paper = {"paper_id": "paper:1", "title": "Fixture", "year": "2026"}
        write_csv(self.reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS)
        write_csv(self.aliases, INSTITUTION_ALIAS_COLUMNS)
        write_csv(self.locations, INSTITUTION_LOCATION_COLUMNS)
        write_csv(self.institutions, INSTITUTION_COLUMNS, [
            blank(INSTITUTION_COLUMNS, institution_id=f"institution:{index}",
                  canonical_name=f"Institution {index}", institution_status="active")
            for index in range(1, 7)
        ])

    def tearDown(self):
        self.temporary_directory.cleanup()

    def mapping(self, index, *, order=None, status="active", authors=None):
        return blank(
            AUTHOR_INSTITUTION_MAPPING_COLUMNS,
            mapping_id=f"mapping:{index}", paper_id=self.paper["paper_id"],
            title=self.paper["title"], year=self.paper["year"],
            institution=f"Institution {index}", institution_id=f"institution:{index}",
            institution_authors=authors or f"Author {index}",
            raw_affiliation=f"Raw {index}", mapping_status=status,
            affiliation_order=index if order is None else order,
            provenance_source="fixture",
        )

    def test_reorder_persists_exact_permutation_and_changes_only_order(self):
        rows = [self.mapping(index) for index in range(1, 6)]
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, rows)
        before = {row["mapping_id"]: dict(row) for row in load_mappings(self.mappings)}

        result = reorder_mappings(
            self.paper,
            ["mapping:1", "mapping:2", "mapping:5", "mapping:3", "mapping:4"],
            mappings_path=self.mappings,
        )

        self.assertEqual(result["mapping_ids"][2], "mapping:5")
        saved = load_mappings(self.mappings)
        self.assertEqual(
            [row["mapping_id"] for row in mappings_for_paper(self.paper, saved)[:5]],
            ["mapping:1", "mapping:2", "mapping:5", "mapping:3", "mapping:4"],
        )
        for row in saved:
            expected = dict(before[row["mapping_id"]])
            expected["affiliation_order"] = row["affiliation_order"]
            self.assertEqual(row, expected)

    def test_admin_endpoint_reorder_survives_disk_reload_and_get(self):
        rows = [self.mapping(index) for index in range(1, 6)]
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, rows)
        root = self.mappings.parent
        curated_papers = root / "papers.csv"
        exclusions = root / "exclusions.csv"
        queue = root / "institution_review_queue.csv"
        public_papers = root / "public_papers.json"
        public_map = root / "public_map.json"
        write_csv(curated_papers, CURATED_PAPER_COLUMNS, [{
            "paper_id": self.paper["paper_id"],
            "title": self.paper["title"],
            "year": self.paper["year"],
            "authors": "Author 1; Author 2; Author 3; Author 4; Author 5",
            "task": "detection",
            "scope_status": "in_scope",
            "source_database": "fixture",
            "metadata_source": "fixture",
            "curation_status": "confirmed",
            "review_status": "reviewed",
        }])
        write_csv(exclusions, PAPER_EXCLUSION_COLUMNS)
        write_csv(queue, INSTITUTION_REVIEW_QUEUE_COLUMNS)
        public_papers.write_text("[]", encoding="utf-8")
        public_map.write_text("[]", encoding="utf-8")
        requested = [
            "mapping:1", "mapping:4", "mapping:2", "mapping:5", "mapping:3"
        ]

        with (
            patch("scripts.serve_admin.PUBLIC_PAPERS_PATH", public_papers),
            patch("scripts.serve_admin.PUBLIC_MAP_PATH", public_map),
        ):
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(
                "test-token",
                exclusions_path=exclusions,
                curated_papers_path=curated_papers,
                mappings_path=self.mappings,
                location_review_path=self.reviews,
                institution_review_queue_path=queue,
            ))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base_url = f"http://127.0.0.1:{server.server_port}"
                request = urllib.request.Request(
                    base_url + "/api/paper/mappings/reorder",
                    data=json.dumps({
                        "id": self.paper["paper_id"],
                        "mapping_ids": requested,
                    }).encode("utf-8"),
                    method="POST",
                    headers={
                        "X-Admin-Token": "test-token",
                        "Content-Type": "application/json",
                    },
                )
                with urllib.request.urlopen(request, timeout=3) as response:
                    saved_response = json.loads(response.read())

                self.assertEqual(saved_response["mapping_ids"], requested)
                del saved_response

                reloaded_rows = load_mappings(self.mappings)
                reloaded = mappings_for_paper(self.paper, reloaded_rows)
                self.assertEqual(
                    [(row["mapping_id"], row["affiliation_order"]) for row in reloaded],
                    [(mapping_id, str(index)) for index, mapping_id in enumerate(requested, 1)],
                )
                del reloaded_rows, reloaded

                get_url = (
                    base_url + "/api/paper/mappings?id="
                    + urllib.parse.quote(self.paper["paper_id"])
                )
                get_request = urllib.request.Request(
                    get_url, headers={"X-Admin-Token": "test-token"}
                )
                with urllib.request.urlopen(get_request, timeout=3) as response:
                    admin_reload = json.loads(response.read())
                self.assertEqual(
                    [row["mapping_id"] for row in admin_reload["curated_mappings"]],
                    requested,
                )
                self.assertEqual(
                    [row["affiliation_order"] for row in admin_reload["curated_mappings"]],
                    ["1", "2", "3", "4", "5"],
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_migration_groups_by_stable_paper_id_and_normalizes_legacy_duplicates(self):
        rows = [
            {**self.mapping(1), "doi": "10.1/formal", "affiliation_order": "1"},
            {**self.mapping(2), "doi": "10.1/preprint", "affiliation_order": "1"},
        ]
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, rows)
        self.assertEqual(migrate(self.mappings), 1)
        self.assertEqual(
            [row["affiliation_order"] for row in load_mappings(self.mappings)],
            ["1", "2"],
        )

    def test_migration_groups_legacy_ids_by_shared_openalex_identity(self):
        rows = [
            {**self.mapping(1), "paper_id": "curated:legacy", "doi": "10.1/shared",
             "openalex_url": "https://openalex.org/W1", "affiliation_order": "1"},
            {**self.mapping(2), "paper_id": "openalex:W1", "doi": "10.1/shared",
             "openalex_url": "https://openalex.org/W1", "affiliation_order": "1"},
            {**self.mapping(3), "paper_id": "curated:legacy", "doi": "10.1/shared",
             "openalex_url": "https://openalex.org/W1", "affiliation_order": "2"},
        ]
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, rows)

        issues = affiliation_order_issues(load_mappings(self.mappings))
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["reasons"], ["duplicate", "gapped_or_non_contiguous"])
        self.assertEqual(migrate(self.mappings), 2)
        self.assertEqual(
            [row["affiliation_order"] for row in load_mappings(self.mappings)],
            ["1", "2", "3"],
        )
        self.assertEqual(migrate(self.mappings), 0)

    def test_audit_reports_missing_duplicate_gapped_and_accepts_valid_sets(self):
        cases = {
            "missing": (["1", ""], "missing"),
            "duplicate": (["1", "1"], "duplicate"),
            "gapped": (["1", "3"], "gapped_or_non_contiguous"),
            "non_integer": (["1", "two"], "non_integer"),
            "zero_based": (["0", "1"], "non_positive"),
        }
        for name, (orders, reason) in cases.items():
            with self.subTest(name=name):
                rows = [self.mapping(index, order=order) for index, order in enumerate(orders, 1)]
                issues = affiliation_order_issues(rows)
                self.assertEqual(len(issues), 1)
                self.assertIn(reason, issues[0]["reasons"])
        self.assertEqual(
            affiliation_order_issues([
                self.mapping(1, order="1"), self.mapping(2, order="2")
            ]),
            [],
        )

    def test_repository_has_no_active_affiliation_order_violations(self):
        rows = load_mappings(ROOT / "data/curated/author_institution_mappings.csv")
        self.assertEqual(affiliation_order_issues(rows), [])

    def test_curated_validator_uses_shared_durable_identity_component(self):
        rows = [
            {**self.mapping(1), "paper_id": "curated:legacy", "openalex_url": "https://openalex.org/W1", "affiliation_order": "1"},
            {**self.mapping(2), "paper_id": "openalex:W1", "openalex_url": "https://openalex.org/W1", "affiliation_order": "2"},
            {**self.mapping(3), "paper_id": "curated:legacy", "openalex_url": "https://openalex.org/W1", "affiliation_order": "3"},
        ]
        issues = []
        validate_mapping_evidence(rows, issues)
        self.assertFalse([
            issue for issue in issues if "affiliation_order" in issue.message
        ])
        rows[2]["affiliation_order"] = "2"
        issues = []
        validate_mapping_evidence(rows, issues)
        self.assertEqual(
            len([issue for issue in issues if "affiliation_order" in issue.message]),
            1,
        )

    def test_reorder_rejects_partial_or_duplicate_requests_without_writing(self):
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            self.mapping(1), self.mapping(2)
        ])
        before = self.mappings.read_bytes()
        for mapping_ids in (["mapping:1"], ["mapping:1", "mapping:1"]):
            with self.assertRaises(CuratedMappingError):
                reorder_mappings(self.paper, mapping_ids, mappings_path=self.mappings)
            self.assertEqual(self.mappings.read_bytes(), before)

    def test_explicit_order_cannot_fall_back_when_incomplete_or_non_contiguous(self):
        for orders in (("1", ""), ("1", "invalid"), ("1", "1"), ("1", "3")):
            rows = [
                self.mapping(index, order=order)
                for index, order in enumerate(orders, start=1)
            ]
            with self.assertRaisesRegex(CuratedMappingError, "explicit, unique"):
                mappings_for_paper(self.paper, rows)

    def test_failed_atomic_save_leaves_original_order_intact(self):
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            self.mapping(1), self.mapping(2)
        ])
        before = self.mappings.read_bytes()
        with patch("pathlib.Path.replace", side_effect=OSError("failed")):
            with self.assertRaisesRegex(CuratedMappingError, "could not write"):
                reorder_mappings(
                    self.paper, ["mapping:2", "mapping:1"],
                    mappings_path=self.mappings,
                )
        self.assertEqual(self.mappings.read_bytes(), before)

    def test_create_appends_and_exclude_compacts_relative_order(self):
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            self.mapping(1), self.mapping(2), self.mapping(3)
        ])
        created = create_mapping(
            self.paper,
            {"institution": "Institution 4", "institution_id": "institution:4",
             "institution_authors": "Author 4", "mapping_status": "active"},
            map_records=[], mappings_path=self.mappings,
            location_review_path=self.reviews, institutions_path=self.institutions,
            institution_aliases_path=self.aliases,
            institution_locations_path=self.locations,
        )["mapping"]
        self.assertEqual(created["affiliation_order"], "4")

        exclude_mapping(
            self.paper, "mapping:2", "fixture removal", mappings_path=self.mappings
        )
        current = mappings_for_paper(self.paper, load_mappings(self.mappings))[:3]
        self.assertEqual([row["mapping_id"] for row in current], [
            "mapping:1", "mapping:3", created["mapping_id"]
        ])
        self.assertEqual([row["affiliation_order"] for row in current], ["1", "2", "3"])

    def test_replace_all_uses_admin_array_order(self):
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [self.mapping(1)])
        result = replace_all_mappings(
            self.paper,
            [
                {"institution": "Institution 3", "institution_id": "institution:3",
                 "institution_authors": "Author 3", "mapping_status": "active"},
                {"institution": "Institution 2", "institution_id": "institution:2",
                 "institution_authors": "Author 2", "mapping_status": "active"},
            ],
            "fixture replacement", confirm_replace_all=True, map_records=[],
            mappings_path=self.mappings, location_review_path=self.reviews,
            institutions_path=self.institutions, institution_aliases_path=self.aliases,
            institution_locations_path=self.locations,
        )
        self.assertEqual(
            [(row["institution"], row["affiliation_order"]) for row in result["mappings"]],
            [("Institution 3", "1"), ("Institution 2", "2")],
        )

    def test_export_preserves_order_and_multi_affiliation_superscripts(self):
        mappings = [
            self.mapping(3, order=3, authors="Chao Wu"),
            self.mapping(1, order=1, authors="Qianshu Cai; Xinmei Tian"),
            self.mapping(2, order=2, authors="Chao Wu"),
        ]
        paper = {**self.paper, "authors": ["Qianshu Cai", "Chao Wu", "Xinmei Tian"]}
        _recalculate_paper_details(paper, [], mappings, set())
        self.assertEqual(paper["aggregated_institutions"], [
            "Institution 1", "Institution 2", "Institution 3"
        ])
        indices = {row["author"]: row["institution_indices"]
                   for row in paper["author_institution_indices"]}
        self.assertEqual(indices["Qianshu Cai"], [1])
        self.assertEqual(indices["Chao Wu"], [2, 3])
        self.assertEqual(indices["Xinmei Tian"], [1])

    def test_final_public_pass_cannot_restore_stale_superscripts_or_map_order(self):
        affiliations = [
            {"index": 1, "institution": "Institution 1", "institution_id": "institution:1",
             "authors": ["Qianshu Cai", "Xinmei Tian"]},
            {"index": 2, "institution": "Institution 2", "institution_id": "institution:2",
             "authors": ["Chao Wu"]},
            {"index": 3, "institution": "Institution 3", "institution_id": "institution:3",
             "authors": ["Chao Wu"]},
        ]
        paper = {
            **self.paper,
            "authors": ["Qianshu Cai", "Chao Wu", "Xinmei Tian"],
            "author_institution_affiliations": affiliations,
            "author_institution_indices": [
                {"author": "Chao Wu", "institution_indices": [2, 5]},
            ],
            "aggregated_institutions": [
                "Institution 1", "Institution 2", "Institution 3"
            ],
            "affiliation_review_state": "curated",
            "institution_source": "curated",
        }
        stale_map_order = [
            {**self.paper, "institution": "Institution 3", "institution_id": "institution:3",
             "institution_authors": ["Chao Wu"], "source_database": "curated",
             "institution_source": "curated", "affiliation_order": 3},
            {**self.paper, "institution": "Institution 1", "institution_id": "institution:1",
             "institution_authors": ["Qianshu Cai", "Xinmei Tian"],
             "source_database": "curated", "institution_source": "curated",
             "affiliation_order": 1},
            {**self.paper, "institution": "Institution 2", "institution_id": "institution:2",
             "institution_authors": ["Chao Wu"], "source_database": "curated",
             "institution_source": "curated", "affiliation_order": 2},
        ]
        canonicalize_public_institutions([paper], stale_map_order, [])
        apply_ordered_paper_location_summaries([paper], stale_map_order)
        add_public_detail_fields([paper], stale_map_order)
        indices = {row["author"]: row["institution_indices"]
                   for row in paper["author_institution_indices"]}
        self.assertEqual(indices["Chao Wu"], [2, 3])
        self.assertEqual(paper["aggregated_institutions"], [
            "Institution 1", "Institution 2", "Institution 3"
        ])

    def test_admin_has_handle_only_drag_reorder_ui(self):
        html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        javascript = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        self.assertIn('<th class="mapping-order-heading">Order</th>', html)
        self.assertIn('handle.textContent = "⋮⋮"', javascript)
        self.assertIn('row.addEventListener("dragstart"', javascript)
        self.assertIn('"/api/paper/mappings/reorder"', javascript)
        self.assertIn("body.ondrop", javascript)
        self.assertIn("restoreMappingRows(previousMappingIds)", javascript)
        self.assertIn("The server did not confirm", javascript)
        self.assertIn("Persisted affiliation_order must be explicit", javascript)
        self.assertNotIn("Move Up", html + javascript)
        self.assertNotIn("Move Down", html + javascript)


class AffiliationOrderReproductionTests(unittest.TestCase):
    def test_affected_papers_have_requested_persisted_admin_order(self):
        rows = load_mappings(
            ROOT / "data/curated/author_institution_mappings.csv"
        )
        expected = {
            "curated:6a5bef99dcdc1ad4ba28": [
                "Zhejiang University",
                "Hangzhou High-Tech Zone (Binjiang) Institute of Blockchain and Data Security",
                "George Mason University",
            ],
            "curated:211ea83fa8d41c8ec810": [
                "Anhui University",
                "Institute of Artificial Intelligence, Hefei Comprehensive National Science Center",
                "National University of Singapore",
                "University of Science and Technology of China",
                "Origin Quantum Computing Technology (Hefei) Co., Ltd.",
            ],
        }
        for paper_id, institutions in expected.items():
            paper = {"paper_id": paper_id}
            mappings = mappings_for_paper(paper, rows)
            self.assertEqual(
                [row["institution"] for row in mappings], institutions
            )
            self.assertEqual(
                [row["affiliation_order"] for row in mappings],
                [str(index) for index in range(1, len(institutions) + 1)],
            )

    def test_towards_generalizable_detector_public_numbering(self):
        paper = {
            "paper_id": "curated:0b5e852ad2faa5d89eb5",
            "title": "Towards Generalizable Detector for Generated Image",
            "year": "2025",
            "authors": ["Qianshu Cai", "Chao Wu", "Yonggang Zhang", "Jun Yu", "Xinmei Tian"],
        }
        mappings = mappings_for_paper(
            paper,
            load_mappings(ROOT / "data/curated/author_institution_mappings.csv"),
        )
        _recalculate_paper_details(paper, [], mappings, set())
        self.assertEqual(paper["aggregated_institutions"], [
            "University of Science and Technology of China",
            "Zhejiang University",
            "Hebei Institute of Communications",
            "The Hong Kong University of Science and Technology",
            "Harbin Institute of Technology, Shenzhen",
        ])
        indices = {row["author"]: row["institution_indices"]
                   for row in paper["author_institution_indices"]}
        self.assertEqual(indices, {
            "Qianshu Cai": [1], "Chao Wu": [2, 3], "Yonggang Zhang": [4],
            "Jun Yu": [5], "Xinmei Tian": [1],
        })


if __name__ == "__main__":
    unittest.main()
