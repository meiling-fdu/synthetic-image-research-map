#!/usr/bin/env python3
"""Render and validate the Tier 2 HIGH evidence-resolution successor layer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from integrate_systematic_tier2_high_priority_evidence import (
    OUT,
    QUEUE,
    ROOT,
    new_institution_rows,
    paper_id,
)
from paper_exclusions import (
    active_exclusions,
    exclusions_with_curated_identities,
    matching_exclusion_rows,
    records_share_any_identity,
)
from systematic_tier2_high_priority_evidence_data import DECISIONS, PAPERS


CSV_PATH = ROOT / "data/manual/systematic_tier2_high_priority_evidence_review_2026_09.csv"
REPORT_PATH = ROOT / "docs/systematic_tier2_high_priority_evidence_review_2026_09.md"
FIELDS = (
    "candidate_id",
    "title",
    "original_policy_cluster",
    "exact_original_unresolved_question",
    "primary_source",
    "decisive_evidence",
    "evidence_resolution_outcome",
    "narrowed_scope_rationale",
    "identity_reconciliation_outcome",
    "added",
    "paper_id",
    "doi",
    "arxiv_id",
    "openalex_id",
    "forensic_task",
    "image_scope",
    "research_type",
    "verified_affiliations",
    "unresolved_metadata",
    "marker_count",
    "final_review_status",
    "next_action",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_records(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))["records"]


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def openalex_short(value: str) -> str:
    return value.rsplit("/", 1)[-1] if value else ""


def expected_rows() -> list[dict[str, str]]:
    queue = {
        row["candidate_id"]: row
        for row in read_csv(QUEUE)
        if row["evidence_review_priority"] == "HIGH"
    }
    papers = {paper["candidate_id"]: paper for paper in PAPERS}
    planned = {
        proposal["candidate_id"]: proposal
        for proposal in json.loads((OUT / "planned_additions.json").read_text(encoding="utf-8"))[
            "proposals"
        ]
    }
    public = {
        row["paper_id"]: row
        for row in load_records(ROOT / "web/data/public_preview_papers.json")
        if row.get("paper_id")
    }
    new_names = set(new_institution_rows())
    result: list[dict[str, str]] = []
    for decision in DECISIONS:
        candidate_id = decision["candidate_id"]
        queue_row = queue[candidate_id]
        paper = papers.get(candidate_id)
        confirmed = decision["evidence_resolution_outcome"] == "EVIDENCE_CONFIRMS_SCOPE"
        added = confirmed and decision["identity_reconciliation_outcome"] == "MISSING_ADD"
        pid = paper_id(candidate_id) if added else ""
        public_row = public.get(pid, {}) if pid else {}
        proposal = planned.get(candidate_id, {})
        affiliations = proposal.get("verified_affiliations", [])
        verified = " | ".join(
            f'{affiliation["institution"]} [{"; ".join(affiliation["authors"])}]'
            for affiliation in affiliations
        )
        pending_new = sorted(
            {
                affiliation["institution"]
                for affiliation in affiliations
                if affiliation["institution"] in new_names
            }
        )
        issues: list[str] = []
        if candidate_id == "audit:0b72dded38f87a65":
            issues.append("No DOI, arXiv ID, or OpenAlex ID was established.")
        if candidate_id == "audit:854cc239481946ba":
            issues.append(
                "IIT Patna affiliation is verified, but its registry location lacks confirmed coordinates."
            )
        if pending_new:
            issues.append("Coordinates pending for: " + "; ".join(pending_new) + ".")
        if not confirmed:
            issues.append("None; the evidence-layer scope exclusion is final for this pass.")
        marker_count = str(public_row.get("map_record_count", "")) if added else ""
        if added:
            assert public_row, candidate_id
        result.append(
            {
                "candidate_id": candidate_id,
                "title": queue_row["title"],
                "original_policy_cluster": queue_row["cluster"],
                "exact_original_unresolved_question": queue_row[
                    "exact_unresolved_question"
                ],
                "primary_source": decision["primary_source"],
                "decisive_evidence": decision["decisive_evidence"],
                "evidence_resolution_outcome": decision[
                    "evidence_resolution_outcome"
                ],
                "narrowed_scope_rationale": decision["narrowed_scope_rationale"],
                "identity_reconciliation_outcome": decision[
                    "identity_reconciliation_outcome"
                ],
                "added": "yes" if added else "no",
                "paper_id": pid,
                "doi": decision["doi"],
                "arxiv_id": decision["arxiv_id"],
                "openalex_id": decision["openalex_id"],
                "forensic_task": str(paper["tasks"]) if paper else "",
                "image_scope": str(paper["image_scopes"]) if paper else "",
                "research_type": str(paper["research_types"]) if paper else "",
                "verified_affiliations": verified,
                "unresolved_metadata": " ".join(issues) if issues else "None",
                "marker_count": marker_count,
                "final_review_status": "reviewed",
                "next_action": (
                    "Integrated into the authoritative successor corpus."
                    if added
                    else "Retain the evidence-layer exclusion; do not add or persist it in the authoritative exclusion registry."
                ),
            }
        )
    assert len(result) == 12
    return result


def identity_audit() -> list[dict[str, object]]:
    baseline = load_records(OUT / "baseline/web/data/public_preview_papers.json")
    current = load_records(ROOT / "web/data/public_preview_papers.json")
    baseline_exclusions = read_csv(OUT / "baseline/data/curated/paper_exclusions.csv")
    results: list[dict[str, object]] = []
    for paper in PAPERS:
        probe = {
            "title": paper["title"],
            "doi": paper["doi"],
            "arxiv_id": paper["arxiv_id"],
            "openalex_url": paper["openalex_url"],
        }
        strong = [
            row.get("paper_id") or row.get("title")
            for row in baseline
            if records_share_any_identity(probe, row)
        ]
        exclusions = [
            row.get("exclusion_id") or row.get("title")
            for row in baseline_exclusions
            if records_share_any_identity(probe, row)
        ]
        current_matches = [
            row.get("paper_id")
            for row in current
            if row.get("paper_id") == paper_id(str(paper["candidate_id"]))
            or records_share_any_identity(probe, row)
        ]
        fuzzy = sorted(
            (
                SequenceMatcher(
                    None,
                    normalize_title(str(paper["title"])),
                    normalize_title(str(row.get("title", ""))),
                ).ratio(),
                row.get("paper_id", ""),
                row.get("title", ""),
            )
            for row in baseline
        )[-3:][::-1]
        decision = next(
            row for row in DECISIONS if row["candidate_id"] == paper["candidate_id"]
        )
        result = {
            "candidate_id": paper["candidate_id"],
            "doi": paper["doi"],
            "arxiv_id": paper["arxiv_id"],
            "openalex_url": paper["openalex_url"],
            "baseline_strong_matches": strong,
            "active_exclusion_matches": exclusions,
            "current_matches": current_matches,
            "top_bounded_fuzzy_title_matches": [
                {"score": round(score, 4), "paper_id": pid, "title": title}
                for score, pid, title in fuzzy
            ],
            "manual_author_venue_method_review": decision["identity_note"],
            "outcome": "MISSING_ADD",
        }
        assert not strong and not exclusions, result
        assert current_matches == [paper_id(str(paper["candidate_id"]))], result
        results.append(result)
    return results


def duplicate_identity_audit() -> dict[str, object]:
    papers = load_records(ROOT / "web/data/public_preview_papers.json")
    duplicate_pairs: list[tuple[str, str]] = []
    for index, first in enumerate(papers):
        for second in papers[index + 1 :]:
            if records_share_any_identity(first, second):
                duplicate_pairs.append((first["title"], second["title"]))

    curated = read_csv(ROOT / "data/curated/papers.csv")
    exclusions = active_exclusions(
        exclusions_with_curated_identities(
            read_csv(ROOT / "data/curated/paper_exclusions.csv"), curated
        )
    )
    leaks = [
        paper["title"] for paper in papers if matching_exclusion_rows(paper, exclusions)
    ]

    def duplicate_values(field: str, normalizer=lambda value: value.casefold()) -> dict[str, list[str]]:
        by_value: dict[str, list[str]] = {}
        for paper in papers:
            value = str(paper.get(field, "") or "")
            if not value:
                continue
            label = str(
                paper.get("paper_id")
                or paper.get("doi")
                or paper.get("arxiv_id")
                or paper.get("openalex_url")
                or paper.get("title")
            )
            by_value.setdefault(normalizer(value), []).append(label)
        return {key: value for key, value in by_value.items() if len(value) > 1}

    result = {
        "duplicate_scientific_work_pairs": duplicate_pairs,
        "duplicate_doi": duplicate_values("doi"),
        "duplicate_arxiv": duplicate_values("arxiv_id"),
        "duplicate_openalex": duplicate_values("openalex_url"),
        "duplicate_normalized_title": duplicate_values("title", normalize_title),
        "active_exclusion_leaks": leaks,
    }
    assert not any(result.values()), result
    return result


def corpus_stats() -> dict[str, object]:
    papers = load_records(ROOT / "web/data/public_preview_papers.json")
    markers = load_records(ROOT / "web/data/public_preview_map_data.json")
    return {
        "public": len(papers),
        "published": sum(
            paper.get("publication_type") != "preprint" for paper in papers
        ),
        "mapped": sum(bool(paper.get("has_map_location")) for paper in papers),
        "markers": len(markers),
        "added_papers": len(PAPERS),
        "markerless_added_papers": sorted(
            paper["title"]
            for paper in papers
            if paper.get("paper_id") in {paper_id(str(row["candidate_id"])) for row in PAPERS}
            and not paper.get("has_map_location")
        ),
    }


def diff_audit() -> dict[str, object]:
    append_expected = {
        "papers.csv": 9,
        "paper_taxonomy.csv": 9,
        "author_institution_mappings.csv": 15,
        "institutions.csv": 6,
        "institution_location_review.csv": 6,
    }
    curated: dict[str, dict[str, int]] = {}
    for name in (
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
    ):
        old = read_csv(OUT / "baseline/data/curated" / name)
        new = read_csv(ROOT / "data/curated" / name)
        changed = [index for index, row in enumerate(old) if index >= len(new) or row != new[index]]
        assert not changed, (name, changed[:10])
        added = len(new) - len(old)
        assert added == append_expected.get(name, 0), (name, added)
        curated[name] = {
            "existing_rows": len(old),
            "existing_rows_changed": 0,
            "new_rows": added,
        }

    baseline_papers = load_records(OUT / "baseline/web/data/public_preview_papers.json")
    current_papers = load_records(ROOT / "web/data/public_preview_papers.json")
    def public_key(row: dict[str, object]) -> tuple[str, str]:
        for field in ("paper_id", "doi", "arxiv_id", "openalex_url"):
            if row.get(field):
                return field, str(row[field]).casefold()
        return "title_year", normalize_title(str(row.get("title", ""))) + ":" + str(row.get("year", ""))

    current_papers_by_id = {public_key(row): row for row in current_papers}
    paper_changes = [
        public_key(row)
        for row in baseline_papers
        if current_papers_by_id.get(public_key(row)) != row
    ]
    assert not paper_changes, paper_changes[:10]

    baseline_markers = load_records(OUT / "baseline/web/data/public_preview_map_data.json")
    current_markers = load_records(ROOT / "web/data/public_preview_map_data.json")
    current_markers_by_id = {row["id"]: row for row in current_markers}
    marker_changes = [
        row["id"]
        for row in baseline_markers
        if current_markers_by_id.get(row["id"]) != row
    ]
    assert not marker_changes, marker_changes[:10]

    hashes = json.loads((OUT / "baseline_sha256.json").read_text(encoding="utf-8"))
    frontend = [
        relative
        for relative in hashes
        if relative.startswith("web/") and not relative.startswith("web/data/")
    ]
    frontend_changed = [
        relative
        for relative in frontend
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != hashes[relative]
    ]
    assert not frontend_changed, frontend_changed
    return {
        "curated": curated,
        "public_paper_records": {
            "existing_records": len(baseline_papers),
            "existing_records_changed": 0,
            "new_records": len(current_papers) - len(baseline_papers),
        },
        "public_marker_records": {
            "existing_records": len(baseline_markers),
            "existing_records_changed": 0,
            "new_records": len(current_markers) - len(baseline_markers),
        },
        "frontend": {
            "files_checked": len(frontend),
            "changed": 0,
        },
    }


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render(rows: list[dict[str, str]], stats: dict[str, object], diff: dict[str, object]) -> str:
    evidence_counts = Counter(row["evidence_resolution_outcome"] for row in rows)
    confirmed = [
        row for row in rows if row["evidence_resolution_outcome"] == "EVIDENCE_CONFIRMS_SCOPE"
    ]
    identity_counts = Counter(row["identity_reconciliation_outcome"] for row in confirmed)
    lines = [
        "# Tier 2 HIGH-priority evidence resolution — September 2026",
        "",
        "This successor pass resolves only the 12 `HIGH` rows from `queue_c_evidence_required.csv`. The remaining 20 evidence rows, 171 policy exclusions, Tier 3, legacy cleanup, and the prior 648-paper inclusion baseline remain outside this pass.",
        "",
        "The canonical ledger is [systematic_tier2_high_priority_evidence_review_2026_09.csv](../data/manual/systematic_tier2_high_priority_evidence_review_2026_09.csv). Counts below are generated from that CSV and the current public exports.",
        "",
        "## Evidence resolution",
        "",
        *[
            f"- `{name}`: {evidence_counts.get(name, 0)}"
            for name in (
                "EVIDENCE_CONFIRMS_SCOPE",
                "EVIDENCE_EXCLUDES_SCOPE",
                "EVIDENCE_STILL_INSUFFICIENT",
            )
        ],
        "",
        "## Identity reconciliation",
        "",
        *[
            f"- `{name}`: {identity_counts.get(name, 0)}"
            for name in (
                "MISSING_ADD",
                "EXISTING_CURRENT",
                "EXISTING_ALTERNATE_TITLE",
                "EXISTING_UPDATE_NEEDED",
                "EXISTING_EXCLUSION",
                "AMBIGUOUS_IDENTITY",
            )
        ],
        "",
        "## All 12 decisions",
        "",
        "| Title | Original unresolved question | Decisive primary evidence | Evidence outcome | Identity | Added / ID | Taxonomy | Markers | Remaining issue |",
        "|---|---|---|---|---|---|---|---:|---|",
    ]
    for row in rows:
        taxonomy = "; ".join(
            part
            for part in (
                "task=" + row["forensic_task"] if row["forensic_task"] else "",
                "scope=" + row["image_scope"] if row["image_scope"] else "",
                "type=" + row["research_type"] if row["research_type"] else "",
            )
            if part
        )
        values = (
            row["title"],
            row["exact_original_unresolved_question"],
            row["decisive_evidence"],
            row["evidence_resolution_outcome"],
            row["identity_reconciliation_outcome"] or "N/A after scope exclusion",
            (row["added"] + (" / " + row["paper_id"] if row["paper_id"] else "")),
            taxonomy or "N/A",
            row["marker_count"] or "N/A",
            row["unresolved_metadata"],
        )
        lines.append("| " + " | ".join(markdown_escape(value) for value in values) + " |")

    lines.extend(
        [
            "",
            "## Corpus impact",
            "",
            f"- Public papers: 648 → {stats['public']}",
            f"- Published-only papers: 538 → {stats['published']}",
            f"- Mapped papers: 632 → {stats['mapped']}",
            f"- Map markers: 1,486 → {stats['markers']}",
            f"- Actual papers added: {stats['added_papers']}",
            f"- Added papers awaiting coordinates: {'; '.join(stats['markerless_added_papers'])}",
            "",
            "## Authoritative record changes",
            "",
            "| Layer | Existing rows changed | Added rows |",
            "|---|---:|---:|",
        ]
    )
    for name, values in diff["curated"].items():
        lines.append(
            f"| `{name}` | {values['existing_rows_changed']} | {values['new_rows']} |"
        )
    lines.extend(
        [
            f"| Public paper records | {diff['public_paper_records']['existing_records_changed']} | {diff['public_paper_records']['new_records']} |",
            f"| Public marker records | {diff['public_marker_records']['existing_records_changed']} | {diff['public_marker_records']['new_records']} |",
            "",
            "No institution aliases, confirmed locations, hierarchy edges, exclusion decisions, or frontend files changed. Six new institutions retain primary affiliation evidence in pending coordinate-review rows. Markerless papers remain visible in the paper list.",
            "",
            "## Integrity and validation",
            "",
            "All nine confirmed papers were reconciled against the pre-task 648-paper export and active exclusions by DOI, arXiv ID, OpenAlex ID, normalized title, alternate-version evidence, author/year/venue, method/acronym, and bounded fuzzy title. The final export has no duplicate scientific identity and no active-exclusion leak. The three out-of-scope results remain evidence-layer decisions and were not appended to `paper_exclusions.csv`.",
            "",
            "Validation and deterministic-regeneration receipts are stored in `data/processed/systematic_tier2_high_priority_evidence_review_2026_09/`. Historical audit layers remain frozen. No commit or push was performed.",
            "",
        ]
    )
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def artifacts(rows: list[dict[str, str]]) -> tuple[str, str, str, str]:
    stats = corpus_stats()
    diff = diff_audit()
    identities = identity_audit()
    duplicates = duplicate_identity_audit()
    report = render(rows, stats, diff)
    identity_json = json.dumps(identities, indent=2, ensure_ascii=False) + "\n"
    diff_json = json.dumps(diff, indent=2, sort_keys=True) + "\n"
    validation = {
        "evidence_outcomes": dict(
            sorted(Counter(row["evidence_resolution_outcome"] for row in rows).items())
        ),
        "identity_outcomes_for_confirmed_scope": dict(
            sorted(
                Counter(
                    row["identity_reconciliation_outcome"]
                    for row in rows
                    if row["evidence_resolution_outcome"] == "EVIDENCE_CONFIRMS_SCOPE"
                ).items()
            )
        ),
        "corpus": stats,
        "duplicates_and_exclusions": duplicates,
        "diff": diff,
    }
    validation_json = json.dumps(validation, indent=2, sort_keys=True) + "\n"
    return report, identity_json, diff_json, validation_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --write or --check")

    expected = expected_rows()
    if args.write:
        write_csv(CSV_PATH, expected)
    actual = read_csv(CSV_PATH)
    assert actual == expected, "Canonical evidence CSV differs from current reviewed/exported state."
    report, identity_json, diff_json, validation_json = artifacts(actual)
    paths_and_contents = (
        (REPORT_PATH, report),
        (OUT / "identity_checks.json", identity_json),
        (OUT / "diff_audit.json", diff_json),
        (OUT / "validation_data.json", validation_json),
    )
    if args.check:
        for path, content in paths_and_contents:
            assert path.read_text(encoding="utf-8") == content, path
    else:
        for path, content in paths_and_contents:
            path.write_text(content, encoding="utf-8")
    print(json.dumps(corpus_stats(), sort_keys=True))


if __name__ == "__main__":
    main()
