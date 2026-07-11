#!/usr/bin/env python3
"""Serve the local maintainer paper browser and durable exclusion workflow."""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import ipaddress
import json
import logging
import re
import secrets
import sys
import threading
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, DefaultDict, Dict, Iterable, List, Mapping, Sequence, Tuple
from urllib.parse import parse_qs, urlsplit

try:
    from .admin_workflows import (
        AdminWorkflowError,
        git_status_result,
        run_workflow,
    )
    from .curated_schema import ALLOWED_EXCLUSION_REASONS
    from .arxiv_autofill import ArxivLookupError, autofill_public_map_arxiv_ids
    from .curated_papers import (
        DEFAULT_CURATED_PAPERS_PATH,
        CuratedPaperError,
        DuplicatePaperError,
        create_curated_paper,
        update_curated_paper,
    )
    from .curated_mappings import (
        DEFAULT_LOCATION_REVIEW_PATH,
        DEFAULT_MAPPINGS_PATH,
        CuratedMappingError,
        DuplicateMappingError,
        create_mapping,
        create_mapping_candidates,
        exclude_mapping,
        load_location_reviews,
        load_mappings,
        location_reviews_for_paper,
        mapping_location_state,
        mappings_for_paper,
        replace_all_mappings,
        update_mapping,
        save_location_reviews,
    )
    from .curated_locations import (
        DEFAULT_INSTITUTION_ALIASES_PATH,
        DEFAULT_INSTITUTION_LOCATIONS_PATH,
        CuratedLocationError,
        confirm_alias,
        create_or_update_confirmed_location,
        location_review_payload,
        load_confirmed_locations,
        load_institution_aliases,
        normalize_institution_name,
        mark_queue_row,
        save_queue_metadata,
    )
    from .openalex_paper_search import (
        OpenAlexFetchError,
        OpenAlexSearchInputError,
        search_openalex_papers,
    )
    from .paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        restore_active_exclusions,
        upsert_active_exclusion,
    )
    from .admin_review_queues import (
        AdminReviewQueueError,
        dashboard_data,
        load_manual_import_queue,
        load_queue,
    )
    from .review_decisions import (
        DEFAULT_REVIEW_DECISIONS_PATH,
        ReviewDecisionError,
        upsert_review_decision,
    )
except ImportError:
    from admin_workflows import (
        AdminWorkflowError,
        git_status_result,
        run_workflow,
    )
    from curated_schema import ALLOWED_EXCLUSION_REASONS
    from arxiv_autofill import ArxivLookupError, autofill_public_map_arxiv_ids
    from curated_papers import (
        DEFAULT_CURATED_PAPERS_PATH,
        CuratedPaperError,
        DuplicatePaperError,
        create_curated_paper,
        update_curated_paper,
    )
    from curated_mappings import (
        DEFAULT_LOCATION_REVIEW_PATH,
        DEFAULT_MAPPINGS_PATH,
        CuratedMappingError,
        DuplicateMappingError,
        create_mapping,
        create_mapping_candidates,
        exclude_mapping,
        load_location_reviews,
        load_mappings,
        location_reviews_for_paper,
        mapping_location_state,
        mappings_for_paper,
        replace_all_mappings,
        update_mapping,
        save_location_reviews,
    )
    from curated_locations import (
        DEFAULT_INSTITUTION_ALIASES_PATH,
        DEFAULT_INSTITUTION_LOCATIONS_PATH,
        CuratedLocationError,
        confirm_alias,
        create_or_update_confirmed_location,
        location_review_payload,
        load_confirmed_locations,
        load_institution_aliases,
        normalize_institution_name,
        mark_queue_row,
        save_queue_metadata,
    )
    from openalex_paper_search import (
        OpenAlexFetchError,
        OpenAlexSearchInputError,
        search_openalex_papers,
    )
    from paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        restore_active_exclusions,
        upsert_active_exclusion,
    )
    from admin_review_queues import (
        AdminReviewQueueError,
        dashboard_data,
        load_manual_import_queue,
        load_queue,
    )
    from review_decisions import (
        DEFAULT_REVIEW_DECISIONS_PATH,
        ReviewDecisionError,
        upsert_review_decision,
    )

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPOSITORY_ROOT / "web"
PUBLIC_PAPERS_PATH = WEB_DIR / "data" / "public_preview_papers.json"
PUBLIC_MAP_PATH = WEB_DIR / "data" / "public_preview_map_data.json"
AUTHOR_MAPPING_REPORT_PATH = (
    REPOSITORY_ROOT / "data" / "manual" / "missing_author_mappings_report.csv"
)
AUTHOR_MAPPING_MARKDOWN_PATH = (
    REPOSITORY_ROOT / "docs" / "missing_author_mappings_report.md"
)
CURATED_PAPERS_PATH = DEFAULT_CURATED_PAPERS_PATH
CURATED_EXCLUSIONS_PATH = DEFAULT_EXCLUSIONS_PATH
CURATED_MAPPINGS_PATH = DEFAULT_MAPPINGS_PATH
LOCATION_REVIEW_PATH = DEFAULT_LOCATION_REVIEW_PATH
INSTITUTION_LOCATIONS_PATH = DEFAULT_INSTITUTION_LOCATIONS_PATH
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
TRUE_VALUES = {"1", "true", "yes", "y"}
MAX_REQUEST_BYTES = 64 * 1024
EXCLUSION_WRITE_LOCK = threading.Lock()
CURATED_PAPER_WRITE_LOCK = threading.Lock()
ARXIV_AUTOFILL_LOCK = threading.Lock()
ARXIV_AUTOFILL_STATE_LOCK = threading.Lock()
ARXIV_AUTOFILL_STATE: Dict[str, Any] = {
    "status": "idle",
    "total_eligible_papers": 0,
    "papers_requiring_lookup": 0,
    "processed_lookups": 0,
    "exact_matches_added": 0,
    "no_matches": 0,
    "ambiguous_matches": 0,
    "failed_lookups": 0,
    "current_paper_title": "",
    "start_time": None,
    "completion_time": None,
    "final_error": "",
    "result": None,
}
CURATED_MAPPING_WRITE_LOCK = threading.Lock()
CURATED_LOCATION_WRITE_LOCK = threading.Lock()
REVIEW_DECISION_WRITE_LOCK = threading.Lock()
AUTHOR_MAPPING_REPORT_WRITE_LOCK = threading.Lock()

AUTHOR_MAPPING_COVERAGE_ENDPOINTS = {
    "/api/review/author-mapping-coverage",
    "/api/reports/author-mapping-coverage",
}
AUTHOR_MAPPING_GENERATE_ENDPOINT = (
    "/api/review/author-mapping-coverage/generate"
)

WORKFLOW_ENDPOINTS = {
    "/api/run-curated-validation": "curated_validation",
    "/api/export-preview": "export_preview",
    "/api/run-public-validation": "public_validation",
    "/api/run-full-refresh": "full_refresh",
    "/api/publish-changes": "publish_changes",
}

STATIC_ROUTES = {
    "/admin/": (WEB_DIR / "admin.html", "text/html; charset=utf-8"),
    "/admin.js": (WEB_DIR / "admin.js", "text/javascript; charset=utf-8"),
    "/admin.css": (WEB_DIR / "admin.css", "text/css; charset=utf-8"),
    "/docs/missing_author_mappings_report.md": (
        AUTHOR_MAPPING_MARKDOWN_PATH,
        "text/markdown; charset=utf-8",
    ),
}
LOGGER = logging.getLogger(__name__)


class AdminDataError(RuntimeError):
    """An expected local data error that should not produce a traceback."""


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalized_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalized_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean(value),
        flags=re.IGNORECASE,
    ).casefold()


def normalized_openalex_url(value: Any) -> str:
    return clean(value).casefold().rstrip("/")


def record_year(record: Mapping[str, Any]) -> str:
    return clean(record.get("year") or record.get("publication_year"))


def title_year_key(record: Mapping[str, Any]) -> str:
    title = normalized_title(record.get("title"))
    year = record_year(record)
    return f"{title}|{year}" if title and year else ""


def identity_keys(record: Mapping[str, Any]) -> List[str]:
    keys: List[str] = []
    openalex_url = normalized_openalex_url(record.get("openalex_url"))
    doi = normalized_doi(record.get("doi"))
    paper_id = clean(record.get("paper_id")).casefold()
    title_key = title_year_key(record)
    if openalex_url:
        keys.append(f"openalex:{openalex_url}")
    if doi:
        keys.append(f"doi:{doi}")
    if paper_id:
        keys.append(f"paper_id:{paper_id}")
    if title_key:
        keys.append(f"title_year:{title_key}")
    return keys


def display_id(record: Mapping[str, Any]) -> str:
    existing_id = clean(record.get("display_id") or record.get("id"))
    if existing_id:
        return existing_id
    openalex_url = clean(record.get("openalex_url")).rstrip("/")
    if openalex_url:
        return f"openalex:{openalex_url.rsplit('/', 1)[-1]}"
    doi = normalized_doi(record.get("doi"))
    if doi:
        return f"doi:{doi}"
    paper_id = clean(record.get("paper_id"))
    if paper_id:
        return paper_id
    key = title_year_key(record) or clean(record.get("title")).casefold()
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"title:{digest}"


def parse_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    return clean(value).casefold() in TRUE_VALUES


def parse_year(value: Any) -> Any:
    text = clean(value)
    if re.fullmatch(r"[+-]?\d+", text):
        return int(text)
    return text


def parse_people(value: Any) -> List[str]:
    if isinstance(value, list):
        return [clean(item) for item in value if clean(item)]
    text = clean(value)
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [clean(item) for item in parsed if clean(item)]
    separator = ";" if ";" in text else "|" if "|" in text else None
    if separator:
        return [clean(item) for item in text.split(separator) if clean(item)]
    return [text]


