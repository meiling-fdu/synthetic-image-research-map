#!/usr/bin/env python3
"""Import a manual key-paper coverage checklist from local Word documents.

The importer reads DOCX files directly as ZIP/XML containers. It updates only the
manual coverage checklist; imported rows do not enter the candidate pipeline or
public map automatically.
"""

from __future__ import annotations

import argparse
import csv
import re
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "data" / "manual" / "source_docs"
DEFAULT_OUTPUT = ROOT / "data" / "manual" / "key_papers.csv"

FIELDS = [
    "title",
    "year",
    "authors",
    "doi",
    "arxiv_id",
    "openalex_url",
    "paper_url",
    "expected_task",
    "source_doc",
    "section",
    "notes",
]

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
W = f"{{{W_NS}}}"
R = f"{{{R_NS}}}"

YEAR_HEADING_RE = re.compile(r"(?:19|20)\d{2}")
YEAR_IN_TEXT_RE = re.compile(r"(?<!\d)((?:19|20)\d{2})(?:\d{4})?(?!\d)")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s<>\"]+", re.IGNORECASE)
ARXIV_RE = re.compile(
    r"(?:arxiv\.org/abs/|arxiv\s*:\s*)(\d{4}\.\d{4,5}(?:v\d+)?)",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)

DETECTION_RE = re.compile(r"\b(?:detect(?:ion|ing|or|ors|ed)?|forensic(?:s)?)\b", re.IGNORECASE)
ATTRIBUTION_RE = re.compile(
    r"\b(?:attribut(?:ion|ing|e|ed)|source identification|source verification|"
    r"origin attribution|provenance)\b",
    re.IGNORECASE,
)

# These markers occur at the start of trailing venue/year annotations in the
# source documents. Keep the list conservative: generic paper-topic words such
# as detection, attribution, synthetic, image, generated, source, and model must
# never become split points.
VENUE_START_PATTERNS = (
    r"AAAI",
    r"ACM\s+MM",
    r"BMVC",
    r"CCS",
    r"CVPR(?:\s+Workshops?)?",
    r"ECCV(?:\s+Workshops?)?",
    r"ICCV(?:\s+Workshops?)?",
    r"ICLR",
    r"ICML",
    r"ICPR",
    r"ICASSP",
    r"ICIP",
    r"IJCNN",
    r"IJCAI",
    r"MAD\s+Workshop",
    r"MIPR",
    r"NeurIPS",
    r"NDSS",
    r"WACV(?:\s+Workshops?)?",
    r"WIFS",
    r"TIFS",
    r"TIP",
    r"TMM",
    r"TCSVT",
    r"TCDS",
    r"TPAMI",
    r"TOMM",
    r"PRL",
    r"SPL",
    r"KBS",
    r"IEEE(?:\s+(?:Access|TPAMI|TIFS|TMM|TCSVT|TCDS|TIP|SPL))?",
    r"Electronics",
    r"arXiv",
    r"Workshop(?:s)?",
    r"Multimedia\s+Systems",
    r"Neurocomputing",
    r"Research\s+Square",
    r"Science\s+China",
    r"Sensors",
    r"Electronic\s+Imaging",
    r"Computer\s+Vision\s+Winter\s+Workshop",
    r"Forensic\s+Science\s+International",
    r"QPAIN",
)
VENUE_START_RE = re.compile(
    rf"^(?:{'|'.join(VENUE_START_PATTERNS)})(?:\b|$)", re.IGNORECASE
)
VENUE_ONLY_RE = re.compile(
    rf"^(?:{'|'.join(VENUE_START_PATTERNS)})(?:[\s,./&:-].*)?$",
    re.IGNORECASE,
)
TRAILING_VENUE_RE = re.compile(
    rf"\s+(?:{'|'.join(VENUE_START_PATTERNS)})(?:\b|$)[^.!?]*?(?:\b(?:19|20)\d{{2}}(?:\d{{4}})?\b)?[.,]?$",
    re.IGNORECASE,
)
TRAILING_YEAR_SUFFIX_RE = re.compile(
    r"(?P<year>(?:19|20)\d{2})(?:\d{4})?\s*\.?$"
)

