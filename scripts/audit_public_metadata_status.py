#!/usr/bin/env python3
"""Audit global versus localized public paper metadata status semantics."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .public_metadata_status import clean, metadata_status, public_status
except ImportError:
    from public_metadata_status import clean, metadata_status, public_status


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPERS = ROOT / "web/data/public_preview_papers.json"
DEFAULT_MAPPINGS = ROOT / "data/curated/author_institution_mappings.csv"
DEFAULT_CSV = ROOT / "docs/public_metadata_status_audit.csv"
DEFAULT_REPORT = ROOT / "docs/public_metadata_status_audit.md"
FIELD_NAMES = (
    "title", "publication_date", "venue", "publication_type",
    "doi", "arxiv", "task_category", "affiliations",
)
UNRESOLVED = {"needs_review", "pending", "pending_review", "unreviewed", "uncertain"}
VERIFIED = {"reviewed", "verified"}
CURATED = {"confirmed", "curated", "approved", "active"}


def truthy(value: Any) -> bool:
    return value is True or clean(value).casefold() in {"1", "true", "yes", "y"}


def normalized(value: Any) -> str:
    return clean(value).casefold().replace("-", "_")


def identity_keys(record: Mapping[str, Any]) -> set[tuple[str, str]]:
    keys = set()
    for field, kind in (
        ("doi", "doi"), ("arxiv_id", "arxiv"),
        ("openalex_url", "openalex"), ("paper_id", "paper_id"),
    ):
        value = clean(record.get(field)).casefold().rstrip("/")
        if not value:
            continue
        if kind == "doi":
            value = value.removeprefix("https://doi.org/")
        elif kind == "arxiv":
            value = value.removeprefix("arxiv:")
        elif kind == "openalex":
            value = value.rsplit("/", 1)[-1]
        keys.add((kind, value))
    title = clean(record.get("title")).casefold()
    if title:
        keys.add(("title", title))
    return keys


def public_paper_id(record: Mapping[str, Any]) -> str:
    explicit = clean(record.get("paper_id") or record.get("id"))
    if explicit:
        return explicit
    doi = clean(record.get("doi"))
    if doi:
        return "doi:" + doi.removeprefix("https://doi.org/")
    arxiv_id = clean(record.get("arxiv_id"))
    if arxiv_id:
        return "arxiv:" + arxiv_id.removeprefix("arXiv:")
    openalex = clean(record.get("openalex_url")).rstrip("/")
    return "openalex:" + openalex.rsplit("/", 1)[-1] if openalex else ""


def matching_evidence(
    record: Mapping[str, Any],
    index: Mapping[tuple[str, str], Sequence[Mapping[str, Any]]],
) -> list[Mapping[str, Any]]:
    result = []
    seen = set()
    for key in identity_keys(record):
        for evidence in index.get(key, ()):
            marker = id(evidence)
            if marker not in seen:
                seen.add(marker)
                result.append(evidence)
    return result


def legacy_overall(
    record: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]]
) -> str:
    """Reconstruct the superseded scope behavior for before/after reporting."""
    base = public_status(
        record.get("review_status"),
        record.get("curation_status"),
        "needs_review" if truthy(record.get("needs_review")) else "",
    )
    local_needs = (
        truthy(record.get("venue_review_required"))
        or clean(record.get("task")).casefold() == "uncertain"
        or clean(record.get("affiliation_review_state")).casefold() == "unreviewed"
        or any(
            truthy(affiliation.get("preliminary"))
            or any(normalized(state) in UNRESOLVED for state in affiliation.get("review_states") or ())
            for affiliation in record.get("affiliations") or ()
            if isinstance(affiliation, Mapping)
        )
        or any(
            clean(item.get("mapping_status")).casefold() == "needs_review"
            and clean(record.get("curation_status")).casefold() == "needs_review"
            and clean(item.get("raw_affiliation"))
            and clean(item.get("provenance_source"))
            for item in evidence
        )
    )
    if local_needs or base == "Needs review":
        return "Needs review"
    if base == "Verified":
        return "Verified"
    if base == "Curated" or clean(record.get("affiliation_review_state")).casefold() in {
        "curated", "reviewed_empty",
    }:
        return "Curated"
    return "Source metadata"


def legacy_unresolved_fields(
    record: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]]
) -> list[str]:
    """Expand the former default/override model for metric comparison."""
    base = public_status(
        record.get("review_status"),
        record.get("curation_status"),
        "needs_review" if truthy(record.get("needs_review")) else "",
    )
    status = {field: base for field in FIELD_NAMES}
    if truthy(record.get("venue_review_required")):
        status["venue"] = "Needs review"
    if clean(record.get("task")).casefold() == "uncertain":
        status["task_category"] = "Needs review"
    affiliation_state = clean(record.get("affiliation_review_state")).casefold()
    affiliation_unresolved = affiliation_state == "unreviewed"
    affiliation_curated = affiliation_state in {"curated", "reviewed_empty"}
    for item in evidence:
        mapping_status = clean(item.get("mapping_status")).casefold()
        supported_pending = (
            mapping_status == "needs_review"
            and clean(record.get("curation_status")).casefold() == "needs_review"
            and clean(item.get("raw_affiliation"))
            and clean(item.get("provenance_source"))
        )
        affiliation_unresolved = affiliation_unresolved or bool(supported_pending)
        affiliation_curated = affiliation_curated or mapping_status == "active"
    for affiliation in record.get("affiliations") or ():
        if not isinstance(affiliation, Mapping):
            continue
        affiliation_unresolved = affiliation_unresolved or truthy(
            affiliation.get("preliminary")
        ) or any(
            normalized(state) in UNRESOLVED
            for state in affiliation.get("review_states") or ()
        )
    if record.get("affiliations") or affiliation_state:
        status["affiliations"] = (
            "Needs review" if affiliation_unresolved
            else "Curated" if affiliation_curated
            else "Source metadata"
        )
    return [
        field for field in FIELD_NAMES
        if field_present(record, field, {
            "field_overrides": {}, "default_field_status": status[field]
        })
        and status[field] == "Needs review"
    ]


def global_reason(record: Mapping[str, Any], overall: str) -> str:
    review = normalized(record.get("review_status"))
    curation = normalized(record.get("curation_status"))
    values = {review, curation} - {""}
    if overall == "Needs review":
        return "; ".join(
            f"{field}={clean(record.get(field))}"
            for field in ("review_status", "curation_status")
            if normalized(record.get(field)) in UNRESOLVED
        )
    if overall == "Verified":
        return "; ".join(
            f"{field}={clean(record.get(field))}"
            for field in ("review_status", "curation_status")
            if normalized(record.get(field)) in VERIFIED
        ) or "recognized completed paper review"
    if overall == "Curated":
        return "; ".join(
            f"{field}={clean(record.get(field))}"
            for field in ("review_status", "curation_status")
            if normalized(record.get(field)) in CURATED
        ) or "recognized accepted paper curation"
    if not values:
        return "no authoritative paper-level review or curation status"
    return "unrecognized paper-level status: " + "; ".join(sorted(values))


def local_reasons(
    record: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]], overall: str
) -> list[str]:
    reasons = []
    if truthy(record.get("venue_review_required")):
        reasons.append("venue_review_required=true")
    if clean(record.get("task")).casefold() == "uncertain":
        reasons.append("task=uncertain")
    state = clean(record.get("affiliation_review_state"))
    if state.casefold() == "unreviewed":
        reasons.append("affiliation_review_state=unreviewed")
    elif state.casefold() in {"curated", "reviewed_empty"}:
        reasons.append(f"affiliation_review_state={state}")
    if truthy(record.get("missing_affiliation")):
        reasons.append("missing_affiliation=true")
    if truthy(record.get("missing_coordinates")):
        reasons.append("missing_coordinates=true")
    for item in evidence:
        if (
            clean(item.get("mapping_status")).casefold() == "needs_review"
            and clean(record.get("curation_status")).casefold() == "needs_review"
            and clean(item.get("raw_affiliation"))
            and clean(item.get("provenance_source"))
        ):
            reasons.append("mapping_status=needs_review (source-backed)")
            break
    preliminary = any(
        truthy(affiliation.get("preliminary"))
        for affiliation in record.get("affiliations") or ()
        if isinstance(affiliation, Mapping)
    )
    if preliminary:
        reasons.append("affiliation.preliminary=true")
    review_states = sorted({
        clean(state)
        for affiliation in record.get("affiliations") or ()
        if isinstance(affiliation, Mapping)
        for state in affiliation.get("review_states") or ()
        if normalized(state) in UNRESOLVED
    })
    if review_states:
        reasons.append("affiliation.review_states=" + "|".join(review_states))
    if truthy(record.get("needs_review")):
        reasons.append(
            "needs_review=true (derived aggregate; not a global paper decision)"
        )
    return list(dict.fromkeys(reasons))


def affiliation_is_locally_unresolved(
    record: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]]
) -> bool:
    if clean(record.get("affiliation_review_state")).casefold() == "unreviewed":
        return True
    if any(
        clean(item.get("mapping_status")).casefold() == "needs_review"
        and clean(record.get("curation_status")).casefold() == "needs_review"
        and clean(item.get("raw_affiliation"))
        and clean(item.get("provenance_source"))
        for item in evidence
    ):
        return True
    if any(
        truthy(affiliation.get("preliminary"))
        or any(
            normalized(state) in UNRESOLVED
            for state in affiliation.get("review_states") or ()
        )
        for affiliation in record.get("affiliations") or ()
        if isinstance(affiliation, Mapping)
    ):
        return True
    return (
        truthy(record.get("needs_review"))
        and public_status(
            record.get("review_status"), record.get("curation_status")
        ) != "Needs review"
        and not truthy(record.get("venue_review_required"))
        and clean(record.get("task")).casefold() != "uncertain"
    )


def field_present(record: Mapping[str, Any], field: str, status: Mapping[str, Any]) -> bool:
    return {
        "title": bool(clean(record.get("title"))),
        "publication_date": bool(clean(record.get("publication_date") or record.get("publication_year") or record.get("year"))),
        "venue": bool(clean(record.get("venue") or record.get("venue_name"))),
        "publication_type": bool(clean(record.get("publication_type"))),
        "doi": bool(clean(record.get("doi"))),
        "arxiv": bool(clean(record.get("arxiv_id"))),
        "task_category": bool(clean(record.get("task")) or record.get("paper_categories")),
        "affiliations": bool(record.get("affiliations")) or field in status.get("field_overrides", {}),
    }[field]


def unresolved_fields(record: Mapping[str, Any], status: Mapping[str, Any]) -> list[str]:
    return [
        field for field in FIELD_NAMES
        if field_present(record, field, status)
        and status.get("field_overrides", {}).get(field, {}).get(
            "status", status["default_field_status"]
        ) == "Needs review"
    ]


def run(papers_path: Path, mappings_path: Path, csv_path: Path, report_path: Path) -> None:
    payload = json.loads(papers_path.read_text(encoding="utf-8"))
    records = payload["records"]
    with mappings_path.open(encoding="utf-8", newline="") as handle:
        mappings = list(csv.DictReader(handle))
    evidence_index: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for mapping in mappings:
        for key in identity_keys(mapping):
            evidence_index[key].append(mapping)

    rows = []
    before = Counter()
    after = Counter()
    before_field_needs = Counter()
    after_field_needs = Counter()
    before_papers_with_field_needs = 0
    papers_with_field_needs = 0
    genuinely_global_before = 0
    localized_affiliations = 0
    for record in records:
        evidence = matching_evidence(record, evidence_index)
        previous = legacy_overall(record, evidence)
        previous_pending_fields = legacy_unresolved_fields(record, evidence)
        corrected = metadata_status(record, evidence)
        corrected_overall = corrected["overall"]
        pending_fields = unresolved_fields(record, corrected)
        before[previous] += 1
        after[corrected_overall] += 1
        if previous_pending_fields:
            before_papers_with_field_needs += 1
            before_field_needs.update(previous_pending_fields)
        if pending_fields:
            papers_with_field_needs += 1
            after_field_needs.update(pending_fields)
        genuinely_global_before += int(public_status(
            record.get("review_status"), record.get("curation_status")
        ) == "Needs review")
        localized_affiliations += int(
            affiliation_is_locally_unresolved(record, evidence)
        )
        local = local_reasons(record, evidence, corrected_overall)
        mapping_statuses = sorted({clean(item.get("mapping_status")) for item in evidence if clean(item.get("mapping_status"))})
        rows.append({
            "paper_id": public_paper_id(record),
            "title": clean(record.get("title")),
            "doi": clean(record.get("doi")),
            "previous_overall": previous,
            "corrected_overall": corrected_overall,
            "overall_changed": str(previous != corrected_overall).lower(),
            "trigger_scope": "local" if previous != corrected_overall else "global",
            "global_reason": global_reason(record, corrected_overall),
            "local_reasons": " | ".join(local),
            "curation_status": clean(record.get("curation_status")),
            "review_status": clean(record.get("review_status")),
            "needs_review": str(truthy(record.get("needs_review"))).lower(),
            "venue_review_required": str(truthy(record.get("venue_review_required"))).lower(),
            "affiliation_review_state": clean(record.get("affiliation_review_state")),
            "mapping_statuses": "|".join(mapping_statuses),
            "field_specific_overrides": json.dumps(corrected.get("field_overrides", {}), ensure_ascii=False, sort_keys=True),
            "unresolved_public_fields": "|".join(pending_fields),
        })

    columns = list(rows[0])
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    changed = sum(row["overall_changed"] == "true" for row in rows)
    previous_needs = [row for row in rows if row["previous_overall"] == "Needs review"]
    local_corrections = sum(
        row["previous_overall"] == "Needs review"
        and row["corrected_overall"] != "Needs review"
        for row in rows
    )
    venue_flags = sum(truthy(record.get("venue_review_required")) for record in records)
    affiliation_flags = sum(
        "affiliations" in unresolved_fields(record, metadata_status(
            record, matching_evidence(record, evidence_index)
        ))
        for record in records
    )
    report = f"""# Public metadata-status global/local audit

