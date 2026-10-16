"""Approved B1A scope exclusions retain source records and independent reviews."""

from collections import Counter
import csv
from functools import lru_cache
import io
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from scripts.paper_exclusions import (
    build_active_exclusion_index,
    filter_public_output_pair,
    normalize_doi,
    normalize_openalex_url,
    read_exclusion_rows,
    record_is_excluded,
)
from scripts.review_decisions import read_review_decisions
from scripts.validate_corpus_quality_audit import load_context

ROOT = Path(__file__).resolve().parents[1]
BASE = "91de08a904847c47f60eb3dfd124e3db3300a459"
PUBLISHED_B1A = "1ea93c53a3d9f5f822ce27f818d8009274d3b12a"
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1a_2026_10_12/evidence_manifest.json"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
LEDGERS = (
    AUDIT + "unmapped_papers.json",
    AUDIT + "taxonomy_review.json",
    AUDIT + "relationship_review.json",
    AUDIT + "publication_metadata_review.json",
)
CASES = {
    "L015": {
        "doi": "10.1145/3772318.3791006",
        "paper_id": "curated:75cbd31c9946c7eb7977",
        "openalex": "https://openalex.org/W4416604008",
        "tasks": "",
        "research_types": "analysis_study",
        "map_rows": 5,
    },
    "P562": {
        "doi": "10.1109/tii.2023.3329711",
        "paper_id": "",  # Candidate identity; do not fabricate a curated paper row.
        "openalex": "https://openalex.org/W4388666300",
        "tasks": "detection",
        "research_types": "method",
        "map_rows": 1,
    },
}


@lru_cache
def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


@lru_cache
def published(path):
    # The B1A transaction is immutable; later reviewed metadata belongs to its own wave.
    return subprocess.check_output(["git", "show", f"{PUBLISHED_B1A}:{path}"], cwd=ROOT)


def csvrows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def matches(record, case):
    return (normalize_doi(record.get("doi")) == case["doi"]
            or normalize_openalex_url(record.get("openalex_url"))
            == case["openalex"].lower()
            or bool(case["paper_id"] and record.get("paper_id") == case["paper_id"]))


def selected_exclusions():
    rows = read_exclusion_rows(ROOT / "data/curated/paper_exclusions.csv")
    selected = {}
    for review_id, case in CASES.items():
        found = [row for row in rows if normalize_doi(row["doi"]) == case["doi"]]
        assert len(found) == 1, review_id
        selected[review_id] = found[0]
    return rows, selected


def manifest():
    return json.loads((ROOT / MANIFEST).read_text())


def test_exactly_two_new_scope_decisions_leave_every_prior_decision_unchanged():
    rows, selected = selected_exclusions()
    assert [row for row in rows if row not in selected.values()] == csvrows(
        previous("data/curated/paper_exclusions.csv"))
    decisions = csvrows(published("data/curated/review_decisions.csv"))
    live_decisions = read_review_decisions(ROOT / "data/curated/review_decisions.csv")
    new_decisions = []
    packet = {record["review_id"]: record for record in manifest()["records"]}
    assert set(packet) == set(CASES)
    for review_id, case in CASES.items():
        row = selected[review_id]
        assert row["paper_id"] == case["paper_id"]
        assert normalize_openalex_url(row["openalex_url"]) == case["openalex"].lower()
        assert row["reason"] == "out_of_scope"
        assert all(row[key] == "true" for key in
                   ("is_active", "excluded_from_public_preview", "excluded_from_map"))
        assert row["review_note"] and row["created_at"] and row["created_by"]
        assert not row["restored_at"] and not row["restore_note"]
        found = [decision for decision in decisions
                 if normalize_doi(decision["doi"]) == case["doi"]]
        assert len(found) == 1, review_id
        decision = found[0]
        assert [row for row in live_decisions if row["decision_id"] == decision["decision_id"]] == [decision]
        assert decision["target_type"] == "paper"
        assert decision["action"] == "exclude_paper_scope"
        assert decision["review_note"]
        new_decisions.append(decision)
        receipt = packet[review_id]["exclusion"]
        assert receipt["exclusion_id"] == row["exclusion_id"]
        assert receipt["review_decision_id"] == decision["decision_id"]
        assert receipt["reversible"] is True
    assert [row for row in decisions if row not in new_decisions] == csvrows(
        previous("data/curated/review_decisions.csv"))