# Regression examples for the conservative suffix parser. These titles used to
# be truncated because generic title words before a workshop token were treated
# as part of the venue suffix.
TITLE_PARSE_REGRESSIONS = (
    (
        "Are CLIP features all you need for Universal Synthetic Image Origin Attribution? ECCV Workshop, 2024",
        "Are CLIP features all you need for Universal Synthetic Image Origin Attribution?",
        "ECCV Workshop, 2024",
    ),
    (
        "Improving Synthetically Generated Image Detection in Cross-Concept Settings MAD Workshop, 2023",
        "Improving Synthetically Generated Image Detection in Cross-Concept Settings",
        "MAD Workshop, 2023",
    ),
    (
        "Reverse engineering of generative models: Inferring model hyperparameters from generated images.IEEE TPAMI 2023",
        "Reverse engineering of generative models: Inferring model hyperparameters from generated images",
        "IEEE TPAMI 2023",
    ),
)

SECTION_ALIASES = {
    "identification": "Identification",
    "verification": "Verification",
    "数据集": "Dataset",
    "dataset": "Dataset",
    "benchmark": "Benchmark",
    "survey": "Survey",
    "review": "Survey",
    "反取证": "Anti-forensics",
    "anti-forensics": "Anti-forensics",
    "anti-forensic": "Anti-forensics",
    "evasion": "Anti-forensics",
    "文献汇总": "Literature summary",
    "待补充": "To supplement",
    "《待补充》": "To supplement",
}

SECTION_PARSE_REGRESSIONS = (
    ("Dataset", "Dataset"),
    ("Benchmark", "Benchmark"),
    ("Identification", "Identification"),
    ("Verification", "Verification"),
    ("数据集", "Dataset"),
    ("反取证", "Anti-forensics"),
    ("文献汇总", "Literature summary"),
    ("待补充", "To supplement"),
    ("Dataset:", ""),
    ("Dataset: GenImage / OSMA", ""),
    ("数据集：", ""),
    ("数据集：GenImage / OSMA", ""),
    ("代码：", ""),
    ("Code: https://example.org", ""),
    ("核心思想：", ""),
)

NON_AUTHOR_PREFIXES = (
    "核心思想",
    "数据集",
    "代码",
    "dataset",
    "code",
    "文献汇总",
    "arxiv",
)


@dataclass(frozen=True)
class ParsedTitle:
    title: str
    year: str = ""
    source_suffix: str = ""
    venue_hint: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import key-paper checklist rows from local DOCX source files."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--preserve-existing",
        action="store_true",
        help="Merge existing output rows instead of regenerating solely from source documents.",
    )
    return parser.parse_args()


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(W + "t")).strip()


def relationship_targets(archive: ZipFile) -> dict[str, str]:
    rel_path = "word/_rels/document.xml.rels"
    if rel_path not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read(rel_path))
    return {
        rel.get("Id", ""): rel.get("Target", "")
        for rel in root.findall(f"{{{PKG_REL_NS}}}Relationship")
        if rel.get("TargetMode") == "External"
    }


def read_docx_paragraphs(path: Path) -> list[dict[str, object]]:
    try:
        with ZipFile(path) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
            targets = relationship_targets(archive)
    except (BadZipFile, KeyError, ET.ParseError) as exc:
        raise ValueError(f"Could not read DOCX structure: {exc}") from exc

    paragraphs: list[dict[str, object]] = []
    for paragraph in document.iter(W + "p"):
        text = paragraph_text(paragraph)
        if not text:
            continue
        style_node = paragraph.find(f"./{W}pPr/{W}pStyle")
        style = style_node.get(W + "val", "") if style_node is not None else ""
        numbered = paragraph.find(f"./{W}pPr/{W}numPr") is not None
        links = []
        for hyperlink in paragraph.iter(W + "hyperlink"):
            target = targets.get(hyperlink.get(R + "id", ""), "")
            if target:
                links.append(target)
        paragraphs.append(
            {"text": text, "style": style, "numbered": numbered, "links": links}
        )
    return paragraphs


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in value).split())


def normalize_title_line(raw_title: str) -> str:
    title = re.sub(r"^[\s·•▪◦*-]+", "", raw_title).strip()
    return re.sub(r"\s+", " ", title)


def is_venue_like(value: str) -> bool:
    venue = value.strip(" ,.;")
    if not venue:
        return False
    return bool(VENUE_START_RE.match(venue) and VENUE_ONLY_RE.fullmatch(venue))


def trim_sentence_period(title: str, separator: str) -> str:
    title = title.rstrip()
    if separator == ".":
        return title.rstrip(" .,")
    return title.rstrip(" ,")