Generated from `{papers_path.relative_to(ROOT)}` and authoritative mapping statuses in `{mappings_path.relative_to(ROOT)}`.

## Finding

The previous implementation allowed localized field status to set the paper-wide status and treated the derived `needs_review` aggregate as global. It also allowed curated affiliation state to upgrade a source-only paper. The corrected rule derives `overall` only from paper-level `review_status` and `curation_status`; venue, task/category, affiliation, mapping, and affiliation-provenance review signals remain field-local.

## Counts

| Metric | Before | After |
|---|---:|---:|
| Overall Verified | {before['Verified']} | {after['Verified']} |
| Overall Curated | {before['Curated']} | {after['Curated']} |
| Overall Needs review | {before['Needs review']} | {after['Needs review']} |
| Overall Source metadata | {before['Source metadata']} | {after['Source metadata']} |
| Papers with at least one Needs-review field | {before_papers_with_field_needs} | {papers_with_field_needs} |
| Needs-review venue fields | {before_field_needs['venue']} | {after_field_needs['venue']} |
| Authoritative `venue_review_required=true` | {venue_flags} | {venue_flags} |
| Localized venue issues | {venue_flags} | {venue_flags} |
| Needs-review affiliation fields | {before_field_needs['affiliations']} | {after_field_needs['affiliations']} |
| Localized affiliation issues | {before_field_needs['affiliations']} | {localized_affiliations} |
| Genuinely globally unresolved papers | {genuinely_global_before} | {after['Needs review']} |

