"""Verify the final evidence ledger against canonical data and duplicate rows."""
from scripts.audit_pending_institution_resolution import verify


def test_reviewed_decisions_preserve_alias_targets_and_paper_provenance():
    summary = verify()
    assert summary["ambiguous"] == 0
