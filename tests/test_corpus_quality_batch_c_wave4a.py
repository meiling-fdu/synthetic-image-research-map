"""Focused regression checks for finalized Batch C Wave 4A adjudication."""

from collections import Counter
import csv
from functools import lru_cache
import io
import json
from pathlib import Path
import subprocess

from scripts.validate_corpus_quality_audit import load_context


ROOT = Path(__file__).resolve().parents[1]
BASE = "ea9a9846a8c2b4886adba06a3e7d0798697f33af"
MANIFEST = ROOT / "data/raw/corpus_quality_batch_c_wave4a_2026_10_07/evidence_manifest.json"
REPORT = ROOT / "docs/corpus_quality_batch_c_wave4a_2026_10_07.md"
R099 = "curated:9c39067ac73e7354c2f3"
R176 = "curated:f6ad15b01df18aadfe1a"
R190 = "curated:c84b04cb8e921be753db"
R455 = "curated:04932cb03f767948ddf4"
FROZEN = {R176, R190, R455}
SOURCE = "https://arxiv.org/pdf/2602.10042"


@lru_cache
def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def csv_rows(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def previous_csv(path):
    return list(csv.DictReader(io.StringIO(previous(path).decode("utf-8-sig"), newline="")))


def records(path, *, current=True):
    payload = json.loads((ROOT / path).read_text()) if current else json.loads(previous(path))
    return payload["records"]


def test_r099_is_the_only_authoritative_research_type_change():
    for path in ("data/curated/papers.csv", "data/curated/paper_taxonomy.csv"):
        before = {row["paper_id"]: row for row in previous_csv(path)}
        after = {row["paper_id"]: row for row in csv_rows(path)}
        assert before.keys() == after.keys()
        assert {paper_id for paper_id in before if before[paper_id] != after[paper_id]} == {R099}
        old, new = before[R099], after[R099]
        assert old["research_types"] == "method;dataset"
        assert new["research_types"] == "method"
        assert "dataset" not in new["research_types"].split(";")
        changed_fields = {field for field in old if old[field] != new[field]}
        if path.endswith("papers.csv"):
            assert changed_fields == {"research_types"}
        else:
            assert changed_fields == {
                "research_types", "research_types_review_reason",
                "research_types_evidence_tier", "research_types_evidence_source",
                "research_types_evidence_excerpt", "audited_at",
            }
            assert new["research_types_status"] == "reviewed"
            assert new["research_types_evidence_tier"] == "primary_paper"
            assert new["research_types_evidence_source"] == SOURCE
            assert new["research_types_review_reason"].startswith("R1:")


def test_r176_r190_and_r455_authoritative_rows_remain_unchanged():
    for path in ("data/curated/papers.csv", "data/curated/paper_taxonomy.csv"):
        before = {row["paper_id"]: row for row in previous_csv(path)}
        after = {row["paper_id"]: row for row in csv_rows(path)}
        assert {paper_id: after[paper_id] for paper_id in FROZEN} == {
            paper_id: before[paper_id] for paper_id in FROZEN
        }
    current = {row["paper_id"]: row for row in csv_rows("data/curated/paper_taxonomy.csv")}
    assert current[R176]["research_types"] == "method;dataset"
    assert current[R190]["research_types"] == "dataset;analysis_study"
    assert current[R455]["research_types"] == "method;dataset"


def test_public_exports_change_only_r099_research_type_evidence():
    for path in ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json"):
        before_rows = records(path, current=False)
        after_rows = records(path)
        assert len(before_rows) == len(after_rows)
        assert [r for r in before_rows if r.get("paper_id") != R099] == [
            r for r in after_rows if r.get("paper_id") != R099
        ]
        before = {paper_id: [r for r in before_rows if r.get("paper_id") == paper_id]
                  for paper_id in {R099} | FROZEN}
        after = {paper_id: [r for r in after_rows if r.get("paper_id") == paper_id]
                 for paper_id in {R099} | FROZEN}
        assert len(after[R099]) == len(before[R099]) and after[R099]
        for old, new in zip(before[R099], after[R099]):
            assert old["research_types"] == ["method", "dataset"]
            assert new["research_types"] == ["method"]
            assert {k: v for k, v in old.items() if k not in {"research_types", "taxonomy_review"}} == {
                k: v for k, v in new.items() if k not in {"research_types", "taxonomy_review"}
            }
            assert new["taxonomy_review"]["research_types"]["status"] == "reviewed"
            assert new["taxonomy_review"]["research_types"]["reason"].startswith("R1:")
        for paper_id in FROZEN:
            assert after[paper_id] == before[paper_id]


def test_r1_policy_and_wave4a_ledger_reconcile_four_actions():
    manifest = json.loads(MANIFEST.read_text())
    report = REPORT.read_text()
    assert manifest["adjudication_status"] == "FINAL"
    assert manifest["policy"]["policy_id"] == "R1"
    assert "substantive contribution" in manifest["policy"]["rule"]
    assert "experiments is insufficient" in manifest["policy"]["rule"]
    assert manifest["scope"]["actions"] == 4
    assert manifest["scope"]["primary_documents_attempted"] == 4
    by_id = {row["review_id"]: row for row in manifest["actions"]}
    assert set(by_id) == {"R099", "R176", "R190", "R455"}
    assert by_id["R099"]["scientific_role"] == "EXPERIMENTAL_DATA_ONLY"
    assert by_id["R099"]["evidence_outcome"] == "EVIDENCE_RESOLVED_CHANGE"
    assert by_id["R099"]["final_disposition"] == "REMEDIATION_APPLIED"
    assert by_id["R099"]["corpus_change_applied"] is True
    assert "GenImage and FakeClue" in by_id["R099"]["claimed_data_contribution"]
    assert "BC-Attr-6 and COCO-Attr" in by_id["R190"]["claimed_data_contribution"]
    assert by_id["R190"]["scientific_role"] == "SUBSTANTIVE_REUSABLE_DATASET_CONTRIBUTION"
    assert by_id["R190"]["evidence_outcome"] == "EVIDENCE_RESOLVED_NO_CHANGE"
    assert by_id["R190"]["final_disposition"] == "REMEDIATION_NOT_REQUIRED"
    for review_id in ("R176", "R455"):
        assert by_id[review_id]["evidence_outcome"] == "EVIDENCE_STILL_INSUFFICIENT"
        assert by_id[review_id]["final_disposition"] == "REMEDIATION_NOT_APPLIED"
        assert by_id[review_id]["corpus_change_applied"] is False
    assert manifest["resolution"]["external_batch_c_after"] == 21
    assert manifest["resolution"]["research_type_cases_after"] == 13
    assert manifest["resolution"]["total_unresolved_batch_c_after_including_t527"] == 22
    for token in (
        "EXPERIMENTAL_DATA_ONLY_NO_DATASET", "DATASET_ROLE_SUPPORTED",
        "EVIDENCE_RESOLVED_CHANGE", "EVIDENCE_RESOLVED_NO_CHANGE",
        "REMEDIATION_APPLIED", "REMEDIATION_NOT_REQUIRED", "REMEDIATION_NOT_APPLIED",
    ):
        assert token in report


def test_remaining_batch_c_counts_reconcile_programmatically():
    phase1 = json.loads((ROOT / "data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json").read_text())
    paths = (
        "data/raw/corpus_quality_batch_c_wave1_2026_10_06/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave2_2026_10_06/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave3a_2026_10_06/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave3b1_2026_10_06/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave3b2_2026_10_06/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave3b3_2026_10_07/evidence_manifest.json",
        "data/raw/corpus_quality_batch_c_wave4a_2026_10_07/evidence_manifest.json",
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
    assert len(external) == 35 and len(residual) == 21
    assert categories == {"task": 7, "institution": 1, "research_type": 13}
    assert "R099" not in residual and "R190" not in residual
    assert "R176" in residual and "R455" in residual


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
