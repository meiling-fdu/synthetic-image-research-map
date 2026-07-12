import unittest
from pathlib import Path

from scripts.admin_review_queues import (
    build_public_visibility_index,
    public_visibility_status,
)


REPOSITORY = Path(__file__).resolve().parent.parent


def paper(**overrides):
    row = {
        "title": "Published paper",
        "year": "2025",
        "doi": "10.1000/published",
        "openalex_url": "https://openalex.org/W1",
    }
    row.update(overrides)
    return row


class AdminReviewVisibilityTests(unittest.TestCase):
    def setUp(self):
        self.public_index = build_public_visibility_index([paper()], [])

    def status(self, row, merges=()):
        return public_visibility_status(row, self.public_index, merges)

    def test_unresolved_review_record_can_already_be_visible(self):
        result = self.status(paper(review_status="unresolved"))
        self.assertEqual(result["public_visibility_status"], "visible_on_map")
        self.assertEqual(result["public_visibility_label"], "Visible on map")

    def test_excluded_suppressed_and_unpublished_candidate_are_not_inferred_visible(self):
        cases = [
            paper(title="Excluded paper", doi="10.1000/excluded", openalex_url="https://openalex.org/W2", excluded_from_public_preview="true"),
            paper(title="Suppressed paper", doi="10.1000/suppressed", openalex_url="https://openalex.org/W3", suppression_reason="resolved"),
            paper(title="Candidate paper", doi="10.1000/candidate", openalex_url="https://openalex.org/W4", candidate_status="ready"),
        ]
        for row in cases:
            with self.subTest(row=row):
                self.assertEqual(
                    self.status(row)["public_visibility_status"],
                    "not_visible_on_map",
                )

    def test_duplicate_visible_through_confirmed_canonical_paper(self):
        merge = {
            "status": "confirmed_duplicate",
            "is_active": "true",
            "duplicate_title": "Preprint paper",
            "duplicate_year": "2024",
            "duplicate_doi": "10.1000/preprint",
            "canonical_title": "Published paper",
            "canonical_year": "2025",
            "canonical_doi": "10.1000/published",
            "canonical_openalex_url": "https://openalex.org/W1",
        }
        result = self.status(
            {"title": "Preprint paper", "year": "2024", "doi": "10.1000/preprint"},
            [merge],
        )
        self.assertEqual(
            result["public_visibility_status"],
            "visible_through_canonical_paper",
        )

    def test_record_without_resolvable_identity_is_explicit(self):
        result = self.status({"review_status": "unresolved"})
        self.assertEqual(result["public_visibility_status"], "identity_unresolved")
        self.assertEqual(result["public_visibility_label"], "Identity unresolved")

    def test_frontend_renders_status_in_rows_and_details_without_stale_selection(self):
        source = (REPOSITORY / "web/admin.js").read_text(encoding="utf-8")
        html = (REPOSITORY / "web/admin.html").read_text(encoding="utf-8")
        self.assertIn('row.public_visibility_label || "Not visible on map"', source)
        self.assertIn('["Public visibility", row.public_visibility_label', source)
        self.assertEqual(html.count("<th>Public visibility</th>"), 4)
        self.assertIn("body.replaceChildren();", source)
        self.assertIn("!visibleKeys.has(state.selectedReviewKeys[name])", source)
        self.assertIn("clearReviewDetail(name);", source)
        self.assertIn("state.reviewQueues[name] = payload.data || {};", source)


if __name__ == "__main__":
    unittest.main()
