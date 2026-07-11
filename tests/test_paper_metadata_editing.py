import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.curated_export import integrate_curated_records
from scripts.curated_papers import (
    CuratedPaperError,
    normalize_author_names,
    update_curated_paper,
)
from scripts.curated_schema import PAPERS_COLUMNS, PAPER_EXCLUSION_COLUMNS
from scripts.export_public_preview import normalize_entry_type
from scripts.paper_exclusions import (
    build_active_exclusion_index,
    record_is_excluded,
    upsert_active_exclusion,
)
from scripts.serve_admin import load_admin_data


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


def write_exclusions(path, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPER_EXCLUSION_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


class PaperMetadataEditingTests(unittest.TestCase):
    def test_admin_data_loading_resolves_identity_matches_to_paper_records(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            public_papers_path = directory / "public_preview_papers.json"
            public_map_path = directory / "public_preview_map_data.json"
            curated_papers_path = directory / "papers.csv"
            exclusions_path = directory / "paper_exclusions.csv"

            shared_title = "Source Generator Attribution via Inversion"
            public_papers_path.write_text(
                json.dumps(
                    [
                        {
                            "paper_id": "openalex:W-PUBLISHED",
                            "title": shared_title,
                            "year": 2025,
                            "authors": ["Published Author"],
                            "doi": "10.1000/published",
                            "openalex_url": "https://openalex.org/W-PUBLISHED",
                        },
                        {
                            "paper_id": "openalex:W-ARXIV",
                            "title": shared_title,
                            "year": 2025,
                            "authors": [{"display_name": "Preprint Author"}],
                            "doi": "10.48550/arxiv.2401.00001",
                            "openalex_url": "https://openalex.org/W-ARXIV",
                        },
                    ]
                ),
                encoding="utf-8",
            )
            public_map_path.write_text("[]", encoding="utf-8")
            write_papers(
                curated_papers_path,
                [
                    curated_row(
                        paper_id="openalex:W-ARXIV",
                        title=shared_title,
                        year="2025",
                        authors='[{"display_name":"Preprint Author"}]',
                        doi="10.48550/arxiv.2401.00001",
                        openalex_url="https://openalex.org/W-ARXIV",
                    )
                ],
            )
            write_exclusions(exclusions_path)

            with (
                patch("scripts.serve_admin.PUBLIC_PAPERS_PATH", public_papers_path),
                patch("scripts.serve_admin.PUBLIC_MAP_PATH", public_map_path),
            ):
                papers, admin_data = load_admin_data(
                    exclusions_path=exclusions_path,
                    curated_papers_path=curated_papers_path,
                )

            self.assertEqual(len(papers), 2)
            self.assertTrue(all(isinstance(record, dict) for record in papers))
            papers_by_paper_id = {record["paper_id"]: record for record in papers}
            self.assertEqual(len(papers_by_paper_id), 2)
            self.assertTrue(
                papers_by_paper_id["openalex:W-ARXIV"]["is_in_curated_papers"]
            )
            self.assertFalse(
                papers_by_paper_id["openalex:W-PUBLISHED"]["is_in_curated_papers"]
            )
            self.assertEqual(len(admin_data["papers_by_id"]), 2)

    def test_author_normalization_accepts_strings_objects_and_json(self):
        cases = (
            ("Alice; Bob", ["Alice", "Bob"]),
            (["Alice", "Bob"], ["Alice", "Bob"]),
            ([{"name": "Alice"}, {"name": "Bob"}], ["Alice", "Bob"]),
            ([{"display_name": "Alice"}, {"display_name": "Bob"}], ["Alice", "Bob"]),
            ('[{"name":"Alice"},{"display_name":"Bob"}]', ["Alice", "Bob"]),
            ('{"display_name":"Alice"}', ["Alice"]),
            (None, []),
            ("", []),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(normalize_author_names(value), expected)

    def test_admin_update_serializes_object_authors_to_canonical_csv_text(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "papers.csv"
            original = curated_row()
            write_papers(path, [original])

            update_curated_paper(
                original,
                {**original, "authors": [{"name": "Alice"}, {"display_name": "Bob"}]},
                preview_records=[],
                path=path,
            )

            with path.open(encoding="utf-8", newline="") as handle:
                saved = next(csv.DictReader(handle))
            self.assertEqual(saved["authors"], "Alice; Bob")
            self.assertNotIn("[object Object]", saved["authors"])

    def test_excluding_one_same_title_record_does_not_exclude_the_other(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "paper_exclusions.csv"
            write_exclusions(path)
            published = curated_row(
                paper_id="openalex:W-PUBLISHED",
                title="Source Generator Attribution via Inversion",
                doi="10.1000/published",
                openalex_url="https://openalex.org/W-PUBLISHED",
                venue="Published Venue",
            )
            preprint = curated_row(
                paper_id="openalex:W-ARXIV",
                title=published["title"],
                doi="10.48550/arxiv.2401.00001",
                openalex_url="https://openalex.org/W-ARXIV",
                venue="arXiv",
            )

            upsert_active_exclusion(preprint, "duplicate", "Duplicate preprint", path)

            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            index = build_active_exclusion_index(rows)
            self.assertEqual(len(rows), 1)
            self.assertTrue(record_is_excluded(preprint, index))
            self.assertFalse(record_is_excluded(published, index))

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
