"""T303's accepted regional attribution review leaves scientific data unchanged."""
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import subprocess

import pytest

from scripts.curated_schema import ALLOWED_REVIEW_ACTIONS, ALLOWED_REVIEW_QUEUES
from scripts.review_decisions import read_review_decisions, upsert_review_decision
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from tests.corpus_quality_test_helpers import csv_records, published_bytes, published_context

ROOT = Path(__file__).resolve().parents[1]
BASE = "990c8221728a44b6ab78cfff5159612edb0983a7"
DECISIONS = "data/curated/review_decisions.csv"
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1f_2026_10_18/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1f_2026_10_18.md"
TARGET = "curated:33788a5e5e6efbd6bddd"
DECISION_ID = "review:75d76227af6d1a934c41"
TASKS = "detection;source_attribution;localization"
TYPES = "dataset;benchmark;analysis_study"


@lru_cache
def packet():
    return json.loads((ROOT / MANIFEST).read_bytes())


@lru_cache
def original():
    return json.loads(published_bytes(BASE, MANIFEST))


def record(data, review_id):
    matches = [r for r in data["records"] if r["review_id"] == review_id]
    assert len(matches) == 1
    return matches[0]


def terminal(decisions):
    result = {}
    for row in decisions:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        if match and row["action"] == "no_action_after_review":
            assert match[1] not in result, "Each review has exactly one terminal outcome"
            result[match[1]] = row["decision_id"]
    return result


def published_paths(*prefixes):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "ls-tree", "-r", "--name-only", BASE,
         "--", *prefixes], cwd=ROOT, text=True).splitlines()


def test_exactly_one_terminal_append_preserves_all_prior_decision_bytes():
    before = published_bytes(BASE, DECISIONS)
    after = (ROOT / DECISIONS).read_bytes()
    assert after.startswith(before)
    old = csv_records(before)
    rows = read_review_decisions(ROOT / DECISIONS)
    assert len(old) == 84 and len(rows) == 85
    assert rows[:-1] == old
    assert len({r["decision_id"] for r in rows}) == len(rows)
    assert terminal(rows) == {**terminal(old), "T303": DECISION_ID}
    row = rows[-1]
    assert row["decision_id"] == DECISION_ID
    assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
    assert row["target_type"] == "paper"
    assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
    assert row["created_by"] == "maintainer-approved-batch-b-b1f"
    assert row["created_at"] == row["updated_at"]
    assert row["doi"] == "" and row["openalex_url"] == "https://openalex.org/W7106655390"
    identity = "|".join(" ".join(row[k].split()).casefold() for k in
                        ("review_queue", "target_type", "doi", "openalex_url", "title", "year", "institution"))
    assert "review:" + hashlib.sha256(identity.encode()).hexdigest()[:20] == DECISION_ID
    for text in ("Batch B review T303;", "SUPPORTED_NO_CHANGE", TASKS, TYPES,
                 "regional", "0.997", "0.961", "0.825", "2511.19111v2", "overlap", "JPEG"):
        assert text in row["review_note"]


def test_accepted_decision_is_idempotent_without_duplicate_or_timestamp_churn(tmp_path):
    path = tmp_path / "review_decisions.csv"
    path.write_bytes((ROOT / DECISIONS).read_bytes())
    before = path.read_bytes()
    row = next(r for r in read_review_decisions(path) if r["decision_id"] == DECISION_ID)
    assert upsert_review_decision(row, path=path) == row
    assert path.read_bytes() == before


@pytest.mark.parametrize("path", ["data/curated/papers.csv", "data/curated/paper_taxonomy.csv"])
def test_no_taxonomy_or_canonical_metadata_edit_for_a_no_change_decision(path):
    before = published_bytes(BASE, path)
    assert (ROOT / path).read_bytes() == before
    row = next(r for r in csv_records(before) if r["paper_id"] == TARGET)
    assert row["tasks"] == TASKS and row["research_types"] == TYPES
    assert row["image_scopes"] == "generative_editing" and row["arxiv_id"] == "2511.19111"


def test_every_other_authoritative_table_and_public_output_is_byte_identical():
    paths = published_paths("data/curated", "data/manual", "web/data")
    assert len(paths) > 30
    for path in paths:
        if path != DECISIONS:
            assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_original_evidence_and_quantitative_protocols_are_preserved():
    old, new = original(), packet()
    assert new["retrieval_accounting"] == old["retrieval_accounting"]
    assert new["locked_policies"] == old["locked_policies"]
    assert new["source_files_sha256"] == old["source_files_sha256"]
    assert new["evidence_only_validation"] == old["validation"]
    assert new["evidence_only_integrity"] == old["integrity"]
    assert [r["review_id"] for r in new["records"]] == ["T093", "T303"]
    old_case, case = record(old, "T303"), record(new, "T303")
    for key in ("identity", "retrieval_accounting", "coverage", "original_question", "task_inventory",
                "labels_outputs_and_training", "construction_and_multi_turn_semantics", "quantitative_main_evidence",
                "contradictions_and_limitations", "policy_application", "dataset_documentation"):
        assert case[key] == old_case[key], key
    assert case["accepted_outcome"] == case["adjudication"]["outcome"] == "SUPPORTED_NO_CHANGE"
    assert case["review_closed"] is True and case["maintainer_acceptance_pending"] is False
    assert case["terminal_review_decision_id"] == DECISION_ID
    assert case["adjudication"]["retained_tasks"] == TASKS.split(";")
    assert case["adjudication"]["retained_research_types"] == TYPES.split(";")
    assert case["proposed_taxonomy_correction"] is None


