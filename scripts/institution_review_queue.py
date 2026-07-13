#!/usr/bin/env python3
"""Persistent Admin review state for generated institution audit findings."""

from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import re
import unicodedata

try:
    from .curated_schema import INSTITUTION_REVIEW_QUEUE_COLUMNS
except ImportError:
    from curated_schema import INSTITUTION_REVIEW_QUEUE_COLUMNS


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_PATH = REPOSITORY_ROOT / "data/curated/institution_review_queue.csv"
OPEN_STATUS = "open"
RESOLVED_STATUS = "resolved"
ARCHIVED_STATUS = "archived"
ALLOWED_STATUSES = {OPEN_STATUS, RESOLVED_STATUS, ARCHIVED_STATUS}
LEGACY_TERMINAL_STATUSES = {
    "accepted",
    "ignored",
    "manually_resolved",
    "resolved_by_reaudit",
}
ALLOWED_SEVERITIES = {"high", "medium", "low"}
DEFAULT_RESOLUTION_NOTES = {
    "manually_resolved": "Confirmed existing curated institution mapping after manual review.",
    "ignore": "Resolved manually; existing mapping retained.",
    "keep_multiple_affiliations": "Multiple affiliations confirmed after manual review.",
}


class InstitutionReviewQueueError(RuntimeError):
    """The institution cleanup queue or requested action is invalid."""


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _bool(value: Any) -> bool:
    return clean(value).casefold() in {"1", "true", "yes", "y"}


def _lifecycle_status(value: Any) -> str:
    status = clean(value)
    if status in LEGACY_TERMINAL_STATUSES:
        return ARCHIVED_STATUS
    return status


def _queue_id(audit_id: str) -> str:
    digest = hashlib.sha256(audit_id.encode("utf-8")).hexdigest()[:20]
    return f"institution-review:{digest}"


