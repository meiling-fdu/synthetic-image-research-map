#!/usr/bin/env python3
"""Canonical paper, author, institution, affiliation, and marker authority."""

from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent.parent
CURATED = ROOT / "data" / "curated"
PAPERS_PATH = CURATED / "papers.csv"
MAPPINGS_PATH = CURATED / "author_institution_mappings.csv"
LOCATIONS_PATH = CURATED / "institution_locations.csv"
ALIASES_PATH = CURATED / "institution_aliases.csv"
EXCLUSIONS_PATH = CURATED / "paper_exclusions.csv"
VISIBLE_MAPPING_STATUSES = {"active", "needs_review"}
FORBIDDEN_RUNTIME_FILENAME = "openalex_candidate_" + "map_data.json"


class CanonicalAuthorshipError(RuntimeError):
    """Canonical data is invalid or a forbidden legacy dependency was found."""


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _normalized(value: Any) -> str:
    text = unicodedata.normalize("NFKC", _clean(value)).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def normalize_title(value: Any) -> str:
    return _normalized(value)


def normalize_doi(value: Any) -> str:
    text = _clean(value).casefold()
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text)
    return text.removeprefix("doi:")


def normalize_arxiv(value: Any) -> str:
    text = _clean(value).casefold()
    text = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", text)
    return text.removesuffix(".pdf").removeprefix("arxiv:")


def normalize_openalex(value: Any) -> str:
    text = _clean(value).rstrip("/")
    return text.rsplit("/", 1)[-1].upper() if text else ""


def institution_id(value: Any) -> str:
    normalized = _normalized(value)
    if not normalized:
        return ""
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"institution:{digest}"


def _people(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        candidates = value
    else:
        text = _clean(value)
        separator = ";" if ";" in text else ","
        candidates = text.split(separator)
    people: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        name = _clean(candidate)
        key = _normalized(name)
        if name and key and key not in seen:
            seen.add(key)
            people.append(name)
    return people


def _read_csv(path: Path) -> list[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except (OSError, UnicodeError, csv.Error) as error:
        raise CanonicalAuthorshipError(f"could not read {path}: {error}") from error


def canonical_identity(record: Mapping[str, Any]) -> str:
    doi = normalize_doi(record.get("doi"))
    if doi:
        return f"doi:{doi}"
    arxiv = normalize_arxiv(record.get("arxiv_id") or record.get("arxiv_url"))
    if arxiv:
        return f"arxiv:{arxiv}"
    openalex = normalize_openalex(record.get("openalex_url"))
    if openalex:
        return f"openalex:{openalex}"
    title = normalize_title(record.get("title"))
    digest = hashlib.sha256(title.encode("utf-8")).hexdigest()[:20]
    return f"title:{digest}"


def identity_keys(record: Mapping[str, Any]) -> list[str]:
    keys = []
    for prefix, value in (
        ("doi", normalize_doi(record.get("doi"))),
        ("arxiv", normalize_arxiv(record.get("arxiv_id") or record.get("arxiv_url"))),
        ("openalex", normalize_openalex(record.get("openalex_url"))),
    ):
        if value:
            keys.append(f"{prefix}:{value}")
    title = normalize_title(record.get("title"))
    if title:
        digest = hashlib.sha256(title.encode("utf-8")).hexdigest()[:20]
        keys.append(f"title:{digest}")
    return keys


def build_canonical_authorship(
    authors: Any,
    institution_sources: Sequence[Mapping[str, Any]],
) -> Dict[str, list[Dict[str, Any]]]:
    ordered_authors = _people(authors)
    author_names = {_normalized(author): author for author in ordered_authors}
    institutions_by_id: Dict[str, Dict[str, Any]] = {}
    for source in institution_sources:
        name = _clean(source.get("canonical_name") or source.get("institution"))
        stable_id = _clean(source.get("institution_id")) or institution_id(name)
        if not name or not stable_id:
            continue
        entry = institutions_by_id.setdefault(
            stable_id,
            {"institution_id": stable_id, "canonical_name": name, "_authors": set()},
        )
        source_authors = _people(source.get("authors") or source.get("institution_authors"))
        if not source_authors and len(ordered_authors) == 1:
            source_authors = ordered_authors
        for author in source_authors:
            key = _normalized(author)
            if key in author_names:
                entry["_authors"].add(key)
    institutions_by_id = {
        stable_id: entry
        for stable_id, entry in institutions_by_id.items()
        if entry["_authors"]
    }
    mapped = {key for entry in institutions_by_id.values() for key in entry["_authors"]}
    unresolved = set(author_names) - mapped
    if unresolved:
        institutions_by_id["institution:unresolved"] = {
            "institution_id": "institution:unresolved",
            "canonical_name": "Unresolved institution (manual review)",
            "_authors": unresolved,
        }
    ordered = sorted(
        institutions_by_id.values(),
        key=lambda item: (_normalized(item["canonical_name"]), item["institution_id"]),
    )
    institutions = [
        {
            "institution_id": entry["institution_id"],
            "canonical_name": entry["canonical_name"],
            "index": index,
        }
        for index, entry in enumerate(ordered, start=1)
    ]
    canonical_authors = [
        {
            "name": author,
            "institutions": [
                entry["institution_id"]
                for entry in ordered
                if _normalized(author) in entry["_authors"]
            ],
        }
        for author in ordered_authors
    ]
    return {"authors": canonical_authors, "institutions": institutions}


def legacy_affiliation_fields(
    canonical: Mapping[str, Any],
) -> tuple[list[Dict[str, Any]], list[Dict[str, Any]]]:
    """Compatibility fields are always derived from canonical data."""
    institutions = canonical.get("institutions") or []
    authors = canonical.get("authors") or []
    by_id = {item["institution_id"]: [] for item in institutions}
    indices = {item["institution_id"]: item["index"] for item in institutions}
    for author in authors:
        for stable_id in author["institutions"]:
            by_id[stable_id].append(author["name"])
    return (
        [
            {
                "index": item["index"],
                "institution_id": item["institution_id"],
                "institution": item["canonical_name"],
                "authors": by_id[item["institution_id"]],
            }
            for item in institutions
        ],
        [
            {
                "author": author["name"],
                "institution_ids": list(author["institutions"]),
                "institution_indices": [
                    indices[stable_id] for stable_id in author["institutions"]
                ],
            }
            for author in authors
        ],
    )


def guard_no_legacy_runtime_references() -> None:
    offenders = []
    runtime_files = [*sorted((ROOT / "scripts").glob("*.py")), ROOT / "web" / "app.js"]
    for path in runtime_files:
        try:
            if FORBIDDEN_RUNTIME_FILENAME in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))
        except OSError as error:
            raise CanonicalAuthorshipError(f"could not inspect {path}: {error}") from error
    if offenders:
        raise CanonicalAuthorshipError(
            "forbidden legacy candidate dependency: " + ", ".join(offenders)
        )


