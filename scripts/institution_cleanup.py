#!/usr/bin/env python3
"""Transactional institution cleanup actions shared by Admin and tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence
import csv

try:
    from .curated_institutions import (
        DEFAULT_INSTITUTIONS_PATH,
        append_mapping_change_resolution_audit,
        load_institutions,
    )
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
        MAPPING_CHANGE_RESOLUTION_ACTIONS,
    )
except ImportError:
    from curated_institutions import (
        DEFAULT_INSTITUTIONS_PATH,
        append_mapping_change_resolution_audit,
        load_institutions,
    )
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
        MAPPING_CHANGE_RESOLUTION_ACTIONS,
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


def _audit_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError as error:
        raise InstitutionReviewQueueError(f"could not read institution audit log: {error}") from error


def _metadata(value: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for part in clean(value).split(";"):
        key, separator, item = part.strip().partition("=")
        if separator and key:
            result[key.strip()] = item.strip()
    return result


def _require_expected_state(
    selected: Sequence[Mapping[str, Any]], mapping: Mapping[str, Any], *,
    expected_mapping_id: Any, expected_institution_id: Any,
    expected_mapping_updated_at: Any, expected_review_updated_at: Any,
) -> None:
    expected = {
        "mapping_id": clean(expected_mapping_id),
        "institution_id": clean(expected_institution_id),
        "mapping_updated_at": clean(expected_mapping_updated_at),
        "review_updated_at": clean(expected_review_updated_at),
    }
    if not all(expected.values()):
        raise InstitutionReviewQueueError(
            "expected mapping and review state is required; refresh the review and try again"
        )
    stale = (
        len(selected) != 1
        or clean(mapping.get("mapping_id")) != expected["mapping_id"]
        or clean(mapping.get("institution_id")) != expected["institution_id"]
        or clean(mapping.get("updated_at")) != expected["mapping_updated_at"]
        or clean(selected[0].get("updated_at")) != expected["review_updated_at"]
    )
    if stale:
        raise InstitutionReviewQueueError(
            "the mapping or review changed after this panel was loaded; refresh and review the new state"
        )


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
    expected_mapping_id: str = "",
    expected_institution_id: str = "",
    expected_mapping_updated_at: str = "",
    expected_review_updated_at: str = "",
) -> dict[str, Any]:
    """Resolve queue rows, updating mappings first when the action requires it."""
    note = clean(review_note)
    selected = _selected_open(queue_ids, queue_path)
    if action in MAPPING_CHANGE_RESOLUTION_ACTIONS:
        if len(selected) != 1 or clean(selected[0].get("issue_type")) != "confirmed_mapping_changed":
            raise InstitutionReviewQueueError(
                "mapping change actions require exactly one confirmed_mapping_changed finding"
            )
        if not note:
            raise InstitutionReviewQueueError("resolution note is required")
        if not confirmed:
            raise InstitutionReviewQueueError("mapping change resolution requires explicit confirmation")
        if institution_audit_path is None:
            raise InstitutionReviewQueueError("institution audit log is required")
        mappings = {clean(row.get("mapping_id")): row for row in load_mappings(mappings_path)}
        finding = selected[0]
        mapping_id = clean(finding.get("mapping_id"))
        mapping = mappings.get(mapping_id)
        if mapping is None:
            raise InstitutionReviewQueueError(f"mapping not found: {mapping_id}")
        _require_expected_state(
            selected, mapping,
            expected_mapping_id=expected_mapping_id,
            expected_institution_id=expected_institution_id,
            expected_mapping_updated_at=expected_mapping_updated_at,
            expected_review_updated_at=expected_review_updated_at,
        )
        source_audit = next((
            row for row in _audit_rows(institution_audit_path)
            if clean(row.get("audit_id")) == clean(finding.get("audit_id"))
            and clean(row.get("action")) == "confirmed_mapping_changed"
        ), None)
        if source_audit is None:
            raise InstitutionReviewQueueError("source mapping-change audit record was not found")
        metadata = _metadata(source_audit.get("confirmation_text"))
        old_id = clean(source_audit.get("previous_institution_id"))
        new_id = clean(source_audit.get("institution_id"))
        if clean(mapping.get("institution_id")) != new_id:
            raise InstitutionReviewQueueError(
                "the mapping no longer matches this review; refresh and review the new state"
            )
        institutions = {
            clean(row.get("institution_id")): row for row in load_institutions(institutions_path)
        }
        old_name = clean(metadata.get("previous_institution")) or clean(
            institutions.get(old_id, {}).get("canonical_name")
        )
        new_name = clean(metadata.get("new_institution")) or clean(mapping.get("institution"))
        if old_id not in institutions:
            raise InstitutionReviewQueueError("previous trusted institution no longer exists")
        at = timestamp()
        snapshot_paths = [mappings_path, location_review_path, queue_path, institution_audit_path]
        snapshots = _snapshot(snapshot_paths)
        changed: list[dict[str, Any]] = []
        try:
            if action == "mapping_reverted":
                target = institutions[old_id]
                draft = dict(mapping)
                prior_note = clean(mapping.get("review_note"))
                audit_note = f"[{at}] Reverted confirmed mapping change: {note}"
                draft.update({
                    "institution": clean(target.get("canonical_name")) or old_name,
                    "institution_id": old_id,
                    "openalex_institution_id": "",
                    "institution_city": "",
                    "institution_country": "",
                    "institution_latitude": "",
                    "institution_longitude": "",
                    "review_note": f"{prior_note} | {audit_note}" if prior_note else audit_note,
                })
                changed.append(update_mapping(
                    mapping, mapping_id, draft,
                    map_records=map_records,
                    mappings_path=mappings_path,
                    location_review_path=location_review_path,
                    institutions_path=institutions_path,
                    institution_audit_path=institution_audit_path,
                    change_source="institution_cleanup:mapping_reverted",
                    changed_by=resolved_by,
                ))
            resolution_audit = append_mapping_change_resolution_audit(
                action=action,
                review_queue_id=finding.get("queue_id"),
                source_audit_id=finding.get("audit_id"),
                mapping_id=mapping_id,
                previous_institution_id=old_id,
                previous_institution_name=old_name,
                new_institution_id=new_id,
                new_institution_name=new_name,
                reverted_institution_id=old_id if action == "mapping_reverted" else "",
                reverted_institution_name=old_name if action == "mapping_reverted" else "",
                evidence_source=mapping.get("evidence_source"),
                evidence_url=mapping.get("evidence_url"),
                review_note=note,
                created_by=resolved_by,
                created_at=at,
                audit_path=institution_audit_path,
            )
            resolved = resolve_rows(
                queue_ids, action, note, resolved_by=resolved_by, path=queue_path, now=at
            )
        except Exception:
            _restore(snapshots)
            raise
        return {
            "resolved": resolved,
            "mappings": changed,
            "audit": resolution_audit,
            "reaudit": "scheduled_for_next_full_refresh",
        }
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
