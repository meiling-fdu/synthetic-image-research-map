#!/usr/bin/env python3
"""Read generated diagnostics as non-authoritative admin review queues."""

from __future__ import annotations

import csv
import fnmatch
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

try:
    from .export_candidate_map_data import paper_identity_keys
    from .paper_version_merges import (
        active_confirmed_merges,
        read_paper_version_merges,
        record_matches_merge_side,
    )
except ImportError:  # pragma: no cover - direct script execution
    from export_candidate_map_data import paper_identity_keys
    from paper_version_merges import (
        active_confirmed_merges,
        read_paper_version_merges,
        record_matches_merge_side,
    )


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
MANUAL_DIR = REPOSITORY_ROOT / "data" / "manual"
WEB_DATA_DIR = REPOSITORY_ROOT / "web" / "data"
CURATED_DIR = REPOSITORY_ROOT / "data" / "curated"

DEFAULT_MAPPINGS_PATH = CURATED_DIR / "author_institution_mappings.csv"
DEFAULT_EXCLUSIONS_PATH = CURATED_DIR / "paper_exclusions.csv"
DEFAULT_RECORD_OVERRIDES_PATH = MANUAL_DIR / "institution_record_overrides.csv"
DEFAULT_AUTHOR_OVERRIDES_PATH = MANUAL_DIR / "institution_author_overrides.csv"
DEFAULT_CORRECTIONS_PATH = MANUAL_DIR / "institution_corrections.csv"
DEFAULT_PUBLIC_PAPERS_PATH = WEB_DATA_DIR / "public_preview_papers.json"
DEFAULT_PUBLIC_MAP_PATH = WEB_DATA_DIR / "public_preview_map_data.json"
DEFAULT_PAPERS_PATH = CURATED_DIR / "papers.csv"
DEFAULT_INSTITUTIONS_PATH = CURATED_DIR / "institutions.csv"
DEFAULT_DECISIONS_PATH = CURATED_DIR / "review_decisions.csv"

QUEUE_PATHS = {
    "high_risk_marker": MANUAL_DIR / "high_risk_marker_review.csv",
    "marker_blocker": MANUAL_DIR / "paper_marker_blocker_report.csv",
    "key_paper_coverage": MANUAL_DIR / "key_paper_coverage_report.csv",
}

# A category's count, endpoint and Review destination describe the same objects.
ACTION_QUEUES = {
    "publication_venues": ("publication_venues", "Publication venues", "publication-venues"),
    "marker_blocker": ("marker_blockers", "Marker blockers", "marker-blockers"),
    "missing_author_mappings": ("missing_author_mappings", "Missing author mappings", "missing-author-mappings"),
    "missing_affiliations": ("missing_affiliations", "Missing affiliations", "missing-affiliations"),
    "missing_coordinates": ("missing_coordinates", "Missing institution locations", "missing-locations"),
    "high_risk_marker": ("high_risk_markers", "High-risk markers", "high-risk"),
    "high_risk_paper": ("high_risk_papers", "High-risk papers", "high-risk-papers"),
    "key_paper_coverage": ("key_paper_coverage_queue", "Key-paper coverage", "key-coverage"),
    "manual_import": ("manual_import_queue", "Manual imports", "manual-import"),
}
QUEUE_ENDPOINTS = {
    name: "/api/review/" + endpoint for name, endpoint in {
        "publication_venues": "publication-venues",
        "marker_blocker": "marker-blockers", "high_risk_marker": "high-risk-markers",
        "high_risk_paper": "high-risk-papers", "key_paper_coverage": "key-paper-coverage",
        "manual_import": "manual-import", "missing_coordinates": "missing-locations",
        "missing_author_mappings": "missing-author-mappings", "missing_affiliations": "missing-affiliations",
    }.items()
}
MANUAL_IMPORT_PATTERNS = (
    "key_papers_openalex_problem_review.csv",
    "key_papers_openalex_ready_all_batches.csv",
    "key_papers_*_import_ready.csv",
    "key_papers_*_manual_review.csv",
    "key_papers_*_openalex_matches.csv",
)


class AdminReviewQueueError(RuntimeError):
    """A generated queue could not be read."""


def clean(value: Any) -> str:
    return " ".join(str("" if value is None else value).split())


def _normalized_words(value: Any) -> str:
    value = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", value, flags=re.UNICODE))


def _normalized_doi(value: Any) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", clean(value), flags=re.I).casefold()


def _identity_keys(row: Mapping[str, Any]) -> set[str]:
    keys: set[str] = set()
    if clean(row.get("paper_id")):
        keys.add(f"paper:{clean(row.get('paper_id')).casefold()}")
    doi = _normalized_doi(row.get("doi"))
    if doi:
        keys.add(f"doi:{doi}")
    openalex = clean(row.get("openalex_url") or row.get("openalex_id")).casefold().rstrip("/")
    if openalex:
        if not openalex.startswith("http"):
            openalex = f"https://openalex.org/{openalex}"
        keys.add(f"openalex:{openalex}")
    title = _normalized_words(row.get("title") or row.get("requested_title"))
    year = clean(row.get("year") or row.get("publication_year"))
    if title and year:
        keys.add(f"title-year:{title}|{year}")
    return keys


