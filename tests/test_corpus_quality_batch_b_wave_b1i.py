"""B1I closes two bounded R2 reviews and adds only R574's benchmark role."""
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

ROOT = Path(__file__).resolve().parents[1]
BASE = "bb4b60b2ee612331b997d7482edaa1e9e657cff2"
# Whole-file transaction receipts describe the immutable published B1I endpoint.
PUBLISHED = "1221cf72f8f77ac3430cad49a49d074d82b36ec2"
TAXONOMY_TOTALS = {"detection": 621, "source_attribution": 84, "localization": 45,
                   "method": 578, "dataset": 134, "benchmark": 91, "survey": 21,
                   "analysis_study": 82}
PAPERS = "data/curated/papers.csv"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1i_2026_10_20/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1i_2026_10_20.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
FIXTURES = "tests/fixtures/historical_test_fixture_manifest.json"
TARGETS = {"R215": "curated:98977aa8b726ead071fe", "R574": "curated:297bed46b62fdf89c9ab"}
IDS = {"R215": "review:dccd35b22dfc68d14007", "R574": "review:ababbf1503d62744757e"}
EVIDENCE_HASHES = {
    "manifest": "110fc5406ea6ca1e1ff6b8233a72127f869532a8962e8a2b5fb71336eb1c54e3",
    "report": "36120f5d98e27237e6c6722cf8cf3a5c88ca4e95b0916232e613732baa06345c",
}
WORKER_HASHES = {
    "R215": "5d76d44bf0a948ba3a1261fdd7d005346f4dfb208721014e026b5a8bc41c7baa",
    "R574": "574edd2aae7ef4801e805264aaaf6cd706f5d729a97a20236d573634af0be5b9",
}
PDF_HASHES = {
    "R215": "f287854182676a679bde7ae3ce022fff0769b7ec792f3a31ec587125ccb558ec",
    "R574": "5ddd9e1df687106483b1d6f2504119042088daf818ad51521bb42a2f8157e891",
}
REPOSITORY_COMMIT = "185b25d9160e09b57c62cea23f08b2b126b62798"
# Filled from the independently reviewed byte-preserving transaction, not a runtime receipt.
CSV_UPDATES = {'data/curated/papers.csv': {'research_types': 'method;dataset;benchmark'},
 'data/curated/paper_taxonomy.csv': {'research_types': 'method;dataset;benchmark',
                                     'research_types_review_reason': 'R574 accepted under locked R2: '
                                                                     'the complete official CVF CVPR '
                                                                     '2023 Main accepted manuscript and '
                                                                     'pinned POSE split documentation '
                                                                     'establish an independently '
                                                                     'reusable OSMA evaluation '
                                                                     'framework with five split '
                                                                     'configurations, controlled '
                                                                     'seed/architecture/training-dataset '
                                                                     'scenarios, source labels, '
                                                                     'protocols, baselines and metrics. '
                                                                     'Add benchmark; retain method, '
                                                                     'dataset and source_attribution. '
                                                                     'Only split1 annotation contents '
                                                                     'were verified; full '
                                                                     'image/checkpoint availability, '
                                                                     'fixed deployment thresholds, '
                                                                     'numerical reproduction and '
                                                                     'IEEE-final/alternate-version '
                                                                     'equivalence remain unverified.',
                                     'research_types_evidence_tier': 'primary_paper',
                                     'research_types_evidence_source': 'https://openaccess.thecvf.com/content/CVPR2023/papers/Yang_Progressive_Open_Space_Expansion_for_Open-Set_Model_Attribution_CVPR_2023_paper.pdf',
                                     'research_types_evidence_excerpt': 'Sections 4.1 and Tables 1-4: '
                                                                        'five OSMA configurations, 15 '
                                                                        'known classes (14 generators '
                                                                        'plus real), 53 unknown '
                                                                        'generators (10 seed/22 '
                                                                        'architecture/21 dataset); '
                                                                        'Table 4 POSE accuracy/AUC/OSCR '
                                                                        '94.81/82.76/80.50, while PRNU '
                                                                        'seed AUC 69.20 exceeds POSE '
                                                                        '68.15. Official POSE commit '
                                                                        '185b25d9160e09b57c62cea23f08b2b126b62798 '
                                                                        'split1 annotations: train '
                                                                        '59998, validation 7500, '
                                                                        'closed-test 8000, unknown-test '
                                                                        '26500; 101998 distinct literal '
                                                                        'paths, no literal overlap. '
                                                                        'This verifies annotation '
                                                                        'protocol, not content '
                                                                        'independence, complete assets '
                                                                        'or numerical reproduction.',
                                     'audited_at': '2026-10-21'}}
