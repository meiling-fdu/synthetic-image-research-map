import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_mappings import create_mapping_candidates, load_mappings
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)
from scripts.serve_admin import prepare_mapping_candidates


class NewPaperMappingCandidateTests(unittest.TestCase):
    def setUp(self):
        self.paper = {
            "title": "Mapping candidate test",
            "year": "2026",
            "authors": "Ada Researcher; Ben Researcher",
            "openalex_url": "https://openalex.org/W1",
            "source_database": "openalex",
        }
        self.locations = [
            {
                "institution": "Canonical University",
                "normalized_institution": "canonical university",
            }
        ]

    def test_openalex_candidate_prefills_canonical_institution(self):
        candidates, warnings = prepare_mapping_candidates(
            self.paper,
            [
                {
                    "institution": "Canonical University",
                    "institution_authors": ["Ada Researcher"],
                    "author_order": ["first"],
                    "raw_affiliations": ["Canonical University, Rome"],
                    "openalex_institution_id": "https://openalex.org/I1",
                    "city": "Rome",
                    "country": "Italy",
                    "latitude": 41.9,
                    "longitude": 12.5,
                    "provenance_source": "OpenAlex authorships",
                }
            ],
            institution_locations=self.locations,
            institution_aliases=[],
        )

        self.assertEqual(warnings, [])
        self.assertEqual(candidates[0]["institution"], "Canonical University")
        self.assertEqual(candidates[0]["mapping_status"], "active")
        self.assertEqual(candidates[0]["institution_latitude"], "41.9")
        self.assertEqual(
            candidates[0]["openalex_institution_id"],
            "https://openalex.org/I1",
        )

    def test_openalex_missing_institutions_creates_paper_warning(self):
        candidates, warnings = prepare_mapping_candidates(
            self.paper,
            [],
            institution_locations=self.locations,
            institution_aliases=[],
        )

        self.assertEqual(candidates, [])
        self.assertTrue(any("Missing author–institution mapping" in item for item in warnings))

    def test_manual_affiliation_creates_needs_review_candidate(self):
        candidates, _warnings = prepare_mapping_candidates(
            {**self.paper, "source_database": "manual", "openalex_url": ""},
            [
                {
                    "institution": "New Institute",
                    "institution_authors": ["Ada Researcher"],
                    "raw_affiliation": "Ada Researcher, New Institute",
                    "provenance_source": "Manual Add Paper affiliation input",
                }
            ],
            institution_locations=self.locations,
            institution_aliases=[],
        )

        self.assertEqual(candidates[0]["mapping_status"], "needs_review")
        self.assertEqual(candidates[0]["institution_authors"], "Ada Researcher")
        self.assertIn("Manual Add Paper", candidates[0]["provenance_source"])

    def test_manual_missing_affiliation_creates_diagnostic(self):
        candidates, warnings = prepare_mapping_candidates(
            {**self.paper, "source_database": "manual", "openalex_url": ""},
            None,
            institution_locations=self.locations,
            institution_aliases=[],
        )

        self.assertEqual(candidates, [])
        self.assertTrue(warnings)

    def test_candidate_is_persisted_in_author_institution_review_store(self):
        with tempfile.TemporaryDirectory() as directory:
            mappings_path = Path(directory) / "mappings.csv"
            reviews_path = Path(directory) / "reviews.csv"
            for path, columns in (
                (mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS),
                (reviews_path, INSTITUTION_LOCATION_REVIEW_COLUMNS),
            ):
                with path.open("w", encoding="utf-8", newline="") as handle:
                    csv.DictWriter(handle, fieldnames=columns).writeheader()
            paper = {
                "paper_id": "curated:test",
                "title": "Persist candidate",
                "year": "2026",
                "openalex_url": "https://openalex.org/W1",
            }
            result = create_mapping_candidates(
                paper,
                [
                    {
                        "institution": "Unresolved Institute",
                        "institution_authors": "Ada Researcher",
                        "raw_affiliation": "Ada, Unresolved Institute",
                        "evidence_source": "OpenAlex authorships",
                        "mapping_status": "needs_review",
                        "review_note": "Review imported evidence.",
                    }
                ],
                map_records=[],
                mappings_path=mappings_path,
                location_review_path=reviews_path,
            )

            self.assertEqual(len(result["mappings"]), 1)
            stored = load_mappings(mappings_path)
            self.assertEqual(stored[0]["mapping_status"], "needs_review")
            self.assertEqual(stored[0]["institution_authors"], "Ada Researcher")


if __name__ == "__main__":
    unittest.main()
