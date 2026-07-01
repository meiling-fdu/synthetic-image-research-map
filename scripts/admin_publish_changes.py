#!/usr/bin/env python3
"""Refresh, validate, commit selected project data, and push explicitly."""

from __future__ import annotations

import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence

try:
    from .admin_workflows import ALLOWED_WORKFLOWS, PUBLIC_VALIDATION
except ImportError:
    from admin_workflows import ALLOWED_WORKFLOWS, PUBLIC_VALIDATION


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
PUBLISH_PATHS = (
    "data/curated/",
    "data/manual/",
    "web/data/",
    "tests/",
)
EXCLUDED_PATHSPECS = (
    ":(exclude,glob)data/manual/key_papers_missing_*",
    ":(exclude,glob)data/manual/key_papers_query_failed_*",
    ":(exclude,glob)data/backups/**",
)
PUBLISH_PATHSPECS = (*PUBLISH_PATHS, *EXCLUDED_PATHSPECS)
RunCommand = Callable[[Sequence[str], Path], subprocess.CompletedProcess[str]]


def run_command(
    command: Sequence[str],
    repository_root: Path,
) -> subprocess.CompletedProcess[str]:
    """Run a command with visible output and return its result."""
    print(f"$ {shlex.join(command)}", flush=True)
    try:
        result = subprocess.run(
            list(command),
            cwd=repository_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError as error:
        print(f"ERROR: could not start command: {error}", file=sys.stderr)
        return subprocess.CompletedProcess(command, 127, stdout=str(error))
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return result


def run_step(
    label: str,
    command: Sequence[str],
    repository_root: Path,
    runner: RunCommand,
) -> bool:
    print(f"\n== {label} ==", flush=True)
    result = runner(command, repository_root)
    if result.returncode != 0:
        print(
            f"ERROR: {label} failed with exit code {result.returncode}.",
            file=sys.stderr,
        )
        return False
    print(f"{label}: succeeded.", flush=True)
    return True


def git_output(
    command: Sequence[str],
    repository_root: Path,
    runner: RunCommand,
) -> tuple[int, str]:
    result = runner(command, repository_root)
    return result.returncode, (result.stdout or "").strip()


def publish_changes(
    *,
    repository_root: Path = REPOSITORY_ROOT,
    runner: RunCommand = run_command,
    now: Callable[[], datetime] = datetime.now,
) -> int:
    print("Publishing curated data and public preview.", flush=True)

    print("\n== Full refresh pipeline ==", flush=True)
    for command in ALLOWED_WORKFLOWS["full_refresh"]:
        if not run_step(
            f"Refresh: {shlex.join(command)}",
            command,
            repository_root,
            runner,
        ):
            print("ERROR: publishing stopped during refresh.", file=sys.stderr)
            return 1
    print("Full refresh pipeline result: succeeded.", flush=True)

    if not run_step(
        "Public preview validation",
        PUBLIC_VALIDATION,
        repository_root,
        runner,
    ):
        print("ERROR: publishing stopped before Git staging.", file=sys.stderr)
        return 1
    print("Validation result: succeeded.", flush=True)

    print("\n== Git status before staging ==", flush=True)
    status_code, status = git_output(
        ("git", "status", "--short"),
        repository_root,
        runner,
    )
    if status_code != 0:
        print("ERROR: could not inspect Git status.", file=sys.stderr)
        return 1
    if not status:
        print("Working tree is clean.", flush=True)

    print("\n== Stage publishable files ==", flush=True)
    stage_command = ("git", "add", "-A", "--", *PUBLISH_PATHSPECS)
    if runner(stage_command, repository_root).returncode != 0:
        print("ERROR: Git staging failed.", file=sys.stderr)
        return 1

    staged_command = (
        "git",
        "diff",
        "--cached",
        "--name-only",
        "--",
        *PUBLISH_PATHSPECS,
    )
    staged_code, staged_files = git_output(
        staged_command,
        repository_root,
        runner,
    )
    if staged_code != 0:
        print("ERROR: could not inspect staged files.", file=sys.stderr)
        return 1
    if not staged_files:
        print("No changes to publish.", flush=True)
        return 0
    print("Staged files:", flush=True)
    for path in staged_files.splitlines():
        print(f"  - {path}", flush=True)

    branch_code, branch = git_output(
        ("git", "branch", "--show-current"),
        repository_root,
        runner,
    )
    if branch_code != 0:
        print("ERROR: could not determine the current branch.", file=sys.stderr)
        return 1
    if not branch:
        print("ERROR: cannot publish from a detached HEAD.", file=sys.stderr)
        return 1

    message = (
        "Update curated data and public preview "
        f"{now().astimezone().strftime('%Y-%m-%d %H:%M')}"
    )
    print("\n== Create commit ==", flush=True)
    commit_command = (
        "git",
        "commit",
        "--only",
        "-m",
        message,
        "--",
        *PUBLISH_PATHSPECS,
    )
    if runner(commit_command, repository_root).returncode != 0:
        print("ERROR: Git commit failed.", file=sys.stderr)
        return 1

    hash_code, commit_hash = git_output(
        ("git", "rev-parse", "HEAD"),
        repository_root,
        runner,
    )
    if hash_code != 0:
        print("ERROR: commit was created but its hash could not be read.", file=sys.stderr)
        return 1
    print(f"Commit created: {commit_hash}", flush=True)

    print(f"\n== Push current branch: {branch} ==", flush=True)
    if runner(("git", "push"), repository_root).returncode != 0:
        print(
            f"ERROR: push failed. Commit {commit_hash} remains local on {branch}.",
            file=sys.stderr,
        )
        return 1
    print(f"Push result: succeeded for {branch}.", flush=True)
    print("Publish Changes completed successfully.", flush=True)
    return 0


def main() -> int:
    return publish_changes()


if __name__ == "__main__":
    raise SystemExit(main())
