import csv
import tempfile
import unittest
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
)
from scripts.export_public_preview import (
    add_public_detail_fields,
    apply_ordered_paper_location_summaries,
    canonicalize_public_institutions,
)
from scripts.migrate_affiliation_order import migrate


ROOT = Path(__file__).resolve().parents[1]


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

    def test_reorder_rejects_partial_or_duplicate_requests_without_writing(self):
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            self.mapping(1), self.mapping(2)
        ])
        before = self.mappings.read_bytes()
        for mapping_ids in (["mapping:1"], ["mapping:1", "mapping:1"]):
            with self.assertRaises(CuratedMappingError):
                reorder_mappings(self.paper, mapping_ids, mappings_path=self.mappings)
            self.assertEqual(self.mappings.read_bytes(), before)

    def test_failed_atomic_save_leaves_original_order_intact(self):
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            self.mapping(1), self.mapping(2)
        ])
        before = self.mappings.read_bytes()
        with patch("scripts.curated_mappings._write_csv", side_effect=OSError("failed")):
            with self.assertRaisesRegex(OSError, "failed"):
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
        self.assertNotIn("Move Up", html + javascript)
        self.assertNotIn("Move Down", html + javascript)


class AffiliationOrderReproductionTests(unittest.TestCase):
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
            "Hong Kong University of Science and Technology",
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
