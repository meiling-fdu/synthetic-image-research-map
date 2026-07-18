#!/usr/bin/env python3
"""Atomically enforce the book invariant in existing public JSON artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .publication_types import normalize_book_record
except ImportError:
    from publication_types import normalize_book_record


DEFAULT_PATHS = (
    Path("web/data/public_preview_papers.json"),
    Path("web/data/public_preview_map_data.json"),
)


def identity(record):
    return (
        record.get("id", ""),
        record.get("paper_id", ""),
        record.get("doi", ""),
        record.get("openalex_url", ""),
        record.get("title", ""),
        record.get("year", record.get("publication_year", "")),
        record.get("institution_id", ""),
        record.get("institution", ""),
    )


def normalize_path(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError(f"{path} has no JSON record list")
    before = [identity(record) for record in records]
    cleaned = [normalize_book_record(record, remove=True) for record in records]
    after = [identity(record) for record in cleaned]
    if before != after or len(records) != len(cleaned):
        raise RuntimeError(f"identity or record count changed while cleaning {path}")
    changed = sum(left != right for left, right in zip(records, cleaned))
    if isinstance(payload, dict):
        payload["records"] = cleaned
    else:
        payload = cleaned
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path, default=list(DEFAULT_PATHS))
    args = parser.parse_args()
    for path in args.paths:
        print(f"{path}: normalized {normalize_path(path)} book records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
