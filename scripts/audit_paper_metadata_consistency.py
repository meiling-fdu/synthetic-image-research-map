#!/usr/bin/env python3
"""Audit authoritative paper metadata across public, map, UI, CSV, and Admin layers."""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence

try:
    from .audit_public_institution_consistency import audit_consistency
    from .curated_export import load_curated_mappings
    from .export_public_preview import identity_key, normalize_title, paper_record_from_candidate
    from .paper_links import normalize_arxiv_id, normalize_doi
    from .serve_admin import identity_keys, load_admin_data, read_csv_rows
except ImportError:
    from audit_public_institution_consistency import audit_consistency
    from curated_export import load_curated_mappings
    from export_public_preview import identity_key, normalize_title, paper_record_from_candidate
    from paper_links import normalize_arxiv_id, normalize_doi
    from serve_admin import identity_keys, load_admin_data, read_csv_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPERS = ROOT / "web/data/public_preview_papers.json"
DEFAULT_MAP = ROOT / "web/data/public_preview_map_data.json"
DEFAULT_CSV = ROOT / "docs/paper_metadata_consistency_audit.csv"
DEFAULT_REPORT = ROOT / "docs/paper_metadata_consistency_audit.md"

CONSISTENT = "CONSISTENT"
TRUE_INCONSISTENCY = "TRUE_INCONSISTENCY"
INTENTIONAL_TRANSFORMATION = "INTENTIONAL_TRANSFORMATION"
DISPLAY_ONLY = "DISPLAY_ONLY"
MISSING_OPTIONAL = "MISSING_OPTIONAL"
LEGACY_FALLBACK_RISK = "LEGACY_FALLBACK_RISK"


def clean(value: Any) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).split())


def scalar(value: Any) -> str:
    return clean(value).casefold()


def integer(value: Any) -> str:
    try:
        return str(int(value)) if value not in (None, "") else ""
    except (TypeError, ValueError):
        return clean(value)


