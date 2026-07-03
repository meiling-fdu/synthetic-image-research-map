#!/usr/bin/env python3
"""Whitelisted local maintenance workflows for the admin server."""

from __future__ import annotations

import os
import hashlib
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
COMMAND_TIMEOUT_SECONDS = 180
PUBLISH_TIMEOUT_SECONDS = 1_200
GIT_TIMEOUT_SECONDS = 15
TAIL_CHARACTER_LIMIT = 16_000
KNOWN_WORKFLOW_OUTPUTS = (
    Path("web/data/public_preview_map_data.json"),
    Path("web/data/public_preview_papers.json"),
    Path("data/curated/institution_location_review.csv"),
    Path("data/manual/key_paper_coverage_report.csv"),
    Path("data/manual/paper_marker_blocker_report.csv"),
    Path("data/manual/high_risk_marker_review.csv"),
    Path("data/manual/missing_author_mappings_report.csv"),
    Path("docs/missing_author_mappings_report.md"),
)

CURATED_VALIDATION = (
    "python3",
    "scripts/validate_curated_database.py",
)
PAPER_EXCLUSION_VALIDATION = (
    "python3",
    "scripts/validate_paper_exclusions.py",
)
EXPORT_PREVIEW = (
    "python3",
    "scripts/export_public_preview.py",
    "--preserve-existing",
)
PUBLIC_VALIDATION = (
    "python3",
    "scripts/validate_public_preview.py",
)
KEY_PAPER_AUDIT = (
    "python3",
    "scripts/audit_key_paper_coverage.py",
)
MARKER_BLOCKER_DIAGNOSIS = (
    "python3",
    "scripts/diagnose_paper_marker_blockers.py",
)
HIGH_RISK_MARKER_REPORT = (
    "python3",
    "scripts/report_high_risk_markers.py",
)
AUTHOR_MAPPING_REPORT = (
    "python3",
    "scripts/report_missing_author_mappings.py",
)
PUBLISH_CHANGES = (
    "python3",
    "scripts/admin_publish_changes.py",
)

ALLOWED_WORKFLOWS: Mapping[str, Sequence[Sequence[str]]] = {
    "curated_validation": (CURATED_VALIDATION,),
    "export_preview": (EXPORT_PREVIEW,),
    "public_validation": (PUBLIC_VALIDATION,),
    "author_mapping_report": (AUTHOR_MAPPING_REPORT,),
    "full_refresh": (
        CURATED_VALIDATION,
        PAPER_EXCLUSION_VALIDATION,
        EXPORT_PREVIEW,
        AUTHOR_MAPPING_REPORT,
        PUBLIC_VALIDATION,
        KEY_PAPER_AUDIT,
        MARKER_BLOCKER_DIAGNOSIS,
        HIGH_RISK_MARKER_REPORT,
    ),
    "publish_changes": (PUBLISH_CHANGES,),
}


class AdminWorkflowError(RuntimeError):
    """A local workflow could not be started safely."""


def _tail(value: str) -> str:
    if len(value) <= TAIL_CHARACTER_LIMIT:
        return value
    return f"… output truncated …\n{value[-TAIL_CHARACTER_LIMIT:]}"


def _display_command(command: Sequence[str]) -> str:
    return " ".join(command)


def _run(
    command: Sequence[str],
    *,
    timeout: int,
) -> Dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            list(command),
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "PYTHONPYCACHEPREFIX": (
                    "/tmp/synthetic-image-research-map-pycache"
                ),
            },
            timeout=timeout,
            check=False,
        )
        return {
            "success": completed.returncode == 0,
            "command": _display_command(command),
            "exit_code": completed.returncode,
            "stdout_tail": _tail(completed.stdout),
            "stderr_tail": _tail(completed.stderr),
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        timeout_message = f"Command timed out after {timeout} seconds."
        return {
            "success": False,
            "command": _display_command(command),
            "exit_code": 124,
            "stdout_tail": _tail(stdout),
            "stderr_tail": _tail(
                f"{stderr}\n{timeout_message}".strip()
            ),
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except OSError as error:
        return {
            "success": False,
            "command": _display_command(command),
            "exit_code": 127,
            "stdout_tail": "",
            "stderr_tail": str(error),
            "duration_seconds": round(time.monotonic() - started, 3),
        }


def _git_status_map() -> Dict[str, str]:
    result = _run(("git", "status", "--short"), timeout=GIT_TIMEOUT_SECONDS)
    if not result["success"]:
        return {}
    statuses: Dict[str, str] = {}
    for line in result["stdout_tail"].splitlines():
        if len(line) < 4:
            continue
        status = line[:2]
        path = line[3:]
        statuses[path] = status
    return statuses


def git_status_result() -> Dict[str, Any]:
    result = _run(("git", "status", "--short"), timeout=GIT_TIMEOUT_SECONDS)
    return {**result, "changed_files": []}


def _changed_files(
    before: Mapping[str, str],
    after: Mapping[str, str],
    before_outputs: Mapping[str, str],
    after_outputs: Mapping[str, str],
) -> list[str]:
    status_changes = {
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    }
    content_changes = {
        path
        for path in set(before_outputs) | set(after_outputs)
        if before_outputs.get(path) != after_outputs.get(path)
    }
    return sorted(status_changes | content_changes)


def _known_output_signatures() -> Dict[str, str]:
    signatures = {}
    for relative_path in KNOWN_WORKFLOW_OUTPUTS:
        path = REPOSITORY_ROOT / relative_path
        try:
            signatures[str(relative_path)] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
        except OSError:
            signatures[str(relative_path)] = ""
    return signatures


def run_workflow(name: str) -> Dict[str, Any]:
    commands = ALLOWED_WORKFLOWS.get(name)
    if commands is None:
        raise AdminWorkflowError(f"unsupported admin workflow: {name}")

    before = _git_status_map()
    before_outputs = _known_output_signatures()
    started = time.monotonic()
    steps = []
    for command in commands:
        timeout = (
            PUBLISH_TIMEOUT_SECONDS
            if name == "publish_changes"
            else COMMAND_TIMEOUT_SECONDS
        )
        result = _run(command, timeout=timeout)
        steps.append(result)
        if not result["success"]:
            break
    after = _git_status_map()
    after_outputs = _known_output_signatures()

    success = len(steps) == len(commands) and all(
        step["success"] for step in steps
    )
    stdout_parts = [
        f"$ {step['command']}\n{step['stdout_tail']}".rstrip()
        for step in steps
        if step["stdout_tail"] or step["command"]
    ]
    stderr_parts = [
        f"$ {step['command']}\n{step['stderr_tail']}".rstrip()
        for step in steps
        if step["stderr_tail"]
    ]
    exit_code = steps[-1]["exit_code"] if steps else 1
    return {
        "success": success,
        "command": [_display_command(command) for command in commands],
        "exit_code": exit_code,
        "stdout_tail": _tail("\n\n".join(stdout_parts)),
        "stderr_tail": _tail("\n\n".join(stderr_parts)),
        "duration_seconds": round(time.monotonic() - started, 3),
        "changed_files": _changed_files(
            before,
            after,
            before_outputs,
            after_outputs,
        ),
        "steps": steps,
    }
