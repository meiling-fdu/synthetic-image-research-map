import unittest
from unittest.mock import patch

from scripts.curated_papers import normalize_paper_draft
from scripts.openalex_paper_search import search_openalex_papers
from scripts.openalex_utils import normalize_title, title_similarity


TITLE = (
    "Bridging the Gap Between Ideal and Real-world Evaluation: "
    "Benchmarking AI-Generated Image Detection in Challenging Scenarios"
)
ARXIV_ID = "2509.09172"
DOI = "10.1109/ICCV51701.2025.01895"


def work(work_id, title, *, doi="", arxiv_id=""):
    locations = []
    if arxiv_id:
        locations.append(
            {"landing_page_url": f"https://arxiv.org/abs/{arxiv_id}"}
        )
    return {
        "id": f"https://openalex.org/{work_id}",
        "display_name": title,
        "doi": f"https://doi.org/{doi}" if doi else "",
        "publication_year": 2025,
        "locations": locations,
        "authorships": [],
    }


class OpenAlexPaperSearchTests(unittest.TestCase):
    def test_title_normalization_equates_typographic_variants(self):
        first = "Real-world “evaluation”—now!"
        second = "real world evaluation now."
        self.assertEqual(normalize_title(first), normalize_title(second))
        self.assertEqual(title_similarity(first, second), 1.0)

    def test_arxiv_fallback_provenance_is_accepted_by_save_layer(self):
        normalized = normalize_paper_draft(
            {
                "title": TITLE,
                "year": "2025",
                "arxiv_id": ARXIV_ID,
                "source_database": "arxiv",
                "task": "detection",
            }
        )

        self.assertEqual(normalized["source_database"], "arxiv")
        self.assertEqual(normalized["metadata_source"], "arxiv")
        self.assertEqual(normalized["curation_status"], "manually_confirmed")

    @patch("scripts.openalex_paper_search._fetch_arxiv_metadata", return_value={})
    @patch("scripts.openalex_paper_search._search_works")
    def test_doi_lookup_is_exact_and_ranked_first(self, search, _arxiv):
        correct = work("WICCV", TITLE, doi=DOI)
        unrelated = work("WOTHER", "ChatGPT Performance on the USMLE")

        def response(params):
            if params.get("filter") == f"doi:{DOI.lower()}":
                return [correct]
            return [unrelated]

        search.side_effect = response
        payload = search_openalex_papers(
            {"title": TITLE, "doi": DOI}, max_results=10
        )

        self.assertEqual(payload["results"][0]["openalex_url"], correct["id"])
        self.assertEqual(payload["results"][0]["match_basis"], "exact_doi")
        self.assertTrue(payload["debug"]["doi_exact_lookup_attempted"])
        self.assertEqual(
            search.call_args_list[0].args[0]["filter"], f"doi:{DOI.lower()}"
        )

    @patch("scripts.openalex_paper_search._fetch_arxiv_metadata")
    @patch("scripts.openalex_paper_search._search_works", return_value=[])
    def test_arxiv_exact_lookup_falls_back_to_arxiv_metadata(
        self, search, fetch_arxiv
    ):
        fetch_arxiv.return_value = {
            "title": TITLE,
            "year": "2025",
            "authors": ["Example Author"],
            "venue": "arXiv",
            "doi": "",
            "arxiv_id": ARXIV_ID,
            "openalex_url": "",
            "primary_url": f"https://arxiv.org/abs/{ARXIV_ID}",
            "paper_url": f"https://arxiv.org/abs/{ARXIV_ID}",
            "publication_type": "preprint",
            "abstract": "",
            "candidate_source": "arxiv",
        }

        payload = search_openalex_papers(
            {"title": TITLE, "arxiv_id": ARXIV_ID}
        )

        self.assertEqual(payload["results"][0]["arxiv_id"], ARXIV_ID)
        self.assertEqual(payload["results"][0]["match_basis"], "exact_arxiv")
        self.assertTrue(payload["debug"]["arxiv_exact_lookup_attempted"])
        self.assertTrue(payload["debug"]["arxiv_fallback_used"])
        self.assertEqual(
            search.call_args_list[0].args[0]["filter"],
            f"doi:10.48550/arxiv.{ARXIV_ID}",
        )

    @patch("scripts.openalex_paper_search._fetch_arxiv_metadata")
    @patch("scripts.openalex_paper_search._search_works")
    def test_arxiv_id_from_openalex_ids_is_accepted(
        self, search, fetch_arxiv
    ):
        candidate = work("WARXIV", TITLE, doi=DOI)
        candidate["ids"] = {"arxiv": f"https://arxiv.org/abs/{ARXIV_ID}"}
        search.return_value = [candidate]

        payload = search_openalex_papers({"arxiv_id": ARXIV_ID})

        self.assertEqual(payload["results"][0]["arxiv_id"], ARXIV_ID)
        self.assertEqual(payload["results"][0]["match_basis"], "exact_arxiv")
        fetch_arxiv.assert_not_called()

    @patch("scripts.openalex_paper_search._search_works")
    def test_title_variants_fetch_50_and_rerank_correct_candidate(self, search):
        correct = work("WCORRECT", TITLE)
        unrelated = work(
            "WUSMLE",
            "ChatGPT and Medical Education: Performance on the USMLE",
        )

        def response(params):
            if params.get("search") == (
                "Benchmarking AI-Generated Image Detection "
                "in Challenging Scenarios"
            ):
                return [correct]
            return [unrelated]

        search.side_effect = response
        payload = search_openalex_papers({"title": TITLE})

        self.assertEqual(payload["results"][0]["openalex_url"], correct["id"])
        self.assertEqual(
            payload["results"][0]["match_basis"], "exact_normalized_title"
        )
        weak = next(
            candidate
            for candidate in payload["results"]
            if candidate["openalex_url"] == unrelated["id"]
        )
        self.assertEqual(weak["match_strength"], "weak")
        self.assertLess(weak["similarity_score"], 0.85)
        self.assertTrue(all(
            call.args[0]["per-page"] == "50" for call in search.call_args_list
        ))
        self.assertEqual(
            [item["name"] for item in payload["debug"]["query_variants"]],
            [
                "exact_title_phrase",
                "full_title",
                "distinctive_subtitle",
                "title_search",
            ],
        )


if __name__ == "__main__":
    unittest.main()
