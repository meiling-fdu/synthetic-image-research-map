#!/usr/bin/env python3
"""Extract reviewable candidate CSVs from raw OpenAlex JSON archives.

These outputs are automatic candidates only. They are not curated records and this
script must never write to data/manual/.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DEFAULT_INPUT_DIR = Path("data/raw/openalex")
DEFAULT_OUTPUT_DIR = Path("data/processed")
PAPERS_FILENAME = "openalex_candidate_papers.csv"
AFFILIATIONS_FILENAME = "openalex_candidate_affiliations.csv"

PAPER_COLUMNS = (
    "openalex_id",
    "title",
    "year",
    "venue",
    "doi",
    "url",
    "arxiv_id",
    "in_scope",
    "relevance_score",
    "relevance_reason",
    "exclusion_reason",
    "preliminary_task",
    "preliminary_subtask",
    "is_survey",
    "is_deepfake_related",
    "is_image_editing_related",
    "source_query",
    "source_database",
    "manual_review",
    "notes",
)

AFFILIATION_COLUMNS = (
    "openalex_id",
    "author_name",
    "author_position",
    "institution_name",
    "city",
    "country",
    "ror_id",
    "latitude",
    "longitude",
    "raw_affiliation_text",
    "manual_review",
    "notes",
)

DETECTION_PATTERNS = (
    r"\bdetect(?:ion|ing|or|ors|ed)?\b",
    r"\bsynthetic image classifier\b",
    r"\bai-generated image classifier\b",
)
ATTRIBUTION_PATTERNS = (
    r"\battribut(?:e|ed|es|ing|ion)\b",
    r"\bgenerator (?:source )?identification\b",
    r"\bgenerative model identification\b",
    r"\bsource identification\b",
    r"\bmodel provenance\b",
    r"\bgenerator fingerprint(?:ing|s)?\b",
)
SURVEY_PATTERNS = (
    r"\bsurvey\b",
    r"\breview\b",
    r"\boverview\b",
    r"\btaxonomy\b",
    r"\bbenchmark\b",
)
DEEPFAKE_PATTERNS = (
    r"\bdeep[ -]?fake(?:s)?\b",
    r"\bface manipulation\b",
    r"\bfacial manipulation\b",
    r"\bface[ -]?swap(?:ping)?\b",
)
IMAGE_EDITING_PATTERNS = (
    r"\bimage edit(?:ing|ed|s)?\b",
    r"\bimage manipulation\b",
    r"\bmanipulated image(?:s)?\b",
    r"\binpaint(?:ing|ed)?\b",
    r"\bediting attribution\b",
)

GENERATION_RELEVANCE_PATTERNS = (
    ("ai-generated", r"\bai[ -]generated\b"),
    ("synthetic image", r"\bsynthetic images?\b"),
    ("generated image", r"\bgenerated images?\b"),
    ("generative model", r"\bgenerative models?\b"),
    ("GAN", r"\bgans?\b"),
    ("diffusion model", r"\bdiffusion models?\b"),
    ("text-to-image", r"\btext[ -]to[ -]image\b"),
    ("AIGC", r"\baigc\b"),
    ("deepfake", r"\bdeep[ -]?fakes?\b"),
    ("fake image", r"\bfake images?\b"),
    ("synthesized image", r"\bsynthesi[sz]ed images?\b"),
)
TASK_RELEVANCE_PATTERNS = (
    ("detection", r"\bdetection\b"),
    ("detector", r"\bdetectors?\b"),
    ("detect", r"\bdetect(?:s|ed|ing)?\b"),
    ("attribution", r"\battribution\b"),
    ("source attribution", r"\bsource attribution\b"),
    ("generator attribution", r"\bgenerator attribution\b"),
    ("provenance", r"\bprovenance\b"),
    ("forensic", r"\bforensics?\b"),
    ("identification", r"\bidentification\b"),
    ("verification", r"\bverification\b"),
)
EXCLUSION_RELEVANCE_PATTERNS = (
    ("object detection", r"\bobject detection\b"),
    ("change detection", r"\bchange detection\b"),
    ("anomaly detection", r"\banomaly detection\b"),
    ("medical image", r"\bmedical imag(?:e|es|ing)\b"),
    ("remote sensing", r"\bremote sensing\b"),
    ("hyperspectral", r"\bhyperspectral\b"),
    ("disease detection", r"\bdisease detection\b"),
    ("target detection", r"\btarget detection\b"),
    ("authorship attribution", r"\bauthorship attribution\b"),
    ("feature attribution", r"\bfeature attribution\b"),
    ("saliency attribution", r"\bsaliency attribution\b"),
    ("camera model attribution", r"\bcamera model attribution\b"),
    ("sensor attribution", r"\bsensor attribution\b"),
)

CANDIDATE_NOTE = (
    "Automatically extracted OpenAlex candidate; all metadata and preliminary "
    "labels require manual review."
)
AFFILIATION_NOTE = (
    "Automatically extracted OpenAlex authorship/affiliation candidate; verify "
    "the author, institution, and location manually."
)


class ExtractionError(RuntimeError):
    """An expected input or output error that should not produce a traceback."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract preliminary paper and affiliation CSVs from raw OpenAlex JSON. "
            "All rows remain candidates requiring manual review."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Raw OpenAlex JSON directory (default: {DEFAULT_INPUT_DIR}).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Processed CSV directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read and summarize candidates without writing CSV files.",
    )
    return parser.parse_args(argv)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def first_nonempty(*values: Any) -> str:
    for value in values:
        cleaned = clean_text(value)
        if cleaned:
            return cleaned
    return ""


