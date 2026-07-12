#!/usr/bin/env python3
"""Stamp validated public-preview outputs with their successful generation time."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATHS = (
    Path("web/data/public_preview_map_data.json"),
    Path("web/data/public_preview_papers.json"),
)
TIMESTAMP_FIELD = "public_preview_generated_at"


def utc_timestamp(now: datetime | None = None) -> str:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stamp_previews(paths: Sequence[Path], timestamp: str) -> None:
    prepared: list[tuple[Path, Path]] = []
    try:
        for path in paths:
            with path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict) or not isinstance(payload.get("metadata"), dict):
                raise ValueError(f"{path} does not contain a metadata object")
            payload["metadata"][TIMESTAMP_FIELD] = timestamp
            temporary = path.with_suffix(path.suffix + ".stamp.tmp")
            with temporary.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            prepared.append((path, temporary))
        for path, temporary in prepared:
            temporary.replace(path)
    finally:
        for _path, temporary in prepared:
            temporary.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", default=utc_timestamp())
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)
    paths = tuple(args.paths) or tuple(ROOT / path for path in DEFAULT_PATHS)
    stamp_previews(paths, args.timestamp)
    print(f"Stamped validated public preview: {args.timestamp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
