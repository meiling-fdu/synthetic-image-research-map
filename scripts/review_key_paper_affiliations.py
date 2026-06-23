#!/usr/bin/env python3
"""Generate a local-only review worksheet for key-paper affiliation enrichment."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


ENRICHMENT = Path("data/manual/key_paper_affiliation_enrichment.csv")
WORK_NOTES = Path("data/manual/work_notes/missing_affiliation_manual_notes.csv")
REVIEW_MD = Path("data/manual/key_paper_affiliation_review.md")
REVIEW_CSV = Path("data/manual/key_paper_affiliation_review.csv")

SEDID_TITLE = "Exposing the Fake: Effective Diffusion-Generated Images Detection"

ENRICHMENT_COLUMNS = [
    "title",
    "year",
    "normalized_title",
    "openalex_url",
    "doi",
    "author",
    "author_position",
    "raw_affiliation",
    "institution",
    "city",
    "region",
    "country",
    "country_code",
    "latitude",
    "longitude",
    "institution_source",
    "confidence",
    "needs_manual_review",
    "notes",
]

REVIEW_CSV_COLUMNS = [
    "title",
    "year",
    "normalized_title",
    "doi",
    "openalex_url",
    "author_rows",
    "authors",
    "raw_affiliations_present",
    "institutions_present",
    "locations_present",
    "coordinate_status",
    "needs_manual_review_values",
    "work_notes_present",
    "notes",
]

WORK_NOTE_FIELDS = [
    "paper_url_or_pdf",
    "authors_found",
    "raw_affiliation_evidence",
    "canonical_institutions",
    "author_institution_mapping",
    "city_region_country",
    "coordinate_notes",
    "evidence_source",
    "manual_notes",
]

CANONICAL_INSTITUTION_ALLOWLIST = {
    "Huawei Noah's Ark Lab",
    "Institute of Computing Technology, Chinese Academy of Sciences",
    "Macao Polytechnic University",
    "Oak Ridge National Laboratory",
    "Renmin University of China",
    "Tencent YouTu Lab",
    "The Chinese University of Hong Kong",
    "University of Electronic Science and Technology of China",
    "University of Macau",
    "University of Science and Technology of China",
}

RAW_AFFILIATION_INSTITUTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bdepartment of\b",
        r"\bschool of\b",
        r"\bfaculty of\b",
        r"\bstate key laborator(?:y|ies)\b",
        r"\bmoe key lab\b",
        r"\bkey lab(?:orator(?:y|ies))?\b",
        r"\b(?:road|street|avenue|building|campus|room)\b",
        r"\bpostal\s+code\b",
        r"\b\d{5,}\b",
        r";",
    ]
]


class ReviewError(RuntimeError):
    """An expected local input, output, or validation error."""


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_title(value: Any) -> str:
    title = clean_text(value).casefold()
    title = title.replace("‐", "-").replace("–", "-").replace("—", "-")
    title = title.replace("real-world", "real world")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", title).split())


def normalize_institution_name(value: Any) -> str:
    return clean_text(value).casefold()


def institution_looks_like_raw_affiliation(value: Any) -> bool:
    institution = clean_text(value)
    if not institution:
        return False
    allowlisted = {
        normalize_institution_name(name) for name in CANONICAL_INSTITUTION_ALLOWLIST
    }
    if normalize_institution_name(institution) in allowlisted:
        return False
    return any(
        pattern.search(institution)
        for pattern in RAW_AFFILIATION_INSTITUTION_PATTERNS
    )


def read_csv(
    path: Path,
    required_columns: Iterable[str],
    optional: bool = False,
) -> List[Dict[str, str]]:
    if not path.exists():
        if optional:
            return []
        raise ReviewError(f"Required local input does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(set(required_columns) - set(reader.fieldnames or []))
            if missing:
                raise ReviewError(
                    f"{path} is missing required columns: {', '.join(missing)}"
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise ReviewError(f"Could not read {path}: {error}") from error


def group_enrichment_rows(
    rows: Sequence[Dict[str, str]],
) -> Dict[str, List[Dict[str, str]]]:
    groups: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean_text(row.get("normalized_title")) or normalize_title(row.get("title"))
        groups[key].append(row)
    for grouped_rows in groups.values():
        grouped_rows.sort(key=lambda row: position_sort_key(row.get("author_position")))
    return dict(sorted(groups.items(), key=lambda item: paper_sort_key(item[1])))


def group_work_notes(rows: Sequence[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    groups: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = normalize_title(row.get("title"))
        if key:
            groups[key].append(row)
    return groups


def position_sort_key(value: Any) -> Tuple[int, str]:
    text = clean_text(value)
    try:
        return int(text), text
    except ValueError:
        return 999999, text


def paper_sort_key(rows: Sequence[Dict[str, str]]) -> Tuple[str, str]:
    first = rows[0] if rows else {}
    return clean_text(first.get("year")), clean_text(first.get("title")).casefold()


def unique_nonempty(rows: Sequence[Dict[str, str]], field: str) -> List[str]:
    values: List[str] = []
    seen = set()
    for row in rows:
        value = clean_text(row.get(field))
        if value and value not in seen:
            values.append(value)
            seen.add(value)
    return values


def coordinate_status(rows: Sequence[Dict[str, str]]) -> str:
    rows_with_coordinates = sum(
        bool(clean_text(row.get("latitude")) or clean_text(row.get("longitude")))
        for row in rows
    )
    if rows_with_coordinates == 0:
        return "none"
    if rows_with_coordinates == len(rows):
        return "all_rows_have_coordinates"
    return f"partial ({rows_with_coordinates}/{len(rows)} rows)"


def has_any_work_note_content(row: Dict[str, str]) -> bool:
    return any(clean_text(row.get(field)) for field in WORK_NOTE_FIELDS)


def markdown_escape(value: Any) -> str:
    text = clean_text(value)
    if not text:
        return ""
    return text.replace("|", "\\|")


def bullet_value(label: str, value: Any) -> str:
    text = clean_text(value) or "_empty_"
    return f"- **{label}:** {text}\n"


def row_location(row: Dict[str, str]) -> str:
    parts = [
        clean_text(row.get("city")),
        clean_text(row.get("region")),
        clean_text(row.get("country")),
        clean_text(row.get("country_code")),
    ]
    return ", ".join(part for part in parts if part)


def render_review_markdown(
    groups: Dict[str, List[Dict[str, str]]],
    work_note_groups: Dict[str, List[Dict[str, str]]],
) -> str:
    lines: List[str] = [
        "# Key Paper Affiliation Review\n",
        "\n",
        "This local worksheet is generated from `data/manual/key_paper_affiliation_enrichment.csv`.\n",
        "It is a manual review aid only: work notes are not treated as validated structured data, and no affiliations, institutions, locations, or coordinates are inferred here.\n",
        "\n",
        f"- Papers grouped: {len(groups)}\n",
        f"- Author rows: {sum(len(rows) for rows in groups.values())}\n",
        f"- SeDID included: {normalize_title(SEDID_TITLE) in groups}\n",
        "\n",
    ]

    for index, (normalized_title, rows) in enumerate(groups.items(), start=1):
        first = rows[0]
        notes = work_note_groups.get(normalized_title, [])
        lines.extend(
            [
                f"## {index}. {clean_text(first.get('title'))}\n",
                "\n",
                bullet_value("Year", first.get("year")),
                bullet_value("DOI", first.get("doi")),
                bullet_value("OpenAlex URL", first.get("openalex_url")),
                bullet_value("Author rows", str(len(rows))),
                bullet_value("Coordinate status", coordinate_status(rows)),
                "\n",
                "### Current Author Rows\n",
                "\n",
                "| Position | Author | Raw Affiliation | Institution | Location | Coordinates | Confidence | Needs Manual Review |\n",
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n",
            ]
        )
        for row in rows:
            coords = ", ".join(
                part
                for part in [
                    clean_text(row.get("latitude")),
                    clean_text(row.get("longitude")),
                ]
                if part
            )
            lines.append(
                "| "
                + " | ".join(
                    [
                        markdown_escape(row.get("author_position")) or "_empty_",
                        markdown_escape(row.get("author")) or "_empty_",
                        markdown_escape(row.get("raw_affiliation")) or "_empty_",
                        markdown_escape(row.get("institution")) or "_empty_",
                        markdown_escape(row_location(row)) or "_empty_",
                        markdown_escape(coords) or "_empty_",
                        markdown_escape(row.get("confidence")) or "_empty_",
                        markdown_escape(row.get("needs_manual_review")) or "_empty_",
                    ]
                )
                + " |\n"
            )

        paper_notes = unique_nonempty(rows, "notes")
        lines.extend(["\n", "### Current Notes\n", "\n"])
        if paper_notes:
            for note in paper_notes:
                lines.append(f"- {note}\n")
        else:
            lines.append("- _none_\n")

        lines.extend(["\n", "### Work Notes (Unvalidated)\n", "\n"])
        if notes:
            any_content = False
            for note_index, note in enumerate(notes, start=1):
                populated = [
                    (field, clean_text(note.get(field)))
                    for field in WORK_NOTE_FIELDS
                    if clean_text(note.get(field))
                ]
                if not populated:
                    continue
                any_content = True
                lines.append(f"Work note row {note_index}:\n")
                for field, value in populated:
                    lines.append(f"- **{field}:** {value}\n")
            if not any_content:
                lines.append("- Work-note row exists, but evidence fields are empty.\n")
        else:
            lines.append("- _No work-note row found._\n")

        lines.extend(
            [
                "\n",
                "### Manual Review Checklist\n",
                "\n",
                "- [ ] Find official paper/PDF/publisher page.\n",
                "- [ ] Verify author list.\n",
                "- [ ] Copy raw affiliation evidence.\n",
                "- [ ] Map authors to canonical institutions.\n",
                "- [ ] Fill city/region/country separately.\n",
                "- [ ] Fill coordinates only from trusted source.\n",
                "- [ ] Set confidence.\n",
                "- [ ] Keep `needs_manual_review=yes` unless fully verified.\n",
                "\n",
            ]
        )
    return "".join(lines)


def validation_summary(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    groups = group_enrichment_rows(rows)
    missing_title_or_normalized = [
        row
        for row in rows
        if not clean_text(row.get("title")) or not clean_text(row.get("normalized_title"))
    ]
    institution_pattern_rows = [
        row
        for row in rows
        if institution_looks_like_raw_affiliation(row.get("institution"))
    ]
    coordinates_without_location = [
        row
        for row in rows
        if (clean_text(row.get("latitude")) or clean_text(row.get("longitude")))
        and (not clean_text(row.get("city")) or not clean_text(row.get("country")))
    ]
    needs_review_empty = [
        row for row in rows if not clean_text(row.get("needs_manual_review"))
    ]
    return {
        "papers": len(groups),
        "rows": len(rows),
        "rows_with_institution": sum(
            bool(clean_text(row.get("institution"))) for row in rows
        ),
        "rows_with_raw_affiliation": sum(
            bool(clean_text(row.get("raw_affiliation"))) for row in rows
        ),
        "rows_with_coordinates": sum(
            bool(clean_text(row.get("latitude")) or clean_text(row.get("longitude")))
            for row in rows
        ),
        "rows_missing_title_or_normalized_title": len(missing_title_or_normalized),
        "rows_with_institution_department_address_or_location_patterns": len(
            institution_pattern_rows
        ),
        "rows_with_coordinates_but_missing_city_or_country": len(
            coordinates_without_location
        ),
        "rows_with_empty_needs_manual_review": len(needs_review_empty),
        "needs_manual_review_values": Counter(
            clean_text(row.get("needs_manual_review")) or "_empty_" for row in rows
        ),
    }


def write_text(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
    except OSError as error:
        raise ReviewError(f"Could not write {path}: {error}") from error


def write_grouped_csv(
    path: Path,
    groups: Dict[str, List[Dict[str, str]]],
    work_note_groups: Dict[str, List[Dict[str, str]]],
) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=REVIEW_CSV_COLUMNS,
                lineterminator="\n",
            )
            writer.writeheader()
            for normalized_title, rows in groups.items():
                first = rows[0]
                author_entries = [
                    f"{clean_text(row.get('author_position'))}: {clean_text(row.get('author'))}"
                    for row in rows
                ]
                locations = [
                    location for location in (row_location(row) for row in rows) if location
                ]
                writer.writerow(
                    {
                        "title": clean_text(first.get("title")),
                        "year": clean_text(first.get("year")),
                        "normalized_title": normalized_title,
                        "doi": clean_text(first.get("doi")),
                        "openalex_url": clean_text(first.get("openalex_url")),
                        "author_rows": str(len(rows)),
                        "authors": "; ".join(author_entries),
                        "raw_affiliations_present": "; ".join(
                            unique_nonempty(rows, "raw_affiliation")
                        ),
                        "institutions_present": "; ".join(
                            unique_nonempty(rows, "institution")
                        ),
                        "locations_present": "; ".join(dict.fromkeys(locations)),
                        "coordinate_status": coordinate_status(rows),
                        "needs_manual_review_values": "; ".join(
                            f"{value}:{count}"
                            for value, count in sorted(
                                Counter(
                                    clean_text(row.get("needs_manual_review"))
                                    or "_empty_"
                                    for row in rows
                                ).items()
                            )
                        ),
                        "work_notes_present": "yes"
                        if any(
                            has_any_work_note_content(note)
                            for note in work_note_groups.get(normalized_title, [])
                        )
                        else "empty_or_missing",
                        "notes": " | ".join(unique_nonempty(rows, "notes")),
                    }
                )
        temporary.replace(path)
    except OSError as error:
        raise ReviewError(f"Could not write {path}: {error}") from error


def print_summary(summary: Dict[str, Any]) -> None:
    print("Key-paper affiliation review validation summary:")
    print(f"  Papers: {summary['papers']}")
    print(f"  Rows: {summary['rows']}")
    print(f"  Rows with non-empty institution: {summary['rows_with_institution']}")
    print(
        "  Rows with non-empty raw_affiliation: "
        f"{summary['rows_with_raw_affiliation']}"
    )
    print(f"  Rows with coordinates: {summary['rows_with_coordinates']}")
    print(
        "  Rows missing title or normalized_title: "
        f"{summary['rows_missing_title_or_normalized_title']}"
    )
    print(
        "  Rows where institution has department/address/city/country patterns: "
        f"{summary['rows_with_institution_department_address_or_location_patterns']}"
    )
    print(
        "  Rows where coordinates exist but city/country is empty: "
        f"{summary['rows_with_coordinates_but_missing_city_or_country']}"
    )
    print(
        "  Rows where needs_manual_review is empty: "
        f"{summary['rows_with_empty_needs_manual_review']}"
    )
    values = ", ".join(
        f"{value}={count}"
        for value, count in sorted(summary["needs_manual_review_values"].items())
    )
    print(f"  needs_manual_review values: {values}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate key-paper affiliation enrichment rows and generate a "
            "local manual review worksheet."
        )
    )
    parser.add_argument(
        "--write-review",
        action="store_true",
        help=f"Write the grouped Markdown review worksheet to {REVIEW_MD}.",
    )
    parser.add_argument(
        "--write-csv",
        action="store_true",
        help=f"Write an optional grouped CSV review worksheet to {REVIEW_CSV}.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        rows = read_csv(ENRICHMENT, ENRICHMENT_COLUMNS)
        work_notes = read_csv(WORK_NOTES, {"title", "year"}, optional=True)
        groups = group_enrichment_rows(rows)
        work_note_groups = group_work_notes(work_notes)
        summary = validation_summary(rows)
        if args.write_review:
            write_text(REVIEW_MD, render_review_markdown(groups, work_note_groups))
        if args.write_csv:
            write_grouped_csv(REVIEW_CSV, groups, work_note_groups)
    except ReviewError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print_summary(summary)
    print(f"  SeDID included: {normalize_title(SEDID_TITLE) in groups}")
    print(f"  Work-note rows loaded: {len(work_notes)}")
    if args.write_review:
        print(f"  Review Markdown: {REVIEW_MD}")
    if args.write_csv:
        print(f"  Review CSV: {REVIEW_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
