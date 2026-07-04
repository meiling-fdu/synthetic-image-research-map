import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_export import integrate_curated_records
from scripts.curated_papers import (
    CuratedPaperError,
    update_curated_paper,
)
from scripts.curated_schema import PAPERS_COLUMNS
from scripts.export_public_preview import normalize_entry_type


def curated_row(**overrides):
    row = {column: "" for column in PAPERS_COLUMNS}
    row.update(
        {
            "paper_id": "curated:survey",
            "title": "A Principled Survey",
            "year": "2026",
            "authors": "Author One; Author Two",
            "doi": "10.1000/survey",
            "paper_url": "https://doi.org/10.1000/survey",
            "publication_type": "preprint",
            "task": "source_attribution",
            "subtask": "source_identification",
            "scope_status": "in_scope",
            "source_database": "openalex",
            "metadata_source": "openalex",
            "curation_status": "corrected_by_admin",
            "review_status": "reviewed",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "entry_type": "method",
        }
    )
    row.update(overrides)
    return row


def write_papers(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPERS_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


class PaperMetadataEditingTests(unittest.TestCase):
    def test_admin_update_persists_normalized_entry_type_to_curated_source(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "papers.csv"
            original = curated_row()
            write_papers(path, [original])

            updated = update_curated_paper(
                original,
                {**original, "entry_type": "  SuRvEy  "},
                preview_records=[],
                path=path,
            )

            with path.open(encoding="utf-8", newline="") as handle:
                saved = next(csv.DictReader(handle))
            self.assertEqual(updated["entry_type"], "survey")
            self.assertEqual(saved["entry_type"], "survey")
            self.assertEqual(saved["authors"], original["authors"])
            self.assertEqual(saved["paper_url"], original["paper_url"])

    def test_admin_update_rejects_empty_or_unknown_entry_type(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "papers.csv"
            original = curated_row()
            write_papers(path, [original])

            for invalid in ("", "tutorial"):
                with self.subTest(entry_type=invalid):
                    with self.assertRaises(CuratedPaperError):
                        update_curated_paper(
                            original,
                            {**original, "entry_type": invalid},
                            preview_records=[],
                            path=path,
                        )

    def test_export_propagates_entry_type_without_changing_coverage(self):
        public_paper = {
            "paper_id": "openalex:W1",
            "title": "A Principled Survey",
            "year": 2026,
            "publication_year": 2026,
            "authors": ["Author One", "Author Two"],
            "doi": "10.1000/survey",
            "paper_url": "https://doi.org/10.1000/survey",
            "task": "source_attribution",
            "subtask": "source_identification",
            "entry_type": "method",
            "review_status": "reviewed",
        }
        public_marker = {
            **public_paper,
            "id": "marker:one",
            "institution": "Example University",
            "institution_authors": ["Author One", "Author Two"],
            "latitude": 43.3188,
            "longitude": 11.3308,
        }

        papers, markers, _reviews, _summary = integrate_curated_records(
            [public_paper],
            [public_marker],
            [curated_row(entry_type="survey")],
            [],
        )

        self.assertEqual(len(papers), 1)
        self.assertEqual(len(markers), 1)
        self.assertEqual(papers[0]["entry_type"], "survey")
        self.assertEqual(markers[0]["entry_type"], "survey")
        self.assertEqual(
            (markers[0]["latitude"], markers[0]["longitude"]),
            (43.3188, 11.3308),
        )
        self.assertEqual(
            markers[0]["institution_authors"],
            ["Author One", "Author Two"],
        )
        self.assertEqual(
            normalize_entry_type(papers[0]),
            "survey",
        )


if __name__ == "__main__":
    unittest.main()
