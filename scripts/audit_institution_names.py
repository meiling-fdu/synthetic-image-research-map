#!/usr/bin/env python3
"""Audit and apply conservative English canonical institution-name updates."""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

try:
    from .curated_institutions import alias_id_for, clean
    from .curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_COLUMNS,
        REPOSITORY_ROOT,
    )
    from .name_matching import canonical_name_key
except ImportError:
    from curated_institutions import alias_id_for, clean
    from curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        CURATED_DATA_DIR,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_COLUMNS,
        REPOSITORY_ROOT,
    )
    from name_matching import canonical_name_key


DEFAULT_REPORT_PATH = REPOSITORY_ROOT / "data" / "processed" / "institution_name_english_audit.csv"
DEFAULT_INSTITUTIONS_PATH = CURATED_DATA_DIR / "institutions.csv"
DEFAULT_ALIASES_PATH = CURATED_DATA_DIR / "institution_aliases.csv"
DEFAULT_MAPPINGS_PATH = CURATED_DATA_DIR / "author_institution_mappings.csv"

REPORT_COLUMNS = (
    "institution_id",
    "country",
    "old_canonical_name",
    "proposed_english_name",
    "final_canonical_name",
    "official_english_evidence",
    "source",
    "confidence",
    "aliases_before",
    "aliases_added",
    "review_required",
    "applied",
    "notes",
)

NON_LATIN_SCRIPT_PATTERN = re.compile(
    "["
    "\u0370-\u03ff"  # Greek
    "\u0400-\u052f"  # Cyrillic
    "\u0590-\u05ff"  # Hebrew
    "\u0600-\u06ff"  # Arabic/Persian
    "\u0900-\u097f"  # Devanagari
    "\u0e00-\u0e7f"  # Thai
    "\u3040-\u30ff"  # Japanese
    "\u3130-\u318f"  # Hangul compatibility
    "\uac00-\ud7af"  # Hangul
    "\u4e00-\u9fff"  # CJK
    "]"
)

LOCAL_NAME_HINTS = (
    "universidade",
    "universidad",
    "université",
    "universita",
    "università",
    "universität",
    "instituto",
    "institut polytechnique",
    "technische universität",
    "sorbonne université",
    "humboldt-universität",
    "politécnica",
)

