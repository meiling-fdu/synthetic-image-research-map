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
    from .venue_tracks import ALLOWED_VENUE_TRACKS, normalize_venue_track
    from .publication_types import normalize_publication_type, resolve_publication_type
except ImportError:
    from curated_schema import VENUE_TYPE_ORDER
    from venue_tracks import ALLOWED_VENUE_TRACKS, normalize_venue_track
    from publication_types import normalize_publication_type, resolve_publication_type


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
TRACKLESS_VENUE_TYPES = {"journal", "preprint", "book"}


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


def normalize_venue_type(value: Any, *, publication_type: Any = "", track: str = "Main") -> str:
    text = clean_text(value).casefold().replace("_", " ").replace("-", " ")
    if normalize_venue_track(track) == "Workshop" or text in {"workshop", "workshops"}:
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
    name = clean_text(record.get("venue_name") or record.get("venue"))
    acronym = clean_text(record.get("venue_acronym"))
    track = normalize_venue_track(record.get("venue_track"))
    if not name:
        return ""
    label = name
    if acronym:
        label += f" ({acronym})"
    track_words = track.replace("_", " ").title()
    already_named = bool(track_words and re.search(
        rf"\b{re.escape(track_words.rstrip('s'))}s?\b", f"{name} {acronym}", re.I
    ))
    if track and track != "Main" and not already_named:
        label += f" · {track_words}"
    return label


def read_venue_aliases(path: Path = DEFAULT_VENUE_ALIASES_PATH, *, include_evidence: bool = True) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != VENUE_ALIAS_COLUMNS:
            raise ValueError(f"{path} does not have the exact venue alias header")
        rows = [dict(row) for row in reader]
    # Evidence is an additive processed layer; never rewrite curated source rows.
    if include_evidence and path.resolve() == DEFAULT_VENUE_ALIASES_PATH.resolve():
        try:
            from .venue_audit import enrich_aliases
        except ImportError:
            from venue_audit import enrich_aliases
        rows = enrich_aliases(rows)
    return rows