@pytest.mark.parametrize("review_id", CASES)
def test_each_exclusion_matches_strong_identities_and_can_be_restored_independently(review_id):
    _, selected = selected_exclusions()
    case = CASES[review_id]
    row = selected[review_id]
    # The exclusion schema stores DOI, OpenAlex and optional curated ID, not arXiv.
    aliases = [{"doi": case["doi"].upper()},
               {"doi": "https://doi.org/" + case["doi"]},
               {"openalex_url": case["openalex"] + "/"}]
    if case["paper_id"]:
        aliases.append({"paper_id": case["paper_id"]})
    active = build_active_exclusion_index([row])
    inactive = build_active_exclusion_index([{**row, "is_active": "false"}])
    assert all(record_is_excluded(alias, active) for alias in aliases)
    assert all(not record_is_excluded(alias, inactive) for alias in aliases)

    # Restoring one paper must not restore the independently excluded other paper.
    before_papers, before_maps = (json.loads(previous(path))["records"] for path in PUBLIC)
    restored_rows = [{**entry, "is_active": "false"} if key == review_id else entry
                     for key, entry in selected.items()]
    papers, maps, impact = filter_public_output_pair(before_papers, before_maps, restored_rows)
    other = CASES[next(key for key in CASES if key != review_id)]
    assert papers == [entry for entry in before_papers if not matches(entry, other)]
    assert maps == [entry for entry in before_maps if not matches(entry, other)]
    assert sum(matches(entry, case) for entry in papers) == 1
    assert sum(matches(entry, case) for entry in maps) == case["map_rows"]
    assert impact == {"active_exclusion_public_papers_removed": 1,
                      "active_exclusion_map_records_removed": other["map_rows"]}


@pytest.mark.parametrize("path", (
    "data/curated/papers.csv",
    "data/curated/paper_taxonomy.csv",
    "data/curated/author_institution_mappings.csv",
    "data/curated/institutions.csv",
    "data/curated/institution_locations.csv",
    "data/processed/openalex_candidate_papers.csv",
))
def test_canonical_metadata_historical_taxonomy_and_affiliations_are_retained(path):
    if path == "data/processed/openalex_candidate_papers.csv":
        # This operational source is deliberately ignored, so its preserved
        # evidence digest is the baseline; it has never been a Git blob.
        expected = "9d6f0ff95f891a3f93816f34d828d23b12245567b243562b2181ba4dee839d1e"
        assert manifest()["evidence_baseline_source_sha256"][path] == expected
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    else:
        assert published(path) == previous(path)


@pytest.mark.parametrize("review_id", CASES)
def test_excluded_scientific_records_remain_recoverable_without_retagging(review_id):
    case = CASES[review_id]
    taxonomy = csvrows((ROOT / "data/curated/paper_taxonomy.csv").read_bytes())
    retained = [row for row in taxonomy if normalize_doi(row["doi"]) == case["doi"]]
    assert len(retained) == 1
    assert retained[0]["tasks"] == case["tasks"]
    assert retained[0]["research_types"] == case["research_types"]
    papers = csvrows((ROOT / "data/curated/papers.csv").read_bytes())
    curated = [row for row in papers if normalize_doi(row["doi"]) == case["doi"]]
    assert len(curated) == int(bool(case["paper_id"]))
    source_path = ("data/curated/papers.csv" if case["paper_id"]
                   else "data/processed/openalex_candidate_papers.csv")
    source_rows = csvrows((ROOT / source_path).read_bytes())
    assert any(matches(row, case) for row in source_rows)


@pytest.mark.parametrize("path", PUBLIC)
def test_public_delta_is_only_the_two_approved_exclusions(path):
    old = json.loads(previous(path))
    new = json.loads(published(path))
    live = json.loads((ROOT / path).read_text())
    assert not any(matches(row, case) for row in live["records"] for case in CASES.values())
    expected = [row for row in old["records"]
                if not any(matches(row, case) for case in CASES.values())]
    assert new["records"] == expected
    for case in CASES.values():
        count = 1 if path == PUBLIC[0] else case["map_rows"]
        assert sum(matches(row, case) for row in old["records"]) == count
    # No alias, hierarchy, provenance or unrelated public metadata rewrite.
    old.pop("records")
    new.pop("records")
    for payload in (old, new):
        payload["metadata"].pop("public_preview_generated_at", None)
    assert new == old


