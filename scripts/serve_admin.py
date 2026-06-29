#!/usr/bin/env python3
"""Serve the local maintainer paper browser and durable exclusion workflow."""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
import re
import secrets
import sys
import threading
import unicodedata
from collections import defaultdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, DefaultDict, Dict, Iterable, List, Mapping, Sequence, Tuple
from urllib.parse import parse_qs, urlsplit

try:
    from .curated_schema import ALLOWED_EXCLUSION_REASONS
    from .paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        restore_active_exclusions,
        upsert_active_exclusion,
    )
except ImportError:
    from curated_schema import ALLOWED_EXCLUSION_REASONS
    from paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        PaperExclusionError,
        restore_active_exclusions,
        upsert_active_exclusion,
    )

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPOSITORY_ROOT / "web"
PUBLIC_PAPERS_PATH = WEB_DIR / "data" / "public_preview_papers.json"
PUBLIC_MAP_PATH = WEB_DIR / "data" / "public_preview_map_data.json"
CURATED_PAPERS_PATH = REPOSITORY_ROOT / "data" / "curated" / "papers.csv"
CURATED_EXCLUSIONS_PATH = DEFAULT_EXCLUSIONS_PATH
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
TRUE_VALUES = {"1", "true", "yes", "y"}
MAX_REQUEST_BYTES = 64 * 1024
EXCLUSION_WRITE_LOCK = threading.Lock()

STATIC_ROUTES = {
    "/admin/": (WEB_DIR / "admin.html", "text/html; charset=utf-8"),
    "/admin.js": (WEB_DIR / "admin.js", "text/javascript; charset=utf-8"),
    "/admin.css": (WEB_DIR / "admin.css", "text/css; charset=utf-8"),
}


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
        "metadata_source",
        "curation_status",
        "review_status",
        "review_note",
        "scope_status",
    ):
        value = curated_record.get(field)
        if clean(value):
            public_record[field] = value
    for field in (
        "title",
        "year",
        "authors",
        "venue",
        "doi",
        "openalex_url",
        "paper_url",
        "publication_type",
        "task",
        "subtask",
        "source_database",
    ):
        if not public_record.get(field) and curated_record.get(field):
            public_record[field] = curated_record[field]


def load_admin_data(
    exclusions_path: Path = CURATED_EXCLUSIONS_PATH,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    public_papers = read_json_records(PUBLIC_PAPERS_PATH)
    map_records = read_json_records(PUBLIC_MAP_PATH)
    curated_rows = read_csv_rows(CURATED_PAPERS_PATH)
    exclusion_rows = read_csv_rows(exclusions_path)

    papers: List[Dict[str, Any]] = []
    paper_identity_index: Dict[str, Dict[str, Any]] = {}
    for source_record in public_papers:
        record = dict(source_record)
        record["record_source"] = "public_preview"
        record["is_in_curated_papers"] = False
        record["curated_record"] = None
        papers.append(record)
        for key in identity_keys(record):
            paper_identity_index.setdefault(key, record)

    for curated_row in curated_rows:
        curated_record = curated_paper_record(curated_row)
        match = next(
            (
                paper_identity_index[key]
                for key in identity_keys(curated_record)
                if key in paper_identity_index
            ),
            None,
        )
        if match is None:
            match = curated_record
            match["is_in_curated_papers"] = True
            match["curated_record"] = dict(curated_row)
            papers.append(match)
            for key in identity_keys(match):
                paper_identity_index.setdefault(key, match)
        else:
            match["is_in_curated_papers"] = True
            match["curated_record"] = dict(curated_row)
            merge_curated_fields(match, curated_record)

    # Keep durable exclusions visible after they disappear from public exports,
    # so maintainers can inspect or restore them later.
    for exclusion_row in exclusion_rows:
        exclusion_record = exclusion_only_paper_record(exclusion_row)
        match = next(
            (
                paper_identity_index[key]
                for key in identity_keys(exclusion_record)
                if key in paper_identity_index
            ),
            None,
        )
        if match is not None:
            continue
        papers.append(exclusion_record)
        for key in identity_keys(exclusion_record):
            paper_identity_index.setdefault(key, exclusion_record)

    marker_index = index_by_identity(map_records)
    exclusion_index = index_by_identity(exclusion_rows)
    for paper in papers:
        markers = [
            marker_for_api(record)
            for record in strongest_matching_records(paper, marker_index)
        ]
        exclusions = matching_records(paper, exclusion_index)
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
        "write_capabilities": ["paper_exclusion", "paper_restore"],
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
    return parser.parse_args(argv)


def make_handler(
    token: str,
    exclusions_path: Path = CURATED_EXCLUSIONS_PATH,
) -> type[BaseHTTPRequestHandler]:
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
            try:
                papers, data = load_admin_data(exclusions_path)
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
            if request.path not in {
                "/api/paper/delete-or-exclude",
                "/api/paper/restore",
            }:
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            try:
                payload = self.read_json_body()
                _papers, data = load_admin_data(exclusions_path)
                paper_id = clean(payload.get("id"))
                if not paper_id:
                    raise AdminDataError("paper id is required")
                paper = data["papers_by_id"].get(paper_id)
                if paper is None:
                    self.send_json(
                        HTTPStatus.NOT_FOUND, {"error": "paper not found"}
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
            except (AdminDataError, PaperExclusionError) as error:
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

    token = secrets.token_urlsafe(32)
    handler = make_handler(token, args.paper_exclusions)
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
