"""Regression boundaries for the two accepted Wave 5A task decisions."""

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
BASE = "114d2e5f352f39f6c3a484e43f3aac593eb7cf64"
WAVE5A = "70a0bd330b76a493597c53f6117dcfa18f2a3c4e"
MANIFEST_PATH = "data/raw/corpus_quality_batch_c_wave5a_2026_10_08/evidence_manifest.json"
REPORT_PATH = "docs/corpus_quality_batch_c_wave5a_2026_10_08.md"
T576 = "curated:62b0a9ae8be24d9f02e0"
T611 = "curated:07ee620b8169b67b900f"
SOURCE = "https://www.bmva-archive.org.uk/bmvc/2021/assets/papers/0197.pdf"
LIMITATION = (
    "Detection evidence is generator-specific real-versus-generated discrimination, "
    "not a demonstrated universal synthetic-image detector."
)
PUBLIC_PATHS = (
    "web/data/public_preview_papers.json",
    "web/data/public_preview_map_data.json",
)


@lru_cache
def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


@lru_cache
def adjudicated(path):
    # Pin the Wave 5A historical boundary; later accepted waves may change other rows.
    return subprocess.check_output(["git", "show", f"{WAVE5A}:{path}"], cwd=ROOT)


def read_json(path):
    return json.loads((ROOT / path).read_text())


def rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def manifest():
    return read_json(MANIFEST_PATH)


@pytest.mark.parametrize("path", ["data/curated/papers.csv", "data/curated/paper_taxonomy.csv"])
def test_only_t611_task_fields_change_and_other_csv_bytes_are_preserved(path):
    old_bytes, new_bytes = previous(path), adjudicated(path)
    before = {r["paper_id"]: r for r in rows(old_bytes)}
    after = {r["paper_id"]: r for r in rows(new_bytes)}
    assert before.keys() == after.keys()
    assert {pid for pid in before if before[pid] != after[pid]} == {T611}
    old, new = before[T611], after[T611]
    assert old["tasks"] == "detection;source_attribution"
    assert new["tasks"] == "source_attribution"
    expected = {"tasks"}
    if path.endswith("paper_taxonomy.csv"):
        expected |= {
            "tasks_review_reason", "tasks_evidence_tier", "tasks_evidence_source",
            "tasks_evidence_excerpt", "audited_at",
        }
        assert new["tasks_status"] == "reviewed"
        assert new["tasks_evidence_tier"] == "primary_paper"
        assert new["tasks_evidence_source"] == SOURCE
        assert new["tasks_review_reason"].startswith("T1:")
        assert "no real-versus-generated decision rule" in new["tasks_review_reason"]
    assert {key for key in old if old[key] != new[key]} == expected
    assert new["research_types"] == old["research_types"] == "method"
    assert after[T576] == before[T576]
    old_lines, new_lines = old_bytes.splitlines(keepends=True), new_bytes.splitlines(keepends=True)
    assert len(old_lines) == len(new_lines)
    differences = [(old, new) for old, new in zip(old_lines, new_lines) if old != new]
    assert len(differences) == 1
    assert all(T611.encode() in line for line in differences[0])
    assert new_bytes.count(b"\r\n") == old_bytes.count(b"\r\n") == 16


@pytest.mark.parametrize("path", PUBLIC_PATHS)
def test_public_changes_are_only_t611_tasks_and_task_review_provenance(path):
    before = json.loads(previous(path))["records"]
    after = json.loads(adjudicated(path))["records"]
    assert len(after) == len(before)
    assert [r for r in after if r.get("paper_id") != T611] == [
        r for r in before if r.get("paper_id") != T611
    ]
    old_rows = [r for r in before if r.get("paper_id") == T611]
    new_rows = [r for r in after if r.get("paper_id") == T611]
    assert len(new_rows) == len(old_rows) and new_rows
    for old, new in zip(old_rows, new_rows):
        assert old["tasks"] == ["detection", "source_attribution"]
        assert new["tasks"] == ["source_attribution"]
        assert new["research_types"] == old["research_types"]
        assert {k: v for k, v in old.items() if k not in {"tasks", "taxonomy_review"}} == {
            k: v for k, v in new.items() if k not in {"tasks", "taxonomy_review"}
        }
        assert {k: v for k, v in new["taxonomy_review"].items() if k != "tasks"} == {
            k: v for k, v in old["taxonomy_review"].items() if k != "tasks"
        }
        assert new["taxonomy_review"]["tasks"]["status"] == "reviewed"
        assert new["taxonomy_review"]["tasks"]["reason"].startswith("T1:")


