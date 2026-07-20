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

    def run_dynamic_option_fixture(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        count_helpers = self.app[
            self.app.index("function dimensionPaperCounts"):
            self.app.index("\nfunction nextCountryOptionIndex")
        ]
        script = f"""
const venueTypeOrder = ['conference', 'journal', 'preprint', 'book'];
function compareTextValues(first, second) {{
  return String(first).localeCompare(String(second), undefined, {{sensitivity: 'base'}});
}}
function formatTask(value) {{ return String(value); }}
const document = {{createElement: () => ({{value: '', textContent: ''}})}};
{count_helpers}
const metadata = new Map([
  ['venue:journal', {{name: 'Journal Venue', label: 'Journal Venue'}}],
  ['venue:preprint', {{name: 'Preprint Venue', label: 'Preprint Venue'}}],
  ['venue:alpha', {{name: 'Alpha Venue', label: 'Alpha Venue'}}],
  ['venue:zulu', {{name: 'Zulu Venue', label: 'Zulu Venue'}}],
  ['__unknown__', {{name: 'Unknown venue/source', label: 'Unknown venue/source'}}],
]);
const papers = [
  {{id: 'j1', region: 'US', venueIds: ['venue:journal', 'venue:journal']}},
  {{id: 'j2', region: 'US', venueIds: ['venue:journal']}},
  {{id: 'j3', region: 'EU', venueIds: ['venue:journal']}},
  {{id: 'p1', region: 'EU', venueIds: ['venue:preprint']}},
  {{id: 'p2', region: 'EU', venueIds: ['venue:preprint']}},
  {{id: 'a1', region: 'EU', venueIds: ['venue:alpha']}},
  {{id: 'z1', region: 'EU', venueIds: ['venue:zulu']}},
  {{id: 'u1', region: 'EU', venueIds: ['__unknown__']}},
  {{id: 'u2', region: 'US', venueIds: ['__unknown__']}},
  {{id: 'u3', region: 'US', venueIds: ['__unknown__']}},
  {{id: 'u4', region: 'US', venueIds: ['__unknown__']}},
];
function optionsFor(records) {{
  const counts = dimensionPaperCounts(records, paper => paper.venueIds);
  const select = {{
    value: 'all',
    options: [],
    replaceChildren(...options) {{ this.options = options; }},
  }};
  replaceCountedFilterOptions(
    select, 'All', sortedVenueCounts(counts, metadata),
    value => metadata.get(value).label, false,
  );
  return select.options.map(option => [option.value, option.textContent]);
}}
const reversedTies = sortedVenueCounts(
  new Map([['venue:zulu', 1], ['venue:alpha', 1], ['venue:journal', 1]]),
  metadata,
).map(([value]) => value);
process.stdout.write(JSON.stringify({{
  runtime: process.version,
  base: optionsFor(papers),
  filtered: optionsFor(papers.filter(paper => paper.region === 'EU')),
  reversedTies,
}}));
"""
        result = subprocess.run(
            [node, "-e", script], check=True, capture_output=True, text=True,
        )
        return json.loads(result.stdout)

    def test_publication_type_filter_is_public_and_combines_with_venue(self):
        self.assertIn('id="venue-type-filter"', self.html)
        self.assertIn("Publication Type", self.html)
        self.assertNotIn("Venue Type", self.html)
        self.assertNotIn("All Publication Types", self.html)
        self.assertIn('matchesVenue &&\n    matchesVenueType', self.app)
        self.assertIn('venueTypeFilter.addEventListener("change", renderRecords)', self.app)
        self.assertIn(
            'String(record.publication_type || record.venue_type || "")',
            self.app,
        )

    def test_dynamic_counts_use_unique_paper_dimension_sets(self):
        self.assertIn('const venueDimensionSets = dimensionSets("ignoreVenue")', self.app)
        self.assertIn('const venueTypeDimensionSets = dimensionSets("ignoreVenueType")', self.app)
        self.assertIn('dimensionPaperCounts(venuePapers', self.app)
        self.assertIn('dimensionPaperCounts(\n    venueTypePapers', self.app)
        identity_start = self.app.index("function paperIdentity")
        identity = self.app[
            identity_start:
            self.app.index("function recordCountry", identity_start)
        ]
        self.assertLess(identity.index("normalizedDoi(record.doi)"), identity.index("record.openalex_url"))

    def test_fixed_type_order_and_dynamic_venue_count_order(self):
        result = self.run_order_helpers()
        self.assertEqual(
            result["types"],
            ["conference", "journal", "preprint", "book", "__unknown__"],
        )
        self.assertEqual(result["venues"], [
            "journal", "preprint", "book", "conf-beta", "conf-alpha", "conf-zulu", "__unknown__",
        ])
        self.assertEqual(
            self.metadata["venue_type_order"],
            ["conference", "journal", "preprint", "book"],
        )

    def test_dynamic_venue_order_all_deduplication_and_active_filters(self):
        result = self.run_dynamic_option_fixture()
        self.assertTrue(result["runtime"].startswith("v"))
        self.assertEqual(result["base"], [
            ["all", "All"],
            ["venue:journal", "Journal Venue (3)"],
            ["venue:preprint", "Preprint Venue (2)"],
            ["venue:alpha", "Alpha Venue (1)"],
            ["venue:zulu", "Zulu Venue (1)"],
            ["__unknown__", "Unknown venue/source (4)"],
        ])
        self.assertEqual(result["filtered"], [
            ["all", "All"],
            ["venue:preprint", "Preprint Venue (2)"],
            ["venue:alpha", "Alpha Venue (1)"],
            ["venue:journal", "Journal Venue (1)"],
            ["venue:zulu", "Zulu Venue (1)"],
            ["__unknown__", "Unknown venue/source (1)"],
        ])
        self.assertEqual(result["reversedTies"], [
            "venue:alpha", "venue:journal", "venue:zulu",
        ])

    def test_workshop_is_track_not_public_type(self):
        self.assertNotIn("workshop", {paper.get("venue_type") for paper in self.papers})
        workshop_papers = [paper for paper in self.papers if paper.get("venue_track") == "workshops"]
        self.assertTrue(workshop_papers)
        self.assertEqual({paper.get("venue_type") for paper in workshop_papers}, {"conference"})
        self.assertTrue(all(not label.startswith("Conference · ") and label.endswith(" · Workshops")
                            for label in (paper.get("venue_label", "") for paper in workshop_papers)))

    def test_book_publication_type_option_uses_deduplicated_paper_count(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not on PATH")
        helper_start = self.app.index("function dimensionPaperCounts")
        helper_end = self.app.index("\nfunction nextCountryOptionIndex", helper_start)
        helpers = self.app[helper_start:helper_end]
        type_start = self.app.index("function recordVenueType")
        type_end = self.app.index("\nfunction venueDisplayHtml", type_start)
        type_helpers = self.app[type_start:type_end]
        script = f"""
const fs = require('fs');
const papers = JSON.parse(fs.readFileSync('web/data/public_preview_papers.json', 'utf8')).records;
const mapRecords = JSON.parse(fs.readFileSync('web/data/public_preview_map_data.json', 'utf8')).records;
const venueTypeOrder = ['conference', 'journal', 'preprint', 'book'];
const document = {{createElement: () => ({{value: '', textContent: ''}})}};
function compareTextValues(first, second) {{
  return String(first).localeCompare(String(second), undefined, {{sensitivity: 'base'}});
}}
function formatTask(value) {{
  return String(value).split('_').map(
    part => part ? part[0].toUpperCase() + part.slice(1) : part
  ).join(' ');
}}
{type_helpers}
{helpers}
const select = {{
  value: 'all',
  options: [],
  replaceChildren(...options) {{ this.options = options; }},
}};
const counts = dimensionPaperCounts(
  papers,
  record => [recordVenueType(record) || '__unknown__'],
);
replaceCountedFilterOptions(
  select,
  'All',
  sortedVenueTypeCounts(counts),
  value => value === '__unknown__' ? 'Unknown' : formatTask(value),
);
select.value = 'book';
const selectedBooks = papers.filter(record => recordVenueType(record) === select.value);
process.stdout.write(JSON.stringify({{
  options: select.options.map(option => [option.value, option.textContent]),
  selectedIds: selectedBooks.map(record => record.id || record.openalex_url || record.title),
  bookPaperCount: papers.filter(record => record.publication_type === 'book').length,
  bookMarkerCount: mapRecords.filter(record => record.publication_type === 'book').length,
  allBookPapersRetainType: papers
    .filter(record => recordVenueType(record) === 'book')
    .every(record => record.publication_type === 'book'),
}}));
"""
        result = subprocess.run(
            [node, "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        output = json.loads(result.stdout)
        self.assertIn(["book", "Book (21)"], output["options"])
        self.assertLess(output["bookPaperCount"], output["bookMarkerCount"])
        self.assertEqual(output["bookPaperCount"], 21)
        self.assertEqual(len(output["selectedIds"]), 21)
        self.assertEqual(len(output["selectedIds"]), len(set(output["selectedIds"])))
        self.assertTrue(output["allBookPapersRetainType"])

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

    def test_public_options_do_not_duplicate_same_name_by_acronym_variant(self):
        by_name_track = {}
        for paper in self.papers:
            key = (
                paper.get("venue_name", "").casefold(),
                paper.get("venue_track", "main"),
            )
            by_name_track.setdefault(key, {
                "ids": set(),
                "labels": set(),
            })
            by_name_track[key]["ids"].add(paper.get("venue_id", ""))
            by_name_track[key]["labels"].add(paper.get("venue_label", ""))
        duplicates = {
            key: value for key, value in by_name_track.items()
            if len(value["ids"] - {""}) > 1 and len(value["labels"]) > 1
        }
        self.assertEqual(duplicates, {})

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

    def test_corrected_public_venue_options_are_unique(self):
        expected = {
            "venue:ijcnn:main": "International Joint Conference on Neural Networks (IJCNN)",
            "venue:icmr:main": "ACM International Conference on Multimedia Retrieval (ICMR)",
            "venue:wacv:workshops": "IEEE/CVF Winter Conference on Applications of Computer Vision (WACV) · Workshops",
        }
        for venue_id, label in expected.items():
            with self.subTest(venue_id=venue_id):
                matching = [paper for paper in self.papers if paper.get("venue_id") == venue_id]
                self.assertTrue(matching)
                self.assertEqual({paper.get("venue_label") for paper in matching}, {label})

        labels_by_id = {}
        for paper in self.papers:
            venue_id = paper.get("venue_id")
            if venue_id in expected:
                labels_by_id.setdefault(venue_id, set()).add(paper.get("venue_label"))
        self.assertEqual({venue_id: len(labels) for venue_id, labels in labels_by_id.items()}, {
            "venue:ijcnn:main": 1,
            "venue:icmr:main": 1,
            "venue:wacv:workshops": 1,
        })
        public_labels = [paper.get("venue_label", "") for paper in self.papers]
        self.assertNotIn("International Conference on Multimedia Retrieval", set(public_labels))
        self.assertFalse(any("WACVW" in label for label in public_labels))
        self.assertFalse(any("Inter national" in label for label in public_labels))

    def test_public_counts_meet_disaster_baseline_after_venue_corrections(self):
        map_records = json.loads(
            (ROOT / "web" / "data" / "public_preview_map_data.json").read_text(encoding="utf-8")
        )["records"]
        baseline = json.loads(
            (ROOT / "data" / "curated" / "public_export_baseline.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertGreaterEqual(len(self.papers), baseline["paper_records"])
        self.assertGreaterEqual(len(map_records), baseline["map_records"])

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
            'replaceCountedFilterOptions(\n    venueFilter,\n    "All",',
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
