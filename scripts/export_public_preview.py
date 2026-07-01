#!/usr/bin/env python3
"""Write public previews exclusively from canonical curated entities."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

try:
    from .canonical_authorship import CanonicalAuthorshipError
    from .curated_export import curated_export
except ImportError:
    from canonical_authorship import CanonicalAuthorshipError
    from curated_export import curated_export


DEFAULT_OUTPUT = Path("web/data/public_preview_map_data.json")
DEFAULT_PAPER_OUTPUT = Path("web/data/public_preview_papers.json")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--paper-output", type=Path, default=DEFAULT_PAPER_OUTPUT)
    parser.add_argument("--paper-id", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _payload(kind: str, records: list[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "metadata": {
            "dataset_type": kind,
            "architecture": "canonical_authorship_only",
        },
        "records": records,
    }


def _read(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"records": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _merge_incremental(
    path: Path, payload: Dict[str, Any], paper_id: str
) -> Dict[str, Any]:
    generated = [
        row for row in payload["records"] if row.get("paper_id") == paper_id
    ]
    old = _read(path)
    merged = []
    inserted = False
    for row in old.get("records", []):
        if row.get("paper_id") == paper_id:
            if not inserted:
                merged.extend(generated)
                inserted = True
        else:
            merged.append(row)
    if not inserted:
        merged.extend(generated)
    return {**payload, "records": merged}


def _write(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        records = curated_export()
        map_payload = _payload("canonical_public_preview_map", records["markers"])
        paper_payload = _payload("canonical_public_preview_papers", records["papers"])
        if args.paper_id:
            map_payload = _merge_incremental(args.output, map_payload, args.paper_id)
            paper_payload = _merge_incremental(
                args.paper_output, paper_payload, args.paper_id
            )
        if not args.dry_run:
            _write(args.output, map_payload)
            _write(args.paper_output, paper_payload)
        print(
            f"Canonical export: {len(paper_payload['records'])} papers, "
            f"{len(map_payload['records'])} markers."
        )
        return 0
    except (CanonicalAuthorshipError, OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
