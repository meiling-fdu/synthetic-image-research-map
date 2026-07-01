import unittest

from scripts.canonical_authorship import _merge_paper_rows, load_canonical_dataset


class PublicPreviewDeduplicationTests(unittest.TestCase):
    def test_w3010699567_is_one_canonical_paper(self):
        papers = load_canonical_dataset(check_runtime=False)["papers"]
        matches = [
            paper for paper in papers
            if paper.get("openalex_url", "").rstrip("/").endswith("W3010699567")
        ]
        self.assertEqual(len(matches), 1)

    def test_iris_and_openalex_are_provenance_not_entities(self):
        papers = _merge_paper_rows(
            [
                {
                    "paper_id": "iris:1", "title": "Example", "year": "2020",
                    "doi": "10.1/example", "source_database": "IRIS",
                },
                {
                    "paper_id": "openalex:W1", "title": "Example", "year": "2020",
                    "doi": "https://doi.org/10.1/example",
                    "openalex_url": "https://openalex.org/W1",
                    "source_database": "OpenAlex",
                },
            ]
        )
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["paper_id"], "doi:10.1/example")
        self.assertEqual(papers[0]["provenance_sources"], ["IRIS", "OpenAlex"])


if __name__ == "__main__":
    unittest.main()
