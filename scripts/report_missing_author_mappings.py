#!/usr/bin/env python3
"""Audit author–institution index coverage in the public paper preview."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

try:
    from .name_matching import canonical_name_key, names_match
except ImportError:
    from name_matching import canonical_name_key, names_match


DEFAULT_PAPERS = Path("web/data/public_preview_papers.json")
DEFAULT_MAP_DATA = Path("web/data/public_preview_map_data.json")
DEFAULT_MAPPINGS = Path("data/curated/author_institution_mappings.csv")
DEFAULT_CURATED_PAPERS = Path("data/curated/papers.csv")
DEFAULT_KEY_PAPERS = Path("data/manual/key_papers.csv")
DEFAULT_CSV_OUTPUT = Path("data/manual/missing_author_mappings_report.csv")
DEFAULT_MARKDOWN_OUTPUT = Path("docs/missing_author_mappings_report.md")

CSV_COLUMNS = (
    "priority_rank",
    "mapping_status",
    "paper_id",
    "title",
    "year",
    "venue",
    "is_key_paper",
    "is_curated_paper",
    "total_authors",
    "mapped_authors",
    "missing_authors",
    "missing_author_names",
    "marker_count",
    "doi",
    "arxiv_id",
    "openalex_id",
    "url",
)


class ReportError(RuntimeError):
    """An expected report input or output error."""


def clean(value: Any) -> str:
    return " ".join(str(value if value is not None else "").split())


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return clean(value).casefold() in {"1", "true", "yes", "y"}


def normalize_doi(value: Any) -> str:
    return re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        clean(value),
        flags=re.IGNORECASE,
    ).casefold()


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalize_author(value: Any) -> str:
    return canonical_name_key(value)


def author_name(value: Any) -> str:
    if isinstance(value, Mapping):
        return clean(value.get("name") or value.get("author"))
    return clean(value)


def year_text(record: Mapping[str, Any]) -> str:
    return clean(record.get("publication_year") or record.get("year"))


def openalex_id(record: Mapping[str, Any]) -> str:
    value = clean(record.get("openalex_id") or record.get("openalex_url"))
    match = re.search(r"(W\d+)(?:/)?$", value, flags=re.IGNORECASE)
    return match.group(1).upper() if match else value


def identity_keys(record: Mapping[str, Any]) -> Tuple[Set[str], str]:
    strong: Set[str] = set()
    paper_id = clean(record.get("paper_id") or record.get("related_paper_id"))
    if paper_id:
        strong.add(f"paper_id:{paper_id.casefold()}")
    doi = normalize_doi(record.get("doi"))
    if doi:
        strong.add(f"doi:{doi}")
    oa_id = openalex_id(record)
    if oa_id:
        strong.add(f"openalex:{oa_id.casefold().rstrip('/')}")
    arxiv_id = clean(record.get("arxiv_id")).casefold().removeprefix("arxiv:")
    if arxiv_id:
        strong.add(f"arxiv:{arxiv_id}")
    title = normalize_title(record.get("title"))
    year = year_text(record)
    title_year = f"title_year:{title}|{year}" if title and year else ""
    return strong, title_year


def records_match(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_strong, left_title = identity_keys(left)
    right_strong, right_title = identity_keys(right)
    if left_strong & right_strong:
        return True
    if left_strong and right_strong:
        return False
    return bool(left_title and left_title == right_title)


def identity_value(record: Mapping[str, Any], kind: str) -> str:
    if kind == "paper_id":
        return clean(record.get("paper_id") or record.get("related_paper_id")).casefold()
    if kind == "openalex":
        return openalex_id(record).casefold().rstrip("/")
    if kind == "doi":
        return normalize_doi(record.get("doi"))
    if kind == "arxiv":
        return clean(record.get("arxiv_id")).casefold().removeprefix("arxiv:")
    _strong, title_year = identity_keys(record)
    return title_year


def marker_counts(
    papers: Sequence[Mapping[str, Any]],
    markers: Sequence[Mapping[str, Any]],
) -> Dict[int, int]:
    counts = {id(paper): 0 for paper in papers}
    for marker in markers:
        matches: List[Mapping[str, Any]] = []
        for kind in ("paper_id", "openalex", "doi", "arxiv", "title_year"):
            marker_value = identity_value(marker, kind)
            if not marker_value:
                continue
            matches = [
                paper
                for paper in papers
                if identity_value(paper, kind) == marker_value
            ]
            if matches:
                break
        if matches:
            counts[id(matches[0])] += 1
    return counts


def read_json_records(path: Path) -> List[Dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ReportError(f"Could not read {path}: {error}") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ReportError(f"Invalid JSON in {path}: {error}") from error
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list) or not all(
        isinstance(record, dict) for record in records
    ):
        raise ReportError(f"{path} must contain a list of record objects")
    return records


def read_csv_rows(path: Path, *, optional: bool = False) -> List[Dict[str, str]]:
    if optional and not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError as error:
        raise ReportError(f"Could not read {path}: {error}") from error
    except (UnicodeError, csv.Error) as error:
        raise ReportError(f"Invalid CSV in {path}: {error}") from error


def matching_rows(
    record: Mapping[str, Any], candidates: Iterable[Mapping[str, Any]]
) -> List[Mapping[str, Any]]:
    return [candidate for candidate in candidates if records_match(record, candidate)]


def split_author_text(value: Any) -> List[str]:
    text = clean(value)
    if not text:
        return []
    separator = ";" if ";" in text else ","
    return [clean(part) for part in text.split(separator) if clean(part)]


def report_authors(record: Mapping[str, Any]) -> List[Any]:
    raw_authors = record.get("authors")
    if isinstance(raw_authors, list) and raw_authors:
        authors: List[Any] = list(raw_authors)
        affiliation_authors = {
            normalize_author(author)
            for affiliation in record.get("author_institution_affiliations") or []
            if isinstance(affiliation, Mapping)
            for author in affiliation.get("authors") or []
            if normalize_author(author)
        }
        if (
            len(authors) == 1
            and len(affiliation_authors) > 1
            and "," in author_name(authors[0])
        ):
            return split_author_text(author_name(authors[0]))
        return authors
    if isinstance(raw_authors, str):
        return split_author_text(raw_authors)
    return split_author_text(record.get("authors_text"))


def author_coverage(record: Mapping[str, Any]) -> Tuple[int, int, List[str]]:
    authors = report_authors(record)
    mapped_names = {
        normalize_author(mapping)
        for mapping in record.get("author_institution_indices") or []
        if isinstance(mapping, Mapping)
        and (
            mapping.get("institution_indices")
            or mapping.get("affiliation_indices")
            or mapping.get("institution_ids")
        )
    }
    missing: List[str] = []
    mapped = 0
    for author in authors:
        name = author_name(author)
        has_direct_indexes = bool(
            isinstance(author, Mapping)
            and (
                author.get("affiliation_indices")
                or author.get("institution_indices")
            )
        )
        if has_direct_indexes or any(
            names_match(author, mapped_name) for mapped_name in mapped_names
        ):
            mapped += 1
        else:
            missing.append(name or "<unnamed author>")
    return len(authors), mapped, missing


def fallback_paper_id(record: Mapping[str, Any]) -> str:
    oa_id = openalex_id(record)
    if oa_id:
        return f"openalex:{oa_id}"
    doi = normalize_doi(record.get("doi"))
    if doi:
        return f"doi:{doi}"
    arxiv_id = clean(record.get("arxiv_id"))
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    seed = f"{normalize_title(record.get('title'))}|{year_text(record)}"
    return f"title-year:{hashlib.sha1(seed.encode('utf-8')).hexdigest()[:16]}"


def record_url(record: Mapping[str, Any]) -> str:
    for field in (
        "url",
        "paper_url",
        "primary_url",
        "landing_page_url",
        "openalex_url",
        "arxiv_url",
    ):
        value = clean(record.get(field))
        if value:
            return value
    doi = clean(record.get("doi"))
    return f"https://doi.org/{normalize_doi(doi)}" if doi else ""


def priority_key(row: Mapping[str, Any]) -> Tuple[Any, ...]:
    status_order = {"zero": 0, "partial": 1, "complete": 2}
    try:
        year = int(clean(row.get("year")))
    except ValueError:
        year = -1
    return (
        status_order[clean(row.get("mapping_status"))],
        -int(row.get("missing_authors") or 0),
        -int(bool(row.get("is_key_paper"))),
        -year,
        clean(row.get("title")).casefold(),
        clean(row.get("paper_id")).casefold(),
    )


def build_report_rows(
    papers: Sequence[Mapping[str, Any]],
    markers: Sequence[Mapping[str, Any]],
    curated_papers: Sequence[Mapping[str, Any]],
    curated_mappings: Sequence[Mapping[str, Any]],
    key_papers: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    paper_marker_counts = marker_counts(papers, markers)
    for paper in papers:
        total, mapped, missing_names = author_coverage(paper)
        missing = len(missing_names)
        if mapped == 0:
            status = "zero"
        elif missing:
            status = "partial"
        else:
            status = "complete"

        curated_matches = matching_rows(paper, curated_papers)
        mapping_matches = matching_rows(paper, curated_mappings)
        matched_ids = sorted(
            {
                clean(match.get("paper_id"))
                for match in (*curated_matches, *mapping_matches)
                if clean(match.get("paper_id"))
            },
            key=str.casefold,
        )
        explicit_id = clean(paper.get("paper_id"))
        paper_id = explicit_id or (matched_ids[0] if matched_ids else fallback_paper_id(paper))
        marker_count = paper_marker_counts[id(paper)]
        is_curated = bool(
            curated_matches
            or clean(paper.get("source_database")).casefold() == "curated"
            or clean(paper.get("curation_status"))
        )
        is_key = bool(
            parse_bool(paper.get("is_key_paper"))
            or parse_bool(paper.get("key_paper"))
            or matching_rows(paper, key_papers)
        )
        rows.append(
            {
                "mapping_status": status,
                "paper_id": paper_id,
                "title": clean(paper.get("title")),
                "year": year_text(paper),
                "venue": clean(paper.get("venue") or paper.get("venue_name")),
                "is_key_paper": is_key,
                "is_curated_paper": is_curated,
                "total_authors": total,
                "mapped_authors": mapped,
                "missing_authors": missing,
                "missing_author_names": "; ".join(missing_names),
                "marker_count": marker_count,
                "doi": clean(paper.get("doi")),
                "arxiv_id": clean(paper.get("arxiv_id")),
                "openalex_id": openalex_id(paper),
                "url": record_url(paper),
            }
        )
    rows.sort(key=priority_key)
    for rank, row in enumerate(rows, start=1):
        row["priority_rank"] = rank
    return rows


def csv_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def write_csv_report(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=CSV_COLUMNS,
                lineterminator="\n",
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        column: csv_value(row.get(column, ""))
                        for column in CSV_COLUMNS
                    }
                )
        temporary.replace(path)
    except OSError as error:
        raise ReportError(f"Could not write {path}: {error}") from error


def markdown_text(value: Any) -> str:
    return clean(value).replace("|", "\\|")


def markdown_table(rows: Sequence[Mapping[str, Any]]) -> List[str]:
    lines = [
        "| Rank | Paper | Year | Coverage | Missing authors | Markers | Key | Curated |",
        "| ---: | --- | ---: | ---: | --- | ---: | :---: | :---: |",
    ]
    if not rows:
        lines.append("| — | None | — | — | — | — | — | — |")
        return lines
    for row in rows:
        coverage = f"{row['mapped_authors']}/{row['total_authors']}"
        lines.append(
            "| {priority_rank} | {title} | {year} | {coverage} | {missing} | "
            "{marker_count} | {key} | {curated} |".format(
                priority_rank=row["priority_rank"],
                title=markdown_text(row["title"]),
                year=markdown_text(row["year"]) or "—",
                coverage=coverage,
                missing=markdown_text(row["missing_author_names"]) or "—",
                marker_count=row["marker_count"],
                key="Yes" if row["is_key_paper"] else "",
                curated="Yes" if row["is_curated_paper"] else "",
            )
        )
    return lines


def write_markdown_report(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    complete = [row for row in rows if row["mapping_status"] == "complete"]
    partial = [row for row in rows if row["mapping_status"] == "partial"]
    zero = [row for row in rows if row["mapping_status"] == "zero"]
    problematic = [*zero, *partial]
    lines = [
        "# Missing Author–Institution Mappings Report",
        "",
        "This audit reports author affiliation-index coverage in the current public "
        "paper preview. It does not modify or infer mappings.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Total public papers | {len(rows)} |",
        f"| Complete mappings | {len(complete)} |",
        f"| Partial mappings | {len(partial)} |",
        f"| Zero mappings | {len(zero)} |",
        f"| Total missing author links | {sum(int(row['missing_authors']) for row in rows)} |",
        "",
        "## Highest Priority",
        "",
        *markdown_table(problematic[:30]),
        "",
        "## Zero-Mapping Papers",
        "",
        *markdown_table(zero),
        "",
        "## Partial-Mapping Papers",
        "",
        *markdown_table(partial),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text("\n".join(lines), encoding="utf-8")
        temporary.replace(path)
    except OSError as error:
        raise ReportError(f"Could not write {path}: {error}") from error


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report incomplete author–institution mappings in the public preview."
    )
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--map-data", type=Path, default=DEFAULT_MAP_DATA)
    parser.add_argument("--mappings", type=Path, default=DEFAULT_MAPPINGS)
    parser.add_argument("--curated-papers", type=Path, default=DEFAULT_CURATED_PAPERS)
    parser.add_argument("--key-papers", type=Path, default=DEFAULT_KEY_PAPERS)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        rows = build_report_rows(
            read_json_records(args.papers),
            read_json_records(args.map_data),
            read_csv_rows(args.curated_papers),
            read_csv_rows(args.mappings),
            read_csv_rows(args.key_papers, optional=True),
        )
        write_csv_report(args.csv_output, rows)
        write_markdown_report(args.markdown_output, rows)
    except ReportError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    counts = {
        status: sum(row["mapping_status"] == status for row in rows)
        for status in ("complete", "partial", "zero")
    }
    print(
        f"Wrote {args.csv_output} and {args.markdown_output}: "
        f"{len(rows)} papers, {counts['complete']} complete, "
        f"{counts['partial']} partial, {counts['zero']} zero."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
