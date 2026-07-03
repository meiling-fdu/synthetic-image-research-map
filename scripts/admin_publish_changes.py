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
MAP_PREVIEW_PATH = Path("web/data/public_preview_map_data.json")
PAPER_PREVIEW_PATH = Path("web/data/public_preview_papers.json")
MAX_SHRINKAGE_RATIO = 0.05
MIN_MAP_RECORDS = 700
MIN_PAPER_RECORDS = 350


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


def shrinkage_percentage(before: int, after: int) -> float:
    if before <= 0 or after >= before:
        return 0.0
    return (before - after) / before * 100.0


def preview_shrinkage_reasons(
    before: PreviewCounts,
    after: PreviewCounts,
) -> list[str]:
    reasons = []
    map_shrinkage = shrinkage_percentage(
        before.map_records, after.map_records
    )
    paper_shrinkage = shrinkage_percentage(
        before.paper_records, after.paper_records
    )
    if map_shrinkage > MAX_SHRINKAGE_RATIO * 100:
        reasons.append(
            f"map records decreased by {map_shrinkage:.2f}% "
            f"(maximum allowed: {MAX_SHRINKAGE_RATIO * 100:.0f}%)"
        )
    if paper_shrinkage > MAX_SHRINKAGE_RATIO * 100:
        reasons.append(
            f"paper records decreased by {paper_shrinkage:.2f}% "
            f"(maximum allowed: {MAX_SHRINKAGE_RATIO * 100:.0f}%)"
        )
    if after.map_records < MIN_MAP_RECORDS:
        reasons.append(
            f"after map records {after.map_records} is below "
            f"the safety floor {MIN_MAP_RECORDS}"
        )
    if after.paper_records < MIN_PAPER_RECORDS:
        reasons.append(
            f"after paper records {after.paper_records} is below "
            f"the safety floor {MIN_PAPER_RECORDS}"
        )
    return reasons


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
    shrinkage_reasons = preview_shrinkage_reasons(
        before_counts, after_counts
    )
    if shrinkage_reasons:
        print(
            "ERROR: Publish Changes aborted by public preview shrinkage guard.",
            file=sys.stderr,
        )
        for reason in shrinkage_reasons:
            print(f"  - {reason}", file=sys.stderr)
        print(
            "No files were staged, committed, or pushed.",
            file=sys.stderr,
        )
        return 1
    if (
        after_counts.map_records < before_counts.map_records
        or after_counts.paper_records < before_counts.paper_records
    ):
        print(
            "Small preview decrease accepted; confirmed paper-version merges "
            "can legitimately remove duplicate papers and markers.",
            flush=True,
        )
    print("Public preview shrinkage guard: passed.", flush=True)

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
    print_publish_size_summary(before_counts, after_counts)
    print("Publish Changes completed successfully.", flush=True)
    return 0


def main() -> int:
    return publish_changes()


if __name__ == "__main__":
    raise SystemExit(main())