HIGH_CONFIDENCE_RENAMES: Dict[str, Dict[str, str]] = {
    "institution:2e62680df0fed751": {
        "previous": "Huawei Noah’s Ark Lab",
        "name": "Huawei Noah's Ark Lab",
        "source": "existing confirmed alias",
        "evidence": "Confirmed alias row preserves ASCII English punctuation variant for the same institution_id.",
        "reason": "Official English lab name with ASCII apostrophe; previous smart-apostrophe form is retained as an alias.",
    },
    "institution:0aed8b5908ebcd25": {
        "previous": "Instituto de Matemática Pura e Aplicada",
        "name": "Institute for Pure and Applied Mathematics (IMPA)",
        "source": "repository location evidence",
        "evidence": "Curated location review records IMPA and the official institute page as evidence.",
        "reason": "Established English expansion of IMPA; Portuguese canonical form is retained as an alias.",
    },
    "institution:c76018a960d2cd12": {
        "previous": "Université de Lille",
        "name": "University of Lille",
        "source": "repository official English contact URL",
        "evidence": "Institution location uses the official English maps-and-contacts URL for Université de Lille.",
        "reason": "English-facing institutional rendering is available in curated location evidence.",
    },
    "institution:6c246ba350e11d5f": {
        "previous": "Université de Rennes",
        "name": "University of Rennes",
        "source": "repository affiliation and location evidence",
        "evidence": "Curated mappings and location review preserve Univ. Rennes affiliation evidence for the same ID.",
        "reason": "English rendering of the university name; French canonical form is retained as an alias.",
    },
    "institution:0c5e25ec47ce33fe": {
        "previous": "Université Paris-Saclay",
        "name": "Paris-Saclay University",
        "source": "structured English rendering",
        "evidence": "Known English institutional rendering for Université Paris-Saclay; old canonical name remains an alias.",
        "reason": "Official English-style rendering is widely used and unambiguous for this ID.",
    },
    "institution:d09040aba5fecf8e": {
        "previous": "Université Polytechnique Hauts-de-France",
        "name": "Polytechnic University of Hauts-de-France",
        "source": "existing canonical English counterpart",
        "evidence": "The repository already contains a confirmed alias from this French name to Polytechnic University of Hauts-de-France.",
        "reason": "Use the existing repository English canonical spelling while preserving the original French name.",
    },
    "institution:14daf7f722d7d91d": {
        "previous": "Universidade Estadual de Campinas (UNICAMP)",
        "name": "University of Campinas",
        "source": "existing confirmed English institution record",
        "evidence": "The repository already confirms University of Campinas / Universidade Estadual de Campinas / UNICAMP.",
        "reason": "Use the established English rendering while preserving Portuguese and acronym forms as aliases.",
    },
    "institution:475fa3f7d32d5d27": {
        "previous": "Institut polytechnique de Grenoble",
        "name": "Grenoble INP",
        "source": "existing canonical English-brand counterpart",
        "evidence": "The repository already contains Grenoble INP as an active canonical institution name.",
        "reason": "Use the English-facing institutional brand and retain the French legal name as an alias.",
    },
    "institution:e0677ab73955e8f3": {
        "previous": "Sorbonne Université",
        "name": "Sorbonne University",
        "source": "existing canonical English counterpart",
        "evidence": "The repository already contains Sorbonne University as an active canonical institution name.",
        "reason": "Use the English rendering while retaining Sorbonne Université as an alias.",
    },
    "institution:f8894017df3dfcc2": {
        "previous": "Ollscoil na Gaillimhe – University of Galway",
        "name": "University of Galway",
        "source": "canonical bilingual name",
        "evidence": "Current canonical name already includes University of Galway alongside the Irish-language form.",
        "reason": "Remove the Irish-language prefix from canonical display and preserve the bilingual name as an alias.",
    },
    "institution:35f84ec19dab5880": {
        "previous": "Computer Research Institute of Montréal",
        "name": "Computer Research Institute of Montreal",
        "source": "English rendering with local-place diacritic removed",
        "evidence": "Current canonical name is already English except the place-name diacritic.",
        "reason": "Standardize the English canonical display while retaining the Montréal spelling as an alias.",
    },
    "institution:bbc6ae7ed9b4bd38": {
        "previous": "Humboldt-Universität zu Berlin",
        "name": "Humboldt University of Berlin",
        "source": "structured English rendering",
        "evidence": "English rendering preserves identity and location for Humboldt-Universität zu Berlin.",
        "reason": "Use the standard English form and retain the German official name as an alias.",
    },
}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path, columns: Sequence[str] | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if columns and tuple(reader.fieldnames or ()) != tuple(columns):
            raise RuntimeError(f"{path} has an unexpected CSV header")
        return [dict(row) for row in reader]


def write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def normalized_alias_key(value: Any) -> str:
    return " ".join(unicodedata.normalize("NFKC", clean(value)).casefold().split())


def contains_non_latin_script(value: str) -> bool:
    return bool(NON_LATIN_SCRIPT_PATTERN.search(value))


def has_local_latin_hint(value: str) -> bool:
    folded = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").casefold()
    return any(hint in folded for hint in LOCAL_NAME_HINTS)


def country_by_institution(locations: Sequence[Mapping[str, str]]) -> dict[str, str]:
    countries: dict[str, str] = {}
    for row in locations:
        institution_id = clean(row.get("institution_id"))
        if institution_id and institution_id not in countries:
            countries[institution_id] = clean(row.get("country"))
    return countries


