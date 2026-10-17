"""Wave 5C task adjudication and historical-boundary regression coverage."""
from tests.baseline_expectations import (
    CURRENT_CORPUS_COUNTS,
    CURRENT_TAXONOMY_TOTALS,
    LITERATURE51_TAXONOMY_ADDITIONS,
)

from collections import Counter
import csv
import io
import json
from pathlib import Path
import subprocess

import pytest

from scripts.validate_corpus_quality_audit import load_context

ROOT = Path(__file__).resolve().parents[1]
BASE = "805edcc5bbd2fb5c1afda348e900f32f02fcd450"
PUBLISHED_WAVE5C = "829b3c79e28c02c622dde2129bd6ce7b62eeb27f"
CASES = {
    "T572": ("curated:5a91cc922c8a3c4c3d0c", "https://arxiv.org/html/2308.11557v1"),
    "T503": ("curated:34fdf09ae334914a2723", "https://arxiv.org/html/2402.10401v2"),
}
PIDS = {pid for pid, _ in CASES.values()}
MANIFEST = ROOT / "data/raw/corpus_quality_batch_c_wave5c_2026_10_09/evidence_manifest.json"
REPORT = ROOT / "docs/corpus_quality_batch_c_wave5c_2026_10_09.md"
EXPORTS = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")


def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def published(path):
    # Frozen wave endpoint; closeout changes corpus membership separately.
    return subprocess.check_output(["git", "show", f"{PUBLISHED_WAVE5C}:{path}"], cwd=ROOT)


def csvrows(raw):
    return {r["paper_id"]: r for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))}


def manifest():
    return json.loads(MANIFEST.read_text())


@pytest.mark.parametrize("path", ("data/curated/papers.csv", "data/curated/paper_taxonomy.csv"))
def test_only_two_authoritative_rows_and_task_provenance_change(path):
    old_bytes, new_bytes = previous(path), published(path)
    old, new = csvrows(old_bytes), csvrows(new_bytes)
    assert old.keys() == new.keys()
    assert {pid for pid in old if old[pid] != new[pid]} == PIDS
    for review, (pid, source) in CASES.items():
        assert old[pid]["tasks"] == "detection;source_attribution"
        assert new[pid]["tasks"] == "source_attribution"
        assert new[pid]["research_types"] == old[pid]["research_types"] == "method"
        changed = {k for k in old[pid] if old[pid][k] != new[pid][k]}
        expected = {"tasks"}
        if path.endswith("paper_taxonomy.csv"):
            expected |= {"tasks_review_reason", "tasks_evidence_tier", "tasks_evidence_source",
                         "tasks_evidence_excerpt", "audited_at"}
            assert new[pid]["tasks_evidence_tier"] == "primary_paper"
            assert new[pid]["tasks_evidence_source"] == source
            assert new[pid]["tasks_review_reason"].startswith("T1:")
        assert changed == expected, (review, changed)
    before, after = old_bytes.splitlines(keepends=True), new_bytes.splitlines(keepends=True)
    assert len(before) == len(after)
    assert {i for i, (a, b) in enumerate(zip(before, after)) if a != b} == {
        i for i, line in enumerate(before) if any(pid.encode() in line for pid in PIDS)
    }
    assert old_bytes.count(b"\r\n") == new_bytes.count(b"\r\n") == 16


def test_manifest_supports_t1_decisions_without_overclaiming_detection():
    wave = manifest()
    assert wave["adjudication_status"] == "FINAL"
    assert wave["additional_retrievals_during_finalization"] == 0
    assert wave["scope"]["authoritative_changes_applied"] == 2
    assert [a["review_id"] for a in wave["actions"]] == ["T572", "T503"]
    assert all(not d["identity"]["conference_final_equivalence_verified"] for d in wave["documents"])
    actions = {a["review_id"]: a for a in wave["actions"]}
    for rid, a in actions.items():
        assert a["adjudication"] == "ATTRIBUTION_ONLY_NO_DETECTION"
        assert a["evidence_outcome"] == "EVIDENCE_RESOLVED_CHANGE"
        assert a["remediation"] == "APPLIED" and a["remediation_applied"]
        assert a["prior_tasks"] == ["detection", "source_attribution"]
        assert a["current_tasks"] == a["final_taxonomy"]["tasks"] == ["source_attribution"]
        assert a["final_taxonomy"]["research_types"] == ["method"]
    assert "synthetic-generator architectures" in actions["T572"]["authenticity_evaluation"]
    assert "0=Real" in actions["T503"]["actual_output_and_decision_space"]
    assert "No explicit binary" in actions["T503"]["authenticity_evaluation"]
    assert "BMVC final PDF" in actions["T572"]["version_limitation"]
    assert "CVF final PDF" in actions["T503"]["version_limitation"]
    text = REPORT.read_text()
    for source in ("https://arxiv.org/html/2308.11557v1", "https://arxiv.org/html/2402.10401v2"):
        assert source in text


