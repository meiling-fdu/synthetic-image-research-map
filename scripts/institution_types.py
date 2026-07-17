#!/usr/bin/env python3
"""Canonical institution-type taxonomy and deterministic migration rules."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any, Mapping, Sequence


INSTITUTION_TYPES = ("university", "research_unit", "company", "other")
INSTITUTION_TYPE_SET = frozenset(INSTITUTION_TYPES)
LEGACY_RESEARCH_TYPES = frozenset({"department", "institute", "laboratory"})

_UNIVERSITY_WORD = re.compile(r"\buniversity\b", re.IGNORECASE)
_RESEARCH_WORDS = re.compile(
    r"\b(?:academy|centre|center|department|institute|laboratory|lab|"
    r"research council|research group|research unit)\b",
    re.IGNORECASE,
)
_COMPANY_WORDS = re.compile(
    r"\b(?:corporation|incorporated|inc|limited|ltd|company|technologies|telecom)\b|"
    r"\bs\.?p\.?a\.?\b",
    re.IGNORECASE,
)
_KNOWN_COMMERCIAL_NAMES = re.compile(
    r"^(?:ant group|fujitsu(?: research of europe)?|identifai|leonardo|miraflow|"
    r"nec laboratories america)(?:\b|$)",
    re.IGNORECASE,
)


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def resolve_public_institution_type(value: Any) -> str:
    """Resolve stored/legacy values to the only four public values."""
    normalized = clean(value).casefold().replace("-", "_").replace(" ", "_")
    aliases = {
        "education": "university",
        "educational": "university",
        "research": "research_unit",
        "institute": "research_unit",
        "laboratory": "research_unit",
        "department": "research_unit",
        "corporate": "company",
        "commercial": "company",
        "unknown": "other",
    }
    resolved = aliases.get(normalized, normalized)
    return resolved if resolved in INSTITUTION_TYPE_SET else "other"


def confirmed_aliases_by_institution(
    aliases: Sequence[Mapping[str, Any]],
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for row in aliases:
        if clean(row.get("review_status")) != "confirmed":
            continue
        institution_id = clean(row.get("institution_id"))
        name = clean(row.get("alias_name"))
        if institution_id and name and name not in result[institution_id]:
            result[institution_id].append(name)
    return dict(result)


def merged_institution_redirects(
    institutions: Sequence[Mapping[str, Any]],
    aliases: Sequence[Mapping[str, Any]],
) -> dict[str, str]:
    """Resolve merged rows through confirmed merge aliases to active entities."""
    active_ids = {
        clean(row.get("institution_id"))
        for row in institutions
        if clean(row.get("institution_status")) == "active"
    }
    confirmed_targets: dict[str, set[str]] = defaultdict(set)
    for alias in aliases:
        if clean(alias.get("review_status")) == "confirmed":
            confirmed_targets[clean(alias.get("alias_name")).casefold()].add(
                clean(alias.get("institution_id"))
            )
    redirects: dict[str, str] = {}
    for row in institutions:
        if clean(row.get("institution_status")) != "merged":
            continue
        source = clean(row.get("institution_id"))
        targets = confirmed_targets.get(clean(row.get("canonical_name")).casefold(), set())
        targets = {target for target in targets if target in active_ids and target != source}
        if len(targets) == 1:
            redirects[source] = next(iter(targets))
    return redirects


def classify_institution_type(
    canonical_name: Any,
    aliases: Sequence[Any],
    previous_type: Any,
) -> tuple[str, str, str]:
    """Return (type, rule, evidence) using deterministic ordered rules."""
    name = clean(canonical_name)
    alias_names = [clean(alias) for alias in aliases if clean(alias)]
    previous = clean(previous_type).casefold()
    names = [name, *alias_names]

    if previous == "company":
        return "company", "preserve_confirmed_company", "previous_type=company"
    if previous == "university":
        return "university", "preserve_confirmed_university", "previous_type=university"
    university_match = next((value for value in names if _UNIVERSITY_WORD.search(value)), "")
    if university_match:
        source = "canonical_name" if university_match == name else "confirmed_alias"
        return "university", "complete_word_university", f"{source}={university_match}"
    if previous in {"laboratory", "department"}:
        return "research_unit", f"legacy_{previous}", f"previous_type={previous}"
    if _KNOWN_COMMERCIAL_NAMES.search(name):
        return "company", "clear_commercial_entity", f"canonical_name={name}"
    if previous == "institute":
        return "research_unit", "legacy_institute", "previous_type=institute"
    research_match = next((value for value in names if _RESEARCH_WORDS.search(value)), "")
    if research_match:
        source = "canonical_name" if research_match == name else "confirmed_alias"
        return "research_unit", "clear_research_organization", f"{source}={research_match}"
    if _COMPANY_WORDS.search(name):
        return "company", "clear_commercial_entity", f"canonical_name={name}"
    if previous == "research_unit":
        return "research_unit", "preserve_research_unit", "previous_type=research_unit"
    if previous == "other":
        return "other", "preserve_other", "previous_type=other"
    return "other", "unresolved_fallback", f"previous_type={previous or '[missing]'}"


def build_migration_rows(
    institutions: Sequence[Mapping[str, Any]],
    aliases: Sequence[Mapping[str, Any]],
    mappings: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, str]]:
    """Build an ordered, machine-readable report without mutating inputs."""
    by_id = {clean(row.get("institution_id")): row for row in institutions}
    redirects = merged_institution_redirects(institutions, aliases)
    aliases_by_id = confirmed_aliases_by_institution(aliases)

    classified: dict[str, tuple[str, str, str]] = {}
    for institution_id, row in by_id.items():
        if institution_id in redirects:
            continue
        classified[institution_id] = classify_institution_type(
            row.get("canonical_name"), aliases_by_id.get(institution_id, ()),
            row.get("institution_type"),
        )

    papers_by_id: dict[str, set[str]] = defaultdict(set)
    for mapping in mappings:
        if clean(mapping.get("mapping_status")) not in {"active", "needs_review"}:
            continue
        institution_id = clean(mapping.get("institution_id"))
        canonical_id = redirects.get(institution_id, institution_id)
        paper = clean(mapping.get("paper_id")) or clean(mapping.get("title"))
        if canonical_id and paper:
            papers_by_id[canonical_id].add(paper)

    report: list[dict[str, str]] = []
    for row in institutions:
        institution_id = clean(row.get("institution_id"))
        canonical_id = redirects.get(institution_id, institution_id)
        canonical = by_id.get(canonical_id, row)
        proposed, rule, evidence = classified.get(canonical_id) or classify_institution_type(
            canonical.get("canonical_name"), aliases_by_id.get(canonical_id, ()),
            canonical.get("institution_type"),
        )
        considered = aliases_by_id.get(canonical_id, [])
        if institution_id != canonical_id:
            rule = "merged_id_resolution_then_" + rule
            evidence = f"merged_to={canonical_id}; {evidence}"
        report.append({
            "institution_id": institution_id,
            "canonical_name": clean(canonical.get("canonical_name")),
            "aliases_considered": json.dumps(considered, ensure_ascii=False),
            "previous_type": clean(row.get("institution_type")),
            "proposed_type": proposed,
            "applied_rule": rule,
            "evidence": evidence,
            "affected_unique_paper_count": str(len(papers_by_id.get(canonical_id, set()))),
        })
    return report
