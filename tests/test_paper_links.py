import unittest

from scripts.paper_links import canonical_url, resolve_public_links


class PaperLinkResolverTests(unittest.TestCase):
    def test_formal_doi_and_arxiv_are_separate(self):
        links = resolve_public_links({
            "doi": "10.1145/Example",
            "arxiv_id": "2401.12345v2",
        })
        self.assertEqual(links["formal_doi"], "10.1145/example")
        self.assertEqual(links["formal_url"], "https://doi.org/10.1145/example")
        self.assertEqual(links["arxiv_url"], "https://arxiv.org/abs/2401.12345")

    def test_arxiv_doi_does_not_override_formal_paper_url(self):
        links = resolve_public_links({
            "doi": "10.48550/arxiv.2401.12345",
            "paper_url": "https://doi.org/10.1000/Formal",
        })
        self.assertEqual(links["formal_doi"], "10.1000/formal")
        self.assertEqual(links["formal_url"], "https://doi.org/10.1000/formal")
        self.assertEqual(links["arxiv_id"], "2401.12345")

    def test_arxiv_doi_url_is_not_a_formal_publication(self):
        links = resolve_public_links({
            "doi": "10.48550/arxiv.2401.12345",
            "paper_url": "https://doi.org/10.48550/arxiv.2401.12345",
        })
        self.assertFalse(links["formal_url"])
        self.assertEqual(links["primary_url"], "https://arxiv.org/abs/2401.12345")

    def test_bare_and_url_dois_normalize_without_duplication(self):
        bare = resolve_public_links({"doi": "doi:10.1000/Example"})
        url = resolve_public_links({"doi": "HTTP://DX.DOI.ORG/10.1000/Example/"})
        self.assertEqual(bare["formal_url"], "https://doi.org/10.1000/example")
        self.assertEqual(url["formal_url"], "https://doi.org/10.1000/example")

    def test_arxiv_only_and_published_only(self):
        preprint = resolve_public_links({
            "doi": "10.48550/arxiv.2401.12345",
        })
        published = resolve_public_links({"paper_url": "https://publisher.example/a"})
        self.assertEqual(preprint["primary_url"], "https://arxiv.org/abs/2401.12345")
        self.assertFalse(preprint["formal_url"])
        self.assertEqual(published["formal_url"], "https://publisher.example/a")
        self.assertFalse(published["arxiv_url"])

    def test_equivalent_doi_urls_have_one_canonical_target(self):
        self.assertEqual(
            canonical_url("http://dx.doi.org/10.1000/Example/"),
            canonical_url("https://doi.org/10.1000/example"),
        )


if __name__ == "__main__":
    unittest.main()