def read_json_records(path: Path) -> List[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AdminDataError(f"could not read {path}: {error}") from error
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list) or not all(
        isinstance(record, dict) for record in records
    ):
        raise AdminDataError(f"{path} does not contain a valid records array")
    return [dict(record) for record in records]


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except (OSError, UnicodeError, csv.Error) as error:
        raise AdminDataError(f"could not read {path}: {error}") from error


def load_author_mapping_coverage(
    path: Path = AUTHOR_MAPPING_REPORT_PATH, *, unresolved_only: bool = False
) -> Dict[str, Any]:
    """Load the fixed generated author-mapping report for the local dashboard."""
    if not path.exists():
        raise AdminDataError(
            "Author mapping coverage report is missing. Run the refresh pipeline "
            "to generate data/manual/missing_author_mappings_report.csv."
        )
    rows = read_csv_rows(path)
    required_fields = {
        "priority_rank",
        "mapping_status",
        "priority",
        "triage_status",
        "suggested_action",
        "public_impact",
        "current_mapping_state",
        "known_canonical_institutions",
        "existing_mapping_authors",
        "suggested_author_matches",
        "raw_affiliation_evidence",
        "title",
        "year",
        "is_key_paper",
        "missing_authors",
        "missing_author_names",
        "marker_count",
    }
    if rows:
        missing_fields = required_fields - set(rows[0])
        if missing_fields:
            raise AdminDataError(
                "Author mapping coverage report is missing required columns: "
                + ", ".join(sorted(missing_fields))
            )

    records: List[Dict[str, Any]] = []
    for index, row in enumerate(rows, start=2):
        try:
            priority_rank = int(clean(row.get("priority_rank")))
            missing_authors = int(clean(row.get("missing_authors")) or 0)
            marker_count = int(clean(row.get("marker_count")) or 0)
        except ValueError as error:
            raise AdminDataError(
                f"Author mapping coverage report has invalid numeric data on row {index}."
            ) from error
        status = clean(row.get("mapping_status")).casefold()
        if status not in {"complete", "partial", "zero"}:
            raise AdminDataError(
                f"Author mapping coverage report has invalid status on row {index}."
            )
        record: Dict[str, Any] = dict(row)
        record.update(
            {
                "priority_rank": priority_rank,
                "missing_authors": missing_authors,
                "marker_count": marker_count,
                "is_key_paper": clean(row.get("is_key_paper")).casefold()
                in TRUE_VALUES,
                "is_curated_paper": clean(row.get("is_curated_paper")).casefold()
                in TRUE_VALUES,
                "mapping_status": status,
            }
        )
        for field in ("total_authors", "mapped_authors"):
            try:
                record[field] = int(clean(row.get(field)) or 0)
            except ValueError as error:
                raise AdminDataError(
                    f"Author mapping coverage report has invalid numeric data on row {index}."
                ) from error
        records.append(record)

    records.sort(key=lambda row: row["priority_rank"])
    counts = {
        status: sum(row["mapping_status"] == status for row in records)
        for status in ("complete", "partial", "zero")
    }
    total = len(records)
    complete = counts["complete"]
    summary = {
        "total_public_papers": total,
        "complete_mappings": complete,
        "partial_mappings": counts["partial"],
        "zero_mappings": counts["zero"],
        "total_missing_author_links": sum(
            row["missing_authors"] for row in records
        ),
        "mapping_coverage_percentage": round(
            (complete / total * 100) if total else 0.0, 1
        ),
        "map_markers_reconciled": sum(row["marker_count"] for row in records),
    }
    all_records = records
    hidden_complete = sum(row["mapping_status"] == "complete" for row in all_records)
    if unresolved_only:
        records = [row for row in all_records if row["mapping_status"] != "complete"]
    return {
        "available": True,
        "summary": summary,
        "records": records,
        "total_unresolved": len(records),
        "hidden_resolved": hidden_complete if unresolved_only else 0,
        "suppression_reasons": (
            {"resolved_by_active_curated_mapping": hidden_complete}
            if unresolved_only and hidden_complete
            else {}
        ),
        "report_url": "/docs/missing_author_mappings_report.md",
        "source": "data/manual/missing_author_mappings_report.csv",
    }


def generate_author_mapping_report() -> Dict[str, Any]:
    """Run the whitelisted local report-only workflow."""
    return run_workflow("author_mapping_report")


def ensure_author_mapping_report(
    path: Path = AUTHOR_MAPPING_REPORT_PATH,
    generator: Callable[[], Mapping[str, Any]] = generate_author_mapping_report,
    companion_path: Path | None = None,
) -> Dict[str, Any]:
    """Generate the report once when the Admin starts without one."""
    if path.exists() and (
        companion_path is None or companion_path.exists()
    ):
        return {
            "success": True,
            "generated": False,
            "message": "Report already exists.",
        }
    result = dict(generator())
    outputs_exist = path.exists() and (
        companion_path is None or companion_path.exists()
    )
    success = bool(result.get("success")) and outputs_exist
    return {
        **result,
        "success": success,
        "generated": success,
        "message": (
            "Author mapping report generated."
            if success
            else "Author mapping report could not be generated."
        ),
    }


def unavailable_author_mapping_coverage(
    message: str = "Author mapping report has not been generated.",
) -> Dict[str, Any]:
    return {
        "available": False,
        "message": message,
        "summary": {},
        "records": [],
        "report_url": "/docs/missing_author_mappings_report.md",
        "source": "data/manual/missing_author_mappings_report.csv",
    }


def curated_paper_record(row: Mapping[str, str]) -> Dict[str, Any]:
    record: Dict[str, Any] = dict(row)
    record["year"] = parse_year(row.get("year"))
    record["publication_year"] = record["year"]
    record["authors"] = parse_people(row.get("authors"))
    record["coverage_status"] = clean(row.get("scope_status")) or "curated_only"
    record["has_map_location"] = False
    record["map_record_count"] = 0
    record["missing_affiliation"] = True
    record["missing_coordinates"] = False
    record["notes"] = clean(row.get("review_note"))
    record["record_source"] = "curated_only"
    return record


def exclusion_only_paper_record(row: Mapping[str, str]) -> Dict[str, Any]:
    record: Dict[str, Any] = dict(row)
    record["year"] = parse_year(row.get("year"))
    record["publication_year"] = record["year"]
    record["authors"] = []
    record["coverage_status"] = "excluded"
    record["has_map_location"] = False
    record["map_record_count"] = 0
    record["missing_affiliation"] = False
    record["missing_coordinates"] = False
    record["notes"] = clean(row.get("review_note"))
    record["record_source"] = "exclusion_only"
    return record


def marker_for_api(record: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "id": clean(record.get("id")),
        "institution": clean(record.get("institution")),
        "institution_authors": record.get("institution_authors") or [],
        "city": clean(record.get("city")),
        "country_code": clean(record.get("country_code")),
        "latitude": record.get("latitude"),
        "longitude": record.get("longitude"),
        "lat": record.get("latitude"),
        "lon": record.get("longitude"),
        "resolution_method": clean(record.get("resolution_method")),
        "resolution_confidence": clean(record.get("resolution_confidence")),
        "needs_review": parse_boolean(record.get("needs_review")),
    }


def index_by_identity(
    records: Iterable[Mapping[str, Any]],
) -> DefaultDict[str, List[Mapping[str, Any]]]:
    index: DefaultDict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        for key in identity_keys(record):
            index[key].append(record)
    return index


def matching_records(
    record: Mapping[str, Any],
    index: Mapping[str, Sequence[Mapping[str, Any]]],
) -> List[Mapping[str, Any]]:
    matches: List[Mapping[str, Any]] = []
    seen: set[int] = set()
    for key in identity_keys(record):
        for candidate in index.get(key, []):
            candidate_identity = id(candidate)
            if candidate_identity not in seen:
                seen.add(candidate_identity)
                matches.append(candidate)
    return matches


def strongest_matching_records(
    record: Mapping[str, Any],
    index: Mapping[str, Sequence[Mapping[str, Any]]],
) -> List[Mapping[str, Any]]:
    """Use title/year only when the paper has no stronger identifier."""
    keys = identity_keys(record)
    strong_keys = [key for key in keys if not key.startswith("title_year:")]
    candidate_keys = strong_keys or keys
    for key in candidate_keys:
        matches = index.get(key, [])
        if matches:
            return list(matches)
    return []


def merge_curated_fields(
    public_record: Dict[str, Any], curated_record: Mapping[str, Any]
) -> None:
    for field in (
        "title",
        "year",
        "authors",
        "venue",
        "doi",
        "arxiv_id",
        "openalex_url",
        "paper_url",
        "publication_type",
        "abstract",
        "task",
        "subtask",
        "entry_type",
        "scope_status",
        "source_database",
        "metadata_source",
        "curation_status",
        "review_status",
        "review_note",
    ):
        if field in curated_record:
            public_record[field] = curated_record[field]
    public_record["publication_year"] = public_record.get("year")
    public_record["notes"] = clean(public_record.get("review_note"))


