"""Retain all20 reviewed R2 cases against their authenticated archival snapshot."""
import hashlib
import json
from pathlib import Path

import pytest

from tests.archived_publish_fixture_successor import load_archived_successor

# This private historical module never replaces the restored live guard module.
history = load_archived_successor()


@pytest.fixture
def fixture_boundary(tmp_path, monkeypatch):
    entry = dict(history.PUBLISH_FIXTURE_TEST_SUCCESSOR)
    root = history.ROOT
    predecessor = history.committed_bytes(entry["predecessor_commit"], entry["path"])
    for relative in (entry["path"], history.PUBLISH_FIXTURE_REVIEW, history.PUBLISH_FIXTURE_DIFF):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root / relative).read_bytes())
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_bytes(b"unchanged")
    baseline = {entry["path"]: entry["predecessor_sha256"],
                "unrelated.txt": hashlib.sha256(unrelated.read_bytes()).hexdigest()}
    monkeypatch.setattr(history, "ROOT", tmp_path)
    monkeypatch.setattr(history, "assert_public_refinement_snapshot", lambda: {})
    monkeypatch.setattr(history, "assert_b1a_test_successor", lambda: {})

    def published_bytes(commit, path):
        assert (commit, path) == (entry["predecessor_commit"], entry["path"])
        return predecessor

    monkeypatch.setattr(history, "committed_bytes", published_bytes)

    def integrity():
        changed = [p for p, digest in baseline.items()
                   if hashlib.sha256((tmp_path / p).read_bytes()).hexdigest() != digest]
        return {"changed_paths": changed, "changed_count": len(changed),
                "protected_files_checked": len(baseline), "authorized_successor_changes": []}

    return tmp_path, entry, baseline, integrity, predecessor


def test_real_reviewed_published_predecessor_and_current_successor_are_accepted():
    assert history.assert_publish_fixture_test_successor() == {
        "tests/test_admin_publish_workflow_reliability.py":
        "34420cb25c55df54ecb65ff9d7e4dcd2e9e258cc85101fe9806f790203e6b60f"}


def test_exact_reviewed_successor_boundary_is_accepted(fixture_boundary):
    _, _, baseline, integrity, _ = fixture_boundary
    history.assert_historical_integrity_with_public_refinement(integrity, baseline)


def test_arbitrary_successor_edit_is_rejected(fixture_boundary):
    root, entry, baseline, integrity, _ = fixture_boundary
    target = root / entry["path"]
    target.write_bytes(target.read_bytes() + b"\n# unauthorized\n")
    with pytest.raises(AssertionError, match="Unreviewed fixture successor"):
        history.assert_historical_integrity_with_public_refinement(integrity, baseline)


def test_changed_predecessor_git_bytes_are_rejected(fixture_boundary, monkeypatch):
    _, _, baseline, integrity, before = fixture_boundary
    monkeypatch.setattr(history, "committed_bytes", lambda *_: before + b"\n# unauthorized\n")
    with pytest.raises(AssertionError, match="Unreviewed fixture predecessor"):
        history.assert_historical_integrity_with_public_refinement(integrity, baseline)


@pytest.mark.parametrize("field,value", [
    ("path", "tests/unreviewed.py"),
    ("predecessor_commit", "0" * 40),
    ("predecessor_sha256", "0" * 64),
    ("reviewed_sha256", "0" * 64),
    ("reviewed_diff_sha256", "0" * 64),
    ("scope", "all_test_changes"),
    ("wildcard", "tests/*"),
])
def test_authorization_metadata_changes_are_rejected(fixture_boundary, monkeypatch, field, value):
    _, entry, baseline, integrity, _ = fixture_boundary
    monkeypatch.setattr(history, "PUBLISH_FIXTURE_TEST_SUCCESSOR", {**entry, field: value})
    with pytest.raises(AssertionError):
        history.assert_historical_integrity_with_public_refinement(integrity, baseline)


def test_mutable_hash_cannot_authorize_arbitrary_successor(fixture_boundary, monkeypatch):
    root, entry, baseline, integrity, _ = fixture_boundary
    target = root / entry["path"]
    target.write_bytes(target.read_bytes() + b"\n# unauthorized\n")
    monkeypatch.setattr(history, "PUBLISH_FIXTURE_TEST_SUCCESSOR", {
        **entry, "reviewed_sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    with pytest.raises(AssertionError, match="Unreviewed fixture authorization metadata"):
        history.assert_historical_integrity_with_public_refinement(integrity, baseline)


@pytest.mark.parametrize("receipt_kind", ["review", "diff"])
def test_changed_receipt_bytes_are_rejected(fixture_boundary, receipt_kind):
    root, _, baseline, integrity, _ = fixture_boundary
    relative = history.PUBLISH_FIXTURE_REVIEW if receipt_kind == "review" else history.PUBLISH_FIXTURE_DIFF
    path = root / relative
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(AssertionError):
        history.assert_historical_integrity_with_public_refinement(integrity, baseline)


@pytest.mark.parametrize("receipt_kind", ["review", "diff"])
def test_missing_receipts_are_rejected(fixture_boundary, receipt_kind):
    root, _, baseline, integrity, _ = fixture_boundary
    relative = history.PUBLISH_FIXTURE_REVIEW if receipt_kind == "review" else history.PUBLISH_FIXTURE_DIFF
    (root / relative).unlink()
    with pytest.raises(FileNotFoundError):
        history.assert_historical_integrity_with_public_refinement(integrity, baseline)


def test_changed_historical_baseline_hash_is_rejected(fixture_boundary):
    _, entry, baseline, integrity, _ = fixture_boundary
    baseline[entry["path"]] = "0" * 64
    with pytest.raises(AssertionError, match="Unexpected historical fixture baseline"):
        history.assert_historical_integrity_with_public_refinement(integrity, baseline)


def test_unrelated_file_edit_is_rejected(fixture_boundary):
    root, _, baseline, integrity, _ = fixture_boundary
    (root / "unrelated.txt").write_bytes(b"unauthorized")
    with pytest.raises(AssertionError):
        history.assert_historical_integrity_with_public_refinement(integrity, baseline)


@pytest.mark.parametrize("field", ["changed_count", "protected_files_checked"])
def test_reduced_count_coverage_is_rejected(fixture_boundary, field):
    _, _, baseline, integrity, _ = fixture_boundary
    result = integrity()
    result[field] -= 1
    with pytest.raises(AssertionError):
        history.assert_historical_integrity_with_public_refinement(lambda: result, baseline)
