"""Historical boundaries accept only the exact reviewed B1A test successor."""
import hashlib

import pytest

import public_refinement_snapshot as history


@pytest.fixture
def reviewed_boundary(tmp_path, monkeypatch):
    relative = history.B1A_TEST_SUCCESSOR["path"]
    content = (history.ROOT / relative).read_bytes()
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_bytes(content)
    monkeypatch.setattr(history, "ROOT", tmp_path)
    monkeypatch.setattr(history, "assert_public_refinement_snapshot", lambda: {})
    monkeypatch.setattr(history, "committed_digest", lambda commit, path:
                        history.B1A_TEST_SUCCESSOR["predecessor_sha256"])
    baseline = {relative: history.B1A_TEST_SUCCESSOR["predecessor_sha256"],
                "unrelated.txt": hashlib.sha256(b"unchanged").hexdigest()}
    result = {"changed_paths": [relative], "changed_count": 1,
              "protected_files_checked": len(baseline), "authorized_successor_changes": []}
    return target, baseline, result


def test_exact_reviewed_successor_is_accepted(reviewed_boundary):
    _, baseline, result = reviewed_boundary
    history.assert_historical_integrity_with_public_refinement(lambda: result, baseline)


@pytest.mark.parametrize("tamper", ["unrelated_path", "successor_content", "predecessor_content"])
def test_historical_boundary_rejects_unreviewed_changes(reviewed_boundary, monkeypatch, tamper):
    target, baseline, result = reviewed_boundary
    if tamper == "unrelated_path":
        result["changed_paths"].append("unrelated.txt")
        result["changed_count"] += 1
    elif tamper == "successor_content":
        target.write_bytes(target.read_bytes() + b"\n# unreviewed change\n")
    else:
        monkeypatch.setattr(history, "committed_digest", lambda commit, path: "0" * 64)
    with pytest.raises(AssertionError):
        history.assert_historical_integrity_with_public_refinement(lambda: result, baseline)