def unique_strings(values: Iterable[Any]) -> List[str]:
    seen = set()
    unique = []
    for value in values:
        cleaned = clean_text(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            unique.append(cleaned)
    return unique


def join_unique(values: Iterable[Any]) -> str:
    return " | ".join(unique_strings(values))


def merge_pipe_values(*values: Any) -> str:
    """Merge existing pipe-delimited fields without repeating their values."""
    parts = []
    for value in values:
        cleaned = clean_text(value)
        if cleaned:
            parts.extend(cleaned.split(" | "))
    return join_unique(parts)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.casefold()).strip()


def matches_any(text: str, patterns: Sequence[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def matched_relevance_terms(
    text: str,
    patterns: Sequence[Tuple[str, str]],
) -> List[str]:
    return [
        label
        for label, pattern in patterns
        if re.search(pattern, text, flags=re.IGNORECASE)
    ]


def classify_relevance(text: str) -> Tuple[bool, int, str, str]:
    """Apply a conservative, reviewable scope filter to title and abstract text."""
    generation_terms = matched_relevance_terms(text, GENERATION_RELEVANCE_PATTERNS)
    task_terms = matched_relevance_terms(text, TASK_RELEVANCE_PATTERNS)
    exclusion_terms = matched_relevance_terms(text, EXCLUSION_RELEVANCE_PATTERNS)

    matched_parts = []
    if generation_terms:
        matched_parts.append(f"generation terms: {', '.join(generation_terms)}")
    if task_terms:
        matched_parts.append(f"task terms: {', '.join(task_terms)}")

    if exclusion_terms:
        relevance_reason = (
            "Matched " + "; ".join(matched_parts) + "."
            if matched_parts
            else "No required generation/task combination matched."
        )
        exclusion_reason = f"Matched exclusion terms: {', '.join(exclusion_terms)}."
        return False, 0, relevance_reason, exclusion_reason

    if generation_terms and task_terms:
        return True, 2, f"Matched {'; '.join(matched_parts)}.", ""

    if generation_terms:
        return (
            False,
            1,
            f"Matched generation terms: {', '.join(generation_terms)}; no task terms matched.",
            "",
        )
    if task_terms:
        return (
            False,
            1,
            f"Matched task terms: {', '.join(task_terms)}; no generation terms matched.",
            "",
        )
    return False, 0, "No generation-related or task-related terms matched.", ""


def reconstruct_abstract(inverted_index: Any) -> str:
    """Rebuild OpenAlex's inverted abstract only for rule-based classification."""
    if not isinstance(inverted_index, dict):
        return ""

    positioned_words = []
    for word, positions in inverted_index.items():
        if not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int) and position >= 0:
                positioned_words.append((position, str(word)))
    positioned_words.sort(key=lambda item: item[0])
    return " ".join(word for _, word in positioned_words)


def classify_task(text: str) -> Tuple[str, str]:
    has_detection = matches_any(text, DETECTION_PATTERNS)
    has_attribution = matches_any(text, ATTRIBUTION_PATTERNS)
    if has_detection and has_attribution:
        return "both", "detection_and_attribution"
    if has_detection:
        return "detection", "synthetic_image_detection"
    if has_attribution:
        return "attribution", "generator_attribution"
    return "uncertain", ""


def merge_task(left: str, right: str) -> Tuple[str, str]:
    tasks = {left, right} - {"", "uncertain"}
    if "both" in tasks or tasks == {"detection", "attribution"}:
        return "both", "detection_and_attribution"
    if "detection" in tasks:
        return "detection", "synthetic_image_detection"
    if "attribution" in tasks:
        return "attribution", "generator_attribution"
    return "uncertain", ""


def normalize_doi(value: Any) -> str:
    doi = clean_text(value)
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)