def test_corpus_delta_is_computed_from_public_membership():
    context = load_context()
    current = context["counts"]
    assert current == {"public": 636, "formal": 528, "mapped": 614,
                       "unmapped": 22, "relationship_rows": 1413,
                       "unique_paper_institution_pairs": 1413}
    endpoint = json.loads(published(PUBLIC[0]))["records"]
    totals = Counter(label for paper in endpoint
                     for dimension in ("tasks", "research_types") for label in paper[dimension])
    before = Counter(label for paper in json.loads(previous(PUBLIC[0]))["records"]
                     for dimension in ("tasks", "research_types") for label in paper[dimension])
    assert before - totals == {"detection": 1, "method": 1, "analysis_study": 1}
    assert not totals - before
    assert manifest()["corpus_after"] == current
    assert manifest()["taxonomy_after"] == dict(totals)


def test_original_batch_b_review_actions_are_preserved_not_closed_by_scope_exclusion():
    pending = []
    for path in LEDGERS:
        assert (ROOT / path).read_bytes() == previous(path)
        ledger = json.loads((ROOT / path).read_text())
        for key in ("records", "formal_records", "nonformal_records"):
            pending.extend(row for row in ledger.get(key, []) if row.get("batch") == "B")
    assert len(pending) == 159
    assert len({row["review_id"] for row in pending}) == 159
    assert len({row["paper_id"] for row in pending}) == 148
    public_ids = set(load_context()["papers"])
    applicable = [row for row in pending if row["paper_id"] in public_ids]
    assert len(applicable) == 157
    assert len({row["paper_id"] for row in applicable}) == 146
    assert {row["review_id"] for row in pending if row["paper_id"] not in public_ids} == set(CASES)
    assert sum(count == 2 for count in Counter(row["paper_id"] for row in pending).values()) == 11
    selected = [row for row in pending if row["review_id"] in CASES]
    assert len(selected) == 2
    assert next(row for row in selected if row["review_id"] == "L015")["issue"] == (
        "PUBLIC_INSTITUTION_NOT_IN_CURATED_REGISTRY")
    assert next(row for row in selected if row["review_id"] == "P562")["status"] == "SOURCE_CONFLICT"
    packet = manifest()
    assert packet["adjudication"]["status"] == "FINAL"
    assert packet["adjudication"]["baseline_commit"] == BASE
    assert packet["adjudication"]["scope_decisions_completed"] == 2
    for record in packet["records"]:
        disposition = record["disposition"]
        assert disposition["scientific_evidence_outcome"] == "EXCLUDE_OUT_OF_SCOPE"
        assert disposition["provisional"] is False
        assert disposition["maintainer_acceptance_pending"] is False
        assert disposition["authoritative_remediation_applied"] is True
        assert disposition["original_action_resolved"] is False
        assert record["original_review"]["status"] == "PENDING_NOT_ADJUDICATED"
    account = packet["accounting"]
    assert {key: account[key] for key in (
        "original_review_actions_closed", "original_review_actions_retained",
        "batch_b_pending_actions", "batch_b_unique_papers", "active_public_review_actions",
        "active_public_affected_papers", "inactive_public_review_actions",
    )} == {
        "original_review_actions_closed": 0, "original_review_actions_retained": 2,
        "batch_b_pending_actions": 159, "batch_b_unique_papers": 148,
        "active_public_review_actions": 157, "active_public_affected_papers": 146,
        "inactive_public_review_actions": 2,
    }


@pytest.mark.parametrize("path", (
    AUDIT + "batch_c_policy_decisions.json",
    "data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
    "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
))
def test_completed_batch_c_decisions_and_policies_are_phase_frozen(path):
    assert (ROOT / path).read_bytes() == previous(path)


def test_evidence_report_reconciles_applied_dispositions_and_public_counts():
    report = (ROOT / "docs/corpus_quality_batch_b_wave_b1a_2026_10_12.md").read_text()
    assert report.count("Accepted outcome: `EXCLUDE_OUT_OF_SCOPE`; reversible exclusion applied.") == 2
    assert "Zero original metadata questions are scientifically resolved or formally closed" in report
    assert "publisher-final" in report or "publisher final" in report
    packet = manifest()
    for label, key in (("Public papers", "public"), ("Formal publications", "formal"),
                       ("Mapped papers", "mapped"), ("Unmapped papers", "unmapped"),
                       ("Relationship rows", "relationship_rows"),
                       ("Unique paper–institution pairs", "unique_paper_institution_pairs")):
        assert f"| {label} | {packet['corpus_before'][key]:,} | {packet['corpus_after'][key]:,} |" in report
    assert "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA" in report
