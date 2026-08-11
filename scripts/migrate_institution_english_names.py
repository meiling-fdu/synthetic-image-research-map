#!/usr/bin/env python3
"""Audit and migrate approved English institution display names by immutable ID."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from .curated_institutions import alias_id_for, clean, normalize_institution
    from .curated_schema import CURATED_DATA_DIR, REPOSITORY_ROOT
    from .name_matching import canonical_name_key
except ImportError:
    from curated_institutions import alias_id_for, clean, normalize_institution
    from curated_schema import CURATED_DATA_DIR, REPOSITORY_ROOT
    from name_matching import canonical_name_key


OVERRIDES_PATH = REPOSITORY_ROOT / "data" / "manual" / "institution_english_name_overrides.csv"
AUDIT_PATH = REPOSITORY_ROOT / "data" / "processed" / "institution_english_name_audit.csv"
SUMMARY_PATH = REPOSITORY_ROOT / "data" / "processed" / "institution_english_name_migration_summary.json"

OVERRIDE_COLUMNS = (
    "institution_id", "english_canonical_name", "local_name_alias",
    "evidence", "status", "notes",
)
AUDIT_COLUMNS = (
    "institution_id", "current_canonical_name", "proposed_english_name",
    "country", "city", "institution_type", "existing_aliases",
    "source_or_evidence", "decision", "decision_reason",
    "affected_paper_count", "affected_relationship_count",
    "collision_status", "review_required",
)

LOCAL_TERM_PATTERN = re.compile(
    r"\b(?:universidad|universidade|università|universita|université|"
    r"universität|universiti|universitatea|universiteit|technische|"
    r"école|ecole|instituto|centre national|fondazione|hochschule)\b",
    re.IGNORECASE,
)
NON_LATIN_PATTERN = re.compile(
    "[\u0370-\u052f\u0590-\u06ff\u0900-\u097f\u0e00-\u0e7f"
    "\u3040-\u30ff\u3130-\u318f\u4e00-\u9fff\uac00-\ud7af]"
)

TABLES: dict[str, tuple[str, ...]] = {
    "institutions.csv": ("canonical_name",),
    "institution_aliases.csv": ("canonical_institution_name",),
    "author_institution_mappings.csv": ("institution",),
    "institution_locations.csv": ("institution",),
    "institution_location_review.csv": (
        "canonical_institution_name", "matched_institution",
        "suggested_canonical_institution",
    ),
    "institution_review_queue.csv": (
        "current_institution", "suggested_canonical_institution",
    ),
}


class MigrationError(RuntimeError):
    pass


def read_csv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return tuple(reader.fieldnames or ()), [dict(row) for row in reader]


def write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def normalized_key(value: Any) -> str:
    return canonical_name_key(clean(value))


def unique_names(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        name = clean(value)
        key = normalize_institution(name)
        if name and key and key not in seen:
            seen.add(key)
            result.append(name)
    return result


def load_overrides(path: Path) -> dict[str, dict[str, str]]:
    columns, rows = read_csv(path)
    if columns != OVERRIDE_COLUMNS:
        raise MigrationError(f"{path} has an unexpected header")
    result: dict[str, dict[str, str]] = {}
    for line, row in enumerate(rows, 2):
        institution_id = clean(row.get("institution_id"))
        status = clean(row.get("status")).casefold()
        name = clean(row.get("english_canonical_name"))
        if not institution_id or institution_id in result:
            raise MigrationError(f"{path}:{line}: missing or duplicate institution_id")
        if status not in {"approved", "keep", "review"}:
            raise MigrationError(f"{path}:{line}: unsupported status {status!r}")
        if status in {"approved", "keep"} and not name:
            raise MigrationError(f"{path}:{line}: {status} row requires a name")
        result[institution_id] = {**row, "status": status}
    return result


def load_tables(curated_dir: Path) -> dict[str, dict[str, Any]]:
    tables: dict[str, dict[str, Any]] = {}
    for filename in TABLES:
        path = curated_dir / filename
        if path.exists():
            columns, rows = read_csv(path)
            tables[filename] = {"path": path, "columns": columns, "rows": rows}
    return tables


def active_institutions(tables: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    return [
        row for row in tables["institutions.csv"]["rows"]
        if clean(row.get("institution_status")) == "active"
    ]


def candidate_signals(name: str, aliases: Sequence[str]) -> list[str]:
    signals: list[str] = []
    if NON_LATIN_PATTERN.search(name):
        signals.append("non_latin_script")
    if any(ord(character) > 127 for character in name):
        signals.append("non_ascii")
    if LOCAL_TERM_PATTERN.search(name):
        signals.append("local_language_term")
    if any(
        alias and normalized_key(alias) != normalized_key(name)
        and re.search(r"\b(?:university|institute|centre|center)\b", alias, re.I)
        for alias in aliases
    ):
        signals.append("different_english_alias")
    return signals


def locations_by_id(tables: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, str]]:
    return {
        clean(row.get("institution_id")): row
        for row in tables.get("institution_locations.csv", {}).get("rows", [])
        if clean(row.get("institution_id"))
    }


def aliases_by_id(tables: Mapping[str, Mapping[str, Any]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in tables.get("institution_aliases.csv", {}).get("rows", []):
        grouped[clean(row.get("institution_id"))].append(clean(row.get("alias_name")))
    return grouped


def mappings_by_id(tables: Mapping[str, Mapping[str, Any]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tables.get("author_institution_mappings.csv", {}).get("rows", []):
        if clean(row.get("mapping_status")) == "active":
            grouped[clean(row.get("institution_id"))].append(row)
    return grouped


def collision_for(
    institution_id: str,
    proposed_name: str,
    institutions: Sequence[Mapping[str, str]],
    locations: Mapping[str, Mapping[str, str]],
) -> tuple[str, list[str]]:
    key = normalized_key(proposed_name)
    matches = [
        row for row in institutions
        if clean(row.get("institution_id")) != institution_id
        and normalized_key(row.get("canonical_name")) == key
    ]
    if not matches:
        return "none", []
    country = clean(locations.get(institution_id, {}).get("country"))
    countries = {
        clean(locations.get(clean(row.get("institution_id")), {}).get("country"))
        for row in matches
    }
    status = (
        "same_country_same_name"
        if country and countries == {country}
        else "cross_country_same_name"
        if country and any(other and other != country for other in countries)
        else "existing_canonical_collision"
    )
    return status, [clean(row.get("institution_id")) for row in matches]


def build_audit(
    tables: Mapping[str, Mapping[str, Any]],
    overrides: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    institutions = active_institutions(tables)
    by_id = {clean(row.get("institution_id")): row for row in institutions}
    unknown = sorted(set(overrides) - set(by_id))
    if unknown:
        raise MigrationError(f"override IDs do not exist as active institutions: {', '.join(unknown)}")
    aliases = aliases_by_id(tables)
    locations = locations_by_id(tables)
    mappings = mappings_by_id(tables)
    audit: list[dict[str, str]] = []
    for institution in institutions:
        institution_id = clean(institution.get("institution_id"))
        current = clean(institution.get("canonical_name"))
        override = overrides.get(institution_id, {})
        status = clean(override.get("status")) or ""
        override_name = clean(override.get("english_canonical_name"))
        proposed = (
            override_name
            if status == "approved"
            or (status == "review" and override_name != current)
            else ""
        )
        recorded_current = (
            clean(override.get("local_name_alias"))
            if status == "approved" and current == proposed
            else current
        )
        signals = candidate_signals(current, aliases.get(institution_id, []))
        if status == "approved":
            decision = "rename"
            reason = clean(override.get("notes")) or "Approved English canonical-name override."
        elif status == "keep":
            decision = "keep"
            reason = clean(override.get("notes")) or "Official international name retained."
        elif status == "review":
            decision = "review"
            reason = clean(override.get("notes")) or "Manual evidence review required."
        elif signals:
            decision = "review"
            reason = "Candidate signals: " + ", ".join(signals)
        else:
            decision = "keep"
            reason = "No local-language or alias-promotion candidate signal."
        target = proposed or current
        collision, collision_ids = collision_for(
            institution_id, target, institutions, locations
        )
        if collision_ids:
            reason += f" Same-name canonical IDs: {', '.join(collision_ids)}."
        relationship_rows = mappings.get(institution_id, [])
        audit.append({
            "institution_id": institution_id,
            "current_canonical_name": recorded_current,
            "proposed_english_name": proposed,
            "country": clean(locations.get(institution_id, {}).get("country")),
            "city": clean(locations.get(institution_id, {}).get("city")),
            "institution_type": clean(institution.get("institution_type")),
            "existing_aliases": "; ".join(unique_names(aliases.get(institution_id, []))),
            "source_or_evidence": clean(override.get("evidence")),
            "decision": decision,
            "decision_reason": reason,
            "affected_paper_count": str(len({
                clean(row.get("paper_id")) for row in relationship_rows
                if clean(row.get("paper_id"))
            })),
            "affected_relationship_count": str(len(relationship_rows)),
            "collision_status": collision,
            "review_required": "true" if decision == "review" else "false",
        })
    return sorted(
        audit,
        key=lambda row: (
            {"rename": 0, "review": 1, "keep": 2}[row["decision"]],
            row["country"], row["current_canonical_name"], row["institution_id"],
        ),
    )


def identity_snapshot(
    tables: Mapping[str, Mapping[str, Any]],
    curated_dir: Path = CURATED_DATA_DIR,
) -> dict[str, Any]:
    institutions = tables["institutions.csv"]["rows"]
    mappings = tables["author_institution_mappings.csv"]["rows"]
    locations = tables["institution_locations.csv"]["rows"]
    snapshot = {
        "institution_ids": sorted(clean(row.get("institution_id")) for row in institutions),
        "institution_count": len(institutions),
        "institution_identity": sorted((
            clean(row.get("institution_id")),
            clean(row.get("institution_type")),
            clean(row.get("institution_status")),
            clean(row.get("parent_institution_id")),
            clean(row.get("public_display")),
        ) for row in institutions),
        "mapping_count": len(mappings),
        "mapping_identity": sorted((
            clean(row.get("mapping_id")), clean(row.get("paper_id")),
            clean(row.get("institution_id")), clean(row.get("institution_authors")),
            clean(row.get("author_order")), clean(row.get("mapping_status")),
            clean(row.get("doi")), clean(row.get("openalex_url")),
        ) for row in mappings),
        "location_identity": sorted((
            clean(row.get("location_id")), clean(row.get("institution_id")),
            clean(row.get("city")), clean(row.get("region")), clean(row.get("country")),
            clean(row.get("country_code")), clean(row.get("lat")), clean(row.get("lon")),
            clean(row.get("coordinate_status")),
        ) for row in locations),
    }
    hierarchy_path = curated_dir / "institution_hierarchy.csv"
    if hierarchy_path.exists():
        _, hierarchy = read_csv(hierarchy_path)
        snapshot["hierarchy"] = sorted(tuple(row.items()) for row in hierarchy)
    papers_path = curated_dir / "papers.csv"
    if papers_path.exists():
        _, papers = read_csv(papers_path)
        snapshot["papers"] = sorted((
            clean(row.get("paper_id")), clean(row.get("title")), clean(row.get("authors")),
            clean(row.get("doi")), clean(row.get("arxiv_id")),
            clean(row.get("openalex_url")), clean(row.get("task")),
            clean(row.get("publication_type")), clean(row.get("venue_id")),
        ) for row in papers)
    return snapshot


def add_previous_alias(
    aliases: list[dict[str, str]],
    columns: Sequence[str],
    institution_id: str,
    old_name: str,
    new_name: str,
) -> bool:
    old_key = normalize_institution(old_name)
    for row in aliases:
        if (
            clean(row.get("institution_id")) == institution_id
            and normalize_institution(row.get("alias_name")) == old_key
        ):
            row["canonical_institution_name"] = new_name
            return False
    alias_id = alias_id_for(old_name)
    conflicting = [
        row for row in aliases
        if clean(row.get("alias_id")) == alias_id
        and clean(row.get("institution_id")) != institution_id
    ]
    if conflicting:
        raise MigrationError(f"alias ID collision for {old_name!r}")
    new_row = {column: "" for column in columns}
    new_row.update({
        "alias_id": alias_id,
        "alias_name": old_name,
        "institution_id": institution_id,
        "canonical_institution_name": new_name,
        "alias_language": "",
        "alias_source": "english-name-migration",
        "review_status": "confirmed",
        "notes": "Previous canonical name retained by English display-name migration.",
    })
    aliases.append(new_row)
    return True


def apply_approved(
    tables: dict[str, dict[str, Any]],
    audit: Sequence[Mapping[str, str]],
) -> tuple[int, int]:
    approved = {
        row["institution_id"]: row
        for row in audit
        if row["decision"] == "rename" and row["proposed_english_name"]
    }
    unsafe = [
        row for row in approved.values()
        if row["collision_status"] != "none"
    ]
    if unsafe:
        raise MigrationError(
            "unsafe approved canonical collision(s): "
            + ", ".join(row["institution_id"] for row in unsafe)
        )
    institutions = tables["institutions.csv"]["rows"]
    aliases_table = tables["institution_aliases.csv"]
    aliases = aliases_table["rows"]
    aliases_added = 0
    renames = 0
    old_by_id: dict[str, str] = {}
    for row in institutions:
        institution_id = clean(row.get("institution_id"))
        proposal = approved.get(institution_id)
        if not proposal:
            continue
        old_name = clean(row.get("canonical_name"))
        new_name = clean(proposal.get("proposed_english_name"))
        if old_name == new_name:
            continue
        old_by_id[institution_id] = old_name
        row["canonical_name"] = new_name
        aliases_added += int(add_previous_alias(
            aliases, aliases_table["columns"], institution_id, old_name, new_name
        ))
        renames += 1
    for filename, fields in TABLES.items():
        if filename == "institutions.csv" or filename not in tables:
            continue
        for row in tables[filename]["rows"]:
            institution_ids = {
                clean(row.get("institution_id")),
                clean(row.get("current_institution_id")),
                clean(row.get("suggested_institution_id")),
            }
            matching_ids = institution_ids & set(approved)
            if len(matching_ids) != 1:
                continue
            institution_id = next(iter(matching_ids))
            new_name = clean(approved[institution_id]["proposed_english_name"])
            old_name = old_by_id.get(institution_id)
            if not old_name:
                continue
            for field in fields:
                if field in row and clean(row.get(field)) == old_name:
                    row[field] = new_name
            if filename == "institution_aliases.csv" and clean(row.get("institution_id")) == institution_id:
                row["canonical_institution_name"] = new_name
            if filename == "institution_locations.csv" and clean(row.get("institution_id")) == institution_id:
                row["institution"] = new_name
                row["normalized_institution"] = normalize_institution(new_name)
    return renames, aliases_added


def validate_approved(
    tables: Mapping[str, Mapping[str, Any]],
    overrides: Mapping[str, Mapping[str, str]],
) -> list[str]:
    issues: list[str] = []
    institutions = active_institutions(tables)
    by_id = {clean(row.get("institution_id")): row for row in institutions}
    aliases = aliases_by_id(tables)
    locations = locations_by_id(tables)
    for institution_id, override in overrides.items():
        if override["status"] != "approved":
            continue
        expected = clean(override.get("english_canonical_name"))
        old_name = clean(override.get("local_name_alias"))
        record = by_id.get(institution_id)
        if not record:
            issues.append(f"approved institution ID missing: {institution_id}")
            continue
        if clean(record.get("canonical_name")) != expected:
            issues.append(
                f"{institution_id}: canonical name is {record.get('canonical_name')!r}, expected {expected!r}"
            )
        if old_name and normalize_institution(old_name) not in {
            normalize_institution(alias) for alias in aliases.get(institution_id, [])
        }:
            issues.append(f"{institution_id}: former canonical name is not retained as an alias")
        collision, ids = collision_for(institution_id, expected, institutions, locations)
        if ids:
            issues.append(f"{institution_id}: unsafe {collision} with {', '.join(ids)}")
    if len({clean(row.get("institution_id")) for row in institutions}) != len(institutions):
        issues.append("active canonical institution IDs are not unique")
    return issues


def summary(
    audit: Sequence[Mapping[str, str]],
    tables: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    renamed = [row for row in audit if row["decision"] == "rename"]
    reviewed = [row for row in audit if row["decision"] in {"rename", "review"} or row["source_or_evidence"]]
    collision_warnings = [row for row in audit if row["collision_status"] != "none"]
    renamed_ids = {row["institution_id"] for row in renamed}
    affected_mappings = [
        row
        for row in tables["author_institution_mappings.csv"]["rows"]
        if clean(row.get("mapping_status")) == "active"
        and clean(row.get("institution_id")) in renamed_ids
    ]
    migrated_aliases = [
        row
        for row in tables["institution_aliases.csv"]["rows"]
        if clean(row.get("institution_id")) in renamed_ids
        and "english-name-migration" in clean(row.get("alias_source"))
    ]
    return {
        "total_canonical_institutions_scanned": len(audit),
        "total_candidates_reviewed": len(reviewed),
        "total_approved_renames": len(renamed),
        "total_names_intentionally_retained": sum(
            1 for row in audit if row["decision"] == "keep" and row["source_or_evidence"]
        ),
        "total_unresolved_manual_review_cases": sum(
            1 for row in audit if row["decision"] == "review"
        ),
        "total_collision_warnings": len(collision_warnings),
        "total_aliases_added": len(migrated_aliases),
        "total_affected_papers": len({
            clean(row.get("paper_id")) for row in affected_mappings
            if clean(row.get("paper_id"))
        }),
        "total_affected_relationships": len(affected_mappings),
        "renamed_institutions": [
            {
                "institution_id": row["institution_id"],
                "from": row["current_canonical_name"],
                "to": row["proposed_english_name"],
            }
            for row in renamed
        ],
        "unresolved_candidates": [
            {
                "institution_id": row["institution_id"],
                "canonical_name": row["current_canonical_name"],
                "reason": row["decision_reason"],
            }
            for row in audit if row["decision"] == "review"
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--validate", action="store_true")
    parser.add_argument("--curated-dir", type=Path, default=CURATED_DATA_DIR)
    parser.add_argument("--overrides", type=Path, default=OVERRIDES_PATH)
    parser.add_argument("--audit-output", type=Path, default=AUDIT_PATH)
    parser.add_argument("--summary-output", type=Path, default=SUMMARY_PATH)
    args = parser.parse_args(argv)

    try:
        overrides = load_overrides(args.overrides)
        tables = load_tables(args.curated_dir)
        before = identity_snapshot(tables, args.curated_dir)
        initial_audit = build_audit(tables, overrides)
        applied_renames = aliases_added = 0
        if args.apply:
            applied_renames, aliases_added = apply_approved(tables, initial_audit)
            after = identity_snapshot(tables, args.curated_dir)
            if before != after:
                raise MigrationError("identity/relationship invariant changed during display-name migration")
            for table in tables.values():
                write_csv(table["path"], table["columns"], table["rows"])
        audit = build_audit(tables, overrides)
        issues = validate_approved(tables, overrides) if (args.apply or args.validate) else []
        if args.dry_run or args.apply:
            write_csv(args.audit_output, AUDIT_COLUMNS, audit)
            result = summary(initial_audit, tables)
            args.summary_output.parent.mkdir(parents=True, exist_ok=True)
            args.summary_output.write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print(f"Applied renames this run: {applied_renames}")
            print(f"Aliases added this run: {aliases_added}")
        if issues:
            for issue in issues:
                print(f"ERROR: {issue}", file=sys.stderr)
            return 1
        if args.validate:
            print(f"Validated {len(audit)} active canonical institutions and {len(overrides)} decisions.")
        return 0
    except (MigrationError, OSError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
