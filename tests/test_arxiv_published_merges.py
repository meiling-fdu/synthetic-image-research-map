import csv
import json
import unittest
from pathlib import Path

from scripts.audit_arxiv_published_duplicates import audit_duplicates, audit_input_records
from scripts.paper_version_merges import (
    apply_confirmed_version_merges,
    read_paper_version_merges,
)
from scripts.validate_public_preview import validate_confirmed_version_merges


ROOT = Path(__file__).resolve().parent.parent
PAPERS_PATH = ROOT / "web/data/public_preview_papers.json"
MAP_PATH = ROOT / "web/data/public_preview_map_data.json"
MERGES_PATH = ROOT / "data/curated/paper_version_merges.csv"


def records(path):
    return json.loads(path.read_text(encoding="utf-8"))["records"]


class ArxivPublishedMergeTests(unittest.TestCase):
    def test_wildfake_arxiv_published_duplicate_merged(self):
        wildfake = [
            record
            for record in records(PAPERS_PATH)
            if "wildfake" in record.get("title", "").casefold()
        ]

        self.assertEqual(len(wildfake), 1)
        paper = wildfake[0]
        self.assertEqual(
            paper["title"],
            "WildFake: A Large-Scale and Hierarchical Dataset for "
            "AI-Generated Images Detection",
        )
        self.assertEqual(paper["publication_year"], 2025)
        self.assertIn("AAAI", paper["venue"])
        self.assertEqual(paper["doi"], "10.1609/aaai.v39i4.32363")
        self.assertEqual(paper["arxiv_id"], "2402.11843")
        self.assertEqual(
            paper["arxiv_url"], "https://arxiv.org/abs/2402.11843"
        )

    def test_duplicate_arxiv_record_excluded_from_map(self):
        wildfake = [
            record
            for record in records(MAP_PATH)
            if "wildfake" in record.get("title", "").casefold()
        ]

        self.assertEqual(len(wildfake), 2)
        self.assertEqual(
            {record["institution"] for record in wildfake},
            {"Ant Group", "Shanghai Jiao Tong University"},
        )
        self.assertTrue(all(record["publication_year"] == 2025 for record in wildfake))
        self.assertTrue(all(record["arxiv_id"] == "2402.11843" for record in wildfake))
        self.assertFalse(
            any("Challenging Dataset" in record["title"] for record in wildfake)
        )

    def test_duplicate_merge_preserves_metadata_and_author_order(self):
        canonical = {
            "title": "Published title",
            "year": 2025,
            "publication_year": 2025,
            "venue": "Conference",
            "doi": "10.1000/formal",
            "openalex_url": "https://openalex.org/W1",
            "authors": ["First Author", "Second Author"],
            "abstract": "",
        }
        duplicate = {
            "title": "Preprint title",
            "year": 2024,
            "publication_year": 2024,
            "venue": "arXiv",
            "doi": "10.48550/arxiv.1234.56789",
            "openalex_url": "https://openalex.org/W2",
            "arxiv_id": "1234.56789",
            "arxiv_url": "https://arxiv.org/abs/1234.56789",
            "authors": ["Second Author", "First Author"],
            "abstract": "Preprint abstract",
        }
        merge = {
            "canonical_title": canonical["title"],
            "canonical_year": "2025",
            "canonical_doi": canonical["doi"],
            "canonical_openalex_url": canonical["openalex_url"],
            "duplicate_title": duplicate["title"],
            "duplicate_year": "2024",
            "duplicate_doi": duplicate["doi"],
            "duplicate_arxiv_id": duplicate["arxiv_id"],
            "duplicate_arxiv_url": duplicate["arxiv_url"],
            "duplicate_openalex_url": duplicate["openalex_url"],
            "status": "confirmed_duplicate",
            "is_active": "true",
        }

        papers, _maps, summary = apply_confirmed_version_merges(
            [canonical, duplicate], [], [merge]
        )

        self.assertEqual(summary["confirmed_version_merges_applied"], 1)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["doi"], "10.1000/formal")
        self.assertEqual(papers[0]["openalex_url"], "https://openalex.org/W1")
        self.assertEqual(papers[0]["arxiv_id"], "1234.56789")
        self.assertEqual(papers[0]["abstract"], "Preprint abstract")
        self.assertEqual(
            papers[0]["merged_versions"][0]["openalex_url"],
            "https://openalex.org/W2",
        )
        self.assertEqual(
            papers[0]["merged_versions"][0]["doi"],
            "10.48550/arxiv.1234.56789",
        )
        self.assertEqual(
            papers[0]["authors"], ["First Author", "Second Author"]
        )

    def test_uncertain_duplicates_go_to_review(self):
        preprint = {
            "title": "A Similar Method for Synthetic Image Detection",
            "year": 2024,
            "venue": "arXiv",
            "publication_type": "preprint",
            "doi": "10.48550/arxiv.1234.00001",
            "openalex_url": "https://openalex.org/W100",
            "authors": [{"name": "Ada Example"}],
            "task": "detection",
            "subtask": "synthetic_image_detection",
        }
        formal = {
            "title": "A Similar Method for Synthetic Image Detection",
            "year": 2025,
            "venue": "Example Conference",
            "publication_type": "article",
            "doi": "10.1000/distinct",
            "openalex_url": "https://openalex.org/W200",
            "authors": [{"name": "Ada Example"}],
            "task": "detection",
            "subtask": "synthetic_image_detection",
        }

        report = audit_duplicates(audit_input_records([preprint, formal], []))

        self.assertEqual(len(report), 1)
        self.assertEqual(
            report[0]["recommended_action"], "needs_manual_review"
        )

    def test_merge_table_has_only_confirmed_reviewed_rows(self):
        with MERGES_PATH.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        self.assertGreaterEqual(len(rows), 3)
        self.assertTrue(
            all(row["status"] == "confirmed_duplicate" for row in rows)
        )
        self.assertEqual(len(read_paper_version_merges(MERGES_PATH)), len(rows))

    def test_validator_detects_confirmed_duplicate_leak(self):
        merge = read_paper_version_merges(MERGES_PATH)[0]
        leaked = {
            "title": merge["duplicate_title"],
            "year": int(merge["duplicate_year"]),
            "doi": merge["duplicate_doi"],
            "arxiv_id": merge["duplicate_arxiv_id"],
            "openalex_url": merge["duplicate_openalex_url"],
        }
        issues = []

        validate_confirmed_version_merges(
            [leaked], [merge], issues, paper_level=False
        )

        self.assertEqual(len(issues), 1)
        self.assertIn("confirmed duplicate", issues[0].message)


if __name__ == "__main__":
    unittest.main()
