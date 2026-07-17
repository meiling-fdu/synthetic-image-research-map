#!/usr/bin/env python3
"""Deterministic canonical venue resolution shared by migration and exports."""

from __future__ import annotations

import csv
import difflib
import hashlib
import html
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from .curated_schema import VENUE_TYPE_ORDER
    from .publication_types import normalize_publication_type
except ImportError:
    from curated_schema import VENUE_TYPE_ORDER
    from publication_types import normalize_publication_type


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VENUE_ALIASES_PATH = REPOSITORY_ROOT / "data" / "curated" / "venue_aliases.csv"
VENUE_ALIAS_COLUMNS = (
    "alias",
    "venue_id",
    "venue_name",
    "venue_acronym",
    "venue_type",
    "venue_track",
    "review_status",
    "notes",
)
ALLOWED_VENUE_TYPES = set(VENUE_TYPE_ORDER)
ALLOWED_VENUE_TRACKS = {
    "main", "workshops", "findings", "industry", "demo", "doctoral_consortium", "other"
}


class VenueRegistryError(RuntimeError):
    """Invalid or conflicting canonical venue registry operation."""


@dataclass(frozen=True)
class CanonicalVenue:
    venue_id: str
    venue_name: str
    venue_acronym: str
    venue_type: str
    venue_track: str
    raw_venue: str
    venue_aliases: tuple[str, ...] = ()
    ambiguity_status: str = "resolved"

    def as_record(self) -> dict[str, Any]:
        result = asdict(self)
        result["venue_aliases"] = list(self.venue_aliases)
        return result


