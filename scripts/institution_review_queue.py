#!/usr/bin/env python3
"""Persistent Admin review state for generated institution audit findings."""

from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from .curated_schema import INSTITUTION_REVIEW_QUEUE_COLUMNS
except ImportError:
    from curated_schema import INSTITUTION_REVIEW_QUEUE_COLUMNS


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_PATH = REPOSITORY_ROOT / "data/curated/institution_review_queue.csv"
OPEN_STATUS = "open"
RESOLVED_STATUSES = {
    "accepted",
    "ignored",
    "manually_resolved",
    "resolved_by_reaudit",
}
ALLOWED_STATUSES = {OPEN_STATUS, *RESOLVED_STATUSES}
ALLOWED_SEVERITIES = {"high", "medium", "low"}


class InstitutionReviewQueueError(RuntimeError):
    """The institution cleanup queue or requested action is invalid."""


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _bool(value: Any) -> bool:
    return clean(value).casefold() in {"1", "true", "yes", "y"}


def _queue_id(audit_id: str) -> str:
    digest = hashlib.sha256(audit_id.encode("utf-8")).hexdigest()[:20]
    return f"institution-review:{digest}"


def load_queue(path: Path = DEFAULT_QUEUE_PATH) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != INSTITUTION_REVIEW_QUEUE_COLUMNS:
            raise InstitutionReviewQueueError(
                f"unexpected institution review queue header in {path}"
            )
        rows = [dict(row) for row in reader]
    seen: set[str] = set()
    for row in rows:
        queue_id = clean(row.get("queue_id"))
        if not queue_id or queue_id in seen:
            raise InstitutionReviewQueueError("queue_id must be present and unique")
        seen.add(queue_id)
        if clean(row.get("finding_status")) not in ALLOWED_STATUSES:
            raise InstitutionReviewQueueError(f"invalid finding status for {queue_id}")
    return rows