- Previous Needs-review papers audited: **{len(previous_needs)}**
- Previous Needs-review papers corrected to a non-global status: **{local_corrections}**
- All papers whose overall label changed, including source-only affiliation upgrades: **{changed}**
- Full per-paper audit: [`public_metadata_status_audit.csv`](public_metadata_status_audit.csv)

## Exact scope rule

1. Normalize paper-level `review_status` and `curation_status` with precedence **Needs review → Verified → Curated → Source metadata**. This is `overall` and `default_field_status`.
2. Apply `venue_review_required` only to Venue, task uncertainty only to Task / category, and affiliation/mapping/provenance review signals only to Institution affiliations.
3. Treat public `needs_review` as a derived aggregate, never as a standalone global decision. When not already explained by a global, venue, or task state, it localizes to affiliation/mapping review because those are the remaining inputs to the export's recomputation.
4. Missing optional metadata creates no field and no downgrade. Unknown internal values provide no confidence and normalize to Source metadata unless a recognized higher-precedence paper-level value is also present.
5. `field_overrides` contains only status/source deviations from `default_field_status`; local fields never change `overall`.
"""
    report_path.write_text(report, encoding="utf-8")
    print(report)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--mappings", type=Path, default=DEFAULT_MAPPINGS)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    run(args.papers, args.mappings, args.csv, args.report)


if __name__ == "__main__":
    main()
