#!/usr/bin/env python3
"""Audit and consolidate exact-equivalent confirmed institution locations."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

try:
    from .curated_locations import consolidate_exact_confirmed_locations
except ImportError:
    from curated_locations import consolidate_exact_confirmed_locations


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "data/processed/institution_location_resolution_audit.csv"
DEFAULT_DOC = ROOT / "docs/institution_location_resolution_audit.md"
COLUMNS = (
    "action", "institution_id", "institution", "source_location_id",
    "target_location_id", "city", "region", "country", "lat", "lon", "status",
)


def write_report(rows, report_path: Path, doc_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = report_path.with_suffix(report_path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(report_path)
    counts = Counter(row["status"] for row in rows)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join((
        "# Institution location resolution audit",
        "",
        "Only exact normalized institution ID, city, region, country, latitude, and longitude equivalence is consolidated. Distinct coordinates are retained.",
        "",
        f"- Exact duplicate locations merged: {counts['merged']}",
        f"- Exact duplicate locations awaiting write: {counts['would_merge']}",
        "",
        f"Machine-readable report: `{report_path.relative_to(ROOT)}`",
        "",
    ))
    temporary_doc = doc_path.with_suffix(doc_path.suffix + ".tmp")
    temporary_doc.write_text(text, encoding="utf-8")
    temporary_doc.replace(doc_path)


def run(*, write: bool, report_path: Path = DEFAULT_REPORT, doc_path: Path = DEFAULT_DOC):
    result = consolidate_exact_confirmed_locations(write=write)
    historical = []
    if write and report_path.exists():
        with report_path.open("r", encoding="utf-8-sig", newline="") as handle:
            historical = list(csv.DictReader(handle))
    combined = {}
    for finding in (*historical, *result["findings"]):
        key = (finding["source_location_id"], finding["target_location_id"])
        combined[key] = finding
    rows = [combined[key] for key in sorted(combined)]
    write_report(rows, report_path, doc_path)
    result["findings"] = rows
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    args = parser.parse_args()
    result = run(write=args.write, report_path=args.report, doc_path=args.doc)
    print(f"Institution location audit: {len(result['findings'])} finding(s).")


if __name__ == "__main__":
    main()