def _normalized(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _group_id(row: Mapping[str, Any]) -> str:
    paper = clean(row.get("paper_id")) or clean(row.get("doi")).casefold() or _normalized(row.get("paper_title"))
    identity = f"{paper}|{_normalized(row.get('author'))}"
    return "institution-review-group:" + hashlib.sha256(identity.encode()).hexdigest()[:20]


def _provenance(mapping: Mapping[str, Any]) -> str:
    source = _normalized(mapping.get("provenance_source")).replace(" ", "_")
    if source in {"manually_confirmed", "admin_accepted", "curated_import", "automatic_import", "unresolved"}:
        return source
    if clean(mapping.get("mapping_status")) == "needs_review":
        return "unresolved"
    if any(token in source for token in ("openalex", "automatic", "pipeline", "api_import")):
        return "automatic_import"
    if any(token in source for token in ("manual", "curator", "confirmed")):
        return "manually_confirmed"
    return "curated_import" if clean(mapping.get("mapping_id")) else "unresolved"


def _classification(issue_types: set[str]) -> str:
    if issue_types & {"confirmed_mapping_changed", "suspicious_replacement"}:
        return "true conflict"
    if "alias_missing" in issue_types:
        return "alias issue"
    if "parent_child_inconsistency" in issue_types:
        return "parent-child issue"
    if "author_institution_conflict" in issue_types:
        return "possible multiple affiliation"
    return "institution review"


def _is_blocking(row: Mapping[str, Any]) -> bool:
    return (
        clean(row.get("finding_status")) == OPEN_STATUS
        and _bool(row.get("is_current"))
        and clean(row.get("severity")) == "high"
        and clean(row.get("issue_type")) in {
            "confirmed_mapping_changed", "suspicious_replacement"
        }
    )


def _same_paper(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_id = clean(left.get("paper_id"))
    right_id = clean(right.get("paper_id") or right.get("id") or right.get("display_id"))
    if left_id and right_id and left_id == right_id:
        return True
    left_doi, right_doi = clean(left.get("doi")).casefold(), clean(right.get("doi")).casefold()
    if left_doi and right_doi and left_doi == right_doi:
        return True
    return bool(
        _normalized(left.get("paper_title") or left.get("title"))
        and _normalized(left.get("paper_title") or left.get("title"))
        == _normalized(right.get("paper_title") or right.get("title"))
    )


def _mapping_authors(row: Mapping[str, Any]) -> set[str]:
    return {
        _normalized(author) for author in clean(row.get("institution_authors")).split(";")
        if _normalized(author)
    }


def _paper_author_id(paper: Mapping[str, Any], author: Any) -> str:
    expected = _normalized(author)
    authors = paper.get("authors") or []
    if isinstance(authors, str):
        return ""
    for value in authors if isinstance(authors, list) else []:
        if not isinstance(value, Mapping):
            continue
        name = value.get("name") or value.get("display_name") or value.get("author")
        if _normalized(name) == expected:
            return clean(value.get("id") or value.get("author_id") or value.get("openalex_id"))
    return ""


def _case_evidence(
    first: Mapping[str, Any],
    findings: Sequence[Mapping[str, Any]],
    mappings: Sequence[Mapping[str, Any]],
    institutions: Sequence[Mapping[str, Any]],
    aliases: Sequence[Mapping[str, Any]],
    hierarchy: Sequence[Mapping[str, Any]],
    papers: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    author = clean(first.get("author"))
    author_key = _normalized(author)
    finding_mapping_ids = {
        clean(row.get("mapping_id")) for row in findings if clean(row.get("mapping_id"))
    }
    case_mappings = [
        row for row in mappings
        if (
            (clean(row.get("mapping_id")) and clean(row.get("mapping_id")) in finding_mapping_ids)
            or (_same_paper(first, row) and author_key in _mapping_authors(row))
        )
    ]
    current_mappings = [
        row for row in case_mappings
        if clean(row.get("mapping_status")) in {"active", "needs_review"}
    ]
    historical_mappings = [
        row for row in case_mappings
        if clean(row.get("mapping_status")) not in {"active", "needs_review"}
    ]
    paper = next((row for row in papers if _same_paper(first, row)), {})
    entity_by_id = {
        clean(row.get("institution_id")): row for row in institutions
        if clean(row.get("institution_id"))
    }
    parent_by_child = {
        identifier: clean(row.get("parent_institution_id"))
        for identifier, row in entity_by_id.items()
        if clean(row.get("parent_institution_id"))
    }
    for row in hierarchy:
        if clean(row.get("review_status")) == "confirmed":
            parent_by_child[clean(row.get("child_institution_id"))] = clean(row.get("parent_institution_id"))
    children_by_parent: dict[str, list[str]] = {}
    for child, parent in parent_by_child.items():
        children_by_parent.setdefault(parent, []).append(child)
    relevant_ids = {
        clean(row.get("institution_id")) for row in case_mappings
    } | {
        clean(row.get("suggested_institution_id")) for row in findings
    }
    relationships = []
    for identifier in sorted(relevant_ids):
        if not identifier:
            continue
        entity = entity_by_id.get(identifier, {})
        parent_id = parent_by_child.get(identifier, "")
        relationships.append({
            "institution_id": identifier,
            "canonical_name": clean(entity.get("canonical_name")) or next((clean(row.get("current_institution") or row.get("suggested_canonical_institution")) for row in findings if identifier in {clean(row.get("current_institution_id")), clean(row.get("suggested_institution_id"))}), ""),
            "aliases": sorted({clean(row.get("alias_name")) for row in aliases if clean(row.get("institution_id")) == identifier and clean(row.get("review_status")) == "confirmed" and clean(row.get("alias_name"))}),
            "parent": {
                "institution_id": parent_id,
                "canonical_name": clean(entity_by_id.get(parent_id, {}).get("canonical_name")),
            } if parent_id else None,
            "children": [
                {
                    "institution_id": child_id,
                    "canonical_name": clean(entity_by_id.get(child_id, {}).get("canonical_name")),
                }
                for child_id in sorted(children_by_parent.get(identifier, []))
            ],
        })
    def mapping_evidence(row: Mapping[str, Any]) -> dict[str, str]:
        return {
        "mapping_id": clean(row.get("mapping_id")),
        "institution_name": clean(row.get("institution")),
        "institution_id": clean(row.get("institution_id")),
        "provenance_source": clean(row.get("provenance_source")),
        "provenance": _provenance(row),
        "mapping_status": clean(row.get("mapping_status")),
        "review_status": "needs review" if clean(row.get("mapping_status")) == "needs_review" else "confirmed",
        "raw_affiliation": clean(row.get("raw_affiliation")),
        "evidence_source": clean(row.get("evidence_source")),
        "evidence_url": clean(row.get("evidence_url")),
        "affiliation_note": clean(row.get("affiliation_note")),
        "review_note": clean(row.get("review_note")),
        "created_at": clean(row.get("created_at")),
        "updated_at": clean(row.get("updated_at")),
        }
    current_mapping_evidence = [mapping_evidence(row) for row in current_mappings]
    historical_mapping_evidence = [mapping_evidence(row) for row in historical_mappings]
    raw_affiliations = sorted({
        clean(value) for value in [
            *(row.get("raw_affiliation") for row in findings),
            *(row.get("raw_affiliation") for row in case_mappings),
        ] if clean(value)
    })
    candidates = sorted({
        clean(row.get("suggested_canonical_institution")) for row in findings
        if clean(row.get("suggested_canonical_institution"))
    })
    sources = sorted({
        clean(value) for row in case_mappings
        for value in (row.get("evidence_source"), row.get("provenance_source"))
        if clean(value)
    })
    reasons = [clean(row.get("reason")) for row in findings if clean(row.get("reason"))]
    return {
        "paper": {
            "title": clean(paper.get("title")) or clean(first.get("paper_title")),
            "year": clean(paper.get("year") or paper.get("publication_year")) or clean(first.get("year")),
            "venue": clean(paper.get("venue") or paper.get("venue_name")),
            "doi": clean(paper.get("doi")) or clean(first.get("doi")),
            "arxiv_id": clean(paper.get("arxiv_id")),
            "paper_url": clean(paper.get("paper_url") or paper.get("url") or paper.get("openalex_url")) or clean(first.get("openalex_url")),
        },
        "author": {"name": author, "author_id": _paper_author_id(paper, author)},
        "current_mappings": current_mapping_evidence,
        "historical_mappings": historical_mapping_evidence,
        "affiliation": {
            "raw_affiliations": raw_affiliations,
            "parsed_candidates": candidates,
            "metadata_sources": sources,
            "confidence": sorted({clean(row.get("confidence")) for row in findings if clean(row.get("confidence"))}),
        },
        "relationships": relationships,
        "audit": {
            "why_flagged": reasons,
            "risk_factors": {
                "provenance": sorted({_provenance(row) for row in case_mappings}),
                "similarity_scores": sorted({clean(row.get("similarity_score")) for row in findings if clean(row.get("similarity_score"))}),
                "issue_types": sorted({clean(row.get("issue_type")) for row in findings}),
                "severities": sorted({clean(row.get("severity")) for row in findings}),
            },
        },
        "comparison": {
            "before": [clean(row.get("institution")) for row in current_mappings],
            "evidence": raw_affiliations,
            "after": candidates,
            "reason": reasons,
        } if any(clean(row.get("issue_type")) == "suspicious_replacement" for row in findings) else None,
    }


def load_queue(path: Path = DEFAULT_QUEUE_PATH) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != INSTITUTION_REVIEW_QUEUE_COLUMNS:
            raise InstitutionReviewQueueError(
                f"unexpected institution review queue header in {path}"
            )
        rows = [dict(row) for row in reader]
    seen: set[str] = set()
    for row in rows:
        queue_id = clean(row.get("queue_id"))
        if not queue_id or queue_id in seen:
            raise InstitutionReviewQueueError("queue_id must be present and unique")
        seen.add(queue_id)
        row["finding_status"] = _lifecycle_status(row.get("finding_status"))
        if row["finding_status"] not in ALLOWED_STATUSES:
            raise InstitutionReviewQueueError(f"invalid finding status for {queue_id}")
    return rows


def save_queue(rows: Iterable[Mapping[str, Any]], path: Path = DEFAULT_QUEUE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=INSTITUTION_REVIEW_QUEUE_COLUMNS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def sync_findings(
    findings: Sequence[Mapping[str, Any]],
    *,
    mappings: Sequence[Mapping[str, Any]] | None = None,
    path: Path = DEFAULT_QUEUE_PATH,
    now: str | None = None,
) -> dict[str, Any]:
    """Upsert report findings without overwriting any human resolution."""
    if mappings is not None:
        mapping_by_id = {clean(row.get("mapping_id")): row for row in mappings}
        findings = [
            finding for finding in findings
            if not clean(finding.get("mapping_id"))
            or (
                clean(mapping_by_id.get(clean(finding.get("mapping_id")), {}).get("mapping_status"))
                in {"active", "needs_review"}
                and (
                    not clean(finding.get("current_institution_id"))
                    or clean(mapping_by_id.get(clean(finding.get("mapping_id")), {}).get("institution_id"))
                    == clean(finding.get("current_institution_id"))
                )
            )
        ]
    rows = load_queue(path)
    by_audit = {clean(row.get("audit_id")): row for row in rows}
    current_ids: set[str] = set()
    created = 0
    refreshed = 0
    archived_by_reaudit = 0
    at = now or timestamp()
    evidence_fields = (
        "mapping_id", "paper_id", "paper_title", "year", "doi",
        "openalex_url", "author", "current_institution",
        "current_institution_id", "raw_affiliation",
        "suggested_canonical_institution", "suggested_institution_id",
        "severity", "issue_type", "reason", "recommended_action",
    )
    for finding in findings:
        audit_id = clean(finding.get("audit_id"))
        if not audit_id:
            raise InstitutionReviewQueueError("audit finding is missing audit_id")
        severity = clean(finding.get("severity"))
        if severity not in ALLOWED_SEVERITIES:
            raise InstitutionReviewQueueError(f"invalid severity for {audit_id}")
        current_ids.add(audit_id)
        row = by_audit.get(audit_id)
        if row is None:
            row = {column: "" for column in INSTITUTION_REVIEW_QUEUE_COLUMNS}
            row.update({
                "queue_id": _queue_id(audit_id),
                "audit_id": audit_id,
                "finding_status": (
                    ARCHIVED_STATUS
                    if clean(finding.get("resolution_status")) == "resolved"
                    else OPEN_STATUS
                ),
                "resolution_action": (
                    "legacy_review_decision"
                    if clean(finding.get("resolution_status")) == "resolved"
                    else ""
                ),
                "resolution_note": (
                    "Imported as resolved from the legacy review decision log."
                    if clean(finding.get("resolution_status")) == "resolved"
                    else ""
                ),
                "created_at": at,
            })
            if row["finding_status"] != OPEN_STATUS:
                row["resolved_at"] = at
                row["resolved_by"] = "queue-sync"
            rows.append(row)
            by_audit[audit_id] = row
            created += 1
        else:
            refreshed += 1
        for field in evidence_fields:
            row[field] = clean(finding.get(field))
        row["is_current"] = "true"
        row["updated_at"] = at

    for row in rows:
        if clean(row.get("audit_id")) in current_ids:
            continue
        row["is_current"] = "false"
        if clean(row.get("finding_status")) == OPEN_STATUS:
            row.update({
                "finding_status": ARCHIVED_STATUS,
                "resolution_action": "resolved_by_reaudit",
                "resolution_note": "Finding no longer appears in the generated audit.",
                "resolved_at": at,
                "resolved_by": "queue-sync",
                "updated_at": at,
            })
            archived_by_reaudit += 1
    save_queue(rows, path)
    return {
        "rows": rows,
        "created": created,
        "refreshed": refreshed,
        "archived_by_reaudit": archived_by_reaudit,
    }


def reconcile_mapping_changes(
    mappings: Sequence[Mapping[str, Any]],
    *,
    path: Path = DEFAULT_QUEUE_PATH,
    now: str | None = None,
) -> dict[str, Any]:
    """Retire stale open findings while retaining their queue rows as history."""
    rows = load_queue(path)
    mapping_by_id = {clean(row.get("mapping_id")): row for row in mappings}
    at = now or timestamp()
    resolved = 0
    for row in rows:
        if clean(row.get("finding_status")) != OPEN_STATUS or not _bool(row.get("is_current")):
            continue
        mapping_id = clean(row.get("mapping_id"))
        if not mapping_id or mapping_id not in mapping_by_id:
            continue
        mapping = mapping_by_id[mapping_id]
        active = clean(mapping.get("mapping_status")) in {"active", "needs_review"}
        same_institution = (
            not clean(row.get("current_institution_id"))
            or clean(row.get("current_institution_id")) == clean(mapping.get("institution_id"))
        )
        if active and same_institution:
            continue
        row.update({
            "finding_status": ARCHIVED_STATUS,
            "resolution_action": "mapping_excluded" if not active else "mapping_replaced",
            "resolution_note": (
                "Linked mapping is excluded; finding retained as historical audit evidence."
                if not active else
                "Linked mapping now targets another institution; prior finding retained as historical audit evidence."
            ),
            "is_current": "false",
            "resolved_at": at,
            "resolved_by": "mapping-sync",
            "updated_at": at,
        })
        resolved += 1
    if resolved:
        save_queue(rows, path)
    return {"rows": rows, "resolved": resolved}


def unresolved(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    return [
        dict(row) for row in rows
        if clean(row.get("finding_status")) == OPEN_STATUS
        and _bool(row.get("is_current"))
    ]


def queue_payload(
    rows: Sequence[Mapping[str, Any]],
    mappings: Sequence[Mapping[str, Any]] = (),
    institutions: Sequence[Mapping[str, Any]] = (),
    aliases: Sequence[Mapping[str, Any]] = (),
    hierarchy: Sequence[Mapping[str, Any]] = (),
    papers: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Return actionable open cases separately from read-only lifecycle history."""
    mapping_by_id = {clean(row.get("mapping_id")): row for row in mappings}
    all_rows = [dict(row) for row in rows]
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in all_rows:
        row["provenance"] = _provenance(mapping_by_id.get(clean(row.get("mapping_id")), {}))
        row["is_blocking"] = "true" if _is_blocking(row) else "false"
        grouped.setdefault(_group_id(row), []).append(row)
    severity_rank = {"high": 0, "medium": 1, "low": 2}
    cases = []
    archived_cases = []
    for group_id, findings in grouped.items():
        open_findings = [
            row for row in findings
            if clean(row.get("finding_status")) == OPEN_STATUS and _bool(row.get("is_current"))
        ]
        terminal_findings = [row for row in findings if row not in open_findings]

        def build_case(
            display_findings: Sequence[dict[str, str]], lifecycle_status: str
        ) -> dict[str, Any]:
            first = display_findings[0]
            issue_types = {
                clean(row.get("issue_type")) for row in display_findings
            }
            provenance_values = sorted({
                clean(row.get("provenance")) for row in display_findings
                if clean(row.get("provenance"))
            })
            case_mappings = [
                row for row in mappings
                if _same_paper(first, row)
                and _normalized(first.get("author")) in _mapping_authors(row)
            ]
            active_mappings = [
                row for row in case_mappings
                if clean(row.get("mapping_status")) in {"active", "needs_review"}
            ]
            historical_mappings = [
                row for row in case_mappings
                if clean(row.get("mapping_status")) not in {"active", "needs_review"}
            ]
            active_ids = {
                clean(row.get("institution_id")) for row in active_mappings
            }
            historical_institutions = {
                clean(row.get("institution")) for row in historical_mappings
                if clean(row.get("institution"))
            } | {
                clean(row.get("current_institution")) for row in findings
                if clean(row.get("current_institution"))
                and clean(row.get("current_institution_id")) not in active_ids
            }
            return {
                **first,
                "review_group_id": group_id,
                "queue_ids": [
                    clean(row.get("queue_id")) for row in display_findings
                    if lifecycle_status == OPEN_STATUS
                ],
                "findings": list(display_findings),
                "current_institutions": sorted({
                    clean(row.get("institution")) for row in active_mappings
                    if clean(row.get("institution"))
                }),
                "historical_institutions": sorted(historical_institutions),
                "historical_findings": terminal_findings,
                "suggested_institutions": sorted({
                    clean(row.get("suggested_canonical_institution"))
                    for row in display_findings
                    if clean(row.get("suggested_canonical_institution"))
                }),
                "evidence": sorted({
                    clean(row.get("raw_affiliation")) for row in findings
                    if clean(row.get("raw_affiliation"))
                }),
                "issue_types": sorted(issue_types),
                "classification": _classification(issue_types),
                "provenance_values": provenance_values,
                "provenance": (
                    provenance_values[0]
                    if len(provenance_values) == 1 else "mixed"
                ),
                "status": lifecycle_status,
                "severity": min(
                    (clean(row.get("severity")) for row in display_findings),
                    key=lambda value: severity_rank.get(value, 9),
                ),
                "is_blocking": (
                    lifecycle_status == OPEN_STATUS
                    and any(_is_blocking(row) for row in display_findings)
                ),
                "evidence_detail": _case_evidence(
                    first, findings, mappings, institutions, aliases,
                    hierarchy, papers
                ),
            }

        if open_findings:
            cases.append(build_case(open_findings, OPEN_STATUS))
        if terminal_findings:
            history_status = (
                ARCHIVED_STATUS
                if any(clean(row.get("finding_status")) == ARCHIVED_STATUS
                       for row in terminal_findings)
                else RESOLVED_STATUS
            )
            archived_cases.append(build_case(terminal_findings, history_status))
    cases.sort(key=lambda row: (severity_rank.get(clean(row.get("severity")), 9), clean(row.get("paper_title")).casefold(), clean(row.get("author")).casefold()))
    archived_cases.sort(key=lambda row: clean(row.get("updated_at")), reverse=True)
    open_rows = unresolved(rows)
    blockers = [row for row in open_rows if _is_blocking(row)]
    return {
        "records": cases,
        "archived_records": archived_cases,
        "total_unresolved": len(open_rows),
        "hidden_resolved": len(rows) - len(open_rows),
        "resolved_count": sum(
            clean(row.get("finding_status")) == RESOLVED_STATUS for row in rows
        ),
        "archived_count": sum(
            clean(row.get("finding_status")) == ARCHIVED_STATUS for row in rows
        ),
        "blocking_count": len(blockers),
        "summary": {
            severity: sum(clean(row.get("severity")) == severity for row in open_rows)
            for severity in ("high", "medium", "low")
        },
    }


def resolve_rows(
    queue_ids: Sequence[str],
    action: str,
    note: str,
    *,
    resolved_by: str = "admin",
    path: Path = DEFAULT_QUEUE_PATH,
    now: str | None = None,
) -> list[dict[str, str]]:
    supported_actions = {
        "accept_suggestion",
        "replace_mapping",
        "ignore",
        "manually_resolved",
        "keep_multiple_affiliations",
    }
    if action not in supported_actions:
        raise InstitutionReviewQueueError("unsupported institution cleanup action")
    resolution_note = clean(note) or DEFAULT_RESOLUTION_NOTES.get(action, "")
    if not resolution_note:
        raise InstitutionReviewQueueError(
            "review note is required for mapping replacement actions"
        )
    requested = {clean(value) for value in queue_ids if clean(value)}
    if not requested:
        raise InstitutionReviewQueueError("at least one queue_id is required")
    rows = load_queue(path)
    selected = [row for row in rows if clean(row.get("queue_id")) in requested]
    if len(selected) != len(requested):
        raise InstitutionReviewQueueError("one or more cleanup findings were not found")
    if any(clean(row.get("finding_status")) != OPEN_STATUS or not _bool(row.get("is_current")) for row in selected):
        raise InstitutionReviewQueueError("only current open findings can be resolved")
    at = now or timestamp()
    for row in selected:
        row.update({
            "finding_status": RESOLVED_STATUS,
            "resolution_action": action,
            "resolution_note": resolution_note,
            "resolved_at": at,
            "resolved_by": clean(resolved_by) or "admin",
            "updated_at": at,
        })
    save_queue(rows, path)
    return [dict(row) for row in selected]


def compatible_mapping_fixes(rows: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    """Return mapping -> suggestion for a safe batch, rejecting conflicts."""
    fixes: dict[str, str] = {}
    for row in rows:
        mapping_id = clean(row.get("mapping_id"))
        suggestion = clean(row.get("suggested_institution_id"))
        if not mapping_id or not suggestion:
            raise InstitutionReviewQueueError(
                "every accepted finding must identify a mapping and suggestion"
            )
        existing = fixes.get(mapping_id)
        if existing and existing != suggestion:
            raise InstitutionReviewQueueError(
                "selected findings contain conflicting fixes for one mapping"
            )
        fixes[mapping_id] = suggestion
    return fixes