def _source_rank(row: Mapping[str, Any]) -> tuple[int, int, str]:
    publication = _clean(row.get("publication_type")).casefold()
    formal = publication not in {"preprint", "posted-content"} and "arxiv" not in _clean(
        row.get("venue")
    ).casefold()
    reviewed = _clean(row.get("review_status")) == "reviewed"
    return (int(formal), int(reviewed), _clean(row.get("updated_at")))


def _merge_paper_rows(rows: Sequence[Dict[str, str]]) -> list[Dict[str, Any]]:
    parent = list(range(len(rows)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    seen: Dict[str, int] = {}
    for index, row in enumerate(rows):
        for key in identity_keys(row):
            if key in seen:
                parent[find(index)] = find(seen[key])
            else:
                seen[key] = index
    groups: Dict[int, list[Dict[str, str]]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[find(index)].append(row)
    merged = []
    for members in groups.values():
        ordered = sorted(members, key=_source_rank, reverse=True)
        result: Dict[str, Any] = {}
        fields = set().union(*(member.keys() for member in members))
        for field in fields:
            result[field] = next(
                (_clean(member.get(field)) for member in ordered if _clean(member.get(field))),
                "",
            )
        result["_member_paper_ids"] = {
            _clean(member.get("paper_id")) for member in members if _clean(member.get("paper_id"))
        }
        result["authors"] = _people(
            next((member.get("authors") for member in ordered if _clean(member.get("authors"))), "")
        )
        source_values = [
            _clean(member.get("source_database"))
            for member in members
            if _clean(member.get("source_database"))
        ]
        if normalize_openalex(result.get("openalex_url")):
            source_values.append("OpenAlex")
        if normalize_arxiv(result.get("arxiv_id")):
            source_values.append("arXiv")
        canonical_source_labels = {
            "openalex": "OpenAlex", "arxiv": "arXiv", "iris": "IRIS"
        }
        sources = {
            value.casefold(): canonical_source_labels.get(value.casefold(), value)
            for value in source_values
        }
        result["provenance_sources"] = sorted(
            sources.values(), key=lambda value: (value.casefold(), value)
        )
        result["paper_id"] = canonical_identity(result)
        merged.append(result)
    return merged


def load_canonical_dataset(*, check_runtime: bool = True) -> Dict[str, Any]:
    if check_runtime:
        guard_no_legacy_runtime_references()
    paper_rows = _read_csv(PAPERS_PATH)
    mappings = _read_csv(MAPPINGS_PATH)
    locations = _read_csv(LOCATIONS_PATH)
    aliases = _read_csv(ALIASES_PATH)
    exclusions = _read_csv(EXCLUSIONS_PATH)
    known_paper_ids = {_clean(row.get("paper_id")) for row in paper_rows}
    orphan_mappings: Dict[str, list[Dict[str, str]]] = defaultdict(list)
    for mapping in mappings:
        if _clean(mapping.get("paper_id")) not in known_paper_ids:
            orphan_mappings[_clean(mapping.get("paper_id"))].append(mapping)
    for paper_id, rows in orphan_mappings.items():
        authors = []
        for row in rows:
            authors.extend(_people(row.get("institution_authors")))
        paper_rows.append(
            {
                "paper_id": paper_id,
                "title": _clean(rows[0].get("title")),
                "year": _clean(rows[0].get("year")),
                "authors": "; ".join(dict.fromkeys(authors)),
                "doi": _clean(rows[0].get("doi")),
                "openalex_url": _clean(rows[0].get("openalex_url")),
                "task": "uncertain",
                "scope_status": "in_scope",
                "source_database": "curated_mapping",
                "metadata_source": "curated_mapping",
                "review_status": "reviewed",
            }
        )
    excluded_ids = {
        _clean(row.get("paper_id"))
        for row in exclusions
        if _clean(row.get("status")).casefold() == "active"
    }
    alias_lookup = {
        _normalized(row.get("alias_name")): _clean(row.get("canonical_institution_name"))
        for row in aliases
        if _clean(row.get("review_status")) == "confirmed"
    }
    location_lookup = {
        _normalized(row.get("normalized_institution") or row.get("institution")): row
        for row in locations
        if _clean(row.get("coordinate_status")) == "known"
    }
    papers = []
    markers = []
    for paper in _merge_paper_rows(paper_rows):
        if paper["_member_paper_ids"] & excluded_ids:
            continue
        paper_mappings = [
            row
            for row in mappings
            if _clean(row.get("paper_id")) in paper["_member_paper_ids"]
            and _clean(row.get("mapping_status")) in VISIBLE_MAPPING_STATUSES
        ]
        sources = []
        marker_locations: Dict[str, Dict[str, str]] = {}
        for mapping in paper_mappings:
            original = _clean(mapping.get("institution"))
            canonical_name = alias_lookup.get(_normalized(original), original)
            stable_id = institution_id(canonical_name)
            sources.append(
                {
                    "institution_id": stable_id,
                    "canonical_name": canonical_name,
                    "authors": _people(mapping.get("institution_authors")),
                }
            )
            location = location_lookup.get(_normalized(canonical_name))
            if location:
                marker_locations[stable_id] = location
        canonical = build_canonical_authorship(paper["authors"], sources)
        affiliations, author_indices = legacy_affiliation_fields(canonical)
        public_paper = {
            key: value for key, value in paper.items() if not key.startswith("_")
        }
        public_paper.update(
            {
                "id": paper["paper_id"],
                "year": int(paper["year"]) if _clean(paper.get("year")).isdigit() else paper.get("year"),
                "publication_year": int(paper["year"]) if _clean(paper.get("year")).isdigit() else paper.get("year"),
                "venue_name": paper.get("venue", ""),
                "primary_url": paper.get("paper_url", ""),
                "canonical_authorship": canonical,
                "author_institution_affiliations": affiliations,
                "author_institution_indices": author_indices,
                "in_scope": _clean(paper.get("scope_status")) == "in_scope",
                "needs_review": (
                    _clean(paper.get("review_status")) != "reviewed"
                    or any(
                        "institution:unresolved" in author["institutions"]
                        for author in canonical["authors"]
                    )
                ),
            }
        )
        paper_markers = []
        for institution in canonical["institutions"]:
            stable_id = institution["institution_id"]
            location = marker_locations.get(stable_id)
            if not location:
                continue
            if _clean(paper.get("task")) == "uncertain":
                continue
            country = _clean(location.get("country"))
            country_code = _clean(location.get("country_code"))
            region = _clean(location.get("region"))
            region_code = ""
            regional_code = {
                "hong kong": "HK", "taiwan": "TW", "macau": "MO", "macao": "MO"
            }.get(_normalized(region) or _normalized(country))
            if country_code in {"HK", "TW", "MO"} or regional_code:
                region_code = regional_code or country_code
                region = {"HK": "Hong Kong", "TW": "Taiwan", "MO": "Macau"}[
                    region_code
                ]
                country, country_code = "China", "CN"
            paper_markers.append(
                {
                    **public_paper,
                    "id": f"{paper['paper_id']}::{stable_id}",
                    "institution_id": stable_id,
                    "institution": institution["canonical_name"],
                    "institution_authors": next(
                        item["authors"]
                        for item in affiliations
                        if item["institution_id"] == stable_id
                    ),
                    "city": _clean(location.get("city")),
                    "region": region,
                    "region_code": region_code,
                    "country": country,
                    "country_code": country_code,
                    "latitude": float(location["lat"]),
                    "longitude": float(location["lon"]),
                    "resolution_confidence": "high",
                    "resolution_method": "curated_canonical_location",
                    "needs_review": False,
                }
            )
        public_paper.update(
            {
                "has_map_location": bool(paper_markers),
                "map_record_count": len(paper_markers),
                "missing_affiliation": not bool(paper_mappings),
                "missing_coordinates": bool(paper_mappings) and not bool(paper_markers),
                "coverage_status": (
                    "map_ready"
                    if paper_markers
                    else "missing_affiliation"
                    if not paper_mappings
                    else "missing_coordinates"
                ),
                "aggregated_institutions": [
                    item["canonical_name"] for item in canonical["institutions"]
                ],
                "aggregated_country_names": sorted(
                    {_clean(item.get("country")) for item in paper_markers if _clean(item.get("country"))}
                ),
                "aggregated_country_codes": sorted(
                    {_clean(item.get("country_code")) for item in paper_markers if _clean(item.get("country_code"))}
                ),
                "aggregated_regions": sorted(
                    {_clean(item.get("region")) for item in paper_markers if _clean(item.get("region"))}
                ),
            }
        )
        for marker in paper_markers:
            marker.update(
                {
                    "has_map_location": True,
                    "map_record_count": len(paper_markers),
                    "missing_affiliation": False,
                    "missing_coordinates": False,
                    "coverage_status": "map_ready",
                }
            )
        papers.append(public_paper)
        markers.extend(paper_markers)
    papers.sort(key=lambda row: (-int(row.get("year") or 0), _clean(row.get("title")).casefold()))
    markers.sort(
        key=lambda row: (
            -int(row.get("year") or 0),
            _clean(row.get("title")).casefold(),
            _clean(row.get("institution")).casefold(),
        )
    )
    validate_canonical_dataset(papers, markers)
    return {"papers": papers, "markers": markers}


def validate_canonical_dataset(
    papers: Sequence[Mapping[str, Any]],
    markers: Sequence[Mapping[str, Any]],
) -> None:
    for field, normalizer in (("doi", normalize_doi), ("arxiv_id", normalize_arxiv)):
        seen: Dict[str, str] = {}
        for paper in papers:
            value = normalizer(paper.get(field))
            if value and value in seen:
                raise CanonicalAuthorshipError(
                    f"duplicate {field}: {value} ({seen[value]} and {paper.get('paper_id')})"
                )
            if value:
                seen[value] = _clean(paper.get("paper_id"))
    paper_ids = [_clean(paper.get("paper_id")) for paper in papers]
    if len(paper_ids) != len(set(paper_ids)):
        raise CanonicalAuthorshipError("more than one record exists per canonical paper")
    for paper in papers:
        institutions = paper["canonical_authorship"]["institutions"]
        ids = [item["institution_id"] for item in institutions]
        if len(ids) != len(set(ids)):
            raise CanonicalAuthorshipError(
                f"duplicate institutions for {paper.get('paper_id')}"
            )
    known = set(paper_ids)
    if any(_clean(marker.get("paper_id")) not in known for marker in markers):
        raise CanonicalAuthorshipError("marker references an unknown canonical paper")
