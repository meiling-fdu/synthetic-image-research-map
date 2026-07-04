#!/usr/bin/env python3
"""Read generated diagnostics as non-authoritative admin review queues."""

from __future__ import annotations

import csv
import fnmatch
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence


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


def project_health_severity(
    key: str, value: float | int | None, *, available: bool = True
) -> str:
    """Classify a health metric using stable, maintainer-facing thresholds."""
    if not available or value is None:
        return "neutral"
    numeric = float(value)
    if key == "author_mapping_coverage":
        return (
            "good"
            if numeric >= 95
            else "warning"
            if numeric >= 90
            else "critical"
        )
    thresholds = {
        "missing_author_mappings": (10, 0),
        "missing_author_links": (50, 0),
        "missing_coordinates": (5, 0),
        "missing_affiliations": (20, 0),
    }
    if key in thresholds:
        warning_max, good_max = thresholds[key]
        return (
            "good"
            if numeric <= good_max
            else "warning"
            if numeric <= warning_max
            else "critical"
        )
    if key in {
        "high_risk_markers",
        "marker_blockers",
        "key_paper_coverage_queue",
        "manual_import_queue",
    }:
        return (
            "good"
            if numeric == 0
            else "warning"
            if numeric <= 100
            else "critical"
        )
    if key == "partial_author_mappings":
        return "good" if numeric == 0 else "warning"
    if key == "pending_locations":
        return "good" if numeric == 0 else "warning" if numeric <= 100 else "critical"
    return "neutral"


