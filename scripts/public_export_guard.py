#!/usr/bin/env python3
"""Explain public-preview reductions from durable curated evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

try:
    from .paper_exclusions import (
        all_identity_keys,
        build_active_exclusion_index,
        clean,
        record_is_excluded,
        records_share_any_identity,
    )
    from .paper_version_merges import (
        active_confirmed_merges,
        record_matches_merge_side,
    )
except ImportError:
    from paper_exclusions import (
        all_identity_keys,
        build_active_exclusion_index,
        clean,
        record_is_excluded,
        records_share_any_identity,
    )
    from paper_version_merges import (
        active_confirmed_merges,
        record_matches_merge_side,
    )


@dataclass(frozen=True)
class Removal:
    kind: str
    identity: str
    title: str
    evidence: str
    explained: bool


@dataclass(frozen=True)
class ShrinkageReport:
    previous_papers: int
    new_papers: int
    previous_maps: int
    new_maps: int
    removed_papers: tuple[Removal, ...]
    removed_maps: tuple[Removal, ...]
    approved_by_baseline: bool = False

    @property
    def unexplained(self) -> tuple[Removal, ...]:
        return tuple(
            row
            for row in (*self.removed_papers, *self.removed_maps)
            if not row.explained
        )

    @property
    def allowed(self) -> bool:
        return not self.unexplained or self.approved_by_baseline


def _keys(record: Mapping[str, Any]) -> set[str]:
    return set(all_identity_keys(record))


def _paper_matches(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return records_share_any_identity(left, right)


def _identity_label(record: Mapping[str, Any]) -> str:
    keys = all_identity_keys(record)
    return keys[0] if keys else f"title:{clean(record.get('title')) or '[unknown]'}"


def _institution_identity(record: Mapping[str, Any]) -> str:
    institution_id = clean(
        record.get("institution_id") or record.get("canonical_institution_id")
    )
    if institution_id:
        return f"institution_id:{institution_id.casefold()}"
    name = clean(
        record.get("canonical_institution_name")
        or record.get("canonical_name")
        or record.get("institution_name")
        or record.get("institution")
    )
    return f"institution_name:{name.casefold()}"


def _canonical_institution_identity(
    identity: str,
    institution_redirects: Optional[Mapping[str, str]] = None,
) -> str:
    if not identity.startswith("institution_id:"):
        return identity
    raw_id = identity.removeprefix("institution_id:")
    redirects = institution_redirects or {}
    visited = {raw_id}
    target = clean(redirects.get(raw_id)).casefold()
    while target and target not in visited:
        visited.add(target)
        next_target = clean(redirects.get(target)).casefold()
        if not next_target:
            return f"institution_id:{target}"
        target = next_target
    return f"institution_id:{target or raw_id}"


def _map_present(
    old: Mapping[str, Any],
    new_maps: Sequence[Mapping[str, Any]],
    institution_redirects: Optional[Mapping[str, str]] = None,
) -> bool:
    institution = _canonical_institution_identity(
        _institution_identity(old), institution_redirects
    )
    return any(
        _canonical_institution_identity(
            _institution_identity(new), institution_redirects
        )
        == institution
        and _paper_matches(old, new)
        for new in new_maps
    )


def _active_mapping_decision(
    record: Mapping[str, Any], decisions: Sequence[Mapping[str, Any]]
) -> Mapping[str, Any] | None:
    institution = clean(
        record.get("canonical_institution_name")
        or record.get("institution_name")
        or record.get("institution")
    ).casefold()
    for row in decisions:
        if clean(row.get("action")) != "exclude_wrong_mapping":
            continue
        if clean(row.get("institution")).casefold() != institution:
            continue
        if _paper_matches(record, row):
            return row
    return None


def _author_set(value: Any) -> frozenset[str]:
    if isinstance(value, str):
        value = value.split(";")
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
        return frozenset()
    return frozenset(clean(author).casefold() for author in value if clean(author))


def _record_author_sets(record: Mapping[str, Any]) -> set[frozenset[str]]:
    author_sets = set()
    direct = _author_set(record.get("institution_authors") or [])
    if direct:
        author_sets.add(direct)
    actual_id = clean(record.get("institution_id")).casefold()
    actual_name = clean(record.get("institution")).casefold()
    for field in ("author_institution_affiliations", "affiliations"):
        values = record.get(field)
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
            continue
        for value in values:
            if not isinstance(value, Mapping):
                continue
            value_id = clean(value.get("institution_id")).casefold()
            value_name = clean(
                value.get("institution")
                or value.get("canonical_name")
                or value.get("name")
            ).casefold()
            same_institution = bool(
                (actual_id and value_id and actual_id == value_id)
                or (actual_name and value_name and actual_name == value_name)
            )
            if not same_institution:
                continue
            nested = _author_set(value.get("authors") or [])
            if nested:
                author_sets.add(nested)
    return author_sets


def _lower_priority_mapping(record: Mapping[str, Any]) -> bool:
    if clean(record.get("mapping_id")):
        return False
    source = clean(record.get("source_database")).casefold()
    institution_source = clean(record.get("institution_source")).casefold()
    return bool(
        record.get("preliminary_affiliations") is True
        or record.get("mapping_fallback") is True
        or institution_source in {"automatic_fallback", "raw_affiliation", "openalex"}
        or source in {"openalex", "raw", "candidate"}
    )


def _curated_mapping_evidence(
    record: Mapping[str, Any],
    mappings: Sequence[Mapping[str, Any]],
    new_maps: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    actual_id = clean(record.get("institution_id")).casefold()
    actual_name = clean(record.get("institution")).casefold()
    author_sets = _record_author_sets(record)
    for row in mappings:
        if not _paper_matches(record, row):
            continue
        row_id = clean(row.get("institution_id")).casefold()
        row_name = clean(row.get("institution")).casefold()
        status = clean(row.get("mapping_status")).casefold()
        row_authors = _author_set(row.get("institution_authors") or "")
        same_institution = bool(
            (actual_id and row_id and actual_id == row_id)
            or (not actual_id and actual_name and actual_name == row_name)
        )
        if status == "excluded" and same_institution:
            return row
        if (
            status == "active"
            and row_authors
            and row_authors in author_sets
            and not same_institution
        ):
            replacement_present = any(
                _paper_matches(row, new)
                and (
                    clean(new.get("institution_id")).casefold() == row_id
                    if row_id
                    else clean(new.get("institution")).casefold() == row_name
                )
                for new in new_maps
            )
            if replacement_present or _lower_priority_mapping(record):
                return row
    return None


def _merge_evidence(
    record: Mapping[str, Any],
    new_papers: Sequence[Mapping[str, Any]],
    merge_rows: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    for row in active_confirmed_merges(merge_rows):
        if not record_matches_merge_side(record, row, "duplicate"):
            continue
        if any(
            record_matches_merge_side(new, row, "canonical")
            for new in new_papers
        ):
            return row
    return None


def _exclusion_evidence(
    record: Mapping[str, Any],
    exclusion_index: Mapping[str, Sequence[Mapping[str, Any]]],
) -> Mapping[str, Any] | None:
    if not record_is_excluded(record, exclusion_index):
        return None
    for key in all_identity_keys(record):
        rows = exclusion_index.get(key)
        if rows:
            return rows[0]
    return None


def filter_preserved_records(
    records: Sequence[Mapping[str, Any]],
    *,
    map_records: bool,
    exclusion_rows: Sequence[Mapping[str, Any]],
    merge_rows: Sequence[Mapping[str, Any]],
    review_decisions: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Keep incomplete-snapshot coverage without reviving explicit removals."""
    exclusion_index = build_active_exclusion_index(exclusion_rows)
    active_merges = active_confirmed_merges(merge_rows)
    kept = []
    for record in records:
        if record_is_excluded(record, exclusion_index):
            continue
        if any(
            record_matches_merge_side(record, row, "duplicate")
            for row in active_merges
        ):
            continue
        if map_records and _active_mapping_decision(record, review_decisions):
            continue
        kept.append(dict(record))
    return kept