def save_queue(rows: Iterable[Mapping[str, Any]], path: Path = DEFAULT_QUEUE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=INSTITUTION_REVIEW_QUEUE_COLUMNS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def sync_findings(
    findings: Sequence[Mapping[str, Any]],
    *,
    path: Path = DEFAULT_QUEUE_PATH,
    now: str | None = None,
) -> dict[str, Any]:
    """Upsert report findings without overwriting any human resolution."""
    rows = load_queue(path)
    by_audit = {clean(row.get("audit_id")): row for row in rows}
    current_ids: set[str] = set()
    created = 0
    refreshed = 0
    resolved_by_reaudit = 0
    at = now or timestamp()
    evidence_fields = (
        "mapping_id", "paper_id", "paper_title", "year", "doi",
        "openalex_url", "author", "current_institution",
        "current_institution_id", "raw_affiliation",
        "suggested_canonical_institution", "suggested_institution_id",
        "severity", "issue_type", "reason", "recommended_action",
    )
    for finding in findings:
        audit_id = clean(finding.get("audit_id"))
        if not audit_id:
            raise InstitutionReviewQueueError("audit finding is missing audit_id")
        severity = clean(finding.get("severity"))
        if severity not in ALLOWED_SEVERITIES:
            raise InstitutionReviewQueueError(f"invalid severity for {audit_id}")
        current_ids.add(audit_id)
        row = by_audit.get(audit_id)
        if row is None:
            row = {column: "" for column in INSTITUTION_REVIEW_QUEUE_COLUMNS}
            row.update({
                "queue_id": _queue_id(audit_id),
                "audit_id": audit_id,
                "finding_status": (
                    "manually_resolved"
                    if clean(finding.get("resolution_status")) == "resolved"
                    else OPEN_STATUS
                ),
                "resolution_action": (
                    "legacy_review_decision"
                    if clean(finding.get("resolution_status")) == "resolved"
                    else ""
                ),
                "resolution_note": (
                    "Imported as resolved from the legacy review decision log."
                    if clean(finding.get("resolution_status")) == "resolved"
                    else ""
                ),
                "created_at": at,
            })
            if row["finding_status"] != OPEN_STATUS:
                row["resolved_at"] = at
                row["resolved_by"] = "queue-sync"
            rows.append(row)
            by_audit[audit_id] = row
            created += 1
        else:
            refreshed += 1
        for field in evidence_fields:
            row[field] = clean(finding.get(field))
        row["is_current"] = "true"
        row["updated_at"] = at

    for row in rows:
        if clean(row.get("audit_id")) in current_ids:
            continue
        row["is_current"] = "false"
        if clean(row.get("finding_status")) == OPEN_STATUS:
            row.update({
                "finding_status": "resolved_by_reaudit",
                "resolution_action": "resolved_by_reaudit",
                "resolution_note": "Finding no longer appears in the generated audit.",
                "resolved_at": at,
                "resolved_by": "queue-sync",
                "updated_at": at,
            })
            resolved_by_reaudit += 1
    save_queue(rows, path)
    return {
        "rows": rows,
        "created": created,
        "refreshed": refreshed,
        "resolved_by_reaudit": resolved_by_reaudit,
    }


def unresolved(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    return [
        dict(row) for row in rows
        if clean(row.get("finding_status")) == OPEN_STATUS
        and _bool(row.get("is_current"))
    ]


def queue_payload(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    open_rows = unresolved(rows)
    return {
        "records": open_rows,
        "total_unresolved": len(open_rows),
        "hidden_resolved": len(rows) - len(open_rows),
        "summary": {
            severity: sum(clean(row.get("severity")) == severity for row in open_rows)
            for severity in ("high", "medium", "low")
        },
    }


def resolve_rows(
    queue_ids: Sequence[str],
    action: str,
    note: str,
    *,
    resolved_by: str = "admin",
    path: Path = DEFAULT_QUEUE_PATH,
    now: str | None = None,
) -> list[dict[str, str]]:
    status_by_action = {
        "accept_suggestion": "accepted",
        "replace_mapping": "accepted",
        "ignore": "ignored",
        "manually_resolved": "manually_resolved",
    }
    if action not in status_by_action:
        raise InstitutionReviewQueueError("unsupported institution cleanup action")
    if not clean(note):
        raise InstitutionReviewQueueError("review note is required")
    requested = {clean(value) for value in queue_ids if clean(value)}
    if not requested:
        raise InstitutionReviewQueueError("at least one queue_id is required")
    rows = load_queue(path)
    selected = [row for row in rows if clean(row.get("queue_id")) in requested]
    if len(selected) != len(requested):
        raise InstitutionReviewQueueError("one or more cleanup findings were not found")
    if any(clean(row.get("finding_status")) != OPEN_STATUS or not _bool(row.get("is_current")) for row in selected):
        raise InstitutionReviewQueueError("only current open findings can be resolved")
    at = now or timestamp()
    for row in selected:
        row.update({
            "finding_status": status_by_action[action],
            "resolution_action": action,
            "resolution_note": clean(note),
            "resolved_at": at,
            "resolved_by": clean(resolved_by) or "admin",
            "updated_at": at,
        })
    save_queue(rows, path)
    return [dict(row) for row in selected]


def compatible_mapping_fixes(rows: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    """Return mapping -> suggestion for a safe batch, rejecting conflicts."""
    fixes: dict[str, str] = {}
    for row in rows:
        mapping_id = clean(row.get("mapping_id"))
        suggestion = clean(row.get("suggested_institution_id"))
        if not mapping_id or not suggestion:
            raise InstitutionReviewQueueError(
                "every accepted finding must identify a mapping and suggestion"
            )
        existing = fixes.get(mapping_id)
        if existing and existing != suggestion:
            raise InstitutionReviewQueueError(
                "selected findings contain conflicting fixes for one mapping"
            )
        fixes[mapping_id] = suggestion
    return fixes
