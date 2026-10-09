"""Final Wave 5B boundaries: one T236 task edit, one T137 no-op, and ledger accounting."""

from collections import Counter
import csv
from functools import lru_cache
import io
import json
from pathlib import Path
import subprocess

import pytest

from scripts.validate_corpus_quality_audit import load_context


ROOT = Path(__file__).resolve().parents[1]
BASE = "70a0bd330b76a493597c53f6117dcfa18f2a3c4e"
T236 = "curated:64635535d7b7b6a12a32"
T137 = "curated:246f07c81b9f91e527eb"
T527 = "doi:10.1109/lsp.2024.3388958"
SOURCE = "https://arxiv.org/html/2601.19430v1"
MANIFEST = ROOT / "data/raw/corpus_quality_batch_c_wave5b_2026_10_09/evidence_manifest.json"
REPORT = ROOT / "docs/corpus_quality_batch_c_wave5b_2026_10_09.md"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")


@lru_cache
def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def manifest():
    return json.loads(MANIFEST.read_text())


def action(review_id):
    return next(a for a in manifest()["actions"] if a["review_id"] == review_id)


@pytest.mark.parametrize("path", ["data/curated/papers.csv", "data/curated/paper_taxonomy.csv"])
def test_exactly_t236_authoritative_task_fields_change_and_csv_bytes_remain_scoped(path):
    old_bytes = previous(path)
    new_bytes = (ROOT / path).read_bytes()
    old = {r["paper_id"]: r for r in rows(old_bytes)}
    new = {r["paper_id"]: r for r in rows(new_bytes)}
    assert old.keys() == new.keys()
    assert {pid for pid in old if old[pid] != new[pid]} == {T236}
    assert new[T137] == old[T137]
    assert old[T236]["tasks"] == "detection"
    assert new[T236]["tasks"] == "detection;localization"
    fields = {k for k in old[T236] if old[T236][k] != new[T236][k]}
    expected = {"tasks"}
    if path.endswith("paper_taxonomy.csv"):
        expected |= {"tasks_review_reason", "tasks_evidence_tier", "tasks_evidence_source",
                     "tasks_evidence_excerpt", "audited_at"}
        assert new[T236]["tasks_evidence_tier"] == "primary_paper"
        assert new[T236]["tasks_evidence_source"] == SOURCE
        assert new[T236]["tasks_review_reason"].startswith("T2:")
        assert all(x in new[T236]["tasks_evidence_excerpt"] for x in
                   ("IoU 27.2", "PixF1 42.7", "IoU 27.3", "PixF1 42.8"))
    assert fields == expected
    old_lines = old_bytes.splitlines(keepends=True)
    new_lines = new_bytes.splitlines(keepends=True)
    assert len(old_lines) == len(new_lines)
    assert [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b] == [
        next(i for i, line in enumerate(old_lines) if T236.encode() in line)
    ]
    assert new_bytes.count(b"\r\n") == old_bytes.count(b"\r\n") == 16


def test_final_evidence_keeps_two_sources_failures_and_version_limits():
    wave = manifest()
    assert wave["adjudication_status"] == "FINAL"
    assert wave["additional_retrievals_during_finalization"] == 0
    assert [a["review_id"] for a in wave["actions"]] == ["T236", "T137"]
    assert len(wave["documents"]) == wave["retrieval_policy"]["full_papers_retrieved"] == 2
    assert [a["policy_id"] for a in wave["actions"]] == ["T2", "T1"]
    assert wave["retrieval_policy"]["previous_blocked_urls_retried"] == 0
    assert wave["documents"][0]["identity_verification"]["arxiv_id_matches_canonical"]
    assert wave["documents"][1]["identity_verification"]["arxiv_id_matches_canonical"]
    assert "inaccessible ICLR final PDF" in wave["actions"][0]["limitations"]
    assert "Yuexuan Tan" in wave["documents"][1]["identity_verification"]["author_variance"]
    assert wave["documents"][1]["identity_verification"]["author_list_exact_match"] is False
    report = REPORT.read_text()
    assert "Yuexuan Tan" in report and "inaccessible ICLR final PDF" in report
    for a in wave["actions"]:
        assert a["first_pass_failure"] and a["first_pass_source_url"]
        assert a["second_pass_source_url"] and a["finalized"]


def test_t236_localization_is_spatial_prediction_not_just_attention():
    a = action("T236")
    assert a["adjudication"] == "LOCALIZATION_TASK_SUPPORTED"
    assert a["evidence_outcome"] == "EVIDENCE_RESOLVED_CHANGE"
    assert a["remediation"] == "APPLIED"
    assert a["final_disposition"] == "REMEDIATION_APPLIED"
    assert a["current_tasks"] == a["final_taxonomy"]["tasks"] == ["detection", "localization"]
    assert "segmentation mask" in a["output_decision_space"]
    assert "human polygon masks" in a["supervision_and_ground_truth"]
    assert "Table 2" in a["evaluation_evidence"]
    assert a["quantitative_metrics"] == {
        "PAD_only_category_agnostic_IoU_reported": 27.2,
        "PAD_only_category_agnostic_PixF1_reported": 42.7,
        "multi_task_category_agnostic_IoU_reported": 27.3,
        "multi_task_category_agnostic_PixF1_reported": 42.8,
    }


