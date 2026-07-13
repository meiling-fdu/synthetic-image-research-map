#!/usr/bin/env python3
"""Generate the review-only institution consistency audit report."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

try:
    from .institution_consistency import DEFAULT_REPORT_PATH, REPORT_COLUMNS, run_repository_audit, unresolved_high
except ImportError:
    from institution_consistency import DEFAULT_REPORT_PATH, REPORT_COLUMNS, run_repository_audit, unresolved_high


def write_report(path: Path, rows) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_COLUMNS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--check", action="store_true", help="Exit nonzero when unresolved high-severity findings exist.")
    args = parser.parse_args(argv)
    findings = run_repository_audit()
    write_report(args.output, findings)
    severities = Counter(row["severity"] for row in findings if row["resolution_status"] == "unresolved")
    print(f"Institution consistency findings: {len(findings)}")
    print(f"Unresolved high / medium / low: {severities['high']} / {severities['medium']} / {severities['low']}")
    print(f"Report: {args.output}")
    return 1 if args.check and unresolved_high(findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
