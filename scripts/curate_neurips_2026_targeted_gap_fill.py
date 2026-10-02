#!/usr/bin/env python3
"""Apply the locked NeurIPS 2026 targeted gap-fill reconciliation.

The evidence and decisions are frozen in
``data/manual/neurips_2026_targeted_gap_fill_reconciliation.json``.  This
script adds exactly the seven ``MISSING_ADD`` papers, updates the existing
MIRROR identity in place, and preserves the taskless SalArt-VQA analysis as a
curated record without forcing it into the task-gated public export.
"""

from __future__ import annotations

import csv
import argparse
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from .curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        INSTITUTION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        PAPERS_COLUMNS,
        PAPER_TAXONOMY_COLUMNS,
    )
    from .paper_exclusions import all_identity_keys
except ImportError:
    from curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        INSTITUTION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        PAPERS_COLUMNS,
        PAPER_TAXONOMY_COLUMNS,
    )
    from paper_exclusions import all_identity_keys


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/processed/neurips_2026_targeted_gap_fill_2026_10"
PAYLOAD_PATH = OUT / "curation_payload.json"
PREDECESSOR_PATH = OUT / "predecessor_623_snapshot.json"
RECONCILIATION_PATH = (
    ROOT / "data/manual/neurips_2026_targeted_gap_fill_reconciliation.json"
)
RECEIPT_PATH = OUT / "curation_receipt.json"
BASELINE_DIR = OUT / "baseline"
NOW = "2026-10-01T00:00:00Z"
AUDITED_AT = "2026-10-01"
MIRROR_ID = "curated:8fe7cb0db76df68a5e38"

TARGETS: dict[str, tuple[str, ...]] = {
    "papers.csv": PAPERS_COLUMNS,
    "paper_taxonomy.csv": PAPER_TAXONOMY_COLUMNS,
    "author_institution_mappings.csv": AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    "institutions.csv": INSTITUTION_COLUMNS,
    "institution_location_review.csv": INSTITUTION_LOCATION_REVIEW_COLUMNS,
}


def digest(value: str, *, prefix: str, length: int) -> str:
    return prefix + hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def serialized_row(
    columns: tuple[str, ...], row: Mapping[str, Any], newline: str = "\n"
) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=columns, lineterminator=newline, extrasaction="raise"
    )
    writer.writerow({field: row.get(field, "") for field in columns})
    return buffer.getvalue().encode("utf-8")


def stage_csv_bytes(
    path: Path,
    columns: tuple[str, ...],
    replacements: Mapping[str, Mapping[str, Any]],
    additions: Iterable[Mapping[str, Any]],
) -> bytes:
    """Preserve untouched bytes while replacing keyed rows and appending rows."""
    original = path.read_bytes()
    lines = original.splitlines(keepends=True)
    if not lines:
        raise AssertionError(f"empty CSV: {path}")
    header = next(csv.reader([lines[0].decode("utf-8-sig")]))
    if tuple(header) != columns:
        raise AssertionError(f"unexpected header in {path}: {header}")
    key = columns[0]
    seen: set[str] = set()
    output = [lines[0]]
    for raw in lines[1:]:
        values = next(csv.reader([raw.decode("utf-8")]))
        if len(values) != len(columns):
            raise AssertionError(f"physical multiline CSV row in {path}")
        row = dict(zip(columns, values))
        row_key = row[key]
        replacement = replacements.get(row_key)
        if replacement is None:
            output.append(raw)
            continue
        newline = "\r\n" if raw.endswith(b"\r\n") else "\n"
        output.append(serialized_row(columns, replacement, newline))
        seen.add(row_key)
    missing = set(replacements) - seen
    if missing:
        raise AssertionError(f"replacement rows missing from {path}: {sorted(missing)}")
    if output and not output[-1].endswith((b"\n", b"\r")):
        output.append(b"\n")
    output.extend(serialized_row(columns, row) for row in additions)
    return b"".join(output)


def row_from_columns(columns: tuple[str, ...], **values: Any) -> dict[str, str]:
    row = dict.fromkeys(columns, "")
    row.update({key: str(value) for key, value in values.items()})
    return row


def paper_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {paper["paper_id"]: paper for paper in payload["papers"]}


