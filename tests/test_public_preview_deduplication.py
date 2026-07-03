import json
import subprocess
import unittest
from pathlib import Path

from scripts.curated_export import _ordered_mapping_authors
from scripts.export_public_preview import (
    add_public_detail_fields,
    exclude_preprint_versions,
)
from scripts.refresh_public_preview import build_steps, parse_args
from scripts.validate_public_preview import validate_preprint_version_duplicates
from scripts.validate_public_preview import (
    is_bad_author_candidate,
    normalized_author_name,
    validate_paper_detail_schema,
    validate_paper_record,
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

        self.assertEqual(len(steps), 4)
        self.assertTrue(
            all("run_pipeline.py" not in " ".join(command) for command in commands)
        )
        self.assertIn("--preserve-existing", commands[0])
        self.assertNotIn("--max-records", commands[0])
        self.assertIn("report_public_preview.py", " ".join(commands[1]))
        self.assertIn("report_missing_author_mappings.py", " ".join(commands[2]))

    def test_default_search_refresh_has_no_implicit_processing_or_record_cap(self):
        args = parse_args(["--user-agent", "test refresh"])

        steps = build_steps(args)
        pipeline_command = steps[0].command
        export_command = steps[1].command

        self.assertIn("run_pipeline.py", " ".join(pipeline_command))
        self.assertNotIn("--limit", pipeline_command)
        self.assertIn("--preserve-existing", export_command)
        self.assertNotIn("--max-records", export_command)

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
        self.assertEqual(
            paper["author_affiliation_indices"][0]["source"], "unmapped"
        )
        self.assertFalse(
            paper["author_affiliation_indices"][0]["fallback"]
        )
        self.assertFalse(paper["authors"][0]["is_current_marker_author"])

    def test_curated_mapping_outranks_stale_raw_author_mapping(self):
        paper = {
            "title": "Admin mapping priority",
            "year": 2024,
            "authors": ["Ada Researcher"],
            "author_institution_affiliations": [
                {
                    "index": 1,
                    "institution": "Stale University",
                    "authors": ["Ada Researcher"],
                },
                {
                    "index": 2,
                    "institution": "Curated University",
                    "authors": ["Ada Researcher"],
                    "mapping_source": "curated_admin",
                    "mapping_fallback": False,
                },
            ],
        }

        add_public_detail_fields([paper], [])

        self.assertEqual(paper["authors"][0]["affiliation_indices"], [2])
        self.assertEqual(
            paper["author_affiliation_indices"][0]["source"],
            "curated_admin",
        )
        self.assertFalse(
            paper["author_affiliation_indices"][0]["fallback"]
        )

    def test_author_order_preserved_from_paper_metadata(self):
        paper = {
            "title": "Paper order wins",
            "year": 2024,
            "doi": "10.1000/paper-order",
            "authors": [
                "Author One",
                "Author Two",
                "Unmapped Author",
                "Author Three",
                "Author Four",
            ],
        }
        first_institution = {
            **paper,
            "institution": "First University",
            "institution_id": "institution:first",
            "institution_authors": [
                "Author One",
                "Author Three",
                "Mapping-only Author",
            ],
        }
        second_institution = {
            **paper,
            "institution": "Second University",
            "institution_id": "institution:second",
            "institution_authors": ["Author Two", "Author Four"],
        }

        add_public_detail_fields(
            [paper], [first_institution, second_institution]
        )

        self.assertEqual(
            [author["name"] for author in paper["authors"]],
            [
                "Author One",
                "Author Two",
                "Unmapped Author",
                "Author Three",
                "Author Four",
            ],
        )
        self.assertEqual(
            [
                author["affiliation_indices"]
                for author in paper["authors"]
            ],
            [[1], [2], [], [1], [2]],
        )

    def test_mapping_authors_are_fallback_when_paper_authors_are_missing(self):
        self.assertEqual(
            _ordered_mapping_authors([], ["Mapped One", "Mapped Two"]),
            ["Mapped One", "Mapped Two"],
        )
        paper = {
            "title": "Mapping-only author source",
            "year": 2024,
            "doi": "10.1000/mapping-only",
            "authors": [],
        }
        marker = {
            **paper,
            "institution": "Fallback University",
            "institution_id": "institution:fallback",
            "institution_authors": ["Mapped One", "Mapped Two"],
        }

        add_public_detail_fields([paper], [marker])

        self.assertEqual(
            [author["name"] for author in paper["authors"]],
            ["Mapped One", "Mapped Two"],
        )
        self.assertEqual(
            [
                author["affiliation_indices"]
                for author in paper["authors"]
            ],
            [[1], [1]],
        )

    def test_legacy_detail_fields_migrate_without_fabricated_indices(self):
        paper = {
            "title": "Legacy schema migration",
            "year": 2021,
            "doi": "10.1000/legacy",
            "authors": "Doe, Jane; John Roe",
            "affiliations": "Legacy Paper University",
        }
        marker = {
            **paper,
            "affiliations": [],
            "current_institution": "Legacy Marker University",
        }

        add_public_detail_fields([paper], [marker])

        self.assertEqual(
            [author["name"] for author in paper["authors"]],
            ["Doe, Jane", "John Roe"],
        )
        self.assertTrue(
            all(
                author["affiliation_indices"] == []
                for author in paper["authors"]
            )
        )
        self.assertEqual(
            [affiliation["name"] for affiliation in paper["affiliations"]],
            ["Legacy Paper University", "Legacy Marker University"],
        )
        self.assertIsInstance(marker["current_institution"], dict)
        self.assertEqual(
            marker["current_institution"]["name"],
            "Legacy Marker University",
        )

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

    def test_latent_recovery_mapping_uses_mapping_author_roster(self):
        title = (
            "Did You Use My GAN to Generate Fake? Post-hoc Attribution of "
            "GAN Generated Images via Latent Recovery"
        )
        paper = {
            "title": title,
            "year": 2022,
            "doi": "10.1109/ijcnn55064.2022.9892704",
            "authors": [
                "Syou Hirofumi, Kazuto Fukuchi, Youhei Akimoto, Jun Sakuma"
            ],
        }
        tsukuba = {
            **paper,
            "institution": "University of Tsukuba",
            "institution_id": "institution:tsukuba",
            "institution_authors": [
                "Syou Hirofumi",
                "Kazuto Fukuchi",
                "Youhei Akimoto",
                "Jun Sakuma",
            ],
        }
        riken = {
            **paper,
            "institution": "RIKEN Center for Advanced Intelligence Project",
            "institution_id": "institution:riken",
            "institution_authors": ["Jun Sakuma"],
        }

        add_public_detail_fields([paper], [tsukuba, riken])

        expected_indices = [[1], [1], [1], [1, 2]]
        self.assertEqual(
            [author["affiliation_indices"] for author in paper["authors"]],
            expected_indices,
        )
        self.assertTrue(
            all(
                not author["is_current_marker_author"]
                for author in paper["authors"]
            )
        )
        self.assertEqual(
            [
                author["is_current_marker_author"]
                for author in tsukuba["authors"]
            ],
            [True, True, True, True],
        )
        self.assertEqual(
            [
                author["is_current_marker_author"]
                for author in riken["authors"]
            ],
            [False, False, False, True],
        )

    def test_generated_previews_have_fewer_unsplit_mapped_author_lines(self):
        repository = Path(__file__).resolve().parents[1]
        target_title = (
            "Did You Use My GAN to Generate Fake? Post-hoc Attribution of "
            "GAN Generated Images via Latent Recovery"
        )
        limits = {
            "public_preview_map_data.json": 41,
            "public_preview_papers.json": 21,
        }
        for filename, maximum in limits.items():
            with (repository / "web" / "data" / filename).open(
                encoding="utf-8"
            ) as handle:
                records = json.load(handle)["records"]
            bad = [
                record for record in records
                if is_bad_author_candidate(record)
            ]
            self.assertLessEqual(len(bad), maximum, filename)
            self.assertNotIn(
                target_title,
                {record.get("title") for record in bad},
                filename,
            )

    def test_source_attribution_survey_author_order_regression(self):
        repository = Path(__file__).resolve().parents[1]
        title = "Source Attribution of AI-Generated Images: a Principled Survey"
        expected_names = [
            "Meiling Li",
            "Benedetta Tondi",
            "Pietro Bongini",
            "Zhenxing Qian",
            "Xinpeng Zhang",
            "Mauro Barni",
        ]
        expected_indices = [[1], [2], [2], [1], [1], [2]]

        for filename in (
            "public_preview_map_data.json",
            "public_preview_papers.json",
        ):
            with (repository / "web" / "data" / filename).open(
                encoding="utf-8"
            ) as handle:
                records = json.load(handle)["records"]
            matches = [
                record for record in records
                if record.get("title") == title
            ]
            self.assertTrue(matches, filename)
            for record in matches:
                names = [author["name"] for author in record["authors"]]
                self.assertEqual(names, expected_names, filename)
                self.assertNotIn("Xi Zhang", names, filename)
                self.assertLess(
                    names.index("Benedetta Tondi"),
                    names.index("Zhenxing Qian"),
                )
                self.assertLess(
                    names.index("Pietro Bongini"),
                    names.index("Zhenxing Qian"),
                )
                self.assertEqual(names[0], "Meiling Li")
                self.assertEqual(names[-1], "Mauro Barni")
                self.assertEqual(
                    [
                        author["affiliation_indices"]
                        for author in record["authors"]
                    ],
                    expected_indices,
                    filename,
                )
                active_names = [
                    author["name"]
                    for author in record["authors"]
                    if author["is_current_marker_author"]
                ]
                expected_active = {
                    "Fudan University": [
                        "Meiling Li",
                        "Zhenxing Qian",
                        "Xinpeng Zhang",
                    ],
                    "University of Siena": [
                        "Benedetta Tondi",
                        "Pietro Bongini",
                        "Mauro Barni",
                    ],
                    None: [],
                }
                self.assertEqual(
                    active_names,
                    expected_active[record.get("institution")],
                    filename,
                )

    def test_evoguard_curated_author_mapping_regression(self):
        repository = Path(__file__).resolve().parents[1]
        title = (
            "EvoGuard: An Extensible Agentic RL-based Framework for Practical "
            "and Evolving AI-Generated Image Detection"
        )
        expected = {
            "Chenyang Zhu": [1, 2],
            "Maorong Wang": [2],
            "Jun O. Liu": [2],
            "Ching-Chun Chang": [2],
            "Isao Echizen": [1, 2],
        }
        for filename in (
            "public_preview_map_data.json",
            "public_preview_papers.json",
        ):
            with (repository / "web" / "data" / filename).open(
                encoding="utf-8"
            ) as handle:
                records = json.load(handle)["records"]
            matches = [
                record for record in records if record.get("title") == title
            ]
            self.assertTrue(matches, filename)
            for record in matches:
                self.assertEqual(
                    {
                        author["name"]: author["affiliation_indices"]
                        for author in record["authors"]
                    },
                    expected,
                    filename,
                )
                self.assertEqual(
                    {
                        mapping["source"]
                        for mapping in record["author_affiliation_indices"]
                    },
                    {"curated_admin"},
                    filename,
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
const html = helpers.renderPaperAuthors(
  {authors: [
    {name: "Jane Doe", affiliation_indices: [1, 2], is_current_marker_author: true},
    {name: "John Roe", affiliation_indices: [], is_current_marker_author: false},
  ]},
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

    def test_validator_warns_for_missing_mapping_without_crashing(self):
        record = {
            "title": "Partially mapped",
            "authors": [
                {
                    "name": "Unmapped Author",
                    "affiliation_indices": [],
                    "is_current_marker_author": False,
                }
            ],
            "affiliations": [
                {
                    "index": 1,
                    "name": "Known University",
                    "institution_id": "institution:known",
                    "country": "",
                    "region": "",
                }
            ],
            "author_affiliation_indices": [
                {
                    "author": "Unmapped Author",
                    "indices": [],
                    "institution_ids": [],
                    "source": "unmapped",
                    "fallback": False,
                }
            ],
            "current_institution": None,
        }
        issues = []

        validate_paper_detail_schema(
            0, record, issues, marker_record=False
        )

        self.assertFalse(
            any(issue.level == "ERROR" for issue in issues)
        )
        validate_paper_record(0, record, issues)
        self.assertTrue(
            any(
                issue.level == "WARNING"
                and "no institution index" in issue.message
                for issue in issues
            )
        )

    def test_validator_rejects_invalid_mapping_indices_and_current_institution(self):
        record = {
            "title": "Invalid mapping",
            "authors": [
                {
                    "name": "Ada Researcher",
                    "affiliation_indices": [1, 1],
                    "is_current_marker_author": True,
                }
            ],
            "affiliations": [
                {
                    "index": 1,
                    "name": "",
                    "institution_id": "institution:one",
                    "country": "",
                    "region": "",
                }
            ],
            "author_affiliation_indices": [
                {
                    "author": "Ada Researcher",
                    "indices": [2],
                    "institution_ids": ["institution:two"],
                    "source": "raw_affiliation",
                    "fallback": False,
                }
            ],
            "current_institution": {
                "index": 1,
                "name": "Different University",
                "institution_id": "institution:different",
            },
        }
        issues = []

        validate_paper_detail_schema(
            0, record, issues, marker_record=True
        )

        messages = {issue.message for issue in issues}
        self.assertTrue(any("has no name" in message for message in messages))
        self.assertTrue(
            any("duplicate affiliation indices" in message for message in messages)
        )
        self.assertTrue(
            any("unknown affiliation index" in message for message in messages)
        )
        self.assertIn(
            "marker current institution does not match affiliation list",
            messages,
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