def split_title_and_venue(prefix: str) -> Optional[tuple[str, str]]:
    prefix = prefix.strip(" ,.;")
    if not prefix:
        return None

    for match in reversed(list(re.finditer(r"[.?!]\s*", prefix))):
        separator = match.group(0).strip() or prefix[match.start()]
        venue = prefix[match.end() :].strip(" ,.;")
        if is_venue_like(venue):
            title = trim_sentence_period(prefix[: match.end()].rstrip(), separator[0])
            return title, venue

    tokens = prefix.split()
    max_venue_tokens = min(6, len(tokens) - 1)
    for token_count in range(max_venue_tokens, 0, -1):
        venue = " ".join(tokens[-token_count:])
        title = " ".join(tokens[:-token_count])
        if title and is_venue_like(venue):
            return title.rstrip(" .,"), venue.strip(" ,.")
    return None


def parse_title_line(raw_title: str) -> ParsedTitle:
    line = normalize_title_line(raw_title)
    if not line:
        return ParsedTitle("")

    working = line.rstrip(" ,.")
    alias_match = re.search(r"\s+(?P<alias>\([A-Za-z0-9][^)]{0,30}\))$", working)
    if alias_match:
        alias = alias_match.group("alias")
        before_alias = working[: alias_match.start()].rstrip(" .,")
        parsed = parse_title_line(before_alias)
        if parsed.source_suffix:
            return ParsedTitle(
                title=parsed.title,
                year=parsed.year,
                source_suffix=(
                    f"{parsed.source_suffix}; source_alias={alias}"
                ),
                venue_hint=parsed.venue_hint,
            )

    year_match = TRAILING_YEAR_SUFFIX_RE.search(working)
    if year_match:
        year = year_match.group("year")
        prefix = working[: year_match.start()].rstrip(" ,")
        split = split_title_and_venue(prefix)
        if split:
            title, venue = split
            source_suffix = working[len(title):].lstrip(" .,")
            return ParsedTitle(
                title=title,
                year=year,
                source_suffix=source_suffix,
                venue_hint=venue,
            )

    if ". " in working:
        title, venue = working.rsplit(". ", 1)
        if is_venue_like(venue):
            return ParsedTitle(
                title=title.rstrip(" .,"),
                source_suffix=venue.strip(" ,."),
                venue_hint=venue.strip(" ,."),
            )

    split = split_title_and_venue(working)
    if split:
        title, venue = split
        source_suffix = working[len(title):].lstrip(" .,")
        return ParsedTitle(
            title=title.rstrip(" .,"),
            source_suffix=source_suffix,
            venue_hint=venue,
        )

    stripped = TRAILING_VENUE_RE.sub("", working).strip()
    if stripped != working:
        source_suffix = working[len(stripped):].lstrip(" .,;")
        return ParsedTitle(title=stripped.rstrip(" .,"), source_suffix=source_suffix)

    return ParsedTitle(working.rstrip(" .,"))


def clean_title(raw_title: str) -> str:
    return parse_title_line(raw_title).title


def check_title_parser_regressions() -> None:
    for raw_title, expected_title, expected_suffix in TITLE_PARSE_REGRESSIONS:
        parsed = parse_title_line(raw_title)
        if (
            parsed.title != expected_title
            or parsed.source_suffix != expected_suffix
        ):
            raise ValueError(
                "Title suffix parser regression: "
                f"{raw_title!r} parsed as title={parsed.title!r}, "
                f"source_suffix={parsed.source_suffix!r}"
            )


def check_section_parser_regressions() -> None:
    for raw_text, expected_section in SECTION_PARSE_REGRESSIONS:
        section = section_from_text(raw_text)
        if section != expected_section:
            raise ValueError(
                "Section parser regression: "
                f"{raw_text!r} parsed as section={section!r}"
            )


def extract_identifiers(text: str, links: list[str]) -> dict[str, str]:
    values = [text, *links]
    joined = " ".join(values)
    urls = [match.rstrip(".,);]") for match in URL_RE.findall(joined)]

    doi = ""
    doi_match = DOI_RE.search(joined)
    if doi_match:
        doi = doi_match.group(0).rstrip(".,);]")
        doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)

    arxiv_id = ""
    arxiv_match = ARXIV_RE.search(joined)
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
    elif doi.lower().startswith("10.48550/arxiv."):
        arxiv_id = doi.split("arXiv.", 1)[-1] if "arXiv." in doi else doi.rsplit(".", 1)[-1]

    openalex_url = next(
        (url for url in urls if urlparse(url).netloc.casefold() in {"openalex.org", "www.openalex.org"}),
        "",
    )
    excluded_hosts = {"doi.org", "dx.doi.org", "arxiv.org", "www.arxiv.org", "openalex.org", "www.openalex.org"}
    paper_url = next(
        (url for url in urls if urlparse(url).netloc.casefold() not in excluded_hosts),
        "",
    )
    return {
        "doi": doi,
        "arxiv_id": arxiv_id,
        "openalex_url": openalex_url,
        "paper_url": paper_url,
    }


