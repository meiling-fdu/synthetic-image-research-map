"""Accepted T579 taxonomy change preserves T608, provenance and audit boundaries."""
from collections import Counter
import base64
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import re

import pytest

from scripts.curated_schema import ALLOWED_REVIEW_ACTIONS, ALLOWED_REVIEW_QUEUES
from scripts.paper_exclusions import normalize_doi
from scripts.review_decisions import read_review_decisions
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from tests.baseline_expectations import CURRENT_CORPUS_COUNTS, CURRENT_TAXONOMY_TOTALS
from tests.corpus_quality_test_helpers import csv_records, published_bytes, published_context

ROOT = Path(__file__).resolve().parents[1]
BASE = "8e60ee5729ab0b29703078b91cf83fb245048f6c"
EVIDENCE_BASE = "a74bdf79f4d8b3c4fb64af7b83701dce60238289"
DOI = "10.24963/ijcai.2023/52"
T579 = "doi:" + DOI
T608_DOI = "10.1109/lsp.2021.3130525"
T608 = "doi:" + T608_DOI
DECISION = "review:e28a216810f3dbb03546"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1d_2026_10_16/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1d_2026_10_16.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
T579_FIELDS = {"tasks", "tasks_review_reason", "tasks_evidence_tier", "tasks_evidence_source",
               "tasks_evidence_excerpt", "audited_at"}
EVIDENCE_ONLY_HASHES = {
    "manifest": "b3643534e71e395736cab05540dcbf02bb22d173e556eabbd44f316b03890684",
    "report": "60071ce822a25d1d0074a586256edca673c8b662f6da6356fcc63d9d4d99a6f2"}


def previous(path):
    return published_bytes(BASE, path)


def rows(path):
    return csv_records((ROOT / path).read_bytes())


def matching(records, doi):
    return [row for row in records if normalize_doi(row.get("doi")) == doi]


@lru_cache
def packet():
    return json.loads((ROOT / MANIFEST).read_bytes())


@lru_cache
def original_packet():
    archive = packet()["evidence_only_packet_archives"]["manifest"]
    return json.loads(gzip.decompress(base64.b64decode(archive["payload"], validate=True)))


def selected_decision():
    selected = matching(read_review_decisions(ROOT / DECISIONS), DOI)
    assert len(selected) == 1
    return selected[0]


def test_only_t579_task_and_six_evidence_fields_change_without_losing_original_csv_bytes():
    before_raw, after_raw = previous(TAXONOMY), (ROOT / TAXONOMY).read_bytes()
    before = {row["taxonomy_id"]: row for row in csv_records(before_raw)}
    after = {row["taxonomy_id"]: row for row in csv_records(after_raw)}
    assert before.keys() == after.keys()
    assert {pid for pid in before if before[pid] != after[pid]} == {T579}
    old, new = before[T579], after[T579]
    assert {field for field in old if old[field] != new[field]} == T579_FIELDS
    assert old["tasks"] == "detection;source_attribution" and new["tasks"] == "detection"
    assert old["research_types"] == new["research_types"] == "method"
    assert new["tasks_status"] == old["tasks_status"] == "reviewed"
    assert new["tasks_evidence_tier"] == "primary_paper"
    assert new["tasks_evidence_source"] == "https://www.ijcai.org/proceedings/2023/0052.pdf"
    assert "T1" in new["tasks_review_reason"] and "T579" in new["tasks_review_reason"]
    assert all(token in new["tasks_evidence_excerpt"] for token in ("3.3", "0.5", "Tables 2-4"))
    assert new["audited_at"] == "2026-10-17"
    assert old["paper_id"] == new["paper_id"] == ""  # Preserve candidate identity.
    old_lines, new_lines = before_raw.splitlines(keepends=True), after_raw.splitlines(keepends=True)
    assert len(old_lines) == len(new_lines)
    changed_lines = [(a, b) for a, b in zip(old_lines, new_lines) if a != b]
    assert len(changed_lines) == 1
    assert all(DOI.encode() in line for line in changed_lines[0])
    assert before_raw.count(b"\r\n") == after_raw.count(b"\r\n")


