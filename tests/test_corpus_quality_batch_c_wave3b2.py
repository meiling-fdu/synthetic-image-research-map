"""Focused regression checks for finalized Batch C Wave 3B-2 adjudication."""

from collections import Counter
import csv
from functools import lru_cache
import io
import json
from pathlib import Path
import subprocess

from scripts.validate_corpus_quality_audit import load_context


ROOT = Path(__file__).resolve().parents[1]
BASE = "1e2c728e0b16cabc1c81ffca9b791829d8aa5d78"
MANIFEST = ROOT / "data/raw/corpus_quality_batch_c_wave3b2_2026_10_06/evidence_manifest.json"
REPORT = ROOT / "docs/corpus_quality_batch_c_wave3b2_2026_10_06.md"
T024 = "curated:1a8e996ef9ce73efc0ef"
T136 = "curated:d59bffe554500b241a3e"
T137 = "curated:246f07c81b9f91e527eb"
T141 = "curated:268336295435cfbbbd5d"
CHANGED = {T024, T136}
FROZEN = {T137, T141}
SOURCES = {
    T024: "https://link.springer.com/content/pdf/10.1007/978-981-92-2856-0_1.pdf",
    T136: "https://arxiv.org/pdf/2605.12967",
}
EXPECTED_TASK_RESIDUAL = {
    "T236", "T137", "T141", "T572", "T576", "T503", "T611", "T634",
}


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
    data = subprocess.check_output(["git", "show", "9b7dec4:" + path], cwd=ROOT)
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline="")))


def records(path, *, current=True):
    payload = json.loads((ROOT / path).read_text()) if current else json.loads(previous(path))
    return payload["records"]


def test_exactly_two_authoritative_task_rows_change():
    for path, key in (
        ("data/curated/papers.csv", "paper_id"),
        ("data/curated/paper_taxonomy.csv", "paper_id"),
    ):
        before = {row[key]: row for row in previous_csv(path)}
        after = {row[key]: row for row in adjudicated_csv(path)}
        assert before.keys() == after.keys()
        assert {paper_id for paper_id in before if before[paper_id] != after[paper_id]} == CHANGED
        for paper_id in CHANGED:
            old, new = before[paper_id], after[paper_id]
            assert old["tasks"] == "detection;source_attribution"
            assert new["tasks"] == "source_attribution"
            changed_fields = {field for field in old if old[field] != new[field]}
            if path.endswith("papers.csv"):
                assert changed_fields == {"tasks"}
            else:
                assert changed_fields == {
                    "tasks", "tasks_review_reason", "tasks_evidence_tier",
                    "tasks_evidence_source", "tasks_evidence_excerpt", "audited_at",
                }
                assert new["tasks_status"] == "reviewed"
                assert new["tasks_evidence_tier"] == "primary_paper"
                assert new["tasks_evidence_source"] == SOURCES[paper_id]


def test_t137_and_t141_remain_semantically_unchanged():
    for path in ("data/curated/papers.csv", "data/curated/paper_taxonomy.csv"):
        before = {row["paper_id"]: row for row in previous_csv(path)}
        after = {row["paper_id"]: row for row in csv_rows(path)}
        assert {paper_id: after[paper_id] for paper_id in FROZEN} == {
            paper_id: before[paper_id] for paper_id in FROZEN
        }


def test_public_exports_change_only_the_two_task_adjudications():
    for path in ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json"):
        before = {paper_id: [row for row in records(path, current=False) if row.get("paper_id") == paper_id]
                  for paper_id in CHANGED | FROZEN}
        after = {paper_id: [row for row in records(path) if row.get("paper_id") == paper_id]
                 for paper_id in CHANGED | FROZEN}
        for paper_id in CHANGED:
            assert len(after[paper_id]) == len(before[paper_id]) and after[paper_id]
            for old, new in zip(before[paper_id], after[paper_id]):
                assert old["tasks"] == ["detection", "source_attribution"]
                assert new["tasks"] == ["source_attribution"]
                assert {k: v for k, v in old.items() if k not in {"tasks", "taxonomy_review"}} == {
                    k: v for k, v in new.items() if k not in {"tasks", "taxonomy_review"}
                }
                assert new["taxonomy_review"]["tasks"]["status"] == "reviewed"
                assert new["taxonomy_review"]["tasks"]["reason"].startswith("T1:")
        for paper_id in FROZEN:
            assert after[paper_id] == before[paper_id]