CSV_AFTER_HASHES = {'data/curated/papers.csv': 'e0805a8bbaf5b3cf9364cdbeba8998c034590f21ff67c79156d455b458a198a1',
 'data/curated/paper_taxonomy.csv': '570744efad27779e397f7f836bd9344991a9df5d4d5a2fbf21397faa7dfaa24b'}


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
    rows = [row for row in data["records"] if row["review_id"] == review_id]
    assert len(rows) == 1
    return rows[0]


def selected_row(raw, paper_id):
    rows = [row for row in csv_records(raw) if row["paper_id"] == paper_id]
    assert len(rows) == 1
    return rows[0]


def terminal(rows):
    done = {}
    for row in rows:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        if match and row["action"] == "no_action_after_review":
            assert match[1] not in done, "Duplicate original-review terminal decision"
            done[match[1]] = row["decision_id"]
    return done


@lru_cache
def baseline_paths(*prefixes):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "ls-tree", "-r", "--name-only", BASE,
         "--", *prefixes], cwd=ROOT, text=True).splitlines()


def logical_csv_chunks(raw):
    lines = raw.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    chunks, start = [], 0
    for _ in reader:
        chunks.append(b"".join(lines[start:reader.line_num]))
        start = reader.line_num
    assert start == len(lines)
    return chunks


def accounting(rows, public):
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    done = terminal(rows)
    pending = [row for row in ledger if row["review_id"] not in done]
    active = [row for row in pending if row["paper_id"] in public]
    return {
        "historical_actions": len(ledger),
        "historical_papers": len({row["paper_id"] for row in ledger}),
        "closed_review_ids": sorted(done),
        "historical_unresolved_actions": len(pending),
        "historical_unresolved_papers": len({row["paper_id"] for row in pending}),
        "active_public_unresolved_actions": len(active),
        "active_public_unresolved_papers": len({row["paper_id"] for row in active}),
        "historical_unresolved_review_ids": [row["review_id"] for row in pending],
        "active_public_unresolved_review_ids": [row["review_id"] for row in active],
    }


