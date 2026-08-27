#!/usr/bin/env python3
"""Canonical public paper/institution/location/author relationship identity."""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from typing import Any, Mapping, Sequence


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalized_text(value: Any) -> str:
    value = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", value, flags=re.UNICODE))


def normalized_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/", "", clean(value), flags=re.I
    ).casefold()


def paper_relationship_identity(record: Mapping[str, Any]) -> tuple[str, ...]:
    """Return the strongest stable paper identity available on a public row."""
    doi = normalized_doi(record.get("doi"))
    if doi:
        return ("doi", doi)
    paper_id = clean(record.get("paper_id")).casefold()
    if paper_id:
        return ("paper", paper_id)
    arxiv = clean(record.get("arxiv_id")).casefold()
    if arxiv:
        return ("arxiv", arxiv)
    openalex = clean(record.get("openalex_url") or record.get("openalex_id")).casefold().rstrip("/")
    if openalex:
        return ("openalex", openalex)
    return (
        "title_year",
        normalized_text(record.get("title")),
        clean(record.get("publication_year") or record.get("year")),
    )


def canonical_author_names(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        values: Sequence[Any] = re.split(r"\s*(?:;|\||\n)\s*", value)
    elif isinstance(value, Sequence):
        values = value
    else:
        values = ()
    names: list[str] = []
    for author in values:
        if isinstance(author, Mapping):
            author = author.get("display_name") or author.get("name")
        author_text = clean(author)
        comma_parts = [clean(part) for part in author_text.split(",")]
        if len(comma_parts) > 1 and all(" " in part for part in comma_parts):
            names.extend(part for part in comma_parts if part)
        elif author_text:
            names.append(author_text)
    return tuple(dict.fromkeys(names))


def normalized_author_set(value: Any) -> tuple[str, ...]:
    names = set()
    for author_text in canonical_author_names(value):
        if "," in author_text:
            family, given = author_text.split(",", 1)
            author_text = f"{given} {family}"
        normalized = normalized_text(author_text)
        if normalized:
            names.add(normalized)
    return tuple(sorted(names))


def public_relationship_key(record: Mapping[str, Any]) -> tuple[Any, ...]:
    """Identity invariant shared by materialization and final validation."""
    institution = clean(
        record.get("institution_id")
        or record.get("canonical_institution_id")
        or record.get("canonical_institution_name")
        or record.get("institution_name")
        or record.get("institution")
    ).casefold()
    location = clean(record.get("location_id")).casefold()
    return (
        paper_relationship_identity(record),
        institution,
        location,
        normalized_author_set(record.get("institution_authors")),
    )


class ReviewedRelationshipResolver:
    """Resolve current curated relationships and stale published predecessors.

    Mapping identity is deliberately kept separate from semantic relationship
    identity. A stable ``mapping_id`` proves that a row is explicit curated
    state, while paper/institution/location/authors determine what is public.
    """

    def __init__(
        self,
        mappings: Sequence[Mapping[str, Any]],
        audits: Sequence[Mapping[str, Any]] = (),
    ) -> None:
        self.targets: dict[
            tuple[tuple[str, ...], tuple[str, ...]],
            set[tuple[str, str]],
        ] = defaultdict(set)
        self.mapping_ids_by_scope: dict[
            tuple[tuple[str, ...], tuple[str, ...]], set[str]
        ] = defaultdict(set)
        self.mapping_ids: set[str] = set()
        self.audits = tuple(audits)
        self.active_mappings = {
            clean(row.get("mapping_id")): row for row in mappings
            if clean(row.get("mapping_status")) == "active"
            and clean(row.get("mapping_id"))
        }
        for mapping in mappings:
            if clean(mapping.get("mapping_status")).casefold() != "active":
                continue
            mapping_id = clean(mapping.get("mapping_id"))
            institution_id = clean(
                mapping.get("institution_id")
                or mapping.get("canonical_institution_id")
            ).casefold()
            authors = normalized_author_set(mapping.get("institution_authors"))
            if not mapping_id or not institution_id or not authors:
                continue
            scope = (paper_relationship_identity(mapping), authors)
            self.targets[scope].add(
                (institution_id, clean(mapping.get("location_id")).casefold())
            )
            self.mapping_ids_by_scope[scope].add(mapping_id)
            self.mapping_ids.add(mapping_id)

    @staticmethod
    def _metadata(value: Any) -> dict[str, str]:
        fields = {}
        for part in clean(value).split(";"):
            key, separator, item = part.partition("=")
            if separator and clean(key):
                fields[clean(key)] = clean(item)
        return fields

    def _audit_authorizes(
        self,
        record: Mapping[str, Any],
        targets: set[tuple[str, str]],
    ) -> bool:
        old_institution = clean(record.get("institution_id")).casefold()
        old_mapping = clean(record.get("mapping_id"))
        authors = normalized_author_set(record.get("institution_authors"))
        paper = paper_relationship_identity(record)
        record_paper_id = clean(record.get("paper_id")).casefold()
        for audit in self.audits:
            if clean(audit.get("action")) not in {
                "confirmed_mapping_changed", "mapping_change_confirmed",
                "mapping_replaced",
            }:
                continue
            metadata = self._metadata(audit.get("confirmation_text"))
            audit_paper_id = clean(
                audit.get("paper_id") or metadata.get("paper_id")
            ).casefold()
            if record_paper_id and audit_paper_id:
                if record_paper_id != audit_paper_id:
                    continue
            elif paper_relationship_identity({"paper_id": audit_paper_id}) != paper:
                continue
            audit_authors = normalized_author_set(
                audit.get("previous_authors") or audit.get("affected_authors")
            )
            if audit_authors != authors:
                continue
            previous_mapping = clean(
                audit.get("previous_mapping_id")
                or audit.get("mapping_id")
                or metadata.get("mapping_id")
            )
            if old_mapping and previous_mapping != old_mapping:
                continue
            if clean(audit.get("previous_institution_id")).casefold() != old_institution:
                continue
            new_target = (
                clean(audit.get("institution_id")).casefold(),
                clean(audit.get("location_id")).casefold(),
            )
            if any(
                target_institution == new_target[0]
                and (not new_target[1] or target_location == new_target[1])
                for target_institution, target_location in targets
            ):
                return True
        return False

    def _audit_removes(self, record: Mapping[str, Any]) -> bool:
        """Return whether an exact reviewed removal retires this public row."""
        old_institution = clean(record.get("institution_id")).casefold()
        old_location = clean(record.get("location_id")).casefold()
        old_mapping = clean(record.get("mapping_id"))
        old_authors = normalized_author_set(record.get("institution_authors"))
        old_paper_id = clean(record.get("paper_id")).casefold()
        for audit in self.audits:
            if clean(audit.get("action")).casefold() != "mapping_removed":
                continue
            metadata = self._metadata(audit.get("confirmation_text"))
            audit_paper_id = clean(
                audit.get("paper_id") or metadata.get("paper_id")
            ).casefold()
            if not audit_paper_id or (old_paper_id and audit_paper_id != old_paper_id):
                continue
            if not old_paper_id:
                # Automatic legacy rows may have no curated paper_id. Their
                # removal still needs an exact paper identity, not merely an
                # author/institution tuple that another paper could share.
                audit_doi = normalized_doi(metadata.get("paper_doi"))
                if not audit_doi or audit_doi != normalized_doi(record.get("doi")):
                    continue
            previous_mapping = clean(
                audit.get("previous_mapping_id")
                or audit.get("mapping_id")
                or metadata.get("mapping_id")
            )
            if old_mapping and previous_mapping != old_mapping:
                continue
            if clean(audit.get("previous_institution_id")).casefold() != old_institution:
                continue
            previous_location = clean(audit.get("previous_location_id")).casefold()
            if old_location and previous_location != old_location:
                continue
            audit_authors = normalized_author_set(
                audit.get("previous_authors") or audit.get("affected_authors")
            )
            if old_authors and audit_authors != old_authors:
                continue
            return True
        return False

    def superseding_mapping_ids(self, record: Mapping[str, Any]) -> tuple[str, ...]:
        """Return exact curated lineage authorizing a supersession."""
        audited = self._audited_replacement_mapping_ids(record)
        if audited:
            return audited
        if not self.supersedes(record):
            return ()
        scope = (
            paper_relationship_identity(record),
            normalized_author_set(record.get("institution_authors")),
        )
        return tuple(sorted(self.mapping_ids_by_scope.get(scope, ())))

    def _audited_replacement_mapping_ids(self, record: Mapping[str, Any]) -> tuple[str, ...]:
        """Honor an exact reviewed legacy-marker transition, including initials.

        Do not fuzzy-match authors or infer a replacement from the institution.
        Both the old exported record and the current target mapping must match
        durable evidence; this permits reviewed author spelling/campus repairs.
        """
        for audit in self.audits:
            if clean(audit.get("action")) not in {"mapping_change_confirmed", "mapping_replaced"}:
                continue
            metadata = self._metadata(audit.get("confirmation_text"))
            old_record_id = metadata.get("previous_record_id")
            if not old_record_id or old_record_id != clean(record.get("id")):
                continue
            doi = normalized_doi(metadata.get("paper_doi"))
            if not doi or doi != normalized_doi(record.get("doi")):
                continue
            if clean(audit.get("previous_institution_id")) != clean(record.get("institution_id")):
                continue
            if clean(audit.get("previous_location_id")) != clean(record.get("location_id")):
                continue
            if normalized_author_set(audit.get("previous_authors")) != normalized_author_set(record.get("institution_authors")):
                continue
            target = self.active_mappings.get(clean(audit.get("mapping_id")))
            if target is None or clean(target.get("paper_id")) != clean(audit.get("paper_id")):
                continue
            if normalized_doi(target.get("doi")) != doi:
                continue
            if (clean(target.get("institution_id")), clean(target.get("location_id"))) != (clean(audit.get("institution_id")), clean(audit.get("location_id"))):
                continue
            if normalized_author_set(target.get("institution_authors")) != normalized_author_set(audit.get("new_authors")):
                continue
            return (clean(target.get("mapping_id")),)
        return ()

    def supersedes(self, record: Mapping[str, Any]) -> bool:
        """Return whether explicit current state replaces this older row."""
        if self._audited_replacement_mapping_ids(record):
            return True
        if self._audit_removes(record):
            return True
        authors = normalized_author_set(record.get("institution_authors"))
        if not authors:
            return False
        targets = self.targets.get((paper_relationship_identity(record), authors))
        if not targets:
            return False
        institution_id = clean(
            record.get("institution_id")
            or record.get("canonical_institution_id")
        ).casefold()
        location_id = clean(record.get("location_id")).casefold()
        same_institution = {
            target_location
            for target_institution, target_location in targets
            if target_institution == institution_id
        }
        if not same_institution:
            # Generated fallback rows have no mapping lineage and are directly
            # superseded by explicit curated state. A different curated mapping
            # remains protected unless the audit trail identifies the exact
            # reviewed transition.
            return not clean(record.get("mapping_id")) or self._audit_authorizes(
                record, targets
            )
        # An explicit non-empty location replaces a stale or missing location.
        # A blank curated location does not discard otherwise compatible
        # preserved coordinates merely because review is still incomplete.
        explicit_locations = {value for value in same_institution if value}
        return bool(explicit_locations and location_id not in explicit_locations)

    def filter_superseded(
        self, records: Sequence[Mapping[str, Any]]
    ) -> tuple[list[dict[str, Any]], int]:
        kept = [dict(record) for record in records if not self.supersedes(record)]
        return kept, len(records) - len(kept)
