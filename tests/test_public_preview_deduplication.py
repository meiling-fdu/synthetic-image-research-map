import json
import subprocess
import unittest
from pathlib import Path

from scripts.export_public_preview import (
    add_public_detail_fields,
    exclude_preprint_versions,
)
from scripts.refresh_public_preview import build_steps, parse_args
from scripts.validate_public_preview import validate_preprint_version_duplicates
from scripts.validate_public_preview import (
    normalized_author_name,
    validate_curated_affiliation_supersession,
)


class PublicPreviewDeduplicationTests(unittest.TestCase):
    def test_no_search_refresh_preserves_large_preview_without_default_cap(self):
        args = parse_args(
            [
                "--skip-search",
                "--user-agent",
                "test refresh",
            ]
        )

        steps = build_steps(args)
        commands = [step.command for step in steps]

        self.assertEqual(len(steps), 3)
        self.assertTrue(
            all("run_pipeline.py" not in " ".join(command) for command in commands)
        )
        self.assertIn("--preserve-existing", commands[0])
        self.assertNotIn("--max-records", commands[0])

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

    def test_affiliations_union_across_unique_paper_and_markers(self):
        paper = {
            "title": "Shared paper",
            "year": 2020,
            "doi": "10.1000/shared",
            "authors": ["Doe, Jane", "John Roe"],
        }
        naples = {
            **paper,
            "institution": "University of Naples Federico II",
            "institution_id": "institution:naples",
            "institution_authors": ["Jane Doe"],
            "country": "Italy",
            "region": "Campania",
        }
        trento = {
            **paper,
            "institution": "University of Trento",
            "institution_id": "institution:trento",
            "institution_authors": ["John Roe"],
            "country": "Italy",
            "region": "Trentino-Alto Adige/Südtirol",
        }

        add_public_detail_fields([paper], [naples, trento])

        self.assertEqual(
            [item["name"] for item in paper["affiliations"]],
            ["University of Naples Federico II", "University of Trento"],
        )
        self.assertEqual(
            [author["affiliation_indices"] for author in paper["authors"]],
            [[1], [2]],
        )
        self.assertTrue(naples["authors"][0]["is_current_marker_author"])
        self.assertFalse(naples["authors"][1]["is_current_marker_author"])
        self.assertFalse(trento["authors"][0]["is_current_marker_author"])
        self.assertTrue(trento["authors"][1]["is_current_marker_author"])

    def test_paper_level_affiliation_does_not_fabricate_author_mapping(self):
        paper = {
            "title": "Manual paper",
            "year": 2021,
            "authors": ["Unmapped Author"],
            "affiliations": ["Known University"],
        }

        add_public_detail_fields([paper], [])

        self.assertEqual(paper["affiliations"][0]["name"], "Known University")
        self.assertEqual(paper["authors"][0]["affiliation_indices"], [])
        self.assertFalse(paper["authors"][0]["is_current_marker_author"])

    def test_incremental_learning_regression_mapping(self):
        title = (
            "Incremental learning for the detection and classification "
            "of GAN-generated images"
        )
        paper = {
            "title": title,
            "year": 2019,
            "doi": "10.1109/wifs47025.2019.9035099",
            "authors": [
                "Marra, Francesco",
                "Saltori, Cristiano",
                "Boato, Giulia",
                "Luisa Verdoliva",
            ],
            "author_institution_affiliations": [
                {
                    "index": 1,
                    "institution_id": "institution:naples",
                    "institution": "University of Naples Federico II",
                    "authors": ["Francesco Marra", "Luisa Verdoliva"],
                },
                {
                    "index": 2,
                    "institution_id": "institution:trento",
                    "institution": "University of Trento",
                    "authors": ["Cristiano Saltori", "Giulia Boato"],
                },
            ],
        }
        naples = {
            **paper,
            "institution": "University of Naples Federico II",
            "institution_id": "institution:naples",
            "institution_authors": ["Francesco Marra", "Luisa Verdoliva"],
        }
        trento = {
            **paper,
            "institution": "University of Trento",
            "institution_id": "institution:trento",
            "institution_authors": ["Cristiano Saltori", "Giulia Boato"],
        }

        add_public_detail_fields([paper], [naples, trento])

        self.assertEqual(
            [author["affiliation_indices"] for author in paper["authors"]],
            [[1], [2], [2], [1]],
        )
        self.assertEqual(
            [
                author["name"]
                for author in naples["authors"]
                if author["is_current_marker_author"]
            ],
            ["Marra, Francesco", "Luisa Verdoliva"],
        )
        self.assertEqual(
            [
                author["name"]
                for author in trento["authors"]
                if author["is_current_marker_author"]
            ],
            ["Saltori, Cristiano", "Boato, Giulia"],
        )

    def test_frontend_renders_numbers_and_current_author_bold(self):
        helper = (
            Path(__file__).resolve().parents[1]
            / "web"
            / "paper_details_helpers.js"
        )
        node = Path(
            "/Users/meilinger/.cache/codex-runtimes/"
            "codex-primary-runtime/dependencies/node/bin/node"
        )
        script = """
const helpers = require(process.argv[1]);
const html = helpers.renderAuthors(
  [
    {name: "Jane Doe", affiliation_indices: [1, 2], is_current_marker_author: true},
    {name: "John Roe", affiliation_indices: [], is_current_marker_author: false},
  ],
  (value) => value,
  1,
);
process.stdout.write(JSON.stringify(html));
"""
        result = subprocess.run(
            [str(node), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)

        self.assertIn(">1,2</sup>", rendered)
        self.assertIn('<strong class="current-institution-author">', rendered)
        self.assertNotIn("John Roe<sup", rendered)

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