def validate_locked_reconciliation(payload: Mapping[str, Any]) -> None:
    reconciliation = json.loads(RECONCILIATION_PATH.read_text(encoding="utf-8"))
    records = reconciliation["records"]
    counts: dict[str, int] = {}
    for record in records:
        action = record["final_reconciliation_action"]
        counts[action] = counts.get(action, 0) + 1
    expected = {
        "EXISTING_CURRENT": 0,
        "EXISTING_UPDATE_NEEDED": 1,
        "MISSING_ADD": 7,
        "HOLD_SCOPE": 2,
        "AMBIGUOUS": 7,
        "EXCLUDE": 0,
    }
    if counts != {key: value for key, value in expected.items() if value}:
        raise AssertionError(f"reconciliation decisions changed: {counts}")
    missing_titles = {
        record["canonical_title"]
        for record in records
        if record["final_reconciliation_action"] == "MISSING_ADD"
    }
    payload_titles = {paper["title"] for paper in payload["papers"]}
    if missing_titles != payload_titles:
        raise AssertionError("payload does not exactly match the seven locked additions")
    updates = [
        record
        for record in records
        if record["final_reconciliation_action"] == "EXISTING_UPDATE_NEEDED"
    ]
    if len(updates) != 1 or updates[0]["existing_authoritative_paper_id"] != MIRROR_ID:
        raise AssertionError("MIRROR must be the only in-place update")


