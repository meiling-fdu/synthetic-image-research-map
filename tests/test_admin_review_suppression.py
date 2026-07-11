import unittest

from scripts.admin_review_queues import suppress_resolved_records


def paper(**overrides):
    row = {
        "title": "A Bias-Free Training Paradigm for More General AI-generated Image Detection",
        "year": "2024",
        "doi": "10.1000/bias-free",
        "openalex_url": "https://openalex.org/W123",
    }
    row.update(overrides)
    return row


class AdminReviewSuppressionTests(unittest.TestCase):
    def test_active_mapping_suppresses_corresponding_confirm_item(self):
        candidate = paper(
            institution="University of Naples Federico II",
            institution_authors="Alice; Bob",
            recommended_action="confirm_marker",
        )
        mapping = paper(
            institution="University of Naples Federico II",
            institution_authors="Alice; Bob",
            mapping_status="active",
        )

        visible, hidden = suppress_resolved_records([candidate], mappings=[mapping])

        self.assertEqual(visible, [])
        self.assertEqual(hidden["resolved_by_active_curated_mapping"], 1)

    def test_same_authors_mapping_supersedes_incorrect_candidate_institution(self):
        candidate = paper(
            institution="Federico II University Hospital",
            institution_authors="Alice; Bob",
            recommended_action="confirm_marker",
        )
        corrected = paper(
            institution="University of Naples Federico II",
            institution_authors="Bob; Alice",
            mapping_status="active",
        )

        visible, hidden = suppress_resolved_records([candidate], mappings=[corrected])

        self.assertEqual(visible, [])
        self.assertEqual(hidden["superseded_by_active_curated_mapping"], 1)

    def test_active_durable_exclusion_suppresses_review_item(self):
        candidate = paper(institution="Example University")
        exclusion = paper(is_active="true")

        visible, hidden = suppress_resolved_records(
            [candidate], exclusions=[exclusion]
        )

        self.assertEqual(visible, [])
        self.assertEqual(hidden["resolved_by_durable_exclusion"], 1)

    def test_unrelated_candidate_institution_remains_visible(self):
        resolved = paper(
            institution="University of Naples Federico II",
            institution_authors="Alice; Bob",
            mapping_status="active",
        )
        unrelated = paper(
            institution="University of Salerno",
            institution_authors="Carol",
            recommended_action="confirm_marker",
        )

        visible, hidden = suppress_resolved_records([unrelated], mappings=[resolved])

        self.assertEqual(visible, [unrelated])
        self.assertEqual(hidden, {})

    def test_active_mapping_never_remains_an_actionable_confirm_item(self):
        mapping = paper(
            institution="University of Naples Federico II",
            institution_authors="Alice; Bob",
            mapping_status="active",
        )
        candidates = [
            paper(
                institution="University of Naples Federico II",
                institution_authors="Alice; Bob",
                recommended_action="confirm_marker",
            ),
            paper(
                institution="Unrelated Institute",
                institution_authors="Carol",
                recommended_action="confirm_marker",
            ),
        ]

        visible, _hidden = suppress_resolved_records(candidates, mappings=[mapping])

        self.assertEqual([row["institution"] for row in visible], ["Unrelated Institute"])


if __name__ == "__main__":
    unittest.main()
