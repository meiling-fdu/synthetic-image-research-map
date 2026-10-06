"""Focused regression checks for finalized Batch C Wave 2 adjudication."""

from collections import Counter
import csv
from functools import lru_cache
import io
import json
from pathlib import Path
import subprocess

from scripts.validate_corpus_quality_audit import load_context


ROOT = Path(__file__).resolve().parents[1]
BASE = "b5766b029a74d5225e2cdf490a8ce9cc55d69da7"
MANIFEST = ROOT / "data/raw/corpus_quality_batch_c_wave2_2026_10_06/evidence_manifest.json"
U010 = "curated:d0eec7c4fce8929c295a"
U017 = "curated:0d918782407e05ade5bd"
MEMBER = "institution:806523d1aae41484"
PARENT = "institution:19d2ee8d44bfb9f0"
AUTHORS = ["Thinh-Phat Vo", "Dang-Khoa Mai", "Minh-Triet Tran", "Trong-Le Do"]
SOURCE = "https://dl.acm.org/doi/pdf/10.1145/3810988.3812660"
PROTECTED_INSTITUTION_FILES = (
    "data/curated/institutions.csv",
    "data/curated/institution_hierarchy.csv",
    "data/curated/institution_locations.csv",
    "data/curated/institution_aliases.csv",
)


@lru_cache
def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def csv_rows(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def previous_csv(path):
    return list(csv.DictReader(io.StringIO(previous(path).decode("utf-8-sig"), newline="")))


def records(path):
    return json.loads((ROOT / path).read_text())["records"]


def test_u010_is_unchanged_and_remains_unresolved():
    for path, key in (
        ("data/curated/papers.csv", "paper_id"),
        ("data/curated/author_institution_mappings.csv", "paper_id"),
    ):
        before = [row for row in previous_csv(path) if row[key] == U010]
        after = [row for row in csv_rows(path) if row[key] == U010]
        assert after == before

    action = next(row for row in json.loads(MANIFEST.read_text())["actions"] if row["review_id"] == "U010")
    assert action["adjudication"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert action["final_disposition"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert action["corpus_change_applied"] is False
    assert action["exact_missing_evidence"] == (
        "Accessible official IEEE paper metadata/PDF containing the complete "
        "author-affiliation block and author markers."
    )


def test_u017_authors_have_exact_order_and_two_explicit_affiliations():
    paper = next(row for row in csv_rows("data/curated/papers.csv") if row["paper_id"] == U017)
    assert paper["authors"].split("; ") == [
        "Thinh-Phat Vo", "Dang-Khoa Mai", "Minh–Triet Tran", "Trong-Le Do"
    ]
    mappings = [
        row for row in csv_rows("data/curated/author_institution_mappings.csv")
        if row["paper_id"] == U017 and row["mapping_status"] == "active"
    ]
    assert [(row["institution_id"], row["affiliation_order"]) for row in mappings] == [
        (MEMBER, "1"), (PARENT, "2")
    ]
    assert {row["mapping_id"] for row in mappings} == {
        "mapping:92ec0a0fa7b4539863d1", "mapping:6307736ef459cb62af5a"
    }
    assert all(row["institution_authors"].split("; ") == AUTHORS for row in mappings)
    assert all(row["provenance_source"] == SOURCE for row in mappings)
    author_institution_links = {
        (author, row["institution_id"])
        for row in mappings
        for author in row["institution_authors"].split("; ")
    }
    assert len(author_institution_links) == 8


def test_member_parent_hierarchy_is_distinct_and_registry_state_is_unchanged():
    institutions = {row["institution_id"]: row for row in csv_rows("data/curated/institutions.csv")}
    assert MEMBER != PARENT
    assert institutions[MEMBER]["canonical_name"] == (
        "University of Science, Viet Nam National University Ho Chi Minh City"
    )
    assert institutions[MEMBER]["parent_institution_id"] == PARENT
    assert institutions[PARENT]["canonical_name"] == "Vietnam National University Ho Chi Minh City"
    for path in PROTECTED_INSTITUTION_FILES:
        assert (ROOT / path).read_bytes() == previous(path)


def test_u017_public_export_has_two_unique_relationships_and_complete_author_links():
    paper = next(
        row for row in records("web/data/public_preview_papers.json")
        if row.get("paper_id") == U017
    )
    relationships = [
        row for row in records("web/data/public_preview_map_data.json")
        if row.get("paper_id") == U017
    ]
    assert [author["name"] for author in paper["authors"]] == [
        "Thinh-Phat Vo", "Dang-Khoa Mai", "Minh–Triet Tran", "Trong-Le Do"
    ]
    assert {row["institution_id"] for row in relationships} == {MEMBER, PARENT}
    assert len(relationships) == 2
    assert len({(row["paper_id"], row["institution_id"]) for row in relationships}) == 2
    for author in paper["authors"]:
        assert author["affiliation_indices"] == [1, 2]
    for relationship in relationships:
        assert relationship["institution_authors"] == AUTHORS
        assert {entry["institution_id"] for entry in relationship["author_institution_affiliations"]} == {
            MEMBER, PARENT
        }


def test_wave2_ledger_reconciles_both_actions_and_remaining_batch_c():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["adjudication_status"] == "FINAL"
    assert {row["review_id"] for row in manifest["actions"]} == {"U010", "U017"}
    u017 = next(row for row in manifest["actions"] if row["review_id"] == "U017")
    assert u017["evidence_outcome"] == "EVIDENCE_RESOLVED_CHANGE"
    assert u017["adjudication"] == "EXPLICIT_DUAL_AFFILIATION_SUPPORTED"
    assert u017["final_disposition"] == "REMEDIATION_APPLIED"
    assert u017["corpus_change_applied"] is True
    assert u017["canonical_institutions"]["member"]["institution_id"] == MEMBER
    assert u017["canonical_institutions"]["parent"]["institution_id"] == PARENT
    assert manifest["reconciliation"] == {
        "EVIDENCE_RESOLVED_CHANGE": 1,
        "EVIDENCE_RESOLVED_NO_CHANGE": 0,
        "EVIDENCE_STILL_INSUFFICIENT": 1,
        "external_batch_c_before": 30,
        "external_batch_c_after": 29,
        "t527_separate_maintainer_scope_judgment": True,
        "total_unresolved_batch_c_after_including_t527": 30,
    }


def test_exact_corpus_and_unchanged_taxonomy_counts():
    context = load_context()
    assert context["counts"] == {
        "public": 639,
        "formal": 531,
        "mapped": 617,
        "unmapped": 22,
        "relationship_rows": 1421,
        "unique_paper_institution_pairs": 1421,
    }
    tasks = Counter(label for row in context["papers"].values() for label in row["tasks"])
    research_types = Counter(
        label for row in context["papers"].values() for label in row["research_types"]
    )
    assert tasks == {"detection": 592, "source_attribution": 85, "localization": 42}
    assert research_types == {
        "method": 547,
        "dataset": 133,
        "benchmark": 88,
        "survey": 20,
        "analysis_study": 78,
    }
