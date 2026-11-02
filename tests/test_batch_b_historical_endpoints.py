"""Independent negatives for exact B5-01 history and separate live B5-02 gates.

No historical authorizations are inferred from mutable current-source hashes.
Every tamper is confined to pytest temporary files or a scoped test double.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from tests import batch_b_historical_endpoints as history
from tests.corpus_quality_test_helpers import csv_records, published_bytes

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "d109c70f6994906ec3d9197baad51cf9d8e51f7c"
MANIFEST = "tests/fixtures/batch_b_b5_01_endpoint.json"
MANIFEST_SHA256 = "22000e8f7fda983e263453781d96f5eae139cfce6ff35f0ad973ac67ca4d1b04"
PREDECESSORS = {
    "tests/test_corpus_quality_batch_b_wave_b1s.py":
        "bde78da60eaf4f3660725dade4d11aed2225e13d28f675eabf52790cde65f5ec",
    "tests/test_corpus_quality_batch_b_wave_b4_02.py":
        "ede273958436346d7b94e24c4f970a6fca6fc6528f7e87b7f0ce87d71077f3a3",
    "tests/test_corpus_quality_batch_b_wave_b5_01.py":
        "87a1766308c46797b2b921e47da2755ea5f4c9144904b4fddd21b34ce0b5fa64",
}
CONTEXT_INPUTS = (
    "data/curated/paper_taxonomy.csv",
    "web/data/public_preview_papers.json",
    "web/data/public_preview_map_data.json",
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def manifest_copy(tmp_path):
    path = tmp_path / MANIFEST
    path.parent.mkdir(parents=True)
    path.write_bytes((ROOT / MANIFEST).read_bytes())
    return tmp_path, path


def test_manifest_authority_and_complete_original_path_inventory():
    manifest = history.authenticated_manifest()
    assert history.B5_01 == COMMIT
    assert history.MANIFEST == MANIFEST
    assert history.MANIFEST_SHA256 == MANIFEST_SHA256
    assert digest((ROOT / MANIFEST).read_bytes()) == MANIFEST_SHA256
    assert manifest["purpose"] == "B5-01 immutable historical transaction; not current-state authorization"
    assert len(manifest["files"]) == 107
    for path, expected in manifest["files"].items():
        assert path.startswith(("data/curated/", "data/manual/", "web/data/"))
        assert digest(published_bytes(COMMIT, path)) == expected
        assert history.b5_01_bytes(path) == published_bytes(COMMIT, path)


@pytest.mark.parametrize("path,expected", PREDECESSORS.items())
def test_original_published_test_predecessor_bytes_remain_immutable(path, expected):
    assert digest(published_bytes(COMMIT, path)) == expected


def test_protected_b1g_helper_is_not_changed_to_authorize_new_boundaries():
    path = "tests/public_refinement_snapshot.py"
    expected = "7d654ae6a8e606172749a4aadea082ed28a8146bd787168873d71a9258719d26"
    assert digest(published_bytes(COMMIT, path)) == expected
    assert (ROOT / path).read_bytes() == published_bytes(COMMIT, path)


def test_historical_127_rows_15_paper_cells_and_taxonomy_state_remain_original():
    raw = history.b5_01_bytes("data/curated/review_decisions.csv")
    assert len(csv_records(raw)) == 127
    assert digest(raw) == "3430814d49d8e73a5836c71fb04b5acb3e95de3dac56bb795ca62dcf734bfda5"
    before = csv_records(published_bytes("7fc8ceae702324628335944cf4b545a3733fdc56", "data/curated/papers.csv"))
    after = csv_records(history.b5_01_bytes("data/curated/papers.csv"))
    assert [r["paper_id"] for r in before] == [r["paper_id"] for r in after]
    assert sum(a[k] != b[k] for a, b in zip(before, after) for k in a) == 15
    ctx = history.b5_01_context()
    assert len(ctx["papers"]) == 674 and sum(ctx["pairs"].values()) == len(ctx["pairs"]) == 1410
    assert sum("dataset" in p["research_types"] for p in ctx["papers"].values()) == 138
    assert sum("benchmark" in p["research_types"] for p in ctx["papers"].values()) == 97


@pytest.mark.parametrize("fault", ["schema", "commit", "purpose", "path_digest", "remove_path", "extra_path", "whitespace"])
def test_original_manifest_tampering_is_rejected(manifest_copy, fault):
    root, path = manifest_copy
    value = json.loads(path.read_bytes())
    if fault == "schema":
        value["schema"] = 2
    elif fault == "commit":
        value["commit"] = "0" * 40
    elif fault == "purpose":
        value["purpose"] = "authorize_current_edits"
    elif fault == "path_digest":
        value["files"]["data/curated/paper_taxonomy.csv"] = "0" * 64
    elif fault == "remove_path":
        value["files"].pop("data/curated/review_decisions.csv")
    elif fault == "extra_path":
        value["files"]["tests/unreviewed.py"] = "0" * 64
    path.write_text(json.dumps(value, sort_keys=True) + ("\n\n" if fault == "whitespace" else "\n"))
    with pytest.raises(AssertionError, match="Unreviewed historical endpoint manifest"):
        history.authenticated_manifest(root)


@pytest.mark.parametrize("field,value", [
    ("B5_01", "0" * 40),
    ("MANIFEST", "tests/fixtures/unreviewed.json"),
    ("MANIFEST_SHA256", "0" * 64),
])
def test_authorization_metadata_cannot_be_redirected(manifest_copy, monkeypatch, field, value):
    root, _ = manifest_copy
    monkeypatch.setattr(history, field, value)
    with pytest.raises(AssertionError, match="authorization metadata"):
        history.authenticated_manifest(root)


def test_matching_mutable_hash_cannot_authorize_an_altered_manifest(manifest_copy, monkeypatch):
    root, path = manifest_copy
    value = json.loads(path.read_bytes())
    value["files"]["data/curated/review_decisions.csv"] = "0" * 64
    path.write_text(json.dumps(value, sort_keys=True) + "\n")
    monkeypatch.setattr(history, "MANIFEST_SHA256", digest(path.read_bytes()))
    with pytest.raises(AssertionError, match="authorization metadata"):
        history.authenticated_manifest(root)


@pytest.mark.parametrize("path", ["tests/unreviewed.py", "../outside", "/etc/passwd", "data/curated/../unreviewed.csv", "*"])
def test_undeclared_or_escaping_snapshot_path_is_rejected_before_git(monkeypatch, path):
    def forbidden(*_):
        pytest.fail("undeclared path reached Git reader")
    monkeypatch.setattr(history, "published_bytes", forbidden)
    with pytest.raises(AssertionError, match="Undeclared historical endpoint path"):
        history.b5_01_bytes(path)


@pytest.mark.parametrize("path", CONTEXT_INPUTS + ("data/curated/review_decisions.csv",))
def test_changed_original_git_snapshot_bytes_are_rejected(monkeypatch, path):
    before = published_bytes(COMMIT, path)
    calls = []
    def changed(commit, relative):
        calls.append((commit, relative))
        return before + b"\n# unauthorized historical change\n"
    monkeypatch.setattr(history, "published_bytes", changed)
    with pytest.raises(AssertionError, match="Historical endpoint bytes changed"):
        history.b5_01_bytes(path)
    assert calls == [(COMMIT, path)]


@pytest.mark.parametrize("damaged", CONTEXT_INPUTS)
def test_context_refuses_any_corrupt_input_before_parsing(monkeypatch, damaged):
    real_reader = published_bytes
    def reader(commit, path):
        raw = real_reader(commit, path)
        return raw + b"tampered" if path == damaged else raw
    def no_parse(*_):
        pytest.fail("corrupt historical context reached parser")
    monkeypatch.setattr(history, "published_bytes", reader)
    monkeypatch.setattr(history, "published_context", no_parse)
    with pytest.raises(AssertionError, match="Historical endpoint bytes changed"):
        history.b5_01_context()


def test_snapshot_reader_has_no_mutable_current_source_fallback(monkeypatch):
    path = "data/curated/review_decisions.csv"
    before = published_bytes(COMMIT, path)
    calls = []
    def reader(commit, relative):
        calls.append((commit, relative))
        assert commit == COMMIT and relative == path
        return before
    monkeypatch.setattr(history, "published_bytes", reader)
    assert history.b5_01_bytes(path) == before
    assert calls == [(COMMIT, path)]
    # The approved current registry has evolved. Historical authentication must
    # neither reject that evolution nor use it to redefine the old endpoint.
    assert (ROOT / path).read_bytes() != before
    assert len(csv_records((ROOT / path).read_bytes())) == 138


@pytest.mark.parametrize("path", [
    "data/curated/papers.csv", "data/curated/paper_taxonomy.csv",
    "data/curated/review_decisions.csv", "data/curated/institutions.csv",
    "data/curated/institution_locations.csv", "data/curated/author_institution_mappings.csv",
    "data/manual/papers.csv",
])
def test_passing_historical_replay_does_not_authorize_current_source_corruption(monkeypatch, path):
    from tests import test_corpus_quality_batch_b_wave_b5_02 as live
    # Prove immutable replay passes first, then inject only a live read fault.
    assert len(csv_records(history.b5_01_bytes("data/curated/review_decisions.csv"))) == 127
    original = live.current
    def reader(relative):
        raw = original(relative)
        return raw + b"\n# unauthorized current change\n" if relative == path else raw
    monkeypatch.setattr(live, "current", reader)
    with pytest.raises(AssertionError):
        live.test_only_approved_authoritative_files_and_exact_source_bytes_change()
