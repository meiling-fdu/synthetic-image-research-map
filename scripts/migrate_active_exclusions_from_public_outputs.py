#!/usr/bin/env python3
"""Remove actively excluded identities from the committed public JSON pair."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from .export_public_preview import PreviewExportError, commit_public_outputs
    from .paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        filter_public_output_pair,
        read_exclusion_rows,
    )
    from .paper_version_merges import (
        DEFAULT_PAPER_VERSION_MERGES_PATH,
        read_paper_version_merges,
    )
except ImportError:
    from export_public_preview import PreviewExportError, commit_public_outputs
    from paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        filter_public_output_pair,
        read_exclusion_rows,
    )
    from paper_version_merges import (
        DEFAULT_PAPER_VERSION_MERGES_PATH,
        read_paper_version_merges,
    )


ROOT = Path(__file__).resolve().parent.parent
MAP_PATH = ROOT / "web/data/public_preview_map_data.json"
PAPER_PATH = ROOT / "web/data/public_preview_papers.json"


def read_payload(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise PaperExclusionError(f"{path} does not contain a records array")
    return payload


def main() -> int:
    try:
        map_payload = read_payload(MAP_PATH)
        paper_payload = read_payload(PAPER_PATH)
        exclusions = read_exclusion_rows(DEFAULT_EXCLUSIONS_PATH)
        papers, maps, summary = filter_public_output_pair(
            paper_payload["records"], map_payload["records"], exclusions
        )
        paper_payload["records"] = papers
        map_payload["records"] = maps
        removed_papers = summary["active_exclusion_public_papers_removed"]
        removed_maps = summary["active_exclusion_map_records_removed"]
        if removed_papers or removed_maps:
            commit_public_outputs(
                MAP_PATH,
                map_payload,
                PAPER_PATH,
                paper_payload,
                read_paper_version_merges(DEFAULT_PAPER_VERSION_MERGES_PATH),
            )
        print(
            "Active-exclusion public migration: "
            f"removed {removed_papers} paper records and {removed_maps} map records"
        )
        return 0
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        PaperExclusionError,
        PreviewExportError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
