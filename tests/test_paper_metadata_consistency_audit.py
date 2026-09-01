import unittest

from scripts.audit_paper_metadata_consistency import (
    INTENTIONAL_TRANSFORMATION,
    audit,
)
from scripts.curated_export import _merge_curated_paper
from scripts.export_public_preview import (
    normalize_exported_paper_identifiers,
    synchronize_public_arxiv_metadata,
    synchronize_public_authors,
)


class PaperMetadataConsistencyAuditTests(unittest.TestCase):
    def test_identifier_boundary_normalizes_doi_and_arxiv(self):
        records = [{
            "doi": "https://doi.org/10.1000/Example",
            "arxiv_id": "https://arxiv.org/abs/2401.01234v2",
        }]

        normalize_exported_paper_identifiers(records)

        self.assertEqual(records[0]["doi"], "10.1000/example")
        self.assertEqual(records[0]["arxiv_id"], "2401.01234")

    def test_confirmed_year_clears_conflicting_candidate_date(self):
        paper = {
            "title": "Example",
            "year": 2023,
            "publication_year": 2023,
            "publication_date": "2023-11-20",
        }

        _merge_curated_paper(paper, {
            "curation_status": "confirmed",
            "year": 2024,
            "publication_year": 2024,
        })

        self.assertEqual(paper["publication_year"], 2024)
        self.assertEqual(paper["publication_date"], "")

    def test_map_only_arxiv_is_promoted_and_synchronized(self):
        paper = {"paper_id": "paper:1", "title": "Example", "year": 2024}
        markers = [{
            **paper,
            "institution_id": "institution:1",
            "arxiv_id": "2401.01234v3",
        }]

        conflicts = synchronize_public_arxiv_metadata([paper], markers)

        self.assertEqual(conflicts, [])
        self.assertEqual(paper["arxiv_id"], "2401.01234")
        self.assertEqual(markers[0]["arxiv_id"], "2401.01234")

    def test_marker_author_order_follows_canonical_paper(self):
        paper = {
            "paper_id": "paper:1", "title": "Example", "year": 2024,
            "authors": ["Ada Author", "Bob Writer"],
        }
        marker = {
            **paper,
            "institution_id": "institution:1",
            "authors": ["Bob Writer", "Ada Author"],
        }

        synchronize_public_authors([paper], [marker])

        self.assertEqual(marker["authors"], paper["authors"])

    def test_full_corpus_has_no_unexplained_metadata_inconsistency(self):
        rows, summary = audit()

        self.assertEqual(summary["papers_audited"], 582)
        self.assertEqual(summary["fields_per_paper"], 18)
        self.assertEqual(len(rows), 582 * 18)
        self.assertEqual(summary["true_inconsistencies"], 0)
        self.assertEqual(summary["legacy_fallback_risks"], 0)
        # Distinct paper–institution pairs; the marker count is one larger
        # because a reviewed relationship has two location markers.
        self.assertEqual(summary["public_paper_institution_relationships"], 1320)
        self.assertEqual(summary["map_markers"], 1321)
        self.assertEqual(summary["published_only_papers"], 520)
        self.assertEqual(summary["affiliation_audit_mismatches"], 0)
        self.assertEqual(summary["retired_institution_affiliation_leaks"], 0)

        mapping_normalizations = [
            row for row in rows
            if row["field"] == "authors"
            and row["classification"] == INTENTIONAL_TRANSFORMATION
            and row["pipeline_layer"]
            == "legacy curated authors→reviewed mapping roster"
        ]
        self.assertEqual(len(mapping_normalizations), 6)


if __name__ == "__main__":
    unittest.main()