def test_public_exports_only_change_target_tasks_and_provenance():
    for path in EXPORTS:
        old = json.loads(previous(path))
        new = json.loads(published(path))
        assert old.keys() == new.keys()
        for key in old:
            if key not in ("records", "metadata"):
                assert old[key] == new[key]
        assert {k: v for k, v in old["metadata"].items() if k != "public_preview_generated_at"} == {
            k: v for k, v in new["metadata"].items() if k != "public_preview_generated_at"
        }
        assert len(old["records"]) == len(new["records"])
        for a, b in zip(old["records"], new["records"]):
            assert a.get("paper_id") == b.get("paper_id")
            if a.get("paper_id") not in PIDS:
                assert a == b
                continue
            assert a["tasks"] == ["detection", "source_attribution"]
            assert b["tasks"] == ["source_attribution"]
            assert {k: v for k, v in a.items() if k not in ("tasks", "taxonomy_review")} == {
                k: v for k, v in b.items() if k not in ("tasks", "taxonomy_review")
            }
            assert {k: v for k, v in a["taxonomy_review"].items() if k != "tasks"} == {
                k: v for k, v in b["taxonomy_review"].items() if k != "tasks"
            }


def test_counts_debt_and_historical_receipts():
    context = load_context()
    assert context["counts"] == CURRENT_CORPUS_COUNTS
    totals = Counter(label for p in context["papers"].values()
                     for key in ("tasks", "research_types") for label in p[key])
    wave = manifest()
    wave5c_totals = Counter(label for p in json.loads(published(EXPORTS[0]))["records"]
                           for key in ("tasks", "research_types") for label in p[key])
    assert dict(wave5c_totals) == wave["taxonomy_after"] == {
        "detection": 587, "source_attribution": 85, "localization": 43,
        "method": 547, "dataset": 132, "benchmark": 88,
        "survey": 20, "analysis_study": 78,
    }
    assert wave["taxonomy_before"]["detection"] == 589
    old_totals = Counter(label for p in json.loads(previous(EXPORTS[0]))["records"]
                         for key in ("tasks", "research_types") for label in p[key])
    assert dict(old_totals) == wave["taxonomy_before"]
    assert old_totals - wave5c_totals == {"detection": 2} and not wave5c_totals - old_totals
    assert totals == CURRENT_TAXONOMY_TOTALS
    pre_import = totals - Counter(LITERATURE51_TAXONOMY_ADDITIONS)
    assert wave5c_totals - pre_import == {"detection": 2, "source_attribution": 1, "method": 2, "analysis_study": 1}
    assert pre_import - wave5c_totals == {"benchmark": 1}
    # T527/B1A/P490 exclusions and B1B R137/R611 research-type successors.
    old_wave = json.loads(previous("data/raw/corpus_quality_batch_c_wave5b_2026_10_09/evidence_manifest.json"))
    assert old_wave["taxonomy_after"]["detection"] == 589
    r = wave["resolution"]
    assert r["after"] == r["after_evidence_only"] == {
        "task_evidence": 1, "institution_evidence": 1,
        "research_type_evidence": 11, "external_unresolved": 13,
        "maintainer_T527": 1, "total_unresolved": 14,
    }
    assert r["remaining_task_ids"] == ["T141"]
    assert r["evidence_debt_subtracted_once"] and r["resolved_change_applied"] == ["T572", "T503"]
    assert r["pending_maintainer_adjudications"] == []
    assert all(context["papers"][pid]["tasks"] == ["source_attribution"] for pid in PIDS)
    assert all(context["papers"][pid]["research_types"] == ["method"] for pid in PIDS)
