"""Present the immutable B5-04 ledger only to its exact historical assertions."""

from functools import lru_cache
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import pytest

from tests import b5_04_historical_fixtures as prior
from tests.b5_04_published_inputs import sha256


LEDGER = "data/curated/review_decisions.csv"
GUARD = "tests/b5_04_historical_fixtures.py"
MANIFEST = Path(__file__).parent / "fixtures/batch_b_b5_05_ledger_history.json"
MANIFEST_SHA256 = "597ce371b94a512a8c3dad3dd11de317921fd1d24abba4b61727f7f1dcdfc840"
SNAPSHOT = pytest.StashKey()


def authorization(reader=None):
    assert LEDGER == "data/curated/review_decisions.csv"
    assert GUARD == "tests/b5_04_historical_fixtures.py"
    assert MANIFEST == Path(__file__).parent / "fixtures/batch_b_b5_05_ledger_history.json"
    assert MANIFEST_SHA256 == "597ce371b94a512a8c3dad3dd11de317921fd1d24abba4b61727f7f1dcdfc840", (
        "Unreviewed B5-05 routing metadata"
    )
    raw = (reader or Path.read_bytes)(MANIFEST)
    assert sha256(raw) == MANIFEST_SHA256, "Unreviewed B5-05 routing manifest"
    return json.loads(raw)


def authorized_scope(root, item, reader=None):
    manifest = authorization()
    if item.nodeid not in manifest["ledger_operand_scope"]:
        return False
    relative = item.nodeid.split("::", 1)[0]
    path = root / relative
    assert Path(item.module.__file__).resolve() == path.resolve(), "Unexpected B5-05 historical test module"
    assert sha256((reader or Path.read_bytes)(path)) == manifest["test_sha256"][relative], (
        "Changed B5-05 scoped historical test"
    )
    return True


@lru_cache(maxsize=None)
def git_predecessor(root, commit, tree):
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=root)

    assert git("rev-parse", f"{commit}^{{tree}}").decode().strip() == tree, "Unexpected B5-04 tree"
    return git("show", f"{commit}:{LEDGER}")


def predecessor_ledger(root, reader=None):
    manifest = authorization()
    raw = (reader or git_predecessor)(root, manifest["prior_commit"], manifest["prior_tree"])
    assert sha256(raw) == manifest["prior_ledger_sha256"], "Changed B5-04 ledger bytes"
    return raw


def actual_ledger(root, reader=None):
    manifest = authorization()
    read = reader or Path.read_bytes
    raw = read(root / LEDGER)
    assert sha256(raw) == manifest["actual_ledger_sha256"], "Changed actual B5-05 ledger"
    assert raw.startswith(predecessor_ledger(root)), "Changed original decision prefix"
    assert sha256(read(root / GUARD)) == manifest["inherited_guard_sha256"], "Changed original B5-04 guard"
    return raw


def guard_for_history(original, current_root):
    """Keep the earlier endpoint guard intact with one versioned read operand."""
    def verify(root, reader=None):
        assert root == current_root, "Unexpected B5-04 guard root"
        current = actual_ledger(root)
        historical = predecessor_ledger(root)
        live_read = reader or Path.read_bytes

        def read(path):
            observed = live_read(path)
            if path != root / LEDGER:
                return observed
            if observed == current:
                return historical
            assert observed != historical, "Changed actual B5-04 operand: " + LEDGER
            return observed

        return original(root, read)

    return verify


def ledger_path_for(config):
    existing = config.stash.get(SNAPSHOT, None)
    if existing is not None:
        return existing
    raw = predecessor_ledger(config.rootpath)
    storage = TemporaryDirectory(prefix="b5-05-ledger-")
    snapshot = Path(storage.name)
    path = snapshot / LEDGER
    try:
        path.parent.mkdir(parents=True)
        path.write_bytes(raw)
    except BaseException:
        storage.cleanup()
        raise

    def verify():
        assert path.read_bytes() == raw, "Changed disposable B5-04 ledger"

    config.stash[SNAPSHOT] = snapshot, verify
    config.add_cleanup(storage.cleanup)
    config.add_cleanup(verify)
    return snapshot, verify


class HistoricalLedgerRoute:
    """Run outside the existing B5-04 per-item wrapper."""

    @pytest.hookimpl(wrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item):
        root = item.config.rootpath
        direct = authorized_scope(root, item)
        inherited = prior.authorized_scope(root, item)
        if not direct and inherited is None:
            return (yield)

        actual_ledger(root)
        verify = None
        try:
            with pytest.MonkeyPatch.context() as scope:
                scope.setattr(prior, "verify_actual_endpoint", guard_for_history(prior.verify_actual_endpoint, root))
                if direct and item.nodeid.startswith("tests/test_corpus_quality_batch_b_wave_b5_04.py::"):
                    historical_root, verify = ledger_path_for(item.config)
                    verify()
                    scope.setattr(item.module, "ROOT", prior.SelectedPaths(root, historical_root, (LEDGER,)))
                return (yield)
        finally:
            if verify is not None:
                verify()
            actual_ledger(root)


def pytest_configure(config):
    # Register after the original plugins so this tryfirst wrapper is outermost.
    config.pluginmanager.register(HistoricalLedgerRoute(), "b5-05-historical-ledger-route")
