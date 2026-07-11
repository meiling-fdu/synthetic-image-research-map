import unittest

from scripts.audit_arxiv_published_duplicates import audit_duplicates, audit_input_records


class ArxivPublishedDuplicateAuditTests(unittest.TestCase):
    def test_source_generator_attribution_spot_check(self):
        curated = [{
            "title": "Source Generator Attribution via Inversion",
            "year": "2019",
            "venue": "CVPR Workshops",
            "arxiv_id": "1905.02259",
            "openalex_url": "https://openalex.org/W2971682216",
            "publication_type": "conference",
        }]
        links = [{
            "title": "Source Generator Attribution via Inversion",
            "year": "2019",
            "venue": "arXiv (Cornell University)",
            "doi": "10.48550/arxiv.1905.02259",
            "arxiv_id": "1905.02259v1",
            "openalex_url": "https://openalex.org/W2943961047",
        }]

        rows = audit_duplicates(audit_input_records(curated, links))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["published_openalex_id"], "W2971682216")
        self.assertEqual(rows[0]["arxiv_openalex_id"], "W2943961047")
        self.assertEqual(rows[0]["arxiv_id"], "1905.02259")
        self.assertEqual(rows[0]["recommended_action"], "keep_published_attach_arxiv")
        self.assertEqual(rows[0]["confidence"], "high")


if __name__ == "__main__":
    unittest.main()
