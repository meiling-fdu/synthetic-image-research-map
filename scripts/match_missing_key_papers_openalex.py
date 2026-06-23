#!/usr/bin/env python3
"""Find reviewable OpenAlex matches for key papers missing from the candidate pool."""

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
DEFAULT_COVERAGE_REPORT = ROOT / "data/manual/key_paper_coverage_report.csv"
PROCESSED_FILES = (
    ROOT / "data/manual/key_papers_missing_top50_openalex_matches.csv",
    ROOT / "data/manual/key_papers_missing_top50_import_ready.csv",
    ROOT / "data/manual/key_papers_missing_next50_openalex_matches.csv",
    ROOT / "data/manual/key_papers_missing_next50_import_ready.csv",
    ROOT / "data/manual/key_papers_missing_batch2_openalex_matches.csv",
    ROOT / "data/manual/key_papers_missing_batch2_import_ready.csv",
)
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
DEFAULT_QUERY_DELAY_SECONDS = 1.0
RESULTS_PER_QUERY = 10
YEAR_EXACT_BONUS = 0.03
YEAR_ADJACENT_BONUS = 0.01


class MatchWorkflowError(RuntimeError):
    """A local input, output, or schema error."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--coverage-report",
        default=str(DEFAULT_COVERAGE_REPORT.relative_to(ROOT)),
        help="Coverage report CSV (default: %(default)s).",
    )
    parser.add_argument(
        "--output-prefix",
        required=True,
        help="Output prefix, for example data/manual/key_papers_missing_batch3.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Maximum number of unprocessed candidates to select (default: 50).",
    )
    parser.add_argument(
        "--start-offset",
        type=int,
        default=0,
        help="Offset within the filtered, unprocessed candidate list (default: 0).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Select and summarize candidates without network requests or writes.",
    )
    parser.add_argument(
        "--include-processed",
        "--no-skip-processed",
        dest="skip_processed",
        action="store_false",
        help="Include titles already present in the known match/import files.",
    )
    parser.set_defaults(skip_processed=True)
    return parser.parse_args(argv)


def project_path(value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def clean(value: Any) -> str:
    return str(value or "").strip()


def parse_year(value: Any) -> Optional[int]:
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
            fieldnames = list(reader.fieldnames or [])
            return fieldnames, [dict(row) for row in reader]
    except OSError as error:
        raise MatchWorkflowError(f"Could not read {path}: {error}") from error


def processed_titles() -> set[str]:
    titles: set[str] = set()
    for path in PROCESSED_FILES:
        if not path.exists():
            continue
        _fieldnames, rows = read_csv(path)
        for row in rows:
            normalized = normalize_title(row.get("title"))
            if normalized:
                titles.add(normalized)
    return titles


def select_candidates(
    coverage_rows: Sequence[Dict[str, str]],
    known_titles: set[str],
    skip_processed: bool,
    start_offset: int,
    batch_size: int,
) -> Tuple[List[Dict[str, str]], int]:
    eligible = [
        dict(row)
        for row in coverage_rows
        if clean(row.get("missing_stage")) == "missing_from_candidate_pool"
    ]
    skipped = 0
    if skip_processed:
        unprocessed = []
        for row in eligible:
            if normalize_title(row.get("title")) in known_titles:
                skipped += 1
            else:
                unprocessed.append(row)
        eligible = unprocessed
    return eligible[start_offset : start_offset + batch_size], skipped


def lightly_cleaned_title(title: str) -> str:
    text = unicodedata.normalize("NFKC", title)
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = re.sub(r"\.{3,}", " ", text)
    text = re.sub(r"\s*[.,;]\s*(?:19|20)\d{2}\s*$", "", text)
    text = re.sub(
        r"\s*[.,]\s*(?:arxiv|cvpr|iccv|eccv|wacv|icml|ijcai|aaai|chi|spw)"
        r"(?:\s+workshops?)?\s*,?\s*(?:19|20)\d{2}\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"[^\w\s'?-]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split()).strip(" .,:;-")


def title_variants(title: str) -> List[str]:
    variants = [clean(title)]
    prefix_match = re.split(r"\s*:\s*|\s+(?:-|–|—)\s+", title, maxsplit=1)
    if len(prefix_match) > 1:
        prefix = clean(prefix_match[0])
        if len(prefix) >= 25 and len(prefix.split()) >= 4:
            variants.append(prefix)
    cleaned = lightly_cleaned_title(title)
    if cleaned:
        variants.append(cleaned)

    unique = []
    seen = set()
    for variant in variants:
        normalized = normalize_title(variant)
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(variant)
    return unique


def search_url(query: str) -> str:
    params = urlencode(
        {
            "search": query,
            "sort": "relevance_score:desc",
            "per-page": RESULTS_PER_QUERY,
        }
    )
    return f"{OPENALEX_API}/works?{params}"


def search_works(query: str) -> List[Dict[str, Any]]:
    payload = fetch_json_with_retry(search_url(query))
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
    title: str,
    year: Optional[int],
    work: Dict[str, Any],
) -> float:
    candidate_title = clean(work.get("display_name") or work.get("title"))
    candidate_year = parse_year(work.get("publication_year"))
    return title_similarity(title, candidate_title) + year_bonus(year, candidate_year)


def location_url(work: Dict[str, Any]) -> str:
    for field in ("primary_location", "best_oa_location"):
        location = work.get(field)
        if isinstance(location, dict):
            for key in ("landing_page_url", "pdf_url"):
                value = clean(location.get(key))
                if value:
                    return value
    open_access = work.get("open_access")
    if isinstance(open_access, dict):
        return clean(open_access.get("oa_url"))
    return ""


def publication_venue(work: Dict[str, Any]) -> str:
    primary_location = work.get("primary_location")
    if isinstance(primary_location, dict):
        source = primary_location.get("source")
        if isinstance(source, dict):
            venue = clean(source.get("display_name"))
            if venue:
                return venue
    host_venue = work.get("host_venue")
    if isinstance(host_venue, dict):
        return clean(host_venue.get("display_name"))
    return ""


def is_retracted(work: Dict[str, Any]) -> bool:
    value = work.get("is_retracted")
    if isinstance(value, bool):
        return value
    return clean(value).casefold() in {"1", "true", "yes"}


def status_for(work: Optional[Dict[str, Any]], score: float, failed: bool) -> str:
    if work is None:
        return "query_failed" if failed else "no_match"
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
    row: Dict[str, str],
    query_delay_seconds: float = DEFAULT_QUERY_DELAY_SECONDS,
) -> Dict[str, str]:
    title = clean(row.get("title"))
    year = parse_year(row.get("year"))
    best_work: Optional[Dict[str, Any]] = None
    best_score = -1.0
    failures = []
    queries_made = 0

    for variant in title_variants(title):
        if queries_made:
            time.sleep(query_delay_seconds)
        queries_made += 1
        try:
            works = search_works(variant)
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

    status = status_for(best_work, best_score, bool(failures))
    if best_work is None:
        notes = (
            "OpenAlex queries failed: " + " | ".join(failures)
            if failures
            else "No OpenAlex search results for the generated title variants."
        )
        return {
            **{column: "" for column in MATCH_COLUMNS},
            "title": title,
            "year": clean(row.get("year")),
            "match_status": status,
            "notes": notes,
        }

    retracted = is_retracted(best_work)
    notes = (
        "Best OpenAlex title-search result. Only match_status=yes is eligible "
        "for automatic import-ready output."
    )
    if failures:
        notes += f" {len(failures)} fallback query or queries failed."
    if retracted:
        notes += " Excluded because OpenAlex marks the work as retracted."
    return {
        "title": title,
        "year": clean(row.get("year")),
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
        "primary_url": location_url(best_work),
        "is_retracted": str(retracted).lower(),
        "notes": notes,
    }


def preliminary_labels(row: Dict[str, str]) -> Tuple[str, str]:
    expected = clean(row.get("expected_task")).casefold()
    if expected == "detection_and_source_attribution":
        return "detection_and_source_attribution", "detection_and_source_attribution"
    if expected == "source_attribution":
        return "source_attribution", "generated_image_source_attribution"
    return "detection", "ai_generated_image_detection"


def is_generated_video(row: Dict[str, str]) -> bool:
    expected = clean(row.get("expected_task")).casefold()
    if expected == "generated_video_detection":
        return True
    normalized = normalize_title(row.get("title"))
    has_video = bool(re.search(r"\b(?:video|videos)\b", normalized))
    has_generated_context = bool(
        re.search(r"\b(?:generated|synthetic|deepfake|deepfakes)\b", normalized)
    )
    has_image = bool(re.search(r"\b(?:image|images)\b", normalized))
    return has_video and has_generated_context and not has_image


def import_ready_row(
    candidate: Dict[str, str],
    match: Dict[str, str],
) -> Dict[str, str]:
    task, subtask = preliminary_labels(candidate)
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
            "Strong OpenAlex title match; ready for broad paper-level import. "
            "Marker depends on affiliation/coordinates."
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


def write_csv_atomic(
    path: Path,
    fieldnames: Sequence[str],
    rows: Iterable[Dict[str, str]],
) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise MatchWorkflowError(f"Could not write {path}: {error}") from error


def ensure_outputs_are_new(paths: Iterable[Path]) -> None:
    existing = [path for path in paths if path.exists()]
    if existing:
        formatted = "\n".join(f"  {path}" for path in existing)
        raise MatchWorkflowError(
            "Refusing to overwrite existing manual output files:\n" + formatted
        )


def print_summary(
    candidates: Sequence[Dict[str, str]],
    skipped: int,
    matches: Sequence[Dict[str, str]],
    ready_count: int,
    review_count: int,
    excluded_video: int,
    excluded_retracted: int,
    dry_run: bool,
) -> None:
    counts = Counter(row.get("match_status", "") for row in matches)
    print("Missing key-paper OpenAlex matching summary:")
    print(f"  Candidates selected: {len(candidates)}")
    print(f"  Already processed skipped: {skipped}")
    print(f"  Match status counts: {dict(sorted(counts.items()))}")
    print(f"  Ready count: {ready_count}")
    print(f"  Manual review count: {review_count}")
    print(f"  Excluded generated_video_detection count: {excluded_video}")
    print(f"  Excluded retracted count: {excluded_retracted}")
    print(f"  Query failures: {counts.get('query_failed', 0)}")
    if dry_run:
        print("  Dry run: no network requests were made and no files were written.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.batch_size < 0:
        print("Error: --batch-size must be non-negative.", file=sys.stderr)
        return 2
    if args.start_offset < 0:
        print("Error: --start-offset must be non-negative.", file=sys.stderr)
        return 2

    try:
        coverage_path = project_path(args.coverage_report)
        coverage_fields, coverage_rows = read_csv(coverage_path)
        required_fields = {"title", "year", "missing_stage", "expected_task"}
        missing_fields = sorted(required_fields - set(coverage_fields))
        if missing_fields:
            raise MatchWorkflowError(
                f"{coverage_path} is missing required columns: {missing_fields}"
            )

        known_titles = processed_titles() if args.skip_processed else set()
        candidates, skipped = select_candidates(
            coverage_rows,
            known_titles,
            args.skip_processed,
            args.start_offset,
            args.batch_size,
        )
        if args.dry_run:
            print_summary(candidates, skipped, [], 0, 0, 0, 0, True)
            return 0

        paths = output_paths(project_path(args.output_prefix))
        ensure_outputs_are_new(paths.values())

        matches = []
        ready = []
        review = []
        excluded_video = 0
        excluded_retracted = 0
        for index, candidate in enumerate(candidates):
            if index:
                time.sleep(DEFAULT_QUERY_DELAY_SECONDS)
            match = match_candidate(candidate)
            matches.append(match)
            if match["match_status"] in {"review_high", "review"}:
                review.append(match)
            if match["match_status"] == "excluded_retracted":
                excluded_retracted += 1
                continue
            if match["match_status"] != "yes":
                continue
            if is_generated_video(candidate):
                excluded_video += 1
                match["notes"] += (
                    " Excluded from import-ready output because "
                    "generated_video_detection is unsupported."
                )
                continue
            ready.append(import_ready_row(candidate, match))

        write_csv_atomic(paths["candidates"], coverage_fields, candidates)
        write_csv_atomic(paths["matches"], MATCH_COLUMNS, matches)
        write_csv_atomic(paths["ready"], IMPORT_READY_COLUMNS, ready)
        write_csv_atomic(paths["review"], MATCH_COLUMNS, review)
        print_summary(
            candidates,
            skipped,
            matches,
            len(ready),
            len(review),
            excluded_video,
            excluded_retracted,
            False,
        )
        return 0
    except MatchWorkflowError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