def _canonical_registry(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for index, raw_row in enumerate(rows, start=2):
        if clean_text(raw_row.get("review_status")) != "confirmed":
            continue
        row = {column: clean_text(raw_row.get(column)) for column in VENUE_ALIAS_COLUMNS}
        row["venue_track"] = normalize_venue_track(row["venue_track"])
        venue_id = row["venue_id"]
        if not venue_id:
            raise VenueRegistryError(f"venue alias row {index} is missing venue_id")
        identity = tuple(row[field] for field in (
            "venue_name", "venue_acronym", "venue_type",
        ))
        alias_track = row["venue_track"]
        valid_track = not alias_track or (
            identity[2] == "conference" and alias_track in ALLOWED_VENUE_TRACKS
        )
        if not identity[0] or identity[2] not in ALLOWED_VENUE_TYPES or not valid_track:
            raise VenueRegistryError(f"venue alias row {index} has invalid canonical metadata")
        if identity[2] != "conference" and identity[0] and venue_id.endswith(":main"):
            raise VenueRegistryError(
                f"venue alias row {index} gives a non-conference venue a track suffix"
            )
        current = registry.setdefault(venue_id, {
            "venue_id": venue_id,
            "venue_name": identity[0],
            "venue_acronym": identity[1],
            "venue_type": identity[2],
            # Track is paper metadata. Alias rows may retain a track hint for
            # deterministic legacy resolution, but it is not canonical identity.
            "venue_track": "",
            "aliases": [],
        })
        current_identity = tuple(current[field] for field in (
            "venue_name", "venue_acronym", "venue_type",
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


def canonical_venue_registry(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Return the validated confirmed registry keyed by canonical venue ID."""
    return _canonical_registry(rows)


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
        item["venue_name"].casefold(),
        item["venue_acronym"].casefold(),
        item["venue_track"].casefold(),
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
    for field in ("venue_name", "venue_acronym", "venue_type"):
        supplied = clean_text(record.get(field))
        if field == "venue_type" and supplied.casefold() in {"workshop", "workshops"}:
            supplied = "conference"
        if supplied and supplied != venue[field]:
            raise VenueRegistryError(
                f"{field} conflicts with canonical venue_id {venue['venue_id']!r}"
            )
    return venue


def materialize_canonical_venue_metadata(
    record: Mapping[str, Any],
    aliases: Sequence[Mapping[str, Any]],
    *,
    registry: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Synchronize redundant metadata for an existing confirmed venue ID.

    Venue identity is never inferred here: the supplied ID must already exist in
    the confirmed registry. Conference track is intentionally paper-level
    metadata, while the registry remains authoritative for name, acronym, and
    type. Missing conference tracks normalize to ``main``; trackless venue types
    always materialize an empty track.
    """
    result = dict(record)
    identifier = clean_text(result.get("venue_id"))
    confirmed_registry = registry or canonical_venue_registry(aliases)
    stored = confirmed_registry.get(identifier)
    if stored is None:
        raise VenueRegistryError(f"venue_id does not exist: {identifier!r}")
    venue = dict(stored)
    venue["venue_label"] = display_venue(venue)
    if venue["venue_type"] == "conference":
        _venue_type, paper_track = validate_venue_type_track(
            venue["venue_type"], clean_text(result.get("venue_track")) or "Main"
        )
    else:
        paper_track = ""
    raw_venue = result.get("raw_venue") or ""
    result.update(venue)
    result["venue_track"] = paper_track
    result.pop("aliases", None)
    result["raw_venue"] = raw_venue
    result["venue_aliases"] = list(venue.get("aliases", []))
    result["venue"] = venue["venue_name"]
    result["venue_label"] = display_venue(result)
    result["ambiguity_status"] = "resolved"
    return result


def materialize_existing_venue_id(
    record: Mapping[str, Any],
    aliases: Sequence[Mapping[str, Any]],
    *,
    registry: Mapping[str, Mapping[str, Any]] | None = None,
    catalog: tuple[
        dict[str, list[dict[str, str]]], dict[str, tuple[str, ...]]
    ] | None = None,
) -> dict[str, Any]:
    """Materialize a confirmed ID or migrate an exact legacy placeholder.

    Arbitrary dangling and ambiguous IDs remain hard errors. The only removable
    legacy ID is the old deterministic resolver ID reproduced exactly from the
    row's own raw venue while still classified as unconfirmed/unmapped.
    """
    result = dict(record)
    identifier = clean_text(result.get("venue_id"))
    if not identifier:
        return result
    confirmed = registry or canonical_venue_registry(aliases)
    if identifier in confirmed:
        return materialize_canonical_venue_metadata(
            result, aliases, registry=confirmed
        )
    resolved = resolve_venue(
        result.get("raw_venue") or result.get("venue_name") or result.get("venue"),
        publication_type=result.get("publication_type"),
        venue_type=result.get("venue_type"),
        aliases=aliases,
        catalog=catalog,
    )
    if resolved.venue_id in confirmed and resolved.ambiguity_status == "resolved":
        result["venue_id"] = resolved.venue_id
        return materialize_canonical_venue_metadata(
            result, aliases, registry=confirmed
        )
    if (
        resolved.venue_id == identifier
        and resolved.ambiguity_status == "unmapped"
        and clean_text(result.get("raw_venue") or result.get("venue"))
    ):
        for field in (
            "venue_id", "venue_name", "venue_acronym", "venue_type",
            "venue_track", "venue_aliases", "venue_label",
        ):
            result.pop(field, None)
        result["venue"] = clean_text(result.get("raw_venue") or result.get("venue"))
        return result
    raise VenueRegistryError(f"venue_id does not exist: {identifier!r}")


def validate_venue_type_track(venue_type: Any, track: Any) -> tuple[str, str]:
    """Return a compatible canonical type/track pair."""
    normalized_type = normalize_venue_type(venue_type)
    normalized_track = normalize_venue_track(track)
    if normalized_type not in ALLOWED_VENUE_TYPES:
        raise VenueRegistryError("venue_type is invalid")
    if normalized_type in TRACKLESS_VENUE_TYPES:
        if normalized_track:
            raise VenueRegistryError(
                f"{normalized_type} venues cannot have conference tracks"
            )
        return normalized_type, ""
    if normalized_track not in ALLOWED_VENUE_TRACKS:
        raise VenueRegistryError("venue_track is invalid")
    return normalized_type, normalized_track


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
    track = normalize_venue_track(draft.get("venue_track"))
    raw_alias = clean_text(draft.get("raw_alias") or draft.get("raw_venue"))
    # An explicit paper track wins. A workshop in the venue's own name is not
    # evidence that it is a workshop track of a different conference.
    review_note = clean_text(draft.get("review_note"))
    if not name:
        raise VenueRegistryError("canonical full name is required")
    if venue_type not in ALLOWED_VENUE_TYPES:
        raise VenueRegistryError("venue type is invalid")
    if venue_type == "conference":
        try:
            from .venue_evidence import stable_event
        except ImportError:
            from venue_evidence import stable_event
        name, _source_acronym = stable_event(name)
        if re.search(r"lecture notes|\bLNCS\b|\bCCIS\b|transactions on computational science|\bvolume\b", name, re.I):
            raise VenueRegistryError("select the underlying scholarly event, not a proceedings/book series")
    venue_type, track = validate_venue_type_track(
        venue_type, track or ("Main" if venue_type == "conference" else "")
    )
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
        if alias_key(name) in {alias_key(venue["venue_name"]), alias_key(venue["venue_acronym"])}
    ), None)
    if duplicate_name:
        raise VenueRegistryError(
            f"canonical name duplicates existing venue {duplicate_name['venue_id']!r}"
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
    venue_id = _stable_id(name, "")
    if venue_id in registry:
        base_id = venue_id
        digest = hashlib.sha256(
            f"{name}|{venue_type}".encode("utf-8")
        ).hexdigest()
        for offset in range(0, len(digest), 8):
            candidate = f"{base_id}-{digest[offset:offset + 8]}"
            if candidate not in registry:
                venue_id = candidate
                break
        else:
            raise VenueRegistryError(
                f"canonical ID collision could not be resolved for {base_id!r}"
            )
    aliases_to_add = list(dict.fromkeys([name, raw_alias]))
    new_rows = [
        {
            "alias": alias,
            "venue_id": venue_id,
            "venue_name": name,
            "venue_acronym": acronym,
            "venue_type": venue_type,
            "venue_track": "",
            "review_status": "confirmed",
            "notes": review_note or "Created through reviewed Admin canonical venue workflow.",
        }
        for alias in aliases_to_add
    ]
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=VENUE_ALIAS_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows([*read_venue_aliases(path, include_evidence=False), *new_rows])
    temporary.replace(path)
    venue = canonical_venue_by_id(venue_id, [*rows, *new_rows])
    return {**venue, "paper_venue_track": track, "aliases": aliases_to_add, "possible_matches": possible_matches}


def resolve_or_create_canonical_venue(
    draft: Mapping[str, Any],
    path: Path = DEFAULT_VENUE_ALIASES_PATH,
) -> dict[str, Any]:
    """Resolve an exact canonical identity or explicitly create it.

    Exact matching is deliberately punctuation/case/whitespace insensitive and
    covers canonical names, acronyms, and reviewed aliases. Near matches remain
    reviewable and are never merged automatically.
    """
    name = clean_text(draft.get("venue_name"))
    acronym = clean_text(draft.get("venue_acronym"))
    raw_alias = clean_text(draft.get("raw_alias") or draft.get("raw_venue") or name)
    if not name:
        raise VenueRegistryError("venue_name is required")
    rows = read_venue_aliases(path)
    registry = _canonical_registry(rows)
    requested_type, requested_track = validate_venue_type_track(
        draft.get("venue_type"),
        draft.get("venue_track")
        or ("Main" if normalize_venue_type(draft.get("venue_type")) == "conference" else ""),
    )
    query_keys = {
        alias_key(value) for value in (name, acronym, raw_alias) if alias_key(value)
    }
    exact_ids = {
        venue["venue_id"]
        for venue in registry.values()
        if query_keys
        & {
            alias_key(value)
            for value in (
                venue["venue_name"],
                venue["venue_acronym"],
                *venue.get("aliases", []),
            )
            if alias_key(value)
        }
    }
    if len(exact_ids) > 1:
        error = VenueRegistryError("venue proposal matches multiple canonical venues")
        error.possible_matches = [  # type: ignore[attr-defined]
            {**registry[venue_id], "venue_label": display_venue(registry[venue_id])}
            for venue_id in sorted(exact_ids)
        ]
        raise error
    if exact_ids:
        venue = dict(registry[next(iter(exact_ids))])
        if venue["venue_type"] != requested_type:
            raise VenueRegistryError(
                "existing venue match conflicts with the proposed venue type"
            )
        return {
            **venue,
            "paper_venue_track": requested_track,
            "venue_label": display_venue(venue),
            "resolution_action": "resolved_to_existing",
            "created": False,
        }
    if draft.get("create_if_missing") is not True:
        raise VenueRegistryError(
            "venue is unresolved; set create_if_missing=true after explicit review"
        )
    venue = create_canonical_venue(
        {
            **draft,
            "venue_name": name,
            "venue_acronym": acronym,
            "venue_type": requested_type,
            "venue_track": requested_track,
            "raw_alias": raw_alias,
        },
        path=path,
    )
    return {
        **venue,
        "paper_venue_track": requested_track,
        "resolution_action": "created_missing_canonical_venue",
        "created": True,
    }


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


def _track_from_text(value: str, canonical_name: str = "") -> str:
    lowered = value.casefold()
    if re.search(r"\bshort[ -]papers?\b", lowered):
        return "Short Paper"
    if re.search(r"\btutorials?\b", lowered):
        return "Tutorial"
    if re.search(r"\bchallenge\s+track\b", lowered):
        return "Challenge"
    if re.search(r"\bfindings\b", lowered):
        return "Findings"
    if re.search(r"\bposters?\b", lowered):
        return "Poster"
    if re.search(r"\bindustry\s+track\b", lowered):
        return "Industry"
    if re.search(r"\b(?:demo|demonstration)\s+track\b", lowered):
        return "Demo"
    if re.search(r"\bdoctoral\s+consortium\b", lowered):
        return "Doctoral Consortium"
    if canonical_name and re.search(r"\bworkshops?\b", lowered) and not re.search(r"\bworkshops?\b", canonical_name, re.I):
        return "Workshop"
    return "Main"


def _stable_id(name: str, track: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()).strip("-")
    if not slug:
        slug = hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]
    # Unconfirmed legacy placeholders must remain reproducible for migration;
    # confirmed canonical IDs are created with no track suffix.
    legacy_track = {"Workshop": "workshops", "Poster": "posters"}.get(track, track.lower().replace(" ", "_"))
    return f"venue:{slug}:{legacy_track}" if track else f"venue:{slug}"


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
            normalized_row["venue_track"] = normalize_venue_track(normalized_row["venue_track"])
            if normalized_row not in by_alias.setdefault(key, []):
                by_alias[key].append(normalized_row)
            for canonical_value in (row.get("venue_name"), row.get("venue_acronym")):
                canonical_key = alias_key(canonical_value)
                if canonical_key and canonical_key != key:
                    canonical_row = {**normalized_row, "venue_track": ""}
                    if canonical_row not in by_alias.setdefault(canonical_key, []):
                        by_alias[canonical_key].append(canonical_row)
        venue_id = clean_text(row.get("venue_id"))
        if venue_id and alias:
            aliases_by_id.setdefault(venue_id, []).append(alias)
    return by_alias, {key: tuple(dict.fromkeys(values)) for key, values in aliases_by_id.items()}


def _known_lookup_keys(raw: str) -> list[str]:
    cleaned = _strip_edition_noise(raw)
    candidates = [raw, cleaned]
    candidates.extend(_icassp_lookup_variants(cleaned))
    candidates.extend(_acronym_prefixed_lookup_variants(cleaned))
    # Only remove numeric proceedings volumes for the series where the suffix is
    # known not to be part of the venue identity.
    if re.search(r"Advances in Neural Information Processing Systems\s+\d+\s*$", cleaned, re.I):
        candidates.append(re.sub(r"\s+\d+\s*$", "", cleaned))
    # ACM MM proceedings commonly encode only the yearly edition in this prefix.
    candidates.append(re.sub(r"^\d+(?:st|nd|rd|th)\s+", "", cleaned, flags=re.I))
    # Edition years and tracks never identify a distinct canonical venue. Keep
    # this exact-match only: stripping noise is not fuzzy identity inference.
    stable = re.sub(r"\b(?:19|20)\d{2}\b", "", cleaned)
    if re.search(r"conference|symposium|congress|meeting|\b(?:ECCV|CVPR|ICCV|WACV|BMVC|ICIAP|NeurIPS|ICLR|IJCNN|ICMR)\b", stable, re.I):
        stable = re.sub(r"\s+(?:Workshops?|Findings|Posters?|Main Track)\s*$", "", stable, flags=re.I)
    stable = re.sub(r"\s*\([A-Za-z][A-Za-z0-9&. -]{1,20}\)\s*$", "", stable)
    candidates.append(clean_text(stable))
    return list(dict.fromkeys(alias_key(candidate) for candidate in candidates if candidate))


def _acronym_prefixed_lookup_variants(value: str) -> list[str]:
    match = re.match(
        r"^\s*([A-Z][A-Z0-9&.-]{1,15})\s*(?:[-:]\s*)"
        r"(?:(?:19|20)\d{2}\s+)?(.+?)\s*$",
        value,
    )
    if not match:
        return []
    acronym = match.group(1)
    rest = clean_text(match.group(2))
    if not rest:
        return []
    without_suffix = re.sub(
        rf"\s*\({re.escape(acronym)}\)\s*$",
        "",
        rest,
        flags=re.I,
    )
    return [rest, without_suffix, f"{without_suffix} ({acronym})"]


def _icassp_lookup_variants(value: str) -> list[str]:
    if not re.search(r"\bICASSP\b|Acoustics,?\s+Speech\s+and\s+Signal\s+Processing", value, re.I):
        return []
    base = "IEEE International Conference on Acoustics, Speech and Signal Processing"
    no_comma = "IEEE International Conference on Acoustics Speech and Signal Processing"
    variants = [base, no_comma, f"{base} (ICASSP)", f"{no_comma} (ICASSP)"]
    without_prefix = re.sub(
        r"^\s*ICASSP\s+(?:19|20)\d{2}\s*[-:]\s*(?:(?:19|20)\d{2}\s+)?",
        "",
        value,
        flags=re.I,
    )
    without_year = re.sub(r"^\s*(?:19|20)\d{2}\s+", "", without_prefix)
    without_acronym_suffix = re.sub(r"\s*\(ICASSP\)\s*$", "", without_year, flags=re.I)
    variants.extend([without_prefix, without_year, without_acronym_suffix])
    return [clean_text(variant) for variant in variants if clean_text(variant)]


def resolve_venue(
    raw_venue: Any,
    *,
    publication_type: Any = "",
    venue_type: Any = "",
    aliases: Sequence[Mapping[str, Any]] | None = None,
    catalog: tuple[
        dict[str, list[dict[str, str]]], dict[str, tuple[str, ...]]
    ] | None = None,
) -> CanonicalVenue:
    source_raw = str(raw_venue or "")
    raw = clean_text(raw_venue)
    if not raw:
        resolved_type = normalize_venue_type(
            venue_type,
            publication_type=publication_type,
        )
        track = "Main" if resolved_type == "conference" else ""
        return CanonicalVenue(
            "",
            "",
            "",
            resolved_type,
            track,
            "",
            (),
            "unresolved",
        )
    rows = list(aliases) if aliases is not None else read_venue_aliases()
    by_alias, aliases_by_id = catalog or _catalog_index(rows)
    inferred_type = normalize_venue_type(
        venue_type, publication_type=publication_type
    )
    track = _track_from_text(raw) if inferred_type == "conference" else ""
    # An exact standalone identity takes precedence over stripped parent hints.
    matches = by_alias.get(alias_key(raw), []) or [row for key in _known_lookup_keys(raw) for row in by_alias.get(key, [])]
    unique_ids = {row["venue_id"] for row in matches}
    if len(unique_ids) > 1:
        return CanonicalVenue(_stable_id(raw, track), raw, "", normalize_venue_type(venue_type, publication_type=publication_type, track=track), track, raw, (), "ambiguous")
    if matches:
        row = matches[0]
        canonical_type = normalize_venue_type(row["venue_type"] or venue_type, publication_type=publication_type)
        canonical_track = (normalize_venue_track(row["venue_track"]) or _track_from_text(raw, row["venue_name"])) if canonical_type == "conference" else ""
        return CanonicalVenue(row["venue_id"], row["venue_name"], row["venue_acronym"], canonical_type, canonical_track, source_raw, aliases_by_id.get(row["venue_id"], ()))

    cleaned = _strip_edition_noise(raw)
    detected_track = (
        _track_from_text(cleaned)
        if normalize_venue_type(venue_type, publication_type=publication_type)
        == "conference"
        else ""
    )
    parenthetical = re.search(r"\s*\(([A-Za-z][A-Za-z0-9&.-]{1,15})\)\s*(?:Workshops?|Findings)?\s*$", cleaned)
    acronym = ""
    name = cleaned
    if parenthetical and re.search(r"[A-Z]", parenthetical.group(1)):
        acronym = parenthetical.group(1)
        name = clean_text(cleaned[: parenthetical.start()] + cleaned[parenthetical.end():])
    # Unverified Workshop words may be part of the event's own identity.
    name = re.sub(r"\s+(?:Findings|Posters?|Industry Track|Demo(?:nstration)? Track|Doctoral Consortium)\s*$", "", name, flags=re.I)
    name = clean_text(name)
    resolved_type = normalize_venue_type(venue_type, publication_type=publication_type, track=detected_track)
    return CanonicalVenue(_stable_id(name, detected_track), name, acronym, resolved_type, detected_track, source_raw, (source_raw,), "unmapped")


def canonicalize_record(
    record: Mapping[str, Any],
    aliases: Sequence[Mapping[str, Any]] | None = None,
    *,
    registry: Mapping[str, Mapping[str, Any]] | None = None,
    catalog: tuple[
        dict[str, list[dict[str, str]]], dict[str, tuple[str, ...]]
    ] | None = None,
) -> dict[str, Any]:
    result = dict(record)
    resolved_aliases = list(aliases) if aliases is not None else read_venue_aliases()
    existing_id = clean_text(result.get("venue_id"))
    confirmed_registry = registry or canonical_venue_registry(resolved_aliases)
    if existing_id:
        result = materialize_existing_venue_id(
            result,
            resolved_aliases,
            registry=confirmed_registry,
            catalog=catalog,
        )
        effective_type, _rule = resolve_publication_type(
            result.get("publication_type"),
            venue=result.get("venue_name"),
            venue_type=result.get("venue_type"),
            arxiv_id=result.get("arxiv_id"),
            arxiv_url=result.get("arxiv_url"),
            doi=result.get("doi"),
            explicit_override=result.get("publication_type_override") is True,
        )
        if effective_type:
            result["publication_type"] = effective_type
        return result
    source = result.get("raw_venue") or result.get("venue_name") or result.get("venue")
    venue = resolve_venue(
        source,
        publication_type=result.get("publication_type"),
        venue_type=result.get("venue_type"),
        aliases=resolved_aliases,
        catalog=catalog,
    )
    result.update(venue.as_record())
    result.pop("aliases", None)
    result["venue"] = venue.venue_name
    result["venue_label"] = display_venue(result)
    if venue.ambiguity_status == "unmapped" and venue.venue_id:
        # The existing-ID path retires these unconfirmed placeholders. Apply
        # that same policy immediately, otherwise repeated exports alternate
        # between a generated ID and raw source text on every pass.
        result = materialize_existing_venue_id(
            result, resolved_aliases, registry=confirmed_registry, catalog=catalog,
        )
    effective_type, _rule = resolve_publication_type(
        result.get("publication_type"),
        venue=result.get("venue_name") or result.get("venue"),
        venue_type=result.get("venue_type"),
        arxiv_id=result.get("arxiv_id"),
        arxiv_url=result.get("arxiv_url"),
        doi=result.get("doi"),
        explicit_override=result.get("publication_type_override") is True,
    )
    if effective_type:
        result["publication_type"] = effective_type
    return result


def canonicalize_records(records: Iterable[Mapping[str, Any]], aliases: Sequence[Mapping[str, Any]] | None = None) -> list[dict[str, Any]]:
    resolved_aliases = list(aliases) if aliases is not None else read_venue_aliases()
    try:
        from .venue_audit import VenueAudit
    except ImportError:
        from venue_audit import VenueAudit
    audit = VenueAudit(resolved_aliases)
    return [audit.effective(record) for record in records]