def test_t1_policy_and_wave_ledger_reconcile_four_actions():
    manifest = json.loads(MANIFEST.read_text())
    report = REPORT.read_text()
    assert manifest["adjudication_status"] == "FINAL"
    assert manifest["policy"]["policy_id"] == "T1"
    by_id = {row["review_id"]: row for row in manifest["actions"]}
    assert set(by_id) == {"T024", "T136", "T137", "T141"}
    for review_id in ("T024", "T136"):
        row = by_id[review_id]
        assert row["adjudication"] == "ATTRIBUTION_ONLY_NO_DETECTION"
        assert row["evidence_outcome"] == "EVIDENCE_RESOLVED_CHANGE"
        assert row["final_disposition"] == "REMEDIATION_APPLIED"
        assert row["corpus_change_applied"] is True
    for review_id in ("T137", "T141"):
        row = by_id[review_id]
        assert row["adjudication"] == "EVIDENCE_STILL_INSUFFICIENT"
        assert row["evidence_outcome"] == "EVIDENCE_STILL_INSUFFICIENT"
        assert row["final_disposition"] == "REMEDIATION_NOT_APPLIED"
        assert row["corpus_change_applied"] is False
    assert "homologous versus non-homologous" in by_id["T024"]["evaluated_class_space"]
    assert "not an individual-image authenticity class" in by_id["T024"]["real_image_role"]
    assert "Thirty-two-way source classification" in by_id["T136"]["evaluated_class_space"]
    assert "does not define a separate binary authenticity protocol" in by_id["T136"]["real_image_role"]
    assert all(token in report for token in (
        "EVIDENCE_RESOLVED_CHANGE", "REMEDIATION_APPLIED",
        "EVIDENCE_STILL_INSUFFICIENT", "REMEDIATION_NOT_APPLIED",
    ))


def test_external_batch_c_residual_reconciles_programmatically():
    phase1 = json.loads((ROOT / "data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json").read_text())
    paths = (
        "data/raw/corpus_quality_batch_c_wave1_2026_10_06/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave2_2026_10_06/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave3a_2026_10_06/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave3b1_2026_10_06/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave3b2_2026_10_06/evidence_manifest.json",
    )
    external = {
        row["review_id"]: row for row in phase1["residual_triage"]
        if row["evidence_status"] == "EXTERNAL_PRIMARY_SOURCE_REQUIRED"
    }
    resolved = set()
    for path in paths:
        wave = json.loads((ROOT / path).read_text())
        resolved.update(
            row["review_id"] for row in wave["actions"]
            if row.get("evidence_outcome", "").startswith("EVIDENCE_RESOLVED")
        )
    residual = {review_id: external[review_id] for review_id in external.keys() - resolved}
    categories = Counter(row["category"] for row in residual.values())
    task_residual = {review_id for review_id, row in residual.items() if row["category"] == "task"}
    manifest = json.loads(MANIFEST.read_text())
    assert len(external) == 35 and len(residual) == 24
    assert task_residual == EXPECTED_TASK_RESIDUAL
    assert categories == {"task": 8, "institution": 1, "research_type": 15}
    assert manifest["resolution"]["external_batch_c_after"] == len(residual)
    assert manifest["resolution"]["total_unresolved_batch_c_after_including_t527"] == 25


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
    assert tasks == {"detection": 589, "source_attribution": 85, "localization": 42}
    assert research_types == {
        "method": 547,
        "dataset": 132,
        "benchmark": 88,
        "survey": 20,
        "analysis_study": 78,
    }
