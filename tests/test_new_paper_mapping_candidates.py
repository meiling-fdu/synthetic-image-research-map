import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_institutions import stable_institution_id
from scripts.curated_mappings import create_mapping_candidates, load_mappings
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)
from scripts.serve_admin import prepare_mapping_candidates


class NewPaperMappingCandidateTests(unittest.TestCase):
    def test_unreviewed_pdf_links_survive_pending_locations_without_markers(self):
        from scripts.curated_export import enforce_affiliation_source_precedence
        for mixed in (False, True):
            with self.subTest(mixed=mixed):
                paper = dict(paper_id="curated:new", title="New paper", year=2026,
                             authors=["Ada", "Ben"] if mixed else ["Ada"],
                             curation_status="needs_review", review_status="pending")
                pending = dict(paper_id="curated:new", institution="Example University",
                               institution_id="institution:example", institution_authors="Ada",
                               mapping_id="pending", mapping_status="needs_review",
                               raw_affiliation="Example University", provenance_source="https://example.org/paper.pdf")
                mappings = [pending]
                if mixed:
                    mappings.append(dict(pending, mapping_id="active", institution="Second University",
                                         institution_id="institution:second", institution_authors="Ben",
                                         mapping_status="active"))
                markers = []
                enforce_affiliation_source_precedence([paper], markers, mappings)
                self.assertEqual(markers, [])
                self.assertEqual(paper["curation_status"], "needs_review")
                self.assertTrue(paper["needs_review"])
                ada = next(a for a in paper["author_institution_indices"] if a["author"] == "Ada")
                self.assertEqual(ada["institution_ids"], ["institution:example"])
                self.assertTrue(ada["fallback"])
                self.assertEqual(paper["author_institution_affiliations"][0]["mapping_source"], "raw_affiliation")
                from scripts.export_public_preview import add_public_detail_fields
                add_public_detail_fields([paper], markers)
                self.assertTrue(all(author["affiliation_indices"] for author in paper["authors"]))
                self.assertEqual(paper["curation_status"], "needs_review")
                self.assertEqual(markers, [])

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
            institutions_path = Path(directory) / "institutions.csv"
            for path, columns in (
                (mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS),
                (reviews_path, INSTITUTION_LOCATION_REVIEW_COLUMNS),
            ):
                with path.open("w", encoding="utf-8", newline="") as handle:
                    csv.DictWriter(handle, fieldnames=columns).writeheader()
            with institutions_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=INSTITUTION_COLUMNS)
                writer.writeheader()
                writer.writerow({
                    **{column: "" for column in INSTITUTION_COLUMNS},
                    "institution_id": stable_institution_id("Unresolved Institute"),
                    "canonical_name": "Unresolved Institute",
                    "institution_type": "institute",
                    "institution_status": "active",
                    "public_display": "self",
                })
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
                institutions_path=institutions_path,
            )

            self.assertEqual(len(result["mappings"]), 1)
            stored = load_mappings(mappings_path)
            self.assertEqual(stored[0]["mapping_status"], "needs_review")
            self.assertEqual(stored[0]["institution_authors"], "Ada Researcher")


if __name__ == "__main__":
    unittest.main()
