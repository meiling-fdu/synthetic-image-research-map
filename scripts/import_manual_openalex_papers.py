#!/usr/bin/env python3
"""Import manually approved OpenAlex works into processed candidate CSVs."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from extract_openalex_candidates import PAPER_COLUMNS, make_paper_row
from openalex_utils import (
    OpenAlexFetchError,
    fetch_openalex_work,
    normalize_openalex_id,
    normalize_title,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = (
    ROOT / "data/manual/key_papers_missing_top50_import_ready.csv",
    ROOT / "data/manual/key_papers_missing_next50_import_ready.csv",
    ROOT / "data/manual/key_papers_missing_batch2_import_ready.csv",
)
OUTPUTS = (
    ROOT / "data/processed/openalex_candidate_papers.csv",
    ROOT / "data/processed/openalex_candidate_papers_in_scope.csv",
)


class ImportWorkflowError(RuntimeError):
    """A local input or output error."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        help="Import-ready CSV; repeat or pass comma-separated paths.",
    )
    parser.add_argument("--limit", type=int, help="Maximum ready rows to process.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and summarize locally without network requests or writes.",
    )
    return parser.parse_args(argv)


def input_paths(values: Sequence[str]) -> List[Path]:
    if not values:
        return list(DEFAULT_INPUTS)
    paths = []
    for value in values:
        paths.extend(ROOT / item.strip() for item in value.split(",") if item.strip())
    return paths


def clean(value: object) -> str:
    return str(value or "").strip()


def is_video(row: Dict[str, str]) -> bool:
    return "generated_video_detection" in {
        clean(row.get("preliminary_task")).casefold(),
        clean(row.get("preliminary_subtask")).casefold(),
    }


def read_ready_rows(paths: Sequence[Path]) -> Tuple[List[Dict[str, str]], int]:
    ready = []
    skipped_video = 0
    for path in paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if clean(row.get("import_status")).casefold() != "ready":
                    continue
                if is_video(row):
                    skipped_video += 1
                    continue
                ready.append(dict(row))
    return ready, skipped_video


def read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), [dict(row) for row in reader]
    except OSError as error:
        raise ImportWorkflowError(f"Could not read {path}: {error}") from error


def write_csv_atomic(
    path: Path,
    fieldnames: Sequence[str],
    rows: Iterable[Dict[str, str]],
) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise ImportWorkflowError(f"Could not write {path}: {error}") from error


def existing_keys(rows: Sequence[Dict[str, str]]) -> Tuple[set[str], set[str]]:
    ids = {
        normalize_openalex_id(row.get("openalex_id") or row.get("openalex_url"))
        for row in rows
    }
    titles = {normalize_title(row.get("title")) for row in rows}
    ids.discard("")
    titles.discard("")
    return ids, titles


def manual_source_labels(row: Dict[str, str], paper: Dict[str, str]) -> None:
    task = clean(row.get("preliminary_task"))
    subtask = clean(row.get("preliminary_subtask"))
    if task:
        paper["preliminary_task"] = task
    if subtask:
        paper["preliminary_subtask"] = subtask
    paper["in_scope"] = "true"
    paper["relevance_score"] = "2"
    paper["relevance_reason"] = "Manually approved key-paper OpenAlex import."
    paper["exclusion_reason"] = ""
    paper["source_query"] = "manual_key_paper_import"
    paper["manual_review"] = "true"
    manual_notes = clean(row.get("notes"))
    paper["notes"] = " ".join(
        part
        for part in (
            paper.get("notes", ""),
            "Imported from a manual import-ready CSV.",
            manual_notes,
        )
        if part
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.limit is not None and args.limit < 0:
        print("Error: --limit must be non-negative.", file=sys.stderr)
        return 2
    try:
        output_data = [read_csv(path) for path in OUTPUTS]
        for path, (header, _rows) in zip(OUTPUTS, output_data):
            if tuple(header) != tuple(PAPER_COLUMNS):
                raise ImportWorkflowError(
                    f"{path} schema does not match PAPER_COLUMNS"
                )

        ready_rows, skipped_video = read_ready_rows(input_paths(args.input))
        if args.limit is not None:
            ready_rows = ready_rows[: args.limit]
        existing_ids, existing_titles = existing_keys(
            [row for _header, rows in output_data for row in rows]
        )

        added = []
        skipped_duplicates = 0
        skipped_retracted = 0
        fetch_failures = 0
        eligible_requests = 0
        if args.dry_run:
            planned_ids = set(existing_ids)
            planned_titles = set(existing_titles)
            for source_row in ready_rows:
                requested_id = normalize_openalex_id(source_row.get("openalex_url"))
                requested_title = normalize_title(
                    source_row.get("best_match_title") or source_row.get("title")
                )
                if requested_id in planned_ids or requested_title in planned_titles:
                    skipped_duplicates += 1
                    continue
                eligible_requests += 1
                if requested_id:
                    planned_ids.add(requested_id)
                if requested_title:
                    planned_titles.add(requested_title)
        else:
            for source_row in ready_rows:
                requested_id = normalize_openalex_id(source_row.get("openalex_url"))
                requested_title = normalize_title(
                    source_row.get("best_match_title") or source_row.get("title")
                )
                if requested_id in existing_ids or requested_title in existing_titles:
                    skipped_duplicates += 1
                    continue
                eligible_requests += 1
                try:
                    work = fetch_openalex_work(requested_id)
                except OpenAlexFetchError as error:
                    fetch_failures += 1
                    print(f"Fetch failed for {requested_id}: {error}", file=sys.stderr)
                    continue
                if work.get("is_retracted"):
                    skipped_retracted += 1
                    continue
                paper = make_paper_row(work, "manual_key_paper_import")
                work_id = normalize_openalex_id(paper.get("openalex_id"))
                work_title = normalize_title(paper.get("title"))
                if work_id in existing_ids or work_title in existing_titles:
                    skipped_duplicates += 1
                    continue
                manual_source_labels(source_row, paper)
                added.append(paper)
                existing_ids.add(work_id)
                existing_titles.add(work_title)

            for path, (header, rows) in zip(OUTPUTS, output_data):
                write_csv_atomic(path, header, [*rows, *added])

        print("Manual OpenAlex paper import summary:")
        print(f"  Ready rows read: {len(ready_rows)}")
        print(f"  Added papers: {len(added)}")
        print(f"  Skipped duplicates: {skipped_duplicates}")
        print(f"  Skipped retracted: {skipped_retracted}")
        print(f"  Skipped generated_video_detection: {skipped_video}")
        print(f"  Fetch failures: {fetch_failures}")
        print(f"  Eligible OpenAlex work requests: {eligible_requests}")
        if args.dry_run:
            print("  Dry run: no network requests were made and no files were written.")
        return 0
    except ImportWorkflowError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
