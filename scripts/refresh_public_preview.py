#!/usr/bin/env python3
"""Refresh, report on, and validate the public preview dataset.

This convenience command delegates all work to the existing pipeline, preview
export, reporting, and validation scripts. It never commits or pushes data.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPOSITORY_ROOT / "scripts"
PREVIEW_JSON = Path("web/data/public_preview_map_data.json")
QUALITY_REPORT = Path("docs/public_preview_report.md")
MAPPING_REPORT = Path("docs/missing_author_mappings_report.md")
MAPPING_REPORT_CSV = Path("data/manual/missing_author_mappings_report.csv")
CONFIDENCE_LEVELS = ("unresolved", "low", "medium", "high")


@dataclass(frozen=True)
class RefreshStep:
    number: int
    name: str
    command: List[str]


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the scoped candidate pipeline, export the public preview, "
            "regenerate its quality report, and validate it."
        )
    )
    parser.add_argument(
        "--skip-search",
        action="store_true",
        help="Reuse existing raw OpenAlex data instead of running a new search.",
    )
    parser.add_argument(
        "--max-results",
        type=positive_int,
        default=100,
        help="Maximum OpenAlex results per search query (default: 100).",
    )
    parser.add_argument(
        "--limit",
        type=positive_int,
        default=None,
        help=(
            "Maximum resolution/geocoding requests per pipeline step "
            "(default: no limit)."
        ),
    )
    parser.add_argument(
        "--max-records",
        type=positive_int,
        default=None,
        help="Maximum records in the public preview (default: no maximum).",
    )
    parser.add_argument(
        "--min-confidence",
        choices=CONFIDENCE_LEVELS,
        default="medium",
        help="Minimum preview resolution confidence (default: medium).",
    )
    parser.add_argument(
        "--user-agent",
        required=True,
        help=(
            "Identifying User-Agent passed to institution resolution and "
            "geocoding steps."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat validation warnings as failures.",
    )
    return parser.parse_args(argv)


def script_command(script_name: str, *arguments: object) -> List[str]:
    return [
        sys.executable,
        str(SCRIPTS_DIR / script_name),
        *(str(argument) for argument in arguments),
    ]


def build_steps(args: argparse.Namespace) -> List[RefreshStep]:
    preview_command = script_command(
        "export_public_preview.py",
        "--min-confidence",
        args.min_confidence,
    )
    if args.max_records is not None:
        preview_command.extend(["--max-records", args.max_records])
    # Every default refresh preserves the complete published baseline. Search
    # and local candidate snapshots can be partial; only an explicit
    # --max-records request may reduce the final preview.
    preview_command.append("--preserve-existing")
    validation_command = script_command("validate_public_preview.py")
    if args.strict:
        validation_command.append("--strict")

    commands = []
    if not args.skip_search:
        pipeline_command = script_command(
            "run_pipeline.py",
            "--max-results",
            args.max_results,
            "--user-agent",
            args.user_agent.strip(),
        )
        if args.limit is not None:
            pipeline_command.extend(["--limit", str(args.limit)])
        commands.append(
            (
                "Run scoped candidate pipeline",
                pipeline_command,
            )
        )
    commands.extend(
        [
            ("Export public preview JSON", preview_command),
            (
                "Generate public preview quality report",
                script_command("report_public_preview.py"),
            ),
            (
                "Generate missing author mappings report",
                script_command("report_missing_author_mappings.py"),
            ),
            ("Validate public preview", validation_command),
        ]
    )
    return [
        RefreshStep(number, name, command)
        for number, (name, command) in enumerate(commands, start=1)
    ]


def execute_steps(steps: Sequence[RefreshStep]) -> int:
    total = len(steps)
    for step in steps:
        prefix = f"[{step.number}/{total}]"
        print(f"{prefix} START: {step.name}", flush=True)
        print(f"  {shlex.join(step.command)}", flush=True)
        try:
            result = subprocess.run(
                step.command,
                cwd=REPOSITORY_ROOT,
                check=False,
            )
        except OSError as error:
            print(
                f"{prefix} ERROR: could not start {step.name}: {error}",
                file=sys.stderr,
            )
            return 1
        if result.returncode != 0:
            print(
                f"{prefix} FAILED: {step.name} exited with code "
                f"{result.returncode}. Refresh stopped.",
                file=sys.stderr,
            )
            return result.returncode or 1
        print(f"{prefix} COMPLETE: {step.name}", flush=True)

    print("\nPublic preview refresh complete.")
    print("Inspect these files before committing:")
    print(f"  - {PREVIEW_JSON}")
    print(f"  - {QUALITY_REPORT}")
    print(f"  - {MAPPING_REPORT}")
    print(f"  - {MAPPING_REPORT_CSV}")
    print("No files were committed or pushed.")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if not args.user_agent.strip():
        print("Error: --user-agent must not be empty.", file=sys.stderr)
        return 2
    return execute_steps(build_steps(args))


if __name__ == "__main__":
    raise SystemExit(main())
