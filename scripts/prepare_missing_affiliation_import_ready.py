#!/usr/bin/env python3
"""Prepare missing-affiliation papers for manual OpenAlex affiliation import."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from openalex_utils import normalize_openalex_id


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/manual/paper_marker_blocker_report.csv"
DEFAULT_OUTPUT = ROOT / "data/manual/missing_affiliation_openalex_import_ready.csv"
DEFAULT_SKIPPED_OUTPUT = (
    ROOT / "data/manual/missing_affiliation_openalex_import_skipped.csv"
)
REFERENCE_PATHS = (
    ROOT / "data/processed/openalex_candidate_papers.csv",
    ROOT / "data/manual/paper_preview_without_map_location.csv",
    ROOT / "data/manual/key_papers_missing_next50_import_ready.csv",
    ROOT / "data/manual/key_papers_missing_batch3_import_ready.csv",
)
OUTPUT_COLUMNS = (
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
SKIPPED_COLUMNS = (
    "title",
    "year",
    "openalex_id",
    "openalex_url",
    "doi",
    "blocker_type",
    "reason",
)
REFERENCE_FIELDS = (
    "doi",
    "publication_venue",
    "publication_type",
    "primary_url",
    "preliminary_task",
    "preliminary_subtask",
)


class PreparationError(RuntimeError):
    """A local input or output error."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--skipped-output", default=str(DEFAULT_SKIPPED_OUTPUT))
    return parser.parse_args(argv)


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError as error:
        raise PreparationError(f"Could not read {path}: {error}") from error


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
        raise PreparationError(f"Could not write {path}: {error}") from error


def openalex_work_id(row: Dict[str, str]) -> str:
    return normalize_openalex_id(row.get("openalex_url")) or normalize_openalex_id(
        row.get("openalex_id")
    )


def reference_value(row: Dict[str, str], field: str) -> str:
    aliases = {
        "publication_venue": ("publication_venue", "venue", "venue_name"),
        "primary_url": ("primary_url", "url", "landing_page_url"),
        "preliminary_task": ("preliminary_task", "task"),
        "preliminary_subtask": ("preliminary_subtask", "subtask"),
    }
    for name in aliases.get(field, (field,)):
        value = clean(row.get(name))
        if value:
            return value
    return ""


def load_reference_rows() -> Dict[str, Dict[str, str]]:
    references: Dict[str, Dict[str, str]] = {}
    for path in REFERENCE_PATHS:
        if not path.exists():
            continue
        for row in read_csv(path):
            work_id = openalex_work_id(row)
            if not work_id:
                continue
            merged = references.setdefault(work_id, {})
            for field in REFERENCE_FIELDS:
                if not merged.get(field):
                    merged[field] = reference_value(row, field)
    return references


def infer_labels(title: str) -> Tuple[str, str]:
    normalized = " ".join(re.sub(r"[^\w]+", " ", title.casefold()).split())
    if re.search(r"\b(?:attribution|source identification)\b", normalized):
        return "source_attribution", "source_attribution"
    if re.search(r"\b(?:provenance|watermark)\b", normalized):
        return "image_provenance", "watermark_or_provenance"
    if re.search(r"\b(?:ct|medical|radiology)\b", normalized):
        return "detection", "medical_synthetic_image_detection"
    if re.search(r"\bdeepfake(?:s)?\b", normalized):
        return "detection", "deepfake_image_detection"
    if re.search(
        r"\b(?:generated|synthetic|fake|forgery|forensic|forensics)\b", normalized
    ):
        return "detection", "ai_generated_image_detection"
    return "uncertain", "unknown"


def is_generated_video(
    row: Dict[str, str],
    task: str,
    subtask: str,
) -> bool:
    if "generated_video_detection" in {task.casefold(), subtask.casefold()}:
        return True
    title = clean(row.get("title")).casefold()
    has_video = bool(re.search(r"\bvideos?\b", title))
    has_generated_context = bool(
        re.search(r"\b(?:generated|synthetic|deepfakes?)\b", title)
    )
    has_image = bool(re.search(r"\bimages?\b", title))
    return has_video and has_generated_context and not has_image


def skipped_row(row: Dict[str, str], reason: str) -> Dict[str, str]:
    return {
        "title": clean(row.get("title")),
        "year": clean(row.get("year")),
        "openalex_id": clean(row.get("openalex_id")),
        "openalex_url": clean(row.get("openalex_url")),
        "doi": clean(row.get("doi")),
        "blocker_type": clean(row.get("blocker_type")),
        "reason": reason,
    }


def prepare_rows(
    source_rows: Sequence[Dict[str, str]],
    references: Dict[str, Dict[str, str]],
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    ready: List[Dict[str, str]] = []
    skipped: List[Dict[str, str]] = []
    seen_work_ids = set()

    for row in source_rows:
        if clean(row.get("blocker_type")) != "missing_affiliation_rows":
            continue

        work_id = openalex_work_id(row)
        if not work_id:
            skipped.append(
                skipped_row(row, "Missing or invalid OpenAlex work ID/URL.")
            )
            continue
        if work_id in seen_work_ids:
            skipped.append(skipped_row(row, f"Duplicate OpenAlex work ID: {work_id}."))
            continue

        reference = references.get(work_id, {})
        task = clean(reference.get("preliminary_task"))
        subtask = clean(reference.get("preliminary_subtask"))
        if not task or not subtask:
            task, subtask = infer_labels(clean(row.get("title")))

        if is_generated_video(row, task, subtask):
            skipped.append(
                skipped_row(row, "Excluded generated_video_detection record.")
            )
            continue

        title = clean(row.get("title"))
        year = clean(row.get("year"))
        doi = clean(row.get("doi")) or clean(reference.get("doi"))
        primary_url = clean(reference.get("primary_url")) or doi
        ready.append(
            {
                "title": title,
                "year": year,
                "openalex_url": f"https://openalex.org/{work_id}",
                "doi": doi,
                "best_match_title": title,
                "best_match_year": year,
                "similarity": "1.000",
                "publication_venue": clean(reference.get("publication_venue")),
                "publication_type": clean(reference.get("publication_type")),
                "primary_url": primary_url,
                "preliminary_task": task,
                "preliminary_subtask": subtask,
                "import_status": "ready",
                "notes": (
                    "Prepared from missing_affiliation_rows blocker report using "
                    "the existing OpenAlex work ID; affiliation import only."
                ),
            }
        )
        seen_work_ids.add(work_id)

    return ready, skipped


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)
    skipped_output_path = resolve_path(args.skipped_output)

    try:
        source_rows = read_csv(input_path)
        ready, skipped = prepare_rows(source_rows, load_reference_rows())
        write_csv_atomic(output_path, OUTPUT_COLUMNS, ready)
        write_csv_atomic(skipped_output_path, SKIPPED_COLUMNS, skipped)
    except PreparationError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Rows selected: {len(ready)}")
    print(f"Rows skipped: {len(skipped)}")
    print(f"Output: {output_path}")
    print(f"Skipped output: {skipped_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
