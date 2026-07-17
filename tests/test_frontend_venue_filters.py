import pathlib
import json
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrontendVenueFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        cls.papers = json.loads(
            (ROOT / "web" / "data" / "public_preview_papers.json").read_text(encoding="utf-8")
        )["records"]

    def test_venue_type_filter_is_public_and_combines_with_venue(self):
        self.assertIn('id="venue-type-filter"', self.html)
        self.assertIn('matchesVenue &&\n    matchesVenueType', self.app)
        self.assertIn('venueTypeFilter.addEventListener("change", renderRecords)', self.app)

    def test_dynamic_counts_use_unique_paper_dimension_sets(self):
        self.assertIn('const venueDimensionSets = dimensionSets("ignoreVenue")', self.app)
        self.assertIn('const venueTypeDimensionSets = dimensionSets("ignoreVenueType")', self.app)
        self.assertIn('dimensionPaperCounts(venuePapers', self.app)
        self.assertIn('dimensionPaperCounts(\n    venueTypePapers', self.app)

    def test_filter_uses_canonical_identity_and_searches_all_fields(self):
        self.assertIn('record.venue_id || ""', self.app)
        for field in ("record.venue_acronym", "record.venue_aliases", "record.venue_type", "record.venue_track"):
            self.assertIn(field, self.app)

    def test_csv_and_human_display_use_canonical_fields(self):
        for column in ("venue_label", "venue_id", "venue_name", "venue_acronym", "venue_type", "venue_track"):
            self.assertGreaterEqual(self.app.count(f'["{column}"'), 2)
        self.assertIn('venueDisplayHtml(record)', self.app)

    def test_public_options_deduplicate_by_canonical_venue_id(self):
        metadata_by_id = {}
        for paper in self.papers:
            venue_id = paper.get("venue_id")
            if not venue_id:
                continue
            metadata = tuple(paper.get(field, "") for field in (
                "venue_name", "venue_acronym", "venue_type", "venue_track", "venue_label",
            ))
            if venue_id in metadata_by_id:
                self.assertEqual(metadata_by_id[venue_id], metadata)
            metadata_by_id[venue_id] = metadata
        self.assertEqual(len(metadata_by_id), len({paper["venue_id"] for paper in self.papers if paper.get("venue_id")}))

    def test_combined_venue_type_and_year_filter_uses_unique_papers(self):
        matching = [paper for paper in self.papers if (
            paper.get("venue_id") == "venue:wifs:main"
            and paper.get("venue_type") == "workshop"
            and paper.get("year") == 2024
        )]
        self.assertTrue(matching)
        identities = {
            paper.get("doi") or paper.get("openalex_url") or (paper.get("title"), paper.get("year"))
            for paper in matching
        }
        self.assertEqual(len(matching), len(identities))
        self.assertIn("matchesMinimumYear", self.app)
        self.assertIn("matchesMaximumYear", self.app)


if __name__ == "__main__":
    unittest.main()
