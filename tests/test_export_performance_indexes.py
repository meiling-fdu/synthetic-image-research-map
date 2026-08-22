import unittest
from unittest.mock import patch

from scripts import venues
from scripts.curated_export import PaperIdentityCache, PaperIdentityIndex
from scripts.export_public_preview import preserve_equal_record_key_order
from scripts.public_export_guard import _PaperIdentityIndex


class ExportPerformanceIndexTests(unittest.TestCase):
    def test_curated_index_preserves_any_identity_and_source_order(self):
        records = [
            {
                "paper_id": "curated:first",
                "title": "Shared title",
                "year": 2026,
                "doi": "10.1000/first",
            },
            {
                "paper_id": "curated:second",
                "title": "Other title",
                "year": 2026,
                "doi": "10.1000/second",
            },
        ]
        query = {
            "title": "Shared title",
            "year": 2026,
            "doi": "10.1000/second",
        }

        matches = PaperIdentityIndex(records, PaperIdentityCache()).matches(query)

        self.assertEqual(matches, records)

    def test_shrinkage_index_keeps_strong_identity_precedence(self):
        records = [
            {"title": "Shared title", "year": 2026, "doi": "10.1000/one"},
            {"title": "Shared title", "year": 2026},
        ]
        index = _PaperIdentityIndex(records)

        self.assertEqual(
            index.matches(
                {"title": "Shared title", "year": 2026, "doi": "10.1000/two"}
            ),
            [],
        )
        self.assertEqual(
            index.matches({"title": "Shared title", "year": 2026}),
            [records[1]],
        )

    def test_equal_record_key_order_is_preserved_without_value_changes(self):
        previous = [{"paper_id": "curated:one", "second": 2, "first": 1}]
        records = [{"paper_id": "curated:one", "first": 1, "second": 2}]

        changed = preserve_equal_record_key_order(records, previous)

        self.assertEqual(changed, 1)
        self.assertEqual(list(records[0]), ["paper_id", "second", "first"])
        self.assertEqual(records[0], previous[0])

    def test_venue_catalog_is_built_once_per_canonicalization_batch(self):
        aliases = venues.read_venue_aliases()
        records = [
            {
                "venue": "IEEE International Conference on Image Processing",
                "publication_type": "conference",
            },
            {
                "venue": "IEEE International Conference on Image Processing",
                "publication_type": "conference",
            },
        ]

        with patch(
            "scripts.venues._catalog_index", wraps=venues._catalog_index
        ) as catalog_index:
            result = venues.canonicalize_records(records, aliases)

        self.assertEqual(catalog_index.call_count, 1)
        self.assertEqual(result[0], result[1])


if __name__ == "__main__":
    unittest.main()
