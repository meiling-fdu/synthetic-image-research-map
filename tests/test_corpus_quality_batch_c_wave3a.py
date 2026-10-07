"""Focused regression checks for finalized Batch C Wave 3A adjudication."""

from collections import Counter
import csv
from functools import lru_cache
import io
import json
from pathlib import Path
import subprocess

from scripts.validate_corpus_quality_audit import load_context


ROOT = Path(__file__).resolve().parents[1]
BASE = "196c9a9d7cfd9fc03422ed318b7985aa84d208e3"
MANIFEST = ROOT / "data/raw/corpus_quality_batch_c_wave3a_2026_10_06/evidence_manifest.json"
REPORT = ROOT / "docs/corpus_quality_batch_c_wave3a_2026_10_06.md"
T236 = "paper_id:curated:64635535d7b7b6a12a32"
T246 = "doi:10.1609/aaai.v40i4.37240"
T246_DOI = "10.1609/aaai.v40i4.37240"
SOURCE = "https://ojs.aaai.org/index.php/AAAI/article/download/37240/41202"


@lru_cache
def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def csv_rows(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def previous_csv(path):
    return list(csv.DictReader(io.StringIO(previous(path).decode("utf-8-sig"), newline="")))


def adjudicated_csv(path):
    # Later approved waves can change unrelated rows; keep this wave's boundary fixed.
    data = subprocess.check_output(["git", "show", "a24a9e6:" + path], cwd=ROOT)
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline="")))


def records(path, *, current=True):
    payload = json.loads((ROOT / path).read_text()) if current else json.loads(previous(path))
    return payload["records"]


def test_t246_is_the_only_authoritative_taxonomy_change():
    path = "data/curated/paper_taxonomy.csv"
    before = {row["taxonomy_id"]: row for row in previous_csv(path)}
    after = {row["taxonomy_id"]: row for row in adjudicated_csv(path)}
    assert before.keys() == after.keys()
    assert {key for key in before if before[key] != after[key]} == {T246}
    old, new = before[T246], after[T246]
    assert old["tasks"] == "detection"
    assert new["tasks"] == "detection;localization"
    assert new["tasks_status"] == "reviewed"
    assert new["tasks_evidence_tier"] == "primary_paper"
    assert new["tasks_evidence_source"] == SOURCE
    changed = {field for field in old if old[field] != new[field]}
    assert changed == {
        "tasks", "tasks_review_reason", "tasks_evidence_tier",
        "tasks_evidence_source", "tasks_evidence_excerpt", "audited_at",
    }


def test_t236_remains_detection_only_and_byte_semantically_unchanged():
    path = "data/curated/paper_taxonomy.csv"
    before = {row["taxonomy_id"]: row for row in previous_csv(path)}[T236]
    after = {row["taxonomy_id"]: row for row in csv_rows(path)}[T236]
    assert after == before
    assert after["tasks"] == "detection"


def test_public_export_changes_only_t246_task_evidence():
    for path in ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json"):
        before = [row for row in records(path, current=False) if row.get("doi") == T246_DOI]
        after = [row for row in records(path) if row.get("doi") == T246_DOI]
        assert len(after) == len(before) and after
        for old, new in zip(before, after):
            assert old["tasks"] == ["detection"]
            assert new["tasks"] == ["detection", "localization"]
            assert {k: v for k, v in old.items() if k not in {"tasks", "taxonomy_review"}} == {
                k: v for k, v in new.items() if k not in {"tasks", "taxonomy_review"}
            }
            assert new["taxonomy_review"]["tasks"] == {
                "status": "reviewed",
                "reason": "T2 satisfied by an evaluated predicted spatial mask",
            }

        t236_before = [row for row in records(path, current=False) if row.get("paper_id") == T236.removeprefix("paper_id:")]
        t236_after = [row for row in records(path) if row.get("paper_id") == T236.removeprefix("paper_id:")]
        assert t236_after == t236_before


def test_wave3a_ledger_finalizes_two_actions_without_rewriting_evidence():
    manifest = json.loads(MANIFEST.read_text())
    report = REPORT.read_text()
    assert manifest["adjudication_status"] == "FINAL"
    assert [row["review_id"] for row in manifest["actions"]] == ["T236", "T246"]
    by_id = {row["review_id"]: row for row in manifest["actions"]}
    assert by_id["T236"]["adjudication"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert by_id["T236"]["final_disposition"] == "REMEDIATION_NOT_APPLIED"
    assert by_id["T236"]["corpus_change_applied"] is False
    assert by_id["T246"]["adjudication"] == "LOCALIZATION_TASK_SUPPORTED"
    assert by_id["T246"]["evidence_outcome"] == "EVIDENCE_RESOLVED_CHANGE"
    assert by_id["T246"]["final_disposition"] == "REMEDIATION_APPLIED"
    assert by_id["T246"]["corpus_change_applied"] is True
    evidence = " ".join((
        by_id["T246"]["output_representation"],
        by_id["T246"]["ground_truth_evidence"],
        by_id["T246"]["evaluation_evidence"],
    ))
    assert "M-hat" in evidence and "ground-truth" in evidence and "IoU 0.907" in evidence
    assert all(token in report for token in (
        "EVIDENCE_STILL_INSUFFICIENT", "REMEDIATION_NOT_APPLIED",
        "LOCALIZATION_TASK_SUPPORTED", "EVIDENCE_RESOLVED_CHANGE", "REMEDIATION_APPLIED",
    ))
    assert manifest["scope"]["research_type_reviewed"] is False


def test_external_batch_c_residual_reconciles_programmatically():
    phase1 = json.loads((ROOT / "data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json").read_text())
    wave1 = json.loads((ROOT / "data/raw/corpus_quality_batch_c_wave1_2026_10_06/evidence_manifest.json").read_text())
    wave2 = json.loads((ROOT / "data/raw/corpus_quality_batch_c_wave2_2026_10_06/evidence_manifest.json").read_text())
    wave3a = json.loads(MANIFEST.read_text())
    external = {
        row["review_id"]: row for row in phase1["residual_triage"]
        if row["evidence_status"] == "EXTERNAL_PRIMARY_SOURCE_REQUIRED"
    }
    resolved = {row["review_id"] for row in wave1["actions"]}
    resolved |= {
        row["review_id"] for row in wave2["actions"]
        if row["evidence_outcome"] != "EVIDENCE_STILL_INSUFFICIENT"
    }
    resolved |= {
        row["review_id"] for row in wave3a["actions"]
        if row.get("evidence_outcome") == "EVIDENCE_RESOLVED_CHANGE"
    }
    residual = {review_id: external[review_id] for review_id in external.keys() - resolved}
    categories = Counter(row["category"] for row in residual.values())
    assert len(external) == 35 and len(residual) == 28
    assert "T236" in residual and "U010" in residual and "T246" not in residual
    assert categories == {"task": 12, "institution": 1, "research_type": 15}
    assert wave3a["resolution"]["external_batch_c_after"] == len(residual)
    assert wave3a["resolution"]["total_unresolved_batch_c_after_including_t527"] == 29


def test_exact_corpus_and_taxonomy_effect():
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
    assert tasks == {"detection": 590, "source_attribution": 85, "localization": 42}
    assert research_types == {
        "method": 547,
        "dataset": 132,
        "benchmark": 88,
        "survey": 20,
        "analysis_study": 78,
    }
