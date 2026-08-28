#!/usr/bin/env python3
"""Explain public-preview reductions from durable curated evidence."""

from __future__ import annotations

import unicodedata
import re

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
    from .public_relationships import (
        ReviewedRelationshipResolver,
        canonical_author_names,
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
    from public_relationships import (
        ReviewedRelationshipResolver,
        canonical_author_names,
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


@dataclass(frozen=True)
class RelationshipExplanation:
    """One conservative, auditable explanation for an old map relationship."""

    reason: str
    evidence: str
    explained: bool


def _keys(record: Mapping[str, Any]) -> set[str]:
    return set(all_identity_keys(record))


def _paper_matches(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return records_share_any_identity(left, right)


class _PaperIdentityIndex:
    """Transaction-local index mirroring records_share_any_identity exactly."""

    def __init__(self, records: Sequence[Mapping[str, Any]]) -> None:
        self.positions = {id(record): index for index, record in enumerate(records)}
        self.strong: dict[str, list[Mapping[str, Any]]] = {}
        self.weak: dict[str, list[Mapping[str, Any]]] = {}
        self.cache: dict[
            int,
            tuple[
                Mapping[str, Any],
                tuple[tuple[str, ...], tuple[str, ...]],
            ],
        ] = {}
        for record in records:
            keys, strong_keys = self._identities(record)
            target = self.strong if strong_keys else self.weak
            for key in strong_keys or keys:
                target.setdefault(key, []).append(record)

    def _identities(
        self, record: Mapping[str, Any]
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        marker = id(record)
        entry = self.cache.get(marker)
        if entry is None or entry[0] is not record:
            keys = tuple(all_identity_keys(record))
            cached = (
                keys,
                tuple(key for key in keys if not key.startswith("title_year:")),
            )
            self.cache[marker] = (record, cached)
            return cached
        return entry[1]

    def matches(self, record: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        keys, strong_keys = self._identities(record)
        source = self.strong if strong_keys else self.weak
        candidates: dict[int, Mapping[str, Any]] = {}
        for key in strong_keys or keys:
            for candidate in source.get(key, ()):
                candidates.setdefault(id(candidate), candidate)
        return sorted(
            candidates.values(), key=lambda candidate: self.positions[id(candidate)]
        )


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


def _location_identity(record: Mapping[str, Any]) -> str:
    location_id = clean(record.get("location_id"))
    return location_id.casefold()


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
    identity_index: _PaperIdentityIndex | None = None,
) -> bool:
    institution = _institution_identity(old)
    location = _location_identity(old)
    authors = _relationship_author_set(old)
    candidates = (
        identity_index.matches(old) if identity_index is not None else new_maps
    )
    return any(
        _institution_identity(new) == institution
        and (not location or _location_identity(new) == location)
        and (
            not authors
            or _relationship_author_set(new) == authors
        )
        and (identity_index is not None or _paper_matches(old, new))
        for new in candidates
    )


def _confirmation_fields(record: Mapping[str, Any]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in clean(record.get("confirmation_text")).split(";"):
        key, separator, value = part.partition("=")
        if separator and clean(key):
            fields[clean(key).casefold()] = clean(value)
    return fields


def _audit_value(record: Mapping[str, Any], field: str) -> str:
    return clean(record.get(field)) or _confirmation_fields(record).get(field, "")


def _single_author_set(value: Any) -> frozenset[str]:
    return _author_set(value)


def _relationship_target(
    old: Mapping[str, Any],
    new_maps: Sequence[Mapping[str, Any]],
    *,
    institution_id: str,
    location_id: str,
    authors: frozenset[str],
) -> Mapping[str, Any] | None:
    expected_institution = f"institution_id:{institution_id.casefold()}"
    for candidate in new_maps:
        if not _paper_matches(old, candidate):
            continue
        if _institution_identity(candidate) != expected_institution:
            continue
        if location_id and _location_identity(candidate) != location_id.casefold():
            continue
        candidate_sets = _record_author_sets(candidate)
        if authors and not any(authors <= candidate for candidate in candidate_sets):
            continue
        if not authors and candidate_sets:
            continue
        return candidate
    return None


def _merge_target(
    institution_id: str,
    institution_rows: Sequence[Mapping[str, Any]],
    audit_rows: Sequence[Mapping[str, Any]],
) -> tuple[str, str]:
    """Return final active merge target and a diagnostic code."""
    registry = {
        clean(row.get("institution_id")).casefold(): clean(
            row.get("institution_status")
        ).casefold()
        for row in institution_rows
        if clean(row.get("institution_id"))
    }
    direct = {
        clean(row.get("previous_institution_id")).casefold(): clean(
            row.get("institution_id")
        ).casefold()
        for row in audit_rows
        if clean(row.get("action")).casefold() == "merge"
        and clean(row.get("previous_institution_id"))
        and clean(row.get("institution_id"))
    }
    source = institution_id.casefold()
    # Automatic exact-equivalent consolidation removes the duplicate canonical
    # row after every dependent reference is rebound. The durable merge audit
    # remains the redirect authority; an extant source must still be a merged
    # tombstone, while an absent source is valid only with that exact audit.
    if source not in direct or registry.get(source, "") not in {"", "merged"}:
        return "", "not_a_reviewed_merge"
    visited = {source}
    target = direct[source]
    while target in direct:
        if target in visited:
            return "", "institution_merge_cycle"
        visited.add(target)
        target = direct[target]
    if target not in registry:
        return "", "dangling_institution_merge"
    if registry[target] != "active":
        return "", "merge_target_not_active"
    return target, "canonical_merge"


def _exact_reviewed_transition(
    old: Mapping[str, Any],
    new_maps: Sequence[Mapping[str, Any]],
    audits: Sequence[Mapping[str, Any]],
) -> RelationshipExplanation | None:
    old_id = clean(old.get("institution_id")).casefold()
    old_location = _location_identity(old)
    old_mapping = clean(old.get("mapping_id")).casefold()
    old_paper = clean(old.get("paper_id")).casefold()
    old_authors = _relationship_author_set(old)
    closest_failure = ""
    for audit in audits:
        action = clean(audit.get("action")).casefold()
        if action not in {
            "confirmed_mapping_changed", "mapping_replaced",
            "mapping_change_confirmed", "mapping_removed",
        }:
            continue
        if clean(audit.get("previous_institution_id")).casefold() != old_id:
            continue
        evidence_paper = _audit_value(audit, "paper_id").casefold()
        if not evidence_paper or (old_paper and evidence_paper != old_paper):
            closest_failure = "paper_scope_mismatch"
            continue
        evidence_mapping = (
            _audit_value(audit, "previous_mapping_id")
            or _audit_value(audit, "mapping_id")
        ).casefold()
        if old_mapping and evidence_mapping != old_mapping:
            closest_failure = "mapping_scope_mismatch"
            continue
        evidence_authors = _single_author_set(
            audit.get("previous_authors") or audit.get("affected_authors")
        )
        if old_authors and evidence_authors != old_authors:
            closest_failure = "author_scope_mismatch"
            continue
        evidence_old_location = clean(audit.get("previous_location_id")).casefold()
        new_id = clean(audit.get("institution_id")).casefold()
        new_location = clean(audit.get("location_id")).casefold()
        if (
            old_location
            and evidence_old_location != old_location
            # The stale export may already contain the reviewed destination
            # location while still carrying the pre-review author scope.  The
            # exact author transition remains valid for that hybrid row.
            and new_location != old_location
            and not (
                not evidence_old_location
                and new_id
                and new_id != old_id
            )
        ):
            closest_failure = "old_location_mismatch"
            continue
        audit_id = clean(audit.get("audit_id")) or "[missing audit_id]"
        if action == "mapping_removed":
            return RelationshipExplanation(
                "explicit_removal", f"explicit reviewed removal {audit_id}", True
            )
        new_authors = _single_author_set(
            audit.get("new_authors") or audit.get("affected_authors")
        )
        if not new_id:
            closest_failure = "invalid_replacement_evidence"
            continue
        if _relationship_target(
            old, new_maps, institution_id=new_id,
            location_id=new_location, authors=new_authors,
        ) is None:
            closest_failure = "replacement_target_missing"
            continue
        reason = (
            "reviewed_location_replacement"
            if new_id == old_id and new_location != old_location
            else "reviewed_institution_location_replacement"
            if new_location != old_location
            else "reviewed_mapping_replacement"
        )
        return RelationshipExplanation(
            reason, f"{reason} via {audit_id}", True
        )
    if closest_failure:
        return RelationshipExplanation(
            closest_failure, f"invalid replacement evidence: {closest_failure}", False
        )
    return None


def explain_removed_relationship(
    old: Mapping[str, Any],
    new_maps: Sequence[Mapping[str, Any]],
    *,
    institution_rows: Sequence[Mapping[str, Any]] = (),
    institution_audits: Sequence[Mapping[str, Any]] = (),
    institution_redirects: Optional[Mapping[str, str]] = None,
) -> RelationshipExplanation:
    """Explain identity preservation/replacement without authorizing data loss."""
    if _map_present(old, new_maps):
        return RelationshipExplanation("preserved", "relationship preserved", True)
    old_id = clean(old.get("institution_id")).casefold()
    old_location = _location_identity(old)
    authors = _relationship_author_set(old)
    if old_id and institution_rows:
        target, merge_reason = _merge_target(
            old_id, institution_rows, institution_audits
        )
        if target:
            candidates = [
                candidate for candidate in new_maps
                if _paper_matches(old, candidate)
                and _institution_identity(candidate)
                == f"institution_id:{target}"
                and (
                    not authors
                    or any(
                        authors <= candidate_authors
                        for candidate_authors in _record_author_sets(candidate)
                    )
                )
            ]
            if candidates:
                audit = next(
                    row for row in institution_audits
                    if clean(row.get("action")).casefold() == "merge"
                    and clean(row.get("previous_institution_id")).casefold() == old_id
                )
                return RelationshipExplanation(
                    "canonical_merge",
                    "canonical_merge via "
                    f"{clean(audit.get('audit_id'))}; target={target}",
                    True,
                )
            return RelationshipExplanation(
                "replacement_target_missing",
                f"canonical merge target {target} has no matching paper/author relationship",
                False,
            )
        if merge_reason not in {"not_a_reviewed_merge"}:
            return RelationshipExplanation(merge_reason, merge_reason, False)
    reviewed = _exact_reviewed_transition(old, new_maps, institution_audits)
    if reviewed is not None and reviewed.explained:
        return reviewed
    canonical_old = _canonical_institution_identity(
        _institution_identity(old), institution_redirects
    )
    for candidate in new_maps:
        if not _paper_matches(old, candidate):
            continue
        if _canonical_institution_identity(
            _institution_identity(candidate), institution_redirects
        ) != canonical_old:
            continue
        if old_location and _location_identity(candidate) != old_location:
            continue
        if authors and not any(
            authors <= candidate_authors
            for candidate_authors in _record_author_sets(candidate)
        ):
            continue
        return RelationshipExplanation(
            "alias_canonical_consolidation",
            "confirmed alias/canonical registry identity preservation",
            True,
        )
    redirect = clean((institution_redirects or {}).get(old_id)).casefold()
    if redirect and _relationship_target(
        old, new_maps, institution_id=redirect,
        location_id=old_location, authors=authors,
    ) is not None:
        return RelationshipExplanation(
            "alias_canonical_consolidation",
            f"confirmed canonical identity redirect {old_id} -> {redirect}",
            True,
        )
    if len(authors) > 1:
        explanations = []
        for author in sorted(authors):
            atom = dict(old)
            atom["institution_authors"] = [author]
            preserved = any(
                _paper_matches(atom, candidate)
                and _institution_identity(atom) == _institution_identity(candidate)
                and (
                    not old_location
                    or _location_identity(candidate) == old_location
                )
                and any(
                    author in candidate_authors
                    for candidate_authors in _record_author_sets(candidate)
                )
                for candidate in new_maps
            )
            explanation = (
                RelationshipExplanation("preserved", "author relationship preserved", True)
                if preserved
                else explain_removed_relationship(
                    atom,
                    new_maps,
                    institution_rows=institution_rows,
                    institution_audits=institution_audits,
                    institution_redirects=institution_redirects,
                )
            )
            explanations.append((author, explanation))
        failures = [item for item in explanations if not item[1].explained]
        if failures:
            author, failure = failures[0]
            return RelationshipExplanation(
                failure.reason,
                f"author scope mismatch for {author}: {failure.evidence}",
                False,
            )
        return RelationshipExplanation(
            "author_set_scoped_supersession",
            "author_set_scoped_supersession: " + "; ".join(
                f"{author}={explanation.reason}"
                for author, explanation in explanations
            ),
            True,
        )
    if reviewed is not None:
        return reviewed
    return RelationshipExplanation(
        "unexplained_removal", "no exact durable relationship-transition evidence", False
    )


def _active_mapping_decision(
    record: Mapping[str, Any], decisions: Sequence[Mapping[str, Any]]
) -> Mapping[str, Any] | None:
    institution_id = clean(record.get("institution_id")).casefold()
    mapping_id = clean(record.get("mapping_id")).casefold()
    author_set = _relationship_author_set(record)
    for row in decisions:
        if clean(row.get("action")) != "exclude_wrong_mapping":
            continue
        if not institution_id or clean(row.get("institution_id")).casefold() != institution_id:
            continue
        if mapping_id and clean(row.get("mapping_id")).casefold() != mapping_id:
            continue
        decision_authors = _author_set(row.get("institution_authors") or "")
        if author_set and decision_authors != author_set:
            continue
        if _paper_matches(record, row):
            return row
    return None


def _normalized_author_name(value: Any) -> str:
    normalized = unicodedata.normalize("NFKD", clean(value).casefold())
    unaccented = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    # Treat punctuation, Unicode dashes, and other presentation separators as
    # whitespace.  Author evidence comes from several metadata sources and the
    # same person commonly arrives as "J.-P. Müller", "J P Muller", or with a
    # composed/decomposed accent.
    return " ".join(re.findall(r"\w+", unaccented, flags=re.UNICODE))


def _author_set(value: Any) -> frozenset[str]:
    return frozenset(
        normalized
        for author in canonical_author_names(value)
        if (normalized := _normalized_author_name(author))
    )


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


def _relationship_author_set(record: Mapping[str, Any]) -> frozenset[str]:
    """Return the map row's primary author scope, preferring its direct field."""
    direct = _author_set(record.get("institution_authors") or [])
    if direct:
        return direct
    nested = _record_author_sets(record)
    return next(iter(nested), frozenset()) if len(nested) == 1 else frozenset()


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
    institution_audits: Sequence[Mapping[str, Any]] = (),
    institution_rows: Sequence[Mapping[str, Any]] = (),
    location_rows: Sequence[Mapping[str, Any]] = (),
    orphan_cleanup_audits: Sequence[Mapping[str, Any]] = (),
    institution_redirects: Optional[Mapping[str, str]] = None,
    approved_by_baseline: bool = False,
) -> ShrinkageReport:
    exclusion_index = build_active_exclusion_index(exclusion_rows)
    relationship_resolver = ReviewedRelationshipResolver(
        curated_mappings, institution_audits, location_rows
    )
    new_paper_index = _PaperIdentityIndex(new_papers)
    new_map_index = _PaperIdentityIndex(new_maps)
    removed_paper_records = [
        old
        for old in previous_papers
        if not new_paper_index.matches(old)
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
        if _map_present(old, new_maps, new_map_index):
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
        superseding_mapping_ids = relationship_resolver.superseding_mapping_ids(old)
        transition = (
            RelationshipExplanation(
                "reviewed_curated_supersession",
                "active curated mapping supersession via "
                + ", ".join(superseding_mapping_ids),
                True,
            )
            if superseding_mapping_ids
            else explain_removed_relationship(
                old,
                new_maps,
                institution_rows=institution_rows,
                institution_audits=institution_audits,
                institution_redirects=institution_redirects,
            )
        )
        if relationship_resolver.location_is_rejected(old):
            transition = RelationshipExplanation(
                "location_review", "explicit current location status requires review; candidate coordinates retained", True,
            )
        institution_id = clean(
            old.get("institution_id") or old.get("canonical_institution_id")
        )
        orphan_cleanup = next(
            (
                row for row in orphan_cleanup_audits
                if clean(row.get("institution_id")) == institution_id
                and clean(row.get("decision")) in {
                    "deleted_orphan", "merged_then_deleted",
                    "alias_preserved_then_deleted",
                }
                and clean(row.get("deleted_from_registry")).casefold() == "true"
            ),
            None,
        )
        follows_paper = any(_keys(old) & keys for keys in explained_paper_keys)
        if exclusion:
            evidence = f"active exclusion {clean(exclusion.get('exclusion_id'))}"
        elif merge:
            evidence = f"confirmed version merge {clean(merge.get('merge_id'))}"
        elif decision:
            evidence = f"reviewed mapping decision {clean(decision.get('decision_id'))}"
        elif orphan_cleanup:
            evidence = (
                "authoritative orphan-institution cleanup "
                f"{clean(orphan_cleanup.get('run_id'))}"
            )
        elif follows_paper:
            evidence = "follows explained paper removal"
        elif transition.explained:
            evidence = transition.evidence
        else:
            evidence = transition.evidence
        explained = bool(
            exclusion or merge or decision
            or orphan_cleanup or follows_paper or transition.explained
        )
        location = _location_identity(old)
        mapping_id = clean(old.get("mapping_id"))
        authors = sorted(_relationship_author_set(old))
        identity = (
            f"{_identity_label(old)} + {_institution_identity(old)}"
            f" + location_id:{location or '[none]'}"
            f" + mapping_id:{mapping_id or '[none]'}"
            f" + authors:{'; '.join(authors) or '[none]'}"
        )
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
