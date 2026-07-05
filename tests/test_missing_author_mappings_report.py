import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.report_missing_author_mappings import CSV_COLUMNS, main, priority_key


class MissingAuthorMappingsReportTests(unittest.TestCase):
    def write_json(self, path, records):
        path.write_text(
            json.dumps({"metadata": {}, "records": records}),
            encoding="utf-8",
        )

    def write_csv(self, path, fieldnames, rows=()):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def test_complete_partial_and_zero_reports_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            papers_path = root / "papers.json"
            map_path = root / "map.json"
            curated_path = root / "curated.csv"
            mappings_path = root / "mappings.csv"
            csv_output = root / "report.csv"
            markdown_output = root / "report.md"
            missing_key_path = root / "missing-key-papers.csv"

            self.write_json(
                papers_path,
                [
                    {
                        "paper_id": "paper:complete",
                        "title": "Complete Paper",
                        "year": 2022,
                        "authors": [
                            {"name": "Ada", "affiliation_indices": [1]},
                            {"name": "Ben", "affiliation_indices": [1]},
                        ],
                    },
                    {
                        "paper_id": "paper:partial",
                        "title": "Partial Paper",
                        "publication_year": 2024,
                        "authors": [
                            {"name": "Cora", "affiliation_indices": [1]},
                            {"name": "Dino"},
                        ],
                    },
                    {
                        "paper_id": "paper:zero",
                        "title": "Zero Paper",
                        "authors": [{"name": "Eve"}],
                    },
                ],
            )
            self.write_json(
                map_path,
                [
                    {"id": "marker:1", "related_paper_id": "paper:complete"},
                    {"id": "marker:2", "related_paper_id": "paper:complete"},
                    {"id": "marker:3", "related_paper_id": "paper:partial"},
                ],
            )
            self.write_csv(
                curated_path,
                ["paper_id", "title", "year"],
                [{"paper_id": "paper:complete", "title": "Complete Paper", "year": "2022"}],
            )
            self.write_csv(
                mappings_path,
                [
                    "paper_id",
                    "mapping_status",
                    "institution",
                    "institution_authors",
                    "raw_affiliation",
                ],
                [
                    {
                        "paper_id": "paper:partial",
                        "mapping_status": "active",
                        "institution": "Example University",
                        "institution_authors": "Dino Example",
                        "raw_affiliation": "Department, Example University",
                    }
                ],
            )

            arguments = [
                "--papers",
                str(papers_path),
                "--map-data",
                str(map_path),
                "--curated-papers",
                str(curated_path),
                "--mappings",
                str(mappings_path),
                "--key-papers",
                str(missing_key_path),
                "--csv-output",
                str(csv_output),
                "--markdown-output",
                str(markdown_output),
            ]
            self.assertEqual(main(arguments), 0)
            first_csv = csv_output.read_bytes()
            first_markdown = markdown_output.read_bytes()
            self.assertEqual(main(arguments), 0)
            self.assertEqual(csv_output.read_bytes(), first_csv)
            self.assertEqual(markdown_output.read_bytes(), first_markdown)

            with csv_output.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
                self.assertEqual(tuple(rows[0]), CSV_COLUMNS)
            self.assertEqual(
                [row["mapping_status"] for row in rows],
                ["zero", "partial", "complete"],
            )
            self.assertEqual(rows[0]["missing_author_names"], "Eve")
            self.assertEqual(rows[1]["mapped_authors"], "1")
            self.assertEqual(rows[1]["missing_authors"], "1")
            self.assertEqual(rows[1]["priority"], "normal")
            self.assertEqual(rows[1]["triage_status"], "likely_auto_fixable")
            self.assertEqual(
                rows[1]["suggested_author_matches"],
                "Dino → Dino Example",
            )
            self.assertEqual(
                rows[1]["known_canonical_institutions"],
                "Example University",
            )
            self.assertEqual(
                rows[1]["raw_affiliation_evidence"],
                "Department, Example University",
            )
            self.assertEqual(rows[2]["marker_count"], "2")
            self.assertEqual(rows[2]["is_curated_paper"], "true")

            markdown = markdown_output.read_text(encoding="utf-8")
            self.assertIn("| Complete mappings | 1 |", markdown)
            self.assertIn("| Partial mappings | 1 |", markdown)
            self.assertIn("| Zero mappings | 1 |", markdown)
            self.assertIn("| Total missing author links | 2 |", markdown)
            self.assertIn("## Zero-Mapping Papers", markdown)
            self.assertIn("## Partial-Mapping Papers", markdown)

    def test_priority_sort_uses_status_missing_key_and_year(self):
        rows = [
            {"mapping_status": "complete", "missing_authors": 0, "title": "Complete"},
            {"mapping_status": "partial", "missing_authors": 9, "title": "Partial"},
            {
                "mapping_status": "zero",
                "missing_authors": 1,
                "is_key_paper": False,
                "year": 2026,
                "title": "Newest",
            },
            {
                "mapping_status": "zero",
                "missing_authors": 1,
                "is_key_paper": True,
                "year": 2020,
                "title": "Key",
            },
            {
                "mapping_status": "zero",
                "missing_authors": 2,
                "is_key_paper": False,
                "year": 2019,
                "title": "Most missing",
            },
        ]

        self.assertEqual(
            [row["title"] for row in sorted(rows, key=priority_key)],
            ["Most missing", "Key", "Newest", "Partial", "Complete"],
        )


if __name__ == "__main__":
    unittest.main()
