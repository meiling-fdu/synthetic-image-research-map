"""Focused regression checks for the finalized Batch C external-evidence Wave 1."""

from collections import Counter
import csv
from functools import lru_cache
import json
from pathlib import Path
import subprocess

from scripts.paper_exclusions import (
    build_active_exclusion_index,
    normalize_arxiv_id,
    normalize_doi,
    normalize_openalex_url,
    normalize_title,
    read_exclusion_rows,
    record_is_excluded,
)
from scripts.validate_corpus_quality_audit import load_context


ROOT = Path(__file__).resolve().parents[1]
BASE = "59bf222"
PAPER_ID = "curated:6c2f591bf6fda3abecbb"
TITLE = "Reasoning-Aware AIGC Detection via Alignment and Reinforcement"
DOI = "10.18653/v1/2026.findings-acl.1043"
ARXIV = "2604.19172"
OPENALEX = "https://openalex.org/W7166812826"
EXCLUSION_ID = "exclusion:713b062c413880d72166"
PUBLIC = (
    "web/data/public_preview_papers.json",
    "web/data/public_preview_map_data.json",
)
VENUE_CASES = {
    "P550": "doi:10.2352/ei.2023.35.4.mwsf-380",
    "P586": "doi:10.1016/j.trpro.2022.09.012",
    "P610": "doi:10.2352/issn.2470-1173.2021.4.mwsf-276",
    "P633": "curated:60066ef08c2226131085",
}


@lru_cache
def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def records(payload):
    value = payload.get("records") if isinstance(payload, dict) else payload
    assert isinstance(value, list)
    return value


