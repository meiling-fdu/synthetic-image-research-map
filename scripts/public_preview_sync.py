#!/usr/bin/env python3
"""Durable single-flight synchronization for public-preview exports."""

from __future__ import annotations

import fcntl
import json
import os
import tempfile
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Mapping


DEFAULT_STATE_PATH = (
    Path(__file__).resolve().parent.parent
    / ".admin"
    / "public_preview_sync.json"
)

_LOCK_REGISTRY_GUARD = threading.Lock()
_PROCESS_LOCKS: Dict[str, threading.RLock] = {}


def _process_lock(path: Path) -> threading.RLock:
    key = str(path.resolve())
    with _LOCK_REGISTRY_GUARD:
        lock = _PROCESS_LOCKS.get(key)
        if lock is None:
            lock = threading.RLock()
            _PROCESS_LOCKS[key] = lock
        return lock


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_state() -> Dict[str, Any]:
    return {
        "version": 1,
        "generation": 0,
        "synchronized_generation": 0,
        "status": "synchronized",
        "running_generation": None,
        "requested_at": None,
        "started_at": None,
        "completed_at": None,
        "last_error": "",
        "export_invocations": 0,
    }


def _normalized_state(value: Mapping[str, Any] | None) -> Dict[str, Any]:
    state = _default_state()
    if value:
        state.update(value)
    state["version"] = 1
    state["generation"] = max(0, int(state.get("generation") or 0))
    state["synchronized_generation"] = max(
        0,
        min(
            state["generation"],
            int(state.get("synchronized_generation") or 0),
        ),
    )
    state["export_invocations"] = max(
        0, int(state.get("export_invocations") or 0)
    )
    if state.get("status") not in {
        "idle", "running", "dirty", "failed", "synchronized",
    }:
        state["status"] = (
            "dirty"
            if state["generation"] > state["synchronized_generation"]
            else "synchronized"
        )
    if state["generation"] <= state["synchronized_generation"]:
        state["status"] = "synchronized"
        state["running_generation"] = None
        state["last_error"] = ""
    return state


def _read_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return _default_state()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"could not read public-preview synchronization state: {error}"
        ) from error
    if not isinstance(value, dict):
        raise RuntimeError("public-preview synchronization state must be an object")
    return _normalized_state(value)


