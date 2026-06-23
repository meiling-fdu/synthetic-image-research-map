#!/usr/bin/env python3
"""Diagnose why paper-level public-preview records lack map markers.

This script uses only local exports and processing artifacts. It does not
modify processed data, call external APIs, or infer new institution locations.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


PAPER_PREVIEW_PATH = Path("web/data/public_preview_papers.json")
MAP_PREVIEW_PATH = Path("web/data/public_preview_map_data.json")
KEY_PAPER_REPORT_PATH = Path("data/manual/key_paper_coverage_report.csv")
AFFILIATION_PATHS = (
    Path("data/processed/openalex_candidate_affiliations_geocoded.csv"),
    Path("data/processed/openalex_candidate_affiliations_resolved.csv"),
    Path("data/processed/openalex_candidate_affiliations_in_scope.csv"),
    Path("data/processed/openalex_candidate_affiliations.csv"),
)
DEFAULT_OUTPUT = Path("data/manual/paper_marker_blocker_report.csv")

FIELDS = (
    "title",
    "year",
    "openalex_id",
    "openalex_url",
    "doi",
    "is_key_paper",
    "has_map_location",
    "map_record_count",
    "missing_affiliation",
    "missing_coordinates",
    "needs_review",
    "coverage_status",
    "affiliation_row_count",
    "institution_count",
    "coordinate_row_count",
    "institutions",
    "locations",
    "coordinate_pairs",
    "blocker_type",
    "recommended_action",
)

MISSING_INSTITUTIONS = {"", "unknown", "none", "n/a", "na", "null"}
LOW_CONFIDENCE = {"", "low", "unknown", "unresolved", "none", "n/a", "na"}


def clean_text(value: Any) -> str:
    return str(value if value is not None else "").strip()


def normalize_title(value: Any) -> str:
    normalized = re.sub(r"[^\w]+", " ", clean_text(value).casefold())
    return " ".join(normalized.replace("_", " ").split())


def normalize_openalex(value: Any) -> str:
    normalized = clean_text(value).casefold().rstrip("/")
    if not normalized:
        return ""
    match = re.search(r"(w\d+)$", normalized)
    return match.group(1) if match else normalized


def openalex_url(value: Any) -> str:
    normalized = normalize_openalex(value)
    if re.fullmatch(r"w\d+", normalized):
        return f"https://openalex.org/{normalized.upper()}"
    return clean_text(value)


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return clean_text(value).casefold() in {"1", "true", "yes", "y"}


def parse_year(value: Any) -> Optional[int]:
    try:
        year = int(clean_text(value))
    except ValueError:
        return None
    return year if 0 < year < 10000 else None


def usable_coordinate_pair(latitude: Any, longitude: Any) -> Optional[Tuple[float, float]]:
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return lat, lon


def load_json_records(path: Path) -> List[Dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        records = next(
            (
                payload[key]
                for key in ("papers", "records", "data")
                if isinstance(payload.get(key), list)
            ),
            [],
        )
    else:
        records = []
    return [record for record in records if isinstance(record, dict)]


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def paper_keys(record: Mapping[str, Any]) -> List[Tuple[str, Any]]:
    keys: List[Tuple[str, Any]] = []
    openalex = normalize_openalex(record.get("openalex_url") or record.get("openalex_id"))
    if openalex:
        keys.append(("openalex", openalex))
    title = normalize_title(record.get("title"))
    year = parse_year(record.get("year") or record.get("publication_year"))
    if title:
        keys.append(("title_year", (title, year)))
        keys.append(("title", title))
    return keys


def build_lookup(records: Iterable[Dict[str, Any]]) -> Dict[Tuple[str, Any], List[Dict[str, Any]]]:
    lookup: Dict[Tuple[str, Any], List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        for key in paper_keys(record):
            lookup[key].append(record)
    return lookup


def matching_records(
    record: Mapping[str, Any],
    lookup: Mapping[Tuple[str, Any], List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    seen = set()
    keys = paper_keys(record)
    strong_keys = [key for key in keys if key[0] in {"openalex", "title_year"}]
    for key in strong_keys or keys:
        for match in lookup.get(key, []):
            marker = id(match)
            if marker not in seen:
                seen.add(marker)
                matches.append(match)
    return matches


def affiliation_identity(row: Mapping[str, Any]) -> Tuple[str, ...]:
    return (
        normalize_openalex(row.get("openalex_id")),
        clean_text(row.get("author_openalex_id")).casefold(),
        clean_text(row.get("author_name")).casefold(),
        clean_text(row.get("institution_openalex_id")).casefold(),
        clean_text(row.get("institution_name")).casefold(),
        clean_text(row.get("raw_affiliation_text")).casefold(),
    )


def merge_affiliation_rows(paths: Sequence[Path]) -> List[Dict[str, str]]:
    """Deduplicate repeated pipeline-stage rows, keeping the richest values."""
    merged: Dict[Tuple[str, ...], Dict[str, str]] = {}
    for path in paths:
        for row in load_csv(path):
            key = affiliation_identity(row)
            if not key[0]:
                continue
            current = merged.setdefault(key, {})
            for field, value in row.items():
                if clean_text(value) and not clean_text(current.get(field)):
                    current[field] = value
    return list(merged.values())


def affiliation_institution(row: Mapping[str, Any]) -> str:
    return clean_text(row.get("resolved_institution_name") or row.get("institution_name"))


def affiliation_coordinates(row: Mapping[str, Any]) -> Optional[Tuple[float, float]]:
    resolved = usable_coordinate_pair(
        row.get("resolved_latitude"),
        row.get("resolved_longitude"),
    )
    return resolved or usable_coordinate_pair(row.get("latitude"), row.get("longitude"))


def affiliation_location(row: Mapping[str, Any]) -> str:
    city = clean_text(row.get("resolved_city") or row.get("city"))
    country = clean_text(
        row.get("resolved_country") or row.get("country") or row.get("country_code")
    )
    return ", ".join(part for part in (city, country) if part)


def affiliation_needs_review(row: Mapping[str, Any]) -> bool:
    if clean_text(row.get("needs_review")):
        return parse_bool(row.get("needs_review"))
    return parse_bool(row.get("manual_review"))


def is_low_confidence(row: Mapping[str, Any]) -> bool:
    confidence = clean_text(row.get("resolution_confidence")).casefold()
    return confidence in LOW_CONFIDENCE


def key_paper_titles(rows: Sequence[Mapping[str, Any]]) -> set[str]:
    titles = set()
    for row in rows:
        title = normalize_title(row.get("title"))
        if title:
            titles.add(title)
        preview_title = normalize_title(row.get("best_public_preview_paper_title_match"))
        if preview_title and clean_text(row.get("best_public_preview_paper_title_score")) == "1.000":
            titles.add(preview_title)
    return titles


def classify_blocker(
    preview_record: Mapping[str, Any],
    map_matches: Sequence[Mapping[str, Any]],
    affiliation_rows: Sequence[Mapping[str, Any]],
    coordinate_rows: Sequence[Mapping[str, Any]],
) -> Tuple[str, str]:
    if parse_bool(preview_record.get("has_map_location")) or map_matches:
        return "already_mapped", "no_action"
    if not affiliation_rows:
        return "missing_affiliation_rows", "import_openalex_affiliations"
    if not coordinate_rows:
        has_named_institution = any(
            affiliation_institution(row).casefold() not in MISSING_INSTITUTIONS
            for row in affiliation_rows
        )
        if not has_named_institution:
            return "needs_review_or_low_confidence", "manual_affiliation_review"
        return "has_affiliation_missing_coordinates", "manual_coordinate_review"

    all_coordinates_flagged = all(
        affiliation_needs_review(row) or is_low_confidence(row)
        for row in coordinate_rows
    )
    if all_coordinates_flagged:
        return "needs_review_or_low_confidence", "check_needs_review_confidence"

    in_scope_values = [
        parse_bool(row.get("in_scope"))
        for row in coordinate_rows
        if clean_text(row.get("in_scope"))
    ]
    if in_scope_values and not any(in_scope_values):
        return "has_coordinates_but_filtered", "check_preview_filter_or_cap"

    return "public_preview_cap_or_filter", "check_preview_filter_or_cap"


def semicolon_join(values: Iterable[str]) -> str:
    return "; ".join(sorted({value for value in values if value}))


def coordinate_text(pair: Tuple[float, float]) -> str:
    return f"{pair[0]:.6f},{pair[1]:.6f}"


def build_report(
    paper_records: Sequence[Dict[str, Any]],
    map_records: Sequence[Dict[str, Any]],
    key_rows: Sequence[Dict[str, str]],
    affiliation_rows: Sequence[Dict[str, str]],
) -> List[Dict[str, Any]]:
    map_lookup = build_lookup(map_records)
    affiliation_lookup: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in affiliation_rows:
        affiliation_lookup[normalize_openalex(row.get("openalex_id"))].append(row)
    known_key_titles = key_paper_titles(key_rows)

    report = []
    for paper in paper_records:
        title = clean_text(paper.get("title"))
        year = parse_year(paper.get("year") or paper.get("publication_year"))
        openalex = normalize_openalex(paper.get("openalex_url") or paper.get("openalex_id"))
        matches = matching_records(paper, map_lookup)
        affiliations = affiliation_lookup.get(openalex, [])
        coordinate_rows = [
            row for row in affiliations if affiliation_coordinates(row) is not None
        ]
        institutions = [
            affiliation_institution(row)
            for row in affiliations
            if affiliation_institution(row).casefold() not in MISSING_INSTITUTIONS
        ]
        locations = [affiliation_location(row) for row in affiliations]
        coordinates = [
            coordinate_text(pair)
            for row in coordinate_rows
            if (pair := affiliation_coordinates(row)) is not None
        ]
        blocker_type, action = classify_blocker(
            paper,
            matches,
            affiliations,
            coordinate_rows,
        )
        preview_openalex_url = clean_text(
            paper.get("openalex_url") or paper.get("openalex_id")
        )
        report.append(
            {
                "title": title,
                "year": year or "",
                "openalex_id": openalex.upper() if re.fullmatch(r"w\d+", openalex) else openalex,
                "openalex_url": openalex_url(preview_openalex_url),
                "doi": clean_text(paper.get("doi")),
                "is_key_paper": "yes"
                if normalize_title(title) in known_key_titles
                else "no",
                "has_map_location": "yes"
                if parse_bool(paper.get("has_map_location")) or bool(matches)
                else "no",
                "map_record_count": max(
                    int(paper.get("map_record_count") or 0),
                    len(matches),
                ),
                "missing_affiliation": "yes"
                if parse_bool(paper.get("missing_affiliation"))
                else "no",
                "missing_coordinates": "yes"
                if parse_bool(paper.get("missing_coordinates"))
                else "no",
                "needs_review": "yes" if parse_bool(paper.get("needs_review")) else "no",
                "coverage_status": clean_text(paper.get("coverage_status")),
                "affiliation_row_count": len(affiliations),
                "institution_count": len(set(institutions)),
                "coordinate_row_count": len(coordinate_rows),
                "institutions": semicolon_join(institutions),
                "locations": semicolon_join(locations),
                "coordinate_pairs": semicolon_join(coordinates),
                "blocker_type": blocker_type,
                "recommended_action": action,
            }
        )
    return report


def print_counts(label: str, values: Iterable[str]) -> None:
    print(f"{label}:")
    for value, count in Counter(values).most_common():
        print(f"  {value}: {count}")


def print_summary(rows: Sequence[Mapping[str, Any]], output: Path) -> None:
    without_map = [row for row in rows if row["has_map_location"] == "no"]
    key_without_map = [
        row for row in without_map if row["is_key_paper"] == "yes"
    ]
    missing_coordinate_institutions = Counter()
    for row in without_map:
        if int(row["coordinate_row_count"]) != 0:
            continue
        for institution in clean_text(row["institutions"]).split("; "):
            if institution:
                missing_coordinate_institutions[institution] += 1

    print(f"Wrote: {output}")
    print(f"total paper preview records: {len(rows)}")
    print(f"records without map: {len(without_map)}")
    print(f"key papers without map: {len(key_without_map)}")
    print_counts("blocker_type counts", (row["blocker_type"] for row in rows))
    print_counts(
        "recommended_action counts",
        (row["recommended_action"] for row in rows),
    )
    print("top institutions missing coordinates:")
    if missing_coordinate_institutions:
        for institution, count in missing_coordinate_institutions.most_common(10):
            print(f"  {institution}: {count}")
    else:
        print("  none available")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnose blockers between paper preview records and map markers."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--key-papers-only",
        action="store_true",
        help="Write only records inferred to be key papers.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Write at most N records after optional key-paper filtering.",
    )
    args = parser.parse_args(argv)
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be zero or greater")
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    paper_records = load_json_records(PAPER_PREVIEW_PATH)
    map_records = load_json_records(MAP_PREVIEW_PATH)
    key_rows = load_csv(KEY_PAPER_REPORT_PATH)
    affiliation_rows = merge_affiliation_rows(AFFILIATION_PATHS)
    report = build_report(paper_records, map_records, key_rows, affiliation_rows)

    if args.key_papers_only:
        report = [row for row in report if row["is_key_paper"] == "yes"]
    if args.limit is not None:
        report = report[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(report)

    print_summary(report, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
