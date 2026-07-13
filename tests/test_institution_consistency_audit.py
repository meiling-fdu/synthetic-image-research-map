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


def mapping(identifier, institution, raw, author="Example Author", paper="paper:1"):
    return {
        "mapping_id": f"mapping:{identifier}:{author}",
        "paper_id": paper,
        "title": "Example paper",
        "year": "2026",
        "institution_id": identifier,
        "institution": institution,
        "institution_authors": author,
        "raw_affiliation": raw,
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

    def test_ignored_institution_does_not_block(self):
        ignored = entity("institution:ignored", "Wrong Institution", status="ignored")
        findings = audit_institution_consistency(
            [mapping("institution:ignored", "Wrong Institution", "Amazon")],
            [*self.entities, ignored], self.aliases,
        )
        self.assertFalse(unresolved_high(findings))

    def test_same_author_unrelated_mapping_is_high_collision(self):
        findings = self.audit([
            mapping("institution:naples", "University of Naples Federico II", "University Federico II of Naples", author="Luisa Verdoliva"),
            mapping("institution:amazon", "Amazon", "University Federico II of Naples", author="Luisa Verdoliva"),
        ])
        collision = next(row for row in findings if row["issue_type"] == "author_institution_conflict")
        self.assertEqual(collision["severity"], "high")

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

    def test_admin_exposes_review_only_institution_audit_actions(self):
        html = (self.root / "web/admin.html").read_text(encoding="utf-8")
        javascript = (self.root / "web/admin.js").read_text(encoding="utf-8")
        self.assertIn("Institution Cleanup", html)
        for label in ("Accept suggestion", "Replace mapping", "Ignore finding", "Open institution editor", "Mark manually resolved"):
            self.assertIn(label, javascript)
        self.assertIn("Accept selected fixes", html)

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
            "severity": "high", "finding_status": "ignored", "is_current": "true",
            "issue_type": "author_institution_conflict", "author": "Resolved",
            "paper_title": "Example", "reason": "Reviewed",
        }])
        self.assertEqual([issue.level for issue in issues], ["ERROR", "WARNING"])


if __name__ == "__main__":
    unittest.main()
