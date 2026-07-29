#!/usr/bin/env python3
"""Audit whether every retained public paper has authoritative source evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = Path("data/processed/full_source_completeness_audit.csv")
DEFAULT_EXCEPTIONS = Path("data/curated/full_source_completeness_exceptions.csv")
FIELDS = (
    "public_paper_id", "title", "doi", "arxiv_id", "publication_type", "venue",
    "current_public_source", "candidate_match", "curated_match",
    "override_match", "alternate_identity_match", "status", "root_cause",
    "proposed_action", "durable_evidence_path",
)
ACCEPTED_STATUSES = {
    "restored_missing_source",
    "resolved_identity_mismatch",
    "override_only_valid",
    "intentionally_preserved",
}
AUTHORITATIVE_SOURCES = (
    ("candidate_map", Path("web/data/openalex_candidate_map_data.json")),
    ("candidate_papers_in_scope", Path("data/processed/openalex_candidate_papers_in_scope.csv")),
    ("candidate_papers_all", Path("data/processed/openalex_candidate_papers.csv")),
    ("curated", Path("data/curated/papers.csv")),
    ("key_papers", Path("data/manual/key_papers.csv")),
    ("key_papers_enriched", Path("data/manual/key_papers_enriched.csv")),
    ("manual_openalex_imports", Path("data/manual/key_paper_openalex_manual_imports.csv")),
    ("reviewed_openalex_intake", Path("data/manual/key_papers_openalex_ready_all_batches.csv")),
)
OVERRIDE_SOURCES = (
    ("paper_arxiv_links", Path("data/manual/paper_arxiv_links.csv")),
    ("curated_arxiv_links", Path("data/curated/paper_arxiv_links.csv")),
    ("paper_version_overrides", Path("data/manual/paper_version_overrides.csv")),
    ("paper_version_merges", Path("data/curated/paper_version_merges.csv")),
    ("publication_overrides", Path("data/manual/publication_overrides.csv")),
)


def clean(value: Any) -> str:
    return str(value or "").strip()


def normalized_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value).casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalized_doi(value: Any) -> str:
    value = clean(value).casefold()
    value = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", value)
    return value.removeprefix("doi:")


def normalized_openalex(value: Any) -> str:
    value = clean(value).casefold().rstrip("/")
    match = re.search(r"(w\d+)$", value)
    return match.group(1) if match else value


def normalized_arxiv(value: Any) -> str:
    value = clean(value).casefold()
    value = re.sub(r"^(?:https?://)?arxiv\.org/(?:abs|pdf)/", "", value)
    value = value.removesuffix(".pdf").removeprefix("arxiv:")
    return re.sub(r"v\d+$", "", value)


def identity_keys(row: Mapping[str, Any]) -> set[str]:
    keys = set()
    paper_id = clean(row.get("paper_id") or row.get("id")).casefold()
    if paper_id:
        keys.add(f"paper:{paper_id}")
    doi = normalized_doi(
        row.get("doi") or row.get("published_doi")
        or row.get("canonical_doi") or row.get("duplicate_doi")
    )
    if doi:
        keys.add(f"doi:{doi}")
    openalex = normalized_openalex(
        row.get("openalex_url") or row.get("openalex_id")
        or row.get("published_openalex_url")
        or row.get("canonical_openalex_url") or row.get("duplicate_openalex_url")
        or row.get("enriched_openalex_url") or row.get("candidate_openalex_url")
    )
    if openalex:
        keys.add(f"openalex:{openalex}")
    arxiv = normalized_arxiv(
        row.get("arxiv_id") or row.get("canonical_arxiv_id")
        or row.get("duplicate_arxiv_id") or row.get("arxiv_url")
    )
    if arxiv:
        keys.add(f"arxiv:{arxiv}")
    return keys


def title_year_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return (
        normalized_text(
            row.get("title") or row.get("canonical_title")
            or row.get("duplicate_title")
        ),
        clean(
            row.get("year") or row.get("publication_year")
            or row.get("canonical_year") or row.get("duplicate_year")
        ),
    )


def read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if path.suffix == ".json":
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        rows = payload.get("records", []) if isinstance(payload, dict) else payload
        return [dict(row) for row in rows if isinstance(row, dict)]
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(frozen=True)
class SourceRow:
    source: str
    path: Path
    row: Mapping[str, Any]


def load_sources(
    specs: Sequence[tuple[str, Path]],
    root: Path = ROOT,
) -> list[SourceRow]:
    return [
        SourceRow(name, path, row)
        for name, path in specs
        for row in read_rows(root / path)
    ]


def exception_index(rows: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    result = {}
    for row in rows:
        if clean(row.get("is_active")).casefold() not in {"1", "true", "yes"}:
            continue
        for key in identity_keys(row):
            result[key] = row
    return result


def audit_completeness(
    public_rows: Sequence[Mapping[str, Any]],
    authoritative: Sequence[SourceRow],
    overrides: Sequence[SourceRow],
    exceptions: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, str]]:
    authoritative_keys: dict[str, list[SourceRow]] = {}
    authoritative_titles: dict[tuple[str, str], list[SourceRow]] = {}
    override_keys: dict[str, list[SourceRow]] = {}
    override_titles: dict[tuple[str, str], list[SourceRow]] = {}
    for item in authoritative:
        for key in identity_keys(item.row):
            authoritative_keys.setdefault(key, []).append(item)
        authoritative_titles.setdefault(title_year_key(item.row), []).append(item)
    for item in overrides:
        for key in identity_keys(item.row):
            override_keys.setdefault(key, []).append(item)
        override_titles.setdefault(title_year_key(item.row), []).append(item)
    exceptions_by_key = exception_index(exceptions)

    audit = []
    for public in public_rows:
        keys = identity_keys(public)
        exact = [item for key in keys for item in authoritative_keys.get(key, ())]
        override = [item for key in keys for item in override_keys.get(key, ())]
        title_matches = authoritative_titles.get(title_year_key(public), [])
        alternate = [
            item for item in title_matches
            if identity_keys(item.row) and not (identity_keys(item.row) & keys)
        ]
        exception = next(
            (exceptions_by_key[key] for key in keys if key in exceptions_by_key),
            None,
        )
        candidate = sorted({
            str(item.path) for item in exact
            if item.source.startswith("candidate") or item.source in {
                "key_papers", "key_papers_enriched", "manual_openalex_imports"
            }
        })
        curated = sorted({
            str(item.path) for item in exact if item.source == "curated"
        })
        override_paths = sorted({str(item.path) for item in override})
        alternate_paths = sorted({str(item.path) for item in alternate})
        if exact:
            status = "restored_missing_source"
            root_cause = "completeness union previously omitted an authoritative exporter input"
            proposed = "include matched authoritative input in completeness proof"
            evidence = sorted({str(item.path) for item in exact})
        elif alternate:
            status = "resolved_identity_mismatch"
            root_cause = "same normalized title/year has a different canonical identity"
            proposed = "review and record the canonical identity transition"
            evidence = alternate_paths
        elif exception and clean(exception.get("status")) in ACCEPTED_STATUSES:
            status = clean(exception.get("status"))
            root_cause = clean(exception.get("reason")) or "curator-approved exception"
            proposed = clean(exception.get("proposed_action")) or "retain with durable evidence"
            evidence = [str(DEFAULT_EXCEPTIONS)]
        elif override:
            status = "ambiguous_manual_review"
            root_cause = "paper appears only in override/version metadata, not an authoritative paper source"
            proposed = "restore an authoritative paper row or add reviewed preservation evidence"
            evidence = override_paths
        else:
            status = "unresolved"
            root_cause = "retained only from an older public export"
            proposed = "restore source evidence or review as stale public data"
            evidence = []
        audit.append({
            "public_paper_id": clean(public.get("paper_id") or public.get("id")),
            "title": clean(public.get("title")),
            "doi": clean(public.get("doi")),
            "arxiv_id": clean(public.get("arxiv_id")),
            "publication_type": clean(public.get("publication_type")),
            "venue": clean(public.get("venue") or public.get("venue_name")),
            "current_public_source": clean(public.get("source") or public.get("record_source")),
            "candidate_match": " | ".join(candidate),
            "curated_match": " | ".join(curated),
            "override_match": " | ".join(override_paths),
            "alternate_identity_match": " | ".join(alternate_paths),
            "status": status,
            "root_cause": root_cause,
            "proposed_action": proposed,
            "durable_evidence_path": " | ".join(evidence),
        })
    return audit


def write_audit(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def accepted(row: Mapping[str, Any]) -> bool:
    return clean(row.get("status")) in ACCEPTED_STATUSES


def repository_audit(
    public: Sequence[Mapping[str, Any]],
    *,
    root: Path = ROOT,
    exceptions_path: Path = DEFAULT_EXCEPTIONS,
) -> list[dict[str, str]]:
    return audit_completeness(
        public,
        load_sources(AUTHORITATIVE_SOURCES, root),
        load_sources(OVERRIDE_SOURCES, root),
        read_rows(root / exceptions_path),
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--exceptions", type=Path, default=DEFAULT_EXCEPTIONS)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    public = read_rows(ROOT / "web/data/public_preview_papers.json")
    rows = repository_audit(public, exceptions_path=args.exceptions)
    narrow_source_rows = [
        *read_rows(ROOT / "web/data/openalex_candidate_map_data.json"),
        *read_rows(ROOT / "data/curated/papers.csv"),
    ]
    narrow_keys = set().union(*(identity_keys(row) for row in narrow_source_rows))
    original_failures = [
        row for public_row, row in zip(public, rows)
        if not (identity_keys(public_row) & narrow_keys)
    ]
    write_audit(ROOT / args.output, original_failures)
    counts = Counter(row["status"] for row in original_failures)
    blockers = sum(not accepted(row) for row in rows)
    print(f"Full-source completeness audit: {dict(sorted(counts.items()))}")
    print(f"Previously missing retained public papers: {len(original_failures)}")
    print(f"Blocking retained public papers across full audit: {blockers}")
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