def test_T093_remains_identical_insufficient_and_open_without_new_retrieval():
    old, current = record(original(), "T093"), record(packet(), "T093")
    assert current == old
    assert current["outcome"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert current["current_authoritative_taxonomy"]["tasks"] == "detection;source_attribution"
    assert current["review_closed"] is False and current["proposed_taxonomy_correction"] is None
    assert current["primary_retrieval"]["attempts"] == 1
    assert current["primary_retrieval"]["http_status"] == 403
    assert "T093" not in terminal(read_review_decisions(ROOT / DECISIONS))


def test_regional_attribution_is_evaluated_separately_from_binary_tasks():
    case = record(packet(), "T303")
    main = case["quantitative_main_evidence"]
    assert main["Table2_p5_baseline_tasks"]["SegFormer"]["semantic"] == [.952, .825, .532]
    assert main["Table2_p5_baseline_tasks"]["SegFormer"]["binary"] == [.989, .961, .678]
    assert main["Table5_p7_binary_image_classification"]["SegFormer"] == [.997, .999]
    assert len(main["Figure5_p7_semantic_confusions"]["column_order"]) == 9
    assert case["labels_outputs_and_training"]["semantic_class_count"] == 9
    assert "Regional" in case["adjudication"]["source_attribution_granularity"]
    assert case["construction_and_multi_turn_semantics"]["overlap_rule_verified"] is False
    assert case["identity"]["arxiv_id"] == "2511.19111v2"
    assert case["identity"]["actual_pdf_pages"] == 17
    assert case["retrieval_accounting"]["separate_supplements_retrieved"] == 0
    assert main["Table3_p5_transformations"]["SegFormer"]["JPEG60"]["semantic"][1] == .032


def test_pending_accounting_is_action_based_and_distinct_papers_recompute():
    ledger = [r for r in decision_rows(load_queues()) if r["batch"] == "B"]
    old_done = terminal(csv_records(published_bytes(BASE, DECISIONS)))
    done = terminal(read_review_decisions(ROOT / DECISIONS))
    assert set(done) - set(old_done) == {"T303"}
    assert len(ledger) == 159 and len({r["paper_id"] for r in ledger}) == 148
    pending = [r for r in ledger if r["review_id"] not in done]
    public = load_context()["papers"]
    active = [r for r in pending if r["paper_id"] in public]
    assert len(pending) == 149 and len(active) == 147
    assert len({r["paper_id"] for r in active}) == 136
    assert {"T093", "T608", "T526", "P526"} <= {r["review_id"] for r in active}
    assert not [r for r in pending if r["paper_id"] == TARGET]
    account = packet()["batch_b_accounting"]
    assert account["historical_unresolved_actions"] == len(pending)
    assert account["active_public_unresolved_actions"] == len(active)
    assert account["active_public_unresolved_papers"] == len({r["paper_id"] for r in active})
    assert account["resolved_review_ids"] == sorted(done)
    assert account["active_public_unresolved_review_ids"] == [r["review_id"] for r in active]


def test_corpus_relationships_and_taxonomy_totals_recompute_without_drift():
    before, current = published_context(BASE), load_context()
    assert current["papers"] == before["papers"]
    assert current["pairs"] == before["pairs"]
    assert current["counts"] == packet()["corpus_counts"] == {
        "public": 674, "formal": 557, "mapped": 613, "unmapped": 61,
        "relationship_rows": 1410, "unique_paper_institution_pairs": 1410}
    totals = Counter(label for p in current["papers"].values()
                     for dimension in ("tasks", "research_types") for label in p[dimension])
    assert totals == packet()["taxonomy_counts"] == {
        "detection": 621, "source_attribution": 84, "localization": 45,
        "method": 579, "dataset": 134, "benchmark": 90, "survey": 21, "analysis_study": 81}


def test_previous_batch_receipts_and_separate_import_and_C13_remain_frozen():
    old = original()
    for path, expected in old["preservation"]["prior_B1A_to_B1E_artifact_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    assert packet()["batch_c_deferred_accounting"] == old["batch_c_deferred_accounting"]
    assert packet()["batch_c_deferred_accounting"]["total_unresolved"] == 13
    assert packet()["separate_import_review_inventory"] == old["separate_import_review_inventory"]
    for path in published_paths("data/processed/literature51_2026_10_16"):
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_publication_history_is_truthful_and_existing_artifacts_not_reimported():
    data = packet()
    source = data["evidence_only_packet_source"]
    assert source["published_commit"] == BASE
    assert source["manifest_sha256"] == hashlib.sha256(published_bytes(BASE, MANIFEST)).hexdigest()
    assert source["report_sha256"] == hashlib.sha256(published_bytes(BASE, REPORT)).hexdigest()
    assert data["publication"]["evidence_publication"]["commit"] == BASE
    assert data["publication"]["adjudication_publication"]["strategy"] == "normal_fast_forward_only"
    report = (ROOT / REPORT).read_text()
    assert "already tracked" in report and DECISION_ID in report
    assert "SUPPORTED_NO_CHANGE" in report and "T093 remains unresolved" in report
    assert "evidence artifacts remain untracked" not in report
    assert "T303 remains an unresolved authoritative action" not in report
    assert "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA" in report
