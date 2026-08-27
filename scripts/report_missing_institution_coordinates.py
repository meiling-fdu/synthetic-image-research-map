#!/usr/bin/env python3
"""Audit active institutions without confirmed coordinates by public relevance."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

try:
    from .paper_exclusions import (
        build_active_exclusion_index,
        record_is_excluded,
    )
except ImportError:
    from paper_exclusions import build_active_exclusion_index, record_is_excluded


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"
DEFAULT_CSV = ROOT / "docs" / "missing_institution_coordinates_audit.csv"
DEFAULT_MARKDOWN = ROOT / "docs" / "missing_institution_coordinates_audit.md"
MAPPING_STATUSES = {"active", "needs_review"}
ACTIONABLE_REVIEW_STATUSES = {"pending_review", "ambiguous"}
USABLE_COORDINATE_STATUSES = {"known", "confirmed"}

CSV_COLUMNS = (
    "tier",
    "actionability_class",
    "institution_id",
    "canonical_name",
    "active_mapping_count",
    "affected_paper_ids",
    "affected_papers",
    "public_export_status",
    "registry_status",
    "review_status",
    "location_evidence",
    "queue_reason",
)


class CoordinateAuditError(RuntimeError):
    """An invalid input or invariant violation."""


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def read_csv(path: Path) -> List[Dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except (OSError, UnicodeError, csv.Error) as error:
        raise CoordinateAuditError(f"could not read {path}: {error}") from error


def usable_coordinate_ids(
    locations: Iterable[Mapping[str, str]],
) -> set[str]:
    return {
        clean(row.get("institution_id"))
        for row in locations
        if clean(row.get("institution_id"))
        and clean(row.get("coordinate_status")).casefold()
        in USABLE_COORDINATE_STATUSES
        and clean(row.get("lat"))
        and clean(row.get("lon"))
    }


def review_is_actionable(row: Mapping[str, str]) -> bool:
    return (
        clean(row.get("review_status")).casefold()
        in ACTIONABLE_REVIEW_STATUSES
        and clean(row.get("coordinate_status")).casefold()
        not in USABLE_COORDINATE_STATUSES
    )


def joined(values: Iterable[str]) -> str:
    return " | ".join(dict.fromkeys(value for value in values if value))


def matching_reviews(
    institution_id: str,
    mappings: Sequence[Mapping[str, str]],
    reviews: Sequence[Mapping[str, str]],
) -> List[Mapping[str, str]]:
    paper_ids = {clean(row.get("paper_id")) for row in mappings}
    return [
        row
        for row in reviews
        if clean(row.get("institution_id")) == institution_id
        and (
            not clean(row.get("related_paper_id"))
            or clean(row.get("related_paper_id")) in paper_ids
        )
    ]


def exclusion_reasons(
    mapping: Mapping[str, str],
    exclusion_index: Mapping[str, Sequence[Mapping[str, str]]],
) -> List[str]:
    reasons: List[str] = []
    for excluded_rows in exclusion_index.values():
        for row in excluded_rows:
            if record_is_excluded(mapping, build_active_exclusion_index([row])):
                reason = clean(row.get("reason")) or "active exclusion"
                if reason not in reasons:
                    reasons.append(reason)
    return reasons


def build_audit_rows(
    institutions: Sequence[Mapping[str, str]],
    locations: Sequence[Mapping[str, str]],
    mappings: Sequence[Mapping[str, str]],
    reviews: Sequence[Mapping[str, str]],
    exclusions: Sequence[Mapping[str, str]],
) -> Tuple[List[Dict[str, str]], List[str]]:
    active = {
        clean(row.get("institution_id")): row
        for row in institutions
        if clean(row.get("institution_status")).casefold() == "active"
        and clean(row.get("institution_id"))
    }
    located = usable_coordinate_ids(locations)
    relevant_mappings = [
        row
        for row in mappings
        if clean(row.get("mapping_status")).casefold() in MAPPING_STATUSES
        and clean(row.get("institution_id")) in active
    ]
    exclusion_index = build_active_exclusion_index(exclusions)
    rows: List[Dict[str, str]] = []
    violations: List[str] = []

    for institution_id in sorted(set(active) - located):
        institution = active[institution_id]
        institution_mappings = [
            row
            for row in relevant_mappings
            if clean(row.get("institution_id")) == institution_id
        ]
        public_mappings = [
            row
            for row in institution_mappings
            if not record_is_excluded(row, exclusion_index)
        ]
        relevant_reviews = matching_reviews(
            institution_id,
            public_mappings or institution_mappings,
            reviews,
        )
        actionable = [row for row in relevant_reviews if review_is_actionable(row)]

        if public_mappings:
            tier = "A_public_referenced"
            if actionable:
                actionability = "A_must_be_actionable"
                export_status = "public_relevant_missing_coordinates"
                queue_reason = "Actionable location-review row is persisted."
            else:
                actionability = "C_data_model_inconsistency"
                export_status = "public_relevant_missing_coordinates_unqueued"
                queue_reason = "ERROR: public-relevant missing coordinates are not actionable."
                violations.append(
                    f"{institution_id} {clean(institution.get('canonical_name'))}"
                )
        elif institution_mappings:
            tier = "B_referenced_non_public"
            actionability = "B_explicitly_non_actionable"
            export_status = "excluded_from_public_preview_and_map"
            reasons = joined(
                reason
                for mapping in institution_mappings
                for reason in exclusion_reasons(mapping, exclusion_index)
            )
            queue_reason = f"Durable active paper exclusion: {reasons or 'unspecified'}."
        else:
            tier = "C_dormant_registry_only"
            actionability = "registry_only"
            export_status = "not_referenced_by_active_mapping"
            queue_reason = "No active or needs-review paper mapping references this identity."

        evidence = joined(
            [clean(row.get("raw_affiliation")) for row in institution_mappings]
            + [
                joined(
                    (
                        clean(row.get("suggested_city")),
                        clean(row.get("suggested_country")),
                        clean(row.get("evidence_source")),
                    )
                )
                for row in relevant_reviews
            ]
        )
        rows.append(
            {
                "tier": tier,
                "actionability_class": actionability,
                "institution_id": institution_id,
                "canonical_name": clean(institution.get("canonical_name")),
                "active_mapping_count": str(len(institution_mappings)),
                "affected_paper_ids": joined(
                    clean(row.get("paper_id")) for row in institution_mappings
                ),
                "affected_papers": joined(
                    clean(row.get("title")) for row in institution_mappings
                ),
                "public_export_status": export_status,
                "registry_status": clean(institution.get("institution_status")),
                "review_status": joined(
                    f"{clean(row.get('review_status'))}/"
                    f"{clean(row.get('location_status'))}/"
                    f"{clean(row.get('coordinate_status'))}"
                    for row in relevant_reviews
                ),
                "location_evidence": evidence,
                "queue_reason": queue_reason,
            }
        )
    return rows, violations


def write_csv(path: Path, rows: Sequence[Mapping[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def markdown_table(rows: Sequence[Mapping[str, str]]) -> List[str]:
    lines = [
        "| Institution ID | Institution | Mappings | Public/export status | Review state | Reason |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        values = [
            row["institution_id"], row["canonical_name"], row["active_mapping_count"],
            row["public_export_status"], row["review_status"], row["queue_reason"],
        ]
        lines.append("| " + " | ".join(value.replace("|", "/") for value in values) + " |")
    return lines


def write_markdown(path: Path, rows: Sequence[Mapping[str, str]]) -> None:
    counts = Counter(row["tier"] for row in rows)
    referenced = [row for row in rows if row["active_mapping_count"] != "0"]
    lines = [
        "# Missing institution coordinates audit",
        "",
        "This report distinguishes current public-map completeness from dormant registry completeness.",
        "",
        f"- Tier A - publicly referenced: {counts['A_public_referenced']}",
        f"- Tier B - referenced but non-public: {counts['B_referenced_non_public']}",
        f"- Tier C - dormant registry-only: {counts['C_dormant_registry_only']}",
        f"- Total active registry identities without coordinates: {len(rows)}",
        "",
        "## Referenced identities without coordinates",
        "",
        *markdown_table(referenced),
        "",
        "Tier C identities are retained for registry completeness and are not presented as missing public markers.",
        "",
        "Machine-readable full registry audit: `docs/missing_institution_coordinates_audit.csv`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text("\n".join(lines), encoding="utf-8")
    temporary.replace(path)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    rows, violations = build_audit_rows(
        read_csv(CURATED / "institutions.csv"),
        read_csv(CURATED / "institution_locations.csv"),
        read_csv(CURATED / "author_institution_mappings.csv"),
        read_csv(CURATED / "institution_location_review.csv"),
        read_csv(CURATED / "paper_exclusions.csv"),
    )
    write_csv(args.csv_output, rows)
    write_markdown(args.markdown_output, rows)
    counts = Counter(row["tier"] for row in rows)
    print(
        "Missing institution coordinates: "
        f"Tier A {counts['A_public_referenced']}, "
        f"Tier B {counts['B_referenced_non_public']}, "
        f"Tier C {counts['C_dormant_registry_only']}, total {len(rows)}"
    )
    print(f"Invariant violations: {len(violations)}")
    return 1 if args.check and violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
