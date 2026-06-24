#!/usr/bin/env python3
"""Consolidate OpenAlex matching artifacts and align them with key-paper gaps."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from openalex_utils import normalize_openalex_id, normalize_title


ROOT = Path(__file__).resolve().parents[1]
MANUAL_DIR = ROOT / "data/manual"
DEFAULT_COVERAGE = MANUAL_DIR / "key_paper_coverage_report.csv"
DEFAULT_PROBLEMS = MANUAL_DIR / "key_papers_openalex_problem_review.csv"
DEFAULT_READY = MANUAL_DIR / "key_papers_openalex_ready_all_batches.csv"
DEFAULT_UNCOVERED = (
    MANUAL_DIR / "key_papers_missing_uncovered_by_batch_artifacts.csv"
)
PROBLEM_STATUSES = {
    "query_failed",
    "weak_match",
    "review",
    "review_high",
    "no_match",
    "excluded_retracted",
}
PROBLEM_COLUMNS = (
    "batch",
    "title",
    "year",
    "match_status",
    "best_match_title",
    "best_match_year",
    "similarity",
    "openalex_url",
    "doi",
    "publication_venue",
    "publication_type",
    "notes",
    "review_decision",
    "review_notes",
)
READY_COLUMNS = (
    "batch",
    "title",
    "year",
    "openalex_url",
    "doi",
    "best_match_title",
    "best_match_year",
    "similarity",
    "publication_venue",
    "publication_type",
    "primary_url",
    "preliminary_task",
    "preliminary_subtask",
    "import_status",
    "notes",
)
PROBLEM_PREFERENCE = {
    "review_high": 6,
    "review": 5,
    "weak_match": 4,
    "excluded_retracted": 3,
    "no_match": 2,
    "query_failed": 1,
}


class ConsolidationError(RuntimeError):
    """A local input or output error."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage-report", default=str(DEFAULT_COVERAGE))
    parser.add_argument("--problem-output", default=str(DEFAULT_PROBLEMS))
    parser.add_argument("--ready-output", default=str(DEFAULT_READY))
    parser.add_argument("--uncovered-output", default=str(DEFAULT_UNCOVERED))
    parser.add_argument(
        "--write-empty-uncovered",
        action="store_true",
        help="Replace the uncovered report even when no rows remain.",
    )
    return parser.parse_args(argv)


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), [dict(row) for row in reader]
    except OSError as error:
        raise ConsolidationError(f"Could not read {path}: {error}") from error


def write_csv_atomic(
    path: Path,
    fieldnames: Sequence[str],
    rows: Iterable[Dict[str, str]],
) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=fieldnames, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise ConsolidationError(f"Could not write {path}: {error}") from error


def title_year_key(row: Dict[str, str]) -> Tuple[str, str]:
    return normalize_title(row.get("title")), clean(row.get("year"))


def batch_name(path: Path, suffix: str) -> str:
    stem = path.name.removeprefix("key_papers_missing_").removesuffix(suffix)
    return stem


def canonical_openalex_url(value: object) -> str:
    work_id = normalize_openalex_id(value)
    return f"https://openalex.org/{work_id}" if work_id else clean(value)


def existing_review_fields(path: Path) -> Dict[Tuple[str, str], Dict[str, str]]:
    if not path.exists():
        return {}
    _header, rows = read_csv(path)
    return {
        title_year_key(row): {
            "review_decision": clean(row.get("review_decision")),
            "review_notes": clean(row.get("review_notes")),
        }
        for row in rows
        if clean(row.get("review_decision")) or clean(row.get("review_notes"))
    }


def consolidate_problems(output_path: Path) -> List[Dict[str, str]]:
    saved_reviews = existing_review_fields(output_path)
    selected: Dict[Tuple[str, str], Dict[str, str]] = {}
    for path in sorted(MANUAL_DIR.glob("key_papers_missing_*_openalex_matches.csv")):
        _header, rows = read_csv(path)
        batch = batch_name(path, "_openalex_matches.csv")
        for source in rows:
            status = clean(
                source.get("match_status") or source.get("is_accepted_match")
            ).casefold()
            if status not in PROBLEM_STATUSES:
                continue
            row = {column: clean(source.get(column)) for column in PROBLEM_COLUMNS}
            row["batch"] = batch
            row["match_status"] = status
            row["openalex_url"] = canonical_openalex_url(
                source.get("openalex_url") or source.get("openalex_id")
            )
            row.update(saved_reviews.get(title_year_key(source), {}))
            key = title_year_key(source)
            current = selected.get(key)
            if current is None or PROBLEM_PREFERENCE[status] > PROBLEM_PREFERENCE[
                current["match_status"]
            ]:
                selected[key] = row

    return sorted(
        selected.values(),
        key=lambda row: (
            -int(row["year"]) if row["year"].isdigit() else 0,
            normalize_title(row["title"]),
        ),
    )


