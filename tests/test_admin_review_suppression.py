import unittest
import csv
import tempfile
from pathlib import Path
from unittest.mock import patch

from scripts.admin_review_queues import load_queue, suppress_resolved_records


REPOSITORY = Path(__file__).resolve().parent.parent


def write_csv(path, rows):
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def paper(**overrides):
    row = {
        "title": "A Bias-Free Training Paradigm for More General AI-generated Image Detection",
        "year": "2025",
        "doi": "10.1109/cvpr52734.2025.01741",
        "openalex_url": "https://openalex.org/W4413145917",
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
            institution_authors=(
                "Fabrizio Guillaro; Giada Zingarini; Davide Cozzolino; "
                "Luisa Verdoliva"
            ),
            recommended_action="confirm_marker",
        )
        corrected = paper(
            institution="University of Naples Federico II",
            institution_authors=(
                "Luisa Verdoliva; Davide Cozzolino; Giada Zingarini; "
                "Fabrizio Guillaro"
            ),
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

    def test_queue_payload_zero_count_has_no_stale_records(self):
        candidate = paper(
            priority="P1",
            institution="University of Naples Federico II",
            institution_authors="Alice; Bob",
            recommended_action="confirm_marker",
        )
        mapping = paper(
            institution="University of Naples Federico II",
            institution_authors="Alice; Bob",
            mapping_status="active",
        )
        with tempfile.TemporaryDirectory(dir=REPOSITORY) as directory:
            directory = Path(directory)
            queue_path = directory / "queue.csv"
            mappings_path = directory / "mappings.csv"
            empty_path = directory / "empty.csv"
            write_csv(queue_path, [candidate])
            write_csv(mappings_path, [mapping])
            empty_path.write_text("", encoding="utf-8")
            with patch.dict(
                "scripts.admin_review_queues.QUEUE_PATHS",
                {"high_risk_marker": queue_path},
            ):
                payload = load_queue(
                    "high_risk_marker",
                    mappings_path=mappings_path,
                    exclusions_path=empty_path,
                    record_overrides_path=empty_path,
                    author_overrides_path=empty_path,
                    corrections_path=empty_path,
                )

        self.assertEqual(payload["total_unresolved"], 0)
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["records"], [])
        self.assertEqual(
            payload["suppression_reasons"],
            {"resolved_by_active_curated_mapping": 1},
        )

    def test_real_corrected_candidate_is_hidden_but_google_candidates_remain(self):
        authors = (
            "Fabrizio Guillaro; Giada Zingarini; Davide Cozzolino; "
            "Luisa Verdoliva"
        )
        records = [
            paper(institution="Federico II University Hospital", institution_authors=authors),
            paper(institution="Google (United States)", institution_authors="Ben Usman; Avneesh Sud"),
            paper(institution="Google DeepMind (United Kingdom)", institution_authors="Ben Usman; Avneesh Sud"),
        ]
        mapping = paper(
            institution="University of Naples Federico II",
            institution_authors=authors,
            mapping_status="active",
        )

        visible, hidden = suppress_resolved_records(records, mappings=[mapping])

        self.assertEqual(
            [row["institution"] for row in visible],
            ["Google (United States)", "Google DeepMind (United Kingdom)"],
        )
        self.assertEqual(hidden["superseded_by_active_curated_mapping"], 1)

    def test_frontend_counts_rendered_rows_and_clears_stale_detail(self):
        source = (REPOSITORY / "web/admin.js").read_text(encoding="utf-8")

        self.assertIn("suppressionCountText(queue, filtered.length)", source)
        self.assertIn("body.replaceChildren();", source)
        self.assertIn("!visibleKeys.has(state.selectedReviewKeys[name])", source)
        self.assertIn("clearReviewDetail(name);", source)


if __name__ == "__main__":
    unittest.main()
