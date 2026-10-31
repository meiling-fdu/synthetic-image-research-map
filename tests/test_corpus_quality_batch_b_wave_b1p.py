"""B1P accepts two original research-type actions; forensic tasks stay intact."""
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
from tests.baseline_expectations import CURRENT_CORPUS_COUNTS, CURRENT_TAXONOMY_TOTALS
from tests.corpus_quality_test_helpers import csv_records, published_bytes, published_context
from tests.test_corpus_quality_batch_b_wave_b1n import logical_csv_chunks, replace_csv_tokens

ROOT = Path(__file__).resolve().parents[1]
BASE = "2d204d42174bd975cedfc0a3d3699b1c2070237c"
# Whole-transaction B1P receipts belong to its immutable published endpoint.
PUBLISHED = "dace181c2a9edbb7c467978e9e958e83fdddc143"
PAPERS = "data/curated/papers.csv"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1p_2026_10_26/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1p_2026_10_26.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
TARGETS = {"R024": "curated:1a8e996ef9ce73efc0ef", "R482": "curated:1eef07ebb6bd7e596f61"}
IDS = {"R024": "review:d8baba67e917010328d4", "R482": "review:575332a380a54630756b"}
BEFORE = {"R024": ["method"], "R482": ["method", "dataset"]}
TYPES = {"R024": ["method", "analysis_study"], "R482": ["method", "dataset", "benchmark"]}
TASKS = {"R024": ["source_attribution"], "R482": ["detection"]}
POLICIES = {"R024": "R3", "R482": "R2"}
PDF_HASHES = {
    "R024": "caf9ac0ae36bf58177409776c0079a7814dbb0a792b84d191d4496b70169d159",
    "R482": "9a2f9d0c6b67198daf0fdbcf9c98340cca9895c8369f832dd3103a6a7f2f1ca7",
}
EVIDENCE_HASHES = {
    "manifest": "86e2305431d309e2b73ccb63ce9dee59ad38703a12bb99639037ddcce648e159",
    "report": "f3883a88f532ba0fd6914f5b725a913970be9a4545d9e467634255106c4a24a0",
}
SCIENCE_HASHES = {
    "R024": "6240cd4a8f7eb9b3cf170d7d7ec1cc7b10ac3e249f30bd087114aaea18fa3479",
    "R482": "1984602407a19b94d5586d3d98e23a6740d30c2d3f3eab78fdfbf67e7fec91dd",
}
QUANTITATIVE_HASHES = {
    "R024": "b225a11354226b60a2cc1416b6414f347a50c509c2266afe79b879384c275a2a",
    "R482": "100474ec96d06910dd5b7de832e72f9a94239a28cf27899ae28aa398a82970e9",
}
B1O_TERMINAL = {"R267": "review:b9f458d69de24b8aae0a", "R236": "review:aa32e93a24ade10ed99d"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def object_digest(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


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


def record(document, rid):
    found = [row for row in document["review_records"] if row["review_id"] == rid]
    assert len(found) == 1
    return found[0]


def case(rid):
    return record(packet(), rid)


def science(rid):
    return case(rid)["scientific_review"]


def selected_row(raw, pid):
    found = [row for row in csv_records(raw) if row["paper_id"] == pid]
    assert len(found) == 1
    return found[0]


def terminal(rows):
    """Read original-action identity, including B1O's separately recorded IDs."""
    found = {}
    for row in rows:
        if row["action"] != "no_action_after_review":
            continue
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        rid = match[1] if match else None
        if row["decision_id"] in B1O_TERMINAL.values():
            recovered = next(key for key, did in B1O_TERMINAL.items() if did == row["decision_id"])
            assert row["review_note"].startswith(recovered + " PROPOSE_CORRECTION_ACCEPTED:")
            assert rid in (None, recovered)
            rid = recovered
        if rid:
            assert rid not in found, "Duplicate terminal decision for an original review"
            found[rid] = row["decision_id"]
    return found


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
def test_original_evidence_packet_is_lossless_portable_and_anchored_before_adjudication(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest", "report"}
    assert original()["published_baseline"] == packet()["published_baseline"] == BASE
    assert original()["authoritative_changes_applied"] is False
    assert original()["terminal_decisions_appended"] == 0
    assert original()["maintainer_acceptance"] == "PENDING"


@pytest.mark.parametrize("rid", TARGETS)
def test_original_science_retrieval_corrections_and_failures_survive_administrative_acceptance(rid):
    before, after = record(original(), rid), case(rid)
    administrative = {"current_authoritative_taxonomy", "authoritative_review_remains_unresolved", "existing_terminal_research_type_decisions", "manual_review", "maintainer_acceptance", "actual_authoritative_data_delta"}
    assert {key: after[key] for key in before if key not in administrative} == {key: value for key, value in before.items() if key not in administrative}
    assert before["authoritative_review_remains_unresolved"] is True and after["authoritative_review_remains_unresolved"] is False
    assert before["manual_review"] is True and after["manual_review"] is False
    assert before["maintainer_acceptance"] == "PENDING" and after["maintainer_acceptance"] == "ACCEPTED"
    assert before["existing_terminal_research_type_decisions"] == []
    assert after["accepted_outcome"] == "PROPOSE_CORRECTION_ACCEPTED"
    assert after["terminal_review_decision_id"] == after["adjudication"]["decision_id"] == IDS[rid]
    assert after["final_authoritative_taxonomy"] == after["current_authoritative_taxonomy"] == {"tasks": TASKS[rid], "image_scopes": ["fully_generated"], "research_types": TYPES[rid]}
    assert object_digest(after["scientific_review"]) == SCIENCE_HASHES[rid]
    assert after["scientific_review"] == before["scientific_review"]
    assert after["numerical_transcription"] == before["numerical_transcription"]
    assert object_digest(after["numerical_transcription"]) == QUANTITATIVE_HASHES[rid]


@pytest.mark.parametrize("rid,n_pages,n_authors,n_bytes", [("R024", 17, 5, 628993), ("R482", 11, 4, 9886237)])
def test_exact_manuscript_versions_fingerprints_pages_and_authors(rid, n_pages, n_authors, n_bytes):
    source = science(rid)["manuscript_identity"] if rid == "R024" else science(rid)["primary_source"]
    fingerprint = source["manuscript"] if rid == "R024" else source
    assert fingerprint["sha256"] == PDF_HASHES[rid] and fingerprint["bytes"] == n_bytes
    assert source["pages"] == n_pages and len(source["authors"]) == n_authors
    if rid == "R024":
        assert source["printed_copyright_and_citation_year"] == 2027 and source["canonical_year_preserved"] == 2026
        assert source["checks"]["strict_pdf"] and source["checks"]["visual_byline"]
    else:
        assert source["complete_primary_identity_verified"] and source["eof"] and source["pdf_magic"]
        assert "11-page" in source["version"] and "No appendix" in source["version"]
        assert "not an independent IEEE-byte comparison" in source["equivalence_statement"]


@pytest.mark.parametrize("path", [PAPERS, TAXONOMY])
def test_exact_two_existing_rows_fourteen_csv_cells_and_no_bibliographic_or_task_changes(path):
    old_raw, new_raw = published_bytes(BASE, path), published_bytes(PUBLISHED, path)
    old, new = csv_records(old_raw), csv_records(new_raw)
    identity = "taxonomy_id" if path == TAXONOMY else "paper_id"
    assert [row[identity] for row in old] == [row[identity] for row in new]
    assert {row["paper_id"] for row, other in zip(old, new) if row != other} == set(TARGETS.values())
    updates = packet()["adjudication"]["csv_updates"][path]
    assert set(updates) == set(TARGETS.values())
    changed_cells = 0
    for rid, pid in TARGETS.items():
        before, after = selected_row(old_raw, pid), selected_row(new_raw, pid)
        allowed = {"research_types"} if path == PAPERS else {"research_types", "research_types_review_reason", "research_types_evidence_tier", "research_types_evidence_source", "research_types_evidence_excerpt", "audited_at"}
        assert set(updates[pid]) == allowed
        assert after == {**before, **updates[pid]}
        assert {key for key in before if before[key] != after[key]} == allowed
        assert before["research_types"] == ";".join(BEFORE[rid]) and after["research_types"] == ";".join(TYPES[rid])
        assert before["tasks"] == after["tasks"] == ";".join(TASKS[rid])
        assert before["image_scopes"] == after["image_scopes"] == "fully_generated"
        assert packet()["adjudication"]["before_rows"][path][pid] == before
        assert packet()["adjudication"]["after_rows"][path][pid] == after
        changed_cells += len(allowed)
        if path == TAXONOMY:
            assert after["research_types_evidence_tier"] == "primary_paper"
            assert after["research_types_status"] == before["research_types_status"] == "reviewed"
    assert changed_cells == (2 if path == PAPERS else 12)
    header = next(csv.reader(io.StringIO(old_raw.decode(), newline="")))
    chunks = logical_csv_chunks(old_raw)
    reconstructed = [chunks[0]]
    for row, chunk in zip(old, chunks[1:]):
        reconstructed.append(replace_csv_tokens(chunk, header, updates[row["paper_id"]]) if row["paper_id"] in updates else chunk)
    assert new_raw == b"".join(reconstructed), "Unapproved CSV token bytes changed"


def test_exact_two_atomic_registry_appends_preserve_the_entire_99_row_byte_prefix():
    old_raw, new_raw = published_bytes(BASE, DECISIONS), published_bytes(PUBLISHED, DECISIONS)
    old, new = csv_records(old_raw), csv_records(new_raw)
    assert new_raw.startswith(old_raw) and new[:-2] == old
    assert len(old) == 99 and len(new) == len({row["decision_id"] for row in new}) == 101
    assert terminal(new) == {**terminal(old), **IDS}
    assert {row["decision_id"] for row in new[-2:]} == set(IDS.values())
    assert packet()["adjudication"]["registry_rows_before"] == 99 and packet()["adjudication"]["registry_rows_after"] == 101
    assert packet()["adjudication"]["accepted_review_ids"] == ["R024", "R482"]
    assert packet()["adjudication"]["prior_decision_bytes_preserved"] is True
    assert packet()["adjudication"]["terminal_decisions"] == {rid: next(row for row in new if row["decision_id"] == did) for rid, did in IDS.items()}


@pytest.mark.parametrize("rid", TARGETS)
def test_terminal_identity_policy_corrected_semantics_and_idempotent_registry_upsert(rid, tmp_path):
    rows = read_review_decisions(ROOT / DECISIONS)
    row = next(row for row in rows if row["decision_id"] == IDS[rid])
    assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
    assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
    assert row["target_type"] == "paper" and row["institution"] == ""
    assert row["created_by"] == "maintainer-approved-batch-b-b1p"
    assert row["created_at"] == row["updated_at"]
    assert datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")).tzinfo == timezone.utc
    before = selected_row(published_bytes(BASE, PAPERS), TARGETS[rid])
    assert all(row[key] == before[key] for key in ("title", "year", "doi", "openalex_url"))
    identity = "|".join(" ".join(row[key].split()).casefold() for key in ("review_queue", "target_type", "doi", "openalex_url", "title", "year", "institution"))
    assert "review:" + digest(identity.encode())[:20] == IDS[rid]
    note = row["review_note"]
    assert note.startswith(f"{rid} PROPOSE_CORRECTION_ACCEPTED: Batch B review {rid};")
    assert all(value in note for value in (POLICIES[rid], PDF_HASHES[rid], ";".join(TYPES[rid]), "no_action_after_review means the approved correction is complete"))
    destination = tmp_path / "review_decisions.csv"
    raw = (ROOT / DECISIONS).read_bytes()
    destination.write_bytes(raw)
    assert upsert_review_decision(row, path=destination) == row
    assert destination.read_bytes() == raw


def test_only_original_R024_R482_close_and_all_unrelated_pending_actions_survive():
    old = accounting(csv_records(published_bytes(BASE, DECISIONS)), published_context(BASE)["papers"])
    new = accounting(csv_records(published_bytes(PUBLISHED, DECISIONS)), published_context(PUBLISHED)["papers"])
    assert new == packet()["batch_b_accounting"]
    keys = ("historical_actions", "historical_papers", "historical_unresolved_actions", "historical_unresolved_papers", "active_public_unresolved_actions", "active_public_unresolved_papers")
    assert [old[key] for key in keys] == [159, 148, 135, 125, 133, 123]
    assert [new[key] for key in keys] == [159, 148, 133, 123, 131, 121]
    assert set(new["closed_review_ids"]) - set(old["closed_review_ids"]) == set(TARGETS)
    for key in ("historical_unresolved_review_ids", "active_public_unresolved_review_ids"):
        assert new[key] == [rid for rid in old[key] if rid not in TARGETS]
        assert {"R234", "T046", "T093", "T608", "T526", "P526"} <= set(new[key])
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    for rid, pid in TARGETS.items():
        assert [(row["review_id"], row["dimension"]) for row in ledger if row["paper_id"] == pid] == [(rid, "research_types")]


def test_R024_R3_is_an_independent_primary_study_with_retained_method_and_qualified_mechanisms():
    r = science("R024")
    assessment = r["contribution_evaluation"]
    assert assessment["provisional_outcome"] == "ANALYSIS_STUDY_ADDITION_SUPPORTED"
    assert assessment["proposed_complete_research_types"] == TYPES["R024"]
    assert assessment["method_retained"] and assessment["scientific_evidence_sufficient"]
    assert "without retaining one proposed specific trained detector" in assessment["rationale"]
    assert "routine model tuning" in assessment["why_not_routine_method_validation_only"]
    assert "causal" in assessment["contrary_interpretation"] or "confound" in assessment["contrary_interpretation"]
    assert len(r["scientific_question_matrix"]) == 20 and all(row["primary_locators"] for row in r["scientific_question_matrix"])
    assert assessment["confidence"] == {"contribution_role": "medium-high", "scientific_generalization": "medium-low", "operational_reproducibility": "low"}


def test_R024_architecture_level_pair_protocol_does_not_turn_into_instance_or_authenticity_claim():
    r = science("R024")
    q = {row["number"]: row for row in r["scientific_question_matrix"]}
    assert "Architecture-level" in q[1]["finding"] and "Instance-level" in q[1]["finding"]
    assert q[8]["evidence_status"] == "NOT_EVALUATED"
    assert q[10]["evidence_status"] == "NOT_DIRECTLY_ESTABLISHED"
    assert q[13]["evidence_status"] == q[14]["evidence_status"] == "UNVERIFIED"
    assert r["scope_boundary"]["no_detection_from_binary_pair_labels"] is True
    assert r["scope_boundary"]["T024_reopened"] is False
    sizes = r["quantitative_findings"]["sample_sizes"]
    assert sizes["training_pairs"] == sizes["training_subsets"] * 4 * sizes["training_N"] == 224000
    assert sizes["test_pairs"] == sizes["test_subsets"] * 4 * sizes["test_N"] == 68000
    assert sizes["unique_images_not_reported"] is True


def test_R024_corrected_raster_table_cells_and_negative_transfer_remain_separate_from_universal_claims():
    tables = {table["id"]: table for table in case("R024")["numerical_transcription"]["tables"]}
    assert sum(table["cell_count"] for table in tables.values()) == 252
    assert tables["Table2"]["rows"][-1] == ["Mean", 63.8, 64.2, 69.9, 72.2, 75.7, 85.6]
    t2 = {row[0]: row[1:] for row in tables["Table2"]["rows"]}
    t3 = {row[0]: row[1:] for row in tables["Table3"]["rows"]}
    assert t2["LDM_100"][0] == 68.3 > t2["LDM_100"][4] == 67.8
    assert t3["Glide_50_27"][1] == 74.4  # Corrected projection, not frozen scratch's 71.4.
    assert t3["AttGAN"][4] == 76.0 > t3["AttGAN"][2] == 74.8
    assert t3["AttGAN"][1] == 80.6 > t3["AttGAN"][3] == 73.7
    assert t3["RelGAN"][1] == 80.3 > t3["RelGAN"][3] == 71.1
    q = science("R024")["quantitative_findings"]["Figures1_2_means"]
    assert q == {"NPR_frozen_finetuned_accuracy": [78.1, 81.0], "POSE_frozen_finetuned_accuracy": [74.1, 76.6]}
    assert science("R024")["negative_and_contradictory_evidence"]


def test_R024_actual_README_only_release_and_original_author_checker_failure_are_preserved():
    r = science("R024")
    release = r["release_status"]
    assert release["pinned_revision"] == "32456adac2e97de8c906eb378bd332d402a62099"
    assert release["tree_truncated"] is False and release["paths"] == ["README.md"]
    assert release["readme_bytes"] == 349 and release["readme_paper_link"] == "placeholder"
    for key in ("executable_code_present", "dataset_artifacts_present", "weights_present", "splits_present", "license_file_present", "numerical_reproduction"):
        assert release[key] is False
    assert r["manuscript_identity"]["original_literal_receipt"]["sha256"] == "05a264ea54f743b196979e9eb75b3bbb0745dc8fe7360652473391b9e2029dbb"
    assert r["manuscript_identity"]["printed_copyright_and_citation_year"] == 2027
    assert selected_row((ROOT / PAPERS).read_bytes(), TARGETS["R024"])["year"] == "2026"


def test_R482_R2_support_is_reusable_detection_protocol_not_extra_images_or_source_attribution():
    r = science("R482")
    assert r["provisional_outcome"] == "BENCHMARK_ADDITION_SUPPORTED"
    assert r["proposed_complete_research_types"] == TYPES["R482"]
    assert r["evidence_scientifically_sufficient"] is True
    assert len(r["benchmark_questions"]) == 20
    assert r["current_tasks"] == ["detection"] and r["current_research_types"] == ["method", "dataset"]
    assert r["policy"]["policy_id"] == "R2"
    assert "reusable" in r["judgment_reason"].lower()
    assert "large" in r["judgment_reason"].lower() or "independent" in r["judgment_reason"].lower()
    assert all(row["locator"] for row in r["benchmark_questions"])


def test_R482_search_date_selection_and_release_do_not_become_verified_splits_or_semantic_oracle():
    r = science("R482")
    q = {row["id"]: row for row in r["benchmark_questions"]}
    assert "2021-01-01" in q["B02"]["finding"]
    assert "globally unique" in q["B05"]["finding"]
    assert "not distributions of reverse-search matching scores" in q["B08"]["finding"]
    assert "not constitute cross-split" in q["B11"]["finding"]
    release = case("R482")["manuscript_and_transport_provenance"]["release"]
    for key in ("archive_contents_inspected", "archive_saved", "archive_extracted", "executable_code_verified", "scoring_interface_verified", "split_membership_verified", "license_verified"):
        assert release[key] is False
    assert release["pinned_revision"] is None and "403" in release["pin_blocker"]
    assert release["public_preview_links"] == 13 and release["no_further_archive_probes"] is True


def test_R482_FPR_real_pool_change_preserves_fixed_recall_and_training_configuration():
    table = case("R482")["numerical_transcription"]["Table2"]
    assert table["metric_columns"][:2] == ["UFD FPR@0.8 recall: ProGAN+LSUN", "UFD FPR@0.8 recall: SD+LAION"]
    rows = {(row[0], row[1]): row[2:] for row in table["rows"]}
    assert rows["DALL-E2", "LAION"][:2] == [0.233, 0.043]
    assert rows["DALL-E2", "RIS"][:2] == [0.457, 0.406]
    assert [rows["Imagen", source][1] for source in ("LAION", "WebLI", "RIS")] == [0.360, 0.664, 0.720]
    assert [rows["Imagen", source][2:] for source in ("LAION", "WebLI", "RIS")] == [[127.1, 2.1], [101.9, 1.2], [83.6, 0.2]]


def test_R482_AUROC_average_uses_all18_rows_and_baseline_counterexamples_survive():
    table = case("R482")["numerical_transcription"]["Table3"]
    rows = table["rows"]
    assert len(rows) == 19 and rows[-1][0] == "Average printed"
    assert table["metric"] == "AUROC, scale 0–1"
    academic = [row for row in rows[:-1] if "(A)" in row[0]]
    synris = [row for row in rows[:-1] if "(A)" not in row[0]]
    assert len(academic) == 3 and len(synris) == 15
    for column, printed in ((5, 0.798), (9, 0.759)):
        assert rows[-1][column] == printed
        assert round(sum(row[column] for row in rows[:-1]) / 18, 3) == printed
    assert round(sum(row[9] for row in synris) / 15, 3) != 0.759
    by_name = {row[0]: row[1:] for row in rows}
    assert by_name["DALL-E2"][7] == 0.776 > by_name["DALL-E2"][8] == 0.747
    assert by_name["SDXL"][5] == 0.814 > by_name["SDXL"][8] == 0.807
    assert "LDM:" in table["columns"][6]


def test_R482_context_separated_Table3_Table4_differences_are_not_reconciled_to_make_uniform_gains():
    q = case("R482")["numerical_transcription"]
    t3 = {row[0]: row[1:] for row in q["Table3"]["rows"]}
    t4 = {row[0]: row[1:] for row in q["Table4"]["rows"]}
    assert [t3["SDXL"][4], t3["SDXL"][8]] == [0.764, 0.807]
    assert [t4["SDXL"][2], t4["SDXL"][5]] == [0.691, 0.884]
    assert t4["DALL-E3"][1] == 0.672 > t4["DALL-E3"][2] == 0.642
    assert science("R482")["contrary_or_limiting_evidence"]


def test_T024_prior_resolution_all_task_provenance_and_history_are_preserved_without_new_terminal():
    old, new = selected_row(published_bytes(BASE, TAXONOMY), TARGETS["R024"]), selected_row((ROOT / TAXONOMY).read_bytes(), TARGETS["R024"])
    for key in old:
        if key in {"tasks", "image_scopes"} or key.startswith("tasks_") or key.startswith("image_scopes_"):
            assert new[key] == old[key]
    source_hashes = original()["preservation"]["authoritative_and_prior_artifact_sha256"]["T024_published_task_history_sha256"]
    assert len(source_hashes) == 2
    for path, sha in source_hashes.items():
        assert digest((ROOT / path).read_bytes()) == digest(published_bytes(BASE, path)) == sha
    task_action = original()["baseline_recomputed"]["T024_historical_action"]
    assert task_action["review_id"] == "T024" and task_action["dimension"] == "tasks"
    assert task_action["current_tasks"] != TASKS["R024"]  # Historical context is not today's authoritative task.
    rows = read_review_decisions(ROOT / DECISIONS)
    assert "T024" not in terminal(rows)
    assert not [row for row in rows if re.search(r"^(?:Batch B review )?T024(?:;|\s+PROPOSE_)", row["review_note"])]


def test_original_retrieval_failures_two_complete_manuscripts_and_zero_adjudication_sources():
    retrieval = packet()["retrieval_accounting"]
    assert retrieval == original()["retrieval_accounting"]
    assert retrieval["whole_B1P_new_complete_primary_manuscripts"] == retrieval["primary_PDF_transport_attempts"] == 2
    assert retrieval["per_paper"] == {"R024": 1, "R482": 1}
    for key in ("recovery_new_complete_manuscripts", "recovery_primary_PDF_transport_attempts", "new_alternate_versions", "partial_responses_used_as_complete", "supplements_saved", "dataset_payloads_saved", "model_weights_saved", "complete_repository_clones"):
        assert retrieval[key] == 0
    assert "transfer bytes unknown" in retrieval["archive_URL_probe"]
    assert packet()["adjudication"]["no_new_scientific_source_retrieval"] is True
    assert case("R024")["manuscript_and_transport_provenance"]["retrieval_events"] == record(original(), "R024")["manuscript_and_transport_provenance"]["retrieval_events"]


def test_public_delta_is_exactly_two_type_reason_updates_with_672_other_records_unchanged():
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


def test_actual_map_dependents_only_update_type_metadata_without_new_relationships():
    old = {row["id"]: row for row in json.loads(published_bytes(BASE, PUBLIC[1]))["records"]}
    new = {row["id"]: row for row in json.loads(published_bytes(PUBLISHED, PUBLIC[1]))["records"]}
    assert old.keys() == new.keys() and len(new) == 1410
    dependents = {key for key, row in old.items() if row.get("paper_id") in TARGETS.values()}
    changed = {key for key in old if old[key] != new[key]}
    assert changed == dependents and dependents
    inverse = {pid: rid for rid, pid in TARGETS.items()}
    for key, row in old.items():
        expected = deepcopy(row)
        if key in dependents:
            expected["research_types"] = TYPES[inverse[row["paper_id"]]]
            expected["taxonomy_review"]["research_types"]["reason"] = selected_row(published_bytes(PUBLISHED, TAXONOMY), row["paper_id"])["research_types_review_reason"]
        assert new[key] == expected, key
    assert packet()["semantic_delta"]["changed_map_rows"] == len(changed)
    for path in PUBLIC:
        before_doc, after_doc = json.loads(published_bytes(BASE, path)), json.loads(published_bytes(PUBLISHED, path))
        oldmeta, newmeta = deepcopy(before_doc["metadata"]), deepcopy(after_doc["metadata"])
        oldmeta.pop("public_preview_generated_at", None); newmeta.pop("public_preview_generated_at", None)
        assert oldmeta == newmeta
        assert {key: value for key, value in before_doc.items() if key not in {"records", "metadata"}} == {key: value for key, value in after_doc.items() if key not in {"records", "metadata"}}


def test_counts_recompute_from_public_rows_with_only_benchmark_and_analysis_additions():
    old, live = published_context(BASE), published_context(PUBLISHED)
    assert old["counts"] == live["counts"] == packet()["corpus_counts"] == CURRENT_CORPUS_COUNTS
    def totals(context):
        return Counter(label for row in context["papers"].values() for dimension in ("tasks", "research_types") for label in row[dimension])
    before, after = totals(old), totals(live)
    assert not before - after and after - before == {"benchmark": 1, "analysis_study": 1}
    assert after == packet()["taxonomy_counts"]
    assert totals(load_context()) == CURRENT_TAXONOMY_TOTALS
    assert after == {"detection": 621, "source_attribution": 84, "localization": 45, "method": 578, "dataset": 138, "benchmark": 96, "survey": 21, "analysis_study": 85}
    for key in ("tasks", "image_scopes"):
        assert {pid: row[key] for pid, row in old["papers"].items()} == {pid: row[key] for pid, row in live["papers"].items()}


def test_original_questions_locked_policies_and_all_unrelated_authority_are_immutable():
    ledger = {row["review_id"]: row for row in load_queues()["taxonomy_review"]["records"]}
    policies = {row["policy_id"]: row for row in json.loads((ROOT / (AUDIT + "batch_c_policy_decisions.json")).read_bytes())["policies"]}
    for rid in TARGETS:
        assert case(rid)["original_review"] == ledger[rid]
        assert original()["locked_policy_ledger"]["policies"][POLICIES[rid]] == policies[POLICIES[rid]]
    # These three publication-dependent tables now have an approved B5 successor.
    # Check their original transaction at its immutable endpoint; every other
    # path, original question and locked policy remains a live byte guard.
    publication_successor_paths = {
        "data/curated/publication_overrides.csv",
        "data/curated/venue_aliases.csv",
        "data/manual/missing_author_mappings_report.csv",
    }
    allowed = {PAPERS, TAXONOMY, DECISIONS, *PUBLIC}
    for path in baseline_paths("data/curated", "data/manual", "web/data"):
        if path not in allowed:
            observed = published_bytes(PUBLISHED, path) if path in publication_successor_paths else (ROOT / path).read_bytes()
            assert observed == published_bytes(BASE, path), path
    for name in ("taxonomy_review", "publication_metadata_review", "relationship_review", "unmapped_papers", "batch_c_policy_decisions"):
        path = AUDIT + name + ".json"
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_prior_30_packets_C13_import39_and_historical_fixture_bytes_survive():
    prior = original()["preservation"]["authoritative_and_prior_artifact_sha256"]["prior_B1A_O_artifact_sha256"]
    assert len(prior) == 30
    for path, sha in prior.items():
        assert digest((ROOT / path).read_bytes()) == digest(published_bytes(BASE, path)) == sha
    for path in baseline_paths("tests/fixtures"):
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path
    debt = original()["baseline_recomputed"]["batch_c_deferred"]
    assert debt["total_actions"] == 41 and debt["resolved"] == 28
    assert debt["total_unresolved"] == debt["external_unresolved"] == len(debt["remaining_external_ids"]) == 13
    assert debt["maintainer_judgments"] == 0
    assert packet()["baseline_recomputed"]["batch_c_deferred"] == debt
    inventory = original()["baseline_recomputed"]["separate_import_inventory"]
    assert inventory["imported_papers"] == inventory["unmapped"] == len(inventory["candidate_to_paper"]) == 39
    assert inventory["relationships"] == 0
    assert packet()["baseline_recomputed"]["separate_import_inventory"] == inventory
    for pid in inventory["candidate_to_paper"].values():
        assert load_context()["papers"][pid] == published_context(BASE)["papers"][pid]


def test_frozen49_original_receipts_and_blocked_NeurIPS_status_survive():
    path = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT / path).read_bytes()
    assert raw == published_bytes(BASE, path)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for path, sha in frozen.items():
        assert digest(preserved_bytes(ROOT, path)) == sha, path
    assert packet()["neurips_status"] == "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"


def test_original_evidence_worker_results_and_report_are_not_relabelled_as_adjudication_runs():
    light = original()["lightweight_validation"]
    assert light["worker_checks"]["R024"]["checks_passed"] == 65
    assert light["worker_checks"]["R482"]["checks_passed"] == 67
    assert light["worker_checks"]["R024"]["checks_failed"] == light["worker_checks"]["R482"]["checks_failed"] == 0
    assert light["full_suite_run"] is light["exporter_run"] is False
    report = (ROOT / REPORT).read_text()
    assert archived_bytes("report").decode() in report
    for value in (*IDS.values(), *PDF_HASHES.values(), "R024", "R482", "T024", "method;analysis_study", "method;dataset;benchmark", "224,000", "68,000", "0.043", "0.406", "18", BASE):
        assert value in report


@pytest.mark.parametrize("rid", TARGETS)
def test_accepted_provenance_binds_policy_source_and_scope_to_actual_authoritative_fields(rid):
    accepted = case(rid)["adjudication"]
    assert accepted["accepted_policy"] == POLICIES[rid]
    assert accepted["previous_research_types"] == BEFORE[rid] and accepted["final_research_types"] == TYPES[rid]
    assert accepted["primary_source_sha256"] == PDF_HASHES[rid]
    assert accepted["review_action_closed"] == rid
    assert accepted["new_historical_review_actions"] == accepted["task_decisions_created"] == 0
    taxonomy = selected_row((ROOT / TAXONOMY).read_bytes(), TARGETS[rid])
    assert accepted["accepted_scientific_rationale"] == taxonomy["research_types_review_reason"]
    assert accepted["numerical_and_source_limits"] == taxonomy["research_types_evidence_excerpt"]
    assert accepted["primary_source"] == taxonomy["research_types_evidence_source"]
    for path in (PAPERS, TAXONOMY):
        assert accepted["authoritative_csv_updates"][path] == packet()["adjudication"]["csv_updates"][path][TARGETS[rid]]
    if rid == "R024":
        for token in ("224000 training pairs", "68000 testing pairs", "not unique-image counts", "63.8/64.2", "69.9/72.2", "75.7/85.6", "78.1 to 81.0", "74.1 to 76.6", "76.0", "74.8", "README-only", "2027"):
            assert token in taxonomy["research_types_evidence_excerpt"]
    else:
        for token in ("SD-trained UFD", "recall 0.8 fixed", "FPR LAION 0.043", "RIS 0.406", "not fake detection accuracy", "18 rows including three academic", "0.776", "0.747", "0.814", "0.807", "unreconciled", "not verified"):
            assert token in taxonomy["research_types_evidence_excerpt"]
