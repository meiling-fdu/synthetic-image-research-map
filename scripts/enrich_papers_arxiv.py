#!/usr/bin/env python3
"""Find arXiv versions of candidate papers for manual review.

Existing arXiv metadata is reused first. Remaining titles are searched through
the arXiv Atom API and matched conservatively; this script never changes the
candidate paper CSV or treats an arXiv year as the publication year.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import sys
import tempfile
import time
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "processed" / "openalex_candidate_papers.csv"
DEFAULT_OUTPUT = ROOT / "data" / "manual" / "paper_arxiv_links.csv"
DEFAULT_KEY_PAPERS = ROOT / "data" / "manual" / "key_papers_enriched.csv"
ARXIV_API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = (
    "synthetic-image-research-map/0.1 "
    "(https://github.com/meiling-fdu/synthetic-image-research-map)"
)
OUTPUT_COLUMNS = (
    "title",
    "year",
    "doi",
    "openalex_url",
    "venue",
    "authors",
    "arxiv_id",
    "arxiv_url",
    "arxiv_year",
    "match_status",
    "title_similarity",
    "author_overlap",
    "match_reason",
    "source",
    "manual_review",
)
COMPLETED_STATUSES = {
    "linked_to_arxiv",
    "possible_arxiv_match",
    "not_found_in_arxiv",
}
ATOM = "{http://www.w3.org/2005/Atom}"
MODERN_ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}(?:v\d+)?$", re.IGNORECASE)
LEGACY_ARXIV_RE = re.compile(
    r"^[a-z-]+(?:\.[a-z-]+)?/\d{7}(?:v\d+)?$", re.IGNORECASE
)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find arXiv versions of candidate papers for manual review."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=positive_int)
    parser.add_argument(
        "--max-new-queries",
        type=nonnegative_int,
        help="Perform at most this many new arXiv network queries in this run.",
    )
    parser.add_argument("--sleep-seconds", type=nonnegative_float, default=3.0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--stop-on-rate-limit",
        action="store_true",
        help="Save partial results and exit successfully if arXiv rate-limits the run.",
    )
    parser.add_argument(
        "--title-contains",
        help="Process only titles containing this text, case-insensitively.",
    )
    return parser.parse_args(argv)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def nonnegative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).casefold()
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", text))


def normalize_doi(value: object) -> str:
    doi = clean(value).casefold()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
    return doi


def normalize_openalex(value: object) -> str:
    identifier = clean(value).casefold().rstrip("/")
    if identifier and not identifier.startswith("http"):
        identifier = f"https://openalex.org/{identifier.rsplit('/', 1)[-1]}"
    return identifier


def extract_arxiv_id(*values: object) -> str:
    for value in values:
        candidate = clean(value)
        if not candidate:
            continue
        doi_match = re.search(
            r"(?:doi\.org/)?10\.48550/arxiv\.([^?#\s]+)",
            candidate,
            flags=re.IGNORECASE,
        )
        url_match = re.search(
            r"arxiv\.org/(?:abs|pdf)/([^?#\s]+)", candidate, flags=re.IGNORECASE
        )
        if doi_match:
            candidate = doi_match.group(1)
        elif url_match:
            candidate = url_match.group(1)
        elif re.search(r"(?:doi\.org/)?10\.", candidate, flags=re.IGNORECASE):
            continue
        candidate = re.sub(r"^arxiv:\s*", "", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"\.pdf$", "", candidate, flags=re.IGNORECASE)
        candidate = candidate.strip(" /.,;)")
        if MODERN_ARXIV_RE.fullmatch(candidate) or LEGACY_ARXIV_RE.fullmatch(candidate):
            return candidate
    return ""


def arxiv_year(arxiv_id: str) -> str:
    identifier = re.sub(r"v\d+$", "", arxiv_id, flags=re.IGNORECASE)
    match = re.match(r"^(\d{2})\d{2}\.", identifier)
    if not match:
        match = re.search(r"/(\d{2})\d{5}$", identifier)
    if not match:
        return ""
    short_year = int(match.group(1))
    return str(1900 + short_year if short_year >= 91 else 2000 + short_year)


def parse_authors(value: object) -> List[str]:
    text = clean(value)
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [clean(item) for item in parsed if clean(item)]
    except json.JSONDecodeError:
        pass
    separator = ";" if ";" in text else ","
    return [part.strip() for part in text.split(separator) if part.strip()]


def author_key(name: str) -> str:
    tokens = normalize_title(name).split()
    if not tokens:
        return ""
    return f"{tokens[-1]}:{tokens[0][0]}"


def author_overlap(left: Iterable[str], right: Iterable[str]) -> Optional[float]:
    left_keys = {author_key(name) for name in left} - {""}
    right_keys = {author_key(name) for name in right} - {""}
    if not left_keys or not right_keys:
        return None
    return len(left_keys & right_keys) / len(left_keys | right_keys)


def row_key(row: Dict[str, str]) -> Tuple[str, str, str]:
    doi = normalize_doi(row.get("doi"))
    openalex = normalize_openalex(row.get("openalex_url") or row.get("openalex_id"))
    title_year = f"{normalize_title(row.get('title'))}|{clean(row.get('year') or row.get('publication_year'))}"
    return doi, openalex, title_year


def index_row(
    index: Dict[Tuple[str, str], Dict[str, str]], row: Dict[str, str]
) -> None:
    """Index a row by each stable key instead of requiring every field to match."""
    doi, openalex, title_year = row_key(row)
    for kind, value in (("doi", doi), ("openalex", openalex), ("title_year", title_year)):
        if value:
            index[(kind, value)] = row


def find_indexed(
    index: Dict[Tuple[str, str], Dict[str, str]], row: Dict[str, str]
) -> Optional[Dict[str, str]]:
    doi, openalex, title_year = row_key(row)
    for kind, value in (("doi", doi), ("openalex", openalex), ("title_year", title_year)):
        if value and (kind, value) in index:
            return index[(kind, value)]
    return None


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def atomic_write(path: Path, rows: Iterable[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def build_known_arxiv_index(path: Path) -> Dict[Tuple[str, str], Dict[str, str]]:
    index: Dict[Tuple[str, str], Dict[str, str]] = {}
    if not path.exists():
        return index
    for row in read_csv(path):
        arxiv_id = extract_arxiv_id(
            row.get("arxiv_id"), row.get("arxiv_url"), row.get("doi"),
            row.get("enriched_doi"), row.get("paper_url"),
            row.get("enriched_paper_url"),
        )
        if not arxiv_id:
            continue
        indexed_row = {
            **row,
            "doi": row.get("doi") or row.get("enriched_doi", ""),
            "openalex_url": row.get("openalex_url") or row.get("enriched_openalex_url", ""),
            "_known_arxiv_id": arxiv_id,
        }
        index_row(index, indexed_row)
    return index


def lookup_known(
    index: Dict[Tuple[str, str], Dict[str, str]], row: Dict[str, str]
) -> Optional[Tuple[str, str]]:
    result = find_indexed(index, row)
    if not result:
        return None
    return result["_known_arxiv_id"], "key_paper_enrichment"


def query_arxiv(title: str) -> List[Dict[str, object]]:
    query_title = normalize_title(title)
    params = urlencode({
        "search_query": f'ti:"{query_title}"',
        "start": 0,
        "max_results": 10,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    request = Request(f"{ARXIV_API_URL}?{params}", headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=45) as response:
        document = ET.fromstring(response.read())
    candidates: List[Dict[str, object]] = []
    for entry in document.findall(f"{ATOM}entry"):
        entry_url = clean(entry.findtext(f"{ATOM}id"))
        arxiv_id = extract_arxiv_id(entry_url)
        if not arxiv_id:
            continue
        candidates.append({
            "title": clean(entry.findtext(f"{ATOM}title")),
            "authors": [
                clean(author.findtext(f"{ATOM}name"))
                for author in entry.findall(f"{ATOM}author")
                if clean(author.findtext(f"{ATOM}name"))
            ],
            "arxiv_id": arxiv_id,
        })
    return candidates


def is_rate_limit_error(error: BaseException) -> bool:
    """Recognize explicit throttling and temporary arXiv overload responses."""
    if isinstance(error, HTTPError) and error.code in {429, 503}:
        return True
    message = str(error).casefold()
    return "rate limit" in message or "too many requests" in message


def score_candidate(
    title: str, authors: List[str], candidate: Dict[str, object]
) -> Tuple[float, Optional[float]]:
    similarity = difflib.SequenceMatcher(
        None, normalize_title(title), normalize_title(candidate["title"])
    ).ratio()
    overlap = author_overlap(authors, candidate["authors"])
    return similarity, overlap


def classify_match(
    title: str, authors: List[str], candidates: List[Dict[str, object]]
) -> Tuple[str, str, str, float, Optional[float]]:
    ranked = []
    for candidate in candidates:
        similarity, overlap = score_candidate(title, authors, candidate)
        ranked.append((similarity, overlap if overlap is not None else -1.0, candidate, overlap))
    if not ranked:
        return "not_found_in_arxiv", "No arXiv results were returned.", "", 0.0, None
    similarity, _, best, overlap = max(ranked, key=lambda item: (item[0], item[1]))
    arxiv_id = str(best["arxiv_id"])
    year_note = arxiv_year(arxiv_id) or "unknown"
    if similarity >= 0.97 or (similarity >= 0.90 and overlap is not None and overlap >= 0.30):
        status = "linked_to_arxiv"
        reason = f"Strong title match; arXiv year {year_note} is diagnostic only."
    elif similarity >= 0.78:
        status = "possible_arxiv_match"
        reason = (
            "Plausible title match without sufficient author support; "
            f"arXiv year {year_note} is diagnostic only."
        )
    else:
        return (
            "not_found_in_arxiv",
            f"Best title similarity {similarity:.3f} was below the review threshold.",
            "",
            similarity,
            overlap,
        )
    return status, reason, arxiv_id, similarity, overlap


def base_output_row(row: Dict[str, str]) -> Dict[str, str]:
    openalex_url = clean(row.get("openalex_url") or row.get("openalex_id"))
    if openalex_url and not openalex_url.startswith("http"):
        openalex_url = f"https://openalex.org/{openalex_url.rsplit('/', 1)[-1]}"
    return {
        "title": clean(row.get("title")),
        "year": clean(row.get("publication_year") or row.get("year")),
        "doi": normalize_doi(row.get("doi")),
        "openalex_url": openalex_url,
        "venue": clean(row.get("venue_name") or row.get("venue")),
        "authors": "; ".join(parse_authors(row.get("authors_ordered") or row.get("authors"))),
        "arxiv_id": "",
        "arxiv_url": "",
        "arxiv_year": "",
        "match_status": "",
        "title_similarity": "",
        "author_overlap": "",
        "match_reason": "",
        "source": "",
        "manual_review": "true",
    }


def set_match(
    output: Dict[str, str], arxiv_id: str, status: str, similarity: object,
    overlap: Optional[float], reason: str, source: str,
) -> None:
    output.update({
        "arxiv_id": arxiv_id,
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
        "arxiv_year": arxiv_year(arxiv_id) if arxiv_id else "",
        "match_status": status,
        "title_similarity": f"{similarity:.3f}" if isinstance(similarity, float) else clean(similarity),
        "author_overlap": f"{overlap:.3f}" if overlap is not None else "",
        "match_reason": reason,
        "source": source,
    })


def append_remaining_completed_rows(
    outputs: List[Dict[str, str]],
    rows: Iterable[Dict[str, str]],
    resume: Dict[Tuple[str, str], Dict[str, str]],
    counts: Counter,
) -> None:
    """Keep later completed cache entries when a network stop ends the loop early."""
    output_index: Dict[Tuple[str, str], Dict[str, str]] = {}
    for output in outputs:
        index_row(output_index, output)
    for row in rows:
        output = base_output_row(row)
        if find_indexed(output_index, output):
            continue
        previous = find_indexed(resume, output)
        if previous and previous.get("match_status") in COMPLETED_STATUSES:
            cached = {column: previous.get(column, "") for column in OUTPUT_COLUMNS}
            outputs.append(cached)
            index_row(output_index, cached)
            counts["reused"] += 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    rows = read_csv(args.input)
    resume: Dict[Tuple[str, str], Dict[str, str]] = {}
    if args.output.exists():
        for resume_row in read_csv(args.output):
            index_row(resume, resume_row)
    known = build_known_arxiv_index(DEFAULT_KEY_PAPERS)
    outputs: List[Dict[str, str]] = []
    counts = Counter(rows_read=len(rows))
    title_filter = (args.title_contains or "").casefold()
    queried_limit = 0
    interrupted = False
    batch_limit_reached = False
    rate_limit_stopped = False

    try:
        for row in rows:
            output = base_output_row(row)
            previous = find_indexed(resume, output)
            if previous and previous.get("match_status") in COMPLETED_STATUSES and not args.force:
                outputs.append({column: previous.get(column, "") for column in OUTPUT_COLUMNS})
                counts["reused"] += 1
                continue
            if title_filter and title_filter not in output["title"].casefold():
                if previous:
                    outputs.append({column: previous.get(column, "") for column in OUTPUT_COLUMNS})
                else:
                    set_match(output, "", "not_searched", "", None, "Not selected by --title-contains.", "not_queried")
                    outputs.append(output)
                continue

            existing_id = extract_arxiv_id(
                row.get("arxiv_id"), row.get("arxiv_url"), row.get("doi"),
                row.get("primary_url"), row.get("landing_page_url"), row.get("url"),
            )
            known_match = lookup_known(known, output)
            if existing_id or known_match:
                arxiv_id, source = (existing_id, "candidate_metadata") if existing_id else known_match
                set_match(
                    output, arxiv_id, "linked_to_arxiv", 1.0, None,
                    "Reused an existing valid arXiv identifier; publication year was preserved.",
                    source,
                )
                outputs.append(output)
                counts["linked_to_arxiv"] += 1
                continue

            if args.limit is not None and queried_limit >= args.limit:
                set_match(output, "", "not_searched", "", None, "Not searched because --limit was reached.", "not_queried")
                outputs.append(output)
                continue

            if not output["title"]:
                set_match(output, "", "not_found_in_arxiv", "", None, "Missing title; arXiv was not queried.", "not_queried")
                outputs.append(output)
                counts["not_found_in_arxiv"] += 1
                continue

            if (
                args.max_new_queries is not None
                and counts["queried"] >= args.max_new_queries
            ):
                batch_limit_reached = True
                set_match(
                    output, "", "not_searched", "", None,
                    "Not searched because --max-new-queries was reached.",
                    "not_queried",
                )
                outputs.append(output)
                continue

            # Count attempted requests so failures cannot bypass the per-run budget.
            counts["queried"] += 1
            queried_limit += 1
            try:
                candidates = query_arxiv(output["title"])
            except (HTTPError, URLError, TimeoutError, ET.ParseError) as error:
                if args.stop_on_rate_limit and is_rate_limit_error(error):
                    rate_limit_stopped = True
                    set_match(
                        output, "", "not_searched", "", None,
                        "Not searched because arXiv rate-limited this run.",
                        "not_queried",
                    )
                    outputs.append(output)
                    print(
                        f"arXiv rate limit encountered: {error}; "
                        "writing partial results and stopping.",
                        file=sys.stderr,
                    )
                    break
                raise
            status, reason, arxiv_id, similarity, overlap = classify_match(
                output["title"], parse_authors(output["authors"]), candidates
            )
            set_match(output, arxiv_id, status, similarity, overlap, reason, "arxiv_api")
            outputs.append(output)
            counts[status] += 1
            atomic_write(args.output, outputs)
            if args.sleep_seconds:
                time.sleep(args.sleep_seconds)
    except KeyboardInterrupt:
        interrupted = True
        print("Interrupted; writing partial results for a later resume.", file=sys.stderr)
    except (HTTPError, URLError, TimeoutError, ET.ParseError) as error:
        interrupted = True
        print(f"arXiv request failed: {error}; writing partial results.", file=sys.stderr)

    if rate_limit_stopped and not args.force:
        append_remaining_completed_rows(outputs, rows, resume, counts)
    if (
        args.max_new_queries is not None
        and counts["queried"] > 0
        and counts["queried"] >= args.max_new_queries
    ):
        batch_limit_reached = True
    atomic_write(args.output, outputs)
    final_counts = Counter(row.get("match_status", "") for row in outputs)
    print(f"Rows read: {counts['rows_read']}")
    print(f"Reused: {counts['reused']}")
    print(f"Queried: {counts['queried']}")
    if args.max_new_queries is not None:
        print(f"Max new queries: {args.max_new_queries}")
    for status in ("linked_to_arxiv", "possible_arxiv_match", "not_found_in_arxiv"):
        print(f"{status}: {final_counts[status]}")
    print(f"Output: {args.output}")
    if batch_limit_reached:
        print("Batch limit reached; partial results were saved.")
    if rate_limit_stopped:
        print(
            "Rate-limit stop requested; partial results were saved and the run can be resumed.",
            file=sys.stderr,
        )
        return 0
    if interrupted:
        print("Partial run saved; rerun the same command to resume.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
