import unittest

from scripts.enrich_papers_arxiv import (
    append_cached_review_candidates,
    base_output_row,
    classify_match,
    local_preprint_enrichment,
)


class ArxivLinkEnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.formal = {
            "openalex_url": "https://openalex.org/W1",
            "title": "A Siamese-based Verification System",
            "publication_year": "2024",
            "venue": "Pattern Recognition Letters",
            "publication_type": "journal",
            "doi": "10.1016/example",
            "authors_ordered": '["Lydia Abady", "Jun Wang", "Mauro Barni"]',
        }
        self.preprint = {
            "openalex_url": "https://openalex.org/W2",
            "title": "a siamese based verification system",
            "publication_year": "2023",
            "venue": "arXiv (Cornell University)",
            "publication_type": "preprint",
            "doi": "10.48550/arxiv.2307.09822",
            "arxiv_id": "2307.09822",
            "authors_ordered": '["Lydia Abady", "Jun Wang", "Mauro Barni"]',
        }

    def test_local_pair_fills_formal_record_without_creating_another_record(self):
        rows = [self.formal, self.preprint]
        outputs = [base_output_row(row) for row in rows]

        report, counts = local_preprint_enrichment(rows, outputs)

        self.assertEqual(len(outputs), 2)
        self.assertEqual(counts["filled"], 1)
        self.assertEqual(outputs[0]["arxiv_id"], "2307.09822")
        self.assertEqual(outputs[0]["doi"], "10.1016/example")
        self.assertEqual(report[0]["action"], "filled")
        self.assertEqual(report[0]["match_basis"], "normalized_title_author")

    def test_low_author_overlap_requires_review_and_does_not_fill(self):
        unrelated = {
            **self.preprint,
            "authors_ordered": '["Unrelated Author", "Different Person"]',
        }
        rows = [self.formal, unrelated]
        outputs = [base_output_row(row) for row in rows]

        report, counts = local_preprint_enrichment(rows, outputs)

        self.assertEqual(counts["needs_review"], 1)
        self.assertEqual(outputs[0]["arxiv_id"], "")
        self.assertEqual(report[0]["action"], "needs_review")

    def test_api_doi_match_is_sufficient(self):
        status, reason, arxiv_id, _similarity, _overlap = classify_match(
            "Published title",
            ["One Author"],
            [
                {
                    "title": "Preprint title",
                    "authors": ["Different Author"],
                    "arxiv_id": "2401.00001",
                    "doi": "10.1016/example",
                }
            ],
            "10.1016/example",
        )

        self.assertEqual(status, "linked_to_arxiv")
        self.assertEqual(arxiv_id, "2401.00001")
        self.assertIn("Exact DOI", reason)

    def test_title_only_api_match_is_not_auto_linked(self):
        status, _reason, _arxiv_id, _similarity, _overlap = classify_match(
            "Exact Same Title",
            ["One Author"],
            [
                {
                    "title": "Exact Same Title",
                    "authors": ["Different Author"],
                    "arxiv_id": "2401.00001",
                    "doi": "",
                }
            ],
        )

        self.assertEqual(status, "possible_arxiv_match")

    def test_cached_possible_match_is_carried_into_review_report(self):
        output = {
            **base_output_row(self.formal),
            "arxiv_id": "2401.00001",
            "arxiv_url": "https://arxiv.org/abs/2401.00001",
            "match_status": "possible_arxiv_match",
            "author_overlap": "0.200",
            "match_reason": "Title-only candidate.",
        }
        report = []

        append_cached_review_candidates([output], report)

        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["action"], "needs_review")
        self.assertEqual(report[0]["confidence"], "low")


if __name__ == "__main__":
    unittest.main()
