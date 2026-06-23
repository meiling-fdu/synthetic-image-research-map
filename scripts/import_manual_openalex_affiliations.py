#!/usr/bin/env python3
"""Import affiliations for manually approved OpenAlex works."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from extract_openalex_candidates import (
    AFFILIATION_COLUMNS,
    institution_geo,
    make_affiliation_row,
)
from openalex_utils import (
    OpenAlexFetchError,
    fetch_openalex_institution,
    fetch_openalex_work,
    normalize_openalex_id,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = (
    ROOT / "data/manual/key_papers_missing_top50_import_ready.csv",
    ROOT / "data/manual/key_papers_missing_next50_import_ready.csv",
    ROOT / "data/manual/key_papers_missing_batch2_import_ready.csv",
)
BASE_OUTPUTS = (
    ROOT / "data/processed/openalex_candidate_affiliations.csv",
    ROOT / "data/processed/openalex_candidate_affiliations_in_scope.csv",
)
RESOLVED_OUTPUTS = (
    ROOT / "data/processed/openalex_candidate_affiliations_resolved.csv",
    ROOT / "data/processed/openalex_candidate_affiliations_geocoded.csv",
)
RESOLUTION_COLUMNS = (
    "resolved_institution_name",
    "resolved_city",
    "resolved_country",
    "resolved_latitude",
    "resolved_longitude",
    "resolution_method",
    "resolution_confidence",
    "resolution_notes",
    "needs_review",
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
    parser.add_argument("--limit", type=int, help="Maximum ready papers to process.")
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


def clean(value: Any) -> str:
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


def affiliation_key(row: Dict[str, str]) -> Tuple[str, str, str]:
    return (
        normalize_openalex_id(row.get("openalex_id")),
        clean(row.get("author_order")),
        normalize_openalex_id(row.get("institution_openalex_id")),
    )


def resolved_row(
    base_row: Dict[str, str],
    institution: Dict[str, Any],
) -> Dict[str, str]:
    row = dict(base_row)
    geo = institution_geo(institution)
    latitude = clean(geo.get("latitude") or institution.get("latitude"))
    longitude = clean(geo.get("longitude") or institution.get("longitude"))
    has_coordinates = bool(latitude and longitude)
    row.update(
        {
            "resolved_institution_name": clean(
                institution.get("display_name") or base_row.get("institution_name")
            ),
            "resolved_city": clean(
                geo.get("city") or institution.get("city") or base_row.get("city")
            ),
            "resolved_country": clean(
                geo.get("country")
                or institution.get("country")
                or geo.get("country_code")
                or institution.get("country_code")
                or base_row.get("country")
                or base_row.get("country_code")
            ),
            "resolved_latitude": latitude,
            "resolved_longitude": longitude,
            "resolution_method": "openalex_institution_api",
            "resolution_confidence": "medium" if has_coordinates else "low",
            "resolution_notes": (
                "Institution metadata fetched from OpenAlex during manual import."
                if has_coordinates
                else "OpenAlex institution metadata has no complete coordinate pair."
            ),
            "needs_review": "false" if has_coordinates else "true",
        }
    )
    return row


def validate_schemas(
    data: Sequence[Tuple[Path, Tuple[List[str], List[Dict[str, str]]]]],
) -> None:
    expected_base = tuple(AFFILIATION_COLUMNS)
    expected_resolved = (*expected_base, *RESOLUTION_COLUMNS)
    for path, (header, _rows) in data:
        expected = expected_resolved if path in RESOLVED_OUTPUTS else expected_base
        if tuple(header) != tuple(expected):
            raise ImportWorkflowError(f"{path} schema does not match expected columns")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.limit is not None and args.limit < 0:
        print("Error: --limit must be non-negative.", file=sys.stderr)
        return 2

    try:
        paths = (*BASE_OUTPUTS, *RESOLVED_OUTPUTS)
        output_data = [(path, read_csv(path)) for path in paths]
        validate_schemas(output_data)
        ready_rows, skipped_video = read_ready_rows(input_paths(args.input))
        if args.limit is not None:
            ready_rows = ready_rows[: args.limit]

        additions: Dict[Path, List[Dict[str, str]]] = {path: [] for path in paths}
        known_keys = {
            path: {affiliation_key(row) for row in rows}
            for path, (_header, rows) in output_data
        }
        institution_cache: Dict[str, Dict[str, Any]] = {}
        papers_processed = 0
        coordinate_rows = 0
        coordinate_papers = set()
        skipped_duplicates = 0
        missing_institution_authorships = 0
        fetch_failures = 0
        eligible_requests = 0

        if args.dry_run:
            seen_work_ids = set()
            for source_row in ready_rows:
                work_id = normalize_openalex_id(source_row.get("openalex_url"))
                if not work_id or work_id in seen_work_ids:
                    skipped_duplicates += 1
                    continue
                seen_work_ids.add(work_id)
                eligible_requests += 1
            papers_processed = eligible_requests
        else:
            seen_work_ids = set()
            for source_row in ready_rows:
                work_id = normalize_openalex_id(source_row.get("openalex_url"))
                if not work_id or work_id in seen_work_ids:
                    skipped_duplicates += 1
                    continue
                seen_work_ids.add(work_id)
                eligible_requests += 1
                try:
                    work = fetch_openalex_work(work_id)
                except OpenAlexFetchError as error:
                    fetch_failures += 1
                    print(f"Fetch failed for {work_id}: {error}", file=sys.stderr)
                    continue
                if work.get("is_retracted"):
                    continue
                papers_processed += 1
                openalex_id = clean(work.get("id")) or f"https://openalex.org/{work_id}"
                authorships = work.get("authorships")
                if not isinstance(authorships, list):
                    authorships = []

                for author_order, authorship in enumerate(authorships, start=1):
                    if not isinstance(authorship, dict):
                        continue
                    embedded = authorship.get("institutions")
                    institutions = (
                        [item for item in embedded if isinstance(item, dict)]
                        if isinstance(embedded, list)
                        else []
                    )
                    if not institutions:
                        missing_institution_authorships += 1
                        institutions = [{}]

                    for embedded_institution in institutions:
                        institution = embedded_institution
                        institution_id = normalize_openalex_id(
                            embedded_institution.get("id")
                        )
                        if institution_id:
                            if institution_id not in institution_cache:
                                try:
                                    institution_cache[institution_id] = (
                                        fetch_openalex_institution(institution_id)
                                    )
                                except OpenAlexFetchError as error:
                                    fetch_failures += 1
                                    institution_cache[institution_id] = embedded_institution
                                    print(
                                        f"Institution fetch failed for {institution_id}: "
                                        f"{error}",
                                        file=sys.stderr,
                                    )
                            institution = institution_cache[institution_id]

                        base = make_affiliation_row(
                            openalex_id,
                            authorship,
                            institution or None,
                            author_order,
                        )
                        base["in_scope"] = "true"
                        resolved = resolved_row(base, institution)
                        if resolved["resolved_latitude"] and resolved["resolved_longitude"]:
                            coordinate_rows += 1
                            coordinate_papers.add(work_id)

                        key = affiliation_key(base)
                        for path in BASE_OUTPUTS:
                            if key in known_keys[path]:
                                skipped_duplicates += 1
                            else:
                                additions[path].append(base)
                                known_keys[path].add(key)
                        for path in RESOLVED_OUTPUTS:
                            if key in known_keys[path]:
                                skipped_duplicates += 1
                            else:
                                additions[path].append(resolved)
                                known_keys[path].add(key)

            for path, (header, rows) in output_data:
                write_csv_atomic(path, header, [*rows, *additions[path]])

        print("Manual OpenAlex affiliation import summary:")
        print(f"  Papers processed: {papers_processed}")
        print(
            "  Base affiliation rows added: "
            f"{sum(len(additions[path]) for path in BASE_OUTPUTS)}"
        )
        print(
            "  Resolved/geocoded rows added: "
            f"{sum(len(additions[path]) for path in RESOLVED_OUTPUTS)}"
        )
        print(f"  Rows with coordinates: {coordinate_rows}")
        print(
            "  Papers with coordinate-bearing institutions: "
            f"{len(coordinate_papers)}"
        )
        print(f"  Skipped duplicates: {skipped_duplicates}")
        print(
            "  Missing institution authorships: "
            f"{missing_institution_authorships}"
        )
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
