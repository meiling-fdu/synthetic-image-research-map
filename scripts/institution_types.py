#!/usr/bin/env python3
"""Canonical institution-type taxonomy and deterministic audit rules."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


INSTITUTION_TYPES = ("university", "research_unit", "company", "other")
INSTITUTION_TYPE_SET = frozenset(INSTITUTION_TYPES)
INSTITUTION_TYPE_LABELS = {
    "university": "University",
    "research_unit": "Research Institute",
    "company": "Company",
    "other": "Other",
}
LEGACY_RESEARCH_TYPES = frozenset({"department", "institute", "laboratory"})


@dataclass(frozen=True)
class TypeDecision:
    proposed_type: str
    rule: str
    evidence: str
    confidence: str
    provenance: str
    review_required: bool


UNIVERSITY_EXCLUSION_RE = re.compile(
    r"\b("
    r"university hospital|university press|university laboratory|"
    r"university medical center|university health science center|"
    r"hospital of .* university|affiliated hospital of .* university|"
    r"department of|faculty of|school of|college of|laboratory of|lab of"
    r")\b",
    re.IGNORECASE,
)
UNIVERSITY_STRUCTURE_RES = (
    re.compile(r"^university of\b", re.IGNORECASE),
    re.compile(r"\buniversity$", re.IGNORECASE),
    re.compile(r"\buniversity\s*[-,]", re.IGNORECASE),
    re.compile(r"\buniversity of\b", re.IGNORECASE),
    re.compile(r"\b(universit[eé]|universit[aà]|universidad|universiti|üniversitesi|universität)\b", re.IGNORECASE),
    re.compile(r"^technische universität\b", re.IGNORECASE),
    re.compile(r"^oll?scoil\b", re.IGNORECASE),
)
UNIVERSITY_INSTITUTE_RES = (
    re.compile(r"\b(indian institute of technology|national institute of technology)\b", re.IGNORECASE),
    re.compile(r"\binstitute of technology\b", re.IGNORECASE),
    re.compile(r"\binstitute of science and technology\b", re.IGNORECASE),
)
RESEARCH_UNIT_RES = (
    re.compile(r"\b(national institute of standards and technology|oak ridge national laboratory)\b", re.IGNORECASE),
    re.compile(r"\b(fraunhofer|max planck|inria|national research council)\b", re.IGNORECASE),
    re.compile(r"\b(academy of sciences|academy of robotics|research council)\b", re.IGNORECASE),
    re.compile(r"\b(center|centre) for .*(security|research|technology|science)\b", re.IGNORECASE),
    re.compile(r"\b(laboratory|national laboratory|research institute)\b", re.IGNORECASE),
)
COMPANY_RES = (
    re.compile(r"\b(inc|ltd|limited|corp|corporation|company|systems|pharm)\b", re.IGNORECASE),
    re.compile(r"\b(adobe|baidu|alibaba|fujitsu|honeywell|microsoft|nvidia|salesforce|samsung|sony|tencent|naver|megvii|mayachitra)\b", re.IGNORECASE),
)
VERIFIED_COLLEGE_UNIVERSITIES = frozenset({
    "anhui business college",
    "imperial college london",
    "king's college london",
    "berkeley college",
    "canadian international college",
})


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


def institution_type_label(value: Any) -> str:
    """Return the shared human-readable label for a stored or legacy value."""
    return INSTITUTION_TYPE_LABELS[resolve_public_institution_type(value)]


def normalized_name(value: Any) -> str:
    return clean(value).casefold().replace("–", "-")


def structurally_excluded_university_name(name: str) -> bool:
    normalized = clean(name)
    return bool(UNIVERSITY_EXCLUSION_RE.search(normalized))


def type_decision(
    canonical_name: Any,
    aliases: Sequence[Any] = (),
    previous_type: Any = "",
    *,
    reviewed_type: bool = True,
    trusted_type: Any = "",
    parent_type: Any = "",
) -> TypeDecision:
    """Classify one institution with conservative, ordered evidence.

    The name checks are intentionally structural: they require recognizable
    institution-name forms and run after explicit exclusions for hospitals,
    presses, laboratories, and subordinate university units.
    """
    name = clean(canonical_name)
    alias_names = [clean(alias) for alias in aliases if clean(alias)]
    previous = resolve_public_institution_type(previous_type)
    raw_previous = clean(previous_type).casefold()
    trusted = resolve_public_institution_type(trusted_type)
    parent = resolve_public_institution_type(parent_type)

    if reviewed_type and raw_previous in INSTITUTION_TYPE_SET:
        return TypeDecision(
            previous,
            f"explicit_reviewed_{previous}",
            f"curated institution_type={previous}",
            "reviewed",
            "curated",
            False,
        )
    if raw_previous in LEGACY_RESEARCH_TYPES:
        return TypeDecision(
            "research_unit",
            f"legacy_{raw_previous}",
            f"legacy institution_type={raw_previous}",
            "high",
            "curated_legacy",
            False,
        )
    if trusted_type and trusted in INSTITUTION_TYPE_SET:
        return TypeDecision(
            trusted,
            f"trusted_structured_{trusted}",
            f"trusted structured institution_type={trusted}",
            "high",
            "structured_evidence",
            False,
        )
    if parent_type and parent in {"university", "research_unit", "company"}:
        return TypeDecision(
            parent,
            f"parent_inheritance_{parent}",
            f"confirmed parent institution_type={parent}",
            "medium",
            "curated_hierarchy",
            parent == "company",
        )

    candidate_names = [name, *alias_names]
    for candidate in candidate_names:
        if not candidate:
            continue
        lowered = normalized_name(candidate)
        if structurally_excluded_university_name(candidate):
            continue
        if lowered in VERIFIED_COLLEGE_UNIVERSITIES:
            return TypeDecision(
                "university",
                "verified_college_evidence",
                f"name={candidate}",
                "high",
                "authoritative_review",
                False,
            )
        if any(pattern.search(candidate) for pattern in UNIVERSITY_STRUCTURE_RES):
            return TypeDecision(
                "university",
                "strong_canonical_name_university"
                if candidate == name else "strong_alias_university",
                f"name={candidate}",
                "high",
                "canonical_name" if candidate == name else "confirmed_alias",
                False,
            )
        if any(pattern.search(candidate) for pattern in UNIVERSITY_INSTITUTE_RES):
            return TypeDecision(
                "university",
                "strong_institute_name_university"
                if candidate == name else "strong_institute_alias_university",
                f"name={candidate}",
                "high",
                "canonical_name" if candidate == name else "confirmed_alias",
                False,
            )

    for candidate in candidate_names:
        if any(pattern.search(candidate) for pattern in COMPANY_RES):
            return TypeDecision(
                "company",
                "strong_canonical_name_company"
                if candidate == name else "strong_alias_company",
                f"name={candidate}",
                "high",
                "canonical_name" if candidate == name else "confirmed_alias",
                False,
            )

    for candidate in candidate_names:
        if structurally_excluded_university_name(candidate):
            continue
        if any(pattern.search(candidate) for pattern in RESEARCH_UNIT_RES):
            return TypeDecision(
                "research_unit",
                "strong_canonical_name_research_unit"
                if candidate == name else "strong_alias_research_unit",
                f"name={candidate}",
                "high",
                "canonical_name" if candidate == name else "confirmed_alias",
                False,
            )

    considered = "; ".join(candidate_names) or "[missing]"
    return TypeDecision(
        "other",
        "manual_review_required",
        f"unverified_names={considered}; previous_type={clean(previous_type) or '[missing]'}",
        "low",
        "fallback",
        True,
    )


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
    """Return the legacy tuple form used by older migration/admin callers."""
    decision = type_decision(canonical_name, aliases, previous_type)
    return decision.proposed_type, decision.rule, decision.evidence


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