def explicit_year(text: str) -> str:
    years = YEAR_IN_TEXT_RE.findall(text)
    return years[-1] if years else ""


def section_from_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = re.sub(r"^[\s·•▪◦*-]+", "", normalized).strip()
    # Only standalone headings change the active section. Lines with colons are
    # paper metadata/comments such as "Dataset: GenImage", not global headings.
    if ":" in normalized or "：" in normalized:
        return ""
    normalized = normalized.casefold()
    return SECTION_ALIASES.get(normalized, "")


def document_mode(path: Path) -> str:
    stem = path.stem.upper()
    has_sid = "SID" in stem
    has_sia = "SIA" in stem
    if has_sid and has_sia:
        return "mixed"
    if has_sia:
        return "attribution"
    return "detection"


def expected_task(title: str, mode: str, section: str) -> str:
    has_detection = bool(DETECTION_RE.search(title))
    has_attribution = bool(ATTRIBUTION_RE.search(title))
    if has_detection and has_attribution:
        return "detection_and_source_attribution"
    if mode == "attribution" or section in {"Identification", "Verification"}:
        return "source_attribution"
    if mode == "mixed" and has_attribution:
        return "source_attribution"
    return "detection"


def auxiliary_notes(title: str, section: str) -> str:
    tags: list[str] = []
    title_text = title.casefold()
    if section == "Benchmark" or "benchmark" in title_text:
        tags.append("benchmark")
    if section == "Dataset":
        tags.append("dataset")
    if section == "Survey" or any(term in title_text for term in ("survey", "review", "综述")):
        tags.append("survey")
    if section == "Anti-forensics" or any(
        term in title_text for term in ("anti-forensic", "anti forensic", "evasion", "反取证")
    ):
        tags.append("anti-forensics")
    return "; ".join(["auxiliary", *tags]) if tags else ""


def combine_note_parts(*parts: str) -> str:
    values: list[str] = []
    for part in parts:
        for value in part.split(";"):
            cleaned = value.strip()
            if cleaned and cleaned not in values:
                values.append(cleaned)
    return "; ".join(values)


def is_candidate(paragraph: dict[str, object]) -> bool:
    text = str(paragraph["text"]).lstrip()
    return bool(paragraph["numbered"]) or text.startswith(("·", "•"))


def looks_like_author_line(paragraph: dict[str, object]) -> bool:
    text = str(paragraph["text"]).strip()
    if not text or is_candidate(paragraph) or YEAR_HEADING_RE.fullmatch(text):
        return False
    if str(paragraph["style"]).casefold().startswith("heading"):
        return False
    if section_from_text(text):
        return False
    lowered = text.casefold()
    if lowered.startswith(NON_AUTHOR_PREFIXES):
        return False
    if URL_RE.fullmatch(text):
        return False
    return True


def infer_document_year(path: Path) -> str:
    years = YEAR_IN_TEXT_RE.findall(path.stem)
    return years[0] if len(years) == 1 else ""


def extract_document(path: Path) -> list[dict[str, str]]:
    paragraphs = read_docx_paragraphs(path)
    mode = document_mode(path)
    default_section = "Source attribution" if mode == "attribution" else "Detection"
    section = default_section
    current_year = infer_document_year(path)
    records: list[dict[str, str]] = []

    for index, paragraph in enumerate(paragraphs):
        text = str(paragraph["text"]).strip()
        style = str(paragraph["style"])

        if not is_candidate(paragraph):
            if YEAR_HEADING_RE.fullmatch(text):
                current_year = text
                continue
            detected_section = section_from_text(text)
            if detected_section:
                section = detected_section
                continue
            if style.casefold().startswith("heading") and not style.casefold().startswith("toc"):
                if not YEAR_HEADING_RE.fullmatch(text):
                    section = text.rstrip(":：")
                continue

        if not is_candidate(paragraph):
            continue

        parsed_title = parse_title_line(text)
        title = parsed_title.title
        if not title:
            continue
        title_year = parsed_title.year or explicit_year(text)
        year = title_year or current_year
        authors = ""
        if index + 1 < len(paragraphs) and looks_like_author_line(paragraphs[index + 1]):
            authors = str(paragraphs[index + 1]["text"]).strip()

        identifiers = extract_identifiers(text, list(paragraph["links"]))
        suffix_note = (
            f"source_suffix={parsed_title.source_suffix}"
            if parsed_title.source_suffix
            else ""
        )
        records.append(
            {
                "title": title,
                "year": year,
                "authors": authors,
                **identifiers,
                "expected_task": expected_task(title, mode, section),
                "source_doc": path.name,
                "section": section,
                "notes": combine_note_parts(auxiliary_notes(title, section), suffix_note),
            }
        )
    return records


