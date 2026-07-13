#!/usr/bin/env python3
"""Alias/parent-aware institution consistency and collision auditing."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from .curated_institutions import stable_institution_id
    from .review_decisions import read_review_decisions
except ImportError:
    from curated_institutions import stable_institution_id
    from review_decisions import read_review_decisions


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAPPINGS_PATH = REPOSITORY_ROOT / "data/curated/author_institution_mappings.csv"
DEFAULT_INSTITUTIONS_PATH = REPOSITORY_ROOT / "data/curated/institutions.csv"
DEFAULT_ALIASES_PATH = REPOSITORY_ROOT / "data/curated/institution_aliases.csv"
DEFAULT_HIERARCHY_PATH = REPOSITORY_ROOT / "data/curated/institution_hierarchy.csv"
DEFAULT_AUDIT_LOG_PATH = REPOSITORY_ROOT / "data/curated/institution_audit_log.csv"
DEFAULT_DECISIONS_PATH = REPOSITORY_ROOT / "data/curated/review_decisions.csv"
DEFAULT_PUBLIC_MAP_PATH = REPOSITORY_ROOT / "web/data/public_preview_map_data.json"
DEFAULT_PUBLIC_PAPERS_PATH = REPOSITORY_ROOT / "web/data/public_preview_papers.json"
DEFAULT_REPORT_PATH = REPOSITORY_ROOT / "data/manual/institution_consistency_audit.csv"

REPORT_COLUMNS = (
    "audit_id",
    "mapping_id",
    "paper_id",
    "paper_title",
    "year",
    "doi",
    "openalex_url",
    "author",
    "current_institution",
    "current_institution_id",
    "raw_affiliation",
    "suggested_canonical_institution",
    "suggested_institution_id",
    "severity",
    "issue_type",
    "reason",
    "recommended_action",
    "resolution_status",
)

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
GENERIC_TOKENS = {
    "a", "an", "and", "at", "corporation", "department", "for", "group",
    "inc", "institute", "institution", "laboratory", "lab", "of", "research",
    "school", "the", "university", "universita", "universite", "univ",
}
ACRONYM_STOPWORDS = GENERIC_TOKENS | {"de", "del", "der", "di", "du", "la"}


class InstitutionConsistencyError(RuntimeError):
    """Institution audit inputs are missing or malformed."""


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_institution(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).casefold()
    text = "".join(character for character in text if not unicodedata.combining(character))
    return " ".join(re.findall(r"[a-z0-9]+", text))


def institution_tokens(value: Any) -> tuple[str, ...]:
    return tuple(token for token in normalize_institution(value).split() if token not in GENERIC_TOKENS)


def institution_signature(value: Any) -> tuple[str, ...]:
    return tuple(sorted(set(institution_tokens(value))))


def institution_acronym(value: Any) -> str:
    words = [
        word for word in normalize_institution(value).split()
        if word not in ACRONYM_STOPWORDS and not word.isdigit()
    ]
    return "".join(word[0] for word in words)


def names_semantically_related(left: Any, right: Any) -> bool:
    left_name = normalize_institution(left)
    right_name = normalize_institution(right)
    if not left_name or not right_name:
        return False
    if left_name == right_name or institution_signature(left) == institution_signature(right):
        return True
    if left_name in right_name or right_name in left_name:
        return True
    left_tokens = set(institution_tokens(left))
    right_tokens = set(institution_tokens(right))
    if not left_tokens or not right_tokens:
        return False
    overlap = len(left_tokens & right_tokens) / max(len(left_tokens | right_tokens), 1)
    if overlap >= 0.75:
        return True
    left_compact = left_name.replace(" ", "")
    right_compact = right_name.replace(" ", "")
    return (
        len(left_compact) <= 12 and left_compact == institution_acronym(right)
    ) or (
        len(right_compact) <= 12 and right_compact == institution_acronym(left)
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except (OSError, UnicodeError, csv.Error) as error:
        raise InstitutionConsistencyError(f"could not read {path}: {error}") from error


def _read_public(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise InstitutionConsistencyError(f"could not read {path}: {error}") from error
    records = payload.get("records") if isinstance(payload, dict) else None
    return records if isinstance(records, list) else []


class InstitutionResolver:
    def __init__(
        self,
        institutions: Sequence[Mapping[str, Any]],
        aliases: Sequence[Mapping[str, Any]],
        hierarchy: Sequence[Mapping[str, Any]] = (),
        merge_audits: Sequence[Mapping[str, Any]] = (),
    ) -> None:
        self.entities = {
            clean(row.get("institution_id")): dict(row)
            for row in institutions if clean(row.get("institution_id"))
        }
        self.active_ids = {
            identifier for identifier, row in self.entities.items()
            if clean(row.get("institution_status")) not in {"ignored", "deprecated", "merged"}
        }
        self.names_by_id: dict[str, list[str]] = defaultdict(list)
        for identifier, row in self.entities.items():
            self.names_by_id[identifier].append(clean(row.get("canonical_name")))
        self.alias_target: dict[str, str] = {}
        for row in aliases:
            if clean(row.get("review_status")) != "confirmed":
                continue
            target = clean(row.get("institution_id"))
            alias = clean(row.get("alias_name"))
            if target and alias:
                self.names_by_id[target].append(alias)
                self.alias_target[normalize_institution(alias)] = target
        self.parents: dict[str, str] = {
            identifier: clean(row.get("parent_institution_id"))
            for identifier, row in self.entities.items()
        }
        for row in hierarchy:
            if clean(row.get("review_status")) == "confirmed":
                self.parents.setdefault(
                    clean(row.get("child_institution_id")),
                    clean(row.get("parent_institution_id")),
                )
        self.merges = {
            (clean(row.get("previous_institution_id")), clean(row.get("institution_id")))
            for row in merge_audits if clean(row.get("action")) == "merge"
        }
        self.merged_sources: dict[str, set[str]] = defaultdict(set)
        for source, target in self.merges:
            self.merged_sources[target].add(source)

    def canonical_name(self, institution_id: Any) -> str:
        return clean(self.entities.get(clean(institution_id), {}).get("canonical_name"))

    def ancestors(self, institution_id: Any) -> set[str]:
        result: set[str] = set()
        cursor = self.parents.get(clean(institution_id), "")
        while cursor and cursor not in result:
            result.add(cursor)
            cursor = self.parents.get(cursor, "")
        return result

    def related_ids(self, left: Any, right: Any) -> bool:
        left_id, right_id = clean(left), clean(right)
        if not left_id or not right_id:
            return False
        if left_id == right_id or right_id in self.ancestors(left_id) or left_id in self.ancestors(right_id):
            return True
        if (left_id, right_id) in self.merges or (right_id, left_id) in self.merges:
            return True
        return names_semantically_related(self.canonical_name(left_id), self.canonical_name(right_id))

    def name_matches_text(self, name: Any, evidence: Any) -> bool:
        normalized_name = normalize_institution(name)
        normalized_evidence = normalize_institution(evidence)
        if not normalized_name or not normalized_evidence:
            return False
        if normalized_name in normalized_evidence:
            return True
        uppercase_tokens = {
            normalize_institution(token)
            for token in re.findall(r"\b[A-Z][A-Z0-9-]{2,}\b", clean(name))
        }
        if uppercase_tokens & set(normalized_evidence.split()):
            return True
        signature = institution_signature(name)
        evidence_tokens = set(normalized_evidence.split())
        if len(signature) >= 2 and set(signature) <= evidence_tokens:
            return True
        acronym = institution_acronym(name)
        return len(acronym) >= 3 and acronym in set(normalized_evidence.split())

    def evidence_matches(self, institution_id: Any, evidence: Any) -> bool:
        identifier = clean(institution_id)
        candidates = list(self.names_by_id.get(identifier, []))
        for ancestor in self.ancestors(identifier):
            candidates.extend(self.names_by_id.get(ancestor, []))
        for source in self.merged_sources.get(identifier, set()):
            candidates.extend(self.names_by_id.get(source, []))
        return any(self.name_matches_text(name, evidence) for name in candidates)

    def candidates(self, evidence: Any) -> list[tuple[float, str]]:
        normalized_evidence = normalize_institution(evidence)
        evidence_tokens = set(normalized_evidence.split())
        matches = []
        for identifier in self.active_ids:
            best = 0.0
            for name in self.names_by_id.get(identifier, []):
                normalized_name = normalize_institution(name)
                signature = set(institution_signature(name))
                if normalized_name and normalized_name in normalized_evidence:
                    best = max(best, 1.0)
                elif len(signature) >= 2 and signature <= evidence_tokens:
                    best = max(best, 0.95)
                elif len(institution_acronym(name)) >= 3 and institution_acronym(name) in evidence_tokens:
                    best = max(best, 0.9)
                elif signature:
                    best = max(best, len(signature & evidence_tokens) / len(signature | evidence_tokens))
            if best >= 0.65:
                matches.append((best, identifier))
        return sorted(matches, key=lambda item: (-item[0], self.canonical_name(item[1]).casefold()))


def _paper_key(row: Mapping[str, Any]) -> str:
    return clean(row.get("paper_id")) or clean(row.get("doi")).casefold() or "|".join((normalize_institution(row.get("title")), clean(row.get("year"))))


def _authors(row: Mapping[str, Any]) -> list[str]:
    value = row.get("institution_authors") or row.get("authors") or []
    if isinstance(value, list):
        return [clean(author.get("name") if isinstance(author, dict) else author) for author in value if clean(author.get("name") if isinstance(author, dict) else author)]
    return [clean(author) for author in clean(value).split(";") if clean(author)]


def _evidence(row: Mapping[str, Any]) -> str:
    raw = clean(row.get("raw_affiliation"))
    if raw.casefold() in {
        "resolved from authoritative candidate institution metadata.",
        "resolved from authoritative candidate institution metadata",
    }:
        raw = ""
    return " | ".join(filter(None, (
        raw,
        clean(row.get("affiliation_note")),
    )))


def _finding(
    mapping: Mapping[str, Any], author: str, *, severity: str, issue_type: str,
    reason: str, recommended_action: str, suggested_id: str = "",
    resolver: InstitutionResolver,
) -> dict[str, str]:
    current_id = clean(mapping.get("institution_id")) or stable_institution_id(mapping.get("institution"))
    identity = "|".join((
        _paper_key(mapping), normalize_institution(author), current_id,
        issue_type, clean(suggested_id), normalize_institution(mapping.get("raw_affiliation")),
    ))
    return {
        "audit_id": "institution-consistency:" + hashlib.sha256(identity.encode()).hexdigest()[:20],
        "mapping_id": clean(mapping.get("mapping_id")),
        "paper_id": clean(mapping.get("paper_id")),
        "paper_title": clean(mapping.get("title")),
        "year": clean(mapping.get("year")),
        "doi": clean(mapping.get("doi")),
        "openalex_url": clean(mapping.get("openalex_url")),
        "author": author,
        "current_institution": clean(mapping.get("institution")) or resolver.canonical_name(current_id),
        "current_institution_id": current_id,
        "raw_affiliation": clean(mapping.get("raw_affiliation")),
        "suggested_canonical_institution": resolver.canonical_name(suggested_id),
        "suggested_institution_id": clean(suggested_id),
        "severity": severity,
        "issue_type": issue_type,
        "reason": reason,
        "recommended_action": recommended_action,
        "resolution_status": "unresolved",
    }


def audit_institution_consistency(
    mappings: Sequence[Mapping[str, Any]],
    institutions: Sequence[Mapping[str, Any]],
    aliases: Sequence[Mapping[str, Any]],
    hierarchy: Sequence[Mapping[str, Any]] = (),
    merge_audits: Sequence[Mapping[str, Any]] = (),
    public_records: Sequence[Mapping[str, Any]] = (),
    decisions: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, str]]:
    resolver = InstitutionResolver(institutions, aliases, hierarchy, merge_audits)
    findings: list[dict[str, str]] = []
    active = [row for row in mappings if clean(row.get("mapping_status")) in {"active", "needs_review"} and clean(row.get("institution_id")) in resolver.active_ids]

    for mapping in active:
        current_id = clean(mapping.get("institution_id"))
        evidence = _evidence(mapping)
        current_matches = resolver.evidence_matches(current_id, evidence) or resolver.name_matches_text(mapping.get("institution"), evidence)
        if not evidence or current_matches:
            specific_children = [
                identifier for score, identifier in resolver.candidates(evidence)
                if score >= 0.9 and current_id in resolver.ancestors(identifier)
            ]
            if specific_children:
                for author in _authors(mapping):
                    findings.append(_finding(mapping, author, severity="low", issue_type="parent_child_inconsistency", reason="Affiliation evidence names a confirmed child institution while the mapping points to its parent.", recommended_action="Review whether the mapping should use the more specific child institution.", suggested_id=specific_children[0], resolver=resolver))
            # A non-literal but token-equivalent form should be registered as an alias.
            raw = clean(mapping.get("raw_affiliation"))
            canonical = resolver.canonical_name(current_id)
            literal_names = resolver.names_by_id.get(current_id, [])
            if raw and canonical and not any(normalize_institution(name) in normalize_institution(raw) for name in literal_names) and resolver.name_matches_text(canonical, raw):
                for author in _authors(mapping):
                    findings.append(_finding(mapping, author, severity="low", issue_type="alias_missing", reason="Affiliation is semantically compatible but uses an unregistered institution-name variant.", recommended_action="Review and add alias if this wording recurs.", resolver=resolver))
            continue
        candidates = resolver.candidates(evidence)
        unrelated = [(score, identifier) for score, identifier in candidates if not resolver.related_ids(current_id, identifier)]
        top_score = unrelated[0][0] if unrelated else 0.0
        top_candidates = [identifier for score, identifier in unrelated if score == top_score]
        suggested_id = top_candidates[0] if top_score >= 0.9 and len(top_candidates) == 1 else ""
        issue_type = "suspicious_replacement" if suggested_id else "affiliation_mismatch"
        severity = "high" if suggested_id else "medium"
        reason = (
            f"Raw affiliation strongly matches {resolver.canonical_name(suggested_id)!r}, not the current institution; no alias, parent, or merge relationship permits the replacement."
            if suggested_id else
            "Current institution and its aliases/parents have no semantic relation to the preserved affiliation evidence."
        )
        for author in _authors(mapping):
            findings.append(_finding(mapping, author, severity=severity, issue_type=issue_type, reason=reason, recommended_action="Replace mapping after reviewing the original affiliation." if suggested_id else "Verify affiliation evidence and canonical institution.", suggested_id=suggested_id, resolver=resolver))

    by_author_paper: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for mapping in active:
        for author in _authors(mapping):
            by_author_paper[(_paper_key(mapping), normalize_institution(author))].append(mapping)
    for (_paper, normalized_author), rows in by_author_paper.items():
        for index, left in enumerate(rows):
            for right in rows[index + 1:]:
                left_id, right_id = clean(left.get("institution_id")), clean(right.get("institution_id"))
                if resolver.related_ids(left_id, right_id):
                    continue
                left_ok = resolver.evidence_matches(left_id, _evidence(left)) or resolver.name_matches_text(left.get("institution"), _evidence(left))
                right_ok = resolver.evidence_matches(right_id, _evidence(right)) or resolver.name_matches_text(right.get("institution"), _evidence(right))
                if left_ok and right_ok:
                    continue
                if left_ok == right_ok:
                    continue
                if normalize_institution(_evidence(left)) != normalize_institution(_evidence(right)):
                    continue
                author = next((name for name in _authors(left) if normalize_institution(name) == normalized_author), normalized_author)
                findings.append(_finding(left, author, severity="high", issue_type="author_institution_conflict", reason=f"Same author and paper have unrelated canonical institutions: {clean(left.get('institution'))!r} and {clean(right.get('institution'))!r}; preserved evidence does not establish two compatible affiliations.", recommended_action="Review both mappings and replace or exclude the incorrect one.", suggested_id=right_id if right_ok and not left_ok else "", resolver=resolver))

    signatures: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for identifier in resolver.active_ids:
        signature = institution_signature(resolver.canonical_name(identifier))
        if signature:
            signatures[signature].append(identifier)
    for identifiers in signatures.values():
        if len(identifiers) < 2:
            continue
        first = resolver.entities[identifiers[0]]
        placeholder = {"institution": first.get("canonical_name"), "institution_id": identifiers[0]}
        findings.append(_finding(placeholder, "", severity="low", issue_type="duplicate_institution", reason="Multiple active institution entities have semantically equivalent canonical names.", recommended_action="Review aliases and merge only with explicit confirmation.", suggested_id=identifiers[1], resolver=resolver))

    # Public markers must not contradict an explicit mapping for the same paper
    # and exact institution-author set.
    mapping_targets: dict[tuple[str, tuple[str, ...]], set[str]] = defaultdict(set)
    for mapping in active:
        mapping_targets[(_paper_key(mapping), tuple(sorted(normalize_institution(a) for a in _authors(mapping))))].add(clean(mapping.get("institution_id")))
    for record in public_records:
        if not clean(record.get("institution")) or not record.get("institution_authors"):
            continue
        authors = tuple(sorted(normalize_institution(a) for a in _authors(record)))
        expected = mapping_targets.get((_paper_key(record), authors))
        actual = clean(record.get("institution_id")) or stable_institution_id(record.get("institution"))
        if expected and all(not resolver.related_ids(actual, target) for target in expected):
            for author in _authors(record):
                findings.append(_finding(record, author, severity="high", issue_type="suspicious_replacement", reason="Public export institution contradicts the explicit curated mapping for the same paper and authors.", recommended_action="Regenerate the public export and inspect institution resolution.", suggested_id=sorted(expected)[0], resolver=resolver))

    resolved_targets = {
        clean(row.get("target_type"))
        for row in decisions
        if clean(row.get("review_queue")) == "institution_consistency"
        and clean(row.get("action")) in {"accept_mapping", "ignore_warning"}
    }
    unique: dict[str, dict[str, str]] = {}
    for finding in findings:
        target = f"institution_audit:{finding['audit_id']}"
        if target in resolved_targets:
            finding["resolution_status"] = "resolved"
        unique[finding["audit_id"]] = finding
    return sorted(unique.values(), key=lambda row: (SEVERITY_ORDER[row["severity"]], row["paper_title"].casefold(), row["author"].casefold(), row["issue_type"]))


def load_audit_inputs(
    *, mappings_path: Path = DEFAULT_MAPPINGS_PATH,
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    aliases_path: Path = DEFAULT_ALIASES_PATH,
    hierarchy_path: Path = DEFAULT_HIERARCHY_PATH,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
    decisions_path: Path = DEFAULT_DECISIONS_PATH,
    public_map_path: Path = DEFAULT_PUBLIC_MAP_PATH,
    public_papers_path: Path = DEFAULT_PUBLIC_PAPERS_PATH,
) -> dict[str, Any]:
    public_records = []
    for path in (public_map_path, public_papers_path):
        if path.exists():
            public_records.extend(_read_public(path))
    return {
        "mappings": _read_csv(mappings_path),
        "institutions": _read_csv(institutions_path),
        "aliases": _read_csv(aliases_path),
        "hierarchy": _read_csv(hierarchy_path),
        "merge_audits": _read_csv(audit_log_path),
        "decisions": read_review_decisions(decisions_path),
        "public_records": public_records,
    }


def run_repository_audit(**paths: Any) -> list[dict[str, str]]:
    return audit_institution_consistency(**load_audit_inputs(**paths))


def unresolved_high(findings: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [row for row in findings if clean(row.get("severity")) == "high" and clean(row.get("resolution_status")) != "resolved"]


def read_audit_report(path: Path = DEFAULT_REPORT_PATH) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows = _read_csv(path)
    return [{column: clean(row.get(column)) for column in REPORT_COLUMNS} for row in rows]
