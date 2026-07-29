#!/usr/bin/env python3
"""Conservatively remove unreachable canonical institutions from a complete graph."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from .full_source_completeness import accepted, repository_audit
except ImportError:
    from full_source_completeness import accepted, repository_audit

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AUDIT = Path("data/processed/orphan_institution_cleanup_audit.csv")
AUDIT_FIELDS = (
    "institution_id", "institution_name", "country", "city",
    "direct_paper_count", "mapping_count", "author_count", "marker_count",
    "alias_count", "child_count", "parent_id", "merge_target",
    "replacement_target", "decision", "reason", "alias_preserved_as",
    "deleted_from_registry", "deleted_location", "run_id", "timestamp",
)
ACTIVE_MAPPING_STATUSES = {"active", "needs_review"}
FINAL_REVIEW_STATUSES = {"confirmed", "alias_of_confirmed"}


def clean(value: Any) -> str:
    return str(value or "").strip()


def normalized(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value).casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def truthy(value: Any) -> bool:
    return clean(value).casefold() in {"1", "true", "yes", "y", "protected", "pinned"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    records = value.get("records", []) if isinstance(value, dict) else value
    return [dict(row) for row in records if isinstance(row, dict)]


def paper_keys(row: Mapping[str, Any]) -> set[str]:
    keys = set()
    for field in ("paper_id", "doi", "openalex_url", "arxiv_id"):
        value = clean(row.get(field)).casefold()
        if value:
            keys.add(f"{field}:{value}")
    return keys


def paper_identity(row: Mapping[str, Any]) -> str:
    keys = paper_keys(row)
    return sorted(keys)[0] if keys else ""


def prove_complete_source(
    current_rows: Sequence[Mapping[str, Any]],
    retained_public_papers: Sequence[Mapping[str, Any]],
) -> tuple[bool, int]:
    """Require each retained public identity to occur in the current source union."""
    current_keys = set().union(*(paper_keys(row) for row in current_rows))
    missing = sum(
        bool(keys := paper_keys(row)) and not bool(keys & current_keys)
        for row in retained_public_papers
    )
    return missing == 0, missing


@dataclass
class CleanupResult:
    rows: list[dict[str, str]]
    institutions: list[dict[str, str]]
    locations: list[dict[str, str]]
    aliases: list[dict[str, str]]
    hierarchy: list[dict[str, str]]

    @property
    def deleted_ids(self) -> set[str]:
        return {
            row["institution_id"]
            for row in self.rows
            if row["decision"] in {
                "deleted_orphan", "merged_then_deleted",
                "alias_preserved_then_deleted",
            }
        }


def analyze(
    *,
    institutions: Sequence[Mapping[str, Any]],
    locations: Sequence[Mapping[str, Any]] = (),
    aliases: Sequence[Mapping[str, Any]] = (),
    hierarchy: Sequence[Mapping[str, Any]] = (),
    mappings: Sequence[Mapping[str, Any]] = (),
    location_review: Sequence[Mapping[str, Any]] = (),
    audit_log: Sequence[Mapping[str, Any]] = (),
    review_queue: Sequence[Mapping[str, Any]] = (),
    override_rows: Sequence[Mapping[str, Any]] = (),
    public_maps: Sequence[Mapping[str, Any]] = (),
    authoritative: bool,
    run_id: str,
    timestamp: str,
) -> CleanupResult:
    by_id = {clean(row.get("institution_id")): dict(row) for row in institutions}
    mapping_rows = [
        row for row in mappings
        if clean(row.get("mapping_status")).casefold() in ACTIVE_MAPPING_STATUSES
    ]
    all_mapping_refs = {
        clean(row.get("institution_id"))
        for row in mappings
        if clean(row.get("institution_id"))
    }
    mapping_counts = Counter(clean(row.get("institution_id")) for row in mapping_rows)
    paper_sets: dict[str, set[str]] = defaultdict(set)
    authors: dict[str, set[str]] = defaultdict(set)
    for row in mapping_rows:
        institution_id = clean(row.get("institution_id"))
        if identity := paper_identity(row):
            paper_sets[institution_id].add(identity)
        authors[institution_id].update(
            normalized(value)
            for value in re.split(r"\s*(?:;|\|)\s*", clean(row.get("institution_authors")))
            if normalized(value)
        )

    active_hierarchy = [
        dict(row) for row in hierarchy
        if clean(row.get("review_status")).casefold() in {"", "confirmed"}
    ]
    children: dict[str, set[str]] = defaultdict(set)
    parents: dict[str, set[str]] = defaultdict(set)
    for row in active_hierarchy:
        parent = clean(row.get("parent_institution_id"))
        child = clean(row.get("child_institution_id"))
        children[parent].add(child)
        parents[child].add(parent)

    target_ids = {
        clean(row.get("institution_id"))
        for row in aliases
        if clean(row.get("review_status")).casefold() in FINAL_REVIEW_STATUSES
    }
    replacements: dict[str, str] = {}
    audit_required = set()
    for row in audit_log:
        current = clean(row.get("institution_id"))
        previous = clean(row.get("previous_institution_id"))
        action = clean(row.get("action")).casefold()
        if current:
            audit_required.add(current)
        if previous and current and action in {"merge", "replace", "replacement"}:
            replacements[previous] = current

    reviewed_location_refs = {
        clean(row.get("institution_id"))
        for row in location_review
        if (
            clean(row.get("paper_id"))
            or clean(row.get("raw_affiliation"))
            or clean(row.get("canonical_institution_name"))
        )
    }
    durable_review_refs = {
        clean(value)
        for row in (*review_queue, *override_rows)
        for field, value in row.items()
        if "institution_id" in field and clean(value).startswith("institution:")
    }
    protected = {
        institution_id
        for institution_id, row in by_id.items()
        if any(truthy(row.get(field)) for field in (
            "protected", "pinned", "manual_retain", "intentionally_standalone"
        ))
        or clean(row.get("institution_status")).casefold() in {
            "protected", "pinned", "manual_retain", "standalone"
        }
    }
    public_marker_counts = Counter(
        clean(row.get("institution_id") or row.get("canonical_institution_id"))
        for row in public_maps
    )
    retained_public_relationships = {
        clean(row.get("institution_id") or row.get("canonical_institution_id"))
        for row in public_maps
        if paper_keys(row)
    }
    location_counts = Counter(clean(row.get("institution_id")) for row in locations)
    alias_counts = Counter(clean(row.get("institution_id")) for row in aliases)
    output_aliases = [dict(row) for row in aliases]
    location_by_id = {
        clean(row.get("institution_id")): row for row in locations
    }

    retained = (
        {key for key, count in mapping_counts.items() if key and count}
        | all_mapping_refs
        | retained_public_relationships
        | target_ids | audit_required | reviewed_location_refs | protected
        | durable_review_refs
    )
    # A retained child makes every confirmed ancestor structurally reachable.
    changed = True
    while changed:
        before = len(retained)
        retained.update(
            parent for child in tuple(retained) for parent in parents.get(child, ())
        )
        changed = len(retained) != before

    decisions: list[dict[str, str]] = []
    delete_ids: set[str] = set()
    for institution_id, institution in by_id.items():
        name = clean(institution.get("canonical_name"))
        parent_id = clean(institution.get("parent_institution_id"))
        child_count = len(children.get(institution_id, ()))
        merge_target = replacements.get(institution_id, "")
        alias_target = merge_target
        if not alias_target:
            source_location = location_by_id.get(institution_id, {})
            source_country = clean(source_location.get("country")).casefold()
            source_city = clean(source_location.get("city")).casefold()
            exact_targets = [
                candidate_id
                for candidate_id in retained
                if candidate_id != institution_id
                and candidate_id in by_id
                and normalized(by_id[candidate_id].get("canonical_name")) == normalized(name)
                and bool(source_country and source_city)
                and clean(location_by_id.get(candidate_id, {}).get("country")).casefold()
                == source_country
                and clean(location_by_id.get(candidate_id, {}).get("city")).casefold()
                == source_city
            ]
            if len(exact_targets) == 1:
                alias_target = exact_targets[0]
        source_tokens = set(normalized(name).split())
        ambiguous_targets = [
            candidate_id
            for candidate_id in retained
            if candidate_id != institution_id and candidate_id in by_id
            and source_tokens
            and len(
                source_tokens
                & set(normalized(by_id[candidate_id].get("canonical_name")).split())
            ) / len(
                source_tokens
                | set(normalized(by_id[candidate_id].get("canonical_name")).split())
            ) >= 0.8
        ]
        reason = ""
        if not authoritative and institution_id not in retained:
            decision = "retained_partial_source_run"
            reason = "source completeness proof failed; report-only mode"
        elif institution_id in protected:
            decision, reason = "retained_protected", "explicit retention flag or status"
        elif (
            institution_id in target_ids
            or institution_id in audit_required
            or institution_id in reviewed_location_refs
            or institution_id in retained_public_relationships
        ):
            decision, reason = "retained_by_reference", "reviewed alias, audit, replacement, or curated review reference"
        elif child_count:
            decision, reason = "retained_as_parent", "confirmed retained child or descendant"
        elif mapping_counts[institution_id]:
            decision, reason = "retained_by_reference", "active author–institution mapping"
        elif institution_id in retained:
            decision, reason = (
                "retained_by_reference",
                "retained mapping, paper, review, alias, audit, or protection reference",
            )
        elif authoritative and not alias_target and ambiguous_targets:
            decision, reason = (
                "ambiguous_duplicate",
                "similar retained canonical institution requires manual review",
            )
        elif authoritative and alias_target:
            decision = (
                "merged_then_deleted" if merge_target
                else "alias_preserved_then_deleted"
            )
            reason = "deterministic reviewed replacement or exact normalized identity"
            delete_ids.add(institution_id)
            target_name = clean(by_id[alias_target].get("canonical_name"))
            alias_id = "alias:" + hashlib.sha256(
                f"{normalized(name)}|{alias_target}".encode()
            ).hexdigest()[:16]
            if not any(
                normalized(row.get("alias_name")) == normalized(name)
                and clean(row.get("institution_id")) == alias_target
                for row in output_aliases
            ):
                output_aliases.append({
                    "alias_id": alias_id,
                    "alias_name": name,
                    "institution_id": alias_target,
                    "canonical_institution_name": target_name,
                    "alias_language": "",
                    "alias_source": "orphan-institution-cleanup",
                    "review_status": "confirmed",
                    "notes": f"Preserved from {institution_id} before canonical cleanup.",
                })
        elif parent_id and parent_id in by_id:
            # A leaf can still be swept; its parent link is owned by the leaf.
            decision, reason = "deleted_orphan", "unreachable leaf with no retained relationship"
            delete_ids.add(institution_id)
        elif authoritative:
            decision, reason = "deleted_orphan", "unreachable canonical institution in complete final graph"
            delete_ids.add(institution_id)
        else:
            decision, reason = "retained_partial_source_run", "report-only mode"
        location = next(
            (row for row in locations if clean(row.get("institution_id")) == institution_id),
            {},
        )
        decisions.append({
            "institution_id": institution_id,
            "institution_name": name,
            "country": clean(location.get("country")),
            "city": clean(location.get("city")),
            "direct_paper_count": str(len(paper_sets[institution_id])),
            "mapping_count": str(mapping_counts[institution_id]),
            "author_count": str(len(authors[institution_id])),
            "marker_count": str(public_marker_counts[institution_id] or location_counts[institution_id]),
            "alias_count": str(alias_counts[institution_id]),
            "child_count": str(child_count),
            "parent_id": parent_id,
            "merge_target": merge_target,
            "replacement_target": merge_target,
            "decision": decision,
            "reason": reason,
            "alias_preserved_as": alias_target,
            "deleted_from_registry": str(institution_id in delete_ids).lower(),
            "deleted_location": str(institution_id in delete_ids and bool(location_counts[institution_id])).lower(),
            "run_id": run_id,
            "timestamp": timestamp,
        })

    return CleanupResult(
        decisions,
        [dict(row) for row in institutions if clean(row.get("institution_id")) not in delete_ids],
        [dict(row) for row in locations if clean(row.get("institution_id")) not in delete_ids],
        [row for row in output_aliases if clean(row.get("institution_id")) not in delete_ids],
        [
            row for row in active_hierarchy
            if clean(row.get("parent_institution_id")) not in delete_ids
            and clean(row.get("child_institution_id")) not in delete_ids
        ],
    )


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def atomic_write_csvs(outputs: Sequence[tuple[Path, Sequence[Mapping[str, Any]], Sequence[str]]]) -> None:
    """Prepare every file first, then replace; restore all originals on failure."""
    prepared: list[tuple[Path, Path]] = []
    originals: dict[Path, bytes | None] = {}
    try:
        for path, rows, fields in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
            os.close(descriptor)
            temp = Path(temp_name)
            write_csv(temp, rows, fields)
            prepared.append((path, temp))
            originals[path] = path.read_bytes() if path.exists() else None
        for path, temp in prepared:
            os.replace(temp, path)
    except Exception:
        for path, content in originals.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise
    finally:
        for _, temp in prepared:
            temp.unlink(missing_ok=True)


def fields_for(path: Path, fallback: Sequence[str]) -> list[str]:
    rows = read_csv(path)
    if rows:
        return list(rows[0])
    if path.exists():
        with path.open(encoding="utf-8", newline="") as handle:
            return next(csv.reader(handle), list(fallback))
    return list(fallback)


def durable_audit_rows(
    current: Sequence[Mapping[str, Any]],
    previous: Sequence[Mapping[str, Any]],
    aliases: Sequence[Mapping[str, Any]],
    audit_log: Sequence[Mapping[str, Any]],
    run_id: str,
    timestamp: str,
) -> list[dict[str, str]]:
    """Keep deletion evidence after the deleted entity leaves the registry."""
    rows = [dict(row) for row in current]
    known = {clean(row.get("institution_id")) for row in rows}
    deletion_decisions = {
        "deleted_orphan", "merged_then_deleted", "alias_preserved_then_deleted",
    }
    for row in previous:
        institution_id = clean(row.get("institution_id"))
        if institution_id not in known and clean(row.get("decision")) in deletion_decisions:
            rows.append({field: clean(row.get(field)) for field in AUDIT_FIELDS})
            known.add(institution_id)
    reviewed_merge_sources = {
        clean(row.get("previous_institution_id"))
        for row in audit_log
        if clean(row.get("action")).casefold() in {
            "merge", "replace", "replacement", "confirmed_mapping_changed",
        }
        and clean(row.get("previous_institution_id"))
    }
    for alias in aliases:
        match = re.search(r"(institution:[0-9a-f]+)", clean(alias.get("notes")))
        source_id = match.group(1) if match else ""
        if not source_id:
            alias_id = clean(alias.get("alias_id"))
            if re.fullmatch(r"alias:[0-9a-f]+", alias_id):
                source_id = f"institution:{alias_id.removeprefix('alias:')}"
        if (
            not source_id
            or source_id in known
            or source_id == clean(alias.get("institution_id"))
            or source_id not in reviewed_merge_sources
        ):
            continue
        institution_id = source_id
        rows.append({
            **{field: "" for field in AUDIT_FIELDS},
            "institution_id": institution_id,
            "institution_name": clean(alias.get("alias_name")),
            "merge_target": clean(alias.get("institution_id")),
            "replacement_target": clean(alias.get("institution_id")),
            "decision": "merged_then_deleted",
            "reason": "reviewed canonical merge; name preserved as alias",
            "alias_preserved_as": clean(alias.get("institution_id")),
            "deleted_from_registry": "true",
            "deleted_location": "false",
            "run_id": run_id,
            "timestamp": timestamp,
        })
        known.add(institution_id)
    return rows


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authoritative", action="store_true",
                        help="Request deletion; still requires completeness proof.")
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    paths = {
        "institutions": Path("data/curated/institutions.csv"),
        "locations": Path("data/curated/institution_locations.csv"),
        "aliases": Path("data/curated/institution_aliases.csv"),
        "hierarchy": Path("data/curated/institution_hierarchy.csv"),
        "mappings": Path("data/curated/author_institution_mappings.csv"),
        "location_review": Path("data/curated/institution_location_review.csv"),
        "audit_log": Path("data/curated/institution_audit_log.csv"),
        "review_queue": Path("data/curated/institution_review_queue.csv"),
        "english_name_overrides": Path("data/manual/institution_english_name_overrides.csv"),
        "curated_papers": Path("data/curated/papers.csv"),
        "candidate": Path("web/data/openalex_candidate_map_data.json"),
        "public_papers": Path("web/data/public_preview_papers.json"),
        "public_maps": Path("web/data/public_preview_map_data.json"),
    }
    current = [*read_csv(paths["curated_papers"]), *read_json_records(paths["candidate"])]
    public_papers = read_json_records(paths["public_papers"])
    completeness_rows = repository_audit(public_papers)
    missing = sum(not accepted(row) for row in completeness_rows)
    complete = missing == 0
    authoritative = bool(args.authoritative and complete)
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    source_digest = hashlib.sha256(
        "\n".join(sorted(key for row in current for key in paper_keys(row))).encode()
    ).hexdigest()[:16]
    run_id = f"orphan-cleanup:{source_digest}"
    previous_audit = read_csv(args.audit)
    result = analyze(
        institutions=read_csv(paths["institutions"]),
        locations=read_csv(paths["locations"]),
        aliases=read_csv(paths["aliases"]),
        hierarchy=read_csv(paths["hierarchy"]),
        mappings=read_csv(paths["mappings"]),
        location_review=read_csv(paths["location_review"]),
        audit_log=read_csv(paths["audit_log"]),
        review_queue=read_csv(paths["review_queue"]),
        override_rows=read_csv(paths["english_name_overrides"]),
        public_maps=read_json_records(paths["public_maps"]),
        authoritative=authoritative,
        run_id=run_id,
        timestamp=stamp,
    )
    audit_rows = durable_audit_rows(
        result.rows, previous_audit, result.aliases,
        read_csv(paths["audit_log"]), run_id, stamp
    )
    outputs = [(args.audit, audit_rows, AUDIT_FIELDS)]
    if authoritative:
        for key, rows in (
            ("institutions", result.institutions), ("locations", result.locations),
            ("aliases", result.aliases), ("hierarchy", result.hierarchy),
        ):
            outputs.append((paths[key], rows, fields_for(paths[key], ())))
    atomic_write_csvs(outputs)
    counts = Counter(row["decision"] for row in audit_rows)
    print(
        f"Orphan institution cleanup: mode={'authoritative' if authoritative else 'report-only'}; "
        f"missing current-source public papers={missing}; deleted={len(result.deleted_ids)}; "
        f"partial-retained={counts['retained_partial_source_run']}; "
        f"parents-retained={counts['retained_as_parent']}; references-retained={counts['retained_by_reference']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
