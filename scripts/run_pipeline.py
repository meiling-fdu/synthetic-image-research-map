#!/usr/bin/env python3
"""Run the existing OpenAlex candidate-data scripts in pipeline order.

This file only orchestrates subprocesses. It does not duplicate collection,
resolution, geocoding, export, or review-queue logic and never writes manually
curated files itself.
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

RAW_DIR = Path("data/raw/openalex")
PROCESSED_DIR = Path("data/processed")
PAPERS_CSV = PROCESSED_DIR / "openalex_candidate_papers.csv"
IN_SCOPE_PAPERS_CSV = PROCESSED_DIR / "openalex_candidate_papers_in_scope.csv"
ORIGINAL_AFFILIATIONS_CSV = (
    PROCESSED_DIR / "openalex_candidate_affiliations.csv"
)
IN_SCOPE_AFFILIATIONS_CSV = (
    PROCESSED_DIR / "openalex_candidate_affiliations_in_scope.csv"
)
RESOLVED_AFFILIATIONS_CSV = (
    PROCESSED_DIR / "openalex_candidate_affiliations_resolved.csv"
)
GEOCODED_AFFILIATIONS_CSV = (
    PROCESSED_DIR / "openalex_candidate_affiliations_geocoded.csv"
)
RESOLUTION_REPORT = PROCESSED_DIR / "institution_resolution_report.csv"
RESOLUTION_CACHE = PROCESSED_DIR / "institution_resolution_cache.json"
GEOCODING_CACHE = PROCESSED_DIR / "geocoding_cache.json"
REVIEW_QUEUE = PROCESSED_DIR / "institution_review_queue.csv"
MAP_JSON = Path("web/data/openalex_candidate_map_data.json")


@dataclass
class PipelineStep:
    number: int
    name: str
    command: List[str]
    enabled: bool = True


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def polite_delay(value: str) -> float:
    parsed = float(value)
    if parsed < 1.0:
        raise argparse.ArgumentTypeError("must be at least 1.0 second")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the OpenAlex candidate workflow from raw search through local "
            "map export and institution review queue generation."
        )
    )
    parser.add_argument(
        "--max-results",
        type=positive_int,
        default=100,
        help="Maximum OpenAlex candidate results per search query (default: 100).",
    )
    parser.add_argument(
        "--limit",
        type=positive_int,
        help="Maximum external resolution/geocoding requests per step.",
    )
    parser.add_argument(
        "--user-agent",
        default="",
        help="Identifying User-Agent passed to resolution and geocoding steps.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=polite_delay,
        default=1.2,
        help="Delay between external requests (default: 1.2).",
    )
    parser.add_argument(
        "--skip-search",
        action="store_true",
        help="Reuse existing raw OpenAlex files instead of searching again.",
    )
    parser.add_argument(
        "--skip-resolution",
        action="store_true",
        help="Skip authoritative institution resolution.",
    )
    parser.add_argument(
        "--skip-geocoding",
        action="store_true",
        help="Skip generic Nominatim geocoding.",
    )
    parser.add_argument(
        "--skip-review-queue",
        action="store_true",
        help="Skip institution review queue generation.",
    )
    parser.add_argument(
        "--include-out-of-scope",
        action="store_true",
        help=(
            "Send all audit candidates through downstream steps for debugging; "
            "the default pipeline processes only in-scope papers and affiliations."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print pipeline commands without executing subprocesses.",
    )
    return parser.parse_args(argv)


def script_command(script_name: str, *arguments: object) -> List[str]:
    return [
        sys.executable,
        str(SCRIPTS_DIR / script_name),
        *(str(argument) for argument in arguments),
    ]


def add_shared_network_arguments(
    command: List[str],
    args: argparse.Namespace,
) -> None:
    command.extend(["--sleep-seconds", str(args.sleep_seconds)])
    if args.limit is not None:
        command.extend(["--limit", str(args.limit)])
    if args.user_agent.strip():
        command.extend(["--user-agent", args.user_agent.strip()])


def build_steps(args: argparse.Namespace) -> List[PipelineStep]:
    search_command = script_command(
        "search_openalex.py",
        "--output-dir",
        RAW_DIR,
        "--max-results",
        args.max_results,
    )
    extract_command = script_command(
        "extract_openalex_candidates.py",
        "--input-dir",
        RAW_DIR,
        "--output-dir",
        PROCESSED_DIR,
    )

    working_papers = PAPERS_CSV if args.include_out_of_scope else IN_SCOPE_PAPERS_CSV
    working_affiliations = (
        ORIGINAL_AFFILIATIONS_CSV
        if args.include_out_of_scope
        else IN_SCOPE_AFFILIATIONS_CSV
    )

    resolution_command = script_command(
        "resolve_candidate_institutions.py",
        "--input",
        working_affiliations,
        "--output",
        RESOLVED_AFFILIATIONS_CSV,
        "--report",
        RESOLUTION_REPORT,
        "--cache",
        RESOLUTION_CACHE,
    )
    if args.include_out_of_scope:
        resolution_command.append("--include-out-of-scope")
    add_shared_network_arguments(resolution_command, args)

    latest_affiliations = (
        working_affiliations
        if args.skip_resolution
        else RESOLVED_AFFILIATIONS_CSV
    )
    geocoding_command = script_command(
        "geocode_candidate_affiliations.py",
        "--input",
        latest_affiliations,
        "--output",
        GEOCODED_AFFILIATIONS_CSV,
        "--cache",
        GEOCODING_CACHE,
    )
    if args.include_out_of_scope:
        geocoding_command.append("--include-out-of-scope")
    add_shared_network_arguments(geocoding_command, args)
    if not args.skip_geocoding:
        latest_affiliations = GEOCODED_AFFILIATIONS_CSV

    export_command = script_command(
        "export_candidate_map_data.py",
        "--papers-csv",
        working_papers,
        "--affiliations-csv",
        latest_affiliations,
        "--output",
        MAP_JSON,
    )
    if args.include_out_of_scope:
        export_command.append("--include-out-of-scope")
    review_command = script_command(
        "build_institution_review_queue.py",
        "--original",
        working_affiliations,
        "--geocoded",
        latest_affiliations,
        "--output",
        REVIEW_QUEUE,
    )
    if args.include_out_of_scope:
        review_command.append("--include-out-of-scope")

    return [
        PipelineStep(1, "Search OpenAlex candidates", search_command, not args.skip_search),
        PipelineStep(2, "Extract candidate CSVs", extract_command),
        PipelineStep(
            3,
            "Resolve institutions from authoritative metadata",
            resolution_command,
            not args.skip_resolution,
        ),
        PipelineStep(
            4,
            "Geocode unresolved institutions",
            geocoding_command,
            not args.skip_geocoding,
        ),
        PipelineStep(5, "Export map-ready JSON", export_command),
        PipelineStep(
            6,
            "Build institution review queue",
            review_command,
            not args.skip_review_queue,
        ),
    ]


def display_command(command: Sequence[str]) -> str:
    return shlex.join(command)


def execute_steps(steps: Sequence[PipelineStep], dry_run: bool) -> int:
    if dry_run:
        print("DRY RUN: no subprocesses will be executed and no files will be written.")

    for step in steps:
        prefix = f"[{step.number}/6]"
        if not step.enabled:
            print(f"{prefix} SKIP: {step.name}")
            continue

        print(
            f"{prefix} {'WOULD RUN' if dry_run else 'START'}: {step.name}",
            flush=not dry_run,
        )
        print(f"  {display_command(step.command)}", flush=not dry_run)
        if dry_run:
            continue

        try:
            result = subprocess.run(step.command, cwd=REPOSITORY_ROOT, check=False)
        except OSError as error:
            print(f"{prefix} ERROR: could not start step: {error}", file=sys.stderr)
            return 1
        if result.returncode != 0:
            print(
                f"{prefix} FAILED: {step.name} exited with code {result.returncode}. "
                "Pipeline stopped.",
                file=sys.stderr,
            )
            return result.returncode or 1
        print(f"{prefix} COMPLETE: {step.name}", flush=True)

    print("Pipeline dry-run complete." if dry_run else "Pipeline complete.")
    return 0


def run(args: argparse.Namespace) -> int:
    if (
        not args.dry_run
        and (not args.skip_resolution or not args.skip_geocoding)
        and not args.user_agent.strip()
    ):
        print(
            "Error: --user-agent is required when resolution or geocoding is enabled.",
            file=sys.stderr,
        )
        return 1
    return execute_steps(build_steps(args), args.dry_run)


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
