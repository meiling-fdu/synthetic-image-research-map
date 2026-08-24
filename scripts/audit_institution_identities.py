#!/usr/bin/env python3
"""Audit and conservatively consolidate exact-equivalent institution identities."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .curated_institutions import (
        DEFAULT_ALIASES_PATH,
        DEFAULT_AUDIT_PATH,
        DEFAULT_HIERARCHY_PATH,
        DEFAULT_INSTITUTIONS_PATH,
        DEFAULT_LOCATIONS_PATH,
        DEFAULT_LOCATION_AUDIT_PATH,
        DEFAULT_LOCATION_REVIEWS_PATH,
        DEFAULT_MAPPINGS_PATH,
        DEFAULT_REVIEW_QUEUE_PATH,
        DEFAULT_SEARCH_RELATIONSHIPS_PATH,
        clean,
        alias_id_for,
        exact_institution_matches,
        institution_match_key,
        load_institutions,
        merge_institutions,
        save_institutions,
    )
    from .curated_schema import (
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        INSTITUTION_REVIEW_QUEUE_COLUMNS,
    )
except ImportError:
    from curated_institutions import (
        DEFAULT_ALIASES_PATH,
        DEFAULT_AUDIT_PATH,
        DEFAULT_HIERARCHY_PATH,
        DEFAULT_INSTITUTIONS_PATH,
        DEFAULT_LOCATIONS_PATH,
        DEFAULT_LOCATION_AUDIT_PATH,
        DEFAULT_LOCATION_REVIEWS_PATH,
        DEFAULT_MAPPINGS_PATH,
        DEFAULT_REVIEW_QUEUE_PATH,
        DEFAULT_SEARCH_RELATIONSHIPS_PATH,
        clean,
        alias_id_for,
        exact_institution_matches,
        institution_match_key,
        load_institutions,
        merge_institutions,
        save_institutions,
    )
    from curated_schema import (
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        INSTITUTION_REVIEW_QUEUE_COLUMNS,
    )


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT_PATH = ROOT / "data/processed/institution_identity_resolution_audit.csv"
DEFAULT_DOC_PATH = ROOT / "docs/institution_identity_resolution_audit.md"
REPORT_COLUMNS = (
    "action",
    "normalized_value",
    "source_name",
    "source_institution_id",
    "target_name",
    "target_institution_id",
    "match_source",
    "status",
    "details",
)


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _components(institutions, aliases):
    active = {
        clean(row.get("institution_id")): row
        for row in institutions
        if clean(row.get("institution_status")) == "active"
    }
    canonical_by_key = defaultdict(set)
    evidence_by_key = defaultdict(set)
    for identifier, row in active.items():
        canonical_by_key[institution_match_key(row.get("canonical_name"))].add(identifier)
        abbreviation = institution_match_key(row.get("abbreviation"))
        if abbreviation:
            evidence_by_key[abbreviation].add(identifier)
    for alias in aliases:
        identifier = clean(alias.get("institution_id"))
        if identifier in active and clean(alias.get("review_status")) == "confirmed":
            evidence_by_key[institution_match_key(alias.get("alias_name"))].add(identifier)

    edges = defaultdict(set)
    ambiguous = []
    for key, canonical_ids in canonical_by_key.items():
        if not key:
            continue
        if len(canonical_ids) > 1:
            for identifier in canonical_ids:
                edges[identifier].update(canonical_ids - {identifier})
            continue
        source = next(iter(canonical_ids))
        targets = evidence_by_key.get(key, set()) - {source}
        if len(targets) == 1:
            target = next(iter(targets))
            edges[source].add(target)
            edges[target].add(source)
        elif len(targets) > 1:
            ambiguous.append((key, source, sorted(targets)))

    components = []
    visited = set()
    for start in sorted(edges):
        if start in visited:
            continue
        stack = [start]
        component = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            stack.extend(edges[current])
        visited.update(component)
        if len(component) > 1:
            components.append(sorted(component))
    return active, components, ambiguous


def _survivor(component, active, paths):
    counts = Counter()
    for path, fields, weight in (
        (paths["mappings"], ("institution_id",), 12),
        (paths["locations"], ("institution_id",), 10),
        (paths["location_reviews"], ("institution_id",), 4),
        (paths["aliases"], ("institution_id",), 3),
        (paths["hierarchy"], ("parent_institution_id", "child_institution_id"), 2),
        (paths["search_relationships"], ("root_institution_id", "related_institution_id"), 2),
    ):
        for row in _read(path):
            for field in fields:
                identifier = clean(row.get(field))
                if identifier in component:
                    counts[identifier] += weight
    def rank(identifier):
        row = active[identifier]
        curated = sum(bool(clean(row.get(field))) for field in (
            "abbreviation", "parent_institution_id", "institution_type", "public_display"
        ))
        if clean(row.get("institution_type")) == "other":
            curated -= 1
        return (-counts[identifier], -curated, clean(row.get("created_at")), identifier)
    return min(component, key=rank)


def _component_conflict(component, active, paths):
    parents = {
        clean(active[identifier].get("parent_institution_id"))
        for identifier in component
        if clean(active[identifier].get("parent_institution_id")) not in component
        and clean(active[identifier].get("parent_institution_id"))
    }
    countries = {
        clean(row.get("country_code") or row.get("country")).casefold()
        for row in _read(paths["locations"])
        if clean(row.get("institution_id")) in component
        and clean(row.get("country_code") or row.get("country"))
    }
    if len(parents) > 1:
        return "Exact names have conflicting curated parents."
    if len(countries) > 1:
        return "Exact names have confirmed locations in different countries."
    return ""


def _match_source(name, target, aliases):
    key = institution_match_key(name)
    if key == institution_match_key(target.get("canonical_name")):
        return "canonical_name"
    if key == institution_match_key(target.get("abbreviation")):
        return "abbreviation"
    if any(
        clean(row.get("institution_id")) == clean(target.get("institution_id"))
        and clean(row.get("review_status")) == "confirmed"
        and institution_match_key(row.get("alias_name")) == key
        for row in aliases
    ):
        return "alias"
    return "exact_identity"


def audit_and_consolidate(*, write: bool, paths: Mapping[str, Path], report_path: Path, doc_path: Path):
    touched = tuple(dict.fromkeys((*paths.values(), report_path, doc_path)))
    snapshots = {path: path.read_bytes() if path.exists() else None for path in touched}
    report = []
    try:
        institutions = load_institutions(paths["institutions"])
        aliases = _read(paths["aliases"])
        active, components, ambiguous_groups = _components(institutions, aliases)
        for key, source, targets in ambiguous_groups:
            report.append({
                "action": "ambiguous_exact_match", "normalized_value": key,
                "source_name": clean(active[source].get("canonical_name")),
                "source_institution_id": source, "target_name": " | ".join(clean(active[x].get("canonical_name")) for x in targets),
                "target_institution_id": " | ".join(targets), "match_source": "alias_or_abbreviation",
                "status": "left_untouched", "details": "More than one exact canonical target remains.",
            })

        for component in components:
            conflict = _component_conflict(component, active, paths)
            if conflict:
                names = [clean(active[identifier].get("canonical_name")) for identifier in component]
                report.append({
                    "action": "ambiguous_exact_match", "normalized_value": institution_match_key(names[0]),
                    "source_name": names[0], "source_institution_id": component[0],
                    "target_name": " | ".join(names[1:]), "target_institution_id": " | ".join(component[1:]),
                    "match_source": "conflicting_curated_metadata", "status": "left_untouched", "details": conflict,
                })
                continue
            survivor = _survivor(component, active, paths)
            survivor_name = clean(active[survivor].get("canonical_name"))
            for source in sorted(set(component) - {survivor}):
                source_name = clean(active[source].get("canonical_name"))
                match_source = _match_source(source_name, active[survivor], aliases)
                report.append({
                    "action": "duplicate_merged", "normalized_value": institution_match_key(source_name),
                    "source_name": source_name, "source_institution_id": source,
                    "target_name": survivor_name, "target_institution_id": survivor,
                    "match_source": match_source,
                    "status": "merged" if write else "would_merge",
                    "details": "Deterministic survivor selected from curated usage and metadata.",
                })
                if write:
                    merge_institutions(
                        source, survivor,
                        confirmation=f"REPLACE {source_name} WITH {survivor_name} GLOBALLY",
                        review_note="Automatic exact-equivalent canonical identity consolidation.",
                        location_resolution="keep_both",
                        institutions_path=paths["institutions"], mappings_path=paths["mappings"],
                        aliases_path=paths["aliases"], locations_path=paths["locations"],
                        location_reviews_path=paths["location_reviews"], location_audit_path=paths["location_audits"],
                        hierarchy_path=paths["hierarchy"], search_relationships_path=paths["search_relationships"],
                        review_queue_path=paths["review_queue"], audit_path=paths["audit"],
                    )

        if write:
            institutions = load_institutions(paths["institutions"])
            automatic_merge_sources = {
                clean(row.get("previous_institution_id"))
                for row in _read(paths["audit"])
                if clean(row.get("action")) == "merge"
                and "Automatic exact-equivalent" in clean(row.get("review_note"))
            }
            institutions = [
                row for row in institutions
                if not (
                    clean(row.get("institution_id")) in automatic_merge_sources
                    and clean(row.get("institution_status")) == "merged"
                )
            ]
            save_institutions(institutions, paths["institutions"])
            aliases = _read(paths["aliases"])
            active = {clean(row.get("institution_id")): row for row in institutions if clean(row.get("institution_status")) == "active"}
            # Canonical names never need to be repeated as aliases.
            aliases = [
                row for row in aliases
                if clean(row.get("institution_id")) not in active
                or clean(row.get("alias_name")) != clean(active[clean(row.get("institution_id"))].get("canonical_name"))
            ]
            for alias in aliases:
                target = active.get(clean(alias.get("institution_id")))
                if target:
                    alias["canonical_institution_name"] = clean(target.get("canonical_name"))
            override_path = ROOT / "data/manual/institution_english_name_overrides.csv"
            if override_path.exists():
                for override in _read(override_path):
                    identifier = clean(override.get("institution_id"))
                    former_name = clean(
                        override.get("former_canonical_name")
                        or override.get("local_name_alias")
                    )
                    target = active.get(identifier)
                    if not target or not former_name or clean(override.get("status")) != "approved":
                        continue
                    if clean(target.get("canonical_name")).casefold() == former_name.casefold():
                        continue
                    if any(clean(row.get("alias_name")).casefold() == former_name.casefold() and clean(row.get("institution_id")) == identifier for row in aliases):
                        continue
                    aliases.append({
                        "alias_id": alias_id_for(former_name), "alias_name": former_name,
                        "institution_id": identifier, "canonical_institution_name": clean(target.get("canonical_name")),
                        "alias_language": "", "alias_source": "english-name-migration",
                        "review_status": "confirmed", "notes": "Previous canonical name retained by approved English-name migration.",
                    })
            _write(paths["aliases"], INSTITUTION_ALIAS_COLUMNS, aliases)

        current_institutions = load_institutions(paths["institutions"]) if write else institutions
        current_aliases = _read(paths["aliases"]) if write else aliases
        current_active = {clean(row.get("institution_id")): row for row in current_institutions if clean(row.get("institution_status")) == "active"}
        reviews = _read(paths["location_reviews"])
        known_locations = defaultdict(list)
        for location in _read(paths["locations"]):
            if clean(location.get("coordinate_status")) == "known" and clean(location.get("lat")) and clean(location.get("lon")):
                known_locations[clean(location.get("institution_id"))].append(location)
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        for row in reviews:
            if clean(row.get("review_status")) not in {"pending_review", "ambiguous"}:
                continue
            name = clean(row.get("institution") or row.get("canonical_institution_name"))
            matches = exact_institution_matches(name, current_institutions, current_aliases)
            if len(matches) == 1:
                target_id = matches[0]
                target = current_active[target_id]
                source = _match_source(name, target, current_aliases)
                has_unique_location = len(known_locations[target_id]) == 1
                action = (
                    "pending_review_resolved"
                    if has_unique_location
                    else "identity_resolved_needs_coordinates"
                )
                report.append({
                    "action": action, "normalized_value": institution_match_key(name),
                    "source_name": name, "source_institution_id": clean(row.get("institution_id")),
                    "target_name": clean(target.get("canonical_name")), "target_institution_id": target_id,
                    "match_source": source,
                    "status": ("resolved" if has_unique_location else "needs_coordinates") if write else ("would_resolve" if has_unique_location else "would_need_coordinates"),
                    "details": (
                        "Exact identity and one confirmed canonical location."
                        if has_unique_location
                        else "Exact identity; location is missing or more than one confirmed location remains."
                    ),
                })
                if write:
                    changes = {
                        "institution_id": target_id,
                        "canonical_institution_name": clean(target.get("canonical_name")),
                        "matched_institution": clean(target.get("canonical_name")),
                        "match_method": f"exact_{source}",
                        "confidence": "high",
                        "review_status": "confirmed" if has_unique_location else "pending_review",
                        "location_status": "known" if has_unique_location else "needs_coordinate_review",
                        "coordinate_status": "known" if has_unique_location else "missing",
                    }
                    if any(clean(row.get(field)) != value for field, value in changes.items()):
                        row.update(changes)
                        row["updated_at"] = now
            elif len(matches) > 1:
                report.append({
                    "action": "ambiguous_pending_review", "normalized_value": institution_match_key(name),
                    "source_name": name, "source_institution_id": clean(row.get("institution_id")),
                    "target_name": " | ".join(clean(current_active[x].get("canonical_name")) for x in matches),
                    "target_institution_id": " | ".join(matches), "match_source": "exact_identity",
                    "status": "left_untouched", "details": "More than one exact canonical target remains.",
                })
                if write:
                    changes = {
                        "review_status": "ambiguous",
                        "location_status": "ambiguous",
                        "coordinate_status": "ambiguous",
                    }
                    if any(clean(row.get(field)) != value for field, value in changes.items()):
                        row.update(changes)
                        row["updated_at"] = now
        if write:
            _write(paths["location_reviews"], INSTITUTION_LOCATION_REVIEW_COLUMNS, reviews)
            queue = _read(paths["review_queue"])
            for row in queue:
                if clean(row.get("issue_type")) == "duplicate_institution" and clean(row.get("current_institution_id")) == clean(row.get("suggested_institution_id")):
                    changes = {"finding_status": "archived", "resolution_action": "resolved_by_reaudit", "resolution_note": "Exact-equivalent canonical records were consolidated.", "is_current": "false", "resolved_by": "institution-identity-audit"}
                    if any(clean(row.get(field)) != value for field, value in changes.items()):
                        row.update(changes)
                        row["updated_at"] = now
                        row["resolved_at"] = now
            _write(paths["review_queue"], INSTITUTION_REVIEW_QUEUE_COLUMNS, queue)

            # Keep the report idempotent and cumulative across later full
            # refreshes; the audit log and exact match_method fields are the
            # durable provenance for previously applied automatic resolutions.
            historical = _read(report_path) if report_path.exists() else []
            current_review_keys = {
                (institution_match_key(review.get("institution")), clean(review.get("institution_id")))
                for review in reviews
                if clean(review.get("match_method")).startswith("exact_")
            }
            historical = [
                finding for finding in historical
                if not (
                    clean(finding.get("action")) in {
                        "identity_resolved_needs_coordinates", "pending_review_resolved",
                    }
                    and (
                        clean(finding.get("normalized_value")),
                        clean(finding.get("target_institution_id")),
                    ) in current_review_keys
                )
            ]
            reported_merges = {
                (clean(row.get("source_institution_id")), clean(row.get("target_institution_id")))
                for row in (*historical, *report) if clean(row.get("action")) == "duplicate_merged"
            }
            by_id = {
                clean(row.get("institution_id")): row
                for row in load_institutions(paths["institutions"])
            }
            for audit in _read(paths["audit"]):
                if clean(audit.get("action")) != "merge" or "Automatic exact-equivalent" not in clean(audit.get("review_note")):
                    continue
                source_id = clean(audit.get("previous_institution_id"))
                target_id = clean(audit.get("institution_id"))
                if (source_id, target_id) in reported_merges:
                    continue
                source = by_id.get(source_id, {})
                target = by_id.get(target_id, {})
                source_name = clean(source.get("canonical_name"))
                historical.append({
                    "action": "duplicate_merged", "normalized_value": institution_match_key(source_name),
                    "source_name": source_name, "source_institution_id": source_id,
                    "target_name": clean(target.get("canonical_name")), "target_institution_id": target_id,
                    "match_source": _match_source(source_name, target, current_aliases),
                    "status": "merged", "details": "Deterministic survivor selected from curated usage and metadata.",
                })
            for review in reviews:
                method = clean(review.get("match_method"))
                if not method.startswith("exact_"):
                    continue
                target_id = clean(review.get("institution_id"))
                target = by_id.get(target_id, {})
                name = clean(review.get("institution"))
                needs_coordinates = clean(review.get("review_status")) == "pending_review"
                historical.append({
                    "action": "identity_resolved_needs_coordinates" if needs_coordinates else "pending_review_resolved",
                    "normalized_value": institution_match_key(name),
                    "source_name": name, "source_institution_id": target_id,
                    "target_name": clean(target.get("canonical_name")), "target_institution_id": target_id,
                    "match_source": method.removeprefix("exact_"),
                    "status": "needs_coordinates" if needs_coordinates else "resolved",
                    "details": (
                        "Exact identity; location is missing or more than one confirmed location remains."
                        if needs_coordinates else "Exact identity and one confirmed canonical location."
                    ),
                })
            combined = [*historical, *report]
            unique = {}
            for finding in combined:
                key = tuple(clean(finding.get(field)) for field in (
                    "action", "normalized_value", "source_institution_id", "target_institution_id", "match_source"
                ))
                unique[key] = finding
            report = list(unique.values())

        _write(report_path, REPORT_COLUMNS, report)
        summary = Counter(row["action"] for row in report)
        try:
            report_label = str(report_path.relative_to(ROOT))
        except ValueError:
            report_label = str(report_path)
        lines = [
            "# Institution identity resolution audit", "",
            "Only normalized exact canonical-name, abbreviation, and confirmed-alias equivalence is considered. No fuzzy matching is performed.", "",
            f"- Duplicates merged: {summary['duplicate_merged']}",
            f"- Abbreviation/alias matches resolved: {sum(1 for row in report if row['status'] in {'merged', 'resolved', 'needs_coordinates', 'would_merge', 'would_resolve', 'would_need_coordinates'} and row['match_source'] in {'abbreviation', 'alias'})}",
            f"- Pending Review records automatically resolved: {summary['pending_review_resolved']}",
            f"- Known identities left in Needs Coordinates: {summary['identity_resolved_needs_coordinates']}",
            f"- Ambiguous cases left untouched: {summary['ambiguous_exact_match'] + summary['ambiguous_pending_review']}", "",
            f"Machine-readable report: `{report_label}`", "",
        ]
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = doc_path.with_suffix(doc_path.suffix + ".tmp")
        temporary.write_text("\n".join(lines), encoding="utf-8")
        temporary.replace(doc_path)
        return {"rows": report, "summary": dict(summary)}
    except Exception:
        for path, content in snapshots.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise


def default_paths() -> dict[str, Path]:
    return {
        "institutions": DEFAULT_INSTITUTIONS_PATH, "mappings": DEFAULT_MAPPINGS_PATH,
        "aliases": DEFAULT_ALIASES_PATH, "locations": DEFAULT_LOCATIONS_PATH,
        "location_reviews": DEFAULT_LOCATION_REVIEWS_PATH, "location_audits": DEFAULT_LOCATION_AUDIT_PATH,
        "hierarchy": DEFAULT_HIERARCHY_PATH, "search_relationships": DEFAULT_SEARCH_RELATIONSHIPS_PATH,
        "review_queue": DEFAULT_REVIEW_QUEUE_PATH, "audit": DEFAULT_AUDIT_PATH,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Apply exact-equivalent consolidations atomically.")
    args = parser.parse_args()
    result = audit_and_consolidate(write=args.write, paths=default_paths(), report_path=DEFAULT_REPORT_PATH, doc_path=DEFAULT_DOC_PATH)
    print(f"Institution identity audit: {len(result['rows'])} finding(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
