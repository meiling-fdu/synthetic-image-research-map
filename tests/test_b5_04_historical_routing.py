"""Negative controls for the exact B5-04 historical input boundary."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests import b5_04_historical_fixtures as history


ROOT = Path(__file__).resolve().parents[1]
CASE = (
    "tests/test_corpus_quality_batch_b_wave_b1b.py::"
    "test_unrelated_author_institution_and_scope_sources_remain_exact"
    "[data/curated/author_institution_mappings.csv]"
)


def selected_item(nodeid=CASE):
    path = ROOT / CASE.split("::", 1)[0]
    return SimpleNamespace(nodeid=nodeid, module=SimpleNamespace(__file__=str(path)))


def test_routing_authority_names_only_exact_nodeids():
    assert history.authorized_scope(ROOT, selected_item())["bindings"] == ["test_root_mappings"]
    alternate = CASE.replace("author_institution_mappings.csv", "institutions.csv")
    assert history.authorized_scope(ROOT, selected_item(alternate)) is None
    assert history.authorized_scope(ROOT, selected_item(CASE.split("[", 1)[0])) is None
    assert history.authorized_scope(ROOT, selected_item(CASE + "-unreviewed")) is None


@pytest.mark.parametrize("damage", ["node", "read_binding", "successor_hash", "predecessor", "path"])
def test_changed_scope_manifest_cannot_expand_authority(damage, monkeypatch):
    manifest = history.authenticated_manifest()
    if damage == "node":
        manifest["scopes"][CASE + "another"] = manifest["scopes"][CASE]
    elif damage == "read_binding":
        manifest["scopes"][CASE]["bindings"].append("old_guard_root")
    elif damage == "successor_hash":
        manifest["successor_sha256"][history.MAPPINGS] = "0" * 64
    elif damage == "predecessor":
        manifest["prior_commit"] = "0" * 40
    else:
        manifest["scopes"][CASE]["path"] = "tests/baseline_expectations.py"
    raw = json.dumps(manifest).encode()
    with pytest.raises(AssertionError, match="Unreviewed B5-04 scope manifest"):
        history.authenticated_manifest(lambda _: raw)
    monkeypatch.setattr(history, "MANIFEST_SHA256", history.sha256(raw))
    with pytest.raises(AssertionError, match="Unreviewed B5-04 routing metadata"):
        history.authenticated_manifest(lambda _: raw)


def test_changed_original_test_source_cannot_receive_history():
    def read(path):
        raw = path.read_bytes()
        return raw if path == history.MANIFEST_PATH else raw + b"\n# unauthorized edit"

    assert history.authorized_scope(ROOT, selected_item())
    with pytest.raises(AssertionError, match="Changed scoped historical test"):
        history.authorized_scope(ROOT, selected_item(), read)


def test_test_module_path_cannot_be_substituted():
    item = selected_item()
    item.module.__file__ = str(ROOT / "tests/baseline_expectations.py")
    with pytest.raises(AssertionError, match="Unexpected test module"):
        history.authorized_scope(ROOT, item)


def test_only_named_path_changes_root(tmp_path):
    current, prior = tmp_path / "current", tmp_path / "prior"
    path = history.SelectedPaths(current, prior, (history.MAPPINGS,))
    assert path / history.MAPPINGS == prior / history.MAPPINGS
    assert path / "data/curated/institution_locations.csv" == current / "data/curated/institution_locations.csv"
    assert Path(path) == current
    with pytest.raises(AssertionError, match="repository-relative"):
        path / "../outside"
    with pytest.raises(AssertionError, match="repository-relative"):
        path / current


def test_prior_guard_keeps_explicit_read_faults(tmp_path):
    current, prior = tmp_path / "current", tmp_path / "prior"
    fault = lambda _: b"altered"

    def check(root, reader):
        assert root == prior
        assert reader is fault
        return reader("data/curated/papers.csv")

    wrapped = history.prior_call(check, current, prior)
    assert wrapped(current, reader=fault) == b"altered"
    with pytest.raises(AssertionError, match="Unexpected historical reader root"):
        wrapped(tmp_path / "unreviewed", reader=fault)


@pytest.mark.parametrize("relative", [
    "data/curated/papers.csv", history.MAPPINGS, "data/curated/review_decisions.csv",
    "data/curated/institution_locations.csv", "web/data/public_preview_map_data.json",
    history.MAPPING_REPORT, "tests/baseline_expectations.py",
])
def test_prior_replay_cannot_hide_actual_b504_tampering(relative):
    history.verify_actual_endpoint(ROOT)

    def read(path):
        raw = path.read_bytes()
        return raw + b"\nUNAUTHORIZED" if path == ROOT / relative else raw

    with pytest.raises(AssertionError, match="Changed actual B5-04 operand"):
        history.verify_actual_endpoint(ROOT, read)


@pytest.mark.parametrize("relative", [history.MAPPINGS, ".git/config", ".git/index"])
def test_disposable_published_snapshot_bytes_are_pinned(pytestconfig, monkeypatch, relative):
    view = history.snapshot_for(pytestconfig)
    assert view.verify()
    original = Path.read_bytes

    def read(path):
        raw = original(path)
        return raw + b"\nUNAUTHORIZED" if path == view.root / relative else raw

    with monkeypatch.context() as scoped:
        scoped.setattr(Path, "read_bytes", read)
        with pytest.raises(AssertionError):
            view.verify()
    assert view.verify()
