import json
import unittest
from pathlib import Path

from scripts.curated_papers import CuratedPaperError, normalize_paper_draft
from scripts.publication_types import normalize_publication_type
from scripts.validate_public_preview import validate_record


class PublicationTypeTests(unittest.TestCase):
    def test_preserves_all_controlled_values(self):
        for value in ("conference", "journal", "preprint", "book"):
            self.assertEqual(normalize_publication_type(value), value)

    def test_proceedings_and_conference_venue_override_article(self):
        self.assertEqual(normalize_publication_type("proceedings-article"), "conference")
        self.assertEqual(
            normalize_publication_type("article", venue="Proceedings of CVPR"),
            "conference",
        )

    def test_common_source_aliases_are_normalized(self):
        self.assertEqual(normalize_publication_type("article"), "journal")
        self.assertEqual(normalize_publication_type("Article"), "journal")
        self.assertEqual(normalize_publication_type("article-journal"), "journal")
        self.assertEqual(normalize_publication_type("journal article"), "journal")
        self.assertEqual(normalize_publication_type("journal-article"), "journal")
        self.assertEqual(normalize_publication_type("journal"), "journal")
        self.assertEqual(normalize_publication_type("inproceedings"), "conference")
        self.assertEqual(normalize_publication_type("posted-content"), "preprint")
        self.assertEqual(normalize_publication_type("book-chapter"), "book")
        self.assertEqual(normalize_publication_type("chapter"), "book")

    def test_arxiv_only_record_is_a_preprint(self):
        self.assertEqual(
            normalize_publication_type("", arxiv_id="2601.00001"), "preprint"
        )

    def test_bibliographic_venue_evidence_resolves_legacy_entry_labels(self):
        self.assertEqual(
            normalize_publication_type("review", venue_type="journal"), "journal"
        )
        self.assertEqual(
            normalize_publication_type("review", venue_type="book series"), "book"
        )
        self.assertEqual(
            normalize_publication_type("survey", venue="ArXiv.org"), "preprint"
        )
        self.assertEqual(
            normalize_publication_type("", arxiv_id="2601.00001", venue="CVPR"),
            "",
        )

    def test_admin_save_rejects_values_outside_vocabulary(self):
        with self.assertRaisesRegex(CuratedPaperError, "publication_type"):
            normalize_paper_draft({
                "title": "Example", "year": "2026", "task": "detection",
                "source_database": "manual", "publication_type": "report",
            })

    def test_persisted_article_is_rejected_but_journal_is_accepted(self):
        base = {"title": "Example", "publication_type": "journal"}
        issues = []
        validate_record(0, base, issues)
        self.assertFalse(any("publication_type must be" in issue.message for issue in issues))

        issues = []
        validate_record(0, {**base, "publication_type": "article"}, issues)
        self.assertTrue(
            any(
                issue.message
                == "publication_type must be conference, journal, preprint, or book"
                for issue in issues
            )
        )

    def test_arxiv_fallback_defaults_to_preprint(self):
        record = normalize_paper_draft({
            "title": "Example", "year": "2026", "task": "detection",
            "source_database": "arxiv", "arxiv_id": "2601.00001",
        })
        self.assertEqual(record["publication_type"], "preprint")

    def test_current_public_exports_use_matching_canonical_types(self):
        root = Path(__file__).resolve().parents[1]
        papers = json.loads(
            (root / "web/data/public_preview_papers.json").read_text(encoding="utf-8")
        )["records"]
        markers = json.loads(
            (root / "web/data/public_preview_map_data.json").read_text(encoding="utf-8")
        )["records"]
        allowed = {"conference", "journal", "preprint", "book"}
        paper_types = {}
        for paper in papers:
            self.assertIn(paper.get("publication_type"), allowed)
            paper_types.setdefault(paper["title"].casefold(), set()).add(
                paper["publication_type"]
            )
        for marker in markers:
            self.assertIn(marker.get("publication_type"), allowed)
            self.assertIn(
                marker["publication_type"], paper_types[marker["title"].casefold()]
            )
        self.assertFalse(
            any(record.get("publication_type") == "article" for record in papers + markers)
        )

    def test_admin_dropdowns_use_journal_and_legacy_form_loading_is_normalized(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "web/admin.html").read_text(encoding="utf-8")
        javascript = (root / "web/admin.js").read_text(encoding="utf-8")
        # Add Paper, metadata override, and canonical venue creation each expose
        # the same normalized journal taxonomy value.
        self.assertEqual(html.count('value="journal"'), 3)
        self.assertNotIn('value="article"', html)
        self.assertIn('"article", "article-journal", "journal-article"', javascript)
        self.assertIn('return "journal";', javascript)


if __name__ == "__main__":
    unittest.main()
