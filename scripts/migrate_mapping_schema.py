#!/usr/bin/env python3
"""Drop obsolete paper-mapping columns without changing mapping rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .curated_mappings import DEFAULT_MAPPINGS_PATH, load_mappings, save_mappings
except ImportError:
    from curated_mappings import DEFAULT_MAPPINGS_PATH, load_mappings, save_mappings


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PUBLIC_OUTPUTS = (
    ROOT / "web/data/public_preview_papers.json",
    ROOT / "web/data/public_preview_map_data.json",
)


def migrate(path: Path = DEFAULT_MAPPINGS_PATH) -> int:
    rows = load_mappings(path)
    save_mappings(rows, path)
    return len(rows)


def migrate_public_output(path: Path) -> tuple[int, int]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise ValueError(f"{path} does not contain a records array")
    removed = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        mapping_records = []
        if record.get("mapping_id"):
            mapping_records.append(record)
        if isinstance(record.get("curated_mappings"), list):
            mapping_records.extend(
                mapping for mapping in record["curated_mappings"]
                if isinstance(mapping, dict)
            )
        for mapping in mapping_records:
            for field in (
                "evidence_source",
                "evidence_url",
                "affiliation_note",
                "review_note",
            ):
                if field in mapping:
                    mapping.pop(field)
                    removed += 1
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary.replace(path)
    return len(records), removed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite paper-level mappings with the canonical schema."
    )
    parser.add_argument("--path", type=Path, default=DEFAULT_MAPPINGS_PATH)
    parser.add_argument(
        "--skip-public", action="store_true",
        help="Do not migrate mapping objects in generated public outputs.",
    )
    args = parser.parse_args()
    count = migrate(args.path)
    print(f"Migrated {count} mapping rows in {args.path}")
    if not args.skip_public:
        for output in DEFAULT_PUBLIC_OUTPUTS:
            records, removed = migrate_public_output(output)
            print(
                f"Migrated {records} public records in {output}; "
                f"removed {removed} obsolete mapping fields"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
