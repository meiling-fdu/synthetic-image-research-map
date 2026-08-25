import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_papers import (
    AmbiguousPaperIdentityError,
    existing_canonical_match,
)
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    PAPER_EXCLUSION_COLUMNS,
    PAPERS_COLUMNS,
)
from scripts.reconcile_duplicate_papers import consolidate


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def row(fields, **values):
    return {field: values.get(field, "") for field in fields}


class DuplicatePaperReconciliationTests(unittest.TestCase):
    def test_consolidates_doi_title_and_reassigns_references_idempotently(self):
        with tempfile.TemporaryDirectory() as directory:
            curated = Path(directory)
            papers = curated / "papers.csv"
            canonical = row(
                PAPERS_COLUMNS, paper_id="paper:canonical", title="Exact Paper",
                year="2025", authors="Ada; Ben", doi="10.1000/exact",
                publication_type="conference", task="detection",
                scope_status="in_scope", source_database="manual",
                metadata_source="manual", curation_status="confirmed",
                review_status="reviewed", paper_categories="method",
                created_at="2026-01-02T00:00:00Z",
            )
            duplicate = row(
                PAPERS_COLUMNS, paper_id="paper:retired", title="Exact Paper",
                year="2025", authors="Ada, Ben, Cora",
                doi="https://doi.org/10.1000/EXACT", abstract="Best abstract",
                publication_type="conference", task="detection",
                scope_status="in_scope", source_database="openalex",
                metadata_source="openalex", curation_status="confirmed",
                review_status="reviewed", paper_categories="dataset",
                created_at="2026-01-01T00:00:00Z",
            )
            write_csv(papers, PAPERS_COLUMNS, [canonical, duplicate])
            mapping = row(
                AUTHOR_INSTITUTION_MAPPING_COLUMNS,
                mapping_id="mapping:one", paper_id="paper:retired",
                title="Exact Paper", year="2025", doi="10.1000/exact",
            )
            write_csv(
                curated / "author_institution_mappings.csv",
                AUTHOR_INSTITUTION_MAPPING_COLUMNS,
                [mapping],
            )
            write_csv(
                curated / "paper_exclusions.csv",
                PAPER_EXCLUSION_COLUMNS,
                [row(
                    PAPER_EXCLUSION_COLUMNS,
                    exclusion_id="exclusion:one", paper_id="paper:retired",
                    title="Exact Paper", year="2025", doi="10.1000/exact",
                    reason="out_of_scope", is_active="true",
                )],
            )
            first = consolidate(
                "paper:canonical", "paper:retired",
                papers_path=papers, curated_dir=curated,
            )
            second = consolidate(
                "paper:canonical", "paper:retired",
                papers_path=papers, curated_dir=curated,
            )
            with papers.open(encoding="utf-8", newline="") as handle:
                saved = list(csv.DictReader(handle))
            self.assertTrue(first["changed"])
            self.assertFalse(second["changed"])
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0]["paper_id"], "paper:canonical")
            self.assertEqual(saved[0]["authors"], "Ada; Ben; Cora")
            self.assertEqual(saved[0]["abstract"], "Best abstract")
            self.assertEqual(saved[0]["paper_categories"], "method; dataset")
            with (curated / "author_institution_mappings.csv").open(encoding="utf-8", newline="") as handle:
                self.assertEqual(next(csv.DictReader(handle))["paper_id"], "paper:canonical")
            with (curated / "paper_exclusions.csv").open(encoding="utf-8", newline="") as handle:
                exclusion = next(csv.DictReader(handle))
            self.assertEqual(exclusion["paper_id"], "paper:canonical")
            self.assertEqual(exclusion["is_active"], "true")

    def test_ingestion_reuses_exact_identity_and_leaves_ambiguity_unresolved(self):
        existing = [{"paper_id": "paper:one", "title": "Known", "year": "2025", "doi": "10.1/known"}]
        self.assertEqual(
            existing_canonical_match(
                {"title": "Different source title", "year": "2026", "doi": "https://doi.org/10.1/KNOWN"},
                existing,
            )["paper_id"],
            "paper:one",
        )
        ambiguous = [
            {"paper_id": "paper:one", "title": "Same", "year": "2025"},
            {"paper_id": "paper:two", "title": "Same", "year": "2025"},
        ]
        with self.assertRaises(AmbiguousPaperIdentityError):
            existing_canonical_match({"title": "Same", "year": "2025"}, ambiguous)
        self.assertIsNone(
            existing_canonical_match(
                {"title": "Same", "year": "2025", "doi": "10.1/new"},
                [{"paper_id": "paper:old", "title": "Same", "year": "2025", "doi": "10.1/old"}],
            )
        )


if __name__ == "__main__":
    unittest.main()
