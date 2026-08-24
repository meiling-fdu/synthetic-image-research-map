#!/usr/bin/env python3
"""Whitelisted local maintenance workflows for the admin server."""

from __future__ import annotations

import os
import hashlib
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
COMMAND_TIMEOUT_SECONDS = 180
PUBLISH_TIMEOUT_SECONDS = 1_200
GIT_TIMEOUT_SECONDS = 15
TAIL_CHARACTER_LIMIT = 16_000
ProgressCallback = Callable[[Mapping[str, Any]], None]
ADMIN_EDITABLE_PATHS = (
    Path("data/curated/papers.csv"),
    Path("data/curated/paper_exclusions.csv"),
    Path("data/curated/author_institution_mappings.csv"),
    Path("data/curated/institution_location_review.csv"),
    Path("data/curated/institution_locations.csv"),
    Path("data/curated/institution_aliases.csv"),
    Path("data/curated/institution_hierarchy.csv"),
    Path("data/curated/institution_search_relationships.csv"),
    Path("data/curated/institutions.csv"),
    Path("data/curated/institution_audit_log.csv"),
    Path("data/curated/institution_review_queue.csv"),
    Path("data/curated/review_decisions.csv"),
    Path("data/curated/paper_arxiv_links.csv"),
)

# Files written by the canonical full-refresh pipeline. Keep this list beside the
# workflow itself so publishing and the admin result UI cannot drift from it.
KNOWN_WORKFLOW_OUTPUTS = (
    Path("web/data/public_preview_map_data.json"),
    Path("web/data/public_preview_papers.json"),
    Path("data/curated/institution_location_review.csv"),
    Path("data/manual/key_paper_coverage_report.csv"),
    Path("data/manual/paper_marker_blocker_report.csv"),
    Path("data/manual/high_risk_marker_review.csv"),
    Path("data/manual/missing_author_mappings_report.csv"),
    Path("data/manual/institution_consistency_audit.csv"),
    Path("data/curated/institution_review_queue.csv"),
    Path("data/processed/orphan_institution_cleanup_audit.csv"),
    Path("data/processed/full_source_completeness_audit.csv"),
    Path("data/processed/institution_identity_resolution_audit.csv"),
    Path("docs/missing_author_mappings_report.md"),
    Path("docs/public_preview_report.md"),
    Path("docs/institution_identity_resolution_audit.md"),
)

