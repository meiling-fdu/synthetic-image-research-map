"""Shared metadata and transactional writes for public-preview exports."""

from __future__ import annotations

import copy
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


TIMESTAMP_FIELD = "public_preview_generated_at"
UTC_TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def utc_timestamp(now: datetime | None = None) -> str:
    """Return the successful export instant as stable second-precision UTC."""
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return (
        value.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def is_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not UTC_TIMESTAMP_PATTERN.fullmatch(value):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def add_export_timestamp(
    map_payload: dict[str, Any],
    paper_payload: dict[str, Any],
    timestamp: str,
) -> None:
    """Attach exactly one computed timestamp to both proposed outputs."""
    if not is_utc_timestamp(timestamp):
        raise ValueError(f"Invalid UTC public-export timestamp: {timestamp!r}")
    for payload in (map_payload, paper_payload):
        metadata = payload.setdefault("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("Public output metadata must be an object")
        metadata[TIMESTAMP_FIELD] = timestamp


def _json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def stable_public_content(payload: Mapping[str, Any]) -> str:
    """Return a deterministic export signature excluding only the volatile timestamp."""
    comparable = copy.deepcopy(dict(payload))
    metadata = comparable.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop(TIMESTAMP_FIELD, None)
    records = comparable.get("records")
    if isinstance(records, list):
        comparable["records"] = sorted(
            records,
            key=lambda record: json.dumps(record, ensure_ascii=False, sort_keys=True),
        )
    return json.dumps(comparable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def atomic_write_json_files(payloads: Mapping[Path, Mapping[str, Any]]) -> None:
    """Commit a set of JSON files together, rolling all targets back on error.

    Each candidate is fully serialized and fsynced beside its destination first.
    Replacements then use ``os.replace``. Existing bytes are retained in memory
    so a later replacement failure restores every target already replaced.
    """
    prepared: dict[Path, Path] = {}
    previous: dict[Path, bytes | None] = {}
    replaced: list[Path] = []
    try:
        for raw_path, payload in payloads.items():
            path = Path(raw_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            previous[path] = path.read_bytes() if path.exists() else None
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
            )
            temporary = Path(temporary_name)
            prepared[path] = temporary
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(_json_bytes(payload))
                handle.flush()
                os.fsync(handle.fileno())

        for path, temporary in prepared.items():
            os.replace(temporary, path)
            replaced.append(path)
    except Exception as error:
        rollback_errors: list[str] = []
        for path in reversed(replaced):
            try:
                content = previous[path]
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    descriptor, rollback_name = tempfile.mkstemp(
                        prefix=f".{path.name}.", suffix=".rollback", dir=path.parent
                    )
                    rollback = Path(rollback_name)
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(content)
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.replace(rollback, path)
            except Exception as rollback_error:  # pragma: no cover - catastrophic I/O
                rollback_errors.append(f"{path}: {rollback_error}")
        detail = (
            f" Rollback also failed for: {'; '.join(rollback_errors)}"
            if rollback_errors
            else ""
        )
        raise OSError(f"Could not commit public outputs: {error}.{detail}") from error
    finally:
        for temporary in prepared.values():
            temporary.unlink(missing_ok=True)
