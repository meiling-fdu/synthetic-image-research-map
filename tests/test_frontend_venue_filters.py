import pathlib
import json
import shutil
import subprocess
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
        cls.metadata = json.loads(
            (ROOT / "web" / "data" / "public_preview_papers.json").read_text(encoding="utf-8")
        )["metadata"]

    def run_order_helpers(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        start = self.app.index("function venueTypeRank")
        end = self.app.index("\nfunction replaceCountedFilterOptions", start)
        helpers = self.app[start:end]
        script = f"""
const venueTypeOrder = ['conference', 'journal', 'preprint', 'book'];
function compareTextValues(first, second) {{
  return String(first).localeCompare(String(second), undefined, {{sensitivity: 'base'}});
}}
function formatTask(value) {{ return String(value); }}
{helpers}
const typeCounts = new Map([
  ['book', 50], ['__unknown__', 999], ['preprint', 80], ['journal', 100], ['conference', 1],
]);
        const venueCounts = new Map([
  ['__unknown__', 999], ['book', 20], ['preprint', 30], ['journal', 100],
  ['conf-alpha', 2], ['conf-zulu', 2], ['conf-beta', 3],
]);
const metadata = new Map([
  ['__unknown__', {{name: 'Unknown venue/source', type: 'conference', acronym: '', track: 'main'}}],
  ['book', {{name: 'Book Venue', type: 'book', acronym: '', track: 'main'}}],
  ['preprint', {{name: 'arXiv', type: 'preprint', acronym: '', track: 'main'}}],
  ['journal', {{name: 'Journal Venue', type: 'journal', acronym: '', track: 'main'}}],
  ['conf-alpha', {{name: 'Alpha Conference', type: 'conference', acronym: '', track: 'main'}}],
  ['conf-zulu', {{name: 'Zulu Conference', type: 'conference', acronym: '', track: 'main'}}],
  ['conf-beta', {{name: 'Beta Conference', type: 'conference', acronym: '', track: 'main'}}],
]);
process.stdout.write(JSON.stringify({{
  types: sortedVenueTypeCounts(typeCounts).map(([value]) => value),
  venues: sortedVenueCounts(venueCounts, metadata).map(([value]) => value),
}}));
"""
        result = subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def test_venue_type_filter_is_public_and_combines_with_venue(self):
        self.assertIn('id="venue-type-filter"', self.html)
        self.assertIn('matchesVenue &&\n    matchesVenueType', self.app)
        self.assertIn('venueTypeFilter.addEventListener("change", renderRecords)', self.app)

    def test_dynamic_counts_use_unique_paper_dimension_sets(self):
        self.assertIn('const venueDimensionSets = dimensionSets("ignoreVenue")', self.app)
        self.assertIn('const venueTypeDimensionSets = dimensionSets("ignoreVenueType")', self.app)
        self.assertIn('dimensionPaperCounts(venuePapers', self.app)
        self.assertIn('dimensionPaperCounts(\n    venueTypePapers', self.app)

    def test_fixed_type_order_and_alphabetical_venue_order(self):
        result = self.run_order_helpers()
        self.assertEqual(
            result["types"],
            ["conference", "journal", "preprint", "book", "__unknown__"],
        )
        self.assertEqual(result["venues"], [
            "conf-alpha", "book", "conf-beta", "journal", "conf-zulu", "preprint", "__unknown__",
        ])
        self.assertEqual(
            self.metadata["venue_type_order"],
            ["conference", "journal", "preprint", "book"],
        )

    def test_workshop_is_track_not_public_type(self):
        self.assertNotIn("workshop", {paper.get("venue_type") for paper in self.papers})
        workshop_papers = [paper for paper in self.papers if paper.get("venue_track") == "workshops"]
        self.assertTrue(workshop_papers)
        self.assertEqual({paper.get("venue_type") for paper in workshop_papers}, {"conference"})
        self.assertTrue(all(not label.startswith("Conference · ") and label.endswith(" · Workshops")
                            for label in (paper.get("venue_label", "") for paper in workshop_papers)))

    def test_filter_uses_canonical_identity_and_searches_all_fields(self):
        self.assertIn('record.venue_id || ""', self.app)
        for field in ("record.venue_acronym", "record.venue_aliases", "record.venue_type", "record.venue_track"):
            self.assertIn(field, self.app)

    def test_csv_and_human_display_use_canonical_fields(self):
        for column in ("venue_label", "venue_id", "venue_name", "venue_acronym", "venue_type", "venue_track"):
            self.assertGreaterEqual(self.app.count(f'["{column}"'), 2)
        self.assertIn('venueDisplayHtml(record)', self.app)

    def test_audited_journal_acronyms_are_exported_and_searchable(self):
        expected = {
            "IEEE Transactions on Pattern Analysis and Machine Intelligence": "TPAMI",
            "IEEE Transactions on Information Forensics and Security": "TIFS",
            "IEEE Transactions on Multimedia": "TMM",
            "IEEE Signal Processing Letters": "SPL",
            "Pattern Recognition": "PR",
            "Pattern Recognition Letters": "PRL",
            "ACM Transactions on Multimedia Computing, Communications, and Applications": "TOMM",
        }
        exported = {paper.get("venue_name"): paper for paper in self.papers}
        for name, acronym in expected.items():
            if name not in exported:
                continue
            with self.subTest(acronym=acronym):
                self.assertEqual(exported[name].get("venue_acronym"), acronym)
                self.assertIn(f"({acronym})", exported[name].get("venue_label", ""))
        self.assertIn("record.venue_acronym", self.app)

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

    def test_icassp_collapses_to_one_main_public_option(self):
        icassp = [
            paper for paper in self.papers
            if paper.get("venue_id") == "venue:icassp:main"
            or "ICASSP" in " ".join(str(paper.get(field, "")) for field in (
                "venue_label", "venue_name", "raw_venue",
            ))
        ]
        self.assertTrue(icassp)
        self.assertEqual({paper.get("venue_id") for paper in icassp}, {"venue:icassp:main"})
        self.assertEqual(
            {paper.get("venue_label") for paper in icassp},
            {"IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)"},
        )
        self.assertFalse(any("ICASSP 2023" in paper.get("venue_label", "") for paper in icassp))
        self.assertFalse(any("ICASSP 2025" in paper.get("venue_label", "") for paper in icassp))

    def test_venue_type_control_precedes_venue_control(self):
        self.assertLess(
            self.html.index('id="venue-type-filter"'),
            self.html.index('id="venue-filter"'),
        )

    def test_venue_labels_drop_type_prefixes(self):
        forbidden = ("Conference ·", "Journal ·", "Preprint ·", "Book ·")
        self.assertFalse(any(
            paper.get("venue_label", "").startswith(forbidden)
            for paper in self.papers
        ))
        self.assertIn(
            "IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)",
            {paper.get("venue_label") for paper in self.papers},
        )

    def test_invalid_venue_selection_is_not_preserved_when_type_changes(self):
        self.assertIn(
            'replaceCountedFilterOptions(\n    venueFilter,\n    "All venues",',
            self.app,
        )
        self.assertIn("sortedVenueCounts(venueCounts, metadataByVenue)", self.app)
        self.assertIn("false,\n  );\n  replaceCountedFilterOptions(\n    venueTypeFilter", self.app)

    def test_combined_venue_type_and_year_filter_uses_unique_papers(self):
        matching = [paper for paper in self.papers if (
            paper.get("venue_id") == "venue:wifs:main"
            and paper.get("venue_type") == "conference"
            and paper.get("venue_track") == "workshops"
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
