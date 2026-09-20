#!/usr/bin/env python3
"""Integrate only confirmed, missing papers from the Tier 2 HIGH evidence pass."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
    PAPERS_COLUMNS,
    PAPER_TAXONOMY_COLUMNS,
)
from paper_exclusions import (
    active_exclusions,
    exclusions_with_curated_identities,
    records_share_any_identity,
)
from systematic_tier2_high_priority_evidence_data import (
    DECISIONS,
    EXISTING_INSTITUTIONS,
    NEW_INSTITUTIONS,
    PAPERS,
)
from title_normalization import canonical_paper_title
from venues import canonicalize_record


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/processed/systematic_tier2_high_priority_evidence_review_2026_09"
QUEUE = ROOT / "data/processed/systematic_tier2_application_2026_09/queue_c_evidence_required.csv"
NOW = "2026-09-20T00:00:00Z"

CURATED_SNAPSHOT_FILES = (
    "papers.csv",
    "paper_taxonomy.csv",
    "author_institution_mappings.csv",
    "institutions.csv",
    "institution_location_review.csv",
    "institution_locations.csv",
    "institution_aliases.csv",
    "institution_hierarchy.csv",
    "paper_exclusions.csv",
    "venue_aliases.csv",
)
PUBLIC_SNAPSHOT_FILES = (
    "web/data/public_preview_papers.json",
    "web/data/public_preview_map_data.json",
)


def hash_id(prefix: str, value: str, length: int) -> str:
    return prefix + hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def paper_id(candidate_id: str) -> str:
    return hash_id(
        "curated:",
        "systematic-tier2-high-priority-evidence:" + candidate_id,
        20,
    )


def institution_id(name: str) -> str:
    return hash_id(
        "institution:",
        "systematic-tier2-high-priority-evidence:" + name,
        16,
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalized_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def identity_preflight() -> list[dict[str, object]]:
    """Reconcile all nine additions against the actual 648-paper baseline."""
    public = json.loads(
        (ROOT / "web/data/public_preview_papers.json").read_text(encoding="utf-8")
    )["records"]
    curated = read_csv(ROOT / "data/curated/papers.csv")
    exclusions = active_exclusions(
        exclusions_with_curated_identities(
            read_csv(ROOT / "data/curated/paper_exclusions.csv"), curated
        )
    )
    decision_by_id = {row["candidate_id"]: row for row in DECISIONS}
    results: list[dict[str, object]] = []
    for paper in PAPERS:
        candidate_id = str(paper["candidate_id"])
        probe = {
            "title": str(paper["title"]),
            "doi": str(paper["doi"]),
            "arxiv_id": str(paper["arxiv_id"]),
            "openalex_url": str(paper["openalex_url"]),
        }
        strong_matches = [
            row.get("paper_id") or row.get("title")
            for row in public
            if records_share_any_identity(probe, row)
        ]
        exclusion_matches = [
            row.get("exclusion_id") or row.get("title")
            for row in exclusions
            if records_share_any_identity(probe, row)
        ]
        fuzzy = sorted(
            (
                SequenceMatcher(
                    None,
                    normalized_title(str(paper["title"])),
                    normalized_title(str(row.get("title", ""))),
                ).ratio(),
                row.get("paper_id", ""),
                row.get("title", ""),
            )
            for row in public
        )[-3:][::-1]
        result = {
            "candidate_id": candidate_id,
            "doi": paper["doi"],
            "arxiv_id": paper["arxiv_id"],
            "openalex_url": paper["openalex_url"],
            "strong_matches": strong_matches,
            "active_exclusion_matches": exclusion_matches,
            "top_bounded_fuzzy_title_matches": [
                {"score": round(score, 4), "paper_id": pid, "title": title}
                for score, pid, title in fuzzy
            ],
            "manual_checks": decision_by_id[candidate_id]["identity_note"],
            "outcome": "MISSING_ADD",
        }
        assert not strong_matches, result
        assert not exclusion_matches, result
        results.append(result)
    assert len(results) == 9
    return results


def append_to_baseline(path: Path, columns: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    """Restore exact pre-task bytes, then append the reviewed successor rows."""
    baseline = OUT / "baseline" / path.relative_to(ROOT)
    original = baseline.read_bytes()
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writerows(rows)
    separator = b"" if not original or original.endswith(b"\n") else b"\n"
    path.write_bytes(original + separator + buffer.getvalue().encode("utf-8"))


def snapshot() -> None:
    base = OUT / "baseline"
    hashes: dict[str, str] = {}
    relative_paths = [f"data/curated/{name}" for name in CURATED_SNAPSHOT_FILES]
    relative_paths.extend(PUBLIC_SNAPSHOT_FILES)
    relative_paths.extend(
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / "web").glob("*"))
        if path.is_file()
    )
    for relative in dict.fromkeys(relative_paths):
        source = ROOT / relative
        hashes[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
        target = base / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    (OUT / "baseline_sha256.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def new_institution_rows() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for item in NEW_INSTITUTIONS:
        name = str(item["name"])
        result[name] = {
            "institution_id": institution_id(name),
            "canonical_name": name,
            "abbreviation": str(item["abbreviation"]),
            "institution_type": str(item["type"]),
            "institution_status": "active",
            "parent_institution_id": "",
            "public_display": "self",
            "created_at": NOW,
            "updated_at": NOW,
            "created_by": "primary-source-curation",
        }
    return result


def validate_scope_and_queue() -> dict[str, dict[str, str]]:
    high = {
        row["candidate_id"]: row
        for row in read_csv(QUEUE)
        if row["evidence_review_priority"] == "HIGH"
    }
    decisions = {row["candidate_id"]: row for row in DECISIONS}
    assert len(high) == 12 and set(high) == set(decisions)
    assert all(high[cid]["title"] for cid in high)
    outcomes = [row["evidence_resolution_outcome"] for row in DECISIONS]
    assert outcomes.count("EVIDENCE_CONFIRMS_SCOPE") == 9
    assert outcomes.count("EVIDENCE_EXCLUDES_SCOPE") == 3
    assert outcomes.count("EVIDENCE_STILL_INSUFFICIENT") == 0
    confirmed_missing = {
        row["candidate_id"]
        for row in DECISIONS
        if row["evidence_resolution_outcome"] == "EVIDENCE_CONFIRMS_SCOPE"
        and row["identity_reconciliation_outcome"] == "MISSING_ADD"
    }
    assert confirmed_missing == {paper["candidate_id"] for paper in PAPERS}
    return high


def build(*, allow_integrated: bool = False) -> dict[str, object]:
    queue = validate_scope_and_queue()
    decisions = {row["candidate_id"]: row for row in DECISIONS}
    new_institutions = new_institution_rows()

    existing_rows = read_csv(ROOT / "data/curated/institutions.csv")
    existing_by_id = {row["institution_id"]: row for row in existing_rows}
    names_by_id = {
        row["institution_id"]: row["canonical_name"] for row in existing_rows
    }
    names_by_id.update(
        {row["institution_id"]: row["canonical_name"] for row in new_institutions.values()}
    )
    locations = {
        row["institution_id"]: row
        for row in read_csv(ROOT / "data/curated/institution_locations.csv")
        if row["coordinate_status"] in {"known", "confirmed"}
    }

    for name, iid in EXISTING_INSTITUTIONS.items():
        assert iid in existing_by_id and existing_by_id[iid]["canonical_name"] == name
    current_names = {row["canonical_name"] for row in existing_rows}
    collisions = current_names.intersection(new_institutions)
    if allow_integrated:
        current_by_name = {row["canonical_name"]: row for row in existing_rows}
        assert all(
            current_by_name[name]["institution_id"]
            == new_institutions[name]["institution_id"]
            for name in collisions
        )
    else:
        assert not collisions

    paper_rows: list[dict[str, str]] = []
    taxonomy_rows: list[dict[str, str]] = []
    mapping_rows: list[dict[str, str]] = []
    proposals: list[dict[str, object]] = []

    for paper in PAPERS:
        candidate_id = str(paper["candidate_id"])
        decision = decisions[candidate_id]
        assert decision["evidence_resolution_outcome"] == "EVIDENCE_CONFIRMS_SCOPE"
        assert decision["identity_reconciliation_outcome"] == "MISSING_ADD"
        pid = paper_id(candidate_id)
        title = canonical_paper_title(str(paper["title"]))

        row = dict.fromkeys(PAPERS_COLUMNS, "")
        row.update(
            paper_id=pid,
            title=title,
            year=str(paper["year"]),
            authors=", ".join(paper["authors"]),
            venue=str(paper["venue"]),
            raw_venue=str(paper["venue"]),
            doi=str(paper["doi"]),
            arxiv_id=str(paper["arxiv_id"]),
            openalex_url=str(paper["openalex_url"]),
            paper_url=str(paper["paper_url"]),
            publication_type=str(paper["publication_type"]),
            abstract=str(paper["abstract"]),
            tasks=str(paper["tasks"]),
            image_scopes=str(paper["image_scopes"]),
            research_types=str(paper["research_types"]),
            scope_status="in_scope",
            source_database="primary_source",
            metadata_source=str(paper["paper_url"]),
            curation_status="confirmed",
            review_status="reviewed",
            created_at=NOW,
            updated_at=NOW,
        )
        canonical = canonicalize_record(row)
        paper_rows.append({column: canonical.get(column, "") or "" for column in PAPERS_COLUMNS})

        taxonomy = dict.fromkeys(PAPER_TAXONOMY_COLUMNS, "")
        taxonomy.update(
            taxonomy_id="paper_id:" + pid,
            paper_id=pid,
            title=title,
            year=str(paper["year"]),
            doi=str(paper["doi"]),
            arxiv_id=str(paper["arxiv_id"]),
            openalex_url=str(paper["openalex_url"]),
            tasks=str(paper["tasks"]),
            image_scopes=str(paper["image_scopes"]),
            research_types=str(paper["research_types"]),
            taxonomy_status="reviewed",
            audited_at="2026-09-20",
        )
        for dimension in ("tasks", "image_scopes", "research_types"):
            taxonomy[dimension + "_status"] = "reviewed"
            taxonomy[dimension + "_review_reason"] = (
                "Primary-source review under the narrowed Tier 2 HIGH evidence policy."
            )
            taxonomy[dimension + "_evidence_tier"] = "primary_paper"
            taxonomy[dimension + "_evidence_source"] = str(decision["primary_source"])
            taxonomy[dimension + "_evidence_excerpt"] = (
                str(decision["decisive_evidence"])
                + " "
                + str(decision["narrowed_scope_rationale"])
            )
        taxonomy_rows.append(taxonomy)

        verified_affiliations: list[dict[str, object]] = []
        for affiliation_order, affiliation in enumerate(paper["affiliations"], start=1):
            name = str(affiliation["institution"])
            iid = EXISTING_INSTITUTIONS.get(name) or new_institutions.get(name, {}).get(
                "institution_id", ""
            )
            assert iid, affiliation
            location = locations.get(str(iid), {})
            authors = list(affiliation["authors"])
            mapping = dict.fromkeys(AUTHOR_INSTITUTION_MAPPING_COLUMNS, "")
            mapping.update(
                mapping_id=hash_id(
                    "mapping:", f"{pid}:{affiliation_order}", 20
                ),
                paper_id=pid,
                title=title,
                year=str(paper["year"]),
                doi=str(paper["doi"]),
                openalex_url=str(paper["openalex_url"]),
                institution=names_by_id[str(iid)],
                institution_id=str(iid),
                location_id=location.get("location_id", ""),
                institution_authors="; ".join(authors),
                author_order="; ".join(
                    str(list(paper["authors"]).index(author) + 1) for author in authors
                ),
                affiliation_order=str(affiliation_order),
                raw_affiliation=str(affiliation["raw"]),
                institution_city=location.get("city", ""),
                institution_country=location.get("country", ""),
                institution_latitude=location.get("lat", ""),
                institution_longitude=location.get("lon", ""),
                provenance_source=str(paper["paper_url"]),
                mapping_status="active",
                created_at=NOW,
                updated_at=NOW,
            )
            mapping_rows.append(mapping)
            verified_affiliations.append(
                {
                    "institution": names_by_id[str(iid)],
                    "institution_id": str(iid),
                    "authors": authors,
                    "raw_affiliation": str(affiliation["raw"]),
                }
            )

        proposals.append(
            {
                **paper,
                "title": title,
                "paper_id": pid,
                "original_title": queue[candidate_id]["title"],
                "exact_unresolved_question": queue[candidate_id]["exact_unresolved_question"],
                "decision": decision,
                "verified_affiliations": verified_affiliations,
            }
        )

    location_review_rows: list[dict[str, str]] = []
    new_metadata = {str(row["name"]): row for row in NEW_INSTITUTIONS}
    for name, institution in new_institutions.items():
        paper = next(
            paper
            for paper in PAPERS
            if any(affiliation["institution"] == name for affiliation in paper["affiliations"])
        )
        affiliation = next(
            affiliation
            for affiliation in paper["affiliations"]
            if affiliation["institution"] == name
        )
        metadata = new_metadata[name]
        review = dict.fromkeys(INSTITUTION_LOCATION_REVIEW_COLUMNS, "")
        review.update(
            institution=name,
            canonical_institution_name=name,
            institution_id=institution["institution_id"],
            related_paper_id=paper_id(str(paper["candidate_id"])),
            title=str(paper["title"]),
            year=str(paper["year"]),
            doi=str(paper["doi"]),
            openalex_url=str(paper["openalex_url"]),
            institution_authors="; ".join(affiliation["authors"]),
            raw_affiliation=str(affiliation["raw"]),
            evidence_source="Primary paper author-affiliation block",
            evidence_url=str(paper["paper_url"]),
            suggested_city=str(metadata["city"]),
            suggested_country=str(metadata["country"]),
            suggested_canonical_institution=name,
            match_method="primary_affiliation_exact",
            confidence="high" if metadata["city"] and metadata["country"] else "medium",
            openalex_institution_id=str(metadata["openalex_institution_id"]),
            ror_id=str(metadata["ror_id"]),
            review_status="pending_review",
            location_status="needs_coordinate_review",
            coordinate_status="missing",
            created_at=NOW,
            updated_at=NOW,
        )
        location_review_rows.append(review)

    assert len(paper_rows) == len(taxonomy_rows) == 9
    assert len(mapping_rows) == 15
    assert len(new_institutions) == len(location_review_rows) == 6
    return {
        "papers.csv": paper_rows,
        "paper_taxonomy.csv": taxonomy_rows,
        "author_institution_mappings.csv": mapping_rows,
        "institutions.csv": list(new_institutions.values()),
        "institution_location_review.csv": location_review_rows,
        "proposals": proposals,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = OUT / "insertion.json"
    if not receipt.exists():
        preflight = identity_preflight()
        (OUT / "preinsertion_identity_checks.json").write_text(
            json.dumps(preflight, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    additions = build(allow_integrated=receipt.exists())
    (OUT / "planned_additions.json").write_text(
        json.dumps(additions, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if not receipt.exists():
        snapshot()

    targets = {
        "papers.csv": PAPERS_COLUMNS,
        "paper_taxonomy.csv": PAPER_TAXONOMY_COLUMNS,
        "author_institution_mappings.csv": AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        "institutions.csv": INSTITUTION_COLUMNS,
        "institution_location_review.csv": INSTITUTION_LOCATION_REVIEW_COLUMNS,
    }
    for name, columns in targets.items():
        path = ROOT / "data/curated" / name
        old = read_csv(OUT / "baseline" / path.relative_to(ROOT))
        key = columns[0]
        old_keys = {row[key] for row in old}
        assert not old_keys.intersection(row[key] for row in additions[name])
        append_to_baseline(path, columns, additions[name])

    result = {
        "papers_added": len(additions["papers.csv"]),
        "taxonomy_rows_added": len(additions["paper_taxonomy.csv"]),
        "mappings_added": len(additions["author_institution_mappings.csv"]),
        "institutions_added": len(additions["institutions.csv"]),
        "location_reviews_added": len(additions["institution_location_review.csv"]),
        "evidence_confirmed": 9,
        "evidence_excluded": 3,
        "evidence_insufficient": 0,
        "created_at": NOW,
    }
    receipt.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
