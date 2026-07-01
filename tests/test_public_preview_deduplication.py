import unittest

from scripts.export_public_preview import exclude_preprint_versions
from scripts.validate_public_preview import validate_preprint_version_duplicates
from scripts.validate_public_preview import (
    normalized_author_name,
    validate_curated_affiliation_supersession,
)


class PublicPreviewDeduplicationTests(unittest.TestCase):
    def test_reversed_author_name_matches_curated_name(self):
        self.assertEqual(
            normalized_author_name("Marra, Francesco"),
            normalized_author_name("Francesco Marra"),
        )

    def test_validator_rejects_stale_openalex_affiliation(self):
        paper = {
            "title": "Example",
            "year": 2019,
            "doi": "10.1000/example",
            "curated_mappings": [
                {
                    "institution": "Correct University",
                    "institution_authors": ["Francesco Marra"],
                    "mapping_status": "active",
                }
            ],
        }
        stale = {
            **paper,
            "institution": "Stale Hospital",
            "institution_authors": ["Marra, Francesco"],
            "source_database": "OpenAlex",
        }
        issues = []

        validate_curated_affiliation_supersession(
            [stale], [paper], issues
        )

        self.assertTrue(
            any("stale public and curated institutions" in issue.message for issue in issues)
        )

    def test_validator_uses_canonical_author_id_when_names_differ(self):
        paper = {
            "title": "Canonical author test",
            "year": 2020,
            "doi": "10.1000/author-id",
            "curated_mappings": [
                {
                    "institution": "Correct University",
                    "institution_authors": ["F. Marra"],
                    "institution_author_ids": [
                        "https://openalex.org/A123"
                    ],
                    "mapping_status": "active",
                }
            ],
        }
        stale = {
            **paper,
            "institution": "Stale Hospital",
            "institution_authors": ["Francesco Marra"],
            "institution_author_ids": ["https://openalex.org/A123"],
            "source_database": "OpenAlex",
        }
        issues = []

        validate_curated_affiliation_supersession(
            [stale], [paper], issues
        )

        self.assertTrue(
            any("stale public and curated institutions" in issue.message for issue in issues)
        )

    def setUp(self):
        self.preprint = {
            "title": "A Siamese-based Verification System",
            "year": 2023,
            "venue": "arXiv (Cornell University)",
            "publication_type": "preprint",
            "doi": "10.48550/arxiv.2307.09822",
            "is_arxiv_preprint": True,
        }
        self.formal = {
            "title": "a siamese based verification system",
            "year": 2024,
            "venue": "Pattern Recognition Letters",
            "publication_type": "article",
            "doi": "10.1016/j.patrec.2024.03.002",
            "is_arxiv_preprint": False,
            "authors": ["Lydia Abady"],
            "institution": "University of Siena",
            "country": "Italy",
            "latitude": 43.31822,
            "longitude": 11.33064,
        }

    def test_formal_version_wins_across_title_punctuation_and_case(self):
        records, excluded = exclude_preprint_versions(
            [self.preprint, self.formal]
        )

        self.assertEqual(excluded, 1)
        self.assertEqual(records, [self.formal])
        self.assertEqual(records[0]["doi"], self.formal["doi"])
        self.assertEqual(records[0]["authors"], self.formal["authors"])
        self.assertEqual(records[0]["institution"], self.formal["institution"])
        self.assertEqual(records[0]["latitude"], self.formal["latitude"])

    def test_formal_doi_and_venue_override_stale_preprint_flag(self):
        formal = {**self.formal, "is_arxiv_preprint": True}

        records, excluded = exclude_preprint_versions(
            [self.preprint, formal]
        )

        self.assertEqual(excluded, 1)
        self.assertEqual(records, [formal])

    def test_preprint_without_formal_version_is_retained(self):
        records, excluded = exclude_preprint_versions([self.preprint])

        self.assertEqual(excluded, 0)
        self.assertEqual(records, [self.preprint])

    def test_validator_rejects_unfiltered_preprint_formal_pair(self):
        issues = []

        validate_preprint_version_duplicates(
            [self.preprint, self.formal],
            issues,
        )

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].level, "ERROR")
        self.assertIn("duplicates a formal publication", issues[0].message)


if __name__ == "__main__":
    unittest.main()
