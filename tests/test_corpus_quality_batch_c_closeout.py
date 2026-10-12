"""Accepted T527 scope exclusion, retained provenance, and Batch C closeout."""

from collections import Counter
import csv
from functools import lru_cache
import io
import json
from pathlib import Path
import subprocess

import pytest

from scripts.paper_exclusions import (
    build_active_exclusion_index,
    filter_public_output_pair,
    normalize_doi,
    normalize_openalex_url,
    normalize_title,
    read_exclusion_rows,
    record_is_excluded,
)
from scripts.review_decisions import read_review_decisions
from scripts.validate_corpus_quality_audit import load_context

ROOT = Path(__file__).resolve().parents[1]
BASE = "829b3c79e28c02c622dde2129bd6ce7b62eeb27f"
DOI = "10.1109/lsp.2024.3388958"
TAXONOMY_ID = "doi:" + DOI
OPENALEX = "https://openalex.org/W4394862914"
TITLE = "Towards Generated Image Provenance Analysis via Conceptual-Similar-Guided-SLIP Retrieval"
REASON = "TRAINING_IMAGE_PROVENANCE_RETRIEVAL_OUTSIDE_CORE_FORENSIC_SCOPE"
MANIFEST = "data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
REMAINING = {"T141", "U010", "R117", "R176", "R376", "R455", "R460", "R535",
             "R537", "R548", "R549", "R580", "R615"}


@lru_cache
def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def csvrows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def matches(record):
    return (normalize_doi(record.get("doi")) == DOI
            or normalize_openalex_url(record.get("openalex_url")) == OPENALEX.lower()
            or normalize_title(record.get("title")) == normalize_title(TITLE))


def exclusion():
    selected = [r for r in read_exclusion_rows() if normalize_doi(r.get("doi")) == DOI]
    assert len(selected) == 1
    return selected[0]


def test_one_durable_exclusion_and_review_decision_preserve_prior_decisions():
    row = exclusion()
    assert row["paper_id"] == ""  # This OpenAlex candidate has no curated paper ID.
    assert row["title"] == TITLE and row["year"] == "2024"
    assert normalize_openalex_url(row["openalex_url"]) == OPENALEX.lower()
    assert row["reason"] == "out_of_scope"
    assert all(row[k] == "true" for k in
               ("is_active", "excluded_from_public_preview", "excluded_from_map"))
    assert "T527_SCOPE_EXCLUDE" in row["review_note"] and REASON in row["review_note"]
    assert row["created_at"] and row["created_by"]
    assert not row["restored_at"] and not row["restore_note"]
    assert [r for r in read_exclusion_rows() if r != row] == csvrows(previous("data/curated/paper_exclusions.csv"))

    decisions = read_review_decisions()
    selected = [r for r in decisions if normalize_doi(r.get("doi")) == DOI]
    assert len(selected) == 1
    decision = selected[0]
    assert decision["target_type"] == "paper"
    assert decision["action"] == "exclude_paper_scope"
    assert REASON in decision["review_note"]
    assert [r for r in decisions if r != decision] == csvrows(previous("data/curated/review_decisions.csv"))


def test_strong_identity_exclusion_is_reversible_without_relabeling():
    row = exclusion()
    index = build_active_exclusion_index([row])
    aliases = ({"doi": DOI.upper()}, {"doi": "https://doi.org/" + DOI},
               {"openalex_url": OPENALEX + "/"})
    assert all(record_is_excluded(alias, index) for alias in aliases)
    restored_index = build_active_exclusion_index([{**row, "is_active": "false"}])
    assert all(not record_is_excluded(alias, restored_index) for alias in aliases)
    before_papers, before_maps = (json.loads(previous(p))["records"] for p in PUBLIC)
    kept_papers, kept_maps, impact = filter_public_output_pair(before_papers, before_maps, [row])
    assert impact == {"active_exclusion_public_papers_removed": 1,
                      "active_exclusion_map_records_removed": 2}
    assert kept_papers == [r for r in before_papers if not matches(r)]
    assert kept_maps == [r for r in before_maps if not matches(r)]
    restored_papers, restored_maps, impact = filter_public_output_pair(
        before_papers, before_maps, [{**row, "is_active": "false"}])
    assert restored_papers == before_papers and restored_maps == before_maps
    assert not any(impact.values())