def combine_values(first: str, second: str, separator: str = " | ") -> str:
    values = [part.strip() for value in (first, second) for part in value.split(separator) if part.strip()]
    return separator.join(dict.fromkeys(values))


def merge_record(existing: dict[str, str], incoming: dict[str, str]) -> None:
    for field in FIELDS:
        if not incoming.get(field):
            continue
        if not existing.get(field):
            existing[field] = incoming[field]
        elif field in {"source_doc", "section", "notes"}:
            separator = "; " if field == "notes" else " | "
            existing[field] = combine_values(existing[field], incoming[field], separator)

    tasks = {existing.get("expected_task", ""), incoming.get("expected_task", "")}
    if {"detection", "source_attribution"}.issubset(tasks) or "detection_and_source_attribution" in tasks:
        existing["expected_task"] = "detection_and_source_attribution"


def deduplicate(records: list[dict[str, str]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    by_title: dict[str, list[dict[str, str]]] = {}
    for record in records:
        title_key = normalize_title(record.get("title", ""))
        year = record.get("year", "").strip()
        key = (title_key, year)
        if not title_key:
            continue
        match = by_key.get(key)
        if match is None:
            exact_title_matches = by_title.get(title_key, [])
            if not year and len(exact_title_matches) == 1:
                match = exact_title_matches[0]
            elif year:
                match = by_key.get((title_key, ""))
        if match is not None:
            merge_record(match, record)
            by_key[(title_key, match.get("year", "").strip())] = match
            continue
        clean_record = {field: record.get(field, "") for field in FIELDS}
        by_key[key] = clean_record
        by_title.setdefault(title_key, []).append(clean_record)
        result.append(clean_record)
    return result


def read_existing(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return []
        if "title" not in reader.fieldnames:
            raise ValueError(f"Existing checklist is missing required column 'title': {path}")
        return [{field: (row.get(field) or "").strip() for field in FIELDS} for row in reader]


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
        temporary_path = Path(handle.name)
    temporary_path.replace(path)


def print_counter(label: str, counts: Counter[str]) -> None:
    print(f"{label}:")
    if not counts:
        print("  (none): 0")
        return
    for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold())):
        print(f"  {name or '(blank)'}: {count}")


def main() -> int:
    args = parse_args()
    try:
        check_title_parser_regressions()
        check_section_parser_regressions()
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    input_dir = args.input_dir.resolve()
    output = args.output.resolve()
    source_docs = sorted(input_dir.glob("*.docx"))
    if not source_docs:
        print(f"No DOCX files found under {input_dir}")
        return 1

    extracted: list[dict[str, str]] = []
    source_counts: Counter[str] = Counter()
    section_counts: Counter[str] = Counter()
    for source_doc in source_docs:
        try:
            rows = extract_document(source_doc)
        except ValueError as exc:
            print(f"Error: {source_doc.name}: {exc}")
            return 1
        extracted.extend(rows)
        source_counts[source_doc.name] += len(rows)
        section_counts.update(row["section"] or "(blank)" for row in rows)

    deduplicated_imports = deduplicate(extracted)
    existing = read_existing(output) if args.preserve_existing else []
    final_rows = deduplicate([*existing, *deduplicated_imports])
    write_csv(output, final_rows)

    cleaned_before_dedup = sum("source_suffix=" in row.get("notes", "") for row in extracted)
    cleaned_after_dedup = sum(
        "source_suffix=" in row.get("notes", "") for row in deduplicated_imports
    )

    print("Key paper DOCX import summary")
    print(f"  Total extracted: {len(extracted)}")
    print(f"  After deduplication: {len(deduplicated_imports)}")
    print(f"  Titles cleaned before deduplication: {cleaned_before_dedup}")
    print(f"  Titles cleaned after deduplication: {cleaned_after_dedup}")
    print(f"  Existing checklist rows preserved: {len(existing)}")
    print(f"  Checklist rows written: {len(final_rows)}")
    print_counter("By expected_task", Counter(row["expected_task"] for row in deduplicated_imports))
    print_counter("By source_doc (before cross-document deduplication)", source_counts)
    print_counter("By section (before cross-document deduplication)", section_counts)
    print(f"Output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