def test_t576_detection_support_is_explicitly_generator_specific():
    action = next(a for a in manifest()["actions"] if a["review_id"] == "T576")
    assert action["adjudication"] == "DETECTION_TASK_SUPPORTED"
    assert action["evidence_outcome"] == "EVIDENCE_RESOLVED_NO_CHANGE"
    assert action["final_disposition"] == "REMEDIATION_NOT_REQUIRED"
    assert action["remediation"] == "NOT_REQUIRED"
    assert not action["corpus_change_applied"]
    assert action["current_tasks"] == action["final_taxonomy"]["tasks"] == [
        "detection", "source_attribution",
    ]
    assert action["accepted_detection_limitation"] == LIMITATION
    assert LIMITATION in (ROOT / REPORT_PATH).read_text()
    assert action["confidence"]["retrieval_and_numeric_evidence"] == "high"
    assert action["confidence"]["T1_classification"] == "moderate"
    result = action["authenticity_evaluation"]["results"][0]
    assert result["CelebA"] == 99.72 and result["LSUN"] == 99.69
    assert "Table 8" in result["locator"]
    assert "universal" in action["authenticity_evaluation"]["scope"]


def test_source_fingerprint_matching_alone_does_not_justify_detection():
    wave = manifest()
    assert "Source attribution does not imply authenticity detection" in wave["policy"]["locked_rule"]
    assert "N+1 classifier with a real class" in wave["policy"]["guard"]
    action = next(a for a in wave["actions"] if a["review_id"] == "T611")
    assert action["adjudication"] == "ATTRIBUTION_ONLY_NO_DETECTION"
    assert action["evidence_outcome"] == "EVIDENCE_RESOLVED_CHANGE"
    assert action["remediation"] == "APPLIED"
    assert action["final_disposition"] == "REMEDIATION_APPLIED"
    assert action["corpus_change_applied"] is True
    assert action["tasks_before"] == ["detection", "source_attribution"]
    assert action["current_tasks"] == action["final_taxonomy"]["tasks"] == ["source_attribution"]
    assert action["authenticity_evaluation"]["reported"] is False
    assert "divergence/correlation" in action["authenticity_evaluation"]["evidence"]
    assert "not an authentic-versus-synthetic decision" in action["evaluated_decision_space"]
    assert "supplement" in action["authenticity_evaluation"]["limitation"]


def test_final_evidence_preserves_both_passes_and_two_paper_budget():
    wave = manifest()
    assert wave["adjudication_status"] == "FINAL"
    assert wave["additional_retrievals_during_finalization"] == 0
    assert [a["review_id"] for a in wave["actions"]] == ["T576", "T611"]
    assert len(wave["documents"]) == wave["retrieval_policy"]["full_papers_obtained"] == 2
    assert [d["sha256"] for d in wave["documents"]] == [
        "449bb229bee4b6f1cfe225f76e1a01854c1e57498f41bab2793a438f111a785d",
        "3ece0cc9c4818a21ae62726b1783548fd109af10f26615f55da2be237227dc7e",
    ]
    for action in wave["actions"]:
        assert action["paper_identity_verification"]["status"] == "MATCH"
        assert action["finalized"] is True
        assert action["second_pass_retrieval_outcome"] == "COMPLETE_PRIMARY_PAPER_RETRIEVED_IDENTITY_MATCHED"
        assert action["first_pass"]["scientific_outcome"] == "EVIDENCE_STILL_INSUFFICIENT"
        old_wave = read_json(action["first_pass"]["manifest"])
        old_doc = next(d for d in old_wave["documents"] if d["review_id"] == action["review_id"])
        assert action["first_pass"]["retrieval_outcome"] == old_doc["retrieval_outcome"]
        assert not action["first_pass"]["retried_in_wave5a"]
    report = (ROOT / REPORT_PATH).read_text()
    for status in ("EVIDENCE_RESOLVED_CHANGE", "EVIDENCE_RESOLVED_NO_CHANGE",
                   "REMEDIATION_APPLIED", "REMEDIATION_NOT_REQUIRED"):
        assert status in report


