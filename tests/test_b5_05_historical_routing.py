"""Negative controls for the authenticated B5-04 ledger boundary."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests import b5_04_historical_fixtures as prior
from tests import b5_05_historical_fixtures as history


ROOT = Path(__file__).resolve().parents[1]
TEST = "tests/test_corpus_quality_batch_b_wave_b5_04.py"
CASE = TEST + "::test_ledger_accounting_from_original_action_inventory"


def item(nodeid=CASE, module_path=TEST):
    return SimpleNamespace(nodeid=nodeid, module=SimpleNamespace(__file__=str(ROOT / module_path)))


def test_route_requires_exact_node_and_unchanged_module_bytes():
    assert history.authorized_scope(ROOT, item())
    assert not history.authorized_scope(ROOT, item(CASE + "_unreviewed"))
    assert not history.authorized_scope(ROOT, item(TEST + "::test_current_generated_reports_are_fresh"))
    with pytest.raises(AssertionError, match="Unexpected B5-05 historical test module"):
        history.authorized_scope(ROOT, item(module_path=history.GUARD))
    with pytest.raises(AssertionError, match="Changed B5-05 scoped historical test"):
        history.authorized_scope(ROOT, item(), lambda path: path.read_bytes() + b"\n# changed")


@pytest.mark.parametrize("field", [
    "prior_commit", "prior_tree", "prior_ledger_sha256", "actual_ledger_sha256",
    "inherited_guard_sha256", "test_sha256", "ledger_operand_scope",
])
def test_altered_authorization_cannot_be_blessed_by_recomputed_hash(field, monkeypatch):
    manifest = history.authorization()
    manifest[field] = "unreviewed"
    raw = json.dumps(manifest).encode()
    with pytest.raises(AssertionError, match="Unreviewed B5-05 routing manifest"):
        history.authorization(lambda _: raw)
    monkeypatch.setattr(history, "MANIFEST_SHA256", history.sha256(raw))
    with pytest.raises(AssertionError, match="Unreviewed B5-05 routing metadata"):
        history.authorization(lambda _: raw)


def test_predecessor_has_no_current_fallback():
    assert history.predecessor_ledger(ROOT) != history.actual_ledger(ROOT)
    with pytest.raises(AssertionError, match="Changed B5-04 ledger bytes"):
        history.predecessor_ledger(ROOT, lambda *_: (ROOT / history.LEDGER).read_bytes())
    with pytest.raises(AssertionError, match="Changed B5-04 ledger bytes"):
        history.predecessor_ledger(ROOT, lambda *_: b"altered historical content")


@pytest.mark.parametrize("relative", [history.LEDGER, history.GUARD])
def test_actual_state_must_authenticate_before_historical_replay(relative):
    assert history.actual_ledger(ROOT).startswith(history.predecessor_ledger(ROOT))

    def read(path):
        raw = path.read_bytes()
        return raw + b"\nUNAUTHORIZED" if path == ROOT / relative else raw

    with pytest.raises(AssertionError, match="Changed actual B5-05 ledger|Changed original B5-04 guard"):
        history.actual_ledger(ROOT, read)


@pytest.mark.parametrize("relative", [history.LEDGER, "data/curated/papers.csv"])
def test_prior_guard_still_rejects_explicit_ledger_and_unrelated_faults(relative):
    verify = history.guard_for_history(prior.verify_actual_endpoint, ROOT)
    verify(ROOT)

    def read(path):
        raw = path.read_bytes()
        return raw + b"\nUNAUTHORIZED" if path == ROOT / relative else raw

    with pytest.raises(AssertionError, match="Changed actual B5-04 operand"):
        verify(ROOT, read)


def test_prior_bytes_cannot_mask_an_explicit_live_rollback():
    verify = history.guard_for_history(prior.verify_actual_endpoint, ROOT)
    old = history.predecessor_ledger(ROOT)
    with pytest.raises(AssertionError, match="Changed actual B5-04 operand"):
        verify(ROOT, lambda path: old if path == ROOT / history.LEDGER else path.read_bytes())
    with pytest.raises(AssertionError, match="Unexpected B5-04 guard root"):
        verify(ROOT / "tests")


def test_disposable_historical_ledger_is_rechecked(pytestconfig, monkeypatch):
    snapshot, verify = history.ledger_path_for(pytestconfig)
    verify()
    read = Path.read_bytes

    def tampered(path):
        raw = read(path)
        return raw + b"\nUNAUTHORIZED" if path == snapshot / history.LEDGER else raw

    with monkeypatch.context() as scoped:
        scoped.setattr(Path, "read_bytes", tampered)
        with pytest.raises(AssertionError, match="Changed disposable B5-04 ledger"):
            verify()
    verify()
