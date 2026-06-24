#!/usr/bin/env python3
"""Retry only query-failed key-paper OpenAlex title matches."""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlencode

from openalex_utils import (
    OPENALEX_API,
    OpenAlexFetchError,
    fetch_json_with_retry,
    normalize_title,
    title_similarity,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/manual/key_papers_openalex_problem_review.csv"
DEFAULT_OUTPUT_PREFIX = ROOT / "data/manual/key_papers_query_failed_retry"
DEFAULT_COVERAGE_REPORT = ROOT / "data/manual/key_paper_coverage_report.csv"
DEFAULT_DELAY_SECONDS = 5.0
DEFAULT_MAX_RETRIES = 5
RESULTS_PER_QUERY = 10
YEAR_EXACT_BONUS = 0.03
YEAR_ADJACENT_BONUS = 0.01
MATCH_COLUMNS = (
    "title",
    "year",
    "match_status",
    "best_match_title",
    "best_match_year",
    "similarity",
    "openalex_url",
    "doi",
    "publication_venue",
    "publication_type",
    "primary_url",
    "is_retracted",
    "notes",
)
IMPORT_READY_COLUMNS = (
    "title",
    "year",
    "openalex_url",
    "doi",
    "best_match_title",
    "best_match_year",
    "similarity",
    "publication_venue",
    "publication_type",
    "primary_url",
    "preliminary_task",
    "preliminary_subtask",
    "import_status",
    "notes",
)
VENUE_HINTS = (
    "aaai",
    "acm mm",
    "bmvc",
    "ccwc",
    "chi",
    "cvpr",
    "eccv",
    "icassp",
    "iccv",
    "icml",
    "ijcai",
    "mmm",
    "neurips",
    "spw",
    "wacv",
    "wdc",
)


class RetryWorkflowError(RuntimeError):
    """A local input, output, or schema error."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT.relative_to(ROOT)),
        help="Consolidated OpenAlex problem-review CSV.",
    )
    parser.add_argument(
        "--output-prefix",
        default=str(DEFAULT_OUTPUT_PREFIX.relative_to(ROOT)),
        help="Prefix for the four retry output CSVs.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum de-duplicated query-failed rows to process.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Select and summarize rows without requests or writes.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help="Minimum delay between OpenAlex requests (default: %(default)s).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help="Retries for rate limits and transient failures (default: %(default)s).",
    )
    return parser.parse_args(argv)


def project_path(value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def clean(value: object) -> str:
    return str(value or "").strip()


def parse_year(value: object) -> Optional[int]:
    text = clean(value)
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        match = re.search(r"\b(?:19|20)\d{2}\b", text)
        return int(match.group(0)) if match else None


def read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), [dict(row) for row in reader]
    except OSError as error:
        raise RetryWorkflowError(f"Could not read {path}: {error}") from error


def write_csv_atomic(
    path: Path,
    fieldnames: Sequence[str],
    rows: Iterable[Dict[str, str]],
) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=fieldnames, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise RetryWorkflowError(f"Could not write {path}: {error}") from error


def title_year_key(row: Dict[str, str]) -> Tuple[str, str]:
    return normalize_title(row.get("title")), clean(row.get("year"))


def select_candidates(
    rows: Sequence[Dict[str, str]], limit: Optional[int]
) -> List[Dict[str, str]]:
    selected = []
    seen = set()
    for source in rows:
        if clean(source.get("match_status")).casefold() != "query_failed":
            continue
        key = title_year_key(source)
        if not key[0] or key in seen:
            continue
        seen.add(key)
        selected.append(dict(source))
        if limit is not None and len(selected) >= limit:
            break
    return selected


def cleaned_title(title: str) -> str:
    text = unicodedata.normalize("NFKC", title)
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = re.sub(r"\s*[\[(][^\])]{1,100}[\])]\s*", " ", text)
    text = re.sub(r"\s*\bcite\s*:\s*\d+\+?\s*", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:19|20)\d{6}\b", " ", text)
    venues = "|".join(re.escape(value) for value in VENUE_HINTS)
    text = re.sub(
        rf"\s*[.,;:-]\s*(?:{venues})(?:\s+workshops?)?"
        rf"(?:\s*[,;-]?\s*(?:19|20)\d{{2}})?\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s*[.,;:-]\s*(?:19|20)\d{2}\s*$", "", text)
    # OpenAlex search can reject otherwise valid encoded punctuation such as
    # question marks, so the fallback variant keeps words but simplifies marks.
    text = re.sub(r"[^\w\s'’-]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .,:;-")


def title_prefix(title: str) -> str:
    parts = re.split(r"\s*:\s*|\s+(?:-|–|—)\s+", title, maxsplit=1)
    if len(parts) < 2:
        return ""
    prefix = clean(parts[0])
    return prefix if len(prefix) >= 25 and len(prefix.split()) >= 4 else ""


def title_variants(title: str) -> List[str]:
    variants = [clean(title), cleaned_title(title), title_prefix(title)]
    unique = []
    seen = set()
    for variant in variants:
        query_key = " ".join(variant.casefold().split())
        if query_key and query_key not in seen:
            seen.add(query_key)
            unique.append(variant)
    return unique


def search_url(query: str) -> str:
    return f"{OPENALEX_API}/works?" + urlencode(
        {
            "search": query,
            "sort": "relevance_score:desc",
            "per-page": RESULTS_PER_QUERY,
        }
    )


class RequestPacer:
    """Enforce a conservative minimum delay between OpenAlex requests."""

    def __init__(self, delay_seconds: float) -> None:
        self.delay_seconds = delay_seconds
        self.last_request_at: Optional[float] = None

    def wait(self) -> None:
        if self.last_request_at is not None:
            elapsed = time.monotonic() - self.last_request_at
            remaining = self.delay_seconds - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self.last_request_at = time.monotonic()


def search_works(
    query: str,
    pacer: RequestPacer,
    max_retries: int,
    retry_sleep_seconds: float,
) -> List[Dict[str, Any]]:
    pacer.wait()
    payload = fetch_json_with_retry(
        search_url(query),
        max_retries=max_retries,
        base_sleep_seconds=retry_sleep_seconds,
    )
    results = payload.get("results")
    if not isinstance(results, list):
        return []
    return [result for result in results if isinstance(result, dict)]


def year_bonus(expected_year: Optional[int], candidate_year: Optional[int]) -> float:
    if expected_year is None or candidate_year is None:
        return 0.0
    difference = abs(expected_year - candidate_year)
    if difference == 0:
        return YEAR_EXACT_BONUS
    if difference == 1:
        return YEAR_ADJACENT_BONUS
    return 0.0


def candidate_score(
    title: str, year: Optional[int], work: Dict[str, Any]
) -> float:
    candidate_title = clean(work.get("display_name") or work.get("title"))
    return title_similarity(title, candidate_title) + year_bonus(
        year, parse_year(work.get("publication_year"))
    )


def publication_venue(work: Dict[str, Any]) -> str:
    primary_location = work.get("primary_location")
    if isinstance(primary_location, dict):
        source = primary_location.get("source")
        if isinstance(source, dict):
            venue = clean(source.get("display_name"))
            if venue:
                return venue
    host_venue = work.get("host_venue")
    return clean(host_venue.get("display_name")) if isinstance(host_venue, dict) else ""


def primary_url(work: Dict[str, Any]) -> str:
    for field in ("primary_location", "best_oa_location"):
        location = work.get(field)
        if isinstance(location, dict):
            for key in ("landing_page_url", "pdf_url"):
                value = clean(location.get(key))
                if value:
                    return value
    open_access = work.get("open_access")
    return clean(open_access.get("oa_url")) if isinstance(open_access, dict) else ""


def is_retracted(work: Dict[str, Any]) -> bool:
    value = work.get("is_retracted")
    return value if isinstance(value, bool) else clean(value).casefold() in {
        "1",
        "true",
        "yes",
    }


def match_status(
    work: Optional[Dict[str, Any]], score: float, failures: Sequence[str]
) -> str:
    if work is None:
        return "query_failed" if failures else "no_match"
    if is_retracted(work):
        return "excluded_retracted"
    if score >= 0.85:
        return "yes"
    if score >= 0.78:
        return "review_high"
    if score >= 0.72:
        return "review"
    return "weak_match"


def match_candidate(
    candidate: Dict[str, str],
    pacer: RequestPacer,
    max_retries: int,
    retry_sleep_seconds: float,
) -> Dict[str, str]:
    title = clean(candidate.get("title"))
    year = parse_year(candidate.get("year"))
    best_work: Optional[Dict[str, Any]] = None
    best_score = -1.0
    failures = []
    attempted = []

    for variant in title_variants(title):
        attempted.append(variant)
        try:
            works = search_works(
                variant, pacer, max_retries, retry_sleep_seconds
            )
        except OpenAlexFetchError as error:
            failures.append(f"{variant!r}: {error}")
            continue
        for work in works:
            score = candidate_score(title, year, work)
            if score > best_score:
                best_work = work
                best_score = score
        if best_work is not None and best_score >= 0.85:
            break

    status = match_status(best_work, best_score, failures)
    if best_work is None:
        notes = (
            "OpenAlex retry queries failed: " + " | ".join(failures)
            if failures
            else "No OpenAlex results for retry title variants."
        )
        return {
            **{column: "" for column in MATCH_COLUMNS},
            "title": title,
            "year": clean(candidate.get("year")),
            "match_status": status,
            "notes": notes,
        }

    retracted = is_retracted(best_work)
    notes = (
        f"Best result from {len(attempted)} conservative retry title variant(s). "
        "Only match_status=yes is eligible for import-ready output."
    )
    if failures:
        notes += f" {len(failures)} query variant(s) failed."
    if retracted:
        notes += " Excluded because OpenAlex marks the work as retracted."
    return {
        "title": title,
        "year": clean(candidate.get("year")),
        "match_status": status,
        "best_match_title": clean(
            best_work.get("display_name") or best_work.get("title")
        ),
        "best_match_year": clean(best_work.get("publication_year")),
        "similarity": f"{best_score:.3f}",
        "openalex_url": clean(best_work.get("id")),
        "doi": clean(best_work.get("doi")),
        "publication_venue": publication_venue(best_work),
        "publication_type": clean(best_work.get("type")),
        "primary_url": primary_url(best_work),
        "is_retracted": str(retracted).lower(),
        "notes": notes,
    }


def coverage_tasks() -> Dict[Tuple[str, str], str]:
    if not DEFAULT_COVERAGE_REPORT.exists():
        return {}
    _header, rows = read_csv(DEFAULT_COVERAGE_REPORT)
    return {
        title_year_key(row): clean(row.get("expected_task")).casefold()
        for row in rows
        if clean(row.get("expected_task"))
    }


def preliminary_labels(
    candidate: Dict[str, str], tasks: Dict[Tuple[str, str], str]
) -> Tuple[str, str]:
    expected = tasks.get(title_year_key(candidate), "")
    if expected == "generated_video_detection":
        return "detection", "generated_video_detection"
    if expected == "detection_and_source_attribution":
        return "detection_and_source_attribution", "detection_and_source_attribution"
    if expected == "source_attribution":
        return "source_attribution", "generated_image_source_attribution"
    return "detection", "ai_generated_image_detection"


def is_generated_video(
    candidate: Dict[str, str], task: str, subtask: str
) -> bool:
    if "generated_video_detection" in {task.casefold(), subtask.casefold()}:
        return True
    normalized = normalize_title(candidate.get("title"))
    has_video = bool(re.search(r"\bvideos?\b", normalized))
    has_generated = bool(
        re.search(r"\b(?:generated|synthetic|deepfakes?)\b", normalized)
    )
    has_image = bool(re.search(r"\bimages?\b", normalized))
    return has_video and has_generated and not has_image


def import_ready_row(
    candidate: Dict[str, str],
    match: Dict[str, str],
    tasks: Dict[Tuple[str, str], str],
) -> Optional[Dict[str, str]]:
    task, subtask = preliminary_labels(candidate, tasks)
    if is_generated_video(candidate, task, subtask):
        match["notes"] += (
            " Excluded from import-ready output because "
            "generated_video_detection is unsupported."
        )
        return None
    return {
        "title": match["title"],
        "year": match["year"],
        "openalex_url": match["openalex_url"],
        "doi": match["doi"],
        "best_match_title": match["best_match_title"],
        "best_match_year": match["best_match_year"],
        "similarity": match["similarity"],
        "publication_venue": match["publication_venue"],
        "publication_type": match["publication_type"],
        "primary_url": match["primary_url"],
        "preliminary_task": task,
        "preliminary_subtask": subtask,
        "import_status": "ready",
        "notes": (
            "Strong OpenAlex match recovered by conservative query-failure retry. "
            "Ready for manual paper import review."
        ),
    }


def output_paths(prefix: Path) -> Dict[str, Path]:
    base = str(prefix)
    return {
        "candidates": Path(base + "_candidates.csv"),
        "matches": Path(base + "_openalex_matches.csv"),
        "ready": Path(base + "_import_ready.csv"),
        "review": Path(base + "_manual_review.csv"),
    }


def ensure_outputs_are_new(paths: Iterable[Path]) -> None:
    existing = [path for path in paths if path.exists()]
    if existing:
        formatted = "\n".join(f"  {path}" for path in existing)
        raise RetryWorkflowError(
            "Refusing to overwrite existing manual output files:\n" + formatted
        )


def print_summary(
    candidates: Sequence[Dict[str, str]],
    matches: Sequence[Dict[str, str]],
    ready_count: int,
    review_count: int,
    excluded_video: int,
    dry_run: bool,
) -> None:
    counts = Counter(clean(row.get("match_status")) for row in matches)
    terminal_failures = sum(
        "OpenAlex retry queries failed:" in clean(row.get("notes")) for row in matches
    )
    terminal_429 = sum(
        "HTTP 429" in clean(row.get("notes")) for row in matches
    )
    print("OpenAlex query-failed retry summary:")
    print(f"  Candidates: {len(candidates)}")
    print(f"  Match status counts: {dict(sorted(counts.items()))}")
    print(f"  Ready count: {ready_count}")
    print(f"  Manual review count: {review_count}")
    print(f"  Query failed count: {counts.get('query_failed', 0)}")
    print(f"  Excluded retracted count: {counts.get('excluded_retracted', 0)}")
    print(f"  Excluded generated_video_detection count: {excluded_video}")
    print(f"  Terminal fetch-failure records: {terminal_failures}")
    print(f"  Terminal HTTP 429 records: {terminal_429}")
    if dry_run:
        print("  Dry run: no network requests were made and no files were written.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.limit is not None and args.limit < 0:
        print("Error: --limit must be non-negative.", file=sys.stderr)
        return 2
    if args.delay_seconds < 0:
        print("Error: --delay-seconds must be non-negative.", file=sys.stderr)
        return 2
    if args.max_retries < 0:
        print("Error: --max-retries must be non-negative.", file=sys.stderr)
        return 2

    try:
        input_path = project_path(args.input)
        input_fields, input_rows = read_csv(input_path)
        required = {"title", "year", "match_status"}
        missing = sorted(required - set(input_fields))
        if missing:
            raise RetryWorkflowError(
                f"{input_path} is missing required columns: {missing}"
            )
        candidates = select_candidates(input_rows, args.limit)
        if args.dry_run:
            print_summary(candidates, [], 0, 0, 0, True)
            return 0

        paths = output_paths(project_path(args.output_prefix))
        ensure_outputs_are_new(paths.values())
        tasks = coverage_tasks()
        pacer = RequestPacer(args.delay_seconds)
        matches = []
        ready = []
        review = []
        excluded_video = 0
        for candidate in candidates:
            match = match_candidate(
                candidate,
                pacer,
                args.max_retries,
                max(args.delay_seconds, 1.0),
            )
            matches.append(match)
            if match["match_status"] in {"review_high", "review"}:
                review.append(match)
            if match["match_status"] != "yes":
                continue
            ready_row = import_ready_row(candidate, match, tasks)
            if ready_row is None:
                excluded_video += 1
            else:
                ready.append(ready_row)

        write_csv_atomic(paths["candidates"], input_fields, candidates)
        write_csv_atomic(paths["matches"], MATCH_COLUMNS, matches)
        write_csv_atomic(paths["ready"], IMPORT_READY_COLUMNS, ready)
        write_csv_atomic(paths["review"], MATCH_COLUMNS, review)
        print_summary(
            candidates,
            matches,
            len(ready),
            len(review),
            excluded_video,
            False,
        )
        return 0
    except RetryWorkflowError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