@pytest.mark.parametrize("kind", ["manifest", "report"])
def test_original_two_paper_evidence_packet_is_portable_and_hash_exact(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest", "report"}
    assert original()["validation"]["status"] == "PASS"
    assert original()["validation"]["lightweight_checks_passed"] == 84
    assert original()["validation"]["independent_packet_review"]["passed"] == 32


@pytest.mark.parametrize("path", [PAPERS, TAXONOMY])
def test_only_R574_allowed_research_type_cells_change_and_all_other_bytes_survive(path):
    before_raw, after_raw = published_bytes(BASE, path), published_bytes(PUBLISHED, path)
    before, after = csv_records(before_raw), csv_records(after_raw)
    key = "taxonomy_id" if path == TAXONOMY else "paper_id"
    assert len(before) == len(after)
    assert [row[key] for row in before] == [row[key] for row in after]
    assert len({row[key] for row in before}) == len(before)
    assert {old["paper_id"] for old, new in zip(before, after) if old != new} == {TARGETS["R574"]}
    old, new = selected_row(before_raw, TARGETS["R574"]), selected_row(after_raw, TARGETS["R574"])
    assert {field for field in old if old[field] != new[field]} == CSV_UPDATES[path].keys()
    assert new == {**old, **CSV_UPDATES[path]}
    assert new["tasks"] == "source_attribution"
    assert new["image_scopes"] == "fully_generated"
    assert new["research_types"] == "method;dataset;benchmark"
    assert digest(after_raw) == CSV_AFTER_HASHES[path]
    old_chunks, new_chunks = logical_csv_chunks(before_raw), logical_csv_chunks(after_raw)
    assert len(old_chunks) == len(new_chunks) == len(before) + 1
    assert new_chunks[0] == old_chunks[0]
    for row, old_chunk, new_chunk in zip(before, old_chunks[1:], new_chunks[1:]):
        if row["paper_id"] != TARGETS["R574"]:
            assert new_chunk == old_chunk
    assert selected_row(after_raw, TARGETS["R215"]) == selected_row(before_raw, TARGETS["R215"])
    # Later approved papers may change, but both accepted B1I target rows stay exact.
    for rid in TARGETS:
        assert selected_row((ROOT / path).read_bytes(), TARGETS[rid]) == selected_row(after_raw, TARGETS[rid])


def test_R215_authoritative_rows_and_every_public_field_are_exactly_unchanged():
    for path in (PAPERS, TAXONOMY):
        old = selected_row(published_bytes(BASE, path), TARGETS["R215"])
        current = selected_row((ROOT / path).read_bytes(), TARGETS["R215"])
        assert current == old
        assert current["research_types"] == "method" and current["tasks"] == "detection"
    public = load_context()["papers"][TARGETS["R215"]]
    assert public == published_context(BASE)["papers"][TARGETS["R215"]]
    assert public["research_types"] == ["method"] and public["tasks"] == ["detection"]
    assert public["venue_track"].casefold() == "workshop"


def test_exactly_two_supported_terminal_appends_preserve_all_87_prior_rows_and_bytes():
    before, after = published_bytes(BASE, DECISIONS), published_bytes(PUBLISHED, DECISIONS)
    old, rows = csv_records(before), csv_records(after)
    assert after.startswith(before)
    assert len(old) == 87 and len(rows) == 89
    assert rows[:-2] == old
    assert len({row["decision_id"] for row in rows}) == len(rows)
    assert terminal(rows) == {**terminal(old), **IDS}
    assert [row["decision_id"] for row in rows[-2:]] == [IDS["R215"], IDS["R574"]]
    for review_id, row in zip(("R215", "R574"), rows[-2:]):
        assert row["decision_id"] == IDS[review_id]
        assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
        assert row["target_type"] == "paper" and row["institution"] == ""
        assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
        assert row["created_by"] == "maintainer-approved-batch-b-b1i"
        assert row["created_at"] == row["updated_at"]
        assert row["created_at"].startswith("2026-10-21T")
        assert datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")).tzinfo == timezone.utc
        prior = selected_row(published_bytes(BASE, PAPERS), TARGETS[review_id])
        for key in ("title", "year", "doi", "openalex_url"):
            assert row[key] == prior[key]
        identity = "|".join(" ".join(row[key].split()).casefold() for key in
                            ("review_queue", "target_type", "doi", "openalex_url", "title", "year", "institution"))
        assert "review:" + digest(identity.encode())[:20] == IDS[review_id]
        assert row["review_note"].startswith("Batch B review " + review_id + ";")
        assert packet()["adjudication"]["terminal_decisions"][review_id] == row
    adjudication = packet()["adjudication"]
    assert adjudication["decision_ids"] == IDS
    assert adjudication["registry_rows_before"] == 87 and adjudication["registry_rows_after"] == 89
    assert adjudication["prior_decision_bytes_preserved"] is True
    assert adjudication["before_registry_sha256"] == digest(before)
    assert adjudication["after_registry_sha256"] == digest(after)
    assert adjudication["existing_csv_cells_changed"] == 7
    assert len(adjudication["csv_changes"]) == 2
    for change in adjudication["csv_changes"]:
        path = change["path"]
        assert change["row_identity"] == {"paper_id": TARGETS["R574"]}
        assert change["after_fields"] == CSV_UPDATES[path]
        assert change["planned_after_sha256"] == CSV_AFTER_HASHES[path]
    live_raw = (ROOT / DECISIONS).read_bytes()
    live_rows = read_review_decisions(ROOT / DECISIONS)
    assert live_raw.startswith(after)
    for row in rows[-2:]:
        assert [item for item in live_rows if item["decision_id"] == row["decision_id"]] == [row]
    assert {rid: terminal(live_rows)[rid] for rid in IDS} == IDS


@pytest.mark.parametrize("review_id", ["R215", "R574"])
def test_each_terminal_upsert_is_idempotent_without_timestamp_or_byte_churn(tmp_path, review_id):
    path = tmp_path / "review_decisions.csv"
    raw = (ROOT / DECISIONS).read_bytes()
    path.write_bytes(raw)
    row = next(row for row in read_review_decisions(path) if row["decision_id"] == IDS[review_id])
    assert upsert_review_decision(row, path=path) == row
    assert path.read_bytes() == raw


def test_exactly_two_original_research_type_questions_close_and_no_D_actions_close():
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    before = accounting(csv_records(published_bytes(BASE, DECISIONS)), published_context(BASE)["papers"])
    after = accounting(csv_records(published_bytes(PUBLISHED, DECISIONS)), published_context(PUBLISHED)["papers"])
    assert after == packet()["batch_b_accounting"]
    assert [before[k] for k in ("historical_actions", "historical_papers", "historical_unresolved_actions",
                                "active_public_unresolved_actions", "active_public_unresolved_papers")] == [159, 148, 147, 145, 134]
    assert [after[k] for k in ("historical_actions", "historical_papers", "historical_unresolved_actions",
                               "active_public_unresolved_actions", "active_public_unresolved_papers")] == [159, 148, 145, 143, 132]
    assert after["historical_unresolved_papers"] == 134
    assert set(after["closed_review_ids"]) - set(before["closed_review_ids"]) == {"R215", "R574"}
    for key in ("historical_unresolved_review_ids", "active_public_unresolved_review_ids"):
        assert after[key] == [rid for rid in before[key] if rid not in TARGETS]
    for review_id, paper_id in TARGETS.items():
        assert [(row["review_id"], row["dimension"]) for row in ledger if row["paper_id"] == paper_id] == [(review_id, "research_types")]
    assert {"R267", "T046", "T093", "T608", "T526", "P526"} <= set(after["active_public_unresolved_review_ids"])
    live_rows = read_review_decisions(ROOT / DECISIONS)
    assert not {"P215", "P574", "T215", "T574"} & terminal(live_rows).keys()
    assert {"R267", "T046", "T093", "T608", "T526", "P526"} <= set(
        accounting(live_rows, load_context()["papers"])["active_public_unresolved_review_ids"])


def test_all_original_scientific_findings_policy_ambiguity_and_provenance_remain_lossless():
    old, new = original(), packet()
    assert [r["review_id"] for r in new["records"]] == ["R215", "R574"]
    flags = {"maintainer_acceptance_pending", "review_closed", "authoritative_changes_applied", "terminal_review_decision_created"}
    for rid in TARGETS:
        prior, accepted = record(old, rid), record(new, rid)
        for key in prior:
            if key not in flags:
                assert accepted[key] == prior[key], (rid, key)
        assert accepted["worker_scientific_review"] == prior["worker_scientific_review"]
        assert accepted["worker_review_sha256"] == WORKER_HASHES[rid]
        assert accepted["maintainer_acceptance_pending"] is False
        assert accepted["review_closed"] is True
        assert accepted["terminal_review_decision_created"] is True
        assert accepted["authoritative_changes_applied"] is (rid == "R574")
        assert accepted["terminal_review_decision_id"] == IDS[rid]
        assert accepted["accepted_outcome"] == {"R215": "SUPPORTED_NO_CHANGE", "R574": "PROPOSE_CORRECTION_ACCEPTED"}[rid]
        assert accepted["final_authoritative_taxonomy"] == {
            "tasks": ["detection"] if rid == "R215" else ["source_attribution"],
            "image_scopes": ["fully_generated"],
            "research_types": ["method"] if rid == "R215" else ["method", "dataset", "benchmark"],
        }
    for key in ("retrieval_accounting", "locked_policy_ledger", "source_files_sha256", "operational_review_sha256",
                "preservation", "batch_c_deferred_accounting", "separate_import_review_inventory", "independent_scientific_review"):
        assert new[key] == old[key], key
    for key in ("scope", "validation", "integrity", "corpus_counts", "taxonomy_counts", "batch_b_accounting",
                "accounting_effect", "final_git_requirements"):
        assert new["evidence_only_" + key] == old[key], key


def test_R215_conservative_R2_decision_preserves_the_independent_framework_counterargument():
    prior = record(original(), "R215")
    current = record(packet(), "R215")
    boundary = current["policy_boundary_review"]
    assert boundary == prior["policy_boundary_review"]
    assert boundary["concrete_missing_disqualifying_framework_criterion"] is None
    assert boundary["no_new_research_type_rule_proposed"] is True
    assert boundary["confidence"]["policy_threshold"] == "medium"
    assert boundary["conditional_complete_research_types"]["if_maintainer_accepts_table4_as_independently_reusable_systematic_comparative_framework"] == ["method", "benchmark"]
    assert boundary["conditional_complete_research_types"]["if_maintainer_treats_the_published_matrix_as_method_supporting_evaluation_only"] == ["method"]
    assert len(boundary["positive_framework_evidence"]) >= 4
    assert "code release" in boundary["reconsidered_boundary"]
    assert "not a necessary condition" in boundary["reconsidered_boundary"]
    row = next(r for r in read_review_decisions(ROOT / DECISIONS) if r["decision_id"] == IDS["R215"])
    note = row["review_note"]
    for token in ("SUPPORTED_NO_CHANGE", "R2", "method", "benchmark", "42", "15", "six", "89.54", "89.81", "75.63", "77.45", "92.94", "92.96", "97.16", "95.67", "medium"):
        assert token.casefold() in note.casefold()
    assert "permissive" in note.casefold()
    assert "code" in note.casefold() and "dataset" in note.casefold()


def test_R215_positive_comparison_and_negative_TAP_result_are_exact_and_version_bounded():
    evidence = record(packet(), "R215")["worker_scientific_review"]
    source = evidence["source"]
    assert source["sha256"] == PDF_HASHES["R215"] and source["bytes"] == 759249
    assert source["pdf_pages"] == 11 and source["pages_read"] == list(range(1, 12))
    assert evidence["canonical_identity"]["not_main_conference"] is True
    assert "IEEE" in source["version"] and "arXiv" in source["version"]
    matrix = evidence["table4"]
    assert (matrix["families"], matrix["named_encoders"], matrix["configurations"]) == (6, 15, 42)
    assert len(matrix["rows"]) == 42 and matrix["TAP_used"] is False
    assert evidence["TAP_method"]["independent_method_supported"] is True
    results = evidence["quantitative_evidence"]
    comparison = next(r for r in results if r["location"] == "Table4" and r.get("baseline_mean_F1") == 75.63)
    assert [comparison[k] for k in ("baseline_mean_F1", "baseline_mean_accuracy", "PE_G_mean_F1", "PE_G_mean_accuracy")] == [75.63, 77.45, 89.54, 89.81]
    gain = next(r for r in results if r["location"] == "Table2")
    assert [gain[k] for k in ("PE_G_TAP_mean_F1", "PE_G_TAP_mean_accuracy")] == [92.94, 92.96]
    counterexample = next(r for r in results if r["setting"] == "GenImage negativeTAPgeneralization")
    assert [counterexample[k] for k in ("PE_G_noTAP_mean_accuracy", "PE_G_TAP_mean_accuracy")] == [97.16, 95.67]
    assert len(evidence["twelve_questions"]) == 12


def test_R574_independent_method_dataset_benchmark_roles_and_nonuniform_results_are_preserved():
    case = record(packet(), "R574")
    evidence = case["worker_scientific_review"]
    assert evidence["source"]["sha256"] == PDF_HASHES["R574"]
    assert evidence["source"]["bytes"] == 2768471
    assert evidence["identity"]["physical_pages"] == 10
    assert evidence["identity"]["pages"] == "15856–15865"
    assert "IEEE" in evidence["identity"]["version"]
    assert evidence["provisional_outcome"] == "BENCHMARK_ADDITION_SUPPORTED"
    assert evidence["proposed_research_types"] == ["method", "dataset", "benchmark"]
    assert evidence["task_taxonomy_adjudicated"] is False
    assert len(evidence["questions"]) == 12
    assert evidence["dataset_contribution"]["known_generator_models"] == 14
    assert evidence["dataset_contribution"]["unknown_generator_models"] == 53
    assert evidence["dataset_contribution"]["unseen_scenarios_models"] == {"seed": 10, "architecture": 22, "dataset": 21}
    assert "progressively" in evidence["method_contribution"]["finding"]
    metrics = evidence["quantitative_evidence"]
    assert metrics["table4"]["POSE"] == [94.81, 68.15, 67.25, 84.17, 81.62, 88.24, 85.64, 82.76, 80.50]
    assert metrics["table6"]["POSE"] == metrics["table4"]["POSE"]
    assert metrics["table4"]["PRNU"][1] == 69.20 > metrics["table4"]["POSE"][1]
    assert metrics["contradictory_superiority_evidence"]
    assert evidence["scientific_evidence_sufficient_for_benchmark"] is True


def test_R574_five_split_configurations_and_three_released_scenarios_match_published_protocol():
    evidence = record(packet(), "R574")["released_annotation_review"]
    assert evidence["repository_commit"] == REPOSITORY_COMMIT
    assert list(evidence["five_configurations"]) == ["split1", "split2", "split3", "split4", "split5"]
    for split in evidence["five_configurations"].values():
        assert split["class_group_counts"] == {"known_classes": 15, "unknown_classes1": 10, "unknown_classes2": 22, "unknown_classes3": 21}
        assert split["class_groups_pairwise_disjoint"] is True
        classes = split["all_classes"]
        assert {k: len(v) for k, v in classes.items()} == split["class_group_counts"]
        assert classes["known_classes"][0] == "real"
    assert evidence["configuration_union_names_including_real"] == 82
    assert evidence["configuration_union_generator_names_excluding_real"] == 81
    assert evidence["all_five_tree_split_structures"] is True
    assert evidence["scenario_union_equals_combined_unknown"] is True
    assert set(evidence["scenario_pairwise_path_intersections"].values()) == {0}
    assert evidence["combined_unknown_label_offsets_match_scenario_lists"] == {"seed": True, "arch": True, "dataset": True}


def test_R574_exact_split1_path_counts_do_not_become_full_dataset_or_content_independence_claims():
    evidence = record(packet(), "R574")["released_annotation_review"]
    counts = evidence["annotation_counts"]
    expected = {"split1_train": 59998, "split1_val": 7500, "split1_test": 8000,
                "split1_test_out": 26500, "split1_test_out_seed": 5000,
                "split1_test_out_arch": 11000, "split1_test_out_dataset": 10500}
    for key, value in expected.items():
        assert counts[key]["row_count"] == counts[key]["unique_image_path_strings"] == value
        assert counts[key]["duplicate_path_strings"] == 0
    assert counts["split1_train"]["class_label_count"] == counts["split1_val"]["class_label_count"] == counts["split1_test"]["class_label_count"] == 15
    assert counts["split1_test_out"]["class_label_count"] == 53
    assert [counts[k]["labels"]["0"]["count"] for k in ("split1_train", "split1_val", "split1_test")] == [4021, 483, 994]
    assert evidence["unique_path_strings_across_core4"] == sum(expected[k] for k in ("split1_train", "split1_val", "split1_test", "split1_test_out")) == 101998
    assert set(evidence["core_pairwise_path_intersections"].values()) == {0}
    assert evidence["scientific_reproduction_executed"] is False
    assert evidence["dataset_assets_verified"] is False and evidence["checkpoints_verified"] is False
    science = record(packet(), "R574")["worker_scientific_review"]
    assert science["release_status"]["complete_reproduction"] == "NOT_EXECUTED_OR_CLAIMED"
    assert science["release_status"]["other_four_annotation_payloads_retrieved"] is False
    limitations = " ".join(science["limitations"]).casefold()
    for token in ("literal", "content", "checkpoint", "threshold", "ieee", "not", "unverified"):
        assert token in limitations


def test_two_complete_manuscripts_and_partial_same_source_continuation_remain_exact():
    retrieval = packet()["retrieval_accounting"]
    assert retrieval == original()["retrieval_accounting"]
    assert retrieval["complete_manuscripts_by_review"] == {"R215": 1, "R574": 1}
    assert retrieval["complete_manuscripts_total"] == 2
    assert retrieval["primary_PDF_transport_requests_by_review"] == {"R215": 1, "R574": 2}
    assert retrieval["primary_PDF_transport_requests_total"] == 3
    assert retrieval["partial_transfer_is_not_a_second_manuscript"] is True
    for key in ("independent_redownloads", "new_alternate_versions", "supplementary_manuscripts", "repository_clones",
                "code_archives", "dataset_image_payloads", "model_or_checkpoint_payloads"):
        assert retrieval[key] == 0
    assert retrieval["supporting_text_documents"] == 12 and retrieval["supporting_text_bytes"] == 8053911
    assert retrieval["annotation_metadata_files"] == 7
    first = retrieval["R574_timed_out_transfer"]
    continuation = retrieval["R574_matching_ETag_missing_byte_continuation"]
    assert first["curl_exit_code"] == 28 and first["response_bytes"] == 1182618
    assert first["candidate_complete_manuscripts"] == 0 and first["PDF_magic_and_EOF"] is False
    assert continuation["http_status"] == 206
    assert continuation["response_headers"]["Content-Range"] == "bytes 1182618-2768470/2768471"
    assert continuation["response_headers"]["ETag"] == continuation["if_range_etag"]
    assert continuation["same_manuscript_continuation"] is True
    assert continuation["response_bytes"] + first["response_bytes"] == continuation["assembled_bytes"] == 2768471
    assert continuation["assembled_sha256"] == PDF_HASHES["R574"]
    assert first["source_url"] == continuation["source_url"] == continuation["effective_url"]


def test_public_semantic_delta_is_only_R574_and_its_existing_three_map_rows():
    old, live = published_context(BASE), published_context(PUBLISHED)
    assert old["papers"].keys() == live["papers"].keys()
    assert {pid for pid in old["papers"] if old["papers"][pid] != live["papers"][pid]} == {TARGETS["R574"]}
    assert sum(old["papers"][pid] == live["papers"][pid] for pid in old["papers"] if pid != TARGETS["R574"]) == 673
    reason = CSV_UPDATES[TAXONOMY]["research_types_review_reason"]
    expected = deepcopy(old["papers"][TARGETS["R574"]])
    expected["research_types"] = ["method", "dataset", "benchmark"]
    expected["taxonomy_review"]["research_types"]["reason"] = reason
    assert live["papers"][TARGETS["R574"]] == expected
    assert old["pairs"] == live["pairs"]
    for path in PUBLIC:
        before, after = json.loads(published_bytes(BASE, path)), json.loads(published_bytes(PUBLISHED, path))
        oldmeta, newmeta = deepcopy(before["metadata"]), deepcopy(after["metadata"])
        oldmeta.pop("public_preview_generated_at", None)
        newmeta.pop("public_preview_generated_at", None)
        assert oldmeta == newmeta
        assert {k: v for k, v in before.items() if k not in {"metadata", "records"}} == {
            k: v for k, v in after.items() if k not in {"metadata", "records"}}
    before = {r["id"]: r for r in json.loads(published_bytes(BASE, PUBLIC[1]))["records"]}
    after = {r["id"]: r for r in json.loads(published_bytes(PUBLISHED, PUBLIC[1]))["records"]}
    assert before.keys() == after.keys() and len(before) == 1410
    target_ids = {key for key, row in before.items() if row.get("paper_id") == TARGETS["R574"]}
    assert len(target_ids) == 3
    assert {key for key in before if before[key] != after[key]} == target_ids
    for key, row in before.items():
        expected = deepcopy(row)
        if key in target_ids:
            expected["research_types"] = ["method", "dataset", "benchmark"]
            expected["taxonomy_review"]["research_types"]["reason"] = reason
        assert after[key] == expected, key


    current = load_context()
    assert current["pairs"] == live["pairs"]
    for rid in TARGETS:
        assert current["papers"][TARGETS[rid]] == live["papers"][TARGETS[rid]]
    current_maps = {r["id"]: r for r in json.loads((ROOT / PUBLIC[1]).read_bytes())["records"]}
    assert {key: current_maps[key] for key in target_ids} == {key: after[key] for key in target_ids}

def test_live_corpus_and_taxonomy_recompute_the_single_benchmark_addition():
    old, live = published_context(BASE), published_context(PUBLISHED)
    assert live["counts"] == old["counts"] == packet()["corpus_counts"] == CURRENT_CORPUS_COUNTS
    def totals(context):
        return Counter(label for row in context["papers"].values() for dimension in ("tasks", "research_types") for label in row[dimension])
    before, after = totals(old), totals(live)
    assert after == packet()["taxonomy_counts"] == TAXONOMY_TOTALS
    assert not before - after and after - before == {"benchmark": 1}
    assert before["benchmark"] == 90 and after["benchmark"] == 91
    assert live["papers"][TARGETS["R215"]]["tasks"] == ["detection"]
    assert live["papers"][TARGETS["R574"]]["tasks"] == ["source_attribution"]


    current = load_context()
    assert current["counts"] == CURRENT_CORPUS_COUNTS
    assert totals(current) == CURRENT_TAXONOMY_TOTALS
    for rid in TARGETS:
        assert current["papers"][TARGETS[rid]] == live["papers"][TARGETS[rid]]

def test_accepted_R2_rule_original_questions_and_unrelated_authoritative_tables_are_unchanged():
    queues = load_queues()
    taxonomy = {r["review_id"]: r for r in queues["taxonomy_review"]["records"]}
    for rid in TARGETS:
        assert record(packet(), rid)["original_review"] == taxonomy[rid]
    assert packet()["locked_policy_ledger"] == json.loads((ROOT / (AUDIT + "batch_c_policy_decisions.json")).read_bytes())
    r2 = next(r for r in packet()["locked_policy_ledger"]["policies"] if r["policy_id"] == "R2")
    assert "systematic comparative framework" in r2["final_rule"]
    allowed = {PAPERS, TAXONOMY, DECISIONS, *PUBLIC}
    for path in baseline_paths("data/curated", "data/manual", "web/data"):
        if path not in allowed:
            assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path
    for name in ("taxonomy_review", "publication_metadata_review", "relationship_review", "unmapped_papers", "batch_c_policy_decisions"):
        path = AUDIT + name + ".json"
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_original_and_current_source_hashes_are_independent_of_ignored_runtime_caches():
    old, data = original(), packet()
    assert data["source_files_sha256"] == old["source_files_sha256"]
    current = data["current_source_sha256"]
    assert current.keys() == old["source_files_sha256"].keys()
    assert {p for p in current if current[p] != old["source_files_sha256"][p]} == {PAPERS, TAXONOMY, DECISIONS, *PUBLIC}
    tracked = set(baseline_paths())
    entries = {r["path"]: r for r in json.loads(published_bytes(BASE, FIXTURES))["entries"]}
    for path, expected in current.items():
        if path in tracked:
            raw = published_bytes(PUBLISHED, path)
        else:
            # Verify immutable committed fixture data, not a developer's operational cache.
            entry = entries[path]
            assert entry["compression"] == "none"
            raw = published_bytes(BASE, entry["source"])
            assert digest(raw) == entry["sha256"] == entry["source_sha256"]
            assert len(raw) == entry["bytes"]
        assert digest(raw) == expected, path


def test_all_sixteen_prior_B_receipts_and_historical_fixture_bytes_remain_frozen():
    # Discover exact published artifact dates instead of assuming date variants.
    prior = [path for path in baseline_paths("data/raw", "docs")
             if re.search(r"(?:data/raw/|docs/)corpus_quality_batch_b_wave_b1[a-h]_", path)
             and (path.endswith("/evidence_manifest.json") or path.endswith(".md"))]
    assert len(prior) == 16
    for path in [*prior, *baseline_paths("tests/fixtures")]:
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_49_NeurIPS_artifacts_C13_and_separate_39_inventory_are_not_reopened():
    frozen_path = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT / frozen_path).read_bytes()
    assert raw == published_bytes(BASE, frozen_path)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for path, expected in frozen.items():
        assert digest(preserved_bytes(ROOT, path)) == expected, path
    assert packet()["neurips_status"] == "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"
    old, new = original(), packet()
    assert new["batch_c_deferred_accounting"] == old["batch_c_deferred_accounting"]
    debt = new["batch_c_deferred_accounting"]
    assert debt["total_actions"] == 41 and debt["resolved"] == 28
    assert debt["total_unresolved"] == debt["external_unresolved"] == 13
    assert debt["maintainer_judgments"] == 0
    assert len(debt["remaining_external_ids"]) == 13
    assert new["separate_import_review_inventory"] == old["separate_import_review_inventory"]
    intake = new["separate_import_review_inventory"]
    assert intake["papers"] == len(intake["candidate_to_paper"]) == 39
    assert intake["taxonomy_pending"] == 14 and intake["held"] == 12
    assert intake["unmapped_all"] is True and intake["taxonomy_needs_review_all"] is True
    live = load_context()
    for paper_id in intake["candidate_to_paper"].values():
        assert live["papers"][paper_id] == published_context(BASE)["papers"][paper_id]
        assert live["papers"][paper_id]["has_map_location"] is False
    for path in ("data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
                 "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
                 "docs/corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md",
                 "tests/test_corpus_quality_batch_c_closeout.py"):
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_report_records_two_adjudications_and_exact_scope_without_dropping_history():
    data, report = packet(), (ROOT / REPORT).read_text()
    for token in (*IDS.values(), "R215", "R574", "SUPPORTED_NO_CHANGE", "PROPOSE_CORRECTION_ACCEPTED",
                  "benchmark", "method", "143", "145", "132", BASE,
                  "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"):
        assert token in report
    assert "permissive" in report.casefold() and "medium" in report.casefold()
    assert "IEEE" in report and "unverified" in report
    assert archived_bytes("report").decode() in report or "evidence_only_packet_archives" in report
    assert data["scope"]["review_decisions_added"] == data["scope"]["review_actions_closed"] == 2
    assert data["scope"]["authoritative_scientific_changes"] == 1
    assert data["scope"]["forensic_task_changes"] == 0
    # Full-suite/export counters are later completion receipts, not scientific state.
