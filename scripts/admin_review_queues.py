#!/usr/bin/env python3
"""Read generated diagnostics as non-authoritative admin review queues."""

from __future__ import annotations

import csv
import fnmatch
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
MANUAL_DIR = REPOSITORY_ROOT / "data" / "manual"
WEB_DATA_DIR = REPOSITORY_ROOT / "web" / "data"

QUEUE_PATHS = {
    "high_risk_marker": MANUAL_DIR / "high_risk_marker_review.csv",
    "marker_blocker": MANUAL_DIR / "paper_marker_blocker_report.csv",
    "key_paper_coverage": MANUAL_DIR / "key_paper_coverage_report.csv",
}
MANUAL_IMPORT_PATTERNS = (
    "key_papers_openalex_problem_review.csv",
    "key_papers_openalex_ready_all_batches.csv",
    "key_papers_*_import_ready.csv",
    "key_papers_*_manual_review.csv",
    "key_papers_*_openalex_matches.csv",
)


class AdminReviewQueueError(RuntimeError):
    """A generated queue could not be read."""


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def read_csv(path: Path) -> list[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except (OSError, UnicodeError, csv.Error) as error:
        raise AdminReviewQueueError(f"could not read {path}: {error}") from error


def read_json(path: Path) -> list[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AdminReviewQueueError(f"could not read {path}: {error}") from error
    if isinstance(payload, dict):
        payload = payload.get("records") or payload.get("papers") or []
    return [dict(row) for row in payload if isinstance(row, dict)]


def _summary(rows: Iterable[Mapping[str, Any]], field: str) -> Dict[str, int]:
    return dict(sorted(Counter(clean(row.get(field)) or "unknown" for row in rows).items()))


def load_queue(name: str) -> Dict[str, Any]:
    path = QUEUE_PATHS.get(name)
    if path is None:
        raise AdminReviewQueueError(f"unsupported review queue: {name}")
    rows = read_csv(path)
    group_field = {
        "high_risk_marker": "priority",
        "marker_blocker": "blocker_type",
        "key_paper_coverage": "missing_stage",
    }[name]
    return {
        "queue": name,
        "available": path.exists(),
        "source_file": str(path.relative_to(REPOSITORY_ROOT)),
        "count": len(rows),
        "summary": _summary(rows, group_field),
        "records": rows,
        "durable_source": False,
    }


def _manual_import_files() -> list[Path]:
    matches = {
        path
        for path in MANUAL_DIR.glob("*.csv")
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in MANUAL_IMPORT_PATTERNS)
    }
    return sorted(matches, key=lambda path: path.name)


def _candidate_status(row: Mapping[str, Any], filename: str) -> str:
    combined = " ".join(
        clean(row.get(field)).casefold()
        for field in ("import_status", "match_status", "status", "review_status")
    )
    if "query_failed" in combined or "query failed" in combined:
        return "query_failed"
    if "weak" in combined:
        return "weak_match"
    if "no_match" in combined or "no match" in combined:
        return "no_match"
    if "ready" in combined or "import_ready" in filename:
        return "ready"
    return "manual_review"


def load_manual_import_queue() -> Dict[str, Any]:
    records: list[Dict[str, Any]] = []
    files = _manual_import_files()
    for path in files:
        for index, source in enumerate(read_csv(path), start=2):
            row: Dict[str, Any] = dict(source)
            row["source_file"] = str(path.relative_to(REPOSITORY_ROOT))
            row["source_row"] = index
            row["candidate_status"] = _candidate_status(row, path.name)
            row.setdefault("candidate_title", row.get("best_match_title", ""))
            row.setdefault("candidate_year", row.get("best_match_year", ""))
            row.setdefault("venue", row.get("publication_venue", ""))
            records.append(row)
    return {
        "queue": "manual_import",
        "available": bool(files),
        "source_files": [str(path.relative_to(REPOSITORY_ROOT)) for path in files],
        "count": len(records),
        "summary": _summary(records, "candidate_status"),
        "records": records,
        "durable_source": False,
    }


def _count_csv(path: Path) -> int:
    return len(read_csv(path))


def dashboard_data(
    *,
    curated_counts: Mapping[str, int],
    validation_status: Mapping[str, Any],
    git_status: Mapping[str, Any],
) -> Dict[str, Any]:
    public_papers = read_json(WEB_DATA_DIR / "public_preview_papers.json")
    map_markers = read_json(WEB_DATA_DIR / "public_preview_map_data.json")
    queues = {
        "high_risk_marker": load_queue("high_risk_marker"),
        "marker_blocker": load_queue("marker_blocker"),
        "key_paper_coverage": load_queue("key_paper_coverage"),
        "manual_import": load_manual_import_queue(),
    }
    return {
        "counts": {
            "public_preview_papers": len(public_papers),
            "map_markers": len(map_markers),
            **dict(curated_counts),
        },
        "queues": {
            name: {
                "available": queue["available"],
                "count": queue["count"],
                "summary": queue["summary"],
            }
            for name, queue in queues.items()
        },
        "latest_validation_status": validation_status,
        "git_status": git_status,
    }
