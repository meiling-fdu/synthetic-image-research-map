"""T631 closes without taxonomy edits; T046 and prior evidence remain intact."""
from collections import Counter
import base64
from functools import lru_cache
import gzip
import hashlib
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

ROOT = Path(__file__).resolve().parents[1]
BASE = "3feff7d6b609183cb8dda4949d2c087e77639003"
# B1G's exact transaction and source hashes belong to its published endpoint.
PUBLISHED = "445b4f8cc7257b3c87868a666bce43d8c20bda0d"
DECISIONS = "data/curated/review_decisions.csv"
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1g_2026_10_19/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1g_2026_10_19.md"
FIXTURES = "tests/fixtures/historical_test_fixture_manifest.json"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
T631 = "curated:170f07b3d7020611e566"
T046 = "curated:9b7e6c57a9f75e06fddf"
DECISION_ID = "review:09ce07963903ecd891c5"
PDF_URL = ("https://openaccess.thecvf.com/content_ICCV_2019/papers/"
           "Yu_Attributing_Fake_Images_to_GANs_Learning_and_Analyzing_GAN_Fingerprints_ICCV_2019_paper.pdf")
PDF_SHA256 = "be717607d2204d42d4a8e96f092bcbbef4e749a43df587bd9e0940afea5cebea"
EVIDENCE_HASHES = {
    "manifest": "b30253c33060547a412326b12d62725c575bfd9dd8025a5553b91b2b98afbfbf",
    "report": "7b7d1d6a65b1633a4b2e50c91a42d12abd5bda8680134a90ee702fd60d13d8fb",
}
CORPUS = {"public": 674, "formal": 557, "mapped": 613, "unmapped": 61,
          "relationship_rows": 1410, "unique_paper_institution_pairs": 1410}
TAXONOMY = {"detection": 621, "source_attribution": 84, "localization": 45,
            "method": 579, "dataset": 134, "benchmark": 90, "survey": 21,
            "analysis_study": 81}
REPAIR_FILES = (
    "docs/historical_test_repair_2026_10_19.md",
    "docs/test_failure_root_cause_2026_10_18.md",
    "docs/testing.md",
    "requirements-test.txt",
    "scripts/restore_historical_test_fixtures.py",
    "tests/fixtures/historical_os_metadata/1d7480faeebe24871c938c8c1751eea1883ace7f057716eccfff35ec167a3079.gz",
    "tests/fixtures/historical_os_metadata/6df64df87f90aed4dee71be480b2e5d710d5aa2ab24924f04eb409432b83b773.gz",
    "tests/fixtures/historical_os_metadata/a68cb7b62b51611eadfae68c198f05dd4990a76e7cbfc523c33c74c7b7a1c3eb.gz",
    FIXTURES,
    "tests/public_refinement_snapshot.py",
    "tests/test_historical_test_fixtures.py",
    "tests/test_public_refinement_successors.py",
)
C13_FILES = (
    "data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
    "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
    "docs/corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md",
    "tests/test_corpus_quality_batch_c_closeout.py",
)


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
    assert len(raw) == archive["bytes"]
    assert digest(raw) == archive["sha256"] == EVIDENCE_HASHES[kind]
    return raw


@lru_cache
def original():
    return json.loads(archived_bytes("manifest"))


def record(data, review_id):
    matches = [row for row in data["records"] if row["review_id"] == review_id]
    assert len(matches) == 1
    return matches[0]


def terminal(decisions):
    result = {}
    for row in decisions:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        if match and row["action"] == "no_action_after_review":
            assert match[1] not in result, "A review must have one terminal decision"
            result[match[1]] = row["decision_id"]
    return result


@lru_cache
def baseline_paths(*prefixes):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "ls-tree", "-r", "--name-only", BASE,
         "--", *prefixes], cwd=ROOT, text=True).splitlines()


def accounting(decisions):
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    done = terminal(decisions)
    pending = [row for row in ledger if row["review_id"] not in done]
    public = published_context(PUBLISHED)["papers"]
    active = [row for row in pending if row["paper_id"] in public]
    return {
        "historical_actions": len(ledger),
        "historical_papers": len({row["paper_id"] for row in ledger}),
        "resolved_review_ids": sorted(done),
        "historical_unresolved_actions": len(pending),
        "active_public_unresolved_actions": len(active),
        "active_public_unresolved_papers": len({row["paper_id"] for row in active}),
        "active_public_unresolved_review_ids": [row["review_id"] for row in active],
    }


