"""Paper-specific author decisions in the existing append-only curation audit.

Missing text is never evidence of independence. Only an explicit reviewed event
can distinguish a publication's non-institutional author from an unresolved one.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

try:
    from .curated_mappings import paper_identity_keys
    from .name_matching import canonical_name_key
except ImportError:
    from curated_mappings import paper_identity_keys
    from name_matching import canonical_name_key


AUDIT_PATH = Path(__file__).resolve().parents[1] / "data/curated/institution_audit_log.csv"
ACTION = "author_affiliation_review"
STATUSES = {"mapped", "non_institutional", "unresolved"}
NON_INSTITUTIONAL_KINDS = {"independent", "role_only", "contact_only"}


def load_author_reviews(path=None):
    path = Path(path or AUDIT_PATH)
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [r for r in csv.DictReader(handle) if r.get("action") == ACTION]


def review_payload(row):
    """Validate the additive event payload; ordinary audit events are untouched."""
    try:
        payload = json.loads(row.get("confirmation_text") or "")
    except (ValueError, TypeError) as error:
        raise ValueError("author review requires a JSON confirmation payload") from error
    if not isinstance(payload, dict) or payload.get("status") not in STATUSES:
        raise ValueError("author review status must be mapped, non_institutional or unresolved")
    for key in ("audit_id", "paper_id", "affected_authors", "evidence_url", "review_note", "created_at"):
        if not str(row.get(key) or "").strip():
            raise ValueError(f"author review requires {key}")
    if ";" in row["affected_authors"]:
        raise ValueError("author review must identify exactly one author")
    if any(row.get(key) for key in ("institution_id", "mapping_id", "location_id")):
        raise ValueError("author review must not create an institution, mapping or location")
    if payload["status"] == "non_institutional" and (
        payload.get("reason_kind") not in NON_INSTITUTIONAL_KINDS
        or not str(payload.get("source_text") or "").strip()
    ):
        raise ValueError("non-institutional review requires source text and a supported reason kind")
    return payload


def strong_keys(record):
    return [key for key in paper_identity_keys(record) if not key.startswith("title")]


class AuthorReviewIndex:
    def __init__(self, rows=()):
        self.by_author = {}
        # Timestamp wins; CSV order breaks ties, matching append-only review history.
        for row in sorted(rows, key=lambda r: r.get("created_at", "")):
            if row.get("action") != ACTION:
                continue
            payload = review_payload(row)
            identity = {"paper_id": row["paper_id"], "doi": payload.get("doi", "")}
            if row["paper_id"].startswith("openalex:"):
                identity["openalex_url"] = "https://openalex.org/" + row["paper_id"].split(":", 1)[1]
            author = canonical_name_key(row["affected_authors"])
            decision = {**payload, "review_id": row["audit_id"],
                        "evidence_url": row["evidence_url"], "review_note": row["review_note"]}
            for key in strong_keys(identity):
                self.by_author[(key, author)] = decision

    def get(self, paper, author):
        name = canonical_name_key(author)
        matches = [self.by_author[(key, name)] for key in strong_keys(paper)
                   if (key, name) in self.by_author]
        if matches and any(m != matches[0] for m in matches):
            raise ValueError("conflicting author review identities")
        return matches[0] if matches else None


def is_non_institutional(author):
    review = author.get("affiliation_review") or {}
    if not isinstance(review, dict):
        return False
    return (
        author.get("affiliation_status") == "non_institutional"
        and not author.get("affiliation_indices")
        and not author.get("institution_indices")
        and review.get("status") == "non_institutional"
        and review.get("reason_kind") in NON_INSTITUTIONAL_KINDS
        and bool(review.get("source_text") and review.get("evidence_url") and review.get("review_id"))
    )


def annotate_author(paper, author, index):
    result = dict(author)
    decision = index.get(paper, author.get("name"))
    result.pop("affiliation_review", None)
    mapped = bool(author.get("affiliation_indices") or author.get("institution_indices"))
    if decision:
        if mapped and decision["status"] != "mapped":
            raise ValueError(f"reviewed {decision['status']} author has an institution mapping: {author['name']}")
        if not mapped and decision["status"] == "mapped":
            raise ValueError(f"reviewed mapped author has no institution mapping: {author['name']}")
        result["affiliation_review"] = dict(decision)
    result["affiliation_status"] = "mapped" if mapped else (decision or {}).get("status", "unresolved")
    return result


def affiliation_counts(authors):
    counts = dict.fromkeys(("mapped", "non_institutional", "unresolved"), 0)
    for author in authors:
        if not isinstance(author, dict):
            counts["unresolved"] += 1
            continue
        status = ("mapped" if author.get("affiliation_indices") or author.get("institution_indices")
                  else "non_institutional" if is_non_institutional(author) else "unresolved")
        counts[status] += 1
    return counts


def author_status_errors(author):
    status = author.get("affiliation_status")
    if status is None:  # Older public snapshots remain readable.
        return []
    if status not in STATUSES:
        return ["invalid author affiliation_status"]
    if "affiliation_review" in author and not isinstance(author["affiliation_review"], dict):
        return ["author affiliation_review must be an object"]
    mapped = bool(author.get("affiliation_indices"))
    if (status == "mapped") != mapped:
        return ["author affiliation_status conflicts with institution indices"]
    if status == "non_institutional" and not is_non_institutional(author):
        return ["non-institutional author requires an explicit source-backed review"]
    return []


def review_mapping_conflicts(rows, mappings):
    index = AuthorReviewIndex(rows)
    conflicts = []
    for mapping in mappings:
        if mapping.get("mapping_status") != "active":
            continue
        for name in (mapping.get("institution_authors") or "").split(";"):
            decision = index.get(mapping, name.strip())
            if decision and decision["status"] != "mapped":
                conflicts.append(f"author review conflicts with active mapping {mapping.get('mapping_id')}: {name.strip()}")
    return conflicts
