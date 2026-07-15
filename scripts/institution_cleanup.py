#!/usr/bin/env python3
"""Transactional institution cleanup actions shared by Admin and tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .curated_institutions import DEFAULT_INSTITUTIONS_PATH, load_institutions
    from .curated_mappings import (
        DEFAULT_LOCATION_REVIEW_PATH,
        DEFAULT_MAPPINGS_PATH,
        load_mappings,
        update_mapping,
    )
    from .institution_review_queue import (
        DEFAULT_QUEUE_PATH,
        InstitutionReviewQueueError,
        clean,
        compatible_mapping_fixes,
        load_queue,
        resolve_rows,
        timestamp,
    )
except ImportError:
    from curated_institutions import DEFAULT_INSTITUTIONS_PATH, load_institutions
    from curated_mappings import (
        DEFAULT_LOCATION_REVIEW_PATH,
        DEFAULT_MAPPINGS_PATH,
        load_mappings,
        update_mapping,
    )
    from institution_review_queue import (
        DEFAULT_QUEUE_PATH,
        InstitutionReviewQueueError,
        clean,
        compatible_mapping_fixes,
        load_queue,
        resolve_rows,
        timestamp,
    )


def _snapshot(paths: Sequence[Path]) -> dict[Path, bytes | None]:
    return {path: path.read_bytes() if path.exists() else None for path in paths}


def _restore(snapshots: Mapping[Path, bytes | None]) -> None:
    for path, content in snapshots.items():
        if content is None:
            if path.exists():
                path.unlink()
        else:
            path.write_bytes(content)


def _selected_open(queue_ids: Sequence[str], queue_path: Path) -> list[dict[str, str]]:
    requested = {clean(value) for value in queue_ids if clean(value)}
    rows = load_queue(queue_path)
    selected = [row for row in rows if clean(row.get("queue_id")) in requested]
    if not requested or len(selected) != len(requested):
        raise InstitutionReviewQueueError("one or more cleanup findings were not found")
    if any(
        clean(row.get("finding_status")) != "open"
        or clean(row.get("is_current")).casefold() != "true"
        for row in selected
    ):
        raise InstitutionReviewQueueError("only current open findings can be resolved")
    return selected


def apply_cleanup_action(
    queue_ids: Sequence[str],
    action: str,
    review_note: str,
    *,
    replacement_institution_id: str = "",
    confirmed: bool = False,
    resolved_by: str = "admin",
    queue_path: Path = DEFAULT_QUEUE_PATH,
    mappings_path: Path = DEFAULT_MAPPINGS_PATH,
    location_review_path: Path = DEFAULT_LOCATION_REVIEW_PATH,
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    institution_audit_path: Path | None = None,
    map_records: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Resolve queue rows, updating mappings first when the action requires it."""
    note = clean(review_note)
    selected = _selected_open(queue_ids, queue_path)
    if action in {"ignore", "manually_resolved", "keep_multiple_affiliations"}:
        resolved = resolve_rows(
            queue_ids, action, note, resolved_by=resolved_by, path=queue_path
        )
        return {"resolved": resolved, "mappings": []}
    if action not in {"accept_suggestion", "replace_mapping"}:
        raise InstitutionReviewQueueError("unsupported institution cleanup action")
    if not note:
        raise InstitutionReviewQueueError(
            "review note is required for mapping replacement actions"
        )
    if not confirmed:
        raise InstitutionReviewQueueError("mapping changes require explicit confirmation")

    if action == "replace_mapping":
        replacement = clean(replacement_institution_id)
        if not replacement:
            raise InstitutionReviewQueueError("replacement_institution_id is required")
        for row in selected:
            row["suggested_institution_id"] = replacement
    fixes = compatible_mapping_fixes(selected)
    institutions = {
        clean(row.get("institution_id")): row
        for row in load_institutions(institutions_path)
        if clean(row.get("institution_status")) == "active"
    }
    mappings = {clean(row.get("mapping_id")): row for row in load_mappings(mappings_path)}
    for mapping_id, institution_id in fixes.items():
        if mapping_id not in mappings:
            raise InstitutionReviewQueueError(f"mapping not found: {mapping_id}")
        if institution_id not in institutions:
            raise InstitutionReviewQueueError(
                f"suggested institution is not active: {institution_id}"
            )

    snapshot_paths = [mappings_path, location_review_path, queue_path]
    if institution_audit_path is not None:
        snapshot_paths.append(institution_audit_path)
    snapshots = _snapshot(snapshot_paths)
    changed: list[dict[str, Any]] = []
    try:
        for mapping_id, institution_id in fixes.items():
            mapping = mappings[mapping_id]
            target = institutions[institution_id]
            prior_note = clean(mapping.get("review_note"))
            audit_note = f"[{timestamp()}] Institution cleanup: {note}"
            draft = dict(mapping)
            draft.update({
                "institution": clean(target.get("canonical_name")),
                "institution_id": institution_id,
                "openalex_institution_id": "",
                "institution_city": "",
                "institution_country": "",
                "institution_latitude": "",
                "institution_longitude": "",
                "provenance_source": "admin_accepted",
                "review_note": f"{prior_note} | {audit_note}" if prior_note else audit_note,
            })
            result = update_mapping(
                mapping,
                mapping_id,
                draft,
                map_records=map_records,
                mappings_path=mappings_path,
                location_review_path=location_review_path,
                institutions_path=institutions_path,
                institution_audit_path=institution_audit_path,
                change_source=f"institution_cleanup:{action}",
                changed_by=resolved_by,
            )
            changed.append(result)
        resolved = resolve_rows(
            queue_ids,
            action,
            note,
            resolved_by=resolved_by,
            path=queue_path,
        )
    except Exception:
        _restore(snapshots)
        raise
    return {"resolved": resolved, "mappings": changed}
