import unittest

from scripts.report_missing_institution_coordinates import build_audit_rows


def institution(identifier, name):
    return {
        "institution_id": identifier,
        "canonical_name": name,
        "institution_status": "active",
    }


def mapping(identifier, paper_id, title):
    return {
        "institution_id": identifier,
        "paper_id": paper_id,
        "title": title,
        "mapping_status": "active",
    }


class MissingInstitutionCoordinatesReportTests(unittest.TestCase):
    def test_public_missing_coordinate_requires_actionable_review(self):
        rows, violations = build_audit_rows(
            [institution("institution:public", "Public Lab")],
            [],
            [mapping("institution:public", "paper:one", "One")],
            [],
            [],
        )
        self.assertEqual(rows[0]["actionability_class"], "C_data_model_inconsistency")
        self.assertEqual(violations, ["institution:public Public Lab"])

        review = {
            "institution_id": "institution:public",
            "related_paper_id": "paper:one",
            "review_status": "pending_review",
            "location_status": "needs_coordinate_review",
            "coordinate_status": "missing",
        }
        rows, violations = build_audit_rows(
            [institution("institution:public", "Public Lab")],
            [],
            [mapping("institution:public", "paper:one", "One")],
            [review],
            [],
        )
        self.assertEqual(rows[0]["actionability_class"], "A_must_be_actionable")
        self.assertEqual(violations, [])

    def test_durable_exclusion_is_explicit_non_actionable_suppression(self):
        excluded_mapping = mapping("institution:hidden", "paper:hidden", "Hidden")
        exclusion = {
            "paper_id": "paper:hidden",
            "title": "Hidden",
            "reason": "out_of_scope",
            "is_active": "true",
        }
        rows, violations = build_audit_rows(
            [institution("institution:hidden", "Hidden Lab")],
            [],
            [excluded_mapping],
            [],
            [exclusion],
        )
        self.assertEqual(rows[0]["tier"], "B_referenced_non_public")
        self.assertEqual(rows[0]["actionability_class"], "B_explicitly_non_actionable")
        self.assertIn("out_of_scope", rows[0]["queue_reason"])
        self.assertEqual(violations, [])

    def test_current_repository_has_no_public_queue_invariant_violation(self):
        from scripts.report_missing_institution_coordinates import CURATED, read_csv

        _rows, violations = build_audit_rows(
            read_csv(CURATED / "institutions.csv"),
            read_csv(CURATED / "institution_locations.csv"),
            read_csv(CURATED / "author_institution_mappings.csv"),
            read_csv(CURATED / "institution_location_review.csv"),
            read_csv(CURATED / "paper_exclusions.csv"),
        )
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