def _atomic_write_state(path: Path, state: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(
                dict(state),
                handle,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary.exists():
            temporary.unlink()


def _durable_unlink(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    directory_descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


class PublicPreviewSyncCoordinator:
    """Coalesce dirty generations onto one full-export worker."""

    def __init__(
        self,
        state_path: Path,
        export_runner: Callable[[], Mapping[str, Any]],
        *,
        retry_delay: float = 0.05,
        autostart: bool = True,
    ) -> None:
        self.state_path = Path(state_path)
        self.state_lock_path = self.state_path.with_suffix(
            self.state_path.suffix + ".lock"
        )
        self.export_lock_path = self.state_path.with_suffix(
            self.state_path.suffix + ".export.lock"
        )
        self.curated_change_intent_path = self.state_path.with_suffix(
            self.state_path.suffix + ".curated-change-intent"
        )
        self.export_runner = export_runner
        self.retry_delay = retry_delay
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._lifecycle_lock = threading.Lock()
        self._thread: threading.Thread | None = None
        if autostart:
            self.start()

    @contextmanager
    def _locked_state(self) -> Iterator[Dict[str, Any]]:
        self.state_lock_path.parent.mkdir(parents=True, exist_ok=True)
        process_lock = _process_lock(self.state_lock_path)
        with process_lock:
            with self.state_lock_path.open("a+b") as lock_handle:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
                try:
                    state = _read_state(self.state_path)
                    yield state
                finally:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)

    @contextmanager
    def _try_export_lock(self) -> Iterator[bool]:
        self.export_lock_path.parent.mkdir(parents=True, exist_ok=True)
        process_lock = _process_lock(self.export_lock_path)
        if not process_lock.acquire(blocking=False):
            yield False
            return
        try:
            with self.export_lock_path.open("a+b") as lock_handle:
                try:
                    fcntl.flock(
                        lock_handle.fileno(),
                        fcntl.LOCK_EX | fcntl.LOCK_NB,
                    )
                except BlockingIOError:
                    yield False
                    return
                try:
                    yield True
                finally:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        finally:
            process_lock.release()

    def start(self) -> None:
        with self._lifecycle_lock:
            if self._thread is not None:
                return
            with self._locked_state() as state:
                if self.curated_change_intent_path.exists():
                    if state["generation"] <= state["synchronized_generation"]:
                        state["generation"] = state["synchronized_generation"] + 1
                    state["status"] = "dirty"
                    state["running_generation"] = None
                    state["requested_at"] = _now()
                    _atomic_write_state(self.state_path, state)
                    _durable_unlink(self.curated_change_intent_path)
                if state["generation"] > state["synchronized_generation"]:
                    state["status"] = "dirty"
                    state["running_generation"] = None
                    _atomic_write_state(self.state_path, state)
                    self._wake.set()
            self._thread = threading.Thread(
                target=self._worker,
                name="public-preview-sync",
                daemon=True,
            )
            self._thread.start()

    def begin_curated_change(self) -> None:
        """Write-ahead crash marker before any curated file is replaced."""
        with self._locked_state():
            _atomic_write_state(
                self.curated_change_intent_path,
                {"version": 1, "created_at": _now()},
            )

    def complete_curated_change(self) -> None:
        """Clear the marker after the dirty generation is durable."""
        with self._locked_state():
            _durable_unlink(self.curated_change_intent_path)

    def cancel_curated_change(self) -> None:
        """Clear the marker after curated file snapshots are restored."""
        self.complete_curated_change()

    def request_sync(self) -> Dict[str, Any]:
        """Durably record one newer curated generation and wake the worker."""
        with self._locked_state() as state:
            state["generation"] = max(
                state["generation"], state["synchronized_generation"]
            ) + 1
            state["status"] = "dirty"
            state["requested_at"] = _now()
            state["last_error"] = ""
            _atomic_write_state(self.state_path, state)
            snapshot = dict(state)
        self._wake.set()
        self.start()
        return snapshot

    def retry(self) -> Dict[str, Any]:
        """Retry a dirty generation, or force a new full synchronization."""
        with self._locked_state() as state:
            if state["generation"] <= state["synchronized_generation"]:
                state["generation"] = state["synchronized_generation"] + 1
            state["status"] = "dirty"
            state["requested_at"] = _now()
            state["last_error"] = ""
            _atomic_write_state(self.state_path, state)
            snapshot = dict(state)
        self._wake.set()
        self.start()
        return snapshot

    def snapshot(self) -> Dict[str, Any]:
        with self._locked_state() as state:
            return dict(state)

    def run_exclusive(self, operation: Callable[[], Any]) -> Any:
        """Run another export-bearing Admin workflow under the same lock."""
        self.export_lock_path.parent.mkdir(parents=True, exist_ok=True)
        process_lock = _process_lock(self.export_lock_path)
        with process_lock:
            with self.export_lock_path.open("a+b") as lock_handle:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
                try:
                    return operation()
                finally:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)

    def close(self, timeout: float | None = None) -> None:
        self._stop.set()
        self._wake.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)

    def wait_for_settled(self, timeout: float = 30.0) -> Dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state = self.snapshot()
            if state["status"] in {"synchronized", "failed"}:
                return state
            time.sleep(0.01)
        raise TimeoutError("public-preview synchronization did not settle")

    @staticmethod
    def _failure_message(result: Mapping[str, Any] | None, error: Exception | None) -> str:
        if error is not None:
            return f"{type(error).__name__}: {error}"
        result = result or {}
        return str(
            result.get("error_summary")
            or result.get("stderr_tail")
            or result.get("message")
            or "public preview export failed"
        ).strip()

    def _worker(self) -> None:
        while not self._stop.is_set():
            self._wake.wait()
            self._wake.clear()
            while not self._stop.is_set():
                state = self.snapshot()
                if state["generation"] <= state["synchronized_generation"]:
                    break
                if state["status"] == "failed":
                    break
                with self._try_export_lock() as acquired:
                    if not acquired:
                        self._wake.wait(self.retry_delay)
                        self._wake.clear()
                        continue
                    with self._locked_state() as current:
                        if current["generation"] <= current["synchronized_generation"]:
                            break
                        start_generation = current["generation"]
                        current["status"] = "running"
                        current["running_generation"] = start_generation
                        current["started_at"] = _now()
                        current["completed_at"] = None
                        current["last_error"] = ""
                        current["export_invocations"] += 1
                        _atomic_write_state(self.state_path, current)

                    result: Mapping[str, Any] | None = None
                    error: Exception | None = None
                    try:
                        result = dict(self.export_runner())
                    except Exception as caught:  # Keep the worker retryable.
                        error = caught
                    success = error is None and bool((result or {}).get("success"))

                    with self._locked_state() as current:
                        current["running_generation"] = None
                        current["completed_at"] = _now()
                        newer_generation_exists = (
                            current["generation"] != start_generation
                        )
                        if success and not newer_generation_exists:
                            current["synchronized_generation"] = start_generation
                            current["status"] = "synchronized"
                            current["last_error"] = ""
                        elif newer_generation_exists:
                            current["status"] = "dirty"
                            current["last_error"] = (
                                "" if success else self._failure_message(result, error)
                            )
                        else:
                            current["status"] = "failed"
                            current["last_error"] = self._failure_message(
                                result, error
                            )
                        _atomic_write_state(self.state_path, current)
                        run_again = current["status"] == "dirty"
                if not run_again:
                    break