def test_t137_authenticity_evidence_is_separate_from_open_set_attribution():
    a = action("T137")
    assert a["adjudication"] == "DETECTION_TASK_SUPPORTED"
    assert a["evidence_outcome"] == "EVIDENCE_RESOLVED_NO_CHANGE"
    assert a["remediation"] == "NOT_REQUIRED"
    assert a["final_disposition"] == "REMEDIATION_NOT_REQUIRED"
    assert not a["remediation_applied"]
    assert a["current_tasks"] == a["final_taxonomy"]["tasks"] == ["detection", "source_attribution"]
    assert "real from generated" in a["authenticity_evaluation"]
    assert "unseen-generator" in a["attribution_evaluation"]
    assert a["quantitative_metrics"]["EP2_Auth_Acc_percent"] == 99.97
    assert a["quantitative_metrics"]["EP1_unseen_generator_accuracy_percent"] == 98.93
    assert "author" in a["limitations"].lower() and "CVF final" in a["limitations"]


def test_remaining_ledger_subtracts_the_two_cases_only_once():
    before = json.loads((ROOT / "data/raw/corpus_quality_batch_c_wave5a_2026_10_08/evidence_manifest.json").read_text())
    wave = manifest()
    r = wave["resolution"]
    assert r["before"] == before["resolution"]["after"]
    assert r["scientifically_resolved"] == 2
    assert r["resolved_change_applied"] == ["T236"]
    assert r["resolved_no_change"] == ["T137"]
    assert r["pending_maintainer_adjudications"] == []
    assert r["evidence_debt_subtracted_once"]
    assert r["after"] == {"task_evidence": 3, "institution_evidence": 1,
                          "research_type_evidence": 11, "external_unresolved": 15,
                          "maintainer_T527": 1, "total_unresolved": 16}
    assert set(r["remaining_external_ids"]) == set(before["resolution"]["remaining_external_ids"]) - {"T236", "T137"}
    assert {x for x in r["remaining_external_ids"] if x.startswith("T")} == {"T141", "T572", "T503"}


@pytest.mark.parametrize("path", PUBLIC)
def test_public_exports_change_only_t236_tasks_and_review_provenance(path):
    old = json.loads(previous(path))["records"]
    new = json.loads((ROOT / path).read_text())["records"]
    assert len(old) == len(new)
    assert [x for x in old if x.get("paper_id") != T236] == [x for x in new if x.get("paper_id") != T236]
    a = [x for x in old if x.get("paper_id") == T236]
    b = [x for x in new if x.get("paper_id") == T236]
    assert len(a) == len(b) and b
    for x, y in zip(a, b):
        assert x["tasks"] == ["detection"]
        assert y["tasks"] == ["detection", "localization"]
        assert {k: v for k, v in x.items() if k not in {"tasks", "taxonomy_review"}} == {
            k: v for k, v in y.items() if k not in {"tasks", "taxonomy_review"}
        }
        assert {k: v for k, v in x["taxonomy_review"].items() if k != "tasks"} == {
            k: v for k, v in y["taxonomy_review"].items() if k != "tasks"
        }
        assert y["taxonomy_review"]["tasks"]["reason"].startswith("T2:")


def test_corpus_and_taxonomy_counts_recompute_from_current_export():
    context = load_context()
    assert context["counts"] == {"public": 639, "formal": 531, "mapped": 617,
                                 "unmapped": 22, "relationship_rows": 1421,
                                 "unique_paper_institution_pairs": 1421}
    totals = Counter(label for p in context["papers"].values()
                     for key in ("tasks", "research_types") for label in p[key])
    assert dict(totals) == manifest()["taxonomy_after"] == {
        "detection": 589, "source_attribution": 85, "localization": 43,
        "method": 547, "dataset": 132, "benchmark": 88,
        "survey": 20, "analysis_study": 78,
    }
    old = Counter(label for p in json.loads(previous(PUBLIC[0]))["records"]
                  for key in ("tasks", "research_types") for label in p[key])
    assert old == manifest()["taxonomy_before"]
    previous_t527 = [x for x in json.loads(previous(PUBLIC[0]))["records"]
                     if x.get("doi") == "10.1109/lsp.2024.3388958"]
    assert len(previous_t527) == 1
    assert context["papers"][T527]["tasks"] == previous_t527[0]["tasks"]
    assert totals - old == {"localization": 1}
    assert not old - totals
