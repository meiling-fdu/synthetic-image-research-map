#!/usr/bin/env python3
"""Audit and migrate canonical paper titles to the shared title-case rule."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

try:
    from .curated_papers import (
        DEFAULT_CURATED_PAPERS_PATH,
        read_curated_papers,
        write_curated_papers,
    )
    from .title_normalization import canonical_paper_title
except ImportError:
    from curated_papers import (
        DEFAULT_CURATED_PAPERS_PATH,
        read_curated_papers,
        write_curated_papers,
    )
    from title_normalization import canonical_paper_title


DEFAULT_AUDIT_PATH = Path("data/processed/paper_title_capitalization_audit.csv")
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PUBLIC_PATHS = (
    Path("web/data/public_preview_papers.json"),
    Path("web/data/public_preview_map_data.json"),
)
AUDIT_COLUMNS = (
    "source",
    "record_id",
    "paper_id",
    "year",
    "original_title",
    "canonical_title",
    "changed",
)


def source_label(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPOSITORY_ROOT))
    except ValueError:
        return str(resolved)


def migrate_titles(
    papers_path: Path = DEFAULT_CURATED_PAPERS_PATH,
    audit_path: Path = DEFAULT_AUDIT_PATH,
    *,
    public_paths: Sequence[Path] = (),
    dry_run: bool = False,
) -> tuple[int, int]:
    prior_audit: dict[tuple[str, str], dict[str, str]] = {}
    if audit_path.exists():
        with audit_path.open(encoding="utf-8", newline="") as handle:
            for prior in csv.DictReader(handle):
                source = source_label(
                    Path(prior.get("source") or str(papers_path))
                )
                record_id = prior.get("record_id") or prior.get("paper_id", "")
                prior_audit[(source, record_id)] = prior
    rows = read_curated_papers(papers_path)
    audit_rows = []
    changed = 0
    for row in rows:
        current = row.get("title", "")
        key = (source_label(papers_path), row.get("paper_id", ""))
        original = prior_audit.get(key, {}).get("original_title", current)
        canonical = canonical_paper_title(current)
        was_changed = canonical != original
        changed += int(was_changed)
        audit_rows.append(
            {
                "source": source_label(papers_path),
                "record_id": row.get("paper_id", ""),
                "paper_id": row.get("paper_id", ""),
                "year": row.get("year", ""),
                "original_title": original,
                "canonical_title": canonical,
                "changed": str(was_changed).lower(),
            }
        )
        row["title"] = canonical

    public_payloads: list[tuple[Path, Mapping[str, Any]]] = []
    for public_path in public_paths:
        with public_path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        records = payload.get("records", [])
        if not isinstance(records, list):
            raise ValueError(f"{public_path} records must be an array")
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise ValueError(f"{public_path} record {index} must be an object")
            current = record.get("title", "")
            legacy_record_id = str(
                record.get("marker_id")
                or record.get("paper_id")
                or record.get("doi")
                or record.get("openalex_url")
                or index
            )
            record_id = str(record.get("id") or legacy_record_id)
            key = (source_label(public_path), record_id)
            legacy_key = (source_label(public_path), legacy_record_id)
            original = prior_audit.get(
                key, prior_audit.get(legacy_key, {})
            ).get("original_title", current)
            canonical = canonical_paper_title(current)
            was_changed = canonical != original
            changed += int(was_changed)
            audit_rows.append(
                {
                    "source": source_label(public_path),
                    "record_id": record_id,
                    "paper_id": record.get("paper_id", ""),
                    "year": record.get("year", record.get("publication_year", "")),
                    "original_title": original,
                    "canonical_title": canonical,
                    "changed": str(was_changed).lower(),
                }
            )
            record["title"] = canonical
        public_payloads.append((public_path, payload))

    if not dry_run:
        write_curated_papers(rows, papers_path)
        for public_path, payload in public_payloads:
            temporary_public_path = public_path.with_suffix(public_path.suffix + ".tmp")
            with temporary_public_path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            temporary_public_path.replace(public_path)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = audit_path.with_suffix(audit_path.suffix + ".tmp")
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=AUDIT_COLUMNS, lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(audit_rows)
        temporary_path.replace(audit_path)
    return len(rows) + sum(
        len(payload.get("records", [])) for _, payload in public_payloads
    ), changed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papers", type=Path, default=DEFAULT_CURATED_PAPERS_PATH)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT_PATH)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    total, changed = migrate_titles(
        args.papers,
        args.audit,
        public_paths=DEFAULT_PUBLIC_PATHS,
        dry_run=args.dry_run,
    )
    action = "Would normalize" if args.dry_run else "Normalized"
    print(f"{action} {changed} of {total} canonical paper titles.")
    if not args.dry_run:
        print(f"Audit: {args.audit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
