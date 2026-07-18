import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_AUDIT_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
    INSTITUTION_REVIEW_QUEUE_COLUMNS,
)
from scripts.curated_mappings import load_mappings, update_mapping
from scripts.institution_cleanup import apply_cleanup_action
from scripts.institution_review_queue import (
    InstitutionReviewQueueError,
    load_queue,
    queue_payload,
    reconcile_mapping_changes,
    sync_findings,
)
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
        self.audit_path = root / "institution_audit.csv"
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
            "provenance_source": "manually_confirmed",
            "mapping_status": "active",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
        })
        write_csv(self.mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [self.mapping])
        write_csv(self.locations_path, INSTITUTION_LOCATION_REVIEW_COLUMNS)
        write_csv(self.audit_path, INSTITUTION_AUDIT_COLUMNS)
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
                "parent_institution_id": "institution:correct" if identifier == "institution:wrong" else "",
                "public_display": "true",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
                "created_by": "test",
            })
            institutions.append(row)
        self.institutions = institutions
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

    def prepare_confirmed_change(self):
        current = dict(self.mapping)
        current.update({
            "institution": "Correct University",
            "institution_id": "institution:correct",
            "updated_at": "2026-02-01T00:00:00+00:00",
            "evidence_url": "https://example.test/evidence",
        })
        write_csv(self.mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [current])
        source_audit = {column: "" for column in INSTITUTION_AUDIT_COLUMNS}
        source_audit.update({
            "audit_id": "institution-audit:change-1",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:correct",
            "previous_institution_id": "institution:wrong",
            "affected_papers": "1",
            "affected_mappings": "1",
            "affected_markers": "1",
            "affected_authors": "Ada Example",
            "confirmation_text": "mapping_id=mapping:1; paper_id=paper:1; paper_title=Example paper; previous_institution=Wrong Lab; new_institution=Correct University; change_source=admin_mapping_update",
            "review_note": "Publisher evidence checked.",
            "created_at": "2026-02-01T00:00:00Z",
            "created_by": "local-admin",
        })
        write_csv(self.audit_path, INSTITUTION_AUDIT_COLUMNS, [source_audit])
        finding = {
            **self.finding,
            "audit_id": source_audit["audit_id"],
            "current_institution": "Correct University",
            "current_institution_id": "institution:correct",
            "suggested_canonical_institution": "",
            "suggested_institution_id": "",
            "issue_type": "confirmed_mapping_changed",
            "reason": "Trusted mapping changed.",
            "recommended_action": "Confirm or revert the change.",
        }
        sync_findings([finding], path=self.queue_path, now="2026-02-01T00:01:00+00:00")
        queue = load_queue(self.queue_path)[0]
        expected = {
            "expected_mapping_id": "mapping:1",
            "expected_institution_id": "institution:correct",
            "expected_mapping_updated_at": current["updated_at"],
            "expected_review_updated_at": queue["updated_at"],
        }
        return current, source_audit, queue, expected

    def test_confirm_intentional_change_is_atomic_and_audited(self):
        current, _, queue, expected = self.prepare_confirmed_change()
        result = apply_cleanup_action(
            [queue["queue_id"]], "mapping_change_confirmed", "Intentional and evidence-backed.",
            confirmed=True, resolved_by="local-admin", queue_path=self.queue_path,
            mappings_path=self.mappings_path, location_review_path=self.locations_path,
            institutions_path=self.institutions_path, institution_audit_path=self.audit_path,
            **expected,
        )
        self.assertEqual(load_mappings(self.mappings_path)[0]["institution_id"], "institution:correct")
        resolved = load_queue(self.queue_path)[0]
        self.assertEqual(resolved["resolution_action"], "mapping_change_confirmed")
        self.assertEqual(resolved["resolution_note"], "Intentional and evidence-backed.")
        self.assertEqual(resolved["is_current"], "false")
        self.assertEqual(result["audit"]["action"], "mapping_change_confirmed")
        self.assertIn(f"review_queue_id={queue['queue_id']}", result["audit"]["confirmation_text"])
        issues = []
        validate_institution_consistency_audit(issues, load_queue(self.queue_path), [current])
        self.assertEqual(issues, [])

    def test_revert_mapping_preserves_mapping_id_and_resolves(self):
        _, _, queue, expected = self.prepare_confirmed_change()
        result = apply_cleanup_action(
            [queue["queue_id"]], "mapping_reverted", "The earlier trusted mapping is correct.",
            confirmed=True, resolved_by="local-admin", queue_path=self.queue_path,
            mappings_path=self.mappings_path, location_review_path=self.locations_path,
            institutions_path=self.institutions_path, institution_audit_path=self.audit_path,
            **expected,
        )
        mappings = load_mappings(self.mappings_path)
        self.assertEqual(len(mappings), 1)
        self.assertEqual(mappings[0]["mapping_id"], "mapping:1")
        self.assertEqual(mappings[0]["institution_id"], "institution:wrong")
        self.assertEqual(load_queue(self.queue_path)[0]["resolution_action"], "mapping_reverted")
        self.assertEqual(result["audit"]["action"], "mapping_reverted")
        self.assertEqual(result["reaudit"], "scheduled_for_next_full_refresh")

    def test_mapping_change_resolution_requires_note(self):
        _, _, queue, expected = self.prepare_confirmed_change()
        with self.assertRaisesRegex(InstitutionReviewQueueError, "resolution note is required"):
            apply_cleanup_action(
                [queue["queue_id"]], "mapping_change_confirmed", "", confirmed=True,
                queue_path=self.queue_path, mappings_path=self.mappings_path,
                location_review_path=self.locations_path, institutions_path=self.institutions_path,
                institution_audit_path=self.audit_path, **expected,
            )

    def test_stale_mapping_change_resolution_is_rejected(self):
        _, _, queue, expected = self.prepare_confirmed_change()
        expected["expected_mapping_updated_at"] = "stale"
        with self.assertRaisesRegex(InstitutionReviewQueueError, "refresh"):
            apply_cleanup_action(
                [queue["queue_id"]], "mapping_change_confirmed", "Checked.", confirmed=True,
                queue_path=self.queue_path, mappings_path=self.mappings_path,
                location_review_path=self.locations_path, institutions_path=self.institutions_path,
                institution_audit_path=self.audit_path, **expected,
            )
        self.assertEqual(load_queue(self.queue_path)[0]["finding_status"], "open")

    def test_revert_rolls_back_when_resolution_audit_write_fails(self):
        current, _, queue, expected = self.prepare_confirmed_change()
        before = {path: path.read_bytes() for path in (self.queue_path, self.mappings_path, self.audit_path)}
        with patch(
            "scripts.institution_cleanup.append_mapping_change_resolution_audit",
            side_effect=OSError("simulated audit failure"),
        ):
            with self.assertRaisesRegex(OSError, "simulated audit failure"):
                apply_cleanup_action(
                    [queue["queue_id"]], "mapping_reverted", "Revert after review.", confirmed=True,
                    queue_path=self.queue_path, mappings_path=self.mappings_path,
                    location_review_path=self.locations_path, institutions_path=self.institutions_path,
                    institution_audit_path=self.audit_path, **expected,
                )
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        self.assertEqual(load_mappings(self.mappings_path)[0]["institution_id"], current["institution_id"])

    def test_mapping_change_payload_has_structured_transition_and_visibility(self):
        _, source_audit, _, _ = self.prepare_confirmed_change()
        payload = queue_payload(
            load_queue(self.queue_path), load_mappings(self.mappings_path), self.institutions,
            audits=[source_audit], public_records=[{
                "paper_id": "paper:1", "institution_id": "institution:correct",
                "institution": "Correct University",
            }],
        )
        change = payload["records"][0]["mapping_change"]
        self.assertEqual(change["previous_institution_id"], "institution:wrong")
        self.assertEqual(change["new_institution_id"], "institution:correct")
        self.assertEqual(change["change_source"], "admin_mapping_update")
        self.assertEqual(change["actor"], "local-admin")
        self.assertTrue(change["publicly_visible"])

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
        row = load_queue(self.queue_path)[0]
        self.assertEqual(row["finding_status"], "resolved")
        self.assertEqual(row["resolution_action"], "accept_suggestion")

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
        self.finding["issue_type"] = "suspicious_replacement"
        sync_findings([self.finding], path=self.queue_path)
        issues = []
        validate_institution_consistency_audit(issues, load_queue(self.queue_path))
        self.assertEqual([issue.level for issue in issues], ["ERROR"])

    def test_same_paper_author_findings_form_one_review_case_and_ignore_together(self):
        second = {
            **self.finding,
            "audit_id": "audit:2",
            "current_institution": "Another Lab",
            "current_institution_id": "institution:another",
            "severity": "medium",
            "issue_type": "author_institution_conflict",
        }
        sync_findings([self.finding, second], path=self.queue_path)
        payload = queue_payload(load_queue(self.queue_path), [self.mapping])
        self.assertEqual(len(payload["records"]), 1)
        review_case = payload["records"][0]
        self.assertEqual(len(review_case["findings"]), 2)
        apply_cleanup_action(
            review_case["queue_ids"], "ignore", "Both child findings reviewed.",
            queue_path=self.queue_path,
        )
        self.assertEqual(
            {row["finding_status"] for row in load_queue(self.queue_path)},
            {"resolved"},
        )

    def test_noncorruption_high_finding_does_not_block_publish(self):
        self.finding["issue_type"] = "author_institution_conflict"
        sync_findings([self.finding], path=self.queue_path)
        issues = []
        validate_institution_consistency_audit(issues, load_queue(self.queue_path))
        self.assertEqual(issues, [])

    def test_confirmed_replacement_records_before_after_source_user_and_time(self):
        sync_findings([self.finding], path=self.queue_path)
        queue_id = load_queue(self.queue_path)[0]["queue_id"]
        apply_cleanup_action(
            [queue_id], "accept_suggestion", "Confirmed replacement.",
            confirmed=True,
            resolved_by="curator@example.test",
            queue_path=self.queue_path,
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
            institutions_path=self.institutions_path,
            institution_audit_path=self.audit_path,
        )
        with self.audit_path.open(encoding="utf-8", newline="") as handle:
            event = next(csv.DictReader(handle))
        self.assertEqual(event["action"], "confirmed_mapping_changed")
        self.assertEqual(event["previous_institution_id"], "institution:wrong")
        self.assertEqual(event["institution_id"], "institution:correct")
        self.assertIn("change_source=institution_cleanup:accept_suggestion", event["confirmation_text"])
        self.assertEqual(event["created_by"], "curator@example.test")
        self.assertTrue(event["created_at"])

    def test_location_only_mapping_edit_does_not_create_change_event(self):
        draft = {**self.mapping, "institution_city": "Rome"}
        update_mapping(
            self.mapping, "mapping:1", draft,
            map_records=(),
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
            institutions_path=self.institutions_path,
            institution_audit_path=self.audit_path,
            change_source="location_edit",
        )
        with self.audit_path.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(list(csv.DictReader(handle)), [])

    def test_empty_manual_resolution_note_uses_default(self):
        sync_findings([self.finding], path=self.queue_path)
        queue_id = load_queue(self.queue_path)[0]["queue_id"]
        apply_cleanup_action(
            [queue_id], "manually_resolved", "",
            queue_path=self.queue_path,
        )
        row = load_queue(self.queue_path)[0]
        self.assertEqual(row["finding_status"], "resolved")
        self.assertEqual(row["resolution_action"], "manually_resolved")
        self.assertEqual(
            row["resolution_note"],
            "Confirmed existing curated institution mapping after manual review.",
        )

    def test_replace_mapping_still_requires_explanation(self):
        sync_findings([self.finding], path=self.queue_path)
        queue_id = load_queue(self.queue_path)[0]["queue_id"]
        with self.assertRaisesRegex(
            InstitutionReviewQueueError, "review note is required"
        ):
            apply_cleanup_action(
                [queue_id], "replace_mapping", "",
                replacement_institution_id="institution:correct",
                confirmed=True,
                queue_path=self.queue_path,
                mappings_path=self.mappings_path,
                location_review_path=self.locations_path,
                institutions_path=self.institutions_path,
            )

    def test_batch_manual_resolution_creates_audit_records(self):
        second = {**self.finding, "audit_id": "audit:batch:2"}
        sync_findings([self.finding, second], path=self.queue_path)
        queue_ids = [row["queue_id"] for row in load_queue(self.queue_path)]
        result = apply_cleanup_action(
            queue_ids, "manually_resolved", "Batch resolution: trusted mappings retained.",
            queue_path=self.queue_path,
        )
        self.assertEqual(len(result["resolved"]), 2)
        rows = load_queue(self.queue_path)
        self.assertEqual({row["resolution_action"] for row in rows}, {"manually_resolved"})
        self.assertEqual(
            {row["resolution_note"] for row in rows},
            {"Batch resolution: trusted mappings retained."},
        )
        self.assertTrue(all(row["resolved_at"] for row in rows))

    def test_evidence_payload_includes_provenance_affiliation_alias_and_parent_without_writes(self):
        self.finding["issue_type"] = "suspicious_replacement"
        sync_findings([self.finding], path=self.queue_path)
        aliases = [{
            "alias_name": "Wrong Laboratory",
            "institution_id": "institution:wrong",
            "review_status": "confirmed",
        }]
        papers = [{
            "paper_id": "paper:1",
            "title": "Example paper",
            "year": "2025",
            "venue": "Example Conference",
            "doi": "10.1234/example",
            "arxiv_id": "2501.00001",
            "paper_url": "https://example.test/paper",
            "authors": [{"name": "Ada Example", "id": "https://openalex.org/A1"}],
        }]
        protected = {
            path: path.read_bytes()
            for path in (self.queue_path, self.mappings_path, self.institutions_path)
        }
        payload = queue_payload(
            load_queue(self.queue_path),
            [self.mapping],
            self.institutions,
            aliases,
            [],
            papers,
        )
        evidence = payload["records"][0]["evidence_detail"]
        self.assertEqual(evidence["paper"]["venue"], "Example Conference")
        self.assertEqual(evidence["author"]["author_id"], "https://openalex.org/A1")
        self.assertEqual(
            evidence["current_mappings"][0]["provenance_source"],
            "manually_confirmed",
        )
        self.assertIn(
            "Ada Example, Correct University",
            evidence["affiliation"]["raw_affiliations"],
        )
        relationship = next(
            row for row in evidence["relationships"]
            if row["institution_id"] == "institution:wrong"
        )
        self.assertIn("Wrong Laboratory", relationship["aliases"])
        self.assertEqual(
            relationship["parent"]["canonical_name"], "Correct University"
        )
        self.assertEqual(evidence["comparison"]["before"], ["Wrong Lab"])
        self.assertEqual(evidence["comparison"]["after"], ["Correct University"])
        self.assertEqual(
            protected,
            {path: path.read_bytes() for path in protected},
        )

    def test_excluded_mapping_moves_from_current_display_to_history_and_stays_resolved(self):
        active = {
            **self.mapping,
            "mapping_id": "mapping:hunan",
            "institution": "Hunan University",
            "institution_id": "institution:hunan",
            "mapping_status": "active",
        }
        excluded = {
            **self.mapping,
            "mapping_id": "mapping:changsha",
            "institution": "Changsha University",
            "institution_id": "institution:changsha",
            "mapping_status": "excluded",
        }
        changsha_finding = {
            **self.finding,
            "audit_id": "audit:changsha",
            "mapping_id": "mapping:changsha",
            "current_institution": "Changsha University",
            "current_institution_id": "institution:changsha",
            "issue_type": "suspicious_replacement",
        }
        hunan_finding = {
            **self.finding,
            "audit_id": "audit:hunan",
            "mapping_id": "mapping:hunan",
            "current_institution": "Hunan University",
            "current_institution_id": "institution:hunan",
            "severity": "low",
            "issue_type": "alias_missing",
        }
        write_csv(
            self.mappings_path,
            AUTHOR_INSTITUTION_MAPPING_COLUMNS,
            [active, excluded],
        )
        sync_findings(
            [changsha_finding, hunan_finding], path=self.queue_path
        )
        result = reconcile_mapping_changes(
            [active, excluded], path=self.queue_path,
            now="2026-07-14T12:00:00+00:00",
        )
        self.assertEqual(result["resolved"], 1)

        rows = load_queue(self.queue_path)
        historical = next(row for row in rows if row["audit_id"] == "audit:changsha")
        self.assertEqual(historical["finding_status"], "archived")
        self.assertEqual(historical["resolution_action"], "mapping_excluded")
        self.assertEqual(historical["is_current"], "false")

        payload = queue_payload(rows, [active, excluded])
        review_case = payload["records"][0]
        self.assertEqual(review_case["current_institutions"], ["Hunan University"])
        self.assertEqual(
            review_case["historical_institutions"], ["Changsha University"]
        )
        archived_case = payload["archived_records"][0]
        self.assertEqual(archived_case["status"], "archived")
        self.assertEqual(
            archived_case["historical_institutions"], ["Changsha University"]
        )

        # A stale generated report cannot reopen an excluded mapping finding.
        sync_findings(
            [changsha_finding, hunan_finding],
            mappings=[active, excluded],
            path=self.queue_path,
        )
        rows = load_queue(self.queue_path)
        historical = next(row for row in rows if row["audit_id"] == "audit:changsha")
        self.assertEqual(historical["finding_status"], "archived")
        self.assertEqual(historical["is_current"], "false")
        issues = []
        validate_institution_consistency_audit(issues, rows, [active, excluded])
        self.assertEqual(issues, [])

    def test_dtbf_excluded_changsha_finding_is_archived_not_actionable(self):
        active = {
            **self.mapping,
            "mapping_id": "mapping:hunan",
            "title": "DTBF",
            "institution": "Hunan University",
            "institution_id": "institution:hunan",
            "institution_authors": "Gaobo Yang",
            "mapping_status": "active",
        }
        excluded = {
            **self.mapping,
            "mapping_id": "mapping:changsha",
            "title": "DTBF",
            "institution": "Changsha University",
            "institution_id": "institution:changsha",
            "institution_authors": "Gaobo Yang",
            "mapping_status": "excluded",
            "review_note": "[2026-07-14T10:00:00+00:00] Replaced: corrected affiliation",
        }
        stale_finding = {
            **self.finding,
            "audit_id": "audit:dtbf:changsha",
            "mapping_id": "mapping:changsha",
            "paper_title": "DTBF",
            "author": "Gaobo Yang",
            "current_institution": "Changsha University",
            "current_institution_id": "institution:changsha",
            "severity": "high",
            "issue_type": "suspicious_replacement",
        }
        sync_findings([stale_finding], path=self.queue_path)
        reconcile_mapping_changes(
            [active, excluded], path=self.queue_path,
            now="2026-07-14T12:00:00+00:00",
        )

        rows = load_queue(self.queue_path)
        payload = queue_payload(rows, [active, excluded])
        self.assertEqual(payload["records"], [])
        self.assertEqual(payload["blocking_count"], 0)
        self.assertEqual(len(payload["archived_records"]), 1)
        history = payload["archived_records"][0]
        self.assertEqual(history["paper_title"], "DTBF")
        self.assertEqual(history["current_institutions"], ["Hunan University"])
        self.assertEqual(history["historical_institutions"], ["Changsha University"])
        self.assertEqual(
            history["evidence_detail"]["historical_mappings"][0]["institution_name"],
            "Changsha University",
        )
        issues = []
        validate_institution_consistency_audit(issues, rows, [active, excluded])
        self.assertEqual(issues, [])

    def test_replaced_mapping_archives_finding_and_preserves_resolution_audit(self):
        sync_findings([self.finding], path=self.queue_path)
        replacement = {
            **self.mapping,
            "institution": "Correct University",
            "institution_id": "institution:correct",
        }
        reconcile_mapping_changes(
            [replacement], path=self.queue_path,
            now="2026-07-14T13:00:00+00:00",
        )
        row = load_queue(self.queue_path)[0]
        self.assertEqual(row["finding_status"], "archived")
        self.assertEqual(row["resolution_action"], "mapping_replaced")
        self.assertIn("prior finding retained", row["resolution_note"])
        self.assertEqual(row["resolved_at"], "2026-07-14T13:00:00+00:00")
        self.assertEqual(row["resolved_by"], "mapping-sync")
        self.assertEqual(queue_payload([row], [replacement])["records"], [])

    def test_legacy_terminal_status_migrates_without_losing_audit_timestamps(self):
        row = {column: "" for column in INSTITUTION_REVIEW_QUEUE_COLUMNS}
        row.update({
            "queue_id": "institution-review:legacy",
            "audit_id": "audit:legacy",
            "severity": "high",
            "issue_type": "suspicious_replacement",
            "reason": "Legacy resolved case.",
            "finding_status": "manually_resolved",
            "resolution_action": "manually_resolved",
            "resolution_note": "Reviewed by curator.",
            "is_current": "false",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-02T00:00:00+00:00",
            "resolved_at": "2026-01-02T00:00:00+00:00",
            "resolved_by": "curator",
        })
        write_csv(self.queue_path, INSTITUTION_REVIEW_QUEUE_COLUMNS, [row])
        migrated = load_queue(self.queue_path)[0]
        self.assertEqual(migrated["finding_status"], "archived")
        self.assertEqual(migrated["resolution_action"], "manually_resolved")
        self.assertEqual(migrated["created_at"], row["created_at"])
        self.assertEqual(migrated["resolved_at"], row["resolved_at"])


if __name__ == "__main__":
    unittest.main()