@pytest.mark.parametrize("path", [
    "data/curated/papers.csv", "data/curated/paper_exclusions.csv",
    "data/curated/publication_overrides.csv", "data/curated/paper_arxiv_links.csv",
    "data/curated/paper_version_merges.csv", "data/curated/venue_aliases.csv",
    "data/curated/author_institution_mappings.csv", "data/curated/institution_author_overrides.csv",
    "data/curated/institutions.csv", "data/curated/institution_locations.csv",
    "data/curated/institution_aliases.csv", "data/curated/institution_hierarchy.csv",
])
def test_bibliography_authors_affiliations_institutions_and_exclusions_are_byte_exact(path):
    assert (ROOT / path).read_bytes() == previous(path)


@pytest.mark.parametrize("path,target_rows", [(PUBLIC[0], 1), (PUBLIC[1], 3)])
def test_public_records_change_only_t579_task_without_changing_any_identity_or_relationship(path, target_rows):
    before, after = json.loads(previous(path)), json.loads((ROOT / path).read_bytes())
    assert len(before["records"]) == len(after["records"])
    assert len(matching(before["records"], DOI)) == len(matching(after["records"], DOI)) == target_rows
    changed = []
    for old, new in zip(before["records"], after["records"]):
        assert normalize_doi(old.get("doi")) == normalize_doi(new.get("doi"))
        if normalize_doi(old.get("doi")) != DOI:
            assert old == new
            continue
        changed.append(new)
        assert old["tasks"] == ["detection", "source_attribution"] and new["tasks"] == ["detection"]
        assert new["research_types"] == old["research_types"] == ["method"]
        assert {k: v for k, v in old.items() if k not in {"tasks", "taxonomy_review"}} == {
            k: v for k, v in new.items() if k not in {"tasks", "taxonomy_review"}}
        assert {k: v for k, v in old["taxonomy_review"].items() if k != "tasks"} == {
            k: v for k, v in new["taxonomy_review"].items() if k != "tasks"}
        assert new["taxonomy_review"]["tasks"]["status"] == "reviewed"
        assert new["taxonomy_review"]["tasks"] == {
            **old["taxonomy_review"]["tasks"],
            "reason": matching(rows(TAXONOMY), DOI)[0]["tasks_review_reason"],
        }
        if path == PUBLIC[1]:
            assert old["id"] == new["id"] and old["institution_id"] == new["institution_id"]
    assert len(changed) == target_rows
    for payload in (before, after):
        payload.pop("records")
        payload["metadata"].pop("public_preview_generated_at", None)
    assert before == after


def test_exactly_one_terminal_t579_decision_appends_and_retains_all_existing_rows():
    old, new = previous(DECISIONS), (ROOT / DECISIONS).read_bytes()
    assert new.startswith(old)
    old_rows, new_rows = csv_records(old), rows(DECISIONS)
    assert new_rows[:len(old_rows)] == old_rows
    assert new_rows[len(old_rows):] == [selected_decision()]
    decision = selected_decision()
    assert decision["decision_id"] == DECISION
    assert decision["review_queue"] == "other" and decision["review_queue"] in ALLOWED_REVIEW_QUEUES
    assert decision["action"] == "no_action_after_review" and decision["action"] in ALLOWED_REVIEW_ACTIONS
    assert decision["target_type"] == "paper" and decision["doi"] == DOI
    assert decision["openalex_url"] == "https://openalex.org/W4385767391"
    assert decision["title"] == matching(csv_records(previous(TAXONOMY)), DOI)[0]["title"]
    assert decision["created_by"] == "maintainer-approved-batch-b-b1d"
    assert decision["created_at"] == decision["updated_at"] == "2026-10-17T00:00:00Z"
    assert "Batch B review T579;" in decision["review_note"]
    assert "DETECTION_ONLY" in decision["review_note"] and "PROPOSE_CORRECTION_ACCEPTED" in decision["review_note"]
    assert "https://www.ijcai.org/proceedings/2023/0052.pdf" in decision["review_note"]
    assert len({row["decision_id"] for row in new_rows}) == len(new_rows)


