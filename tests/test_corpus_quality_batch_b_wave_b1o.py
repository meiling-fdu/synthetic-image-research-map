"""B1O accepts two atomic research-type corrections without changing forensic tasks."""
from collections import Counter
from copy import deepcopy
import base64
import csv
from datetime import datetime, timezone
from functools import lru_cache
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

import pytest

from scripts.curated_schema import ALLOWED_REVIEW_ACTIONS, ALLOWED_REVIEW_QUEUES
from scripts.literature51_reproducibility import preserved_bytes
from scripts.review_decisions import read_review_decisions, upsert_review_decision
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from tests.corpus_quality_test_helpers import csv_records, published_bytes, published_context
from tests.test_corpus_quality_batch_b_wave_b1n import logical_csv_chunks, replace_csv_tokens

ROOT = Path(__file__).resolve().parents[1]
BASE = "9581e17cc1dd78384966009b7f2d767b1961e3b6"
# Whole-transaction B1O receipts are checked at its immutable published endpoint.
PUBLISHED = "2d204d42174bd975cedfc0a3d3699b1c2070237c"
PAPERS = "data/curated/papers.csv"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1o_2026_10_25/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1o_2026_10_25.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
TARGETS = {"R267": "curated:7693a9c0107feaf90e10", "R236": "curated:64635535d7b7b6a12a32"}
IDS = {"R267": "review:b9f458d69de24b8aae0a", "R236": "review:aa32e93a24ade10ed99d"}
TYPES = {"R267": ["method", "analysis_study"], "R236": ["method", "dataset", "benchmark", "analysis_study"]}
POLICIES = {"R267": ["R3"], "R236": ["R1", "R2", "R3"]}
PDF_HASHES = {
    "R267": "01986259aeeaad807fd4034fa59783dd3d4615045ced2db50545788f566b2358",
    "R236": "3604416a9a60e895da2f3d789763f9477f7cbfcf8ef6976e16bb57abbfbbd3b7",
}
EVIDENCE_HASHES = {
    "manifest": "634c17a66a00c58921c5df69769e077b04a67ce70d3310ea92af8daaee56bffc",
    "report": "66c1b408bcbc049aa23eebcc923274255449947de4bc855ca3fba4ce01dffc93",
}
QUANTITATIVE_HASHES = {'R267': 'e923f680ec28c7853adb4c8f8e45eab354f0576ec10bb1d44f2e2460eca09fe3', 'R236': 'a7d63b50c53d3c6221602879b1b08897c090a0d2c4583799a0fee51450bd016e'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache
def packet():
    return json.loads((ROOT / MANIFEST).read_bytes())


@lru_cache
def archived_bytes(kind):
    archive = packet()["evidence_only_packet_archives"][kind]
    assert archive["encoding"] == "gzip+base64"
    raw = gzip.decompress(base64.b64decode(archive["gzip_base64"], validate=True))
    assert len(raw) == archive["bytes"] and digest(raw) == archive["sha256"] == EVIDENCE_HASHES[kind]
    return raw


@lru_cache
def original():
    return json.loads(archived_bytes("manifest"))


def record(data, review_id):
    found = [row for row in data["records"] if row["review_id"] == review_id]
    assert len(found) == 1
    return found[0]


def case(review_id):
    return record(packet(), review_id)


def selected_row(raw, paper_id):
    found = [row for row in csv_records(raw) if row["paper_id"] == paper_id]
    assert len(found) == 1
    return found[0]


def terminal(rows):
    """Historical registry prefix plus the two recovered B1O terminal identities."""
    result = {}
    for row in rows:
        if row["action"] != "no_action_after_review":
            continue
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        rid = match[1] if match else None
        if row["decision_id"] in IDS.values():
            recovered = next(key for key, value in IDS.items() if value == row["decision_id"])
            assert row["review_note"].startswith(recovered + " PROPOSE_CORRECTION_ACCEPTED:")
            assert rid in (None, recovered)
            rid = recovered
        if rid:
            assert rid not in result, "Duplicate terminal original review"
            result[rid] = row["decision_id"]
    return result


def accounting(rows, public):
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    done = terminal(rows)
    pending = [row for row in ledger if row["review_id"] not in done]
    active = [row for row in pending if row["paper_id"] in public]
    return {
        "historical_actions": len(ledger), "historical_papers": len({row["paper_id"] for row in ledger}),
        "closed_review_ids": sorted(done),
        "historical_unresolved_actions": len(pending), "historical_unresolved_papers": len({row["paper_id"] for row in pending}),
        "active_public_unresolved_actions": len(active), "active_public_unresolved_papers": len({row["paper_id"] for row in active}),
        "historical_unresolved_review_ids": [row["review_id"] for row in pending],
        "active_public_unresolved_review_ids": [row["review_id"] for row in active],
    }


@lru_cache
def baseline_paths(*prefixes):
    return subprocess.check_output(["git", "--no-optional-locks", "ls-tree", "-r", "--name-only", BASE, "--", *prefixes], cwd=ROOT, text=True).splitlines()


@pytest.mark.parametrize("kind", ["manifest", "report"])
def test_complete_evidence_packet_is_losslessly_portable_and_not_reconstructed(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest", "report"}
    assert original()["baseline_commit"] == packet()["baseline_commit"] == BASE
    assert original()["scope"]["authoritative_data_changes"] == original()["scope"]["review_actions_closed"] == 0


@pytest.mark.parametrize("rid", TARGETS)
def test_original_science_all_limitations_and_timestamps_survive_the_four_administrative_changes(rid):
    before, after = record(original(), rid), case(rid)
    flags = {"maintainer_acceptance_pending", "review_closed", "authoritative_changes_applied", "terminal_review_decision_created"}
    assert {key: after[key] for key in before if key not in flags} == {key: value for key, value in before.items() if key not in flags}
    assert before["maintainer_acceptance_pending"] is True and after["maintainer_acceptance_pending"] is False
    assert all(before[key] is False and after[key] is True for key in flags - {"maintainer_acceptance_pending"})
    assert after["accepted_outcome"] == "PROPOSE_CORRECTION_ACCEPTED"
    assert after["terminal_review_decision_id"] == after["adjudication"]["decision_id"] == IDS[rid]
    policies = after["adjudication"].get("accepted_policies", [after["adjudication"].get("accepted_policy")])
    assert policies == POLICIES[rid]
    assert after["final_authoritative_taxonomy"] == {
        "tasks": ["detection"] if rid == "R267" else ["detection", "localization"],
        "image_scopes": ["fully_generated"], "research_types": TYPES[rid]}


@pytest.mark.parametrize("rid,pages,n_authors,n_bytes", [("R267", 22, 10, 13757845), ("R236", 29, 11, 27826426)])
def test_exact_complete_primary_identity_version_and_page_accounting(rid, pages, n_authors, n_bytes):
    source = case(rid)["source"]
    assert source["sha256"] == PDF_HASHES[rid] and source["bytes"] == n_bytes
    assert source["pages"] == pages and source["pages_read"] == list(range(1, pages + 1))
    assert source["full_manuscript_read"] is source["identity_verified"] is True
    assert len(source["authors"]) == n_authors
    assert source["url"].endswith("xiao25g.pdf" if rid == "R267" else "65b4e84b66ed049f8066919a803e3942-Paper-Conference.pdf")


@pytest.mark.parametrize("path", [PAPERS, TAXONOMY])
def test_only_two_existing_authoritative_rows_and_fourteen_exact_cells_change(path):
    before_raw, after_raw = published_bytes(BASE, path), published_bytes(PUBLISHED, path)
    before, after = csv_records(before_raw), csv_records(after_raw)
    identity = "taxonomy_id" if path == TAXONOMY else "paper_id"
    assert [row[identity] for row in before] == [row[identity] for row in after]
    assert {row["paper_id"] for row, other in zip(before, after) if row != other} == set(TARGETS.values())
    updates = packet()["adjudication"]["csv_updates"][path]
    assert set(updates) == set(TARGETS.values())
    changed_cells = 0
    for rid, pid in TARGETS.items():
        old, new = selected_row(before_raw, pid), selected_row(after_raw, pid)
        assert old["research_types"] == "method" and new["research_types"] == ";".join(TYPES[rid])
        expected_keys = {"research_types"} if path == PAPERS else {"research_types", "research_types_review_reason", "research_types_evidence_tier", "research_types_evidence_source", "research_types_evidence_excerpt", "audited_at"}
        assert set(updates[pid]) == expected_keys
        assert new == {**old, **updates[pid]}
        assert {key for key in old if old[key] != new[key]} == expected_keys
        changed_cells += len(expected_keys)
        assert old["tasks"] == new["tasks"] == ("detection" if rid == "R267" else "detection;localization")
        assert old["image_scopes"] == new["image_scopes"] == "fully_generated"
        assert packet()["adjudication"]["before_rows"][path][pid] == old
        assert packet()["adjudication"]["after_rows"][path][pid] == new
        if path == TAXONOMY:
            assert new["research_types_evidence_tier"] == "primary_paper"
            assert new["research_types_evidence_source"] == case(rid)["source"]["url"]
            assert new["research_types_status"] == old["research_types_status"] == "reviewed"
    assert changed_cells == (2 if path == PAPERS else 12)
    header = next(csv.reader(io.StringIO(before_raw.decode(), newline="")))
    chunks = logical_csv_chunks(before_raw)
    reconstructed = [chunks[0]]
    for row, chunk in zip(before, chunks[1:]):
        reconstructed.append(replace_csv_tokens(chunk, header, updates[row["paper_id"]]) if row["paper_id"] in updates else chunk)
    assert after_raw == b"".join(reconstructed), "Unapproved CSV token bytes changed"


def test_two_terminal_decisions_are_atomic_unique_and_preserve_all_prior_registry_bytes():
    before, after = published_bytes(BASE, DECISIONS), published_bytes(PUBLISHED, DECISIONS)
    prior, rows = csv_records(before), csv_records(published_bytes(PUBLISHED, DECISIONS))
    assert after.startswith(before) and rows[:-2] == prior
    assert len(prior) == 97 and len(rows) == len({row["decision_id"] for row in rows}) == 99
    assert terminal(rows) == {**terminal(prior), **IDS}
    assert set(row["decision_id"] for row in rows[-2:]) == set(IDS.values())
    assert packet()["adjudication"]["registry_rows_before"] == 97 and packet()["adjudication"]["registry_rows_after"] == 99
    assert packet()["adjudication"]["prior_decision_bytes_preserved"] is True
    assert packet()["adjudication"]["accepted_review_ids"] == ["R267", "R236"]
    assert packet()["adjudication"]["terminal_decisions"] == {rid: next(row for row in rows if row["decision_id"] == did) for rid, did in IDS.items()}


@pytest.mark.parametrize("rid", TARGETS)
def test_exact_terminal_identity_rationale_no_action_semantics_and_idempotent_upsert(rid, tmp_path):
    rows = csv_records(published_bytes(PUBLISHED, DECISIONS))
    row = next(row for row in rows if row["decision_id"] == IDS[rid])
    assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
    assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
    assert row["target_type"] == "paper" and row["institution"] == ""
    assert row["created_by"] == "maintainer-approved-batch-b-b1o"
    assert row["created_at"] == row["updated_at"]
    assert datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")).tzinfo == timezone.utc
    paper = selected_row(published_bytes(BASE, PAPERS), TARGETS[rid])
    assert all(row[key] == paper[key] for key in ("title", "year", "doi", "openalex_url"))
    identity = "|".join(" ".join(row[key].split()).casefold() for key in ("review_queue", "target_type", "doi", "openalex_url", "title", "year", "institution"))
    assert "review:" + digest(identity.encode())[:20] == IDS[rid]
    note = row["review_note"]
    assert all(token in note for token in (rid, "PROPOSE_CORRECTION_ACCEPTED", PDF_HASHES[rid], ";".join(TYPES[rid]), "no_action_after_review means the approved correction is complete"))
    assert all(policy in note for policy in POLICIES[rid])
    destination = tmp_path / "review_decisions.csv"
    raw = published_bytes(PUBLISHED, DECISIONS)
    destination.write_bytes(raw)
    assert upsert_review_decision(row, path=destination) == row
    assert destination.read_bytes() == raw


def test_exactly_two_original_actions_close_without_new_questions_or_unrelated_closures():
    before = accounting(csv_records(published_bytes(BASE, DECISIONS)), published_context(BASE)["papers"])
    after = accounting(csv_records(published_bytes(PUBLISHED, DECISIONS)), published_context(PUBLISHED)["papers"])
    assert after == packet()["batch_b_accounting"]
    keys = ("historical_actions", "historical_papers", "historical_unresolved_actions", "historical_unresolved_papers", "active_public_unresolved_actions", "active_public_unresolved_papers")
    assert [before[key] for key in keys] == [159, 148, 137, 127, 135, 125]
    assert [after[key] for key in keys] == [159, 148, 135, 125, 133, 123]
    assert set(after["closed_review_ids"]) - set(before["closed_review_ids"]) == set(TARGETS)
    for key in ("historical_unresolved_review_ids", "active_public_unresolved_review_ids"):
        assert after[key] == [rid for rid in before[key] if rid not in TARGETS]
        assert {"R234", "T046", "T093", "T608", "T526", "P526"} <= set(after[key])
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    for rid, pid in TARGETS.items():
        assert [(row["review_id"], row["dimension"]) for row in ledger if row["paper_id"] == pid] == [(rid, "research_types")]


def test_R267_independent_R3_analysis_and_patch_method_are_both_retained():
    r = case("R267")
    assert r["provisional_outcome"] == "ANALYSIS_STUDY_ADDITION_SUPPORTED"
    assert r["proposed_complete_research_types"] == TYPES["R267"]
    assert r["policy_assessment"]["R3"]["outcome"] == "ANALYSIS_STUDY_ADDITION_SUPPORTED"
    assert r["policy_assessment"]["retained_method"]["outcome"] == "RETAIN_EXISTING_METHOD_WITHOUT_R4_REOPENING"
    assert "Sections3–4" in r["systematic_analysis_contribution"]["primary_role"]
    assert "without the patch method" in r["systematic_analysis_contribution"]["primary_role"]
    assert "technically evaluated inference procedure" in r["method_contribution"]["independent_role"]
    assert "causal effect" in r["causal_interpretation"] and "not established" in r["causal_interpretation"]
    assert len(r["question_matrix"]) == 20 and all(row["source_locators"] for row in r["question_matrix"])


def test_R267_preference_correctness_generator_inventory_and_inference_qualifications():
    q = {row["question_number"]: row for row in case("R267")["question_matrix"]}
    assert all(name in q[4]["finding"] for name in ("Stable Diffusion2.1", "SDXL1.0", "Stable Diffusion3", "PixArt-alpha", "FLUX.1[dev]", "Infinity"))
    assert "main four" in q[4]["finding"] and "six generators" in q[6]["finding"]
    assert "UNIQUE source photographs" in q[6]["limitations"]
    assert "No new direct human-quality rating" in q[2]["limitations"]
    assert "not detector confidence or balanced all-image accuracy" in q[9]["finding"]
    fig = case("R267")["quantitative_evidence"]["figure4"]
    assert len(fig["rows"]) == 8 and all(row["p"] > 0 for row in fig["rows"])
    assert "not causal effects" in fig["limitations"]


def test_R267_RINE_AP_accuracy_tradeoff_and_detector_specific_counterexamples():
    r = case("R267")
    rows = {(row["detector"], row["strategy"]): row["values"] for row in r["quantitative_evidence"]["table3"]["rows"]}
    assert rows["RINE", "Center"] == [75.0, 90.2, 51.6, 98.5]
    assert rows["RINE", "Easiest"] == [74.2, 91.9, 49.7, 98.9]
    counter = json.dumps(r["counterevidence"], ensure_ascii=False)
    assert all(value in counter for value in ("90.2→91.9", "75.0→74.2", "88.4→86.7", "NPR and SSP", "66.8→89.1"))
    assert len(r["counterevidence"]) == 6


def test_R267_metadata_availability_does_not_become_reproduction_or_verified_implementation():
    r = case("R267")
    release = r["release_review"]
    assert release["repository"]["commit"] == "2f170fa7f15a52e503b2dcb87115fbab51e6e5ae"
    assert release["repository"]["complete_tree_paths"] == [".gitignore", "LICENSE", "README.md"]
    assert "no implementation or experiment code" in release["repository"]["implementation_availability"]
    data = release["author_linked_dataset"]
    assert data["metadata_splits"][0]["num_examples"] == 24000
    assert data["asset_contents_verified"] is data["dataset_code_executed"] is False
    assert data["full_asset_downloads"] == 0
    assert r["confidence"]["primary_contribution_classification"] == "high"
    assert r["confidence"]["operational_reproducibility"].startswith("low:")


@pytest.mark.parametrize("policy,outcome", [("R1", "DATASET_ADDITION_SUPPORTED"), ("R2", "BENCHMARK_ADDITION_SUPPORTED"), ("R3", "ANALYSIS_STUDY_ADDITION_SUPPORTED")])
def test_R236_has_separate_independently_sufficient_primary_bases_for_R1_R2_R3(policy, outcome):
    assessment = case("R236")["policy_assessment"][policy]
    assert assessment["provisional_outcome"] == outcome
    assert assessment["evidence_scientifically_sufficient"] is True
    assert assessment["primary_locators"] and assessment["confidence"].startswith("high")
    basis = assessment["basis"]
    expected = {"R1": "human polygon/category", "R2": "Separately defined AJ/PAD", "R3": "informative without §6"}
    assert expected[policy] in basis


def test_R236_two_source_counts_remain_conflicting_and_instances_are_not_images():
    r = case("R236")
    d = r["data_resource"]
    assert d["real_count"] == 4000 and d["reused_real_images"] is True
    assert len(r["generator_protocol"]["rows"]) == 13
    assert d["main_valid_annotated_fake_count"] == 3035 and d["table8_labeled_fake_count"] == 3337
    assert d["count_discrepancy_resolved"] is False
    assert d["annotated_artifact_instances"] == 18285
    assert d["Table8_selected_values"]["labeled_fake_images"] == 3337
    assert d["Table8_selected_values"]["artifact_instances"] == 18285
    conflict = next(row for row in r["contradictory_and_negative_evidence"] if row.get("main_valid") == 3035)
    assert conflict["table8_labeled"] == 3337 and conflict["clear_reconciliation"] is False
    assert conflict["pdf_pages"] == [4, 20]


def test_R236_segmentation_and_classifier_heatmaps_preserve_distinct_outputs_conditions_and_metrics():
    tables = {row["table"]: row for row in case("R236")["quantitative_tables"]}
    seg = next(row for row in tables["2"]["rows"] if row["label"] == "Multi-task learning")
    heat = next(row for row in tables["13"]["rows"] if row["label"] == "Swin Multi-task")
    assert seg["values"][4::3] == ["27.3", "42.8"]
    assert heat["values"][::3] == ["4.8", "9.2"]
    assert "segmentation outputs" in tables["2"]["conditions"]
    assert "not segmentation outputs" in tables["13"]["conditions"]
    protocol = case("R236")["benchmark_protocol"]
    assert protocol["joint_detection_localization_gating_verified"] is False
    assert protocol["weak_instance_is_IoU_matching"] is False


def test_R236_interpretability_is_not_causal_reliance_and_generic_controls_can_improve():
    r = case("R236")
    boundary = r["causal_boundary"]
    assert boundary["artifact_overlap_is_causal_reliance"] is boundary["attention_is_proven_faithful"] is False
    assert boundary["artifact_ablation_necessity_intervention_reported"] is False
    assert boundary["extra_mask_supervision_confound_remains"] is True
    negative = r["contradictory_and_negative_evidence"]
    chameleon = next(row for row in negative if row.get("before_Acc") == "71.4")
    assert chameleon["after_Acc"] == "71.2" and chameleon["before_F1"] == "62.7" and chameleon["after_F1"] == "63.5"
    masks = next(row for row in negative if "Random_Acc_F1" in row)
    assert masks["None_Acc_F1"] == ["72.1", "63.6"] and masks["Random_Acc_F1"] == ["72.3", "64.1"]
    assert masks["Saliency_Acc_F1"] == ["72.4", "64.5"]


def test_R236_paper_non_strict_coverage_and_code_strict_threshold_are_not_silently_reconciled():
    p = case("R236")["benchmark_protocol"]
    assert p["paper_weak_instance_match_expression"].endswith(">= t")
    assert p["current_code_weak_instance_match_expression"] == "intersection_area/predicted_box_area > overlap_threshold"
    assert p["weak_instance_metrics"]["matching"] == "flag-based many-to-many, NOTstrictone-to-one"
    assert p["weak_instance_is_IoU_matching"] is False
    assert p["release_exact_paper_implementation_certified"] is False


def test_R236_asset_split_licensing_and_training_release_limits_survive_acceptance():
    r = case("R236")
    release = r["author_release"]["release_status"]
    assert release["README_experiment_training_and_model_evaluation_code"] == "TODO"
    assert release["standalone_metric_code_present"] is release["dataset_viewer_present_in_tree"] is True
    assert release["complete_experiment_code_or_checkpoints_verified"] is False
    assert release["HF_split_membership_or_asset_completeness_verified"] is release["upstream_image_rights_verified"] is False
    assert release["image_mask_Parquet_CSV_dataset_assets_downloaded"] == 0
    assert r["data_resource"]["public_complete_assets_verified"] is r["data_resource"]["upstream_rights_verified"] is False
    assert r["source"]["arxiv_publisher_global_equivalence_verified"] is False
    assert r["source"]["prior_arxiv_full_body_available_now"] is False
    assert r["source"]["original_final_receipt_complete_flag_preserved"] is False
    assert r["source"]["recovery_new_full_manuscript_requests"] == 0


@pytest.mark.parametrize("rid,key", [("R267", "quantitative_evidence"), ("R236", "quantitative_tables")])
def test_every_retained_quantitative_cell_is_frozen_to_the_independently_reviewed_evidence(rid, key):
    raw = json.dumps(case(rid)[key], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    assert digest(raw) == QUANTITATIVE_HASHES[rid]
    assert case(rid)[key] == record(original(), rid)[key]


def test_T236_resolved_structured_task_history_and_all_task_provenance_remain_untouched():
    t236 = packet()["T236_preserved_task_review"]
    assert t236 == original()["T236_preserved_task_review"] == case("R236")["T236_preservation"]
    assert t236["registry_literal_T236_rows"] == [] and t236["adjudication_status"] == "FINAL"
    assert t236["action"]["review_id"] == "T236" and t236["action"]["finalized"] is True
    assert t236["action"]["second_pass_source_url"] == "https://arxiv.org/html/2601.19430v1"
    assert t236["action"]["final_taxonomy"]["tasks"] == ["detection", "localization"]
    for path, sha in ((t236["source"], t236["source_sha256"]), (t236["report"], t236["report_sha256"])):
        assert digest((ROOT / path).read_bytes()) == digest(published_bytes(BASE, path)) == sha
    before, after = selected_row(published_bytes(BASE, TAXONOMY), TARGETS["R236"]), selected_row(published_bytes(PUBLISHED, TAXONOMY), TARGETS["R236"])
    for key in before:
        if key == "tasks" or key.startswith("tasks_") or key == "image_scopes" or key.startswith("image_scopes_"):
            assert after[key] == before[key]
    rows = csv_records(published_bytes(PUBLISHED, DECISIONS))
    assert "T236" not in terminal(rows)
    assert not [row for row in rows if re.search(r"^(?:Batch B review )?T236(?:;|\s+PROPOSE_)", row["review_note"])]


def test_original_retrieval_history_failures_two_complete_manuscripts_and_zero_new_adjudication_retrievals():
    retrieval = packet()["retrieval_accounting"]
    assert retrieval == original()["retrieval_accounting"]
    assert retrieval["new_complete_manuscripts_by_review"] == {"R267": 1, "R236": 1}
    assert retrieval["new_complete_manuscripts_total"] == retrieval["complete_successes"] == 2
    assert retrieval["manuscript_transport_attempts_total"] == 5
    assert retrieval["same_official_object_manuscript_transport_attempts_by_review"] == {"R267": 2, "R236": 3}
    events = retrieval["primary_transport_events"]
    assert len(events) == 5 and [event["exit_code"] for event in events] == [56, 0, 28, -15, 0]
    assert events[-1]["original_complete_flag"] is False and events[-1]["current_verified_complete"] is True
    for key in ("complete_new_manuscript_downloads_during_recovery", "new_scientific_source_network_operations_during_recovery", "dataset_image_mask_Parquet_CSV_assets_downloaded", "model_weights_or_checkpoints_downloaded", "supplement_or_repository_archives_downloaded", "repository_clones", "author_source_code_executions", "large_experiments"):
        assert retrieval[key] == 0
    assert packet()["adjudication"]["scientific_source_retrievals_during_adjudication"] == 0


def test_actual_public_delta_is_two_type_and_reason_updates_and_672_unchanged_other_papers():
    old, live = published_context(BASE), published_context(PUBLISHED)
    assert old["papers"].keys() == live["papers"].keys() and len(live["papers"]) == 674
    changed = {pid for pid in old["papers"] if old["papers"][pid] != live["papers"][pid]}
    assert changed == set(TARGETS.values())
    assert sum(old["papers"][pid] == live["papers"][pid] for pid in old["papers"] if pid not in changed) == 672
    for rid, pid in TARGETS.items():
        expected = deepcopy(old["papers"][pid])
        expected["research_types"] = TYPES[rid]
        expected["taxonomy_review"]["research_types"]["reason"] = selected_row(published_bytes(PUBLISHED, TAXONOMY), pid)["research_types_review_reason"]
        assert live["papers"][pid] == expected
    assert old["pairs"] == live["pairs"] and sum(live["pairs"].values()) == len(live["pairs"]) == 1410
    semantic = packet()["semantic_delta"]
    assert semantic["status"] == "PASS" and set(semantic["changed_paper_ids"]) == changed
    assert semantic["unchanged_other_public_papers"] == 672 and semantic["all_relationship_identities_unchanged"] is True


def test_actual_existing_map_dependents_only_change_research_type_metadata():
    before = {row["id"]: row for row in json.loads(published_bytes(BASE, PUBLIC[1]))["records"]}
    after = {row["id"]: row for row in json.loads(published_bytes(PUBLISHED, PUBLIC[1]))["records"]}
    assert before.keys() == after.keys() and len(after) == 1410
    dependents = {key for key, row in before.items() if row.get("paper_id") in TARGETS.values()}
    changed = {key for key in before if before[key] != after[key]}
    assert changed == dependents and dependents
    inverse = {pid: rid for rid, pid in TARGETS.items()}
    for key, row in before.items():
        expected = deepcopy(row)
        if key in dependents:
            pid = row["paper_id"]
            expected["research_types"] = TYPES[inverse[pid]]
            expected["taxonomy_review"]["research_types"]["reason"] = selected_row(published_bytes(PUBLISHED, TAXONOMY), pid)["research_types_review_reason"]
        assert after[key] == expected, key
    assert packet()["semantic_delta"]["changed_map_row_count"] == len(changed)
    for path in PUBLIC:
        before_doc, after_doc = json.loads(published_bytes(BASE, path)), json.loads(published_bytes(PUBLISHED, path))
        oldmeta, newmeta = deepcopy(before_doc["metadata"]), deepcopy(after_doc["metadata"])
        oldmeta.pop("public_preview_generated_at", None); newmeta.pop("public_preview_generated_at", None)
        assert oldmeta == newmeta
        assert {key: value for key, value in before_doc.items() if key not in {"records", "metadata"}} == {key: value for key, value in after_doc.items() if key not in {"records", "metadata"}}


def test_current_counts_are_recomputed_and_only_the_four_approved_type_additions_occur():
    old, live = published_context(BASE), published_context(PUBLISHED)
    assert old["counts"] == live["counts"] == packet()["corpus_counts"] == published_context(PUBLISHED)["counts"]
    def totals(context):
        return Counter(label for row in context["papers"].values() for dimension in ("tasks", "research_types") for label in row[dimension])
    before, after = totals(old), totals(live)
    assert not before - after and after - before == {"dataset": 1, "benchmark": 1, "analysis_study": 2}
    assert after == packet()["taxonomy_counts"]
    assert after == {"detection": 621, "source_attribution": 84, "localization": 45, "method": 578, "dataset": 138, "benchmark": 95, "survey": 21, "analysis_study": 84}
    assert {pid: row["image_scopes"] for pid, row in old["papers"].items()} == {pid: row["image_scopes"] for pid, row in live["papers"].items()}
    assert {pid: row["tasks"] for pid, row in old["papers"].items()} == {pid: row["tasks"] for pid, row in live["papers"].items()}


def test_original_review_questions_locked_policies_and_unrelated_authority_are_immutable():
    rows = {row["review_id"]: row for row in load_queues()["taxonomy_review"]["records"]}
    locked = {row["policy_id"]: row for row in json.loads((ROOT / (AUDIT + "batch_c_policy_decisions.json")).read_bytes())["policies"]}
    for rid in TARGETS:
        assert case(rid)["original_review"] == rows[rid]
        evidence_policies = case(rid)["locked_policies"]
        if isinstance(evidence_policies, list):
            evidence_policies = {row["policy_id"]: row for row in evidence_policies}
        for policy in POLICIES[rid]:
            assert evidence_policies[policy] == locked[policy]
    allowed = {PAPERS, TAXONOMY, DECISIONS, *PUBLIC}
    for path in baseline_paths("data/curated", "data/manual", "web/data"):
        if path not in allowed:
            assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path
    for name in ("taxonomy_review", "publication_metadata_review", "relationship_review", "unmapped_papers", "batch_c_policy_decisions"):
        path = AUDIT + name + ".json"
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_prior_packets_historical_fixtures_C13_and_separate_39_inventory_remain_unchanged():
    prior = original()["prior_B1A_N_artifact_sha256"]
    assert len(prior) == 28
    for path, sha in prior.items():
        assert digest((ROOT / path).read_bytes()) == digest(published_bytes(BASE, path)) == sha
    for path in baseline_paths("tests/fixtures"):
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path
    debt = packet()["batch_c_deferred_accounting"]
    assert debt == original()["batch_c_deferred_accounting"]
    assert debt["total_actions"] == 41 and debt["resolved"] == 28
    assert debt["total_unresolved"] == debt["external_unresolved"] == len(debt["remaining_external_ids"]) == 13
    assert debt["maintainer_judgments"] == 0
    inventory = packet()["separate_import_review_inventory"]
    assert inventory == original()["separate_import_review_inventory"]
    assert inventory["imported_papers"] == inventory["unmapped"] == len(inventory["candidate_to_paper"]) == 39
    assert inventory["relationships"] == 0
    for pid in inventory["candidate_to_paper"].values():
        assert load_context()["papers"][pid] == published_context(BASE)["papers"][pid]


def test_all_frozen_49_receipts_and_blocked_NeurIPS_status_survive():
    path = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT / path).read_bytes()
    assert raw == published_bytes(BASE, path)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for path, sha in frozen.items():
        assert digest(preserved_bytes(ROOT, path)) == sha, path
    assert packet()["neurips_status"] == "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"


def test_original_worker_and_independent_checks_remain_frozen_not_relabelled_as_new_runs():
    groups = original()["validation"]["completed_check_groups"]
    for name, count in (("R267_source_owner_recovered", 57), ("R236_source_owner_completed", 76), ("independent_scientific_crosscheck", 82), ("assembled_packet_content", 33), ("complete_preservation_gate", 45)):
        assert groups[name]["passed"] == count and groups[name]["failed"] == 0
    assert original()["validation"]["full_suite_runs"] == original()["validation"]["exports_run"] == 0
    assert packet()["evidence_only_validation"] == original()["validation"]


def test_report_preserves_original_history_and_separates_accepted_research_roles_from_T236():
    report = (ROOT / REPORT).read_text()
    assert archived_bytes("report").decode() in report
    for token in (*IDS.values(), *PDF_HASHES.values(), "R267", "R236", "T236", "method;analysis_study", "method;dataset;benchmark;analysis_study", "3,035", "3,337", "27.3", "42.8", "4.8", "9.2", "71.4", "71.2", "TODO", BASE):
        assert token in report
    scope = packet()["scope"]
    assert scope["review_decisions_added"] == scope["review_actions_closed"] == 2
    for key in ("forensic_task_changes", "image_scope_changes", "publication_metadata_changes", "new_Batch_B_actions_added", "Batch_B_denominator_changes"):
        assert scope[key] == 0
