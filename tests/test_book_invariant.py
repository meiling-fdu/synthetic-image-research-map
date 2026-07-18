import csv
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.curated_export import _merge_curated_paper
from scripts.curated_papers import update_curated_paper, write_curated_papers
from scripts.curated_schema import PAPERS_COLUMNS
from scripts.export_public_preview import synchronize_publication_types
from scripts.migrate_book_invariant import audit_rows
from scripts.publication_types import (
    BOOK_INCOMPATIBLE_FIELDS,
    book_incompatibilities,
    normalize_book_record,
)
from scripts.validate_curated_database import validate_book_invariant
from scripts.validate_public_preview import validate_paper_record


def paper_row(**overrides):
    row = {field: "" for field in PAPERS_COLUMNS}
    row.update({
        "paper_id": "curated:book-test",
        "title": "A Book Chapter",
        "year": "2025",
        "authors": "Ada Author; Bob Writer",
        "venue": "Stale Conference",
        "venue_id": "venue:stale:main",
        "venue_name": "Stale Conference",
        "venue_acronym": "SC",
        "venue_type": "conference",
        "venue_track": "main",
        "raw_venue": "Proceedings of Stale Conference",
        "doi": "10.1000/book.chapter",
        "publication_type": "book",
        "entry_type": "method",
        "task": "detection",
        "scope_status": "in_scope",
        "source_database": "openalex",
        "metadata_source": "openalex",
        "curation_status": "manually_confirmed",
        "review_status": "reviewed",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    })
    row.update(overrides)
    return row


class BookInvariantTests(unittest.TestCase):
    def test_shared_normalizer_clears_only_book_incompatible_fields(self):
        source = paper_row()
        normalized = normalize_book_record(source)
        for field in BOOK_INCOMPATIBLE_FIELDS:
            if field in normalized:
                self.assertFalse(normalized[field], field)
        for field in ("paper_id", "title", "authors", "doi", "task"):
            self.assertEqual(normalized[field], source[field])

        conference = {**source, "publication_type": "conference"}
        self.assertEqual(normalize_book_record(conference), conference)

    def test_backend_update_normalizes_invalid_book_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.csv"
            existing = paper_row(
                publication_type="conference",
                venue="",
                venue_id="",
                venue_name="",
                venue_acronym="",
                venue_type="",
                venue_track="",
                raw_venue="",
            )
            write_curated_papers([existing], path)
            saved = update_curated_paper(
                existing,
                paper_row(),
                preview_records=[],
                path=path,
            )
            self.assertEqual(saved["publication_type"], "book")
            self.assertEqual(book_incompatibilities(saved), {})
            self.assertEqual(saved["paper_id"], existing["paper_id"])
            self.assertEqual(saved["authors"], existing["authors"])

    def test_write_failure_does_not_partially_change_curated_row(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.csv"
            existing = paper_row(publication_type="conference", entry_type="method")
            write_curated_papers([existing], path)
            before = path.read_bytes()
            with mock.patch(
                "scripts.curated_papers.write_curated_papers",
                side_effect=OSError("simulated write failure"),
            ):
                with self.assertRaises(OSError):
                    update_curated_paper(
                        existing, paper_row(), preview_records=[], path=path
                    )
            self.assertEqual(path.read_bytes(), before)

    def test_validator_reports_id_title_field_and_value(self):
        issues = []
        validate_book_invariant([paper_row()], issues)
        messages = "\n".join(issue.message for issue in issues)
        for expected in (
            "curated:book-test", "A Book Chapter", "venue='Stale Conference'",
            "entry_type='method'", "venue_track='main'",
        ):
            self.assertIn(expected, messages)

    def test_public_validator_rejects_defensively_stale_book_metadata(self):
        issues = []
        validate_paper_record(0, paper_row(), issues)
        messages = "\n".join(issue.message for issue in issues)
        self.assertIn("book has incompatible venue='Stale Conference'", messages)
        self.assertIn("book has incompatible entry_type='method'", messages)

    def test_curated_merge_and_public_synchronization_clean_after_merge(self):
        external = paper_row(paper_id="", publication_type="conference")
        curated = paper_row(
            venue="", venue_id="", venue_name="", venue_acronym="",
            venue_type="", venue_track="", raw_venue="", entry_type="",
        )
        _merge_curated_paper(external, curated)
        self.assertEqual(external["publication_type"], "book")
        self.assertEqual(book_incompatibilities(external), {})

        paper = paper_row()
        marker = {**paper, "id": "marker-1", "institution": "Example U"}
        unresolved = synchronize_publication_types([paper], [marker])
        self.assertEqual(unresolved, [])
        self.assertEqual(book_incompatibilities(paper), {})
        self.assertEqual(book_incompatibilities(marker), {})

    def test_migration_audits_and_preserves_identity(self):
        source = paper_row()
        migrated, report = audit_rows([source], apply=True)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["action_taken"], "cleared incompatible metadata")
        for field in ("paper_id", "doi", "title", "authors"):
            self.assertEqual(migrated[0][field], source[field])
        self.assertEqual(book_incompatibilities(migrated[0]), {})

    def test_repository_curated_and_public_books_satisfy_invariant(self):
        root = Path(__file__).resolve().parents[1]
        with (root / "data" / "curated" / "papers.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            curated = list(csv.DictReader(handle))
        self.assertTrue(any(row.get("publication_type") == "book" for row in curated))
        self.assertFalse(any(book_incompatibilities(row) for row in curated))

        import json
        for filename in (
            "public_preview_papers.json", "public_preview_map_data.json"
        ):
            payload = json.loads((root / "web" / "data" / filename).read_text())
            self.assertFalse(
                any(book_incompatibilities(row) for row in payload["records"]),
                filename,
            )


class BookFrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.admin = (root / "web" / "admin.js").read_text(encoding="utf-8")
        cls.app = (root / "web" / "app.js").read_text(encoding="utf-8")

    def test_admin_confirmation_cancel_and_existing_book_contract(self):
        for text in (
            "Changing this record to book will clear these incompatible values",
            "select.value = previousType",
            "clearBookIncompatibleFormFields()",
            'elements["metadata-entry-type"].disabled = isBook',
            'state.previousPublicationType = nextType',
        ):
            self.assertIn(text, self.admin)

    def test_frontend_venue_search_filter_detail_and_csv_are_defensive(self):
        for text in (
            "if (isBookRecord(record)) return \"\";",
            "(record) => isBookRecord(record) ? [] : [venueFilterValue(record)]",
            "const venueTerms = isBookRecord(record) ? []",
            "isBookRecord(record) ? \"\" : record.venue_track",
            "const venueRow = venueDisplayLabel(record)",
        ):
            self.assertIn(text, self.app)


if __name__ == "__main__":
    unittest.main()
