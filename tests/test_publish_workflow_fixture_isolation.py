"""Live additive isolation is independent of the retained archival R2 protocol."""
import hashlib
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest

import public_refinement_snapshot as live_history
from scripts import serve_admin
from scripts.public_preview_sync import DEFAULT_STATE_PATH
from tests import test_admin_publish_workflow_reliability as published
from tests.archived_publish_fixture_successor import ARCHIVE, load_archived_successor
from tests.publish_workflow_fixtures import (
    install_publish_fixture_isolation, isolated_publish_server,
)

ROOT = Path(__file__).resolve().parents[1]
PROTECTED = {
    "tests/test_admin_publish_workflow_reliability.py": "bf7258d1d23df60eb0cf5a342ac0209d629b72703c901ea13b22f5763d8aac63",
    "tests/public_refinement_snapshot.py": "7d654ae6a8e606172749a4aadea082ed28a8146bd787168873d71a9258719d26",
}


def endpoint(**overrides):
    return SimpleNamespace(**{**vars(published), **overrides})


def test_live_protected_sources_are_exact_published_bytes():
    for path, digest in PROTECTED.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    assert not hasattr(live_history, "PUBLISH_FIXTURE_TEST_SUCCESSOR")


def test_real_http_uses_owned_state_and_stable_lock_inode(monkeypatch):
    default_paths = [DEFAULT_STATE_PATH.with_suffix(DEFAULT_STATE_PATH.suffix + suffix)
                     for suffix in ("", ".lock", ".export.lock", ".curated-change-intent")]
    snapshot = lambda: {p: p.read_bytes() if p.exists() else None for p in default_paths}
    before = snapshot()
    original_open = Path.open

    def reject_default_writes(path, mode="r", *args, **kwargs):
        if path in default_paths and any(c in mode for c in "wa+"):
            raise AssertionError("Fixture attempted to write production sync state")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", reject_default_writes)
    server_class = isolated_publish_server(published)
    with server_class(lambda _name, *, progress: published.success_result()) as server:
        coordinator = server.RequestHandlerClass.public_preview_sync
        temporary_root = coordinator.state_path.parent
        assert coordinator.state_path != DEFAULT_STATE_PATH
        inodes = []
        for _ in range(2):
            status, result = published.request(server, "/api/publish-changes", body={"confirmed": True})
            assert status == 200 and result["success"]
            assert coordinator.export_lock_path.parent == temporary_root
            inodes.append(coordinator.export_lock_path.stat().st_ino)
        assert inodes[0] == inodes[1]
        assert snapshot() == before
    assert not temporary_root.exists()
    assert snapshot() == before


def test_nested_servers_have_independent_state_and_teardown():
    factory = isolated_publish_server(published)
    with factory(lambda _name, *, progress: published.success_result()) as first:
        a = first.RequestHandlerClass.public_preview_sync.state_path.parent
        with factory(lambda _name, *, progress: published.success_result()) as second:
            b = second.RequestHandlerClass.public_preview_sync.state_path.parent
            assert a != b
            for server in (first, second):
                status, payload = published.request(server, "/api/publish-changes", body={"confirmed": True})
                assert status == 200 and payload["success"]
        assert not b.exists() and a.exists()
    assert not a.exists()


def test_body_failure_propagates_and_owned_state_is_removed():
    instance = isolated_publish_server(published)(lambda _name, *, progress: published.success_result())
    root = Path(instance.temporary.name)
    with pytest.raises(RuntimeError, match="original failure"):
        with instance:
            raise RuntimeError("original failure")
    assert not root.exists() and instance.server.fileno() == -1


def test_bind_failure_closes_coordinator_and_temp_root():
    handlers = []

    def fail_bind(_address, handler):
        handlers.append(handler)
        raise OSError("controlled bind failure")

    factory = isolated_publish_server(endpoint(ThreadingHTTPServer=fail_bind))
    with pytest.raises(OSError, match="controlled bind failure"):
        factory(lambda _name, *, progress: published.success_result())
    coordinator = handlers[0].public_preview_sync
    assert coordinator._stop.is_set()
    assert not coordinator.state_path.parent.exists()