def aliases_by_institution(aliases: Sequence[Mapping[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in aliases:
        grouped[clean(row.get("institution_id"))].append(dict(row))
    return grouped


def aliases_for_report(rows: Sequence[Mapping[str, str]]) -> str:
    return "; ".join(clean(row.get("alias_name")) for row in rows if clean(row.get("alias_name")))


def unique_names(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        name = clean(value)
        key = normalized_alias_key(name)
        if name and key and key not in seen:
            seen.add(key)
            result.append(name)
    return result


def build_report(
    institutions: Sequence[Mapping[str, str]],
    aliases: Sequence[Mapping[str, str]],
    locations: Sequence[Mapping[str, str]] = (),
    mappings: Sequence[Mapping[str, str]] = (),
) -> list[dict[str, str]]:
    countries = country_by_institution(locations)
    grouped_aliases = aliases_by_institution(aliases)
    canonical_counts = Counter(
        normalized_alias_key(row.get("canonical_name"))
        for row in institutions
        if clean(row.get("institution_status")) == "active"
    )
    rows: list[dict[str, str]] = []
    for row in institutions:
        if clean(row.get("institution_status")) != "active":
            continue
        institution_id = clean(row.get("institution_id"))
        current_name = clean(row.get("canonical_name"))
        proposal = HIGH_CONFIDENCE_RENAMES.get(institution_id, {})
        proposed = clean(proposal.get("name"))
        previous_name = clean(proposal.get("previous"))
        applied_previous_migration = bool(
            proposed and previous_name and current_name == proposed
        )
        old_name = previous_name if applied_previous_migration else current_name
        aliases_before = grouped_aliases.get(institution_id, [])
        stale_mapping_count = sum(
            1
            for mapping in mappings
            if clean(mapping.get("institution_id")) == institution_id
            and clean(mapping.get("institution"))
            and clean(mapping.get("institution")) != (proposed or current_name)
        )
        reasons = []
        review_required = "false"
        confidence = "already_english"
        if applied_previous_migration:
            confidence = "applied"
            reasons.append(proposal.get("reason", "High-confidence repository-backed English name."))
        elif proposed and proposed != old_name:
            confidence = "high"
            reasons.append(proposal.get("reason", "High-confidence repository-backed English name."))
        elif contains_non_latin_script(current_name):
            confidence = "review"
            review_required = "true"
            reasons.append("Canonical name contains a non-Latin script.")
        elif has_local_latin_hint(current_name):
            confidence = "review"
            review_required = "true"
            reasons.append("Canonical name contains a local-language Latin-script cue.")
        elif any(ord(char) > 127 for char in current_name):
            confidence = "review"
            review_required = "true"
            reasons.append("Canonical name contains non-ASCII characters; confirm official English branding before changing.")
        if canonical_counts[normalized_alias_key(proposed or current_name)] > 1:
            reasons.append("Duplicate canonical name after English normalization; keep institution_id as identity.")
        if stale_mapping_count:
            reasons.append(f"{stale_mapping_count} mapping display name(s) differ from the target canonical name.")
        if proposed == current_name and not applied_previous_migration:
            proposed = ""
        aliases_added = unique_names([old_name]) if proposed else []
        rows.append({
            "institution_id": institution_id,
            "country": countries.get(institution_id, ""),
            "old_canonical_name": old_name,
            "proposed_english_name": proposed,
            "final_canonical_name": proposed or current_name,
            "official_english_evidence": clean(proposal.get("evidence")),
            "source": clean(proposal.get("source")) if proposal else "",
            "confidence": confidence,
            "aliases_before": aliases_for_report(aliases_before),
            "aliases_added": "; ".join(aliases_added),
            "review_required": review_required,
            "applied": "true" if applied_previous_migration else "false",
            "notes": " ".join(reason for reason in reasons if reason),
        })
    return rows


def add_alias_rows(
    aliases: list[dict[str, str]],
    institution_id: str,
    canonical_name: str,
    alias_names: Sequence[str],
) -> list[str]:
    existing_keys = {
        (clean(row.get("institution_id")), normalized_alias_key(row.get("alias_name")))
        for row in aliases
    }
    added: list[str] = []
    for alias_name in unique_names(alias_names):
        key = (institution_id, normalized_alias_key(alias_name))
        if not key[1] or key in existing_keys or normalized_alias_key(alias_name) == normalized_alias_key(canonical_name):
            continue
        aliases.append({
            "alias_id": alias_id_for(alias_name),
            "alias_name": alias_name,
            "institution_id": institution_id,
            "canonical_institution_name": canonical_name,
            "alias_language": "",
            "alias_source": "english-name-migration",
            "review_status": "confirmed",
            "notes": "Previous canonical institution name retained during English canonical-name migration.",
        })
        existing_keys.add(key)
        added.append(alias_name)
    return added


def apply_high_confidence(
    institutions: list[dict[str, str]],
    aliases: list[dict[str, str]],
    mappings: list[dict[str, str]],
    report_rows: list[dict[str, str]],
) -> tuple[int, int]:
    proposed_by_id = {
        row["institution_id"]: row
        for row in report_rows
        if row["confidence"] == "high" and row["proposed_english_name"]
    }
    updated_names = 0
    updated_mappings = 0
    now = utc_timestamp()
    for row in institutions:
        institution_id = clean(row.get("institution_id"))
        proposal = proposed_by_id.get(institution_id)
        if not proposal:
            continue
        old_name = clean(row.get("canonical_name"))
        new_name = proposal["proposed_english_name"]
        if old_name == new_name:
            continue
        added = add_alias_rows(aliases, institution_id, new_name, [old_name])
        row["canonical_name"] = new_name
        row["updated_at"] = now
        for alias in aliases:
            if clean(alias.get("institution_id")) == institution_id:
                alias["canonical_institution_name"] = new_name
        for mapping in mappings:
            if clean(mapping.get("institution_id")) == institution_id and clean(mapping.get("institution")) != new_name:
                mapping["institution"] = new_name
                mapping["updated_at"] = now
                updated_mappings += 1
        proposal["final_canonical_name"] = new_name
        proposal["aliases_added"] = "; ".join(added)
        proposal["applied"] = "true"
        updated_names += 1
    return updated_names, updated_mappings


def duplicate_canonical_names(institutions: Sequence[Mapping[str, str]]) -> dict[str, list[str]]:
    by_name: dict[str, list[str]] = defaultdict(list)
    display: dict[str, str] = {}
    for row in institutions:
        if clean(row.get("institution_status")) != "active":
            continue
        key = normalized_alias_key(row.get("canonical_name"))
        if not key:
            continue
        by_name[key].append(clean(row.get("institution_id")))
        display[key] = clean(row.get("canonical_name"))
    return {display[key]: ids for key, ids in by_name.items() if len(ids) > 1}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Write the deterministic audit report without mutating curated CSVs.")
    parser.add_argument("--apply-high-confidence", action="store_true", help="Apply only built-in high-confidence English-name proposals.")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--institutions", type=Path, default=DEFAULT_INSTITUTIONS_PATH)
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES_PATH)
    parser.add_argument("--mappings", type=Path, default=DEFAULT_MAPPINGS_PATH)
    parser.add_argument("--locations", type=Path, default=CURATED_DATA_DIR / "institution_locations.csv")
    args = parser.parse_args(argv)
    if args.check and args.apply_high_confidence:
        parser.error("--check and --apply-high-confidence are mutually exclusive")

    institutions = read_csv(args.institutions, INSTITUTION_COLUMNS)
    aliases = read_csv(args.aliases, INSTITUTION_ALIAS_COLUMNS)
    mappings = read_csv(args.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
    locations = read_csv(args.locations)
    report_rows = build_report(institutions, aliases, locations, mappings)
    updated_names = 0
    updated_mappings = 0
    if args.apply_high_confidence:
        updated_names, updated_mappings = apply_high_confidence(institutions, aliases, mappings, report_rows)
        write_csv(args.institutions, INSTITUTION_COLUMNS, institutions)
        write_csv(args.aliases, INSTITUTION_ALIAS_COLUMNS, aliases)
        write_csv(args.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, mappings)
        report_rows = build_report(institutions, aliases, locations, mappings)
        for row in report_rows:
            proposal = HIGH_CONFIDENCE_RENAMES.get(row["institution_id"])
            if proposal and row["old_canonical_name"] == proposal["name"]:
                row["applied"] = "true"

    report_rows = sorted(report_rows, key=lambda row: (row["review_required"] != "true", row["country"], row["old_canonical_name"], row["institution_id"]))
    write_csv(args.output, REPORT_COLUMNS, report_rows)
    active_count = sum(1 for row in institutions if clean(row.get("institution_status")) == "active")
    review_count = sum(1 for row in report_rows if row["review_required"] == "true")
    high_count = sum(1 for row in report_rows if row["confidence"] == "high")
    duplicates = duplicate_canonical_names(institutions)
    print(f"Active canonical institutions: {active_count}")
    print(f"High-confidence proposals: {high_count}")
    print(f"Applied institution renames: {updated_names}")
    print(f"Mapping display names updated: {updated_mappings}")
    print(f"Review candidates: {review_count}")
    print(f"Duplicate English canonical names: {len(duplicates)}")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
