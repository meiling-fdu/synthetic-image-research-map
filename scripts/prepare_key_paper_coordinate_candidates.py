#!/usr/bin/env python3
"""Prepare local-only coordinate candidates for manual key-paper review."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DIAGNOSTICS = Path("data/manual/key_paper_coordinate_diagnostics.csv")
OUTPUT = Path("data/manual/key_paper_coordinate_candidates.csv")
REVIEW_MD = Path("data/manual/key_paper_coordinate_candidates_review.md")
AFFILIATION_ENRICHMENT = Path("data/manual/key_paper_affiliation_enrichment.csv")
CANDIDATE_MAP_JSON = Path("web/data/openalex_candidate_map_data.json")
PUBLIC_PREVIEW_JSON = Path("web/data/public_preview_map_data.json")

INSTITUTION_RECORD_OVERRIDES = Path("data/manual/institution_record_overrides.csv")
INSTITUTION_RESOLUTION_CACHE = Path("data/processed/institution_resolution_cache.json")

SEDID_TITLE = "Exposing the Fake: Effective Diffusion-Generated Images Detection"

OUTPUT_COLUMNS = [
    "title",
    "year",
    "normalized_title",
    "openalex_url",
    "doi",
    "author",
    "author_position",
    "institution",
    "city",
    "region",
    "country",
    "country_code",
    "current_latitude",
    "current_longitude",
    "candidate_latitude",
    "candidate_longitude",
    "candidate_source",
    "candidate_source_detail",
    "candidate_confidence",
    "coordinate_status",
    "apply_status",
    "risk_flags",
    "notes",
]

DIAGNOSTIC_COLUMNS = {
    "title",
    "year",
    "normalized_title",
    "openalex_url",
    "doi",
    "author",
    "author_position",
    "institution",
    "city",
    "region",
    "country",
    "country_code",
    "latitude",
    "longitude",
    "coordinate_status",
    "coordinate_source",
    "recommended_action",
    "notes",
}

ALLOWED_APPLY_STATUSES = {
    "proposed",
    "needs_manual_review",
    "rejected",
    "confirmed",
}
ALLOWED_CONFIDENCE = {"high", "medium", "low", "unresolved"}
CORPORATE_OR_LAB_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bai\b",
        r"\blab\b",
        r"\blaborator(?:y|ies)\b",
        r"\bresearch\b",
        r"\binc\.?\b",
        r"\bcorp(?:oration)?\b",
        r"\bcompany\b",
        r"\btencent\b",
        r"\bhuawei\b",
        r"\bibm\b",
        r"\bsony\b",
        r"\bxiaohongshu\b",
        r"\bant group\b",
    ]
]
PRESERVE_COLUMNS = {
    "candidate_latitude",
    "candidate_longitude",
    "candidate_source",
    "candidate_source_detail",
    "candidate_confidence",
    "apply_status",
    "risk_flags",
    "notes",
}


class CandidateError(RuntimeError):
    """An expected local input, validation, or output error."""


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: Any) -> str:
    title = clean_text(value).casefold()
    title = title.replace("‐", "-").replace("–", "-").replace("—", "-")
    title = title.replace("real-world", "real world")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", title).split())


def normalize_institution_name(value: Any) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", clean_text(value).casefold()).split())


def parse_coordinate(value: Any, minimum: float, maximum: float) -> Optional[float]:
    text = clean_text(value)
    if not text:
        return None
    try:
        coordinate = float(text)
    except ValueError:
        return None
    if math.isfinite(coordinate) and minimum <= coordinate <= maximum:
        return coordinate
    return None


def valid_coordinate_pair(row: Dict[str, Any], prefix: str = "") -> Optional[Tuple[float, float]]:
    latitude_key = f"{prefix}latitude"
    longitude_key = f"{prefix}longitude"
    latitude = parse_coordinate(row.get(latitude_key), -90.0, 90.0)
    longitude = parse_coordinate(row.get(longitude_key), -180.0, 180.0)
    if latitude is not None and longitude is not None:
        return latitude, longitude
    return None


def read_csv(
    path: Path,
    required_columns: Iterable[str],
    optional: bool = False,
) -> List[Dict[str, str]]:
    if not path.exists():
        if optional:
            return []
        raise CandidateError(f"Required local input does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(set(required_columns) - set(reader.fieldnames or []))
            if missing:
                raise CandidateError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise CandidateError(f"Could not read {path}: {error}") from error


def read_json(path: Path, optional: bool = True) -> Dict[str, Any]:
    if not path.exists():
        if optional:
            return {}
        raise CandidateError(f"Required local input does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise CandidateError(f"Could not read {path}: {error}") from error
    return payload if isinstance(payload, dict) else {}


def file_hash(path: Path) -> str:
    import hashlib

    if not path.exists():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_key(row: Dict[str, Any]) -> Tuple[str, str, str, str]:
    return (
        clean_text(row.get("normalized_title")) or normalize_title(row.get("title")),
        clean_text(row.get("author")).casefold(),
        clean_text(row.get("author_position")),
        normalize_institution_name(row.get("institution")),
    )


def sort_key(row: Dict[str, Any]) -> Tuple[str, str, int, str]:
    try:
        position = int(clean_text(row.get("author_position")))
    except ValueError:
        position = 999999
    return (
        clean_text(row.get("title")).casefold(),
        normalize_institution_name(row.get("institution")),
        position,
        clean_text(row.get("author")).casefold(),
    )


def source_parts(source: str) -> Tuple[str, str]:
    cleaned = clean_text(source)
    if ":" in cleaned:
        head, tail = cleaned.split(":", 1)
        return head, tail
    return cleaned, cleaned


def has_corporate_or_lab_risk(institution: str) -> bool:
    return any(pattern.search(institution) for pattern in CORPORATE_OR_LAB_PATTERNS)


def merge_flags(*flag_groups: Any) -> str:
    flags: List[str] = []
    for group in flag_groups:
        for flag in str(group or "").split(";"):
            cleaned = clean_text(flag)
            if cleaned and cleaned not in flags:
                flags.append(cleaned)
    return "; ".join(flags)


def local_coordinate_entry(
    latitude: float,
    longitude: float,
    source: str,
    detail: str,
) -> Dict[str, str]:
    return {
        "latitude": f"{latitude:.8g}",
        "longitude": f"{longitude:.8g}",
        "source": source,
        "detail": detail,
    }


def add_local_coordinate(
    index: Dict[str, List[Dict[str, str]]],
    institution: Any,
    entry: Dict[str, str],
) -> None:
    key = normalize_institution_name(institution)
    if key:
        index[key].append(entry)


def build_local_coordinate_index() -> Dict[str, List[Dict[str, str]]]:
    index: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in read_csv(
        INSTITUTION_RECORD_OVERRIDES,
        {"institution", "latitude", "longitude", "notes"},
        optional=True,
    ):
        pair = valid_coordinate_pair(row)
        if pair is None:
            continue
        add_local_coordinate(
            index,
            row.get("institution"),
            local_coordinate_entry(
                pair[0],
                pair[1],
                "data/manual/institution_record_overrides.csv",
                clean_text(row.get("notes")) or "manual institution record override",
            ),
        )

    resolution_cache = read_json(INSTITUTION_RESOLUTION_CACHE)
    records = resolution_cache.get("records", {})
    if isinstance(records, dict):
        for record in records.values():
            if not isinstance(record, dict) or record.get("status") != "resolved":
                continue
            latitude = parse_coordinate(record.get("resolved_latitude"), -90.0, 90.0)
            longitude = parse_coordinate(record.get("resolved_longitude"), -180.0, 180.0)
            if latitude is None or longitude is None:
                continue
            source = "data/processed/institution_resolution_cache.json"
            detail = clean_text(record.get("provider")) or "local institution resolution cache"
            entry = local_coordinate_entry(latitude, longitude, source, detail)
            add_local_coordinate(index, record.get("resolved_institution_name"), entry)
            for name in record.get("match_names", []):
                add_local_coordinate(index, name, entry)

    deduped: Dict[str, List[Dict[str, str]]] = {}
    for key, entries in index.items():
        seen = set()
        unique = []
        for entry in entries:
            identity = (
                entry["latitude"],
                entry["longitude"],
                entry["source"],
                entry["detail"],
            )
            if identity in seen:
                continue
            seen.add(identity)
            unique.append(entry)
        deduped[key] = unique
    return deduped


def exact_local_match(
    row: Dict[str, str],
    index: Dict[str, List[Dict[str, str]]],
) -> Optional[Dict[str, str]]:
    matches = index.get(normalize_institution_name(row.get("institution")), [])
    if len(matches) == 1:
        return matches[0]
    if not matches:
        return None
    latitude = clean_text(row.get("latitude"))
    longitude = clean_text(row.get("longitude"))
    if latitude and longitude:
        same_coordinate = [
            match
            for match in matches
            if match["latitude"] == latitude and match["longitude"] == longitude
        ]
        if len(same_coordinate) == 1:
            return same_coordinate[0]
    return None


def proposed_row_from_diagnostic(
    row: Dict[str, str],
    local_index: Dict[str, List[Dict[str, str]]],
    include_review_needed: bool,
) -> Optional[Dict[str, str]]:
    status = clean_text(row.get("coordinate_status"))
    institution = clean_text(row.get("institution"))
    risk_flags: List[str] = []
    candidate_latitude = ""
    candidate_longitude = ""
    candidate_source = ""
    candidate_source_detail = ""
    confidence = "unresolved"
    apply_status = "needs_manual_review"

    if has_corporate_or_lab_risk(institution):
        risk_flags.append("corporate_or_lab_institution")

    if status == "has_valid_coordinates":
        if not clean_text(row.get("latitude")) or not clean_text(row.get("longitude")):
            return None
        candidate_latitude = clean_text(row.get("latitude"))
        candidate_longitude = clean_text(row.get("longitude"))
        candidate_source, candidate_source_detail = source_parts(
            row.get("coordinate_source")
        )
        local_match = exact_local_match(row, local_index)
        if local_match:
            candidate_source = candidate_source or local_match["source"]
            candidate_source_detail = candidate_source_detail or local_match["detail"]
            confidence = "high"
            apply_status = "proposed"
            risk_flags.append("exact_local_coordinate_match")
        else:
            confidence = "medium"
            apply_status = "needs_manual_review"
            risk_flags.append("coordinate_requires_manual_source_review")
    elif status == "missing_coordinates_but_has_city_country":
        local_match = exact_local_match(row, local_index)
        if local_match is None:
            if not include_review_needed:
                return None
            risk_flags.append("no_exact_local_coordinate_match")
        else:
            candidate_latitude = local_match["latitude"]
            candidate_longitude = local_match["longitude"]
            candidate_source = local_match["source"]
            candidate_source_detail = local_match["detail"]
            confidence = "high"
            apply_status = "proposed"
            risk_flags.append("exact_local_coordinate_match")
    elif status == "ambiguous_institution_location" and include_review_needed:
        risk_flags.append("ambiguous_institution_location")
        apply_status = "needs_manual_review"
    elif include_review_needed and status in {
        "missing_city_country",
        "missing_affiliation_records",
        "needs_manual_coordinate_review",
    }:
        risk_flags.append(status)
        apply_status = "needs_manual_review"
    else:
        return None

    if risk_flags and "corporate_or_lab_institution" in risk_flags and not candidate_source:
        candidate_latitude = ""
        candidate_longitude = ""
        confidence = "unresolved"
        apply_status = "needs_manual_review"

    return {
        "title": clean_text(row.get("title")),
        "year": clean_text(row.get("year")),
        "normalized_title": clean_text(row.get("normalized_title")),
        "openalex_url": clean_text(row.get("openalex_url")),
        "doi": clean_text(row.get("doi")),
        "author": clean_text(row.get("author")),
        "author_position": clean_text(row.get("author_position")),
        "institution": institution,
        "city": clean_text(row.get("city")),
        "region": clean_text(row.get("region")),
        "country": clean_text(row.get("country")),
        "country_code": clean_text(row.get("country_code")),
        "current_latitude": clean_text(row.get("latitude")),
        "current_longitude": clean_text(row.get("longitude")),
        "candidate_latitude": candidate_latitude,
        "candidate_longitude": candidate_longitude,
        "candidate_source": candidate_source,
        "candidate_source_detail": candidate_source_detail,
        "candidate_confidence": confidence,
        "coordinate_status": status,
        "apply_status": apply_status,
        "risk_flags": merge_flags(*risk_flags),
        "notes": clean_text(row.get("notes")),
    }


def merge_existing(
    proposed: Sequence[Dict[str, str]],
    existing: Sequence[Dict[str, str]],
) -> List[Dict[str, str]]:
    existing_by_key: Dict[Tuple[str, str, str, str], Dict[str, str]] = {}
    for row in existing:
        key = candidate_key(row)
        if key in existing_by_key:
            raise CandidateError(f"Existing candidate file has duplicate key: {key}")
        existing_by_key[key] = row

    merged = []
    seen = set()
    for row in proposed:
        key = candidate_key(row)
        output_row = dict(row)
        existing_row = existing_by_key.get(key)
        if existing_row is not None:
            existing_status = clean_text(existing_row.get("apply_status"))
            preserve_manual_values = existing_status in {"confirmed", "rejected"}
            for column in PRESERVE_COLUMNS:
                existing_value = clean_text(existing_row.get(column))
                if existing_value and (preserve_manual_values or column == "apply_status"):
                    output_row[column] = existing_value
        merged.append(output_row)
        seen.add(key)

    for key, row in existing_by_key.items():
        if key not in seen:
            merged.append({column: clean_text(row.get(column)) for column in OUTPUT_COLUMNS})
    return sorted(merged, key=sort_key)


def validate(rows: Sequence[Dict[str, str]]) -> None:
    keys = [candidate_key(row) for row in rows]
    if len(keys) != len(set(keys)):
        raise CandidateError("Duplicate candidate rows detected")
    for row in rows:
        has_lat = bool(clean_text(row.get("candidate_latitude")))
        has_lon = bool(clean_text(row.get("candidate_longitude")))
        if has_lat != has_lon:
            raise CandidateError(
                f"Partial candidate coordinate pair: {row['title']} / {row['institution']}"
            )
        if has_lat:
            if not clean_text(row.get("candidate_source")):
                raise CandidateError(
                    f"Candidate coordinate has no source: {row['title']} / {row['institution']}"
                )
            if valid_coordinate_pair(row, "candidate_") is None:
                raise CandidateError(
                    f"Invalid candidate coordinate pair: {row['title']} / {row['institution']}"
                )
        if clean_text(row.get("apply_status")) not in ALLOWED_APPLY_STATUSES:
            raise CandidateError(f"Invalid apply_status: {row.get('apply_status')}")
        if clean_text(row.get("candidate_confidence")) not in ALLOWED_CONFIDENCE:
            raise CandidateError(
                f"Invalid candidate_confidence: {row.get('candidate_confidence')}"
            )


def build_candidates(include_review_needed: bool) -> Tuple[List[Dict[str, str]], int]:
    diagnostics = read_csv(DIAGNOSTICS, DIAGNOSTIC_COLUMNS)
    local_index = build_local_coordinate_index()
    proposed = [
        candidate
        for row in diagnostics
        for candidate in [
            proposed_row_from_diagnostic(row, local_index, include_review_needed)
        ]
        if candidate is not None
    ]
    existing = read_csv(OUTPUT, OUTPUT_COLUMNS, optional=True)
    merged = merge_existing(proposed, existing)
    validate(merged)
    return merged, len(diagnostics)


def write_csv(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    except OSError as error:
        raise CandidateError(f"Could not write {path}: {error}") from error


def render_review(rows: Sequence[Dict[str, str]]) -> str:
    lines = [
        "# Key Paper Coordinate Candidates Review\n",
        "\n",
        "Generated from `data/manual/key_paper_coordinate_diagnostics.csv`.\n",
        "Coordinates are candidates only and must be manually reviewed before copying anywhere.\n",
        "\n",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row['title']}\n",
                "\n",
                f"- Author: {row['author']} ({row['author_position']})\n",
                f"- Institution: {row['institution']}\n",
                f"- Candidate: {row['candidate_latitude'] or '_none_'}, {row['candidate_longitude'] or '_none_'}\n",
                f"- Source: {row['candidate_source'] or '_none_'} {row['candidate_source_detail'] or ''}\n",
                f"- Apply status: {row['apply_status']}\n",
                f"- Risk flags: {row['risk_flags'] or '_none_'}\n",
                f"- Notes: {row['notes'] or '_none_'}\n",
                "\n",
            ]
        )
    return "".join(lines)


def write_text(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
    except OSError as error:
        raise CandidateError(f"Could not write {path}: {error}") from error


def print_summary(rows: Sequence[Dict[str, str]], diagnostic_rows: int) -> None:
    print("Key-paper coordinate candidate summary:")
    print(f"  Diagnostic rows loaded: {diagnostic_rows}")
    print(f"  Candidate rows generated: {len(rows)}")
    print(
        "  Rows with candidate coordinates: "
        f"{sum(bool(clean_text(row.get('candidate_latitude'))) for row in rows)}"
    )
    print(
        "  Rows without candidate coordinates: "
        f"{sum(not bool(clean_text(row.get('candidate_latitude'))) for row in rows)}"
    )
    print("  By apply_status:")
    for key, count in Counter(row["apply_status"] for row in rows).most_common():
        print(f"    {key}: {count}")
    print("  By candidate_source:")
    source_counts = Counter(row["candidate_source"] or "(none)" for row in rows)
    for key, count in source_counts.most_common():
        print(f"    {key}: {count}")
    print("  By risk_flags:")
    flag_counts: Counter[str] = Counter()
    for row in rows:
        flags = [clean_text(flag) for flag in row["risk_flags"].split(";") if clean_text(flag)]
        if flags:
            flag_counts.update(flags)
        else:
            flag_counts["(none)"] += 1
    for key, count in flag_counts.most_common():
        print(f"    {key}: {count}")
    print(
        "  SeDID appears: "
        f"{any(normalize_title(row['title']) == normalize_title(SEDID_TITLE) for row in rows)}"
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare local-only key-paper coordinate candidates."
    )
    parser.add_argument("--write", action="store_true", help=f"Write {OUTPUT}.")
    parser.add_argument(
        "--write-review",
        action="store_true",
        help=f"Write optional Markdown review file {REVIEW_MD}.",
    )
    parser.add_argument(
        "--include-review-needed",
        action="store_true",
        help="Include ambiguous/review-needed rows without candidate coordinates.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    before_hashes = {
        AFFILIATION_ENRICHMENT: file_hash(AFFILIATION_ENRICHMENT),
        CANDIDATE_MAP_JSON: file_hash(CANDIDATE_MAP_JSON),
        PUBLIC_PREVIEW_JSON: file_hash(PUBLIC_PREVIEW_JSON),
    }
    try:
        rows, diagnostic_rows = build_candidates(args.include_review_needed)
        if args.write:
            write_csv(OUTPUT, rows)
        if args.write_review:
            write_text(REVIEW_MD, render_review(rows))
        after_hashes = {
            path: file_hash(path) for path in before_hashes
        }
        changed = [
            str(path)
            for path, before_hash in before_hashes.items()
            if after_hashes[path] != before_hash
        ]
        if changed:
            raise CandidateError(
                "Protected files changed during candidate generation: "
                + ", ".join(changed)
            )
    except CandidateError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if not args.write:
        print(f"DRY RUN: no files were written. Would write: {OUTPUT}")
    print_summary(rows, diagnostic_rows)
    if args.write_review:
        print(f"  Review Markdown: {REVIEW_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