def load_admin_data(
    exclusions_path: Path = CURATED_EXCLUSIONS_PATH,
    curated_papers_path: Path = CURATED_PAPERS_PATH,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    public_papers = read_json_records(PUBLIC_PAPERS_PATH)
    map_records = read_json_records(PUBLIC_MAP_PATH)
    curated_rows = read_csv_rows(curated_papers_path)
    exclusion_rows = read_csv_rows(exclusions_path)

    papers: List[Dict[str, Any]] = []
    paper_identity_index: DefaultDict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for source_record in public_papers:
        record = dict(source_record)
        record["record_source"] = "public_preview"
        record["is_in_curated_papers"] = False
        record["curated_record"] = None
        papers.append(record)
        for key in identity_keys(record):
            paper_identity_index[key].append(record)

    for curated_row in curated_rows:
        curated_record = curated_paper_record(curated_row)
        match = next(iter(strongest_matching_records(
            curated_record, paper_identity_index
        )), None)
        if match is None:
            match = curated_record
            match["is_in_curated_papers"] = True
            match["curated_record"] = dict(curated_row)
            papers.append(match)
            for key in identity_keys(match):
                paper_identity_index[key].append(match)
        else:
            match["is_in_curated_papers"] = True
            match["curated_record"] = dict(curated_row)
            merge_curated_fields(match, curated_record)

    # Keep durable exclusions visible after they disappear from public exports,
    # so maintainers can inspect or restore them later.
    for exclusion_row in exclusion_rows:
        exclusion_record = exclusion_only_paper_record(exclusion_row)
        match = next(iter(strongest_matching_records(
            exclusion_record, paper_identity_index
        )), None)
        if match is not None:
            continue
        papers.append(exclusion_record)
        for key in identity_keys(exclusion_record):
            paper_identity_index[key].append(exclusion_record)

    marker_index = index_by_identity(map_records)
    exclusion_index = index_by_identity(exclusion_rows)
    for paper in papers:
        markers = [
            marker_for_api(record)
            for record in strongest_matching_records(paper, marker_index)
        ]
        exclusions = strongest_matching_records(paper, exclusion_index)
        aggregated_institutions = parse_people(
            paper.get("aggregated_institutions")
        )
        institutions = sorted(
            {
                institution
                for institution in (
                    aggregated_institutions
                    + [
                        clean(marker.get("institution"))
                        for marker in markers
                    ]
                )
                if institution
            },
            key=str.casefold,
        )
        paper["display_id"] = display_id(paper)
        paper["normalized_title_year_key"] = title_year_key(paper)
        paper["marker_records"] = markers
        paper["institutions"] = institutions
        paper["has_map_location"] = bool(markers) or parse_boolean(
            paper.get("has_map_location")
        )
        paper["map_record_count"] = len(markers)
        paper["is_in_curated_exclusions"] = bool(exclusions)
        paper["has_active_exclusion"] = any(
            parse_boolean(exclusion.get("is_active")) for exclusion in exclusions
        )
        paper["exclusion_reasons"] = sorted(
            {
                clean(exclusion.get("reason"))
                for exclusion in exclusions
                if clean(exclusion.get("reason"))
            }
        )

    papers.sort(key=lambda paper: clean(paper.get("title")).casefold())
    papers_by_id = {paper["display_id"]: paper for paper in papers}
    if len(papers_by_id) != len(papers):
        raise AdminDataError("paper display IDs are not unique")

    status = {
        "read_only": False,
        "public_site_read_only": True,
        "write_capabilities": [
            "paper_exclusion",
            "paper_restore",
            "paper_create",
            "paper_metadata_update",
            "mapping_create",
            "mapping_update",
            "mapping_exclude",
            "mapping_replace_all",
            "local_validation",
            "local_preview_export",
        ],
        "counts": {
            "total_papers": len(papers),
            "public_preview_papers": len(public_papers),
            "curated_papers": len(curated_rows),
            "map_records": len(map_records),
            "papers_with_map_locations": sum(
                bool(paper.get("has_map_location")) for paper in papers
            ),
            "papers_missing_affiliations": sum(
                parse_boolean(paper.get("missing_affiliation")) for paper in papers
            ),
            "papers_missing_coordinates": sum(
                parse_boolean(paper.get("missing_coordinates")) for paper in papers
            ),
            "active_exclusions": sum(
                parse_boolean(row.get("is_active")) for row in exclusion_rows
            ),
        },
    }
    return papers, {"status": status, "papers_by_id": papers_by_id}


def paper_summary(paper: Mapping[str, Any]) -> Dict[str, Any]:
    fields = (
        "display_id",
        "title",
        "year",
        "publication_year",
        "authors",
        "venue",
        "venue_name",
        "doi",
        "openalex_url",
        "paper_url",
        "task",
        "subtask",
        "entry_type",
        "coverage_status",
        "has_map_location",
        "map_record_count",
        "missing_affiliation",
        "missing_coordinates",
        "source_database",
        "metadata_source",
        "record_source",
        "institutions",
        "normalized_title_year_key",
        "is_in_curated_papers",
        "is_in_curated_exclusions",
        "has_active_exclusion",
        "exclusion_reasons",
    )
    return {field: paper.get(field) for field in fields}


def api_payload(
    *,
    success: bool = True,
    message: str = "",
    data: Any = None,
    warnings: Sequence[str] = (),
    errors: Sequence[str] = (),
) -> Dict[str, Any]:
    return {
        "success": success,
        "message": message,
        "data": data,
        "warnings": list(warnings),
        "errors": list(errors),
    }


def prepare_mapping_candidates(
    paper: Mapping[str, Any],
    raw_candidates: Any,
    *,
    institution_locations: Sequence[Mapping[str, Any]],
    institution_aliases: Sequence[Mapping[str, Any]],
) -> Tuple[List[Dict[str, str]], List[str]]:
    """Normalize imported affiliation evidence and prefill reviewed canonicals."""
    candidates = raw_candidates if isinstance(raw_candidates, list) else []
    canonical_by_key = {
        normalize_institution_name(
            row.get("normalized_institution") or row.get("institution")
        ): clean(row.get("institution"))
        for row in institution_locations
        if clean(row.get("institution"))
    }
    for alias in institution_aliases:
        if clean(alias.get("review_status")) != "confirmed":
            continue
        alias_key = normalize_institution_name(alias.get("alias_name"))
        canonical = clean(alias.get("canonical_institution_name"))
        if alias_key and canonical:
            canonical_by_key[alias_key] = canonical

    normalized: List[Dict[str, str]] = []
    warnings: List[str] = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        raw_institution = clean(
            candidate.get("institution")
            or candidate.get("raw_institution_name")
        )
        authors_value = candidate.get("institution_authors")
        authors = (
            [clean(value) for value in authors_value if clean(value)]
            if isinstance(authors_value, list)
            else parse_people(authors_value)
        )
        if not raw_institution or not authors:
            warnings.append(
                "Skipped incomplete affiliation evidence without both an "
                "institution and associated author."
            )
            continue
        canonical = canonical_by_key.get(
            normalize_institution_name(raw_institution), ""
        )
        raw_affiliations = candidate.get("raw_affiliations")
        raw_affiliation = (
            " | ".join(
                clean(value) for value in raw_affiliations if clean(value)
            )
            if isinstance(raw_affiliations, list)
            else clean(candidate.get("raw_affiliation"))
        )
        source = clean(
            candidate.get("provenance_source")
            or candidate.get("evidence_source")
            or paper.get("source_database")
            or "manual"
        )
        latitude = candidate.get("latitude")
        if latitude in (None, ""):
            latitude = candidate.get("institution_latitude")
        longitude = candidate.get("longitude")
        if longitude in (None, ""):
            longitude = candidate.get("institution_longitude")
        normalized.append(
            {
                "institution": canonical or raw_institution,
                "institution_authors": "; ".join(authors),
                "author_order": "; ".join(
                    clean(value)
                    for value in candidate.get("author_order", [])
                    if clean(value)
                )
                if isinstance(candidate.get("author_order"), list)
                else clean(candidate.get("author_order")),
                "raw_affiliation": raw_affiliation or raw_institution,
                "openalex_institution_id": clean(
                    candidate.get("openalex_institution_id")
                ),
                "institution_city": clean(
                    candidate.get("city") or candidate.get("institution_city")
                ),
                "institution_country": clean(
                    candidate.get("country")
                    or candidate.get("institution_country")
                ),
                "institution_latitude": clean(latitude),
                "institution_longitude": clean(longitude),
                "provenance_source": source,
                "evidence_source": source,
                "evidence_url": clean(
                    candidate.get("evidence_url")
                    or paper.get("openalex_url")
                    or paper.get("paper_url")
                ),
                "affiliation_note": (
                    f"Raw institution: {raw_institution}"
                    if canonical and canonical != raw_institution
                    else ""
                ),
                "mapping_status": "active" if canonical else "needs_review",
                "review_note": (
                    "Automatically matched to a confirmed canonical institution; "
                    "review imported authorship evidence."
                    if canonical
                    else "Automatically imported affiliation candidate; confirm "
                    "the canonical institution before public export."
                ),
            }
        )
    grouped: Dict[str, Dict[str, str]] = {}
    for candidate in normalized:
        key = normalize_institution_name(candidate["institution"])
        existing = grouped.get(key)
        if existing is None:
            grouped[key] = candidate
            continue
        existing["institution_authors"] = "; ".join(
            dict.fromkeys(
                parse_people(existing["institution_authors"])
                + parse_people(candidate["institution_authors"])
            )
        )
        for field in ("author_order", "raw_affiliation"):
            values = [
                value
                for value in (
                    clean(existing.get(field)),
                    clean(candidate.get(field)),
                )
                if value
            ]
            existing[field] = " | ".join(dict.fromkeys(values))
    normalized = list(grouped.values())
    if not normalized:
        warnings.append(
            "Missing author–institution mapping: this paper cannot produce "
            "institution markers or author affiliation numbers until reviewed."
        )
    return normalized, warnings


def original_public_record(paper: Mapping[str, Any]) -> Dict[str, Any] | None:
    index = index_by_identity(read_json_records(PUBLIC_PAPERS_PATH))
    matches = strongest_matching_records(paper, index)
    return dict(matches[0]) if matches else None


def queue_location_review(
    draft: Mapping[str, Any],
    *,
    path: Path,
) -> Dict[str, str]:
    institution = clean(draft.get("institution"))
    note = clean(draft.get("review_note"))
    if not institution:
        raise AdminDataError("institution is required for location review")
    if not note:
        raise AdminDataError("review note is required")
    rows = load_location_reviews(path)
    identity = (
        normalized_title(draft.get("title")),
        record_year(draft),
        institution.casefold(),
    )
    existing = next(
        (
            row
            for row in rows
            if (
                normalized_title(row.get("title")),
                record_year(row),
                clean(row.get("institution")).casefold(),
            )
            == identity
        ),
        None,
    )
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    row = {
        "institution": institution,
        "related_paper_id": clean(
            draft.get("paper_id") or draft.get("id")
        ),
        "title": clean(draft.get("title")),
        "year": record_year(draft),
        "doi": clean(draft.get("doi")),
        "openalex_url": clean(draft.get("openalex_url")),
        "institution_authors": clean(draft.get("institution_authors")),
        "raw_affiliation": clean(draft.get("raw_affiliation")),
        "evidence_source": clean(draft.get("evidence_source")),
        "evidence_url": clean(draft.get("evidence_url")),
        "suggested_city": clean(draft.get("city")),
        "suggested_country": clean(draft.get("country")),
        "review_status": "needs_coordinates",
        "location_status": "needs_location_review",
        "coordinate_status": "missing",
        "review_note": note,
        "created_at": clean((existing or {}).get("created_at")) or now,
        "updated_at": now,
    }
    if existing:
        rows[rows.index(existing)] = row
    else:
        rows.append(row)
    save_location_reviews(rows, path)
    return row


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the local maintainer paper curation browser."
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Interface to bind (default: {DEFAULT_HOST}).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to bind (default: {DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--unsafe-bind-all",
        action="store_true",
        help="Permit binding to a non-loopback interface such as 0.0.0.0.",
    )
    parser.add_argument(
        "--paper-exclusions",
        type=Path,
        default=CURATED_EXCLUSIONS_PATH,
        help=(
            "Curated paper exclusion CSV "
            f"(default: {CURATED_EXCLUSIONS_PATH})."
        ),
    )
    parser.add_argument(
        "--curated-papers",
        type=Path,
        default=CURATED_PAPERS_PATH,
        help=(
            "Curated paper CSV "
            f"(default: {CURATED_PAPERS_PATH})."
        ),
    )
    parser.add_argument(
        "--curated-mappings",
        type=Path,
        default=CURATED_MAPPINGS_PATH,
        help=(
            "Curated author–institution mapping CSV "
            f"(default: {CURATED_MAPPINGS_PATH})."
        ),
    )
    parser.add_argument(
        "--location-review",
        type=Path,
        default=LOCATION_REVIEW_PATH,
        help=(
            "Institution location-review CSV "
            f"(default: {LOCATION_REVIEW_PATH})."
        ),
    )
    parser.add_argument(
        "--institution-locations",
        type=Path,
        default=INSTITUTION_LOCATIONS_PATH,
        help=(
            "Confirmed institution-location CSV "
            f"(default: {INSTITUTION_LOCATIONS_PATH})."
        ),
    )
    parser.add_argument(
        "--institution-aliases",
        type=Path,
        default=DEFAULT_INSTITUTION_ALIASES_PATH,
        help=f"Curated institution alias CSV (default: {DEFAULT_INSTITUTION_ALIASES_PATH}).",
    )
    return parser.parse_args(argv)


def make_handler(
    token: str,
    exclusions_path: Path = CURATED_EXCLUSIONS_PATH,
    curated_papers_path: Path = CURATED_PAPERS_PATH,
    mappings_path: Path = CURATED_MAPPINGS_PATH,
    location_review_path: Path = LOCATION_REVIEW_PATH,
    institution_locations_path: Path = INSTITUTION_LOCATIONS_PATH,
    institution_aliases_path: Path = DEFAULT_INSTITUTION_ALIASES_PATH,
    review_decisions_path: Path = DEFAULT_REVIEW_DECISIONS_PATH,
    author_mapping_report_path: Path = AUTHOR_MAPPING_REPORT_PATH,
    author_mapping_report_generator: Callable[
        [], Mapping[str, Any]
    ] = generate_author_mapping_report,
    autofill_runner: Callable[..., Mapping[str, Any]] = (
        autofill_public_map_arxiv_ids
    ),
) -> type[BaseHTTPRequestHandler]:
    workflow_lock = threading.Lock()
    workflow_status_lock = threading.Lock()
    latest_workflow_status: Dict[str, Any] = {
        "state": "idle",
        "workflow": None,
        "started_at": None,
        "completed_at": None,
        "result": None,
    }

    class AdminRequestHandler(BaseHTTPRequestHandler):
        server_version = "SyntheticImageResearchMapAdmin/0.1"

        def send_common_headers(self, content_type: str, length: int) -> None:
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'")

        def send_bytes(
            self,
            status: HTTPStatus,
            payload: bytes,
            content_type: str,
        ) -> None:
            self.send_response(status)
            self.send_common_headers(content_type, len(payload))
            self.end_headers()
            self.wfile.write(payload)

        def send_json(self, status: HTTPStatus, payload: Mapping[str, Any]) -> None:
            body = json.dumps(
                payload, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")
            self.send_bytes(status, body, "application/json; charset=utf-8")

        def is_authorized(self, query: Mapping[str, Sequence[str]]) -> bool:
            supplied = self.headers.get("X-Admin-Token", "")
            if not supplied:
                supplied = next(iter(query.get("token", [])), "")
            return bool(supplied) and hmac.compare_digest(supplied, token)

        def is_header_authorized(self) -> bool:
            supplied = self.headers.get("X-Admin-Token", "")
            return bool(supplied) and hmac.compare_digest(supplied, token)

        def is_loopback_client(self) -> bool:
            try:
                return ipaddress.ip_address(
                    self.client_address[0]
                ).is_loopback
            except ValueError:
                return False

        def send_method_not_allowed(self, allowed: str) -> None:
            payload = json.dumps(
                {"error": f"method not allowed; use {allowed}"},
                separators=(",", ":"),
            ).encode("utf-8")
            self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
            self.send_header("Allow", allowed)
            self.send_common_headers(
                "application/json; charset=utf-8", len(payload)
            )
            self.end_headers()
            self.wfile.write(payload)

        def workflow_status_snapshot(self) -> Dict[str, Any]:
            with workflow_status_lock:
                return dict(latest_workflow_status)

        def autofill_status_snapshot(self) -> Dict[str, Any]:
            with ARXIV_AUTOFILL_STATE_LOCK:
                return dict(ARXIV_AUTOFILL_STATE)

        @staticmethod
        def update_autofill_progress(progress: Mapping[str, Any]) -> None:
            with ARXIV_AUTOFILL_STATE_LOCK:
                ARXIV_AUTOFILL_STATE.update({
                    "total_eligible_papers": int(
                        progress.get("eligible_public_map_papers", 0)
                    ),
                    "papers_requiring_lookup": int(
                        progress.get("papers_requiring_lookup", 0)
                    ),
                    "processed_lookups": int(
                        progress.get("processed_lookups", 0)
                    ),
                    "exact_matches_added": int(
                        progress.get("exact_matches_added", 0)
                    ),
                    "no_matches": int(progress.get("no_match_count", 0)),
                    "ambiguous_matches": int(
                        progress.get("ambiguous_match_count", 0)
                    ),
                    "failed_lookups": int(
                        progress.get("failed_lookup_count", 0)
                    ),
                    "current_paper_title": clean(
                        progress.get("current_paper_title")
                    ),
                })

        @classmethod
        def run_arxiv_autofill_job(cls) -> None:
            try:
                stats = dict(autofill_runner(
                    export=lambda: run_workflow("export_preview"),
                    progress=cls.update_autofill_progress,
                ))
                cls.update_autofill_progress(stats)
                export_failed = bool(
                    stats.get("export_ran")
                    and not stats.get("export_success")
                )
                with ARXIV_AUTOFILL_STATE_LOCK:
                    ARXIV_AUTOFILL_STATE.update({
                        "status": "failed" if export_failed else "completed",
                        "completion_time": datetime.now(timezone.utc).isoformat(),
                        "current_paper_title": "",
                        "final_error": (
                            "Public preview export failed."
                            if export_failed else ""
                        ),
                        "result": stats,
                    })
            except Exception as error:  # Preserve status for polling clients.
                LOGGER.exception("arXiv autofill job failed")
                with ARXIV_AUTOFILL_STATE_LOCK:
                    ARXIV_AUTOFILL_STATE.update({
                        "status": "failed",
                        "completion_time": datetime.now(timezone.utc).isoformat(),
                        "current_paper_title": "",
                        "final_error": f"{type(error).__name__}: {error}",
                    })
            finally:
                ARXIV_AUTOFILL_LOCK.release()

        def run_admin_workflow(self, workflow_name: str) -> None:
            if not self.is_loopback_client():
                self.send_json(
                    HTTPStatus.FORBIDDEN,
                    {"error": "command workflows are restricted to loopback clients"},
                )
                return
            if not workflow_lock.acquire(blocking=False):
                self.send_json(
                    HTTPStatus.CONFLICT,
                    {
                        "error": "another admin workflow is already running",
                        "status": self.workflow_status_snapshot(),
                    },
                )
                return
            started_at = datetime.now(timezone.utc).isoformat()
            with workflow_status_lock:
                latest_workflow_status.update(
                    {
                        "state": "running",
                        "workflow": workflow_name,
                        "started_at": started_at,
                        "completed_at": None,
                        "result": None,
                    }
                )
            try:
                result = run_workflow(workflow_name)
                completed_at = datetime.now(timezone.utc).isoformat()
                with workflow_status_lock:
                    latest_workflow_status.update(
                        {
                            "state": (
                                "succeeded" if result["success"] else "failed"
                            ),
                            "completed_at": completed_at,
                            "result": result,
                        }
                    )
                self.send_json(HTTPStatus.OK, result)
            except AdminWorkflowError as error:
                completed_at = datetime.now(timezone.utc).isoformat()
                failure = {
                    "success": False,
                    "command": [],
                    "exit_code": 2,
                    "stdout_tail": "",
                    "stderr_tail": str(error),
                    "duration_seconds": 0,
                    "changed_files": [],
                }
                with workflow_status_lock:
                    latest_workflow_status.update(
                        {
                            "state": "failed",
                            "completed_at": completed_at,
                            "result": failure,
                        }
                    )
                self.send_json(HTTPStatus.BAD_REQUEST, failure)
            except Exception as error:  # Keep workflow state recoverable.
                completed_at = datetime.now(timezone.utc).isoformat()
                failure = {
                    "success": False,
                    "command": [],
                    "exit_code": 1,
                    "stdout_tail": "",
                    "stderr_tail": (
                        "Unexpected local workflow failure: "
                        f"{type(error).__name__}: {error}"
                    ),
                    "duration_seconds": 0,
                    "changed_files": [],
                }
                with workflow_status_lock:
                    latest_workflow_status.update(
                        {
                            "state": "failed",
                            "completed_at": completed_at,
                            "result": failure,
                        }
                    )
                self.send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR, failure
                )
            finally:
                workflow_lock.release()

        def serve_static(self, path: Path, content_type: str) -> None:
            try:
                payload = path.read_bytes()
            except OSError as error:
                self.send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": f"could not read admin asset: {error}"},
                )
                return
            self.send_bytes(HTTPStatus.OK, payload, content_type)

        def read_json_body(self) -> Dict[str, Any]:
            length_text = self.headers.get("Content-Length", "")
            try:
                length = int(length_text)
            except ValueError as error:
                raise AdminDataError("valid Content-Length is required") from error
            if length < 1 or length > MAX_REQUEST_BYTES:
                raise AdminDataError(
                    f"request body must be between 1 and {MAX_REQUEST_BYTES} bytes"
                )
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as error:
                raise AdminDataError("request body must be valid JSON") from error
            if not isinstance(payload, dict):
                raise AdminDataError("request body must be a JSON object")
            return payload

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            request = urlsplit(self.path)
            query = parse_qs(request.query)
            if request.path == "/admin":
                self.send_response(HTTPStatus.TEMPORARY_REDIRECT)
                self.send_header("Location", f"/admin/?{request.query}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if request.path in STATIC_ROUTES:
                path, content_type = STATIC_ROUTES[request.path]
                self.serve_static(path, content_type)
                return
            if not request.path.startswith("/api/"):
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            if not self.is_authorized(query):
                self.send_json(
                    HTTPStatus.UNAUTHORIZED,
                    {"error": "missing or invalid admin token"},
                )
                return
            if request.path in WORKFLOW_ENDPOINTS:
                self.send_method_not_allowed("POST")
                return
            if request.path == "/api/admin/papers/autofill-arxiv/status":
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        {"error": "X-Admin-Token header is required"},
                    )
                    return
                self.send_json(HTTPStatus.OK, self.autofill_status_snapshot())
                return
            if request.path == "/api/latest-validation-status":
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        {"error": "X-Admin-Token header is required"},
                    )
                    return
                self.send_json(
                    HTTPStatus.OK, self.workflow_status_snapshot()
                )
                return
            if request.path == "/api/git-status":
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        {"error": "X-Admin-Token header is required"},
                    )
                    return
                if not self.is_loopback_client():
                    self.send_json(
                        HTTPStatus.FORBIDDEN,
                        {"error": "git status is restricted to loopback clients"},
                    )
                    return
                self.send_json(HTTPStatus.OK, git_status_result())
                return
            if request.path == "/api/location-review":
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        {"error": "X-Admin-Token header is required"},
                    )
                    return
                if not self.is_loopback_client():
                    self.send_json(
                        HTTPStatus.FORBIDDEN,
                        {
                            "error": (
                                "location review is restricted to loopback clients"
                            )
                        },
                    )
                    return
                try:
                    payload = location_review_payload(
                        review_path=location_review_path,
                        locations_path=institution_locations_path,
                        aliases_path=institution_aliases_path,
                    )
                except CuratedLocationError as error:
                    self.send_json(
                        HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)}
                    )
                    return
                self.send_json(HTTPStatus.OK, payload)
                return
            if request.path in AUTHOR_MAPPING_COVERAGE_ENDPOINTS:
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        api_payload(
                            success=False,
                            errors=("X-Admin-Token header is required",),
                        ),
                    )
                    return
                if not self.is_loopback_client():
                    self.send_json(
                        HTTPStatus.FORBIDDEN,
                        api_payload(
                            success=False,
                            errors=("admin report APIs are restricted to loopback clients",),
                        ),
                    )
                    return
                try:
                    report = load_author_mapping_coverage(
                        author_mapping_report_path,
                        unresolved_only=True,
                    )
                except AdminDataError as error:
                    self.send_json(
                        HTTPStatus.OK,
                        api_payload(
                            data=unavailable_author_mapping_coverage(
                                (
                                    "Author mapping report has not been generated."
                                    if not author_mapping_report_path.exists()
                                    else str(error)
                                )
                            )
                        ),
                    )
                    return
                self.send_json(HTTPStatus.OK, api_payload(data=report))
                return
            review_get_paths = {
                "/api/review/high-risk-markers": "high_risk_marker",
                "/api/review/marker-blockers": "marker_blocker",
                "/api/review/key-paper-coverage": "key_paper_coverage",
            }
            if request.path in review_get_paths or request.path in {
                "/api/review/manual-import",
                "/api/dashboard",
                "/api/paper/metadata",
                "/api/admin/papers/autofill-arxiv/status",
            }:
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        api_payload(
                            success=False,
                            errors=("X-Admin-Token header is required",),
                        ),
                    )
                    return
                if not self.is_loopback_client():
                    self.send_json(
                        HTTPStatus.FORBIDDEN,
                        api_payload(
                            success=False,
                            errors=("admin review APIs are restricted to loopback clients",),
                        ),
                    )
                    return
                try:
                    if request.path in review_get_paths:
                        queue = load_queue(
                            review_get_paths[request.path],
                            mappings_path=mappings_path,
                            exclusions_path=exclusions_path,
                        )
                        self.send_json(HTTPStatus.OK, api_payload(data=queue))
                        return
                    if request.path == "/api/review/manual-import":
                        self.send_json(
                            HTTPStatus.OK,
                            api_payload(data=load_manual_import_queue(
                                mappings_path=mappings_path,
                                exclusions_path=exclusions_path,
                            )),
                        )
                        return
                    if request.path == "/api/dashboard":
                        _papers, admin_data = load_admin_data(
                            exclusions_path, curated_papers_path
                        )
                        counts = admin_data["status"]["counts"]
                        location_payload = location_review_payload(
                            review_path=location_review_path,
                            locations_path=institution_locations_path,
                            aliases_path=institution_aliases_path,
                        )
                        curated_counts = {
                            "total_papers": counts["total_papers"],
                            "curated_papers": counts["curated_papers"],
                            "active_exclusions": counts["active_exclusions"],
                            "papers_missing_affiliations": counts[
                                "papers_missing_affiliations"
                            ],
                            "papers_missing_coordinates": counts[
                                "papers_missing_coordinates"
                            ],
                            "curated_mappings": len(load_mappings(mappings_path)),
                            "pending_location_reviews": sum(
                                clean(row.get("coordinate_status")) != "known"
                                for row in location_payload.get("records", [])
                            ),
                            "confirmed_institution_locations": len(
                                read_csv_rows(institution_locations_path)
                            ),
                        }
                        try:
                            author_mapping_coverage = (
                                load_author_mapping_coverage(author_mapping_report_path)
                            )
                        except AdminDataError:
                            author_mapping_coverage = unavailable_author_mapping_coverage(
                                "Report missing"
                            )
                        dashboard = dashboard_data(
                            curated_counts=curated_counts,
                            validation_status=self.workflow_status_snapshot(),
                            git_status=git_status_result(),
                            author_mapping_coverage=author_mapping_coverage,
                        )
                        self.send_json(
                            HTTPStatus.OK, api_payload(data=dashboard)
                        )
                        return
                    paper_id = next(iter(query.get("id", [])), "")
                    if not paper_id:
                        raise AdminDataError("id query parameter is required")
                    _papers, admin_data = load_admin_data(
                        exclusions_path, curated_papers_path
                    )
                    paper = admin_data["papers_by_id"].get(paper_id)
                    if paper is None:
                        self.send_json(
                            HTTPStatus.NOT_FOUND,
                            api_payload(
                                success=False, errors=("paper not found",)
                            ),
                        )
                        return
                    curated_record = paper.get("curated_record")
                    self.send_json(
                        HTTPStatus.OK,
                        api_payload(
                            data={
                                "public_preview_record": original_public_record(
                                    paper
                                ),
                                "curated_record": curated_record,
                                "effective_record": paper,
                                "identity_keys": {
                                    "paper_id": clean(
                                        (curated_record or {}).get("paper_id")
                                        or paper.get("paper_id")
                                        or paper.get("display_id")
                                    ),
                                    "doi": clean(paper.get("doi")),
                                    "openalex_url": clean(
                                        paper.get("openalex_url")
                                    ),
                                    "normalized_title_year": title_year_key(
                                        paper
                                    ),
                                },
                            }
                        ),
                    )
                    return
                except (
                    AdminDataError,
                    AdminReviewQueueError,
                    CuratedLocationError,
                    CuratedMappingError,
                ) as error:
                    self.send_json(
                        HTTPStatus.BAD_REQUEST,
                        api_payload(success=False, errors=(str(error),)),
                    )
                    return
            try:
                papers, data = load_admin_data(
                    exclusions_path,
                    curated_papers_path,
                )
            except AdminDataError as error:
                self.send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)}
                )
                return
            if request.path == "/api/status":
                self.send_json(HTTPStatus.OK, data["status"])
                return
            if request.path == "/api/papers":
                self.send_json(
                    HTTPStatus.OK,
                    {
                        "count": len(papers),
                        "records": [paper_summary(paper) for paper in papers],
                    },
                )
                return
            if request.path == "/api/paper":
                paper_id = next(iter(query.get("id", [])), "")
                if not paper_id:
                    self.send_json(
                        HTTPStatus.BAD_REQUEST,
                        {"error": "id query parameter is required"},
                    )
                    return
                paper = data["papers_by_id"].get(paper_id)
                if paper is None:
                    self.send_json(
                        HTTPStatus.NOT_FOUND, {"error": "paper not found"}
                    )
                    return
                self.send_json(HTTPStatus.OK, {"paper": paper})
                return
            if request.path == "/api/paper/mappings":
                paper_id = next(iter(query.get("id", [])), "")
                if not paper_id:
                    self.send_json(
                        HTTPStatus.BAD_REQUEST,
                        {"error": "id query parameter is required"},
                    )
                    return
                paper = data["papers_by_id"].get(paper_id)
                if paper is None:
                    self.send_json(
                        HTTPStatus.NOT_FOUND, {"error": "paper not found"}
                    )
                    return
                try:
                    map_records = read_json_records(PUBLIC_MAP_PATH)
                    mapping_rows = mappings_for_paper(
                        paper, load_mappings(mappings_path)
                    )
                    location_rows = location_reviews_for_paper(
                        paper, load_location_reviews(location_review_path)
                    )
                except CuratedMappingError as error:
                    self.send_json(
                        HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)}
                    )
                    return
                for mapping in mapping_rows:
                    mapping["location_status"] = mapping_location_state(
                        mapping,
                        map_records=map_records,
                        location_rows=location_rows,
                    )
                self.send_json(
                    HTTPStatus.OK,
                    {
                        "paper": paper_summary(paper),
                        "public_marker_records": paper.get("marker_records", []),
                        "curated_mappings": mapping_rows,
                        "location_reviews": location_rows,
                        "mapping_diagnostic": {
                            "status": (
                                "available"
                                if any(
                                    clean(row.get("mapping_status"))
                                    in {"active", "needs_review"}
                                    for row in mapping_rows
                                )
                                else "missing_mapping"
                            ),
                            "message": (
                                ""
                                if any(
                                    clean(row.get("mapping_status"))
                                    in {"active", "needs_review"}
                                    for row in mapping_rows
                                )
                                else "No eligible author–institution mapping "
                                "exists; public markers and author affiliation "
                                "numbers are blocked."
                            ),
                        },
                    },
                )
                return
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            request = urlsplit(self.path)
            query = parse_qs(request.query)
            if not request.path.startswith("/api/"):
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            if not self.is_authorized(query):
                self.send_json(
                    HTTPStatus.UNAUTHORIZED,
                    {"error": "missing or invalid admin token"},
                )
                return
            if request.path in {
                "/api/latest-validation-status",
                "/api/git-status",
                "/api/location-review",
                "/api/dashboard",
                "/api/review/high-risk-markers",
                "/api/review/marker-blockers",
                "/api/review/key-paper-coverage",
                "/api/review/manual-import",
                *AUTHOR_MAPPING_COVERAGE_ENDPOINTS,
                "/api/paper/metadata",
            }:
                self.send_method_not_allowed("GET")
                return
            if request.path in WORKFLOW_ENDPOINTS:
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        {"error": "X-Admin-Token header is required"},
                    )
                    return
                if request.path == "/api/publish-changes":
                    try:
                        payload = self.read_json_body()
                    except AdminDataError as error:
                        self.send_json(
                            HTTPStatus.BAD_REQUEST,
                            {"error": str(error)},
                        )
                        return
                    if payload.get("confirmed") is not True:
                        self.send_json(
                            HTTPStatus.BAD_REQUEST,
                            {
                                "error": (
                                    "explicit confirmation is required "
                                    "before publishing"
                                )
                            },
                        )
                        return
                self.run_admin_workflow(WORKFLOW_ENDPOINTS[request.path])
                return
            if request.path == "/api/admin/papers/autofill-arxiv":
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        {"error": "X-Admin-Token header is required"},
                    )
                    return
                if not self.is_loopback_client():
                    self.send_json(
                        HTTPStatus.FORBIDDEN,
                        {
                            "error": (
                                "arXiv auto-fill is restricted to "
                                "loopback clients"
                            )
                        },
                    )
                    return
                if not ARXIV_AUTOFILL_LOCK.acquire(blocking=False):
                    self.send_json(
                        HTTPStatus.CONFLICT,
                        {"error": "arXiv auto-fill is already running"},
                    )
                    return
                try:
                    with ARXIV_AUTOFILL_STATE_LOCK:
                        ARXIV_AUTOFILL_STATE.update({
                            "status": "running",
                            "total_eligible_papers": 0,
                            "papers_requiring_lookup": 0,
                            "processed_lookups": 0,
                            "exact_matches_added": 0,
                            "no_matches": 0,
                            "ambiguous_matches": 0,
                            "failed_lookups": 0,
                            "current_paper_title": "",
                            "start_time": datetime.now(timezone.utc).isoformat(),
                            "completion_time": None,
                            "final_error": "",
                            "result": None,
                        })
                    worker = threading.Thread(
                        target=self.run_arxiv_autofill_job,
                        name="arxiv-autofill",
                        daemon=True,
                    )
                    worker.start()
                    self.send_json(
                        HTTPStatus.ACCEPTED,
                        api_payload(
                            message="arXiv ID auto-fill started.",
                            data=self.autofill_status_snapshot(),
                        ),
                    )
                except Exception as error:
                    ARXIV_AUTOFILL_LOCK.release()
                    with ARXIV_AUTOFILL_STATE_LOCK:
                        ARXIV_AUTOFILL_STATE.update({
                            "status": "failed",
                            "completion_time": datetime.now(timezone.utc).isoformat(),
                            "final_error": f"{type(error).__name__}: {error}",
                        })
                    self.send_json(
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        api_payload(success=False, errors=(str(error),)),
                    )
                return
            if request.path == AUTHOR_MAPPING_GENERATE_ENDPOINT:
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        api_payload(
                            success=False,
                            errors=("X-Admin-Token header is required",),
                        ),
                    )
                    return
                if not self.is_loopback_client():
                    self.send_json(
                        HTTPStatus.FORBIDDEN,
                        api_payload(
                            success=False,
                            errors=("admin report generation is restricted to loopback clients",),
                        ),
                    )
                    return
                if not AUTHOR_MAPPING_REPORT_WRITE_LOCK.acquire(blocking=False):
                    self.send_json(
                        HTTPStatus.CONFLICT,
                        api_payload(
                            success=False,
                            errors=("Author mapping report generation is already running.",),
                        ),
                    )
                    return
                try:
                    result = dict(author_mapping_report_generator())
                    if not result.get("success"):
                        message = clean(
                            result.get("stderr_tail")
                            or result.get("stdout_tail")
                            or "Author mapping report generation failed."
                        )
                        self.send_json(
                            HTTPStatus.INTERNAL_SERVER_ERROR,
                            api_payload(success=False, errors=(message,)),
                        )
                        return
                    report = load_author_mapping_coverage(
                        author_mapping_report_path
                    )
                    self.send_json(
                        HTTPStatus.OK,
                        api_payload(
                            message="Author mapping report generated.",
                            data=report,
                        ),
                    )
                except AdminDataError as error:
                    self.send_json(
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        api_payload(success=False, errors=(str(error),)),
                    )
                finally:
                    AUTHOR_MAPPING_REPORT_WRITE_LOCK.release()
                return
            location_actions = {
                "/api/location-review/confirm": "confirm",
                "/api/location-review/mark-ambiguous": "ambiguous",
                "/api/location-review/mark-needs-coordinates": "needs_coordinates",
                "/api/location-review/mark-pending-review": "pending_review",
                "/api/location-review/mark-alias-candidate": "alias_candidate",
                "/api/location-review/mark-ignore": "ignore",
                "/api/location-review/mark-excluded": "excluded",
                "/api/location-review/confirm-alias": "confirm_alias",
                "/api/location-review/save-metadata": "save_metadata",
            }
            if request.path in location_actions:
                if not self.is_header_authorized():
                    self.send_json(
                        HTTPStatus.UNAUTHORIZED,
                        {"error": "X-Admin-Token header is required"},
                    )
                    return
                if not self.is_loopback_client():
                    self.send_json(
                        HTTPStatus.FORBIDDEN,
                        {
                            "error": (
                                "location review is restricted to loopback clients"
                            )
                        },
                    )
                    return
                try:
                    payload = self.read_json_body()
                    with CURATED_LOCATION_WRITE_LOCK:
                        action = location_actions[request.path]
                        if action == "confirm":
                            result = create_or_update_confirmed_location(
                                payload.get("queue_id"),
                                payload,
                                locations_path=institution_locations_path,
                                review_path=location_review_path,
                            )
                            message = (
                                "Location saved. Run full refresh pipeline "
                                "to update markers."
                            )
                        elif action == "confirm_alias":
                            result = confirm_alias(
                                payload.get("queue_id"),
                                payload.get("canonical_institution_name"),
                                alias_language=payload.get("detected_language"),
                                alias_source=payload.get("alias_source"),
                                note=payload.get("coordinate_review_note")
                                or payload.get("review_note"),
                                review_path=location_review_path,
                                locations_path=institution_locations_path,
                                aliases_path=institution_aliases_path,
                            )
                            message = "Alias confirmed against the canonical institution."
                        elif action == "save_metadata":
                            result = {
                                "queue_row": save_queue_metadata(
                                    payload.get("queue_id"),
                                    payload,
                                    review_path=location_review_path,
                                )
                            }
                            message = "Institution metadata saved."
                        else:
                            result = {
                                "queue_row": mark_queue_row(
                                    payload.get("queue_id"),
                                    action,
                                    payload.get("coordinate_review_note")
                                    or payload.get("review_note"),
                                    review_path=location_review_path,
                                )
                            }
                            message = (
                                "Location review status saved. "
                                "No coordinates were created."
                            )
                except (AdminDataError, CuratedLocationError) as error:
                    self.send_json(
                        HTTPStatus.BAD_REQUEST, {"error": str(error)}
                    )
                    return
                self.send_json(
                    (
                        HTTPStatus.CREATED
                        if result.get("action") == "created"
                        else HTTPStatus.OK
                    ),
                    {**result, "message": message},
                )
                return
            if request.path not in {
                "/api/paper/delete-or-exclude",
                "/api/paper/restore",
                "/api/openalex/search-paper",
                "/api/paper/create",
                "/api/paper/mapping/create",
                "/api/paper/mapping/update",
                "/api/paper/mapping/exclude",
                "/api/paper/mappings/replace-all",
                "/api/paper/metadata/update",
                "/api/review/high-risk-markers/action",
                "/api/review/marker-blockers/action",
                "/api/review/key-paper-coverage/action",
                "/api/review/manual-import/action",
            }:
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            try:
                payload = self.read_json_body()
                new_write_paths = {
                    "/api/paper/metadata/update",
                    "/api/review/high-risk-markers/action",
                    "/api/review/marker-blockers/action",
                    "/api/review/key-paper-coverage/action",
                    "/api/review/manual-import/action",
                }
                if request.path in new_write_paths:
                    if not self.is_header_authorized():
                        self.send_json(
                            HTTPStatus.UNAUTHORIZED,
                            api_payload(
                                success=False,
                                errors=("X-Admin-Token header is required",),
                            ),
                        )
                        return
                    if not self.is_loopback_client():
                        self.send_json(
                            HTTPStatus.FORBIDDEN,
                            api_payload(
                                success=False,
                                errors=(
                                    "admin review writes are restricted to loopback clients",
                                ),
                            ),
                        )
                        return

                if request.path == "/api/paper/metadata/update":
                    paper_id = clean(payload.get("id"))
                    if not paper_id:
                        raise AdminDataError("paper id is required")
                    _papers, admin_data = load_admin_data(
                        exclusions_path, curated_papers_path
                    )
                    paper = admin_data["papers_by_id"].get(paper_id)
                    if paper is None:
                        self.send_json(
                            HTTPStatus.NOT_FOUND,
                            api_payload(
                                success=False, errors=("paper not found",)
                            ),
                        )
                        return
                    try:
                        with CURATED_PAPER_WRITE_LOCK:
                            row = update_curated_paper(
                                paper,
                                payload,
                                preview_records=read_json_records(
                                    PUBLIC_PAPERS_PATH
                                ),
                                path=curated_papers_path,
                            )
                    except DuplicatePaperError as error:
                        self.send_json(
                            HTTPStatus.CONFLICT,
                            api_payload(
                                success=False,
                                data={"duplicate_matches": error.matches},
                                errors=("paper identity collides with another paper",),
                            ),
                        )
                        return
                    self.send_json(
                        HTTPStatus.OK,
                        api_payload(
                            message=(
                                "Saved to curated database. Run full refresh "
                                "pipeline to update public preview."
                            ),
                            data={"paper": row},
                        ),
                    )
                    return

                review_action_paths = {
                    "/api/review/high-risk-markers/action": "high_risk_marker",
                    "/api/review/marker-blockers/action": "marker_blocker",
                    "/api/review/key-paper-coverage/action": "key_paper_coverage",
                    "/api/review/manual-import/action": "manual_import",
                }
                if request.path in review_action_paths:
                    note = clean(payload.get("review_note"))
                    if not note:
                        raise AdminDataError("review note is required")
                    action = clean(payload.get("action"))
                    action_warnings: List[str] = []
                    mapping_result = None
                    exclusion_result = None
                    if action == "send_to_location_review":
                        with CURATED_LOCATION_WRITE_LOCK:
                            location_row = queue_location_review(
                                payload, path=location_review_path
                            )
                    else:
                        location_row = None
                    if action == "confirm_marker":
                        papers, admin_data = load_admin_data(
                            exclusions_path, curated_papers_path
                        )
                        requested_id = clean(
                            payload.get("id") or payload.get("paper_id")
                        )
                        paper = admin_data["papers_by_id"].get(requested_id)
                        if paper is None:
                            requested_keys = set(identity_keys(payload))
                            paper = next(
                                (
                                    candidate
                                    for candidate in papers
                                    if requested_keys
                                    & set(identity_keys(candidate))
                                ),
                                None,
                            )
                        institution = clean(payload.get("institution"))
                        institution_authors = clean(
                            payload.get("institution_authors")
                        )
                        if paper and institution and institution_authors:
                            mapping_draft = {
                                "institution": institution,
                                "institution_authors": institution_authors,
                                "raw_affiliation": clean(
                                    payload.get("raw_affiliation")
                                    or payload.get("resolution_notes")
                                    or institution
                                ),
                                "evidence_source": clean(
                                    payload.get("evidence_source")
                                    or payload.get("resolution_method")
                                    or "Admin marker review"
                                ),
                                "evidence_url": clean(
                                    payload.get("evidence_url")
                                    or payload.get("paper_url")
                                    or payload.get("openalex_url")
                                ),
                                "affiliation_note": (
                                    "Confirmed from the high-risk marker review queue."
                                ),
                                "mapping_status": "active",
                                "review_note": note,
                            }
                            existing = next(
                                (
                                    row
                                    for row in mappings_for_paper(
                                        paper, load_mappings(mappings_path)
                                    )
                                    if clean(row.get("institution")).casefold()
                                    == institution.casefold()
                                    and clean(row.get("institution_authors")).casefold()
                                    == institution_authors.casefold()
                                ),
                                None,
                            )
                            with CURATED_MAPPING_WRITE_LOCK:
                                if existing and clean(
                                    existing.get("mapping_status")
                                ) == "active":
                                    mapping_result = {
                                        "mapping": existing,
                                        "status": "already_active",
                                    }
                                elif existing:
                                    mapping_result = update_mapping(
                                        paper,
                                        clean(existing.get("mapping_id")),
                                        mapping_draft,
                                        map_records=read_json_records(
                                            PUBLIC_MAP_PATH
                                        ),
                                        mappings_path=mappings_path,
                                        location_review_path=location_review_path,
                                    )
                                else:
                                    mapping_result = create_mapping(
                                        paper,
                                        mapping_draft,
                                        map_records=read_json_records(
                                            PUBLIC_MAP_PATH
                                        ),
                                        mappings_path=mappings_path,
                                        location_review_path=location_review_path,
                                    )
                        else:
                            action_warnings.append(
                                "Marker confirmation was recorded, but no curated "
                                "mapping was created because paper, institution, or "
                                "institution-author evidence was incomplete."
                            )
                    if action == "exclude_wrong_mapping":
                        papers, admin_data = load_admin_data(
                            exclusions_path, curated_papers_path
                        )
                        requested_keys = set(identity_keys(payload))
                        paper = next(
                            (
                                candidate
                                for candidate in papers
                                if requested_keys
                                & set(identity_keys(candidate))
                            ),
                            None,
                        )
                        institution = clean(payload.get("institution"))
                        matching_mappings = (
                            [
                                row
                                for row in mappings_for_paper(
                                    paper, load_mappings(mappings_path)
                                )
                                if clean(row.get("institution")).casefold()
                                == institution.casefold()
                                and clean(row.get("mapping_status"))
                                in {"active", "needs_review"}
                            ]
                            if paper and institution
                            else []
                        )
                        if matching_mappings:
                            excluded_mappings = []
                            with CURATED_MAPPING_WRITE_LOCK:
                                for mapping in matching_mappings:
                                    excluded_mappings.append(
                                        exclude_mapping(
                                            paper,
                                            clean(mapping.get("mapping_id")),
                                            note,
                                            mappings_path=mappings_path,
                                        )
                                    )
                            mapping_result = {
                                "excluded_mappings": excluded_mappings
                            }
                        else:
                            action_warnings.append(
                                "No curated mapping matched; the durable review "
                                "decision will suppress matching automatic markers "
                                "during export."
                            )
                    if action == "exclude_paper_scope":
                        if identity_keys(payload):
                            with EXCLUSION_WRITE_LOCK:
                                exclusion_result = upsert_active_exclusion(
                                    payload,
                                    "out_of_scope",
                                    note,
                                    exclusions_path,
                                )
                        else:
                            action_warnings.append(
                                "The scope decision was recorded, but no paper "
                                "exclusion was created because stable identity "
                                "evidence was missing."
                            )
                    decision_draft = {
                        **payload,
                        "review_queue": review_action_paths[request.path],
                    }
                    with REVIEW_DECISION_WRITE_LOCK:
                        decision = upsert_review_decision(
                            decision_draft, path=review_decisions_path
                        )
                    self.send_json(
                        HTTPStatus.OK,
                        api_payload(
                            message=(
                                "Saved to curated database. Run full refresh "
                                "pipeline to update public preview."
                            ),
                            data={
                                "decision": decision,
                                "location_review": location_row,
                                "mapping": mapping_result,
                                "exclusion": exclusion_result,
                            },
                            warnings=action_warnings,
                        ),
                    )
                    return

                if request.path == "/api/openalex/search-paper":
                    try:
                        results = search_openalex_papers(payload)
                    except OpenAlexSearchInputError as error:
                        self.send_json(
                            HTTPStatus.BAD_REQUEST,
                            {
                                "error": str(error),
                                "manual_fallback_available": True,
                            },
                        )
                        return
                    except OpenAlexFetchError as error:
                        self.send_json(
                            HTTPStatus.BAD_GATEWAY,
                            {
                                "error": (
                                    f"OpenAlex search failed: {error}. "
                                    "You can still add the paper manually."
                                ),
                                "manual_fallback_available": True,
                            },
                        )
                        return
                    self.send_json(HTTPStatus.OK, results)
                    return

                if request.path == "/api/paper/create":
                    preview_records = read_json_records(PUBLIC_PAPERS_PATH)
                    exclusion_records = read_csv_rows(exclusions_path)
                    candidate_drafts, mapping_warnings = prepare_mapping_candidates(
                        payload,
                        payload.get("mapping_candidates"),
                        institution_locations=load_confirmed_locations(
                            institution_locations_path
                        ),
                        institution_aliases=load_institution_aliases(
                            institution_aliases_path
                        ),
                    )
                    if (
                        not candidate_drafts
                        and payload.get("acknowledge_missing_mappings") is not True
                    ):
                        self.send_json(
                            HTTPStatus.UNPROCESSABLE_ENTITY,
                            {
                                "error": mapping_warnings[-1],
                                "code": "missing_author_institution_mapping",
                                "warnings": mapping_warnings,
                            },
                        )
                        return
                    try:
                        # Preflight both stores before the first write, then hold
                        # their existing locks for the coupled create operation.
                        load_mappings(mappings_path)
                        load_location_reviews(location_review_path)
                        with CURATED_PAPER_WRITE_LOCK, CURATED_MAPPING_WRITE_LOCK:
                            row = create_curated_paper(
                                payload,
                                preview_records=preview_records,
                                exclusion_records=exclusion_records,
                                path=curated_papers_path,
                            )
                            mapping_result = create_mapping_candidates(
                                row,
                                candidate_drafts,
                                map_records=read_json_records(PUBLIC_MAP_PATH),
                                mappings_path=mappings_path,
                                location_review_path=location_review_path,
                            )
                    except DuplicatePaperError as error:
                        self.send_json(
                            HTTPStatus.CONFLICT,
                            {
                                "error": (
                                    "Paper already exists in the public preview, "
                                    "curated database, or exclusion history."
                                ),
                                "duplicate_matches": error.matches,
                            },
                        )
                        return
                    self.send_json(
                        HTTPStatus.CREATED,
                        {
                            "paper": row,
                            "mapping_candidates": mapping_result["mappings"],
                            "mapping_diagnostic": {
                                "status": (
                                    "candidates_created"
                                    if mapping_result["mappings"]
                                    else "missing_mapping"
                                ),
                                "candidate_count": len(
                                    mapping_result["mappings"]
                                ),
                                "warnings": mapping_warnings,
                            },
                            "warnings": mapping_warnings,
                            "message": (
                                f"Saved to curated database with "
                                f"{len(mapping_result['mappings'])} "
                                "author–institution mapping candidate(s). "
                                "Run Export preview or Full refresh to update "
                                "local public-preview JSON."
                            ),
                        },
                    )
                    return

                _papers, data = load_admin_data(
                    exclusions_path,
                    curated_papers_path,
                )
                paper_id = clean(payload.get("id"))
                if not paper_id:
                    raise AdminDataError("paper id is required")
                paper = data["papers_by_id"].get(paper_id)
                if paper is None:
                    self.send_json(
                        HTTPStatus.NOT_FOUND, {"error": "paper not found"}
                    )
                    return
                if request.path.startswith("/api/paper/mapping"):
                    map_records = read_json_records(PUBLIC_MAP_PATH)
                    try:
                        with CURATED_MAPPING_WRITE_LOCK:
                            if request.path == "/api/paper/mapping/create":
                                result = create_mapping(
                                    paper,
                                    payload,
                                    map_records=map_records,
                                    mappings_path=mappings_path,
                                    location_review_path=location_review_path,
                                )
                                response_status = HTTPStatus.CREATED
                                message = "Curated author–institution mapping saved."
                            elif request.path == "/api/paper/mapping/update":
                                result = update_mapping(
                                    paper,
                                    clean(payload.get("mapping_id")),
                                    payload,
                                    map_records=map_records,
                                    mappings_path=mappings_path,
                                    location_review_path=location_review_path,
                                )
                                response_status = HTTPStatus.OK
                                message = "Curated author–institution mapping updated."
                            elif request.path == "/api/paper/mapping/exclude":
                                result = {
                                    "mapping": exclude_mapping(
                                        paper,
                                        clean(payload.get("mapping_id")),
                                        clean(payload.get("review_note")),
                                        mappings_path=mappings_path,
                                    )
                                }
                                response_status = HTTPStatus.OK
                                message = "Curated mapping excluded; audit history preserved."
                            else:
                                drafts = payload.get("mappings")
                                if not isinstance(drafts, list):
                                    raise CuratedMappingError(
                                        "mappings must be a JSON array"
                                    )
                                result = replace_all_mappings(
                                    paper,
                                    drafts,
                                    clean(payload.get("review_note")),
                                    confirm_replace_all=(
                                        payload.get("confirm_replace_all") is True
                                    ),
                                    map_records=map_records,
                                    mappings_path=mappings_path,
                                    location_review_path=location_review_path,
                                )
                                response_status = HTTPStatus.OK
                                message = (
                                    "All active curated mappings were replaced; "
                                    "prior rows remain as excluded audit records."
                                )
                    except DuplicateMappingError as error:
                        self.send_json(
                            HTTPStatus.CONFLICT,
                            {
                                "error": str(error),
                                "duplicate_mapping": error.mapping,
                            },
                        )
                        return
                    self.send_json(
                        response_status,
                        {**result, "message": message},
                    )
                    return
                if request.path == "/api/paper/delete-or-exclude":
                    reason = clean(payload.get("reason"))
                    review_note = clean(payload.get("review_note"))
                    if not reason:
                        raise AdminDataError("exclusion reason is required")
                    if reason not in ALLOWED_EXCLUSION_REASONS:
                        raise AdminDataError(
                            f"unsupported exclusion reason: {reason!r}"
                        )
                    if not review_note:
                        raise AdminDataError("review note is required")
                    with EXCLUSION_WRITE_LOCK:
                        result = upsert_active_exclusion(
                            paper,
                            reason,
                            review_note,
                            exclusions_path,
                        )
                    response_status = (
                        HTTPStatus.CREATED
                        if result["status"] == "created"
                        else HTTPStatus.OK
                    )
                    self.send_json(
                        response_status,
                        {
                            **result,
                            "message": (
                                "Paper exclusion saved. Run "
                                "export_public_preview.py to update public preview JSON."
                            ),
                        },
                    )
                    return

                restore_note = clean(payload.get("restore_note"))
                if not restore_note:
                    raise AdminDataError("restore note is required")
                with EXCLUSION_WRITE_LOCK:
                    result = restore_active_exclusions(
                        paper,
                        restore_note,
                        exclusions_path,
                    )
                self.send_json(
                    HTTPStatus.OK,
                    {
                        **result,
                        "message": (
                            "Paper exclusion restored. Run "
                            "export_public_preview.py to update public preview JSON."
                        ),
                    },
                )
            except (
                AdminDataError,
                CuratedPaperError,
                CuratedMappingError,
                PaperExclusionError,
                ReviewDecisionError,
                AdminReviewQueueError,
            ) as error:
                if request.path in {
                    "/api/paper/metadata/update",
                    "/api/review/high-risk-markers/action",
                    "/api/review/marker-blockers/action",
                    "/api/review/key-paper-coverage/action",
                    "/api/review/manual-import/action",
                }:
                    self.send_json(
                        HTTPStatus.BAD_REQUEST,
                        api_payload(success=False, errors=(str(error),)),
                    )
                else:
                    self.send_json(
                        HTTPStatus.BAD_REQUEST,
                        {"error": str(error)},
                    )

        def log_message(self, format_string: str, *args: Any) -> None:
            sys.stderr.write(
                f"{self.address_string()} - {format_string % args}\n"
            )

    return AdminRequestHandler


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not 1 <= args.port <= 65535:
        print("ERROR: --port must be between 1 and 65535", file=sys.stderr)
        return 2
    if args.host not in LOOPBACK_HOSTS and not args.unsafe_bind_all:
        print(
            "ERROR: refusing to bind to a non-loopback interface without "
            "--unsafe-bind-all",
            file=sys.stderr,
        )
        return 2

    startup_report = ensure_author_mapping_report(
        companion_path=AUTHOR_MAPPING_MARKDOWN_PATH
    )
    if startup_report.get("generated"):
        print("Generated missing Author Mapping Coverage report.")
    elif not startup_report.get("success"):
        detail = clean(
            startup_report.get("stderr_tail")
            or startup_report.get("stdout_tail")
            or startup_report.get("message")
        )
        print(
            f"WARNING: Author Mapping Coverage report is unavailable: {detail}",
            file=sys.stderr,
        )

    token = secrets.token_urlsafe(32)
    handler = make_handler(
        token,
        args.paper_exclusions,
        args.curated_papers,
        args.curated_mappings,
        args.location_review,
        args.institution_locations,
        args.institution_aliases,
    )
    try:
        server = ThreadingHTTPServer((args.host, args.port), handler)
    except OSError as error:
        print(f"ERROR: could not start admin server: {error}", file=sys.stderr)
        return 1
    server.daemon_threads = True

    display_host = "localhost" if args.host == DEFAULT_HOST else args.host
    print("Local admin server")
    print(f"Admin token: {token}")
    print(f"Open: http://{display_host}:{args.port}/admin/?token={token}")
    print("API authentication: X-Admin-Token header or token query parameter")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping admin server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
