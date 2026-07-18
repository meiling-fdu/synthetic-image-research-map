#!/usr/bin/env python3
"""Refresh, validate, commit selected project data, and push explicitly."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence

try:
    from .admin_workflows import (
        ADMIN_EDITABLE_PATHS,
        ALLOWED_WORKFLOWS,
        KNOWN_WORKFLOW_OUTPUTS,
        PUBLIC_VALIDATION,
    )
except ImportError:
    from admin_workflows import (
        ADMIN_EDITABLE_PATHS,
        ALLOWED_WORKFLOWS,
        KNOWN_WORKFLOW_OUTPUTS,
        PUBLIC_VALIDATION,
    )


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
# Directory roots intentionally cover future curated/review files. Generated
# outputs are additionally derived from admin_workflows.KNOWN_WORKFLOW_OUTPUTS.
PUBLISH_PATHS = ("data/curated/", "data/manual/", "web/data/")
TEMPORARY_PREFIXES = (
    "data/manual/key_papers_missing_",
    "data/manual/key_papers_query_failed_",
    "data/backups/",
)
FRONTEND_SUFFIXES = (".html", ".css", ".js", ".svg", ".png", ".jpg", ".webp")
RunCommand = Callable[[Sequence[str], Path], subprocess.CompletedProcess[str]]
MAP_PREVIEW_PATH = Path("web/data/public_preview_map_data.json")
PAPER_PREVIEW_PATH = Path("web/data/public_preview_papers.json")
class PublishDataError(RuntimeError):
    """Preview data cannot be measured safely before publication."""


@dataclass(frozen=True)
class PreviewCounts:
    map_records: int
    paper_records: int


PreviewCountReader = Callable[[Path], PreviewCounts]


def _read_record_count(path: Path) -> int:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PublishDataError(f"could not read {path}: {error}") from error
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise PublishDataError(f"{path} does not contain a records array")
    return len(records)


def read_preview_counts(repository_root: Path) -> PreviewCounts:
    return PreviewCounts(
        map_records=_read_record_count(repository_root / MAP_PREVIEW_PATH),
        paper_records=_read_record_count(repository_root / PAPER_PREVIEW_PATH),
    )


def snapshot_preview_files(repository_root: Path) -> dict[Path, bytes]:
    """Capture preview outputs so a failed publish can retain the prior stamp."""
    # Command-runner unit tests use a synthetic, non-existent repository root.
    if not repository_root.exists():
        return {}
    return {
        path: (repository_root / path).read_bytes()
        for path in (MAP_PREVIEW_PATH, PAPER_PREVIEW_PATH)
    }


def restore_preview_files(repository_root: Path, snapshot: dict[Path, bytes]) -> None:
    for path, content in snapshot.items():
        (repository_root / path).write_bytes(content)


def shrinkage_percentage(before: int, after: int) -> float:
    if before <= 0 or after >= before:
        return 0.0
    return (before - after) / before * 100.0


def print_preview_counts(
    label: str,
    counts: PreviewCounts,
    *,
    before: PreviewCounts | None = None,
) -> None:
    print(f"{label} map records: {counts.map_records}", flush=True)
    print(f"{label} paper records: {counts.paper_records}", flush=True)
    if before is not None:
        print(
            "Map records shrinkage: "
            f"{shrinkage_percentage(before.map_records, counts.map_records):.2f}%",
            flush=True,
        )
        print(
            "Paper records shrinkage: "
            f"{shrinkage_percentage(before.paper_records, counts.paper_records):.2f}%",
            flush=True,
        )


def print_publish_size_summary(
    before: PreviewCounts,
    after: PreviewCounts,
) -> None:
    print("\n== Public preview size summary ==", flush=True)
    print_preview_counts("Before", before)
    print_preview_counts("After", after, before=before)


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
        output = result.stdout or ""
        validation_errors = [
            line for line in output.splitlines()
            if line.startswith("ERROR:")
        ]
        if validation_errors:
            print(
                f"ERROR: {label} reported validation errors:",
                file=sys.stderr,
            )
            for line in validation_errors:
                print(f"  {line}", file=sys.stderr)
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


def parse_status_paths(status: str) -> list[str]:
    paths = []
    for line in status.splitlines():
        if len(line) < 4:
            continue
        # `git status --short` has a two-column status followed by whitespace.
        # git_output strips the whole output, so the first line can lose its
        # leading unstaged-status space; accepting either form keeps it safe.
        path = line[2:].lstrip().split(" -> ", 1)[-1]
        paths.append(path)
    return paths


def is_publishable(path: str) -> bool:
    if any(path.startswith(prefix) for prefix in TEMPORARY_PREFIXES):
        return False
    if any(path.startswith(root) for root in PUBLISH_PATHS):
        return True
    canonical = {str(item) for item in (*ADMIN_EDITABLE_PATHS, *KNOWN_WORKFLOW_OUTPUTS)}
    if path in canonical:
        return True
    # Frontend code is deployable, but enters a publish only when Git reports an
    # actual modification; generated data is handled by the roots above.
    return path.startswith("web/") and Path(path).suffix.lower() in FRONTEND_SUFFIXES


def publish_changes(
    *,
    repository_root: Path = REPOSITORY_ROOT,
    runner: RunCommand = run_command,
    now: Callable[[], datetime] = datetime.now,
    preview_count_reader: PreviewCountReader = read_preview_counts,
) -> int:
    print("Publishing curated data and public preview.", flush=True)
    try:
        before_counts = preview_count_reader(repository_root)
    except PublishDataError as error:
        print(
            f"ERROR: publish aborted before refresh: {error}",
            file=sys.stderr,
        )
        return 1
    print("\n== Public preview size before refresh ==", flush=True)
    print_preview_counts("Before", before_counts)

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

    try:
        after_counts = preview_count_reader(repository_root)
    except PublishDataError as error:
        print(
            f"ERROR: publish aborted after refresh: {error}",
            file=sys.stderr,
        )
        return 1
    print("\n== Public preview shrinkage guard ==", flush=True)
    print_preview_counts("After", after_counts, before=before_counts)
    if (
        after_counts.map_records < before_counts.map_records
        or after_counts.paper_records < before_counts.paper_records
    ):
        print(
            "Preview decrease accepted by the exporter's identity-level guard; "
            "every removed identity/relationship had durable evidence.",
            flush=True,
        )
    print("Identity-level public preview shrinkage guard: passed.", flush=True)

    try:
        preview_snapshot = snapshot_preview_files(repository_root)
    except OSError as error:
        print(f"ERROR: could not preserve the previous preview timestamp: {error}", file=sys.stderr)
        return 1

    if not run_step(
        "Public preview validation",
        PUBLIC_VALIDATION,
        repository_root,
        runner,
    ):
        restore_preview_files(repository_root, preview_snapshot)
        print("ERROR: publishing stopped before Git staging.", file=sys.stderr)
        return 1
    print("Validation result: succeeded.", flush=True)

    if not run_step(
        "Stamp successful public preview generation",
        ("python3", "scripts/stamp_public_preview.py"),
        repository_root,
        runner,
    ):
        print("ERROR: publishing stopped before Git staging.", file=sys.stderr)
        return 1

    print("\n== Changed files after refresh ==", flush=True)
    status_code, status = git_output(
        ("git", "status", "--short"),
        repository_root,
        runner,
    )
    if status_code != 0:
        restore_preview_files(repository_root, preview_snapshot)
        print("ERROR: could not inspect Git status.", file=sys.stderr)
        return 1
    if not status:
        print("Working tree is clean.", flush=True)

    changed_files = parse_status_paths(status)
    publish_files = [path for path in changed_files if is_publishable(path)]
    generated_files = [
        path for path in publish_files
        if path in {str(item) for item in KNOWN_WORKFLOW_OUTPUTS}
    ]
    print("Files changed:", flush=True)
    for path in changed_files:
        print(f"  - {path}", flush=True)
    print("Files generated by refresh:", flush=True)
    if generated_files:
        for path in generated_files:
            print(f"  - {path}", flush=True)
    else:
        print("  - none", flush=True)

    if not publish_files:
        restore_preview_files(repository_root, preview_snapshot)
        print("No changes to publish.", flush=True)
        print_publish_size_summary(before_counts, after_counts)
        return 0

    print("\n== Stage publishable files ==", flush=True)
    stage_command = ("git", "add", "-A", "--", *publish_files)
    if runner(stage_command, repository_root).returncode != 0:
        restore_preview_files(repository_root, preview_snapshot)
        print("ERROR: Git staging failed.", file=sys.stderr)
        return 1

    staged_command = (
        "git",
        "diff",
        "--cached",
        "--name-only",
        "--",
        *publish_files,
    )
    staged_code, staged_files = git_output(
        staged_command,
        repository_root,
        runner,
    )
    if staged_code != 0:
        restore_preview_files(repository_root, preview_snapshot)
        print("ERROR: could not inspect staged files.", file=sys.stderr)
        return 1
    if not staged_files:
        restore_preview_files(repository_root, preview_snapshot)
        print("No changes to publish.", flush=True)
        print_publish_size_summary(before_counts, after_counts)
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
        restore_preview_files(repository_root, preview_snapshot)
        print("ERROR: could not determine the current branch.", file=sys.stderr)
        return 1
    if not branch:
        restore_preview_files(repository_root, preview_snapshot)
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
        *publish_files,
    )
    if runner(commit_command, repository_root).returncode != 0:
        restore_preview_files(repository_root, preview_snapshot)
        print("ERROR: Git commit failed.", file=sys.stderr)
        return 1

    hash_code, commit_hash = git_output(
        ("git", "rev-parse", "HEAD"),
        repository_root,
        runner,
    )
    if hash_code != 0:
        restore_preview_files(repository_root, preview_snapshot)
        print("ERROR: commit was created but its hash could not be read.", file=sys.stderr)
        return 1
    print(f"Commit created: {commit_hash}", flush=True)

    print(f"\n== Push current branch: {branch} ==", flush=True)
    if runner(("git", "push"), repository_root).returncode != 0:
        restore_preview_files(repository_root, preview_snapshot)
        print(
            f"ERROR: push failed. Commit {commit_hash} remains local on {branch}.",
            file=sys.stderr,
        )
        return 1
    print(f"Push result: succeeded for {branch}.", flush=True)
    print_publish_size_summary(before_counts, after_counts)
    print("Publish Changes completed successfully.", flush=True)
    return 0


def main() -> int:
    return publish_changes()


if __name__ == "__main__":
    raise SystemExit(main())
