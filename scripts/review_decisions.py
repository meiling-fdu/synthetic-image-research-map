#!/usr/bin/env python3
"""Persist explicit admin review outcomes without editing generated reports."""

from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

try:
    from .curated_schema import (
        ALLOWED_REVIEW_ACTIONS,
        ALLOWED_REVIEW_QUEUES,
        CURATED_DATA_DIR,
        REVIEW_DECISION_COLUMNS,
    )
except ImportError:
    from curated_schema import (
        ALLOWED_REVIEW_ACTIONS,
        ALLOWED_REVIEW_QUEUES,
        CURATED_DATA_DIR,
        REVIEW_DECISION_COLUMNS,
    )


DEFAULT_REVIEW_DECISIONS_PATH = CURATED_DATA_DIR / "review_decisions.csv"


class ReviewDecisionError(RuntimeError):
    """A review decision is invalid or could not be saved."""


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def read_review_decisions(
    path: Path = DEFAULT_REVIEW_DECISIONS_PATH,
) -> list[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != REVIEW_DECISION_COLUMNS:
                raise ReviewDecisionError(
                    f"{path} does not have the exact review-decision header"
                )
            return [dict(row) for row in reader]
    except (OSError, UnicodeError, csv.Error) as error:
        raise ReviewDecisionError(f"could not read {path}: {error}") from error


def _write(rows: list[Mapping[str, Any]], path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=REVIEW_DECISION_COLUMNS,
                extrasaction="ignore",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise ReviewDecisionError(f"could not write {path}: {error}") from error


def upsert_review_decision(
    draft: Mapping[str, Any],
    path: Path = DEFAULT_REVIEW_DECISIONS_PATH,
) -> Dict[str, str]:
    queue = clean(draft.get("review_queue"))
    action = clean(draft.get("action"))
    note = clean(draft.get("review_note"))
    if queue not in ALLOWED_REVIEW_QUEUES:
        raise ReviewDecisionError(f"unsupported review queue: {queue!r}")
    if action not in ALLOWED_REVIEW_ACTIONS:
        raise ReviewDecisionError(f"unsupported review action: {action!r}")
    if not note:
        raise ReviewDecisionError("review note is required")

    identity = "|".join(
        clean(draft.get(field)).casefold()
        for field in (
            "review_queue",
            "target_type",
            "doi",
            "openalex_url",
            "title",
            "year",
            "institution",
        )
    )
    if not any(
        clean(draft.get(field))
        for field in ("doi", "openalex_url", "title", "institution")
    ):
        raise ReviewDecisionError("a paper or institution identity is required")
    decision_id = "review:" + hashlib.sha256(identity.encode()).hexdigest()[:20]
    rows = read_review_decisions(path)
    now = _now()
    existing = next(
        (row for row in rows if clean(row.get("decision_id")) == decision_id),
        None,
    )
    created_at = clean(existing.get("created_at")) if existing else now
    row = {
        "decision_id": decision_id,
        "review_queue": queue,
        "target_type": clean(draft.get("target_type")) or "paper",
        "title": clean(draft.get("title")),
        "year": clean(draft.get("year")),
        "doi": clean(draft.get("doi")),
        "openalex_url": clean(draft.get("openalex_url")),
        "institution": clean(draft.get("institution")),
        "action": action,
        "review_note": note,
        "created_at": created_at,
        "updated_at": now,
        "created_by": clean(draft.get("created_by")) or "local_admin",
    }
    if existing:
        rows[rows.index(existing)] = row
    else:
        rows.append(row)
    _write(rows, path)
    return row
