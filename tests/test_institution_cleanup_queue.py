import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)
from scripts.curated_mappings import load_mappings
from scripts.institution_cleanup import apply_cleanup_action
from scripts.institution_review_queue import load_queue, sync_findings
from scripts.validate_curated_database import validate_institution_consistency_audit


def write_csv(path, columns, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class InstitutionCleanupQueueTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.queue_path = root / "queue.csv"
        self.mappings_path = root / "mappings.csv"
        self.locations_path = root / "locations.csv"
        self.institutions_path = root / "institutions.csv"
        self.mapping = {
            column: "" for column in AUTHOR_INSTITUTION_MAPPING_COLUMNS
        }
        self.mapping.update({
            "mapping_id": "mapping:1",
            "paper_id": "paper:1",
            "title": "Example paper",
            "year": "2025",
            "institution": "Wrong Lab",
            "institution_id": "institution:wrong",
            "institution_authors": "Ada Example",
            "raw_affiliation": "Ada Example, Correct University",
            "evidence_source": "publisher",
            "mapping_status": "active",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
        })
        write_csv(self.mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [self.mapping])
        write_csv(self.locations_path, INSTITUTION_LOCATION_REVIEW_COLUMNS)
        institutions = []
        for identifier, name in (
            ("institution:wrong", "Wrong Lab"),
            ("institution:correct", "Correct University"),
        ):
            row = {column: "" for column in INSTITUTION_COLUMNS}
            row.update({
                "institution_id": identifier,
                "canonical_name": name,
                "institution_type": "university" if "University" in name else "research_institute",
                "institution_status": "active",
                "public_display": "true",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
                "created_by": "test",
            })
            institutions.append(row)
        write_csv(self.institutions_path, INSTITUTION_COLUMNS, institutions)
        self.finding = {
            "audit_id": "audit:1",
            "mapping_id": "mapping:1",
            "paper_id": "paper:1",
            "paper_title": "Example paper",
            "year": "2025",
            "author": "Ada Example",
            "current_institution": "Wrong Lab",
            "current_institution_id": "institution:wrong",
            "raw_affiliation": "Ada Example, Correct University",
            "suggested_canonical_institution": "Correct University",
            "suggested_institution_id": "institution:correct",
            "severity": "high",
            "issue_type": "affiliation_mismatch",
            "reason": "Raw affiliation identifies another institution.",
            "recommended_action": "Replace the mapping.",
            "resolution_status": "unresolved",
        }

    def tearDown(self):
        self.temporary.cleanup()

    def test_audit_finding_appears_in_persistent_admin_queue(self):
        result = sync_findings([self.finding], path=self.queue_path, now="2026-01-02T00:00:00+00:00")
        self.assertEqual(result["created"], 1)
        row = load_queue(self.queue_path)[0]
        self.assertEqual(row["finding_status"], "open")
        self.assertEqual(row["raw_affiliation"], self.finding["raw_affiliation"])

    def test_accepting_correction_updates_mapping_and_resolves_finding(self):
        sync_findings([self.finding], path=self.queue_path)
        queue_id = load_queue(self.queue_path)[0]["queue_id"]
        result = apply_cleanup_action(
            [queue_id],
            "accept_suggestion",
            "Confirmed against publisher affiliation.",
            confirmed=True,
            queue_path=self.queue_path,
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
            institutions_path=self.institutions_path,
        )
        self.assertEqual(len(result["mappings"]), 1)
        mapping = load_mappings(self.mappings_path)[0]
        self.assertEqual(mapping["institution_id"], "institution:correct")
        self.assertEqual(mapping["institution"], "Correct University")
        self.assertIn("Institution cleanup", mapping["review_note"])
        self.assertEqual(load_queue(self.queue_path)[0]["finding_status"], "accepted")

    def test_ignored_finding_does_not_block_publish(self):
        sync_findings([self.finding], path=self.queue_path)
        queue_id = load_queue(self.queue_path)[0]["queue_id"]
        apply_cleanup_action(
            [queue_id], "ignore", "Evidence supports both affiliations.",
            queue_path=self.queue_path,
        )
        issues = []
        validate_institution_consistency_audit(issues, load_queue(self.queue_path))
        self.assertEqual(issues, [])

    def test_unresolved_high_severity_still_blocks_publish(self):
        sync_findings([self.finding], path=self.queue_path)
        issues = []
        validate_institution_consistency_audit(issues, load_queue(self.queue_path))
        self.assertEqual([issue.level for issue in issues], ["ERROR"])


if __name__ == "__main__":
    unittest.main()
