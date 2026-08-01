import csv
import pathlib
import tempfile
import unittest

from scripts.curated_papers import CuratedPaperError, apply_canonical_venue_selection
from scripts.venues import VENUE_ALIAS_COLUMNS, canonical_venue_options, display_venue, read_venue_aliases


ROOT = pathlib.Path(__file__).resolve().parents[1]


class PaperLevelVenueTrackTests(unittest.TestCase):
    def setUp(self):
        self.aliases = read_venue_aliases()

    def selection(self, track="main"):
        return apply_canonical_venue_selection({
            "venue_id": "venue:iclr",
            "venue_name": "International Conference on Learning Representations",
            "venue_acronym": "ICLR",
            "venue_type": "conference",
            "venue_track": track,
            "publication_type": "conference",
        })

    def test_main_and_workshop_share_one_canonical_id(self):
        main = self.selection("main")
        workshop = self.selection("workshops")
        self.assertEqual(main["venue_id"], workshop["venue_id"])
        self.assertEqual(workshop["venue_id"], "venue:iclr")
        self.assertEqual((main["venue_track"], workshop["venue_track"]), ("main", "workshops"))
        self.assertNotIn("Main", main["venue_label"])
        self.assertIn("Workshops", workshop["venue_label"])

    def test_invalid_track_is_rejected_independently(self):
        with self.assertRaisesRegex(CuratedPaperError, "venue_track is invalid"):
            self.selection("free text")

    def test_missing_legacy_conference_track_defaults_to_main(self):
        selected = apply_canonical_venue_selection({
            "venue_id": "venue:iclr",
            "venue_name": "International Conference on Learning Representations",
            "venue_acronym": "ICLR",
            "venue_type": "conference",
            "publication_type": "conference",
        })
        self.assertEqual(selected["venue_track"], "main")

    def test_venue_options_aggregate_tracks_by_id(self):
        options = canonical_venue_options(self.aliases, [
            {"paper_id": "main", "venue_id": "venue:iclr", "venue_track": "main"},
            {"paper_id": "workshop", "venue_id": "venue:iclr", "venue_track": "workshops"},
        ])
        iclr = next(option for option in options if option["venue_id"] == "venue:iclr")
        self.assertEqual(iclr["paper_count"], 2)
        self.assertEqual(iclr["venue_track"], "")

    def test_creation_registry_track_is_only_an_alias_hint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "aliases.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=VENUE_ALIAS_COLUMNS)
                writer.writeheader()
                writer.writerow({
                    "alias": "Example Conference Workshops",
                    "venue_id": "venue:example",
                    "venue_name": "Example Conference",
                    "venue_acronym": "EX",
                    "venue_type": "conference",
                    "venue_track": "workshops",
                    "review_status": "confirmed",
                    "notes": "paper-level resolution hint",
                })
            rows = read_venue_aliases(path)
            options = canonical_venue_options(rows)
            self.assertEqual(options[0]["venue_track"], "")
            self.assertEqual(display_venue({**options[0], "venue_track": "main"}), "Example Conference (EX)")


if __name__ == "__main__":
    unittest.main()