def analyze_shrinkage(
    previous_papers: Sequence[Mapping[str, Any]],
    new_papers: Sequence[Mapping[str, Any]],
    previous_maps: Sequence[Mapping[str, Any]],
    new_maps: Sequence[Mapping[str, Any]],
    *,
    exclusion_rows: Sequence[Mapping[str, Any]] = (),
    merge_rows: Sequence[Mapping[str, Any]] = (),
    review_decisions: Sequence[Mapping[str, Any]] = (),
    curated_mappings: Sequence[Mapping[str, Any]] = (),
    institution_redirects: Optional[Mapping[str, str]] = None,
    approved_by_baseline: bool = False,
) -> ShrinkageReport:
    exclusion_index = build_active_exclusion_index(exclusion_rows)
    removed_paper_records = [
        old
        for old in previous_papers
        if not any(_paper_matches(old, new) for new in new_papers)
    ]
    paper_removals = []
    explained_paper_keys: list[set[str]] = []
    for old in removed_paper_records:
        exclusion = _exclusion_evidence(old, exclusion_index)
        merge = _merge_evidence(old, new_papers, merge_rows)
        if exclusion:
            evidence = (
                f"active exclusion {clean(exclusion.get('exclusion_id'))} "
                f"({clean(exclusion.get('reason'))})"
            )
        elif merge:
            evidence = f"confirmed version merge {clean(merge.get('merge_id'))}"
        else:
            evidence = "no durable exclusion, merge, or reviewed replacement"
        explained = bool(exclusion or merge)
        if explained:
            explained_paper_keys.append(_keys(old))
        paper_removals.append(
            Removal(
                "paper",
                _identity_label(old),
                clean(old.get("title")),
                evidence,
                explained,
            )
        )

    map_removals = []
    for old in previous_maps:
        if _map_present(old, new_maps, institution_redirects):
            continue
        exclusion = _exclusion_evidence(old, exclusion_index)
        merge = next(
            (
                row
                for row in active_confirmed_merges(merge_rows)
                if record_matches_merge_side(old, row, "duplicate")
                and any(
                    record_matches_merge_side(new, row, "canonical")
                    and _institution_identity(new) == _institution_identity(old)
                    for new in new_maps
                )
            ),
            None,
        )
        decision = _active_mapping_decision(old, review_decisions)
        mapping = _curated_mapping_evidence(old, curated_mappings, new_maps)
        follows_paper = any(_keys(old) & keys for keys in explained_paper_keys)
        if exclusion:
            evidence = f"active exclusion {clean(exclusion.get('exclusion_id'))}"
        elif merge:
            evidence = f"confirmed version merge {clean(merge.get('merge_id'))}"
        elif decision:
            evidence = f"reviewed mapping decision {clean(decision.get('decision_id'))}"
        elif mapping:
            evidence = (
                "curated/manual mapping supersession; reviewed mapping scope: "
                f"author set; authoritative mapping IDs: {clean(mapping.get('mapping_id'))}"
            )
        elif follows_paper:
            evidence = "follows explained paper removal"
        else:
            evidence = "no durable paper or institution-mapping evidence"
        explained = bool(exclusion or merge or decision or mapping or follows_paper)
        identity = f"{_identity_label(old)} + {_institution_identity(old)}"
        map_removals.append(
            Removal("map", identity, clean(old.get("title")), evidence, explained)
        )

    return ShrinkageReport(
        len(previous_papers),
        len(new_papers),
        len(previous_maps),
        len(new_maps),
        tuple(paper_removals),
        tuple(map_removals),
        approved_by_baseline,
    )


def format_shrinkage_report(report: ShrinkageReport) -> str:
    lines = [
        "Public export identity shrinkage audit",
        f"  Previous papers: {report.previous_papers}",
        f"  New papers: {report.new_papers}",
        f"  Previous map records: {report.previous_maps}",
        f"  New map records: {report.new_maps}",
    ]
    for label, rows in (
        ("Removed papers", report.removed_papers),
        ("Removed map relationships", report.removed_maps),
    ):
        lines.append(f"  {label}: {len(rows)}")
        for row in rows:
            status = "explained" if row.explained else "UNEXPLAINED"
            lines.append(
                f"    - [{status}] {row.identity} | {row.title} | {row.evidence}"
            )
    lines.append(f"  Unexplained removals: {len(report.unexplained)}")
    if report.approved_by_baseline and report.unexplained:
        lines.append(
            "  Exceptional reviewed --approved-baseline authorizes the reduction"
        )
    lines.append(f"  Decision: {'PROCEED' if report.allowed else 'BLOCK'}")
    return "\n".join(lines)