def ready_key(row: Dict[str, str]) -> Tuple[str, str]:
    return (
        canonical_openalex_url(row.get("openalex_url")).casefold(),
        normalize_title(row.get("title")),
    )


def consolidate_ready() -> List[Dict[str, str]]:
    selected: Dict[Tuple[str, str], Dict[str, str]] = {}
    for path in sorted(MANUAL_DIR.glob("key_papers_missing_*_import_ready.csv")):
        _header, rows = read_csv(path)
        batch = batch_name(path, "_import_ready.csv")
        for source in rows:
            if clean(source.get("import_status")).casefold() != "ready":
                continue
            row = {column: clean(source.get(column)) for column in READY_COLUMNS}
            row["batch"] = batch
            row["openalex_url"] = canonical_openalex_url(source.get("openalex_url"))
            key = ready_key(row)
            if key not in selected:
                selected[key] = row

    return sorted(
        selected.values(),
        key=lambda row: (
            -int(row["year"]) if row["year"].isdigit() else 0,
            normalize_title(row["title"]),
        ),
    )


def alignment_counts(
    coverage_rows: Sequence[Dict[str, str]],
    problem_rows: Sequence[Dict[str, str]],
    ready_rows: Sequence[Dict[str, str]],
) -> Tuple[Dict[str, int], List[Dict[str, str]]]:
    missing = [
        row
        for row in coverage_rows
        if clean(row.get("missing_stage")) == "missing_from_candidate_pool"
    ]
    problem_keys = {title_year_key(row) for row in problem_rows}
    ready_keys = {title_year_key(row) for row in ready_rows}
    covered_problem = sum(title_year_key(row) in problem_keys for row in missing)
    covered_ready = sum(title_year_key(row) in ready_keys for row in missing)
    uncovered = [
        row
        for row in missing
        if title_year_key(row) not in problem_keys
        and title_year_key(row) not in ready_keys
    ]
    return (
        {
            "missing_from_candidate_pool": len(missing),
            "covered_by_problem_review": covered_problem,
            "covered_by_ready_all_batches": covered_ready,
            "still_not_covered": len(uncovered),
        },
        uncovered,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    coverage_path = resolve_path(args.coverage_report)
    problem_path = resolve_path(args.problem_output)
    ready_path = resolve_path(args.ready_output)
    uncovered_path = resolve_path(args.uncovered_output)

    try:
        coverage_header, coverage_rows = read_csv(coverage_path)
        problem_rows = consolidate_problems(problem_path)
        ready_rows = consolidate_ready()
        counts, uncovered_rows = alignment_counts(
            coverage_rows, problem_rows, ready_rows
        )
        write_csv_atomic(problem_path, PROBLEM_COLUMNS, problem_rows)
        write_csv_atomic(ready_path, READY_COLUMNS, ready_rows)
        uncovered_written = bool(uncovered_rows) or args.write_empty_uncovered
        if uncovered_written:
            write_csv_atomic(uncovered_path, coverage_header, uncovered_rows)
    except ConsolidationError as error:
        print(f"Error: {error}")
        return 1

    print(f"Problem review rows: {len(problem_rows)}")
    print(
        "Problem status counts:",
        dict(sorted(Counter(row["match_status"] for row in problem_rows).items())),
    )
    print(f"Ready rows: {len(ready_rows)}")
    print(
        "Ready import status counts:",
        dict(sorted(Counter(row["import_status"] for row in ready_rows).items())),
    )
    for label, count in counts.items():
        print(f"{label}: {count}")
    if uncovered_written:
        print(f"Uncovered report written: {uncovered_path}")
    else:
        print(
            "Uncovered report preserved because the regenerated result is empty: "
            f"{uncovered_path}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