@pytest.mark.parametrize("path", (
    "data/curated/papers.csv",
    "data/curated/paper_taxonomy.csv",
    "data/curated/author_institution_mappings.csv",
    "data/curated/institutions.csv",
    "data/curated/institution_locations.csv",
))
def test_historical_bibliography_taxonomy_and_affiliations_are_byte_preserved(path):
    assert (ROOT / path).read_bytes() == previous(path)


def test_t527_taxonomy_and_source_provenance_survive_public_exclusion():
    retained = [r for r in csvrows((ROOT / "data/curated/paper_taxonomy.csv").read_bytes())
                if r["taxonomy_id"] == TAXONOMY_ID]
    assert len(retained) == 1
    assert retained[0]["tasks"] == "source_attribution"
    assert retained[0]["research_types"] == "method"
    assert retained[0]["tasks_evidence_source"] == "OpenAlex local raw cache"
    context = load_context()
    assert TAXONOMY_ID not in context["papers"] and TAXONOMY_ID not in context["taxonomy"]
    prior_empty = {r["title"] for r in json.loads(previous(PUBLIC[0]))["records"] if not r["tasks"]}
    assert {r["title"] for r in context["papers"].values() if not r["tasks"]} == prior_empty


@pytest.mark.parametrize("path,removed_count", ((PUBLIC[0], 1), (PUBLIC[1], 2)))
def test_public_changes_remove_only_t527_and_preserve_every_other_record(path, removed_count):
    old = json.loads(previous(path))["records"]
    new = json.loads((ROOT / path).read_text())["records"]
    target = [r for r in old if matches(r)]
    assert len(target) == removed_count
    assert not any(matches(r) for r in new)
    assert new == [r for r in old if not matches(r)]
    if removed_count == 2:
        assert {r["institution_id"] for r in target} == {
            "institution:213a2f107c1f76df", "institution:33d54ba20fb76125"}


def test_corpus_and_overlapping_taxonomy_counts_are_recomputed():
    context = load_context()
    assert context["counts"] == {"public": 638, "formal": 530, "mapped": 616,
                                 "unmapped": 22, "relationship_rows": 1419,
                                 "unique_paper_institution_pairs": 1419}
    totals = Counter(label for paper in context["papers"].values()
                     for key in ("tasks", "research_types") for label in paper[key])
    assert totals == {"detection": 587, "source_attribution": 84, "localization": 43,
                      "method": 546, "dataset": 132, "benchmark": 88,
                      "survey": 20, "analysis_study": 78}
    old = Counter(label for paper in json.loads(previous(PUBLIC[0]))["records"]
                  for key in ("tasks", "research_types") for label in paper[key])
    assert old - totals == {"source_attribution": 1, "method": 1}
    assert not totals - old


def test_closeout_resolves_scope_only_and_preserves_all_thirteen_external_debts():
    manifest = json.loads((ROOT / MANIFEST).read_text())
    assert manifest["baseline_commit"] == BASE
    decision = manifest["decision"]
    assert decision["review_id"] == "T527" and decision["applied"] is True
    assert decision["disposition"] == "T527_SCOPE_EXCLUDE"
    assert decision["reason"] == REASON
    result = manifest["resolution"]
    assert {k: result[k] for k in ("total_actions", "resolved", "external_unresolved",
                                  "maintainer_judgments", "total_unresolved")} == {
        "total_actions": 41, "resolved": 28, "external_unresolved": 13,
        "maintainer_judgments": 0, "total_unresolved": 13,
    }
    assert len(result["remaining_external_ids"]) == len(REMAINING)
    assert set(result["remaining_external_ids"]) == REMAINING
    previous_wave_path = "data/raw/corpus_quality_batch_c_wave5c_2026_10_09/evidence_manifest.json"
    previous_wave = json.loads(previous(previous_wave_path))
    wave5b_path = "data/raw/corpus_quality_batch_c_wave5b_2026_10_09/evidence_manifest.json"
    wave5b = json.loads(previous(wave5b_path))
    assert (set(wave5b["resolution"]["remaining_external_ids"])
            - set(previous_wave["resolution"]["resolved_change_applied"])) == REMAINING
    # Evidence-debt receipts remain historical; no inaccessible source is resolved here.
    for path in (previous_wave_path,
                 "data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json",
                 "docs/corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md"):
        assert (ROOT / path).read_bytes() == previous(path)