def test_batch_c_remaining_ledger_reconciles_exact_identities():
    phase1 = read_json("data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json")
    external = {r["review_id"]: r for r in phase1["residual_triage"]
                if r["evidence_status"] == "EXTERNAL_PRIMARY_SOURCE_REQUIRED"}
    tracked = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE,
                                       "data/raw"], cwd=ROOT).decode().splitlines()
    paths = [p for p in tracked if "/corpus_quality_batch_c_wave" in p
             and p.endswith("/evidence_manifest.json")]
    assert len(paths) == 12
    resolved_before = {a["review_id"] for path in paths for a in read_json(path)["actions"]
                       if a["evidence_outcome"].startswith("EVIDENCE_RESOLVED")}
    assert len(external.keys() - resolved_before) == 19
    resolved_after = resolved_before | {a["review_id"] for a in manifest()["actions"]
                                       if a["evidence_outcome"].startswith("EVIDENCE_RESOLVED")}
    remaining = {rid: external[rid] for rid in external.keys() - resolved_after}
    assert Counter(r["category"] for r in remaining.values()) == {
        "task": 5, "institution": 1, "research_type": 11,
    }
    assert {rid for rid, r in remaining.items() if r["category"] == "task"} == {
        "T236", "T137", "T141", "T572", "T503",
    }
    resolution = manifest()["resolution"]
    assert set(resolution["remaining_external_ids"]) == set(remaining)
    assert resolution["scientifically_resolved"] == 2
    assert resolution["still_insufficient_in_wave"] == 0
    assert resolution["authoritative_changes_applied"] == 1
    assert resolution["pending_maintainer_adjudications"] == []
    assert resolution["after"] == {
        "task_evidence": 5, "institution_evidence": 1, "research_type_evidence": 11,
        "external_unresolved": 17, "maintainer_T527": 1, "total_unresolved": 18,
    }
    assert {r["review_id"] for r in phase1["residual_triage"]
            if r["evidence_status"] == "MAINTAINER_SCOPE_JUDGMENT_REQUIRED"} == {"T527"}
    assert phase1["reconciliation"]["batch_b_remaining"] == 159


def test_recomputed_corpus_and_taxonomy_change_only_detection_by_one():
    context = load_context()
    assert context["counts"] == {
        "public": 639, "formal": 531, "mapped": 617, "unmapped": 22,
        "relationship_rows": 1421, "unique_paper_institution_pairs": 1421,
    }
    before = json.loads(previous(PUBLIC_PATHS[0]))["records"]
    old = Counter(label for row in before for key in ("tasks", "research_types") for label in row[key])
    wave5a = Counter(label for row in json.loads(adjudicated(PUBLIC_PATHS[0]))["records"]
                     for key in ("tasks", "research_types") for label in row[key])
    current = Counter(label for row in context["papers"].values()
                      for key in ("tasks", "research_types") for label in row[key])
    assert old == manifest()["taxonomy_before"]
    assert wave5a == manifest()["taxonomy_after"]
    assert wave5a == {"detection": 589, "source_attribution": 85, "localization": 42,
                      "method": 547, "dataset": 132, "benchmark": 88,
                      "survey": 20, "analysis_study": 78}
    assert old - wave5a == {"detection": 1}
    assert not wave5a - old
    assert current - wave5a == {"localization": 1}
    assert not wave5a - current