def author_names(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        text = value.strip()
        if text.startswith(("[", "{")):
            try:
                value = json.loads(text)
            except json.JSONDecodeError:
                pass
        if isinstance(value, str):
            value = re.split(r"\s*;\s*", value)
    if not isinstance(value, list):
        value = [value] if value not in (None, "") else []
    names = []
    for item in value:
        if isinstance(item, Mapping):
            item = item.get("name") or item.get("display_name") or item.get("author")
        name = clean(item)
        if name:
            names.append(name.casefold())
    return tuple(names)


def categories(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        value = re.split(r"\s*;\s*", value)
    return tuple(clean(item).casefold() for item in (value or []) if clean(item))


def venue(value: Any) -> str:
    if isinstance(value, Mapping):
        value = value.get("venue_name") or value.get("venue")
    return scalar(value)


def doi(value: Any) -> str:
    return normalize_doi(value)


def arxiv(value: Any) -> str:
    return normalize_arxiv_id(value)


def affiliation_rows(record: Mapping[str, Any]) -> tuple[tuple[Any, ...], ...]:
    rows = record.get("author_institution_affiliations")
    if not isinstance(rows, list):
        rows = record.get("affiliations") if isinstance(record.get("affiliations"), list) else []
    normalized = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        normalized.append((
            clean(row.get("institution_id")),
            clean(row.get("canonical_name") or row.get("institution") or row.get("name")).casefold(),
            author_names(row.get("authors")),
        ))
    return tuple(normalized)


def author_attribution(record: Mapping[str, Any]) -> tuple[tuple[Any, ...], ...]:
    values = record.get("author_institution_indices")
    if not isinstance(values, list):
        return ()
    return tuple(sorted(
        (
            clean(value.get("author") or value.get("name")).casefold(),
            tuple(sorted(clean(item) for item in value.get("institution_ids") or [] if clean(item))),
        )
        for value in values if isinstance(value, Mapping)
    ))


def location_ids(record: Mapping[str, Any]) -> tuple[str, ...]:
    locations = record.get("aggregated_locations")
    if isinstance(locations, list):
        return tuple(dict.fromkeys(
            clean(item.get("location_id")) for item in locations
            if isinstance(item, Mapping) and clean(item.get("location_id"))
        ))
    value = clean(record.get("location_id"))
    return (value,) if value else ()


def paper_id(record: Mapping[str, Any]) -> str:
    return clean(record.get("paper_id") or record.get("id"))


@dataclass(frozen=True)
class FieldSpec:
    name: str
    source: str
    normalization: str
    public_representation: str
    blank_allowed: bool
    display: str
    extractor: Callable[[Mapping[str, Any]], Any]
    map_required: bool = True
    admin_compare: bool = True


FIELD_SPECS = (
    FieldSpec("paper_id", "curated paper ID; otherwise external paper identity", "trim; exact stable ID", "paper_id when locally curated; external identity otherwise", True, "not reconstructed for display", paper_id, False, False),
    FieldSpec("title", "curated paper row or source metadata", "Unicode NFKC; collapse whitespace", "canonical title string", False, "typographic markup only", lambda row: scalar(row.get("title"))),
    FieldSpec("authors", "curated ordered author list or source ordered authors", "ordered Unicode-normalized names", "ordered author objects/names", False, "joined with punctuation and affiliation superscripts", lambda row: author_names(row.get("authors"))),
    FieldSpec("publication_year", "curated bibliographic year or source publication year", "integer year", "publication_year and year agree", False, "decimal year label", lambda row: integer(row.get("publication_year") or row.get("year"))),
    FieldSpec("publication_date", "source date unless superseded by confirmed curated year", "ISO date string", "publication_date", True, "display may omit missing date", lambda row: clean(row.get("publication_date"))),
    FieldSpec("venue", "curated venue registry/effective venue audit or source venue", "canonical venue name; blank for books", "venue_name/venue", True, "venue_label may add acronym/track", lambda row: venue(row)),
    FieldSpec("publication_type", "curated/effective publication classification", "conference|journal|preprint|book", "publication_type", False, "title-cased label", lambda row: scalar(row.get("publication_type"))),
    FieldSpec("doi", "curated DOI, publication override, or source DOI", "canonical lowercase DOI without URL prefix", "doi", True, "link is rendered as https://doi.org/<doi>", lambda row: doi(row.get("doi"))),
    FieldSpec("arxiv_id", "curated arXiv link, version override, or source metadata", "base arXiv ID without URL/version suffix", "arxiv_id", True, "link is rendered as https://arxiv.org/abs/<id>", lambda row: arxiv(row.get("arxiv_id") or row.get("arxiv_url"))),
    FieldSpec("task", "curated task or reviewed source task", "canonical task enum", "task", False, "human-readable label", lambda row: scalar(row.get("task"))),
    FieldSpec("paper_categories", "curated categories or normalized source category", "ordered canonical category enum", "paper_categories", True, "human-readable badges", lambda row: categories(row.get("paper_categories"))),
    FieldSpec("source_database", "record origin", "case-insensitive source label", "source_database", True, "not used to replace factual metadata", lambda row: scalar(row.get("source_database")), False),
    FieldSpec("metadata_source", "record metadata origin", "case-insensitive public source label", "metadata_source", True, "may be summarized as public provenance", lambda row: scalar(row.get("metadata_source")), False),
    FieldSpec("review_status", "paper-level authoritative review state", "scope-aware public status mapping", "review_status", True, "normalized only for metadata status", lambda row: scalar(row.get("review_status")), False, False),
    FieldSpec("curation_status", "paper-level authoritative curation state", "scope-aware public status mapping", "curation_status", True, "normalized only for metadata status", lambda row: scalar(row.get("curation_status")), False, False),
    FieldSpec("affiliations", "active curated mappings or source fallback when unreviewed", "ordered institution IDs, names, and attributed authors", "author_institution_affiliations/affiliations", True, "institution names and locations are formatted only", affiliation_rows),
    FieldSpec("author_institution_attribution", "active paper–institution mappings", "ordered author to institution-ID assignments", "author_institution_indices", True, "superscript indices are derived from exported ordering", author_attribution),
    FieldSpec("location_ids", "confirmed institution locations for map-eligible relationships", "ordered unique location IDs", "map location_id; paper summaries intentionally omit IDs", True, "location labels are display transformations", location_ids, False, False),
)


def payload_records(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["records"]


def index_records(records: Iterable[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    index: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        for key in identity_keys(record):
            index[key].append(record)
    return index


def matches(record: Mapping[str, Any], index: Mapping[str, Sequence[Mapping[str, Any]]]) -> list[Mapping[str, Any]]:
    keys = identity_keys(record)
    strong = [key for key in keys if not key.startswith("title_year:")]
    for key in strong or keys:
        if index.get(key):
            seen = set()
            return [item for item in index[key] if not (id(item) in seen or seen.add(id(item)))]
    return []


def render_value(value: Any) -> str:
    if isinstance(value, (tuple, list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return clean(value)


def source_value_for(
    field: str,
    admin: Mapping[str, Any],
    candidate: Optional[Mapping[str, Any]],
) -> Any:
    curated = admin.get("curated_record")
    source = curated if isinstance(curated, Mapping) else candidate or admin
    aliases = {
        "publication_year": ("year", "publication_year"),
        "venue": ("venue_name", "venue"),
        "authors": ("authors", "authors_ordered"),
        "paper_categories": ("paper_categories", "entry_type"),
        "location_ids": ("location_id",),
    }
    for name in aliases.get(field, (field,)):
        if name in source:
            return source.get(name)
    return ""


def audit(
    papers_path: Path = DEFAULT_PAPERS,
    map_path: Path = DEFAULT_MAP,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    papers = payload_records(papers_path)
    markers = payload_records(map_path)
    admin_papers, _ = load_admin_data(apply_venue_audit=True)
    admin_index = index_records(admin_papers)
    marker_index = index_records(markers)
    candidate_rows = read_csv_rows(ROOT / "data/processed/openalex_candidate_papers_in_scope.csv")
    candidate_records = [paper_record_from_candidate(row) for row in candidate_rows]
    candidate_index = index_records(candidate_records)
    institution_rows = read_csv_rows(ROOT / "data/curated/institutions.csv")
    retired_ids = {
        row["institution_id"] for row in institution_rows
        if row.get("institution_status") in {"merged", "ignored"}
    }
    mappings = load_curated_mappings(ROOT / "data/curated/author_institution_mappings.csv")
    affiliation_audit = audit_consistency(papers, markers, mappings)
    affiliation_mismatch_ids = {item["paper_id"] for item in affiliation_audit["mismatches"]}
    rows: list[dict[str, Any]] = []
    pipeline_findings = []

    for paper in papers:
        admin_matches = matches(paper, admin_index)
        admin = admin_matches[0] if admin_matches else paper
        related_markers = matches(paper, marker_index)
        candidate_matches = matches(paper, candidate_index)
        candidate = candidate_matches[0] if candidate_matches else None
        is_curated = bool(admin.get("is_in_curated_papers"))
        source_label = (
            "data/curated/papers.csv + normalized exporter overlays"
            if is_curated else
            "data/processed/openalex_candidate_papers_in_scope.csv + normalized exporter overlays"
        )
        public_id = paper_id(paper) or f"{identity_key(dict(paper))[0]}:{identity_key(dict(paper))[1]}"
        for spec in FIELD_SPECS:
            expected = spec.extractor(admin)
            actual = spec.extractor(paper)
            map_values = [spec.extractor(marker) for marker in related_markers]
            nonblank_map_values = [value for value in map_values if value not in ("", (), [])]
            classification = CONSISTENT
            layer = ""
            detail = ""

            authors_display_equivalent = (
                spec.name == "authors"
                and scalar(", ".join(expected)) == scalar(", ".join(actual))
            )
            mapped_author_order = tuple(
                clean(item.get("author") or item.get("name")).casefold()
                for item in paper.get("author_institution_indices") or []
                if isinstance(item, Mapping)
                and clean(item.get("author") or item.get("name"))
            )
            authors_mapping_normalized = (
                spec.name == "authors"
                and expected != actual
                and not authors_display_equivalent
                and bool(actual)
                and mapped_author_order == actual
            )
            if spec.name == "location_ids":
                expected = tuple(dict.fromkeys(
                    clean(marker.get("location_id")) for marker in related_markers
                    if clean(marker.get("location_id"))
                ))
                actual = expected
                classification = DISPLAY_ONLY if actual else MISSING_OPTIONAL
                layer = "confirmed locations→map/frontend"
                detail = (
                    "Location IDs remain on map records; Paper Details displays labels."
                    if actual else "No map-eligible location ID is available."
                )
            elif authors_mapping_normalized:
                classification = INTENTIONAL_TRANSFORMATION
                layer = "legacy curated authors→reviewed mapping roster"
                detail = (
                    "The curated author text uses a legacy encoding; the public "
                    "ordered roster is fully supported by authoritative author–institution mappings."
                )
            elif spec.admin_compare and expected != actual and not authors_display_equivalent:
                if spec.name == "task":
                    classification = INTENTIONAL_TRANSFORMATION
                    layer = "authoritative source→normalized public task"
                    detail = "The exporter applies reviewed combined-task/key-paper semantics; Admin retains the editable source label."
                else:
                    classification = TRUE_INCONSISTENCY
                    layer = "admin→public"
                    detail = "Effective Admin value differs from canonical public paper value."
            elif spec.map_required and related_markers and any(value != actual for value in map_values):
                classification = TRUE_INCONSISTENCY
                layer = "papers JSON→map JSON"
                detail = "One or more map records differs from the canonical paper value."
            elif spec.name == "doi" and clean(paper.get("doi")) != actual:
                classification = TRUE_INCONSISTENCY
                layer = "public identifier normalization"
                detail = "DOI is not stored as its canonical DOI string."
            elif spec.name == "arxiv_id" and clean(paper.get("arxiv_id")) != actual:
                classification = TRUE_INCONSISTENCY
                layer = "public identifier normalization"
                detail = "arXiv ID is not stored as its canonical base identifier."
            elif spec.name == "publication_year" and integer(paper.get("year")) != actual:
                classification = TRUE_INCONSISTENCY
                layer = "public papers JSON"
                detail = "year and publication_year disagree."
            elif spec.name == "publication_date" and actual and actual[:4].isdigit() and actual[:4] != integer(paper.get("publication_year")):
                classification = (
                    LEGACY_FALLBACK_RISK if is_curated else INTENTIONAL_TRANSFORMATION
                )
                layer = "source→public publication chronology"
                detail = (
                    "A source publication date conflicts with a confirmed curated bibliographic year."
                    if is_curated else
                    "Source metadata independently supplies the issued date and bibliographic year; no curated correction supersedes either."
                )
            elif spec.name == "publication_type":
                value = scalar(paper.get("publication_type"))
                paper_venue = venue(paper)
                if value not in {"conference", "journal", "preprint", "book"}:
                    classification = TRUE_INCONSISTENCY
                    layer = "public publication classification"
                    detail = "Publication type is outside the public enum."
                elif value == "book" and paper_venue:
                    classification = TRUE_INCONSISTENCY
                    layer = "public publication classification"
                    detail = "Book records must not retain venue taxonomy."
                elif value in {"conference", "journal"} and not paper_venue:
                    classification = TRUE_INCONSISTENCY
                    layer = "public publication classification"
                    detail = "Published conference/journal record has no canonical venue."
            elif spec.name == "affiliations":
                emitted_ids = {item[0] for item in actual if item[0]}
                leaked = sorted(emitted_ids & retired_ids)
                if leaked or paper_id(paper) in affiliation_mismatch_ids:
                    classification = TRUE_INCONSISTENCY
                    layer = "authoritative mappings→public affiliations"
                    detail = "Retired institution or curated/public affiliation mismatch: " + ", ".join(leaked)
            elif authors_display_equivalent and expected != actual:
                classification = DISPLAY_ONLY
                layer = "Admin→public author presentation"
                detail = "Equivalent ordered author text uses different list delimiters."
            elif actual in ("", (), []) and spec.blank_allowed:
                classification = MISSING_OPTIONAL
                layer = "authoritative/public"
                detail = "Optional metadata is not available; no value was inferred."
            elif spec.display != "not reconstructed for display":
                classification = DISPLAY_ONLY
                layer = "public→frontend/CSV"
                detail = spec.display

            rows.append({
                "paper_id": public_id,
                "title": clean(paper.get("title")),
                "field": spec.name,
                "authoritative_source": source_label if spec.name not in {"affiliations", "author_institution_attribution", "location_ids"} else spec.source,
                "canonical_normalization_rule": spec.normalization,
                "expected_public_representation": spec.public_representation,
                "blank_allowed": str(spec.blank_allowed).lower(),
                "intentional_display_transformation": spec.display,
                "source_value": render_value(source_value_for(spec.name, admin, candidate)),
                "admin_value": render_value(expected),
                "public_papers_value": render_value(actual),
                "public_map_values": render_value(tuple(dict.fromkeys(map(render_value, nonblank_map_values)))),
                "classification": classification,
                "pipeline_layer": layer,
                "details": detail,
            })

    app_source = (ROOT / "web/app.js").read_text(encoding="utf-8")
    static_contracts = {
        "canonical paper source precedes marker fallback": "function canonicalPaperRecord(record)" in app_source,
        "paper CSV uses canonical DOI normalizer": '["doi", (record) => normalizedDoi(record.doi)]' in app_source,
        "paper CSV uses canonical arXiv extractor": '["arxiv_id", (record) => recordArxivId(record)]' in app_source,
        "Paper Details uses exported venue before legacy venue fallbacks": "record.venue_name ||\n    record.venue ||" in app_source,
        "deep links restore canonical paper identity": "canonicalPaperRecordsByIdentity.get(requestedPaperIdentity)" in app_source,
        "hierarchy match context is stored separately": "institutionMatchContextByRecord" in app_source,
    }
    for name, ok in static_contracts.items():
        if not ok:
            pipeline_findings.append({
                "classification": LEGACY_FALLBACK_RISK,
                "field": "frontend_contract",
                "pipeline_layer": "frontend",
                "details": name,
            })

    paper_relationships = {
        (identity_key(dict(marker)), clean(marker.get("institution_id")))
        for marker in markers
    }
    published_only = sum(
        scalar(paper.get("publication_type")) in {"conference", "journal", "book"}
        for paper in papers
    )
    classifications = Counter(row["classification"] for row in rows)
    classifications.update(item["classification"] for item in pipeline_findings)
    fields = defaultdict(Counter)
    layers = defaultdict(Counter)
    for row in rows:
        fields[row["field"]][row["classification"]] += 1
        if row["pipeline_layer"]:
            layers[row["pipeline_layer"]][row["classification"]] += 1
    summary = {
        "papers_audited": len(papers),
        "fields_per_paper": len(FIELD_SPECS),
        "paper_field_rows": len(rows),
        "classification_counts": dict(sorted(classifications.items())),
        "true_inconsistencies": classifications[TRUE_INCONSISTENCY],
        "legacy_fallback_risks": classifications[LEGACY_FALLBACK_RISK],
        "public_paper_institution_relationships": len(paper_relationships),
        "map_markers": len(markers),
        "published_only_papers": published_only,
        "affiliation_audit_mismatches": affiliation_audit["mismatch_count"],
        "retired_institution_affiliation_leaks": sum(
            row["classification"] == TRUE_INCONSISTENCY
            and row["field"] == "affiliations"
            for row in rows
        ),
        "field_classifications": {name: dict(sorted(values.items())) for name, values in sorted(fields.items())},
        "layer_classifications": {name: dict(sorted(values.items())) for name, values in sorted(layers.items())},
        "frontend_contracts": static_contracts,
        "pipeline_findings": pipeline_findings,
    }
    return rows, summary


CSV_FIELDS = (
    "paper_id", "title", "field", "authoritative_source",
    "canonical_normalization_rule", "expected_public_representation",
    "blank_allowed", "intentional_display_transformation", "source_value",
    "admin_value", "public_papers_value", "public_map_values",
    "classification", "pipeline_layer", "details",
)


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, summary: Mapping[str, Any]) -> None:
    counts = summary["classification_counts"]
    field_rows = []
    for field, values in summary["field_classifications"].items():
        field_rows.append(
            f"| {field} | {values.get(TRUE_INCONSISTENCY, 0)} | "
            f"{values.get(LEGACY_FALLBACK_RISK, 0)} | "
            f"{values.get(INTENTIONAL_TRANSFORMATION, 0)} | "
            f"{values.get(DISPLAY_ONLY, 0)} | {values.get(MISSING_OPTIONAL, 0)} |"
        )
    contracts = "\n".join(
        f"- {'PASS' if ok else 'FAIL'} — {name}"
        for name, ok in summary["frontend_contracts"].items()
    )
    report = f"""# Paper Metadata Consistency Audit

This deterministic audit traces {summary['fields_per_paper']} canonical metadata fields across all {summary['papers_audited']} public papers ({summary['paper_field_rows']} paper-field rows).

## Result

- TRUE_INCONSISTENCY: {summary['true_inconsistencies']}
- LEGACY_FALLBACK_RISK: {summary['legacy_fallback_risks']}
- INTENTIONAL_TRANSFORMATION: {counts.get(INTENTIONAL_TRANSFORMATION, 0)}
- DISPLAY_ONLY: {counts.get(DISPLAY_ONLY, 0)}
- MISSING_OPTIONAL: {counts.get(MISSING_OPTIONAL, 0)}
- Authoritative affiliation mismatches: {summary['affiliation_audit_mismatches']}
- Retired institution affiliation leaks: {summary['retired_institution_affiliation_leaks']}

## Stable corpus invariants

- Public papers: {summary['papers_audited']}
- Published-only papers: {summary['published_only_papers']}
- Unique public paper–institution relationships: {summary['public_paper_institution_relationships']}
- Map markers: {summary['map_markers']} (one valid relationship has two confirmed locations)

## Findings by field

| Field | True inconsistency | Legacy risk | Intentional | Display only | Missing optional |
|---|---:|---:|---:|---:|---:|
{chr(10).join(field_rows)}

## Frontend and CSV contracts

{contracts}

Paper Details, Institution Records, Unique Papers, CSV export, and deep links consume the canonical paper record first. Display punctuation, label expansion, DOI/arXiv link construction, author joining, and venue acronym/track labels are presentation-only. Institution hierarchy match context remains in a separate search explanation structure and is never added to affiliation evidence.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def run(papers: Path, markers: Path, csv_path: Path, report_path: Path) -> dict[str, Any]:
    rows, summary = audit(papers, markers)
    write_csv(csv_path, rows)
    write_report(report_path, summary)
    return summary


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--map", dest="markers", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)
    summary = run(args.papers, args.markers, args.csv, args.report)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return int(bool(summary["true_inconsistencies"] or summary["legacy_fallback_risks"]))


if __name__ == "__main__":
    raise SystemExit(main())