CURATED_VALIDATION = (
    "python3",
    "scripts/validate_curated_database.py",
)
INSTITUTION_CONSISTENCY_REPORT = (
    "python3",
    "scripts/audit_institution_consistency.py",
)
INSTITUTION_IDENTITY_RESOLUTION = (
    "python3",
    "scripts/audit_institution_identities.py",
    "--write",
)
INSTITUTION_REVIEW_QUEUE_SYNC = (
    "python3",
    "scripts/sync_institution_review_queue.py",
)
ORPHAN_INSTITUTION_CLEANUP = (
    "python3",
    "scripts/orphan_institution_cleanup.py",
    "--authoritative",
)
FULL_SOURCE_COMPLETENESS_AUDIT = (
    "python3",
    "scripts/full_source_completeness.py",
)
VENUE_CANONICALIZATION_PREFLIGHT = (
    "python3",
    "scripts/synchronize_venue_metadata.py",
)
CURATED_SCHEMA_MIGRATION = (
    "python3",
    "scripts/curated_schema_migrations.py",
)
VENUE_CANONICALIZATION = (
    "python3",
    "scripts/synchronize_venue_metadata.py",
    "--write",
)
PAPER_EXCLUSION_VALIDATION = (
    "python3",
    "scripts/validate_paper_exclusions.py",
)
ACTIVE_EXCLUSION_PUBLIC_MIGRATION = (
    "python3",
    "scripts/migrate_active_exclusions_from_public_outputs.py",
)
EXPORT_PREVIEW = (
    "python3",
    "scripts/export_public_preview.py",
    "--preserve-existing",
)
PUBLIC_PREVIEW_REPORT = (
    "python3",
    "scripts/report_public_preview.py",
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
    "institution_consistency_audit": (INSTITUTION_CONSISTENCY_REPORT,),
    "full_refresh": (
        VENUE_CANONICALIZATION_PREFLIGHT,
        CURATED_SCHEMA_MIGRATION,
        VENUE_CANONICALIZATION,
        INSTITUTION_IDENTITY_RESOLUTION,
        INSTITUTION_CONSISTENCY_REPORT,
        INSTITUTION_REVIEW_QUEUE_SYNC,
        FULL_SOURCE_COMPLETENESS_AUDIT,
        ORPHAN_INSTITUTION_CLEANUP,
        CURATED_VALIDATION,
        ACTIVE_EXCLUSION_PUBLIC_MIGRATION,
        PAPER_EXCLUSION_VALIDATION,
        EXPORT_PREVIEW,
        PUBLIC_PREVIEW_REPORT,
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


def _error_summary(stderr: str, stdout: str) -> str:
    lines = [
        line.strip()
        for line in (stderr or stdout).splitlines()
        if line.strip() and not line.startswith("$ ")
    ]
    errors = [line for line in lines if line.startswith("ERROR:")]
    generic_fragments = (
        "reported validation errors",
        "failed with exit code",
        "publishing stopped",
    )
    specific_errors = [
        line for line in errors
        if not any(fragment in line.casefold() for fragment in generic_fragments)
    ]
    summary = (
        specific_errors[-1]
        if specific_errors
        else (errors[-1] if errors else (lines[-1] if lines else ""))
    )
    return summary.replace(str(REPOSITORY_ROOT), ".")[:1_000]


def _safe_output(value: str) -> str:
    return value.replace(str(REPOSITORY_ROOT), ".")


def _run(
    command: Sequence[str],
    *,
    timeout: int,
    progress: ProgressCallback | None = None,
) -> Dict[str, Any]:
    started = time.monotonic()
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    last_stage = ""
    timed_out = False

    def read_stream(stream: Any, parts: list[str], stream_name: str) -> None:
        nonlocal last_stage
        for line in iter(stream.readline, ""):
            parts.append(line)
            stripped = line.strip()
            if stripped.startswith("== ") and stripped.endswith(" =="):
                last_stage = stripped[3:-3].strip()
            if progress and stripped:
                progress(
                    {
                        "stage": last_stage,
                        "command": stripped[2:] if stripped.startswith("$ ") else "",
                        "stream": stream_name,
                        "line": stripped,
                        "elapsed_seconds": round(time.monotonic() - started, 3),
                    }
                )
        stream.close()

    try:
        process = subprocess.Popen(
            list(command),
            cwd=REPOSITORY_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={
                **os.environ,
                "PYTHONPYCACHEPREFIX": (
                    "/tmp/synthetic-image-research-map-pycache"
                ),
            },
            start_new_session=True,
        )
        readers = [
            threading.Thread(
                target=read_stream,
                args=(process.stdout, stdout_parts, "stdout"),
                daemon=True,
            ),
            threading.Thread(
                target=read_stream,
                args=(process.stderr, stderr_parts, "stderr"),
                daemon=True,
            ),
        ]
        for reader in readers:
            reader.start()
        try:
            return_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                return_code = process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                return_code = process.wait()
        for reader in readers:
            reader.join(timeout=2)

        stdout = "".join(stdout_parts)
        stderr = "".join(stderr_parts)
        if timed_out:
            timeout_message = f"Command timed out after {timeout} seconds."
            stderr = f"{stderr}\n{timeout_message}".strip()
            return_code = 124
        return {
            "success": return_code == 0,
            "command": _display_command(command),
            "stage": last_stage or _display_command(command),
            "exit_code": return_code,
            "stdout_tail": _tail(_safe_output(stdout)),
            "stderr_tail": _tail(_safe_output(stderr)),
            "error_summary": _error_summary(stderr, stdout),
            "timed_out": timed_out,
            "failure_kind": (
                "timeout" if timed_out
                else ("subprocess_exit" if return_code else "")
            ),
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except OSError as error:
        return {
            "success": False,
            "command": _display_command(command),
            "stage": last_stage or _display_command(command),
            "exit_code": 127,
            "stdout_tail": "",
            "stderr_tail": str(error),
            "error_summary": str(error)[:1_000],
            "timed_out": False,
            "failure_kind": "start_failure",
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


def run_workflow(
    name: str,
    *,
    progress: ProgressCallback | None = None,
) -> Dict[str, Any]:
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
        if progress:
            progress(
                {
                    "stage": f"Starting {name}",
                    "command": _display_command(command),
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                }
            )
        result = _run(command, timeout=timeout, progress=progress)
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
    failed_step = next(
        (step for step in reversed(steps) if not step["success"]),
        None,
    )
    return {
        "success": success,
        "command": [_display_command(command) for command in commands],
        "exit_code": exit_code,
        "failed_stage": failed_step.get("stage", "") if failed_step else "",
        "error_summary": (
            failed_step.get("error_summary", "") if failed_step else ""
        ),
        "timed_out": bool(failed_step and failed_step.get("timed_out")),
        "failure_kind": (
            failed_step.get("failure_kind", "") if failed_step else ""
        ),
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