def load_csv(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def identity_matches(record, identity):
    if identity.startswith("doi:"):
        return normalize_doi(record.get("doi")) == identity.removeprefix("doi:")
    return str(record.get("paper_id") or "").casefold() == identity.casefold()


def is_r188_identity(record):
    return any((
        str(record.get("paper_id") or "").casefold() == PAPER_ID.casefold(),
        normalize_doi(record.get("doi")) == DOI,
        normalize_arxiv_id(record.get("arxiv_id") or record.get("arxiv_url")) == ARXIV,
        normalize_openalex_url(record.get("openalex_url")) == OPENALEX.casefold(),
        normalize_title(record.get("title")) == normalize_title(TITLE),
        "2026.findings-acl.1043" in json.dumps(record, ensure_ascii=False).casefold(),
    ))


def test_r188_is_durably_excluded_but_retains_one_historical_identity():
    papers = [row for row in load_csv("data/curated/papers.csv") if row["paper_id"] == PAPER_ID]
    taxonomy = [row for row in load_csv("data/curated/paper_taxonomy.csv") if row["paper_id"] == PAPER_ID]
    mappings = [
        row for row in load_csv("data/curated/author_institution_mappings.csv")
        if row["paper_id"] == PAPER_ID
    ]
    assert len(papers) == len(taxonomy) == 1
    assert len(mappings) == 3
    paper = papers[0]
    assert paper["title"] == TITLE
    assert normalize_doi(paper["doi"]) == DOI
    assert normalize_arxiv_id(paper["arxiv_id"]) == ARXIV
    assert normalize_openalex_url(paper["openalex_url"]) == OPENALEX.casefold()
    assert paper["authors"] == "Zhao Wang; Max Xiong; Jianxun Lian; Zhicheng Dou"
    assert paper["source_database"] == "openalex"

    exclusions = read_exclusion_rows()
    matches = [row for row in exclusions if row["exclusion_id"] == EXCLUSION_ID]
    assert len(matches) == 1
    exclusion = matches[0]
    assert exclusion["paper_id"] == PAPER_ID
    assert exclusion["reason"] == "out_of_scope"
    assert exclusion["is_active"] == "true"
    assert "TEXT_ONLY_OUT_OF_SCOPE" in exclusion["review_note"]
    assert "SOURCE_RECORD_CORRUPTION" in exclusion["review_note"]
    assert "2026.findings-acl.1043" in exclusion["review_note"]
    assert ARXIV in exclusion["review_note"]
    assert record_is_excluded(paper, build_active_exclusion_index(exclusions))
    assert record_is_excluded(taxonomy[0], build_active_exclusion_index(exclusions))


def test_r188_has_no_active_public_alias_or_taxonomy_contribution():
    for path in PUBLIC:
        payload = json.loads((ROOT / path).read_text())
        assert not [record for record in records(payload) if is_r188_identity(record)]
    context = load_context()
    assert PAPER_ID not in context["papers"]
    assert PAPER_ID not in context["taxonomy"]


def test_all_four_venue_cases_are_byte_semantically_unchanged():
    for path in PUBLIC:
        before = records(json.loads(previous(path)))
        after = records(json.loads((ROOT / path).read_text()))
        for review_id, identity in VENUE_CASES.items():
            old_rows = [row for row in before if identity_matches(row, identity)]
            new_rows = [row for row in after if identity_matches(row, identity)]
            assert old_rows, review_id
            assert new_rows == old_rows, review_id


def test_wave1_manifest_is_final_and_v1_requires_no_schema_change():
    manifest = json.loads((ROOT / "data/raw/corpus_quality_batch_c_wave1_2026_10_06/evidence_manifest.json").read_text())
    actions = manifest["actions"]
    assert manifest["adjudication_status"] == "FINAL"
    assert len(actions) == 5
    assert all(row["finalized"] for row in actions)
    outcomes = Counter(row["final_disposition"] for row in actions)
    assert outcomes == {
        "WAVE1_RESOLVED_NO_CHANGE": 4,
        "WAVE1_RESOLVED_CHANGE": 1,
    }
    r188 = next(row for row in actions if row["review_id"] == "R188")
    assert r188["identity_classification"] == "SOURCE_RECORD_CORRUPTION"
    assert r188["exclusion"] == {
        "exclusion_id": EXCLUSION_ID,
        "mechanism": "active durable paper exclusion",
        "reason": "out_of_scope",
        "review_semantics": "TEXT_ONLY_OUT_OF_SCOPE",
        "evidence_finding": "SOURCE_RECORD_CORRUPTION",
        "historical_identity_retained": True,
        "active_duplicate_remaining": False,
    }
    assert all(
        not row["schema_change_required"]
        for row in actions if row["review_id"] in VENUE_CASES
    )
    assert manifest["reconciliation"]["v1_schema_change_required"] is False


def test_batch_c_residual_counts_reconcile_from_phase1_ledger():
    phase1 = json.loads((ROOT / "data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json").read_text())
    wave1 = json.loads((ROOT / "data/raw/corpus_quality_batch_c_wave1_2026_10_06/evidence_manifest.json").read_text())
    external = {
        row["review_id"] for row in phase1["residual_triage"]
        if row["evidence_status"] == "EXTERNAL_PRIMARY_SOURCE_REQUIRED"
    }
    scope = {
        row["review_id"] for row in phase1["residual_triage"]
        if row["evidence_status"] == "MAINTAINER_SCOPE_JUDGMENT_REQUIRED"
    }
    resolved = {row["review_id"] for row in wave1["actions"]}
    assert len(external) == 35
    assert resolved <= external
    assert len(external - resolved) == 30
    assert scope == {"T527"}
    assert len(external - resolved) + len(scope) == 31
    assert phase1["reconciliation"]["batch_b_remaining"] == 159
    assert wave1["reconciliation"]["external_primary_source_required_after"] == 30
    assert wave1["reconciliation"]["total_unresolved_batch_c"] == 31
    v1 = next(policy for policy in phase1["policies"] if policy["policy_id"] == "V1")
    assert v1["decision"] == "ACCEPT"
    assert set(v1["affected_review_ids"]) == set(VENUE_CASES)
    assert all(not resolved_by_policy for resolved_by_policy in v1["policy_alone_resolves"].values())


def test_exact_corpus_and_taxonomy_impact():
    context = load_context()
    assert context["counts"] == {
        "public": 639,
        "formal": 531,
        "mapped": 617,
        "unmapped": 22,
        "relationship_rows": 1421,
        "unique_paper_institution_pairs": 1421,
    }
    tasks = Counter(
        label for row in context["papers"].values() for label in row["tasks"]
    )
    research_types = Counter(
        label for row in context["papers"].values() for label in row["research_types"]
    )
    assert tasks == {"detection": 590, "source_attribution": 85, "localization": 42}
    assert research_types == {
        "method": 547,
        "dataset": 132,
        "benchmark": 88,
        "survey": 20,
        "analysis_study": 78,
    }