def test_t608_canonical_public_and_review_states_remain_exact_without_scientific_endorsement():
    for path in PUBLIC:
        old = matching(json.loads(previous(path))["records"], T608_DOI)
        new = matching(json.loads((ROOT / path).read_bytes())["records"], T608_DOI)
        assert old and old == new
        assert all(row["tasks"] == ["detection", "source_attribution"] for row in new)
    assert matching(rows(TAXONOMY), T608_DOI) == matching(csv_records(previous(TAXONOMY)), T608_DOI)
    assert matching(rows(DECISIONS), T608_DOI) == matching(csv_records(previous(DECISIONS)), T608_DOI) == []
    before = next(row for row in original_packet()["records"] if row["review_id"] == "T608")
    after = next(row for row in packet()["records"] if row["review_id"] == "T608")
    assert before == after
    assert after["provisional_outcome"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert after["scientifically_sufficient"] is False and after["proposed_tasks"] is None
    assert after["full_text_examined"] is False
    assert after["formal_review_action_closed"] is after["authoritative_changes_applied"] is False


def test_current_counts_and_taxonomy_delta_recompute_from_preferred_public_identities():
    old, new = published_context(BASE), load_context()
    assert old["counts"] == new["counts"] == CURRENT_CORPUS_COUNTS == {
        "public": 674, "formal": 557, "mapped": 613, "unmapped": 61,
        "relationship_rows": 1410, "unique_paper_institution_pairs": 1410}
    assert list(old["papers"]) == list(new["papers"])
    assert old["pairs"] == new["pairs"] and all(count == 1 for count in new["pairs"].values())
    before = Counter(label for row in old["papers"].values()
                     for dimension in ("tasks", "research_types") for label in row[dimension])
    after = Counter(label for row in new["papers"].values()
                    for dimension in ("tasks", "research_types") for label in row[dimension])
    assert before - after == {"source_attribution": 1} and not after - before
    assert after == CURRENT_TAXONOMY_TOTALS == {
        "detection": 621, "source_attribution": 86, "localization": 45,
        "method": 579, "dataset": 134, "benchmark": 90, "survey": 21, "analysis_study": 81}
    # Preserve aliases such as TWIGMA's preferred public ID in map pair keys.
    for taxonomy_id, public_id in old["taxonomy_to_public_id"].items():
        assert old["taxonomy"][public_id]["taxonomy_id"] == taxonomy_id
        assert (old["papers"][public_id].get("paper_id") or taxonomy_id) == public_id


def test_original_questions_survive_and_only_t579_resolves_in_live_accounting():
    ledger = [row for row in decision_rows(load_queues()) if row.get("batch") == "B"]
    assert len(ledger) == 159 and len({row["paper_id"] for row in ledger}) == 148
    assert [(row["review_id"], row["dimension"]) for row in ledger if row["paper_id"] == T579] == [("T579", "tasks")]
    def closed(decisions):
        result = {}
        for decision in decisions:
            match = re.search(r"\bBatch B review ([A-Z]\d{3});", decision["review_note"])
            if match and decision["action"] == "no_action_after_review":
                assert match.group(1) not in result
                result[match.group(1)] = decision["decision_id"]
        return result
    before, after = closed(csv_records(previous(DECISIONS))), closed(rows(DECISIONS))
    assert after == {**before, "T579": DECISION} and "T608" not in after
    assert set(before) == {"L013", "P139", "P153", "P490", "R137", "R611"}
    pending = [row for row in ledger if row["review_id"] not in after]
    public = load_context()["papers"]
    active = [row for row in pending if row["paper_id"] in public]
    inactive = [row for row in pending if row["paper_id"] not in public]
    assert len(pending) == 152 and len(active) == 150
    assert len({row["paper_id"] for row in active}) == 139
    assert {row["review_id"] for row in inactive} == {"L015", "P562"}
    assert {"T608", "T526", "P526"} <= {row["review_id"] for row in active}
    account = packet()["batch_b_accounting"]
    assert account["historical_actions"] == len(ledger)
    assert account["historical_papers"] == len({row["paper_id"] for row in ledger})
    assert account["resolved_review_ids"] == sorted(after)
    assert account["historical_unresolved_actions"] == len(pending)
    assert account["active_public_unresolved_actions"] == len(active)
    assert account["active_public_unresolved_papers"] == len({row["paper_id"] for row in active})
    assert account["active_public_unresolved_review_ids"] == [row["review_id"] for row in active]


def test_complete_evidence_only_packet_and_report_are_archived_without_retrieval_history_changes():
    evidence = packet()
    assert len(evidence["records"]) == 2
    assert {row["review_id"] for row in evidence["records"]} == {"T579", "T608"}
    archives = evidence["evidence_only_packet_archives"]
    assert archives.keys() == EVIDENCE_ONLY_HASHES.keys()
    for key, expected in EVIDENCE_ONLY_HASHES.items():
        archive = archives[key]
        assert archive["encoding"] == "gzip+base64"
        compressed = base64.b64decode(archive["payload"], validate=True)
        assert hashlib.sha256(compressed).hexdigest() == archive["compressed_sha256"]
        raw = gzip.decompress(compressed)
        assert len(raw) == archive["bytes"]
        assert hashlib.sha256(raw).hexdigest() == archive["sha256"] == expected
        assert archive["source_path"] == (MANIFEST if key == "manifest" else REPORT)
    original = original_packet()
    assert original["baseline"]["commit"] == EVIDENCE_BASE
    for field in ("retrieval_history", "retrieval_accounting", "source_files", "operational_source_files", "locked_policy"):
        assert evidence[field] == original[field]
    assert original["scope"]["authoritative_changes"] == original["scope"]["review_actions_closed"] == 0
    assert original["batch_b_accounting"]["historical_unresolved_actions"] == 153
    assert original["retrieval_accounting"]["new_full_manuscripts_by_review"] == {"T579": 1, "T608": 0}
    assert original["retrieval_accounting"]["ieee_retries"] == 0
    old = next(row for row in original["records"] if row["review_id"] == "T579")
    new = next(row for row in evidence["records"] if row["review_id"] == "T579")
    for field in ("canonical_identity", "original_review", "original_review_record", "source_provenance",
                  "review_coverage", "scientific_findings", "provisional_outcome", "proposed_tasks", "confidence"):
        assert new[field] == old[field]
    assert new["scientifically_sufficient"] is True and new["full_text_examined"] is True
    assert new["maintainer_acceptance_pending"] is False
    assert new["authoritative_changes_applied"] is new["formal_review_action_closed"] is True
    accepted = new["adjudication"]
    assert accepted["accepted_outcome"] == "DETECTION_ONLY" and accepted["applied"] is True
    assert accepted["tasks_before"] == ["detection", "source_attribution"]
    assert accepted["tasks_after"] == ["detection"]
    assert accepted["taxonomy_before"] == matching(csv_records(previous(TAXONOMY)), DOI)[0]
    assert accepted["taxonomy_after"] == matching(rows(TAXONOMY), DOI)[0]
    assert set(accepted["changed_fields"]) == T579_FIELDS
    assert accepted["review_decision"] == selected_decision()
    assert new["post_adjudication_public_state"] == load_context()["papers"][T579]
    assert evidence["corpus_after"] == load_context()["counts"]
    assert evidence["taxonomy_after"] == CURRENT_TAXONOMY_TOTALS
    original_hashes = {entry["path"]: entry["sha256"] for entry in original["source_files"]}
    assert len(original_hashes) == 12
    assert evidence["current_source_sha256"].keys() == original_hashes.keys()
    for path, expected in evidence["current_source_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path


@pytest.mark.parametrize("filename", ["unmapped_papers.json", "taxonomy_review.json", "relationship_review.json", "publication_metadata_review.json", "batch_c_policy_decisions.json"])
def test_original_audit_ledgers_and_locked_policies_are_frozen(filename):
    path = AUDIT + filename
    assert (ROOT / path).read_bytes() == previous(path)


@pytest.mark.parametrize("path", [
    "data/raw/corpus_quality_batch_b_wave_b1a_2026_10_12/evidence_manifest.json",
    "docs/corpus_quality_batch_b_wave_b1a_2026_10_12.md",
    "data/raw/corpus_quality_batch_b_wave_b1b_2026_10_15/evidence_manifest.json",
    "docs/corpus_quality_batch_b_wave_b1b_2026_10_15.md",
    "data/raw/corpus_quality_batch_b_wave_b1c_2026_10_16/evidence_manifest.json",
    "docs/corpus_quality_batch_b_wave_b1c_2026_10_16.md",
    "data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
    "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
])
def test_earlier_published_decisions_and_batch_c_thirteen_debts_remain_frozen(path):
    assert (ROOT / path).read_bytes() == previous(path)


def test_all_49_frozen_neurips_artifacts_are_identical():
    receipt = json.loads((ROOT / "data/raw/systematic_gap_migration_2026_10_03/baseline.json").read_bytes())
    assert len(receipt["frozen_sha256"]) == 49
    for path, expected in receipt["frozen_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