def _same_paper(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_keys, right_keys = _identity_keys(left), _identity_keys(right)
    left_strong = {key for key in left_keys if not key.startswith("title-year:")}
    right_strong = {key for key in right_keys if not key.startswith("title-year:")}
    if left_strong and right_strong:
        return bool(left_strong & right_strong)
    return not (left_strong or right_strong) and bool(left_keys & right_keys)


def _authors(row: Mapping[str, Any]) -> set[str]:
    value = row.get("institution_authors") or row.get("authors") or ""
    if isinstance(value, list):
        parts = [item.get("display_name", "") if isinstance(item, dict) else item for item in value]
    else:
        parts = re.split(r"\s*;\s*", clean(value))
    return {_normalized_words(part) for part in parts if _normalized_words(part)}


def suppression_reason(
    row: Mapping[str, Any],
    *,
    mappings: Sequence[Mapping[str, Any]] = (),
    exclusions: Sequence[Mapping[str, Any]] = (),
    record_overrides: Sequence[Mapping[str, Any]] = (),
    author_overrides: Sequence[Mapping[str, Any]] = (),
    corrections: Sequence[Mapping[str, Any]] = (),
) -> str:
    """Return the curated fact that makes a generated review row non-actionable."""
    if any(clean(item.get("is_active")).casefold() in {"1", "true", "yes", "y"} and _same_paper(row, item) for item in exclusions):
        return "resolved_by_durable_exclusion"

    institution = _normalized_words(row.get("institution"))
    row_authors = _authors(row)
    active_mappings = [
        item for item in mappings
        if clean(item.get("mapping_status")).casefold() == "active" and _same_paper(row, item)
    ]
    if institution and any(_normalized_words(item.get("institution")) == institution for item in active_mappings):
        return "resolved_by_active_curated_mapping"
    if row_authors and any(_authors(item) == row_authors for item in active_mappings):
        return "superseded_by_active_curated_mapping"

    for item in record_overrides:
        if _same_paper(row, item) and (
            not institution
            or _normalized_words(item.get("institution")) == institution
            or clean(item.get("mode")).casefold() == "replace"
        ):
            return "resolved_by_active_institution_override"
    for item in author_overrides:
        if _same_paper(row, item) and (
            not row_authors or _authors(item) == row_authors
        ):
            return "resolved_by_curated_correction"
    if institution and any(
        _normalized_words(item.get("match_key")) == institution for item in corrections
    ):
        return "resolved_by_curated_correction"

    # Paper-level diagnostics without a candidate institution are resolved only
    # when their stated missing stage is exactly what an active mapping supplies.
    if not institution and active_mappings:
        diagnostic = " ".join(clean(row.get(field)).casefold() for field in (
            "blocker_type", "missing_stage", "recommended_action"
        ))
        if any(token in diagnostic for token in ("mapping", "affiliation", "marker")):
            return "resolved_by_active_curated_mapping"
    return ""


def suppress_resolved_records(
    records: Sequence[Mapping[str, Any]], **evidence: Sequence[Mapping[str, Any]]
) -> tuple[list[Dict[str, Any]], Counter[str]]:
    visible: list[Dict[str, Any]] = []
    hidden: Counter[str] = Counter()
    for source in records:
        reason = suppression_reason(source, **evidence)
        if reason:
            hidden[reason] += 1
        else:
            visible.append(dict(source))
    return visible, hidden


def read_csv(path: Path) -> list[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except (OSError, UnicodeError, csv.Error) as error:
        raise AdminReviewQueueError(f"could not read {path}: {error}") from error


def read_json(path: Path) -> list[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AdminReviewQueueError(f"could not read {path}: {error}") from error
    if isinstance(payload, dict):
        payload = payload.get("records") or payload.get("papers") or []
    return [dict(row) for row in payload if isinstance(row, dict)]


def _summary(rows: Iterable[Mapping[str, Any]], field: str) -> Dict[str, int]:
    return dict(sorted(Counter(clean(row.get(field)) or "unknown" for row in rows).items()))


PUBLIC_VISIBILITY_LABELS = {
    "visible_on_map": "Visible on map",
    "not_visible_on_map": "Not visible on map",
    "visible_through_canonical_paper": "Visible through canonical paper",
    "identity_unresolved": "Identity unresolved",
}


def build_public_visibility_index(
    public_papers: Sequence[Mapping[str, Any]],
    public_map_records: Sequence[Mapping[str, Any]],
) -> set[tuple[str, Any]]:
    """Index identities already emitted by the effective public export."""
    return {
        key
        for record in (*public_papers, *public_map_records)
        for key in paper_identity_keys(dict(record))
    }


def public_visibility_status(
    row: Mapping[str, Any],
    public_identity_index: set[tuple[str, Any]],
    merge_rows: Sequence[Mapping[str, Any]] = (),
) -> Dict[str, str]:
    """Return authoritative public visibility for one review record."""
    identities = paper_identity_keys(dict(row))
    if not identities:
        status = "identity_unresolved"
    elif any(key in public_identity_index for key in identities):
        status = "visible_on_map"
    else:
        status = "not_visible_on_map"
        for merge in active_confirmed_merges(merge_rows):
            if not record_matches_merge_side(row, merge, "duplicate"):
                continue
            canonical = {
                "title": merge.get("canonical_title"),
                "year": merge.get("canonical_year"),
                "doi": merge.get("canonical_doi"),
                "openalex_url": merge.get("canonical_openalex_url"),
            }
            if any(
                key in public_identity_index
                for key in paper_identity_keys(canonical)
            ):
                status = "visible_through_canonical_paper"
                break
    return {
        "public_visibility_status": status,
        "public_visibility_label": PUBLIC_VISIBILITY_LABELS[status],
    }


def annotate_public_visibility(
    rows: Sequence[Mapping[str, Any]],
    *,
    public_papers_path: Path = DEFAULT_PUBLIC_PAPERS_PATH,
    public_map_path: Path = DEFAULT_PUBLIC_MAP_PATH,
    merge_rows: Sequence[Mapping[str, Any]] | None = None,
) -> list[Dict[str, Any]]:
    """Annotate rows while loading/indexing effective public data only once."""
    public_index = build_public_visibility_index(
        read_json(public_papers_path), read_json(public_map_path)
    )
    merges = list(merge_rows) if merge_rows is not None else read_paper_version_merges()
    return [
        {**dict(row), **public_visibility_status(row, public_index, merges)}
        for row in rows
    ]


TERMINAL_STATUSES = {
    "confirmed", "resolved", "reviewed", "ignore", "ignored", "excluded",
    "inactive", "superseded", "archived", "rejected", "out_of_scope",
    "alias_of_confirmed", "merged", "imported", "complete",
}


def terminal_reason(row: Mapping[str, Any]) -> str:
    """Only explicit lifecycle facts suppress; missing flags are not false."""
    for field in ("effective_review_status", "review_status", "status", "paper_status", "mapping_status", "import_status",
                  "institution_status", "scope_status"):
        if clean(row.get(field)).casefold() in TERMINAL_STATUSES:
            return f"terminal_{field}"
    if clean(row.get("is_active")).casefold() in {"false", "0", "no"}:
        return "inactive_record"
    return ""


class ReviewContext:
    """Request-local evidence snapshot. Never caches generated actionable totals."""

    def __init__(self, *, mappings_path=DEFAULT_MAPPINGS_PATH,
                 exclusions_path=DEFAULT_EXCLUSIONS_PATH,
                 papers_path=DEFAULT_PAPERS_PATH,
                 institutions_path=DEFAULT_INSTITUTIONS_PATH,
                 decisions_path=DEFAULT_DECISIONS_PATH,
                 record_overrides_path=DEFAULT_RECORD_OVERRIDES_PATH,
                 author_overrides_path=DEFAULT_AUTHOR_OVERRIDES_PATH,
                 corrections_path=DEFAULT_CORRECTIONS_PATH,
                 public_papers_path=DEFAULT_PUBLIC_PAPERS_PATH,
                 public_map_path=DEFAULT_PUBLIC_MAP_PATH, merge_rows=None):
        self.rows = {
            name: read_csv(path) for name, path in {
                "mappings": mappings_path, "exclusions": exclusions_path,
                "papers": papers_path, "institutions": institutions_path,
                "decisions": decisions_path, "record_overrides": record_overrides_path,
                "author_overrides": author_overrides_path, "corrections": corrections_path,
            }.items()
        }
        self.rows["public_papers"] = read_json(public_papers_path)
        self.rows["public_markers"] = read_json(public_map_path)
        self.indexes = {}
        for name, rows in self.rows.items():
            index = defaultdict(list)
            for row in rows:
                for key in _identity_keys(row):
                    index[key].append(row)
            self.indexes[name] = index
        self.merges = list(merge_rows) if merge_rows is not None else read_paper_version_merges()
        self.public_index = build_public_visibility_index(
            self.rows["public_papers"], self.rows["public_markers"]
        )

    def matching(self, name, row):
        keys = _identity_keys(row)
        strong = {key for key in keys if not key.startswith("title-year:")}
        matches = {id(item): item for key in strong for item in self.indexes[name].get(key, [])}
        if not matches:
            # Exact title/year is necessary for title-only key-paper/import rows.
            # Conflicting strong identities never get merged by title similarity.
            for key in keys - strong:
                candidates = self.indexes[name].get(key, [])
                identities = {tuple(sorted(k for k in _identity_keys(item)
                                           if not k.startswith("title-year:"))) for item in candidates}
                if not strong and len(identities) <= 1:
                    matches.update({id(item): item for item in candidates})
                elif strong:
                    matches.update({id(item): item for item in candidates
                                    if not any(not k.startswith("title-year:") for k in _identity_keys(item))})
        return list(matches.values())

    def paper_suppression(self, row):
        if any(clean(item.get("is_active")).casefold() in {"1", "true", "yes", "y"}
               for item in self.matching("exclusions", row)):
            return "resolved_by_durable_exclusion"
        for paper in self.matching("papers", row):
            # Metadata confirmation is not confirmation of every marker.
            lifecycle = {k: v for k, v in paper.items() if k not in {"review_status", "status"}}
            if terminal_reason(lifecycle):
                return "suppressed_by_curated_paper"
            if clean(paper.get("curation_status")) in {"excluded", "inactive", "superseded", "merged"}:
                return "suppressed_by_curated_paper"
        if any(record_matches_merge_side(row, merge, "duplicate")
               for merge in active_confirmed_merges(self.merges)):
            return "superseded_by_canonical_paper"
        return ""

    def reason(self, name, row):
        reason = self.paper_suppression(row)
        if reason:
            return reason
        institution = _normalized_words(row.get("institution"))
        institution_id = clean(row.get("institution_id"))
        if any((institution_id and institution_id == clean(item.get("institution_id"))
                or institution and institution == _normalized_words(item.get("canonical_name")))
               and clean(item.get("institution_status")) in TERMINAL_STATUSES
               for item in self.rows["institutions"]):
            return "suppressed_by_inactive_institution"
        decisions = [item for item in self.matching("decisions", row)
                     if clean(item.get("review_queue")) in {name, "high_risk_marker" if name == "high_risk_paper" else name}
                     and _normalized_words(item.get("institution")) == institution]
        if decisions:
            decision = max(decisions, key=lambda item: clean(item.get("updated_at") or item.get("created_at")))
            action = clean(decision.get("action"))
            if action in {"confirm_marker", "exclude_wrong_mapping", "exclude_paper_scope",
                          "no_action_after_review", "ignore_warning", "accept_mapping", "add_paper", "add_manually"}:
                return "resolved_by_review_decision"
            if action == "unresolved":
                return ""  # Explicit reopening beats stale diagnostic status.
        if terminal_reason(row):
            return terminal_reason(row)
        if clean(row.get("recommended_action")) == "no_action":
            return "diagnostic_no_action"
        if row.get("blocker_type") == "already_mapped" or row.get("missing_stage") == "covered_as_map_marker":
            return "diagnostic_already_covered"
        mappings = self.matching("mappings", row)
        if institution and any(_normalized_words(item.get("institution")) == institution
                               and clean(item.get("mapping_status")) in {"excluded", "inactive", "superseded"}
                               for item in mappings) and not any(
                _normalized_words(item.get("institution")) == institution
                and clean(item.get("mapping_status")) == "active" for item in mappings):
            return "suppressed_by_curated_mapping"
        # Reuse marker-specific override precedence with already identity-matched evidence.
        evidence = {key: [dict(item, paper_id="matched") for item in self.matching(key, row)
                          if key == "mappings" or not (
                              clean(item.get("is_active")).casefold() in {"false", "0", "no"}
                              or clean(item.get("status")) in {"inactive", "excluded", "superseded"})]
                    for key in ("mappings", "record_overrides", "author_overrides")}
        diagnostic = " ".join(clean(row.get(field)).casefold() for field in
                              ("blocker_type", "missing_stage", "review_type"))
        if name in {"high_risk_marker", "marker_blocker", "high_risk_paper", "key_paper_coverage"} and (
                institution or any(token in diagnostic for token in ("affiliation", "mapping"))):
            reason = suppression_reason(dict(row, paper_id="matched"), **evidence,
                                        corrections=self.rows["corrections"])
            if reason:
                return reason
        curated = self.matching("papers", row)
        if name == "manual_import" and (curated or self.matching("public_papers", row)):
            return "already_imported"
        if name in {"marker_blocker", "key_paper_coverage", "high_risk_paper"} and self.matching("public_markers", row):
            return "covered_by_current_public_marker"
        return ""


def diagnostic_identities(source_rows, context):
    """Join exact identifiers, with title/year fallback only when unambiguous.

    This deduplicates work items, not author/institution entities or source files.
    Conflicting DOI/OpenAlex records are never joined on title alone.
    """
    keys_by_row = []
    parent = {}

    def root(key):
        parent.setdefault(key, key)
        while parent[key] != key:
            key = parent[key]
        return key

    for row in source_rows:
        curated = context.matching("papers", row)
        keys = _identity_keys(curated[0] if len(curated) == 1 else row)
        keys_by_row.append(keys)
        strong = sorted(k for k in keys if not k.startswith("title-year:"))
        for key in strong[1:]:
            left, right = sorted((root(strong[0]), root(key)))
            parent[right] = left
    by_title = defaultdict(set)
    for keys in keys_by_row:
        for title in (k for k in keys if k.startswith("title-year:")):
            by_title[title].update(root(k) for k in keys if not k.startswith("title-year:"))
    identities = []
    for row, keys in zip(source_rows, keys_by_row):
        strong = sorted(k for k in keys if not k.startswith("title-year:"))
        if strong:
            identity = root(strong[0])
        elif keys:
            title = sorted(keys)[0]
            identity = next(iter(by_title[title])) if len(by_title[title]) == 1 else title
        else:
            identity = json.dumps(row, sort_keys=True)
        identities.append(identity)
    return identities


def actionable_payload(name, source_rows, context, *, available=True, group_field="review_type", **metadata):
    records = []
    hidden = Counter()
    seen = {}
    for source, identity in zip(source_rows, diagnostic_identities(source_rows, context)):
        row = dict(source)
        reason = context.reason(name, row)
        if reason:
            hidden[reason] += 1
            continue
        if name == "missing_coordinates":
            identity = clean(row.get("institution_id")) or _normalized_words(row.get("institution"))
        # One work item per paper, except marker queues (paper + institution + authors).
        key = (identity, _normalized_words(row.get("institution")) if name == "high_risk_marker" else "",
               tuple(sorted(_authors(row))) if name == "high_risk_marker" else ())
        provenance = {k: row[k] for k in ("source_file", "source_row", "review_type", "missing_stage", "blocker_type") if k in row}
        if key in seen:
            seen[key]["diagnostic_sources"].append(provenance)
            hidden["duplicate_diagnostic"] += 1
            continue
        row.update(public_visibility_status(row, context.public_index, context.merges))
        row["effective_review_status"] = "unresolved"
        row["actionable"] = True
        row["actionable_id"] = "|".join((name, *map(str, key)))
        row["diagnostic_sources"] = [provenance]
        seen[key] = row
        records.append(row)
    return {
        "queue": name, "available": available, "records": records,
        "count": len(records), "total_unresolved": len(records),
        "raw_count": len(source_rows), "hidden_resolved": sum(hidden.values()),
        "suppression_reasons": dict(sorted(hidden.items())),
        "summary": _summary(records, group_field), "durable_source": False, **metadata,
    }


def build_action_queues(context, *, location_payload, author_mapping_coverage, papers, venue_aliases=None):
    """All Action Required categories, computed from one effective evidence snapshot."""
    queues = {name: load_queue(name, context=context) for name in
              ("high_risk_marker", "high_risk_paper", "marker_blocker", "key_paper_coverage")}
    queues["manual_import"] = load_manual_import_queue(context=context)
    queues["missing_coordinates"] = actionable_payload(
        "missing_coordinates", [row for row in location_payload["records"]
                                if row.get("actionable") and not row.get("has_usable_confirmed_location")], context)
    queues["missing_author_mappings"] = actionable_payload(
        "missing_author_mappings", [row for row in author_mapping_coverage.get("records", [])
                                    if row.get("mapping_status") == "zero"], context,
        available=bool(author_mapping_coverage.get("available")))
    queues["missing_affiliations"] = actionable_payload(
        "missing_affiliations", [dict(row, review_status="unresolved", effective_review_status="unresolved") for row in papers
                                 if row.get("missing_affiliation")
                                 and not any(clean(m.get("mapping_status")) == "active"
                                             for m in context.matching("mappings", row))
                                 and not context.matching("public_markers", row)], context)
    try:
        from .venue_audit import review_queue
        from .venues import read_venue_aliases
    except ImportError:
        from venue_audit import review_queue
        from venues import read_venue_aliases
    queues["publication_venues"] = review_queue(
        papers, venue_aliases if venue_aliases is not None else read_venue_aliases(),
        decisions=context.rows["decisions"])
    for name, queue in queues.items():
        queue["endpoint"] = QUEUE_ENDPOINTS[name]
    return queues


def load_queue(
    name: str,
    *,
    mappings_path: Path = DEFAULT_MAPPINGS_PATH,
    exclusions_path: Path = DEFAULT_EXCLUSIONS_PATH,
    record_overrides_path: Path = DEFAULT_RECORD_OVERRIDES_PATH,
    author_overrides_path: Path = DEFAULT_AUTHOR_OVERRIDES_PATH,
    corrections_path: Path = DEFAULT_CORRECTIONS_PATH,
    public_papers_path: Path = DEFAULT_PUBLIC_PAPERS_PATH,
    public_map_path: Path = DEFAULT_PUBLIC_MAP_PATH,
    merge_rows: Sequence[Mapping[str, Any]] | None = None,
    context: ReviewContext | None = None,
    papers_path: Path = DEFAULT_PAPERS_PATH,
    institutions_path: Path = DEFAULT_INSTITUTIONS_PATH,
    decisions_path: Path = DEFAULT_DECISIONS_PATH,
) -> Dict[str, Any]:
    path = QUEUE_PATHS.get("high_risk_marker" if name == "high_risk_paper" else name)
    if path is None:
        raise AdminReviewQueueError(f"unsupported review queue: {name}")
    source_rows = [dict(row, source_file=str(path.relative_to(REPOSITORY_ROOT)), source_row=index)
                   for index, row in enumerate(read_csv(path), 2)]
    if name in {"high_risk_marker", "high_risk_paper"}:
        source_rows = [row for row in source_rows
                       if bool(clean(row.get("institution"))) == (name == "high_risk_marker")]
    context = context or ReviewContext(
        mappings_path=mappings_path, exclusions_path=exclusions_path,
        papers_path=papers_path, institutions_path=institutions_path, decisions_path=decisions_path,
        record_overrides_path=record_overrides_path, author_overrides_path=author_overrides_path,
        corrections_path=corrections_path, public_papers_path=public_papers_path,
        public_map_path=public_map_path, merge_rows=merge_rows,
    )
    group_field = {
        "high_risk_marker": "priority",
        "high_risk_paper": "priority",
        "marker_blocker": "blocker_type",
        "key_paper_coverage": "missing_stage",
    }[name]
    return actionable_payload(name, source_rows, context, available=path.exists(),
                              group_field=group_field, source_file=str(path.relative_to(REPOSITORY_ROOT)))


def _manual_import_files() -> list[Path]:
    matches = {
        path
        for path in MANUAL_DIR.glob("*.csv")
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in MANUAL_IMPORT_PATTERNS)
    }
    return sorted(matches, key=lambda path: path.name)


def _candidate_status(row: Mapping[str, Any], filename: str) -> str:
    combined = " ".join(
        clean(row.get(field)).casefold()
        for field in ("import_status", "match_status", "status", "review_status")
    )
    if "query_failed" in combined or "query failed" in combined:
        return "query_failed"
    if "weak" in combined:
        return "weak_match"
    if "no_match" in combined or "no match" in combined:
        return "no_match"
    if "ready" in combined or "import_ready" in filename:
        return "ready"
    return "manual_review"


def load_manual_import_queue(
    *,
    mappings_path: Path = DEFAULT_MAPPINGS_PATH,
    exclusions_path: Path = DEFAULT_EXCLUSIONS_PATH,
    public_papers_path: Path = DEFAULT_PUBLIC_PAPERS_PATH,
    public_map_path: Path = DEFAULT_PUBLIC_MAP_PATH,
    merge_rows: Sequence[Mapping[str, Any]] | None = None,
    context: ReviewContext | None = None,
) -> Dict[str, Any]:
    records: list[Dict[str, Any]] = []
    files = _manual_import_files()
    for path in files:
        for index, source in enumerate(read_csv(path), start=2):
            row: Dict[str, Any] = dict(source)
            row["source_file"] = str(path.relative_to(REPOSITORY_ROOT))
            row["source_row"] = index
            row["candidate_status"] = _candidate_status(row, path.name)
            row.setdefault("candidate_title", row.get("best_match_title", ""))
            row.setdefault("candidate_year", row.get("best_match_year", ""))
            row.setdefault("venue", row.get("publication_venue", ""))
            records.append(row)
    context = context or ReviewContext(mappings_path=mappings_path, exclusions_path=exclusions_path,
                                       public_papers_path=public_papers_path,
                                       public_map_path=public_map_path, merge_rows=merge_rows)
    return actionable_payload("manual_import", records, context, available=bool(files),
                              group_field="candidate_status",
                              source_files=[str(path.relative_to(REPOSITORY_ROOT)) for path in files])


def _count_csv(path: Path) -> int:
    return len(read_csv(path))


def project_health_severity(
    key: str, value: float | int | None, *, available: bool = True
) -> str:
    """Classify a health metric using stable, maintainer-facing thresholds."""
    if not available or value is None:
        return "neutral"
    numeric = float(value)
    if key == "author_mapping_coverage":
        return (
            "good"
            if numeric >= 95
            else "warning"
            if numeric >= 90
            else "critical"
        )
    thresholds = {
        "missing_author_mappings": (10, 0),
        "missing_author_links": (50, 0),
        "missing_coordinates": (5, 0),
        "missing_affiliations": (20, 0),
    }
    if key in thresholds:
        warning_max, good_max = thresholds[key]
        return (
            "good"
            if numeric <= good_max
            else "warning"
            if numeric <= warning_max
            else "critical"
        )
    if key in {
        "high_risk_markers",
        "marker_blockers",
        "key_paper_coverage_queue",
        "manual_import_queue",
    }:
        return (
            "good"
            if numeric == 0
            else "warning"
            if numeric <= 100
            else "critical"
        )
    if key == "partial_author_mappings":
        return "good" if numeric == 0 else "warning"
    if key == "pending_locations":
        return "good" if numeric == 0 else "warning" if numeric <= 100 else "critical"
    return "neutral"


def overall_project_health(
    *,
    counts: Mapping[str, int],
    queues: Mapping[str, Mapping[str, Any]],
    author_mapping_coverage: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return a bounded heuristic maintenance score and its deductions."""
    required_queues = ("high_risk_marker", "marker_blocker")
    if not author_mapping_coverage.get("available") or any(
        not queues[name].get("available") for name in required_queues
    ):
        return {
            "available": False,
            "score": None,
            "display_value": "Needs refresh",
            "level": "Unavailable",
            "severity": "neutral",
            "note": "Heuristic maintenance score; not a paper-quality rating.",
            "explanation": (
                "Heuristic maintenance score; refresh missing reports. "
                "It is not a paper-quality rating."
            ),
            "deductions": {},
        }

    summary = author_mapping_coverage.get("summary") or {}
    coverage = max(
        0.0,
        min(100.0, float(summary.get("mapping_coverage_percentage", 0))),
    )
    high_risk_backlog = int(queues["high_risk_marker"].get("count", 0))
    blocker_backlog = int(queues["marker_blocker"].get("count", 0))
    deductions = {
        "author_mapping_coverage": min(25.0, (100.0 - coverage) * 0.25),
        "missing_coordinates": min(
            15.0, float(counts.get("papers_missing_coordinates", 0)) * 0.5
        ),
        "missing_affiliations": min(
            15.0, float(counts.get("papers_missing_affiliations", 0)) * 0.1
        ),
        "review_backlog": min(
            20.0, float(high_risk_backlog + blocker_backlog) / 150.0
        ),
        "missing_author_links": min(
            15.0, float(summary.get("total_missing_author_links", 0)) / 50.0
        ),
    }
    score = max(0, min(100, round(100.0 - sum(deductions.values()))))
    level = (
        "Excellent"
        if score >= 90
        else "Needs attention"
        if score >= 75
        else "Critical maintenance"
    )
    severity = "good" if score >= 90 else "warning" if score >= 75 else "critical"
    return {
        "available": True,
        "score": score,
        "display_value": f"{score} / 100",
        "level": level,
        "severity": severity,
        "note": "Heuristic maintenance score; not a paper-quality rating.",
        "explanation": (
            "Starts at 100. Deductions: 0.25 per uncovered author-mapping "
            "percentage point (max 25), 0.5 per missing coordinate (max 15), "
            "0.1 per missing affiliation (max 15), one per 150 combined "
            "high-risk and blocker rows (max 20), and one per 50 missing "
            "author links (max 15). This is not a paper-quality rating."
        ),
        "deductions": {
            key: round(value, 2) for key, value in deductions.items()
        },
    }


def compact_queue_breakdown(summary: Mapping[str, Any]) -> Dict[str, str]:
    """Format existing queue summary counts without recomputing the queue."""
    ordered = sorted(
        ((clean(key), int(value)) for key, value in summary.items()),
        key=lambda item: (-item[1], item[0]),
    )
    return {
        "compact": " · ".join(f"{key}: {value}" for key, value in ordered[:3]),
        "full": " · ".join(f"{key}: {value}" for key, value in ordered),
    }


def project_health_data(
    *,
    counts: Mapping[str, int],
    queues: Mapping[str, Mapping[str, Any]],
    author_mapping_coverage: Mapping[str, Any],
) -> Dict[str, Any]:
    """Arrange existing dashboard/report totals into UI-ready health groups."""

    def metric(
        key: str,
        label: str,
        value: Any,
        *,
        target: str = "",
        source_available: bool = True,
        suffix: str = "",
        navigation: Mapping[str, str] | None = None,
        detail: str = "",
        full_detail: str = "",
    ) -> Dict[str, Any]:
        return {
            "key": key,
            "label": label,
            "value": value if source_available else None,
            "display_value": (
                f"{value}{suffix}" if source_available else "Report missing"
            ),
            "available": source_available,
            "target": target,
            "navigation": dict(navigation or {}),
            "severity": project_health_severity(
                key, value, available=source_available
            ),
            "detail": detail,
            "full_detail": full_detail or detail,
        }

    def group(
        key: str, label: str, metrics: Sequence[Mapping[str, Any]]
    ) -> Dict[str, Any]:
        return {"key": key, "label": label, "metrics": list(metrics)}

    mapping_available = bool(author_mapping_coverage.get("available"))
    mapping_summary = author_mapping_coverage.get("summary") or {}
    queue_available = {
        name: bool(queue.get("available")) for name, queue in queues.items()
    }
    queue_breakdowns = {
        name: compact_queue_breakdown(queue.get("summary") or {})
        for name, queue in queues.items()
    }

    groups = [
        group(
            "corpus",
            "Corpus",
            [
                metric("total_papers", "Total papers", counts.get("total_papers", 0)),
                metric(
                    "public_preview_papers",
                    "Public preview papers",
                    counts.get("public_preview_papers", 0),
                ),
                metric("map_markers", "Map markers", counts.get("map_markers", 0)),
                metric(
                    "missing_affiliations",
                    "Missing affiliations",
                    counts.get("papers_missing_affiliations", 0),
                    target="papers",
                    navigation={"paper_filter": "missing_affiliations"},
                ),
                metric(
                    "missing_coordinates",
                    "Missing coordinates",
                    counts.get("papers_missing_coordinates", 0),
                    target="location-review",
                    navigation={"location_status": "needs_coordinates"},
                ),
            ],
        ),
        group(
            "author_mapping",
            "Author Mapping",
            [
                metric(
                    "author_mapping_coverage",
                    "Author Mapping Coverage",
                    mapping_summary.get("mapping_coverage_percentage", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    suffix="%",
                    navigation={"mapping_status": "", "mapping_sort": "rank-asc"},
                ),
                metric(
                    "complete_author_mappings",
                    "Complete author mappings",
                    mapping_summary.get("complete_mappings", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    navigation={
                        "mapping_status": "complete",
                        "mapping_sort": "rank-asc",
                    },
                ),
                metric(
                    "partial_author_mappings",
                    "Partial author mappings",
                    mapping_summary.get("partial_mappings", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    navigation={
                        "mapping_status": "partial",
                        "mapping_sort": "rank-asc",
                    },
                ),
                metric(
                    "missing_author_mappings",
                    "Missing author mappings",
                    mapping_summary.get("zero_mappings", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    navigation={
                        "mapping_status": "zero",
                        "mapping_sort": "rank-asc",
                    },
                ),
                metric(
                    "missing_author_links",
                    "Missing author links",
                    mapping_summary.get("total_missing_author_links", 0),
                    target="author-mapping-coverage",
                    source_available=mapping_available,
                    navigation={
                        "mapping_status": "",
                        "mapping_sort": "missing-desc",
                    },
                ),
            ],
        ),
        group(
            "institution_location",
            "Institution / Location",
            [
                metric(
                    "pending_locations",
                    "Pending locations",
                    counts.get("pending_location_reviews", 0),
                    target="location-review",
                    navigation={"location_status": "pending_review"},
                ),
                metric(
                    "confirmed_locations",
                    "Confirmed locations",
                    counts.get("confirmed_institution_locations", 0),
                    target="location-review",
                ),
            ],
        ),
        group(
            "review_queues",
            "Review Queues",
            [
                metric(
                    "high_risk_markers",
                    "High-risk markers",
                    queues["high_risk_marker"].get("count", 0),
                    target="high-risk",
                    source_available=queue_available["high_risk_marker"],
                    suffix=" total",
                    detail=queue_breakdowns["high_risk_marker"]["compact"],
                    full_detail=queue_breakdowns["high_risk_marker"]["full"],
                ),
                metric(
                    "marker_blockers",
                    "Marker blockers",
                    queues["marker_blocker"].get("count", 0),
                    target="marker-blockers",
                    source_available=queue_available["marker_blocker"],
                    suffix=" total",
                    detail=queue_breakdowns["marker_blocker"]["compact"],
                    full_detail=queue_breakdowns["marker_blocker"]["full"],
                ),
                metric(
                    "key_paper_coverage_queue",
                    "Key paper coverage queue",
                    queues["key_paper_coverage"].get("count", 0),
                    target="key-coverage",
                    source_available=queue_available["key_paper_coverage"],
                    suffix=" total",
                    detail=queue_breakdowns["key_paper_coverage"]["compact"],
                    full_detail=queue_breakdowns["key_paper_coverage"]["full"],
                ),
                metric(
                    "manual_import_queue",
                    "Manual import queue",
                    queues["manual_import"].get("count", 0),
                    target="manual-import",
                    source_available=queue_available["manual_import"],
                    suffix=" total",
                    detail=queue_breakdowns["manual_import"]["compact"],
                    full_detail=queue_breakdowns["manual_import"]["full"],
                ),
            ],
        ),
        group(
            "publication_exclusions",
            "Publication / Exclusions",
            [
                metric(
                    "curated_papers",
                    "Curated papers",
                    counts.get("curated_papers", 0),
                ),
                metric(
                    "active_exclusions",
                    "Active exclusions",
                    counts.get("active_exclusions", 0),
                ),
            ],
        ),
    ]
    return {
        "overall": overall_project_health(
            counts=counts,
            queues=queues,
            author_mapping_coverage=author_mapping_coverage,
        ),
        "groups": groups,
    }


def dashboard_data(
    *,
    curated_counts: Mapping[str, int],
    validation_status: Mapping[str, Any],
    git_status: Mapping[str, Any],
    author_mapping_coverage: Mapping[str, Any],
    queues: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    public_papers = read_json(WEB_DATA_DIR / "public_preview_papers.json")
    map_markers = read_json(WEB_DATA_DIR / "public_preview_map_data.json")
    counts = {
        "public_preview_papers": len(public_papers),
        "map_markers": len(map_markers),
        **dict(curated_counts),
    }
    queue_summaries = {
        name: {
            "available": queue["available"],
            "count": queue["count"],
            "summary": queue["summary"],
        }
        for name, queue in queues.items()
    }
    return {
        "counts": counts,
        "queues": {
            name: dict(summary) for name, summary in queue_summaries.items()
        },
        "author_mapping_coverage": dict(author_mapping_coverage),
        "action_queues": dict(queues),
        "action_required": [
            {"key": key, "label": label, "target": target,
             "queue": name, "endpoint": QUEUE_ENDPOINTS[name],
             "value": len(queues[name]["records"]), "available": queues[name]["available"]}
            for name, (key, label, target) in ACTION_QUEUES.items() if name in queues
        ],
        "project_health": project_health_data(
            counts=counts,
            queues=queue_summaries,
            author_mapping_coverage=author_mapping_coverage,
        ),
        "latest_validation_status": validation_status,
        "git_status": git_status,
    }