@pytest.mark.parametrize("kind", ["manifest", "report"])
def test_complete_original_packet_is_losslessly_archived_with_fixed_hashes(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest", "report"}


def test_exactly_one_T631_terminal_append_preserves_every_prior_byte_and_decision():
    before = published_bytes(BASE, DECISIONS)
    after = published_bytes(PUBLISHED, DECISIONS)
    assert after.startswith(before)
    old, rows = csv_records(before), csv_records(after)
    # Later terminal actions append; the complete accepted B1G bytes survive.
    assert (ROOT / DECISIONS).read_bytes().startswith(after)
    live = read_review_decisions(ROOT / DECISIONS)
    assert sum(row["decision_id"] == DECISION_ID for row in live) == 1
    assert len(old) == 85 and len(rows) == 86
    assert rows[:-1] == old
    assert len({row["decision_id"] for row in rows}) == len(rows)
    assert terminal(rows) == {**terminal(old), "T631": DECISION_ID}
    row = rows[-1]
    assert row["decision_id"] == DECISION_ID
    assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
    assert row["target_type"] == "paper"
    assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
    assert row["created_by"] == "maintainer-approved-batch-b-b1g"
    assert row["created_at"] and row["created_at"] == row["updated_at"]
    assert row["doi"] == "10.1109/iccv.2019.00765"
    assert row["openalex_url"] == "https://openalex.org/W2991318208"
    assert row["institution"] == "" and row["year"] == "2019"
    identity = "|".join(" ".join(row[key].split()).casefold() for key in
                        ("review_queue", "target_type", "doi", "openalex_url", "title", "year", "institution"))
    assert "review:" + digest(identity.encode())[:20] == DECISION_ID
    for token in ("Batch B review T631;", "SUPPORTED_NO_CHANGE", "source_attribution",
                  "method", "99.43", "98.58", "99.14", "97.04", PDF_URL, PDF_SHA256):
        assert token in row["review_note"]
    adjudication = packet()["adjudication"]
    assert adjudication["decision_id"] == DECISION_ID
    assert adjudication["terminal_decision"] == row
    assert adjudication["outcome"] == "SUPPORTED_NO_CHANGE"
    assert adjudication["before_registry_sha256"] == digest(before)
    assert adjudication["after_registry_sha256"] == digest(after)


def test_T631_decision_upsert_is_idempotent_without_timestamp_or_byte_churn(tmp_path):
    path = tmp_path / "review_decisions.csv"
    before = (ROOT / DECISIONS).read_bytes()
    path.write_bytes(before)
    row = next(row for row in read_review_decisions(path) if row["decision_id"] == DECISION_ID)
    assert upsert_review_decision(row, path=path) == row
    assert path.read_bytes() == before


@pytest.mark.parametrize("paper_id,tasks", [(T631, "source_attribution"), (T046, "detection")])
def test_selected_canonical_and_taxonomy_rows_preserve_all_fields_and_method_type(paper_id, tasks):
    for path in ("data/curated/papers.csv", "data/curated/paper_taxonomy.csv"):
        old = [row for row in csv_records(published_bytes(BASE, path)) if row["paper_id"] == paper_id]
        current = [row for row in csv_records((ROOT / path).read_bytes()) if row["paper_id"] == paper_id]
        assert len(old) == len(current) == 1 and current == old
        assert current[0]["tasks"] == tasks and current[0]["research_types"] == "method"
    public = load_context()["papers"][paper_id]
    assert public["tasks"] == [tasks] and public["research_types"] == ["method"]


def test_every_other_authoritative_table_and_public_output_preserves_complete_bytes():
    paths = baseline_paths("data/curated", "data/manual", "web/data")
    assert len(paths) > 30
    for path in paths:
        if path != DECISIONS:
            assert published_bytes(PUBLISHED, path) == published_bytes(BASE, path), path


def test_public_papers_relationships_and_taxonomy_totals_recompute_without_drift():
    before, current = published_context(BASE), published_context(PUBLISHED)
    assert current["papers"] == before["papers"]
    assert current["pairs"] == before["pairs"]
    assert current["counts"] == packet()["corpus_counts"] == CORPUS
    totals = Counter(label for paper in current["papers"].values()
                     for dimension in ("tasks", "research_types") for label in paper[dimension])
    assert totals == packet()["taxonomy_counts"] == TAXONOMY
    # Keep original579/81 evidence while validating the reviewed live corpus.
    live = load_context()
    assert live["counts"] == CURRENT_CORPUS_COUNTS
    assert Counter(label for paper in live["papers"].values()
                   for dimension in ("tasks", "research_types") for label in paper[dimension]) == CURRENT_TAXONOMY_TOTALS
    assert live["pairs"] == current["pairs"]
    for paper_id in (T631, T046):
        assert live["papers"][paper_id] == current["papers"][paper_id]


def test_original_scientific_evidence_and_provenance_are_retained_in_full():
    old, new = original(), packet()
    assert [row["review_id"] for row in new["records"]] == ["T046", "T631"]
    assert record(new, "T046") == record(old, "T046")
    accepted, prior = record(new, "T631"), record(old, "T631")
    for key in prior:
        if key not in {"maintainer_acceptance_pending", "review_closed",
                       "terminal_review_decision_created"}:
            assert accepted[key] == prior[key], key
    assert accepted["scientific_evidence"] == prior["scientific_evidence"]
    for key in ("retrieval_accounting", "locked_policies", "source_files_sha256",
                "operational_source_files", "separate_import_review_inventory", "batch_c_deferred_accounting"):
        assert new[key] == old[key], key
    for key in ("scope", "validation", "integrity", "final_git_requirements",
                "accounting_effect", "batch_b_accounting"):
        assert new["evidence_only_" + key] == old[key], key


def test_T631_acceptance_closes_only_the_review_registry_and_keeps_science_unchanged():
    case = record(packet(), "T631")
    assert case["accepted_outcome"] == "SUPPORTED_NO_CHANGE"
    assert case["terminal_review_decision_id"] == DECISION_ID
    assert case["maintainer_acceptance_pending"] is False
    assert case["review_closed"] is True and case["terminal_review_decision_created"] is True
    assert case["authoritative_changes_applied"] is False
    assert case["review_registry_change_applied"] is True
    assert case["proposed_taxonomy_correction"] is None
    assert case["adjudication"] == packet()["adjudication"]
    assert case["adjudication"]["retained_tasks"] == ["source_attribution"]
    assert case["adjudication"]["retained_research_types"] == ["method"]
    assert case["adjudication"]["scientific_data_changed"] is False
    assert "main paper" in case["adjudication"]["main_paper_limitation"].lower()


def test_official_ICCV_identity_main_paper_and_version_boundaries_remain_explicit():
    evidence = record(packet(), "T631")["scientific_evidence"]
    identity = evidence["identity"]
    assert identity["canonical_doi"] == "10.1109/iccv.2019.00765"
    assert identity["source_url"] == PDF_URL and identity["sha256"] == PDF_SHA256
    assert identity["bytes"] == 1860415 and identity["pdf_pages"] == 11
    assert identity["printed_pages"] == "7556–7566"
    assert identity["canonical_authors"] == ["Ning Yu", "Larry Davis", "Mario Fritz"]
    assert "not arXiv1811.08180v3" in identity["version_boundary"]
    provenance = evidence["retrieval_provenance"]
    assert provenance["successful_new_full_manuscripts"] == provenance["full_text_attempts"] == 1
    for key in ("automatic_retries", "separate_supplements_retrieved", "extra_versions_retrieved",
                "code_or_dataset_downloads"):
        assert provenance[key] == 0
    assert evidence["coverage"]["pages_read_completely"] == list(range(1, 12))


def test_real_inclusive_source_accuracy_is_not_promoted_to_an_independent_binary_metric():
    evidence = record(packet(), "T631")["scientific_evidence"]
    results = evidence["quantitative_results"]
    table1, table3 = results["Table1_p6_printed7561"], results["Table3_p6_printed7561"]
    assert table1["label_set"] == ["real", "ProGAN", "SNGAN", "CramerGAN", "MMDGAN"]
    assert table1["dataset_order"] == table3["dataset_order"] == ["CelebA", "LSUN"]
    assert table1["source_accuracy_percent"]["Ours"] == [99.43, 98.58]
    assert table3["source_accuracy_percent"]["Ours"] == [99.14, 97.04]
    assert table3["label_set"] == "real plus10ProGAN_seed_v#i sources"
    assert "not separately reported binary" in results["metric_boundary"]
    assert "cross-entropy" in evidence["method_and_label_space"]["main_loss"]
    assert "known source" in evidence["experimental_protocol"]["known_source_boundary"]
    issues = {row["issue"]: row for row in evidence["contradictions_and_limitations"]}
    assert {"Strong real-versus-GAN language", "N+1classification versus independent binary detection",
            "Dataset sample counts", "Unreviewed supplementary material"} <= issues.keys()
    assert "authors explicitly claim" in issues["Strong real-versus-GAN language"]["finding"].lower()
    assert evidence["proposed_authoritative_tasks"] == ["source_attribution"]
    assert evidence["proposed_task_addition"] is None


def test_T046_mask_implementation_support_and_missing_published_spatial_results_stay_distinct():
    case = record(packet(), "T046")
    evidence = case["scientific_evidence"]
    assert case["provisional_disposition"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert case["review_closed"] is False and case["terminal_review_decision_created"] is False
    assert case["proposed_authoritative_tasks"] is None
    assert case["administrative_retained_tasks"] == ["detection"]
    primary = evidence["primary_retrieval"]
    assert primary["http_status"] == 403 and primary["response_is_manuscript"] is False
    assert primary["attempts"] == 1 and primary["successful_full_manuscripts"] == 0
    assert primary["document_version_verified"] is False
    assert primary["no_more_full_requests"] is True
    assert primary["response_sha256"] == "6fbd1f11ecffaa708cef94dfce330190363d1f499854e0c5a3c00d8a6b6ab178"
    support = evidence["implementation_details_supported_but_not_publisher_verified"]
    assert "224" in support["default_spatial_output"] and "raw mask logits" in support["default_spatial_output"]
    assert "BCE-with-logits" in support["training_loss"]
    assert "sigmoid" in support["mask_training_threshold"]
    assert "raw returned mask" in support["evaluation_spatial_rule"]
    assert "no verified immutable commit" in evidence["supporting_source_identity"]["code_version_boundary"]
    assert evidence["supporting_source_identity"]["code_execution"] is False
    assert len(evidence["nine_requested_scientific_checks"]) == 9
    quantitative = evidence["quantitative_evidence"]
    readme = quantitative["README_detection_values"]
    assert readme["ID_LA_Inpainting"]["F1_percent"] == 94.80
    assert readme["ID_Inpainting"]["F1_percent"] == 90.46
    assert "not independently verified paper spatial metrics" in readme["metric_interpretation"]
    assert quantitative["published_spatial_values"]["status"] == "UNAVAILABLE_NOT_NEGATIVE_EVIDENCE"
    assert quantitative["published_spatial_values"]["pixel_or_region_metric_values"] is None
    assert evidence["scientific_sufficiency"]["sufficient_to_propose_localization_addition"] is False


def test_exact_manuscript_budget_and_failed_access_receipts_are_not_reclassified():
    retrieval = packet()["retrieval_accounting"]
    assert retrieval == original()["retrieval_accounting"]
    assert retrieval["successful_new_full_manuscripts"] == 1
    assert retrieval["full_text_attempts"] == 2 and retrieval["maximum_attempts_used_per_case"] == 1
    assert retrieval["by_case"]["T046"]["successful_full_manuscripts"] == 0
    assert retrieval["by_case"]["T046"]["http_status"] == 403
    assert retrieval["by_case"]["T631"]["successful_full_manuscripts"] == 1
    assert retrieval["by_case"]["T631"]["sha256"] == PDF_SHA256


def test_original_review_questions_and_locked_policies_remain_immutable():
    queues = load_queues()
    taxonomy = {row["review_id"]: row for row in queues["taxonomy_review"]["records"]}
    for review_id in ("T046", "T631"):
        case = record(packet(), review_id)
        assert case["original_review"] == taxonomy[review_id]
        assert case["original_intake_question"] == record(original(), review_id)["original_intake_question"]
    policy_path = AUDIT + "batch_c_policy_decisions.json"
    assert (ROOT / policy_path).read_bytes() == published_bytes(BASE, policy_path)
    policies = json.loads((ROOT / policy_path).read_bytes())["policies"]
    assert packet()["locked_policies"] == [row for row in policies if row["policy_id"] in {"T1", "T2", "T3"}]
    for path in (AUDIT + name + ".json" for name in
                 ("taxonomy_review", "publication_metadata_review", "relationship_review", "unmapped_papers")):
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_accounting_recomputes_only_T631_closure_and_keeps_independent_questions_open():
    before = accounting(csv_records(published_bytes(BASE, DECISIONS)))
    rows = csv_records(published_bytes(PUBLISHED, DECISIONS))
    after = accounting(rows)
    assert before == original()["batch_b_accounting"] == packet()["evidence_only_batch_b_accounting"]
    assert after == packet()["batch_b_accounting"]
    assert before["historical_actions"] == after["historical_actions"] == 159
    assert before["historical_papers"] == after["historical_papers"] == 148
    assert [before[key] for key in ("historical_unresolved_actions", "active_public_unresolved_actions",
                                   "active_public_unresolved_papers")] == [149, 147, 136]
    assert [after[key] for key in ("historical_unresolved_actions", "active_public_unresolved_actions",
                                  "active_public_unresolved_papers")] == [148, 146, 135]
    assert set(after["resolved_review_ids"]) - set(before["resolved_review_ids"]) == {"T631"}
    assert after["active_public_unresolved_review_ids"] == [
        review for review in before["active_public_unresolved_review_ids"] if review != "T631"]
    assert {"T046", "T093", "T608", "T526", "P526"} <= set(after["active_public_unresolved_review_ids"])
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    still_pending = [row for row in ledger if row["review_id"] not in terminal(rows)]
    assert not [row for row in still_pending if row["paper_id"] == T631]
    live_done = terminal(read_review_decisions(ROOT / DECISIONS))
    assert live_done["T631"] == DECISION_ID
    assert {"T046", "T093", "T608", "T526", "P526"}.isdisjoint(live_done)


def test_historical_source_hashes_and_current_registry_hash_have_separate_meanings():
    old, new = original(), packet()
    assert new["source_files_sha256"] == old["source_files_sha256"]
    current = new["current_source_sha256"]
    assert current.keys() == old["source_files_sha256"].keys()
    assert {path for path, value in current.items() if value != old["source_files_sha256"][path]} == {DECISIONS}
    tracked = set(baseline_paths())
    fixture_entries = {entry["path"]: entry for entry in json.loads(published_bytes(BASE, FIXTURES))["entries"]}
    for path, expected in current.items():
        if path in tracked:
            # Recorded current hashes describe the published B1G endpoint.
            raw = published_bytes(PUBLISHED, path)
        else:
            # Authenticate ignored responses through declared committed snapshots,
            # without requiring the developer's runtime-cache destination to exist.
            entry = fixture_entries[path]
            assert entry["compression"] == "none"
            raw = published_bytes(BASE, entry["source"])
            assert digest(raw) == entry["sha256"] == entry["source_sha256"]
            assert len(raw) == entry["bytes"]
        assert digest(raw) == expected, path


def test_previous_twelve_batch_receipts_and_predecessor_repair_files_keep_original_bytes():
    receipts = original()["preservation"]["prior_B1A_to_B1F_artifact_sha256"]
    assert len(receipts) == 12
    for path, expected in receipts.items():
        assert digest(published_bytes(BASE, path)) == expected
        assert digest((ROOT / path).read_bytes()) == expected, path
    recorded = packet()["adjudication_baseline"]["predecessor_repair_sha256"]
    assert packet()["adjudication_baseline"]["commit"] == BASE
    assert set(recorded) == set(REPAIR_FILES) and len(recorded) == 12
    for path in REPAIR_FILES:
        assert recorded[path] == digest(published_bytes(BASE, path))
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_checksum_locked_neurips_snapshot_and_all_49_frozen_inputs_remain_exact():
    path = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT / path).read_bytes()
    assert raw == published_bytes(BASE, path)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for relative, expected in frozen.items():
        assert digest(preserved_bytes(ROOT, relative)) == expected, relative
    assert packet()["neurips_status"] == "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"


def test_batch_C_debts_and_separate_import_inventory_are_preserved_without_recounting_as_B():
    data, old = packet(), original()
    assert data["batch_c_deferred_accounting"] == old["batch_c_deferred_accounting"]
    debts = data["batch_c_deferred_accounting"]
    assert debts["total_actions"] == 41 and debts["resolved"] == 28
    assert debts["total_unresolved"] == debts["external_unresolved"] == 13
    assert debts["maintainer_judgments"] == 0 and len(debts["remaining_external_ids"]) == 13
    intake = data["separate_import_review_inventory"]
    assert intake == old["separate_import_review_inventory"]
    assert intake["imported_affiliation_debt_papers"] == 39
    assert intake["overlapping_taxonomy_review_papers"] == 14 and intake["held_candidates"] == 12
    for path in C13_FILES:
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_report_and_packet_consistently_record_acceptance_without_new_scientific_changes():
    data = packet()
    report = (ROOT / REPORT).read_text()
    assert data["scope"]["review_decisions_added"] == data["scope"]["review_actions_closed"] == 1
    assert data["scope"]["authoritative_scientific_changes"] == 0
    assert data["scope"]["exports_run"] == data["scope"]["full_suites_run"] == 0
    assert DECISION_ID in report and "SUPPORTED_NO_CHANGE" in report
    assert "T046" in report and "EVIDENCE_STILL_INSUFFICIENT" in report
    for token in ("99.43", "98.58", "99.14", "97.04", BASE,
                  "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"):
        assert token in report
    assert re.search(r"\b148\s*/\s*146\s*/\s*135\b", report)
    assert "accepted" in report.casefold() and "terminal decision" in report.casefold()
    assert "does not close T631" not in report
    assert data["adjudication"]["scientific_data_changed"] is False
    assert data["adjudication"]["terminal_decision"]["decision_id"] == DECISION_ID
