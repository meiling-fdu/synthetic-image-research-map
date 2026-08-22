import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from scripts.public_preview_sync import PublicPreviewSyncCoordinator


class PublicPreviewSyncCoordinatorTests(unittest.TestCase):
    def coordinator(self, directory, runner, *, autostart=True):
        coordinator = PublicPreviewSyncCoordinator(
            Path(directory) / "sync.json",
            runner,
            retry_delay=0.005,
            autostart=autostart,
        )
        self.addCleanup(coordinator.close, 2)
        return coordinator

    def test_one_request_runs_one_export_and_clears_dirty_state(self):
        with tempfile.TemporaryDirectory() as directory:
            calls = []
            coordinator = self.coordinator(
                directory, lambda: calls.append("export") or {"success": True}
            )

            requested = coordinator.request_sync()
            self.assertEqual(requested["generation"], 1)
            settled = coordinator.wait_for_settled()

            self.assertEqual(calls, ["export"])
            self.assertEqual(settled["status"], "synchronized")
            self.assertEqual(settled["synchronized_generation"], 1)

    def test_request_returns_while_export_is_still_running(self):
        with tempfile.TemporaryDirectory() as directory:
            started = threading.Event()
            release = threading.Event()

            def runner():
                started.set()
                release.wait(2)
                return {"success": True}

            coordinator = self.coordinator(directory, runner)
            before = time.perf_counter()
            coordinator.request_sync()
            elapsed = time.perf_counter() - before

            self.assertLess(elapsed, 0.25)
            self.assertTrue(started.wait(1))
            self.assertEqual(coordinator.snapshot()["status"], "running")
            release.set()
            self.assertEqual(
                coordinator.wait_for_settled()["status"], "synchronized"
            )

    def test_saves_during_export_coalesce_without_concurrent_exporters(self):
        with tempfile.TemporaryDirectory() as directory:
            first_started = threading.Event()
            release_first = threading.Event()
            calls = 0
            active = 0
            max_active = 0
            guard = threading.Lock()

            def runner():
                nonlocal calls, active, max_active
                with guard:
                    calls += 1
                    call_number = calls
                    active += 1
                    max_active = max(max_active, active)
                try:
                    if call_number == 1:
                        first_started.set()
                        release_first.wait(2)
                    return {"success": True}
                finally:
                    with guard:
                        active -= 1

            coordinator = self.coordinator(directory, runner)
            coordinator.request_sync()
            self.assertTrue(first_started.wait(1))
            for _ in range(4):
                coordinator.request_sync()
            release_first.set()
            settled = coordinator.wait_for_settled()

            self.assertEqual(calls, 2)
            self.assertEqual(max_active, 1)
            self.assertEqual(settled["generation"], 5)
            self.assertEqual(settled["synchronized_generation"], 5)

    def test_stale_export_cannot_mark_newer_generation_synchronized(self):
        with tempfile.TemporaryDirectory() as directory:
            first_started = threading.Event()
            release_first = threading.Event()
            second_started = threading.Event()
            release_second = threading.Event()
            calls = 0

            def runner():
                nonlocal calls
                calls += 1
                if calls == 1:
                    first_started.set()
                    release_first.wait(2)
                else:
                    second_started.set()
                    release_second.wait(2)
                return {"success": True}

            coordinator = self.coordinator(directory, runner)
            coordinator.request_sync()
            self.assertTrue(first_started.wait(1))
            coordinator.request_sync()
            release_first.set()
            self.assertTrue(second_started.wait(1))

            between_runs = coordinator.snapshot()
            self.assertEqual(between_runs["generation"], 2)
            self.assertEqual(between_runs["synchronized_generation"], 0)
            self.assertEqual(between_runs["running_generation"], 2)

            release_second.set()
            self.assertEqual(
                coordinator.wait_for_settled()["synchronized_generation"], 2
            )

    def test_failure_preserves_old_output_and_is_retryable(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "public.json"
            output.write_bytes(b'{"valid":"old"}\n')
            old_bytes = output.read_bytes()
            calls = 0

            def runner():
                nonlocal calls
                calls += 1
                if calls == 1:
                    return {"success": False, "error_summary": "controlled failure"}
                output.write_bytes(b'{"valid":"new"}\n')
                return {"success": True}

            coordinator = self.coordinator(directory, runner)
            coordinator.request_sync()
            failed = coordinator.wait_for_settled()
            self.assertEqual(failed["status"], "failed")
            self.assertEqual(failed["synchronized_generation"], 0)
            self.assertEqual(output.read_bytes(), old_bytes)

            coordinator.retry()
            synchronized = coordinator.wait_for_settled()
            self.assertEqual(calls, 2)
            self.assertEqual(synchronized["status"], "synchronized")
            self.assertEqual(output.read_bytes(), b'{"valid":"new"}\n')

    def test_startup_detects_durable_dirty_state_and_synchronizes(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "sync.json"
            state_path.write_text(
                json.dumps({
                    "version": 1,
                    "generation": 4,
                    "synchronized_generation": 3,
                    "status": "running",
                    "running_generation": 4,
                    "export_invocations": 7,
                }),
                encoding="utf-8",
            )
            calls = []
            coordinator = self.coordinator(
                directory,
                lambda: calls.append("startup-export") or {"success": True},
                autostart=False,
            )

            coordinator.start()
            settled = coordinator.wait_for_settled()

            self.assertEqual(calls, ["startup-export"])
            self.assertEqual(settled["generation"], 4)
            self.assertEqual(settled["synchronized_generation"], 4)
            self.assertEqual(settled["status"], "synchronized")

    def test_crash_after_curated_commit_before_generation_replays_latest_state(self):
        with tempfile.TemporaryDirectory() as directory:
            curated = Path(directory) / "papers.csv"
            curated.write_text("old curated state\n", encoding="utf-8")
            crashed = self.coordinator(
                directory, lambda: {"success": True}, autostart=False
            )
            crashed.begin_curated_change()
            curated.write_text("latest curated state\n", encoding="utf-8")

            exported = []
            restarted = self.coordinator(
                directory,
                lambda: exported.append(curated.read_text(encoding="utf-8"))
                or {"success": True},
            )
            settled = restarted.wait_for_settled()

            self.assertEqual(exported, ["latest curated state\n"])
            self.assertEqual(settled["generation"], 1)
            self.assertEqual(settled["synchronized_generation"], 1)
            self.assertFalse(restarted.curated_change_intent_path.exists())

    def test_crash_after_publication_before_generation_commit_reexports_safely(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "sync.json"
            public_output = Path(directory) / "public.json"
            public_output.write_text("latest public output\n", encoding="utf-8")
            state_path.write_text(
                json.dumps({
                    "version": 1,
                    "generation": 3,
                    "synchronized_generation": 2,
                    "status": "running",
                    "running_generation": 3,
                    "export_invocations": 1,
                }),
                encoding="utf-8",
            )
            observed_before_replay = []
            restarted = self.coordinator(
                directory,
                lambda: observed_before_replay.append(public_output.read_text())
                or {"success": True},
            )

            settled = restarted.wait_for_settled()

            self.assertEqual(observed_before_replay, ["latest public output\n"])
            self.assertEqual(settled["generation"], 3)
            self.assertEqual(settled["synchronized_generation"], 3)
            self.assertEqual(settled["export_invocations"], 2)

    def test_failed_export_with_newer_generation_retries_latest_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            first_started = threading.Event()
            release_failure = threading.Event()
            calls = 0

            def runner():
                nonlocal calls
                calls += 1
                if calls == 1:
                    first_started.set()
                    release_failure.wait(2)
                    return {"success": False, "error_summary": "stale failure"}
                return {"success": True}

            coordinator = self.coordinator(directory, runner)
            coordinator.request_sync()
            self.assertTrue(first_started.wait(1))
            coordinator.request_sync()
            release_failure.set()

            settled = coordinator.wait_for_settled()

            self.assertEqual(calls, 2)
            self.assertEqual(settled["status"], "synchronized")
            self.assertEqual(settled["generation"], 2)
            self.assertEqual(settled["synchronized_generation"], 2)
            self.assertEqual(settled["last_error"], "")

    def test_durable_generation_prevents_intent_recovery_from_double_incrementing(self):
        with tempfile.TemporaryDirectory() as directory:
            coordinator = self.coordinator(
                directory, lambda: {"success": True}, autostart=False
            )
            coordinator.begin_curated_change()
            coordinator.request_sync()
            coordinator.close(2)
            state = json.loads((Path(directory) / "sync.json").read_text())
            state["status"] = "dirty"
            state["synchronized_generation"] = 0
            (Path(directory) / "sync.json").write_text(json.dumps(state))

            calls = []
            restarted = self.coordinator(
                directory, lambda: calls.append(1) or {"success": True}
            )
            settled = restarted.wait_for_settled()

            self.assertEqual(calls, [1])
            self.assertEqual(settled["generation"], 1)
            self.assertEqual(settled["synchronized_generation"], 1)

    def test_two_coordinators_share_single_export_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            first_started = threading.Event()
            release_first = threading.Event()
            calls = 0
            active = 0
            max_active = 0
            guard = threading.Lock()

            def runner():
                nonlocal calls, active, max_active
                with guard:
                    calls += 1
                    call_number = calls
                    active += 1
                    max_active = max(max_active, active)
                try:
                    if call_number == 1:
                        first_started.set()
                        release_first.wait(2)
                    return {"success": True}
                finally:
                    with guard:
                        active -= 1

            first = self.coordinator(directory, runner)
            second = self.coordinator(directory, runner)
            first.request_sync()
            self.assertTrue(first_started.wait(1))
            second.request_sync()
            release_first.set()
            settled = second.wait_for_settled()

            self.assertEqual(calls, 2)
            self.assertEqual(max_active, 1)
            self.assertEqual(settled["synchronized_generation"], 2)

    def test_export_bearing_workflow_uses_same_exclusive_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            export_started = threading.Event()
            release_export = threading.Event()
            workflow_started = threading.Event()

            def runner():
                export_started.set()
                release_export.wait(2)
                return {"success": True}

            coordinator = self.coordinator(directory, runner)
            coordinator.request_sync()
            self.assertTrue(export_started.wait(1))

            workflow_thread = threading.Thread(
                target=lambda: coordinator.run_exclusive(workflow_started.set)
            )
            workflow_thread.start()
            self.assertFalse(workflow_started.wait(0.05))
            release_export.set()
            self.assertTrue(workflow_started.wait(1))
            workflow_thread.join(1)
            self.assertEqual(
                coordinator.wait_for_settled()["status"], "synchronized"
            )


if __name__ == "__main__":
    unittest.main()