def normalize_ror(value: Any) -> str:
    ror = clean_text(value)
    return re.sub(r"^https?://ror\.org/", "", ror, flags=re.IGNORECASE)


def normalize_arxiv_id(value: Any) -> str:
    arxiv_id = clean_text(value)
    arxiv_id = re.sub(
        r"^https?://arxiv\.org/(?:abs|pdf)/", "", arxiv_id, flags=re.IGNORECASE
    )
    return arxiv_id.removesuffix(".pdf")


def extract_arxiv_id(work: Dict[str, Any]) -> str:
    ids = work.get("ids") if isinstance(work.get("ids"), dict) else {}
    direct_id = normalize_arxiv_id(ids.get("arxiv"))
    if direct_id:
        return direct_id

    locations = work.get("locations") if isinstance(work.get("locations"), list) else []
    for location in locations:
        if not isinstance(location, dict):
            continue
        source = location.get("source") if isinstance(location.get("source"), dict) else {}
        if clean_text(source.get("display_name")).casefold() != "arxiv":
            continue
        candidate = normalize_arxiv_id(
            first_nonempty(location.get("landing_page_url"), location.get("pdf_url"))
        )
        if candidate:
            return candidate
    return ""


def extract_venue(work: Dict[str, Any]) -> str:
    primary_location = (
        work.get("primary_location")
        if isinstance(work.get("primary_location"), dict)
        else {}
    )
    source = (
        primary_location.get("source")
        if isinstance(primary_location.get("source"), dict)
        else {}
    )
    host_venue = work.get("host_venue") if isinstance(work.get("host_venue"), dict) else {}
    return first_nonempty(
        source.get("display_name"),
        primary_location.get("raw_source_name"),
        host_venue.get("display_name"),
    )


def extract_url(work: Dict[str, Any], openalex_id: str) -> str:
    primary_location = (
        work.get("primary_location")
        if isinstance(work.get("primary_location"), dict)
        else {}
    )
    return first_nonempty(
        primary_location.get("landing_page_url"),
        work.get("doi"),
        openalex_id,
    )


def paper_dedup_key(work: Dict[str, Any], source_marker: str) -> str:
    ids = work.get("ids") if isinstance(work.get("ids"), dict) else {}
    openalex_id = first_nonempty(work.get("id"), ids.get("openalex"))
    if openalex_id:
        return f"openalex:{openalex_id.casefold()}"

    normalized = normalize_title(clean_text(work.get("title")))
    if normalized:
        return f"title:{normalized}"
    return f"missing:{source_marker}"


def make_paper_row(work: Dict[str, Any], source_query: str) -> Dict[str, str]:
    ids = work.get("ids") if isinstance(work.get("ids"), dict) else {}
    openalex_id = first_nonempty(work.get("id"), ids.get("openalex"))
    title = clean_text(work.get("title"))
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    classification_text = f"{title} {abstract}".strip()
    task, subtask = classify_task(classification_text)
    in_scope, relevance_score, relevance_reason, exclusion_reason = (
        classify_relevance(classification_text)
    )

    notes = [CANDIDATE_NOTE]
    if not openalex_id:
        notes.append("OpenAlex ID missing; deduplicated by normalized title when possible.")
    if not title:
        notes.append("Title missing in source record.")

    return {
        "openalex_id": openalex_id,
        "title": title,
        "year": clean_text(work.get("publication_year")),
        "venue": extract_venue(work),
        "doi": normalize_doi(first_nonempty(work.get("doi"), ids.get("doi"))),
        "url": extract_url(work, openalex_id),
        "arxiv_id": extract_arxiv_id(work),
        "in_scope": bool_text(in_scope),
        "relevance_score": str(relevance_score),
        "relevance_reason": relevance_reason,
        "exclusion_reason": exclusion_reason,
        "preliminary_task": task,
        "preliminary_subtask": subtask,
        "is_survey": bool_text(matches_any(title, SURVEY_PATTERNS)),
        "is_deepfake_related": bool_text(matches_any(classification_text, DEEPFAKE_PATTERNS)),
        "is_image_editing_related": bool_text(
            matches_any(classification_text, IMAGE_EDITING_PATTERNS)
        ),
        "source_query": clean_text(source_query),
        "source_database": "OpenAlex",
        "manual_review": "true",
        "notes": " ".join(notes),
    }


