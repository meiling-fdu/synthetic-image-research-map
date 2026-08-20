import unittest
from unittest import mock

from scripts.orphan_institution_cleanup import (
    analyze, atomic_write_csvs, durable_audit_rows, prove_complete_source,
)


def institution(identifier, name=None, **extra):
    return {
        "institution_id": identifier,
        "canonical_name": name or identifier,
        "institution_status": "active",
        **extra,
    }


class OrphanInstitutionCleanupTests(unittest.TestCase):
    def analyze(self, institutions, **kwargs):
        return analyze(
            institutions=institutions,
            authoritative=kwargs.pop("authoritative", True),
            run_id="test-run",
            timestamp="2026-07-29T00:00:00+00:00",
            **kwargs,
        )

    def test_unused_institution_and_exclusive_location_are_deleted(self):
        result = self.analyze(
            [institution("orphan")],
            locations=[{"location_id": "one", "institution_id": "orphan"}],
        )
        self.assertEqual(result.deleted_ids, {"orphan"})
        self.assertEqual(result.locations, [])
        self.assertEqual(result.rows[0]["deleted_location"], "true")

    def test_retained_public_paper_relationship_retains_institution(self):
        result = self.analyze(
            [institution("orphan")],
            public_maps=[{"institution_id": "orphan", "paper_id": "paper:1"}],
        )
        self.assertFalse(result.deleted_ids)
        self.assertEqual(result.rows[0]["marker_count"], "1")

    def test_location_marker_without_paper_relationship_does_not_retain(self):
        result = self.analyze(
            [institution("orphan")],
            locations=[{"location_id": "one", "institution_id": "orphan"}],
        )
        self.assertEqual(result.deleted_ids, {"orphan"})

    def test_parent_of_retained_child_remains(self):
        result = self.analyze(
            [institution("parent"), institution("child")],
            hierarchy=[{
                "parent_institution_id": "parent",
                "child_institution_id": "child",
                "review_status": "confirmed",
            }],
            mappings=[{
                "institution_id": "child",
                "mapping_status": "active",
                "paper_id": "paper:1",
            }],
        )
        decisions = {row["institution_id"]: row["decision"] for row in result.rows}
        self.assertEqual(decisions["parent"], "retained_as_parent")
        self.assertNotIn("parent", result.deleted_ids)

    def test_confirmed_search_relationship_retains_both_canonical_endpoints(self):
        relationship = {
            "root_institution_id": "root",
            "related_institution_id": "related",
            "relationship_type": "search_family",
            "review_status": "confirmed",
        }
        result = self.analyze(
            [institution("root"), institution("related")],
            search_relationships=[relationship],
        )
        self.assertFalse(result.deleted_ids)
        self.assertEqual(result.search_relationships, [relationship])

    def test_alias_and_merge_targets_remain(self):
        result = self.analyze(
            [institution("alias-target"), institution("merge-target")],
            aliases=[{
                "institution_id": "alias-target",
                "review_status": "confirmed",
            }],
            audit_log=[{
                "action": "merge",
                "previous_institution_id": "old",
                "institution_id": "merge-target",
            }],
        )
        self.assertFalse(result.deleted_ids)

    def test_reviewed_replacement_preserves_name_as_alias_then_deletes(self):
        result = self.analyze(
            [institution("old", "Old Name"), institution("target", "Target Name")],
            mappings=[{
                "institution_id": "target",
                "mapping_status": "active",
                "paper_id": "paper:1",
            }],
            audit_log=[{
                "action": "merge",
                "previous_institution_id": "old",
                "institution_id": "target",
            }],
        )
        old = next(row for row in result.rows if row["institution_id"] == "old")
        self.assertEqual(old["decision"], "merged_then_deleted")
        self.assertTrue(any(
            row["alias_name"] == "Old Name" and row["institution_id"] == "target"
            for row in result.aliases
        ))

    def test_ambiguous_similar_duplicate_requires_review(self):
        result = self.analyze(
            [
                institution("old", "China People's Public Security University"),
                institution("used", "People’s Public Security University of China"),
            ],
            mappings=[{
                "institution_id": "used",
                "mapping_status": "active",
                "paper_id": "paper:1",
            }],
        )
        old = next(row for row in result.rows if row["institution_id"] == "old")
        self.assertEqual(old["decision"], "ambiguous_duplicate")
        self.assertNotIn("old", result.deleted_ids)

    def test_partial_source_is_report_only(self):
        result = self.analyze([institution("orphan")], authoritative=False)
        self.assertFalse(result.deleted_ids)
        self.assertEqual(result.rows[0]["decision"], "retained_partial_source_run")

    def test_review_queue_and_override_ids_are_retained(self):
        result = self.analyze(
            [
                institution("institution:reviewed"),
                institution("institution:overridden"),
            ],
            review_queue=[{"current_institution_id": "institution:reviewed"}],
            override_rows=[{"institution_id": "institution:overridden"}],
        )
        self.assertFalse(result.deleted_ids)

    def test_shared_location_rows_for_other_institution_remain(self):
        result = self.analyze(
            [institution("orphan"), institution("used")],
            locations=[
                {"location_id": "a", "institution_id": "orphan"},
                {"location_id": "b", "institution_id": "used"},
            ],
            mappings=[{
                "institution_id": "used",
                "mapping_status": "active",
                "paper_id": "paper:1",
            }],
        )
        self.assertEqual(
            [row["institution_id"] for row in result.locations], ["used"]
        )

    def test_idempotent_second_analysis(self):
        first = self.analyze([institution("orphan")])
        second = self.analyze(first.institutions)
        self.assertFalse(second.deleted_ids)
        self.assertEqual(second.rows, [])

    def test_deleted_audit_evidence_survives_second_run(self):
        previous = [{
            "institution_id": "orphan",
            "institution_name": "Orphan",
            "decision": "deleted_orphan",
            "deleted_from_registry": "true",
        }]
        rows = durable_audit_rows([], previous, [], [], "run:2", "later")
        self.assertEqual(rows[0]["institution_id"], "orphan")
        self.assertEqual(rows[0]["decision"], "deleted_orphan")

    def test_completeness_requires_every_retained_public_identity(self):
        complete, missing = prove_complete_source(
            [{"doi": "10.1/a"}], [{"doi": "10.1/a"}, {"doi": "10.1/b"}]
        )
        self.assertFalse(complete)
        self.assertEqual(missing, 1)

    def test_transaction_failure_restores_prior_files(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as directory:
            one = Path(directory) / "one.csv"
            two = Path(directory) / "two.csv"
            one.write_text("value\nold-one\n", encoding="utf-8")
            two.write_text("value\nold-two\n", encoding="utf-8")
            real_replace = __import__("os").replace
            calls = 0

            def fail_second(source, target):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated")
                real_replace(source, target)

            with mock.patch(
                "scripts.orphan_institution_cleanup.os.replace",
                side_effect=fail_second,
            ), self.assertRaises(OSError):
                atomic_write_csvs([
                    (one, [{"value": "new-one"}], ["value"]),
                    (two, [{"value": "new-two"}], ["value"]),
                ])
            self.assertIn("old-one", one.read_text(encoding="utf-8"))
            self.assertIn("old-two", two.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