def overall_project_health(
    *,
    counts: Mapping[str, int],
    queues: Mapping[str, Mapping[str, Any]],
    author_mapping_coverage: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return a bounded heuristic maintenance score and its deductions."""
    required_queues = ("high_risk_marker", "marker_blocker")
    if not author_mapping_coverage.get("available") or any(
        not queues[name].get("available") for name in required_queues
    ):
        return {
            "available": False,
            "score": None,
            "display_value": "Needs refresh",
            "level": "Unavailable",
            "severity": "neutral",
            "note": "Heuristic maintenance score; not a paper-quality rating.",
            "explanation": (
                "Heuristic maintenance score; refresh missing reports. "
                "It is not a paper-quality rating."
            ),
            "deductions": {},
        }

    summary = author_mapping_coverage.get("summary") or {}
    coverage = max(
        0.0,
        min(100.0, float(summary.get("mapping_coverage_percentage", 0))),
    )
    high_risk_backlog = int(queues["high_risk_marker"].get("count", 0))
    blocker_backlog = int(queues["marker_blocker"].get("count", 0))
    deductions = {
        "author_mapping_coverage": min(25.0, (100.0 - coverage) * 0.25),
        "missing_coordinates": min(
            15.0, float(counts.get("papers_missing_coordinates", 0)) * 0.5
        ),
        "missing_affiliations": min(
            15.0, float(counts.get("papers_missing_affiliations", 0)) * 0.1
        ),
        "review_backlog": min(
            20.0, float(high_risk_backlog + blocker_backlog) / 150.0
        ),
        "missing_author_links": min(
            15.0, float(summary.get("total_missing_author_links", 0)) / 50.0
        ),
    }
    score = max(0, min(100, round(100.0 - sum(deductions.values()))))
    level = (
        "Excellent"
        if score >= 90
        else "Needs attention"
        if score >= 75
        else "Critical maintenance"
    )
    severity = "good" if score >= 90 else "warning" if score >= 75 else "critical"
    return {
        "available": True,
        "score": score,
        "display_value": f"{score} / 100",
        "level": level,
        "severity": severity,
        "note": "Heuristic maintenance score; not a paper-quality rating.",
        "explanation": (
            "Starts at 100. Deductions: 0.25 per uncovered author-mapping "
            "percentage point (max 25), 0.5 per missing coordinate (max 15), "
            "0.1 per missing affiliation (max 15), one per 150 combined "
            "high-risk and blocker rows (max 20), and one per 50 missing "
            "author links (max 15). This is not a paper-quality rating."
        ),
        "deductions": {
            key: round(value, 2) for key, value in deductions.items()
        },
    }


def compact_queue_breakdown(summary: Mapping[str, Any]) -> Dict[str, str]:
    """Format existing queue summary counts without recomputing the queue."""
    ordered = sorted(
        ((clean(key), int(value)) for key, value in summary.items()),
        key=lambda item: (-item[1], item[0]),
    )
    return {
        "compact": " · ".join(f"{key}: {value}" for key, value in ordered[:3]),
        "full": " · ".join(f"{key}: {value}" for key, value in ordered),
    }


def project_health_data(
    *,
    counts: Mapping[str, int],
    queues: Mapping[str, Mapping[str, Any]],
    author_mapping_coverage: Mapping[str, Any],
) -> Dict[str, Any]:
    """Arrange existing dashboard/report totals into UI-ready health groups."""

    def metric(
        key: str,
        label: str,
        value: Any,
        *,
        target: str = "",
        source_available: bool = True,
        suffix: str = "",
        navigation: Mapping[str, str] | None = None,
        detail: str = "",
        full_detail: str = "",
    ) -> Dict[str, Any]:
        return {
            "key": key,
            "label": label,
            "value": value if source_available else None,
            "display_value": (
                f"{value}{suffix}" if source_available else "Report missing"
            ),
            "available": source_available,
            "target": target,
            "navigation": dict(navigation or {}),
            "severity": project_health_severity(
                key, value, available=source_available
            ),
            "detail": detail,
            "full_detail": full_detail or detail,
        }

    def group(
        key: str, label: str, metrics: Sequence[Mapping[str, Any]]
    ) -> Dict[str, Any]:
        return {"key": key, "label": label, "metrics": list(metrics)}

    mapping_available = bool(author_mapping_coverage.get("available"))
    mapping_summary = author_mapping_coverage.get("summary") or {}
    queue_available = {
        name: bool(queue.get("available")) for name, queue in queues.items()
    }
    queue_breakdowns = {
        name: compact_queue_breakdown(queue.get("summary") or {})
        for name, queue in queues.items()
    }

    groups = [
        group(
            "corpus",
            "Corpus",
            [
                metric("total_papers", "Total papers", counts.get("total_papers", 0)),
                metric(
                    "public_preview_papers",
                    "Public preview papers",
                    counts.get("public_preview_papers", 0),
                ),
                metric("map_markers", "Map markers", counts.get("map_markers", 0)),
                metric(
                    "missing_affiliations",
                    "Missing affiliations",
                    counts.get("papers_missing_affiliations", 0),
                ),
                metric(
                    "missing_coordinates",
                    "Missing coordinates",
                    counts.get("papers_missing_coordinates", 0),
                    target="location-review",
                    navigation={"location_status": "needs_coordinates"},
                ),
            ],
        ),
        group(
            "author_mapping",
            "Author Mapping",
            [
                metric(
                    "author_mapping_coverage",
                    "Author Mapping Coverage",
                    mapping_summary.get("mapping_coverage_percentage", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    suffix="%",
                    navigation={"mapping_status": "", "mapping_sort": "rank-asc"},
                ),
                metric(
                    "complete_author_mappings",
                    "Complete author mappings",
                    mapping_summary.get("complete_mappings", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    navigation={
                        "mapping_status": "complete",
                        "mapping_sort": "rank-asc",
                    },
                ),
                metric(
                    "partial_author_mappings",
                    "Partial author mappings",
                    mapping_summary.get("partial_mappings", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    navigation={
                        "mapping_status": "partial",
                        "mapping_sort": "rank-asc",
                    },
                ),
                metric(
                    "missing_author_mappings",
                    "Missing author mappings",
                    mapping_summary.get("zero_mappings", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    navigation={
                        "mapping_status": "zero",
                        "mapping_sort": "rank-asc",
                    },
                ),
                metric(
                    "missing_author_links",
                    "Missing author links",
                    mapping_summary.get("total_missing_author_links", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    navigation={
                        "mapping_status": "",
                        "mapping_sort": "missing-desc",
                    },
                ),
            ],
        ),
        group(
            "institution_location",
            "Institution / Location",
            [
                metric(
                    "pending_locations",
                    "Pending locations",
                    counts.get("pending_location_reviews", 0),
                    target="location-review",
                    navigation={"location_status": "pending_review"},
                ),
                metric(
                    "confirmed_locations",
                    "Confirmed locations",
                    counts.get("confirmed_institution_locations", 0),
                    target="location-review",
                ),
            ],
        ),
        group(
            "review_queues",
            "Review Queues",
            [
                metric(
                    "high_risk_markers",
                    "High-risk markers",
                    queues["high_risk_marker"].get("count", 0),
                    target="high-risk",
                    source_available=queue_available["high_risk_marker"],
                    suffix=" total",
                    detail=queue_breakdowns["high_risk_marker"]["compact"],
                    full_detail=queue_breakdowns["high_risk_marker"]["full"],
                ),
                metric(
                    "marker_blockers",
                    "Marker blockers",
                    queues["marker_blocker"].get("count", 0),
                    target="marker-blockers",
                    source_available=queue_available["marker_blocker"],
                    suffix=" total",
                    detail=queue_breakdowns["marker_blocker"]["compact"],
                    full_detail=queue_breakdowns["marker_blocker"]["full"],
                ),
                metric(
                    "key_paper_coverage_queue",
                    "Key paper coverage queue",
                    queues["key_paper_coverage"].get("count", 0),
                    target="key-coverage",
                    source_available=queue_available["key_paper_coverage"],
                    suffix=" total",
                    detail=queue_breakdowns["key_paper_coverage"]["compact"],
                    full_detail=queue_breakdowns["key_paper_coverage"]["full"],
                ),
                metric(
                    "manual_import_queue",
                    "Manual import queue",
                    queues["manual_import"].get("count", 0),
                    target="manual-import",
                    source_available=queue_available["manual_import"],
                    suffix=" total",
                    detail=queue_breakdowns["manual_import"]["compact"],
                    full_detail=queue_breakdowns["manual_import"]["full"],
                ),
            ],
        ),
        group(
            "publication_exclusions",
            "Publication / Exclusions",
            [
                metric(
                    "curated_papers",
                    "Curated papers",
                    counts.get("curated_papers", 0),
                ),
                metric(
                    "active_exclusions",
                    "Active exclusions",
                    counts.get("active_exclusions", 0),
                ),
            ],
        ),
    ]
    return {
        "overall": overall_project_health(
            counts=counts,
            queues=queues,
            author_mapping_coverage=author_mapping_coverage,
        ),
        "groups": groups,
    }


def dashboard_data(
    *,
    curated_counts: Mapping[str, int],
    validation_status: Mapping[str, Any],
    git_status: Mapping[str, Any],
    author_mapping_coverage: Mapping[str, Any],
) -> Dict[str, Any]:
    public_papers = read_json(WEB_DATA_DIR / "public_preview_papers.json")
    map_markers = read_json(WEB_DATA_DIR / "public_preview_map_data.json")
    queues = {
        "high_risk_marker": load_queue("high_risk_marker"),
        "marker_blocker": load_queue("marker_blocker"),
        "key_paper_coverage": load_queue("key_paper_coverage"),
        "manual_import": load_manual_import_queue(),
    }
    counts = {
        "public_preview_papers": len(public_papers),
        "map_markers": len(map_markers),
        **dict(curated_counts),
    }
    queue_summaries = {
        name: {
            "available": queue["available"],
            "count": queue["count"],
            "summary": queue["summary"],
        }
        for name, queue in queues.items()
    }
    return {
        "counts": counts,
        "queues": {
            name: dict(summary) for name, summary in queue_summaries.items()
        },
        "author_mapping_coverage": dict(author_mapping_coverage),
        "project_health": project_health_data(
            counts=counts,
            queues=queue_summaries,
            author_mapping_coverage=author_mapping_coverage,
        ),
        "latest_validation_status": validation_status,
        "git_status": git_status,
    }
