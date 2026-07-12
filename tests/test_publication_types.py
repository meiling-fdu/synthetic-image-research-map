import unittest

from scripts.curated_papers import CuratedPaperError, normalize_paper_draft
from scripts.publication_types import normalize_publication_type


class PublicationTypeTests(unittest.TestCase):
    def test_preserves_all_controlled_values(self):
        for value in ("conference", "article", "preprint", "book"):
            self.assertEqual(normalize_publication_type(value), value)

    def test_proceedings_and_conference_venue_override_article(self):
        self.assertEqual(normalize_publication_type("proceedings-article"), "conference")
        self.assertEqual(
            normalize_publication_type("article", venue="Proceedings of CVPR"),
            "conference",
        )

    def test_common_source_aliases_are_normalized(self):
        self.assertEqual(normalize_publication_type("journal-article"), "article")
        self.assertEqual(normalize_publication_type("posted-content"), "preprint")
        self.assertEqual(normalize_publication_type("book-chapter"), "book")

    def test_admin_save_rejects_values_outside_vocabulary(self):
        with self.assertRaisesRegex(CuratedPaperError, "publication_type"):
            normalize_paper_draft({
                "title": "Example", "year": "2026", "task": "detection",
                "source_database": "manual", "publication_type": "report",
            })

    def test_arxiv_fallback_defaults_to_preprint(self):
        record = normalize_paper_draft({
            "title": "Example", "year": "2026", "task": "detection",
            "source_database": "arxiv", "arxiv_id": "2601.00001",
        })
        self.assertEqual(record["publication_type"], "preprint")


if __name__ == "__main__":
    unittest.main()
