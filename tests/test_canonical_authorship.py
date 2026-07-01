import json
import tempfile
import unittest
from pathlib import Path

from scripts.canonical_authorship import (
    build_canonical_authorship,
    guard_no_legacy_runtime_references,
)
from scripts.export_public_preview import _merge_incremental
from scripts.validate_public_preview import validate_canonical_authorship


class CanonicalAuthorshipTests(unittest.TestCase):
    def test_no_legacy_candidate_runtime_dependency(self):
        guard_no_legacy_runtime_references()

    def test_single_author_gets_index_one(self):
        canonical = build_canonical_authorship(
            ["Ada Researcher"],
            [{"institution_id": "i:1", "canonical_name": "Example University"}],
        )
        self.assertEqual(canonical["institutions"][0]["index"], 1)
        self.assertEqual(canonical["authors"][0]["institutions"], ["i:1"])

    def test_multi_affiliation_is_deduplicated_and_ordered(self):
        canonical = build_canonical_authorship(
            ["Ada Researcher", "Ben Researcher"],
            [
                {
                    "institution_id": "i:1",
                    "canonical_name": "First University",
                    "authors": ["Ada Researcher"],
                },
                {
                    "institution_id": "i:2",
                    "canonical_name": "Second University",
                    "authors": ["Ada Researcher", "Ben Researcher"],
                },
                {
                    "institution_id": "i:1",
                    "canonical_name": "First University",
                    "authors": ["Ada Researcher"],
                },
            ],
        )
        self.assertEqual(
            [item["index"] for item in canonical["institutions"]], [1, 2]
        )
        self.assertEqual(
            canonical["authors"][0]["institutions"], ["i:1", "i:2"]
        )

    def test_unresolved_membership_is_explicit_not_missing(self):
        canonical = build_canonical_authorship(["Ada Researcher"], [])
        self.assertEqual(canonical["institutions"][0]["index"], 1)
        self.assertEqual(
            canonical["authors"][0]["institutions"],
            ["institution:unresolved"],
        )

    def test_validator_rejects_orphan_and_raw_affiliation(self):
        issues = []
        validate_canonical_authorship(
            0,
            {
                "title": "Broken graph",
                "canonical_authorship": {
                    "authors": [{"name": "Ada", "institutions": []}],
                    "institutions": [
                        {
                            "institution_id": "i:1",
                            "canonical_name": "Example",
                            "index": 2,
                        }
                    ],
                },
                "curated_mappings": [{"raw_affiliation": "stale"}],
            },
            issues,
        )
        self.assertGreaterEqual(len(issues), 3)
        self.assertTrue(all(issue.level == "ERROR" for issue in issues))

    def test_incremental_rebuild_preserves_unaffected_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "preview.json"
            path.write_text(
                json.dumps(
                    {
                        "metadata": {"version": "old"},
                        "records": [
                            {"paper_id": "openalex:W1", "openalex_url": "https://openalex.org/W1"},
                            {"paper_id": "openalex:W2", "openalex_url": "https://openalex.org/W2", "old": True},
                            {"paper_id": "openalex:W3", "openalex_url": "https://openalex.org/W3"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            merged = _merge_incremental(
                path,
                {
                    "metadata": {"version": "new"},
                    "records": [
                        {"paper_id": "openalex:W2", "openalex_url": "https://openalex.org/W2", "new": True}
                    ],
                },
                "openalex:W2",
            )
        self.assertEqual(
            [row["openalex_url"].rsplit("/", 1)[-1] for row in merged["records"]],
            ["W1", "W2", "W3"],
        )
        self.assertTrue(merged["records"][1]["new"])


if __name__ == "__main__":
    unittest.main()