def clean_text(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = unicodedata.normalize("NFKC", text)
    text = "".join(" " if unicodedata.category(char).startswith("C") else char for char in text)
    return " ".join(text.split()).strip(" ,;:")


def alias_key(value: Any) -> str:
    return " ".join(re.findall(r"[\w]+", clean_text(value).casefold(), flags=re.UNICODE))


def normalize_venue_type(value: Any, *, publication_type: Any = "", track: str = "main") -> str:
    text = clean_text(value).casefold().replace("_", " ").replace("-", " ")
    if track == "workshops" or text in {"workshop", "workshops"}:
        return "conference"
    if text in ALLOWED_VENUE_TYPES:
        return text
    if text in {"article", "journal article"}:
        return "journal"
    if text in {"book series", "book chapter"}:
        return "book"
    if text in {"repository", "posted content"}:
        return "preprint"
    normalized = normalize_publication_type(publication_type or value)
    if normalized in {"conference", "journal", "preprint", "book"}:
        return normalized
    if "workshop" in text:
        return "conference"
    return ""


def publication_type_for_venue_type(value: Any) -> str:
    return normalize_venue_type(value)


def venue_type_rank(value: Any) -> int:
    normalized = normalize_venue_type(value)
    try:
        return VENUE_TYPE_ORDER.index(normalized)
    except ValueError:
        return len(VENUE_TYPE_ORDER)


def display_venue(record: Mapping[str, Any]) -> str:
    venue_type = clean_text(record.get("venue_type") or record.get("publication_type"))
    name = clean_text(record.get("venue_name") or record.get("venue"))
    acronym = clean_text(record.get("venue_acronym"))
    track = clean_text(record.get("venue_track") or "main")
    if not name:
        return ""
    label = f"{venue_type.title()} · {name}" if venue_type else name
    if acronym:
        label += f" ({acronym})"
    if track and track != "main":
        label += f" · {track.replace('_', ' ').title()}"
    return label


def read_venue_aliases(path: Path = DEFAULT_VENUE_ALIASES_PATH) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != VENUE_ALIAS_COLUMNS:
            raise ValueError(f"{path} does not have the exact venue alias header")
        return [dict(row) for row in reader]


def _canonical_registry(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for index, raw_row in enumerate(rows, start=2):
        if clean_text(raw_row.get("review_status")) != "confirmed":
            continue
        row = {column: clean_text(raw_row.get(column)) for column in VENUE_ALIAS_COLUMNS}
        venue_id = row["venue_id"]
        if not venue_id:
            raise VenueRegistryError(f"venue alias row {index} is missing venue_id")
        identity = tuple(row[field] for field in (
            "venue_name", "venue_acronym", "venue_type", "venue_track",
        ))
        if not identity[0] or identity[2] not in ALLOWED_VENUE_TYPES or identity[3] not in ALLOWED_VENUE_TRACKS:
            raise VenueRegistryError(f"venue alias row {index} has invalid canonical metadata")
        current = registry.setdefault(venue_id, {
            "venue_id": venue_id,
            "venue_name": identity[0],
            "venue_acronym": identity[1],
            "venue_type": identity[2],
            "venue_track": identity[3],
            "aliases": [],
        })
        current_identity = tuple(current[field] for field in (
            "venue_name", "venue_acronym", "venue_type", "venue_track",
        ))
        if current_identity != identity:
            raise VenueRegistryError(
                f"venue_id {venue_id!r} has inconsistent canonical metadata"
            )
        if row["alias"] and row["alias"] not in current["aliases"]:
            current["aliases"].append(row["alias"])
    acronym_names: dict[str, tuple[str, str]] = {}
    for venue_id, venue in registry.items():
        acronym = alias_key(venue["venue_acronym"])
        if not acronym:
            continue
        name = alias_key(venue["venue_name"])
        previous = acronym_names.get(acronym)
        if previous and previous[1] != name:
            raise VenueRegistryError(
                f"venue acronym {venue['venue_acronym']!r} collides between "
                f"{previous[0]!r} and {venue_id!r}"
            )
        acronym_names[acronym] = (venue_id, name)
    return registry


def canonical_venue_options(
    aliases: Sequence[Mapping[str, Any]],
    papers: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Return canonical Admin options with aliases, historical variants, and usage."""
    registry = _canonical_registry(aliases)
    paper_ids_by_venue: dict[str, set[str]] = {}
    raw_variants: dict[str, list[str]] = {}
    for index, paper in enumerate(papers):
        venue_id = clean_text(paper.get("venue_id"))
        if venue_id not in registry:
            continue
        identity = clean_text(
            paper.get("paper_id") or paper.get("doi") or paper.get("openalex_url")
        ) or f"row:{index}"
        paper_ids_by_venue.setdefault(venue_id, set()).add(identity)
        raw = clean_text(paper.get("raw_venue"))
        if raw and raw not in raw_variants.setdefault(venue_id, []):
            raw_variants[venue_id].append(raw)
    options = []
    for venue_id, venue in registry.items():
        option = {
            **venue,
            "raw_variants": raw_variants.get(venue_id, []),
            "paper_count": len(paper_ids_by_venue.get(venue_id, set())),
        }
        option["venue_label"] = display_venue(option)
        option["search_text"] = " ".join(dict.fromkeys(filter(None, (
            option["venue_name"], option["venue_acronym"], option["venue_type"],
            option["venue_track"], *option["aliases"], *option["raw_variants"],
        ))))
        options.append(option)
    return sorted(options, key=lambda item: (
        venue_type_rank(item["venue_type"]),
        -item["paper_count"],
        item["venue_name"].casefold(),
        item["venue_id"],
    ))


def canonical_venue_by_id(
    venue_id: Any,
    aliases: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    identifier = clean_text(venue_id)
    venue = _canonical_registry(aliases).get(identifier)
    if venue is None:
        raise VenueRegistryError(f"venue_id does not exist: {identifier!r}")
    result = dict(venue)
    result["venue_label"] = display_venue(result)
    return result


def validate_canonical_venue_fields(
    record: Mapping[str, Any],
    aliases: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    venue = canonical_venue_by_id(record.get("venue_id"), aliases)
    for field in ("venue_name", "venue_acronym", "venue_type", "venue_track"):
        supplied = clean_text(record.get(field))
        if supplied and supplied != venue[field]:
            raise VenueRegistryError(
                f"{field} conflicts with canonical venue_id {venue['venue_id']!r}"
            )
    return venue


def _possible_registry_matches(
    name: str,
    acronym: str,
    raw_alias: str,
    registry: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    query_values = [value for value in (name, acronym, raw_alias) if value]
    matches = []
    for venue in registry.values():
        candidate_values = [
            venue["venue_name"], venue["venue_acronym"], *venue.get("aliases", []),
        ]
        strongest = max(
            (difflib.SequenceMatcher(None, alias_key(query), alias_key(candidate)).ratio()
             for query in query_values for candidate in candidate_values if candidate),
            default=0.0,
        )
        acronym_match = bool(acronym and venue["venue_acronym"] and alias_key(acronym) == alias_key(venue["venue_acronym"]))
        if strongest >= 0.72 or acronym_match:
            matches.append({
                **{field: venue[field] for field in (
                    "venue_id", "venue_name", "venue_acronym", "venue_type", "venue_track",
                )},
                "venue_label": display_venue(venue),
                "similarity": round(strongest, 3),
                "acronym_match": acronym_match,
            })
    return sorted(matches, key=lambda item: (-item["similarity"], item["venue_label"]))


def create_canonical_venue(
    draft: Mapping[str, Any],
    path: Path = DEFAULT_VENUE_ALIASES_PATH,
) -> dict[str, Any]:
    name = clean_text(draft.get("venue_name"))
    acronym = clean_text(draft.get("venue_acronym"))
    venue_type = normalize_venue_type(draft.get("venue_type"))
    track = clean_text(draft.get("venue_track")) or "main"
    raw_alias = clean_text(draft.get("raw_alias") or draft.get("raw_venue"))
    if _track_from_text(f"{name} {raw_alias}") == "workshops":
        track = "workshops"
    review_note = clean_text(draft.get("review_note"))
    if not name:
        raise VenueRegistryError("canonical full name is required")
    if venue_type not in ALLOWED_VENUE_TYPES:
        raise VenueRegistryError("venue type is invalid")
    if track not in ALLOWED_VENUE_TRACKS:
        raise VenueRegistryError("venue track is invalid")
    if not raw_alias:
        raise VenueRegistryError("raw input or alias is required")
    rows = read_venue_aliases(path)
    registry = _canonical_registry(rows)
    exact_values: dict[str, str] = {}
    for venue in registry.values():
        for value in (venue["venue_name"], venue["venue_acronym"], *venue["aliases"]):
            key = alias_key(value)
            if key:
                exact_values.setdefault(key, venue["venue_id"])
    duplicate_name = next((
        venue for venue in registry.values()
        if alias_key(venue["venue_name"]) == alias_key(name)
        and venue["venue_track"] == track
    ), None)
    if duplicate_name:
        raise VenueRegistryError(
            f"canonical name and track duplicate existing venue {duplicate_name['venue_id']!r}"
        )
    duplicate_alias_id = exact_values.get(alias_key(raw_alias))
    if duplicate_alias_id:
        raise VenueRegistryError(
            f"alias duplicates existing venue {duplicate_alias_id!r}"
        )
    acronym_collision = next((
        venue for venue in registry.values()
        if acronym and alias_key(venue["venue_acronym"]) == alias_key(acronym)
        and alias_key(venue["venue_name"]) != alias_key(name)
    ), None)
    if acronym_collision:
        raise VenueRegistryError(
            f"venue acronym collides with existing venue {acronym_collision['venue_id']!r}"
        )
    possible_matches = _possible_registry_matches(name, acronym, raw_alias, registry)
    if possible_matches and draft.get("confirmed_similar") is not True:
        error = VenueRegistryError("possible canonical venue matches require explicit confirmation")
        error.possible_matches = possible_matches  # type: ignore[attr-defined]
        raise error
    venue_id = _stable_id(name, track)
    if venue_id in registry:
        suffix = hashlib.sha256(f"{name}|{venue_type}|{track}".encode("utf-8")).hexdigest()[:8]
        venue_id = f"{venue_id}-{suffix}"
    aliases_to_add = list(dict.fromkeys([name, raw_alias]))
    new_rows = [
        {
            "alias": alias,
            "venue_id": venue_id,
            "venue_name": name,
            "venue_acronym": acronym,
            "venue_type": venue_type,
            "venue_track": track,
            "review_status": "confirmed",
            "notes": review_note or "Created through reviewed Admin canonical venue workflow.",
        }
        for alias in aliases_to_add
    ]
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=VENUE_ALIAS_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows([*rows, *new_rows])
    temporary.replace(path)
    venue = canonical_venue_by_id(venue_id, [*rows, *new_rows])
    return {**venue, "aliases": aliases_to_add, "possible_matches": possible_matches}


def _strip_edition_noise(value: str) -> str:
    text = re.sub(r"^\s*(?:19|20)\d{2}\s+", "", value)
    text = re.sub(r"^\s*Proceedings\s+of\s+(?:the\s+)?", "", text, flags=re.I)
    text = re.sub(r"^\s*(?:19|20)\d{2}\s+", "", text)
    text = re.sub(
        r"^\s*(?:the\s+)?(?:\d{1,3}(?:st|nd|rd|th)|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
        r"eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|"
        r"thirty(?:[ -](?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth))?|forty(?:[ -](?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth))?)\s+",
        "",
        text,
        flags=re.I,
    )
    return clean_text(text)


def _track_from_text(value: str) -> str:
    lowered = value.casefold()
    if re.search(r"\bworkshops?\b", lowered):
        return "workshops"
    if re.search(r"\bfindings\b", lowered):
        return "findings"
    if re.search(r"\bindustry\s+track\b", lowered):
        return "industry"
    if re.search(r"\b(?:demo|demonstration)\s+track\b", lowered):
        return "demo"
    if re.search(r"\bdoctoral\s+consortium\b", lowered):
        return "doctoral_consortium"
    return "main"


def _stable_id(name: str, track: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()).strip("-")
    if not slug:
        slug = hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]
    return f"venue:{slug}:{track}"


def _catalog_index(rows: Sequence[Mapping[str, Any]]) -> tuple[dict[str, list[dict[str, str]]], dict[str, tuple[str, ...]]]:
    by_alias: dict[str, list[dict[str, str]]] = {}
    aliases_by_id: dict[str, list[str]] = {}
    for row in rows:
        if clean_text(row.get("review_status")) != "confirmed":
            continue
        alias = clean_text(row.get("alias"))
        key = alias_key(alias)
        if key:
            normalized_row = {column: clean_text(row.get(column)) for column in VENUE_ALIAS_COLUMNS}
            if normalized_row not in by_alias.setdefault(key, []):
                by_alias[key].append(normalized_row)
        venue_id = clean_text(row.get("venue_id"))
        if venue_id and alias:
            aliases_by_id.setdefault(venue_id, []).append(alias)
    return by_alias, {key: tuple(dict.fromkeys(values)) for key, values in aliases_by_id.items()}


def _known_lookup_keys(raw: str) -> list[str]:
    cleaned = _strip_edition_noise(raw)
    candidates = [raw, cleaned]
    # Only remove numeric proceedings volumes for the series where the suffix is
    # known not to be part of the venue identity.
    if re.search(r"Advances in Neural Information Processing Systems\s+\d+\s*$", cleaned, re.I):
        candidates.append(re.sub(r"\s+\d+\s*$", "", cleaned))
    # ACM MM proceedings commonly encode only the yearly edition in this prefix.
    candidates.append(re.sub(r"^\d+(?:st|nd|rd|th)\s+", "", cleaned, flags=re.I))
    return list(dict.fromkeys(alias_key(candidate) for candidate in candidates if candidate))


def resolve_venue(
    raw_venue: Any,
    *,
    publication_type: Any = "",
    venue_type: Any = "",
    aliases: Sequence[Mapping[str, Any]] | None = None,
) -> CanonicalVenue:
    raw = clean_text(raw_venue)
    if not raw:
        return CanonicalVenue("", "", "", normalize_venue_type(venue_type, publication_type=publication_type), "main", "", (), "unresolved")
    rows = list(aliases) if aliases is not None else read_venue_aliases()
    by_alias, aliases_by_id = _catalog_index(rows)
    track = _track_from_text(raw)
    matches = [row for key in _known_lookup_keys(raw) for row in by_alias.get(key, [])]
    unique_ids = {row["venue_id"] for row in matches}
    if len(unique_ids) > 1:
        return CanonicalVenue(_stable_id(raw, track), raw, "", normalize_venue_type(venue_type, publication_type=publication_type, track=track), track, raw, (), "ambiguous")
    if matches:
        row = matches[0]
        canonical_track = row["venue_track"] or track
        canonical_type = normalize_venue_type(row["venue_type"] or venue_type, publication_type=publication_type, track=canonical_track)
        return CanonicalVenue(row["venue_id"], row["venue_name"], row["venue_acronym"], canonical_type, canonical_track, raw, aliases_by_id.get(row["venue_id"], ()))

    cleaned = _strip_edition_noise(raw)
    detected_track = _track_from_text(cleaned)
    parenthetical = re.search(r"\s*\(([A-Za-z][A-Za-z0-9&.-]{1,15})\)\s*(?:Workshops?|Findings)?\s*$", cleaned)
    acronym = ""
    name = cleaned
    if parenthetical and re.search(r"[A-Z]", parenthetical.group(1)):
        acronym = parenthetical.group(1)
        name = clean_text(cleaned[: parenthetical.start()] + cleaned[parenthetical.end():])
    name = re.sub(r"\s+(?:Workshops?|Findings|Industry Track|Demo(?:nstration)? Track|Doctoral Consortium)\s*$", "", name, flags=re.I)
    name = clean_text(name)
    resolved_type = normalize_venue_type(venue_type, publication_type=publication_type, track=detected_track)
    return CanonicalVenue(_stable_id(name, detected_track), name, acronym, resolved_type, detected_track, raw, (raw,), "unmapped")


def canonicalize_record(record: Mapping[str, Any], aliases: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    result = dict(record)
    resolved_aliases = list(aliases) if aliases is not None else read_venue_aliases()
    existing_id = clean_text(result.get("venue_id"))
    if existing_id:
        try:
            canonical = validate_canonical_venue_fields(result, resolved_aliases)
        except VenueRegistryError:
            canonical = None
        if canonical is not None:
            raw = clean_text(result.get("raw_venue"))
            result.update(canonical)
            result["raw_venue"] = raw
            result["venue_aliases"] = list(canonical.get("aliases", []))
            result["venue"] = canonical["venue_name"]
            result["venue_label"] = display_venue(result)
            result["ambiguity_status"] = "resolved"
            return result
    source = result.get("raw_venue") or result.get("venue_name") or result.get("venue")
    venue = resolve_venue(source, publication_type=result.get("publication_type"), venue_type=result.get("venue_type"), aliases=resolved_aliases)
    result.update(venue.as_record())
    result["venue"] = venue.venue_name
    result["venue_label"] = display_venue(result)
    return result


def canonicalize_records(records: Iterable[Mapping[str, Any]], aliases: Sequence[Mapping[str, Any]] | None = None) -> list[dict[str, Any]]:
    resolved_aliases = list(aliases) if aliases is not None else read_venue_aliases()
    return [canonicalize_record(record, resolved_aliases) for record in records]