def build() -> dict[str, Any]:
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    validate_locked_reconciliation(payload)
    if payload["track"] != "" or payload["venue"]["venue_track"] != "" or len(payload["papers"]) != 7:
        raise AssertionError("unexpected curation payload")

    predecessor = json.loads(PREDECESSOR_PATH.read_text(encoding="utf-8"))
    for relative, expected in predecessor["tracked_pre_gap_fill_sha256"].items():
        if relative.startswith("data/curated/"):
            actual = sha256(ROOT / relative)
            if actual != expected:
                raise AssertionError(
                    f"pre-gap-fill curated baseline changed: {relative}: {actual} != {expected}"
                )

    current = {
        name: read_csv(ROOT / "data/curated" / name) for name in TARGETS
    }
    current_papers = current["papers.csv"]
    current_taxonomy = current["paper_taxonomy.csv"]
    current_mappings = current["author_institution_mappings.csv"]
    current_institutions = current["institutions.csv"]
    current_reviews = current["institution_location_review.csv"]
    papers = paper_by_id(payload)

    if len(current_papers) != 479 or len(current_taxonomy) != 666:
        raise AssertionError("unexpected starting curated paper/taxonomy counts")
    if sum(row["paper_id"] == MIRROR_ID for row in current_papers) != 1:
        raise AssertionError("MIRROR authoritative identity is missing or duplicated")

    existing_identity: set[str] = set()
    public = json.loads((ROOT / "web/data/public_preview_papers.json").read_text())
    for row in [*current_papers, *public["records"]]:
        existing_identity.update(all_identity_keys(row))
    new_identity: set[str] = set()
    for paper in payload["papers"]:
        draft = {
            "paper_id": paper["paper_id"],
            "title": paper["title"],
            "year": payload["year"],
            "arxiv_id": paper["arxiv_id"],
        }
        keys = set(all_identity_keys(draft))
        if keys & existing_identity or keys & new_identity:
            raise AssertionError(f"duplicate paper identity: {paper['title']}")
        new_identity.update(keys)

    venue = payload["venue"]
    paper_additions: list[dict[str, str]] = []
    for paper in payload["papers"]:
        row = row_from_columns(
            PAPERS_COLUMNS,
            paper_id=paper["paper_id"],
            title=paper["title"],
            year=payload["year"],
            authors="; ".join(paper["authors"]),
            doi="",
            arxiv_id=paper["arxiv_id"],
            openalex_url="",
            paper_url=f"https://neurips.cc/virtual/2026/poster/{paper['poster_id']}",
            abstract=paper["abstract"],
            tasks=paper["tasks"],
            image_scopes=paper["image_scopes"],
            research_types=paper["research_types"],
            scope_status="in_scope",
            source_database="manual",
            metadata_source=paper["metadata_source"],
            curation_status="confirmed",
            review_status="reviewed",
            created_at=NOW,
            updated_at=NOW,
            **venue,
        )
        paper_additions.append(row)

    mirror_current = next(row for row in current_papers if row["paper_id"] == MIRROR_ID)
    mirror = dict(mirror_current)
    mirror_update = payload["mirror_update"]
    mirror.update(
        title=mirror_update["title"],
        paper_url=f"https://neurips.cc/virtual/2026/poster/{mirror_update['poster_id']}",
        metadata_source=mirror_update["metadata_source"],
        source_database="manual",
        updated_at=NOW,
        **venue,
    )
    mirror["abstract"] = mirror["abstract"].replace(
        "https://github.com/349793927/MIRROR",
        mirror_update["canonical_code_url"],
    )

    taxonomy_additions: list[dict[str, str]] = []
    for paper in payload["papers"]:
        # The registry covers the task-gated public corpus plus active strong-ID
        # exclusions. SalArt-VQA has no formal repository root task, so keeping
        # it out avoids either a false detection label or an orphan registry row.
        if not paper["tasks"]:
            continue
        evidence = " ".join(paper["abstract"].split())[:1200]
        taxonomy = row_from_columns(
            PAPER_TAXONOMY_COLUMNS,
            taxonomy_id="paper_id:" + paper["paper_id"],
            paper_id=paper["paper_id"],
            title=paper["title"],
            year=payload["year"],
            doi="",
            arxiv_id=paper["arxiv_id"],
            openalex_url="",
            tasks=paper["tasks"],
            image_scopes=paper["image_scopes"],
            research_types=paper["research_types"],
            taxonomy_status="reviewed",
            audited_at=AUDITED_AT,
        )
        for dimension in ("tasks", "image_scopes", "research_types"):
            taxonomy[dimension + "_status"] = "reviewed"
            taxonomy[dimension + "_review_reason"] = paper["curation_notes"]
            taxonomy[dimension + "_evidence_tier"] = (
                "primary_paper+production_listing"
            )
            taxonomy[dimension + "_evidence_source"] = paper["metadata_source"]
            taxonomy[dimension + "_evidence_excerpt"] = evidence
        taxonomy_additions.append(taxonomy)
    if len(taxonomy_additions) != 6:
        raise AssertionError("expected six task-bearing taxonomy additions")

    mirror_taxonomy_current = next(
        row for row in current_taxonomy if row["paper_id"] == MIRROR_ID
    )
    mirror_taxonomy = dict(mirror_taxonomy_current)
    mirror_taxonomy.update(title=mirror_update["title"], audited_at=AUDITED_AT)
    for field in (
        "tasks_evidence_excerpt",
        "image_scopes_evidence_excerpt",
        "research_types_evidence_excerpt",
    ):
        mirror_taxonomy[field] = mirror_taxonomy[field].replace(
            "https://github.com/349793927/MIRROR",
            mirror_update["canonical_code_url"],
        )

    institution_by_id = {row["institution_id"]: row for row in current_institutions}
    institution_by_name = {row["canonical_name"]: row for row in current_institutions}
    institution_additions: list[dict[str, str]] = []
    for institution in payload["new_institutions"]:
        if institution["institution_id"] in institution_by_id:
            raise AssertionError(f"institution ID already exists: {institution}")
        if institution["canonical_name"].casefold() in {
            name.casefold() for name in institution_by_name
        }:
            raise AssertionError(f"institution name already exists: {institution}")
        row = row_from_columns(
            INSTITUTION_COLUMNS,
            **institution,
            institution_status="active",
            parent_institution_id="",
            public_display="self",
            created_at=NOW,
            updated_at=NOW,
            created_by="neurips-2026-targeted-gap-fill",
        )
        institution_additions.append(row)
        institution_by_id[row["institution_id"]] = row

    locations = read_csv(ROOT / "data/curated/institution_locations.csv")
    location_by_institution: dict[str, dict[str, str]] = {}
    for location in locations:
        if location["coordinate_status"] in {"confirmed", "known"}:
            location_by_institution.setdefault(location["institution_id"], location)

    mapping_additions: list[dict[str, str]] = []
    for paper in payload["papers"]:
        author_positions = {name: index for index, name in enumerate(paper["authors"], 1)}
        for affiliation_order, affiliation in enumerate(paper["affiliations"], 1):
            unknown = set(affiliation["authors"]) - set(author_positions)
            if unknown:
                raise AssertionError(
                    f"affiliation authors absent from paper roster: {paper['title']}: {unknown}"
                )
            institution_id = affiliation["institution_id"]
            institution = institution_by_id.get(institution_id)
            if institution is None:
                raise AssertionError(f"unknown institution ID: {institution_id}")
            if institution["canonical_name"] != affiliation["institution"]:
                raise AssertionError(f"institution name mismatch: {affiliation}")
            location = location_by_institution.get(institution_id, {})
            mapping_id = digest(
                paper["paper_id"]
                + ":"
                + institution_id
                + ":"
                + ";".join(affiliation["authors"]),
                prefix="mapping:",
                length=20,
            )
            mapping = row_from_columns(
                AUTHOR_INSTITUTION_MAPPING_COLUMNS,
                mapping_id=mapping_id,
                paper_id=paper["paper_id"],
                title=paper["title"],
                year=payload["year"],
                doi="",
                openalex_url="",
                institution=affiliation["institution"],
                institution_id=institution_id,
                location_id=location.get("location_id", ""),
                institution_authors="; ".join(affiliation["authors"]),
                author_order="; ".join(
                    str(author_positions[name]) for name in affiliation["authors"]
                ),
                affiliation_order=str(affiliation_order),
                raw_affiliation=affiliation["raw_affiliation"],
                institution_city=location.get("city", ""),
                institution_country=location.get("country", ""),
                institution_latitude=location.get("lat", ""),
                institution_longitude=location.get("lon", ""),
                provenance_source=paper["metadata_source"],
                mapping_status="active",
                created_at=NOW,
                updated_at=NOW,
            )
            mapping_additions.append(mapping)

    mirror_mapping_replacements: dict[str, dict[str, str]] = {}
    for mapping in current_mappings:
        if mapping["paper_id"] != MIRROR_ID:
            continue
        updated = dict(mapping)
        updated.update(title=mirror_update["title"], updated_at=NOW)
        mirror_mapping_replacements[mapping["mapping_id"]] = updated
    if len(mirror_mapping_replacements) != 9:
        raise AssertionError("expected nine existing MIRROR affiliation mappings")

    review_additions: list[dict[str, str]] = []
    for review in payload["location_reviews"]:
        paper = papers[review["paper_id"]]
        row = row_from_columns(
            INSTITUTION_LOCATION_REVIEW_COLUMNS,
            institution=review["institution"],
            canonical_institution_name=review["institution"],
            institution_id=review["institution_id"],
            related_paper_id=review["paper_id"],
            title=paper["title"],
            year=payload["year"],
            doi="",
            openalex_url="",
            institution_authors="; ".join(review["authors"]),
            raw_affiliation=review["raw_affiliation"],
            evidence_source=review["evidence_source"],
            evidence_url=review["evidence_url"],
            suggested_city=review["suggested_city"],
            suggested_country=review["suggested_country"],
            suggested_canonical_institution=review["institution"],
            match_method="primary_affiliation_exact",
            confidence=review["confidence"],
            review_status="pending_review",
            location_status="needs_coordinate_review",
            coordinate_status="missing",
            created_at=NOW,
            updated_at=NOW,
        )
        review_additions.append(row)

    existing_primary_keys = {
        name: {row[columns[0]] for row in current[name]}
        for name, columns in TARGETS.items()
    }
    additions_by_file = {
        "papers.csv": paper_additions,
        "paper_taxonomy.csv": taxonomy_additions,
        "author_institution_mappings.csv": mapping_additions,
        "institutions.csv": institution_additions,
        "institution_location_review.csv": review_additions,
    }
    for name, additions in additions_by_file.items():
        key = TARGETS[name][0]
        values = [row[key] for row in additions]
        if len(values) != len(set(values)):
            raise AssertionError(f"duplicate new primary keys in {name}")
        if existing_primary_keys[name] & set(values):
            raise AssertionError(f"new primary key already exists in {name}")

    replacements_by_file: dict[str, dict[str, Mapping[str, Any]]] = {
        "papers.csv": {MIRROR_ID: mirror},
        "paper_taxonomy.csv": {mirror_taxonomy["taxonomy_id"]: mirror_taxonomy},
        "author_institution_mappings.csv": mirror_mapping_replacements,
        "institutions.csv": {},
        "institution_location_review.csv": {},
    }
    return {
        "payload": payload,
        "current": current,
        "additions": additions_by_file,
        "replacements": replacements_by_file,
    }


