"""Only the reviewed SRI delta may succeed the immutable frontend snapshot."""
from pathlib import Path

import pytest

import public_refinement_snapshot as history


def test_exact_published_sri_transition_and_snapshot_are_accepted():
    history.assert_leaflet_sri_transition()
    expected = history.assert_public_refinement_snapshot()
    assert expected["web/index.html"] == history.LEAFLET_INDEX_AFTER
    assert (history.LEAFLET_SRI_SUCCESSOR, ("web/index.html",)) in history.PUBLISHED_FRONTEND_SUCCESSORS


@pytest.mark.parametrize("commit", [history.LEAFLET_SRI_PREDECESSOR, history.LEAFLET_SRI_SUCCESSOR])
def test_changed_predecessor_or_successor_git_bytes_are_rejected(monkeypatch, commit):
    original = history.committed_bytes
    monkeypatch.setattr(history, "committed_bytes", lambda ref, path:
                        original(ref, path) + (b"\n<!-- unauthorized -->" if ref == commit else b""))
    with pytest.raises(AssertionError):
        history.assert_leaflet_sri_transition()


def test_wrong_predecessor_commit_is_rejected(monkeypatch):
    original = history.subprocess.check_output
    monkeypatch.setattr(history.subprocess, "check_output", lambda args, **kwargs:
                        "0" * 40 + "\n" if args[1] == "rev-parse" else original(args, **kwargs))
    with pytest.raises(AssertionError, match="Unexpected Leaflet predecessor"):
        history.assert_leaflet_sri_transition()


@pytest.mark.parametrize("relative", ["web/index.html", "web/style.css", "web/app.js"])
def test_unrelated_current_frontend_edits_are_rejected(monkeypatch, relative):
    original = history.historical_bytes
    target = history.ROOT / relative
    monkeypatch.setattr(history, "historical_bytes", lambda path:
                        original(path) + (b"\n/* unreviewed */" if path == target else b""))
    with pytest.raises(AssertionError, match="Public refinement differs"):
        history.assert_public_refinement_snapshot()


def test_extra_frontend_file_is_rejected_without_mutating_the_checkout(monkeypatch):
    extra = history.ROOT / "web/unreviewed.js"
    original_glob, original_is_file = Path.glob, Path.is_file

    def glob(path, pattern):
        yield from original_glob(path, pattern)
        if path == history.ROOT / "web" and pattern == "*":
            yield extra

    monkeypatch.setattr(Path, "glob", glob)
    monkeypatch.setattr(Path, "is_file", lambda path: path == extra or original_is_file(path))
    with pytest.raises(AssertionError):
        history.assert_public_refinement_snapshot()


def test_reviewed_node_test_successor_and_snapshot_are_accepted():
    history.assert_node_test_path_transition()
    expected = history.assert_public_refinement_snapshot()
    assert (history.NODE_TEST_SUCCESSOR, history.NODE_TEST_PATHS) in history.PUBLISHED_FRONTEND_SUCCESSORS
    for relative in history.NODE_TEST_PATHS:
        assert expected[relative] == history.committed_digest(history.NODE_TEST_SUCCESSOR, relative)


@pytest.mark.parametrize("commit", [history.NODE_TEST_PREDECESSOR, history.NODE_TEST_SUCCESSOR])
@pytest.mark.parametrize("relative", history.NODE_TEST_PATHS)
def test_node_test_successor_rejects_modified_history(monkeypatch, commit, relative):
    original = history.committed_bytes
    monkeypatch.setattr(history, "committed_bytes", lambda ref, path:
                        original(ref, path) + (b"\n# unreviewed\n" if (ref, path) == (commit, relative) else b""))
    with pytest.raises(AssertionError):
        history.assert_node_test_path_transition()


@pytest.mark.parametrize("relative", history.NODE_TEST_PATHS)
def test_node_test_successor_rejects_current_unreviewed_edit(monkeypatch, relative):
    original = history.historical_bytes
    target = history.ROOT / relative
    monkeypatch.setattr(history, "historical_bytes", lambda path:
                        original(path) + (b"\n# unauthorized\n" if path == target else b""))
    with pytest.raises(AssertionError, match="Public refinement differs"):
        history.assert_public_refinement_snapshot()


def test_date_header_node_test_successor_is_exactly_reviewed():
    history.assert_header_node_path_transition()
    expected = history.assert_public_refinement_snapshot()
    assert (history.HEADER_NODE_SUCCESSOR, (history.HEADER_NODE_PATH,)) in history.PUBLISHED_FRONTEND_SUCCESSORS
    assert expected[history.HEADER_NODE_PATH] == history.committed_digest(history.HEADER_NODE_SUCCESSOR, history.HEADER_NODE_PATH)


@pytest.mark.parametrize("commit", [history.HEADER_NODE_PREDECESSOR, history.HEADER_NODE_SUCCESSOR])
def test_date_header_node_successor_rejects_changed_commit_bytes(monkeypatch, commit):
    original = history.committed_bytes
    monkeypatch.setattr(history, "committed_bytes", lambda ref, path:
                        original(ref, path) + (b"\n# unauthorized\n" if ref == commit and path == history.HEADER_NODE_PATH else b""))
    with pytest.raises(AssertionError):
        history.assert_header_node_path_transition()


def test_date_header_node_successor_rejects_unreviewed_current_test(monkeypatch):
    original = history.historical_bytes
    target = history.ROOT / history.HEADER_NODE_PATH
    monkeypatch.setattr(history, "historical_bytes", lambda path:
                        original(path) + (b"\n# unauthorized\n" if path == target else b""))
    with pytest.raises(AssertionError, match="Public refinement differs"):
        history.assert_public_refinement_snapshot()
