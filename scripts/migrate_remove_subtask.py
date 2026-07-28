#!/usr/bin/env python3
"""Audit and permanently remove the retired paper subtask field.

The canonical ``task`` value is never derived or changed. The migration is
idempotent and verifies that every non-removed CSV value is preserved.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PAPERS = ROOT / "data" / "curated" / "papers.csv"
DEFAULT_AUDIT = ROOT / "docs" / "subtask_removal_audit.csv"
RETIRED_COLUMNS = {"subtask", "preliminary_subtask"}

DETECTION_VALUES = {
    "ai_generated_image_detection",
    "deepfake_image_detection",
    "synthetic_image_detection",
}
ATTRIBUTION_VALUES = {
    "generated_image_source_attribution",
    "source_identification",
    "source_verification",
}


def compatibility(task: str, old_value: str) -> str:
    task = task.strip().casefold()
    old_value = old_value.strip().casefold()
    if not old_value:
        return "empty"
    if task == "detection" and old_value in DETECTION_VALUES:
        return "consistent"
    if task == "source_attribution" and old_value in ATTRIBUTION_VALUES:
        return "consistent"
    if (
        task == "detection_and_source_attribution"
        and old_value == "detection_and_source_attribution"
    ):
        return "consistent"
    if task == "uncertain" or old_value == "unknown":
        return "uncertain"
    return "conflicting"


def audit_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    result = []
    for row in rows:
        old_value = row.get("subtask", "")
        if "subtask" not in row:
            continue
        result.append(
            {
                "paper_id": row.get("paper_id", ""),
                "title": row.get("title", ""),
                "task": row.get("task", ""),
                "old_subtask": old_value,
                "assessment": compatibility(row.get("task", ""), old_value),
            }
        )
    return result


def write_audit(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("paper_id", "title", "task", "old_subtask", "assessment"),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def migrate_csv(path: Path) -> tuple[int, list[dict[str, str]]]:
    original = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(original))
    fields = list(reader.fieldnames or ())
    rows = [dict(row) for row in reader]
    removed_fields = RETIRED_COLUMNS.intersection(fields)
    if not removed_fields:
        return 0, []

    audit = audit_rows(rows)
    new_fields = [field for field in fields if field not in removed_fields]
    expected = [
        {key: value for key, value in row.items() if key not in removed_fields}
        for row in rows
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=new_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(expected)
    reparsed = list(csv.DictReader(io.StringIO(output.getvalue())))
    if reparsed != expected:
        raise RuntimeError(f"non-subtask values changed while migrating {path}")
    path.write_text(output.getvalue(), encoding="utf-8")
    return len(rows), audit


def migrate_json(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    removed = 0

    def visit(value: object) -> None:
        nonlocal removed
        if isinstance(value, dict):
            for field in tuple(RETIRED_COLUMNS):
                if field in value:
                    value.pop(field)
                    removed += 1
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payload)
    if removed:
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return removed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument(
        "--all-data",
        action="store_true",
        help="also remove retired columns from curated, processed, and manual CSVs",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    removed, audit = migrate_csv(args.papers)
    migrated_files = int(bool(removed))
    if args.all_data:
        for directory in ("curated", "processed", "manual"):
            for path in sorted((ROOT / "data" / directory).glob("*.csv")):
                if path == args.papers:
                    continue
                file_rows, _ = migrate_csv(path)
                if file_rows:
                    migrated_files += 1
        for path in (
            ROOT / "web" / "data" / "public_preview_papers.json",
            ROOT / "web" / "data" / "public_preview_map_data.json",
        ):
            if migrate_json(path):
                migrated_files += 1
    write_audit(args.audit, audit)
    conflicts = sum(row["assessment"] == "conflicting" for row in audit)
    print(
        f"Removed subtask from {removed} records; "
        f"audited {len(audit)} records with {conflicts} meaningful conflicts; "
        f"migrated {migrated_files} CSV files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
