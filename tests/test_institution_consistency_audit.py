import unittest
from pathlib import Path

from scripts.institution_consistency import (
    audit_institution_consistency,
    names_semantically_related,
    unresolved_high,
)


def entity(identifier, name, *, status="active", parent=""):
    return {
        "institution_id": identifier,
        "canonical_name": name,
        "institution_status": status,
        "parent_institution_id": parent,
    }


def mapping(identifier, institution, raw, author="Example Author", paper="paper:1", provenance="curated_import"):
    return {
        "mapping_id": f"mapping:{identifier}:{author}",
        "paper_id": paper,
        "title": "Example paper",
        "year": "2026",
        "institution_id": identifier,
        "institution": institution,
        "institution_authors": author,
        "raw_affiliation": raw,
        "provenance_source": provenance,
        "mapping_status": "active",
    }


class InstitutionConsistencyAuditTests(unittest.TestCase):
    def setUp(self):
        self.amazon = entity("institution:amazon", "Amazon")
        self.amazon_prime = entity("institution:prime", "Amazon Prime Video")
        self.certh = entity("institution:certh", "Centre for Research and Technology Hellas (CERTH)")
        self.naples = entity("institution:naples", "University of Naples Federico II")
        self.parent = entity("institution:parent", "Example University")
        self.child = entity("institution:child", "Vision Laboratory", parent="institution:parent")
        self.entities = [self.amazon, self.amazon_prime, self.certh, self.naples, self.parent, self.child]
        self.aliases = [{
            "alias_name": "University Federico II of Naples",
            "institution_id": "institution:naples",
            "review_status": "confirmed",
        }, {
            "alias_name": "Information Technologies Institute",
            "institution_id": "institution:certh",
            "review_status": "confirmed",
        }]

    def audit(self, rows, **kwargs):
        return audit_institution_consistency(rows, self.entities, self.aliases, **kwargs)

    def test_certh_affiliation_cannot_map_to_amazon(self):
        findings = self.audit([mapping(
            "institution:amazon", "Amazon",
            "Information Technologies Institute, Centre for Research and Technology Hellas (CERTH)",
        )])
        finding = next(row for row in findings if row["issue_type"] == "suspicious_replacement")
        self.assertEqual(finding["severity"], "high")
        self.assertEqual(finding["suggested_institution_id"], "institution:certh")

    def test_luisa_naples_affiliation_cannot_map_to_amazon(self):
        findings = self.audit([mapping(
            "institution:amazon", "Amazon", "University Federico II of Naples",
            author="Luisa Verdoliva",
        )])
        self.assertTrue(unresolved_high(findings))
        self.assertEqual(findings[0]["suggested_institution_id"], "institution:naples")

    def test_automatic_university_to_amazon_mismatch_is_high(self):
        findings = self.audit([mapping(
            "institution:amazon", "Amazon", "University Federico II of Naples",
            provenance="automatic_import",
        )])
        finding = next(row for row in findings if row["issue_type"] == "suspicious_replacement")
        self.assertEqual(finding["severity"], "high")
        self.assertEqual(finding["provenance"], "automatic_import")

    def test_university_to_research_institute_mismatch_is_medium(self):
        institute = entity("institution:institute", "Example Research Institute")
        findings = audit_institution_consistency(
            [mapping(
                "institution:naples", "University of Naples Federico II",
                "Example Research Institute", provenance="automatic_import",
            )],
            [*self.entities, institute], self.aliases,
        )
        finding = next(row for row in findings if row["suggested_institution_id"] == "institution:institute")
        self.assertEqual(finding["severity"], "medium")
        self.assertEqual(finding["is_blocking"], "false")

    def test_amazon_prime_video_affiliation_is_compatible(self):
        findings = self.audit([mapping(
            "institution:prime", "Amazon Prime Video",
            "Amazon Prime Video, Sunnyvale, CA, USA",
        )])
        self.assertFalse(any(row["issue_type"] in {"affiliation_mismatch", "suspicious_replacement"} for row in findings))

    def test_naples_name_variants_pass_through_confirmed_alias(self):
        findings = self.audit([mapping(
            "institution:naples", "University of Naples Federico II",
            "Department of Engineering, University Federico II of Naples",
        )])
        self.assertEqual(findings, [])
        self.assertTrue(names_semantically_related(
            "University Federico II of Naples", "University of Naples Federico II"
        ))

    def test_child_institution_passes_with_parent_affiliation(self):
        findings = self.audit([mapping(
            "institution:child", "Vision Laboratory",
            "Department of Computer Science, Example University",
        )])
        self.assertFalse(unresolved_high(findings))
        self.assertFalse(any(row["issue_type"] == "affiliation_mismatch" for row in findings))

    def test_cnrs_and_gipsa_parent_child_relationship_is_not_blocking(self):
        cnrs = entity("institution:cnrs", "CNRS")
        gipsa = entity("institution:gipsa", "GIPSA-Lab", parent="institution:cnrs")
        findings = audit_institution_consistency(
            [mapping("institution:gipsa", "GIPSA-Lab", "CNRS, GIPSA-Lab, Université Grenoble Alpes")],
            [*self.entities, cnrs, gipsa], self.aliases,
        )
        self.assertFalse(unresolved_high(findings))

    def test_ignored_institution_does_not_block(self):
        ignored = entity("institution:ignored", "Wrong Institution", status="ignored")
        findings = audit_institution_consistency(
            [mapping("institution:ignored", "Wrong Institution", "Amazon")],
            [*self.entities, ignored], self.aliases,
        )
        self.assertFalse(unresolved_high(findings))

    def test_same_author_unrelated_mapping_is_grouped_nonblocking_collision(self):
        findings = self.audit([
            mapping("institution:naples", "University of Naples Federico II", "University Federico II of Naples", author="Luisa Verdoliva"),
            mapping("institution:amazon", "Amazon", "University Federico II of Naples", author="Luisa Verdoliva"),
        ])
        collision = next(row for row in findings if row["issue_type"] == "author_institution_conflict")
        self.assertEqual(collision["severity"], "low")
        self.assertEqual(collision["classification"], "possible multiple affiliation")
        self.assertEqual(collision["is_blocking"], "false")

    def test_manually_confirmed_alias_variation_is_not_high(self):
        findings = self.audit([mapping(
            "institution:naples", "University of Naples Federico II",
            "Department of Electrical Engineering, University Federico II of Naples",
            provenance="manually_confirmed",
        )])
        self.assertFalse(unresolved_high(findings))

    def test_explicit_curated_replacement_makes_stale_public_row_nonblocking(self):
        current = mapping(
            "institution:naples", "University of Naples Federico II",
            "University Federico II of Naples", provenance="manually_confirmed",
        )
        stale = {
            **current, "institution": "Amazon", "institution_id": "institution:amazon",
            "institution_authors": ["Example Author"], "mapping_id": "",
        }
        findings = self.audit([current], public_records=[stale])
        self.assertFalse(any(
            row["issue_type"] == "suspicious_replacement"
            and row["reason"].startswith("Why flagged: public export")
            for row in findings
        ))

    def test_confirmed_mapping_change_event_is_high(self):
        current = mapping(
            "institution:amazon", "Amazon", "Centre for Research and Technology Hellas",
            author="Symeon Papadopoulos", provenance="manually_confirmed",
        )
        findings = self.audit([current], merge_audits=[{
            "audit_id": "mapping-change:1",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "affected_authors": "Symeon Papadopoulos",
            "confirmation_text": "mapping_id=mapping:institution:amazon:Symeon Papadopoulos; previous_institution=Centre for Research and Technology Hellas; new_institution=Amazon; change_source=automatic_import",
            "created_at": "2026-07-14T00:00:00Z",
            "created_by": "import-job",
        }])
        changed = next(row for row in findings if row["issue_type"] == "confirmed_mapping_changed")
        self.assertEqual(changed["severity"], "high")
        self.assertEqual(changed["is_blocking"], "true")

    def test_confirmed_transition_is_not_reopened_but_later_change_is(self):
        current = mapping(
            "institution:amazon", "Amazon", "Centre for Research and Technology Hellas",
            author="Symeon Papadopoulos", provenance="manually_confirmed",
        )
        first = {
            "audit_id": "mapping-change:1",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "affected_authors": "Symeon Papadopoulos",
            "confirmation_text": "mapping_id=mapping:institution:amazon:Symeon Papadopoulos; previous_institution=CERTH; new_institution=Amazon; change_source=admin_mapping_update",
        }
        resolution = {
            "audit_id": "mapping-resolution:1",
            "action": "mapping_change_confirmed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "confirmation_text": (
                "source_audit_id=mapping-change:1; "
                "mapping_id=mapping:institution:amazon:Symeon Papadopoulos; "
                "paper_id=paper:1; author=Symeon Papadopoulos"
            ),
        }
        findings = self.audit([current], merge_audits=[first, resolution])
        self.assertFalse(any(row["issue_type"] == "confirmed_mapping_changed" for row in findings))
        later = {
            **first,
            "audit_id": "mapping-change:2",
            "institution_id": "institution:naples",
            "previous_institution_id": "institution:amazon",
            "confirmation_text": "mapping_id=mapping:institution:amazon:Symeon Papadopoulos; previous_institution=Amazon; new_institution=Naples; change_source=admin_mapping_update",
        }
        later_findings = self.audit([current], merge_audits=[first, resolution, later])
        self.assertTrue(any(
            row["issue_type"] == "confirmed_mapping_changed" and row["audit_id"] == "mapping-change:2"
            for row in later_findings
        ))

    def test_identical_regenerated_transition_uses_prior_mapping_wide_confirmation(self):
        current = mapping(
            "institution:amazon", "Amazon", "Centre for Research and Technology Hellas",
            author="Ada Example; Bob Reviewer", provenance="manually_confirmed",
        )
        original = {
            "audit_id": "mapping-change:original",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "previous_mapping_id": current["mapping_id"],
            "mapping_id": current["mapping_id"],
            "paper_id": "paper:1",
            "new_authors": "Ada Example; Bob Reviewer",
        }
        resolution = {
            "audit_id": "mapping-resolution:original",
            "action": "mapping_change_confirmed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "previous_mapping_id": current["mapping_id"],
            "mapping_id": current["mapping_id"],
            "paper_id": "paper:1",
            "new_authors": "Ada Example; Bob Reviewer",
            "confirmation_text": "source_audit_id=mapping-change:original",
        }
        regenerated = {
            **original,
            "audit_id": "mapping-change:regenerated",
            "new_authors": "Ada Example",
            "affected_authors": "Ada Example",
        }
        findings = self.audit(
            [current], merge_audits=[original, resolution, regenerated]
        )
        self.assertFalse(any(
            row["issue_type"] == "confirmed_mapping_changed"
            and row["audit_id"] == "mapping-change:regenerated"
            for row in findings
        ))

    def test_prior_confirmation_does_not_cross_stable_transition_dimensions(self):
        current = mapping(
            "institution:amazon", "Amazon", "Centre for Research and Technology Hellas",
            author="Ada Example; Bob Reviewer", provenance="manually_confirmed",
        )
        mapping_id = current["mapping_id"]
        resolution = {
            "audit_id": "mapping-resolution:prior",
            "action": "mapping_change_confirmed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "previous_mapping_id": mapping_id,
            "mapping_id": mapping_id,
            "paper_id": "paper:1",
            "new_authors": "Ada Example; Bob Reviewer",
            "confirmation_text": "source_audit_id=mapping-change:prior",
        }
        base = {
            "audit_id": "mapping-change:regenerated",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "previous_mapping_id": mapping_id,
            "mapping_id": mapping_id,
            "paper_id": "paper:1",
            "new_authors": "Ada Example; Bob Reviewer",
        }
        variants = {
            "old institution": {"previous_institution_id": "institution:naples"},
            "new institution": {"institution_id": "institution:prime"},
            "paper": {"paper_id": "paper:other"},
            "mapping": {
                "mapping_id": "mapping:other",
                "previous_mapping_id": "mapping:other",
            },
            "mapping lineage": {"previous_mapping_id": "mapping:other"},
        }
        for label, changes in variants.items():
            with self.subTest(label=label):
                regenerated = {**base, **changes, "audit_id": f"mapping-change:{label}"}
                findings = self.audit([current], merge_audits=[resolution, regenerated])
                self.assertTrue(any(
                    row["issue_type"] == "confirmed_mapping_changed"
                    and row["audit_id"] == regenerated["audit_id"]
                    for row in findings
                ))

        wrong_authors = {**resolution, "new_authors": "Ada Example"}
        findings = self.audit([current], merge_audits=[wrong_authors, base])
        self.assertTrue(any(
            row["issue_type"] == "confirmed_mapping_changed"
            and row["audit_id"] == base["audit_id"]
            for row in findings
        ))

    def test_explicit_merge_allows_former_name(self):
        old = entity("institution:old", "Old Research Center", status="merged")
        new = entity("institution:new", "New Research Institute")
        findings = audit_institution_consistency(
            [mapping("institution:new", "New Research Institute", "Old Research Center")],
            [old, new], [],
            merge_audits=[{
                "action": "merge",
                "previous_institution_id": "institution:old",
                "institution_id": "institution:new",
            }],
        )
        self.assertFalse(unresolved_high(findings))
        self.assertFalse(any(row["issue_type"] == "affiliation_mismatch" for row in findings))

    def test_confirmed_mapping_migrated_by_exact_merge_is_not_reopened(self):
        old = entity("institution:old", "Old Research Center", status="merged")
        new = entity("institution:new", "New Research Institute")
        change = {
            "audit_id": "mapping-change:merge",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:new",
            "previous_institution_id": "institution:old",
            "affected_authors": "Example Author",
            "confirmation_text": (
                "mapping_id=mapping:institution:new:Example Author; "
                "previous_institution=Old Research Center; "
                "new_institution=New Research Institute; "
                "change_source=global_merge"
            ),
        }
        merge = {
            "audit_id": "institution-merge:1",
            "action": "merge",
            "previous_institution_id": "institution:old",
            "institution_id": "institution:new",
        }
        findings = audit_institution_consistency(
            [mapping("institution:new", "New Research Institute", "Old Research Center")],
            [old, new], [], merge_audits=[merge, change],
        )
        self.assertFalse(any(
            row["issue_type"] == "confirmed_mapping_changed" for row in findings
        ))

    def test_confirmed_mapping_removed_with_exact_review_decision_is_not_reopened(self):
        current = mapping(
            "institution:certh", "Centre for Research and Technology Hellas (CERTH)",
            "Centre for Research and Technology Hellas", provenance="manually_confirmed",
        )
        change = {
            "audit_id": "mapping-change:removed",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "affected_authors": "Example Author",
            "confirmation_text": (
                "mapping_id=mapping:institution:certh:Example Author; "
                "previous_institution=CERTH; new_institution=Amazon; "
                "change_source=admin_mapping_update"
            ),
        }
        decision = {
            "audit_id": "mapping-resolution:removed",
            "action": "mapping_reverted",
            "institution_id": "institution:certh",
            "previous_institution_id": "institution:amazon",
            "confirmation_text": (
                "source_audit_id=mapping-change:removed; "
                "mapping_id=mapping:institution:certh:Example Author; "
                "paper_id=paper:1; author=Example Author; "
                "evidence_source=Publisher PDF; "
                "evidence_url=https://example.test/paper.pdf"
            ),
            "review_note": "The replacement relationship was intentionally retired.",
        }
        findings = self.audit([current], merge_audits=[change, decision])
        self.assertFalse(any(
            row["issue_type"] == "confirmed_mapping_changed" for row in findings
        ))

    def test_confirmed_mapping_change_without_durable_evidence_still_fails(self):
        current = mapping(
            "institution:amazon", "Amazon", "Centre for Research and Technology Hellas",
            provenance="manually_confirmed",
        )
        change = {
            "audit_id": "mapping-change:unreviewed",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "affected_authors": "Example Author",
            "confirmation_text": (
                "mapping_id=mapping:institution:amazon:Example Author; "
                "previous_institution=CERTH; new_institution=Amazon; "
                "change_source=admin_mapping_update"
            ),
            "evidence_source": "Publisher PDF",
            "review_note": "Exact reviewed replacement described in prose.",
        }
        findings = self.audit([current], merge_audits=[change])
        changed = next(
            row for row in findings
            if row["issue_type"] == "confirmed_mapping_changed"
        )
        self.assertEqual(changed["is_blocking"], "true")

    def test_same_id_display_name_correction_is_not_identity_change(self):
        current = mapping(
            "institution:ubc", "The University of British Columbia",
            "University of British Columbia", author="Panos Nasiopoulos",
        )
        change = {
            "audit_id": "mapping-change:display",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:ubc",
            "previous_institution_id": "institution:ubc",
            "affected_authors": "Panos Nasiopoulos",
            "confirmation_text": (
                "mapping_id=mapping:institution:ubc:Panos Nasiopoulos; "
                "paper_id=paper:1; previous_institution=University of British Columbia; "
                "new_institution=The University of British Columbia; "
                "change_source=admin_mapping_update"
            ),
        }
        findings = self.audit([current], merge_audits=[change])
        self.assertFalse(any(
            row["issue_type"] == "confirmed_mapping_changed" for row in findings
        ))

    def test_mapping_confirmation_for_wrong_paper_does_not_resolve(self):
        current = mapping(
            "institution:amazon", "Amazon", "Centre for Research and Technology Hellas",
            author="Symeon Papadopoulos", provenance="manually_confirmed",
        )
        change = {
            "audit_id": "mapping-change:wrong-paper",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "affected_authors": "Symeon Papadopoulos",
            "confirmation_text": (
                "mapping_id=mapping:institution:amazon:Symeon Papadopoulos; "
                "paper_id=paper:1; previous_institution=CERTH; new_institution=Amazon; "
                "change_source=admin_mapping_update"
            ),
        }
        resolution = {
            "action": "mapping_change_confirmed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "affected_authors": "Symeon Papadopoulos",
            "confirmation_text": (
                "source_audit_id=mapping-change:wrong-paper; "
                "mapping_id=mapping:institution:amazon:Symeon Papadopoulos; "
                "paper_id=paper:other; author=Symeon Papadopoulos"
            ),
        }
        findings = self.audit([current], merge_audits=[change, resolution])
        self.assertTrue(any(
            row["issue_type"] == "confirmed_mapping_changed" for row in findings
        ))

    def test_mapping_confirmation_for_wrong_author_does_not_resolve(self):
        current = mapping(
            "institution:amazon", "Amazon", "Centre for Research and Technology Hellas",
            author="Symeon Papadopoulos", provenance="manually_confirmed",
        )
        change = {
            "audit_id": "mapping-change:wrong-author",
            "action": "confirmed_mapping_changed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "affected_authors": "Symeon Papadopoulos",
            "confirmation_text": (
                "mapping_id=mapping:institution:amazon:Symeon Papadopoulos; "
                "paper_id=paper:1; previous_institution=CERTH; new_institution=Amazon; "
                "change_source=admin_mapping_update"
            ),
        }
        resolution = {
            "action": "mapping_change_confirmed",
            "institution_id": "institution:amazon",
            "previous_institution_id": "institution:certh",
            "affected_authors": "Another Author",
            "confirmation_text": (
                "source_audit_id=mapping-change:wrong-author; "
                "mapping_id=mapping:institution:amazon:Symeon Papadopoulos; "
                "paper_id=paper:1; author=Another Author"
            ),
        }
        findings = self.audit([current], merge_audits=[change, resolution])
        self.assertTrue(any(
            row["issue_type"] == "confirmed_mapping_changed" for row in findings
        ))

    def test_review_decision_resolves_without_changing_mapping(self):
        rows = [mapping("institution:amazon", "Amazon", "University Federico II of Naples", author="Luisa Verdoliva")]
        initial = self.audit(rows)
        audit_id = next(row["audit_id"] for row in initial if row["severity"] == "high")
        resolved = self.audit(rows, decisions=[{
            "review_queue": "institution_consistency",
            "target_type": f"institution_audit:{audit_id}",
            "action": "ignore_warning",
        }])
        self.assertFalse(unresolved_high(resolved))
        self.assertEqual(rows[0]["institution"], "Amazon")


class InstitutionConsistencyIntegrationTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def test_current_admin_mapping_replacements_are_not_stale_preview_blockers(self):
        from scripts.institution_consistency import run_repository_audit

        regression_titles = {
            "Fake or JPEG? Revealing Common Biases in Generated Image Detection Datasets",
            "WILD: a new in-the-Wild Image Linkage Dataset for synthetic image attribution",
        }
        stale_preview_findings = [
            row for row in run_repository_audit()
            if row["paper_title"] in regression_titles
            and row["issue_type"] == "suspicious_replacement"
            and row["reason"].startswith("Why flagged: public export")
        ]
        self.assertEqual(stale_preview_findings, [])

    def test_admin_exposes_review_only_institution_audit_actions(self):
        html = (self.root / "web/admin.html").read_text(encoding="utf-8")
        javascript = (self.root / "web/admin.js").read_text(encoding="utf-8")
        self.assertIn("Institution Cleanup", html)
        for label in ("Accept suggestion", "Replace mapping", "Ignore finding", "Open institution editor", "Mark manually resolved"):
            self.assertIn(label, javascript)
        self.assertIn("Accept selected fixes", html)
        self.assertIn('id="institution-resolution-dialog"', html)
        self.assertIn("Existing curated mapping is correct", html)
        self.assertIn("Alias/name variation only", html)
        self.assertIn("Parent-child relationship", html)
        self.assertIn("Multiple affiliation confirmed", html)
        self.assertIn("Resolve selected cases", html)
        self.assertNotIn('window.prompt(`${labels[action] || action} review note:`)', javascript)
        self.assertIn('id="institution-evidence-dialog"', html)
        self.assertIn("View evidence", javascript)
        self.assertIn("Provenance source", javascript)
        self.assertIn("Raw affiliation text", javascript)
        self.assertIn("Institution relationships", javascript)
        self.assertIn("Suspicious replacement comparison", javascript)
        self.assertIn("resolveInstitutionAudit(item, action)", javascript)
        self.assertIn('openMappingDialog("replace")', javascript)
        self.assertIn("Current active institutions", html)
        self.assertIn("Historical/excluded institutions", html)
        self.assertIn("Historical/excluded mappings", javascript)

    def test_full_refresh_generates_audit_before_curated_validation(self):
        from scripts.admin_workflows import ALLOWED_WORKFLOWS, KNOWN_WORKFLOW_OUTPUTS

        commands = ALLOWED_WORKFLOWS["full_refresh"]
        audit_index = next(i for i, command in enumerate(commands) if "scripts/audit_institution_consistency.py" in command)
        sync_index = next(i for i, command in enumerate(commands) if "scripts/sync_institution_review_queue.py" in command)
        validation_index = next(i for i, command in enumerate(commands) if "scripts/validate_curated_database.py" in command)
        self.assertLess(audit_index, sync_index)
        self.assertLess(sync_index, validation_index)
        self.assertTrue(any(path.name == "institution_consistency_audit.csv" for path in KNOWN_WORKFLOW_OUTPUTS))

    def test_publish_validation_blocks_only_unresolved_high_findings(self):
        from scripts.validate_curated_database import validate_institution_consistency_audit

        issues = []
        validate_institution_consistency_audit(issues, [{
            "severity": "high", "finding_status": "open", "is_current": "true",
            "issue_type": "suspicious_replacement", "author": "Luisa Verdoliva",
            "paper_title": "Example", "reason": "Naples cannot map to Amazon",
        }, {
            "severity": "medium", "finding_status": "open", "is_current": "true",
            "issue_type": "affiliation_mismatch", "author": "Example",
            "paper_title": "Example", "reason": "Review requested",
        }, {
            "severity": "high", "finding_status": "archived", "is_current": "true",
            "issue_type": "author_institution_conflict", "author": "Resolved",
            "paper_title": "Example", "reason": "Reviewed",
        }])
        self.assertEqual([issue.level for issue in issues], ["ERROR", "WARNING"])


if __name__ == "__main__":
    unittest.main()
