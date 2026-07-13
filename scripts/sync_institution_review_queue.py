#!/usr/bin/env python3
"""Import generated institution audit findings into the persistent Admin queue."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .institution_consistency import DEFAULT_REPORT_PATH, read_audit_report
    from .institution_review_queue import DEFAULT_QUEUE_PATH, sync_findings, unresolved
except ImportError:
    from institution_consistency import DEFAULT_REPORT_PATH, read_audit_report
    from institution_review_queue import DEFAULT_QUEUE_PATH, sync_findings, unresolved


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE_PATH)
    args = parser.parse_args(argv)
    result = sync_findings(read_audit_report(args.report), path=args.queue)
    open_rows = unresolved(result["rows"])
    high = sum(row.get("severity") == "high" for row in open_rows)
    print(
        f"Institution cleanup queue: {len(open_rows)} open "
        f"({high} high); {result['created']} added, "
        f"{result['resolved_by_reaudit']} resolved by re-audit."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