def validate_staged(staged: Mapping[str, Path]) -> dict[str, int]:
    rows = {name: read_csv(path) for name, path in staged.items()}
    expected_counts = {
        "papers.csv": 486,
        "paper_taxonomy.csv": 672,
        "author_institution_mappings.csv": 1333,
        "institutions.csv": 745,
        "institution_location_review.csv": 664,
    }
    actual = {name: len(value) for name, value in rows.items()}
    if actual != expected_counts:
        raise AssertionError(f"unexpected staged counts: {actual}")
    for name, values in rows.items():
        if name == "institution_location_review.csv":
            # This queue has no single primary key; one institution can recur.
            continue
        key = TARGETS[name][0]
        keys = [row[key] for row in values]
        if not all(keys) or len(keys) != len(set(keys)):
            raise AssertionError(f"invalid primary keys in staged {name}")
    paper_ids = {row["paper_id"] for row in rows["papers.csv"]}
    if any(
        row["paper_id"] not in paper_ids
        for row in rows["paper_taxonomy.csv"]
        if row["paper_id"]
    ):
        raise AssertionError("staged taxonomy contains an unknown paper ID")
    prior_mapping_ids = {
        row["mapping_id"]
        for row in read_csv(ROOT / "data/curated/author_institution_mappings.csv")
    }
    if any(
        row["paper_id"] not in paper_ids
        for row in rows["author_institution_mappings.csv"]
        if row["mapping_id"] not in prior_mapping_ids
    ):
        raise AssertionError("staged mapping contains an unknown paper ID")
    mirror = next(row for row in rows["papers.csv"] if row["paper_id"] == MIRROR_ID)
    if mirror["publication_type"] != "conference" or mirror["venue_track"] != "":
        raise AssertionError("MIRROR publication upgrade was not staged")
    salart = next(
        row
        for row in rows["papers.csv"]
        if row["paper_id"] == "curated:baafdb8ac5488ceea198"
    )
    if salart["tasks"] or any(
        row["paper_id"] == salart["paper_id"]
        for row in rows["paper_taxonomy.csv"]
    ):
        raise AssertionError("SalArt-VQA must remain taskless and outside the public registry")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-only", action="store_true", help="Write reviewable CSVs without modifying curated data")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if RECEIPT_PATH.exists():
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        counts = {
            name: len(read_csv(ROOT / "data/curated" / name)) for name in TARGETS
        }
        if counts != receipt["row_counts_after"] or any(
            sha256(ROOT / "data/curated" / name) != expected
            for name, expected in receipt["sha256_after"].items()
        ):
            raise AssertionError("existing curation receipt does not match current rows")
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
        return

    built = build()
    with tempfile.TemporaryDirectory(prefix="neurips2026-stage-", dir=OUT) as directory:
        stage_root = Path(directory)
        staged: dict[str, Path] = {}
        for name, columns in TARGETS.items():
            source = ROOT / "data/curated" / name
            target = stage_root / name
            target.write_bytes(
                stage_csv_bytes(
                    source,
                    columns,
                    built["replacements"][name],
                    built["additions"][name],
                )
            )
            staged[name] = target
        row_counts_after = validate_staged(staged)

        if args.stage_only:
            review_dir = OUT / "staged"
            review_dir.mkdir(exist_ok=True)
            for name, path in staged.items():
                shutil.copy2(path, review_dir / name)
            print(json.dumps({"status": "staged_only", "row_counts": row_counts_after}, indent=2))
            return

        # Do not apply records which the unchanged conference policy rejects.
        try:
            from .venues import VenueRegistryError, validate_venue_type_track
        except ImportError:
            from venues import VenueRegistryError, validate_venue_type_track
        try:
            validate_venue_type_track("conference", "")
        except VenueRegistryError as error:
            raise SystemExit(
                "Not applied: the current conference policy rejects missing tracks. "
                "Use --stage-only to review the locked changes. No track may be inferred."
            ) from error

        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        for name in TARGETS:
            source = ROOT / "data/curated" / name
            backup = BASELINE_DIR / name
            if backup.exists():
                if sha256(backup) != sha256(source):
                    raise AssertionError(f"baseline backup already differs: {backup}")
            else:
                shutil.copy2(source, backup)

        for name in TARGETS:
            os.replace(staged[name], ROOT / "data/curated" / name)

    receipt = {
        "applied_at": NOW,
        "papers_added": 7,
        "papers_updated": [MIRROR_ID],
        "taxonomy_rows_added": 6,
        "author_institution_mappings_added": len(
            built["additions"]["author_institution_mappings.csv"]
        ),
        "institutions_added": len(built["additions"]["institutions.csv"]),
        "location_reviews_added": len(
            built["additions"]["institution_location_review.csv"]
        ),
        "row_counts_after": row_counts_after,
        "sha256_after": {name: sha256(ROOT / "data/curated" / name) for name in TARGETS},
        "salart_public_export_policy": (
            "curated taskless analysis; omitted by the existing task-gated public exporter"
        ),
        "human_aigi_dataset_status": "Coming soon; not added as released",
    }
    RECEIPT_PATH.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
