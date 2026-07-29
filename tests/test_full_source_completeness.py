import unittest
from pathlib import Path

from scripts.full_source_completeness import SourceRow, audit_completeness, identity_keys


class FullSourceCompletenessTests(unittest.TestCase):
    def source(self, row, name="candidate"):
        return SourceRow(name, Path(f"data/{name}.csv"), row)

    def test_identity_normalizes_doi_openalex_and_arxiv_urls(self):
        left = identity_keys({
            "doi": "https://doi.org/10.1/ABC",
            "openalex_url": "https://openalex.org/W123",
            "arxiv_id": "2401.00001v2",
        })
        right = identity_keys({
            "doi": "10.1/abc",
            "openalex_id": "W123",
            "arxiv_url": "https://arxiv.org/abs/2401.00001",
        })
        self.assertEqual(left, right)

    def test_authoritative_exporter_input_is_accepted(self):
        rows = audit_completeness(
            [{"title": "Paper", "year": 2025, "doi": "10.1/a"}],
            [self.source({"title": "Paper", "year": 2025, "doi": "10.1/a"})],
            [],
        )
        self.assertEqual(rows[0]["status"], "restored_missing_source")

    def test_override_only_is_not_automatically_accepted(self):
        rows = audit_completeness(
            [{"title": "Paper", "year": 2025, "doi": "10.1/a"}],
            [],
            [self.source({"doi": "10.1/a"}, "override")],
        )
        self.assertEqual(rows[0]["status"], "ambiguous_manual_review")

    def test_different_identity_with_same_title_year_is_reported(self):
        rows = audit_completeness(
            [{"title": "Paper!", "year": 2025, "doi": "10.1/old"}],
            [self.source({"title": "Paper", "year": 2025, "doi": "10.1/new"})],
            [],
        )
        self.assertEqual(rows[0]["status"], "resolved_identity_mismatch")

    def test_active_durable_exception_can_preserve_record(self):
        rows = audit_completeness(
            [{"title": "Paper", "year": 2025, "doi": "10.1/a"}],
            [],
            [],
            [{
                "doi": "10.1/a",
                "status": "intentionally_preserved",
                "is_active": "true",
                "reason": "reviewed historical record",
            }],
        )
        self.assertEqual(rows[0]["status"], "intentionally_preserved")


if __name__ == "__main__":
    unittest.main()