def merge_paper_rows(existing: Dict[str, str], incoming: Dict[str, str]) -> None:
    existing_task, existing_subtask = merge_task(
        existing["preliminary_task"], incoming["preliminary_task"]
    )
    existing["preliminary_task"] = existing_task
    existing["preliminary_subtask"] = existing_subtask

    existing["source_query"] = merge_pipe_values(
        existing["source_query"], incoming["source_query"]
    )
    existing["relevance_reason"] = merge_pipe_values(
        existing["relevance_reason"], incoming["relevance_reason"]
    )
    existing["exclusion_reason"] = merge_pipe_values(
        existing["exclusion_reason"], incoming["exclusion_reason"]
    )
    if existing["exclusion_reason"]:
        existing["in_scope"] = "false"
        existing["relevance_score"] = "0"
    else:
        existing["in_scope"] = bool_text(
            existing["in_scope"] == "true" or incoming["in_scope"] == "true"
        )
        existing["relevance_score"] = str(
            max(int(existing["relevance_score"]), int(incoming["relevance_score"]))
        )
    for boolean_column in (
        "is_survey",
        "is_deepfake_related",
        "is_image_editing_related",
    ):
        existing[boolean_column] = bool_text(
            existing[boolean_column] == "true" or incoming[boolean_column] == "true"
        )

    for column in PAPER_COLUMNS:
        if not existing[column] and incoming[column]:
            existing[column] = incoming[column]


def institution_geo(institution: Dict[str, Any]) -> Dict[str, Any]:
    for key in ("geo", "location"):
        value = institution.get(key)
        if isinstance(value, dict):
            return value
    return {}


def raw_strings_for_institution(
    authorship: Dict[str, Any],
    institution: Dict[str, Any],
) -> List[str]:
    institution_id = clean_text(institution.get("id"))
    matched = []
    affiliations = authorship.get("affiliations")
    if isinstance(affiliations, list) and institution_id:
        for affiliation in affiliations:
            if not isinstance(affiliation, dict):
                continue
            institution_ids = affiliation.get("institution_ids")
            if isinstance(institution_ids, list) and institution_id in institution_ids:
                matched.append(affiliation.get("raw_affiliation_string"))

    if matched:
        return unique_strings(matched)
    raw_strings = authorship.get("raw_affiliation_strings")
    return unique_strings(raw_strings if isinstance(raw_strings, list) else [])


def make_affiliation_row(
    openalex_id: str,
    authorship: Dict[str, Any],
    institution: Optional[Dict[str, Any]],
) -> Dict[str, str]:
    author = authorship.get("author") if isinstance(authorship.get("author"), dict) else {}
    institution = institution or {}
    geo = institution_geo(institution)
    raw_strings = raw_strings_for_institution(authorship, institution)
    countries = authorship.get("countries")
    authorship_countries = join_unique(countries if isinstance(countries, list) else [])

    if not institution:
        source_strings = authorship.get("raw_affiliation_strings")
        raw_strings = unique_strings(source_strings if isinstance(source_strings, list) else [])

    return {
        "openalex_id": openalex_id,
        "author_name": first_nonempty(
            author.get("display_name"), authorship.get("raw_author_name")
        ),
        "author_position": clean_text(authorship.get("author_position")),
        "institution_name": clean_text(institution.get("display_name")),
        "city": first_nonempty(geo.get("city"), institution.get("city")),
        "country": first_nonempty(
            geo.get("country"),
            geo.get("country_code"),
            institution.get("country"),
            institution.get("country_code"),
            authorship_countries,
        ),
        "ror_id": normalize_ror(institution.get("ror")),
        "latitude": first_nonempty(geo.get("latitude"), institution.get("latitude")),
        "longitude": first_nonempty(geo.get("longitude"), institution.get("longitude")),
        "raw_affiliation_text": join_unique(raw_strings),
        "manual_review": "true",
        "notes": AFFILIATION_NOTE,
    }


def affiliation_key(
    paper_key: str,
    authorship_index: int,
    row: Dict[str, str],
    institution: Optional[Dict[str, Any]],
) -> Tuple[str, int, str, str]:
    institution = institution or {}
    institution_identity = first_nonempty(
        institution.get("id"), row["ror_id"], row["institution_name"]
    )
    return paper_key, authorship_index, row["author_name"], institution_identity


def merge_affiliation_rows(existing: Dict[str, str], incoming: Dict[str, str]) -> None:
    existing["raw_affiliation_text"] = merge_pipe_values(
        existing["raw_affiliation_text"], incoming["raw_affiliation_text"]
    )
    for column in AFFILIATION_COLUMNS:
        if not existing[column] and incoming[column]:
            existing[column] = incoming[column]