def test_thread_construction_failure_closes_bound_server_and_state():
    servers = []

    def server_factory(*args):
        server = published.ThreadingHTTPServer(*args)
        servers.append(server)
        return server

    def fail_thread(**_kwargs):
        raise RuntimeError("controlled thread construction failure")

    factory = isolated_publish_server(endpoint(
        ThreadingHTTPServer=server_factory, threading=SimpleNamespace(Thread=fail_thread),
    ))
    with pytest.raises(RuntimeError, match="controlled thread construction failure"):
        factory(lambda _name, *, progress: published.success_result())
    assert servers[0].fileno() == -1
    assert not servers[0].RequestHandlerClass.public_preview_sync.state_path.parent.exists()


def test_thread_start_failure_does_not_shutdown_an_unstarted_server():
    class FailedThread:
        def __init__(self, **_kwargs):
            pass

        def start(self):
            raise RuntimeError("controlled start failure")

        def is_alive(self):
            return False

        def join(self, **_kwargs):
            pytest.fail("Unstarted thread must not be joined")

    factory = isolated_publish_server(endpoint(threading=SimpleNamespace(Thread=FailedThread)))
    instance = factory(lambda _name, *, progress: published.success_result())
    root = Path(instance.temporary.name)
    with pytest.raises(RuntimeError, match="controlled start failure"):
        with instance:
            pytest.fail("Unstarted server must not enter")
    assert instance.server.fileno() == -1 and not root.exists()


def test_module_binding_is_scoped_and_production_defaults_do_not_change(monkeypatch):
    local = endpoint()
    original, handler = local.RunningServer, serve_admin.make_handler
    with monkeypatch.context() as scoped:
        replacement = install_publish_fixture_isolation(local, scoped)
        assert local.RunningServer is replacement and issubclass(replacement, original)
        assert published.RunningServer is original
        assert serve_admin.make_handler is handler
    assert local.RunningServer is original
    assert serve_admin.make_handler is handler


def test_archived_modules_are_private_and_do_not_replace_live_history():
    a, b = load_archived_successor(), load_archived_successor()
    assert a is not b and a.__name__ != b.__name__
    assert a is not live_history and a.ROOT != live_history.ROOT
    assert hasattr(a, "PUBLISH_FIXTURE_TEST_SUCCESSOR")
    assert not hasattr(live_history, "PUBLISH_FIXTURE_TEST_SUCCESSOR")


@pytest.mark.parametrize("tamper", [
    "archive_manifest.json", "tests/public_refinement_snapshot.py",
    "tests/test_admin_publish_workflow_reliability.py", "original_successor_tests.py",
    "boundary_implementation_review.json", "reviewed_helper.diff",
    "data/raw/corpus_quality_batch_b_wave_b5_01_2026_10_30/publish_fixture_successor_review.json",
    "data/raw/corpus_quality_batch_b_wave_b5_01_2026_10_30/publish_fixture_reviewed.diff",
    "unreviewed.py",
])
def test_archive_loader_rejects_tampering_before_execution(tmp_path, tamper):
    archive = tmp_path / ARCHIVE
    shutil.copytree(ROOT / ARCHIVE, archive)
    path = archive / tamper
    path.write_bytes((path.read_bytes() if path.exists() else b"") + b"\n# unreviewed\n")
    with pytest.raises(AssertionError):
        load_archived_successor(tmp_path)


@pytest.mark.parametrize("guard", ["B1G", "Tier2_application", "Tier2_policy"])
def test_restored_live_guards_still_reject_protected_source_tampering(monkeypatch, guard):
    from tests import test_corpus_quality_batch_b_wave_b1g as b1g
    from tests import test_systematic_tier2_application as application
    from tests import test_systematic_tier2_policy as policy

    if guard == "B1G":
        target = ROOT / "tests/public_refinement_snapshot.py"
        check = b1g.test_previous_twelve_batch_receipts_and_predecessor_repair_files_keep_original_bytes
    else:
        target = ROOT / "tests/test_admin_publish_workflow_reliability.py"
        check = (application.test_pre_application_baseline_includes_and_preserves_previous_policy_pass
                 if guard == "Tier2_application" else policy.test_pre_task_repository_files_are_byte_identical)
    original = Path.read_bytes

    def altered(path):
        raw = original(path)
        return raw + b"\n# unreviewed\n" if path == target else raw

    monkeypatch.setattr(Path, "read_bytes", altered)
    with pytest.raises(AssertionError):
        check()