def iter_archive_works(
    path: Path,
) -> Iterable[Tuple[str, Dict[str, Any], str]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as error:
        raise ExtractionError(f"Could not read {path}: {error}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ExtractionError(f"Invalid JSON in {path}: {error}") from error

    if not isinstance(payload, dict):
        raise ExtractionError(f"Expected a JSON object in {path}.")

    source_query = clean_text(payload.get("query"))
    pages = payload.get("pages")
    if isinstance(pages, list):
        response_pages = pages
    elif isinstance(payload.get("results"), list):
        response_pages = [payload]
    else:
        return

    for page_index, page in enumerate(response_pages):
        if not isinstance(page, dict):
            continue
        results = page.get("results")
        if not isinstance(results, list):
            continue
        for result_index, work in enumerate(results):
            if isinstance(work, dict):
                marker = f"{path.name}:{page_index}:{result_index}"
                yield source_query, work, marker


def extract_candidates(
    input_dir: Path,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], int]:
    if not input_dir.is_dir():
        raise ExtractionError(f"Input directory does not exist: {input_dir}")

    json_files = sorted(
        path for path in input_dir.glob("*.json") if not path.name.startswith("manifest_")
    )
    if not json_files:
        raise ExtractionError(f"No raw OpenAlex JSON files found in {input_dir}")

    papers_by_key: Dict[str, Dict[str, str]] = {}
    affiliations_by_key: Dict[Tuple[str, int, str, str], Dict[str, str]] = {}

    for path in json_files:
        for source_query, work, marker in iter_archive_works(path):
            paper_key = paper_dedup_key(work, marker)
            paper_row = make_paper_row(work, source_query)
            existing_paper = papers_by_key.get(paper_key)
            if existing_paper is None:
                papers_by_key[paper_key] = paper_row
            else:
                merge_paper_rows(existing_paper, paper_row)

            authorships = work.get("authorships")
            if not isinstance(authorships, list):
                continue
            for authorship_index, authorship in enumerate(authorships):
                if not isinstance(authorship, dict):
                    continue
                institutions = authorship.get("institutions")
                institution_rows = (
                    [item for item in institutions if isinstance(item, dict)]
                    if isinstance(institutions, list)
                    else []
                )
                if not institution_rows:
                    institution_rows = [None]

                for institution in institution_rows:
                    row = make_affiliation_row(
                        paper_row["openalex_id"], authorship, institution
                    )
                    key = affiliation_key(
                        paper_key, authorship_index, row, institution
                    )
                    existing_affiliation = affiliations_by_key.get(key)
                    if existing_affiliation is None:
                        affiliations_by_key[key] = row
                    else:
                        merge_affiliation_rows(existing_affiliation, row)

    return list(papers_by_key.values()), list(affiliations_by_key.values()), len(json_files)


def write_csv(path: Path, columns: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    except OSError as error:
        raise ExtractionError(f"Could not write {path}: {error}") from error


def run(args: argparse.Namespace) -> int:
    try:
        papers, affiliations, file_count = extract_candidates(args.input_dir)
    except ExtractionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    papers_path = args.output_dir / PAPERS_FILENAME
    affiliations_path = args.output_dir / AFFILIATIONS_FILENAME

    print(f"Read {file_count} raw OpenAlex JSON files from {args.input_dir}")
    print(f"Candidate papers after deduplication: {len(papers)}")
    print(f"Candidate author-institution rows: {len(affiliations)}")
    print(f"Candidates marked in scope: {sum(row['in_scope'] == 'true' for row in papers)}")
    print(
        "Candidates requiring relevance review: "
        f"{sum(row['relevance_score'] == '1' for row in papers)}"
    )
    print(
        "Candidates matched by exclusion terms: "
        f"{sum(bool(row['exclusion_reason']) for row in papers)}"
    )

    if args.dry_run:
        print("DRY RUN: no files were written.")
        print(f"Would write: {papers_path}")
        print(f"Would write: {affiliations_path}")
        return 0

    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(papers_path, PAPER_COLUMNS, papers)
        write_csv(affiliations_path, AFFILIATION_COLUMNS, affiliations)
    except OSError as error:
        print(f"Error: could not create output directory {args.output_dir}: {error}", file=sys.stderr)
        return 1
    except ExtractionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Wrote candidate papers: {papers_path}")
    print(f"Wrote candidate affiliations: {affiliations_path}")
    print("All rows are preliminary candidates with manual_review=true.")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
